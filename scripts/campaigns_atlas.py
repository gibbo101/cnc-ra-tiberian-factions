#!/usr/bin/env python3
"""Paint the CAMPAIGNS page art into the UI atlas, in place (docs/campaigns-page.md): TD-style tab
icons for the factions TD lacks, and green mission rows with each faction's crest faded in.

usage: campaigns_atlas.py <MT_COMMANDBAR_COMMON.TGA, edited in place> <MT_COMMANDBAR_COMMON.MTD>
"""
import os
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H, HDR = 6871, 6716, 18
ROW = W * 4
EMBLEMS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tab_emblems')

# Tab icons: TD tab regions the RA page never draws, repainted with the RA and TS crests.
TAB_STATES = ('OFF', 'ON', 'OVER', 'PRESSED', 'DISABLED')
TAB_TARGETS = [('COVERTOPS', 'allied.png'), ('CONTROLLER', 'soviet.png'), ('DINO', 'tsgdi.png')]
INSET = (12, 12, 166, 66)
CLEAN_STRIP = (14, 40)
EMBLEM_BOX = (62, 17, 116, 60)
ERASE = (44, 134)

# Mission rows: RA's own Allied and Soviet row regions, rebuilt from TD's plain rows.
ROW_FACTIONS = [('ALLIED', 'allied.png'), ('SOVIET', 'soviet.png')]
ROW_STATES = {'NORMAL': 'UI_MISSIONSELECT_ITEMLIST_OFF', 'PRESSED': 'UI_MISSIONSELECT_ITEMLIST_SELECTED',
              'SELECTED': 'UI_MISSIONSELECT_ITEMLIST_SELECTED', 'HOVER': 'UI_MISSIONSELECT_ITEMLIST_HOVER'}
CREST_ALPHA = 0.24
CREST_HEIGHT = 1.12
CREST_X = -0.03


class Atlas:
    def __init__(self, path, mtd_path):
        self.data = bytearray(open(path, 'rb').read())
        assert len(self.data) == HDR + W * H * 4
        self.mtd = open(mtd_path, 'rb').read()

    def region(self, name):
        nb = (name + '.TGA').encode()
        i = self.mtd.find(nb)
        assert i >= 0, name
        o = i + len(nb)
        while self.mtd[o] == 0:
            o += 1
        return struct.unpack_from('<4i', self.mtd, o)

    def crop(self, r):
        rx, ry, rw, rh = r
        rows = [bytes(self.data[HDR + (H - 1 - (ry + y)) * ROW + rx * 4:][:rw * 4]) for y in range(rh)]
        return Image.frombytes('RGBA', (rw, rh), b''.join(rows), 'raw', 'BGRA')

    def place(self, r, img):
        rx, ry, rw, rh = r
        assert img.size == (rw, rh)
        b = img.tobytes('raw', 'BGRA')
        for y in range(rh):
            off = HDR + (H - 1 - (ry + y)) * ROW + rx * 4
            self.data[off:off + rw * 4] = b[y * rw * 4:(y + 1) * rw * 4]


def erase_emblem(tab):
    """Cover the emblem: a row-wise blend between the clean columns either side of it, with the
    inset's scanline texture (a clean strip minus its blur) laid back on top, so no seam shows."""
    arr = np.asarray(tab, dtype=np.float32).copy()
    x0, y0, x1, y1 = INSET
    e0, e1 = ERASE
    left, right = arr[:, e0 - 2:e0, :].mean(1), arr[:, e1:e1 + 2, :].mean(1)
    strip = tab.crop((CLEAN_STRIP[0], y0, CLEAN_STRIP[1], y1))
    detail = np.asarray(strip, dtype=np.float32) - np.asarray(strip.filter(ImageFilter.BoxBlur(4)), dtype=np.float32)
    sw = detail.shape[1]
    for x in range(e0, e1):
        t = (x - e0) / float(e1 - e0)
        col = left[y0:y1] * (1 - t) + right[y0:y1] * t + detail[:, (x - e0) % sw, :]
        arr[y0:y1, x, :3] = col[:, :3]
        arr[:y0, x, :] = arr[:y0, e0 - 1, :] * (1 - t) + arr[:y0, e1, :] * t
        arr[y1:, x, :] = arr[y1:, e0 - 1, :] * (1 - t) + arr[y1:, e1, :] * t
    return Image.fromarray(np.clip(arr, 0, 255).astype('uint8'), 'RGBA')


def ramp(tab, clean):
    """The emblem's colours in this state, darkest to brightest, from pixels that differ from the
    erased background."""
    px = []
    for y in range(EMBLEM_BOX[1], EMBLEM_BOX[3]):
        for x in range(EMBLEM_BOX[0], EMBLEM_BOX[2]):
            a, b = tab.getpixel((x, y)), clean.getpixel((x, y))
            if sum(abs(a[k] - b[k]) for k in range(3)) > 90:
                px.append(a[:3])
    px.sort(key=lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2])
    return [px[min(len(px) - 1, i * len(px) // 256)] for i in range(256)]


def recolour(emblem_path, colours, size):
    """The emblem fitted to `size`, its brightness mapped through `colours`, with a dark outline."""
    src = Image.open(emblem_path).convert('RGBA')
    src = src.crop(src.getbbox())
    scale = min(size[0] / src.width, size[1] / src.height)
    src = src.resize((max(1, int(src.width * scale)), max(1, int(src.height * scale))), Image.LANCZOS)
    alpha = src.split()[3]
    lum = src.convert('L')
    lo, hi = lum.getextrema()
    span = max(1, hi - lo)
    fill = Image.new('RGBA', src.size)
    lp, fp = lum.load(), fill.load()
    for y in range(src.height):
        for x in range(src.width):
            v = int(20 + 235 * ((lp[x, y] - lo) / float(span)) ** 1.4)
            fp[x, y] = colours[min(255, v)] + (255,)
    fill.putalpha(alpha)
    pad = 4
    canvas = Image.new('RGBA', (src.width + 2 * pad, src.height + 2 * pad), (0, 0, 0, 0))
    outline_mask = Image.new('L', canvas.size, 0)
    outline_mask.paste(alpha, (pad, pad))
    outline_mask = outline_mask.filter(ImageFilter.MaxFilter(5)).point(lambda v: 255 if v > 40 else 0)
    outline = Image.new('RGBA', canvas.size, colours[0] + (255,))
    outline.putalpha(outline_mask.filter(ImageFilter.GaussianBlur(0.6)))
    canvas.alpha_composite(outline)
    canvas.alpha_composite(fill, (pad, pad))
    return canvas


def interior(row):
    """The area inside the row's solid border: each line filled between its outermost border
    pixels, then pulled in so the crest never touches the border."""
    alpha = row.split()[3].load()
    mask = Image.new('L', row.size, 0)
    draw = ImageDraw.Draw(mask)
    rows = [y for y in range(row.height) if any(alpha[x, y] >= 250 for x in range(0, row.width, 4))]
    top, bottom = rows[0], rows[-1]
    span = None
    for y in range(top + 1, bottom):
        xs = [x for x in range(row.width) if alpha[x, y] >= 200]
        if len(xs) >= 2 and xs[-1] - xs[0] > row.width // 2:
            span = (xs[0] + 1, xs[-1] - 1)
        if span:
            draw.line([(span[0], y), (span[1], y)], fill=255)
    return mask.filter(ImageFilter.MinFilter(7))


def crest_row(row, emblem):
    """`row` with the crest `emblem` (a tab_emblems file) faded into its left end, clipped to the
    row's own shape."""
    em = Image.open(os.path.join(EMBLEMS, emblem)).convert('RGBA')
    em = em.crop(em.getbbox())
    h = int(row.height * CREST_HEIGHT)
    em = em.resize((int(em.width * h / em.height), h), Image.LANCZOS)
    em.putalpha(em.split()[3].point(lambda v: int(v * CREST_ALPHA)))
    layer = Image.new('RGBA', row.size, (0, 0, 0, 0))
    layer.alpha_composite(em, (int(row.width * CREST_X), (row.height - h) // 2))
    clip = interior(row)
    layer.putalpha(Image.composite(layer.split()[3], Image.new('L', row.size, 0), clip))
    out = row.copy()
    out.alpha_composite(layer)
    return out


def paint_tabs(atlas):
    for target, emblem in TAB_TARGETS:
        for state in TAB_STATES:
            template = atlas.crop(atlas.region('UI_MISSIONSELECT_TABICON_GDI_%s' % state))
            clean = erase_emblem(template)
            colours = ramp(template, clean)
            ex0, ey0, ex1, ey1 = EMBLEM_BOX
            icon = recolour(os.path.join(EMBLEMS, emblem), colours, (ex1 - ex0, ey1 - ey0))
            tab = clean.copy()
            tab.alpha_composite(icon, ((tab.width - icon.width) // 2, (tab.height - icon.height) // 2))
            r = atlas.region('UI_MISSIONSELECT_TABICON_%s_%s' % (target, state))
            if tab.size != (r[2], r[3]):
                tab = tab.resize((r[2], r[3]), Image.LANCZOS)
            atlas.place(r, tab)
        print('tab icon', target, '<-', emblem)


def paint_rows(atlas):
    for faction, emblem in ROW_FACTIONS:
        for state, source in ROW_STATES.items():
            r = atlas.region('RA_UI_MISSIONSELECT_ITEMLIST_%s_%s' % (faction, state))
            row = atlas.crop(atlas.region(source)).resize((r[2], r[3]), Image.LANCZOS)
            if state != 'HOVER':
                row = crest_row(row, emblem)
            atlas.place(r, row)
        print('rows', faction, '<-', emblem)


def main(path, mtd):
    atlas = Atlas(path, mtd)
    paint_tabs(atlas)
    paint_rows(atlas)
    open(path, 'wb').write(bytes(atlas.data))
    print('wrote', path)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
