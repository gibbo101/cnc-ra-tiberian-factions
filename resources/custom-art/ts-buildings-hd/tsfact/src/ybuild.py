"""Build-up for the Construction Yard: 32 frames in the order TS's GTCNSTMK (24 frames) builds it.

  0     the MCV where the unit deployed, facing south-west (yard.MCV_FROM)
  1- 8  it deploys: the concrete pad spreads out from under it while it drives to where the crane stands
        (2-8); once the pad reaches the west edge (6-9) the foot rail slides out north along it
  9-14  the seven ribs grow from the west foot up and over
 13-19  the east half is clad from the north end to the south (roof, window-box base, south wall) - TS starts
        the cladding while the ribs are still going up
 18-22  the grey panels fill in between the ribs from the foot up; the fans go in
 23-27  the MCV folds down into the crane's base and the boom swings up
 27-30  the window box and the stacks rise
 20     the roof lamps come on (TS lights them as soon as the roof is on), 22 the door lamp
 31     the finished building (= the healthy frame)"""
import yard as Y

K = Y.BUILD_KEYS


def _p(**kw):
    d = {k: 0.0 for k in K}
    d.update(kw)
    return d


F = 1.0
PAD = [0.0, 0.04, 0.12, 0.22, 0.33, 0.45, 0.58, 0.72, 0.86, F]
RAIL = {6: 0.02, 7: 0.2, 8: 0.5, 9: 0.8}
RIBS = {9: 0.12, 10: 0.3, 11: 0.48, 12: 0.66, 13: 0.84}
CLAD = {13: 0.08, 14: 0.22, 15: 0.38, 16: 0.54, 17: 0.7, 18: 0.86}
PANELS = {18: 0.2, 19: 0.4, 20: 0.6, 21: 0.8}
FANS = {19: 0.5, 20: 0.5, 21: 1.0}
DRIVE = {2: 0.06, 3: 0.2, 4: 0.38, 5: 0.57, 6: 0.74, 7: 0.88, 8: 0.97}
MCV = {23: 0.2, 24: 0.4, 25: 0.6, 26: 0.8}
CRANE = {24: 0.1, 25: 0.3, 26: 0.55, 27: 0.8}
BOX = {27: 0.15, 28: 0.45, 29: 0.75}
STACKS = {28: 0.2, 29: 0.5, 30: 0.8}


def _at(tab, i, start):
    """value at frame i: the table's value, 0 before the table starts, 1 after it ends."""
    if i in tab:
        return tab[i]
    return 0.0 if i < start else 1.0


SEQ = []
for i in range(31):
    SEQ.append(_p(pad=PAD[min(i, len(PAD) - 1)],
                  rail=_at(RAIL, i, 6), ribs=_at(RIBS, i, 9), clad=_at(CLAD, i, 13), panels=_at(PANELS, i, 18),
                  fans=_at(FANS, i, 19), mcv=_at(MCV, i, 23), crane=_at(CRANE, i, 24), box=_at(BOX, i, 27),
                  stacks=_at(STACKS, i, 28), drive=_at(DRIVE, i, 2)))
# TS lights the roof lamps as soon as the roof is on, and the door lamp once the south wall is up
for i in range(20, 31):
    SEQ[i]['lamps'] = 1.0
for i in range(22, 31):
    SEQ[i]['door'] = 1.0
SEQ.append(dict(Y.DONE))
assert len(SEQ) == 32


# ------------------------------------------------------------------------------------------ rendering / previews
OUT = '/home/claude/work/scratch/build'
TSMK = '/home/claude/work/ts/ts-buildings-hd-handoff/01-TSFACT/ts-original/GTCNSTMK/frames'
TS_N = 24                                              # GTCNSTMK's drawn frames (the rest are empty)


def render(view_name, ss=2, frames=None):
    import os
    import yanim as A, yrender as R
    os.makedirs(f'{OUT}/{view_name}', exist_ok=True)
    view = R.iso_view(ss) if view_name == 'iso' else R.ra_view(52, ss)
    for i in (frames if frames is not None else range(len(SEQ))):
        pr = A.Prep(view, prog=SEQ[i])
        pr.frame().save(f'{OUT}/{view_name}/b{i:02d}.png')
        print(view_name, i, flush=True)


def ts_frame(j):
    import numpy as np
    from PIL import Image
    a = np.array(Image.open(f'{TSMK}/{j:02d}.png').convert('RGBA'))
    big = np.repeat(np.repeat(a, 3, 0), 3, 1)
    return Image.fromarray(big[166:166 + 256, 42:42 + 384])


def ts_index(i):
    return int(round(i * (TS_N - 1) / (len(SEQ) - 1)))


def gif(path, hold=12):
    from PIL import Image, ImageDraw
    BG = (90, 100, 80, 255)
    frames = []
    for i in list(range(len(SEQ))) + [len(SEQ) - 1] * hold:
        S = Image.new('RGBA', (384 * 3 + 24, 360 + 34), (30, 30, 30, 255))
        d = ImageDraw.Draw(S)
        j = ts_index(i)
        for k, (im, dy) in enumerate(((ts_frame(j), 52), (Image.open(f'{OUT}/iso/b{i:02d}.png'), 52),
                                      (Image.open(f'{OUT}/ra/b{i:02d}.png'), 0))):
            b = Image.new('RGBA', im.size, BG); b.alpha_composite(im.convert('RGBA'))
            S.paste(b, (k * 396, 34 + dy))
        d.text((6, 4), f'TS GTCNSTMK (x3)  frame {j:02d}/{TS_N - 1}', fill=(255, 255, 0, 255))
        d.text((402, 4), 'HD, TS angle', fill=(255, 255, 0, 255))
        d.text((798, 4), 'HD, RA grid', fill=(255, 255, 0, 255))
        d.text((402, 18), f'frame {i:02d}/{len(SEQ) - 1}', fill=(255, 255, 255, 255))
        frames.append(S.convert('RGB').quantize(colors=255, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=110, loop=0, optimize=True)


def strip(path, pick=(0, 3, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 31)):
    """TS above, ours (TS angle) below, for a handful of frames."""
    from PIL import Image, ImageDraw
    BG = (90, 100, 80, 255)
    w, h = 384 // 2, 256 // 2
    S = Image.new('RGB', (len(pick) // 2 * (w + 4), 4 * (h + 16)), (30, 30, 30))
    d = ImageDraw.Draw(S)
    for n, i in enumerate(pick):
        col, blk = n % (len(pick) // 2), n // (len(pick) // 2)
        j = ts_index(i)
        for k, im in enumerate((ts_frame(j), Image.open(f'{OUT}/iso/b{i:02d}.png'))):
            b = Image.new('RGBA', im.size, BG); b.alpha_composite(im.convert('RGBA'))
            y = (blk * 2 + k) * (h + 16)
            S.paste(b.resize((w, h), Image.LANCZOS).convert('RGB'), (col * (w + 4), y + 14))
            d.text((col * (w + 4) + 4, y + 1), (f'TS {j:02d}' if k == 0 else f'HD {i:02d}'), fill=(255, 255, 0))
    S.save(path)


if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'render':
        fr = [int(a) for a in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
        render(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 2, fr)
    elif sys.argv[1] == 'gif':
        gif(sys.argv[2] if len(sys.argv) > 2 else '/home/claude/work/out/checkpoint/yard-buildup-vs-ts.gif')
    elif sys.argv[1] == 'strip':
        strip(sys.argv[2] if len(sys.argv) > 2 else '/home/claude/work/out/checkpoint/yard-buildup-strip.png')
