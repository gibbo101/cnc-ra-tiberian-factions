"""Previews for the second-pass faction gates (gates4.py) and overviews of all six gates on both wall types.

  python3 gatepreview4.py review [facs]    quick review sheets (frames 0 4 9 10 20)
  python3 gatepreview4.py all [facs]       opening GIFs, all-frames sheets, closed stills (TS GDI wall + RA wall)
  python3 gatepreview4.py overview         all six gates, closed / open, horizontal + vertical, both wall types
"""
import os
from PIL import Image, ImageDraw
from gatemap2 import horizontal, vertical, horizontal_brik, vertical_brik, img, label

OUT = 'gates/out4'
BGD = (40, 40, 40, 255)
YEL = (255, 255, 0, 255)
NAMES = {'allies': 'RA Allies', 'soviet': 'RA Soviets', 'tdgdi': 'TD GDI', 'tdnod': 'TD Nod'}
# where each gate's frames live: (folder, file prefix, closed frame, open frame, damaged offset, destroyed frame)
SRC = {'tsgdi': ('gates/out2', 'gdi', 0, 9, 10, 20, 'TS GDI'),
       'tsnod': ('gates/out2', 'nod', 0, 6, 7, 14, 'TS Nod'),
       'allies': ('gates/out4', 'allies', 0, 9, 10, 20, 'RA Allies'),
       'soviet': ('gates/out4', 'soviet', 0, 9, 10, 20, 'RA Soviets'),
       'tdgdi': ('gates/out4', 'tdgdi', 0, 9, 10, 20, 'TD GDI'),
       'tdnod': ('gates/out3', 'tdnod', 0, 9, 10, 20, 'TD Nod')}
ORDER = ['tsgdi', 'tsnod', 'allies', 'soviet', 'tdgdi', 'tdnod']


def gpath(fac, o, f):
    d, p = SRC[fac][:2]
    return f'{d}/{p}-gate-{o}-{f:02d}.png'


def st(fac, f):
    dmg, dead = SRC[fac][4], SRC[fac][5]
    return ('ok', 0) if f < dmg else (('damaged', 1) if f < dead else ('destroyed', 2))


def hmap(gate, state, wall_stage, wall):
    if wall == 'ts':
        return horizontal(gate, state=state, wall_stage=wall_stage)
    return horizontal_brik(gate, state=state)


def vmap(gate, state, wall_stage, wall):
    if wall == 'ts':
        return vertical(gate, state=state, wall_stage=wall_stage)
    return vertical_brik(gate, state=state)


# --------------------------------------------------------------------------------------------- per gate
def review(fac, frames):
    rows, cols = [], []
    for f in frames:
        s, w = st(fac, f)
        rows.append(label(horizontal(img(gpath(fac, 'h', f)), state=s, wall_stage=w).crop((96, 96, 800, 288)),
                          f'{NAMES[fac]}  frame {f}'))
        cols.append(label(vertical(img(gpath(fac, 'v', f)), state=s, wall_stage=w).crop((96, 224, 288, 672)), str(f)))
    c = Image.new('RGBA', (704 + 12 + 196 * len(cols), max(196 * len(rows), 448)), BGD)
    for i, r in enumerate(rows):
        c.paste(r, (0, i * 196))
    for i, cl in enumerate(cols):
        c.paste(cl, (716 + i * 196, 0))
    return c


def still_from(hok, hdm, vok, vdm, title, sub, wall='ts', dstate='damaged'):
    """closed + damaged, horizontal + vertical, on one canvas."""
    H1 = hmap(img(hok), 'ok', 0, wall).crop((96, 96, 800, 288))
    H2 = hmap(img(hdm), dstate, 1, wall).crop((96, 96, 800, 288))
    V1 = vmap(img(vok), 'ok', 0, wall).crop((96, 96, 288, 800))
    V2 = vmap(img(vdm), dstate, 1, wall).crop((96, 96, 288, 800))
    c = Image.new('RGBA', (704 + 16 + 192 * 2 + 8, 704), BGD)
    c.paste(H1, (0, 0)); c.paste(H2, (0, 200)); c.paste(V1, (720, 0)); c.paste(V2, (920, 0))
    d = ImageDraw.Draw(c)
    d.text((6, 4), title, fill=YEL)
    d.text((6, 204), 'damaged', fill=YEL)
    d.text((726, 4), 'vertical', fill=YEL)
    d.text((926, 4), 'damaged', fill=YEL)
    d.text((6, 420), sub, fill=(200, 200, 200, 255))
    return c


def still(fac, f_ok, f_dmg, wall='ts'):
    return still_from(gpath(fac, 'h', f_ok), gpath(fac, 'h', f_dmg), gpath(fac, 'v', f_ok), gpath(fac, 'v', f_dmg),
                      NAMES[fac] + ' gate' + ('' if wall == 'ts' else '  (RA concrete wall)'),
                      f'frame {f_ok} / {f_dmg}', wall)


def idle_paths(o, k):
    """the Tesla gate's optional idle frames: k = 0 is frame 0 / 10 itself."""
    if k == 0:
        return gpath('soviet', o, 0), gpath('soviet', o, 10)
    return f'{OUT}/soviet-gate-{o}-idle-ok-{k}.png', f'{OUT}/soviet-gate-{o}-idle-damaged-{k}.png'


def save_gif(frames, path, ms=110):
    frames = [f.convert('RGB') for f in frames]
    # palette from a montage of shut / half / open frames so glows and lights keep their colour
    pick = [frames[0], frames[len(frames) // 4], frames[len(frames) // 2]]
    w, h = pick[0].size
    mont = Image.new('RGB', (w, h * len(pick)))
    for i, f in enumerate(pick):
        mont.paste(f, (0, i * h))
    pal = mont.quantize(colors=255, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [fr.quantize(palette=pal, dither=Image.NONE) for fr in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=ms, loop=0)


def animation(fac, wall='ts'):
    seq = [0] * 4 + list(range(10)) + [9] * 5 + list(range(9, -1, -1)) + [0] * 2
    tag = '' if wall == 'ts' else '-ra-wall'
    if fac == 'soviet':
        # the closed hold cycles the idle arcs
        frames = []
        hold = [0, 1, 2, 3]
        for i, f in enumerate(seq):
            if f == 0 and (i < 4 or i >= len(seq) - 3):
                k = hold[i % 4]
                hok, hdm = idle_paths('h', k); vok, vdm = idle_paths('v', k)
                frames.append(still_from(hok, hdm, vok, vdm, 'RA Soviets gate', 'shut: idle arcs', wall))
            else:
                frames.append(still(fac, f, f + 10, wall))
    else:
        frames = [still(fac, f, f + 10, wall) for f in seq]
    save_gif(frames, f'{OUT}/{fac}-gate-opening{tag}.gif')


def sheets(fac):
    BG = (90, 100, 80, 255)

    def tile(path, text):
        t = Image.new('RGBA', Image.open(path).size, BG)
        t.alpha_composite(img(path))
        ImageDraw.Draw(t).text((4, 2), text, fill=YEL)
        return t
    hs = [tile(gpath(fac, 'h', f), str(f)) for f in range(21)]
    H = Image.new('RGBA', (3 * 388, 7 * 132), BGD)
    for i, t in enumerate(hs):
        H.paste(t, ((i // 7) * 388, (i % 7) * 132))
    H.save(f'{OUT}/{fac}-all-frames-horizontal.png')
    vs = [tile(gpath(fac, 'v', f), str(f)) for f in range(21)]
    V = Image.new('RGBA', (11 * 132, 2 * 388), BGD)
    for i, t in enumerate(vs):
        V.paste(t, ((i % 11) * 132, (i // 11) * 388))
    V.save(f'{OUT}/{fac}-all-frames-vertical.png')


# --------------------------------------------------------------------------------------------- overviews
def overview_h(wall='ts', states=('closed', 'open')):
    row_h = 184
    c = Image.new('RGBA', (448 * 2 + 12, 24 + row_h * len(ORDER)), BGD)
    d = ImageDraw.Draw(c)
    wname = 'TS GDI wall' if wall == 'ts' else 'RA concrete wall'
    d.text((6, 6), f'with the {wname} - closed', fill=(235, 235, 235, 255))
    d.text((466, 6), 'open', fill=(235, 235, 235, 255))
    for r, fac in enumerate(ORDER):
        closed, opened = SRC[fac][2], SRC[fac][3]
        for k, f in enumerate((closed, opened)):
            m = hmap(img(gpath(fac, 'h', f)), 'ok', 0, wall).crop((224, 112, 672, 288))
            label(m, SRC[fac][6])
            c.paste(m, (k * 460, 24 + r * row_h))
    return c


def overview_v(wall='ts'):
    c = Image.new('RGBA', (len(ORDER) * 2 * 132, 24 + 448), BGD)
    d = ImageDraw.Draw(c)
    wname = 'TS GDI wall' if wall == 'ts' else 'RA concrete wall'
    d.text((6, 6), f'vertical, with the {wname}: closed / open', fill=(235, 235, 235, 255))
    for i, fac in enumerate(ORDER):
        closed, opened = SRC[fac][2], SRC[fac][3]
        for k, f in enumerate((closed, opened)):
            m = vmap(img(gpath(fac, 'v', f)), 'ok', 0, wall).crop((128, 224, 256, 672))
            if k == 0:
                label(m, SRC[fac][6])
            c.paste(m, ((2 * i + k) * 132, 24))
    return c


def overview_damage(wall='ts'):
    """damaged (closed) and destroyed, horizontal, all six."""
    row_h = 184
    c = Image.new('RGBA', (448 * 2 + 12, 24 + row_h * len(ORDER)), BGD)
    d = ImageDraw.Draw(c)
    wname = 'TS GDI wall' if wall == 'ts' else 'RA concrete wall'
    d.text((6, 6), f'with the {wname} - damaged', fill=(235, 235, 235, 255))
    d.text((466, 6), 'destroyed', fill=(235, 235, 235, 255))
    for r, fac in enumerate(ORDER):
        dmg, dead = SRC[fac][4], SRC[fac][5]
        for k, (f, s, w) in enumerate(((dmg, 'damaged', 1), (dead, 'destroyed', 2))):
            m = hmap(img(gpath(fac, 'h', f)), s, w, wall).crop((224, 112, 672, 288))
            label(m, SRC[fac][6])
            c.paste(m, (k * 460, 24 + r * row_h))
    return c


if __name__ == '__main__':
    import sys
    mode = sys.argv[1]
    facs = sys.argv[2:] or ['allies', 'soviet', 'tdgdi']
    if mode == 'review':
        for fac in facs:
            review(fac, [0, 4, 9, 10, 20]).save(f'{OUT}/review-{fac}.png')
    elif mode == 'all':
        for fac in facs:
            animation(fac); sheets(fac)
            still(fac, 0, 10).save(f'{OUT}/{fac}-gate-closed.png')
            still(fac, 0, 10, wall='ra').save(f'{OUT}/{fac}-gate-closed-ra-wall.png')
            print(fac, 'done', flush=True)
    elif mode == 'overview':
        for wall, tag in (('ts', ''), ('ra', '-ra-wall')):
            overview_h(wall).save(f'{OUT}/all-gates-horizontal{tag}.png')
            overview_v(wall).save(f'{OUT}/all-gates-vertical{tag}.png')
            overview_damage(wall).save(f'{OUT}/all-gates-damage{tag}.png')
        print('overviews done')
