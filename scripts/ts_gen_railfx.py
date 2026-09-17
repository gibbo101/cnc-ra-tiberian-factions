#!/usr/bin/env python3
"""Generate the TS railgun particle art: one small soft spark on a 12-frame colour
ladder, for each of TS's two railgun particle types.

TS draws each railgun particle as a coloured pixel that blends from the first to the
second colour of its ColorList as it ages. The DLL tracks each spark's own blend the
way TS does (anim.cpp Rail_Spark_AI) and shows the frame for it, so the frames are an
even ladder: frame 0 is the start colour, frame 11 the end colour.

  RAILFX     [LargeRailgunPart] (Mammoth Mk. II): (25,70,205) -> (150,150,150).
  TSRAILFXS  [SmallRailgunPart] (Ghost Stalker): (200,200,200) -> (150,150,150).

A new spark also needs its RA_VFX.XML tile run (ts_pack_pods.patch_tileset) and a
classic stub in build_tfassets.sh.

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

# name -> (start colour, end colour)
SPARKS = {
    'RAILFX': ((25, 70, 205), (150, 150, 150)),
    'TSRAILFXS': ((200, 200, 200), (150, 150, 150)),
}


def spark(i, start, end):
    t = i / (FRAMES - 1)
    color = tuple(int(round(start[k] + (end[k] - start[k]) * t)) for k in range(3))
    alpha = ALPHA
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
        start, end = SPARKS[name]
        path = os.path.join(os.path.abspath(outdir), f'{name}.ZIP')
        write_zip(path, name.lower(), [spark(i, start, end) for i in range(FRAMES)])
        print(f'wrote {path} ({FRAMES} frames)')


if __name__ == '__main__':
    main()
