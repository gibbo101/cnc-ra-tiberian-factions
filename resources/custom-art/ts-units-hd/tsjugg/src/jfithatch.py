"""refit the hatch on the cabin's roof (and the roof's height) to DJUGG_A's 32 facings with TS's white faces told
apart from its light grey ones: TS draws the hatch's top light grey (its palette 14, 39-51) and the sides that face
the camera white (15, 33-38), so the hatch's height and width show apart from the silhouette.  The shell's other
sizes stay as the cabin fit has them.

    python3 jfithatch.py out.json iters
"""
import json, sys, time
import numpy as np
import cma
import rc
import jugg as JG
import jfit as JF
import jfitcabin as JC
from jclass import classes, HOUSE, LGREY, DGREY, KHAKI, TAN, BRIGHT, OLIVE, BLUE

WHITE_IDX = {15, 33, 34, 35, 36, 37, 38}
# agreement, model class (rows) against TS's (columns): 0 none, 1 house, 2 light grey, 3 khaki, 4 tan, 5 dark, 6 white
A7 = np.zeros((7, 7))
A7[:6, :6] = JF.AGREE
A7[6, 6] = 1.0; A7[6, 2] = A7[2, 6] = 0.35; A7[6, 5] = A7[5, 6] = 0.05


def ts_cls7(f):
    c, im = classes('cabin', f)
    out = np.zeros(c.shape, int)
    out[c == HOUSE] = 1
    out[c == LGREY] = 2
    out[np.isin(im, list(WHITE_IDX))] = 6
    out[im == 13] = 5
    out[(c == KHAKI)] = 3
    out[(c == TAN) | (c == BRIGHT)] = 4
    out[(c == OLIVE) | (c == DGREY) | (c == BLUE)] = 5
    return out, c > 0


class HatchViews(JC.CabinViews):
    def __init__(self, frames, win=(28, 26, 76, 62)):
        self.frames = list(frames); self.win = win
        x0, y0, x1, y1 = win
        self.cls, self.masks = [], []
        for f in self.frames:
            c, m = ts_cls7(f)
            self.cls.append(c[y0:y1, x0:x1]); self.masks.append(m[y0:y1, x0:x1])

    def model_cls(self, parts, k, ax, y0, ss=2):
        x0, yw, x1, y1 = self.win; h, w = y1 - yw, x1 - x0
        cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
        M = JG.facing_matrix((32 - self.frames[k]) % 32, 32)
        pk = [p.moved(M) for p in parts]
        t, who, nrm, O = rc.render_ids(pk, cam, x0, yw, w, h, ss=ss, zstart=200.0)
        cls_of = np.array([0] + [JG.CLASS[p.comp] for p in parts])
        cl = cls_of[who + 1]
        hatch = np.array([False] + [p.comp == JG.HATCH for p in parts])[who + 1]
        cl = np.where(hatch & (nrm[..., 2] < 0.7), 6, cl)
        return cl.reshape(h, ss, w, ss).transpose(0, 2, 1, 3).reshape(h, w, ss * ss)

    def loss(self, parts, ax, y0, ss=2, w_cls=0.8):
        out = []
        for k in range(len(self.frames)):
            cl = self.model_cls(parts, k, ax, y0, ss)
            cov = (cl > 0).mean(-1); m = self.masks[k]
            l = np.abs(cov - m).sum() / m.sum()
            tc = self.cls[k]; both = m & (cov >= 0.5) & (tc > 0)
            agree = A7[cl, tc[..., None]].mean(-1) / np.maximum(cov, 1e-6)
            l += w_cls * (1 - agree[both]).sum() / m.sum()
            out.append(l)
        return float(np.mean(out))


SPEC = [('bw1', 22, 31), ('hu0', -20, -4), ('hu1', -4, 6), ('hv', 3, 9), ('hh', 0.8, 6), ('hs', 0, 2.5),
        ('rf0', 0.3, 0.8), ('rf1', 0.0, 0.45), ('rvf', 0.15, 0.7)]


def parts_of(P):
    return JC.cabin_parts(P) + JG.details(P)


def unpack(x, base):
    P = dict(base)
    for (k, *_), v in zip(SPEC, x):
        P[k] = float(v)
    return P


if __name__ == '__main__':
    out, iters = sys.argv[1], int(sys.argv[2])
    jc = json.load(open('fit_cabin_a.json'))
    base = dict(JG.P0); base.update(jc['P'])
    base.update(rf0=0.574, rf1=0.164, rvf=0.375)
    V = HatchViews(range(0, 32, 2))
    lo = np.array([s[1] for s in SPEC]); hi = np.array([s[2] for s in SPEC]); span = hi - lo
    x0 = np.clip((np.array([base[k] for k, *_ in SPEC]) - lo) / span, 1e-3, 1 - 1e-3)
    f = lambda z: V.loss(parts_of(unpack(lo + np.clip(z, 0, 1) * span, base)), jc['cax'], jc['cy0'])
    print('start %.4f' % f(x0), flush=True)
    es = cma.CMAEvolutionStrategy(x0, 0.12, {'bounds': [0, 1], 'popsize': 14, 'maxiter': iters, 'seed': 1,
                                             'verbose': -9})
    t0 = time.time(); it = 0
    while not es.stop():
        Z = es.ask(); es.tell(Z, [f(z) for z in Z]); it += 1
        if it % 5 == 0 or es.stop():
            P = unpack(lo + np.clip(es.result.xbest, 0, 1) * span, base)
            json.dump(dict(P=P, cax=jc['cax'], cy0=jc['cy0'], f=es.result.fbest), open(out, 'w'), default=float)
            print('it', it, 'best %.4f' % es.result.fbest, {k: round(P[k], 2) for k, *_ in SPEC},
                  '%.0fs' % (time.time() - t0), flush=True)
    print('done %.4f' % es.result.fbest, flush=True)
