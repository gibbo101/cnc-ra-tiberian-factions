"""
infliedown.py - lying down and getting up (2 frames a facing each): the in-betweens from the standing pose to the prone
one (the crawl's first step), each fitted to its TS frame and held near the straight path between the two (a third and
two thirds of the way), so standing -> down -> prone runs as one movement.  TS's get-up frames are its lie-down frames
backwards, pixel for pixel, so getting up uses the same two poses backwards.

    python3 infliedown.py UNIT shape.json iters
        reads UNIT_stand_frames.json (standing, per facing) and UNIT_crawl_frames.json (prone = its step 0)
        writes UNIT_lie_down_frames.json and UNIT_get_up_frames.json {frame: {Q, facing, iou}}
"""
import json, os, sys, time
import numpy as np
import inf as I
import inffit as F
import infseq as SQ
from infsmooth import fit_one

W_PATH = 0.002            # towards the straight path between standing and prone (weak: TS kneels on the way)


def lerp(A, B, t):
    return {k: (1 - t) * A[k] + t * B[k] if isinstance(A.get(k), (int, float)) and k in B else A[k] for k in A}


def kneel(A, B):
    """on all fours on the way down: the torso near level, the thighs down to the knees on the ground, the lower legs
    back along it, the arms down to the hands (a rifle held as standing), looking ahead; placed as the prone pose."""
    K = dict(A)
    K.update(pitch=72.0, roll=0.0, yaw=0.0, sp=-8.0, sy=0.0, sr=0.0, hp=-35.0, hy=0.0,
             lhf=88.0, rhf=88.0, lha=8.0, rha=8.0, lht=0.0, rht=0.0, lkf=100.0, rkf=100.0, laf=35.0, raf=35.0)
    if A.get('ik', 1.0) <= 0.5:
        K.update(lsf=70.0, rsf=70.0, lsa=10.0, rsa=10.0, lst=0.0, rst=0.0, lef=15.0, ref=15.0)
    for k in ('bx', 'by', 'dx', 'dy'):
        if k in B:
            K[k] = 0.5 * (A.get(k, 0.0) + B[k]) if k in ('dx', 'dy') else B[k] * (0.5 if k in ('bx', 'by') else 1.0)
    return K


def main():
    unit, shape = sys.argv[1:3]
    import infunit; infunit.use(unit)
    iters = int(sys.argv[3])
    js = json.load(open(shape))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    ax, y0 = js['ax'], js['y0']
    stand = json.load(open('%s_stand_frames.json' % unit))
    crawl = json.load(open('%s_crawl_frames.json' % unit))
    lie = SQ.frames_of(unit, 'lie_down')
    get = SQ.frames_of(unit, 'get_up')
    out = '%s_lie_down_frames.json' % unit
    res = json.load(open(out)) if os.path.exists(out) else {}
    for f in range(8):
        A = dict(js['Q'], **stand[str(f)]['Q']) if str(f) in stand else dict(js['Q'])
        B = dict(js['Q'], **crawl[str(SQ.frames_of(unit, 'crawl')[0][1][f])]['Q'])
        # (through kneeling on all fours, as TS's second frame is and as anyone lies down: the straight path from
        # standing to prone passes through a dive, the legs up behind)
        K = kneel(A, B)
        for s, ks in lie:
            k = ks[f]
            if str(k) in res:
                continue
            P = lerp(A, K, 0.5) if s == 0 else K
            t0 = time.time()
            Q, fb, iu = fit_one(unit, S, ax, y0, k, f, P, [(W_PATH, P)], iters, win=60.0, sigma=0.12)
            if s == 1:
                # (TS's second frame is down on all fours for some, nearly flat for others - the Ghost's legs are already
                # out behind him: it is also fitted from half way to prone and from prone, and the frame TS's matches
                # best kept, TS's shadow counting)
                tg = F.Target(unit, k, f)
                best = (F.frame_loss(S, Q, tg, ax, y0), Q, fb, iu)
                for P2 in (lerp(K, B, 0.5), B):
                    Q2, fb2, iu2 = fit_one(unit, S, ax, y0, k, f, P2, [(W_PATH, P2)], iters, win=60.0, sigma=0.12)
                    l2 = F.frame_loss(S, Q2, tg, ax, y0)
                    if l2 < best[0]:
                        best = (l2, Q2, fb2, iu2)
                _, Q, fb, iu = best
            res[str(k)] = dict(Q=Q, f=fb, iou=iu, facing=f, step=s)
            json.dump(res, open(out, 'w'), default=float)
            print('lie_down facing', f, 'frame', k, 'f %.3f iou %.3f' % (fb, iu), '%.0fs' % (time.time() - t0), flush=True)
    # getting up: the same poses backwards (TS: get-up frame 0 = lie-down frame 1, 1 = 0)
    gu = {}
    for f in range(8):
        for s, ks in get:
            src = lie[len(lie) - 1 - s][1][f]
            gu[str(ks[f])] = dict(res[str(src)], step=s, source=src)
    json.dump(gu, open('%s_get_up_frames.json' % unit, 'w'), default=float)
    print('done', flush=True)


if __name__ == '__main__':
    main()
