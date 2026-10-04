"""
infsmooth.py - a sequence TS draws once in one facing (the idles, the deaths) as one smooth motion: each frame fitted to
its TS frame starting from the frame before, then the whole run of poses relaxed together, every frame pulled towards
the middle of its neighbours (a smooth path, no jitter from frame to frame); an idle starts from the standing pose and
comes back to it, a death starts from it.

    python3 infsmooth.py UNIT shape.json SEQ FACING iters [sweeps]
        FACING: the standing facing TS draws the sequence in (its first frame matches that standing frame)
        writes UNIT_SEQ_frames.json {frame: {Q, facing, iou}}
"""
import json, os, sys, time
import numpy as np
import inf as I
import inffit as F
import infseq as SQ
from infstatic import ABS

WIN = dict(dx=2.0, dy=2.0, rgx=1.5, rgy=1.5, rgz=1.5, lfx=1.5, gy=80.0, gp=80.0, gr=60.0, lsf=70.0, rsf=70.0,
           lef=60.0, ref=60.0, lsa=40.0, rsa=40.0)
DIST = ('dx', 'dy', 'rgx', 'rgy', 'rgz', 'lfx')
W_PREV = 0.0015           # sequential pass: towards the frame before
W_MID = 0.004             # relaxing: towards the middle of the neighbours
W_END = 0.01              # the ends: towards the standing pose (idles at both ends, deaths at the start)
# the rifle can swing a long way between two of TS's frames (idle 1 lowers it to point at the ground, then brings it
# up level): each frame also starts from the rifle held these ways (yaw, pitch against the chest), and the body
# pitched further forward or back (the deaths' falls), keeping the best two starts
RIFLE_STARTS = [(-60.0, -10.0), (-20.0, -75.0), (0.0, 0.0), (-85.0, 10.0), (-10.0, 30.0)]
PITCH_STEPS = (-25.0, 25.0)


def keys_of(Q):
    return [k for k, a, b in F.qspec(Q)]


# (DENSE_RIFLE: a long gun TS swings far between frames - the Ghost's railgun thrown up and over as he falls: every
# frame also starts from the gun pointed every way (30-degree steps), and the pulls between frames hold the gun's
# angles a tenth as hard as the body's)
DENSE = bool(os.environ.get('DENSE_RIFLE'))
if DENSE:
    RIFLE_STARTS = [(float(gy), float(gp)) for gy in range(-180, 180, 30) for gp in (-80, -40, 0, 40, 80)]
# (GUN_LINE: each frame also starts from the gun laid along TS's own gun - the longest straight run of its green
# pixels - found by pointing the held gun every way and moving the grip about; the pulls between frames hold the gun a
# tenth as hard as the body: the Ghost's railgun, thrown up and over as he falls)
GUN_LINE = bool(os.environ.get('GUN_LINE'))
GUN_KEYS = ('gy', 'gp', 'gr', 'rgx', 'rgy', 'rgz', 'rsf', 'rsa', 'rst', 'ref')
# (GUN_ONE=frame: from that frame on the gun is in his right hand alone, his left arm free)
GUN_ONE = int(os.environ.get('GUN_ONE', '0') or 0)


def scale(keys):
    out = []
    for k in keys:
        v = 1.0 if k in DIST else 10.0
        if (DENSE and k in ('gy', 'gp', 'gr')) or (GUN_LINE and k in GUN_KEYS):
            v *= 3.16
        out.append(v)
    return np.array(out)


def ts_gun_line(unit, k, min_len=4.5):
    """TS's long gun in frame k: the longest straight run of its green pixels (two screen points), or None."""
    a = F.ts_frame(unit, k)
    cls = F.ts_classes(a)
    ys, xs = np.nonzero((cls == I.GREEN) & (a[..., 3] > 0))
    if len(xs) < 5:
        return None
    P = np.stack([xs + 0.5, ys + 0.5], 1).astype(float)
    rng = np.random.default_rng(0)
    best = None
    for _ in range(600):
        i, j = rng.choice(len(P), 2, replace=False)
        d = P[j] - P[i]; L = float(np.linalg.norm(d))
        if L < 3.0:
            continue
        u = d / L; n = np.array([-u[1], u[0]])
        inl = np.abs((P - P[i]) @ n) < 0.75
        t = np.sort((P[inl] - P[i]) @ u)
        runs = np.split(t, np.nonzero(np.diff(t) > 2.0)[0] + 1)
        r = max(runs, key=len)
        key = (len(r), float(r[-1] - r[0]))
        if best is None or key > best[0]:
            best = (key, P[i] + u * r[0], P[i] + u * r[-1])
    if best is None or best[0][1] < min_len:
        return None
    return best[1], best[2]


def gun_ends(S, Q, facing, cam):
    th = I.facing_angle(facing)
    parts, dz = I.grounded(S, Q, th)
    P = I.Pose(S, Q, th)
    G0, RG = P.rifle
    back = np.asarray(G0, float) - RG[:, 0] * S['gg'] + np.array([0.0, 0.0, dz])
    front = back + RG[:, 0] * S['gl']
    return np.array(cam.project(back), float), np.array(cam.project(front), float)


def to_one_hand(S, Q, facing):
    """the pose Q (gun in both hands) with the same arms as joint angles and the gun in the right hand alone."""
    if Q.get('ik', 1.0) < 0.5:
        return dict(Q, gone=1.0)
    from scipy.optimize import least_squares
    th = I.facing_angle(facing)
    P = I.Pose(S, Q, th)
    out = dict(Q, ik=0.0, gone=1.0)
    for side in ('l', 'r'):
        Sh, RU, E, RF, W = P.arms[side]

        def res(v):
            q = dict(out, **{side + 'sf': v[0], side + 'sa': v[1], side + 'st': v[2], side + 'ef': v[3]})
            Pq = I.Pose(S, q, th)
            _, _, E2, _, W2 = Pq.arms[side]
            return np.concatenate([E2 - E, W2 - W])
        best = None
        for v0 in ((30.0, 20.0, 0.0, 40.0), (90.0, 30.0, 0.0, 60.0), (0.0, 40.0, 30.0, 90.0), (120.0, 10.0, -30.0, 30.0)):
            r = least_squares(res, np.array(v0), bounds=([-60, -30, -60, 0], [200, 90, 60, 150]))
            if best is None or r.cost < best.cost:
                best = r
        out.update({side + 'sf': float(best.x[0]), side + 'sa': float(best.x[1]), side + 'st': float(best.x[2]),
                    side + 'ef': float(best.x[3])})
    return out


def one_hand_starts(unit, S, ax, y0, k, facing, Q0, n=3):
    """poses from Q0 (gun in his right hand) with the gun laid along TS's gun line in frame k (best n): his right arm
    and the gun's aim searched."""
    line = ts_gun_line(unit, k)
    if line is None:
        return []
    import rc
    A, B = line
    cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
    ut = (B - A) / max(float(np.linalg.norm(B - A)), 1e-6)
    out = []
    for gy in range(-150, 91, 30):
        for gp in range(-100, 141, 30):
            Q = dict(Q0, gy=float(gy), gp=float(gp))
            for rsf in (-40.0, 0.0, 40.0, 80.0, 120.0, 160.0):
                for rsa in (-20.0, 20.0, 60.0):
                    for ref in (10.0, 60.0, 110.0):
                        Qg = dict(Q, rsf=rsf, rsa=rsa, ref=ref)
                        b, f = gun_ends(S, Qg, facing, cam)
                        um = f - b
                        L = float(np.linalg.norm(um))
                        if L < 1e-6 or abs(float(um @ ut)) / L < 0.94:
                            continue
                        e = min(np.linalg.norm(b - A) + np.linalg.norm(f - B), np.linalg.norm(b - B) + np.linalg.norm(f - A))
                        out.append((e, Qg))
    out.sort(key=lambda t: t[0])
    return [Q for e, Q in out[:n]]


def line_starts(unit, S, ax, y0, k, facing, Q0, n=3):
    """poses from Q0 with the held gun laid along TS's gun line in frame k (best n)."""
    if Q0.get('ik', 1.0) < 0.5:
        return one_hand_starts(unit, S, ax, y0, k, facing, Q0, n) if Q0.get('gone', 0.0) > 0.5 else []
    line = ts_gun_line(unit, k)
    if line is None:
        return []
    import rc
    A, B = line
    cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
    ut = (B - A) / max(float(np.linalg.norm(B - A)), 1e-6)
    out = []
    grips = [(x, y, z) for x in (0.5, 2.0, 3.5, 5.0) for y in (-2.0, 0.0, 2.0) for z in (-5.0, -2.5, 0.0, 2.5, 4.0)]
    for gy in range(-150, 91, 15):
        for gp in range(-100, 141, 15):
            Q = dict(Q0, gy=float(gy), gp=float(gp))
            b, f = gun_ends(S, Q, facing, cam)
            um = f - b
            if np.linalg.norm(um) < 1e-6:
                continue
            um = um / np.linalg.norm(um)
            if abs(float(um @ ut)) < 0.94:                  # (within 20 degrees on screen, either way round)
                continue
            for g in grips:
                Qg = dict(Q, rgx=g[0], rgy=g[1], rgz=g[2])
                b, f = gun_ends(S, Qg, facing, cam)
                e = min(np.linalg.norm(b - A) + np.linalg.norm(f - B), np.linalg.norm(b - B) + np.linalg.norm(f - A))
                out.append((e, Qg))
    out.sort(key=lambda t: t[0])
    return [Q for e, Q in out[:n]]


# free arms (no rifle): the arms down, forward, the right one raised, both bent
ARM_STARTS = [(0.0, 20.0, 0.0, 20.0), (60.0, 60.0, 60.0, 60.0), (130.0, 40.0, 20.0, 30.0), (30.0, 100.0, 30.0, 100.0)]


def starts_of(Q0, falls=False):
    out = [dict(Q0)]
    if Q0.get('ik', 1.0) > 0.5:
        for gy, gp in RIFLE_STARTS:
            out.append(dict(Q0, gy=gy, gp=gp))
    else:
        for rsf, ref, lsf, lef in ARM_STARTS:
            out.append(dict(Q0, rsf=rsf, ref=ref, lsf=lsf, lef=lef))
    if falls:
        for d in PITCH_STEPS:
            out.append(dict(Q0, pitch=float(np.clip(Q0['pitch'] + d, *ABS['pitch']))))
    return out


def fit_best(unit, S, ax, y0, k, facing, Q0, pulls, iters, win=35.0, sigma=0.1, falls=False, keep=2):
    """fit_one from several starts (the pose before, the rifle held other ways, the body pitched further): the two
    that start best are fitted, the better kept."""
    tgt = F.Target(unit, k, facing)
    sts = starts_of(Q0, falls)
    keys = keys_of(Q0); sc = scale(keys)
    tv = [(w, np.array([t[q] for q in keys])) for w, t in pulls]

    def total(Q):
        x = np.array([Q[q] for q in keys])
        return F.frame_loss(S, Q, tgt, ax, y0) + sum(w * float((((x - t) / sc) ** 2).sum()) for w, t in tv)
    ls = line_starts(unit, S, ax, y0, k, facing, Q0) if GUN_LINE else []
    sts = sorted(sts + ls, key=total)
    kept = sts[:keep]
    if ls:
        bl = min(ls, key=total)
        if not any(bl is q for q in kept):
            kept.append(bl)                 # (the gun along TS's gun is always tried)
    sts = kept
    best = None
    for st in sts:
        r = fit_one(unit, S, ax, y0, k, facing, st, pulls, iters, win, sigma, centre=Q0)
        if best is None or r[1] < best[1]:
            best = r
    return best


def fit_one(unit, S, ax, y0, k, facing, Q0, pulls, iters, win=35.0, sigma=0.1, centre=None):
    """a pose on frame k, starting from Q0 (its window round centre, Q0 if not given), plus sum of
    w * |(Q - target) / scale|^2 for (w, target) in pulls."""
    tgt = F.Target(unit, k, facing)
    C0 = Q0 if centre is None else centre
    keys = keys_of(Q0)
    sc = scale(keys)
    lo = np.array([max(ABS[q][0], min(C0[q], Q0[q]) - WIN.get(q, win)) for q in keys])
    hi = np.array([min(ABS[q][1], max(C0[q], Q0[q]) + WIN.get(q, win)) for q in keys])
    x0 = np.clip(np.array([Q0[q] for q in keys]), lo, hi)
    tv = [(w, np.array([t[q] for q in keys])) for w, t in pulls]

    def unpack(x):
        Q = dict(Q0); Q.update({q: float(v) for q, v in zip(keys, x)})
        return Q

    def f(x):
        l = F.frame_loss(S, unpack(x), tgt, ax, y0)
        for w, t in tv:
            l += w * float((((x - t) / sc) ** 2).sum())
        return l
    best = {}

    def cb(x, fb, it, dt):
        best['x'] = x; best['f'] = fb
    F.cma_fit(f, lo, hi, x0, iters, cb, sigma=sigma, pop=16, seed=1)
    Q = unpack(best['x'])
    return Q, best['f'], F.iou(S, Q, tgt, ax, y0)


def main():
    unit, shape, seq = sys.argv[1:4]
    import infunit; infunit.use(unit)
    facing = int(sys.argv[4])
    iters = int(sys.argv[5])
    sweeps = int(sys.argv[6]) if len(sys.argv) > 6 else 2
    js = json.load(open(shape))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    ax, y0 = js['ax'], js['y0']
    stand = dict(js['Q'])
    if os.path.exists('%s_stand_frames.json' % unit):
        sf = json.load(open('%s_stand_frames.json' % unit))
        if str(facing) in sf:
            stand = dict(stand, **sf[str(facing)]['Q'])
    frames = [k for k, f in SQ.frames_of(unit, seq)]
    idle = seq.startswith('idle')
    out = '%s_%s_frames.json' % (unit, seq)
    res = json.load(open(out)) if os.path.exists(out) else {}
    # (the Medic's case set down or dropped: UNIT_SEQ_case.json (casespot.py) gives its spot on the ground and, frame
    # by frame, how far it is there from his hand)
    cpath = '%s_%s_case.json' % (unit, seq)
    case = json.load(open(cpath)) if os.path.exists(cpath) else None

    def with_case(Q, k):
        if GUN_ONE and k >= GUN_ONE and Q.get('gone', 0.0) < 0.5:
            Q = to_one_hand(S, Q, facing)
        if case is None:
            return Q
        return dict(Q, cfx=case['cfx'], cfy=case['cfy'], cfa=case['cfa'], cft=case.get('cft', 0.0),
                    cfix=float(case['cfix'].get(str(k), 0.0)))
    # 1: frame after frame, each from the one before
    prev = stand
    for i, k in enumerate(frames):
        if str(k) in res:
            prev = dict(stand, **res[str(k)]['Q']); continue
        t0 = time.time()
        Q, fb, iu = fit_best(unit, S, ax, y0, k, facing, with_case(prev, k), [(W_PREV, with_case(prev, k))],
                             int(iters * 0.6), falls=not idle)
        res[str(k)] = dict(Q=Q, f=fb, iou=iu, facing=facing, sweep=0)
        json.dump(res, open(out, 'w'), default=float)
        prev = Q
        print(seq, 'frame', k, 'f %.3f iou %.3f' % (fb, iu), '%.0fs' % (time.time() - t0), flush=True)
    # 2: relax the path: each frame towards the middle of its neighbours (the standing pose before the first and, for
    # an idle, after the last)
    for sw in range(1, sweeps + 1):
        for i, k in enumerate(frames):
            if res[str(k)].get('sweep', 0) >= sw:
                continue
            t0 = time.time()
            Qs = [dict(stand, **res[str(kk)]['Q']) for kk in frames]
            before = with_case(Qs[i - 1] if i > 0 else stand, k)
            after = Qs[i + 1] if i + 1 < len(frames) else (stand if idle else None)
            after = None if after is None else with_case(after, k)
            if after is not None:
                mid = {q: 0.5 * (before[q] + after[q]) for q in before}
                pulls = [(W_MID, mid)]
            else:
                pulls = [(W_PREV, before)]
            if i == 0 or (idle and i == len(frames) - 1):
                pulls.append((W_END, stand))
            Q, fb, iu = fit_one(unit, S, ax, y0, k, facing, with_case(Qs[i], k), pulls, max(iters // 2, 40), win=20.0,
                                sigma=0.06)
            res[str(k)] = dict(Q=Q, f=fb, iou=iu, facing=facing, sweep=sw)
            json.dump(res, open(out, 'w'), default=float)
            print(seq, 'sweep', sw, 'frame', k, 'f %.3f iou %.3f' % (fb, iu), '%.0fs' % (time.time() - t0), flush=True)
    print('done', flush=True)


if __name__ == '__main__':
    main()
