#!/usr/bin/env python3
"""Paint the TD sidebar pieces RA has no twin for, into atlas space the RA launcher never draws.

The RAM patch (docs/radar-crest-ram-spike.md) re-points RA's cached region records at TD art
already in MT_COMMANDBAR_COMMON.TGA. Two RA pieces have no same-named TD region, so their TD
look is painted here, over TD front-end regions that have an RA-prefixed twin (this launcher
draws the twin, never these):

  RAIL   UI_WORKSHOP_MAP_FRAME (5698,2474): a 500x500 stand-in for RA's 868x868 radar bezel,
         transparent above and TD's sell/repair rail (UI_SIDEBAR_SELLREPAIRBG) across the
         bottom 12%, where RA's own rail with the bolts sat. TD's plate under it carries the frame.
  FILLS  UI_BONUSBUTTONHIGHLIGHT (5698,94): three 905x31 flat strips (green, red, yellow) that
         stand in for RA's rounded fill tubes. The fill draws OVER the background, so the strips
         are translucent: TD's background pips read through them as lit, the gaps stay dark.
  PLATE  UI_OBSERVER_MAP_BG (4220,2883): a 434x422 stand-in for the 868x868 radar under-screen:
         TD's plate (UI_SIDEBAR_RADARBG) scaled into the top 86%, sidebar metal below, so the
         plate's bottom frame edge clears the rail instead of running under it.

The DLL points the bezel and the three fill records at these rects for GDI/Nod (TF_Crest_Slots).
Byte-edits the targets in place, same size.

usage: td_sidebar_extras_paint.py <target MT_COMMANDBAR_COMMON.TGA> [more targets...]
"""
import hashlib
import sys

from PIL import Image

sys.path.insert(0, 'scripts')
from picker_emblems_paint import regions, read_region, row_off, PRISTINE  # noqa: E402

RAIL_AT = (5698, 2474)
RAIL_SIZE = 500
RAIL_TOP = round(761 / 868 * RAIL_SIZE)   # RA's bezel rail starts at row 761 of 868
FILLS_AT = (5698, 94)
FILL_W, FILL_H = 905, 31
FILL_ALPHA = 150
FILL_COLOURS = [(70, 165, 35), (190, 40, 30), (205, 175, 30)]   # green, red, yellow (TD's lit green sampled in-game)
PLATE_AT = (4220, 2883)
PLATE_SIZE = (434, 422)
GAP_METAL = (44, 48, 52)
PLATE_ROWS = round(422 * 746 / 868)   # plate spans rows 0..746 of the 868 slot: native 763 aspect, clear of the rail


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
    regs = regions()
    src = open(PRISTINE, 'rb')
    rail_src = read_region(src, regs['UI_SIDEBAR_SELLREPAIRBG'])
    rail = Image.new('RGBA', (RAIL_SIZE, RAIL_SIZE), (0, 0, 0, 0))
    rail.paste(rail_src.resize((RAIL_SIZE, RAIL_SIZE - RAIL_TOP), Image.LANCZOS), (0, RAIL_TOP))
    rows = rows_of(rail, RAIL_AT)
    for k, colour in enumerate(FILL_COLOURS):
        strip = Image.new('RGBA', (FILL_W, FILL_H), colour + (FILL_ALPHA,))
        rows += rows_of(strip, (FILLS_AT[0], FILLS_AT[1] + k * FILL_H))
    plate_src = read_region(src, regs['UI_SIDEBAR_RADARBG'])
    # Below the plate nothing else draws (RA's bezel used to cover this band), so the rest of
    # the piece is opaque sidebar metal, sampled from TD's own gap between plate and rail.
    plate = Image.new('RGBA', PLATE_SIZE, GAP_METAL + (255,))
    plate.paste(plate_src.resize((PLATE_SIZE[0], PLATE_ROWS), Image.LANCZOS), (0, 0))
    rows += rows_of(plate, PLATE_AT)
    for t in targets:
        with open(t, 'r+b') as f:
            for off, b in rows:
                f.seek(off)
                f.write(b)
        print(t, hashlib.md5(open(t, 'rb').read()).hexdigest())
    rail.save('/tmp/td_rail_preview.png')
    print('plate rect', PLATE_AT + PLATE_SIZE)
    print('rail rect', RAIL_AT + (RAIL_SIZE, RAIL_SIZE), 'fill rects',
          [(FILLS_AT[0], FILLS_AT[1] + k * FILL_H, FILL_W, FILL_H) for k in range(3)])


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1:])
