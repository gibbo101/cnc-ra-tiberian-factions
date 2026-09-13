#!/usr/bin/env python3
"""Generate the TS railgun particle art: one small soft spark on a 12-frame colour
ladder, for each of TS's two railgun particle types.

TS draws each railgun particle as a coloured pixel that walks its ColorList at
ColorSpeed per frame (+0..0.05 random), then holds the end colour until MaxEC=70
frames (~2.3 s at the ~30 fps of Luke's TS). Here the stage timer does the
walking: adata.cpp gives each spark 12 stages at 4 ticks (= 48 ticks, 1.2 s at
~40 tick/s -- half TS's life, so the coil is gone before the 1.5 s refire).

  RAILFX     [LargeRailgunPart] (Mammoth Mk. II): (25,70,205) -> (150,150,150) at
             ColorSpeed .009, so frames 0-4 fade blue->grey (0.5 s).
  TSRAILFXS  [SmallRailgunPart] (Ghost Stalker): (200,200,200) -> (150,150,150) at
             ColorSpeed .03, three times faster, so frames 0-1 fade.

Frames up to the fade end hold the end colour and frame 11 dims out. A new spark
also needs its RA_VFX.XML tile run (ts_pack_pods.patch_tileset) and a classic stub
in build_tfassets.sh.

Usage:  ts_gen_railfx.py [OUTDIR] [NAME ...]      default: every spark
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

# name -> (start colour, end colour, frames the fade takes)
SPARKS = {
    'RAILFX': ((25, 70, 205), (150, 150, 150), 5),
    'TSRAILFXS': ((200, 200, 200), (150, 150, 150), 2),
}


def spark(i, start, end, fade_frames):
    t = i / (fade_frames - 1) if i < fade_frames else 1.0
    color = tuple(int(round(start[k] + (end[k] - start[k]) * t)) for k in range(3))
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
    for name in (sys.argv[2:] or list(SPARKS)):
        start, end, fade = SPARKS[name]
        path = os.path.join(os.path.abspath(outdir), f'{name}.ZIP')
        write_zip(path, name.lower(), [spark(i, start, end, fade) for i in range(FRAMES)])
        print(f'wrote {path} ({FRAMES} frames)')


if __name__ == '__main__':
    main()
