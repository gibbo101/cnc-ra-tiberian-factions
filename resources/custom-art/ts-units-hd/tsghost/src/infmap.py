"""an infantry unit's in-mod frames as TS's sprite scaled: canvas = TS px x K + (dx, dy) (alpha IoU over the body and its
shadow, coarse then fine).

    python3 infmap.py 17-TSE1 E1 tse1
"""
import numpy as np
from PIL import Image

import sys
from paths import HANDOFF
ROOT = HANDOFF + '/'


def iou_for(ts_m, im_m, K, dx, dy):
    """scale TS's mask by K (nearest), place at (dx, dy) on the canvas, IoU with the in-mod mask."""
    H, W = im_m.shape
    ys, xs = np.mgrid[0:H, 0:W]
    tx = ((xs + 0.5 - dx) / K).astype(int); ty = ((ys + 0.5 - dy) / K).astype(int)
    ok = (tx >= 0) & (tx < ts_m.shape[1]) & (ty >= 0) & (ty < ts_m.shape[0])
    m = np.zeros_like(im_m)
    m[ok] = ts_m[ty[ok], tx[ok]]
    return (m & im_m).sum() / max((m | im_m).sum(), 1)


def fit(pairs, K0=6.4):
    """pairs: [(ts mask, in-mod mask)]: the best K, dx, dy."""
    # bbox estimate
    est = []
    for t, m in pairs:
        ty, tx = np.nonzero(t); my, mx = np.nonzero(m)
        K = (mx.max() - mx.min() + 1) / (tx.max() - tx.min() + 1)
        est.append((K, mx.min() - K * tx.min(), my.max() + 1 - K * (ty.max() + 1)))
    K, dx, dy = np.median(np.array(est), 0)
    best = None
    for k in np.arange(K - 0.2, K + 0.21, 0.05):
        for x in np.arange(dx - 8, dx + 8.1, 1.0):
            for y in np.arange(dy - 8, dy + 8.1, 1.0):
                s = np.mean([iou_for(t, m, k, x, y) for t, m in pairs[:2]])
                if best is None or s > best[0]:
                    best = (s, k, x, y)
    s, k0, x0, y0 = best
    for k in np.arange(k0 - 0.05, k0 + 0.051, 0.01):
        for x in np.arange(x0 - 1, x0 + 1.01, 0.25):
            for y in np.arange(y0 - 1, y0 + 1.01, 0.25):
                s = np.mean([iou_for(t, m, k, x, y) for t, m in pairs])
                if s > best[0]:
                    best = (s, k, x, y)
    return best



def mask(p, thr):
    return np.array(Image.open(p).convert('RGBA'))[..., 3] > thr


if __name__ == '__main__':
    d, ts, mod = sys.argv[1:4]
    TS = ROOT + d + '/ts-original/%s/frames/%s-%%03d.png' % (ts, ts.lower())
    INMOD = ROOT + d + '/in-mod/%s/frames/%s-%%04d.png' % (mod, mod)
    pairs = [(mask(TS % f, 0), mask(INMOD % f, 200)) for f in (0, 2, 4, 6)]
    print(d, fit(pairs, K0=3.2))
