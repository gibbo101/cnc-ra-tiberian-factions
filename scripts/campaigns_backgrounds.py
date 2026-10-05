#!/usr/bin/env python3
"""Paint the CAMPAIGNS page backgrounds (docs/campaigns-page.md): TD's steel frame rebuilt in the
two-column layout with see-through boxes, and the green scanline underlays beneath them.

usage: campaigns_backgrounds.py <dir with the stock UI_MISSIONSELECT_BG and UI_LOADGAME_BG_SCANLINES .DDS> <out dir>
"""
import os
import random
import struct
import sys

from PIL import Image, ImageFilter

FRAME_SOURCE = 'UI_MISSIONSELECT_BG'
SCANLINE_SOURCE = 'UI_LOADGAME_BG_SCANLINES'
UNDERLAYS = ('RA_UI_MISSIONSELECT_BG_BLUE', 'RA_UI_MISSIONSELECT_BG_RED')
SCANLINES = ('RA_UI_MISSIONSELECT_SCANLINES_BLUE', 'RA_UI_MISSIONSELECT_SCANLINES_RED')

# Stock TD geometry, texture pixels.
PANEL = (63, 219, 1041, 1376)
LIST_BOX = (77, 390, 1023, 1346)
LIST_HOLE = (97, 410, 1003, 1326)
BRIEF_HOLE = (1127, 786, 2013, 1117)
CONTROLS = (1150, 1138, 1980, 1302)
CLEAN_PANEL = (600, 255, 1000, 385)
CLEAN_FRAME = (300, 1386, 1800, 1494)
UNDERLAY_FILL = (14, 18, 16, 255)

# CAMPAIGNS layout, texture pixels; campaigns_screen.py places the widgets on it.
TOP = 520
NEW_PANELS = [(62, 217, 2060, 498), (62, TOP, 1042, 1376), (1080, TOP, 2060, 1376)]
NEW_LIST_BOX = (81, 640, 1019, 1342)
NEW_BRIEF_BOX = (1101, 662, 2039, 1120)
NEW_CONTROLS_AT = (1155, 1132)


def read_dds(path):
    b = open(path, 'rb').read()
    h, w = struct.unpack_from('<II', b, 12)
    return b[:128], Image.frombuffer('RGBA', (w, h), b[128:128 + w * h * 4], 'raw', 'BGRA', 0, 1).copy()


def write_dds(path, header, img):
    w, h = img.size
    hdr = bytearray(header)
    struct.pack_into('<III', hdr, 12, h, w, w * 4)
    open(path, 'wb').write(bytes(hdr) + img.tobytes('raw', 'BGRA'))


def tile(src, size):
    out = Image.new('RGBA', size)
    for y in range(0, size[1], src.height):
        for x in range(0, size[0], src.width):
            piece = src
            if (x // src.width) % 2:
                piece = piece.transpose(Image.FLIP_LEFT_RIGHT)
            if (y // src.height) % 2:
                piece = piece.transpose(Image.FLIP_TOP_BOTTOM)
            out.paste(piece, (x, y))
    return out


def quilt(src, size, patch=160, seed=1):
    """Fill `size` with randomly placed `patch`-square crops of `src`, feathered so no seam or
    mirror symmetry shows."""
    rnd = random.Random(seed)
    out = tile(src, size)
    mask = Image.new('L', (patch, patch), 0)
    edge = patch // 5
    mask.paste(255, (edge, edge, patch - edge, patch - edge))
    mask = mask.filter(ImageFilter.GaussianBlur(edge / 2))
    step = patch * 3 // 5
    for y in range(-edge, size[1], step):
        for x in range(-edge, size[0], step):
            sx = rnd.randint(0, src.width - patch)
            sy = rnd.randint(0, max(0, src.height - patch))
            piece = src.crop((sx, sy, sx + patch, sy + min(patch, src.height)))
            if piece.height < patch:
                piece = piece.resize((patch, patch))
            out.paste(piece, (x + rnd.randint(-8, 8), y + rnd.randint(-8, 8)), mask)
    return out


def run(src, crop, length, horizontal):
    """`crop` of `src` repeated (not stretched) to `length` along one axis."""
    piece = src.crop(crop)
    w, h = piece.size
    out = Image.new('RGBA', (length, h) if horizontal else (w, length))
    step = w if horizontal else h
    for at in range(0, length, step):
        out.paste(piece, (at, 0) if horizontal else (0, at))
    return out


def nine_slice(src, box, size, corners, edges, spans, centre=None):
    """Rebuild box `box` of `src` at `size`: `corners` (w, top h, bottom h) kept whole, `edges`
    (left, top, right, bottom) strips cut from the clean `spans` (x0, x1, y0, y1) and repeated."""
    x0, y0, x1, y1 = box
    cw, cth, cbh = corners
    lt, tt, rt, bt = edges
    w, h = size
    out = Image.new('RGBA', size, (0, 0, 0, 0))
    if centre is not None:
        out.paste(quilt(centre, size), (0, 0))
    ex0, ex1, ey0, ey1 = spans
    pieces = [(run(src, (ex0, y0, ex1, y0 + tt), w, True), (0, 0)),
              (run(src, (ex0, y1 - bt, ex1, y1), w, True), (0, h - bt)),
              (run(src, (x0, ey0, x0 + lt, ey1), h, False), (0, 0)),
              (run(src, (x1 - rt, ey0, x1, ey1), h, False), (w - rt, 0)),
              (src.crop((x0, y0, x0 + cw, y0 + cth)), (0, 0)),
              (src.crop((x1 - cw, y0, x1, y0 + cth)), (w - cw, 0)),
              (src.crop((x0, y1 - cbh, x0 + cw, y1)), (0, h - cbh)),
              (src.crop((x1 - cw, y1 - cbh, x1, y1)), (w - cw, h - cbh))]
    inner = {(0, 0): 'rb', (1, 0): 'lb', (0, 1): 'rt', (1, 1): 'lt'}
    for k, (piece, at) in enumerate(pieces):
        if centre is None:
            out.paste(piece, at)
        elif k < 4:
            out.alpha_composite(piece, at)
        else:
            corner = ((k - 4) % 2, (k - 4) // 2)
            out.paste(piece, at, feather(piece.size, inner[corner]))
    return out


def feather(size, sides, ramp=18):
    """An L mask of `size` ramping from 0 to 255 over `ramp` px on the given sides ('l','t','r','b')."""
    w, h = size
    mask = Image.new('L', size, 255)
    px = mask.load()
    for y in range(h):
        for x in range(w):
            d = ramp
            if 'l' in sides:
                d = min(d, x)
            if 'r' in sides:
                d = min(d, w - 1 - x)
            if 't' in sides:
                d = min(d, y)
            if 'b' in sides:
                d = min(d, h - 1 - y)
            if d < ramp:
                px[x, y] = 255 * d // ramp
    return mask


def size_of(r):
    return (r[2] - r[0], r[3] - r[1])


def build_frame(stock):
    out = stock.copy()
    zone = (PANEL[0] - 8, 188, NEW_PANELS[-1][2] + 8, PANEL[3] + 8)
    fill = quilt(stock.crop(CLEAN_FRAME), size_of(zone), patch=100, seed=2)
    fill = Image.blend(fill, fill.filter(ImageFilter.GaussianBlur(40)), 0.45)
    out.paste(fill, zone[:2])
    clean = stock.crop(CLEAN_PANEL)
    panel_spans = (PANEL[0] + 44, PANEL[2] - 44, PANEL[1] + 34, PANEL[3] - 34)
    for p in NEW_PANELS:
        out.paste(nine_slice(stock, PANEL, size_of(p), (40, 30, 26), (18, 24, 18, 26), panel_spans, centre=clean), p[:2])
    box_spans = (LIST_BOX[0] + 44, LIST_BOX[2] - 44, LIST_BOX[1] + 44, LIST_BOX[3] - 44)
    for box in (NEW_LIST_BOX, NEW_BRIEF_BOX):
        out.paste(nine_slice(stock, LIST_BOX, size_of(box), (44, 44, 44), (44, 44, 44, 44), box_spans), box[:2])
    ctrl = stock.crop(CONTROLS)
    out.paste(ctrl, NEW_CONTROLS_AT, feather(ctrl.size, 'lrtb', 14))
    return out


def build_underlay(stock, scanlines):
    """Box contents under the frame's holes: the scanlines tiled (keeping their line pitch), over a
    dark fill unless they are the scanline layer itself."""
    out = Image.new('RGBA', stock.size, (0, 0, 0, 0))
    for src_hole, box in ((LIST_HOLE, NEW_LIST_BOX), (BRIEF_HOLE, NEW_BRIEF_BOX)):
        dst = (box[0] + 4, box[1] + 4, box[2] - 4, box[3] - 4)
        piece = tile(stock.crop(src_hole), size_of(dst))
        if not scanlines:
            base = Image.new('RGBA', piece.size, UNDERLAY_FILL)
            base.alpha_composite(piece)
            piece = base
        out.paste(piece, dst[:2])
    return out


def main(src_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    def stock(name):
        return read_dds(os.path.join(src_dir, name + '.DDS'))

    jobs = [('RA_UI_MISSIONSELECT_BG', stock(FRAME_SOURCE), build_frame)]
    scanlines = stock(SCANLINE_SOURCE)
    jobs += [(name, scanlines, lambda s: build_underlay(s, False)) for name in UNDERLAYS]
    jobs += [(name, scanlines, lambda s: build_underlay(s, True)) for name in SCANLINES]
    for name, (header, source), build in jobs:
        write_dds(os.path.join(out_dir, name + '.DDS'), header, build(source))
        print('wrote', name)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
