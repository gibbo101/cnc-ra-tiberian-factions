"""fit the Wolverine's shape and standing pose to TS's 8 standing frames (SMECH 96-103).

    python3 wfitstand.py out.json iters [start.json] [seed]
"""
import json, sys, time
import numpy as np
import cma
import wolf as WF
import wfit as WFT

SPEC = [('tu0', -6, -1), ('tu1', 1, 5), ('tv', 2.4, 5.0), ('tw0', 10, 18), ('tch', 0.3, 2.0), ('tcb', 0.0, 3.0),
        ('wu0', -4.5, -0.5), ('wu1', 0.5, 4.5), ('wv', 1.5, 5), ('ww0', 8, 15),
        ('hu0', -6, -1), ('hu1', 1.5, 6), ('hv', 2.5, 5), ('hcv', -1.5, 1.5), ('hw0', 18, 24), ('hw1', 24, 30),
        ('hs', 0, 5), ('hsu', -4, 3), ('nw', 0.3, 2),
        ('pu0', -8, -3), ('pu1', -5, -1.5), ('pv', 2, 5), ('pw0', 11, 20), ('pw1', 20, 28),
        ('su0', -4, 0), ('su1', 0, 4), ('sv0', 2.5, 6), ('sv1', 6, 10), ('sw0', 15, 23), ('sw1', 20, 27), ('sch', 0, 2.5),
        ('au0', -3, 0), ('au1', 0, 3), ('agap', 0.3, 3.0), ('av1', 6.0, 10), ('aw0', 10, 16), ('aw1', 16, 23),
        ('gv', 5.5, 10), ('gw', 12, 18), ('gu0', -6, 0), ('gu1', 4, 9), ('gh', 0.6, 2.2), ('gk', 0.6, 2.2), ('gm', 0.6, 3),
        ('anu', -4, 1), ('anv', 2.5, 6), ('antop', 30, 38),
        ('pel_u0', -4, 0), ('pel_u1', 0, 4), ('pel_v', 1.5, 4.5), ('pel_w0', 7, 11), ('pel_w1', 11, 15),
        ('jv', 2.5, 6), ('jw', 8, 14), ('ju', -2, 2), ('Lt', 3, 8), ('tw', 2, 5), ('td', 2, 5), ('Ls', 3, 8),
        ('sw', 1.8, 4.5), ('sd', 1.8, 4.5), ('lf', 3, 8), ('lh', 1, 5), ('fw', 3.5, 8), ('fh', 1, 3.5)]
POSE = [('lat', -35, 35), ('las', -35, 35), ('laf', -25, 25), ('rat', -35, 35), ('ras', -35, 35), ('raf', -25, 25)]
CAM = [('ax', 47.5, 49.0), ('y0', 48.0, 53.0)]
ALL = SPEC + POSE + CAM


def unpack(x):
    P = dict(WF.P0)
    for (k, *_), v in zip(SPEC, x[:len(SPEC)]):
        P[k] = float(v)
    n = len(SPEC)
    pose = [float(v) for v in x[n:n + 6]] + [0.0]
    ax, y0 = float(x[n + 6]), float(x[n + 7])
    return P, pose, ax, y0


def pack(P, pose, ax, y0):
    return [P[k] for k, *_ in SPEC] + list(pose[:6]) + [ax, y0]


W_CLS = 0.5


def objective(V, x):
    P, pose, ax, y0 = unpack(x)
    parts = WF.body_parts(P, pose)
    l = V.loss(parts, ax, y0, w_cls=W_CLS)
    lows = WF.soles(P, pose)
    pen = (min(lows)) ** 2 + 2.0 * sum(max(0.0, -lo) ** 2 for lo in lows)
    return l + 0.02 * pen


if __name__ == '__main__':
    out = sys.argv[1]; iters = int(sys.argv[2])
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    W_CLS = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
    V = WFT.Views(range(96, 104))
    lo = np.array([s[1] for s in ALL], float); hi = np.array([s[2] for s in ALL], float); span = hi - lo
    if len(sys.argv) > 3 and sys.argv[3] != '-':
        js = json.load(open(sys.argv[3]))
        P = dict(WF.P0); P.update(js['P'])
        x0 = np.array(pack(P, js['pose'], js['ax'], js['y0']), float)
        sigma = 0.06
    else:
        x0 = np.array(pack(WF.P0, [0, 0, 0, 0, 0, 0, 0], 48.25, 50.5), float)
        sigma = 0.12
    x0 = np.clip(x0, lo + 1e-3, hi - 1e-3)
    f = lambda z: objective(V, lo + np.clip(z, 0, 1) * span)
    es = cma.CMAEvolutionStrategy((x0 - lo) / span, sigma, {'bounds': [0, 1], 'popsize': 24, 'maxiter': iters,
                                                            'seed': seed, 'verbose': -9})
    t0 = time.time(); it = 0
    print('start %.4f' % f((x0 - lo) / span), flush=True)
    while not es.stop():
        Z = es.ask(); es.tell(Z, [f(z) for z in Z]); it += 1
        if it % 10 == 0 or es.stop():
            xb = lo + np.clip(es.result.xbest, 0, 1) * span
            P, pose, ax, y0 = unpack(xb)
            json.dump(dict(P=P, pose=pose, ax=ax, y0=y0, f=es.result.fbest), open(out, 'w'), default=float)
            print('it', it, 'best %.4f' % es.result.fbest, '%.0fs' % (time.time() - t0), flush=True)
    print('done %.4f' % es.result.fbest, flush=True)
