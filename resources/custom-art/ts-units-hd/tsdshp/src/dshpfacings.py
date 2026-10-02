"""the TS Dropship in all 32 directions (facings/): the ship level at each of the mod's facings (counter-clockwise from
north: 0 N, 8 W, 16 S, 24 E) on the same 656 x 656 canvas at the same size, turned about the canvas centre (where the
game puts the unit), so facing 8 is frames/ frame 0 exactly.  Each with an all-black -trim.png (it never takes house
colour).

    PKG=out python3 dshpfacings.py render PART N [ss] [sky]     renders facings/ (every N-th from PART)
    python3 dshpfacings.py previews PKG                          facings.png, facings-turn.gif
    python3 dshpfacings.py check PKG                             the canvas, alpha and trims; facing 8 = frame 0
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
import dshprender as R
import dshpspec as S

N = 32
NAMES = {0: 'N', 4: 'NW', 8: 'W', 12: 'SW', 16: 'S', 20: 'SE', 24: 'E', 28: 'NE'}
BG = (96, 108, 72, 255)
CROP = (0, 20, 656, 520)


def path(pkg, k):
    return '%s/facings/%s-%04d.png' % (pkg, S.NAME, k)


def render(pkg, part, n, ss=4, sky=True):
    from frameio import save
    os.makedirs(pkg + '/facings', exist_ok=True)
    u = R.load()
    for k in list(range(N))[part::n]:
        out = path(pkg, k)
        if os.path.exists(out) and os.path.exists(out[:-4] + '-trim.png'):
            continue
        t0 = time.time()
        img, _ = R.facing(u, k, ss, sky, house=S.GOLD)
        save(img, Image.new('L', S.CANVAS, 0), out)
        print('facing', k, '%.0fs' % (time.time() - t0), flush=True)
    print('done', flush=True)


def tile(pkg, k, scale=0.5):
    im = Image.open(path(pkg, k)).convert('RGBA')
    b = Image.new('RGBA', im.size, BG); b.alpha_composite(im)
    b = b.crop(CROP).convert('RGB')
    b = b.resize((round(b.size[0] * scale), round(b.size[1] * scale)), Image.LANCZOS)
    t = Image.new('RGB', (b.size[0], b.size[1] + 16), (28, 30, 34))
    t.paste(b, (0, 16))
    ImageDraw.Draw(t).text((4, 2), 'facing %d%s' % (k, (' (%s)' % NAMES[k]) if k in NAMES else ''), fill=(230, 220, 160))
    return t


def previews(pkg):
    pv = pkg + '/previews'
    os.makedirs(pv, exist_ok=True)
    tiles = [tile(pkg, k) for k in range(0, N, 4)]
    W, H = tiles[0].size
    out = Image.new('RGB', (4 * (W + 8) + 8, 2 * (H + 8) + 8), (20, 22, 26))
    for i, t in enumerate(tiles):
        out.paste(t, (8 + (i % 4) * (W + 8), 8 + (i // 4) * (H + 8)))
    out.save(pv + '/facings.png')
    frames = [tile(pkg, k, 0.4).convert('P', palette=Image.ADAPTIVE, colors=255) for k in range(N)]
    frames[0].save(pv + '/facings-turn.gif', save_all=True, append_images=frames[1:], duration=120, loop=0,
                   disposal=1)
    print('facing previews done')


def check(pkg):
    bad = []
    f0 = np.asarray(Image.open('%s/frames/%s-%04d.png' % (pkg, S.NAME, 0)))
    for k in range(N):
        p = path(pkg, k)
        if not (os.path.exists(p) and os.path.exists(p[:-4] + '-trim.png')):
            bad.append((k, 'missing')); continue
        a = np.asarray(Image.open(p))
        t = np.asarray(Image.open(p[:-4] + '-trim.png'))
        if a.shape[:2] != (S.CANVAS[1], S.CANVAS[0]) or a.shape[2] != 4:
            bad.append((k, 'size')); continue
        al = a[..., 3]
        if not (al > 0).any():
            bad.append((k, 'empty'))
        if al[0].any() or al[-1].any() or al[:, 0].any() or al[:, -1].any():
            bad.append((k, 'touches the canvas edge'))
        if t.any():
            bad.append((k, 'trim not black'))
        if k == 8 and not np.array_equal(a, f0):
            bad.append((k, 'facing 8 differs from frame 0'))
    return bad


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'render':
        render(os.environ['PKG'], int(sys.argv[2]), int(sys.argv[3]),
               int(sys.argv[4]) if len(sys.argv) > 4 else 4, bool(int(sys.argv[5])) if len(sys.argv) > 5 else True)
    elif cmd == 'previews':
        previews(sys.argv[2])
    elif cmd == 'check':
        print('facings: problems', check(sys.argv[2]))
