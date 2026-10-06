"""fit the Juggernaut's upper body (shell, hatch, sensor, dark front) to the deployed cabin's 32 facings (DJUGG_A,
counter-clockwise from north): the rigid body seen all the way round, with no legs or barrel pack in front of it.

    python3 jfitcabin.py out.json iters [start.json|-] [seed]
"""
import json, sys, time
import numpy as np
import cma
import rc
import jugg as JG
import jfit as JF

FRONT = 78          # the cabin's dark front plate (where the barrels mount)
JG.CLASS[FRONT] = 5

SPEC = [('bu0', -34, -11), ('bu1', -4, 12), ('bv', 7, 12), ('bw0', 11, 22), ('bwb', 14, 27), ('bw1', 24, 36),
        ('br', 1.0, 2.2), ('bch', 0, 4),
        ('hu0', -28, -4), ('hu1', -10, 8), ('hv', 4, 10), ('hh', 0.5, 5), ('hs', 0, 3), ('so', 0.2, 3), ('sh', 0.3, 2),
        ('anu', -32, -2), ('anv', -9, 9), ('anh', 1, 8), ('anr', 0.5, 2.0),
        ('fu', -3, 3), ('fv', 3, 10), ('fw0', 10, 24), ('fw1', 18, 32)]
CAM = [('ax', 44, 52), ('y0', 40, 75)]
ALL = SPEC + CAM


def cabin_parts(P):
    """the shell, the hatch and its slot, the sensor box at the back, and the dark front plate."""
    out = JG.upper_parts(P, 0.0)
    keep = [p for p in out if p.comp in (JG.SHELL, JG.HATCH, JG.SLOT)]
    if P.get('sensor', 0) >= 1.5:
        keep += JG.antenna_parts(P)                 # v2.1: the Titan's antenna in place of the box, as the walker's
    else:
        a = np.array([P['anu'], P['anv'], P['bw1'] - 0.5])
        keep.append(rc.box(a + np.array([0, 0, P['anh'] / 2]), np.eye(3), (P['anr'], P['anr'], P['anh'] / 2 + 0.5),
                           JG.ANT, name='sensor'))
    c = np.array([P['bu1'] + P['fu'] / 2 + 0.2, 0, (P['fw0'] + P['fw1']) / 2])
    keep.append(rc.box(c, np.eye(3), (abs(P['fu']) / 2 + 0.3, P['fv'], (P['fw1'] - P['fw0']) / 2), FRONT, name='front'))
    return keep


class CabinViews(JF.Views):
    def __init__(self, frames, win=(28, 26, 76, 62)):
        self.frames = list(frames)
        self.win = win
        x0, y0, x1, y1 = win
        self.cls, self.masks = [], []
        for f in self.frames:
            c, m = JF.ts_cls(f, 'cabin')
            self.cls.append(c[y0:y1, x0:x1]); self.masks.append(m[y0:y1, x0:x1])

    def model_cls(self, parts, k, ax, y0, ss=2):
        x0, yw, x1, y1 = self.win; h, w = y1 - yw, x1 - x0
        cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
        M = JG.facing_matrix((32 - self.frames[k]) % 32, 32)
        pk = [p.moved(M) for p in parts]
        t, who, nrm, O = rc.render_ids(pk, cam, x0, yw, w, h, ss=ss, zstart=200.0)
        cls_of = np.array([0] + [JG.CLASS[p.comp] for p in parts])
        cl = cls_of[who + 1]
        return cl.reshape(h, ss, w, ss).transpose(0, 2, 1, 3).reshape(h, w, ss * ss)


def unpack(x):
    P = dict(JG.P0)
    for (k, *_), v in zip(SPEC, x[:len(SPEC)]):
        P[k] = float(v)
    return P, float(x[len(SPEC)]), float(x[len(SPEC) + 1])


if __name__ == '__main__':
    out = sys.argv[1]; iters = int(sys.argv[2])
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    V = CabinViews(range(0, 32, 2))
    lo = np.array([s[1] for s in ALL], float); hi = np.array([s[2] for s in ALL], float); span = hi - lo
    if len(sys.argv) > 3 and sys.argv[3] != '-':
        js = json.load(open(sys.argv[3]))
        P0 = dict(JG.P0); P0.update(js['P'])
        P0.setdefault('anr', 1.0)
        for k, v in (('fu', 0.5), ('fv', 6.0), ('fw0', P0['bw0']), ('fw1', P0['bw1'] - 2)):
            P0.setdefault(k, v)
        x0 = np.array([P0[k] for k, *_ in SPEC] + [js.get('cax', 48.0), js.get('cy0', 60.0)], float)
    else:
        P0 = dict(JG.P0); P0.update(anr=1.0, fu=0.5, fv=6.0, fw0=16.0, fw1=26.0)
        x0 = np.array([P0[k] for k, *_ in SPEC] + [48.0, 60.0], float)
    x0 = np.clip(x0, lo + 1e-3, hi - 1e-3)
    f = lambda z: (lambda P, ax, y0: V.loss(cabin_parts(P), ax, y0, w_cls=0.6))(*unpack(lo + np.clip(z, 0, 1) * span))
    es = cma.CMAEvolutionStrategy((x0 - lo) / span, 0.1, {'bounds': [0, 1], 'popsize': 20, 'maxiter': iters,
                                                         'seed': seed, 'verbose': -9})
    t0 = time.time(); it = 0
    print('start %.4f' % f((x0 - lo) / span), flush=True)
    while not es.stop():
        Z = es.ask(); es.tell(Z, [f(z) for z in Z]); it += 1
        if it % 10 == 0 or es.stop():
            P, ax, y0 = unpack(lo + np.clip(es.result.xbest, 0, 1) * span)
            json.dump(dict(P=P, cax=ax, cy0=y0, f=es.result.fbest), open(out, 'w'), default=float)
            print('it', it, 'best %.4f' % es.result.fbest, '%.0fs' % (time.time() - t0), flush=True)
    print('done %.4f' % es.result.fbest, flush=True)
