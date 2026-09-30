import numpy as np, time
from PIL import Image
import hyp, tsview as T

REF = {m: np.kron(np.array(Image.open(f'ref/frames/ntwall-{m:02d}.png').convert('RGBA'))[..., 3] > 0, np.ones((2, 2), bool)) for m in range(16)}


def score(p, masks=range(16)):
    tot = 0
    for m in masks:
        hit = T.render(hyp.model(m, p), S=2, dz=1 / (T.ZS * 2))[0]
        r = REF[m]
        tot += (hit & r).sum() / max((hit | r).sum(), 1)
    return tot / len(list(masks))


if __name__ == '__main__':
    p = dict(hyp.P)
    steps = dict(H=0.03, zc=0.05, ta=0.015, edge=0.03, tl=0.02, zl=0.04, R=0.04)
    masks = [0, 1, 3, 5, 6, 9, 10, 12, 15]
    best = score(p, masks)
    print('start %.4f' % best, flush=True)
    for it in range(3):
        for k, st in steps.items():
            for sgn in (+1, -1):
                while True:
                    q = dict(p); q[k] = p[k] + sgn * st
                    s = score(q, masks)
                    if s > best + 1e-4:
                        best, p = s, q
                        print(it, k, round(p[k], 3), '%.4f' % best, flush=True)
                    else:
                        break
        steps = {k: v / 2 for k, v in steps.items()}
    print('final', {k: round(v, 3) for k, v in p.items()}, '%.4f' % best)
    print('all16 %.4f' % score(p))
