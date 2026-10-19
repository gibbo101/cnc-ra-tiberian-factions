#!/usr/bin/env python3
"""TS ground drawn flat on RA's grid from TS's own tiles (docs/ts-theatres.md): a contact sheet of a map
region as TS shows it and as RA would, and a count of the distinct RA cells the TS maps need.

Usage: ts_ground_sample.py [--map NAME] [--at U,V] [--size W,H] [--out DIR]
"""
import argparse
import os
import sys
from collections import Counter

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import ts_map  # noqa: E402
import ts_map_to_ra as conv  # noqa: E402

HD = 128
# TS lifts a cell 15 px per height level on screen.
LEVEL_PX = 15


def ts_cells_in(tsmap, x_lo, x_hi, y_lo, y_hi):
    """TS cells whose screen position (x - y, x + y) lies in the given range, back to front."""
    found = [((x - y), (x + y), (x, y)) for (x, y) in tsmap.cells
             if x_lo <= x - y <= x_hi and y_lo <= x + y <= y_hi]
    return sorted(found, key=lambda f: (f[1], tsmap.cells[f[2]][2]))


def draw_ground(tsmap, tileset, layout, u0, v0, w, h, lifted):
    """The region's ground in TS's screen space (48 x 24 px per RA cell): flat, or lifted by height
    with cliff faces, as TS draws it."""
    margin = 6 if lifted else 1
    sx, sy = layout.x0 + 2 * u0, layout.y0 + 2 * v0
    canvas = Image.new("RGBA", (w * 48, h * 24 + (240 if lifted else 0)), (0, 0, 0, 255))
    top = 240 if lifted else 0
    for dx, dy, cell in ts_cells_in(tsmap, sx - margin, sx + 2 * w + margin, sy - margin,
                                    sy + 2 * h + margin + (24 if lifted else 0)):
        tile, sub, level = tsmap.cells[cell]
        rec = tileset.record(tile, sub)
        light = tsmap.light(level)
        px = (dx - sx) * 24 - 24
        py = (dy - sy) * 12 - 12 + top - (LEVEL_PX * level if lifted else 0)
        img = tileset.diamond(rec, light)
        canvas.paste(img, (px, py), img)
        if lifted and rec["extra"]:
            ex, ey, ew, eh, data = rec["extra"]
            extra = Image.new("RGBA", (ew, eh), (0, 0, 0, 0))
            put = extra.load()
            for i, p in enumerate(data):
                if p:
                    r, g, b = tileset.palette[p]
                    put[i % ew, i // ew] = (min(255, int(r * light[0])), min(255, int(g * light[1])),
                                            min(255, int(b * light[2])), 255)
            canvas.paste(extra, (px + ex - rec["x"], py + ey - rec["y"]), extra)
    return canvas


def flat_hd(tsmap, tileset, layout, u0, v0, w, h):
    """The region flattened and stretched to top-down, at HD size (128 px per RA cell)."""
    flat = draw_ground(tsmap, tileset, layout, u0, v0, w, h, lifted=False)
    top_down = flat.resize((w * 48, h * 48), Image.NEAREST)
    return top_down.resize((w * HD, h * HD), Image.LANCZOS)


def cell_key(tsmap, tileset, layout, u, v):
    """What an RA cell's flat art depends on: its centre and four corner TS cells' tiles and heights."""
    cells = [layout.centre(u, v)] + [layout.corner(u + a, v + b) for a, b in ((0, 0), (1, 0), (0, 1), (1, 1))]
    key = []
    for c in cells:
        tile, sub, level = tsmap.cells.get(c, (0, 0, 0))
        key.append((tileset.fixup(tile), sub, level))
    return tuple(key)


def count_cells(install, maps):
    """Distinct RA cells per theatre over the maps that fit, with and without baked height lighting."""
    tilesets, lit, unlit, total = {}, {}, {}, Counter()
    for name, text in sorted(maps.items()):
        tsmap = ts_map.TsMap(text)
        th = tsmap.theatre
        tilesets.setdefault(th, ts_map.Tileset(install, th))
        layout = conv.Layout(tsmap)
        if layout.width > conv.RA_MAX or layout.height > conv.RA_MAX:
            continue
        for v in range(layout.height):
            for u in range(layout.width):
                key = cell_key(tsmap, tilesets[th], layout, u, v)
                lit.setdefault(th, set()).add(key)
                unlit.setdefault(th, set()).add(tuple(k[:2] for k in key))
                total[th] += 1
    return {th: (total[th], len(lit[th]), len(unlit[th])) for th in total}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--map", default="Tiers of Sorrow")
    parser.add_argument("--at", default="10,8")
    parser.add_argument("--size", default="12,8")
    parser.add_argument("--out", default=os.path.expanduser("~/Desktop/Tiberian Factions/ts-theatres/ground-sample"))
    args = parser.parse_args()
    u0, v0 = (int(v) for v in args.at.split(","))
    w, h = (int(v) for v in args.size.split(","))
    os.makedirs(args.out, exist_ok=True)
    install = ts_map.TsInstall()
    maps = install.maps()
    tsmap = ts_map.TsMap(maps[args.map])
    tileset = ts_map.Tileset(install, tsmap.theatre)
    layout = conv.Layout(tsmap)

    lifted = draw_ground(tsmap, tileset, layout, u0, v0, w, h, lifted=True)
    lifted = lifted.resize((lifted.width * 2, lifted.height * 2), Image.NEAREST)
    hd = flat_hd(tsmap, tileset, layout, u0, v0, w, h)
    grid = hd.copy()
    d = ImageDraw.Draw(grid)
    for u in range(w + 1):
        d.line([u * HD, 0, u * HD, h * HD], fill=(255, 255, 255, 90))
    for v in range(h + 1):
        d.line([0, v * HD, w * HD, v * HD], fill=(255, 255, 255, 90))
    slug = conv.slug(args.map)
    lifted.save(os.path.join(args.out, f"{slug}_ts_view.png"))
    hd.save(os.path.join(args.out, f"{slug}_ra_flat_hd.png"))
    grid.save(os.path.join(args.out, f"{slug}_ra_flat_hd_grid.png"))
    print("wrote", args.out)
    for th, (total, lit, unlit) in count_cells(install, maps).items():
        print(f"{th}: {total} RA cells on the maps that fit; {lit} distinct with height lighting baked, "
              f"{unlit} without")


if __name__ == "__main__":
    main()
