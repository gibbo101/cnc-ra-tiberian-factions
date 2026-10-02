#!/usr/bin/env python3
r"""
Sign-off sheet for unit placement: our units beside EA's own on one cell row, before and after.

Draws the units in scripts/unit_centring.py UNITS (or the ones named) at one facing, each with
its turret at its draw seat, its selection box from _art_boxes in udata.cpp and a red cross on
the unit's centre, beside EA's Medium Tank, Mammoth, APC and MCV for reference. The top half
is the art and boxes at a git revision (main by default), the bottom half the working tree, so
a change can be judged before anything is deployed.

EA's art is read from the game install's texture bundles (scripts/meg_extract.py).

Usage:
  scripts/unit_placement_sheet.py OUT.png [--facing 0..31] [--rev main] [UNIT ...]
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs
import unit_centring as uc

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_DATA = os.path.expanduser("~/.steam/steam/steamapps/common/CnCRemastered/Data")
EA_DENSITY = 128 / 24
K = 4.0  # sheet px per classic px
# label, bundle, path inside it, first turret frame
EA_REFS = [
    ("EA Medium", "TEXTURES_TD_SRGB.MEG", "TIBERIAN_DAWN\\UNITS\\MTNK.ZIP", 32),
    ("EA Mammoth", "TEXTURES_RA_SRGB.MEG", "RED_ALERT\\UNITS\\4TNK.ZIP", 32),
    ("EA APC", "TEXTURES_RA_SRGB.MEG", "RED_ALERT\\UNITS\\APC.ZIP", None),
    ("EA MCV", "TEXTURES_RA_SRGB.MEG", "RED_ALERT\\UNITS\\MCV.ZIP", None),
]


def ea_zips(tmp):
    out = []
    for label, bundle, inner, turret in EA_REFS:
        subprocess.run([sys.executable, os.path.join(REPO, "scripts", "meg_extract.py"), "extract",
                        os.path.join(GAME_DATA, bundle), inner, tmp], capture_output=True, check=True)
        path = os.path.join(tmp, inner.split("\\")[-1])
        out.append((label, zipfile.ZipFile(path), turret))
    return out


def zip_at(path, rev):
    if rev is None:
        return zipfile.ZipFile(path)
    blob = subprocess.run(["git", "-C", REPO, "show", f"{rev}:{os.path.relpath(path, REPO)}"],
                          capture_output=True, check=True).stdout
    return zipfile.ZipFile(io.BytesIO(blob))


def art_boxes(rev):
    if rev is None:
        src = open(os.path.join(REPO, "redalert", "udata.cpp"), encoding="latin-1").read()
    else:
        src = subprocess.run(["git", "-C", REPO, "show", f"{rev}:redalert/udata.cpp"],
                             capture_output=True, text=True, check=True).stdout
    return {m[0]: (int(m[1]), int(m[2])) for m in re.findall(r"\{UNIT_(\w+), (\d+), (\d+)\},", src)}


def canvas(z, name):
    meta = json.loads(z.read(name[:-4] + ".meta"))
    im = Image.open(io.BytesIO(z.read(name))).convert("RGBA")
    c = Image.new("RGBA", tuple(meta["size"]), (0, 0, 0, 0))
    c.paste(im, tuple(meta["crop"][:2]))
    return c


def tgas(z):
    return sorted(n for n in z.namelist() if n.lower().endswith(".tga"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("out")
    ap.add_argument("--facing", type=int, default=0)
    ap.add_argument("--rev", default="main")
    ap.add_argument("units", nargs="*")
    a = ap.parse_args()
    units = a.units or list(uc.UNITS)
    f = a.facing
    with tempfile.TemporaryDirectory() as tmp:
        refs = ea_zips(tmp)
        cols = [("ea", r) for r in refs] + [("tf", u) for u in units]
        per_row = 9
        rows = [cols[i:i + per_row] for i in range(0, len(cols), per_row)]
        cell = round(24 * K)
        col_w = round(cell * 1.9)
        row_h = cell * 2 + 40
        img = Image.new("RGB", (col_w * per_row, row_h * len(rows) * 2 + 20), (52, 68, 42))
        dr = ImageDraw.Draw(img)
        for state, rev in enumerate((a.rev, None)):
            boxes = art_boxes(rev)
            for r, row in enumerate(rows):
                oy = (state * len(rows) + r) * row_h + state * 20
                cy = oy + 30 + cell
                if r == 0:
                    dr.text((6, oy + 4), f"BEFORE ({a.rev})" if rev else "AFTER (working tree)", fill=(255, 230, 120))
                for x in range(0, img.width, cell):
                    dr.line([(x, cy - cell), (x, cy + cell)], fill=(70, 88, 58))
                for y in (cy - cell // 2, cy + cell // 2):
                    dr.line([(0, y), (img.width, y)], fill=(70, 88, 58))
                for k, (kind, item) in enumerate(row):
                    cx = col_w * k + col_w // 2
                    if kind == "ea":
                        label, z, turret = item
                        density, names, box = EA_DENSITY, tgas(item[1]), None
                        parts = [(names[f], (0, 0))] + ([(names[turret + f], (0, 0))] if turret else [])
                    else:
                        label = item
                        hull_frames, per_facing, turret, seat, _ = uc.UNITS.get(item, (32, 1, None, None, ()))
                        z = zip_at(asset_packs.art_zip(item, "UNITS"), rev)
                        density, names, box = uc.UNIT_DENSITY, tgas(z), boxes.get(item)
                        parts = [(names[f * per_facing], (0, 0))]
                        if turret is not None:
                            parts.append((names[turret + f], uc.seats_for(seat)[f]))
                    for name, (sx, sy) in parts:
                        c = canvas(z, name)
                        s = K / density
                        c = c.resize((round(c.width * s), round(c.height * s)), Image.LANCZOS)
                        img.paste(c, (cx - c.width // 2 + round(sx * K), cy - c.height // 2 + round(sy * K)), c)
                    if box:
                        w, h = box[0] * K / 2, box[1] * K / 2
                        dr.rectangle([cx - w, cy - h, cx + w, cy + h], outline=(255, 255, 255))
                    dr.line([(cx - 5, cy), (cx + 5, cy)], fill=(255, 60, 60), width=2)
                    dr.line([(cx, cy - 5), (cx, cy + 5)], fill=(255, 60, 60), width=2)
                    dr.text((cx - 36, oy + 16), label, fill=(255, 255, 255))
    img.save(a.out)
    print(a.out, img.size)


if __name__ == "__main__":
    main()
