#!/usr/bin/env python3
"""Pack the HD TS GDI Component Tower (resources/custom-art/ts-gdi-component-tower-hd).

The source frames are already on the tower family's 176x320 canvas with the cell's centre
on the canvas centre, so they ship as drawn. Frame sets written (RA_STRUCTURES.XML patched):

  TSCTWR       2    healthy, damaged
  TSCTWRMAKE   17   build-up (also written as each armed tower's <ini>MAKE)
  TSVULC / TSROCK / TSCSAM
               128  the armed tower's own frames, in the TDGUN layout Shape_Number expects
                    (32 facings x {idle, recoil, damaged idle, damaged recoil}): the body only
  TSVULCT / TSROCKT / TSCSAMT
               128  the turret alone, same layout: TS's own GTCTWR_B/_C/_D seated on the
                    platform ring (scripts/ts_pack_towers.py's turret code). The engine draws
                    it after every other layer, so couplings and links sit behind it
  TSCTWRX      26   the layers the engine draws over any tower of the family
                    (BuildingClass::Draw_It):
                      0-7    wall coupling, side N/E/S/W x {healthy, damaged}
                      8-13   south wall end, wall gdi/nod/brik x {healthy, damaged}
                      14-19  north wall end, same order, with the tower's own pixels cut out:
                             it belongs behind the tower but draws after it
                      20-25  the lamp by the south-east door (TS GACTWR_A)
                      26-41  link to a finished tower on side N/E/S/W, x this tower's state
                             x that tower's state (26 + side*4 + this*2 + other); both towers
                             draw it, and it replaces that side's coupling

The turret pivot, measured off the ring here, is written to redalert/tsctwr_seat.h for the
towers' fire points, so the art and the shot cannot drift apart.

Env: TS_ART_DIR  holds shp_gtctwr_b / _c / _d (TS's turret sprites, decoded against
                 UNITTEM.PAL by scripts/ts_rebuild_art.sh).
     TS_SEAT_DY  turret lift over the ring centre in TS px (default -1.5).
Usage: ts_pack_ctwr_hd.py [--preview OUT.png]
License: GPL v3.
"""
import os, sys
import numpy as np
from PIL import Image

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS)
# The turret sits down in this body's platform ring, its front rim showing: a smaller lift
# than TS's own body wants (ts_pack_towers.py TS_SEAT_DY).
os.environ.setdefault("TS_SEAT_DY", "-1.5")
import ts_pack_walls as W
import ts_pack_towers as T

SRC = os.path.join(SCRIPTS, "..", "resources", "custom-art", "ts-gdi-component-tower-hd")
SEAT_H = os.path.join(SCRIPTS, "..", "redalert", "tsctwr_seat.h")
SIDES = "NESW"
WALLS = ("gdi", "nod", "brik")
STATES = 2          # healthy, damaged; the destroyed tower is never on the map
MAKE_FRAMES = 17
LAMP_FRAMES = 6


def load(*parts):
    img = Image.open(os.path.join(SRC, *parts)).convert("RGBA")
    if img.size != (T.CANVAS_W, T.CANVAS_H):
        raise SystemExit(f"{os.path.join(*parts)} is {img.size}, expected {T.CANVAS_W}x{T.CANVAS_H}")
    return img


def seat(body):
    """Turret pivot on the canvas: the ring's centre lifted by TS's seat offset."""
    rx, ry, rw = T.ring_of(body)
    k = rw / T.TS_RING_W
    return rx + T.TS_TURRET_OFFSET[0] * k, ry + T.TS_TURRET_OFFSET[1] * k


def with_turret(body, spr_pivot, bare=False):
    """The body with the turret seated on it, or with bare=True the turret alone on the canvas."""
    spr, pivot = spr_pivot
    px, py = seat(body)
    cv = Image.new("RGBA", body.size, (0, 0, 0, 0)) if bare else body.copy()
    cv.paste(spr, (int(round(px - pivot[0])), int(round(py - pivot[1]))), spr)
    return cv


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
    for i in range(LAMP_FRAMES):
        out.append(load("light", f"component-tower-light-{i:02d}.png"))
    for side in SIDES:
        for s in range(STATES):
            for o in range(STATES):
                out.append(load("links", f"link-{side}-{s:02d}-{o:02d}.png"))
    return out


def armed(bodies):
    """The armed tower's body frames in the turret layout: the body for each state."""
    return [bodies[1 if state >= 2 else 0] for state in range(4) for f in range(32)]


def turrets(bodies, tdir):
    frames = []
    for state in range(4):
        dmg = state >= 2
        frames += [with_turret(bodies[1 if dmg else 0], T.turret(tdir, f, damaged=dmg, recoil=bool(state % 2)),
                               bare=True) for f in range(32)]
    return frames


def overlap_report(bodies, extra):
    """Pixels where a turret and the lamp, the one layer drawn after it, would both paint."""
    worst = 0
    for tdir in T.TURRETS.values():
        for f in range(32):
            ta = np.array(with_turret(bodies[0], T.turret(tdir, f), bare=True))[:, :, 3] > 0
            for lay in extra[20:26]:
                worst = max(worst, int((ta & (np.array(lay)[:, :, 3] > 0)).sum()))
    print(f"  turret pixels under the lamp: {worst}")


def write_seat(body):
    px, py = seat(body)
    east = px - T.CANVAS_W / 2.0
    north = T.CANVAS_H / 2.0 - py
    with open(SEAT_H, "w") as f:
        f.write("// Generated by scripts/ts_pack_ctwr_hd.py -- do not edit.\n")
        f.write("// Component tower turret pivot, canvas px from the building centre (2 leptons per px).\n")
        f.write("#pragma once\n")
        f.write(f"#define TSCTWR_PIVOT_EAST_PX {east:.1f}\n")
        f.write(f"#define TSCTWR_PIVOT_NORTH_PX {north:.1f}\n")
    print(f"wrote {SEAT_H} (pivot {east:+.1f} px east, {north:.1f} px north)")


def pack():
    bodies = [load("tower", f"component-tower-{s:02d}.png") for s in range(STATES)]
    make = [load("build-up", f"component-tower-build-{i:02d}.png") for i in range(MAKE_FRAMES)]
    extra = layers(bodies)
    T.write_zip("TSCTWR", bodies)
    T.write_zip("TSCTWRMAKE", make)
    for ini, tdir in T.TURRETS.items():
        T.write_zip(ini, armed(bodies))
        T.write_zip(ini + "T", turrets(bodies, tdir))
        T.write_zip(ini + "MAKE", make)
    T.write_zip("TSCTWRX", extra)
    write_seat(bodies[0])
    overlap_report(bodies, extra)


def preview(path):
    """The four towers healthy and damaged, each with a coupling on every side."""
    bodies = [load("tower", f"component-tower-{s:02d}.png") for s in range(STATES)]
    extra = layers(bodies)
    tiles = []
    for s in range(STATES):
        bases = [bodies[s]] + [with_turret(bodies[s], T.turret(d, 4, damaged=bool(s))) for d in T.TURRETS.values()]
        for b in bases:
            cv = b.copy()
            for side in range(4):
                cv.alpha_composite(extra[side * STATES + s])
            cv.alpha_composite(extra[20 + 1])
            tiles.append(cv)
    g = Image.new("RGBA", (len(tiles) // 2 * T.CANVAS_W, 2 * 200), (88, 96, 72, 255))
    for k, t in enumerate(tiles):
        g.alpha_composite(t.crop((0, 40, T.CANVAS_W, 240)), ((k % 4) * T.CANVAS_W, (k // 4) * 200))
    g.save(path)
    print("wrote", path)


if __name__ == "__main__":
    if not T.ART:
        raise SystemExit("set TS_ART_DIR to the directory holding shp_gtctwr_b/_c/_d")
    if "--preview" in sys.argv:
        preview(sys.argv[sys.argv.index("--preview") + 1])
    else:
        pack()
