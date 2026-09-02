#!/usr/bin/env python3
"""Paint the Allied and Soviet emblems over the Greece/USSR flags in the lobby picker icons.

The RA lobby picker icon for a faction is a preloaded atlas region (`FACTIONS.XML` SmallIconName,
only the UI_MULTIPLAYER_PLAYERSLOT_FACTION_NN regions are safe). Our Allies entry uses _04
(Greece) and Soviet uses _05 (USSR); each has _ON / _OVER variants. The region is a 150x80
parallelogram: a flag on the left, the side crest badge on the right. This keeps the badge and
the outline, fills the flag area with a dark field, and centres the faction emblem (the lobby's
own gold line-art logos) on it. Byte-edits the target atlases in place, same size.

usage: picker_emblems_paint.py <target MT_COMMANDBAR_COMMON.TGA> [more targets...]
"""
import hashlib
import re
import struct
import sys

from PIL import Image

MTD = 'scripts/cameo_work/MT_COMMANDBAR_COMMON.MTD'
PRISTINE = 'scripts/cameo_work/MT_COMMANDBAR_COMMON.TGA'
W, H, HDR = 6871, 6716, 18
FLAG_W = 104            # flag area of the 150-wide parallelogram at the top row; the badge edge slants
FLAG_SLANT = 21         # extra flag width at the bottom row (the parallelogram leans right)
SLOTS = {
    'ALLIED': (['UI_MULTIPLAYER_PLAYERSLOT_FACTION_04', 'UI_MULTIPLAYER_PLAYERSLOT_FACTION_04_ON',
                'UI_MULTIPLAYER_PLAYERSLOT_FACTION_04_OVER'],
               'RA_UI_MULTIPLAYER_ALLIED_LOGO_LARGE_SELECTED', (24, 44, 96)),
    'SOVIET': (['UI_MULTIPLAYER_PLAYERSLOT_FACTION_05', 'UI_MULTIPLAYER_PLAYERSLOT_FACTION_05_ON',
                'UI_MULTIPLAYER_PLAYERSLOT_FACTION_05_OVER'],
               'RA_UI_MULTIPLAYER_SOVIET_LOGO_LARGE_SELECTED', (110, 18, 18)),
}


def regions():
    mtd = open(MTD, 'rb').read()
    out = {}
    for m in re.finditer(rb'([A-Za-z0-9_]+)\.TGA', mtd):
        j = m.end()
        while mtd[j] == 0:
            j += 1
        x, y, w, h = struct.unpack('<4i', mtd[j:j + 16])
        if 0 < w < 4000 and 0 < h < 4000:
            out[m.group(1).decode().upper()] = (x, y, w, h)
    return out


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


def compose(src, logo, field):
    """src = pristine flag region; replace the flag pixels left of the badge with field + logo."""
    out = src.copy()
    px = out.load()
    w, h = out.size
    for yy in range(h):
        edge = FLAG_W + FLAG_SLANT * yy // max(1, h - 1)
        for xx in range(edge):
            r, g, b, a = px[xx, yy]
            if a > 0:
                px[xx, yy] = (field[0], field[1], field[2], a)
    # logo: gold line art with alpha; fit to ~62 px high, centred in the flag area
    lg = logo.copy()
    lg.thumbnail((FLAG_W - 20, 62), Image.LANCZOS)
    ox = (FLAG_W - lg.width) // 2 + 4
    oy = (h - lg.height) // 2
    mask = out.split()[3]          # only where the region is opaque (keeps the parallelogram)
    tmp = Image.new('RGBA', out.size, (0, 0, 0, 0))
    tmp.paste(lg, (ox, oy), lg)
    tmp.putalpha(Image.eval(tmp.split()[3], lambda a: a).point(lambda v: v))
    tmp_alpha = Image.composite(tmp.split()[3], Image.new('L', out.size, 0), mask)
    tmp.putalpha(tmp_alpha)
    out.alpha_composite(tmp)
    return out


def main(targets):
    regs = regions()
    src = open(PRISTINE, 'rb')
    rows = []
    preview = []
    for name, (slots, logo_region, field) in SLOTS.items():
        logo = read_region(src, regs[logo_region])
        for slot in slots:
            rect = regs[slot]
            img = compose(read_region(src, rect), logo, field)
            preview.append(img)
            x0, y0 = rect[0], rect[1]
            px = img.load()
            for yy in range(img.height):
                b = bytearray()
                for xx in range(img.width):
                    r, g, bb, a = px[xx, yy]
                    b += bytes((bb, g, r, a))
                rows.append((row_off(x0, y0 + yy), bytes(b)))
    for t in targets:
        with open(t, 'r+b') as f:
            for off, b in rows:
                f.seek(off)
                f.write(b)
        print(t, hashlib.md5(open(t, 'rb').read()).hexdigest())
    sheet = Image.new('RGBA', (len(preview) * 160, 90), (0, 110, 0, 255))
    for i, im in enumerate(preview):
        sheet.paste(im, (i * 160, 5), im)
    sheet.save('/tmp/picker_preview.png')
    print('preview /tmp/picker_preview.png')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1:])
