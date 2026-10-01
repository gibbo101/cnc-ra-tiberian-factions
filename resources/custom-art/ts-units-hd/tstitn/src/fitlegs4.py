"""alternating fit of the Titan's legs over all 15 walk steps: (a) each step's pose with the shape fixed,
(b) the shared shape with the poses fixed.  Silhouettes mostly (the colour classes weigh little).

    python3 fitlegs4.py rounds start.json [steps]
"""
import json, sys, time
import numpy as np
import cma
import fitlegs2 as F2

F2.POSE_SPEC = [(-95, 15), (-5, 85), (-30, 30), (-95, 15), (-5, 85), (-30, 30), (-1.5, 1.5)]
F2.SHAPE_SPEC = [('hip_cu', -2, 3), ('hip_cw', 15, 24), ('hip_ra', 4, 9), ('hip_rb', 5, 9.5), ('hip_rc', 5, 14),
                 ('hip_bot', 13, 21), ('jv', 3.0, 8.0), ('jw', 13, 21), ('ju', -3, 3), ('splay', -10, 15),
                 ('Lt', 6.0, 15), ('tw', 3.0, 8.0), ('td', 3.0, 8.0), ('Ls', 8, 20), ('sw', 2.5, 7.0), ('sd', 2.5, 7.0),
                 ('lf', 5, 14), ('lh', 0, 6), ('fw', 3, 8), ('fh', 1.5, 5), ('ks', 1.5, 10), ('ka', -30, 45),
                 ('kw', 1.5, 6), ('kd', 1, 5), ('g', 0.5, 5)]


def fit_shape_all(S, poses, steps, iters=25, popsize=12, sigma=0.06, seed=21):
    losses = {s: F2.StepLoss(s, ss=2, w_cls=0.4) for s in steps}
    lo = np.array([p[1] for p in F2.SHAPE_SPEC], float); hi = np.array([p[2] for p in F2.SHAPE_SPEC], float)
    x0 = np.clip(np.array([F2.S_get(S, k) for k, *_ in F2.SHAPE_SPEC], float), lo + 1e-3, hi - 1e-3)
    span = hi - lo

    def unpack(x):
        S2 = dict(S)
        for (k, *_), v in zip(F2.SHAPE_SPEC, x):
            F2.S_set(S2, k, float(v))
        return S2

    f = lambda z: sum(losses[s](unpack(lo + np.clip(z, 0, 1) * span), poses[s]) for s in steps) / len(steps)
    es = cma.CMAEvolutionStrategy((x0 - lo) / span, sigma, {'bounds': [0, 1], 'popsize': popsize, 'maxiter': iters,
                                                              'seed': seed, 'verbose': -9})
    while not es.stop():
        Z = es.ask(); es.tell(Z, [f(z) for z in Z])
    return unpack(lo + np.clip(es.result.xbest, 0, 1) * span), es.result.fbest


def fit_pose(step, S, init, iters=35, popsize=10, sigma=0.1, seed=3):
    Lf = F2.StepLoss(step, ss=2, w_cls=0.4)
    lo = np.array([p[0] for p in F2.POSE_SPEC], float); hi = np.array([p[1] for p in F2.POSE_SPEC], float)
    span = hi - lo
    z0 = np.clip((np.array(init, float) - lo) / span, 0.01, 0.99)
    f = lambda z: Lf(S, lo + np.clip(z, 0, 1) * span)
    es = cma.CMAEvolutionStrategy(z0, sigma, {'bounds': [0, 1], 'popsize': popsize, 'maxiter': iters, 'seed': seed,
                                               'verbose': -9})
    while not es.stop():
        Z = es.ask(); es.tell(Z, [f(z) for z in Z])
    return (lo + np.clip(es.result.xbest, 0, 1) * span).tolist(), es.result.fbest


if __name__ == '__main__':
    rounds = int(sys.argv[1]); start = json.load(open(sys.argv[2]))
    steps = [int(a) for a in sys.argv[3].split(',')] if len(sys.argv) > 3 else list(range(15))
    tag = sys.argv[4] if len(sys.argv) > 4 else 'a'
    S = start['S']; S['hip_c'] = tuple(S['hip_c']); S['hip_r'] = tuple(S['hip_r'])
    poses = {int(k): v for k, v in start['poses'].items()}
    base = F2.init_poses()
    for s in steps:
        poses.setdefault(s, base[s])
    for rd in range(rounds):
        t0 = time.time(); tot = 0
        for s in steps:
            p, fb = fit_pose(s, S, poses[s], seed=3 + rd)
            poses[s] = p; tot += fb
            print('round', rd, 'step', s, 'loss %.4f' % fb, np.round(p, 1).tolist(), flush=True)
        print('round', rd, 'poses mean %.4f' % (tot / len(steps)), '%.0fs' % (time.time() - t0), flush=True)
        json.dump(dict(S=S, poses={str(k): v for k, v in poses.items()}), open('legs4_%s.json' % tag, 'w'), default=float)
        t0 = time.time()
        S, fb = fit_shape_all(S, poses, steps, seed=21 + rd)
        print('round', rd, 'shape %.4f' % fb, {k: round(float(F2.S_get(S, k)), 2) for k, *_ in F2.SHAPE_SPEC},
              '%.0fs' % (time.time() - t0), flush=True)
        json.dump(dict(S=S, poses={str(k): v for k, v in poses.items()}), open('legs4_%s.json' % tag, 'w'), default=float)
