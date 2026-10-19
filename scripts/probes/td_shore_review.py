#!/usr/bin/env python3
"""Probe: the TD shore tiles laid out for a cell-by-cell land review (water, beach, clear or rock).

usage: td_shore_review.py <out dir>
Writes <out>/tiles.json (each tile's size, cells, measured water share and TD's own land type),
<out>/seed.json (TD's own land type per cell, the review's starting point) and <out>/img/*.jpg (each
tile from its HD art).
A tile is listed when TD types any of it water or its classic art draws water; rivers are not.
"""
import io
import json
import os
import re
import struct
import sys

from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import steam_library  # noqa: E402
import td_templates  # noqa: E402
from meg_extract import member_index  # noqa: E402

TEMS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_td_tems")
TILE_MAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "td_ra_tile_map.json")
TEX = str(steam_library.path("common/CnCRemastered/Data/TEXTURES_TD_SRGB.MEG"))
CELL_PX = 64
# review group -> (theatres reviewed together, the one measured and drawn first)
GROUPS = {"des": (["DES"], "DES"), "tw": (["TEM", "WIN"], "TEM")}
THEATRE_KEY = {"DES": "desert", "TEM": "temperate", "WIN": "winter"}
LETTER = {"WATER": "W", "BEACH": "B", "CLEAR": "C", "ROCK": "R", "ROUGH": "U", "ROAD": "D"}


def iconset(name, suffix):
    """(width, height, [576-byte icon or None per cell]) of a staged TD iconset."""
    d = open(os.path.join(TEMS, "TD%s.%s" % (name.upper(), suffix)), "rb").read()
    f = struct.unpack_from("<6H7i", d, 0)
    w, h, icons, imap = f[4], f[5], f[7], f[12]
    cells = d[imap:imap + w * h]
    return w, h, [None if i == 0xFF else d[icons + i * 576:icons + (i + 1) * 576] for i in cells]


def water_share(suffix):
    """name -> per-cell water share (0-100, None undrawn) for one theatre, against W1's colours."""
    colours = {b for icon in iconset("w1", suffix)[2] if icon for b in icon}

    def share(name):
        return [None if icon is None else round(100 * sum(1 for b in icon if b in colours) / 576, 1)
                for icon in iconset(name, suffix)[2]]
    return share


def hd_frames(index):
    """(theatre suffix, NAME, cell) -> the first animation frame's member, for every TD terrain cell."""
    found = {}
    for key in index:
        m = re.search(r"\\TERRAIN\\\w+\\[^\\]+\\(\w+)\.(DES|TEM|WIN)-(\d{4})(?:-(\d+))?\.DDS$", key)
        if m:
            cell = (m.group(2), m.group(1), int(m.group(3)))
            frame = int(m.group(4) or 0)
            if cell not in found or frame < found[cell][0]:
                found[cell] = (frame, key)
    return {cell: key for cell, (_, key) in found.items()}


def hd_cell(index, frames, suffix, name, k):
    """One cell's HD art (first animation frame), or None."""
    key = frames.get((suffix, name.upper(), k))
    if key is None:
        return None
    size, offset = index[key]
    with open(TEX, "rb") as f:
        f.seek(offset)
        return Image.open(io.BytesIO(f.read(size))).convert("RGBA")


def tile_image(index, frames, suffix, name, w, h, path):
    img = Image.new("RGBA", (w * CELL_PX, h * CELL_PX), (0, 0, 0, 0))
    for k in range(w * h):
        cell = hd_cell(index, frames, suffix, name, k)
        if cell:
            img.paste(cell.resize((CELL_PX, CELL_PX), Image.LANCZOS), ((k % w) * CELL_PX, (k // w) * CELL_PX))
    flat = Image.new("RGB", img.size, (52, 50, 46))
    flat.paste(img, mask=img.split()[3])
    flat.save(path, quality=88)


def main():
    out = sys.argv[1]
    os.makedirs(os.path.join(out, "img"), exist_ok=True)
    lands = td_templates.land_specs()
    tiles = json.load(open(TILE_MAP))
    index = member_index(TEX)
    frames = hd_frames(index)
    rivers = {n for n, (land, alt, _) in lands.items() if "RIVER" in (land, alt)}
    listing, seed = [], {}
    for group, (suffixes, first) in GROUPS.items():
        shares = {s: water_share(s) for s in suffixes}
        for name in sorted(tiles):
            if name in rivers or not all(THEATRE_KEY[s] in tiles[name] for s in suffixes):
                continue
            land, alt, alts = lands[name]
            pct = {s: shares[s](name) for s in suffixes}
            typed = [alt if k in alts else land for k in range(len(pct[first]))]
            if "WATER" not in (land, alt) and not any((p or 0) >= 5 for p in pct[first]):
                continue
            w, h = tiles[name][THEATRE_KEY[first]]["size"]
            images = []
            for s in suffixes:
                rel = "img/%s_%s.jpg" % (s.lower(), name)
                tile_image(index, frames, s, name, w, h, os.path.join(out, rel))
                images.append(rel)
            doc = "%s_%s" % (group, name)
            listing.append({"id": doc, "group": group, "name": name.upper(), "w": w, "h": h, "images": images,
                            "pct": [pct[s] for s in suffixes], "td": [None if p is None else t
                                                                      for p, t in zip(pct[first], typed)]})
            seed[doc] = {"cells": [None if p is None else LETTER[t] for p, t in zip(pct[first], typed)],
                         "reviewed": False}
    json.dump(listing, open(os.path.join(out, "tiles.json"), "w"))
    json.dump(seed, open(os.path.join(out, "seed.json"), "w"))
    print("%d tiles: %d desert, %d temperate and winter" % (
        len(listing), sum(t["group"] == "des" for t in listing), sum(t["group"] == "tw" for t in listing)))


if __name__ == "__main__":
    main()
