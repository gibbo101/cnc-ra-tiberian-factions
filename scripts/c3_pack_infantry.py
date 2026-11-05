#!/usr/bin/env python3
"""Package C&C3 infantry, each as a single soldier and as a squad: GDI's Rifleman (C3RIFLE, C3RIFLESQ) from
Tiberium Wars, and from Kane's Wrath Nod's Militant (C3MILIT, C3MILITSQ; Kane's Wrath's remade model) and Cyborg
(C3CYBORG, C3CYBORGSQ).

Tileset layout per unit (292 tiles): Tiberian Sun's light infantry (idata.cpp TsE1DoControls, TS art.ini
[E1Sequence]), 8 facings CCW from north where a sequence turns with the soldier:
  0-7 ready, 8-55 walk (6 a facing), 56-70 idle1, 71-84 idle2 (85 repeats its last), 86-133 crawl (6),
  134-148 die1, 149-163 die2, 164-211 fire (6), 212-259 fire prone (6), 260-275 down (2), 276-291 up (2).
Idles and deaths face south, toward the camera. Frames sit on the TS infantry's 267 x 208 canvas with the feet
on TSE1's line, scaled to TF's TS infantry height, each over its own shadow cast along the
render light onto the ground. Each soldier's team colour is raised to the TS infantry's (TEAM_BOOST), and his frames
are exposed to their brightness (TS_LUM_MEAN).

Inputs (set C3_ART_DIR): infantry/<unit>.npz and infantry/<unit>_squad.npz from tools/cnc3/c3_extract_infantry.py
(workspace), cameo/<NAME>.png for each single soldier, and audio/<model>/<C&C3 name>.wav from
tools/cnc3/c3_extract_audio.py. Audio: each soldier's crew voices and gunfire, as the tanks' (c3_pack_tanks.py).
Usage: c3_pack_infantry.py [NAME ...]; with no names, all of them.

License: GPL v3.
"""
import multiprocessing
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import asset_packs  # noqa: E402
import c3_pack_tanks as tanks  # noqa: E402
import c3_render  # noqa: E402

ART = tanks.ART
RENDER_PPU = 12.0
# TF's TS infantry stand about 61 px tall, the C&C3 Rifleman 52 at the tanks' 4 px a C&C3 unit.
PACK_PPU = 4.7
RENDER_CANVAS = 900
CANVAS = (267, 208)
FEET = (133.5, 103)  # the ground point; the feet's lowest pixels then sit where TSE1's do (about y 109)
# The cast shadow's opacity: TF's TS infantry shadows sit at a median alpha of about 90.
SHADOW_ALPHA = 0.36
# Team colour level over the tanks': the TS infantry's team green has a median G of about 120, the C&C3 soldiers'
# 85 at the tanks' level.
TEAM_BOOST = 1.45
SOUTH = 4
# Mean luminance over the body pixels of TF's TS infantry (TSE1, TSE2, TSGHOST), which each soldier's frames are
# exposed to; above KNEE, colour rolls off toward white instead of clipping.
TS_LUM_MEAN = 63.9
KNEE = 200.0

# name, model file, cameo (None: the squad keeps its single soldier's)
INFANTRY = (
    ("C3RIFLE", "rifleman", "C3RIFLE"),
    ("C3RIFLESQ", "rifleman_squad", None),
    ("C3MILIT", "militant", "C3MILIT"),
    ("C3MILITSQ", "militant_squad", None),
    ("C3CYBORG", "cyborg", "C3CYBORG"),
    ("C3CYBORGSQ", "cyborg_squad", None),
)
# (sequence, first shape, poses a facing, directional) in shape order
LAYOUT = (("ready", 0, 1, True), ("walk", 8, 6, True), ("idle1", 56, 15, False), ("idle2", 71, 14, False),
          ("crawl", 86, 6, True), ("die1", 134, 15, False), ("die2", 149, 15, False), ("fire", 164, 6, True),
          ("fireprone", 212, 6, True), ("down", 260, 2, True), ("up", 276, 2, True))
SHAPES = 292


def _takes(stem, model, sample, letters):
    """One sound event per take letter: C3<stem><LETTER> plays <sample><letter>."""
    return [(f"{stem}{c}", model, [f"{sample}{c.lower()}"]) for c in letters]


# VOC stem -> (model, C&C3 sample names), every stem listed in asset_packs.PACK_ONLY_SOUNDS. The squads speak and
# fire with their soldier's sounds.
SOUNDS = (
    _takes("C3LSE", "rifleman", "GURifle_VoiSelect", "ABCDEF")
    + _takes("C3LMO", "rifleman", "GURifle_VoiMove", "ABCDEFGHI")
    + _takes("C3LAT", "rifleman", "GURifle_VoiAttack", "ABCDEFGH")
    + [("C3LGUN", "rifleman", [f"GURifle_gun5Fire{c}" for c in "abcdefghij"])]
    + _takes("C3YSE", "cyborg", "NUCyInf_VoiSelect", "ABCDEFGHIJ")
    + _takes("C3YMO", "cyborg", "NUCyInf_VoiMove", "ABCDEFGHI")
    + _takes("C3YAT", "cyborg", "NUCyInf_VoiAttack", "ABCDEFGHI")
    + [("C3YGUN", "cyborg", [f"NUAwake_gunFire{c}" for c in "abcde"])]
    + _takes("C3NSE", "militant", "NUMilit_VoiSelect", "ABCDEFG")
    + _takes("C3NMO", "militant", "NUMilit_VoiMove", "ABCDEFGHIJK")
    + _takes("C3NAT", "militant", "NUMilit_VoiAttack", "ABCDEFG")
    + [("C3NGUN", "militant", [f"NURifle_gunFire2{c}" for c in "abcdefg"])]
)
SFX_BEGIN = "  <!-- BEGIN C&C3 infantry sounds (scripts/c3_pack_infantry.py) -->"
SFX_END = "  <!-- END C&C3 infantry sounds -->"


def shape_jobs(model):
    """(shape, pose, facing) for every shape the layout fills, and the shape 85 repeat."""
    d = np.load(f"{ART}/infantry/{model}.npz")
    start = dict(zip(d["seq_names"], d["seq_start"]))
    jobs = []
    for seq, first, count, directional in LAYOUT:
        for f in range(8 if directional else 1):
            for i in range(count):
                jobs.append((first + f * count + i, int(start[seq]) + i, f if directional else SOUTH))
    return jobs


def bled(body):
    """The sheet with each transparent texel's colour filled from its opaque neighbours, so edges never sample black."""
    out = body.copy()
    solid = out[..., 3] >= 128
    for _ in range(32):
        if solid.all():
            break
        acc = np.zeros(out.shape[:2] + (3,))
        cnt = np.zeros(out.shape[:2])
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            s = np.roll(solid, (dy, dx), (0, 1))
            acc += np.roll(out[..., :3], (dy, dx), (0, 1)) * s[..., None]
            cnt += s
        grow = ~solid & (cnt > 0)
        out[grow, :3] = acc[grow] / cnt[grow, None]
        solid = solid | grow
    return out


def prepared(m):
    """The model with its diffuse sheet bled into its transparent texels and its team colour raised (TEAM_BOOST)."""
    m.body = bled(m.body)
    m.sheets[0] = (m.body, m.sheets[0][1], m.sheets[0][2])
    m.team_means[0] = m._team_mean(m.body, m.sheets[0][1]) / TEAM_BOOST
    return m


def render_shape(args):
    """The soldier at a pose and facing, and his shadow cast along the render light onto the ground: two PNG paths."""
    model, pose, facing = args
    path = f"{ART}/renders/inf_{model}/pose{pose:03d}-f{facing}.png"
    shadow = path[:-4] + "-shadow.png"
    if os.path.exists(path) and os.path.exists(shadow):
        return path, shadow
    m = prepared(c3_render.Model(f"{ART}/infantry/{model}.npz"))
    d = np.load(f"{ART}/infantry/{model}.npz")
    m.pos, m.nrm = d["poses_pos"][pose], d["poses_nrm"][pose]
    m.hull_centre = np.zeros(3)
    yaw = 90.0 + facing * 45.0
    os.makedirs(os.path.dirname(path), exist_ok=True)
    c3_render.render(m, yaw, "hull", RENDER_PPU, RENDER_CANVAS, 32.0).save(path)
    a = np.radians(yaw)
    light = np.array([[np.cos(a), np.sin(a), 0], [-np.sin(a), np.cos(a), 0], [0, 0, 1]]) @ c3_render.LIGHT
    pos = m.pos.copy()
    m.pos = pos - light[None, :] * (np.maximum(pos[:, 2], 0) / light[2])[:, None]
    m.pos[:, 2] = 0.0
    c3_render.render(m, yaw, "hull", RENDER_PPU, RENDER_CANVAS, 32.0).getchannel("A").save(shadow)
    return path, shadow


def placed(path):
    """The render (or shadow mask) scaled to the pack and placed on the canvas with its feet on the line."""
    im = Image.open(path)
    im = im.convert("RGBA") if im.mode != "L" else Image.merge("RGBA", (im, im, im, im))
    f = PACK_PPU / RENDER_PPU
    im = im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
    x, y = round(FEET[0] - im.width / 2), round(FEET[1] - im.height / 2)
    b = im.getbbox()
    if b and (x + b[0] < 0 or y + b[1] < 0 or x + b[2] > CANVAS[0] or y + b[3] > CANVAS[1]):
        raise SystemExit(f"{path}: content clipped by the {CANVAS} canvas")
    fr = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    fr.alpha_composite(im, (max(x, 0), max(y, 0)), (max(-x, 0), max(-y, 0)))
    return fr


def toned(frames, shadows):
    """The frames exposed by one factor that takes the body pixels' mean luminance over every frame to the TS
    infantry's, so darks stay dark and colours keep their saturation; each laid over its cast shadow."""
    arrs = [np.asarray(f).astype(np.float32) for f in frames]
    body = np.concatenate([a[a[..., 3] > 250][:, :3] for a in arrs])
    k = TS_LUM_MEAN / max(float((body @ c3_render.LUMA).mean()), 1.0)
    out = []
    for a, sh in zip(arrs, shadows):
        a = a.copy()
        x = a[..., :3] * k
        x = np.where(x > KNEE, KNEE + (255.0 - KNEE) * (1 - np.exp(-(x - KNEE) / (255.0 - KNEE))), x)
        a[..., :3] = x * (a[..., 3:] > 0)
        under = np.zeros_like(a)
        under[..., 3] = np.asarray(sh)[..., 3].astype(np.float32) * SHADOW_ALPHA
        fr = Image.fromarray(under.astype(np.uint8), "RGBA")
        fr.alpha_composite(Image.fromarray(a.astype(np.uint8), "RGBA"))
        out.append(fr)
    return out


def pack(name, model, cameo):
    jobs = shape_jobs(model)
    with multiprocessing.Pool(8) as pool:
        paths = pool.map(render_shape, [(model, p, f) for _, p, f in jobs])
    by_shape = dict(zip([s for s, _, _ in jobs], paths))
    numbers = sorted(by_shape)
    frames = toned([placed(by_shape[s][0]) for s in numbers], [placed(by_shape[s][1]) for s in numbers])
    tanks.write_zip(asset_packs.art_zip(name, "UNITS"), name.lower(), frames, numbers=numbers)
    sub = name.lower()
    tiles = [f"{sub}\\{sub}-{(s if s in by_shape else s - 1):04d}.tga" for s in range(SHAPES)]
    tanks.patch_tileset(name, SHAPES, tiles)
    if cameo:
        tanks.write_cameo(cameo)


def main(names):
    if not ART:
        raise SystemExit("set C3_ART_DIR (holding infantry/, cameo/)")
    for name, model, cameo in INFANTRY:
        if not names or name in names:
            pack(name, model, cameo)
    tanks.write_audio({m.split("_")[0] for n, m, _ in INFANTRY if n in names} if names else None, SOUNDS, SFX_BEGIN,
                      SFX_END)


if __name__ == "__main__":
    main(sys.argv[1:])
