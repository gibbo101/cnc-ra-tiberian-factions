"""
deathfix.py - frames of a fitted death refitted again, backwards from the frame after them (and from their own pose),
then relaxed with their neighbours: for the frames a check sheet shows still off (a leg up while TS's shadow has it
down).  Same loss as deathfit2.py (TS's outline and shadow; a raised part TS's shadow doesn't show counts most).

    SHADOW=0.5 python3 deathfix.py UNIT SEQ FIRST-LAST iters
"""
import json, os, sys, time
import numpy as np
import inf as I
import inffit as F
import infseq as SQ


def main():
    unit, seq, rng, iters = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    a, b = [int(v) for v in rng.split('-')]
    import infunit; infunit.use(unit)
    import infsmooth as SM
    from infstatic import ABS
    ABS['yaw'] = (-180.0, 180.0); ABS['roll'] = (-80.0, 80.0); ABS['dx'] = (-16.0, 16.0); ABS['dy'] = (-16.0, 16.0)
    SM.WIN['dx'] = SM.WIN['dy'] = 5.0
    if F.W_SHADOW <= 0:
        F.W_SHADOW = 0.5
    js = json.load(open('%s_shape.json' % unit))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    ax, y0 = js['ax'], js['y0']
    path = '%s_%s_frames.json' % (unit, seq)
    res = json.load(open(path))
    json.dump(res, open('%s_%s_frames_pre_fix.json' % (unit, seq), 'w'), default=float)
    frames = [k for k, f in SQ.frames_of(unit, seq)]
    facing = res[str(frames[0])]['facing']
    stand = dict(js['Q'])
    cpath = '%s_%s_case.json' % (unit, seq)
    case = json.load(open(cpath)) if os.path.exists(cpath) else None

    def with_case(Q, k):
        if case is None:
            return Q
        return dict(Q, cfx=case['cfx'], cfy=case['cfy'], cfa=case['cfa'], cft=case.get('cft', 0.0),
                    cfix=float(case['cfix'].get(str(k), 0.0)))
    # (the legs held down: LEGS=w, ANKLE=units - a falling soldier's feet don't rise past his knees)
    import ground
    w_legs = float(os.environ.get('LEGS', 0.003)); ank = float(os.environ.get('ANKLE', 5.0))
    F.EXTRA = lambda S_, Q_, t_, dz_: ground.legs_down(S_, Q_, facing, dz_, w=w_legs, ankle=ank, knee=ank + 2.5)
    tg = {}

    def loss(Q, k):
        if k not in tg:
            tg[k] = F.Target(unit, k, facing)
        return F.frame_loss(S, with_case(Q, k), tg[k], ax, y0)

    def Qof(k):
        return dict(stand, **res[str(k)]['Q'])
    for k in range(b, a - 1, -1):
        t0 = time.time()
        nxt = Qof(k + 1) if str(k + 1) in res else Qof(k)
        cands = [(loss(Qof(k), k), Qof(k), 'had')]
        Q, fb, iu = SM.fit_best(unit, S, ax, y0, k, facing, with_case(nxt, k), [(SM.W_PREV, with_case(nxt, k))],
                                iters, falls=True)
        cands.append((loss(Q, k), Q, 'from next'))
        Q2, fb2, iu2 = SM.fit_one(unit, S, ax, y0, k, facing, with_case(Qof(k), k), [], iters, win=40.0, sigma=0.1)
        cands.append((loss(Q2, k), Q2, 'refit'))
        if os.environ.get('FROM_PREV') and str(k - 1) in res:
            # (from the frame before: a death's last frame fitted on its own can land in another pose altogether)
            prv = Qof(k - 1)
            Q3, fb3, iu3 = SM.fit_best(unit, S, ax, y0, k, facing, with_case(prv, k), [(SM.W_PREV, with_case(prv, k))],
                                       iters, falls=True)
            cands.append((loss(Q3, k), Q3, 'from prev'))
        cands.sort(key=lambda t: t[0])
        res[str(k)] = dict(res[str(k)], Q=cands[0][1], f=cands[0][0], how='fix ' + cands[0][2])
        print(seq, 'frame', k, ' '.join('%s %.3f' % (c[2], c[0]) for c in cands), '%.0fs' % (time.time() - t0),
              flush=True)
    for k in range(max(a - 1, frames[1]), min(b + 1, frames[-1]) + 1):
        i = frames.index(k)
        t0 = time.time()
        before = with_case(Qof(frames[i - 1]), k)
        if i + 1 < len(frames):
            after = with_case(Qof(frames[i + 1]), k)
            pulls = [(SM.W_MID, {q: 0.5 * (before[q] + after[q]) for q in before})]
        else:
            pulls = [(SM.W_PREV, before)]
        Q, fb, iu = SM.fit_one(unit, S, ax, y0, k, facing, with_case(Qof(k), k), pulls, max(iters // 2, 40), win=20.0,
                               sigma=0.06)
        res[str(k)] = dict(res[str(k)], Q=Q, f=loss(Q, k), iou=F.iou(S, with_case(Q, k), tg.get(k) or
                                                                      F.Target(unit, k, facing), ax, y0))
        print(seq, 'relax', k, 'f %.3f' % res[str(k)]['f'], '%.0fs' % (time.time() - t0), flush=True)
    json.dump(res, open(path, 'w'), default=float)
    print('done', flush=True)


if __name__ == '__main__':
    main()
