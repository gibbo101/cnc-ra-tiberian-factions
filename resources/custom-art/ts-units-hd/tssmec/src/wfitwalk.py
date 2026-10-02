"""fit the Wolverine's walk: each of TS's 12 walk steps (frames facing x 12 + step, 8 facings) gets its own leg
pose with the shape fixed; then the legs' shared dimensions over all steps with the poses fixed (alternating).

    python3 wfitwalk.py shape.json out.json rounds [steps]
"""
import json, os, sys, time
import numpy as np
import cma
import wolf as WF
import wfit as WFT

POSE_SPEC = [(-50, 55), (-85, 40), (-35, 35), (-50, 55), (-85, 40), (-35, 35), (-1.5, 1.5), (-6, 6), (-6, 6)]
LEG_SPEC = [('jv', 2.5, 6), ('jw', 8, 14), ('ju', -2, 2), ('Lt', 2.6, 7.5), ('tw', 2, 5.0), ('td', 2.5, 6.0),
            ('Ls', 2.6, 7.5), ('sw', 1.8, 4.5), ('sd', 2.0, 5.5), ('lf', 3.5, 8.5), ('lh', 1, 5), ('fw', 3.5, 8),
            ('fh', 1.2, 3.4)]


class StepLoss:
    def __init__(self, step, w_cls=0.4):
        # step 0-11: TS's walk frames; 'stand': TS's standing frames (96-103), the stance the firing frames use
        frames = list(range(96, 104)) if step == 'stand' else [k * 12 + step for k in range(8)]
        self.V = WFT.Views(frames)
        self.w_cls = w_cls

    def __call__(self, P, pose, ax, y0):
        parts = WF.body_parts(P, pose)
        l = self.V.loss(parts, ax, y0, w_cls=self.w_cls)
        lows = WF.soles(P, pose)
        pen = (min(lows)) ** 2 + 2.0 * sum(max(0.0, -lo) ** 2 for lo in lows)
        return l + 0.02 * pen


def fit_pose(Lf, P, init, ax, y0, iters=50, popsize=12, sigma=0.12, seed=3):
    lo = np.array([p[0] for p in POSE_SPEC], float); hi = np.array([p[1] for p in POSE_SPEC], float)
    span = hi - lo
    init = list(init) + [0.0] * (len(POSE_SPEC) - len(init))
    z0 = np.clip((np.array(init, float) - lo) / span, 0.01, 0.99)
    f = lambda z: Lf(P, lo + np.clip(z, 0, 1) * span, ax, y0)
    es = cma.CMAEvolutionStrategy(z0, sigma, {'bounds': [0, 1], 'popsize': popsize, 'maxiter': iters, 'seed': seed,
                                               'verbose': -9})
    while not es.stop():
        Z = es.ask(); es.tell(Z, [f(z) for z in Z])
    return (lo + np.clip(es.result.xbest, 0, 1) * span).tolist(), es.result.fbest


def fit_legs(losses, P, poses, ax, y0, steps, iters=30, popsize=14, sigma=0.06, seed=21):
    lo = np.array([p[1] for p in LEG_SPEC], float); hi = np.array([p[2] for p in LEG_SPEC], float); span = hi - lo
    x0 = np.clip(np.array([P[k] for k, *_ in LEG_SPEC], float), lo + 1e-3, hi - 1e-3)

    def unpack(x):
        P2 = dict(P)
        for (k, *_), v in zip(LEG_SPEC, x):
            P2[k] = float(v)
        return P2

    f = lambda z: sum(losses[s](unpack(lo + np.clip(z, 0, 1) * span), poses[s], ax, y0) for s in steps) / len(steps)
    es = cma.CMAEvolutionStrategy((x0 - lo) / span, sigma, {'bounds': [0, 1], 'popsize': popsize, 'maxiter': iters,
                                                            'seed': seed, 'verbose': -9})
    while not es.stop():
        Z = es.ask(); es.tell(Z, [f(z) for z in Z])
    return unpack(lo + np.clip(es.result.xbest, 0, 1) * span), es.result.fbest


if __name__ == '__main__':
    js = json.load(open(sys.argv[1])); out = sys.argv[2]; rounds = int(sys.argv[3])
    steps = [int(a) for a in sys.argv[4].split(',')] if len(sys.argv) > 4 else list(range(12))
    P = dict(WF.P0); P.update(js['P']); ax, y0 = js['ax'], js['y0']
    stand = js['pose']
    poses = {int(k): v for k, v in js.get('walk', {}).items()}
    if len(sys.argv) > 5:                                 # poses from another fit as the start
        poses.update({int(k): v for k, v in json.load(open(sys.argv[5]))['walk'].items()})
    poses['stand'] = list(stand)
    if not os.environ.get('NOSTAND'):
        steps = steps + ['stand']
    losses = {s: StepLoss(s) for s in steps}
    if os.environ.get('LEGSFIRST'):
        t0 = time.time()
        P, fb = fit_legs(losses, P, poses, ax, y0, steps, iters=int(os.environ.get('LEGITERS', 30)), seed=17)
        print('legs first %.4f' % fb, {k: round(P[k], 2) for k, *_ in LEG_SPEC}, '%.0fs' % (time.time() - t0), flush=True)
        json.dump(dict(P=P, ax=ax, y0=y0, pose=poses['stand'],
                       walk={str(k): v for k, v in poses.items() if k != 'stand'}), open(out, 'w'), default=float)
    for rd in range(rounds):
        t0 = time.time(); tot = 0
        for s in steps:
            init = poses.get(s, poses.get(s - 1, stand)) if s != 'stand' else poses['stand']
            # try the step's own start and the mirrored pose half a stride away, keep the better
            cands = [init]
            m = poses.get((s + 6) % 12) if s != 'stand' else None
            if m is not None:
                m = list(m) + [0.0] * (9 - len(m))
                cands.append(m[3:6] + m[0:3] + [m[6], -m[7], m[8]])
            best = None
            for c in cands:
                p, fb = fit_pose(losses[s], P, c, ax, y0, seed=3 + rd)
                if best is None or fb < best[1]:
                    best = (p, fb)
            poses[s] = best[0]; tot += best[1]
            print('round', rd, 'step', s, 'loss %.4f' % best[1], np.round(best[0], 1).tolist(), flush=True)
            stand = poses['stand']
            json.dump(dict(P=P, ax=ax, y0=y0, pose=stand, walk={str(k): v for k, v in poses.items() if k != 'stand'}),
                      open(out, 'w'), default=float)
        print('round', rd, 'poses mean %.4f' % (tot / len(steps)), '%.0fs' % (time.time() - t0), flush=True)
        if os.environ.get('NOLEGS'):
            continue
        if rd < rounds - 1 or rounds == 1:
            t0 = time.time()
            P, fb = fit_legs(losses, P, poses, ax, y0, steps, seed=21 + rd)
            print('round', rd, 'legs %.4f' % fb, {k: round(P[k], 2) for k, *_ in LEG_SPEC}, '%.0fs' % (time.time() - t0),
                  flush=True)
            json.dump(dict(P=P, ax=ax, y0=y0, pose=poses['stand'],
                           walk={str(k): v for k, v in poses.items() if k != 'stand'}), open(out, 'w'), default=float)
