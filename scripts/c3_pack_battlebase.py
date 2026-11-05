#!/usr/bin/env python3
"""Package the C&C3 Rig's deployed form, GDI's Battle Base, as a turret building in the layout of the dug-in Tick
Tank (bdata.cpp Shape_Number: 32 facings x {idle, recoil, damaged idle, damaged recoil}):
  C3BBASE      the base without its guns, healthy and damaged: 128 tiles, 64 of each
  C3BBASET     both cannons in 32 facings (CCW, 0 = N), drawn in place over the base: 128 tiles, the facings x 4
  C3BBASEMAKE  the deploy, 32 frames from the mobile Rig to the finished base; played backwards it packs up.
               At 2 ticks a frame it runs as long as C&C3's (3.37 s); a host sets that rate itself.

The base stands as the Rig left it, hull facing south (nose to the camera, the Tick's deploy facing), so both guns
sit beside the tower. Each gun turns about its own yaw pivot (TURRET_L, TURRET_R). The canvas is centred on the
Rig's ground point, at 128 px per cell (C&C3 units at 32 a cell, as the tanks), and its first deploy frame matches
the mobile Rig's sprite. Body and deploy frames carry EA's drop shadow; gun frames none.

Inputs (set C3_ART_DIR): rig_deploy/ and rig_deploy_whole/ (tools/cnc3/c3_extract_anim.py --all, without and with
--whole), and cameo/C3BBASE.png.
Usage: c3_pack_battlebase.py [render | pack]; with neither, both. Renders cache in $C3_ART_DIR/renders/bbase_*.

License: GPL v3.
"""
import json
import math
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
import unit_centring  # noqa: E402
from ts_reshadow import drop_shadow, EA_DX, EA_DY  # noqa: E402

ART = tanks.ART
RENDER_PPU = 9.0
PACK_PPU = 4.0  # 128 px a cell over the 32 C&C3 units a cell the tanks are packed at
RENDER_CANVAS = 1400
HULL_YAW = 270.0  # facing 16, south
DEPLOY_FRAMES = 101
MAKE_FRAMES = 32  # at 2 game ticks a frame, C&C3's 3.37 s deploy at the speed TF is played at
MAKE = [round(i * (DEPLOY_FRAMES - 1) / (MAKE_FRAMES - 1)) for i in range(MAKE_FRAMES)]
GUN_PIVOTS = ("TURRET_L", "TURRET_R")


def npz(whole, frame):
    return f"{ART}/rig_deploy{'_whole' if whole else ''}/rigdeploy-{frame:03d}.npz"


def out(kind, i):
    return f"{ART}/renders/bbase_{kind}/frame-{i:04d}.png"


def turned_guns(path, facing):
    """The deployed model with each gun turned about its own yaw pivot to point at the facing."""
    m = c3_render.Model(path)
    d = np.load(path)
    pivots = dict(zip(d["gun_pivot_names"], d["gun_pivot_pos"]))
    gun = m.part == 1
    piv = np.array([pivots[n][:2] for n in GUN_PIVOTS])
    nearest = np.argmin(((m.pos[:, None, :2] - piv[None]) ** 2).sum(2), 1)
    a = math.radians(90.0 + facing * 360.0 / 32 - HULL_YAW)
    rot = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
    pos = m.pos.copy()
    for g in range(len(GUN_PIVOTS)):
        sel = gun & (nearest == g)
        centre = np.array([*piv[g], 0.0])
        pos[sel] = (pos[sel] - centre) @ rot.T + centre
        for attr in ("nrm", "tan", "bin"):
            arr = getattr(m, attr).copy()
            arr[sel] = arr[sel] @ rot.T
            setattr(m, attr, arr)
    m.pos = pos
    return m


def render_one(job):
    kind, i = job
    path = out(kind, i)
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if kind == "make":
        m, part, stock = c3_render.Model(npz(True, MAKE[i])), "hull", False
    elif kind in ("body", "bodyd"):
        m, part, stock = c3_render.Model(npz(False, DEPLOY_FRAMES - 1), damaged=kind == "bodyd"), "hull", False
    else:
        m, part, stock = turned_guns(npz(False, DEPLOY_FRAMES - 1), i), "turret", True
    img = c3_render.render(m, HULL_YAW, part, RENDER_PPU, RENDER_CANVAS, tanks.ELEV_DEG,
                           turret_on_hull_origin=stock)
    img.save(path)


def jobs():
    return ([("body", 0), ("bodyd", 0)] + [("gun", i) for i in range(32)] + [("make", i) for i in range(len(MAKE))])


def render_all():
    with multiprocessing.Pool(tanks.RENDER_WORKERS) as pool:
        for n, _ in enumerate(pool.imap_unordered(render_one, jobs()), 1):
            print(f"rendered {n}/{len(jobs())}", flush=True)


def scaled(kind, i):
    return tanks.scaled(Image.open(out(kind, i)).convert("RGBA"), RENDER_PPU, PACK_PPU)


def rig_drop():
    """The Rig's art drop (unit_art_drop.json), in this canvas's pixels: the base moves with the Rig's sprite."""
    drops = json.load(open(unit_centring.DROPS_JSON))
    return round(drops["C3RIG"] / unit_centring.UNIT_DENSITY * unit_centring.BUILDING_DENSITY)


def canvas_size(images, drop):
    """The smallest canvas, in multiples of 32 px, that holds every frame and its shadow centred as rendered and
    moved down by the drop."""
    half_w = half_h = 0
    for im in images:
        x0, y0, x1, y1 = im.getbbox()
        cx, cy = im.width / 2, im.height / 2
        half_w = max(half_w, cx - x0, x1 + EA_DX - cx)
        half_h = max(half_h, cy - y0 - drop, y1 + EA_DY + drop - cy)
    return 32 * math.ceil(2 * half_w / 32), 32 * math.ceil(2 * half_h / 32)


def framed(im, size, shadow, drop):
    fr = Image.new("RGBA", size, (0, 0, 0, 0))
    fr.alpha_composite(im, (round(size[0] / 2 - im.width / 2), round(size[1] / 2 - im.height / 2) + drop))
    return drop_shadow(fr, EA_DX, EA_DY) if shadow else fr


def pack():
    body = [scaled("body", 0), scaled("bodyd", 0)]
    guns = [scaled("gun", i) for i in range(32)]
    make = [scaled("make", i) for i in range(len(MAKE))]
    drop = rig_drop()
    size = canvas_size(body + guns + make, drop)
    print(f"canvas {size[0]} x {size[1]}, the Rig's drop {drop} px")
    for name, frames, shadow, tiles in (
            ("C3BBASE", body, True, [0] * 64 + [1] * 64),
            ("C3BBASET", guns, False, list(range(32)) * 4),
            ("C3BBASEMAKE", make, True, list(range(len(MAKE))))):
        tanks.write_zip(asset_packs.art_zip(name, "STRUCTURES"), name.lower(),
                        [framed(f, size, shadow, drop) for f in frames])
        sub = name.lower()
        tanks.patch_tileset(name, len(tiles), [f"{sub}\\{sub}-{t:04d}.tga" for t in tiles], kind="STRUCTURES")
    tanks.write_cameo("C3BBASE")


if __name__ == "__main__":
    if not ART:
        raise SystemExit("set C3_ART_DIR (holding rig_deploy/, rig_deploy_whole/, cameo/)")
    step = sys.argv[1:] or ["render", "pack"]
    if "render" in step:
        render_all()
    if "pack" in step:
        pack()
