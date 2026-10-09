"""
e2_subfit.py - refit a few of a shape's sizes (the rest held) on the 8 standing frames: used for E2's pouch and the
pack above it, which a full fit gives up for a pixel of silhouette elsewhere.

    python3 e2_subfit.py UNIT start.json out.json iters KEY,KEY,... [poses.json]
        KEYs of inffit.SSPEC / TSPEC; poses.json: each facing's own standing pose (else the shared one)
        env CW=3:3.0,7:3.0  colour classes counted more;  BOUNDS=fva:18:75,...  wider ranges
"""
import json, os, sys
import numpy as np


def main():
    unit, start, out, iters, keys = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5].split(',')
    import infunit; infunit.use(unit)
    import inffit as F
    import inf as I
    js = json.load(open(start))
    S0 = dict(F.S0); S0.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    spec = {k: (a, b, 'S') for k, a, b in F.SSPEC}
    spec.update({k: (a, b, 'T') for k, a, b in F.TSPEC})
    for b in filter(None, os.environ.get('BOUNDS', '').split(',')):
        k, a, z = b.split(':')
        spec[k] = (float(a), float(z), spec[k][2])
    for b in filter(None, os.environ.get('CW', '').split(',')):
        c, w = b.split(':')
        F.CW[int(c)] = float(w)
    lo = np.array([spec[k][0] for k in keys]); hi = np.array([spec[k][1] for k in keys])
    x0 = np.array([S0[k] if spec[k][2] == 'S' else S0[k][0] / F.S0[k][0] for k in keys])
    x0 = np.clip(x0, lo, hi)
    tg = [F.Target(unit, f, f) for f in range(8)]
    Q, ax, y0 = js['Q'], js['ax'], js['y0']
    PQ = json.load(open(sys.argv[6])) if len(sys.argv) > 6 else {}
    Qf = [dict(Q, **PQ[str(f)]['Q']) if str(f) in PQ else dict(Q) for f in range(8)]

    def shape(x):
        S = dict(S0)
        for k, v in zip(keys, x):
            S[k] = float(v) if spec[k][2] == 'S' else tuple(float(v) * b for b in F.S0[k])
        return S

    def f(x):
        S = shape(x)
        return float(np.mean([F.frame_loss(S, Qf[i], t, ax, y0) for i, t in enumerate(tg)]))
    print('start %.4f' % f(x0), dict(zip(keys, np.round(x0, 3))), flush=True)

    def cb(x, fb, it, dt):
        S = shape(x)
        ious = [F.iou(S, Qf[i], t, ax, y0) for i, t in enumerate(tg)]
        json.dump(dict(js, S=S, f=float(fb), iou=ious), open(out, 'w'), default=float)
        print('it', it, 'best %.4f' % fb, 'iou %.3f' % np.mean(ious), dict(zip(keys, np.round(x, 3))), '%.0fs' % dt,
              flush=True)
    F.cma_fit(f, lo, hi, x0, iters, cb, sigma=0.2, pop=12, seed=1)
    print('done', flush=True)


if __name__ == '__main__':
    main()
