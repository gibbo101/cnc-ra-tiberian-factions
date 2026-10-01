"""
legfit.py - the Titan's legs as convex parts, posed per walk step, fitted to TS's MMCH walk frames.

Body frame: u forward, v right, w up (units = TS sprite px along the screen).  Facing CW k (TS's own order,
k = 0 north, clockwise, 45 degrees a step) turns the body so forward = (sin th, -cos th).
"""
import numpy as np
import rc
from tspal import load

HIP, THIGH, SHIN, FOOT, KNEE = 1, 2, 3, 4, 5
CLS = {HIP: 2, THIGH: 1, SHIN: 1, FOOT: 1, KNEE: 2}

# shared shape (initial guesses, refined by the fit)
SHAPE = dict(
    hip_c=(0.0, 0.0, 19.0), hip_r=(6.5, 7.0, 10.5), hip_bot=16.0,     # dome: ellipsoid cut at hip_bot
    jv=4.6, jw=17.5, ju=0.0,                                         # hip joints at (ju, +-jv, jw)
    splay=6.0,                                                       # legs lean out (degrees)
    Lt=8.5, tw=4.2, td=4.6,                                          # thigh
    Ls=9.0, sw=3.6, sd=3.8,                                          # shin
    lf=6.0, lh=3.0, fw=5.0, fh=2.6,                                  # foot: toe and heel length past the ankle
)


JOINT = 6


def leg_parts(side, a_t, a_s, a_f, S, dw=0.0, detail=False):
    """side -1 left, +1 right.  a_t, a_s: thigh and shin pitch from straight down (degrees, + = forward);
    the Titan's knees bend backward (thigh back, shin forward).  a_f: foot pitch (+ = toe up)."""
    sp = np.deg2rad(S['splay']) * side
    J = np.array([S['ju'], side * S['jv'], S['jw'] + dw])

    def dirn(a):
        a = np.deg2rad(a)
        return np.array([np.sin(a), np.sin(sp) * np.cos(a), -np.cos(a) * np.cos(sp)])

    K = J + S['Lt'] * dirn(a_t)
    A = K + S['Ls'] * dirn(a_s)
    parts = [rc.seg_box(J, K, S['tw'], S['td'], THIGH, up=(1, 0, 0), chamfer=0.8, ext=1.0, name='thigh'),
             rc.seg_box(K, A, S['sw'], S['sd'], SHIN, up=(1, 0, 0), chamfer=0.6, ext=0.6, name='shin')]
    # the knee spur: a block from the knee straight back (TS's dark-tipped spike), tilted up by ka degrees
    ka = np.deg2rad(S.get('ka', 10.0))
    back = np.array([-np.cos(ka), 0.0, np.sin(ka)])
    ks = S.get('ks', 5.0)
    parts.append(rc.seg_box(K - back * 0.5, K + back * ks, S.get('kw', 3.0), S.get('kd', 2.4), KNEE,
                            up=(0, 0, 1.0), chamfer=0.6, name='spur'))
    af = np.deg2rad(a_f)
    fwd = np.array([np.cos(af), 0.0, np.sin(af)])
    up = np.array([-np.sin(af), 0.0, np.cos(af)])
    side_ax = np.cross(up, fwd)
    Rf = np.stack([fwd, side_ax, up], axis=1)
    if not detail:
        c = A + fwd * (S['lf'] - S['lh']) / 2 - up * S['fh'] / 2
        parts.append(rc.box(c, Rf, ((S['lf'] + S['lh']) / 2, S['fw'] / 2, S['fh'] / 2), FOOT, chamfer=(0.8, 0.8, 0.6),
                            name='foot'))
        return parts, (J, K, A)
    # detail: the foot as a heel block and two toes with a gap between (TS's split toes), round joints at the
    # knee and the ankle
    lf, lh, fw, fh = S['lf'], S['lh'], S['fw'], S['fh']
    x0, x1 = -lh, lf * 0.42
    c = A + fwd * (x0 + x1) / 2 - up * fh / 2
    parts.append(rc.box(c, Rf, ((x1 - x0) / 2, fw / 2, fh / 2), FOOT, chamfer=(0.8, 0.8, 0.6), name='foot'))
    gap = min(0.7, fw * 0.12)
    tw = (fw - gap) / 2
    for sgn in (-1, 1):
        cy = sgn * (gap / 2 + tw / 2)
        tx0, tx1 = lf * 0.3, lf
        c = A + fwd * (tx0 + tx1) / 2 + side_ax * cy - up * fh * 0.55
        toe = rc.box(c, Rf, ((tx1 - tx0) / 2, tw / 2, fh * 0.45), FOOT, chamfer=(0.7, 0.55, 0.5), name='toe')
        # the toe's top slopes down to its tip
        tip = A + fwd * tx1 - up * fh * 0.62; back_top = A + fwd * (tx0 + 0.6) - up * fh * 0.1
        dvec = tip - back_top; nrm = np.cross(side_ax, dvec); nrm = nrm / np.linalg.norm(nrm)
        if nrm @ up < 0:
            nrm = -nrm
        toe.cons.append(rc.Plane(nrm, nrm @ tip))
        parts.append(toe)
    lat = np.array([0, 1.0, 0])
    for P_, r_, w_ in ((K, S['sd'] * 0.42, S['sw'] * 0.62), (A, S['sd'] * 0.38, S['sw'] * 0.6)):
        parts.append(rc.cylinder(P_ - lat * w_, P_ + lat * w_, r_, JOINT, 'joint'))
    return parts, (J, K, A)


PELVIS, HIPDOME, HIPRING, HIPJOINT = 7, 8, 9, 10


def hip_parts(S, dw=0.0, detail=False):
    """the hip.  Fitting uses a dome (an ellipsoid cut below); the rendered hip is TS's read of it as a machine: a
    chamfered pelvis block with round hip joints at its sides where the thighs hang, a grey bearing ring on it,
    and the rounded olive dome above that the upper body turns on."""
    if detail:
        cu = S['hip_c'][0]
        jw = S['jw'] + dw
        top = jw + 4.4                                         # the pelvis's top, where the ring sits
        pel = rc.box((cu, 0.0, (jw - 1.4 + top) / 2), np.eye(3), (5.6, 6.2, (top - jw + 1.4) / 2), PELVIS,
                     chamfer=(1.9, 1.4, 1.4), name='pelvis')
        ring = rc.cylinder((cu, 0.0, top - 0.25), (cu, 0.0, top + 0.95), 6.3, HIPRING, 'ring')
        dome = rc.Part([rc.Ellip((cu, 0.0, top + 0.6), np.eye(3), (5.5, 5.9, 6.4)),
                        rc.Plane((0, 0, -1.0), -(top + 0.6))], HIPDOME, 'hipdome',
                       sphere=(np.array([cu, 0.0, top + 0.6]), 6.5))
        out = [pel, ring, dome]
        for side in (-1, 1):
            J = np.array([S['ju'], side * S['jv'], jw])
            out.append(rc.cylinder(J - np.array([0, side * 1.6, 0]), J + np.array([0, side * 2.4, 0]), 2.35, HIPJOINT,
                                   'hipjoint'))
        return out
    c = np.array(S['hip_c']) + (0, 0, dw)
    return [rc.Part([rc.Ellip(c, np.eye(3), S['hip_r']), rc.Plane((0, 0, -1.0), -(S['hip_bot'] + dw))], HIP, 'hip',
                    sphere=(c, float(max(S['hip_r'])) + 1e-3))]


def body_parts(S, pose, dw=0.0, detail=False):
    """pose: (left a_t, a_s, a_f, right a_t, a_s, a_f)."""
    l, _ = leg_parts(-1, *pose[:3], S, dw, detail)
    r, _ = leg_parts(+1, *pose[3:6], S, dw, detail)
    return hip_parts(S, dw, detail) + l + r


def facing_matrix(k, nfac=8):
    th = 2 * np.pi * k / nfac
    f = np.array([np.sin(th), -np.cos(th), 0.0]); r = np.array([np.cos(th), np.sin(th), 0.0])
    return np.stack([f, r, np.array([0, 0, 1.0])], axis=1)


class TSViews:
    """TS's masks for one walk step at the 8 facings, in a window round the legs."""

    def __init__(self, step, win=(26, 24, 70, 62), ax=47.4, y0=51.5, elev=30.0):
        self.win = win
        x0, y0w, x1, y1 = win
        self.masks = [load(k * 15 + step)[y0w:y1, x0:x1, 3] > 0 for k in range(8)]
        self.cam = rc.Cam((0, -1), elev, 1.0, (ax, y0))

    def render(self, parts_body, ss=2):
        x0, y0w, x1, y1 = self.win
        out = []
        for k in range(8):
            M = facing_matrix(k)
            parts = [p.moved(M) for p in parts_body]
            t, who, nrm, O = rc.render_ids(parts, self.cam, x0, y0w, x1 - x0, y1 - y0w, ss=ss)
            cov = (who >= 0).reshape(y1 - y0w, ss, x1 - x0, ss).mean(axis=(1, 3))
            out.append((cov >= 0.5, who))
        return out

    def loss(self, parts_body, ss=2):
        r = self.render(parts_body, ss)
        tot = 0.0
        for (m, _), t in zip(r, self.masks):
            inter = (m & t).sum(); uni = (m | t).sum()
            tot += 1 - inter / max(uni, 1)
        return tot / 8
