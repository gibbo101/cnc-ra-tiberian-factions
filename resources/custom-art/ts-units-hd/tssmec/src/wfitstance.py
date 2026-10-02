"""refit the firing stance with both feet planted (TS's standing frames 96-103)."""
import json, sys
import numpy as np
import cma
import wolf as WF
from wfitwalk import StepLoss

js = json.load(open(sys.argv[1])); out = sys.argv[2]
P = dict(WF.P0); P.update(js['P']); ax, y0 = js['ax'], js['y0']
L = StepLoss('stand')
lo = np.array([-50, -85, -35, -50, -85, -35, -1.5]); hi = np.array([55, 40, 35, 55, 40, 35, 1.5]); span = hi - lo


def f(z):
    x = lo + np.clip(z, 0, 1) * span
    pose = list(x) + [0.0, 0.0]
    s = WF.soles(P, pose)
    return L(P, pose, ax, y0) + 0.5 * sum(v * v for v in s)          # both feet on the ground


x0 = np.array(list(js['pose'][:7]), float)
es = cma.CMAEvolutionStrategy(np.clip((x0 - lo) / span, 0.01, 0.99), 0.05, {'bounds': [0, 1], 'popsize': 12,
                                                                             'maxiter': 60, 'seed': 9, 'verbose': -9})
while not es.stop():
    Z = es.ask(); es.tell(Z, [f(z) for z in Z])
x = lo + np.clip(es.result.xbest, 0, 1) * span
pose = list(map(float, x)) + [0.0, 0.0]
print('stance', np.round(pose, 1).tolist(), 'loss %.4f' % L(P, pose, ax, y0), 'soles', np.round(WF.soles(P, pose), 2))
js['pose'] = pose
json.dump(js, open(out, 'w'), default=float)
