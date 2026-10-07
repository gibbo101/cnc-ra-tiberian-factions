"""
crawlfit.py - the crawl read off TS's own frames, one pose a step, the way TS draws it.

TS's crawl is one 3D pose a step rendered in its facings - but for the Disc Thrower, the Engineer and the Medic, TS drew
only the west side (and north and south) and mirrored them for the east side: their E, NE and SE crawl frames are the
W, NW and SW ones flipped (the same pixels).  One pose can't fit both sides of a mirrored set (his left and right swap),
which is what kept every crawl fit so far round 0.6 overlap, and the free-arm crawls jittery.  So each step's pose is
fitted to the facings TS rendered (all 8 for E1 and the Ghost; N, NW, W, SW, S for the mirrored three), and the
mirrored facings get the mirrored pose (his left and right swapped), so the HD frames show what TS's show.

The Jumpjet never lies down in TS (his crawl frames are his walk frames): he is not fitted here.

Each step: a wide search (poses drawn over the crawl's whole range, the step before and its neighbours, and a start
pose) scored on the step's frames, the best refined (CMA); a small pull toward the step before keeps the steps alike
where TS's are.  A second pass starts each step from both its neighbours, so the cycle closes.

    python3 crawlfit.py UNIT [n_draws] [iters] [passes]     writes UNIT_crawlfit.json {step: {Q, f, iou: {facing: v}}}
        SIDE=w|e: which side TS rendered (mirrored units; default w)    STEPS=0,1: only those steps
"""
import json, os, sys, time
import numpy as np
import inf as I
import inffit as F
import infseq as SQ
import infkey as K

MIRRORED = ('e2', 'eng', 'medic')
# the key families swapped left for right in the mirror, and the keys whose sign turns
LR = ('hf', 'ha', 'ht', 'kf', 'af', 'sf', 'sa', 'st', 'ef', 'sw')
NEG = ('roll', 'yaw', 'sy', 'sr', 'hy', 'by', 'dx', 'gy', 'gr', 'rgy')
TWIST = ('ht', 'st')
# the crawl's range (infkey's, the hands free to reach anywhere along the ground)
RANGE = dict(K.RANGE, pitch=(55, 110), sp=(-45, 25), hp=(-100, 35), dy=(0.0, 12.0), dx=(-4.0, 5.0), bx=(-8.0, 3.0),
             by=(-3.0, 3.0))


def mirror(Q, off=None):
    """the pose with his left and right swapped (TS's flipped sprites); off: the flipped facing's own place (dx, dy:
    TS flipped each sprite about its own frame, a pixel or so off the soldier's ground point)."""
    M = dict(Q)
    for k in LR:
        if 'l' + k in Q and 'r' + k in Q:
            # (the twists turn the same way on both sides in inf.py, so the mirror turns them back)
            sg = -1.0 if k in TWIST else 1.0
            M['l' + k], M['r' + k] = sg * Q['r' + k], sg * Q['l' + k]
    for k in NEG:
        if k in Q:
            M[k] = -Q[k]
    # the case or toolbox in the other hand
    M['tbl'] = 1.0 - float(Q.get('tbl', 0.0))
    if off is not None:
        M['dx'], M['dy'] = float(off[0]), float(off[1])
    return M


def mirror_offsets(unit, S, js, res):
    """each flipped facing's place (dx, dy), fitted over the crawl's 6 steps with the poses mirrored."""
    gen = genuine(unit)
    out = {}
    for f in range(8):
        if f in gen:
            continue
        tg = [(dict(js['Q'], **res[str(s)]['Q']), F.Target(unit, res[str(s)]['frames'][f], f)) for s in range(6)
              if str(s) in res]
        q0 = mirror(tg[0][0])
        best = None
        for dx in np.arange(-4.0, 6.01, 0.5):
            for dy in np.arange(0.0, 14.01, 0.5):
                l = np.mean([F.frame_loss(S, mirror(q, (dx, dy)), t, js['ax'], js['y0']) for q, t in tg[::2]])
                if best is None or l < best[0]:
                    best = (l, dx, dy)
        l, dx, dy = best
        for it in range(3):
            st = 0.5 / 2 ** (it + 1)
            for ddx in (-st, 0.0, st):
                for ddy in (-st, 0.0, st):
                    l2 = np.mean([F.frame_loss(S, mirror(q, (dx + ddx, dy + ddy)), t, js['ax'], js['y0']) for q, t in tg])
                    if l2 < best[0]:
                        best = (l2, dx + ddx, dy + ddy)
            l, dx, dy = best
        out[str(f)] = (float(dx), float(dy))
        print('flipped facing', f, 'place', round(dx, 2), round(dy, 2), 'loss %.4f' % l, flush=True)
    return out


def genuine(unit, side=None):
    """the facings TS rendered (the others are mirror images of these)."""
    if unit not in MIRRORED:
        return list(range(8))
    side = side or os.environ.get('SIDE', 'w')
    if side == 'all':
        # (a crawl fitted to EA's own HD frames, drawn in all 8 facings: nothing mirrored)
        return list(range(8))
    return [0, 1, 2, 3, 4] if side == 'w' else [0, 4, 5, 6, 7]


def mirror_of(f):
    """the facing whose frames facing f's are the flip of (N and S: themselves)."""
    return (8 - f) % 8


def keys_of(Q):
    return [k for k, a, b in F.qspec(Q)] + ['bx', 'by']


def fit_step(unit, S, ax, y0, tgs, seeds, n_draw, iters, prev=None, w_prev=0.0, seed=1):
    keys = keys_of(seeds[0])
    rngs = {k: RANGE[k] for k in keys}
    rng = np.random.default_rng(seed)
    cands = list(seeds)
    for q in seeds:
        cands += K.jitter(rng, q, keys, rngs, max(n_draw // 8, 4))
    cands += K.draw(rng, seeds[0], keys, rngs, n_draw)
    span = np.array([rngs[k][1] - rngs[k][0] for k in keys], float)

    def pull(Q):
        if prev is None or w_prev <= 0:
            return 0.0
        d = np.array([(Q[k] - prev[k]) for k in keys], float) / span
        return w_prev * float((d ** 2).sum())

    def loss(Q, ts):
        return float(np.mean([F.frame_loss(S, Q, t, ax, y0) for t in ts])) + pull(Q)
    few = tgs[::2] if len(tgs) > 4 else tgs
    sc = sorted(((loss(q, few), i) for i, q in enumerate(cands)))[:8]
    sc = sorted(((loss(cands[i], tgs), i) for _, i in sc))[:2]
    lo = np.array([rngs[k][0] for k in keys], float); hi = np.array([rngs[k][1] for k in keys], float)
    best = None
    for l0, i in sc:
        Q0 = cands[i]
        x0 = np.clip(np.array([Q0[k] for k in keys], float), lo, hi)

        def f(x):
            Q = dict(Q0); Q.update({k: float(v) for k, v in zip(keys, x)})
            return loss(Q, tgs)
        res = {}

        def cb(x, fb, it, dt):
            res['x'] = x; res['f'] = fb
        F.cma_fit(f, lo, hi, x0, iters, cb, sigma=0.07, pop=16, seed=seed)
        Q = dict(Q0); Q.update({k: float(v) for k, v in zip(keys, res['x'])})
        if best is None or res['f'] < best[1]:
            best = (Q, res['f'], l0)
    return best


def ious(unit, S, js, Q, frames, offs=None):
    """each facing's overlap: the pose on the facings TS rendered, its mirror on the flipped ones."""
    gen = genuine(unit)
    out = {}
    for f, k in enumerate(frames):
        q = Q if f in gen else mirror(Q, (offs or {}).get(str(f)))
        out[f] = float(F.iou(S, q, F.Target(unit, k, f), js['ax'], js['y0']))
    return out


def pose_for(unit, res, s, f):
    """step s's pose in facing f (the mirror, at its place, on a flipped facing)."""
    Q = dict(res[str(s)]['Q'])
    if f in genuine(unit, res.get('side')):
        return Q
    return mirror(Q, res.get('mirror_off', {}).get(str(f)))


def write_frames(unit, path=None):
    js = json.load(open('%s_shape.json' % unit))
    res = json.load(open(path or '%s_crawlfit.json' % unit))
    out = {}
    for s, ks in SQ.frames_of(unit, 'crawl'):
        for f, k in enumerate(ks):
            out[str(k)] = dict(Q=pose_for(unit, res, s, f), facing=f, step=s, cycle_step=s)
    json.dump(out, open('%s_crawl_frames.json' % unit, 'w'), default=float)
    print(unit, 'crawl frames', len(out))


def main():
    unit = sys.argv[1]
    n_draw = int(sys.argv[2]) if len(sys.argv) > 2 else 250
    iters = int(sys.argv[3]) if len(sys.argv) > 3 else 70
    passes = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    import infunit; infunit.use(unit)
    js = json.load(open('%s_shape.json' % unit))
    S = dict(F.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    ax, y0 = js['ax'], js['y0']
    out = os.environ.get('OUT', '%s_crawlfit.json' % unit)
    res = json.load(open(out)) if (os.path.exists(out) and os.environ.get('KEEP')) else {}
    only = [int(v) for v in os.environ['STEPS'].split(',')] if os.environ.get('STEPS') else None
    gen = genuine(unit)
    steps = SQ.frames_of(unit, 'crawl')
    base = dict(js['Q'], bx=0.0, by=0.0)
    if os.environ.get('TBG'):
        base['tbg'] = float(os.environ['TBG'])
    start = json.load(open(os.environ['START'])) if os.environ.get('START') else {}
    for pas in range(passes):
        for s, frames in steps:
            if only is not None and s not in only:
                continue
            if pas == 0 and str(s) in res and os.environ.get('KEEP'):
                continue
            tgs = [F.Target(unit, frames[f], f) for f in gen]
            seeds = []
            for t in ((s - 1) % 6, (s + 1) % 6, s):
                if str(t) in res:
                    seeds.append(dict(base, **res[str(t)]['Q']))
            if str(s) in start or 'pitch' in start:
                seeds.append(dict(base, **(start[str(s)] if str(s) in start else start)))
                if os.environ.get('TBG'):
                    seeds[-1]['tbg'] = base['tbg']
            if not seeds:
                seeds = [dict(base, pitch=85.0)]
            prev = dict(base, **res[str((s - 1) % 6)]['Q']) if str((s - 1) % 6) in res else None
            t0 = time.time()
            Q, fb, l0 = fit_step(unit, S, ax, y0, tgs, seeds, n_draw if pas == 0 else n_draw // 3, iters, prev=prev,
                                 w_prev=float(os.environ.get('W_PREV', '0.02')), seed=1 + s + 10 * pas)
            if str(s) in res and pas > 0 and res[str(s)]['f'] < fb:
                print('pass', pas, 'step', s, 'kept (%.4f < %.4f)' % (res[str(s)]['f'], fb), flush=True)
                continue
            io = ious(unit, S, js, Q, frames)
            res[str(s)] = dict(Q=Q, frames=frames, f=fb, iou=io)
            json.dump(res, open(out, 'w'), default=float)
            print('pass', pas, 'step', s, 'f %.4f (start %.4f)' % (fb, l0), 'iou', ' '.join('%.2f' % io[f] for f in range(8)),
                  'mean genuine %.3f' % np.mean([io[f] for f in gen]), '%.0fs' % (time.time() - t0), flush=True)
    if only is None and gen != list(range(8)):
        res['mirror_off'] = mirror_offsets(unit, S, js, res)
        for s, frames in steps:
            res[str(s)]['iou'] = ious(unit, S, js, res[str(s)]['Q'], frames, res['mirror_off'])
            io = res[str(s)]['iou']
            print('step', s, 'iou', ' '.join('%.2f' % io[f] for f in range(8)), flush=True)
        json.dump(res, open(out, 'w'), default=float)
    print('done', flush=True)


if __name__ == '__main__':
    if sys.argv[2:3] == ['mirror']:
        unit = sys.argv[1]
        import infunit; infunit.use(unit)
        js = json.load(open('%s_shape.json' % unit))
        S = dict(F.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
        path = sys.argv[3] if len(sys.argv) > 3 else '%s_crawlfit.json' % unit
        res = json.load(open(path))
        res['mirror_off'] = mirror_offsets(unit, S, js, res)
        for s, frames in SQ.frames_of(unit, 'crawl'):
            res[str(s)]['iou'] = ious(unit, S, js, res[str(s)]['Q'], frames, res['mirror_off'])
            io = res[str(s)]['iou']
            print('step', s, 'iou', ' '.join('%.2f' % io[f] for f in range(8)), flush=True)
        json.dump(res, open(path, 'w'), default=float)
    elif sys.argv[2:3] == ['frames']:
        import infunit; infunit.use(sys.argv[1])
        write_frames(sys.argv[1], sys.argv[3] if len(sys.argv) > 3 else None)
    else:
        main()
