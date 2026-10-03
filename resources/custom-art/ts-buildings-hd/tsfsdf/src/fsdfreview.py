"""Animated comparisons of the Firestorm Wall Section against TS's own GTFSDF / GTFSDF_A, from the package's frames:

  run-vs-original.gif       a run (a ring with a tail: corners, straights, a T, an end) three ways - TS's own frames
                            (x3.5) on TS's grid, HD in TS's angle, HD on the RA grid: the field off, switching on (the
                            live frames with GTFSDF_A pulsing on every emitter), off again; then damaged, off and on
                            (TS has no damaged frames - its 16-31 are rubble - so its panel stays healthy there)
  sections-vs-original.gif  every section (mask 00-15) on its own, TS | HD TS angle | HD RA grid at 2x: off, then the
                            field on with the pulse

    python3 fsdfreview.py"""
import os
import numpy as np
from PIL import Image, ImageDraw
import ypreview as P
import fsdfpack as F

OUT = f'{F.PKG}/previews'
DARK = (30, 30, 30, 255)
RUN = F.RING | {(4, 2), (5, 2)}             # a 4x3 ring with a tail east off its south-east corner: a T there, an end


def ts_sec(k, live=False, a=None):
    im = F.ts(k + (32 if live else 0))
    if a is not None:
        im.alpha_composite(F.ts(a, 'GTFSDF_A'))
    return im


def hd_sec(view, k, add=0, a=None):
    im = F.fr(view, k + add)
    if a is not None:
        im.alpha_composite(F.pulse(view, a))
    return im


def ra_run(getter, cells, cols=8, rows=5, at=(1, 1)):
    cv = P.canvas(cols, rows)
    for c in sorted(cells, key=lambda c: (c[1], c[0])):
        P.paste(cv, getter(F.mask_of(cells, c)), (at[0] + c[0]) * 128 - 24, (at[1] + c[1]) * 128 - 96)
    return cv


def panel(im, title, w, h, sub=None):
    t = im.convert('RGBA')
    s = min(w / t.width, (h - 34) / t.height)
    t = t.resize((max(1, int(t.width * s)), max(1, int(t.height * s))), Image.LANCZOS)
    c = Image.new('RGBA', (w, h), DARK)
    c.paste(P.on_bg(t), ((w - t.width) // 2, 34 + (h - 34 - t.height) // 2))
    d = ImageDraw.Draw(c)
    d.text((6, 4), title, fill=(255, 255, 0, 255))
    if sub:
        d.text((6, 18), sub, fill=(230, 230, 230, 255))
    return c


def row(ims, gap=8):
    W = sum(i.width for i in ims) + gap * (len(ims) - 1)
    S = Image.new('RGBA', (W, max(i.height for i in ims)), DARK)
    x = 0
    for i in ims:
        S.paste(i, (x, 0)); x += i.width + gap
    return S


def gif(frames, path, ms):
    q = [f.convert('RGB').quantize(colors=255, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=ms, loop=0, optimize=True)


def crop_run(im, box):
    return im.crop(box)


def run_gif():
    # crop boxes round the run, the same for every frame
    iso_box = (110, 20, 900, 520)
    ra_box = (96, 64, 1024 - 96 + 64, 640 - 64)
    W, H = 560, 400
    seq = ([('off', None)] * 5 + [('on', t % 4) for t in range(16)] + [('off', None)] * 4 +
           [('dmg', None)] * 5 + [('dmg-on', t % 4) for t in range(12)])
    frames = []
    for state, a in seq:
        live = state in ('on', 'dmg-on')
        add = {'off': 0, 'on': 32, 'dmg': 16, 'dmg-on': 48}[state]
        t_ = F.iso_run(RUN, lambda m: ts_sec(m, live, a if live else None))
        i_ = F.iso_run(RUN, lambda m: hd_sec('iso', m, add, a if live else None))
        r_ = ra_run(lambda m: hd_sec('ra', m, add, a if live else None), RUN)
        sub = {'off': 'the field off', 'on': 'the field on: GTFSDF_A pulsing on every emitter',
               'dmg': 'damaged, the field off', 'dmg-on': 'damaged, the field on'}[state]
        ts_sub = sub if not state.startswith('dmg') else ('TS has no damaged frames (16-31 are rubble): healthy shown'
                                                          + (', the field on' if live else ''))
        frames.append(row([panel(t_.crop(iso_box), "TS's own frames (GTFSDF x3.5) on TS's grid", W, H, ts_sub),
                           panel(i_.crop(iso_box), 'HD, TS angle', W, H, sub),
                           panel(r_.crop(ra_box), "HD, RA grid (RA's wall view)", W, H, sub)]))
    gif(frames, f'{OUT}/run-vs-original.gif', 150)
    return frames


def sections_gif():
    band = (0, 84, 176, 236)
    frames = []
    for m in range(16):
        for state, a in [('off', None)] * 3 + [('on', t % 4) for t in range(4)]:
            live = state == 'on'
            t_ = ts_sec(m, live, a).crop(band)
            i_ = hd_sec('iso', m, 32 if live else 0, a).crop(band)
            r_ = hd_sec('ra', m, 32 if live else 0, a).crop(band)
            sub = f"mask {m:02d} (N1 E2 S4 W8): frame {m + (32 if live else 0):02d}" + (', GTFSDF_A %d' % a if live else ', the field off')
            frames.append(row([panel(t_, 'TS GTFSDF', 360, 340, sub), panel(i_, 'HD, TS angle', 360, 340, sub),
                               panel(r_, 'HD, RA grid', 360, 340, sub)]))
    gif(frames, f'{OUT}/sections-vs-original.gif', 120)
    return frames


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    a = run_gif()
    a[8].convert('RGB').save(f'{OUT}/run-vs-original-on.png')
    b = sections_gif()
    print('done', len(a), len(b))
