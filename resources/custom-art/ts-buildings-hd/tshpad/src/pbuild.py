"""Build-up for the Power Plant: 24 frames in the order TS's GTPOWRMK (20 frames) builds it, without TS's
construction arm (Luke: not needed).

  0- 5  the middle of the slab spreads, then the round pads
  5- 8  the dark drum rises on the tower's site
  7-10  the east mound, the green pipes, the decks
 10-19  the cooling tower goes up course by course; the west mound, then the south one
 17-19  the green collar
 13-18  the east pod rises out of its mound, cap first, then its ring (the plant always has it)
 20-22  the rings and the plates on the other two sockets
 23     the finished plant with its east pod (= the healthy frame)"""
import os
import powr as PW

K = PW.BUILD_KEYS


def _p(**kw):
    d = {k: 0.0 for k in K}
    d.update(kw)
    return d


F = 1.0
ST = dict(slab=F, pads=F)
SEQ = [
    _p(slab=0.2),
    _p(slab=0.5),
    _p(slab=0.8),
    _p(slab=F, pads=0.3),
    _p(slab=F, pads=0.65),
    _p(**ST, drum=0.15),
    _p(**ST, drum=0.4),
    _p(**ST, drum=0.7, mound_ne=0.2),
    _p(**ST, drum=F, mound_ne=0.5, pipes=0.3),
    _p(**ST, drum=F, mound_ne=0.8, pipes=0.7, decks=0.4),
    _p(**ST, drum=F, mound_ne=F, pipes=F, decks=0.8, cone=0.08),
    _p(**ST, drum=F, mound_ne=F, pipes=F, decks=F, cone=0.18, mound_sw=0.3),
    _p(**ST, drum=F, mound_ne=F, pipes=F, decks=F, cone=0.28, mound_sw=0.6),
    _p(**ST, drum=F, mound_ne=F, pipes=F, decks=F, cone=0.38, mound_sw=0.9),
    _p(**ST, drum=F, mound_ne=F, pipes=F, decks=F, cone=0.48, mound_sw=F, mound_se=0.3),
    _p(**ST, drum=F, mound_ne=F, pipes=F, decks=F, cone=0.58, mound_sw=F, mound_se=0.6),
    _p(**ST, drum=F, mound_ne=F, pipes=F, decks=F, cone=0.68, mound_sw=F, mound_se=0.9),
    _p(**ST, drum=F, mound_ne=F, pipes=F, decks=F, cone=0.78, mound_sw=F, mound_se=F, collar=0.3),
    _p(**ST, drum=F, mound_ne=F, pipes=F, decks=F, cone=0.88, mound_sw=F, mound_se=F, collar=0.65),
    _p(**ST, drum=F, mound_ne=F, pipes=F, decks=F, cone=F, mound_sw=F, mound_se=F, collar=F),
    _p(**ST, drum=F, mound_ne=F, pipes=F, decks=F, cone=F, mound_sw=F, mound_se=F, collar=F, rings=0.5),
    _p(**ST, drum=F, mound_ne=F, pipes=F, decks=F, cone=F, mound_sw=F, mound_se=F, collar=F, rings=F, plates=0.5),
    _p(**ST, drum=F, mound_ne=F, pipes=F, decks=F, cone=F, mound_sw=F, mound_se=F, collar=F, rings=F, plates=F),
    dict(PW.DONE),
]
assert len(SEQ) == 24
# the east pod comes with the plant: it rises out of its mound, cap first, then its ring (TS's GTPOWRMK 11-15)
for _i, _v in zip(range(13, 23), (0.15, 0.3, 0.45, 0.62, 0.8, 1.0, 1.0, 1.0, 1.0, 1.0)):
    SEQ[_i]['pod'] = _v

OUT = '/home/claude/work/scratch/pbuild'
TSMK = '/home/claude/work/ts/ts-buildings-hd-handoff/02-TSPOWR/ts-original/GTPOWRMK/frames'
TS_N = 20


def ts_index(i):
    return int(round(i * (TS_N - 1) / (len(SEQ) - 1)))


def render(view_name, ss=2, frames=None):
    import prender as PR
    os.makedirs(f'{OUT}/{view_name}', exist_ok=True)
    view = PR.iso_view(ss) if view_name == 'iso' else PR.ra_view(8, ss)
    for i in (frames if frames is not None else range(len(SEQ))):
        pr = PR.Prep(view, prog=SEQ[i])
        pr.frame().save(f'{OUT}/{view_name}/b{i:02d}.png')
        print(view_name, i, flush=True)


def ts_frame(j):
    import numpy as np
    from PIL import Image
    import prender as PR
    K_, OX, OY = PR.ISO_K, -30.0, -53.5
    ts = np.array(Image.open(f'{TSMK}/{j:02d}.png').convert('RGBA'))
    yy, xx = np.mgrid[0:256, 0:256]
    tx = np.floor((xx + 0.5 - OX) / K_).astype(int); ty = np.floor((yy + 0.5 - OY) / K_).astype(int)
    ok = (tx >= 0) & (tx < 96) & (ty >= 0) & (ty < 96)
    out = np.zeros((256, 256, 4), np.uint8); out[ok] = ts[ty[ok], tx[ok]]
    return Image.fromarray(out)


def gif(path, hold=8, Z=2):
    from PIL import Image, ImageDraw
    BG = (90, 100, 80, 255)
    frames = []
    for i in list(range(len(SEQ))) + [len(SEQ) - 1] * hold:
        j = ts_index(i)
        ims = [ts_frame(j), Image.open(f'{OUT}/iso/b{i:02d}.png'), Image.open(f'{OUT}/ra/b{i:02d}.png')]
        W = sum(im.width * Z for im in ims) + 24; H = max(im.height * Z for im in ims) + 34
        S = Image.new('RGBA', (W, H), (30, 30, 30, 255)); d = ImageDraw.Draw(S); x = 0
        for k, im in enumerate(ims):
            b = Image.new('RGBA', im.size, BG); b.alpha_composite(im.convert('RGBA'))
            S.paste(b.resize((im.width * Z, im.height * Z), Image.NEAREST if k == 0 else Image.LANCZOS), (x, 34 + (H - 34 - im.height * Z) // 2))
            d.text((x + 6, 4), (f'TS GTPOWRMK (x3.36) {j:02d}/{TS_N - 1}', 'HD, TS angle', 'HD, RA grid')[k], fill=(255, 255, 0, 255))
            x += im.width * Z + 12
        d.text((6, 18), f'build-up {i:02d}/{len(SEQ) - 1}', fill=(255, 255, 255, 255))
        frames.append(S.convert('RGB').quantize(colors=255, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=120, loop=0, optimize=True)


def strip(path, pick=(0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 23)):
    from PIL import Image, ImageDraw
    BG = (90, 100, 80, 255)
    w = 192
    cols = len(pick) // 2
    S = Image.new('RGB', (cols * (w + 4), 6 * (w + 18)), (30, 30, 30))
    d = ImageDraw.Draw(S)
    for n, i in enumerate(pick):
        col, blk = n % cols, n // cols
        j = ts_index(i)
        for k, im in enumerate((ts_frame(j), Image.open(f'{OUT}/iso/b{i:02d}.png'), Image.open(f'{OUT}/ra/b{i:02d}.png'))):
            b = Image.new('RGBA', im.size, BG); b.alpha_composite(im.convert('RGBA'))
            h = int(round(w * im.height / im.width))
            tile = b.resize((w, h), Image.NEAREST if k == 0 else Image.LANCZOS).convert('RGB')
            if h > w:
                tile = tile.crop((0, h - w, w, h))
            y = (blk * 3 + k) * (w + 18)
            S.paste(tile, (col * (w + 4), y + 16))
            d.text((col * (w + 4) + 4, y + 2), (f'TS {j:02d}', f'HD {i:02d} TS angle', f'HD {i:02d} RA grid')[k], fill=(255, 255, 0))
    S.save(path)


if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'render':
        fr = [int(a) for a in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
        render(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 2, fr)
    elif sys.argv[1] == 'gif':
        gif(sys.argv[2])
    elif sys.argv[1] == 'strip':
        strip(sys.argv[2])
