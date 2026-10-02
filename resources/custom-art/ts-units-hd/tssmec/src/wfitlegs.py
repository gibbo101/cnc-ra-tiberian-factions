"""refit the Wolverine's leg dimensions over all walk steps and the stance with their poses fixed (two worker
processes evaluate the candidates).

    python3 wfitlegs.py walk.json out.json [iters]
"""
import json, sys, time
from multiprocessing import Pool
import numpy as np
import cma
import wolf as WF
from wfitwalk import StepLoss, LEG_SPEC

_W = {}
STEPS = list(range(12)) + ['stand']


def _init(src):
    js = json.load(open(src))
    P = dict(WF.P0); P.update(js['P'])
    poses = {int(k): v for k, v in js['walk'].items()}
    poses['stand'] = js['pose']
    _W.update(P=P, ax=js['ax'], y0=js['y0'], poses=poses, losses={s: StepLoss(s) for s in STEPS})


def _loss(x):
    P = dict(_W['P'])
    for (k, *_), v in zip(LEG_SPEC, x):
        P[k] = float(v)
    return sum(_W['losses'][s](P, _W['poses'][s], _W['ax'], _W['y0']) for s in STEPS) / len(STEPS)


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    iters = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    js = json.load(open(src))
    P = dict(WF.P0); P.update(js['P'])
    lo = np.array([p[1] for p in LEG_SPEC], float); hi = np.array([p[2] for p in LEG_SPEC], float); span = hi - lo
    x0 = np.clip(np.array([P[k] for k, *_ in LEG_SPEC], float), lo + 1e-3, hi - 1e-3)
    pool = Pool(2, initializer=_init, initargs=(src,))
    print('start %.4f' % pool.map(_loss, [x0])[0], flush=True)
    es = cma.CMAEvolutionStrategy((x0 - lo) / span, 0.08, {'bounds': [0, 1], 'popsize': 14, 'maxiter': iters,
                                                           'seed': 23, 'verbose': -9})
    t0 = time.time(); it = 0
    while not es.stop():
        Z = es.ask()
        es.tell(Z, pool.map(_loss, [lo + np.clip(z, 0, 1) * span for z in Z])); it += 1
        if it % 5 == 0 or es.stop():
            xb = lo + np.clip(es.result.xbest, 0, 1) * span
            for (k, *_), v in zip(LEG_SPEC, xb):
                P[k] = float(v)
            out = dict(js); out['P'] = P
            json.dump(out, open(dst, 'w'), default=float)
            print('it', it, 'best %.4f' % es.result.fbest, {k: round(P[k], 2) for k, *_ in LEG_SPEC},
                  '%.0fs' % (time.time() - t0), flush=True)
    print('done %.4f' % es.result.fbest, flush=True)
