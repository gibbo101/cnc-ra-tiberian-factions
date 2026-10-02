"""fit the Juggernaut walker with its upper body's shape taken from the cabin fit (the same body, seen in 32 facings
when deployed): the body's place on the walker (its front bu1 and roof bw1), the barrel pack, barrels, muzzles, arch,
hip, legs, the step's pose and TS's ground point are fitted to TS's 8 facings at a walk step.

    python3 jfitwalker.py cabin.json start.json out.json iters [seed] [step]
"""
import json, sys, time
import numpy as np
import cma
import jugg as JG
import jfit as JF

# the cabin's shape, relative to its front (bu1) and roof (bw1)
REL_U = ['bu0', 'hu0', 'hu1', 'anu']
REL_W = ['bw0', 'bwb']
SAME = ['bv', 'br', 'bch', 'hv', 'hh', 'hs', 'so', 'sh', 'anv', 'anh', 'anr']

SPEC = [('bu1', -2, 14), ('bw1', 22, 36), ('bsc', 0.85, 1.3),
        ('pu0', -4, 10), ('pu1', 2, 16), ('pv', 3, 10), ('pw0', 11, 26), ('pw1', 16, 32),
        ('bs', 2.5, 6), ('bz', 14, 30), ('brad', 1, 4), ('bl', 2, 16), ('ml', 1, 6), ('mh', 1, 4),
        ('au0', -6, 8), ('au1', 2, 16), ('ah', 0.5, 6), ('av', -4, 4),
        ('hp_u0', -10, -1), ('hp_u1', 0, 9), ('hp_v', 3, 10), ('hp_w0', 6, 20),
        ('jv', 3, 10), ('jw', 9, 24), ('ju', -6, 4), ('Lt', 4, 13), ('tw', 2, 6.5), ('td', 2, 7), ('Ls', 3, 13),
        ('sw', 2, 6), ('sd', 2, 6), ('lf', 3, 11), ('lh', 1, 7), ('fw', 3, 9), ('fh', 1, 4)]
POSE = [('lat', -80, 80), ('las', -80, 80), ('laf', -40, 40), ('rat', -80, 80), ('ras', -80, 80), ('raf', -40, 40),
        ('dw', -8, 8)]
CAM = [('ax', 46.5, 48.5), ('y0', 44, 56)]
ALL = SPEC + POSE + CAM


SCALED = ['bv', 'hv', 'hh', 'so', 'sh', 'anv', 'anh', 'anr']


def body_from(cab, bu1, bw1, bsc=1.0):
    """the cabin's shell, hatch and sensor moved to a front at bu1 and a roof at bw1, and scaled by bsc (the walker's
    sprite and the cabin's were drawn separately and need not share a scale exactly)."""
    out = {}
    for k in REL_U:
        out[k] = (cab[k] - cab['bu1']) * bsc + bu1
    for k in REL_W:
        out[k] = (cab[k] - cab['bw1']) * bsc + bw1
    for k in SAME:
        out[k] = cab[k] * (bsc if k in SCALED else 1.0)
    out['bu1'] = bu1; out['bw1'] = bw1
    return out


def unpack(x, cab):
    P = dict(JG.P0)
    for (k, *_), v in zip(SPEC, x[:len(SPEC)]):
        P[k] = float(v)
    P.update(body_from(cab, P['bu1'], P['bw1'], P['bsc']))
    n = len(SPEC)
    pose = [float(v) for v in x[n:n + 7]]
    return P, pose, float(x[n + 7]), float(x[n + 8])


def objective(V, x, cab, w_cls):
    P, pose, ax, y0 = unpack(x, cab)
    parts = JG.body_parts(P, pose)
    l = V.loss(parts, ax, y0, w_cls=w_cls)
    lows = JG.soles(P, pose)
    pen = (min(lows)) ** 2 + 2.0 * sum(max(0.0, -lo) ** 2 for lo in lows)
    pen += max(0.0, P['hp_w0'] - P['jw'] + 1.0) ** 2
    return l + 0.02 * pen


if __name__ == '__main__':
    cab = dict(JG.P0); cab.update(json.load(open(sys.argv[1]))['P'])
    st = json.load(open(sys.argv[2]))
    out = sys.argv[3]; iters = int(sys.argv[4])
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    step = int(sys.argv[6]) if len(sys.argv) > 6 else 0
    V = JF.Views([cw * 15 + step for cw in range(8)])
    lo = np.array([s[1] for s in ALL], float); hi = np.array([s[2] for s in ALL], float); span = hi - lo
    P0 = dict(JG.P0); P0.update(st['P'])
    P0.setdefault('bsc', 1.0)
    x0 = np.array([P0[k] for k, *_ in SPEC] + list(st['pose'][:7]) + [st['ax'], st['y0']], float)
    x0 = np.clip(x0, lo + 1e-3, hi - 1e-3)
    f = lambda z: objective(V, lo + np.clip(z, 0, 1) * span, cab, 0.6)
    es = cma.CMAEvolutionStrategy((x0 - lo) / span, 0.07, {'bounds': [0, 1], 'popsize': 24, 'maxiter': iters,
                                                          'seed': seed, 'verbose': -9})
    t0 = time.time(); it = 0
    print('start %.4f' % f((x0 - lo) / span), flush=True)
    while not es.stop():
        Z = es.ask(); es.tell(Z, [f(z) for z in Z]); it += 1
        if it % 10 == 0 or es.stop():
            P, pose, ax, y0 = unpack(lo + np.clip(es.result.xbest, 0, 1) * span, cab)
            json.dump(dict(P=P, pose=pose, ax=ax, y0=y0, f=es.result.fbest), open(out, 'w'), default=float)
            print('it', it, 'best %.4f' % es.result.fbest, '%.0fs' % (time.time() - t0), flush=True)
    print('done %.4f' % es.result.fbest, flush=True)
