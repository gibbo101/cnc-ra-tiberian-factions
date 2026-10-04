"""
inffit.py - fits the soldier (inf.py) to an infantry unit's TS frames in TS's own camera (orthographic, 30 degrees,
looking north; the sprite's 8 facings turned 45 degrees apart): silhouette plus colour classes.  TS's muzzle flashes
and blood are left out of both.

    python3 inffit.py UNIT stand out.json iters [start.json]
        the shape, the standing pose and the ground point (TS's frame x, y), on the 8 standing frames
    python3 inffit.py UNIT pose shape.json out.json iters FRAMES [start.json]
        one pose (the shape fixed) on several frames, each a facing: FRAMES like 20,26,32... (one per facing, f order)
UNIT: a key of UNITS (e1 ...).
"""
import json, os, sys, time
import numpy as np
from PIL import Image
import rc
import inf as I
from paths import HANDOFF

ROOT = HANDOFF + '/'
UNITS = {'e1': ('17-TSE1', 'E1')}
G, N, LB, GR, D, FX, OR, YE, SK = 1, 2, 3, 4, 5, 6, 7, 8, 9
AG = np.eye(10)
AG[0, 0] = 0.0
for a, b, v in ((N, LB, 0.5), (N, D, 0.5), (GR, D, 0.4), (N, GR, 0.3), (G, D, 0.15), (LB, GR, 0.3), (OR, D, 0.25),
                (YE, OR, 0.4), (YE, D, 0.2), (SK, OR, 0.3), (SK, D, 0.25)):
    AG[a, b] = AG[b, a] = v
S0 = I.S0                    # the unit's default shape (infunit.use switches it)
# how much a TS pixel of each colour class counts in the colour term (a small patch of a colour TS shows nowhere else,
# like E2's orange pouch, would otherwise be given up for a pixel of silhouette; infunit.use sets it per unit)
CW = np.ones(10)


def ts_frame(unit, k):
    d, name = UNITS[unit]
    return np.asarray(Image.open(ROOT + '%s/ts-original/%s/frames/%s-%03d.png' % (d, name, name.lower(), k))
                      .convert('RGBA')).astype(int)


def ts_classes(a):
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    m = al > 0
    c = np.zeros(r.shape, int)
    mean = (r + g + b) / 3.0
    green = m & (r == 0) & (b == 0) & (g > 0)
    blue = m & ~green & (b > r + 15) & (b > g + 15)
    warm = m & ~green & ~blue & (r > b + 30)
    neutral = m & ~green & ~blue & ~warm
    c[green] = G
    c[blue & (mean >= 125)] = LB
    c[blue & (mean < 125)] = N
    c[neutral & (mean >= 90)] = GR
    c[neutral & (mean < 90)] = D
    c[warm] = FX
    return c


# (SHADOW=w: TS's own shadow (the mod's frames carry it) counts too, w as much as the silhouette: from TS's camera a leg
# raised in the air and a leg lying further back look the same, the shadow tells them apart - Luke: "leg in the air
# way above the shadow")
W_SHADOW = float(os.environ.get('SHADOW', 0) or 0)
W_THIN = float(os.environ.get('THIN', 0) or 0)


class Target:
    """one TS frame: its classes and silhouette (effects left out) in a window round it."""

    def __init__(self, unit, k, facing, margin=3):
        self.shadow = None
        if W_SHADOW > 0:
            import tsshadow
            self.shadow = tsshadow.ShadowTarget(unit, k)
        a = ts_frame(unit, k)
        c = ts_classes(a)
        ys, xs = np.nonzero(c > 0)
        self.win = (max(xs.min() - margin, 0), max(ys.min() - margin, 0), min(xs.max() + margin + 1, a.shape[1]),
                    min(ys.max() + margin + 1, a.shape[0]))
        x0, y0, x1, y1 = self.win
        self.cls = c[y0:y1, x0:x1]
        self.mask = (self.cls > 0) & (self.cls != FX)
        self.fx = self.cls == FX
        # (THIN=w: TS's thin parts - an arm or a gun a pixel or two wide, flung out from the body - count w times in the
        # outline: a pixel each, against the body's hundreds, the fit gave them up; Luke compares those first)
        self.wts = None
        if W_THIN > 1.0:
            from scipy import ndimage as _nd
            body = _nd.binary_opening(self.mask, structure=np.ones((5, 5)))
            thin = self.mask & ~_nd.binary_dilation(body, structure=np.ones((3, 3)))
            self.wts = np.where(thin, W_THIN, 1.0)
        self.k, self.facing = k, facing


# TS's light for its sprites (hd.L_CAM_TS) in this camera: its highlight on the glossy helmet is TS's light-blue pixel on
# the helmet's top left, in every facing
H_TS = np.array([-0.329, 0.771, 0.543])


GLINT_CLASS = I.LBLUE        # the class TS draws the helmet's glint in (infunit.use: none for the Engineer's hood)
EDGE_DARK = False            # the soldier's edge pixels count as dark (infunit.use: the Engineer, all bright yellow)
SS = int(os.environ.get("FIT_SS", 3) or 3)   # supersampling of the model's classes per TS pixel (FIT_SS=2: a coarser, faster pass)


def model_cls(parts, cam, win, ss=None):
    ss = SS if ss is None else ss
    x0, y0, x1, y1 = win
    w, h = x1 - x0, y1 - y0
    t, who, nrm, O = rc.render_ids(parts, cam, x0, y0, w, h, ss=ss, zstart=80.0)
    comps = np.array([0] + [p.comp for p in parts])[who + 1]
    cls_of = np.array([0] + [I.CLASS[p.comp] for p in parts])
    cl = cls_of[who + 1]
    if GLINT_CLASS:
        hl = (comps == I.HELMET) & ((nrm @ H_TS) > 0.95)
        cl = np.where(hl, GLINT_CLASS, cl)
    cl = cl.reshape(h, ss, w, ss).transpose(0, 2, 1, 3).reshape(h, w, ss * ss)
    if EDGE_DARK:
        # TS's sprites were drawn on black: a pixel the soldier only partly covers comes out dark, whatever the part
        cov = (cl > 0).mean(-1, keepdims=True)
        cl = np.where((cov < 1.0) & (cl > 0), D, cl)
    return cl


# TS's sprites draw every pixel a shape touches (their edges antialiased dark), so a pixel a third covered is in TS's
# silhouette: matching coverage 1 there would fatten every limb by a pixel
COVER = 0.3


def frame_loss(S, Q, tgt, ax, y0, w_cls=0.6, rifle=True):
    parts, dz = I.grounded(S, Q, I.facing_angle(tgt.facing), rifle)
    l = parts_loss(parts, tgt, ax, y0, w_cls)
    if getattr(tgt, 'shadow', None) is not None:
        l += W_SHADOW * tgt.shadow.loss(parts, rc.Cam((0, -1), 30.0, 1.0, (ax, y0)))
    if EXTRA is not None:
        l += EXTRA(S, Q, tgt, dz)
    return l


# (EXTRA(S, Q, tgt, dz): a script's own term on the pose, e.g. a soldier TS shows lying must touch the ground)
EXTRA = None


def parts_loss(parts, tgt, ax, y0, w_cls=0.6):
    """the loss of the soldier's grounded parts (world) on one TS frame."""
    cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
    cl = model_cls(parts, cam, tgt.win)
    cov = np.clip((cl > 0).mean(-1) / COVER, 0, 1)
    keep = ~tgt.fx
    d = np.abs(cov - tgt.mask)
    if getattr(tgt, 'wts', None) is not None:
        d = d * tgt.wts
    l = d[keep].sum() / tgt.mask.sum()
    both = tgt.mask & (cov >= 0.5)
    agree = AG[cl, tgt.cls[..., None]].mean(-1) / np.maximum((cl > 0).mean(-1), 1e-6)
    return l + w_cls * ((1 - agree[both]) * CW[tgt.cls[both]]).sum() / tgt.mask.sum()


def iou(S, Q, tgt, ax, y0):
    parts, dz = I.grounded(S, Q, I.facing_angle(tgt.facing))
    return parts_iou(parts, tgt, ax, y0)


def parts_iou(parts, tgt, ax, y0):
    cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
    cov = (model_cls(parts, cam, tgt.win) > 0).mean(-1) >= COVER
    m = tgt.mask
    return (cov & m).sum() / max((cov | m).sum(), 1)


# the shape's free sizes and their ranges
SSPEC = [('hw', 0.9, 1.6), ('lt', 4.0, 6.0), ('lsr', 0.85, 1.05), ('rt', 1.0, 1.6), ('rs', 0.75, 1.25), ('ah', 0.6, 1.4),
         ('bl', 2.0, 3.4), ('bw', 0.7, 1.3), ('bh', 0.8, 1.5), ('lsp', 5.0, 8.4), ('sw', 2.5, 4.6),
         ('lu', 3.2, 4.4), ('lf', 3.0, 4.0), ('ru', 0.6, 1.2), ('rf', 0.55, 1.1), ('rh', 0.5, 0.9), ('ln', 0.0, 1.2),
         ('fva', 18.0, 45.0), ('fe0', -60.0, -15.0), ('fe1', -5.0, 35.0), ('fd', 0.06, 0.3), ('fj', 10.0, 40.0),
         ('vt', -0.6, 0.6), ('gl', 9.0, 14.0), ('gt', 0.8, 1.3),
         ('gg', 2.5, 6.0), ('gs', 1.2, 2.0), ('pdz', -0.2, 1.2)]
# tuple sizes, each as a scale on its default
TSPEC = [('pr', 0.8, 1.15), ('cr', 0.8, 1.15), ('ar', 0.8, 1.15), ('hr', 0.85, 1.12), ('pk', 0.5, 1.5), ('po', 0.3, 1.5),
         ('pd', 0.6, 1.3)]
# the pose's free angles
QBODY = [('pitch', -15, 25), ('roll', -10, 10), ('sp', -15, 30), ('sy', -40, 40), ('sr', -15, 15), ('hp', -30, 30),
         ('hy', -50, 50), ('lhf', -50, 70), ('lha', -15, 30), ('lht', -40, 40), ('lkf', 0, 110), ('laf', -30, 30),
         ('rhf', -50, 70), ('rha', -15, 30), ('rht', -40, 40), ('rkf', 0, 110), ('raf', -30, 30), ('yaw', -40, 40),
         ('dx', -3, 3), ('dy', -3, 3), ('gp', -60, 60), ('gy', -60, 60), ('gr', -45, 45)]
# the arms: holding the rifle (two-bone reach for its grip and fore-end), or free (joint angles)
QHOLD = [('rgx', 0.5, 5.0), ('rgy', -2.0, 3.0), ('rgz', -6.0, 0.5), ('lfx', 1.0, 5.0), ('lsw', -60, 60), ('rsw', -60, 60)]
QFREE = [('lsf', -40, 120), ('lsa', -30, 60), ('lst', -60, 60), ('lef', 0, 140), ('rsf', -40, 120), ('rsa', -30, 60),
         ('rst', -60, 60), ('ref', 0, 140)]
QSPEC = QBODY + QHOLD


def qspec(Q):
    return QBODY + (QHOLD if Q.get('ik', 1.0) > 0.5 else QFREE)


def unpack_shape(x, base):
    S = dict(base)
    i = 0
    for k, lo, hi in SSPEC:
        S[k] = float(x[i]); i += 1
    S['ls'] = S['lt'] * S.pop('lsr')
    for k, lo, hi in TSPEC:
        S[k] = tuple(float(v) * float(x[i]) for v in S0[k]); i += 1
    return S, i


def unpack_pose(x, base, i=0):
    Q = dict(base)
    for k, lo, hi in qspec(base):
        Q[k] = float(x[i]); i += 1
    return Q, i


def cma_fit(f, lo, hi, x0, iters, out_cb, sigma=0.15, pop=24, seed=1):
    import cma
    span = hi - lo
    z0 = np.clip((x0 - lo) / span, 1e-3, 1 - 1e-3)
    g = lambda z: f(lo + np.clip(z, 0, 1) * span)
    es = cma.CMAEvolutionStrategy(z0, sigma, {'bounds': [0, 1], 'popsize': pop, 'maxiter': iters, 'seed': seed,
                                              'verbose': -9})
    t0 = time.time(); it = 0
    while not es.stop():
        Z = es.ask(); es.tell(Z, [g(z) for z in Z]); it += 1
        if it % 25 == 0 or es.stop():
            out_cb(lo + np.clip(es.result.xbest, 0, 1) * span, es.result.fbest, it, time.time() - t0)
    return lo + np.clip(es.result.xbest, 0, 1) * span


# the ready stance: the rifle forward at the chest, the left foot forward (TS's S view: the soldier's left foot lower)
STAND_Q = dict(I.Q0, gp=-4.0, lhf=12.0, rhf=-10.0, lkf=8.0, rkf=5.0, lha=2.0, rha=2.0)


def fit_stand(unit, out, iters, start=None):
    tg = [Target(unit, f, f) for f in range(8)]
    Sb = S0
    S0_, Q0 = dict(Sb), dict(STAND_Q)
    ax0, y00 = 30.5, 32.5
    if start:
        js = json.load(open(start)); S0_.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
        Q0.update(js['Q']); ax0, y00 = js['ax'], js['y0']
    lo, hi, x0 = [], [], []
    # (BOUNDS=key:lo:hi,... narrows or widens a size's range for this fit)
    bd = {b.split(':')[0]: (float(b.split(':')[1]), float(b.split(':')[2]))
          for b in filter(None, os.environ.get('BOUNDS', '').split(','))}
    for k, a, b in SSPEC:
        a, b = bd.get(k, (a, b))
        lo.append(a); hi.append(b); x0.append(S0_[k] if k != 'lsr' else S0_['ls'] / S0_['lt'])
    for k, a, b in TSPEC:
        a, b = bd.get(k, (a, b))
        lo.append(a); hi.append(b); x0.append(S0_[k][0] / Sb[k][0] if Sb[k][0] else 1.0)
    # the pose stays near the ready stance it starts from (the 8 facings are one pose); the knees nearly straight
    for k, a, b in qspec(Q0):
        w = {'yaw': 10.0, 'dx': 3.0, 'dy': 3.0, 'rgx': 2.0, 'rgy': 2.0, 'rgz': 2.0, 'lfx': 2.0}.get(k, 35.0)
        if k in ('lkf', 'rkf'):
            # (KNEE_MAX: a unit TS draws standing with bent knees, the Ghost's wide stance)
            km = float(os.environ.get('KNEE_MAX', 15.0))
            lo.append(0.0); hi.append(km); x0.append(min(Q0[k], km)); continue
        if k == 'hp':                                   # TS's soldier looks straight ahead: his face shows
            # (HP_RANGE=lo:hi narrows it: the Medic's faceplate is TS's dark row under his crown)
            hl, hh = [float(v) for v in os.environ.get('HP_RANGE', '-10:10').split(':')]
            lo.append(hl); hi.append(hh); x0.append(float(np.clip(Q0[k], hl, hh))); continue
        lo.append(max(a, Q0[k] - w)); hi.append(min(b, Q0[k] + w)); x0.append(Q0[k])
    # (the ground point's range: GROUND=ax_lo:ax_hi:y_lo:y_hi widens it for a unit drawn higher in its frames)
    g = [float(v) for v in os.environ['GROUND'].split(':')] if os.environ.get('GROUND') else [28.5, 32.5, 30.0, 35.5]
    lo += [g[0], g[2]]; hi += [g[1], g[3]]; x0 += [ax0, y00]
    lo, hi, x0 = np.array(lo, float), np.array(hi, float), np.clip(np.array(x0, float), lo, hi)

    # (NO_RIFLE: the body alone; a gun TS holds a different way in every facing is left to each facing's own fit)
    rifle = not os.environ.get('NO_RIFLE')

    def f(x):
        S, i = unpack_shape(x, Sb)
        Q, i = unpack_pose(x, Q0, i)
        return float(np.mean([frame_loss(S, Q, t, x[-2], x[-1], rifle=rifle) for t in tg]))

    def cb(x, fb, it, dt):
        S, i = unpack_shape(x, Sb); Q, i = unpack_pose(x, Q0, i)
        ious = [iou(S, Q, t, x[-2], x[-1]) for t in tg]
        json.dump(dict(S=S, Q=Q, ax=float(x[-2]), y0=float(x[-1]), f=float(fb), iou=ious), open(out, 'w'), default=float)
        print('it', it, 'best %.4f' % fb, 'iou %.3f' % np.mean(ious), '%.0fs' % dt, flush=True)
    cma_fit(f, lo, hi, x0, iters, cb, sigma=float(os.environ.get('SIGMA', 0.1)), seed=int(os.environ.get('SEED', 1)))
    print('done', flush=True)


def fit_pose(unit, shape, out, iters, frames, start=None, sigma=0.15):
    js = json.load(open(shape))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    ax, y0 = js['ax'], js['y0']
    tg = [Target(unit, k, f) for f, k in enumerate(frames)]
    Q0 = dict(js['Q'])
    if start:
        Q0.update(json.load(open(start))['Q'])
    lo = np.array([a for k, a, b in qspec(Q0)], float); hi = np.array([b for k, a, b in qspec(Q0)], float)
    x0 = np.clip(np.array([Q0[k] for k, a, b in qspec(Q0)], float), lo, hi)

    def f(x):
        Q, i = unpack_pose(x, Q0)
        return float(np.mean([frame_loss(S, Q, t, ax, y0) for t in tg]))

    def cb(x, fb, it, dt):
        Q, i = unpack_pose(x, Q0)
        ious = [iou(S, Q, t, ax, y0) for t in tg]
        json.dump(dict(Q=Q, frames=list(frames), f=float(fb), iou=ious), open(out, 'w'), default=float)
        print('it', it, 'best %.4f' % fb, 'iou %.3f' % np.mean(ious), '%.0fs' % dt, flush=True)
    cma_fit(f, lo, hi, x0, iters, cb, sigma=sigma, seed=int(os.environ.get('SEED', 1)))
    print('done', flush=True)


if __name__ == '__main__':
    unit, mode = sys.argv[1], sys.argv[2]
    import infunit; infunit.use(unit)
    import inffit as M                     # the module infunit switched (this script's own globals are __main__'s)
    if mode == 'stand':
        M.fit_stand(unit, sys.argv[3], int(sys.argv[4]), sys.argv[5] if len(sys.argv) > 5 else None)
    elif mode == 'pose':
        fr = [int(v) for v in sys.argv[6].split(',')]
        M.fit_pose(unit, sys.argv[3], sys.argv[4], int(sys.argv[5]), fr, sys.argv[7] if len(sys.argv) > 7 else None)
