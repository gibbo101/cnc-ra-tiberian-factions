"""TS camera helpers for reading geometry off TS's war factory frames (TS px, foundation-centre origin).
x = gx + 24(X - Y)/128,  y = gy + 12(X + Y)/128 - 0.2297 Z   (X east, Y south, Z up; 1 cell = 128)"""
import numpy as np
from PIL import Image, ImageDraw

GX, GY = 108.0, 126.0
KZ = 24 * np.sqrt(2) / 128 * np.cos(np.radians(30))      # 0.2297 px per unit of height
TSDIR = '/home/claude/work/ts/ts-buildings-hd-handoff/06-TSWEAP/ts-original/'


def proj(X, Y, Z=0.0):
    X, Y, Z = np.asarray(X, float), np.asarray(Y, float), np.asarray(Z, float)
    return GX + 24 * (X - Y) / 128, GY + 12 * (X + Y) / 128 - KZ * Z


def unproj_z(x, y, Z=0.0):
    """pixel -> ground position at height Z"""
    a = (x - GX) * 128 / 24          # X - Y
    b = (y - GY + KZ * Z) * 128 / 12  # X + Y
    return (a + b) / 2, (b - a) / 2


def unproj_x(x, y, X):
    """pixel -> (Y, Z) on the plane X = const"""
    Y = X - (x - GX) * 128 / 24
    Z = (GY + 12 * (X + Y) / 128 - y) / KZ
    return Y, Z


def unproj_y(x, y, Y):
    """pixel -> (X, Z) on the plane Y = const"""
    X = Y + (x - GX) * 128 / 24
    Z = (GY + 12 * (X + Y) / 128 - y) / KZ
    return X, Z


def load(name, f):
    return Image.open(f'{TSDIR}{name}/frames/{f:02d}.png').convert('RGBA')


def wire(img, lines, z=8, box=(28, 56, 184, 166), out=None, colors=None, bg=(96, 108, 72, 255), labels=()):
    """draw 3D polylines (lists of (X,Y,Z)) over a TS frame zoomed x z.  pixel centres: TS px (i+0.5)."""
    base = Image.new('RGBA', img.size, bg); base.alpha_composite(img)
    W, H = (box[2] - box[0]) * z, (box[3] - box[1]) * z
    im = base.crop(box).resize((W, H), Image.NEAREST).convert('RGB')
    d = ImageDraw.Draw(im)
    pal = colors or [(255, 0, 255), (0, 255, 255), (255, 255, 0), (255, 128, 0), (255, 255, 255), (255, 60, 60)]
    for i, ln in enumerate(lines):
        pts = [proj(*p) for p in ln]
        pts = [((px - box[0]) * z, (py - box[1]) * z) for px, py in pts]
        d.line(pts, fill=pal[i % len(pal)], width=1)
    for (X, Y, Z, t) in labels:
        px, py = proj(X, Y, Z)
        d.text(((px - box[0]) * z + 3, (py - box[1]) * z - 10), t, fill=(255, 255, 255))
    for x in range(box[0], box[2] + 1):
        if x % 10 == 0:
            d.text(((x - box[0]) * z + 2, 2), str(x), fill=(255, 255, 255))
    for y in range(box[1], box[3] + 1):
        if y % 10 == 0:
            d.text((2, (y - box[1]) * z + 2), str(y), fill=(255, 255, 255))
    if out:
        im.save(out)
    return im


def box3(x0, x1, y0, y1, z0, z1):
    """the 12 edges of an axis box as polylines"""
    P = lambda X, Y, Z: (X, Y, Z)
    L = []
    for Z in (z0, z1):
        L.append([P(x0, y0, Z), P(x1, y0, Z), P(x1, y1, Z), P(x0, y1, Z), P(x0, y0, Z)])
    for X in (x0, x1):
        for Y in (y0, y1):
            L.append([P(X, Y, z0), P(X, Y, z1)])
    return L
