#!/usr/bin/env python3
"""Pack the C&C3 Scorpion Tank (C3SCORP) and its Laser Capacitor variant (C3SCORPLAS) for sign-off, outside the packs.

Both ZIPs take C3PRED's layout (hull 0-95: 32 facings x 3 tread steps; turret 96-127) and its packing, drop and
seat tables, through c3_pack_tanks.py and unit_centring.py. The laser hull carries the uncannoned body and the
tail mount, so C3SCORPLAS ships its own hull frames; its turret is the tail laser, seated on the TURRET2 bone.
Nothing here touches a tileset XML, c3tanks.h or the packs: the ZIPs, a cameo, the seat tables and a preview
sheet land in OUT.

Inputs (set C3_ART_DIR): model/scorpion{,_laser}.npz from tools/cnc3/c3_extract_model.py (workspace),
renders/scorpion{,_laser}_{hull,turret}/ from c3_render.py, cameo/C3SCORP.png.
Usage: c3_scorpion_preview.py <out dir>
License: GPL v3.
"""
import io
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import asset_packs  # noqa: E402
import c3_pack_tanks as P  # noqa: E402
import unit_centring as U  # noqa: E402

# name, model, ShapeSize, fire-point pivots per weapon
UNITS = (
    ("C3SCORP", "scorpion", 48, (("TURRETFX",),)),
    ("C3SCORPLAS", "scorpion_laser", 48, (("TURRETMS",),)),
)
TURRET = 96
SHEET_FACINGS = range(0, 32, 4)
BG = (96, 104, 88, 255)


def pack(out):
    """Each unit's ZIP in OUT, dropped by C3SCORP's hull offset as unit_centring.py drops the shipped tanks."""
    paths = {}
    for name, model, shape, _ in UNITS:
        canvas = shape * 8
        frames = [P.packed(f"{P.ART}/renders/{model}_hull/frame-{i:04d}.png", canvas, True)
                  for i in range(32 * P.TREAD_STEPS)]
        frames += [P.packed(f"{P.ART}/renders/{model}_turret/frame-{i:04d}.png", canvas, False)
                   for i in range(32)]
        paths[name] = os.path.join(out, f"{name}.ZIP")
        P.write_zip(paths[name], name.lower(), frames)
    _, data = U.read_zip(paths["C3SCORP"])
    offset = U.hull_offset(data, U.frame_names(data), TURRET)
    drop = -round(offset * U.UNIT_DENSITY)
    for path in paths.values():
        U.shift_zip(path, drop)
    print(f"hull offset {offset:+.2f} classic px: dropped {drop} canvas px")
    return paths, drop


def write_tables(out, drop):
    """The seat and fire tables as c3_pack_tanks.write_header emits them, to OUT only."""
    lines = [f"// C3SCORP / C3SCORPLAS preview tables (scripts/probes/c3_scorpion_preview.py); art drop {drop} canvas px.",
             "// By Dir_To_32 (CW, 0 = N). _seat_px classic px, _seat_lep leptons, _fire leptons from the seat.", ""]
    seats = {}
    for name, model, _, weapons in UNITS:
        seat, fire = P.tables(model, weapons)
        seats[name] = [(round(x / 8), round(y / 8)) for x, y in seat]
        low = name.lower()
        lines.append(f"static const signed char _{low}_seat_px[32][2] = {P.rows_c(seat, 1 / 8)};")
        lines.append(f"static const short _{low}_seat_lep[32][2] = {P.rows_c(seat, P.LEPTONS_PER_PX)};")
        lines.append(f"static const short _{low}_fire[1][1][32][2] = {{{{{P.rows_c(fire[0][0], P.LEPTONS_PER_PX)}}}}};")
        lines.append("")
    with open(os.path.join(out, "c3scorp_tables.h"), "w") as fh:
        fh.write("\n".join(lines))
    return seats


def on_canvas(image, meta):
    """A packed frame's cropped image put back on its full canvas."""
    meta = json.loads(meta)
    fr = Image.new("RGBA", tuple(meta["size"]), (0, 0, 0, 0))
    fr.alpha_composite(Image.open(io.BytesIO(image)).convert("RGBA"), tuple(meta["crop"][:2]))
    return fr


def frames_of(path):
    """Every frame of a packed ZIP on its full canvas, in member order."""
    _, data = U.read_zip(path)
    return [on_canvas(data[n], data[n[:-4] + ".meta"]) for n in U.frame_names(data)]


def predator():
    """The shipped C3PRED frames by shape, and its seats per hull frame from c3tanks.h."""
    _, data = U.read_zip(asset_packs.art_zip("C3PRED", "UNITS"))
    frames = [on_canvas(data[n], data[n[:-4] + ".meta"]) for n in U.shape_names("C3PRED", data)]
    return frames, U.c3_seats("c3pred")


def assembled(frames, seats, f, cell):
    """Hull frame f (tread step 0) with turret frame f laid on at its seat, as the DLL draws it, on a cell canvas."""
    sx, sy = seats[f]
    hull, turret = frames[f * P.TREAD_STEPS], frames[TURRET + f]
    img = Image.new("RGBA", (cell, cell), BG)
    img.alpha_composite(hull, ((cell - hull.width) // 2, (cell - hull.height) // 2))
    img.alpha_composite(turret, ((cell - turret.width) // 2 + sx * 8, (cell - turret.height) // 2 + sy * 8))
    return img


def team_green(frames):
    """Median G and green luminance of the green-dominant opaque pixels, for the house-colour target."""
    px = np.concatenate([np.asarray(f).reshape(-1, 4) for f in frames])
    px = px[px[:, 3] > 200].astype(float)
    g = px[(px[:, 1] > px[:, 0] + 30) & (px[:, 1] > px[:, 2] + 30)]
    return float(np.median(g[:, 1])), float(np.median(g[:, :3] @ np.array([0.299, 0.587, 0.114])))


def closeups(unit_frames, facings, scale=2):
    """A unit's turret frames alone, cropped to their joint art and scaled up nearest-neighbour, as one strip."""
    frames = [unit_frames[TURRET + f] for f in facings]
    x0, y0, x1, y1 = frames[0].getbbox()
    for fr in frames[1:]:
        b = fr.getbbox()
        x0, y0, x1, y1 = min(x0, b[0]), min(y0, b[1]), max(x1, b[2]), max(y1, b[3])
    x0, y0, x1, y1 = x0 - 8, y0 - 8, x1 + 8, y1 + 8
    w, h = (x1 - x0) * scale, (y1 - y0) * scale
    strip = Image.new("RGBA", (w * len(frames), h), BG)
    for i, fr in enumerate(frames):
        strip.alpha_composite(fr.crop((x0, y0, x1, y1)).resize((w, h), Image.NEAREST), (i * w, 0))
    return strip


def sheet(out, paths, seats):
    """Rows of 8 facings at packed size: Predator, Scorpion, Scorpion laser; then both turrets alone at 2x."""
    pred, pred_seats = predator()
    units = [("C3PRED (shipped)", pred, pred_seats)]
    for name, *_ in UNITS:
        units.append((name, frames_of(paths[name]), [seats[name][(32 - f) % 32] for f in range(32)]))
    cell, label = 576, 24
    strips = [(f"{name} turret alone, 2x nearest, facings 4 12 20 28", closeups(frames, (4, 12, 20, 28)))
              for name, frames, _ in units[1:]]
    w = max(cell * len(SHEET_FACINGS), max(s.width for _, s in strips))
    h = (cell + label) * len(units) + sum(s.height + label for _, s in strips)
    img = Image.new("RGBA", (w, h), (40, 40, 40, 255))
    d = ImageDraw.Draw(img)
    y = 0
    for title, frames, by_frame in units:
        d.text((6, y + 6), f"{title}: facings {list(SHEET_FACINGS)} (0 = N, CCW), tread step 0, turret at its seat; "
               "packed canvas px (full zoom)", fill=(230, 230, 230, 255))
        for c, f in enumerate(SHEET_FACINGS):
            img.alpha_composite(assembled(frames, by_frame, f, cell), (c * cell, y + label))
        y += cell + label
    for title, strip in strips:
        d.text((6, y + 6), title, fill=(230, 230, 230, 255))
        img.alpha_composite(strip, (0, y + label))
        y += strip.height + label
    path = os.path.join(out, "C3SCORP_preview_sheet.png")
    img.save(path)
    print(f"wrote {path}")
    for title, frames, _ in units:
        g, lum = team_green(frames[:TURRET + 32])
        print(f"{title}: team green median G {g:.0f}, luminance {lum:.0f}")


def cameo(out):
    asset_packs.cameo_tga = lambda icon: os.path.join(out, f"{icon}.tga")
    P.write_cameo("C3SCORP")


def main():
    if not P.ART or len(sys.argv) != 2:
        raise SystemExit(__doc__)
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    paths, drop = pack(out)
    seats = write_tables(out, drop)
    cameo(out)
    sheet(out, paths, seats)


if __name__ == "__main__":
    main()
