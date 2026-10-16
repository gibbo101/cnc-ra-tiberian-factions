#!/usr/bin/env python3
"""Write the encyclopedia's fixed pictures (docs/encyclopedia.md): each faction's logo for its About page,
TF_ENC_ABOUT_<FACTION>.TGA from scripts/tab_emblems/ as the loading screen draws them (logo_art.py), and
TF_ENC_LIVE.TGA, the blank canvas the DLL draws each selected entry's sprite into. 4:3 RLE TGA.

usage: encyclopedia_logos.py <SRGB out dir>
License: GPL v3.
"""
import os
import sys

from PIL import Image

import logo_art

SIZE = (256, 192)   # LIVE_WIDTH, LIVE_HEIGHT in redalert/tf_launcher.cpp
LOGOS = {'ALLIES': 'allied.png', 'SOVIETS': 'soviet.png', 'GDI': 'gdi.png', 'NOD': 'nod.png', 'TSGDI': 'tsgdi.png'}
LOGO_HEIGHT = 160


def logo(faction):
    """A faction's logo with the loading screen's shadow, centred on a SIZE canvas at its own proportions."""
    emblem = logo_art.load(LOGOS[faction], LOGO_HEIGHT)
    if faction == 'TSGDI':
        emblem = logo_art.tame(emblem, 0.80, 0.90)
    out = Image.new('RGBA', SIZE)
    logo_art.put(out, emblem, SIZE[0] // 2, SIZE[1] // 2 - 4)
    return out


def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for faction in LOGOS:
        logo(faction).save(os.path.join(out_dir, f'TF_ENC_ABOUT_{faction}.TGA'), compression='tga_rle')
    Image.new('RGBA', SIZE).save(os.path.join(out_dir, 'TF_ENC_LIVE.TGA'), compression='tga_rle')
    print(f'wrote {len(LOGOS)} logos and the live canvas in {out_dir}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
