"""fit the Hunter-Seeker (hseek.py) to TS's sprite (GGHUNT frame 4, between the flashes) in TS's camera: silhouette plus
colour classes.  The model starts from the readings in hseek.py; the fit only moves them within a pixel or two.

    python3 hsfit.py out.json iters [start.json]
"""
import json, sys, time
import numpy as np
import cma
from PIL import Image
import rc
import hseek as S
from paths import HANDOFF

TS = HANDOFF + '/16-TSHUNT/ts-original/GGHUNT/frames/gghunt-%03d.png'
WIN = (22, 2, 52, 38)
AGREE = np.array([[0, 0, 0, 0, 0, 0, 0],
                  [0, 1.0, 0.0, 0.0, 0.0, 0.1, 0.0],
                  [0, 0.0, 1.0, 0.3, 0.1, 0.4, 0.1],
                  [0, 0.0, 0.3, 1.0, 0.5, 0.2, 0.2],
                  [0, 0.0, 0.1, 0.5, 1.0, 0.5, 0.4],
                  [0, 0.1, 0.3, 0.1, 0.4, 1.0, 0.4],
                  [0, 0.0, 0.1, 0.2, 0.4, 0.4, 1.0]])
# TS's highlight on the shoulder's front (white, pink and grey among the bronze) is bronze, lit
HIGHLIGHT = (34, 21, 39, 24)


def ts_cls(f=4):
    a = np.asarray(Image.open(TS % f).convert('RGBA')).astype(int)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    m = al > 0
    c = np.zeros(r.shape, int)
    green = m & (r == 0) & (b == 0) & (g > 0)
    grey = m & ~green & (np.abs(r - g) < 14) & (np.abs(g - b) < 14)
    blue = m & ~green & (b > r + 20)
    warm = m & ~green & ~grey & ~blue
    c[warm] = 4
    c[grey & ((r + g + b) / 3 >= 100)] = 2
    c[grey & ((r + g + b) / 3 < 100)] = 5
    c[blue] = 5
    c[green] = 2
    red = m & ~green & (r - g > 35) & (g - b < 25) & (r + g + b < 300)
    c[red] = 6
    hx0, hy0, hx1, hy1 = HIGHLIGHT
    hl = np.zeros_like(m); hl[hy0:hy1, hx0:hx1] = True
    c[hl & grey & ((r + g + b) / 3 >= 100)] = 4
    x0, y0, x1, y1 = WIN
    return c[y0:y1, x0:x1], m[y0:y1, x0:x1]


def model_cls(parts, ax, y0, ss=4):
    x0, yw, x1, y1 = WIN; h, w = y1 - yw, x1 - x0
    cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
    t, who, nrm, O = rc.render_ids(parts, cam, x0, yw, w, h, ss=ss, zstart=100.0)
    cls_of = np.array([0] + [S.CLASS[p.comp] for p in parts])
    cl = cls_of[who + 1]
    return cl.reshape(h, ss, w, ss).transpose(0, 2, 1, 3).reshape(h, w, ss * ss)


TC, TM = ts_cls(4)


def loss(P, ax, y0, w_cls=0.6):
    cl = model_cls(S.parts(P), ax, y0)
    cov = (cl > 0).mean(-1)
    l = np.abs(cov - TM).sum() / TM.sum()
    both = TM & (cov >= 0.5) & (TC > 0)
    agree = AGREE[cl, TC[..., None]].mean(-1) / np.maximum(cov, 1e-6)
    return l + w_cls * (1 - agree[both]).sum() / TM.sum()


def iou(P, ax, y0):
    cov = (model_cls(S.parts(P), ax, y0) > 0).mean(-1) >= 0.5
    return (cov & TM).sum() / (cov | TM).sum()


SPEC = [('rb', 3.0, 4.2), ('zb', 4, 10), ('dbt', -1.5, 1.0), ('hbl', 4, 10),
        ('dch', -0.3, 0.8), ('rch', 2.2, 3.2), ('zs', 11.5, 15), ('sx', 4, 6.5), ('sb', 1.0, 2.2),
        ('lx', 4, 6), ('ldz', 0.3, 2.0), ('lr', 0.8, 1.9),
        ('gx', 3.0, 4.2), ('zg', 5.5, 10), ('gr', 0.6, 1.4),
        ('rn', 1.2, 1.8), ('znt', 21, 24), ('zc', 20.5, 23),
        ('bz0', 30.5, 31.5), ('bz1', 31.8, 32.5), ('zmt', 32.9, 33.6),
        ('rst', 1.2, 1.9), ('zst', 25.5, 28), ('ls', 0.6, 1.5), ('lsb', 0.3, 1.2),
        ('stz', 16, 19), ('stl', 3.5, 5.5), ('str_', 0.35, 0.6),
        ('wxa', 4.5, 7.5), ('wza', 14.5, 17), ('wb', 2.2, 5), ('wi', 1.2, 3), ('wtop', 2, 4), ('wh1', 1.2, 3),
        ('wh2', 4, 6),
        ('fr', 1.5, 3.5), ('fz', 2.5, 6), ('fl', 1.5, 4.5), ('fd', 1, 4), ('fw', 1.0, 2.0), ('fh', 0.8, 2.5),
        ('fa', 60, 130), ('tz', 7, 11), ('th', 1.2, 2.2)]
CAM = [('ax', 35.5, 37.5), ('y0', 33, 36.5)]
ALL = SPEC + CAM

if __name__ == '__main__':
    out, iters = sys.argv[1], int(sys.argv[2])
    lo = np.array([a[1] for a in ALL]); hi = np.array([a[2] for a in ALL]); span = hi - lo
    start = dict(S.P0)
    if len(sys.argv) > 3:
        js = json.load(open(sys.argv[3])); start.update(js['P']); start.update(ax=js['ax'], y0=js['y0'])
    start.setdefault('ax', 36.5); start.setdefault('y0', 34.6)
    x0 = np.array([start[k] for k, *_ in ALL])

    def unpack(x):
        P = dict(S.P0)
        for (k, *_), v in zip(SPEC, x):
            P[k] = float(v)
        return P, float(x[-2]), float(x[-1])
    f = lambda z: loss(*unpack(lo + np.clip(z, 0, 1) * span))
    z0 = np.clip((x0 - lo) / span, 1e-3, 1 - 1e-3)
    print('start %.4f' % f(z0), flush=True)
    es = cma.CMAEvolutionStrategy(z0, 0.12, {'bounds': [0, 1], 'popsize': 20, 'maxiter': iters, 'seed': 1, 'verbose': -9})
    t0 = time.time(); it = 0
    while not es.stop():
        Z = es.ask(); es.tell(Z, [f(z) for z in Z]); it += 1
        if it % 25 == 0 or es.stop():
            P, ax, y0 = unpack(lo + np.clip(es.result.xbest, 0, 1) * span)
            json.dump(dict(P=P, ax=ax, y0=y0, f=es.result.fbest), open(out, 'w'), default=float)
            print('it', it, 'best %.4f iou %.3f' % (es.result.fbest, iou(P, ax, y0)), '%.0fs' % (time.time() - t0), flush=True)
    print('done', flush=True)
