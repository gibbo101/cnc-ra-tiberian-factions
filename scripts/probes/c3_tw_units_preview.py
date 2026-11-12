#!/usr/bin/env python3
"""Sign-off sheets for the C&C3 pack's Tiberium Wars units: 8 facings of each vehicle as the DLL would draw it (hull,
then the turret at its c3tanks.h seat), beside the shipped C3PRED and C3SCORP.
Usage: c3_tw_units_preview.py <out dir> <sheet.png> NAME ... | --walker NAME STAGES FACINGS
License: GPL v3.
"""
import io
import json
import math
import os
import re
import sys
import zipfile

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import asset_packs  # noqa: E402

REPO = os.path.dirname(os.path.dirname(HERE))
HEADER = open(os.path.join(REPO, "redalert", "c3tanks.h")).read()
DROPS = json.load(open(os.path.join(REPO, "scripts", "unit_art_drop.json")))
BG = (96, 104, 88, 255)
K = 128 / 192           # unit canvas px (8 per classic px) to the launcher's HD px per cell
LEP = 128 / 256         # leptons to HD px
TURRET = 96


def frames(name, kind):
    """Shape number -> full-canvas RGBA, through the tileset, so members shared with another ZIP resolve."""
    xml = open(asset_packs.tileset_xml(name, kind), encoding="utf-8").read()
    tiles = re.findall(r"<Name>%s</Name>\s*<Shape>(\d+)</Shape>.*?<Frame>([^<]+)</Frame>" % re.escape(name), xml, re.S)
    out = {}
    for shape, frame in tiles:
        folder, member = frame.split("\\")
        z = zipfile.ZipFile(asset_packs.art_zip(folder.upper(), kind))
        shape = int(shape)
        meta = json.loads(z.read(member[:-4] + ".meta"))
        im = Image.new("RGBA", tuple(meta["size"]))
        im.alpha_composite(Image.open(io.BytesIO(z.read(member))).convert("RGBA"), tuple(meta["crop"][:2]))
        out[shape] = im
    return out


def table(name, suffix):
    body = re.search(r"_%s_%s\[[^=]*= \{(.*?)\};" % (name.lower(), suffix), HEADER, re.S).group(1)
    return [(int(a), int(b)) for a, b in re.findall(r"\{(-?\d+), (-?\d+)\}", body)]


SEAT_OF = {"C3PITBMOR": "C3PITB", "C3BUGGYEMP": "C3BUGGY"}


def unit_image(name, facing, art):
    """The vehicle at facing (frame order, CCW from N) with its turret seated, at unit canvas density."""
    im = art[facing * 3].copy()
    if TURRET + facing in art:
        seat = table(SEAT_OF.get(name, name), "seat_px")[(32 - facing) % 32]
        im.alpha_composite(art[TURRET + facing], (seat[0] * 8, seat[1] * 8))
    return im


def sheet(out, names, file):
    cell = 256
    img = Image.new("RGBA", (8 * cell, len(names) * cell), BG)
    d = ImageDraw.Draw(img)
    for r, name in enumerate(names):
        art = frames(name, "UNITS")
        for c, f in enumerate(range(0, 32, 4)):
            u = unit_image(name, f, art)
            img.alpha_composite(u, (c * cell + (cell - u.width) // 2, r * cell + (cell - u.height) // 2))
        d.text((6, r * cell + 4), name, fill=(255, 255, 255, 255))
    img.convert("RGB").save(os.path.join(out, file))



def walker_sheet(out, name, stages, facings, file):
    """Each walk facing at rest with its turret seated (top row), and every stage of the stride facing east."""
    art = frames(name, "UNITS")
    cell = 384
    img = Image.new("RGBA", (max(facings, stages) * cell // 2, 2 * cell), BG)
    for c in range(facings):
        f32 = c * 32 // facings
        u = art[c * stages].copy()
        if TURRET + f32 in art and stages * facings == TURRET:
            seat = table(name, "seat_px")[(32 - f32) % 32]
            u.alpha_composite(art[TURRET + f32], (seat[0] * 8, seat[1] * 8))
        u = u.resize((u.width // 2, u.height // 2))
        img.alpha_composite(u, (c * cell // 2 + (cell // 2 - u.width) // 2, (cell - u.height) // 2))
    east = facings * 3 // 4
    for i in range(stages):
        u = art[east * stages + i].resize((art[0].width // 2, art[0].height // 2))
        img.alpha_composite(u, (i * cell // 2 + (cell // 2 - u.width) // 2, cell + (cell - u.height) // 2))
    img.convert("RGB").save(os.path.join(out, file))


if __name__ == "__main__":
    out, file, *names = sys.argv[1:]
    os.makedirs(out, exist_ok=True)
    if names[0] == "--walker":
        walker_sheet(out, names[1], int(names[2]), int(names[3]), file)
    else:
        sheet(out, ["C3PRED", "C3SCORP"] + names, file)
