#!/usr/bin/env python3
"""Render a C&C3 tank (tools/cnc3/c3_extract_model.py .npz) to the mod's per-facing PNGs.

Camera and light are vxl_render.py's, so a C&C3 tank sits beside the TS and RA2 voxel units:
orthographic at --elev 32 (the ground-vehicle ledger), yaw0 90 so frame 0 faces north and
frames advance counter-clockwise, and the fixed top-north-west light shaded through Tiberian
Sun's VOXELS.VPL brightness ramp (contract 11). The ramp is sampled continuously rather than
in TS's 32 steps: mesh normals are smooth, and a stepped table bands them. C&C3's own
tangent-space normal maps supply the panel detail.

House colour: HC_<model>'s alpha is C&C3's recolour mask. Masked texels become the launcher's
team green following the texel's own luminance, scaled so the mask's average texel lands on
TEAM_LEVEL. C&C3 paints house colour over panels of very different brightness (the Mammoth's
bright tan, the Predator's darker olive); normalising puts both at the green the shipped TS and
RA2 units carry (post-shade median G about 145).

Tread animation: the belts' U coordinate scrolls by the tread phase in link pitches. Driving
forwards, a track's top run travels forwards relative to the hull and its ground run backwards,
so rising phase moves the top run the way the nose points (against the model's tread_dudx sign).

Usage:
  c3_render.py <model.npz> <out_dir> --part hull|turret [--frames 32] [--tread-steps 3]
               [--ppu 13] [--canvas 1000] [--damaged]
Writes frame-FFFF.png (hull: frame = facing * tread_steps + step; turret: frame = facing).
Hull renders pivot on the model origin (ground under the hull centre); turret renders pivot
on the turret bone, which the pack step seats per hull facing.

License: GPL v3.
"""
import argparse
import math
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

LIGHT = np.array([-0.5, 0.6, 0.75])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
TS_VPL_SCALE = np.array([
    0.619, 0.662, 0.701, 0.736, 0.777, 0.889, 0.925, 0.975,
    1.000, 1.023, 1.066, 1.106, 1.142, 1.169, 1.204, 1.233,
    1.264, 1.339, 1.396, 1.454, 1.517, 1.564, 1.609, 1.646,
    1.696, 1.737, 1.775, 1.802, 1.833, 1.859, 1.893, 1.922])
TS_LIGHT_LEN = 1.5
TEAM_GREEN = np.array([0.0, 1.0, 0.0])
TEAM_LEVEL = 128.0
LUMA = np.array([0.299, 0.587, 0.114], dtype=np.float32)


def load_rgba(path):
    return np.asarray(Image.open(path).convert("RGBA")).astype(np.float32)


def sample(tex, uv):
    """Bilinear, wrapping. uv (N,2) in texture space (v down)."""
    h, w = tex.shape[:2]
    x = uv[:, 0] * w - 0.5
    y = uv[:, 1] * h - 0.5
    x0 = np.floor(x).astype(np.int64)
    y0 = np.floor(y).astype(np.int64)
    fx = (x - x0)[:, None]
    fy = (y - y0)[:, None]
    x0 %= w
    y0 %= h
    x1 = (x0 + 1) % w
    y1 = (y0 + 1) % h
    return ((tex[y0, x0] * (1 - fx) + tex[y0, x1] * fx) * (1 - fy)
            + (tex[y1, x0] * (1 - fx) + tex[y1, x1] * fx) * fy)


class Model:
    def __init__(self, path, damaged=False):
        d = np.load(path)
        self.pos, self.nrm, self.tan, self.bin = d["pos"], d["nrm"], d["tan"], d["bin"]
        self.uv, self.tris, self.part, self.mat = d["uv"], d["tris"], d["part"], d["mat"]
        self.turret_pivot = d["turret_pivot"]
        self.dudx_sign = 1.0 if float(d["tread_dudx"]) >= 0 else -1.0
        tex = dict(d["textures"])
        base = os.path.dirname(path)
        self.body = load_rgba(os.path.join(base, tex["body_damaged" if damaged else "body"]))
        self.house = load_rgba(os.path.join(base, tex["house"]))
        self.treads = load_rgba(os.path.join(base, tex["treads"]))
        self.normal = load_rgba(os.path.join(base, tex["normal"]))
        self.link_pitch = self._link_pitch()
        self.team_mean = self._team_mean()

    def _team_mean(self):
        """Mean luminance of the diffuse texels under the house-colour mask."""
        h, w = self.body.shape[:2]
        mask = np.asarray(Image.fromarray(self.house[..., 3].astype(np.uint8)).resize((w, h), Image.BILINEAR))
        lum = self.body[..., :3] @ LUMA
        return float(lum[mask > 128].mean())

    def _link_pitch(self):
        """Tread link spacing in U, from the sheet's horizontal autocorrelation."""
        lum = self.treads[..., :3].mean(2)
        row = lum.mean(0) - lum.mean()
        w = len(row)
        ac = np.array([np.dot(row, np.roll(row, k)) for k in range(w // 2)])
        ac /= ac[0]
        # the FIRST strong peak: a multiple of the pitch correlates as well, and a step
        # sized off it aliases into the belt rolling backwards
        best = ac[4:].max()
        for k in range(4, w // 2 - 1):
            if ac[k] >= ac[k - 1] and ac[k] >= ac[k + 1] and ac[k] > 0.8 * best:
                return k / w
        return (4 + int(np.argmax(ac[4:]))) / w


def render(m, yaw_deg, part, ppu, canvas, elev_deg, tread_phase=0.0, ss=3, turret_on_hull_origin=False):
    E = math.radians(elev_deg)
    sinE, cosE = math.sin(E), math.cos(E)
    tri_part = m.part[m.tris[:, 0]]
    if part == "hull":
        tsel = tri_part != 1
        origin = np.zeros(3)
    else:
        tsel = tri_part == 1
        origin = np.zeros(3) if turret_on_hull_origin else np.array([m.turret_pivot[0], m.turret_pivot[1], 0.0])
    tris = m.tris[tsel]

    yaw = math.radians(yaw_deg)
    c, s = math.cos(yaw), math.sin(yaw)
    R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    P = (m.pos - origin) @ R.T
    N = m.nrm @ R.T
    T = m.tan @ R.T
    B = m.bin @ R.T

    S = canvas * ss
    k = ppu * ss
    sx = S / 2 + P[:, 0] * k
    sy = S / 2 - (P[:, 1] * sinE + P[:, 2] * cosE) * k
    depth = P[:, 2] * sinE - P[:, 1] * cosE

    zbuf = np.full((S, S), -1e9, dtype=np.float64)
    tid = np.full((S, S), -1, dtype=np.int64)
    bary = np.zeros((S, S, 3), dtype=np.float64)
    for t, (a, b, cc) in enumerate(tris):
        xa, xb, xc = sx[a], sx[b], sx[cc]
        ya, yb, yc = sy[a], sy[b], sy[cc]
        den = (yb - yc) * (xa - xc) + (xc - xb) * (ya - yc)
        if abs(den) < 1e-9:
            continue
        x0 = max(int(math.floor(min(xa, xb, xc))), 0)
        x1 = min(int(math.ceil(max(xa, xb, xc))), S - 1)
        y0 = max(int(math.floor(min(ya, yb, yc))), 0)
        y1 = min(int(math.ceil(max(ya, yb, yc))), S - 1)
        if x0 > x1 or y0 > y1:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        w0 = ((yb - yc) * (gx - xc) + (xc - xb) * (gy - yc)) / den
        w1 = ((yc - ya) * (gx - xc) + (xa - xc) * (gy - yc)) / den
        w2 = 1 - w0 - w1
        inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not inside.any():
            continue
        z = w0 * depth[a] + w1 * depth[b] + w2 * depth[cc]
        sub = zbuf[y0:y1 + 1, x0:x1 + 1]
        win = inside & (z > sub)
        sub[win] = z[win]
        tid[y0:y1 + 1, x0:x1 + 1][win] = t
        bsub = bary[y0:y1 + 1, x0:x1 + 1]
        bsub[win] = np.stack([w0[win], w1[win], w2[win]], -1)

    ys, xs = np.nonzero(tid >= 0)
    ti = tid[ys, xs]
    tv = tris[ti]
    w = bary[ys, xs]

    def interp(arr):
        return (arr[tv[:, 0]] * w[:, 0:1] + arr[tv[:, 1]] * w[:, 1:2] + arr[tv[:, 2]] * w[:, 2:3])

    uv = interp(m.uv)
    n = interp(N)
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    is_tread = m.mat[tv[:, 0]] == 1

    rgb = np.zeros((len(ys), 3), dtype=np.float32)
    body = ~is_tread
    if body.any():
        buv = uv[body]
        col = sample(m.body, buv)[:, :3]
        mask = sample(m.house, buv)[:, 3:4] / 255.0
        lum = (col @ LUMA)[:, None]
        team = np.clip(TEAM_GREEN * TEAM_LEVEL * lum / m.team_mean, 0, 255)
        # white decals painted over house colour (unit numbers, the GDI eagle) stay white
        sat = (col.max(1, keepdims=True) - col.min(1, keepdims=True)) / np.maximum(col.max(1, keepdims=True), 1)
        white = np.clip((lum - 170.0) / 40.0, 0, 1) * np.clip(1 - sat * 3, 0, 1)
        mask = mask * (1 - white)
        rgb[body] = col * (1 - mask) + team * mask
        # tangent-space normal map
        t = interp(T)[body]
        bn = interp(B)[body]
        nm = sample(m.normal, buv)[:, :3] / 127.5 - 1.0
        nb = n[body]
        t = t - nb * (t * nb).sum(1, keepdims=True)
        t /= np.linalg.norm(t, axis=1, keepdims=True) + 1e-12
        bn = bn - nb * (bn * nb).sum(1, keepdims=True)
        bn /= np.linalg.norm(bn, axis=1, keepdims=True) + 1e-12
        pn = t * nm[:, 0:1] + bn * nm[:, 1:2] + nb * nm[:, 2:3]
        pn /= np.linalg.norm(pn, axis=1, keepdims=True) + 1e-12
        n[body] = pn
    if is_tread.any():
        tuv = uv[is_tread].copy()
        tuv[:, 0] -= m.dudx_sign * tread_phase * m.link_pitch
        rgb[is_tread] = sample(m.treads, tuv)[:, :3]

    lam = np.clip(n @ LIGHT, 0, 1)
    shade = np.interp(lam * TS_LIGHT_LEN * 16, np.arange(32), TS_VPL_SCALE)
    rgb = np.clip(rgb * shade[:, None], 0, 255)

    img = np.zeros((S, S, 4), dtype=np.float32)
    img[ys, xs, :3] = rgb
    img[ys, xs, 3] = 255
    # premultiplied box downsample, then un-premultiply
    img[..., :3] *= img[..., 3:4] / 255.0
    img = img.reshape(canvas, ss, canvas, ss, 4).mean((1, 3))
    a = img[..., 3:4]
    img[..., :3] = np.where(a > 0, img[..., :3] * 255.0 / np.maximum(a, 1e-6), 0)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGBA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("out")
    ap.add_argument("--part", choices=("hull", "turret"), required=True)
    ap.add_argument("--frames", type=int, default=32)
    ap.add_argument("--tread-steps", type=int, default=3)
    ap.add_argument("--ppu", type=float, default=13.0)
    ap.add_argument("--canvas", type=int, default=1000)
    ap.add_argument("--elev", type=float, default=32.0)
    ap.add_argument("--yaw0", type=float, default=90.0)
    ap.add_argument("--damaged", action="store_true")
    ap.add_argument("--only", type=str, default="", help="comma list of facings to render")
    ap.add_argument("--stock-turret", action="store_true",
                    help="turret frames stay where they sit on the hull at the hull's own heading, "
                         "for a stock engine that draws every turret at the unit centre")
    a = ap.parse_args()
    m = Model(a.model, a.damaged)
    print(f"link pitch {m.link_pitch:.4f} U, scroll sign {m.dudx_sign:+.0f}")
    os.makedirs(a.out, exist_ok=True)
    only = {int(x) for x in a.only.split(",")} if a.only else None
    steps = a.tread_steps if a.part == "hull" else 1
    for f in range(a.frames):
        if only is not None and f not in only:
            continue
        yaw = a.yaw0 + f * 360.0 / a.frames
        for st in range(steps):
            img = render(m, yaw, a.part, a.ppu, a.canvas, a.elev, st / steps, turret_on_hull_origin=a.stock_turret)
            img.save(os.path.join(a.out, f"frame-{f * steps + st:04d}.png"))
        print(f"facing {f}", flush=True)


if __name__ == "__main__":
    main()
