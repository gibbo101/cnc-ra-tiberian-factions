"""
jbase.py - the Juggernaut's deployed base (DJUGG frame 0, one orientation: it deploys facing south-west, TS's CW
facing 5): a dark pivot column the cabin turns on, and four limbs splayed out to feet on the ground.  Fitted to TS's
base frame in TS's camera (30 degrees); the base frame shares DJUGGMK's and DJUGG_A's 96 x 96 coordinates.

Base frame: x east, y south, z up (world axes), origin = the pivot's foot on the ground.

    python3 jbase.py out.json iters [start.json|-] [seed]
"""
import json, sys, time
import numpy as np
import cma
import rc
import jugg as JG
import jfit as JF

PIVOT, RIM, LIMB, LKNEE, LFOOT = 91, 92, 93, 94, 95
JG.CLASS.update({PIVOT: 5, RIM: 5, LIMB: 4, LKNEE: 5, LFOOT: 4})

# the four limbs: yaw (degrees clockwise from north, world), hip height and reach, knee height; shared sizes
P0 = dict(pr=3.2, ph=17.0, rr=3.8, rh=1.2,
          y0_=200.0, y1_=250.0, y2_=110.0, y3_=20.0,          # yaws (TS: W, SSW, E, N)
          hh=12.0, hr=2.5, kh=8.0, kr=8.0, fr=13.0, lw=3.2, ld=3.4, fl=5.0, fw=4.0, fhh=2.0)


def limb(P, yaw):
    a = np.deg2rad(yaw)
    d = np.array([np.sin(a), -np.cos(a), 0.0])           # yaw clockwise from north (north = -y)
    H = d * P['hr'] + np.array([0, 0, P['hh']])
    K = d * P['kr'] + np.array([0, 0, P['kh']])
    F = d * P['fr'] + np.array([0, 0, P['fhh']])
    out = [rc.seg_box(H, K, P['lw'], P['ld'], LIMB, up=(0, 0, 1.0), chamfer=0.5, ext=0.6, name='limb_up'),
           rc.seg_box(K, F, P['lw'] * 0.9, P['ld'] * 0.9, LIMB, up=(0, 0, 1.0), chamfer=0.5, ext=0.5, name='limb_lo')]
    side = np.cross([0, 0, 1.0], d)
    out.append(rc.cylinder(K - side * P['lw'] * 0.55, K + side * P['lw'] * 0.55, P['ld'] * 0.42, LKNEE, 'lknee'))
    Rf = np.stack([d, side, [0, 0, 1.0]], 1)
    out.append(rc.box(F + d * P['fl'] * 0.25 + np.array([0, 0, -P['fhh'] / 2]), Rf,
                      (P['fl'] / 2, P['fw'] / 2, P['fhh'] / 2), LFOOT, chamfer=(0.5, 0.5, 0.4), name='lfoot'))
    return out


def base_parts(P):
    out = [rc.cylinder((0, 0, 0.0), (0, 0, P['ph']), P['pr'], PIVOT, 'pivot'),
           rc.cylinder((0, 0, P['ph'] - P['rh']), (0, 0, P['ph']), P['rr'], RIM, 'rim')]
    for k in range(4):
        out += limb(P, P['y%d_' % k])
    return out


class BaseView(JF.Views):
    def __init__(self, win=(26, 34, 94, 72)):
        self.frames = [0]; self.win = win
        x0, y0, x1, y1 = win
        c, m = JF.ts_cls(0, 'base')
        self.cls = [c[y0:y1, x0:x1]]; self.masks = [m[y0:y1, x0:x1]]

    def model_cls(self, parts, k, ax, y0, ss=2):
        x0, yw, x1, y1 = self.win; h, w = y1 - yw, x1 - x0
        cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
        t, who, nrm, O = rc.render_ids(parts, cam, x0, yw, w, h, ss=ss, zstart=200.0)
        cls_of = np.array([0] + [JG.CLASS[p.comp] for p in parts])
        cl = cls_of[who + 1]
        return cl.reshape(h, ss, w, ss).transpose(0, 2, 1, 3).reshape(h, w, ss * ss)


SPEC = [('pr', 1.5, 5), ('ph', 8, 24), ('rr', 2, 6), ('rh', 0.5, 3),
        ('y0_', 0, 360), ('y1_', 0, 360), ('y2_', 0, 360), ('y3_', 0, 360),
        ('hh', 4, 20), ('hr', 0, 6), ('kh', 2, 18), ('kr', 2, 16), ('fr', 6, 24), ('lw', 1.5, 6), ('ld', 1.5, 6),
        ('fl', 2, 9), ('fw', 2, 7), ('fhh', 1, 4)]
CAM = [('bax', 44, 56), ('by0', 50, 66)]
ALL = SPEC + CAM


def unpack(x):
    P = dict(P0)
    for (k, *_), v in zip(SPEC, x[:len(SPEC)]):
        P[k] = float(v)
    return P, float(x[len(SPEC)]), float(x[len(SPEC) + 1])


if __name__ == '__main__':
    out = sys.argv[1]; iters = int(sys.argv[2])
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    V = BaseView()
    lo = np.array([s[1] for s in ALL], float); hi = np.array([s[2] for s in ALL], float); span = hi - lo
    if len(sys.argv) > 3 and sys.argv[3] != '-':
        js = json.load(open(sys.argv[3])); Ps = dict(P0); Ps.update(js['P'])
        x0 = np.array([Ps[k] for k, *_ in SPEC] + [js['bax'], js['by0']], float)
    else:
        x0 = np.array([P0[k] for k, *_ in SPEC] + [50.5, 58.7], float)
    x0 = np.clip(x0, lo + 1e-3, hi - 1e-3)
    f = lambda z: (lambda P, ax, y0: V.loss(base_parts(P), ax, y0, w_cls=0.6))(*unpack(lo + np.clip(z, 0, 1) * span))
    es = cma.CMAEvolutionStrategy((x0 - lo) / span, 0.1, {'bounds': [0, 1], 'popsize': 20, 'maxiter': iters,
                                                         'seed': seed, 'verbose': -9})
    t0 = time.time(); it = 0
    print('start %.4f' % f((x0 - lo) / span), flush=True)
    while not es.stop():
        Z = es.ask(); es.tell(Z, [f(z) for z in Z]); it += 1
        if it % 10 == 0 or es.stop():
            P, ax, y0 = unpack(lo + np.clip(es.result.xbest, 0, 1) * span)
            json.dump(dict(P=P, bax=ax, by0=y0, f=es.result.fbest), open(out, 'w'), default=float)
            print('it', it, 'best %.4f' % es.result.fbest, '%.0fs' % (time.time() - t0), flush=True)
    print('done %.4f' % es.result.fbest, flush=True)
