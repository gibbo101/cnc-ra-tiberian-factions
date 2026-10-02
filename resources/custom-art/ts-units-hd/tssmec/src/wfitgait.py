"""refine the Wolverine's walk as one smooth symmetric gait (gait.py: each leg angle a Fourier series in the
walk phase, the right leg half a stride behind the left, the body bobbing twice a stride) on TS's silhouettes over
all 12 walk steps.

    python3 wfitgait.py walk.json out.json [iters]
"""
import json, sys, time
import numpy as np
import cma
import wolf as WF
import gait as G
from wfitwalk import StepLoss


_W = {}


def _init(src):
    js = json.load(open(src))
    P = dict(WF.P0); P.update(js['P'])
    _W.update(P=P, ax=js['ax'], y0=js['y0'], losses={s: StepLoss(s) for s in range(12)})


def _total_vec(args):
    x, sway = args
    g = G.Gait.from_vector(x, sway=sway)
    P, ax, y0, losses = _W['P'], _W['ax'], _W['y0'], _W['losses']
    return sum(losses[s](P, g.pose(2 * np.pi * s / 12), ax, y0) for s in range(12)) / 12


def main(src, dst, iters=60, workers=2):
    from multiprocessing import Pool
    js = json.load(open(src))
    P = dict(WF.P0); P.update(js['P']); ax, y0 = js['ax'], js['y0']
    poses = {int(k): v for k, v in js['walk'].items()}
    g0 = G.fit_from_poses(poses, nsteps=12)
    _init(src)
    losses = _W['losses']
    pool = Pool(workers, initializer=_init, initargs=(src,))

    def total(g):
        return sum(losses[s](P, g.pose(2 * np.pi * s / 12), ax, y0) for s in range(12)) / 12

    per = sum(losses[s](P, poses[s], ax, y0) for s in range(12)) / 12
    print('per-step poses %.4f   gait from them %.4f' % (per, total(g0)), flush=True)
    x0 = g0.vector()
    n_ang = 3 * (1 + 2 * G.NH)
    sway = g0.roll is not None
    nb = 1 + 2 * G.NB
    scale = np.concatenate([np.full(n_ang, 6.0), np.full(nb, 0.4)] + ([np.full(4, 1.5), np.full(nb, 1.5)] if sway else []))
    assert len(scale) == len(x0)

    def f(z):
        return total(G.Gait.from_vector(x0 + scale * z, sway=sway))

    def dump(g):
        out = dict(js); out['gait'] = g.to_json()
        out['walk_gait'] = {str(s): g.pose(2 * np.pi * s / 12) for s in range(12)}
        json.dump(out, open(dst, 'w'), default=float)

    dump(g0)
    import os
    es = cma.CMAEvolutionStrategy(np.zeros_like(x0), float(os.environ.get('SIGMA', 0.5)), {'popsize': 14, 'maxiter': iters, 'seed': 31, 'verbose': -9})
    t0 = time.time(); it = 0
    while not es.stop():
        Z = es.ask()
        es.tell(Z, pool.map(_total_vec, [(x0 + scale * z, sway) for z in Z])); it += 1
        if it % 5 == 0:
            dump(G.Gait.from_vector(x0 + scale * es.result.xbest, sway=sway))
            print('it', it, 'best %.4f' % es.result.fbest, '%.0fs' % (time.time() - t0), flush=True)
    dump(G.Gait.from_vector(x0 + scale * es.result.xbest, sway=sway))
    print('done %.4f' % es.result.fbest, flush=True)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 60)
