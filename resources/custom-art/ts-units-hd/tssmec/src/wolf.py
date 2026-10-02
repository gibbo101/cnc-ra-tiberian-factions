"""
wolf.py - the Wolverine (TS [SMECH]) as convex parts, for fitting to TS's frames and for the HD renders.

Body frame: u forward, v right, w up; units = TS sprite px; the ground at w = 0.  TS's facing k (of 8, clockwise
from screen-up) turns the body so forward = (sin th, -cos th) (legfit.facing_matrix).

Parts (component ids):
  upper body: TORSO (the tan chest block), HEAD (the cockpit: a box, its top sloping down to the front), NECK (the
  dark recess between head and chest), PACK (the house-colour back panel), SHOULDER (the house-colour pads),
  ARM (the arms the guns hang from), GUN (the dark gun bodies), MUZZLE (their grey front ends), ANT (the black
  antenna), ANTBASE (its mount), LAMP (the orange lamp on the head's front-right corner)
  legs: PELVIS (dark), HIPJ (grey hip joints), THIGH, KNEE (grey), SHIN, ANKLE (grey), FOOT
"""
import numpy as np
import rc

TORSO, HEAD, NECK, PACK, SHOULDER, ARM, GUN, MUZZLE, ANT, ANTBASE, LAMP = 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51
PELVIS, HIPJ, THIGH, KNEE, SHIN, ANKLE, FOOT = 61, 62, 63, 64, 65, 66, 67

WAIST = 52
# colour classes for fitting: 1 tan, 2 dark material, 3 gun dark, 4 light metal, 5 house
CLASS = {TORSO: 1, WAIST: 1, HEAD: 1, NECK: 2, PACK: 5, SHOULDER: 5, ARM: 1, GUN: 3, MUZZLE: 4, ANT: 3, ANTBASE: 2,
         LAMP: 1, PELVIS: 2, HIPJ: 2, THIGH: 1, KNEE: 4, SHIN: 1, ANKLE: 4, FOOT: 1}

P0 = dict(
    # chest: u from tu0 to tu1, half width tv, w from tw0 to tw1, chamfer tch
    tu0=-3.6, tu1=3.0, tv=3.5, tw0=13.0, tw1=22.5, tch=0.8, tcb=1.0,
    # waist (below the chest, between the arms): u wu0..wu1, half width wv, w from ww0 up to the chest
    wu0=-2.6, wu1=2.4, wv=3.2, ww0=11.5,
    # head: u hu0..hu1, half width hv, centre offset hc (v), w hw0..hw1; the top slopes down by hs to the front
    # from u = hsu
    hu0=-3.2, hu1=3.6, hv=3.6, hcv=0.0, hw0=21.0, hw1=27.5, hs=2.6, hsu=-1.0,
    # neck: the dark band under the head's front (inset)
    nw=1.0,
    # back panel
    pu0=-5.2, pu1=-3.2, pv=3.6, pw0=15.0, pw1=24.5,
    # shoulders: u su0..su1, v from sv0 to sv1 (outward), w sw0..sw1
    su0=-2.2, su1=2.0, sv0=3.4, sv1=7.4, sw0=19.5, sw1=24.0, sch=0.8,
    # arms: hanging from the shoulders to the guns
    au0=-1.6, au1=1.6, av0=5.6, av1=7.8, aw0=13.5, aw1=20.0, agap=1.0,
    # guns: centre (v gv, w gw), from u gu0 to gu1, half sizes gh (across) gk (tall); muzzle length gm
    gv=7.6, gw=15.0, gu0=-3.6, gu1=6.6, gh=1.3, gk=1.3, gm=1.6,
    # antenna: at (anu, anv) from the head to antop; its mount box
    anu=-2.0, anv=4.2, antop=34.5,
    # pelvis
    pel_u0=-2.0, pel_u1=2.0, pel_v=3.2, pel_w0=9.5, pel_w1=13.0,
    # legs
    jv=4.0, jw=11.0, ju=0.0, splay=0.0, Lt=5.4, tw=3.4, td=3.6, Ls=5.0, sw=2.8, sd=3.0,
    lf=5.6, lh=2.8, fw=5.6, fh=2.2,
)


def leg_parts(side, a_t, a_s, a_f, P, dw=0.0):
    """side -1 left, +1 right; a_t, a_s: thigh and shin pitch from straight down (degrees, + = forward);
    a_f: foot pitch (+ = toe up)."""
    sp = np.deg2rad(P['splay']) * side
    J = np.array([P['ju'], side * P['jv'], P['jw'] + dw])

    def dirn(a):
        a = np.deg2rad(a)
        return np.array([np.sin(a), np.sin(sp) * np.cos(a), -np.cos(a) * np.cos(sp)])

    K = J + P['Lt'] * dirn(a_t)
    A = K + P['Ls'] * dirn(a_s)
    parts = [rc.seg_box(J, K, P['tw'], P['td'], THIGH, up=(1, 0, 0), chamfer=0.6, ext=0.8, name='thigh'),
             rc.seg_box(K, A, P['sw'], P['sd'], SHIN, up=(1, 0, 0), chamfer=0.5, ext=0.5, name='shin')]
    af = np.deg2rad(a_f)
    fwd = np.array([np.cos(af), 0.0, np.sin(af)])
    up = np.array([-np.sin(af), 0.0, np.cos(af)])
    side_ax = np.cross(up, fwd)
    Rf = np.stack([fwd, side_ax, up], axis=1)
    c = A + fwd * (P['lf'] - P['lh']) / 2 - up * P['fh'] / 2
    parts.append(rc.box(c, Rf, ((P['lf'] + P['lh']) / 2, P['fw'] / 2, P['fh'] / 2), FOOT, chamfer=(0.6, 0.6, 0.5),
                        name='foot'))
    lat = np.array([0, 1.0, 0])
    parts.append(rc.cylinder(K - lat * P['sw'] * 0.62, K + lat * P['sw'] * 0.62, P['sd'] * 0.45, KNEE, 'knee'))
    parts.append(rc.cylinder(A - lat * P['sw'] * 0.6, A + lat * P['sw'] * 0.6, P['sd'] * 0.4, ANKLE, 'ankle'))
    return parts, (J, K, A)


def upper_parts(P, dw=0.0):
    """the upper body (rigid): chest, head, back panel, shoulders, arms, guns, antenna, lamp; dw lifts it."""
    o = np.array([0, 0, dw])
    I = np.eye(3)
    out = []
    # chest: the narrower block under the head (the arms hang clear of it), from tw0 up into the head, its
    # front-bottom edge bevelled by tcb
    tw1 = P['hw0'] + 0.4
    c = np.array([(P['tu0'] + P['tu1']) / 2, 0, (P['tw0'] + tw1) / 2]) + o
    h = np.array([(P['tu1'] - P['tu0']) / 2, P['tv'], (tw1 - P['tw0']) / 2])
    chest = rc.box(c, I, h, TORSO, chamfer=(P['tch'], P['tch'], P['tch']), name='chest')
    if P.get('tcb', 0) > 0.05:
        n = np.array([1.0, 0, -1.0]) / np.sqrt(2)
        p = np.array([P['tu1'] - P['tcb'], 0, P['tw0'] + dw])
        chest.cons.append(rc.Plane(n, n @ p))
    out.append(chest)
    c = np.array([(P['wu0'] + P['wu1']) / 2, 0, (P['ww0'] + P['tw0'] + 0.5) / 2]) + o
    h = np.array([(P['wu1'] - P['wu0']) / 2, P['wv'], (P['tw0'] + 0.5 - P['ww0']) / 2])
    out.append(rc.box(c, I, h, WAIST, chamfer=(0.6, 0.6, 0.6), name='waist'))
    # head with its sloping top
    c = np.array([(P['hu0'] + P['hu1']) / 2, P['hcv'], (P['hw0'] + P['hw1']) / 2]) + o
    h = np.array([(P['hu1'] - P['hu0']) / 2, P['hv'], (P['hw1'] - P['hw0']) / 2])
    head = rc.box(c, I, h, HEAD, chamfer=(0.5, 0.5, 0.5), name='head')
    du = P['hu1'] - P['hsu']
    if du > 0.2 and P['hs'] > 0.05:
        n = np.array([P['hs'], 0, du]); n = n / np.linalg.norm(n)
        p = np.array([P['hsu'], 0, P['hw1'] + dw])
        head.cons.append(rc.Plane(n, n @ p))
    out.append(head)
    # neck: a dark block under the head, inset from its front and sides
    c = np.array([(P['hu0'] + P['hu1']) / 2 - 0.4, P['hcv'], P['hw0'] - P['nw'] / 2 + 0.3]) + o
    out.append(rc.box(c, I, ((P['hu1'] - P['hu0']) / 2 - 0.5, P['hv'] - 0.4, P['nw'] / 2 + 0.3), NECK, name='neck'))
    # back panel
    c = np.array([(P['pu0'] + P['pu1']) / 2, 0, (P['pw0'] + P['pw1']) / 2]) + o
    out.append(rc.box(c, I, ((P['pu1'] - P['pu0']) / 2, P['pv'], (P['pw1'] - P['pw0']) / 2), PACK, chamfer=(0.4, 0.4, 0.4),
                      name='pack'))
    for s in (-1, 1):
        # shoulder pad
        c = np.array([(P['su0'] + P['su1']) / 2, s * (P['sv0'] + P['sv1']) / 2, (P['sw0'] + P['sw1']) / 2]) + o
        pad = rc.box(c, I, ((P['su1'] - P['su0']) / 2, (P['sv1'] - P['sv0']) / 2, (P['sw1'] - P['sw0']) / 2),
                     SHOULDER, chamfer=(0.6, 0.6, 0.6), name='shoulder')
        if P.get('sch', 0) > 0.05:                       # the pad's top-outer edge sloping down and out
            n = np.array([0, s * 1.0, 1.0]) / np.sqrt(2)
            p = np.array([0, s * (P['sv1'] - P['sch']), P['sw1'] + dw])
            pad.cons.append(rc.Plane(n, n @ p))
        out.append(pad)
        # arm: hanging clear of the chest (its inner face agap outside the chest's side)
        av0 = P['tv'] + P.get('agap', 0.6)
        c = np.array([(P['au0'] + P['au1']) / 2, s * (av0 + P['av1']) / 2, (P['aw0'] + P['aw1']) / 2]) + o
        out.append(rc.box(c, I, ((P['au1'] - P['au0']) / 2, max(P['av1'] - av0, 0.6) / 2, (P['aw1'] - P['aw0']) / 2),
                          ARM, chamfer=(0.5, 0.5, 0.5), name='arm'))
        # gun body and muzzle
        gm = P['gm']
        c = np.array([(P['gu0'] + P['gu1'] - gm) / 2, s * P['gv'], P['gw']]) + o
        out.append(rc.box(c, I, ((P['gu1'] - gm - P['gu0']) / 2, P['gh'], P['gk']), GUN, chamfer=(0.4, 0.4, 0.4),
                          name='gun'))
        c = np.array([P['gu1'] - gm / 2, s * P['gv'], P['gw']]) + o
        out.append(rc.box(c, I, (gm / 2, P['gh'] * 0.85, P['gk'] * 0.85), MUZZLE, chamfer=(0.3, 0.3, 0.3), name='muzzle'))
    # antenna and its mount
    top = P['hw1'] + dw
    out.append(rc.cylinder((P['anu'], P['anv'], top - 2.0), (P['anu'], P['anv'], P['antop'] + dw), 0.5, ANT, 'antenna'))
    out.append(rc.box((P['anu'], P['anv'], top - 1.6), I, (0.9, 0.9, 1.6), ANTBASE, name='antbase'))
    return out


def lower_static(P, dw=0.0):
    c = np.array([(P['pel_u0'] + P['pel_u1']) / 2, 0, (P['pel_w0'] + P['pel_w1']) / 2 + dw])
    pel = rc.box(c, np.eye(3), ((P['pel_u1'] - P['pel_u0']) / 2, P['pel_v'], (P['pel_w1'] - P['pel_w0']) / 2), PELVIS,
                 chamfer=(0.6, 0.6, 0.6), name='pelvis')
    out = [pel]
    for s in (-1, 1):
        J = np.array([P['ju'], s * P['jv'], P['jw'] + dw])
        out.append(rc.cylinder(J - np.array([0, s * 1.2, 0]), J + np.array([0, s * 1.8, 0]), 1.6, HIPJ, 'hipjoint'))
    return out


def body_turn(P, pose):
    """the body's sway in a pose: (R, pivot) - roll (pose[7], + = right side down) and pitch (pose[8], + = nose
    down), in degrees, about the hips' centre; none if the pose has no sway."""
    roll = pose[7] if len(pose) > 7 else 0.0
    pitch = pose[8] if len(pose) > 8 else 0.0
    if abs(roll) < 1e-9 and abs(pitch) < 1e-9:
        return None
    R = rc.rot_y(np.deg2rad(pitch)) @ rc.rot_x(np.deg2rad(roll))
    pivot = np.array([P['ju'], 0.0, P['jw'] + pose[6]])
    return R, pivot


def body_parts(P, pose, upper=True):
    """pose: (left a_t, a_s, a_f, right a_t, a_s, a_f, dw[, roll, pitch]).  The upper body and the pelvis sway
    together about the hips' centre; the legs hang from the swayed hip joints."""
    dw = pose[6]
    turn = body_turn(P, pose)
    lp, rp = legs_of(P, pose, turn)
    body = lower_static(P, dw) + (upper_parts(P, dw) if upper else [])
    if turn is not None:
        R, pv = turn
        body = [p.moved(R, pv - R @ pv) for p in body]
    if not upper:
        return body + lp + rp
    n_up = len(upper_parts(P, dw))
    return body[len(body) - n_up:] + body[:len(body) - n_up] + lp + rp


def legs_of(P, pose, turn=None):
    """both legs' parts; with a sway, each leg is built at its swayed hip joint."""
    out = []
    for side, ang in ((-1, pose[0:3]), (1, pose[3:6])):
        parts, (J, K, A) = leg_parts(side, *ang, P, pose[6])
        if turn is not None:
            R, pv = turn
            J2 = pv + R @ (J - pv)
            parts = [p.moved(np.eye(3), J2 - J) for p in parts]
        out.append(parts)
    return out


def facing_matrix(k, nfac=8):
    th = 2 * np.pi * k / nfac
    f = np.array([np.sin(th), -np.cos(th), 0.0]); r = np.array([np.cos(th), np.sin(th), 0.0])
    return np.stack([f, r, np.array([0, 0, 1.0])], axis=1)


def soles(P, pose):
    out = []
    turn = body_turn(P, pose)
    for side, (a_t, a_s, a_f) in ((-1, pose[0:3]), (1, pose[3:6])):
        _, (J, K, A) = leg_parts(side, a_t, a_s, a_f, P, pose[6])
        if turn is not None:
            R, pv = turn
            A = A + (pv + R @ (J - pv) - J)
        af = np.deg2rad(a_f)
        fwd = np.array([np.cos(af), 0.0, np.sin(af)]); up = np.array([-np.sin(af), 0.0, np.cos(af)])
        toe = A + fwd * P['lf'] - up * P['fh']; heel = A - fwd * P['lh'] - up * P['fh']
        out.append(min(toe[2], heel[2]))
    return out
