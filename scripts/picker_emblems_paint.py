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
import os
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
for nn in ('10', '06', '09'):
    SLOTS[nn] = ('UI_SIDEBAR_FACTIONLOGO_ALLIES', None)
# _08 (Germany) is the Tiberian Sun GDI row when the fifth faction is switched on. Its
# emblem has no atlas region to borrow, so the source is our own art file; a 'file:' key is
# read from disk instead. With TF_TS_GDI_FACTION=0 the row is an Allied duplicate again and
# wears the Allied crest, matching a DLL built with the faction compiled out.
if os.environ.get('TF_TS_GDI_FACTION', '1') != '0':
    SLOTS['08'] = ('file:scripts/tab_emblems/tsgdi.png', None)
else:
    SLOTS['08'] = ('UI_SIDEBAR_FACTIONLOGO_ALLIES', None)
for nn in ('05', '07'):
    SLOTS[nn] = ('UI_SIDEBAR_FACTIONLOGO_SOVIET', None)

# The lobby's start-position markers on the map preview are UI_MAPSELECT_FACTION_NN, 40x40
# circle badges indexed one above the picker plates (_01 GDI, _02 Nod, _03 Spain .. _10 Turkey).
# Same emblem per country as the plate, filling the badge.
MAP_SLOTS = {nn: SLOTS[nn][0] for nn in SLOTS}


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


def read_logo(f, regs, key):
    """Emblem source: an atlas region name, or 'file:<path>' for art of our own."""
    if key.startswith('file:'):
        img = Image.open(key[5:]).convert('RGBA')
        return img.crop(img.getbbox())
    return read_region(f, regs[key])


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
    lg = logo.crop(logo.getbbox())       # drop the crest's transparent margins first
    lg.thumbnail((w - 4, h), Image.LANCZOS)  # the plate's full height: the box fits the plate by width, so height is the only lever
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


BADGE_DISC = 22   # the base flag badge's opaque disc within the 40x40 slot; the launcher draws the
                  # player-colour ring behind it, so the crest must stay inside the disc


def compose_badge(size, logo):
    lg = logo.crop(logo.getbbox())
    lg.thumbnail((BADGE_DISC, BADGE_DISC), Image.LANCZOS)
    lg = lg.filter(ImageFilter.GaussianBlur(0.3))
    out = Image.new('RGBA', size, (0, 0, 0, 0))
    out.paste(lg, ((size[0] - lg.width) // 2, (size[1] - lg.height) // 2), lg)
    return out


def paint_rows(rows, rect, img):
    x0, y0 = rect[0], rect[1]
    px = img.load()
    for yy in range(img.height):
        b = bytearray()
        for xx in range(img.width):
            r, g, bb, a = px[xx, yy]
            b += bytes((bb, g, r, a))
        rows.append((row_off(x0, y0 + yy), bytes(b)))


def main(targets):
    regs = regions()
    src = open(PRISTINE, 'rb')
    rows = []
    preview = []
    logos = {}
    for nn, logo_region in MAP_SLOTS.items():
        if logo_region not in logos:
            logos[logo_region] = read_logo(src, regs, logo_region)
        rect = regs['UI_MAPSELECT_FACTION_' + nn]
        img = compose_badge((rect[2], rect[3]), logos[logo_region])
        preview.append(img)
        paint_rows(rows, rect, img)
    for nn, (logo_region, field) in SLOTS.items():
        if logo_region not in logos:
            logos[logo_region] = read_logo(src, regs, logo_region)
        logo = logos[logo_region]
        for slot in _variants(nn):
            rect = regs[slot]
            img = compose(read_region(src, rect), logo, field)
            preview.append(img)
            paint_rows(rows, rect, img)
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
