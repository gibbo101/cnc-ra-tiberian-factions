#!/usr/bin/env python3
"""Paint faction emblem plates over the country flags in the lobby picker icons.

The RA lobby picker icon for a faction is a preloaded atlas region (`FACTIONS.XML` SmallIconName,
only the UI_MULTIPLAYER_PLAYERSLOT_FACTION_NN regions are safe). GDI uses _03, Nod _10, Allies
_04, Soviet _05, and the country duplicates _06.._09; each has _ON / _OVER variants. The region is a 150x80
parallelogram: a flag on the left, the side crest badge on the right. The region becomes the faction's
radar crest alone, centred, on a transparent plate: no flag, no badge, no field (Luke, 2026-09-02). Byte-edits the target atlases in place, same size.

usage: picker_emblems_paint.py <target MT_COMMANDBAR_COMMON.TGA> [more targets...]
"""
import hashlib
import re
import struct
import sys

from PIL import Image, ImageFilter

MTD = 'scripts/cameo_work/MT_COMMANDBAR_COMMON.MTD'
PRISTINE = 'scripts/cameo_work/MT_COMMANDBAR_COMMON.TGA'
W, H, HDR = 6871, 6716, 18
def _variants(nn):
    b = 'UI_MULTIPLAYER_PLAYERSLOT_FACTION_%s' % nn
    return [b, b + '_ON', b + '_OVER']


# picker region -> (emblem source region, field colour). Rows follow the launcher's country
# order: _03 Spain = GDI, _04 Greece = Nod (DLL remap), _05 USSR = Soviet, _06 England = Allies,
# _07 Ukraine = Soviet duplicate, _08 Germany / _09 France / _10 Turkey = Allied duplicates.
PLATE_RED = (150, 14, 14)   # unused: red plates looked wrong on the dropdown's black panel (Luke, 2026-09-02)
SLOTS = {}
for nn in ('03',):
    SLOTS[nn] = ('UI_SIDEBAR_FACTIONLOGO_GDI', None)
for nn in ('04',):
    SLOTS[nn] = ('UI_SIDEBAR_FACTIONLOGO_NOD', None)
for nn in ('10', '06', '08', '09'):
    SLOTS[nn] = ('UI_SIDEBAR_FACTIONLOGO_ALLIES', None)
for nn in ('05', '07'):
    SLOTS[nn] = ('UI_SIDEBAR_FACTIONLOGO_SOVIET', None)


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
    """src = pristine flag region; replace every opaque pixel with the field, then centre the logo."""
    out = src.copy()
    px = out.load()
    w, h = out.size
    for yy in range(h):
        for xx in range(w):
            r, g, b, a = px[xx, yy]
            if field is None:
                px[xx, yy] = (0, 0, 0, 0)          # emblem only, no plate
            elif a > 0:
                px[xx, yy] = (field[0], field[1], field[2], a)
    # logo: gold line art with alpha; fit to ~66 px high, centred in the whole shape
    lg = logo.copy()
    lg.thumbnail((w - 40, 72), Image.LANCZOS)
    # The launcher draws the plate at roughly a third of this size with no mip filtering, so
    # soften the fine metallic detail a touch or it aliases into speckle in the list.
    lg = lg.filter(ImageFilter.GaussianBlur(0.7))
    ox = (w - lg.width) // 2
    oy = (h - lg.height) // 2
    tmp = Image.new('RGBA', out.size, (0, 0, 0, 0))
    tmp.paste(lg, (ox, oy), lg)
    if field is not None:
        mask = out.split()[3]      # keep the emblem inside the parallelogram
        tmp.putalpha(Image.composite(tmp.split()[3], Image.new('L', out.size, 0), mask))
    out.alpha_composite(tmp)
    return out


def main(targets):
    regs = regions()
    src = open(PRISTINE, 'rb')
    rows = []
    preview = []
    logos = {}
    for nn, (logo_region, field) in SLOTS.items():
        if logo_region not in logos:
            logos[logo_region] = read_region(src, regs[logo_region])
        logo = logos[logo_region]
        for slot in _variants(nn):
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
    cols = 6
    sheet = Image.new('RGBA', (cols * 160, ((len(preview) + cols - 1) // cols) * 90), (0, 110, 0, 255))
    for i, im in enumerate(preview):
        sheet.paste(im, ((i % cols) * 160, (i // cols) * 90 + 5), im)
    sheet.save('/tmp/picker_preview.png')
    print('preview /tmp/picker_preview.png')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1:])
