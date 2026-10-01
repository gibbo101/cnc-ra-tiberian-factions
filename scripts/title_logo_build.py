#!/usr/bin/env python3
"""Install the TIBERIAN FACTIONS title over Red Alert's two front-end copies of its logo.

The launcher draws the RA title from two textures:
  * UI_RA_MAINLOGO.DDS, 1948x552, standalone (main menu, skirmish loading screen). Shipped loose
    in the mod's Data/ART/TEXTURES/SRGB/, it replaces the stock file while the mod is enabled.
  * UI_RA_MAINMENU_LOGO, a 908x257 region of MT_COMMANDBAR_COMMON.TGA (campaign select, loading
    screen). The stock region is a straight downscale of the big logo, so the title is scaled
    the same way and byte-written into the region in place.

Both copies carry colour under their transparent pixels (bled outward from the art) so the
launcher's texture filtering does not draw a dark fringe round the edges.

The title is rendered by title_art.py unless a 1948x552 RGBA PNG is given.

usage: title_logo_build.py <mod Data/ART/TEXTURES/SRGB dir> [title.png]
"""
import hashlib
import os
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import title_art  # noqa: E402

TITLE_SIZE = (1948, 552)
ATLAS = 'MT_COMMANDBAR_COMMON.TGA'
ATLAS_W, ATLAS_H, ATLAS_HDR = 6871, 6716, 18
LOGO_REGION = (4788, 94, 908, 257)


def bleed(img):
    """Fill the RGB under fully transparent pixels with the colour of the nearest art."""
    px = np.asarray(img.convert('RGBA')).copy()
    todo = px[..., 3] == 0
    pm = img.convert('RGBa')
    for radius in (1, 2, 4, 8, 16, 32, 64, 128):
        if not todo.any():
            break
        near = np.asarray(pm.filter(ImageFilter.GaussianBlur(radius)).convert('RGBA'))
        fill = todo & (near[..., 3] > 0)
        px[fill, :3] = near[fill, :3]
        todo &= ~fill
    px[todo, :3] = px[~todo, :3].mean(0).astype(np.uint8) if (~todo).any() else 0
    return Image.fromarray(px, 'RGBA')


def scale(img, size):
    return img.convert('RGBa').resize(size, Image.LANCZOS).convert('RGBA')


def dds_bytes(img):
    """Uncompressed A8R8G8B8 DDS, no mips: the stock UI_RA_MAINLOGO.DDS layout."""
    w, h = img.size
    header = struct.pack('<4s7I44x', b'DDS ', 124, 0x100F, h, w, w * 4, 0, 0)
    header += struct.pack('<2I4s5I', 32, 0x41, b'\0\0\0\0', 32,
                          0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
    header += struct.pack('<5I', 0x1000, 0, 0, 0, 0)
    r, g, b, a = img.split()
    return header + Image.merge('RGBA', (b, g, r, a)).tobytes()


def paint_atlas(path, img, region):
    x0, y0, w, h = region
    rows = Image.merge('RGBA', img.split()[2::-1] + (img.getchannel('A'),)).tobytes()
    with open(path, 'r+b') as f:
        for yy in range(h):
            f.seek(ATLAS_HDR + ((ATLAS_H - 1 - (y0 + yy)) * ATLAS_W + x0) * 4)
            f.write(rows[yy * w * 4:(yy + 1) * w * 4])


def md5(path):
    return hashlib.md5(open(path, 'rb').read()).hexdigest()


def main(srgb_dir, title_path=None):
    title = Image.open(title_path).convert('RGBA') if title_path else title_art.render()
    if title.size != TITLE_SIZE:
        sys.exit(f'title is {title.size}, expected {TITLE_SIZE}')
    dds = os.path.join(srgb_dir, 'UI_RA_MAINLOGO.DDS')
    with open(dds, 'wb') as f:
        f.write(dds_bytes(bleed(title)))
    atlas = os.path.join(srgb_dir, ATLAS)
    paint_atlas(atlas, bleed(scale(title, LOGO_REGION[2:])), LOGO_REGION)
    for p in (dds, atlas):
        print(md5(p), p)


if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
