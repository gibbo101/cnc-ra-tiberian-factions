"""Probe: one skirmish map per theatre, set to that theatre, with every template the DLL has for it
placed once, each icon its own tileset draws in its cell.

usage: td_catalogue_maps.py <out dir>
Writes tf-catalogue-<theatre>.mpr/.json/.tga and tf-catalogue-<theatre>.txt, the templates in
reading order (left to right, top to bottom) with their map cells.
"""
import json
import os
import re
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from meg_extract import read_member  # noqa: E402
from td_map_to_ra import EDITOR_SRC, OVERLAY_NONE, RA_CELLS, RA_TEMPLATE_NONE, parse_templates  # noqa: E402
from td_map_to_ra import ra_cell, write_triplet  # noqa: E402

CONFIG = os.path.expanduser("~/.steam/steam/steamapps/common/CnCRemastered/Data/CONFIG.MEG")
TILE_MAP = os.path.join(os.path.dirname(__file__), "..", "td_ra_tile_map.json")
# map theatre -> (tileset, the editor's RA theatre or the tile map's TD key, launcher label)
THEATRES = {"temperate": ("RA_TERRAIN_TEMPERATE", "Temperate", "TEMPERATE"),
            "snow": ("RA_TERRAIN_SNOW", "Snow", "SNOW"),
            "interior": ("RA_TERRAIN_INTERIOR", "Interior", "INTERIOR"),
            "desert": ("TD_TERRAIN_DESERT", "desert", "DESERT"),
            "tdtemperate": ("TD_TERRAIN_TEMPERATE", "temperate", "TEMPERATE"),
            "winter": ("TD_TERRAIN_WINTER", "winter", "WINTER")}
# terrain objects placed in a row above the starts, each TD theatre's own
OBJECTS = {"desert": ["T04", "T08", "T09", "T18", "ROCK1", "ROCK2", "ROCK3", "ROCK4", "ROCK5", "ROCK6", "ROCK7"],
           "tdtemperate": ["T01", "T02", "T03", "T05", "T06", "T07", "T08", "T10", "T11", "T12", "T13", "T14", "T15",
                           "T16", "T17", "TC01", "TC02", "TC03", "TC04", "TC05"]}
OBJECTS["winter"] = OBJECTS["tdtemperate"]
INTERIOR_FLOOR = 268  # FLOR0001: interior's clear cells are impassable rock
MAP_X, MAP_Y, MAP_W, MAP_H = 16, 16, 96, 96
LEFT, TOP, RIGHT, START_ROW = MAP_X + 1, MAP_Y + 1, MAP_X + MAP_W - 1, MAP_Y + 62


def icons_of(tileset):
    """Tile name -> the icon numbers its tileset draws."""
    text = read_member(CONFIG, "DATA\\XML\\TILESETS\\%s.XML" % tileset).decode("latin-1")
    out = {}
    for name, shape in re.findall(r"<Name>([^<]+)</Name>\s*<Shape>(\d+)</Shape>", text):
        out.setdefault(name.upper(), set()).add(int(shape))
    return out


def templates(key):
    """(tileset name, map id, map name, w, h) for every template of this theatre."""
    tileset_key = THEATRES[key][1]
    if key in ("temperate", "snow", "interior"):
        ra = parse_templates(os.path.join(EDITOR_SRC, "RedAlert", "TemplateTypes.cs"))
        return [(n.upper(), i, n.upper(), w, h) for i, n, w, h, th in ra if tileset_key in th and n != "clear1"]
    tiles = json.load(open(TILE_MAP))
    return [(n.upper(), v[tileset_key]["ra_id"], v[tileset_key]["ra_name"], v[tileset_key]["size"][0],
             v[tileset_key]["size"][1]) for n, v in sorted(tiles.items()) if tileset_key in v]


def build(key, out_dir):
    tileset, _, label = THEATRES[key]
    icons = icons_of(tileset)
    ttype = [RA_TEMPLATE_NONE] * RA_CELLS
    ticon = [0] * RA_CELLS
    x, y, row_h = LEFT, TOP, 0
    legend = []
    for name, tid, map_name, w, h in templates(key):
        if x + w > RIGHT:
            x, y, row_h = LEFT, y + row_h + 1, 0
        if y + h >= START_ROW:
            raise SystemExit("%s: catalogue does not fit" % key)
        drawn = icons.get(name, set()) & set(range(w * h))
        for i in drawn:
            c = ra_cell(x + i % w, y + i // w)
            ttype[c], ticon[c] = tid, i
        legend.append("%-10s %-11s %dx%d at (%d,%d), %d of %d icons in the tileset"
                      % (name, map_name, w, h, x, y, len(drawn), w * h))
        x += w + 1
        row_h = max(row_h, h)
    if key == "interior":
        for cy in range(MAP_Y, MAP_Y + MAP_H):
            for cx in range(MAP_X, MAP_X + MAP_W):
                if ttype[ra_cell(cx, cy)] == RA_TEMPLATE_NONE:
                    ttype[ra_cell(cx, cy)] = INTERIOR_FLOOR
    packed = b"".join(struct.pack("<H", t) for t in ttype) + bytes(ticon)
    starts = [ra_cell(MAP_X + 12 + (i % 4) * 22, START_ROW + 8 + (i // 4) * 14) for i in range(8)]
    base = os.path.join(out_dir, "tf-catalogue-%s" % key)
    theatre = {"tdtemperate": "TDTemperate"}.get(key, key.capitalize())
    objects = [(ra_cell(LEFT + 4 * i, START_ROW - 6), "%s,None" % o) for i, o in enumerate(OBJECTS.get(key, []))]
    legend += ["%-10s object at (%d,%d)" % (o, LEFT + 4 * i, START_ROW - 6) for i, o in enumerate(OBJECTS.get(key, []))]
    write_triplet(base + ".mpr", "TF Catalogue %s" % theatre, theatre, MAP_X, MAP_Y, MAP_W, MAP_H,
                  packed, bytes([OVERLAY_NONE]) * RA_CELLS, starts, objects, [], [RA_TEMPLATE_NONE] * RA_CELLS)
    manifest = json.load(open(base + ".json"))
    manifest["Theater"] = label
    json.dump(manifest, open(base + ".json", "w"), separators=(",", ":"))
    open(base + ".txt", "w").write("\n".join(legend) + "\n")
    print(key, len(legend), "templates, rows end at", y + row_h)


if __name__ == "__main__":
    os.makedirs(sys.argv[1], exist_ok=True)
    for k in THEATRES:
        build(k, sys.argv[1])
