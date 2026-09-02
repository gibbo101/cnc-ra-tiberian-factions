#!/usr/bin/env python3
"""Paint the radar-crest art the DLL's crest patch relies on into a shipped MT_COMMANDBAR_COMMON.TGA.

The per-faction radar crest (docs/radar-crest-ram-spike.md) re-points ClientG's cached region
records at atlas regions, so the shipped atlas must hold:
  * the PRISTINE Allied / Soviet crests in UI_SIDEBAR_FACTIONLOGO_ALLIES / _SOVIET (the old
    C&C-logo-for-all paint is retired), and
  * an aspect-correct GDI eagle (scaled to EAGLE_H high, centred horizontally and TOP-aligned in
    a 495x444 window = the slot's 794:713, so it clears the launcher's "GDI" label drawn over the
    bottom of the slot) in the top-left of the never-referenced UI_SIDEBAR_FACTIONLOGO_DINO
    region, which is the rect the DLL points the GDI crest at (TF_Crest_Slots: {2154, 1900, 495, 444}).

Byte-edits the target in place (same size, format-identical). Source of truth for the pristine
pixels is the base atlas kept at scripts/cameo_work/MT_COMMANDBAR_COMMON.TGA.

usage: crest_atlas_paint.py <target MT_COMMANDBAR_COMMON.TGA> [more targets...]
"""
import hashlib
import sys

from PIL import Image

PRISTINE = 'scripts/cameo_work/MT_COMMANDBAR_COMMON.TGA'
W, H, HDR = 6871, 6716, 18
ALLIES = (5698, 1706, 794, 713)
SOVIET = (2684, 1709, 794, 713)
GDI = (1, 1875, 718, 706)


def row_off(x, y):
    return HDR + (H - 1 - y) * W * 4 + x * 4


def read_region(f, rect):
    x, y, w, h = rect
    img = Image.new('RGBA', (w, h))
    px = img.load()
    for yy in range(h):
        f.seek(row_off(x, y + yy))
        b = f.read(w * 4)
        for xx in range(w):
            B, G, R, A = b[xx * 4:xx * 4 + 4]
            px[xx, yy] = (R, G, B, A)
    return img


def rows_of(img, origin):
    x0, y0 = origin
    px = img.load()
    out = []
    for yy in range(img.height):
        b = bytearray()
        for xx in range(img.width):
            r, g, bb, a = px[xx, yy]
            b += bytes((bb, g, r, a))
        out.append((row_off(x0, y0 + yy), bytes(b)))
    return out


def main(targets):
    src = open(PRISTINE, 'rb')
    rows = []
    for rect in (ALLIES, SOVIET):
        x, y, w, h = rect
        for yy in range(h):
            src.seek(row_off(x, y + yy))
            rows.append((row_off(x, y + yy), src.read(w * 4)))
    for t in targets:
        with open(t, 'r+b') as f:
            for off, b in rows:
                f.seek(off)
                f.write(b)
        print(t, hashlib.md5(open(t, 'rb').read()).hexdigest())


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1:])
