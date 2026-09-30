"""Previews for the component tower."""
import sys
sys.path.insert(0, 'ctwr')
from PIL import Image, ImageDraw
from ctmap import compose, compose_towers, label, canvas, paste

OUT = 'ctwr/out'
BGD = (40, 40, 40, 255)


def tower(level=0):
    return Image.open(f'{OUT}/component-tower-{level:02d}.png').convert('RGBA')


def cpl(level=0):
    return {s: Image.open(f'{OUT}/coupling-{s}-{level:02d}.png').convert('RGBA') for s in 'NESW'}


def ends(level=0):
    """the walls that come into the tower's cell, north and south: GDI (G), Nod (N), RA concrete (B)."""
    return {(ch, s): Image.open(f'{OUT}/end-{kind}-{s}-{level:02d}.png').convert('RGBA')
            for ch, kind in (('G', 'gdi'), ('N', 'nod'), ('B', 'brik')) for s in 'NS'}


def stack(images, gap=16, horizontal=False):
    if horizontal:
        H = max(i.height for i in images)
        out = Image.new('RGBA', (sum(i.width for i in images) + gap * (len(images) - 1), H), BGD)
        x = 0
        for i in images:
            out.paste(i, (x, 0)); x += i.width + gap
        return out
    Wd = max(i.width for i in images)
    out = Image.new('RGBA', (Wd, sum(i.height for i in images) + gap * (len(images) - 1)), BGD)
    y = 0
    for i in images:
        out.paste(i, (0, y)); y += i.height + gap
    return out


def main_sheet():
    t, c, e = tower(0), cpl(0), ends(0)
    alone = label(compose(['...', '.T.', '...'], t, c, ends=e), 'on its own')
    scale = label(compose(['.....', 'GGG.T', '.....'], t, c, ends=e), 'next to a GDI wall run (not joined) for scale')
    cross = label(compose(['..G..', '..G..', 'GGTGG', '..G..', '..G..'], t, c, ends=e), 'GDI walls on all four sides')
    L = label(compose(['.G...', '.G...', '.TGGG', '.....'], t, c, ends=e), 'L: walls north and east')
    T = label(compose(['.....', 'GGTGG', '..G..', '..G..'], t, c, ends=e), 'T: walls west, east and south')
    mixed = label(compose(['..G..', '..G..', 'GGTNN', '..B..', '..B..'], t, c, ends=e),
                  'any wall: GDI north and west, Nod east, RA concrete south')
    mixed2 = label(compose(['..B..', '..B..', 'BBTGG', '..N..', '..N..'], t, c, ends=e),
                   'any wall: RA concrete north and west, GDI east, Nod south')
    south = label(compose(['.......', '.......', '.T.T.T.', '.G.N.B.', '.G.N.B.'], t, c, ends=e),
                  'from the south: GDI, Nod, RA concrete')
    top = stack([alone, scale], horizontal=True)
    mid = stack([cross, stack([L, T])], horizontal=True)
    return stack([top, mid, stack([mixed, mixed2], horizontal=True), south])


def states_sheet():
    tiles = []
    for lvl, name in ((0, 'healthy'), (1, 'damaged'), (2, 'destroyed')):
        st = {(x, y): lvl for x in range(5) for y in range(5)}
        tiles.append(label(compose(['..G..', '..G..', 'GGTGG', '..G..', '..G..'], tower(lvl), cpl(lvl),
                                   wall_stage=st, ends=ends(lvl)), f'frame {lvl}: {name}'))
    return stack(tiles, horizontal=True)


def ends_sheet():
    """Nod and RA concrete walls coming in north and south, in the three states."""
    rows = []
    for lay, name in ((['..N..', '..N..', 'GGTGG', '..N..', '..N..'], 'Nod'),
                      (['..B..', '..B..', 'GGTGG', '..B..', '..B..'], 'RA concrete')):
        tiles = []
        for lvl, st_name in ((0, 'healthy'), (1, 'damaged'), (2, 'destroyed')):
            st = {(x, y): (3 if (lay[y][x] == 'B' and lvl == 2) else lvl) for x in range(5) for y in range(5)}
            m = compose(lay, tower(lvl), cpl(lvl), wall_stage=st, ends=ends(lvl))
            tiles.append(label(m.crop((128, 64, 512, 576)), f'{name} north and south, frame {lvl}: {st_name}'))
        rows.append(stack(tiles, horizontal=True))
    return stack(rows)


def buildup_strip():
    frames = [Image.open(f'{OUT}/component-tower-build-{i:02d}.png').convert('RGBA') for i in range(17)]
    tiles = []
    for i, f in enumerate(frames):
        t = Image.new('RGBA', (176, 250), (90, 100, 80, 255))
        t.alpha_composite(f.crop((0, 40, 176, 290)))
        ImageDraw.Draw(t).text((4, 2), str(i), fill=(255, 255, 0, 255))
        tiles.append(t)
    row1 = stack(tiles[:9], gap=4, horizontal=True)
    row2 = stack(tiles[9:], gap=4, horizontal=True)
    return stack([row1, row2], gap=4)


def buildup_gif(path):
    frames = [Image.open(f'{OUT}/component-tower-build-{i:02d}.png').convert('RGBA') for i in range(17)]
    seq = frames + [frames[-1]] * 6
    out = []
    for f in seq:
        t = Image.new('RGBA', (176 * 2, 250 * 2), (90, 100, 80, 255))
        t.alpha_composite(f.crop((0, 40, 176, 290)).resize((352, 500), Image.LANCZOS))
        out.append(t.convert('RGB'))
    pal = out[len(out) // 2].quantize(colors=255, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [o.quantize(palette=pal, dither=Image.NONE) for o in out]
    q[0].save(path, save_all=True, append_images=q[1:], duration=120, loop=0)


def light_gif(path):
    t = tower(0)
    lights = [Image.open(f'{OUT}/component-tower-light-{i:02d}.png').convert('RGBA') for i in range(6)]
    out = []
    for l in lights * 3:
        c = Image.new('RGBA', t.size, (90, 100, 80, 255)); c.alpha_composite(t); c.alpha_composite(l)
        out.append(c.crop((40, 110, 150, 240)).resize((330, 390), Image.NEAREST).convert('RGB'))
    pal = out[2].quantize(colors=255, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [o.quantize(palette=pal, dither=Image.NONE) for o in out]
    q[0].save(path, save_all=True, append_images=q[1:], duration=110, loop=0)


def vs_original():
    BG = (90, 100, 80, 255)

    def on_bg(im):
        b = Image.new('RGBA', im.size, BG); b.alpha_composite(im); return b
    orig = on_bg(Image.open('ctwr/frames-4x/tower-00.png').convert('RGBA')).resize((352, 352), Image.NEAREST)
    t = tower(0)
    a = on_bg(t).crop((0, 64, 176, 240)).resize((352, 352), Image.LANCZOS)
    m = compose(['.G.', 'GTG', '.G.'], t, cpl(0), ends=ends(0))   # tower canvas at (104, 32) in this map
    b = m.crop((104, 96, 280, 272)).resize((352, 352), Image.LANCZOS)
    c = Image.new('RGBA', (3 * 364, 378), BGD)
    d = ImageDraw.Draw(c)
    for i, (im, lab) in enumerate(((orig, 'TS original (GTCTWR frame 0)'), (a, 'RA HD frame 00, on its own'),
                                   (b, 'RA HD frame 00 + couplings, GDI walls all round'))):
        c.paste(im, (i * 364, 26)); d.text((i * 364 + 4, 6), lab, fill=(255, 255, 0, 255))
    return c


def build_vs_original():
    BG = (90, 100, 80, 255)

    def on_bg(im):
        b = Image.new('RGBA', im.size, BG); b.alpha_composite(im); return b
    ts = [on_bg(Image.open(f'ctwr/frames-4x/build-{i:02d}.png').convert('RGBA')).crop((0, 40, 192, 192)).resize((120, 95), Image.NEAREST) for i in range(11)]
    ours = [on_bg(Image.open(f'{OUT}/component-tower-build-{i:02d}.png').convert('RGBA')).crop((0, 64, 176, 240)).resize((110, 110), Image.LANCZOS) for i in range(17)]
    Wb = max(11 * 124, 17 * 114)
    b = Image.new('RGBA', (Wb, 22 + 95 + 30 + 110 + 4), BGD)
    d = ImageDraw.Draw(b)
    d.text((4, 4), 'TS build-up (GTCTWRMK, 11 frames)', fill=(255, 255, 0, 255))
    for i, t in enumerate(ts):
        b.paste(t, (i * 124, 22)); d.text((i * 124 + 3, 24), str(i), fill=(255, 255, 255, 255))
    d.text((4, 22 + 95 + 10), 'RA HD build-up (17 frames)', fill=(255, 255, 0, 255))
    for i, t in enumerate(ours):
        b.paste(t, (i * 114, 22 + 95 + 30)); d.text((i * 114 + 3, 22 + 95 + 32), str(i), fill=(255, 255, 255, 255))
    return b


def links_sheet():
    """towers next to towers: east-west they share a sleeve (link-*), north-south a tower counts as a GDI
    wall; with walls round them as usual."""
    ct = compose_towers
    pair = label(ct(['.....', '.TT..', '.....']).crop((64, 0, 448, 384)), 'east-west pair')
    ns = label(ct(['...', '.T.', '.T.', '...']), 'north-south pair')
    row = label(ct(['.......', 'GTTTG..', '.......']).crop((0, 0, 640, 384)), 'three in a GDI wall line')
    blk = label(ct(['....', '.TT.', '.TT.', '....']), '2x2 block')
    colm = label(ct(['..G..', '..T..', '..T..', '..T..', '..G..']).crop((64, 0, 576, 640)),
                 'three in a north-south wall')
    fort = label(ct(['.......', '.TTTTGG', '.T.....', '.T.....', '.G.....', '.G.....']),
                 'a corner: towers and walls')
    mixed = label(ct(['..N...', 'BBTTGG', '..B...', '......']),
                  'with other walls: RA concrete west, Nod north, GDI east, concrete south')
    top = stack([pair, ns, blk], horizontal=True)
    mid = stack([row, colm], horizontal=True)
    return stack([top, mid, stack([fort, mixed], horizontal=True)])


def link_states_sheet():
    """every pair of states (RA's two: 00 healthy, 01 damaged): east-west (rows: the west tower, columns: the
    east one) and north-south (rows: the north tower, columns: the south one)."""
    names = ('healthy', 'damaged')
    ew, ns = [], []
    for a in range(2):
        ew_row, ns_row = [], []
        for b in range(2):
            m = compose_towers(['....', '.TT.', '....'], level={(1, 1): a, (2, 1): b})
            ew_row.append(label(m.crop((64, 64, 448, 320)), f'W {a:02d} {names[a]} / E {b:02d} {names[b]}'))
            m = compose_towers(['...', '.T.', '.T.', '...'], level={(1, 1): a, (1, 2): b})
            ns_row.append(label(m.crop((32, 32, 352, 448)), f'N {a:02d} {names[a]} / S {b:02d} {names[b]}'))
        ew.append(stack(ew_row, gap=8, horizontal=True)); ns.append(stack(ns_row, gap=8, horizontal=True))
    return stack([stack(ew, gap=8), stack(ns, gap=8)], horizontal=True)


def link_zoom_sheet():
    """the links up close (x3): east-west and north-south in each pair of states, and an east-west pair drawn
    both ways round (two buildings in the same row can be drawn in either order; north-south the south
    one always comes last)."""
    def ew(a, b, order='we'):
        m = compose_towers(['....', '.TT.', '....'], level={(1, 1): a, (2, 1): b}, order=order)
        return m.crop((168, 100, 344, 260)).resize((528, 480), Image.LANCZOS)

    def ns(a, b):
        m = compose_towers(['...', '.T.', '.T.', '...'], level={(1, 1): a, (1, 2): b})
        return m.crop((104, 160, 280, 320)).resize((528, 480), Image.LANCZOS)
    pairs = ((0, 0), (0, 1), (1, 0), (1, 1))
    r1 = [label(ew(a, b), f'east-west, west {a:02d} / east {b:02d}') for a, b in pairs]
    r2 = [label(ns(a, b), f'north-south, north {a:02d} / south {b:02d}') for a, b in pairs]
    r3 = [label(ew(0, 1), 'west 00 / east 01, west drawn first'), label(ew(0, 1, 'ew'), 'west 00 / east 01, east drawn first'),
          label(ew(1, 0), 'west 01 / east 00, west drawn first'), label(ew(1, 0, 'ew'), 'west 01 / east 00, east drawn first')]
    return stack([stack(r1, horizontal=True), stack(r2, horizontal=True), stack(r3, horizontal=True)])


if __name__ == '__main__':
    if sys.argv[1:] == ['links']:
        links_sheet().save(f'{OUT}/preview-towers-linked.png')
        link_states_sheet().save(f'{OUT}/preview-towers-linked-states.png')
        link_zoom_sheet().save(f'{OUT}/preview-towers-linked-close.png')
        print('link previews done')
        sys.exit()
    vs_original().save(f'{OUT}/tower-vs-original.png')
    build_vs_original().save(f'{OUT}/build-up-vs-original.png')
    main_sheet().save(f'{OUT}/preview-tower-and-walls.png')
    ends_sheet().save(f'{OUT}/preview-nod-and-concrete.png')
    states_sheet().save(f'{OUT}/preview-states.png')
    buildup_strip().save(f'{OUT}/preview-build-up.png')
    buildup_gif(f'{OUT}/build-up.gif')
    light_gif(f'{OUT}/light.gif')
    links_sheet().save(f'{OUT}/preview-towers-linked.png')
    link_states_sheet().save(f'{OUT}/preview-towers-linked-states.png')
    link_zoom_sheet().save(f'{OUT}/preview-towers-linked-close.png')
    print('previews done')
