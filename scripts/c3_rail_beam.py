#!/usr/bin/env python3
"""Render C&C3's railgun shot (FX_RailGunFire, FX_RailGunHit) as HD anim frames for the railguns.

C&C3 draws the shot as a core in a glow, a flare at the muzzle and a bloom with sparks at the impact
(docs/cnc3-railgun-beam.md); here every piece is in its core line's colour. The launcher draws an exported sprite
unrotated, so every piece is round and TF_Railgun_Beam lays glow dots along the core line. The launcher blends straight
alpha only, so the additive light is baked into RGBA.

  C3RAILGLOW  the core's blue glow, a soft dot on 64 px, 12 frames.
  C3RAILMZ    the muzzle flash, 5 frames on 192 px.
  C3RAILHIT   the impact bloom with sparks thrown all round, 12 frames on 256 px.
  C3RAILGLOWO, C3RAILMZO, C3RAILHITO: the same in the Ghost Stalker's orange.

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
GLOW_FRAME, MUZZLE_FRAME, HIT_FRAME = 64, 192, 256
FRAMES = 12         # game frames: the core blazes for about a third of a second, then fades
MUZZLE_FRAMES = 5
GLOW_PX = 34

# Game-frame keys (age 0..1 over FRAMES) per set, each in its core line's colour: the blue of palette 0x0A, and the
# orange of TS [SmallRailgunSys] LaserColor=255,128,0 (the Ghost Stalker, names suffixed O).
SETS = {
    "": {"halo": [(0, (.35, .55, 1)), (.35, (.3, .5, 1)), (.7, (0, 0, 0)), (1, (0, 0, 0))],
         "flash": [(0, (.65, .7, 1)), (.5, (.45, .5, 1)), (1, (0, 0, 0))],
         "glow": [(0, (.65, .7, 1)), (.4, (.45, .5, 1)), (1, (0, 0, 0))],
         "spark": [(0, (.55, .62, 1)), (.5, (.3, .38, .8)), (1, (0, 0, 0))]},
    "O": {"halo": [(0, (1, .5, .1)), (.35, (1, .45, .05)), (.7, (0, 0, 0)), (1, (0, 0, 0))],
          "flash": [(0, (1, .68, .3)), (.5, (1, .5, .1)), (1, (0, 0, 0))],
          "glow": [(0, (1, .68, .3)), (.4, (1, .5, .1)), (1, (0, 0, 0))],
          "spark": [(0, (1, .48, .1)), (.5, (.8, .32, .03)), (1, (0, 0, 0))]},
}


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
    """Additive light to straight-alpha RGBA at size px (alpha = the brightest channel); overbright light keeps its hue."""
    acc = acc / np.maximum(acc.max(axis=2, keepdims=True), 1.0)
    a = acc.max(axis=2, keepdims=True)
    pm = Image.fromarray((np.concatenate([acc, a], 2) * 255).astype(np.uint8), "RGBA").resize((size, size),
                                                                                             Image.LANCZOS)
    pm = np.asarray(pm, np.float32) / 255
    al = pm[..., 3:]
    st = np.where(al > 1e-3, pm[..., :3] / np.maximum(al, 1e-3), 0)
    return Image.fromarray((np.concatenate([st, al], 2).clip(0, 1) * 255).astype(np.uint8), "RGBA")


def dot(f, size, px, colour_keys, gain):
    """A soft round dot px wide at game frame f, centred on a size px frame."""
    acc = np.zeros((size * SS, size * SS, 3), np.float32)
    yy, xx = np.mgrid[0:size * SS, 0:size * SS].astype(np.float32)
    r = np.hypot(xx - size * SS / 2, yy - size * SS / 2) / (px * SS / 2)
    acc += (np.exp(-4.0 * r ** 2)[..., None] * keys(colour_keys, f / FRAMES) * gain).astype(np.float32)
    return bake(acc, size)


def muzzle(f, rng, flash_keys):
    acc = np.zeros((MUZZLE_FRAME * SS, MUZZLE_FRAME * SS, 3), np.float32)
    c = MUZZLE_FRAME / 2 * SS
    size = rng["flash"] + 2 * f
    sprite(acc, T_FLARE, c, c, size * UNIT * SS, keys(flash_keys, f / MUZZLE_FRAMES), math.radians(rng["angle"]))
    return bake(acc, MUZZLE_FRAME)


def impact(f, glows, sparks, glow_keys, spark_keys):
    """The hit at the frame centre, its sparks thrown all round so it needs no turning."""
    acc = np.zeros((HIT_FRAME * SS, HIT_FRAME * SS, 3), np.float32)
    c = HIT_FRAME / 2 * SS
    px = UNIT * SS
    t = 2 * f
    for g in glows:
        sprite(acc, T_BLAST, c, c, max(g[0] - t, 0) * px, keys(glow_keys, f / FRAMES), g[1] + g[2] * t)
    if t < 5:
        for vx, vy, damp, size, shade in sparks:
            pos, vel, trail = np.zeros(2), np.array([vx, vy]), [np.zeros(2)]
            for _ in range(t + 1):
                pos = pos + vel; vel = vel * damp; trail.append(pos.copy())
            pts = np.array([[c + p[0] * px, c + p[1] * px] for p in trail[-6:]])
            if np.hypot(*(pts[-1] - pts[0])) > 1:
                streak(acc, pts, size * px * .5, np.clip(keys(spark_keys, t / 5) + shade, 0, None), False)
    return bake(acc, HIT_FRAME)


def write_zip(name, frames):
    """Full frames, uncropped: each anim is drawn centred on its point."""
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
    flash = {"flash": rng.uniform(22, 30), "angle": rng.uniform(-7, 7)}
    glows = [(rng.uniform(32, 48), rng.uniform(0, 7), rng.uniform(-.1, .1)) for _ in range(8)]
    sparks = []
    for _ in range(20):
        a, v = rng.uniform(0, 2 * math.pi), rng.uniform(10, 30)
        sparks.append((v * math.cos(a), v * math.sin(a), rng.uniform(.65, .8), rng.uniform(2, 5),
                       rng.uniform(-50, 50) / 255))
    for suffix, k in SETS.items():
        write_zip("C3RAILGLOW" + suffix, [dot(f, GLOW_FRAME, GLOW_PX, k["halo"], 1.0) for f in range(FRAMES)])
        write_zip("C3RAILMZ" + suffix, [muzzle(f, flash, k["flash"]) for f in range(MUZZLE_FRAMES)])
        write_zip("C3RAILHIT" + suffix, [impact(f, glows, sparks, k["glow"], k["spark"]) for f in range(FRAMES)])


if __name__ == "__main__":
    main()
