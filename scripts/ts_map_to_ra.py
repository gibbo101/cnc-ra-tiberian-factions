#!/usr/bin/env python3
"""Lays a Tiberian Sun map on Red Alert's square grid (docs/ts-theatres.md): land, heights, ramps,
overlays, trees and start points per RA cell, with a preview image of each map.

Usage: ts_map_to_ra.py [--out DIR] [--all | <map name> ...]

Writes <map>.json and <map>.png per map and summary.tsv into DIR
(default ~/Desktop/Tiberian Factions/ts-theatres/converter).
"""
import argparse
import heapq
import json
import os
import re
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ts_map  # noqa: E402

RA_MAX = 126
# TS draws a cell one height level higher 15 px up: 1.25 rows of its 12 px screen grid.
LEVEL_ROWS = 1.25

# TS land type to the converter's cell class: one letter each in the JSON grid.
LAND_CLASS = {"clear": ".", "ice": "i", "rough": "r", "road": "=", "railroad": "=",
              "water": "~", "beach": "b", "rock": "#", "tunnel": "#"}
BLOCKING = "#~"
CLASS_COLOUR = {".": (96, 140, 70), "i": (170, 190, 210), "r": (130, 120, 80), "=": (150, 140, 125),
                "~": (50, 90, 170), "b": (190, 170, 120), "#": (60, 45, 35)}


def overlay_kind(name):
    """The converter's group for a TS overlay type."""
    if name.startswith("TIB"):
        return "tiberium"
    if name.startswith("VEIN"):
        return "veins"
    if re.search(r"WALL|FENC|GATE", name):
        return "wall"
    if re.search(r"BRDG|BRIDGE|RAIL|TRACK", name):
        return "bridge"
    return "other"


class Layout:
    """Where a TS map's cells land on RA's grid: one RA cell per TS screen diamond (two TS cells)."""

    def __init__(self, tsmap):
        lx, ly, lw, lh = tsmap.local
        dx0 = min(x - y for x, y in tsmap.cells)
        dy0 = min(x + y for x, y in tsmap.cells)
        left, right = dx0 + 2 * lx, dx0 + 2 * (lx + lw)
        top, bottom = dy0 + 2 * ly, dy0 + 2 * (ly + lh)
        shown = [(x - y, x + y) for (x, y), (_t, _s, level) in tsmap.cells.items()
                 if left <= x - y < right and top <= x + y - LEVEL_ROWS * level < bottom]
        self.x0 = min(d for d, _ in shown)
        self.y0 = min(d for _, d in shown)
        if (self.x0 - self.y0) % 2:
            self.y0 -= 1
        self.width = (max(d for d, _ in shown) - self.x0) // 2 + 1
        self.height = (max(d for _, d in shown) - self.y0) // 2 + 1

    def centre(self, u, v):
        """The TS cell at the centre of RA cell (u, v)."""
        dx, dy = self.x0 + 2 * u + 1, self.y0 + 2 * v + 1
        return (dx + dy) // 2, (dy - dx) // 2

    def corner(self, u, v):
        """The TS cell on the north-west corner of RA cell (u, v)."""
        dx, dy = self.x0 + 2 * u, self.y0 + 2 * v
        return (dx + dy) // 2, (dy - dx) // 2

    def ra_cell(self, x, y):
        """The RA cell a TS cell's centre falls in: a corner cell goes to the cell south-east of it."""
        return (x - y - self.x0) // 2, (x + y - self.y0) // 2


def open_neighbours(grid, cell, width, height):
    """How many of a cell's four side neighbours are open."""
    u, v = cell
    return sum(1 for a, b in ((u - 1, v), (u + 1, v), (u, v - 1), (u, v + 1))
               if 0 <= a < width and 0 <= b < height and grid[b][a] not in BLOCKING)


def close_diagonal_gaps(grid, heights, layout, cell_class):
    """Blocks one open cell of each 2x2 whose blocked pair touches only diagonally across a blocked
    TS corner cell, since RA's pathfinding cuts diagonal corners. The more enclosed cell takes it."""
    closed = 0
    for v in range(layout.height - 1):
        for u in range(layout.width - 1):
            for (p, q), (o1, o2) in ((((u, v), (u + 1, v + 1)), ((u + 1, v), (u, v + 1))),
                                    (((u + 1, v), (u, v + 1)), ((u, v), (u + 1, v + 1)))):
                kp, kq = grid[p[1]][p[0]], grid[q[1]][q[0]]
                if kp in BLOCKING and kp == kq and grid[o1[1]][o1[0]] not in BLOCKING \
                        and grid[o2[1]][o2[0]] not in BLOCKING \
                        and cell_class(layout.corner(u + 1, v + 1)) == kp:
                    rank = [(open_neighbours(grid, o, layout.width, layout.height), heights[o[1]][o[0]], o)
                            for o in (o1, o2)]
                    lo = min(rank)[2]
                    grid[lo[1]][lo[0]] = kp
                    closed += 1
    return closed


def can_step(height_a, ramp_a, height_b, ramp_b):
    """TS's rule for stepping between two cells (FootClass::Can_Reach): level ground, or one level
    with the lower cell a ramp."""
    if height_a == height_b:
        return True
    if abs(height_a - height_b) == 1:
        return (ramp_a if height_a < height_b else ramp_b) != 0
    return False


def route_lengths(passable, step_ok, step, source):
    """Shortest 8-way route length from `source` to each cell, a step of (dx, dy) costing
    step * (1 or sqrt 2)."""
    best = {source: 0.0}
    queue = [(0.0, source)]
    while queue:
        d, (x, y) = heapq.heappop(queue)
        if d > best[(x, y)]:
            continue
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                c = (x + dx, y + dy)
                if (dx or dy) and passable(c) and step_ok((x, y), c):
                    nd = d + step * (1.4142 if dx and dy else 1.0)
                    if nd < best.get(c, 1e18):
                        best[c] = nd
                        heapq.heappush(queue, (nd, c))
    return best


def route_check(tsmap, tileset, layout, grid, heights, ramps):
    """Land route length between each pair of start points in TS and on the converted grid with
    TS's step rule on its heights, in TS cell widths: [(a, b, TS length, RA length)]."""
    def ts_passable(c):
        entry = tsmap.cells.get(c)
        return entry is not None and tileset.record(entry[0], entry[1])["land"] not in ("rock", "tunnel", "water")

    def ts_step(a, b):
        ea, eb = tsmap.cells[a], tsmap.cells[b]
        return can_step(ea[2], tileset.record(ea[0], ea[1])["ramp"], eb[2], tileset.record(eb[0], eb[1])["ramp"])

    def ra_passable(c):
        return 0 <= c[0] < layout.width and 0 <= c[1] < layout.height and grid[c[1]][c[0]] not in BLOCKING

    def ra_step(a, b):
        return can_step(heights[a[1]][a[0]], ramps[a[1]][a[0]], heights[b[1]][b[0]], ramps[b[1]][b[0]])

    def nearest(cell, passable):
        ring = [(cell[0] + a, cell[1] + b) for r in range(3) for a in range(-r, r + 1) for b in range(-r, r + 1)]
        return next((c for c in ring if passable(c)), None)

    starts = sorted((n, c) for n, c in tsmap.waypoints().items() if n < 8)
    out = []
    for i, (na, ca) in enumerate(starts):
        ts_a, ra_a = nearest(ca, ts_passable), nearest(layout.ra_cell(*ca), ra_passable)
        ts_best = route_lengths(ts_passable, ts_step, 1.0, ts_a) if ts_a else {}
        ra_best = route_lengths(ra_passable, ra_step, 1.4142, ra_a) if ra_a else {}
        for nb, cb in starts[i + 1:]:
            ts_b, ra_b = nearest(cb, ts_passable), nearest(layout.ra_cell(*cb), ra_passable)
            ts_len, ra_len = ts_best.get(ts_b), ra_best.get(ra_b)
            out.append((na + 1, nb + 1, ts_len and round(ts_len), ra_len and round(ra_len)))
    return out


def convert(tsmap, tileset, overlay_names):
    """The map laid on RA's grid, as a JSON-ready dict."""
    layout = Layout(tsmap)

    def cell_class(cell):
        entry = tsmap.cells.get(cell)
        if entry is None:
            return "#"
        return LAND_CLASS[tileset.record(entry[0], entry[1])["land"]]

    grid, heights, ramps = [], [], []
    for v in range(layout.height):
        row, hrow, rrow = [], [], []
        for u in range(layout.width):
            cell = layout.centre(u, v)
            entry = tsmap.cells.get(cell)
            row.append(cell_class(cell))
            hrow.append(entry[2] if entry else 0)
            rrow.append(tileset.record(entry[0], entry[1])["ramp"] if entry else 0)
        grid.append(row)
        heights.append(hrow)
        ramps.append(rrow)
    closed = close_diagonal_gaps(grid, heights, layout, cell_class)
    routes = route_check(tsmap, tileset, layout, grid, heights, ramps)

    def inside(c):
        return 0 <= c[0] < layout.width and 0 <= c[1] < layout.height

    overlays = {}
    for (x, y), (kind, _data) in tsmap.overlays().items():
        c = layout.ra_cell(x, y)
        if inside(c):
            name = overlay_names[kind] if kind < len(overlay_names) else str(kind)
            overlays.setdefault(overlay_kind(name), {}).setdefault(name, set()).add(c)
    terrain = {}
    for (x, y), name in tsmap.terrain().items():
        c = layout.ra_cell(x, y)
        if inside(c):
            terrain.setdefault(name, []).append(c)
    starts = {n: layout.ra_cell(*c) for n, c in tsmap.waypoints().items() if n < 8}
    structures = [(o, t, *layout.ra_cell(x, y)) for o, t, x, y in tsmap.objects("Structures")]
    return {
        "name": tsmap.name, "theatre": tsmap.theatre, "ts_size": tsmap.size, "ts_local": tsmap.local,
        "width": layout.width, "height": layout.height,
        "fits": layout.width <= RA_MAX and layout.height <= RA_MAX,
        "gaps_closed": closed, "routes": routes,
        "grid": ["".join(r) for r in grid], "heights": heights, "ramps": ramps,
        "starts": starts,
        "overlays": {k: {n: sorted(c) for n, c in v.items()} for k, v in overlays.items()},
        "terrain": terrain, "structures": structures,
        "lighting": {"ambient": tsmap.light(0)[0], "per_level": tsmap.light(1)[0] - tsmap.light(0)[0]},
    }


def preview(data, path, px=6):
    """A picture of the converted map: land by colour, brighter with height as TS lights it, ramps
    hatched, Tiberium and veins dotted, trees and start points marked."""
    w, h = data["width"], data["height"]
    img = Image.new("RGB", (w * px, h * px))
    draw = ImageDraw.Draw(img)
    amb, per = data["lighting"]["ambient"], data["lighting"]["per_level"]
    for v, row in enumerate(data["grid"]):
        for u, k in enumerate(row):
            f = (amb + per * data["heights"][v][u]) / (amb + per * 4)
            colour = tuple(min(255, int(c * f)) for c in CLASS_COLOUR[k])
            draw.rectangle([u * px, v * px, u * px + px - 1, v * px + px - 1], fill=colour)
            if data["ramps"][v][u] and k not in BLOCKING:
                draw.line([u * px, v * px + px - 1, u * px + px - 1, v * px], fill=tuple(c // 2 for c in colour))
    dots = {"tiberium": (60, 230, 60), "veins": (200, 60, 90), "wall": (230, 230, 230), "bridge": (240, 150, 40)}
    for kind, names in data["overlays"].items():
        for cells in names.values():
            for u, v in cells:
                if kind in dots:
                    draw.rectangle([u * px + 2, v * px + 2, u * px + px - 3, v * px + px - 3], fill=dots[kind])
    for cells in data["terrain"].values():
        for u, v in cells:
            draw.ellipse([u * px + 1, v * px + 1, u * px + px - 2, v * px + px - 2], fill=(20, 70, 20))
    for n, (u, v) in data["starts"].items():
        draw.rectangle([u * px - 6, v * px - 6, u * px + 12, v * px + 12], fill=(255, 255, 255))
        draw.text((u * px - 2, v * px - 5), str(n + 1), fill=(0, 0, 0))
    img.save(path)


def route_ratio(routes):
    """'min-max' of RA route length over TS route length across start pairs, or what differs."""
    ratios = [r / t for _a, _b, t, r in routes if t and r]
    broken = [(a, b) for a, b, t, r in routes if bool(t) != bool(r)]
    text = f"{min(ratios):.2f}-{max(ratios):.2f}" if ratios else "-"
    return text + (f" route lost/gained {broken}" if broken else "")


def slug(name):
    """A map name as a file name."""
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("maps", nargs="*")
    parser.add_argument("--all", action="store_true", help="every multiplayer map of TS")
    parser.add_argument("--out", default=os.path.expanduser("~/Desktop/Tiberian Factions/ts-theatres/converter"))
    args = parser.parse_args()
    install = ts_map.TsInstall()
    maps = install.maps()
    names = sorted(maps) if args.all else args.maps
    if not names:
        parser.error("name a map or pass --all; maps: " + ", ".join(sorted(maps)))
    os.makedirs(args.out, exist_ok=True)
    overlay_names = install.overlay_names()
    tilesets, rows = {}, []
    for name in names:
        tsmap = ts_map.TsMap(maps[name])
        if tsmap.theatre not in tilesets:
            tilesets[tsmap.theatre] = ts_map.Tileset(install, tsmap.theatre)
        data = convert(tsmap, tilesets[tsmap.theatre], overlay_names)
        with open(os.path.join(args.out, slug(name) + ".json"), "w") as f:
            json.dump(data, f, separators=(",", ":"))
        preview(data, os.path.join(args.out, slug(name) + ".png"))
        players = sum(1 for n in data["starts"])
        rows.append((name, data["theatre"], players, data["width"], data["height"], data["fits"],
                     data["gaps_closed"], route_ratio(data["routes"])))
        print(f"{name:32} {data['theatre']:9} {players}p {data['width']:3}x{data['height']:<3} "
              f"{'fits' if data['fits'] else 'too big'}  gaps closed {data['gaps_closed']:3}  "
              f"RA/TS route length {route_ratio(data['routes'])}")
    with open(os.path.join(args.out, "summary.tsv"), "w") as f:
        f.write("map\ttheatre\tstarts\twidth\theight\tfits\tgaps_closed\troute_ratio_min_max\n")
        for r in rows:
            f.write("\t".join(str(v) for v in r) + "\n")


if __name__ == "__main__":
    main()
