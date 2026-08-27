#!/usr/bin/env python3
"""Generate the TS railgun particle art (RAILFX.ZIP): one small soft spark on a
12-frame colour ladder.

TS ([LargeRailgunPart]) draws each railgun particle as a coloured pixel that
walks ColorList (25,70,205)->(150,150,150) at ColorSpeed=.009 (+0..0.05 random
per frame, so ~1 s), then holds grey until MaxEC=70 frames (~2.3 s at the
~30 fps of Luke's TS). Here the stage timer does the walking: adata.cpp gives
RAILFX 12 stages at 4 ticks (= 48 ticks, 1.2 s at ~40 tick/s -- half TS's
life, so the coil is gone before the 1.5 s refire); frames 0-4 fade blue->grey
(0.5 s), 5-10 hold grey, 11 dims out.

Usage:  ts_gen_railfx.py [OUTDIR]
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ts_gen_sonicwave import write_zip

CANVAS = 128
FRAMES = 12
DIAMETER = 12.0        # ~2.25 classic px: a TS pixel with a little HD body
EDGE_SOFT = 1.5
ALPHA = 220
BLUE = (25, 70, 205)
GREY = (150, 150, 150)
FADE_FRAMES = 5        # blue -> grey across frames 0..4


def spark(i):
    if i < FADE_FRAMES:
        t = i / (FADE_FRAMES - 1)
    else:
        t = 1.0
    color = tuple(int(round(BLUE[k] + (GREY[k] - BLUE[k]) * t)) for k in range(3))
    alpha = ALPHA if i < FRAMES - 1 else ALPHA // 2
    ss = 4
    big = Image.new('L', (CANVAS * ss, CANVAS * ss), 0)
    d = ImageDraw.Draw(big)
    c = CANVAS * ss / 2.0
    r = DIAMETER * ss / 2.0
    d.ellipse([c - r, c - r, c + r, c + r], fill=255)
    mask = big.resize((CANVAS, CANVAS), Image.LANCZOS).filter(ImageFilter.GaussianBlur(EDGE_SOFT))
    out = Image.new('RGBA', (CANVAS, CANVAS), color + (0,))
    out.putalpha(mask.point(lambda v: v * alpha // 255))
    return out


def main():
    mod = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                       'resources', 'remaster_mods', 'Vanilla_RA', 'Data')
    outdir = sys.argv[1] if len(sys.argv) > 1 else (
        os.path.join(mod, 'ART', 'TEXTURES', 'SRGB', 'RED_ALERT', 'VFX'))
    path = os.path.join(os.path.abspath(outdir), 'RAILFX.ZIP')
    write_zip(path, 'railfx', [spark(i) for i in range(FRAMES)])
    print(f'wrote {path} ({FRAMES} frames)')


if __name__ == '__main__':
    main()
