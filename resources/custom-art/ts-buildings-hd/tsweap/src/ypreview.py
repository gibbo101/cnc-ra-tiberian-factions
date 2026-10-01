"""Previews for the Construction Yard (checkpoint and delivery)."""
import numpy as np
from PIL import Image, ImageDraw

HAND = '/home/claude/work/ts/ts-buildings-hd-handoff/01-TSFACT'
PKG = '/home/claude/work/pkg'
BG = (90, 100, 80, 255)
GRID = (82, 92, 72, 255)
YARD_HEAD = 52                       # RA canvas: 384 x 360, the plot at y 52 .. 308


def on_bg(im, bg=BG):
    b = Image.new('RGBA', im.size, bg); b.alpha_composite(im.convert('RGBA')); return b


def label(im, text, xy=(6, 4), fill=(255, 255, 0, 255)):
    ImageDraw.Draw(im).text(xy, text, fill=fill)
    return im


def canvas(cols, rows, grid=True):
    c = Image.new('RGBA', (cols * 128, rows * 128), BG)
    if grid:
        d = ImageDraw.Draw(c)
        for i in range(cols + 1):
            d.line([(i * 128, 0), (i * 128, rows * 128)], fill=GRID)
        for j in range(rows + 1):
            d.line([(0, j * 128), (cols * 128, j * 128)], fill=GRID)
    return c


def paste(c, im, x, y):
    x0, y0 = max(x, 0), max(y, 0)
    crop = im.crop((x0 - x, y0 - y, min(im.width, c.width - x), min(im.height, c.height - y)))
    c.alpha_composite(crop, (x0, y0))


def gdi_wall(n):
    return Image.open(f'{PKG}/ts-gdi-wall-hd/frames/gdi-wall-{n:02d}.png').convert('RGBA')


def tower(state=0):
    return Image.open(f'{PKG}/ts-gdi-component-tower-hd/tower/component-tower-{state:02d}.png').convert('RGBA')


def ra_scene(yard_img, cols=8, rows=6, yard_at=(1, 2), tower_at=(6, 2), wall_row=5, wall_cols=(0, 7),
             yard_head=YARD_HEAD, extra=None):
    """RA order: walls (overlays) with the map, then buildings from the back (north) to the front."""
    c = canvas(cols, rows)
    y0 = wall_row
    for x in range(wall_cols[0], wall_cols[1] + 1):
        m = (2 if x < wall_cols[1] else 0) + (8 if x > wall_cols[0] else 0)
        paste(c, gdi_wall(m), x * 128, y0 * 128)
    items = []
    if tower_at:
        tx, ty = tower_at
        items.append((ty + 1, tower(), tx * 128 - 24, ty * 128 - 96))
    yx, yy = yard_at
    items.append((yy + 2, yard_img, yx * 128, yy * 128 - yard_head))
    for it in (extra or []):
        items.append(it)
    for _, im, x, y in sorted(items, key=lambda t: t[0]):
        paste(c, im, x, y)
    d = ImageDraw.Draw(c)
    d.rectangle([yx * 128, yy * 128, yx * 128 + 384 - 1, yy * 128 + 256 - 1], outline=(255, 255, 0, 110))
    return c


def fit_sheet(iso_img, scale=2):
    inmod = on_bg(Image.open(f'{HAND}/in-mod/tsfact-0000.png'))
    iso = on_bg(iso_img)
    W, H = 384 * scale, 256 * scale
    s = Image.new('RGBA', (W * 2 + 12, H + 28), (30, 30, 30, 255))
    s.paste(inmod.resize((W, H), Image.NEAREST), (0, 28))
    s.paste(iso.resize((W, H), Image.LANCZOS), (W + 12, 28))
    label(s, 'In the mod now: TS GTCNST frame 0 (x3, 384x256)', (6, 8))
    label(s, 'HD rebuild, TS angle (same canvas, scale and place)', (W + 18, 8))
    return s
