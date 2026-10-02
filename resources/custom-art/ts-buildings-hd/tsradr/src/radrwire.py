"""Wireframe overlays for reading the radar's geometry off TS's frames (TS px, ground centre (72, 96)).
    python3 radrwire.py <frame spec, e.g. GTRADR/00[+GTRADR_A/00]> <out.png> [zoom 8] [x0 y0 x1 y1]
Primitives come from WIRE below (edit and rerun)."""
import sys
import numpy as np
from PIL import Image, ImageDraw
import radrgeo as G
from tsgeo import proj

BG = (96, 108, 72, 255)


def boxl(x0, x1, y0, y1, z0, z1):
    L = []
    for Z in (z0, z1):
        L.append([(x0, y0, Z), (x1, y0, Z), (x1, y1, Z), (x0, y1, Z), (x0, y0, Z)])
    for X in (x0, x1):
        for Y in (y0, y1):
            L.append([(X, Y, z0), (X, Y, z1)])
    return L


def polyl(pts, z0, z1):
    L = [[(x, y, z0) for x, y in list(pts) + [pts[0]]], [(x, y, z1) for x, y in list(pts) + [pts[0]]]]
    for x, y in pts:
        L.append([(x, y, z0), (x, y, z1)])
    return L


def circ(cx, cy, r, z, n=48):
    t = np.linspace(0, 2 * np.pi, n + 1)
    return [[(cx + r * np.cos(a), cy + r * np.sin(a), z) for a in t]]


def cyl(cx, cy, r, z0, z1, n=48):
    return circ(cx, cy, r, z0, n) + circ(cx, cy, r, z1, n)


def draw(spec, out, z=8, box=None, wires=()):
    im = Image.new('RGBA', (144, 144), BG)
    for s in spec.split('+'):
        n, f = s.split('/')
        im.alpha_composite(G.load(n, int(f)))
    box = box or (24, 0, 120, 122)
    W, H = (box[2] - box[0]) * z, (box[3] - box[1]) * z
    big = im.crop(box).resize((W, H), Image.LANCZOS).convert('RGB')
    d = ImageDraw.Draw(big)
    pal = [(255, 0, 255), (0, 255, 255), (255, 255, 0), (255, 128, 0), (255, 255, 255), (255, 60, 60), (60, 160, 255)]
    for i, (name, lines) in enumerate(wires):
        col = pal[i % len(pal)]
        for ln in lines:
            pts = [proj(*p) for p in ln]
            d.line([((px - box[0]) * z, (py - box[1]) * z) for px, py in pts], fill=col, width=1)
        px, py = proj(*lines[0][0])
        d.text(((px - box[0]) * z + 3, (py - box[1]) * z - 11), name, fill=col)
    for x in range(box[0], box[2] + 1):
        if x % 10 == 0:
            d.text(((x - box[0]) * z + 2, 2), str(x), fill=(255, 255, 255))
    for y in range(box[1], box[3] + 1):
        if y % 10 == 0:
            d.text((2, (y - box[1]) * z + 2), str(y), fill=(255, 255, 255))
    big.save(out)
