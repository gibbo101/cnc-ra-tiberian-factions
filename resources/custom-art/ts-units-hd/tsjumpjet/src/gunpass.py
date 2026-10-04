"""
gunpass.py - the Ghost's railgun laid where TS draws it, frame by frame, his body as fitted: TS swings the railgun about
from facing to facing and step to step (running south it is up across his chest, then down at his side, then across
again), and a gun shared by the facings, or held the same through a stride, can't follow it (Luke: the run south "gun
still clipping into stomach").  Each frame's gun and hands are fitted to TS's frame: silhouette and colours, the gun
along TS's gun (gunline.py), started from where TS's gun lies.

    python3 gunpass.py UNIT SEQ iters [FACINGS]     (rewrites UNIT_SEQ_frames.json; the old kept as _pre_gun)
"""
import json, os, sys, time
import numpy as np
import inf as I
import inffit as F
import infseq as SQ

KEYS = ('gy', 'gp', 'gr', 'rgx', 'rgy', 'rgz', 'lfx', 'lsw', 'rsw')


def main():
    unit, seq, iters = sys.argv[1], sys.argv[2], int(sys.argv[3])
    facings = [int(v) for v in sys.argv[4].split(',')] if len(sys.argv) > 4 else list(range(8))
    import infunit; infunit.use(unit)
    import infsmooth as SM
    import gunline as G
    from infstatic import ABS
    js = json.load(open('%s_shape.json' % unit))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    ax, y0 = js['ax'], js['y0']
    path = '%s_%s_frames.json' % (unit, seq)
    bak = '%s_%s_frames_pre_gun.json' % (unit, seq)
    if not os.path.exists(bak):
        json.dump(json.load(open(path)), open(bak, 'w'), default=float)
    old = json.load(open(bak))
    state = '%s_%s_frames_gun.json' % (unit, seq)
    res = json.load(open(state)) if os.path.exists(state) else {}
    first, n, fc = SQ.SEQ[unit][seq]
    todo = []
    for a, b in SQ.frames_of(unit, seq):
        if isinstance(b, list):                    # (8 facings: a = step, b = its frames by facing)
            todo += [(k, f) for f, k in enumerate(b) if f in facings]
        else:                                      # (one facing: a = frame)
            todo.append((a, int(old[str(a)]['facing'])))
    for k, f in sorted(todo):
        if True:
            if str(k) in res or str(k) not in old:
                continue
            t0 = time.time()
            Q0 = dict(js['Q'], **old[str(k)]['Q'])
            if Q0.get('ik', 1.0) < 0.5 and Q0.get('gone', 0.0) < 0.5:
                res[str(k)] = old[str(k)]; continue
            tgt = F.Target(unit, k, f)
            gt = G.GunTarget(unit, k)
            # (the gun in both hands: its aim and grip; in his right hand alone - the deaths, once he lets go with
            # his left - its aim and his right arm)
            keys = list(KEYS) if Q0.get('ik', 1.0) > 0.5 else ['gy', 'gp', 'gr', 'rsf', 'rsa', 'rst', 'ref']
            sc = SM.scale(keys)

            def loss(Q):
                parts, dz = I.grounded(S, Q, I.facing_angle(f))
                return F.parts_loss(parts, tgt, ax, y0) + gt.pen(S, Q, f, ax, y0, dz)
            starts = [Q0] + (SM.line_starts(unit, S, ax, y0, k, f, Q0, n=4) if gt.line is not None else
                             [dict(Q0, gy=gy, gp=gp) for gy, gp in SM.RIFLE_STARTS])
            starts.sort(key=loss)
            best = None
            for st in starts[:2]:
                lo = np.array([max(ABS[q][0], st[q] - SM.WIN.get(q, 35.0)) for q in keys])
                hi = np.array([min(ABS[q][1], st[q] + SM.WIN.get(q, 35.0)) for q in keys])
                x0 = np.clip(np.array([st[q] for q in keys]), lo, hi)
                bx = {}

                def unpack(x):
                    Q = dict(st); Q.update({q: float(v) for q, v in zip(keys, x)})
                    return Q

                def cb(x, fb, it, dt):
                    bx['x'] = x; bx['f'] = fb
                F.cma_fit(lambda x: loss(unpack(x)), lo, hi, x0, iters, cb, sigma=0.12, pop=12, seed=1)
                Q = unpack(bx['x'])
                if best is None or bx['f'] < best[1]:
                    best = (Q, bx['f'])
            Q, fb = best
            dz = I.grounded(S, Q, I.facing_angle(f))[1]
            res[str(k)] = dict(old[str(k)], Q=Q, f=fb, iou=F.iou(S, Q, tgt, ax, y0))
            json.dump(res, open(state, 'w'), default=float)
            dz0 = I.grounded(S, Q0, I.facing_angle(f))[1]
            print(seq, 'frame', k, 'facing', f, 'loss %.3f -> %.3f' % (loss(Q0), fb), 'gun %.2f -> %.2f' % (
                gt.pen(S, Q0, f, ax, y0, dz0), gt.pen(S, Q, f, ax, y0, dz)), 'iou %.3f' % res[str(k)]['iou'],
                '%.0fs' % (time.time() - t0), flush=True)
    if all(str(k) in res for k, f in todo if str(k) in old):
        out = dict(old); out.update(res)
        json.dump(out, open(path, 'w'), default=float)
        print('written', path, flush=True)
    print('done', flush=True)


if __name__ == '__main__':
    main()
