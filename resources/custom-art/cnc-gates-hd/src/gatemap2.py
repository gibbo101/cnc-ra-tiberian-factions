"""Test maps: gates with their wall end pieces, drawn in the order the game should use.

walls (overlays) -> N end piece -> gate -> W / E / S end pieces
"""
from PIL import Image, ImageDraw

BG = (90, 100, 80, 255)
GRID = (82, 92, 72, 255)
OUT = 'gates/out2'


def img(path):
    return Image.open(path).convert('RGBA')


def wall(n):
    return img(f'out2/gdi-wall-{n:02d}.png')


def end(side, state):
    return img(f'{OUT}/end-gdi-{side}-{state}.png')


def canvas(cols, rows):
    c = Image.new('RGBA', (cols * 128, rows * 128), BG)
    d = ImageDraw.Draw(c)
    for i in range(cols + 1):
        d.line([(i * 128, 0), (i * 128, rows * 128)], fill=GRID)
    for j in range(rows + 1):
        d.line([(0, j * 128), (cols * 128, j * 128)], fill=GRID)
    return c


def horizontal(gate, west=True, east=True, state='ok', wall_stage=0):
    """7x3 cells, gate on cells 2-4 of the middle row."""
    c = canvas(7, 3)
    if west:
        c.alpha_composite(wall(16 * wall_stage + 2), (0, 128))
        c.alpha_composite(wall(16 * wall_stage + 10), (128, 128))
    if east:
        c.alpha_composite(wall(16 * wall_stage + 10), (5 * 128, 128))
        c.alpha_composite(wall(16 * wall_stage + 8), (6 * 128, 128))
    c.alpha_composite(gate, (2 * 128, 128))
    if west:
        c.alpha_composite(end('W', state), (2 * 128, 128))
    if east:
        c.alpha_composite(end('E', state), (4 * 128, 128))
    return c


def vertical(gate, north=True, south=True, state='ok', wall_stage=0):
    """3x7 cells, gate on cells 2-4 of the middle column."""
    c = canvas(3, 7)
    if north:
        c.alpha_composite(wall(16 * wall_stage + 4), (128, 0))
        c.alpha_composite(wall(16 * wall_stage + 5), (128, 128))
    if south:
        c.alpha_composite(wall(16 * wall_stage + 5), (128, 5 * 128))
        c.alpha_composite(wall(16 * wall_stage + 1), (128, 6 * 128))
    if north:
        c.alpha_composite(end('N', state), (128, 2 * 128))
    c.alpha_composite(gate, (128, 2 * 128))
    if south:
        c.alpha_composite(end('S', state), (128, 4 * 128))
    return c


def label(im, text):
    ImageDraw.Draw(im).text((6, 4), text, fill=(255, 255, 0, 255))
    return im


# ---- RA concrete wall (BRIK) versions
def brik(n):
    return img(f'ref/brik-{n:02d}.png') if n < 16 else img(f'ref-dmg/brik-{n:02d}.png')


def end_brik(side, state):
    return img(f'{OUT}/end-brik-{side}-{state}.png')


def horizontal_brik(gate, state='ok', west=True, east=True):
    off = 16 if state != 'ok' else 0
    c = canvas(7, 3)
    if west:
        c.alpha_composite(brik(off + 2), (0, 128)); c.alpha_composite(brik(off + 10), (128, 128))
    if east:
        c.alpha_composite(brik(off + 10), (5 * 128, 128)); c.alpha_composite(brik(off + 8), (6 * 128, 128))
    c.alpha_composite(gate, (2 * 128, 128))
    if west:
        c.alpha_composite(end_brik('W', state), (2 * 128, 128))
    if east:
        c.alpha_composite(end_brik('E', state), (4 * 128, 128))
    return c


def vertical_brik(gate, state='ok', north=True, south=True):
    off = 16 if state != 'ok' else 0
    c = canvas(3, 7)
    if north:
        c.alpha_composite(brik(off + 4), (128, 0)); c.alpha_composite(brik(off + 5), (128, 128))
    if south:
        c.alpha_composite(brik(off + 5), (128, 5 * 128)); c.alpha_composite(brik(off + 1), (128, 6 * 128))
    if north:
        c.alpha_composite(end_brik('N', state), (128, 2 * 128))
    c.alpha_composite(gate, (128, 2 * 128))
    if south:
        c.alpha_composite(end_brik('S', state), (128, 4 * 128))
    return c
