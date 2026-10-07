"""
wriggle.py - the crawl's body movement (Luke: "the body stays stiff as a board"; TS's E1 crawl shows the body
wriggling), fitted on top of a crawl (crawlbio.py's stroke kept: the legs, the arms, the rifle, how he lies).

TS's crawl frames move the head across the body by 3-4 TS px from step to step (the NW, NE and S views) and lift it
about 2 px (the side views); the fitted crawl moved it under 1 px, the whole body pivoting as one board.  So the
body gets its own movement (crawlbio.WRIGGLE): the spine bends to the side (sr) and twists (sy) on its own timing
against the hips' swing (yaw, roll), the chest lifts on each pull (sp, twice a cycle), the head pitching against it.

The loss: crawlbio's (TS's silhouette and colour classes in TS's camera, TS's shadow, lying on the ground) plus how
the head moves against the body step by step: in each facing, the head's centroid against the silhouette's, less
its mean over the 6 steps (the wriggle itself), TS's against the model's (HEADW per TS px squared).

    python3 wriggle.py UNIT [iters] [pop]      reads UNIT_crawlfit.json, writes UNIT_crawlfit_wriggle.json
        env: HEADW (0.05), SHADOW (0.5), LYING (0.03), FREE=extra,keys (crawlbio keys also freed)
"""
import json, os, sys, time
import numpy as np
import multiprocessing as mp
import rc
import inf as I
import inffit as F
import infseq as SQ
import crawlbio as B
import crawlfit as CF
import ground

N = 6
unit = sys.argv[1]
iters = int(sys.argv[2]) if len(sys.argv) > 2 else 100
pop = int(sys.argv[3]) if len(sys.argv) > 3 else 16
HEADW = float(os.environ.get('HEADW', 0.05))
W_LYING = float(os.environ.get('LYING', 0.03))
import infunit
infunit.use(unit)
js = json.load(open('%s_shape.json' % unit))
S = dict(F.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
ax, y0 = js['ax'], js['y0']
base = dict(js['Q'], bx=0.0, by=0.0)
src = json.load(open(os.environ.get('START', '%s_crawlfit.json' % unit)))
p0 = dict(src['bio'])
gen = CF.genuine(unit)
frames = SQ.frames_of(unit, 'crawl')
TG = [[F.Target(unit, frames[s][1][f], f) for f in gen] for s in range(N)]
CAM = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))


def head_rel(sil, head, win):
    """the head's centroid against the silhouette's (TS px), or None."""
    ys, xs = np.nonzero(sil)
    hy, hx = np.nonzero(head)
    if len(xs) == 0 or len(hx) == 0:
        return None
    return np.array([hx.mean() - xs.mean(), hy.mean() - ys.mean()])


# TS's: the head (its navy and light blue) against the silhouette, per step and facing
TS_H = np.zeros((N, len(gen), 2))
for s in range(N):
    for j, t in enumerate(TG[s]):
        TS_H[s, j] = head_rel(t.mask, np.isin(t.cls, (F.N, F.LB)), t.win)
TS_D = TS_H - TS_H.mean(0, keepdims=True)

# the wriggle's keys (crawlbio.WRIGGLE) and the body's lateral amplitudes, refitted together
KEYS = B.WRIGGLE + [(k, lo, hi, c) for k, lo, hi, c in B.COMMON if k in ('A_roll', 'A_yaw', 'A_sy', 'A_hy', 'A_by',
                                                                       'A_bob')]
KEYS = [(k, lo, hi, p0.get(k, c)) for k, lo, hi, c in KEYS]
for k in filter(None, os.environ.get('FREE', '').split(',')):
    for kk, lo, hi, c in B.spec(unit):
        if kk == k:
            KEYS.append((kk, lo, hi, p0.get(kk, c)))
# (A_sy widened: the old range stopped the shoulders' turn at 18 degrees)
KEYS = [(k, -35, 35, c) if k == 'A_sy' else (k, lo, hi, c) for k, lo, hi, c in KEYS]


def step_terms(args):
    p, s = args
    Q = B.pose(unit, base, p, s)
    out = []
    for j, t in enumerate(TG[s]):
        parts, dz = I.grounded(S, Q, I.facing_angle(t.facing))
        cl = F.model_cls(parts, CAM, t.win)
        cov = np.clip((cl > 0).mean(-1) / F.COVER, 0, 1)
        keep = ~t.fx
        d = np.abs(cov - t.mask)
        l = d[keep].sum() / t.mask.sum()
        both = t.mask & (cov >= 0.5)
        agree = F.AG[cl, t.cls[..., None]].mean(-1) / np.maximum((cl > 0).mean(-1), 1e-6)
        l += 0.6 * ((1 - agree[both]) * F.CW[t.cls[both]]).sum() / t.mask.sum()
        if t.shadow is not None:
            l += F.W_SHADOW * t.shadow.loss(parts, CAM)
        if W_LYING > 0:
            l += ground.lying(S, Q, t.facing, dz, w=W_LYING, head=False, elbows=True, chest=False)
        sil = (cl > 0).mean(-1) >= F.COVER
        head = (np.isin(cl, (I.NAVY, I.LBLUE)).sum(-1) >= (cl > 0).sum(-1) / 2.0) & sil
        h = head_rel(sil, head, t.win)
        out.append((l, h if h is not None else np.array([np.nan, np.nan])))
    return out


POOL = None


def evaluate(p):
    res = POOL.map(step_terms, [(p, s) for s in range(N)])
    L = np.mean([[l for l, h in r] for r in res])
    H = np.array([[h for l, h in r] for r in res])
    D = H - np.nanmean(H, 0, keepdims=True)
    e = np.nanmean(np.sum((D - TS_D) ** 2, -1))
    return float(L + HEADW * e), float(L), float(e)


def main():
    global POOL
    POOL = mp.Pool(2)
    keys = [k for k, a, b, c in KEYS]
    lo = np.array([a for k, a, b, c in KEYS], float); hi = np.array([b for k, a, b, c in KEYS], float)
    x0 = np.clip(np.array([c for k, a, b, c in KEYS], float), lo, hi)
    print('TS head wriggle (rms px)', float(np.sqrt(np.mean(np.sum(TS_D ** 2, -1)))), flush=True)
    print('start', evaluate(p0), flush=True)
    # the bend's and the twist's timing first: a coarse look over their phases with a fair amplitude
    best = None
    if not os.environ.get('KEEP_PHASE'):
        for psr in range(-180, 180, 60):
            for asr in (-15.0, 15.0):
                for asy in (-15.0, 15.0):
                    p = dict(p0, A_sr=asr, ph_sr=float(psr), A_sy=asy, ph_sy=float(psr))
                    v = evaluate(p)
                    if best is None or v[0] < best[0][0]:
                        best = (v, p)
        print('coarse', best[0], {k: best[1][k] for k in ('A_sr', 'ph_sr', 'A_sy', 'ph_sy')}, flush=True)
        x0 = np.clip(np.array([best[1].get(k, c) for k, a, b, c in KEYS], float), lo, hi)
    out_path = os.environ.get('OUT', '%s_crawlfit_wriggle.json' % unit)

    def save(p, final=False):
        out = {str(s): dict(Q=B.pose(unit, base, p, s), frames=frames[s][1]) for s in range(N)}
        out['bio'] = p
        for k in ('side', 'mirror_off'):
            if k in src:
                out[k] = src[k]
        if final:
            for s in range(N):
                out[str(s)]['iou'] = CF.ious(unit, S, js, out[str(s)]['Q'], frames[s][1], out.get('mirror_off'))
        json.dump(out, open(out_path, 'w'), default=float)

    res = {}

    def cb(x, fb, it, dt):
        res['x'] = x
        p = dict(p0, **{k: float(v) for k, v in zip(keys, x)})
        print('it', it, 'f %.4f' % fb, evaluate(p), '%.0fs' % dt, flush=True)
        save(p)
    F.cma_fit(lambda x: evaluate(dict(p0, **{k: float(v) for k, v in zip(keys, x)}))[0], lo, hi, x0, iters, cb,
              sigma=float(os.environ.get('SIGMA', '0.12')), pop=pop, seed=1)
    p = dict(p0, **{k: float(v) for k, v in zip(keys, res['x'])})
    print('fitted', {k: round(p[k], 2) for k in keys}, flush=True)
    print('final', evaluate(p), flush=True)
    save(p, final=True)
    print('done', flush=True)


if __name__ == '__main__':
    main()
