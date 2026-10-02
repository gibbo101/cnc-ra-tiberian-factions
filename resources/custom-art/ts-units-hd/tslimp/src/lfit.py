"""fit the Limpet (limp.py) to TS's sprite (LIMPED frame 0) in TS's camera: silhouette plus colour classes.

    python3 lfit.py out.json iters
"""
import json, sys, time
import numpy as np
import cma
from PIL import Image
import rc
import limp as L
from paths import HANDOFF

# agreement of a model class (rows) with TS's (columns: 0 none, 1 house, 2 light grey, 3 khaki, 4 tan, 5 dark)
AGREE = np.array([[0, 0, 0, 0, 0, 0],
                  [0, 1.0, 0.0, 0.0, 0.0, 0.1],
                  [0, 0.0, 1.0, 0.3, 0.1, 0.4],
                  [0, 0.0, 0.3, 1.0, 0.5, 0.2],
                  [0, 0.0, 0.1, 0.5, 1.0, 0.5],
                  [0, 0.1, 0.3, 0.1, 0.4, 1.0]])

TS = HANDOFF + '/15-TSLIMP/ts-original/LIMPED/frames/limped-%03d.png'
WIN = (36, 6, 60, 38)


def ts_cls(f=0):
    a = np.asarray(Image.open(TS % f).convert('RGBA')).astype(int)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    c = np.zeros(r.shape, int)
    m = al > 0
    green = m & (r == 0) & (b == 0) & (g > 0)
    grey = m & ~green & (np.abs(r - g) < 12) & (np.abs(g - b) < 12)
    c[grey & ((r + g + b) / 3 >= 70)] = 2
    c[grey & ((r + g + b) / 3 < 70)] = 5
    c[green] = 1
    c[m & (c == 0)] = 1                       # the light (red, orange, white) sits on the dome
    x0, y0, x1, y1 = WIN
    return c[y0:y1, x0:x1], m[y0:y1, x0:x1]


def model_cls(parts, ax, y0, ss=4):
    x0, yw, x1, y1 = WIN; h, w = y1 - yw, x1 - x0
    cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
    t, who, nrm, O = rc.render_ids(parts, cam, x0, yw, w, h, ss=ss, zstart=100.0)
    cls_of = np.array([0] + [L.CLASS[p.comp] for p in parts])
    cl = cls_of[who + 1]
    return cl.reshape(h, ss, w, ss).transpose(0, 2, 1, 3).reshape(h, w, ss * ss)


TC, TM = ts_cls(0)


def loss(P, ax, y0, w_cls=0.6):
    cl = model_cls(L.parts(P), ax, y0)
    cov = (cl > 0).mean(-1)
    l = np.abs(cov - TM).sum() / TM.sum()
    both = TM & (cov >= 0.5) & (TC > 0)
    agree = AGREE[cl, TC[..., None]].mean(-1) / np.maximum(cov, 1e-6)
    return l + w_cls * (1 - agree[both]).sum() / TM.sum()


def iou(P, ax, y0):
    cov = (model_cls(L.parts(P), ax, y0) > 0).mean(-1) >= 0.5
    return (cov & TM).sum() / (cov | TM).sum()


# the cap, the nub and the lenses read straight off TS's pixels (row 14 grey 6 px wide; rows 12-13 dark, 2 then 4 px;
# the lenses 3 px either side of the axis on rows 26-27): the rest fitted
FIXED = dict(kr=3.0, kh=0.9, nr=1.6, nh=1.5, la=36.0)
SPEC = [('cf', 0.6, 1.0), ('ch', 2, 10), ('tr', 0.1, 2), ('br', 3, 7), ('bh', 0.8, 4), ('dr', 3, 7), ('dh', 2.5, 7),
        ('dz', -5, 2), ('lz', 0.2, 0.8), ('lr', 0.4, 1.4)]
CAM = [('ax', 46, 50), ('y0', 30, 37)]
ALL = SPEC + CAM

if __name__ == '__main__':
    out, iters = sys.argv[1], int(sys.argv[2])
    lo = np.array([a[1] for a in ALL]); hi = np.array([a[2] for a in ALL]); span = hi - lo
    L.P0.setdefault('cf', 0.85)
    x0 = np.array([L.P0[k] for k, *_ in SPEC] + [48.0, 33.0])

    def unpack(x):
        P = dict(L.P0); P.update(FIXED)
        for (k, *_), v in zip(SPEC, x):
            P[k] = float(v)
        P['cr'] = P['cf'] * P['br']                  # the cone's top inside the band
        return P, float(x[-2]), float(x[-1])
    f = lambda z: loss(*unpack(lo + np.clip(z, 0, 1) * span))
    z0 = np.clip((x0 - lo) / span, 1e-3, 1 - 1e-3)
    print('start %.4f' % f(z0), flush=True)
    es = cma.CMAEvolutionStrategy(z0, 0.15, {'bounds': [0, 1], 'popsize': 16, 'maxiter': iters, 'seed': 1, 'verbose': -9})
    t0 = time.time(); it = 0
    while not es.stop():
        Z = es.ask(); es.tell(Z, [f(z) for z in Z]); it += 1
        if it % 20 == 0 or es.stop():
            P, ax, y0 = unpack(lo + np.clip(es.result.xbest, 0, 1) * span)
            json.dump(dict(P=P, ax=ax, y0=y0, f=es.result.fbest), open(out, 'w'), default=float)
            print('it', it, 'best %.4f iou %.3f' % (es.result.fbest, iou(P, ax, y0)), '%.0fs' % (time.time() - t0), flush=True)
    print('done', flush=True)
