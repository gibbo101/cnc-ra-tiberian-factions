"""Checks on the finished Power Plant package: counts, sizes, trims, overlays, the pod piece, the house green."""
import glob, os
import numpy as np
from PIL import Image
from pfinal import PKG, NAME, VIEWS as V, POD_NAMES

HAND = '/home/claude/work/ts/ts-buildings-hd-handoff/02-TSPOWR'
YARD = '/home/claude/work/out/ts-gdi-construction-yard-hd'
SIZE = {'ts-angle': (256, 256), 'ra-grid': (256, 272)}
EXPECT = {'plant': 2, 'A-lights': 24, 'B-pods/east': 24, 'B-pods/middle': 24, 'B-pods/west': 24, 'loop': 72,
          'pod-128': 2, 'pod-128/turning': 24, 'build-up': 24}
bad = []


def arr(p):
    return np.array(Image.open(p).convert('RGBA')).astype(int)


for v in V.values():
    for sub, n in EXPECT.items():
        fs = sorted(f for f in glob.glob(f'{PKG}/{v}/{sub}/*.png') if not f.endswith('-trim.png'))
        ts = sorted(glob.glob(f'{PKG}/{v}/{sub}/*-trim.png'))
        size = (128, 128) if sub.startswith('pod-128') else SIZE[v]
        sizes = {Image.open(f).size for f in fs + ts}
        modes = {Image.open(f).mode for f in ts}
        ok = len(fs) == n and len(ts) == n and sizes == {size} and modes <= {'L'}
        print(f'{v:9s} {sub:16s} {len(fs):3d} frames {len(ts):3d} trims  sizes {sizes}  {"ok" if ok else "BAD"}')
        if not ok:
            bad.append((v, sub))
        for f in fs:
            a = arr(f)
            t = np.array(Image.open(f[:-4] + '-trim.png')).astype(int)
            if (t[a[..., 3] == 0] > 0).any():
                bad.append(('trim outside alpha', f))
    # the last build-up frame is the healthy plant
    if not (arr(f'{PKG}/{v}/build-up/{NAME}-build-23.png') == arr(f'{PKG}/{v}/plant/{NAME}-00.png')).all():
        bad.append(('build 23 != plant 00', v))
    # overlays drawn in order give back the straight loop frames; lights never overlap a pod
    for lv in (0, 1):
        for npods in (1, 2, 3):
            worst, most = 0, 0
            for t in range(12):
                i = t + 12 * lv
                c = Image.open(f'{PKG}/{v}/plant/{NAME}-{lv:02d}.png').convert('RGBA')
                for nm in POD_NAMES[:npods]:
                    c.alpha_composite(Image.open(f'{PKG}/{v}/B-pods/{nm}/{NAME}-pod-{nm}-{i:02d}.png').convert('RGBA'))
                c.alpha_composite(Image.open(f'{PKG}/{v}/A-lights/{NAME}-lights-{i:02d}.png').convert('RGBA'))
                L = arr(f'{PKG}/{v}/loop/{NAME}-loop-{(2 * (npods - 1) + lv) * 12 + t:02d}.png')
                d = np.abs(np.array(c).astype(int) - L).max(axis=2)
                worst, most = max(worst, int(d.max())), max(most, int((d > 8).sum()))
            print(f'{v:9s} level {lv} {npods} pods: overlays vs loop max diff {worst}, px > 8: {most}')
            if most > 40:                    # a few antialiased edge pixels can't be matched by an overlay
                bad.append(('overlays != loop', v, lv, npods, worst, most))
        lit = np.zeros(SIZE[v][::-1], bool)
        for t in range(12):
            lit |= arr(f'{PKG}/{v}/A-lights/{NAME}-lights-{t + 12 * lv:02d}.png')[..., 3] > 0
        for nm in POD_NAMES:
            pa = np.zeros_like(lit)
            for t in range(12):
                pa |= arr(f'{PKG}/{v}/B-pods/{nm}/{NAME}-pod-{nm}-{t + 12 * lv:02d}.png')[..., 3] > 0
            if (pa & lit).any():
                bad.append(('lights overlap pod', v, lv, nm, int((pa & lit).sum())))
        # the 12-frame turn closes: frame 11 -> 00 is a step like the others
        d = [np.abs(arr(f'{PKG}/{v}/loop/{NAME}-loop-{lv * 12 + (t + 1) % 12:02d}.png')
                    - arr(f'{PKG}/{v}/loop/{NAME}-loop-{lv * 12 + t:02d}.png')).sum() for t in range(12)]
        print(f'{v:9s} level {lv} loop steps (sum abs diff, k): ' + ' '.join('%d' % (x / 1000) for x in d))

# the pod piece vs the mod's TSTURB (TS angle): where the rings sit
tt = arr(f'{HAND}/in-mod/tsturb-0000.png')
ours = arr(f'{PKG}/ts-angle/pod-128/power-pod-00.png')
green = lambda a: (a[..., 3] > 128) & (a[..., 1] > 120) & (a[..., 1] > 1.6 * a[..., 0]) & (a[..., 1] > 1.6 * a[..., 2])
for nm, a in (('mod tsturb', tt), ('HD piece ', ours)):
    ys, xs = np.nonzero(green(a))
    ya, xa = np.nonzero(a[..., 3] > 20)
    print(f'{nm}: green ring x {xs.min()}-{xs.max()} y {ys.min()}-{ys.max()} centre ({(xs.min() + xs.max()) / 2:.1f}, '
          f'{(ys.min() + ys.max()) / 2:.1f});  everything x {xa.min()}-{xa.max()} y {ya.min()}-{ya.max()}')
ia, ib = tt[..., 3] > 20, ours[..., 3] > 20
print('alpha overlap (IoU) with the mod\'s piece: %.2f' % ((ia & ib).sum() / (ia | ib).sum()))

# house green: the plant's fully-trim pixels vs the yard's (hue and the share of green)
def house(path):
    a = arr(path)
    t = np.array(Image.open(path[:-4] + '-trim.png')) > 250
    px = a[t & (a[..., 3] == 255)][:, :3].astype(float)
    g = px[:, 1] / np.maximum(px.sum(axis=1), 1)
    return np.median(px, axis=0), np.median(g), np.percentile(px[:, 1], (10, 50, 90))
for v in V.values():
    for nm, p in (('yard ', f'{YARD}/{v}/yard/construction-yard-00.png'), ('plant', f'{PKG}/{v}/plant/{NAME}-00.png')):
        m, g, pc = house(p)
        print(f'{v:9s} {nm} house px median RGB {m.round()}  green share {g:.3f}  G p10/50/90 {pc.round()}')

sz = sum(os.path.getsize(f) for f in glob.glob(f'{PKG}/**/*', recursive=True) if os.path.isfile(f))
print('package %.1f MiB' % (sz / 2 ** 20))
print('PROBLEMS:', bad if bad else 'none')
