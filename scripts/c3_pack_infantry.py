#!/usr/bin/env python3
"""Package C&C3 infantry, each as a single soldier and as a squad: GDI's Rifleman (C3RIFLE, C3RIFLESQ) from
Tiberium Wars, and from Kane's Wrath Nod's Militant (C3MILIT, C3MILITSQ; Kane's Wrath's remade model) and Cyborg
(C3CYBORG, C3CYBORGSQ).

Tileset layout per unit (292 tiles): Tiberian Sun's light infantry (idata.cpp TsE1DoControls, TS art.ini
[E1Sequence]), 8 facings CCW from north where a sequence turns with the soldier:
  0-7 ready, 8-55 walk (6 a facing), 56-70 idle1, 71-84 idle2 (85 repeats its last), 86-133 crawl (6),
  134-148 die1, 149-163 die2, 164-211 fire (6), 212-259 fire prone (6), 260-275 down (2), 276-291 up (2).
Idles and deaths face south, toward the camera. Frames sit on the TS infantry's 267 x 208 canvas with the feet
on its line (6 px below the centre), at the C&C3 tanks' scale (32 C&C3 units a cell), and carry EA's drop shadow.
Each soldier's diffuse sheet is lifted to the tanks' brightness first (TARGET_LUM).

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
from ts_reshadow import drop_shadow  # noqa: E402

ART = tanks.ART
RENDER_PPU = 12.0
PACK_PPU = 4.0
RENDER_CANVAS = 900
CANVAS = (267, 208)
FEET = (133.5, 110)
SHADOW = (1, 4)  # EA's vehicle drop shadow, (2, 6) at 8 px a classic px, at the infantry's 16/3
SOUTH = 4
# Mean diffuse luminance the infantry sheets are lifted to: the C&C3 tanks' sheets sit at 85 to 103, the infantry's
# at 35 to 50, which C&C3's own lighting brightens and the TS voxel ramp does not.
TARGET_LUM = 85.0

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


def lifted(m):
    """The model with its diffuse sheet gamma-lifted to TARGET_LUM mean luminance (darks rise, highlights hold)."""
    rgb = m.body[..., :3] / 255.0
    mean = float((rgb @ c3_render.LUMA).mean())
    if mean <= 0 or mean * 255.0 >= TARGET_LUM:
        return m
    g = np.log(TARGET_LUM / 255.0) / np.log(mean)
    m.body = m.body.copy()
    m.body[..., :3] = np.power(rgb, g) * 255.0
    m.sheets[0] = (m.body, m.sheets[0][1], m.sheets[0][2])
    m.team_means[0] = m._team_mean(m.body, m.sheets[0][1])
    return m


def render_shape(args):
    model, pose, facing = args
    path = f"{ART}/renders/inf_{model}/pose{pose:03d}-f{facing}.png"
    if os.path.exists(path):
        return path
    m = lifted(c3_render.Model(f"{ART}/infantry/{model}.npz"))
    d = np.load(f"{ART}/infantry/{model}.npz")
    m.pos, m.nrm = d["poses_pos"][pose], d["poses_nrm"][pose]
    m.hull_centre = np.zeros(3)
    img = c3_render.render(m, 90.0 + facing * 45.0, "hull", RENDER_PPU, RENDER_CANVAS, 32.0)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return path


def framed(path):
    im = Image.open(path).convert("RGBA")
    f = PACK_PPU / RENDER_PPU
    im = im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
    x, y = round(FEET[0] - im.width / 2), round(FEET[1] - im.height / 2)
    b = im.getbbox()
    if b and (x + b[0] < 0 or y + b[1] < 0 or x + b[2] > CANVAS[0] - SHADOW[0] or y + b[3] > CANVAS[1] - SHADOW[1]):
        raise SystemExit(f"{path}: content clipped by the {CANVAS} canvas")
    fr = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    fr.alpha_composite(im, (max(x, 0), max(y, 0)), (max(-x, 0), max(-y, 0)))
    return drop_shadow(fr, *SHADOW)


def pack(name, model, cameo):
    jobs = shape_jobs(model)
    with multiprocessing.Pool(8) as pool:
        paths = pool.map(render_shape, [(model, p, f) for _, p, f in jobs])
    by_shape = dict(zip([s for s, _, _ in jobs], paths))
    numbers = sorted(by_shape)
    tanks.write_zip(asset_packs.art_zip(name, "UNITS"), name.lower(), [framed(by_shape[s]) for s in numbers],
                    numbers=numbers)
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
