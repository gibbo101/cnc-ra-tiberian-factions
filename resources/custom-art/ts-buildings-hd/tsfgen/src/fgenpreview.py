"""Extra previews for the Firestorm Generator package (bdeliver extra_previews), from the package's own frames:
  layers-<view>.png          every layer on its own, then how they stack
  dome-vs-original.gif       GTFIRE_A: the arm lifting the dome and lowering it again, next to TS's
  lightning-vs-original.gif  GTFIRE_B (with C): the raised dome, lightning and the ring's glow by turns, next to TS's"""
import numpy as np
from PIL import Image, ImageDraw
import ypreview as P

DARK = (30, 30, 30, 255)
NM = 'firestorm-generator'
V = {'iso': 'ts-angle', 'ra': 'ra-grid'}


def lay(pk, view, sub, name):
    return pk.fr(view, sub, f'{NM}-{name}')


def tile(im, w, h, z, title, sub=None):
    t = P.on_bg(im).resize((max(1, int(round(im.width * z))), max(1, int(round(im.height * z)))), Image.LANCZOS)
    c = Image.new('RGBA', (w, h), DARK)
    c.paste(t, ((w - t.width) // 2, 34 + (h - 34 - t.height) // 2))
    d = ImageDraw.Draw(c)
    d.text((6, 4), title, fill=(255, 255, 0, 255))
    if sub:
        d.text((6, 18), sub, fill=(220, 220, 220, 255))
    return c


def stack(*ims):
    out = ims[0].copy()
    for im in ims[1:]:
        out.alpha_composite(im)
    return out


def layers(pk, out):
    for view in ('iso', 'ra'):
        z = 0.75
        b0 = lay(pk, view, 'building', '00')
        ims = [
            (b0, 'building/ 00', 'GTFIRE: no dome, the pit open'),
            (lay(pk, view, 'building', '01'), 'building/ 01', 'damaged'),
            (lay(pk, view, 'A-dome', 'dome-00'), 'A-dome/ 00', 'GTFIRE_A: the dome closed'),
            (lay(pk, view, 'A-dome', 'dome-10'), 'A-dome/ 10', 'lifting'),
            (lay(pk, view, 'A-dome', 'dome-19'), 'A-dome/ 19', 'raised'),
            (lay(pk, view, 'B-lightning', 'lightning-00'), 'B-lightning/ 00', 'GTFIRE_B: raised, lightning'),
            (lay(pk, view, 'B-lightning', 'lightning-01'), 'B-lightning/ 01', 'raised, the ring glowing'),
            (lay(pk, view, 'C-lamps', 'lamps-05'), 'C-lamps/ 05', "GTFIRE_C: the front fin's lamp"),
            (stack(b0, lay(pk, view, 'A-dome', 'dome-00')), 'closed', 'building + A 00 (the build-up ends so)'),
            (stack(b0, lay(pk, view, 'B-lightning', 'lightning-00'), lay(pk, view, 'C-lamps', 'lamps-00')), 'idle',
             'building + B + C (the mod: loop/)'),
        ]
        cw = int(round(ims[0][0].width * z))
        ch = int(round(ims[0][0].height * z)) + 36
        cols = 5
        rows = (len(ims) + cols - 1) // cols
        S = Image.new('RGBA', (cols * (cw + 8), rows * (ch + 8) + 30), DARK)
        P.label(S, f'Firestorm Generator, {V[view]}: the layers (each on its own), and how they stack', (6, 8))
        for n, (im, title, sub) in enumerate(ims):
            S.paste(tile(im, cw, ch, z, title, sub), ((n % cols) * (cw + 8), 30 + (n // cols) * (ch + 8)))
        S.save(f'{out}/layers-{V[view]}.png')


def dome_gif(pk, out):
    zg = pk.s.get('gif_zoom', 1.0)
    T = f"{pk.s['hand']}/ts-original"
    frs = []
    seq = [0] * 4 + list(range(20)) + [19] * 6 + list(range(19, -1, -1)) + [0] * 2
    for k in seq:
        ts = pk.ts_canvas([f'{T}/GTFIRE/frames/00.png', f'{T}/GTFIRE_A/frames/{k:02d}.png'])
        ims = [ts] + [stack(lay(pk, v, 'building', '00'), lay(pk, v, 'A-dome', f'dome-{k:02d}')) for v in ('iso', 'ra')]
        frs.append(pk.three_up(ims, ('TS: GTFIRE + GTFIRE_A', 'HD, TS angle', 'HD, RA grid'), f'A-dome {k:02d} (played forward, then back)', z=zg))
    pk.gif(frs, f'{out}/dome-vs-original.gif', 90)


def lightning_gif(pk, out):
    zg = pk.s.get('gif_zoom', 1.0)
    T = f"{pk.s['hand']}/ts-original"
    frs = []
    for t in range(48):
        b, c = t % 16, t % 6
        ts = pk.ts_canvas([f'{T}/GTFIRE/frames/00.png', f'{T}/GTFIRE_B/frames/{b:02d}.png', f'{T}/GTFIRE_C/frames/{c:02d}.png'])
        ims = [ts] + [lay(pk, v, 'loop', f'loop-{t:02d}') for v in ('iso', 'ra')]
        frs.append(pk.three_up(ims, ('TS: GTFIRE + _B + _C', 'HD, TS angle: loop/', 'HD, RA grid: loop/'), f'loop {t:02d} (B {b:02d}, C {c:02d})', z=zg))
    pk.gif(frs, f'{out}/lightning-vs-original.gif', 110)


EXTRAS = [layers, dome_gif, lightning_gif]
