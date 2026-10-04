"""
infrefine.py - each frame's own arms, rifle and head: TS's facings are not always one pose turned (its standing
soldier holds the rifle up in one facing and down in the next; its runner swings it across in some facings and
not others), so after a step's pose is fitted to its 8 facings together, each frame's upper body is fitted to that
frame alone, held close to the step's pose and to the same facing's step before (smooth motion).

    python3 infrefine.py UNIT shape.json SEQ [iters]
        SEQ 'stand' refines frames 0-7 from the shape's own pose; others read UNIT_SEQ.json
        writes UNIT_SEQ_frames.json: {frame: {Q, f, iou}}
"""
import json, os, sys, time
import numpy as np
import inf as I
import inffit as F
import infseq as SQ

KEYS = [('rgx', 1.5), ('rgy', 1.5), ('rgz', 1.5), ('lfx', 1.5), ('lsw', 40.0), ('rsw', 40.0), ('gp', 45.0),
        ('gy', 60.0), ('gr', 45.0), ('sy', 20.0), ('hy', 25.0), ('hp', 10.0)]
# free arms (no rifle): the arms' own joints
KEYS_FREE = [('lsf', 30.0), ('lsa', 25.0), ('lst', 30.0), ('lef', 40.0), ('rsf', 30.0), ('rsa', 25.0), ('rst', 30.0),
             ('ref', 40.0), ('sy', 20.0), ('hy', 25.0), ('hp', 10.0)]
SCALE = dict(rgx=1.0, rgy=1.0, rgz=1.0, lfx=1.0)


def refine(unit, S, ax, y0, k, facing, Q0, Qprev, iters, w_pull=0.003, w_prev=0.002):
    tgt = F.Target(unit, k, facing)
    keys = [(key, w) for key, w in (KEYS if Q0.get('ik', 1.0) > 0.5 else KEYS_FREE) if key in Q0]
    # (HP_DEV: how far a frame's head pitch may leave the step's - the Medic's, whose faceplate sits where he looks)
    if os.environ.get('HP_DEV'):
        keys = [(key, float(os.environ['HP_DEV']) if key == 'hp' else w) for key, w in keys]
    lo = np.array([Q0[key] - w for key, w in keys]); hi = np.array([Q0[key] + w for key, w in keys])
    x0 = np.array([Q0[key] for key, w in keys])
    sc = np.array([SCALE.get(key, 10.0) for key, w in keys])
    xp = np.array([Qprev[key] for key, w in keys]) if Qprev is not None else None

    def unpack(x):
        Q = dict(Q0)
        for (key, w), v in zip(keys, x):
            Q[key] = float(v)
        return Q

    def f(x):
        l = F.frame_loss(S, unpack(x), tgt, ax, y0) + w_pull * float((((x - x0) / sc) ** 2).sum())
        if xp is not None:
            l += w_prev * float((((x - xp) / sc) ** 2).sum())
        return l
    best = {}

    def cb(x, fb, it, dt):
        best['x'] = x; best['f'] = fb
    F.cma_fit(f, lo, hi, x0, iters, cb, sigma=0.15, pop=14, seed=1)
    Q = unpack(best['x'])
    return Q, best['f'], F.iou(S, Q, tgt, ax, y0)


if __name__ == '__main__':
    unit, shape, name = sys.argv[1], sys.argv[2], sys.argv[3]
    import infunit; infunit.use(unit)
    iters = int(sys.argv[4]) if len(sys.argv) > 4 else 120
    js = json.load(open(shape))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    ax, y0 = js['ax'], js['y0']
    out = '%s_%s_frames.json' % (unit, name)
    res = json.load(open(out)) if os.path.exists(out) else {}
    only = [int(v) for v in os.environ['FACINGS'].split(',')] if os.environ.get('FACINGS') else list(range(8))
    if name == 'stand':
        jobs = [[(f, f, dict(js['Q']))] for f in only]
    else:
        steps = json.load(open('%s_%s.json' % (unit, name)))
        jobs = []
        for f in only:
            jobs.append([(v['frames'][f], f, dict(v['Q'])) for s, v in sorted(steps.items(), key=lambda kv: int(kv[0]))])
    for job in jobs:
        prev = None
        for k, f, Q0 in job:
            if str(k) in res:
                prev = res[str(k)]['Q']; continue
            t0 = time.time()
            Q, fb, iu = refine(unit, S, ax, y0, k, f, Q0, prev, iters)
            res = json.load(open(out)) if os.path.exists(out) else {}
            res[str(k)] = dict(Q=Q, f=fb, iou=iu, facing=f)
            json.dump(res, open(out, 'w'), default=float)
            prev = Q
            print(name, 'frame', k, 'facing', f, 'f %.3f iou %.3f' % (fb, iu), '%.0fs' % (time.time() - t0), flush=True)
    print('done', flush=True)
