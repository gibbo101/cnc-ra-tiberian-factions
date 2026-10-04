"""
deathback.py - a death fitted backwards as well: TS's soldier can fall faster than a fit started from the frame before
can follow (it stays half up while TS's lies flat), so each frame is also fitted starting from the frame after it (from
the last, lying on the ground, back to the first), and keeps whichever start matches TS's frame better; the frames that
changed are then relaxed again (infsmooth.py's sweeps).

    python3 deathback.py UNIT SEQ FACING iters
"""
import json, os, sys, time
import numpy as np
import inf as I
import inffit as F
import infseq as SQ


def main():
    unit, seq, facing, iters = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    import infunit; infunit.use(unit)
    import infsmooth as SM
    js = json.load(open('%s_shape.json' % unit))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    ax, y0 = js['ax'], js['y0']
    stand = dict(js['Q'])
    frames = [k for k, f in SQ.frames_of(unit, seq)]
    out = '%s_%s_frames.json' % (unit, seq)
    res = json.load(open(out))
    cpath = '%s_%s_case.json' % (unit, seq)
    case = json.load(open(cpath)) if os.path.exists(cpath) else None

    def with_case(Q, k):
        if case is None:
            return Q
        return dict(Q, cfx=case['cfx'], cfy=case['cfy'], cfa=case['cfa'], cft=case.get('cft', 0.0),
                    cfix=float(case['cfix'].get(str(k), 0.0)))

    def img(Q, k):
        return F.frame_loss(S, with_case(Q, k), F.Target(unit, k, facing), ax, y0)
    nxt = dict(stand, **res[str(frames[-1])]['Q'])
    changed = []
    for i in range(len(frames) - 2, 0, -1):
        k = frames[i]
        t0 = time.time()
        cur = dict(stand, **res[str(k)]['Q'])
        Q, fb, iu = SM.fit_best(unit, S, ax, y0, k, facing, with_case(nxt, k), [(SM.W_PREV, with_case(nxt, k))],
                                iters, falls=True)
        a, b = img(cur, k), img(Q, k)
        if b < a - 0.005:
            res[str(k)] = dict(Q=Q, f=fb, iou=iu, facing=facing, sweep=0)
            changed.append(k)
            nxt = Q
            print(seq, 'frame', k, 'backwards better: %.3f -> %.3f iou %.3f' % (a, b, iu), '%.0fs' % (time.time() - t0),
                  flush=True)
        else:
            nxt = cur
            print(seq, 'frame', k, 'kept (%.3f, backwards %.3f)' % (a, b), '%.0fs' % (time.time() - t0), flush=True)
    # the neighbours of what changed are relaxed again too
    for k in list(changed):
        i = frames.index(k)
        for j in (i - 1, i + 1):
            if 0 <= j < len(frames) and str(frames[j]) in res:
                res[str(frames[j])]['sweep'] = 0
    json.dump(res, open(out, 'w'), default=float)
    print('changed', changed, flush=True)


if __name__ == '__main__':
    main()
