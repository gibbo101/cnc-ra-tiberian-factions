"""staged fit of the Titan's legs to TS's walk frames.

    python3 fitlegs2.py poses [shape.json]     every step's pose with the shape fixed (from shape.json or init)
    python3 fitlegs2.py shape                  shared dims over 5 steps with their poses free (small sigma)
"""
import sys, json, time
import numpy as np
import cma
import rc
import legfit as LF

AX = 47.4
Y0 = 55.0          # heights are relative to TS's line y 55; the ground's own height g is fitted

SHAPE0 = dict(LF.SHAPE)
SHAPE0.update(hip_c=(0.8, 0.0, 19.0), hip_r=(6.4, 7.8, 10.0), hip_bot=16.6, jv=5.4, jw=17.0, ju=0.4, splay=0.0,
              Lt=6.6, tw=4.8, td=4.6, Ls=11.6, sw=3.8, sd=3.4, lf=6.6, lh=2.8, fw=4.8, fh=2.6, kb=1.9, kw=3.4,
              kd=2.6, g=2.5)

SHAPE_SPEC = [('hip_cu', -2, 3), ('hip_cw', 15, 24), ('hip_ra', 4, 9), ('hip_rb', 5, 9.5), ('hip_rc', 5, 14),
              ('hip_bot', 13, 21), ('jv', 3.5, 7.5), ('jw', 14, 21), ('ju', -2.5, 3), ('splay', -8, 12),
              ('Lt', 3.5, 10), ('tw', 2.5, 6.5), ('td', 2.5, 6.5), ('Ls', 7, 15), ('sw', 2.2, 5.5), ('sd', 2.2, 5.5),
              ('lf', 3, 10), ('lh', 0, 5), ('fw', 3, 7), ('fh', 1.2, 4), ('kb', 0, 3.5), ('kw', 1.5, 5), ('kd', 1, 4),
              ('g', 0.5, 5)]
POSE_SPEC = [(-78, 32), (8, 68), (-28, 28), (-78, 32), (8, 68), (-28, 28), (-1.5, 1.5)]


def S_get(S, k):
    if k == 'hip_cu': return S['hip_c'][0]
    if k == 'hip_cw': return S['hip_c'][2]
    if k in ('hip_ra', 'hip_rb', 'hip_rc'): return S['hip_r']['abc'.index(k[-1])]
    return S[k]


def S_set(S, k, v):
    if k == 'hip_cu': S['hip_c'] = (v, 0.0, S['hip_c'][2]); return
    if k == 'hip_cw': S['hip_c'] = (S['hip_c'][0], 0.0, v); return
    if k in ('hip_ra', 'hip_rb', 'hip_rc'):
        r = list(S['hip_r']); r['abc'.index(k[-1])] = v; S['hip_r'] = tuple(r); return
    S[k] = v


def soles(S, pose):
    out = []
    for side, (a_t, a_s, a_f) in ((-1, pose[0:3]), (1, pose[3:6])):
        _, (J, K, A) = LF.leg_parts(side, a_t, a_s, a_f, S, pose[6])
        af = np.deg2rad(a_f)
        fwd = np.array([np.cos(af), 0.0, np.sin(af)]); up = np.array([-np.sin(af), 0.0, np.cos(af)])
        toe = A + fwd * S['lf'] - up * S['fh']; heel = A - fwd * S['lh'] - up * S['fh']
        out.append(min(toe[2], heel[2]))
    return out


class StepLoss:
    def __init__(self, step, ss=3, w_cls=0.3):
        self.v = LF.TSViews(step, ax=AX, y0=Y0)
        self.ss, self.w_cls = ss, w_cls
        from tsclass import classes
        x0, yw, x1, y1 = self.v.win
        self.cls = []
        for k in range(8):
            c, _ = classes(k * 15 + step)
            c = c[yw:y1, x0:x1]
            # 1 gold (legs), 2 dark (hip: grey, olive, blue); 0 elsewhere
            cc = np.zeros(c.shape, int); cc[c == 1] = 1; cc[(c == 2) | (c == 3) | (c == 4)] = 2
            self.cls.append(cc)

    def __call__(self, S, pose):
        v = self.v; ss = self.ss
        x0, yw, x1, y1 = v.win; h, w = y1 - yw, x1 - x0
        parts = LF.body_parts(S, pose[:6], pose[6])
        dark = (LF.HIP, LF.THIGH, LF.KNEE)
        cls_of = np.array([0] + [2 if p.comp in dark else 1 for p in parts])
        tot = 0.0
        for k in range(8):
            M = LF.facing_matrix(k)
            pk = [p.moved(M) for p in parts]
            t, who, nrm, O = rc.render_ids(pk, v.cam, x0, yw, w, h, ss=ss, zstart=200.0)
            cl = cls_of[who + 1].reshape(h, ss, w, ss).transpose(0, 2, 1, 3).reshape(h, w, ss * ss)
            cov = (cl > 0).mean(-1)
            m = v.masks[k]
            tot += np.abs(cov - m).sum() / m.sum()
            tc = self.cls[k]; both = m & (cov >= 0.5) & (tc > 0)
            agree = (cl == tc[..., None]).mean(-1)
            tot += self.w_cls * (1 - agree[both]).sum() / m.sum()
        lows = soles(S, pose)
        pen = (min(lows) - S['g']) ** 2 + 2.0 * sum(max(0.0, S['g'] - l) ** 2 for l in lows)
        return tot / 8 + 0.02 * pen


def init_poses():
    from leginit import centre_lines, fit_polyline
    J = np.array([0.5, 17.0])
    poses = {}
    for step in range(15):
        L, R = centre_lines(step)
        pp = []
        for pts in (L, R):
            K, A, rms = fit_polyline(pts, J)
            at = np.degrees(np.arctan2(K[0] - J[0], J[1] - K[1])); as_ = np.degrees(np.arctan2(A[0] - K[0], K[1] - A[1]))
            pp += [float(at), float(as_), 0.0]
        poses[step] = pp + [0.0]
    return poses


def fit_pose(step, S, init, iters=60, sigma=0.12, popsize=14, seed=3):
    Lf = StepLoss(step)
    lo = np.array([p[0] for p in POSE_SPEC], float); hi = np.array([p[1] for p in POSE_SPEC], float)
    span = hi - lo
    z0 = np.clip((np.array(init, float) - lo) / span, 0.01, 0.99)
    f = lambda z: Lf(S, lo + np.clip(z, 0, 1) * span)
    es = cma.CMAEvolutionStrategy(z0, sigma, {'bounds': [0, 1], 'popsize': popsize, 'maxiter': iters, 'seed': seed,
                                               'verbose': -9})
    while not es.stop():
        Z = es.ask(); es.tell(Z, [f(z) for z in Z])
    return (lo + np.clip(es.result.xbest, 0, 1) * span).tolist(), es.result.fbest


def fit_shape(S, poses, steps=(0, 3, 7, 10, 13), iters=120, sigma=0.08, popsize=16, seed=5):
    losses = {s: StepLoss(s) for s in steps}
    lo = np.array([p[1] for p in SHAPE_SPEC] + sum([[q[0] for q in POSE_SPEC] for _ in steps], []), float)
    hi = np.array([p[2] for p in SHAPE_SPEC] + sum([[q[1] for q in POSE_SPEC] for _ in steps], []), float)
    x0 = np.array([S_get(S, k) for k, *_ in SHAPE_SPEC] + sum([list(poses[s]) for s in steps], []), float)
    span = hi - lo

    def unpack(x):
        S2 = dict(S)
        for (k, *_), v in zip(SHAPE_SPEC, x):
            S_set(S2, k, float(v))
        n = len(SHAPE_SPEC)
        ps = {s: x[n + 7 * i: n + 7 * i + 7] for i, s in enumerate(steps)}
        return S2, ps

    def f(z):
        S2, ps = unpack(lo + np.clip(z, 0, 1) * span)
        return sum(losses[s](S2, ps[s]) for s in steps) / len(steps)

    es = cma.CMAEvolutionStrategy(np.clip((x0 - lo) / span, 0.01, 0.99), sigma,
                                  {'bounds': [0, 1], 'popsize': popsize, 'maxiter': iters, 'seed': seed, 'verbose': -9})
    t0 = time.time(); it = 0
    while not es.stop():
        Z = es.ask(); es.tell(Z, [f(z) for z in Z]); it += 1
        if it % 5 == 0:
            S2, ps = unpack(lo + np.clip(es.result.xbest, 0, 1) * span)
            print('shape it', it, 'best %.4f' % es.result.fbest, '%.0fs' % (time.time() - t0), flush=True)
            json.dump(dict(S=S2, poses={str(k): list(map(float, v)) for k, v in ps.items()}, f=es.result.fbest),
                      open('legs_shape.json', 'w'), default=float)
    S2, ps = unpack(lo + np.clip(es.result.xbest, 0, 1) * span)
    return S2, {k: list(map(float, v)) for k, v in ps.items()}, es.result.fbest


if __name__ == '__main__':
    what = sys.argv[1]
    if what == 'poses':
        if len(sys.argv) > 2:
            js = json.load(open(sys.argv[2])); S = js['S']
            S['hip_c'] = tuple(S['hip_c']); S['hip_r'] = tuple(S['hip_r'])
            init = {int(k): v for k, v in js.get('poses', {}).items()}
        else:
            S = dict(SHAPE0); init = {}
        base = init_poses()
        out = {}
        for step in range(15):
            p0 = init.get(step, base[step])
            t0 = time.time()
            p, fb = fit_pose(step, S, p0)
            out[step] = p
            print('step', step, 'loss %.4f' % fb, np.round(p, 1).tolist(), '%.0fs' % (time.time() - t0), flush=True)
            json.dump(dict(S=S, poses={str(k): v for k, v in out.items()}), open('legs_poses.json', 'w'), default=float)
    elif what == 'shape':
        js = json.load(open(sys.argv[2])); S = js['S']; S['hip_c'] = tuple(S['hip_c']); S['hip_r'] = tuple(S['hip_r'])
        poses = {int(k): v for k, v in js['poses'].items()}
        S2, ps, fb = fit_shape(S, poses)
        print('shape done', fb)
