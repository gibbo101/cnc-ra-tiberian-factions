"""Previews, README, src and zip for the Construction Yard package (run after yfinal.py has made the frames).
    python3 ydeliver.py previews | readme | src | zip | all"""
import os, sys, shutil, glob
import numpy as np
from PIL import Image, ImageDraw
import ypreview as P, ybuild as B

PKG = '/home/claude/work/out/ts-gdi-construction-yard-hd'
TS = '/home/claude/work/ts/ts-buildings-hd-handoff/01-TSFACT/ts-original'
NAME = 'construction-yard'
V = {'iso': 'ts-angle', 'ra': 'ra-grid'}
BG = P.BG
DARK = (30, 30, 30, 255)


def frame(view, sub, name):
    return Image.open(f'{PKG}/{V[view]}/{sub}/{name}.png').convert('RGBA')


def yard(view, level=0):
    return frame(view, 'yard', f'{NAME}-{level:02d}')


def ts_x3(path_list):
    """TS frames composited, x3 nearest, cut to the in-mod canvas (384x256)."""
    base = Image.open(path_list[0]).convert('RGBA')
    for p in path_list[1:]:
        base.alpha_composite(Image.open(p).convert('RGBA'))
    a = np.repeat(np.repeat(np.array(base), 3, 0), 3, 1)
    return Image.fromarray(a[166:166 + 256, 42:42 + 384])


def ts_still(level=0):
    return ts_x3([f'{TS}/GTCNST/frames/{level:02d}.png'])


def three_up(ims, titles, sub=None):
    """TS (384x256, placed like the TS-angle canvas) | TS angle | RA grid (384x360)."""
    S = Image.new('RGBA', (384 * 3 + 24, 360 + 34), DARK)
    d = ImageDraw.Draw(S)
    for k, im in enumerate(ims):
        dy = 52 if im.height == 256 else 0
        S.paste(P.on_bg(im), (k * 396, 34 + dy))
        d.text((k * 396 + 6, 4), titles[k], fill=(255, 255, 0, 255))
    if sub:
        d.text((6, 18), sub, fill=(255, 255, 255, 255))
    return S


def gif(frames, path, ms):
    q = [f.convert('RGB').quantize(colors=255, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=ms, loop=0, optimize=True)


def over(base, *ovs):
    im = base.copy()
    for o in ovs:
        im.alpha_composite(o)
    return im


def previews():
    out = f'{PKG}/previews'
    os.makedirs(out, exist_ok=True)
    T3 = ('TS original (x3)', 'HD, TS angle (384x256)', 'HD, RA grid (384x360)')
    # on its own, both views, 2x
    W = Image.new('RGBA', (768 * 2 + 16, 720 + 30), DARK)
    W.paste(P.on_bg(yard('iso')).resize((768, 512), Image.LANCZOS), (0, 30 + 104))
    W.paste(P.on_bg(yard('ra')).resize((768, 720), Image.LANCZOS), (768 + 16, 30))
    P.label(W, 'TS angle, 2x', (6, 8)); P.label(W, 'RA grid, 2x (the 3x2 plot is y 52-308 of the canvas)', (768 + 22, 8))
    W.save(f'{out}/yard-on-its-own.png')
    # the two states next to TS's
    S = Image.new('RGBA', (384 * 3 + 24, (360 + 34) * 2), DARK)
    for lv, txt in ((0, 'healthy (frame 00)'), (1, 'damaged (frame 01)')):
        S.paste(three_up([ts_still(lv), yard('iso', lv), yard('ra', lv)], T3, txt), (0, lv * (360 + 34)))
    S.save(f'{out}/yard-states-vs-original.png')
    # in the mod's canvas: now vs HD
    P.fit_sheet(yard('iso')).save(f'{out}/in-mod-vs-hd.png')
    # next to the Component Tower and a GDI wall run (RA grid)
    c = P.ra_scene(yard('ra'))
    c.save(f'{out}/yard-with-tower-and-walls.png')
    c2 = P.ra_scene(yard('ra', 1), extra=None)
    c2.save(f'{out}/yard-damaged-with-tower-and-walls.png')
    # build-up: strip and GIF against GTCNSTMK
    n = len(B.SEQ)
    tsmk = lambda j: ts_x3([f'{TS}/GTCNSTMK/frames/{j:02d}.png'])
    pick = (0, 3, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 31)
    w, h = 192, 128
    half = len(pick) // 2
    S = Image.new('RGB', (half * (w + 4), 6 * (h + 16)), (30, 30, 30))
    d = ImageDraw.Draw(S)
    for m, i in enumerate(pick):
        col, blk = m % half, m // half
        j = B.ts_index(i)
        ims = (tsmk(j), frame('iso', 'build-up', f'{NAME}-build-{i:02d}'), frame('ra', 'build-up', f'{NAME}-build-{i:02d}'))
        for k, im in enumerate(ims):
            y = (blk * 3 + k) * (h + 16)
            hh = h if im.height == 256 else int(h * 360 / 256)
            tile = P.on_bg(im).resize((w, hh), Image.LANCZOS).convert('RGB')
            if im.height != 256:
                tile = tile.crop((0, (hh - h) // 2, w, (hh - h) // 2 + h))
            S.paste(tile, (col * (w + 4), y + 14))
            d.text((col * (w + 4) + 4, y + 1), (f'TS {j:02d}', f'HD {i:02d} TS angle', f'HD {i:02d} RA grid')[k], fill=(255, 255, 0))
    S.save(f'{out}/build-up-strip-vs-original.png')
    fr = []
    for i in list(range(n)) + [n - 1] * 10:
        j = B.ts_index(i)
        fr.append(three_up([tsmk(j), frame('iso', 'build-up', f'{NAME}-build-{i:02d}'),
                            frame('ra', 'build-up', f'{NAME}-build-{i:02d}')],
                           (f'TS GTCNSTMK (x3) {j:02d}/{B.TS_N - 1}', 'HD, TS angle', 'HD, RA grid'), f'build-up {i:02d}/{n - 1}'))
    gif(fr, f'{out}/build-up-vs-original.gif', 110)
    # idle (A + B + C over the building), healthy and damaged, from the package's own overlays
    for lv in (0, 1):
        fr = []
        for t in range(30):
            ims = [ts_x3([f'{TS}/GTCNST/frames/{lv:02d}.png', f'{TS}/GTCNST_A/frames/{t % 10 + 10 * lv:02d}.png',
                          f'{TS}/GTCNST_C/frames/{t % 15 + 15 * lv:02d}.png', f'{TS}/GTCNST_B/frames/{t % 10:02d}.png'])]
            for v in ('iso', 'ra'):
                ims.append(over(yard(v, lv), frame(v, 'A-fans', f'{NAME}-fans-{t % 10 + 10 * lv:02d}'),
                                frame(v, 'B-door-lamp', f'{NAME}-door-lamp-{t % 10 + 10 * lv:02d}'),
                                frame(v, 'C-roof-lamps', f'{NAME}-roof-lamps-{t % 15 + 15 * lv:02d}')))
            fr.append(three_up(ims, T3, f'{("healthy", "damaged")[lv]} idle {t:02d}: building + A (fans) + B (door lamp, running light) + C (roof lamps)'))
        gif(fr, f'{out}/idle-{("healthy", "damaged")[lv]}-vs-original.gif', 100)
    # producing (D over the building; the fans and lamps carry on)
    fr = []
    for t in range(20):
        ims = [ts_x3([f'{TS}/GTCNST/frames/00.png', f'{TS}/GTCNST_A/frames/{t % 10:02d}.png',
                      f'{TS}/GTCNST_C/frames/{t % 15:02d}.png', f'{TS}/GTCNST_D/frames/{t:02d}.png'])]
        for v in ('iso', 'ra'):
            ims.append(over(yard(v), frame(v, 'A-fans', f'{NAME}-fans-{t % 10:02d}'),
                            frame(v, 'C-roof-lamps', f'{NAME}-roof-lamps-{t % 15:02d}'),
                            frame(v, 'D-producing', f'{NAME}-producing-{t:02d}')))
        fr.append(three_up(ims, T3, f'producing {t:02d}: building + A + C + D'))
    gif(fr, f'{out}/producing-vs-original.gif', 120)
    print('previews done')


def src():
    d = f'{PKG}/src'
    os.makedirs(d, exist_ok=True)
    for f in ('hd.py', 'walls2.py', 'wnoise.py', 'yard.py', 'ymat.py', 'ydamage.py', 'yrender.py', 'yanim.py',
              'ybuild.py', 'yfinal.py', 'ydeliver.py', 'ypreview.py', 'yanim_preview.py', 'yfit.py', 'yfeat.py'):
        shutil.copy(f'/home/claude/work/r/{f}', d)


def zipit():
    base = os.path.dirname(PKG)
    name = os.path.basename(PKG)
    z = shutil.make_archive(f'{base}/{name}', 'zip', base, name)
    print(z, os.path.getsize(z))


if __name__ == '__main__':
    what = sys.argv[1]
    if what in ('previews', 'all'):
        previews()
    if what in ('src', 'all'):
        src()
    if what in ('zip', 'all'):
        zipit()
