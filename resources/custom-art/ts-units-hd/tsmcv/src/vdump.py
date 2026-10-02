"""MCV.VXL inventory: plan view of the top voxel per column (colour and height), side and front elevations."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
import vxl

from paths import HANDOFF
VXL = HANDOFF + '/11-TSMCV/ts-original/MCV.VXL'
PAL = vxl.read_pal(HANDOFF + '/02-TSSMEC/ts-original/UNITTEM.PAL')
sec = vxl.read_vxl(VXL)[0]
col = sec['col']                       # (x, y, z), -1 empty
X, Y, Z = col.shape


def colour(idx):
    c = PAL[np.clip(idx, 0, 255)].copy()
    house = (idx >= 16) & (idx <= 31)
    c[house] = np.stack([np.zeros(house.sum()), 60 + (31 - idx[house]) * 10, np.zeros(house.sum())], -1)
    return c


def plan(k=12):
    filled = col >= 0
    top = np.where(filled.any(2), Z - 1 - np.argmax(filled[:, :, ::-1], axis=2), -1)
    img = np.zeros((Y, X, 3)); img[:] = (40, 40, 40)
    for x in range(X):
        for y in range(Y):
            t = top[x, y]
            if t >= 0:
                c = colour(np.array([col[x, y, t]]))[0]
                img[y, x] = c * (0.55 + 0.45 * t / (Z - 1))
    im = Image.fromarray(img.clip(0, 255).astype(np.uint8)).resize((X * k, Y * k), Image.NEAREST)
    d = ImageDraw.Draw(im)
    for x in range(0, X, 5):
        d.line([(x * k, 0), (x * k, Y * k)], fill=(90, 90, 90))
    for y in range(0, Y, 5):
        d.line([(0, y * k), (X * k, y * k)], fill=(90, 90, 90))
    return im, top


def elevation(axis, k=12):
    """side (axis=1: looking along y from y=0) or front (axis=0: along x from the front, x max)."""
    filled = col >= 0
    if axis == 1:
        first = np.where(filled.any(1), np.argmax(filled, axis=1), -1)           # (x, z): nearest y
        img = np.zeros((Z, X, 3)); img[:] = (40, 40, 40)
        for x in range(X):
            for z in range(Z):
                y = first[x, z]
                if y >= 0:
                    img[Z - 1 - z, x] = colour(np.array([col[x, y, z]]))[0] * (0.6 + 0.4 * (1 - y / Y))
        return Image.fromarray(img.clip(0, 255).astype(np.uint8)).resize((X * k, Z * k), Image.NEAREST)
    first = np.where(filled.any(0), X - 1 - np.argmax(filled[::-1], axis=0), -1)  # (y, z): frontmost x
    img = np.zeros((Z, Y, 3)); img[:] = (40, 40, 40)
    for y in range(Y):
        for z in range(Z):
            x = first[y, z]
            if x >= 0:
                img[Z - 1 - z, y] = colour(np.array([col[x, y, z]]))[0] * (0.6 + 0.4 * x / X)
    return Image.fromarray(img.clip(0, 255).astype(np.uint8)).resize((Y * k, Z * k), Image.NEAREST)


if __name__ == '__main__':
    p, top = plan()
    s = elevation(1); f = elevation(0)
    W = max(p.size[0], s.size[0] + f.size[0] + 10)
    out = Image.new('RGB', (W, p.size[1] + s.size[1] + 20), (20, 20, 20))
    out.paste(p, (0, 0)); out.paste(s, (0, p.size[1] + 10)); out.paste(f, (s.size[0] + 10, p.size[1] + 10))
    out.save('mcv_views.png')
    print('size', col.shape, 'filled', (col >= 0).sum())
    vals, cnt = np.unique(col[col >= 0], return_counts=True)
    print('colour indices used:', [(int(v), int(c)) for v, c in zip(vals, cnt)])
