"""Test maps for the component tower with walls, in RA's order: walls are overlays, drawn with the map
under every building; then the towers, row by row.
Layout chars: G = TS GDI wall, N = TS Nod wall, B = RA concrete wall (BRIK), T = tower, . = ground.
Walls join their own kind and the tower. After the tower, its coupling overlays are drawn for every side
that has a wall."""
from PIL import Image, ImageDraw

BG = (90, 100, 80, 255)
GRID = (82, 92, 72, 255)
WALLS = {'G': lambda n: f'out2/gdi-wall-{n:02d}.png', 'N': lambda n: f'nod/out/nod-wall-{n:02d}.png',
         'B': lambda n: (f'ref/brik-{n:02d}.png' if n < 16 else f'ref-dmg/brik-{n:02d}.png')}


def canvas(cols, rows):
    c = Image.new('RGBA', (cols * 128, rows * 128), BG)
    d = ImageDraw.Draw(c)
    for i in range(cols + 1):
        d.line([(i * 128, 0), (i * 128, rows * 128)], fill=GRID)
    for j in range(rows + 1):
        d.line([(0, j * 128), (cols * 128, j * 128)], fill=GRID)
    return c


def paste(c, im, x, y):
    """alpha-composite allowing negative offsets."""
    x0, y0 = max(x, 0), max(y, 0)
    crop = im.crop((x0 - x, y0 - y, im.width, im.height))
    c.alpha_composite(crop, (x0, y0))


def compose(layout, tower_img, couplings=None, wall_stage=None, ends=None):
    """couplings: dict side -> overlay image. wall_stage: dict (x, y) -> damage row (0-3).
    ends: dict (wall char, side) -> end piece (the wall coming into the tower's cell up to its coupling):
    the north one drawn before the tower, the others after the couplings."""
    h, w = len(layout), len(layout[0])
    c = canvas(w, h)
    at = lambda x, y: layout[y][x] if (0 <= x < w and 0 <= y < h) else '.'
    # walls are overlays in RA: drawn with the map cells, under every building
    for y in range(h):
        for x in range(w):
            ch = at(x, y)
            if ch in WALLS:
                ok = lambda q: q == ch or q == 'T'
                m = ok(at(x, y - 1)) * 1 + ok(at(x + 1, y)) * 2 + ok(at(x, y + 1)) * 4 + ok(at(x - 1, y)) * 8
                st = (wall_stage or {}).get((x, y), 0)
                if st == 3 and m == 0:
                    continue
                c.alpha_composite(Image.open(WALLS[ch](16 * st + m)).convert('RGBA'), (x * 128, y * 128))
    for y in range(h):
        for x in range(w):
            ch = at(x, y)
            if ch == 'T':
                sides = (('N', (0, -1)), ('E', (1, 0)), ('S', (0, 1)), ('W', (-1, 0)))
                key = (at(x, y - 1), 'N')                  # the north end piece goes behind the tower
                if ends and key in ends:
                    paste(c, ends[key], x * 128 - 24, y * 128 - 96)
                paste(c, tower_img, x * 128 - 24, y * 128 - 96)
                for side, (ddx, ddy) in sides:
                    if couplings and at(x + ddx, y + ddy) in WALLS:
                        paste(c, couplings[side], x * 128 - 24, y * 128 - 96)
                for side, (ddx, ddy) in sides[1:]:
                    key = (at(x + ddx, y + ddy), side)
                    if ends and key in ends:
                        paste(c, ends[key], x * 128 - 24, y * 128 - 96)
    return c


KINDS = {'G': 'gdi', 'N': 'nod', 'B': 'brik'}


def compose_towers(layout, level=None, order='we', wall_stage=None, out='ctwr/out'):
    """Like compose, with towers joining towers. level: dict (x, y) -> tower frame (0 / 1 / 2, default 0).
    Per tower, in this order: the north end piece (a wall to the north), the tower, its couplings (walls on
    any side), its links (towers on any side: link-<side>-<own>-<neighbour>), the south end piece (a wall to
    the south). Rows go north to south; order 'we' draws each row west to east, 'ew' east to west (two
    buildings in the same row can come in either order)."""
    h, w = len(layout), len(layout[0])
    c = canvas(w, h)
    at = lambda x, y: layout[y][x] if (0 <= x < w and 0 <= y < h) else '.'
    lv = lambda x, y: (level or {}).get((x, y), 0)
    cache = {}

    def img(name):
        if name not in cache:
            cache[name] = Image.open(f'{out}/{name}.png').convert('RGBA')
        return cache[name]
    for y in range(h):
        for x in range(w):
            ch = at(x, y)
            if ch in WALLS:
                ok = lambda q: q == ch or q == 'T'
                m = ok(at(x, y - 1)) * 1 + ok(at(x + 1, y)) * 2 + ok(at(x, y + 1)) * 4 + ok(at(x - 1, y)) * 8
                st = (wall_stage or {}).get((x, y), 0)
                if st == 3 and m == 0:
                    continue
                c.alpha_composite(Image.open(WALLS[ch](16 * st + m)).convert('RGBA'), (x * 128, y * 128))
    sides = (('N', (0, -1)), ('E', (1, 0)), ('S', (0, 1)), ('W', (-1, 0)))
    for y in range(h):
        xs = range(w) if order == 'we' else range(w - 1, -1, -1)
        for x in xs:
            if at(x, y) != 'T':
                continue
            L, X, Y = lv(x, y), x * 128 - 24, y * 128 - 96
            if at(x, y - 1) in KINDS:
                paste(c, img(f"end-{KINDS[at(x, y - 1)]}-N-{L:02d}"), X, Y)
            paste(c, img(f'component-tower-{L:02d}'), X, Y)
            for side, (dx, dy) in sides:
                if at(x + dx, y + dy) in WALLS:
                    paste(c, img(f'coupling-{side}-{L:02d}'), X, Y)
            for side, (dx, dy) in sides:
                if at(x + dx, y + dy) == 'T':
                    paste(c, img(f'link-{side}-{L:02d}-{lv(x + dx, y + dy):02d}'), X, Y)
            if at(x, y + 1) in KINDS:
                paste(c, img(f"end-{KINDS[at(x, y + 1)]}-S-{L:02d}"), X, Y)
    return c


def label(im, text):
    ImageDraw.Draw(im).text((6, 4), text, fill=(255, 255, 0, 255))
    return im
