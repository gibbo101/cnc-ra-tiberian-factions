"""
jugg.py - the Juggernaut (Firestorm [JUGG]) walker as convex parts, for fitting to TS's JUGGER frames and for the HD
renders.

Body frame: u forward, v right, w up; units = TS sprite px; the ground at w = 0.  TS's facing k (of 8, clockwise from
screen-up) turns the body so forward = (sin th, -cos th) (facing_matrix).

Parts (component ids):
  SHELL (the house-colour body, its back rounded), HATCH (the light grey roof block), SLOT (its dark slot), PACK (the
  khaki barrel housing at the front), BARREL (the three khaki barrels), MUZZLE (their grey ends), ANT (the house-colour
  spike at the back), HIP (the dark block under the body), THIGH, KNEE, SHIN, ANKLE, FOOT
"""
import numpy as np
import rc

SHELL, HATCH, SLOT, PACK, BARREL, MUZZLE, ANT, ARCH, CABLE = 71, 72, 73, 74, 75, 76, 77, 79, 80
HIP, THIGH, KNEE, SHIN, ANKLE, FOOT = 81, 82, 83, 84, 85, 86

# fitting classes: 1 house, 2 light grey, 3 khaki, 4 tan (the legs), 5 dark
CLASS = {SHELL: 1, ANT: 1, ARCH: 1, CABLE: 2, HATCH: 2, MUZZLE: 2, SLOT: 5, PACK: 3, BARREL: 3, HIP: 5, THIGH: 4, KNEE: 5, SHIN: 4,
         ANKLE: 5, FOOT: 4}

P0 = dict(
    # shell: u bu0 (back) .. bu1 (front), half width bv, w bw0 .. bw1; its back rounded (an ellipse across the body,
    # br its height over the shell's half height); its top side edges chamfered by bch
    bu0=-17.0, bu1=4.5, bv=10.0, bw0=16.0, bwb=22.0, bw1=29.0, br=1.25, bch=1.0,
    # hatch on the roof: u hu0..hu1, half width hv, hh tall; its front sloping by hs
    hu0=-11.5, hu1=2.5, hv=7.0, hh=2.0, hs=1.0,
    # barrel pack at the front: u pu0..pu1, half width pv, w pw0..pw1
    pu0=4.0, pu1=9.5, pv=6.5, pw0=17.0, pw1=25.0,
    # barrels: three, spaced bs apart across, at height bz, radius brad, from the pack's front to bl long; muzzles ml
    bs=4.4, bz=21.5, brad=2.3, bl=8.0, ml=3.0, mh=2.4,
    # the hatch's slot: so above the roof, sh tall
    so=1.0, sh=0.8,
    # the sensor at the roof's back corner: 0 TS's house-colour box with its dark core (v1, v2); 2 the HD Titan's
    # antenna in its place (Luke, v2.1: "remove the box and go for a Titan-esque antenna")
    anu=-14.0, anv=-3.3, anh=4.6, anr=1.5, sensor=2.0,
    # the arch over the pack: from au0 (roof) to au1 (pack top), its peak ah above the roof, at av across
    arch=1.0, au0=2.2, au1=9.5, ah=3.0, av=0.0,
    # hip block under the shell
    hp_u0=-6.0, hp_u1=4.0, hp_v=6.0, hp_w0=14.0,
    # legs
    jv=6.5, jw=16.0, ju=-1.0, Lt=8.0, tw=4.0, td=4.5, Ls=8.0, sw=3.5, sd=4.0, lf=6.0, lh=3.0, fw=5.5, fh=2.5,
)


def shell_part(P, dw=0.0):
    c = np.array([(P['bu0'] + P['bu1']) / 2, 0, (P['bw0'] + P['bw1']) / 2 + dw])
    h = np.array([(P['bu1'] - P['bu0']) / 2, P['bv'], (P['bw1'] - P['bw0']) / 2])
    cons = rc.box_planes(c, np.eye(3), h, chamfer=(0.0, 0.0, 0.0))
    # the belly slopes: the shell comes down to bw0 at the front (its cheeks either side of the barrel pack) and only
    # to bwb at the back
    if P.get('bwb', P['bw0']) > P['bw0'] + 0.05:
        d = (P['bwb'] - P['bw0']) / (P['bu1'] - P['bu0'])
        n = np.array([-d, 0.0, -1.0]); n = n / np.linalg.norm(n)
        p = np.array([P['bu1'], 0.0, P['bw0'] + dw])
        cons.append(rc.Plane(n, n @ p))
    # top side edges chamfered (the shell's shoulders)
    for s in (-1.0, 1.0):
        n = np.array([0, s, 1.0]) / np.sqrt(2)
        p = np.array([0, s * P['bv'], P['bw1'] - P['bch'] + dw])
        cons.append(rc.Plane(n, n @ p))
    # the back rounded: an elliptic cylinder across the body (an ellipsoid with a huge radius across), centred on the
    # front face at mid-height and reaching back to bu0: the back curves round from the roof to the belly, the front
    # half stays square.  br > 1 widens the ellipse's height so the curve starts further back.
    cw = (P['bw0'] + P['bw1']) / 2 + dw
    cons.append(rc.Ellip(np.array([P['bu1'], 0, cw]), np.eye(3),
                         np.array([P['bu1'] - P['bu0'], 1000.0, (P['bw1'] - P['bw0']) / 2 * P['br']])))
    return rc.Part(cons, SHELL, 'shell', sphere=(c, float(np.linalg.norm(h)) + 1e-3))


def upper_parts(P, dw=0.0):
    """the rigid upper body: shell, hatch, pack, barrels, muzzles, antenna; dw lifts it."""
    o = np.array([0, 0, dw]); I = np.eye(3)
    out = [shell_part(P, dw)]
    c = np.array([(P['hu0'] + P['hu1']) / 2, 0, P['bw1'] + P['hh'] / 2]) + o
    hatch = rc.box(c, I, ((P['hu1'] - P['hu0']) / 2, P['hv'], P['hh'] / 2 + 0.3), HATCH, chamfer=(0.4, 0.4, 0.4),
                   name='hatch')
    if P['hs'] > 0.05:
        n = np.array([P['hh'], 0, P['hs']]); n = n / np.linalg.norm(n)
        p = np.array([P['hu1'] - P['hs'], 0, P['bw1'] + P['hh']]) + o
        hatch.cons.append(rc.Plane(n, n @ p))
    out.append(hatch)
    # the hatch's dark slot: a thin band round it, so above its foot
    c = np.array([(P['hu0'] + P['hu1']) / 2, 0, P['bw1'] + P['so'] + P['sh'] / 2]) + o
    out.append(rc.box(c, I, ((P['hu1'] - P['hu0']) / 2 - P['hs'] * 0.5 + 0.15, P['hv'] + 0.15, P['sh'] / 2), SLOT,
                      name='slot'))
    c = np.array([(P['pu0'] + P['pu1']) / 2, 0, (P['pw0'] + P['pw1']) / 2]) + o
    out.append(rc.box(c, I, ((P['pu1'] - P['pu0']) / 2, P['pv'], (P['pw1'] - P['pw0']) / 2), PACK,
                      chamfer=(0.6, 0.6, 0.6), name='pack'))
    for k in (-1, 0, 1):
        a = np.array([P['pu1'] - 0.5, k * P['bs'], P['bz']]) + o
        b = np.array([P['pu1'] + P['bl'], k * P['bs'], P['bz']]) + o
        out.append(rc.cylinder(a, b, P['brad'], BARREL, 'barrel'))
        # the muzzle: a square grey block on the barrel's end (TS draws a blocky grey brake)
        c = b + np.array([P['ml'] / 2, 0, 0])
        out.append(rc.box(c, I, (P['ml'] / 2, P['mh'], P['mh']), MUZZLE, chamfer=(0.3, 0.3, 0.3), name='muzzle'))
        if P.get('mslots', 0) > 0.5:
            # the muzzle brake's two slots (JUGGER CW2: darker columns 2 and 4 px from the muzzle's back)
            for fr in (0.42, 0.78):
                out.append(rc.box(b + np.array([P['ml'] * fr, 0, 0]), I, (0.22, P['mh'] + 0.06, P['mh'] + 0.06),
                                  MSLOT, name='mslot'))
    # the sensor: a small house-colour box standing on the roof's back corner (TS draws it with a dark core); v2.1:
    # the Titan's antenna in its place (antenna_parts)
    if P.get('sensor', 0) >= 1.5:
        out += antenna_parts(P, dw)
    else:
        a = np.array([P['anu'], P['anv'], P['bw1'] - 0.5]) + o
        out.append(rc.box(a + np.array([0, 0, P['anh'] / 2]), I, (P['anr'], P['anr'], P['anh'] / 2 + 0.5), ANT,
                          name='sensor'))
    if P.get('arch', 1.0) > 0.5:
        # the arch: a thin house-colour hoop along the centre line, from the roof at the hatch's front over to the
        # barrel pack's top (two straight runs up to its peak), and a grey cable from its front foot along the pack
        y = P['av']
        b0 = np.array([P['au0'], y, P.get('aw0', P['bw1'])]) + o
        b1 = np.array([P['au1'], y, P.get('aw1', P['pw1'])]) + o
        if P.get('side_arches', 0) > 0.5:
            # two hoops, one each side of the body's front (JUGGER's diagonal and side views show the far one rising
            # over the body: CW1 at the left, CW7 at the right, CW2 over the hatch's front): each leaves the roof's
            # edge by the hatch's front, peaks ah over the roof and comes down onto the outer housing's top
            n = 8
            for sg in (-1.0, 1.0):
                a0 = np.array([P['au0'], sg * (P['bv'] - 0.35), P.get('aw0', P['bw1'])]) + o
                a1 = np.array([P['au1'], sg * P.get('av1', P['bv'] - 0.35), P.get('aw1', P['pw1'])]) + o
                mid = (a0[2] + a1[2]) / 2
                H = (P['bw1'] + P['ah'] + o[2]) - mid
                pts = [a0 + (a1 - a0) * s_ + np.array([0, 0, 4 * s_ * (1 - s_) * H]) for s_ in np.linspace(0, 1, n + 1)]
                for a_, b_ in zip(pts[:-1], pts[1:]):
                    out.append(rc.seg_box(a_, b_, 0.9, 0.9, ARCH, up=(0, 0, 1.0), ext=0.25, name='arch'))
                if P.get('cl', 0.0) > 0:
                    e = a1 + np.array([P['cl'], 0, -0.3])
                    out.append(rc.cylinder(a1, e, 0.45, CABLE, 'cable'))
            return out
        if P.get('round_arch', 0) > 0.5:
            # a smooth hoop: a parabola from b0 to b1 peaking ah over the roof at its middle
            n = 8
            mid = (b0[2] + b1[2]) / 2
            H = (P['bw1'] + P['ah'] + o[2]) - mid
            pts = [b0 + (b1 - b0) * s_ + np.array([0, 0, 4 * s_ * (1 - s_) * H]) for s_ in np.linspace(0, 1, n + 1)]
            for a_, b_ in zip(pts[:-1], pts[1:]):
                out.append(rc.seg_box(a_, b_, 0.9, 0.9, ARCH, up=(0, 0, 1.0), ext=0.25, name='arch'))
        else:
            pk = np.array([(P['au0'] + P['au1']) / 2, y, P['bw1'] + P['ah']]) + o
            out.append(rc.seg_box(b0, pk, 0.9, 0.9, ARCH, up=(0, 0, 1.0), ext=0.3, name='arch'))
            out.append(rc.seg_box(pk, b1, 0.9, 0.9, ARCH, up=(0, 0, 1.0), ext=0.3, name='arch'))
        e = np.array([P.get('cu', P['pu1'] + P['bl'] * 0.8), y, P.get('cw', P['pw1'] - 0.2)]) + o
        out.append(rc.cylinder(b1, e, 0.45, CABLE, 'cable'))
    return out


RECESS, HSLIT, SCORE, MSLOT = 87, 88, 89, 90
CLASS.update({RECESS: 5, HSLIT: 5, SCORE: 5, MSLOT: 5})
# the antenna (Luke, v2.1: "remove the box and go for a Titan-esque antenna"): the HD Titan's (titan/torso2.py: a plain
# black rod 0.45 px in radius standing 16 px above its shell), on the spot of TS's box at the roof's back corner
# (ids clear of jbase.py's 91-95, jtlegs.py's 111-119 and jdeprender.py's 300-301)
ANTENNA = 123
CLASS.update({ANTENNA: 5})
ANT_R = 0.45
ANT_L = 7.5             # above the roof: short enough to hide in a TS war factory's bay behind the shut door


def roof_at(P, u, v, dw=0.0):
    """the shell's top at (u, v): a ray straight down onto it (the roof curves down towards the back)."""
    t, who, _ = rc.cast([shell_part(P, dw)], np.array([[u, v, 200.0]]), np.array([0, 0, -1.0]), want_normals=False)
    return 200.0 - float(t[0])


ANT_BACK, ANT_OUT = 2.5, 1.2   # Luke: off the edge, into the house colour: 2.5 px behind the hatch's back left corner
                               # and 1.2 px out from its side (the walker: u -10.5, v -7.5, 2.9 px in from the body's
                               # side and clear of the roof's curve down at the back); the cabin the same against its hatch


def antenna_parts(P, dw=0.0):
    """the Titan's antenna standing on the roof just in from its back left corner, its foot inside the shell."""
    u, v = P['hu0'] - ANT_BACK, -(P['hv'] + ANT_OUT)
    top = roof_at(P, u, v, dw) + ANT_L
    return [rc.cylinder((u, v, P['bw1'] - 2.0 + dw), (u, v, top), ANT_R, ANTENNA, 'antenna')]


def details(P, dw=0.0):
    """the small dark details TS draws on the body (read from DJUGG_A's and JUGGER's frames, the same body in both):
    a dark panel in the hatch's top towards its front (from 2 px behind its front edge, 5 px long, 5 px wide, centred
    across), a dark slit across the hatch's front face at mid height, and the sensor's dark core (a dark stripe
    down the middle of each of its sides)."""
    o = np.array([0, 0, dw]); I = np.eye(3)
    L = P['hu1'] - P['hu0']
    top = P['bw1'] + P['hh'] + 0.3                      # the hatch box's top (see upper_parts)
    u0, u1 = P['hu1'] - P.get('rf0', 0.574) * L, P['hu1'] - P.get('rf1', 0.164) * L
    rv = P.get('rvf', 0.375) * P['hv']
    out = [rc.box(np.array([(u0 + u1) / 2, 0, top - 0.03]) + o, I, ((u1 - u0) / 2, rv, 0.07), RECESS, name='recess')]
    # the slit: on the front face (sloped back by hs over the hatch's height) at mid height
    wm = P['bw1'] + P['hh'] * 0.5
    uf = P['hu1'] - P['hs'] + P['hs'] * (P['bw1'] + P['hh'] - wm) / max(P['hh'], 1e-3)
    out.append(rc.box(np.array([uf - 0.1, 0, wm]) + o, I, (0.16, P['hv'] * 0.85, max(P['hh'] * 0.17, 0.25)), HSLIT,
                      name='slit'))
    # the sensor's dark core (the electronics box has its vents instead)
    if P.get('sensor', 0) < 0.5:
        a = np.array([P['anu'], P['anv'], P['bw1'] - 0.5 + P['anh'] / 2 - 0.25]) + o
        r = P['anr']
        out.append(rc.box(a, I, (r + 0.03, r * 0.38, P['anh'] / 2 + 0.2), SCORE, name='core'))
        out.append(rc.box(a, I, (r * 0.38, r + 0.03, P['anh'] / 2 + 0.2), SCORE, name='core'))
    return out


def lower_static(P, dw=0.0):
    c = np.array([(P['hp_u0'] + P['hp_u1']) / 2, 0, (P['hp_w0'] + P['bw0'] + 0.5) / 2 + dw])
    h = ((P['hp_u1'] - P['hp_u0']) / 2, P['hp_v'], (P['bw0'] + 0.5 - P['hp_w0']) / 2)
    return [rc.box(c, np.eye(3), h, HIP, chamfer=(0.6, 0.6, 0.6), name='hip')]


def leg_parts(side, a_t, a_s, a_f, P, dw=0.0):
    """side -1 left, +1 right; a_t, a_s: thigh and shin pitch from straight down (degrees, + = forward); a_f: the
    foot's pitch (+ = toe up)."""
    J = np.array([P['ju'], side * P['jv'], P['jw'] + dw])

    def dirn(a):
        a = np.deg2rad(a)
        return np.array([np.sin(a), 0.0, -np.cos(a)])

    K = J + P['Lt'] * dirn(a_t)
    A = K + P['Ls'] * dirn(a_s)
    parts = [rc.seg_box(J, K, P['tw'], P['td'], THIGH, up=(1, 0, 0), chamfer=0.6, ext=0.8, name='thigh'),
             rc.seg_box(K, A, P['sw'], P['sd'], SHIN, up=(1, 0, 0), chamfer=0.5, ext=0.5, name='shin')]
    af = np.deg2rad(a_f)
    fwd = np.array([np.cos(af), 0.0, np.sin(af)]); up = np.array([-np.sin(af), 0.0, np.cos(af)])
    Rf = np.stack([fwd, np.cross(up, fwd), up], axis=1)
    c = A + fwd * (P['lf'] - P['lh']) / 2 - up * P['fh'] / 2
    parts.append(rc.box(c, Rf, ((P['lf'] + P['lh']) / 2, P['fw'] / 2, P['fh'] / 2), FOOT, chamfer=(0.6, 0.6, 0.5),
                        name='foot'))
    lat = np.array([0, 1.0, 0])
    parts.append(rc.cylinder(K - lat * P['sw'] * 0.62, K + lat * P['sw'] * 0.62, P['sd'] * 0.45, KNEE, 'knee'))
    parts.append(rc.cylinder(A - lat * P['sw'] * 0.6, A + lat * P['sw'] * 0.6, P['sd'] * 0.4, ANKLE, 'ankle'))
    return parts, (J, K, A)


def soles(P, pose):
    out = []
    for side, (a_t, a_s, a_f) in ((-1, pose[0:3]), (1, pose[3:6])):
        _, (J, K, A) = leg_parts(side, a_t, a_s, a_f, P, pose[6])
        af = np.deg2rad(a_f)
        fwd = np.array([np.cos(af), 0.0, np.sin(af)]); up = np.array([-np.sin(af), 0.0, np.cos(af)])
        toe = A + fwd * P['lf'] - up * P['fh']; heel = A - fwd * P['lh'] - up * P['fh']
        out.append(min(toe[2], heel[2]))
    return out


def body_parts(P, pose):
    """pose: (left a_t, a_s, a_f, right a_t, a_s, a_f, dw)."""
    dw = pose[6]
    out = upper_parts(P, dw) + lower_static(P, dw)
    for side, ang in ((-1, pose[0:3]), (1, pose[3:6])):
        out += leg_parts(side, *ang, P, dw)[0]
    return out


def facing_matrix(k, nfac=8):
    th = 2 * np.pi * k / nfac
    f = np.array([np.sin(th), -np.cos(th), 0.0]); r = np.array([np.cos(th), np.sin(th), 0.0])
    return np.stack([f, r, np.array([0, 0, 1.0])], axis=1)
