"""
jtlegs.py - the Titan's legs on the Juggernaut (Luke: "use the Titan's legs").  TS's JUGGER walk frames draw the
Titan's own leg sprite (MMCH's walk frames 0-119: below the Juggernaut's body every pixel is MMCH's, 3 TS px higher
in the frame) and TS's deployed base (DJUGG) draws MMCH's dome as the pivot the cabin turns on, so the walker here
stands on the HD Titan's legs as signed off (titan/legfit.py, titan/gait.py, titan/titanmat.py, titan/legs_final.json,
copied here as titan_legs.json): its thighs, knees with their spurs, shins and split-toed feet, its waist (the pelvis
with the round hip joints the thighs hang from, the bearing ring and the dome, under the body), its paint, and its
walk (a smooth gait fitted to all 120 of TS's walk frames), sampled at TS's 15 steps (step s = phase 2 pi s / 15).

Units and axes as jugg.py's (TS sprite px; u forward, v right, w up; the ground at w = 0).  The Titan's fit put its
frame's origin at TS (47.4, 55) in MMCH's frames with its ground at w = g; JUGGER's legs are MMCH's 3 px higher and
the Juggernaut's origin is at TS (47.47, 48.22) in JUGGER's frames, so the same legs stand (52 - 48.22) / cos 30 =
4.36 px lower here, their soles 0.39 px under the Juggernaut's ground (a third of a TS pixel; the walk's silhouette
overlap with TS's is flat over that range: 0.807 to 0.809).  They are set DW = -g lower, soles on the ground.
"""
import json, os
import numpy as np
import rc
import walls2 as W
from walls2 import smoothstep

HERE = os.path.dirname(os.path.abspath(__file__))
# component ids clear of jugg.py's (71-90), jbase.py's (91-95) and jdeprender.py's (300, 301)
TTHIGH, TSHIN, TFOOT, TSPUR, TJOINT, THIPJ, TPELVIS, TRING, TDOME = 111, 112, 113, 114, 115, 116, 117, 118, 119
COMPS = (TTHIGH, TSHIN, TFOOT, TSPUR, TJOINT, THIPJ, TPELVIS, TRING, TDOME)
LEG_COMPS = (TTHIGH, TSHIN, TFOOT, TSPUR, TJOINT)                 # lit on their own, as TS's leg sprite
WAIST_COMPS = (THIPJ, TPELVIS, TRING, TDOME)                      # under the body, in its shadow (the Titan's)
GOLD_COMPS = (TTHIGH, TSHIN, TFOOT)                               # the Titan's highlight
# fitting classes (jfit): 4 tan (the legs), 5 dark (TS's dark dome and joints)
CLASS = {TTHIGH: 4, TSHIN: 4, TFOOT: 4, TSPUR: 5, TJOINT: 5, THIPJ: 5, TPELVIS: 5, TRING: 5, TDOME: 5}
NSTEPS = 15


# ------------------------------------------------------------------ the Titan's gait (titan/gait.py)
NH, NB = 3, 1


def basis(phi, nh=NH):
    cols = [np.ones_like(phi)]
    for n in range(1, nh + 1):
        cols += [np.cos(n * phi), np.sin(n * phi)]
    return np.stack(cols, -1)


def bob_basis(phi, nb=NB):
    cols = [np.ones_like(phi)]
    for n in range(1, nb + 1):
        cols += [np.cos(2 * n * phi), np.sin(2 * n * phi)]
    return np.stack(cols, -1)


class Gait:
    def __init__(self, coef, bob, phase0=0.0):
        self.coef = np.asarray(coef, float); self.bob = np.asarray(bob, float); self.phase0 = float(phase0)

    def pose(self, phi):
        """(lt, ls, lf, rt, rs, rf, dw) at walk phase phi (TS step s is phi = 2 pi s / 15)."""
        pl = phi + self.phase0
        L = basis(np.array([pl]))[0] @ self.coef.T
        R = basis(np.array([pl + np.pi]))[0] @ self.coef.T
        dw = bob_basis(np.array([pl]))[0] @ self.bob
        return [float(L[0]), float(L[1]), float(L[2]), float(R[0]), float(R[1]), float(R[2]), float(dw)]


def load(path=os.path.join(HERE, 'titan_legs.json')):
    js = json.load(open(path))
    S = js['S']
    g = js['gait']
    return S, Gait(g['coef'], g['bob'], g.get('phase0', 0.0))


S, GAIT = load()
DW = -S['g']                       # the Titan's legs in the Juggernaut's frame: soles on its ground (see above)
GROUND = S['g'] + DW               # 0


def step_pose(step, nsteps=NSTEPS):
    return GAIT.pose(2 * np.pi * step / nsteps)


# ------------------------------------------------------------------ the Titan's legs (titan/legfit.py, detail)
def leg_parts(side, a_t, a_s, a_f, S=S, dw=0.0):
    """side -1 left, +1 right; the Titan's knees bend backward (thigh back, shin forward); a_f the foot's pitch.
    In the Titan's own leg frame (ground at w = g)."""
    sp = np.deg2rad(S['splay']) * side
    J = np.array([S['ju'], side * S['jv'], S['jw'] + dw])

    def dirn(a):
        a = np.deg2rad(a)
        return np.array([np.sin(a), np.sin(sp) * np.cos(a), -np.cos(a) * np.cos(sp)])

    K = J + S['Lt'] * dirn(a_t)
    A = K + S['Ls'] * dirn(a_s)
    parts = [rc.seg_box(J, K, S['tw'], S['td'], TTHIGH, up=(1, 0, 0), chamfer=0.8, ext=1.0, name='thigh'),
             rc.seg_box(K, A, S['sw'], S['sd'], TSHIN, up=(1, 0, 0), chamfer=0.6, ext=0.6, name='shin')]
    ka = np.deg2rad(S.get('ka', 10.0))
    back = np.array([-np.cos(ka), 0.0, np.sin(ka)])
    ks = S.get('ks', 5.0)
    parts.append(rc.seg_box(K - back * 0.5, K + back * ks, S.get('kw', 3.0), S.get('kd', 2.4), TSPUR,
                            up=(0, 0, 1.0), chamfer=0.6, name='spur'))
    af = np.deg2rad(a_f)
    fwd = np.array([np.cos(af), 0.0, np.sin(af)])
    up = np.array([-np.sin(af), 0.0, np.cos(af)])
    side_ax = np.cross(up, fwd)
    Rf = np.stack([fwd, side_ax, up], axis=1)
    lf, lh, fw, fh = S['lf'], S['lh'], S['fw'], S['fh']
    x0, x1 = -lh, lf * 0.42
    c = A + fwd * (x0 + x1) / 2 - up * fh / 2
    parts.append(rc.box(c, Rf, ((x1 - x0) / 2, fw / 2, fh / 2), TFOOT, chamfer=(0.8, 0.8, 0.6), name='foot'))
    gap = min(0.7, fw * 0.12)
    tw = (fw - gap) / 2
    for sgn in (-1, 1):
        cy = sgn * (gap / 2 + tw / 2)
        tx0, tx1 = lf * 0.3, lf
        c = A + fwd * (tx0 + tx1) / 2 + side_ax * cy - up * fh * 0.55
        toe = rc.box(c, Rf, ((tx1 - tx0) / 2, tw / 2, fh * 0.45), TFOOT, chamfer=(0.7, 0.55, 0.5), name='toe')
        tip = A + fwd * tx1 - up * fh * 0.62; back_top = A + fwd * (tx0 + 0.6) - up * fh * 0.1
        dvec = tip - back_top; nrm = np.cross(side_ax, dvec); nrm = nrm / np.linalg.norm(nrm)
        if nrm @ up < 0:
            nrm = -nrm
        toe.cons.append(rc.Plane(nrm, nrm @ tip))
        parts.append(toe)
    lat = np.array([0, 1.0, 0])
    for P_, r_, w_ in ((K, S['sd'] * 0.42, S['sw'] * 0.62), (A, S['sd'] * 0.38, S['sw'] * 0.6)):
        parts.append(rc.cylinder(P_ - lat * w_, P_ + lat * w_, r_, TJOINT, 'joint'))
    return parts, (J, K, A)


def waist_parts(S=S, dw=0.0, joints=(-1, 1)):
    """the Titan's waist (titan/legfit.py hip_parts, detail): a chamfered pelvis block with round hip joints at its
    sides where the thighs hang (those of the sides in joints: -1 left, +1 right), the grey bearing ring on it and the
    rounded dome above.  In the Titan's leg frame."""
    cu = S['hip_c'][0]
    jw = S['jw'] + dw
    top = jw + 4.4
    out = [rc.box((cu, 0.0, (jw - 1.4 + top) / 2), np.eye(3), (5.6, 6.2, (top - jw + 1.4) / 2), TPELVIS,
                  chamfer=(1.9, 1.4, 1.4), name='pelvis'),
           rc.cylinder((cu, 0.0, top - 0.25), (cu, 0.0, top + 0.95), 6.3, TRING, 'ring'),
           rc.Part([rc.Ellip((cu, 0.0, top + 0.6), np.eye(3), (5.5, 5.9, 6.4)), rc.Plane((0, 0, -1.0), -(top + 0.6))],
                   TDOME, 'hipdome', sphere=(np.array([cu, 0.0, top + 0.6]), 6.5))]
    for side in joints:
        J = np.array([S['ju'], side * S['jv'], jw])
        out.append(rc.cylinder(J - np.array([0, side * 1.6, 0]), J + np.array([0, side * 2.4, 0]), 2.35, THIPJ,
                               'hipjoint'))
    return out


def tag(parts, M=None, t=None):
    """give parts their texture frame (M, t): the frame their materials read (r.lu, r.lv, r.lw), here the Titan's leg
    frame; move() carries it along."""
    M = np.eye(3) if M is None else np.asarray(M, float)
    t = np.zeros(3) if t is None else np.asarray(t, float)
    for p in parts:
        p.lframe = (M, t)
    return parts


def move(parts, R, t=(0.0, 0.0, 0.0)):
    """rc's Part.moved for a list, keeping each part's texture frame."""
    R = np.asarray(R, float); t = np.asarray(t, float)
    out = []
    for p in parts:
        q = p.moved(R, t)
        f = getattr(p, 'lframe', None)
        if f is not None:
            q.lframe = (R @ f[0], R @ f[1] + t)
        out.append(q)
    return out


def frames_of(parts):
    """RCRender's frames: each part's texture frame (the world's for parts without one)."""
    return [getattr(p, 'lframe', (np.eye(3), np.zeros(3))) for p in parts]


def waist(pose, S=S, joints=()):
    """the waist alone (pelvis, ring, dome; and the hip joints of the sides in joints) at a gait pose, in the
    Juggernaut's frame."""
    return move(tag(waist_parts(S, pose[6], joints)), np.eye(3), (0.0, 0.0, DW))


def dome_centre(pose, S=S):
    """the centre of the dome's base (on the bearing ring), in the Juggernaut's frame."""
    return np.array([S['hip_c'][0], 0.0, S['jw'] + 5.0 + pose[6] + DW])


def legs(pose, S=S, waist=True, joints=(-1, 1)):
    """the two legs (with the hip joints of the sides in joints, and the waist) at a gait pose (lt, ls, lf, rt, rs, rf,
    dw), in the Juggernaut's frame."""
    dw = pose[6]
    out = [p for p in waist_parts(S, dw, joints) if waist or p.comp == THIPJ]
    for side, ang in ((-1, pose[0:3]), (1, pose[3:6])):
        out += leg_parts(side, *ang, S, dw)[0]
    return move(tag(out), np.eye(3), (0.0, 0.0, DW))


# ------------------------------------------------------------------ the Titan's paint (titan/titanmat.py, legs)
GOLD = np.array([208, 162, 70.])              # the Titan's own yellow-brown paint (TS's ochre ramp)
OLIVE = np.array([84, 76, 52.])
STEEL = np.array([150, 152, 160.])
STEEL_D = np.array([78, 79, 84.])
GRIME = np.array([112, 104, 78.])


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


def phase(v, per, off=0.0):
    return np.abs(np.mod(v - off + per / 2, per) - per / 2)


def grain_local(r, scale=1 / 1.5):
    """titanmat's grain: walls2's, sampled triplanar in the legs' own frame (r.lu, r.lv, r.lw = the Titan's leg
    frame), so it turns with them as on the Titan."""
    X, Y, Z = r.lu * 6.4 * scale, r.lv * 6.4 * scale, r.lw * 6.4 * scale
    ax, ay, az = np.abs(r.nx) + 1e-3, np.abs(r.ny) + 1e-3, np.abs(r.nz) + 1e-3
    s_ = ax + ay + az

    def tri(noise, o):
        return (W.sample(noise, Y + o, Z + 2 * o) * ax + W.sample(noise, X + 3 * o, Z + o) * ay +
                W.sample(noise, X + o, Y + 5 * o) * az) / s_
    return tri(W.NOISE_FINE, 0) * 0.035 + tri(W.NOISE_MOTTLE, 17) * 0.05


def along(r, name):
    """for hits on parts called `name` (seg_box parts): the position along the part's length, 0..1."""
    t = np.zeros(r.x.shape, np.float32)
    for i, p in enumerate(r.parts):
        if p.name != name:
            continue
        m = r.who == i
        if not m.any():
            continue
        n1 = p.cons[1].n; d1 = p.cons[1].d; d0 = -p.cons[0].d
        P = np.stack([r.x[m], r.y[m], r.z[m]], 1)
        t[m] = np.clip((P @ n1 - d0) / max(d1 - d0, 1e-6), 0, 1)
    return t


def materials(r, alb):
    """the Titan's leg and waist paint (titanmat.materials, legs) into alb, for the hits on the Titan's parts."""
    comp = r.comp
    if not np.isin(comp, COMPS).any():
        return alb
    grain = grain_local(r)
    g1 = (1 + 0.45 * grain)[..., None]
    lu, lv, lw = r.lu, r.lv, r.lw
    z = r.z
    nzl = r.nz
    top = nzl > 0.7
    spur_t = along(r, 'spur')
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])
    dust = smoothstep(4.0, 0.0, z) * 0.45
    thigh = comp == TTHIGH
    if thigh.any():
        put(thigh, GOLD * 0.92 * g1)
        put(thigh & (phase(lw, 2.4) < 0.12), GOLD * 0.6 * g1)            # the armour plate's edges down the thigh
    pel = comp == TPELVIS
    if pel.any():
        put(pel, GOLD * 0.95 * g1)
        put(pel & (np.abs(lv) < 0.18) & ~top, GOLD * 0.6 * g1)           # the seam down its front and back
    put(comp == TDOME, GOLD * 0.95 * g1)
    ring = comp == TRING
    if ring.any():
        put(ring, STEEL * 0.8 * g1)
        put(ring & (np.abs(nzl) < 0.3) & (phase(np.arctan2(lv, lu) * 3.0, 1.6) < 0.09), STEEL_D * g1)   # bolts
    put(comp == THIPJ, STEEL * 0.8 * g1)
    shin = comp == TSHIN
    if shin.any():
        put(shin, mix(GOLD * g1, GRIME, dust))
    foot = comp == TFOOT
    if foot.any():
        put(foot, mix(GOLD * 0.96 * g1, GRIME, dust))
        put(foot & (z < 0.5), mix(OLIVE * 0.8 * g1, GRIME, 0.4))         # a dark sole edge
    put(comp == TJOINT, STEEL * 0.8 * g1)
    spur = comp == TSPUR
    if spur.any():
        put(spur, STEEL * g1)
        put(spur & (spur_t > 0.72), STEEL_D * 0.6 * g1)                  # its dark tip
    return alb


def spec(r, comps=GOLD_COMPS, strength=0.28, power=22.0, shadow_extra=None):
    """the Titan's soft highlight on its gold (titanrender.spec)."""
    L = r.L; V = -r.cam.D
    Hh = (L + V) / np.linalg.norm(L + V)
    nh = np.clip(r.nx * Hh[0] + r.ny * Hh[1] + r.nz * Hh[2], 0, 1)
    sh = getattr(r, 'inshadow', 0.0)
    m = np.isin(r.comp, comps)
    out = (strength * nh ** power * (1 - 0.9 * sh) * m * 255.0)[..., None] * np.array([1.0, 0.86, 0.58])
    if shadow_extra is not None:
        out = out * (1 - shadow_extra)[..., None]
    return out
