"""fit the Wolverine's walk symmetrically: TS's walk has the right leg half a stride (6 steps) behind the left, so
steps s and s + 6 share the same two leg poses with the legs swapped.  For each pair the two leg poses (and each
step's bob) are fitted to both steps' frames together.

    python3 wfitsym.py walk.json out.json pairs(e.g. 0,1,2)
"""
import json, sys, time
import numpy as np
import cma
import wolf as WF
from wfitwalk import StepLoss

LEG = [(-50, 55), (-85, 40), (-35, 35)]
BOB = (-1.5, 1.5)

if __name__ == '__main__':
    js = json.load(open(sys.argv[1])); out = sys.argv[2]
    pairs = [int(a) for a in sys.argv[3].split(',')]
    P = dict(WF.P0); P.update(js['P']); ax, y0 = js['ax'], js['y0']
    walk = {int(k): v for k, v in js['walk'].items()}
    res = {}
    lo = np.array([b[0] for b in LEG] * 2 + [BOB[0]] * 2); hi = np.array([b[1] for b in LEG] * 2 + [BOB[1]] * 2)
    span = hi - lo
    for s in pairs:
        t = s + 6
        La, Lb = StepLoss(s), StepLoss(t)

        def f(z):
            x = lo + np.clip(z, 0, 1) * span
            a, b = list(x[0:3]), list(x[3:6])
            return (La(P, a + b + [x[6], 0, 0], ax, y0) + Lb(P, b + a + [x[7], 0, 0], ax, y0)) / 2

        cands = [walk[s][0:3] + walk[s][3:6] + [walk[s][6], walk[t][6]],          # from step s's own fit
                 walk[t][3:6] + walk[t][0:3] + [walk[s][6], walk[t][6]]]          # from step s+6's fit
        best = None
        for c in cands:
            z0 = np.clip((np.array(c, float) - lo) / span, 0.01, 0.99)
            es = cma.CMAEvolutionStrategy(z0, 0.08, {'bounds': [0, 1], 'popsize': 12, 'maxiter': 45, 'seed': 5,
                                                      'verbose': -9})
            while not es.stop():
                Z = es.ask(); es.tell(Z, [f(z) for z in Z])
            if best is None or es.result.fbest < best[1]:
                best = (lo + np.clip(es.result.xbest, 0, 1) * span, es.result.fbest)
        x = best[0]
        res[s] = list(x[0:3]) + list(x[3:6]) + [float(x[6]), 0.0, 0.0]
        res[t] = list(x[3:6]) + list(x[0:3]) + [float(x[7]), 0.0, 0.0]
        print('pair', s, t, 'loss %.4f' % best[1], np.round(x, 1).tolist(), flush=True)
        o = dict(js); o['walk'] = {str(k): v for k, v in res.items()}
        json.dump(o, open(out, 'w'), default=float)
