#!/usr/bin/env python3
"""Compose the mod logo: the TIBERIAN FACTIONS title over a 3x2 grid of faction emblems.

Square, on a dark radial backdrop, for the Workshop preview, ModDB and the README. Columns are the
eras (RA, TD, TS); the top row is the GDI side (Allied, GDI, TS GDI), the bottom row the enemies
(Soviet, Nod, TS Nod). TS GDI's gold coin is toned down to sit with the others, and TS Nod is a
blacked-out silhouette with a faint red rim until that faction is playable.

usage: logo_art.py <out.png> [emblem height, default 280] [--size N]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageEnhance, ImageFilter

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import title_art  # noqa: E402

EMBLEMS = SCRIPT_DIR / 'tab_emblems'
W = 1200
COLS = [240, 600, 960]
ROWS = [590, 960]
CELLS = [('allied.png', 0, 0, 1.0), ('gdi.png', 1, 0, 0.95), ('tsgdi.png', 2, 0, 0.92),
         ('soviet.png', 0, 1, 1.0), ('nod.png', 1, 1, 1.0), ('tsnod.png', 2, 1, 1.0)]


def backdrop():
    yy, xx = np.mgrid[0:W, 0:W]
    d = np.clip(np.hypot(xx - W / 2, yy - W / 2) / 850, 0, 1)
    c0, c1 = np.array([44, 46, 54]), np.array([20, 21, 26])
    return Image.fromarray((c0 * (1 - d[..., None]) + c1 * d[..., None]).astype('uint8')).convert('RGBA')


def load(name, h):
    e = Image.open(EMBLEMS / name).convert('RGBA')
    s = h / max(e.size)
    return e.resize((round(e.width * s), round(e.height * s)), Image.LANCZOS)


def put(img, e, cx, cy):
    x, y = cx - e.width // 2, cy - e.height // 2
    sh = Image.new('RGBA', e.size, (0, 0, 0, 0))
    sh.putalpha(e.getchannel('A').point(lambda v: int(v * 0.75)))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)), (x + 6, y + 12))
    img.alpha_composite(e, (x, y))


def tame(e, sat, bright):
    a = e.getchannel('A')
    rgb = ImageEnhance.Brightness(ImageEnhance.Color(e.convert('RGB')).enhance(sat)).enhance(bright)
    rgb.putalpha(a)
    return rgb


def blackout(e):
    """A dark silhouette keeping a ghost of the emblem's relief, with a thin red rim light."""
    a = e.getchannel('A')
    lum = np.array(e.convert('L')).astype(float)
    lo, hi = np.percentile(lum[np.array(a) > 128], [5, 95])
    body = (14 + ((lum - lo) / (hi - lo)).clip(0, 1) * 38).astype('uint8')
    sil = Image.merge('RGBA', [Image.fromarray(body)] * 3 + [a])
    rim = ImageChops.subtract(a, a.filter(ImageFilter.MinFilter(7))).filter(ImageFilter.GaussianBlur(1.2))
    glow = Image.new('RGBA', e.size, (150, 40, 40, 0))
    glow.putalpha(rim.point(lambda v: int(v * 0.55)))
    sil.alpha_composite(glow)
    return sil


def compose(emblem_h=280):
    img = backdrop()
    for name, c, r, k in CELLS:
        e = load(name, int(emblem_h * k))
        if name == 'tsgdi.png':
            e = tame(e, 0.80, 0.90)
        if name == 'tsnod.png':
            e = blackout(e)
        put(img, e, COLS[c], ROWS[r])
    t = title_art.render()
    t = t.resize((1150, round(t.height * 1150 / t.width)), Image.LANCZOS)
    sh = Image.new('RGBA', t.size, (0, 0, 0, 0))
    sh.putalpha(t.getchannel('A').point(lambda v: int(v * 0.6)))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), (25 + 4, 40 + 10))
    img.alpha_composite(t, (25, 40))
    return img.convert('RGB')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('out')
    ap.add_argument('emblem_h', nargs='?', type=int, default=280)
    ap.add_argument('--size', type=int, help='resample the square to N x N')
    opt = ap.parse_args()
    img = compose(opt.emblem_h)
    if opt.size:
        img = img.resize((opt.size, opt.size), Image.LANCZOS)
    img.save(opt.out)
