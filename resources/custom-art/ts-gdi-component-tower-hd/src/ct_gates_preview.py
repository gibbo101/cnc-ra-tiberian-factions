"""Towers next to gates (cnc-gates-hd): each counts the other as a TS GDI wall. The tower draws its coupling on
that side (and the GDI end piece north or south); the gate draws its ts-gdi-wall end piece at that end.
Walls are overlays (drawn first); buildings go row by row, a gate sorting on its middle row; two buildings in
the same row can come in either order, so east-west is shown both ways round.

    python3 ct_gates_preview.py      -> ctwr/out/preview-towers-and-gates.png
"""
import sys
sys.path.insert(0, 'ctwr')
from PIL import Image, ImageDraw
from ctmap import canvas, paste

GATE = {'tsgdi': ('gates/out2/gdi', 10, 'TS GDI'), 'tsnod': ('gates/out2/nod', 7, 'TS Nod'),
        'allies': ('gates/out4/allies', 10, 'RA Allies'), 'soviet': ('gates/out4/soviet', 10, 'RA Soviets'),
        'tdgdi': ('gates/out4/tdgdi', 10, 'TD GDI'), 'tdnod': ('gates/out3/tdnod', 10, 'TD Nod')}
SIDES = (('N', (0, -1)), ('E', (1, 0)), ('S', (0, 1)), ('W', (-1, 0)))
OPP = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
BGD = (40, 40, 40, 255)
_cache = {}


def img(p):
    if p not in _cache:
        _cache[p] = Image.open(p).convert('RGBA')
    return _cache[p]


def compose(cols, rows, walls, towers, gates, fac='tsgdi', gate_first=True):
    """walls: set of cells (TS GDI wall); towers: {cell: frame}; gates: [(orient 'h'/'v', x, y, frame)]
    with (x, y) the gate's top-left cell."""
    prefix, dmg_from, _ = GATE[fac]
    c = canvas(cols, rows)
    ends = {}                                          # gate end cell -> (gate index, which end)
    for i, (o, gx, gy, f) in enumerate(gates):
        cells = [(gx + k, gy) for k in range(3)] if o == 'h' else [(gx, gy + k) for k in range(3)]
        for cell, e in zip((cells[0], cells[2]), ('W', 'E') if o == 'h' else ('N', 'S')):
            ends[cell] = (i, e)

    def wall_nb(cell):
        return cell in walls or cell in towers or cell in ends
    for (x, y) in walls:
        m = wall_nb((x, y - 1)) * 1 + wall_nb((x + 1, y)) * 2 + wall_nb((x, y + 1)) * 4 + wall_nb((x - 1, y)) * 8
        c.alpha_composite(img(f'out2/gdi-wall-{m:02d}.png'), (x * 128, y * 128))

    def gate_end_on(x, y, side):                       # a gate running into this cell end-on from that side
        dx, dy = dict(SIDES)[side]
        g = ends.get((x + dx, y + dy))
        return g is not None and g[1] == OPP[side]

    def tower(x, y):
        L, X, Y = towers[(x, y)], x * 128 - 24, y * 128 - 96
        wallish = lambda s: (x + dict(SIDES)[s][0], y + dict(SIDES)[s][1]) in walls or gate_end_on(x, y, s)
        if wallish('N'):
            paste(c, img(f'ctwr/out/end-gdi-N-{L:02d}.png'), X, Y)
        paste(c, img(f'ctwr/out/component-tower-{L:02d}.png'), X, Y)
        for s, _ in SIDES:
            if wallish(s):
                paste(c, img(f'ctwr/out/coupling-{s}-{L:02d}.png'), X, Y)
        for s, (dx, dy) in SIDES:
            if (x + dx, y + dy) in towers:
                paste(c, img(f'ctwr/out/link-{s}-{L:02d}-{towers[(x + dx, y + dy)]:02d}.png'), X, Y)
        if wallish('S'):
            paste(c, img(f'ctwr/out/end-gdi-S-{L:02d}.png'), X, Y)

    def gate(i):
        o, gx, gy, f = gates[i]
        state = 'ok' if f < dmg_from else 'damaged'
        pieces = {}
        for cell, (j, e) in ends.items():
            if j != i:
                continue
            dx, dy = dict(SIDES)[e]
            if (cell[0] + dx, cell[1] + dy) in walls or (cell[0] + dx, cell[1] + dy) in towers:
                pieces[e] = (cell, img(f'gates/out2/end-gdi-{e}-{state}.png'))
        if 'N' in pieces:
            paste(c, pieces['N'][1], pieces['N'][0][0] * 128, pieces['N'][0][1] * 128)
        paste(c, img(f'{prefix}-gate-{o}-{f:02d}.png'), gx * 128, gy * 128)
        for e in ('W', 'E', 'S'):
            if e in pieces:
                paste(c, pieces[e][1], pieces[e][0][0] * 128, pieces[e][0][1] * 128)
    items = [(y, 1 if gate_first else 0, 't', (x, y)) for (x, y) in towers]
    items += [(gy + (1 if o == 'v' else 0), 0 if gate_first else 1, 'g', i) for i, (o, gx, gy, f) in enumerate(gates)]
    for _, _, kind, key in sorted(items, key=lambda t: (t[0], t[1])):
        tower(*key) if kind == 't' else gate(key)
    return c


def lab(im, t):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 8 + 6 * len(t), 16), fill=(0, 0, 0, 170)); d.text((4, 3), t, fill=(255, 255, 0, 255))
    return im


def stack(ims, gap=10, horizontal=False):
    if horizontal:
        H = max(i.height for i in ims)
        out = Image.new('RGBA', (sum(i.width for i in ims) + gap * (len(ims) - 1), H), BGD); x = 0
        for i in ims:
            out.paste(i, (x, 0)); x += i.width + gap
        return out
    Wd = max(i.width for i in ims)
    out = Image.new('RGBA', (Wd, sum(i.height for i in ims) + gap * (len(ims) - 1)), BGD); y = 0
    for i in ims:
        out.paste(i, (0, y)); y += i.height + gap
    return out


EAST = dict(cols=6, rows=3, walls={(0, 1), (5, 1)}, towers={(1, 1): 0}, gates=[('h', 2, 1, 0)])
SOUTH = dict(cols=3, rows=6, walls={(1, 0)}, towers={(1, 1): 0}, gates=[('v', 1, 2, 0)])
NORTH = dict(cols=3, rows=6, walls={(1, 5)}, towers={(1, 4): 0}, gates=[('v', 1, 1, 0)])


def sheet():
    rows = []
    for fac in GATE:
        name = GATE[fac][2]
        a = compose(**EAST, fac=fac, gate_first=True).crop((104, 64, 424, 288))
        b = compose(**EAST, fac=fac, gate_first=False).crop((104, 64, 424, 288))
        s = compose(**SOUTH, fac=fac).crop((64, 64, 320, 496)).resize((133, 224), Image.LANCZOS)
        n = compose(**NORTH, fac=fac).crop((64, 160, 320, 592)).resize((133, 224), Image.LANCZOS)
        rows.append(stack([lab(a, f'{name}: tower drawn last'), lab(b, 'gate drawn last'),
                           lab(s, 'gate S'), lab(n, 'gate N')], horizontal=True))
    return stack(rows)


if __name__ == '__main__':
    sheet().save('ctwr/out/preview-towers-and-gates.png')
    print('done')
