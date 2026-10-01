"""refine the Titan's walk as a smooth symmetric gait (gait.py) on TS's silhouettes over all 15 walk steps.

    python3 fitgait.py legs.json out.json [iters]
"""
import json, sys, time
import numpy as np
import cma
import fitlegs2 as F2
import gait as G


def main(src, dst, iters=60):
    js = json.load(open(src))
    S = js['S']; S['hip_c'] = tuple(S['hip_c']); S['hip_r'] = tuple(S['hip_r'])
    poses = {int(k): v for k, v in js['poses'].items()}
    g0 = G.fit_from_poses(poses)
    losses = {s: F2.StepLoss(s, ss=2, w_cls=0.4) for s in range(15)}

    def total(g):
        return sum(losses[s](S, g.pose(2 * np.pi * s / 15)) for s in range(15)) / 15

    per = sum(losses[s](S, poses[s]) for s in range(15)) / 15
    print('per-step poses %.4f   gait from them %.4f' % (per, total(g0)), flush=True)
    x0 = g0.vector()
    n_ang = 3 * (1 + 2 * G.NH)
    scale = np.concatenate([np.full(n_ang, 6.0), np.full(len(x0) - n_ang, 0.4)])

    def f(z):
        return total(G.Gait.from_vector(x0 + scale * z))

    es = cma.CMAEvolutionStrategy(np.zeros_like(x0), 0.5, {'popsize': 14, 'maxiter': iters, 'seed': 31, 'verbose': -9})
    t0 = time.time(); it = 0
    while not es.stop():
        Z = es.ask(); es.tell(Z, [f(z) for z in Z]); it += 1
        if it % 5 == 0:
            g = G.Gait.from_vector(x0 + scale * es.result.xbest)
            print('it', it, 'best %.4f' % es.result.fbest, '%.0fs' % (time.time() - t0), flush=True)
            json.dump(dict(S=S, gait=g.to_json(), poses={str(s): g.pose(2 * np.pi * s / 15) for s in range(15)}),
                      open(dst, 'w'), default=float)
    g = G.Gait.from_vector(x0 + scale * es.result.xbest)
    json.dump(dict(S=S, gait=g.to_json(), poses={str(s): g.pose(2 * np.pi * s / 15) for s in range(15)}),
              open(dst, 'w'), default=float)
    print('done %.4f' % es.result.fbest, flush=True)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 60)
