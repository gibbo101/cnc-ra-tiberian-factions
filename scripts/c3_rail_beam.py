#!/usr/bin/env python3
"""Render C&C3's railgun shot (FX_RailGunFire, FX_RailGunHit) as HD anim frames for the Mammoth Mk. II.

C&C3 draws the shot as particle streaks: a straight white core and three blue sine threads that widen toward the
target, a lens flare at the muzzle and a blue-white glow with sparks at the impact (the values are C&C3 1.9's,
docs/cnc3-railgun-beam.md). The launcher blends straight alpha only, so the additive light is baked into RGBA.

  C3RAILSEG  one cell of beam pointing east on a square 192 px frame, drawn rotated along the shot: shape
             (tier * 4 + length) * 15 + frame, with 4 thread-strength tiers by distance along the shot, lengths
             32/64/96/128 px (the last piece of a shot is shorter) and 15 game frames.
  C3RAILMZ   the muzzle flash, 5 frames on 192 px, drawn unrotated.
  C3RAILHIT  the impact glow and sparks, 15 frames on 256 px, the sparks thrown west (drawn rotated to the shot).

Inputs: resources/custom-art/c3-railgun-beam/ (FXRailgunThread, FXLenzFlare01, FXFireBlast04, from C&C3's
static stream). Writes the ZIPs and tiles where scripts/asset_packs.py routes the names.
Usage: c3_rail_beam.py
License: GPL v3.
"""
import io
import json
import math
import os
import sys
import zipfile

import numpy as np
from PIL import Image

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS)
import asset_packs  # noqa: E402
from ts_gen_sonicwave import patch_tileset  # noqa: E402

TEX = os.path.join(SCRIPTS, "..", "resources", "custom-art", "c3-railgun-beam")
SS = 2              # supersample
UNIT = 4.0          # HD px per C&C3 world unit (the C&C3 tanks' packing scale)
SEG = 128           # one cell of beam
SEG_FRAME = 192
HIT_FRAME = 256
TIERS = 4
LENGTHS = (32, 64, 96, 128)
FRAMES = 15         # game frames: C&C3 runs its particles at 30 Hz, two to a game frame
MUZZLE_FRAMES = 5
THREADS = [(1, 0.0, 1.0), (1, 2.1, 0.85), (2, 4.2, 0.7)]   # cycles per cell, phase, share of the tier's amplitude

CORE_K = [(0, (1, 1, 1)), (.5, (1, 1, 1)), (1, (0, 0, 0))]
THREAD_K = [(0, (1, 1, 1)), (.25, (.12549, .278431, 1)), (.5, (.117647, .219608, .466667)), (.9, (0, 0, 0)),
            (1, (0, 0, 0))]
FLASH_K = [(0, (1, 1, 1)), (.33, (.517647, .6, 1)), (.66, (.258824, .643137, .486275)), (1, (0, 0, 0))]
GLOW_K = [(0, (.72549, .8, .858824)), (.5, (.470588, .717647, .772549)), (1, (0, 0, 0))]
SPARK_K = [(0, (.552941, .705882, .796078)), (.5, (.203922, .301961, .345098)), (1, (0, 0, 0))]


def texture(name):
    return np.asarray(Image.open(os.path.join(TEX, name + ".png")).convert("RGB"), np.float32) / 255.0


T_THREAD = texture("FXRailgunThread")
T_FLARE = texture("FXLenzFlare01")
T_BLAST = texture("FXFireBlast04")


def keys(k, age):
    """A colour keyframe list [(age 0..1, rgb)] read at age."""
    for (a0, c0), (a1, c1) in zip(k, k[1:]):
        if age <= a1:
            f = 0 if a1 == a0 else (age - a0) / (a1 - a0)
            return np.array(c0) * (1 - f) + np.array(c1) * f
    return np.array(k[-1][1])


def bilinear(t, u, v, wrap_v=True):
    h, w, _ = t.shape
    x = np.clip(u, 0, 1) * (w - 1)
    y = (v % 1.0 if wrap_v else np.clip(v, 0, 1)) * (h - 1)
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    x1, y1 = np.minimum(x0 + 1, w - 1), np.minimum(y0 + 1, h - 1)
    fx, fy = (x - x0)[..., None], (y - y0)[..., None]
    return (t[y0, x0] * (1 - fx) * (1 - fy) + t[y0, x1] * fx * (1 - fy)
            + t[y1, x0] * (1 - fx) * fy + t[y1, x1] * fx * fy)


def streak(acc, pts, width, colour, v_per_segment):
    """Adds a textured ribbon through pts (N x 2 px): the thread texture across it, along it per segment or whole."""
    H, W, _ = acc.shape
    x0 = int(max(pts[:, 0].min() - width, 0)); x1 = int(min(pts[:, 0].max() + width + 1, W))
    y0 = int(max(pts[:, 1].min() - width, 0)); y1 = int(min(pts[:, 1].max() + width + 1, H))
    if x1 <= x0 or y1 <= y0:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    best = np.full(xx.shape, 1e9, np.float32); bu = np.zeros_like(xx); bv = np.zeros_like(xx)
    n = len(pts) - 1
    for i in range(n):
        a, b = pts[i], pts[i + 1]
        d = b - a; L2 = float(d @ d) or 1e-6
        s = np.clip(((xx - a[0]) * d[0] + (yy - a[1]) * d[1]) / L2, 0, 1)
        px, py = a[0] + s * d[0], a[1] + s * d[1]
        nx, ny = -d[1] / math.sqrt(L2), d[0] / math.sqrt(L2)
        dist = np.hypot(xx - px, yy - py)
        m = dist < best
        best = np.where(m, dist, best)
        bu = np.where(m, (xx - px) * nx + (yy - py) * ny, bu)
        bv = np.where(m, s if v_per_segment else (i + s) / n, bv)
    c = bilinear(T_THREAD, bu / width + 0.5, bv) * np.array(colour, np.float32)
    acc[y0:y1, x0:x1] += np.where((best <= width / 2)[..., None], c, 0)


def sprite(acc, t, cx, cy, size, colour, angle=0.0):
    """Adds a rotated square texture of size px centred on (cx, cy)."""
    H, W, _ = acc.shape
    r = size * 0.75
    x0 = int(max(cx - r, 0)); x1 = int(min(cx + r + 1, W)); y0 = int(max(cy - r, 0)); y1 = int(min(cy + r + 1, H))
    if x1 <= x0 or y1 <= y0 or size <= 0:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    dx, dy = xx - cx, yy - cy
    ca, sa = math.cos(angle), math.sin(angle)
    u = (dx * ca + dy * sa) / size + 0.5
    v = (-dx * sa + dy * ca) / size + 0.5
    ok = (u >= 0) & (u <= 1) & (v >= 0) & (v <= 1)
    acc[y0:y1, x0:x1] += np.where(ok[..., None], bilinear(t, u, v, wrap_v=False) * np.array(colour, np.float32), 0)


def bake(acc, size):
    """Additive light to straight-alpha RGBA at size px (alpha = the brightest channel)."""
    acc = np.clip(acc, 0, 1)
    a = acc.max(axis=2, keepdims=True)
    pm = Image.fromarray((np.concatenate([acc, a], 2) * 255).astype(np.uint8), "RGBA").resize((size, size),
                                                                                             Image.LANCZOS)
    pm = np.asarray(pm, np.float32) / 255
    al = pm[..., 3:]
    st = np.where(al > 1e-3, pm[..., :3] / np.maximum(al, 1e-3), 0)
    return Image.fromarray((np.concatenate([st, al], 2).clip(0, 1) * 255).astype(np.uint8), "RGBA")


def segment(t, tier, length):
    """One beam piece at C&C3 frame t: from x = -SEG/2 for length px, threads at the tier's strength."""
    acc = np.zeros((SEG_FRAME * SS, SEG_FRAME * SS, 3), np.float32)
    x0 = (SEG_FRAME / 2 - SEG / 2) * SS
    y = SEG_FRAME / 2 * SS
    px = UNIT * SS
    if t < 25:
        streak(acc, np.array([[x0, y], [x0 + length * SS, y]]), (1 + .1 * t) * px, keys(CORE_K, t / 25), False)
    if t < 30:
        amp = 12.5 * (tier + 1) / TIERS * px
        s = np.linspace(0, length / SEG, int(round(12 * length / SEG)) + 1)
        for cycles, phase, share in THREADS:
            off = amp * share * np.sin(2 * math.pi * cycles * s + phase)
            streak(acc, np.stack([x0 + s * SEG * SS, y + off], 1), (1 + .1 * t) * px, keys(THREAD_K, t / 30), True)
    return bake(acc, SEG_FRAME)


def muzzle(t, rng):
    acc = np.zeros((SEG_FRAME * SS, SEG_FRAME * SS, 3), np.float32)
    c = SEG_FRAME / 2 * SS
    size = rng["flash"] + sum(rng["damp"] ** k for k in range(t))
    sprite(acc, T_FLARE, c, c, size * UNIT * SS, keys(FLASH_K, t / 10), math.radians(rng["angle"]))
    return bake(acc, SEG_FRAME)


def impact(t, glows, sparks):
    """The hit at the frame centre, the shot arriving from the west, sparks thrown back west."""
    acc = np.zeros((HIT_FRAME * SS, HIT_FRAME * SS, 3), np.float32)
    c = HIT_FRAME / 2 * SS
    px = UNIT * SS
    for g in glows:
        sprite(acc, T_BLAST, c, c, max(g[0] - .5 * t, 0) * px, keys(GLOW_K, t / 30), g[1] + g[2] * t)
    if t < 5:
        for vx, vy, damp, size, shade in sparks:
            pos, vel, trail = np.zeros(2), np.array([vx, vy]), [np.zeros(2)]
            for _ in range(t + 1):
                pos = pos + vel; vel = vel * damp; trail.append(pos.copy())
            pts = np.array([[c - p[0] * px, c + p[1] * px] for p in trail[-6:]])
            if np.hypot(*(pts[-1] - pts[0])) > 1:
                streak(acc, pts, size * px * .5, np.clip(keys(SPARK_K, t / 5) + shade, 0, None), False)
    return bake(acc, HIT_FRAME)


def write_zip(name, frames):
    """Full square frames, never cropped: a rotated anim is clipped to its unrotated frame
    (docs/launcher-render-contracts.md)."""
    path = asset_packs.art_zip(name, "VFX")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    low = name.lower()
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for i, img in enumerate(frames):
            buf = io.BytesIO()
            img.save(buf, format="TGA")
            z.writestr(f"{low}-{i:04d}.tga", buf.getvalue())
            z.writestr(f"{low}-{i:04d}.meta", json.dumps({"size": [img.width, img.height],
                                                          "crop": [0, 0, img.width, img.height]}))
    patch_tileset(asset_packs.tileset_xml(name, "VFX"), name, len(frames))
    print(f"wrote {path} ({len(frames)} frames)")


def main():
    rng = np.random.default_rng(7)
    segs = [segment(2 * f, tier, length) for tier in range(TIERS) for length in LENGTHS for f in range(FRAMES)]
    write_zip("C3RAILSEG", segs)
    flash = {"flash": rng.uniform(15, 25), "damp": rng.uniform(.95, .99), "angle": rng.uniform(-7, 7)}
    write_zip("C3RAILMZ", [muzzle(2 * f, flash) for f in range(MUZZLE_FRAMES)])
    glows = [(rng.uniform(20, 30), rng.uniform(0, 7), rng.uniform(-.1, .1)) for _ in range(8)]
    sparks = [(rng.uniform(10, 30), rng.uniform(-5, 5), rng.uniform(.65, .8), rng.uniform(2, 5),
               rng.uniform(-50, 50) / 255) for _ in range(20)]
    write_zip("C3RAILHIT", [impact(2 * f, glows, sparks) for f in range(FRAMES)])


if __name__ == "__main__":
    main()
