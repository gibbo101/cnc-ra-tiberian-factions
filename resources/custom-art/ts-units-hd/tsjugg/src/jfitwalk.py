"""fit the Juggernaut's walk: the shape fixed (from a stand fit), each of the 15 steps' pose (the two legs' thigh,
shin and foot angles and the body's lift) fitted to TS's 8 facings at that step.

    python3 jfitwalk.py shape.json out.json [iters] [steps]
"""
import json, sys, time
import numpy as np
import cma
import jugg as JG
import jfit as JF

LO = np.array([-80, -80, -40, -80, -80, -40, -8], float)
HI = np.array([80, 80, 40, 80, 80, 40, 8], float)


def objective(V, P, pose, ax, y0, w_cls=0.5):
    parts = JG.body_parts(P, list(pose))
    l = V.loss(parts, ax, y0, w_cls=w_cls)
    lows = JG.soles(P, pose)
    pen = (min(lows)) ** 2 + 2.0 * sum(max(0.0, -lo) ** 2 for lo in lows)
    return l + 0.02 * pen


if __name__ == '__main__':
    js = json.load(open(sys.argv[1]))
    P = dict(JG.P0); P.update(js['P']); ax, y0 = js['ax'], js['y0']
    out = sys.argv[2]
    iters = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    steps = [int(s) for s in sys.argv[4].split(',')] if len(sys.argv) > 4 else list(range(15))
    res = {'P': P, 'ax': ax, 'y0': y0, 'poses': {}}
    try:
        res['poses'] = json.load(open(out))['poses']
    except Exception:
        pass
    prev = list(js['pose'])
    for s in steps:
        V = JF.Views([cw * 15 + s for cw in range(8)])
        x0 = np.array(res['poses'].get(str(s), prev), float)
        span = HI - LO
        f = lambda z: objective(V, P, LO + np.clip(z, 0, 1) * span, ax, y0)
        best = None
        # start from the previous step's pose and from its mirror (the legs swapped), keep the better
        for start in (x0, np.r_[x0[3:6], x0[0:3], x0[6]]):
            es = cma.CMAEvolutionStrategy((np.clip(start, LO + 1e-3, HI - 1e-3) - LO) / span, 0.08,
                                          {'bounds': [0, 1], 'popsize': 12, 'maxiter': iters, 'seed': 3 + s,
                                           'verbose': -9})
            while not es.stop():
                Z = es.ask(); es.tell(Z, [f(z) for z in Z])
            if best is None or es.result.fbest < best[0]:
                best = (es.result.fbest, LO + np.clip(es.result.xbest, 0, 1) * span)
        pose = [float(v) for v in best[1]]
        res['poses'][str(s)] = pose
        prev = pose
        iou = V.iou(JG.body_parts(P, pose), ax, y0)
        print('step', s, 'loss %.4f' % best[0], 'iou %.3f' % iou.mean(), np.round(pose, 1), flush=True)
        json.dump(res, open(out, 'w'), default=float)
    print('done', flush=True)
