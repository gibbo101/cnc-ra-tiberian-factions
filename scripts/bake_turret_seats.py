#!/usr/bin/env python3
"""Turn turret-spot dot marks into per-facing Turret_Adjust offset tables.

Input: ~/Desktop/turret-marking/<SHIP>/{N,NE,E}.png with a PURE RED (255,0,0)
dot at the turret mount point (TDCA also PURE BLUE (0,0,255) for the aft spot).
Marks may be saved over the originals or as <name>-marked.png.

Model: the mount is a fixed point on the hull -> its screen offset over heading h is
  dx(h) = a*sin(h) + b*cos(h)
  dy(h) = (-a*cos(h) + b*sin(h)) * C + L        (C = iso y-compression, L = lift)
a,b come straight from the N/E dx marks; C,L least-squares from the three dy marks.
Output: the 16-facing offset table in art px and classic px (art_px / PX_PER_CLASSIC,
which Turret_Adjust works in; launcher upscales classic->virtual by ~128/24).

Usage: bake_turret_seats.py [ship ...]        (default: all four)
License: GPL v3.
"""
import math, os, sys
from PIL import Image

BASE = os.path.expanduser("~/Desktop/turret-marking")
PX_PER_CLASSIC = 128 / 24        # HD art px (=virtual px at 128px/cell) per classic px
# marks on RENDER canvases must apply the tileset pack scale first (art px = render px * pack)
PACK_SCALE = {"TDBOAT": 0.652}   # clones are marked on their native art canvases (1.0)
HEADINGS = {"N": 0.0, "NE": math.radians(45), "E": math.radians(90)}

def dot_clusters(path, rgb, heading):
    """All pure-rgb pixels, clustered along the heading axis. Returns list of
    (dx, dy) offsets from canvas centre, ordered fore-most first."""
    im = Image.open(path).convert("RGBA")
    px = im.load()
    pts = []
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a > 200 and (r, g, b) == rgb:
                pts.append((x, y))
    if not pts:
        return []
    fwd = (math.sin(heading), -math.cos(heading))          # screen bow direction
    proj = [p[0] * fwd[0] + p[1] * fwd[1] for p in pts]
    cx, cy = im.width / 2, im.height / 2
    if max(proj) - min(proj) < 30:                          # one dot
        groups = [pts]
    else:                                                   # two dots: split at mid-projection
        mid = (max(proj) + min(proj)) / 2
        groups = [[p for p, q in zip(pts, proj) if q >= mid],
                  [p for p, q in zip(pts, proj) if q < mid]]
    out = []
    for g in groups:
        out.append((sum(p[0] for p in g) / len(g) - cx, sum(p[1] for p in g) / len(g) - cy))
    return out

def solve(marks):
    """marks: {heading_rad: (dx, dy)} art-px offsets from canvas centre."""
    hN, hNE, hE = 0.0, math.radians(45), math.radians(90)
    b = marks[hN][0]
    a = marks[hE][0]
    # dy(h) = u(h)*C + L with u(h) = -a*cos(h) + b*sin(h); LSQ over the 3 marks
    us = [(-a * math.cos(h) + b * math.sin(h)) for h in (hN, hNE, hE)]
    dys = [marks[h][1] for h in (hN, hNE, hE)]
    n = len(us)
    su, sy, suu, suy = sum(us), sum(dys), sum(u * u for u in us), sum(u * y for u, y in zip(us, dys))
    denom = n * suu - su * su
    C = (n * suy - su * sy) / denom if abs(denom) > 1e-6 else 0.5
    L = (sy - C * su) / n
    # check NE dx consistency
    pred_ne = (a + b) / math.sqrt(2)
    err = pred_ne - marks[hNE][0]
    return a, b, C, L, err

def table(a, b, C, L):
    rows = []
    for s in range(16):
        h = math.radians(s * 22.5)
        dx = a * math.sin(h) + b * math.cos(h)
        dy = (-a * math.cos(h) + b * math.sin(h)) * C + L
        rows.append((dx, dy))
    return rows

def run(ship, rgb, tag):
    """tag 'fore'/'aft': with two red dots per image, index 0 = fore, 1 = aft."""
    idx = 0 if tag == "fore" else 1
    marks = {}
    for name, h in HEADINGS.items():
        p = f"{BASE}/{ship}/{name}-marked.png"
        if not os.path.exists(p):
            p = f"{BASE}/{ship}/{name}.png"
        cl = dot_clusters(p, rgb, h)
        if len(cl) <= idx:
            print(f"  {ship} {tag}: no dot #{idx+1} in {name} - skipped")
            return
        marks[h] = cl[idx]
    a, b, C, L, err = solve(marks)
    print(f"  {ship} {tag}: a={a:.1f} b={b:.1f} C={C:.3f} L={L:.1f}  (NE dx consistency err {err:.1f}px)")
    print(f"    // {ship} {tag} turret seat, classic px (from Luke's dot marks)")
    print(f"    static const signed char {ship.lower()}_{tag}[16][2] = {{")
    pack = PACK_SCALE.get(ship, 1.0)
    for s, (dx, dy) in enumerate(table(a, b, C, L)):
        cx, cy = dx * pack / PX_PER_CLASSIC, dy * pack / PX_PER_CLASSIC
        print(f"        {{{round(cx):4d}, {round(cy):4d}}},   // {s*22.5:.1f} deg")
    print("    };")

ships = sys.argv[1:] or ["TDBOAT", "TDPT", "TDDD", "TDCA"]
for ship in ships:
    run(ship, (255, 0, 0), "fore")
    if ship == "TDCA":
        run(ship, (255, 0, 0), "aft")   # both TDCA spots are red dots; fore = bow-most
