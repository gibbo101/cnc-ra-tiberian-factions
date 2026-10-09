#!/usr/bin/env python3
"""Pack the HD TS GDI Component Tower (resources/custom-art/ts-gdi-component-tower-hd).

The source frames are already on the tower family's 176x320 canvas with the cell's centre
on the canvas centre, so they ship as drawn. Frame sets written to the TS-HD-Graphics-Pack
(TSHD_STRUCTURES.XML patched; ts_pack_towers.write_zip routes each name by asset_packs.py):

  TSCTWR       2    healthy, damaged
  TSCTWRMAKE   17   build-up
  TSVULCT / TSROCKT / TSCSAMT
               128  the turret alone, in the TDGUN layout Shape_Number expects (32 facings x
                    {idle, recoil, damaged idle, damaged recoil}), from the HD turrets in
                    resources/custom-art/ts-tower-turrets-hd (drawn in place on the tower's
                    canvas; the RPG and SAM have no recoil pose, so their idle frame stands in).
                    The engine draws it after every other layer, so couplings and links sit
                    behind it
  TSCTWRX      50   the layers the engine draws over any tower of the family
                    (BuildingClass::Draw_It):
                      0-7    wall coupling, side N/E/S/W x {healthy, damaged}
                      8-13   south wall end, wall gdi/nod/brik x {healthy, damaged}
                      14-19  north wall end, same order, with the tower's own pixels cut out:
                             it belongs behind the tower but draws after it
                      20-25  the lamps by the south-east door (TS GACTWR_A) and the south-west one
                      26-41  link to a finished tower on side N/E/S/W, x this tower's state
                             x that tower's state (26 + side*4 + this*2 + other); both towers
                             draw it, and it replaces that side's coupling
                      42-49  connector to a gate's end on side N/E/S/W, x this tower's state
                             (42 + side*2 + state): the tower's half of a link, capped by its
                             flange on the cell edge (the art's src/ct_gatelink.py); it replaces
                             that side's coupling and wall end

The armed towers (TSVULC, TSROCK, TSCSAM) have no body art of their own: rules.ini gives them
Image=TSCTWR, and BuildingClass::Draw_It draws the bare tower's healthy or damaged frame under the turret.

The fire points come from the turret art's measured aim points (aim-<turret>-healthy.json) and
are written to redalert/tsctwr_muzzle.h, leptons from the building centre per turret frame, so the
art and the shot cannot drift apart.

Usage: ts_pack_ctwr_hd.py [--preview OUT.png]
License: GPL v3.
"""
import os, sys
import numpy as np
from PIL import Image

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS)
import json
import ts_pack_walls as W
import ts_pack_towers as T

SRC = os.path.join(SCRIPTS, "..", "resources", "custom-art", "ts-gdi-component-tower-hd")
TURRET_SRC = os.path.join(SCRIPTS, "..", "resources", "custom-art", "ts-tower-turrets-hd")
MUZZLE_H = os.path.join(SCRIPTS, "..", "redalert", "tsctwr_muzzle.h")
TURRETS = {"TSVULC": "vulcan", "TSROCK": "rpg", "TSCSAM": "sam"}
SIDES = "NESW"
WALLS = ("gdi", "nod", "brik")
STATES = 2          # healthy, damaged; the destroyed tower is never on the map
# The art is drawn on the 176x320 canvas; it ships padded to 192 wide so its classic stub (36x60)
# has an even width and the launcher's half-width offset lands on a whole pixel (an odd 33 drew
# the tower 2.7 px east of a gate's end). The padding moves nothing on screen.
SHIP_W = 192
# A tower's plot is its cell and the head's headroom cell above (bdata.cpp), so the launcher centres its art half
# a cell higher: every frame carries that much more canvas on top.
TOWER_PAD = 128
MAKE_FRAMES = 17
LAMP_FRAMES = 6


def load(*parts):
    img = Image.open(os.path.join(SRC, *parts)).convert("RGBA")
    if img.size != (T.CANVAS_W, T.CANVAS_H):
        raise SystemExit(f"{os.path.join(*parts)} is {img.size}, expected {T.CANVAS_W}x{T.CANVAS_H}")
    return img


def cut(piece, cover):
    """piece with every pixel the cover draws removed."""
    a = np.array(piece)
    a[np.array(cover)[:, :, 3] > 0] = 0
    return Image.fromarray(a)


def layers(bodies):
    out = []
    for side in SIDES:
        for s in range(STATES):
            out.append(load("couplings", f"coupling-{side}-{s:02d}.png"))
    for wall in WALLS:
        for s in range(STATES):
            out.append(load("ends", f"end-{wall}-S-{s:02d}.png"))
    for wall in WALLS:
        for s in range(STATES):
            out.append(cut(load("ends", f"end-{wall}-N-{s:02d}.png"), bodies[s]))
    # The lamp, and its mirror across the cell centre in the west door's slot: the body is symmetric.
    for i in range(LAMP_FRAMES):
        lamp = load("light", f"component-tower-light-{i:02d}.png")
        out.append(Image.alpha_composite(lamp, lamp.transpose(Image.FLIP_LEFT_RIGHT)))
    for side in SIDES:
        for s in range(STATES):
            for o in range(STATES):
                out.append(load("links", f"link-{side}-{s:02d}-{o:02d}.png"))
    for side in SIDES:
        for s in range(STATES):
            out.append(load("gatelinks", f"gatelink-{side}-{s:02d}.png"))
    return out


def turret_frame(name, state, f):
    """A turret frame; state 0-3 = idle, recoil, damaged idle, damaged recoil."""
    damaged = "damaged-" if state >= 2 else ""
    recoil = "recoil-" if state % 2 else ""
    path = os.path.join(TURRET_SRC, name, f"turret-{damaged}{recoil}{f:02d}.png")
    if not os.path.exists(path):
        path = os.path.join(TURRET_SRC, name, f"turret-{damaged}{f:02d}.png")
    img = Image.open(path).convert("RGBA")
    if img.size != (T.CANVAS_W, T.CANVAS_H):
        raise SystemExit(f"{path} is {img.size}, expected {T.CANVAS_W}x{T.CANVAS_H}")
    return img


def turrets(name):
    return [turret_frame(name, state, f) for state in range(4) for f in range(32)]


def overlap_report(extra):
    """Pixels where a turret and the lamp, the one layer drawn after it, would both paint."""
    worst = 0
    for name in TURRETS.values():
        for f in range(32):
            ta = np.array(turret_frame(name, 0, f))[:, :, 3] > 0
            for lay in extra[20:26]:
                worst = max(worst, int((ta & (np.array(lay)[:, :, 3] > 0)).sum()))
    print(f"  turret pixels under the lamp: {worst}")


def lep(point):
    """An aim point (canvas px, pixel-edge coordinates) as leptons east/south of the building
    centre, which sits at the canvas centre (2 leptons per px)."""
    x, y = point
    return (int(round((x - 0.5 - T.CANVAS_W / 2.0) * 2)), int(round((y - 0.5 - T.CANVAS_H / 2.0) * 2)))


def write_muzzles():
    """Per turret frame: the Vulcan's two muzzles, the RPG's two tube mouths, the SAM's launch face."""
    out = ["// Generated by scripts/ts_pack_ctwr_hd.py from the turret art's aim points -- do not edit.",
           "// Leptons east/south of the building centre, indexed by turret frame (0 = north, CCW).",
           "#pragma once", ""]
    for ini, name, points in (("TSVULC", "vulcan", 2), ("TSROCK", "rpg", 2), ("TSCSAM", "sam", 1)):
        aim = json.load(open(os.path.join(TURRET_SRC, f"aim-{name}-healthy.json")))
        out.append(f"static const short _{ini.lower()}_fire[32][{points}][2] = {{")
        for f in range(32):
            pts = ", ".join("{%d, %d}" % lep(p) for p in aim[str(f)][:points])
            out.append(f"    {{{pts}}},")
        out.append("};")
        out.append("")
    with open(MUZZLE_H, "w") as fh:
        fh.write("\n".join(out))
    print(f"wrote {MUZZLE_H}")


def write_zip(ini, frames, pad_top=0):
    """ts_pack_towers.write_zip on the SHIP_W canvas: each frame centred in it, pad_top px added above."""
    pad = (SHIP_W - T.CANVAS_W) // 2
    wide = []
    for f in frames:
        cv = Image.new("RGBA", (SHIP_W, T.CANVAS_H + pad_top), (0, 0, 0, 0))
        cv.paste(f, (pad, pad_top))
        wide.append(cv)
    w0, h0 = T.CANVAS_W, T.CANVAS_H
    T.CANVAS_W, T.CANVAS_H = SHIP_W, T.CANVAS_H + pad_top
    try:
        T.write_zip(ini, wide)
    finally:
        T.CANVAS_W, T.CANVAS_H = w0, h0


def pack():
    bodies = [load("tower", f"component-tower-{s:02d}.png") for s in range(STATES)]
    make = [load("build-up", f"component-tower-build-{i:02d}.png") for i in range(MAKE_FRAMES)]
    extra = layers(bodies)
    write_zip("TSCTWR", bodies, TOWER_PAD)
    write_zip("TSCTWRMAKE", make, TOWER_PAD)
    for ini, name in TURRETS.items():
        write_zip(ini + "T", turrets(name), TOWER_PAD)
    write_zip("TSCTWRX", extra, TOWER_PAD)
    dims = json.load(open(W.STUB_MANIFEST))
    for ini in ("TSCTWR",) + tuple(TURRETS):
        dims[ini] = [SHIP_W * 3 // 16, (T.CANVAS_H + TOWER_PAD) * 3 // 16]
    json.dump(dims, open(W.STUB_MANIFEST, "w"), indent=1)
    open(W.STUB_MANIFEST, "a").write("\n")
    write_muzzles()
    overlap_report(extra)


def preview(path):
    """The four towers healthy and damaged, each with a coupling on every side."""
    bodies = [load("tower", f"component-tower-{s:02d}.png") for s in range(STATES)]
    extra = layers(bodies)
    tiles = []
    for s in range(STATES):
        for name in (None,) + tuple(TURRETS.values()):
            cv = bodies[s].copy()
            for side in range(4):
                cv.alpha_composite(extra[side * STATES + s])
            if name is not None:
                cv.alpha_composite(turret_frame(name, 2 * s, 4))
            cv.alpha_composite(extra[20 + 1])
            tiles.append(cv)
    g = Image.new("RGBA", (len(tiles) // 2 * T.CANVAS_W, 2 * 200), (88, 96, 72, 255))
    for k, t in enumerate(tiles):
        g.alpha_composite(t.crop((0, 40, T.CANVAS_W, 240)), ((k % 4) * T.CANVAS_W, (k // 4) * 200))
    g.save(path)
    print("wrote", path)


if __name__ == "__main__":
    if "--preview" in sys.argv:
        preview(sys.argv[sys.argv.index("--preview") + 1])
    else:
        pack()
