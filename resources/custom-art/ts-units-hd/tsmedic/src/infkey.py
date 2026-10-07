"""
infkey.py - an 8-facing sequence's key poses read off TS's frames: each step's one pose fitted to its frame in all 8
facings together (TS renders one 3D pose 8 ways, so the 8 views pin it down), with a wide search so the fit is not
stuck where it starts: a few hundred poses drawn across the whole range of the sequence's poses are scored on 4 of
the facings, the best few on all 8, and the best two refined (CMA).  Each step also starts from the step before and
small changes of it, so neighbouring steps stay alike where TS's do.

    python3 infkey.py UNIT shape.json SEQ [n_draws] [iters]     writes UNIT_SEQ_key.json {step: {Q, frames, f, iou}}
        STEPS=0,1 fits only those steps; KEEP=1 keeps steps already in the file
"""
import json, os, sys, time
import numpy as np
import inf as I
import inffit as F
import infseq as SQ

# the range each pose key is drawn from and held within (wide: the crawl's whole range of poses)
RANGE = dict(pitch=(45, 105), roll=(-35, 35), yaw=(-40, 40), sp=(-45, 35), sy=(-40, 40), sr=(-20, 20), hp=(-115, 35),
             hy=(-50, 50), dx=(-4.5, 4.5), dy=(-4.5, 4.5),
             lhf=(-35, 100), rhf=(-35, 100), lha=(-12, 55), rha=(-12, 55), lht=(-45, 45), rht=(-45, 45),
             lkf=(0, 145), rkf=(0, 145), laf=(-35, 65), raf=(-35, 65),
             lsf=(-35, 205), rsf=(-35, 205), lsa=(-30, 90), rsa=(-30, 90), lst=(-60, 60), rst=(-60, 60),
             lef=(0, 150), ref=(0, 150),
             rgx=(0.0, 5.5), rgy=(-2.5, 3.5), rgz=(-6.5, 4.0), lfx=(1.0, 5.5), lsw=(-60, 60), rsw=(-60, 60),
             gp=(-100, 140), gy=(-150, 90), gr=(-90, 90), bx=(-7, 5), by=(-4, 4))
# the run: upright, a stride
RANGE_WALK = dict(RANGE, pitch=(-10, 45), roll=(-20, 20), sp=(-25, 35), hp=(-40, 40), lhf=(-80, 100),
                  rhf=(-80, 100), lha=(-10, 30), rha=(-10, 30), lkf=(0, 150), rkf=(0, 150), laf=(-45, 60),
                  raf=(-45, 60), dx=(-3, 3), dy=(-3, 3))


def keys_of(Q):
    return [k for k, a, b in F.qspec(Q)] + ['bx', 'by']


def draw(rng, Q0, keys, rngs, n):
    out = []
    for _ in range(n):
        Q = dict(Q0)
        for k in keys:
            a, b = rngs[k]
            Q[k] = float(rng.uniform(a, b))
        out.append(Q)
    return out


def jitter(rng, Q0, keys, rngs, n, scale=0.12):
    out = []
    for _ in range(n):
        Q = dict(Q0)
        for k in keys:
            a, b = rngs[k]
            Q[k] = float(np.clip(Q0[k] + rng.normal(0, scale * (b - a)), a, b))
        out.append(Q)
    return out


def fit_step(unit, S, ax, y0, frames, seeds, rngs, n_draw, iters, seed=1):
    tg = [F.Target(unit, k, f) for f, k in enumerate(frames)]
    tg4 = [tg[f] for f in (0, 2, 4, 6)]
    keys = keys_of(seeds[0])
    rng = np.random.default_rng(seed)
    cands = list(seeds)
    for q in seeds:
        cands += jitter(rng, q, keys, rngs, max(n_draw // 10, 4))
    cands += draw(rng, seeds[0], keys, rngs, n_draw)

    def loss(Q, ts):
        return float(np.mean([F.frame_loss(S, Q, t, ax, y0) for t in ts]))
    sc = sorted(((loss(q, tg4), i) for i, q in enumerate(cands)))[:8]
    sc = sorted(((loss(cands[i], tg), i) for _, i in sc))[:2]
    lo = np.array([rngs[k][0] for k in keys], float); hi = np.array([rngs[k][1] for k in keys], float)
    best = None
    for l0, i in sc:
        Q0 = cands[i]
        x0 = np.clip(np.array([Q0[k] for k in keys], float), lo, hi)

        def f(x):
            Q = dict(Q0); Q.update({k: float(v) for k, v in zip(keys, x)})
            return loss(Q, tg)
        res = {}

        def cb(x, fb, it, dt):
            res['x'] = x; res['f'] = fb
        F.cma_fit(f, lo, hi, x0, iters, cb, sigma=0.08, pop=16, seed=seed)
        Q = dict(Q0); Q.update({k: float(v) for k, v in zip(keys, res['x'])})
        if best is None or res['f'] < best[1]:
            best = (Q, res['f'], l0)
    Q, fb, l0 = best
    return Q, fb, [F.iou(S, Q, t, ax, y0) for t in tg], l0


def main():
    unit, shape, seq = sys.argv[1:4]
    n_draw = int(sys.argv[4]) if len(sys.argv) > 4 else 300
    iters = int(sys.argv[5]) if len(sys.argv) > 5 else 90
    import infunit; infunit.use(unit)
    js = json.load(open(shape))
    S = dict(F.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    ax, y0 = js['ax'], js['y0']
    rngs = RANGE_WALK if seq == 'walk' else RANGE
    out = '%s_%s_key.json' % (unit, seq)
    res = json.load(open(out)) if (os.path.exists(out) and os.environ.get('KEEP')) else {}
    only = [int(v) for v in os.environ['STEPS'].split(',')] if os.environ.get('STEPS') else None
    # seeds: the poses the unit has now for each step (its current frames' shared part), the standing pose made prone
    base = dict(js['Q'])
    cur = {}
    try:
        cf = json.load(open('%s_%s_frames.json' % (unit, seq)))
        for s, frames in SQ.frames_of(unit, seq):
            if str(frames[0]) in cf:
                cur[s] = dict(base, **cf[str(frames[0])]['Q'])
    except FileNotFoundError:
        pass
    prev = None
    for s, frames in SQ.frames_of(unit, seq):
        if only is not None and s not in only:
            continue
        if str(s) in res:
            prev = dict(base, **res[str(s)]['Q']); continue
        seeds = [dict(dict(bx=0.0, by=0.0), **q) for q in (prev, cur.get(s)) if q is not None] or \
            [dict(base, pitch=85.0, bx=0.0, by=0.0)]
        if os.environ.get('SEED_KEY') and os.path.exists(os.environ['SEED_KEY']):
            sk = json.load(open(os.environ['SEED_KEY']))
            if str(s) in sk:
                seeds.insert(0, dict(dict(bx=0.0, by=0.0), **dict(base, **sk[str(s)]['Q'])))
        t0 = time.time()
        Q, fb, ious, l0 = fit_step(unit, S, ax, y0, frames, seeds, rngs, n_draw, iters, seed=1 + s)
        res = json.load(open(out)) if os.path.exists(out) else res
        res[str(s)] = dict(Q=Q, frames=frames, f=fb, iou=ious)
        json.dump(res, open(out, 'w'), default=float)
        prev = Q
        print(seq, 'step', s, 'f %.3f (start %.3f) iou %.3f' % (fb, l0, np.mean(ious)), [round(v, 2) for v in ious],
              '%.0fs' % (time.time() - t0), flush=True)
    print('done', flush=True)


if __name__ == '__main__':
    main()
