"""
infcycle.py - a looping sequence (the run, the crawl) as one smooth cycle.  Fitted a step at a time, the run's arms and
rifle jumped between steps and snapped back at the loop (Luke: "should be fluid movements and not teleport back to
start position").  Here every joint follows one smooth curve through the cycle: a short Fourier series of the step's
phase (6 steps a cycle), so step 5 runs into step 0 as smoothly as any step into the next.  The two legs follow one
curve half a cycle apart; the body's sideways sway swings the other way on the other stride (odd harmonics only); the
body stays on its spot.  The cycle is fitted to the sequence's frames in all 8 facings together, held near a natural
run (the template below) unless TS's frames say otherwise.

TS's facings don't all show one 3D motion of the rifle (its runner swings the rifle side to side in the south view and
from his left to the front in the others), so a second pass lets each facing's arms and rifle follow their own smooth
loop, held close to the shared one: every facing still loops without a jump.

    python3 infcycle.py UNIT shape.json SEQ out.json iters [start.json]
        shared cycle.  env FREE=ch,ch... (only these fitted), SIGMA, SEED, POP; STEPS_OUT=path writes the steps' poses
        {step: {Q, frames, iou}} (as infcheck and infgif read them)
    python3 infcycle.py UNIT shape.json SEQ out.json iters cycle.json facing F[,F...]
        each facing's own upper-body loop on top of the shared cycle (cycle.json); out.json collects them;
        FRAMES_OUT=path writes every frame's pose {frame: {Q, facing, iou}}
"""
import json, os, sys, time
import numpy as np
import inf as I
import inffit as F
import infseq as SQ

N = 6                     # steps a cycle (the Cyborg Commando's CyborgSequence: 9 - infunit.use sets it)
try:
    import infunit as _IU
    if _IU.CURRENT[0]:
        N = _IU.CYCLE_N.get(_IU.CURRENT[0], 6)
except ImportError:
    pass
LEGS = ('hf', 'kf', 'af', 'ha', 'ht')
# arms swinging free (no rifle to hold): one curve for both, the right arm on it, the left half a cycle on (so the
# right arm swings forward with the left leg); st (twist) mirrored
ARMS = ('sf', 'sa', 'st', 'ef')
# (channel, {harmonic: bound}) - the mean (harmonic 0) between (lo, hi), each harmonic's cos and sin within +-bound
#   legs: one curve for both legs, the right leg's half a cycle on; ht turns the toes out (mirrored)
#   sideways (roll, the spine's roll): odd harmonics only, so the other stride mirrors them
SPEC = {
    'walk': [
        ('hf', {0: (0, 55), 1: 60, 2: 12}), ('kf', {0: (20, 50), 1: 75, 2: 30}), ('af', {0: (-30, 20), 1: 35, 2: 20}),
        ('ha', {0: (-5, 10)}), ('ht', {0: (-15, 25)}),
        ('pitch', {0: (10, 20), 2: 8}), ('roll', {1: 8}), ('yaw', {0: (-25, 25), 1: 14}),
        ('dx', {0: (-3, 3)}), ('dy', {0: (-3, 3)}),
        ('sp', {0: (0, 8)}), ('sy', {0: (-35, 35), 1: 25}), ('sr', {1: 10}),
        ('hp', {0: (-10, 12), 2: 5}), ('hy', {0: (-20, 20), 1: 10}),
        ('gp', {0: (-30, 50), 1: 40, 2: 20}), ('gy', {0: (-110, 20), 1: 60, 2: 25}), ('gr', {0: (-50, 50), 1: 40, 2: 20}),
        ('rgx', {0: (0.8, 4.5), 1: 1.5, 2: 0.8}), ('rgy', {0: (-1.5, 2.5), 1: 1.5, 2: 0.8}),
        ('rgz', {0: (-5.5, 0.0), 1: 1.5, 2: 0.8}), ('lfx', {0: (1.5, 4.5)}),
        ('lsw', {0: (-50, 50), 1: 30}), ('rsw', {0: (-50, 50), 1: 30})],
    # the crawl, a calm low crawl (Luke: the free fits "flailing around, not crawling"): lying flat and steady on his
    # front (the pelvis pitched 82-95 degrees, no rocking), the chest up on the elbows, the head up; a knee drawn up in
    # turn, the rifle worked forward a little each stride; every joint on one smooth swing a cycle (no second
    # harmonics), in a narrow range round that crawl
    'crawl': [
        ('hf', {0: (-15, 25), 1: 18}), ('kf', {0: (5, 55), 1: 30}), ('af', {0: (0, 50)}), ('ha', {0: (0, 30), 1: 12}),
        ('ht', {0: (-20, 20)}),
        ('pitch', {0: (82, 95)}), ('roll', {1: 4}), ('yaw', {0: (-6, 6)}), ('dx', {0: (-6, 6)}), ('dy', {0: (-4, 14)}),
        ('sp', {0: (-25, 0)}), ('sy', {0: (-8, 8), 1: 6}), ('sr', {1: 4}), ('hp', {0: (-95, -40)}), ('hy', {0: (-10, 10)}),
        ('gp', {0: (60, 130), 1: 10}), ('gy', {0: (-30, 30), 1: 6}), ('gr', {0: (-30, 30)}),
        ('rgx', {0: (0.0, 4.5), 1: 1.0}), ('rgy', {0: (-2.0, 2.5)}), ('rgz', {0: (-3.0, 4.0), 1: 0.8}),
        ('lfx', {0: (1.5, 4.5)}), ('lsw', {0: (-50, 50)}), ('rsw', {0: (-50, 50)})],
}
# each facing's own loop: these channels, within these bounds of the shared cycle
FACE = {'walk': [('gp', {0: 30, 1: 30, 2: 15}), ('gy', {0: 45, 1: 45, 2: 20}), ('gr', {0: 30, 1: 30, 2: 15}),
                 ('rgx', {0: 1.2, 1: 1.0, 2: 0.6}), ('rgy', {0: 1.2, 1: 1.0, 2: 0.6}), ('rgz', {0: 1.2, 1: 1.0, 2: 0.6}),
                 ('lfx', {0: 1.0}), ('lsw', {0: 30, 1: 20}), ('rsw', {0: 30, 1: 20}), ('sy', {0: 15, 1: 12}),
                 ('hy', {0: 15, 1: 12})]}
# (the crawl: each facing only its own head turn, shoulder set and rifle angle, held through the loop)
FACE['crawl'] = [('sy', {0: 6}), ('hy', {0: 10}), ('gp', {0: 10}), ('gy', {0: 10})]
# the joints' own limits, whatever the curves add up to
CLAMP = dict(kf=(0.0, 155.0), af=(-50.0, 60.0), rgx=(0.3, 5.5), rgy=(-2.5, 3.5), rgz=(-6.5, 1.0), lfx=(0.8, 5.5),
             ef=(0.0, 150.0), lef=(0.0, 150.0), ref=(0.0, 150.0), lkf=(0.0, 155.0), rkf=(0.0, 155.0))
DIST = ('dx', 'dy', 'rgx', 'rgy', 'rgz', 'lfx')
W_PEN = 0.02              # the hands off the rifle, the rifle or elbows through the body
W_PRIOR = 0.0015          # the pull towards the natural run, per (30 degrees or 1.5 px) squared of each coefficient
W_FACE = float(os.environ.get('W_FACE', 0.006))   # the pull of a facing's own loop towards the shared one
# a real stride: each thigh swings forward and back once a cycle, the knee bends with it (TS's side views can't tell
# the legs apart, so without this the fit lets both legs move together, a hop): the first harmonic at least this big
# (the run's knee swings at least 45 degrees about a bend of at most 50: it straightens through each stride - TS's
# front leg lands straight and its back leg pushes off straight; left freer, the fits kept every knee bent the whole
# way round: Luke, of the Engineer, "his knee is always bent")
MIN_AMP = {'walk': {'hf': 18.0, 'kf': 45.0}, 'crawl': {'hf': 8.0, 'kf': 15.0}}
W_MIN_AMP = 0.002         # per degree squared short of it


def layout(spec):
    """the coefficients: (channel, harmonic, 0 cos / 1 sin, lo, hi)."""
    out = []
    for ch, hs in spec:
        for n, b in sorted(hs.items()):
            if n == 0:
                out.append((ch, 0, 0, float(b[0]), float(b[1])) if isinstance(b, tuple) else (ch, 0, 0, -b, b))
            else:
                out += [(ch, n, 0, -b, b), (ch, n, 1, -b, b)]
    return out


def basis(n, k, phi):
    return 1.0 if n == 0 else (np.cos(n * phi) if k == 0 else np.sin(n * phi))


def channel(lay, x, ch, phi):
    return float(sum(v * basis(n, k, phi) for (c, n, k, lo, hi), v in zip(lay, x) if c == ch))


def channels(lay):
    seen = []
    for c, n, k, lo, hi in lay:
        if c not in seen:
            seen.append(c)
    return seen


def scale_of(lay):
    return np.array([1.5 if c in DIST else 30.0 for c, n, k, lo, hi in lay])


# the head's pitch measured from level, not from the chest: the runner looks where he runs, his visor showing (TS's
# south view), however far he leans
HEAD_LEVEL = ('walk',)


def step_pose(Qbase, lay, x, s, face=None, seq=None):
    """the pose of step s (0..N-1) from the coefficients x (plus a facing's own (lay, x) on top)."""
    phi = 2 * np.pi * s / N
    Q = dict(Qbase)
    # (a sequence's own fixed settings: the crippled Cyborg crawls without its legs)
    import infunit
    Q.update(SEQ_BASE.get((infunit.CURRENT[0], seq), {}))
    for ch in channels(lay):
        lo, hi = CLAMP.get(ch, (-1e9, 1e9))

        def val(p):
            v = channel(lay, x, ch, p)
            if face is not None:
                v += channel(face[0], face[1], ch, p)
            return float(np.clip(v, lo, hi))
        if ch in LEGS:
            vl, vr = val(phi), val(phi + np.pi)
            if ch == 'ht':
                Q['lht'], Q['rht'] = -vl, vr
            else:
                Q['l' + ch], Q['r' + ch] = vl, vr
        elif ch in ARMS:
            vr, vl = val(phi), val(phi + np.pi)
            if ch == 'st':
                Q['lst'], Q['rst'] = -vl, vr
            else:
                Q['l' + ch], Q['r' + ch] = vl, vr
        else:
            Q[ch] = val(phi)
    if seq in HEAD_LEVEL:
        Q['hp'] = Q['hp'] - Q['pitch'] - Q['sp']
    return Q


def fit_keys(lay, keys, x=None):
    """coefficients whose curves pass closest to per-step values keys {channel: [N values]} (the left leg's for legs)."""
    x = np.array([0.5 * (lo + hi) if n == 0 else 0.0 for c, n, k, lo, hi in lay]) if x is None else np.array(x, float)
    for ch, vals in keys.items():
        idx = [i for i, (c, n, k, lo, hi) in enumerate(lay) if c == ch]
        if not idx:
            continue
        # (each channel's own steps: a 6-step start serves a 9-step cycle too)
        phis = 2 * np.pi * np.arange(len(vals)) / len(vals)
        A = np.array([[basis(lay[i][1], lay[i][2], p) for i in idx] for p in phis])
        sol = np.linalg.lstsq(A, np.asarray(vals, float), rcond=None)[0]
        for i, v in zip(idx, sol):
            x[i] = np.clip(v, lay[i][3], lay[i][4])
    return x


def ellip_depth(p, c, R, r):
    q = (R.T @ (p - c)) / r
    return max(0.0, 1.0 - float(np.linalg.norm(q)))


def pose_penalty(S, Q):
    """the hands off the rifle (a grip out of the arm's reach) and the rifle or the elbows through the body (the same
    in every facing); free arms (no rifle): the elbows and hands through the body."""
    P = I.Pose(S, Q, 0.0)
    pen = 0.0
    held = S.get('rifle', 1) > 0.5 and Q.get('ik', 1.0) > 0.5
    P0, B = P.pelvis
    C0, RC = P.chest
    Hc, RH = P.head
    cr = np.asarray(S['cr']); ar = np.asarray(S['ar']); hr = np.asarray(S['hr'])
    body = [(C0 + RC @ np.array([0, 0, -cr[2] * 0.55]), RC, cr * 0.8), (P0 + (C0 - P0) * 0.45, RC, ar * 0.8),
            (Hc, RH, hr * 0.85)]
    if held:
        G0, RG = P.rifle
        for side in ('l', 'r'):
            Sh = P.arms[side][0]
            T = G0 if side == 'r' else G0 + RG @ np.array([Q['lfx'], 0, -0.25 - S['rh'] * 0.5])
            d = np.linalg.norm(T - Sh) - S['rh'] * 0.6 - (S['lu'] + S['lf'])
            pen += max(d, 0.0) ** 2
        back = G0 - RG[:, 0] * S['gg']
        if S.get('kit') == 'e3':
            back = back + I.launcher_lift(S, RG)          # (the launcher's tube on his shoulder, above the hands)
        for t in np.linspace(0.0, 1.0, 10):
            p = back + RG[:, 0] * S['gl'] * t
            pen += sum(ellip_depth(p, c, R, r) for c, R, r in body)
    for side in ('l', 'r'):
        E = P.arms[side][2]
        pen += sum(ellip_depth(E, c, R, r) for c, R, r in body[:2])
        if not held:
            W = P.arms[side][4]
            pen += sum(ellip_depth(W, c, R, r) for c, R, r in body)
    return pen


def amp_short(lay, x, mins):
    """how far each channel's first harmonic falls short of its least amplitude (squared, summed)."""
    pen = 0.0
    for ch, amin in mins.items():
        ab = [v for (c, n, k, lo, hi), v in zip(lay, x) if c == ch and n == 1]
        pen += max(0.0, amin - float(np.hypot(*ab))) ** 2 if len(ab) == 2 else 0.0
    return pen


def facing_parts(S, Q):
    """the soldier's grounded parts facing east with no offset (rotated and moved into each facing after)."""
    Q0 = dict(Q, dx=0.0, dy=0.0)
    return I.grounded(S, Q0, 0.0)[0]


def turned(parts, f, Q):
    R = I.Rz(I.facing_angle(f))
    t = (Q['dx'], Q['dy'], 0.0)
    return [p.moved(R, t) for p in parts]


def phase_of(unit, seq):
    """each facing's step offset: TS draws some facings' loops starting a step or two on (E2's run facing west), so
    the cycle's step s is that facing's TS step (s - offset) (UNIT_SEQ_phase.json, from phase.py; none: all 0)."""
    path = '%s_%s_phase.json' % (unit, seq)
    if os.path.exists(path):
        return [int(v) for v in json.load(open(path))]
    return [0] * 8


class Problem:
    """the sequence's frames (all 8 facings, or some) and the shared cycle's layout; face: a facing's own layout."""

    def __init__(self, unit, S, ax, y0, seq, Qbase, lay, facings=range(8), face_lay=None, shared=None):
        self.unit, self.S, self.ax, self.y0, self.Qbase, self.lay = unit, S, ax, y0, Qbase, lay
        self.seq = seq
        self.phase = phase_of(unit, seq)
        ts = SQ.frames_of(unit, seq)
        # the cycle's step s against each facing's TS frame of step s - offset
        self.steps = [(s, [ts[(s - self.phase[f]) % len(ts)][1][f] for f in range(8)]) for s, frames in ts]
        self.facings = list(facings)
        self.tg = {(s, f): F.Target(unit, frames[f], f) for s, frames in self.steps for f in self.facings}
        self.sc = scale_of(lay)
        self.x_prior = None
        self.face_lay, self.shared = face_lay, shared
        if face_lay is not None:
            self.face_sc = scale_of(face_lay)

    def poses(self, x, face_x=None):
        if self.face_lay is None:
            return {s: step_pose(self.Qbase, self.lay, x, s, seq=self.seq) for s, frames in self.steps}
        return {s: step_pose(self.Qbase, self.lay, self.shared, s, (self.face_lay, face_x), self.seq)
                for s, frames in self.steps}

    def loss(self, x):
        if self.face_lay is None:
            Qs = self.poses(x)
            reg = W_PRIOR * float((((np.asarray(x) - self.x_prior) / self.sc) ** 2).sum()) if self.x_prior is not None \
                else 0.0
            reg += W_MIN_AMP * amp_short(self.lay, x, min_amp_of(self.unit, self.seq))
        else:
            Qs = self.poses(None, x)
            reg = W_FACE * float(((np.asarray(x) / self.face_sc) ** 2).sum())
        tot = 0.0
        for s, frames in self.steps:
            Q = Qs[s]
            base = facing_parts(self.S, Q)
            pen = W_PEN * pose_penalty(self.S, Q)
            for f in self.facings:
                tot += F.parts_loss(turned(base, f, Q), self.tg[(s, f)], self.ax, self.y0) + pen
        return tot / len(self.tg) + reg

    def ious(self, x, face_x=None):
        Qs = self.poses(x, face_x)
        out = {}
        for s, frames in self.steps:
            base = facing_parts(self.S, Qs[s])
            for f in self.facings:
                out[(s, f)] = F.parts_iou(turned(base, f, Qs[s]), self.tg[(s, f)], self.ax, self.y0)
        return out


_P = None


def _loss(x):
    return _P.loss(x)


def fit(P, x0, lay, free, iters, sigma=0.1, pop=20, seed=1, out=None, log_every=10, workers=2):
    """CMA-ES over the free coefficients (scaled to their ranges), the population scored on both CPUs."""
    import cma
    from multiprocessing import Pool
    global _P
    _P = P
    fi = np.array([i for i, (c, n, k, lo, hi) in enumerate(lay) if c in free])
    lo = np.array([lay[i][3] for i in fi], float); hi = np.array([lay[i][4] for i in fi], float)
    span = hi - lo
    z0 = np.clip((x0[fi] - lo) / span, 1e-3, 1 - 1e-3)

    def full(z):
        x = np.array(x0, float)
        x[fi] = lo + np.clip(z, 0, 1) * span
        return x
    es = cma.CMAEvolutionStrategy(z0, sigma, {'bounds': [0, 1], 'popsize': pop, 'maxiter': iters, 'seed': seed,
                                              'verbose': -9})
    t0 = time.time(); it = 0
    pool = Pool(workers) if workers > 1 else None
    try:
        while not es.stop():
            Z = es.ask()
            xs = [full(z) for z in Z]
            fs = pool.map(_loss, xs) if pool else [_loss(x) for x in xs]
            es.tell(Z, fs); it += 1
            if it % log_every == 0 or es.stop():
                xb = full(es.result.xbest)
                print('it', it, 'best %.4f' % es.result.fbest, '%.0fs' % (time.time() - t0), flush=True)
                if out:
                    json.dump(dict(coef=coef_list(lay, xb), f=float(es.result.fbest)), open(out, 'w'))
    finally:
        if pool:
            pool.close(); pool.join()
    return full(es.result.xbest), float(es.result.fbest)


def coef_list(lay, x):
    return [[c, n, k, float(v)] for (c, n, k, a, b), v in zip(lay, x)]


def load_coef(path, lay, x=None, key='coef'):
    js = json.load(open(path))
    d = {(c, n, k): v for c, n, k, v in js[key]}
    x = np.zeros(len(lay)) if x is None else np.array(x, float)
    for i, (c, n, k, lo, hi) in enumerate(lay):
        if (c, n, k) in d:
            x[i] = d[(c, n, k)]
    return x


# the natural run the fit starts from and is held near, read from TS's side views: the runner leans forward ~22
# degrees (TS's south view stands 2-5 px shorter than its standing soldier: the lean towards the camera; its east and
# west views 1-2 px) with his head up, his visor showing.  A leg pushes off behind (step 0), lifts with its shin level
# behind (1), kicks its heel up (2), comes through with the knee forward (3) and stands straight under him (4-5) while
# the other leg does the same half a cycle on.  The rifle across the body to his left on one stride, to the front on
# the other (TS's facings, steps 0-2 and 3-5), on one smooth swing.
def walk_keys():
    thigh = np.array([-25.0, -35.0, -10.0, 20.0, 0.0, -5.0])
    sw = np.cos(2 * np.pi * (np.arange(N) - 1) / N)
    # TS's east view: the torso leans ~32 degrees at the push-offs (steps 0, 3), ~22 between
    pitch = 17.0 + 7.0 * np.cos(2 * 2 * np.pi * np.arange(N) / N)
    return dict(hf=list(thigh + pitch), kf=[10.0, 95.0, 130.0, 60.0, 10.0, 10.0], af=[-25.0, -10.0, 10.0, 10.0, 0.0, -15.0],
                ha=[2.0] * N, ht=[5.0] * N, pitch=list(pitch), roll=[0.0] * N, yaw=[0.0] * N, sp=[5.0] * N,
                sy=[0.0] * N, sr=[0.0] * N, hp=[2.0] * N, hy=[0.0] * N,
                gy=list(-45.0 - 45.0 * sw), gp=list(10.0 + 15.0 * sw), gr=[0.0] * N,
                rgx=[2.4] * N, rgy=[0.4] * N, rgz=[-3.0] * N, lfx=[3.0] * N, lsw=[0.0] * N, rsw=[0.0] * N)


# the crawl's start: TS's prone soldier (the crawl's first frame is the prone pose) lies with his head up, the rifle
# held out in front; a knee drawn up in turn, the arms pushing the rifle forward on alternate strides
def crawl_keys():
    c = np.cos(2 * np.pi * np.arange(N) / N)
    # lying flat, the chest up on the elbows; the rifle aimed ahead: with the chest pitched forward ~75 degrees its
    # muzzle points ~100 degrees 'up' the chest
    return dict(hf=list(10.0 + 12.0 * c), kf=list(30.0 + 22.0 * c), af=[30.0] * N, ha=list(15.0 + 8.0 * c),
                ht=[0.0] * N, pitch=[88.0] * N, roll=[0.0] * N, yaw=[0.0] * N, sp=[-12.0] * N, sy=[0.0] * N,
                sr=[0.0] * N, hp=[-70.0] * N, hy=[0.0] * N, gp=[100.0] * N, gy=[0.0] * N, gr=[0.0] * N,
                rgx=[1.5] * N, rgy=[0.4] * N, rgz=list(1.0 + 0.5 * c), lfx=[3.0] * N, lsw=[0.0] * N, rsw=[0.0] * N,
                dx=[2.0] * N, dy=[6.0] * N)


KEYS = dict(walk=walk_keys, crawl=crawl_keys)


# ---------------------------------------------------------------------------------------------- the Disc Thrower
# no rifle: his arms swing as he runs and crawls, and his fire is a throw (TS's 6 steps a facing: the arm raised,
# drawn back, brought over, thrown forward, followed through, back - the disc leaves on the last step), looped so one
# throw runs into the next
_BODY_WALK = [('pitch', {0: (10, 20), 2: 8}), ('roll', {1: 8}), ('yaw', {0: (-25, 25), 1: 14}), ('dx', {0: (-3, 3)}),
              ('dy', {0: (-3, 3)}), ('sp', {0: (0, 8)}), ('sy', {0: (-35, 35), 1: 25}), ('sr', {1: 10}),
              ('hp', {0: (-10, 12), 2: 5}), ('hy', {0: (-20, 20), 1: 10})]
_LEGS_WALK = [('hf', {0: (0, 55), 1: 60, 2: 12}), ('kf', {0: (20, 95), 1: 70, 2: 40}),
              ('af', {0: (-30, 20), 1: 35, 2: 20}), ('ha', {0: (-5, 10)}), ('ht', {0: (-15, 25)})]
# E2's run (TS's side views): a sprint, the trailing leg thrown far back (straight back from the hip at the push-off,
# the shin kicked up level behind it the step after), the body nearly upright: the thigh may swing well behind
_LEGS_RUN_E2 = [('hf', {0: (-30, 50), 1: 75, 2: 25}), ('kf', {0: (20, 50), 1: 75, 2: 30}),
                ('af', {0: (-30, 20), 1: 35, 2: 20}), ('ha', {0: (-5, 10)}), ('ht', {0: (-15, 25)})]
_BODY_RUN_E2 = [('pitch', {0: (0, 20), 2: 8})] + _BODY_WALK[1:]
_ONE_ARM = lambda side, sf, sa, ef, st: [(side + 'sf', sf), (side + 'sa', sa), (side + 'ef', ef), (side + 'st', st)]
UNIT_SPEC = {
    ('e2', 'walk'): _LEGS_RUN_E2 + _BODY_RUN_E2 + [('sf', {0: (-20, 40), 1: 55, 2: 15}), ('sa', {0: (0, 40), 1: 10}),
                                              ('st', {0: (-30, 30)}), ('ef', {0: (10, 115), 1: 40, 2: 20})],
    # (E2's crawl: the calm low crawl, the arms reaching ahead in turn: the Engineer's, set below)
    ('e2', 'fire'): (
        [('pitch', {0: (-10, 25), 1: 10, 2: 5}), ('roll', {0: (-8, 8), 1: 5}), ('yaw', {0: (-30, 30), 1: 30, 2: 10}),
         ('dx', {0: (-3, 3)}), ('dy', {0: (-3, 3)}), ('sp', {0: (-10, 25), 1: 12, 2: 6}),
         ('sy', {0: (-50, 50), 1: 75, 2: 30}), ('sr', {0: (-15, 15), 1: 10}), ('hp', {0: (-20, 15), 1: 8}),
         ('hy', {0: (-40, 40), 1: 40, 2: 15})] +
        _ONE_ARM('r', {0: (-40, 150), 1: 90, 2: 45}, {0: (-10, 80), 1: 60, 2: 30}, {0: (0, 140), 1: 70, 2: 35},
                 {0: (-50, 50), 1: 30}) +
        _ONE_ARM('l', {0: (-40, 100), 1: 50, 2: 25}, {0: (-10, 60), 1: 50, 2: 20}, {0: (0, 130), 1: 50, 2: 20},
                 {0: (-40, 40)}) +
        [('lhf', {0: (-30, 50), 1: 10}), ('lkf', {0: (0, 60), 1: 10}), ('rhf', {0: (-40, 40), 1: 10}),
         ('rkf', {0: (0, 60), 1: 10}), ('laf', {0: (-30, 30)}), ('raf', {0: (-30, 30)}), ('lha', {0: (-5, 20)}),
         ('rha', {0: (-5, 20)})]),
    ('e2', 'prone_fire'): (
        [('pitch', {0: (55, 100)}), ('roll', {0: (-15, 15), 1: 6}), ('yaw', {0: (-25, 25), 1: 8}),
         ('dx', {0: (-6, 6)}), ('dy', {0: (-4, 10)}), ('sp', {0: (-40, 15), 1: 8}), ('sy', {0: (-35, 35), 1: 15}),
         ('sr', {0: (-15, 15), 1: 8}), ('hp', {0: (-85, 0)}), ('hy', {0: (-30, 30), 1: 10})] +
        _ONE_ARM('r', {0: (0, 240), 1: 90, 2: 40}, {0: (-10, 90), 1: 40, 2: 20}, {0: (0, 140), 1: 60, 2: 30},
                 {0: (-50, 50), 1: 30}) +
        _ONE_ARM('l', {0: (40, 180), 1: 20}, {0: (-10, 60)}, {0: (10, 140), 1: 20}, {0: (-40, 40)}) +
        [('lhf', {0: (-25, 45)}), ('lkf', {0: (0, 110)}), ('rhf', {0: (-25, 45)}), ('rkf', {0: (0, 110)}),
         ('laf', {0: (0, 60)}), ('raf', {0: (0, 60)}), ('lha', {0: (-5, 40)}), ('rha', {0: (-5, 40)})]),
}
# the Engineer: the run and the crawl with each arm on its own curve (the right one carries the toolbox, the left
# swings); his legs and body as the soldiers' run (TS's side views: hunched forward)
# (the run is a sprint, as E2's: TS's side views, frames 20-25 and 44-49, throw the trailing leg back level behind the
# hip, one leg then the other; with the soldiers' legs the fit kept his knees bent and his strides short)
# (the Engineer's legs: the knee straightens through each stride - TS draws his front leg straight as it lands and the
# back one straight behind at the push-off; left free, the fit kept both knees bent the whole way round: "his knee
# is always bent")
_LEGS_RUN_ENG = [('hf', {0: (-30, 50), 1: 75, 2: 25}), ('kf', {0: (20, 50), 1: 75, 2: 30}),
                 ('af', {0: (-30, 20), 1: 35, 2: 20}), ('ha', {0: (-5, 10)}), ('ht', {0: (-15, 25)})]
UNIT_SPEC[('eng', 'walk')] = (_LEGS_RUN_ENG + _BODY_RUN_E2 +
                              _ONE_ARM('r', {0: (-30, 50), 1: 30, 2: 10}, {0: (0, 40), 1: 10}, {0: (0, 90), 1: 25},
                                       {0: (-30, 30)}) +
                              _ONE_ARM('l', {0: (-30, 60), 1: 55, 2: 15}, {0: (0, 40), 1: 10},
                                       {0: (10, 115), 1: 40, 2: 20}, {0: (-30, 30)}))
# the Engineer's crawl, a calm low crawl (the first fits, free in every joint, matched TS's pixels with his arms
# waving overhead and his body rolling: "flailing around, not crawling"): lying flat and steady on his front, the
# chest up on the forearms, the head up; the arms reaching ahead in turn, the toolbox in the right hand going with it;
# a knee drawn up in turn on the other side; every joint on one smooth swing a cycle (no second harmonics), in a
# narrow range round that crawl, and each facing only its own head turn and shoulder set
UNIT_SPEC[('e2', 'crawl')] = UNIT_SPEC[('eng', 'crawl')] = [
    ('hf', {0: (-15, 25), 1: 18}), ('kf', {0: (5, 55), 1: 30}), ('af', {0: (0, 50)}), ('ha', {0: (0, 30), 1: 12}),
    ('ht', {0: (-20, 20)}),
    ('pitch', {0: (82, 95)}), ('roll', {1: 4}), ('yaw', {0: (-6, 6)}), ('dx', {0: (-6, 6)}), ('dy', {0: (-4, 14)}),
    ('sp', {0: (-25, 0)}), ('sy', {0: (-8, 8), 1: 6}), ('sr', {1: 4}), ('hp', {0: (-95, -40)}), ('hy', {0: (-10, 10)}),
    ('sf', {0: (140, 180), 1: 15}), ('sa', {0: (5, 40)}), ('st', {0: (-60, 10)}), ('ef', {0: (0, 70), 1: 25})]
UNIT_FACE = {
    ('eng', 'crawl'): [('sy', {0: 6}), ('hy', {0: 10})],
    ('e2', 'crawl'): [('sy', {0: 6}), ('hy', {0: 10})],
    ('e2', 'walk'): [('sf', {0: 20, 1: 20, 2: 10}), ('sa', {0: 15}), ('ef', {0: 30, 1: 20}), ('sy', {0: 15, 1: 12}),
                     ('hy', {0: 15, 1: 12})],
    ('e2', 'fire'): [('rsf', {0: 30, 1: 30, 2: 15}), ('rsa', {0: 25, 1: 20}), ('ref', {0: 30, 1: 25}),
                     ('lsf', {0: 25, 1: 15}), ('lef', {0: 25, 1: 15}), ('sy', {0: 20, 1: 15}), ('hy', {0: 15, 1: 12})],
    ('e2', 'prone_fire'): [('rsf', {0: 30, 1: 30, 2: 15}), ('rsa', {0: 25, 1: 20}), ('ref', {0: 30, 1: 25}),
                           ('lsf', {0: 25}), ('lef', {0: 25}), ('sy', {0: 15}), ('hy', {0: 15})],
}
UNIT_MIN_AMP = {('e2', 'walk'): {'hf': 18.0, 'kf': 45.0, 'sf': 15.0}, ('e2', 'crawl'): {'hf': 8.0, 'kf': 15.0, 'sf': 8.0},
                ('e2', 'fire'): {}, ('e2', 'prone_fire'): {}, ('eng', 'walk'): {'hf': 18.0, 'kf': 45.0},
                ('eng', 'crawl'): {'hf': 8.0, 'kf': 15.0, 'sf': 8.0}}


def walk_keys_e2():
    k = walk_keys()
    for ch in ('gy', 'gp', 'gr', 'rgx', 'rgy', 'rgz', 'lfx', 'lsw', 'rsw'):
        k.pop(ch)
    # TS's side views (frames 20-25, 44-49), the left leg: kicked up behind (the shin level), passing under him, out in
    # front, planted, under him again, thrown straight back (TS draws it level behind the hip at steps 2 and 5, one
    # leg then the other); the thigh's angle from straight down (forward +), the knee's bend
    thigh = np.array([-30.0, 0.0, 35.0, 20.0, 0.0, -50.0])
    knee = [100.0, 90.0, 30.0, 20.0, 20.0, 15.0]
    pitch = np.full(N, 12.0)
    if os.environ.get('RUN_FLIP'):                      # the other leg first
        thigh = np.roll(thigh, 3); knee = list(np.roll(knee, 3))
    # the right arm swings forward as the left leg does (and the left arm with the right leg), the elbows bent
    return dict(k, hf=list(thigh + pitch), kf=knee, pitch=list(pitch), sf=list(15.0 + 0.6 * thigh), sa=[12.0] * N,
                st=[0.0] * N, ef=[70.0] * N)


def crawl_keys_e2():
    # the low crawl, the arms reaching ahead in turn (the Engineer's)
    return crawl_keys_eng()


def fire_keys_e2():
    # TS's throw (facing west, frames 176-181), right-handed: the disc raised by the head; the wind-up, his back turned
    # to the target's side (the chest turned ~90 degrees right: TS shows his back), both arms out level; the right arm
    # straight up; out forward at the release; the follow-through, the chest turned ~90 degrees left (TS shows his
    # front), the arms drawn in; back to the ready stance.  The head keeps looking at the target as the chest turns
    sy = np.array([-10.0, 70.0, 20.0, 0.0, -60.0, -10.0])
    return dict(pitch=[0.0, 0.0, 5.0, 10.0, 8.0, 2.0], roll=[0.0] * N, yaw=[0.0, 15.0, 5.0, 0.0, -15.0, 0.0],
                sp=[0.0, 0.0, 5.0, 12.0, 10.0, 3.0], sy=list(sy), sr=[0.0] * N,
                hp=[0.0] * N, hy=list(-0.5 * sy),
                rsf=[150.0, 0.0, 170.0, 90.0, 40.0, 10.0], rsa=[30.0, 85.0, 20.0, 15.0, 20.0, 10.0],
                ref=[120.0, 10.0, 20.0, 10.0, 90.0, 30.0], rst=[0.0] * N,
                lsf=[20.0, 0.0, 30.0, 40.0, 40.0, 15.0], lsa=[15.0, 85.0, 20.0, 20.0, 20.0, 10.0],
                lef=[40.0, 10.0, 40.0, 60.0, 90.0, 30.0], lst=[0.0] * N,
                lhf=[20.0] * N, lkf=[10.0] * N, rhf=[-15.0] * N, rkf=[5.0] * N, laf=[0.0] * N, raf=[0.0] * N,
                lha=[6.0] * N, rha=[6.0] * N)


def prone_fire_keys_e2():
    # lying on his front, the chest up: TS's prone throw (facing west, frames 224-229) draws the right arm along the
    # ground ahead, raised behind the head, straight up, over the head and forward, down ahead again
    return dict(pitch=[85.0] * N, roll=[0.0] * N, yaw=[0.0] * N, sp=[-15.0] * N, sy=[0.0] * N, sr=[0.0] * N,
                hp=[-60.0] * N, hy=[0.0] * N,
                rsf=[150.0, 160.0, 220.0, 260.0, 200.0, 160.0], rsa=[20.0, 20.0, 30.0, 30.0, 20.0, 20.0],
                ref=[80.0, 80.0, 60.0, 20.0, 10.0, 40.0], rst=[0.0] * N,
                lsf=[140.0] * N, lsa=[20.0] * N, lef=[80.0] * N, lst=[0.0] * N,
                lhf=[0.0] * N, lkf=[20.0] * N, rhf=[0.0] * N, rkf=[20.0] * N, laf=[40.0] * N, raf=[40.0] * N,
                lha=[12.0] * N, rha=[12.0] * N, dx=[2.0] * N, dy=[6.0] * N)


def walk_keys_eng():
    # the soldiers' run legs and lean; the toolbox hanging in his right hand, the left arm swinging against the legs
    k = walk_keys()
    for ch in ('gy', 'gp', 'gr', 'rgx', 'rgy', 'rgz', 'lfx', 'lsw', 'rsw'):
        k.pop(ch)
    thigh = np.array([-25.0, -35.0, -10.0, 20.0, 0.0, -5.0])
    return dict(k, rsf=[5.0] * N, rsa=[12.0] * N, rst=[0.0] * N, ref=[10.0] * N,
                lsf=list(10.0 - np.roll(thigh, 3)), lsa=[12.0] * N, lst=[0.0] * N, lef=[70.0] * N)


def walk_keys_eng_sprint():
    # E2's sprint legs and lean (TS's Engineer runs the same way: frames 20-25, 44-49); the right arm carries the toolbox
    # with a short swing, the left arm swings against the right leg
    k = walk_keys_e2()
    for ch in ('sf', 'sa', 'st', 'ef'):
        k.pop(ch)
    thigh = np.array(k['hf']) - np.array(k['pitch'])
    return dict(k, rsf=list(5.0 + 0.3 * thigh), rsa=[12.0] * N, rst=[0.0] * N, ref=[10.0] * N,
                lsf=list(15.0 + 0.6 * np.roll(thigh, 3)), lsa=[12.0] * N, lst=[0.0] * N, lef=[70.0] * N)


def crawl_keys_eng():
    # the low crawl: flat on his front, the chest up on the forearms, the head up; the right arm reaching ahead as the
    # left knee draws up (step 0), then the other pair (the arms' and legs' curves half a cycle apart per side)
    c = np.cos(2 * np.pi * np.arange(N) / N)
    return dict(hf=list(10.0 + 12.0 * c), kf=list(30.0 + 22.0 * c), af=[30.0] * N, ha=list(15.0 + 8.0 * c),
                ht=[0.0] * N, pitch=[88.0] * N, roll=[0.0] * N, yaw=[0.0] * N, dx=[2.0] * N, dy=[6.0] * N,
                sp=[-12.0] * N, sy=[0.0] * N, sr=[0.0] * N, hp=[-70.0] * N, hy=[0.0] * N,
                sf=list(165.0 + 12.0 * c), sa=[20.0] * N, st=[-30.0] * N, ef=list(25.0 - 15.0 * c))


# the Medic carries his case as the Engineer his toolbox: the same run and crawl
for _k in ('walk', 'crawl'):
    UNIT_SPEC[('medic', _k)] = UNIT_SPEC[('eng', _k)]
UNIT_FACE[('medic', 'crawl')] = UNIT_FACE[('eng', 'crawl')]
UNIT_MIN_AMP[('medic', 'walk')] = UNIT_MIN_AMP[('eng', 'walk')]
UNIT_MIN_AMP[('medic', 'crawl')] = UNIT_MIN_AMP[('eng', 'crawl')]
UNIT_KEYS = {('e2', 'walk'): walk_keys_e2, ('e2', 'crawl'): crawl_keys_e2, ('e2', 'fire'): fire_keys_e2,
             ('e2', 'prone_fire'): prone_fire_keys_e2, ('eng', 'walk'): walk_keys_eng_sprint,
             ('eng', 'crawl'): crawl_keys_eng, ('medic', 'walk'): walk_keys_eng_sprint, ('medic', 'crawl'): crawl_keys_eng}


def spec_of(unit, seq):
    return UNIT_SPEC.get((unit, seq), SPEC.get(seq))


def face_of(unit, seq):
    return UNIT_FACE.get((unit, seq), FACE.get(seq))


def keys_fn(unit, seq):
    return UNIT_KEYS.get((unit, seq), KEYS.get(seq))


def min_amp_of(unit, seq):
    return UNIT_MIN_AMP.get((unit, seq), MIN_AMP.get(seq, {}))


def load_shape(shape):
    js = json.load(open(shape))
    S = dict(F.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    return js, S


def start_coef(js, seq, lay, unit='e1'):
    # (the start curves are written for 6 steps: fit_keys spreads them over the cycle whatever its length)
    global N
    n0, N = N, 6
    try:
        keys = keys_fn(unit, seq)()
    finally:
        N = n0
    x0 = fit_keys(lay, keys)
    for i, l in enumerate(lay):
        if l[0] in ('dx', 'dy') and l[1] == 0 and l[0] not in keys:
            x0[i] = js['Q'][l[0]]
    return x0


def write_steps(P, x, path, ious=None):
    Qs = P.poses(x)
    res = {}
    for s, frames in P.steps:
        r = dict(Q=Qs[s], frames=frames)
        if ious is not None:
            r['iou'] = [ious[(s, f)] for f in range(len(frames))]
        res[str(s)] = r
    json.dump(res, open(path, 'w'), default=float)


# ---------------------------------------------------------------------------------------------- Nod: the Rocket Infantry
# TS's E3 runs with the launcher steady on his right shoulder, level and pointing ahead (frames 20-25, 32-37): the
# soldiers' run legs and lean, the launcher held as he stands (no swing of a rifle across the body); prone he holds it
# along his shoulder pointing ahead (frames 98-103) as E1 holds his rifle
_E3_GUN_WALK = [('gp', {0: (-30, 30), 1: 8}), ('gy', {0: (-40, 40), 1: 8}), ('gr', {0: (-40, 40), 1: 8}),
                ('rgx', {0: (0.3, 4.5), 1: 0.6}), ('rgy', {0: (-1.0, 3.5), 1: 0.6}), ('rgz', {0: (-3.0, 1.0), 1: 0.6}),
                ('lfx', {0: (1.5, 4.5)}), ('lsw', {0: (-50, 50), 1: 30}), ('rsw', {0: (-50, 50), 1: 30})]
UNIT_SPEC[('e3', 'walk')] = [c for c in SPEC['walk'] if c[0] not in ('gp', 'gy', 'gr', 'rgx', 'rgy', 'rgz', 'lfx', 'lsw',
                                                                   'rsw')] + _E3_GUN_WALK
E3_HOLD = dict(gp=-11.0, gy=-11.5, gr=15.5, rgx=2.6, rgy=2.95, rgz=0.4, lfx=2.4)     # (its standing hold: e3_shape.json)


def walk_keys_e3():
    k = walk_keys()
    for ch, v in E3_HOLD.items():
        k[ch] = [v] * N
    return k


UNIT_KEYS[('e3', 'walk')] = walk_keys_e3


# ---------------------------------------------------------------------------------------------- Nod: unarmed runners
# the Chameleon Spy and the Hijacker run as the Disc Thrower does (TS's side views, frames 20-25: a sprint, the
# trailing leg kicked up behind, the body nearly upright), both arms swinging free against the legs
for _u in ('chamspy', 'mhijack'):
    UNIT_SPEC[(_u, 'walk')] = UNIT_SPEC[('e2', 'walk')]
    UNIT_KEYS[(_u, 'walk')] = walk_keys_e2
    UNIT_FACE[(_u, 'walk')] = UNIT_FACE[('e2', 'walk')]
    UNIT_MIN_AMP[(_u, 'walk')] = UNIT_MIN_AMP[('e2', 'walk')]


# ---------------------------------------------------------------------------------------------- Nod: the Cyborg
# a sequence's fixed settings (step_pose): crawling, the Cyborg has no legs (TS's crawl frames: a crippled cyborg drags
# itself along on its arms)
SEQ_BASE = {('cyborg', 'crawl'): {'legless': 1.0}}
# TS's Cyborg runs heavily (frames 20-25, 32-37): the soldiers' stride and lean, the free left arm swinging against
# the legs, the gun arm swinging forward and back with them, out level ahead at the top of its swing
UNIT_SPEC[('cyborg', 'walk')] = (_LEGS_WALK + _BODY_WALK +
                                 _ONE_ARM('r', {0: (-30, 90), 1: 45, 2: 15}, {0: (0, 40), 1: 10},
                                          {0: (0, 110), 1: 45, 2: 15}, {0: (-40, 40)}) +
                                 _ONE_ARM('l', {0: (-40, 60), 1: 50, 2: 15}, {0: (0, 40), 1: 10},
                                          {0: (0, 110), 1: 40, 2: 20}, {0: (-30, 30)}))
UNIT_FACE[('cyborg', 'walk')] = [('rsf', {0: 25, 1: 20}), ('rsa', {0: 15}), ('ref', {0: 25, 1: 20}),
                                 ('lsf', {0: 20, 1: 15}), ('lef', {0: 20, 1: 15}), ('sy', {0: 15, 1: 12}),
                                 ('hy', {0: 15, 1: 12})]
UNIT_MIN_AMP[('cyborg', 'walk')] = {'hf': 18.0, 'kf': 45.0}


def walk_keys_cyborg():
    k = walk_keys()
    for ch in ('gy', 'gp', 'gr', 'rgx', 'rgy', 'rgz', 'lfx', 'lsw', 'rsw'):
        k.pop(ch)
    thigh = np.array([-25.0, -35.0, -10.0, 20.0, 0.0, -5.0])
    return dict(k, rsf=list(30.0 + 0.8 * thigh), rsa=[12.0] * N, rst=[0.0] * N, ref=[30.0] * N,
                lsf=list(10.0 - 0.8 * np.roll(thigh, 3)), lsa=[12.0] * N, lst=[0.0] * N, lef=[40.0] * N)


# crawling (legless): flat on its front, the chest up a little, the head up; the free left arm reaching ahead along
# the ground and pulling back, the gun arm out ahead, worked forward a little with each pull
UNIT_SPEC[('cyborg', 'crawl')] = [
    ('pitch', {0: (70, 98)}), ('roll', {1: 6}), ('yaw', {0: (-8, 8)}), ('dx', {0: (-8, 8)}), ('dy', {0: (-4, 16)}),
    ('sp', {0: (-35, 0)}), ('sy', {0: (-12, 12), 1: 8}), ('sr', {1: 6}), ('hp', {0: (-100, -30)}), ('hy', {0: (-12, 12)}),
    ('lsf', {0: (90, 190), 1: 45}), ('lsa', {0: (0, 45), 1: 12}), ('lst', {0: (-45, 45)}), ('lef', {0: (0, 110), 1: 45}),
    ('rsf', {0: (110, 190), 1: 15}), ('rsa', {0: (0, 35)}), ('rst', {0: (-35, 35)}), ('ref', {0: (0, 70), 1: 15})]
UNIT_FACE[('cyborg', 'crawl')] = [('sy', {0: 6}), ('hy', {0: 10})]
UNIT_MIN_AMP[('cyborg', 'crawl')] = {'lsf': 15.0}


def crawl_keys_cyborg():
    c = np.cos(2 * np.pi * np.arange(N) / N)
    return dict(pitch=[86.0] * N, roll=[0.0] * N, yaw=[0.0] * N, dx=[2.0] * N, dy=[6.0] * N, sp=[-12.0] * N,
                sy=[0.0] * N, sr=[0.0] * N, hp=[-65.0] * N, hy=[0.0] * N,
                lsf=list(150.0 + 30.0 * c), lsa=[18.0] * N, lst=[0.0] * N, lef=list(45.0 - 35.0 * c),
                rsf=list(160.0 + 8.0 * c), rsa=[10.0] * N, rst=[0.0] * N, ref=[20.0] * N)


UNIT_KEYS[('cyborg', 'walk')] = walk_keys_cyborg
UNIT_KEYS[('cyborg', 'crawl')] = crawl_keys_cyborg
# the Cyborg Commando: the Cyborg's run (9 steps a cycle) and legless crawl
SEQ_BASE[('cyc2', 'crawl')] = {'legless': 1.0}
for _s in ('walk', 'crawl'):
    UNIT_SPEC[('cyc2', _s)] = UNIT_SPEC[('cyborg', _s)]
    UNIT_FACE[('cyc2', _s)] = UNIT_FACE[('cyborg', _s)]
    UNIT_MIN_AMP[('cyc2', _s)] = UNIT_MIN_AMP[('cyborg', _s)]
    UNIT_KEYS[('cyc2', _s)] = UNIT_KEYS[('cyborg', _s)]
# (TS draws the crawling Commando well behind where it stands, its cannon reaching back towards its position - 8 to
# 14 TS px in the facings fitted one by one: the body moved back along its facing (bx, by), the same in every facing,
# as the GDI soldiers' prone; without it the shared crawl settled tilted up off the ground, overlap 0.24)
UNIT_SPEC[('cyc2', 'crawl')] = [c for c in UNIT_SPEC[('cyborg', 'crawl')] if c[0] not in ('dx', 'dy')] + [
    ('dx', {0: (-6, 6)}), ('dy', {0: (-6, 6)}), ('bx', {0: (-18, 4)}), ('by', {0: (-6, 6)})]


def crawl_keys_cyc2():
    return dict(crawl_keys_cyborg(), dx=[0.0] * N, dy=[0.0] * N, bx=[-10.0] * N, by=[0.0] * N, pitch=[86.0] * N)


UNIT_KEYS[('cyc2', 'crawl')] = crawl_keys_cyc2


def main_shared(unit, shape, seq, out, iters, start):
    js, S = load_shape(shape)
    lay = layout(spec_of(unit, seq))
    x0 = start_coef(js, seq, lay, unit)
    P = Problem(unit, S, js['ax'], js['y0'], seq, dict(js['Q']), lay)
    P.x_prior = np.array(x0)
    if start:
        keep = os.environ['START_CH'].split(',') if os.environ.get('START_CH') else None
        xs = load_coef(start, lay, x0)
        for i, l in enumerate(lay):
            if keep is None or l[0] in keep:
                x0[i] = xs[i]
    free = os.environ['FREE'].split(',') if os.environ.get('FREE') else channels(lay)
    print('free', len([l for l in lay if l[0] in free]), 'of', len(lay), 'start f %.4f' % P.loss(x0), flush=True)
    x, fb = fit(P, x0, lay, free, iters, sigma=float(os.environ.get('SIGMA', 0.1)),
                pop=int(os.environ.get('POP', 20)), seed=int(os.environ.get('SEED', 1)), out=out,
                workers=int(os.environ.get('WORKERS', 2)))
    ious = P.ious(x)
    json.dump(dict(coef=coef_list(lay, x), f=fb, iou={'%d,%d' % sf: v for sf, v in ious.items()}), open(out, 'w'))
    if os.environ.get('STEPS_OUT'):
        write_steps(P, x, os.environ['STEPS_OUT'], ious)
    print('done f %.4f iou %.3f' % (fb, np.mean(list(ious.values()))), flush=True)


def main_face(unit, shape, seq, out, iters, cycle, facings):
    js, S = load_shape(shape)
    lay = layout(spec_of(unit, seq))
    shared = load_coef(cycle, lay)
    flay = layout(face_of(unit, seq))
    res = json.load(open(out)) if os.path.exists(out) else {}
    for f in facings:
        if str(f) in res:
            continue
        P = Problem(unit, S, js['ax'], js['y0'], seq, dict(js['Q']), lay, facings=[f], face_lay=flay, shared=shared)
        x0 = np.zeros(len(flay))
        t0 = time.time()
        x, fb = fit(P, x0, flay, channels(flay), iters, sigma=float(os.environ.get('SIGMA', 0.15)),
                    pop=int(os.environ.get('POP', 16)), seed=int(os.environ.get('SEED', 1)), log_every=1000,
                    workers=int(os.environ.get('WORKERS', 1)))
        ious = P.ious(None, x)
        res = json.load(open(out)) if os.path.exists(out) else {}
        res[str(f)] = dict(coef=coef_list(flay, x), f=fb, iou=[ious[(s, f)] for s, fr in P.steps])
        json.dump(res, open(out, 'w'))
        print('facing', f, 'f %.4f iou %.3f' % (fb, np.mean([ious[(s, f)] for s, fr in P.steps])),
              '%.0fs' % (time.time() - t0), flush=True)
    print('done', flush=True)


def write_frames(unit, shape, seq, cycle, faces, path):
    """every frame's pose {frame: {Q, facing, iou}}: the shared cycle plus its facing's own loop."""
    js, S = load_shape(shape)
    lay = layout(spec_of(unit, seq)); flay = layout(face_of(unit, seq))
    shared = load_coef(cycle, lay)
    fc = json.load(open(faces)) if faces else {}
    ph = phase_of(unit, seq)
    out = {}
    for s, frames in SQ.frames_of(unit, seq):
        for f, k in enumerate(frames):
            face = (flay, load_coef_list(fc[str(f)]['coef'], flay)) if str(f) in fc else None
            c = (s + ph[f]) % N                       # the cycle's step this TS frame shows
            Q = step_pose(dict(js['Q']), lay, shared, c, face, seq)
            out[str(k)] = dict(Q=Q, facing=f, step=s, cycle_step=c)
    json.dump(out, open(path, 'w'), default=float)
    return out


def load_coef_list(cl, lay):
    d = {(c, n, k): v for c, n, k, v in cl}
    return np.array([d.get((c, n, k), 0.0) for c, n, k, lo, hi in lay])


if __name__ == '__main__':
    unit, shape, seq, out = sys.argv[1:5]
    import infunit; infunit.use(unit)
    N = infunit.CYCLE_N.get(unit, 6)          # (run as a script: this module's own steps a cycle)
    iters = int(sys.argv[5])
    if len(sys.argv) > 7 and sys.argv[7] == 'facing':
        main_face(unit, shape, seq, out, iters, sys.argv[6], [int(v) for v in sys.argv[8].split(',')])
    else:
        main_shared(unit, shape, seq, out, iters, sys.argv[6] if len(sys.argv) > 6 else None)


