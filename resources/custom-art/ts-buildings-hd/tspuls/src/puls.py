"""
TS EMP Pulse Cannon (NAPULS; TSPULS / TSPULST in the mod) as a model for hd.py, at TS's own size on its 2x2 foundation.

World: X east, Y south, units (1 cell = 128), origin at the centre of the 2x2 foundation, Z up.
Read from NAPULS / NAPULSMK / NAPULS_A in TS's own camera (the head's 32 facings give its shape all round; MK 12, before
the snow goes on, gives the base's):
  base   a squat concrete star: four sloping arms (gabled, a narrow flat strip along the top) out to near the
         foundation's corners, turned a little off the diagonals, over a low cone; TS draws it snowed over (snow theatre),
         the mod's art has no snow, so neither has this (a switch: snow=True)
  rim    a round collar at the top of the cone, the drum standing in it
  drum   the turntable: a house-green drum with two seams, a small house-green lamp at its foot (front left)
  head   NAPULS_A: the EMP cannon turning on the drum (32 facings), read from TS's 32 facings with Luke's two reference
         renders (CANNON): a box body with a light top, dark sides and a light back, its front top cut back; a short
         barrel out of its front with two coil rings and a muzzle (a dark bore, a pale ring at its back: TS's light ring);
         two slanted dark yoke plates from the drum up the body's sides, a light trunnion boss on each; a dark round tank
         under the body; two cables looping off the back down to the drum.  Raised 15 degrees about the trunnions
         (Luke's choice; TS's idle facings are level).  The hooded head before it (HEAD3, 'prim3') is kept as a switch.
Layouts: 'ts' (TS's camera) and 'ra' (RA's grid): the same model; the head's facing is measured from screen-up (north)
in each view, so a frame number means the same facing in both.
"""
import numpy as np
import hd
from radr import Acc, rod_interval, inbox
from dept import quad_interval

(BASE, ARM, RIM, CRATER, DRUM, SEAM, LIGHT, PIVOT, HOOD, HSIDE, HDARK, LEG, LENS, LENSC, PACK, PORT,
 SNOW) = range(1, 18)
# the cannon head (v2)
(BARREL, MZHI, MZLO, HBOX, YOKE, BOSS, TANK, CABLE, PISTON, TTABLE, RAIL) = range(18, 29)
DEBRIS, DEB_IN, DEB_BURNT = 40, 41, 42
HOUSE = {DRUM, SEAM, LIGHT}
HEAD = {PIVOT, HOOD, HSIDE, HDARK, LEG, LENS, LENSC, PACK, PORT,
        BARREL, MZHI, MZLO, HBOX, YOKE, BOSS, TANK, CABLE, PISTON, TTABLE, RAIL}

LAYOUTS = {'ts': dict(north=225.0), 'ra': dict(north=270.0)}

P = dict(
    # the arms: k-th points at 45 + 90 k + delta degrees (from east towards south); the ridge offset `off` to its
    # left; the ridge z0 out to s0, then down kr per unit to the end s1 (a steep end, endk); a flat strip wt wide on
    # top; sides falling ka per unit
    # the arms: the k-th points at 45 + 90 k + delta degrees (from east towards south: 0 SE, 1 SW, 2 NW, 3 NE), its
    # ridge offset `off` to the right of its line; per pair (SE / NW 'low', SW / NE 'wing'): the ridge z0 out to s0,
    # then down kr per unit to the end s1 (falling endk per unit past it); a flat strip wt wide on top, the sides
    # falling ka per unit (fitted to NAPULSMK 12 in TS's camera: silhouette 0.89)
    arms=dict(delta=-6.0, off=8.75,
              low=dict(z0=60.0, s0=48.0, kr=0.6, s1=114.0, endk=3.0, wt=8.75, ka=0.9),
              wing=dict(z0=56.0, s0=36.0, kr=0.69, s1=106.0, endk=4.0, wt=19.25, ka=1.25)),
    cone=dict(R0=79.0, R1=42.0, hc=45.0),
    rim=dict(R=45.0, z=42.0, ri=36.0, lip=1.5),
    crater=dict(z=38.0),
    drum=dict(r=31.0, z=65.0, seams=(50.0, 57.5), dome=1.5),
    light=dict(at=(4.0, 54.5), r=5.5, h=6.5),       # (TS's lamp px (37-40, 68-71) on the cone, just under the drum)
    head=dict(
        mode='cannon',           # the head as built (CANNON: v2); 'prim3' (HEAD3) was v1; 'vox' / 'prim2' / '' tries
        # side profile (u forward to the lens, w up), convex, going round
        prof=((21.0, 136.5), (-29.0, 140.5), (-47.0, 128.0), (-48.0, 84.0), (-22.0, 76.0), (8.0, 118.0)),
        hv=22.5, bev=1.3, bev_w=124.0,
        legs=dict(v=20.0, hw=5.0, hu=7.0),
        pivot=dict(r=25.5, z=72.0),
        pack=dict(u=(-58.0, -24.0), v=13.0, w=(84.0, 96.0)),
        lens=dict(w=128.0, r=8.0, out=2.5),
        port=dict(w=104.0, r=7.0),
    ),
)

BUILD_KEYS = ('ring', 'ringh', 'cone', 'arms', 'drum', 'snow', 'light')
DONE = {k: 1.0 for k in BUILD_KEYS}


def to_local(X, Y, layout='ts'):
    return X, Y


def to_world(x, y, layout='ts'):
    return x, y


def facing_deg(f, layout='ts'):
    """the head's forward direction (degrees from east towards south) for frame f (TS's NAPULS_A order: 0 north, then
    turning anticlockwise as seen from above: 8 west, 16 south, 24 east)."""
    return LAYOUTS[layout]['north'] - 11.25 * f


def arm_frame(X, Y, k, a):
    ang = np.radians(45.0 + 90.0 * k + a['delta'])
    d = np.array([np.cos(ang), np.sin(ang)]); q = np.array([d[1], -d[0]])
    s = X * d[0] + Y * d[1]
    t = X * q[0] + Y * q[1] - a['off']
    return s, t


def arm_pair(k, a):
    return a['low'] if k % 2 == 0 else a['wing']


def arm_top(s, b):
    zr = np.minimum(b['z0'], b['z0'] - b['kr'] * (s - b['s0']))
    return np.where(s > b['s1'], zr - b['endk'] * (s - b['s1']), zr)


def base_field(X, Y, p, g=None):
    """the base's height (and comps) over the ground; g = build progress."""
    g = dict(DONE) if g is None else g
    r = np.hypot(X, Y)
    H = np.zeros_like(X); C = np.zeros(X.shape, np.int16)
    rm = p['rim']; cn = p['cone']; a = p['arms']
    # the collar ring (the build-up: it grows round as an arc, then up)
    ring_f = float(np.clip(g['ring'], 0, 1))
    if ring_f > 0:
        ang = (np.degrees(np.arctan2(Y, X)) - rm.get('arc_from', 272.0) + 180.0) % 360.0 - 180.0   # (TS: from the back)
        arc = np.abs(ang) <= ring_f * 180.0
        zr = rm['z'] * (0.25 + 0.75 * float(np.clip(g.get('ringh', 1.0), 0, 1)))
        m = (r <= rm['R']) & (r >= rm['ri']) & arc
        top = zr + rm['lip'] * np.clip((r - rm['ri']) / 3.0, 0, 1) * np.clip((rm['R'] - r) / 3.0, 0, 1)
        H = np.where(m, top, H); C = np.where(m, RIM, C)
    # the cone under the collar
    cf = float(np.clip(g['cone'], 0, 1))
    if cf > 0:
        zc = np.clip((cn['R0'] - r) / (cn['R0'] - cn['R1']), 0, 1) * cn['hc'] * cf
        zc = np.where(r < rm['ri'], 0.0, zc)
        w = zc > H
        H = np.where(w, zc, H); C = np.where(w, BASE, C)
    # the arms (the build-up: each slides up out of the ground)
    af = float(np.clip(g['arms'], 0, 1))
    if af > 0:
        for k in range(4):
            b = arm_pair(k, a)
            s, t = arm_frame(X, Y, k, a)
            zt = arm_top(s, b)
            tt = np.maximum(np.abs(t) - b['wt'] / 2, 0)
            za = zt - b['ka'] * tt - (1 - af) * b['z0']
            za = np.where((s > 0) & (r >= rm['ri']), za, 0.0)
            ridge = (np.abs(t) <= b['wt'] / 2)
            w = za > H + 1e-4
            H = np.where(w, za, H); C = np.where(w, np.where(ridge, ARM, BASE), C)
    # the crater floor inside the collar
    inside = r < rm['ri']
    if cf > 0:
        H = np.where(inside & (ring_f > 0), np.maximum(H, p['crater']['z'] * cf), H)
        C = np.where(inside & (ring_f > 0), CRATER, C)
    return H, C


def light_spot(p):
    return p['light']['at']


def head_profile_interval(u, prof):
    lo, hi, ok = quad_interval(u, list(prof))
    return lo, hi, ok


def add_head(X, Y, p, f_deg, A, layout='ts', zlift=0.0):
    """the head on the drum, its forward direction f_deg (degrees from east towards south)."""
    hp = p['head']
    a = np.radians(f_deg)
    du = np.array([np.cos(a), np.sin(a)]); dv = np.array([np.sin(a), -np.cos(a)])   # v: to the head's left
    u = X * du[0] + Y * du[1]
    v = X * dv[0] + Y * dv[1]
    av = np.abs(v)
    dz = zlift
    # the body: the profile polygon, sides bevelled in above bev_w
    lo, hi, ok = head_profile_interval(u, hp['prof'])
    cap = hp['bev_w'] + (hp['hv'] - av) / hp['bev']
    hi2 = np.minimum(hi, cap)
    m = ok & (av <= hp['hv']) & (hi2 > lo)
    # the hood (light): the top / upper part; the sides dark below the bevel line (material decides by normal)
    A('hood').add(lo + dz, hi2 + dz, HOOD, m, 'hood')
    # the lens: a short drum out of the leaning front, high on it
    ln = hp['lens']
    fu, fw = hp['prof'][0]; bu, bw = hp['prof'][-1]
    # the front face's line from (bu, bw) to (fu, fw); the lens centre on it at height ln['w']
    t_ = (ln['w'] - bw) / (fw - bw)
    lc = np.array([bu + t_ * (fu - bu), 0.0, ln['w']])
    fn = np.array([fw - bw, 0.0, -(fu - bu)]); fn = fn / np.linalg.norm(fn)       # the face's outward normal (u, w)
    p0 = lc - fn * 1.0; p1 = lc + fn * ln['out']
    # world points
    def W3(q):
        return np.array([q[0] * du[0] + q[1] * dv[0], q[0] * du[1] + q[1] * dv[1], q[2] + dz])
    lo_, hi_, mm = rod_interval(X, Y, W3(p0), W3(p1), ln['r'])
    A('lens').add(lo_, hi_, LENS, mm, 'lens')
    lo_, hi_, mm = rod_interval(X, Y, W3(p1 - fn * 0.6), W3(p1 + fn * 0.4), ln['r'] * 0.45)
    A('lensc').add(lo_, hi_, LENSC, mm, 'lensc')
    # the pack at the back, low; its round port on the back face
    pk = hp['pack']
    mp = inbox(u, av, pk['u'], (0.0, pk['v']))
    A('pack').add(pk['w'][0] + dz, pk['w'][1] + dz, PACK, mp, 'pack')
    po = hp['port']
    pb = np.array([pk['u'][0] - 0.8, 0.0, pk['w'][0] + 0.5 * (pk['w'][1] - pk['w'][0])])
    lo_, hi_, mm = rod_interval(X, Y, W3(pb + np.array([0.6, 0, 0])), W3(pb + np.array([-0.4, 0, 0])), min(po['r'], 0.5 * (pk['w'][1] - pk['w'][0]) - 0.5))
    A('port').add(lo_, hi_, PORT, mm, 'port')
    # two legs from the turntable up under the body
    lg = hp['legs']
    ml = (np.abs(av - lg['v']) <= lg['hw']) & (np.abs(u) <= lg['hu'])
    A('legs').add(hp['pivot']['z'] - 2 + dz, 106.0 + dz, LEG, ml, 'legs')
    # the turntable ring on the drum
    pv = hp['pivot']
    rr = np.hypot(X, Y)
    A('pivot').add(p['drum']['z'] - 0.5, pv['z'] + dz, PIVOT, rr <= pv['r'], 'pivot')


def head_local(X, Y, fdeg):
    a = np.radians(fdeg)
    du = np.array([np.cos(a), np.sin(a)]); dv = np.array([np.sin(a), -np.cos(a)])
    return X * du[0] + Y * du[1], X * dv[0] + Y * dv[1]


def add_head_vox(X, Y, p, fdeg, A, zlift=0.0):
    """the head from TS's 32 facings (pulshead: the visual hull's columns), plus the turntable ring."""
    import pulshead as PH
    u, v = head_local(X, Y, fdeg)
    for k, (lo, hi, m) in enumerate(PH.intervals(u, v)):
        A(f'hv{k}').add(lo + zlift, hi + zlift, HOOD, m, f'hv{k}')
    pv = p['head']['pivot']
    rr = np.hypot(X, Y)
    A('pivot').add(p['drum']['z'] - 0.5, pv['z'] + zlift, PIVOT, rr <= pv['r'], 'pivot')


HEAD2 = dict(core=dict(u=(-34.0, 16.0), hv=22.0, w=(90.0, 126.0), rnd=7.0),
             hood=dict(u=(-42.0, 22.0), hw=(28.0, 18.0), w=(120.0, 140.0), ridge=0.3),
             face=dict(u=(15.0, 21.0), hv=20.0, w=(94.0, 132.0), frame=3.5),
             lens=dict(w=113.0, r=7.0, out=4.0),
             pack=dict(u=(-54.0, -28.0), w=100.0, r=13.0, port=6.5),
             legs=dict(v=17.0, u=0.0, r=3.6, w=(66.0, 93.0)),
             pivot=dict(r=16.0, w=(64.5, 69.0)))


def add_head_prim2(X, Y, p, fdeg, A, zlift=0.0, h=None):
    """the head built of parts (read from NAPULS_A's 32 facings): a dark core, a light hood on top (wide at the back,
    narrow at the front, a low ridge), the face plate with the lens, a rounded pack at the back with a port, two legs
    and a turntable ring on the drum."""
    h = HEAD2 if h is None else h
    u, v = head_local(X, Y, fdeg)
    av = np.abs(v)
    dz = zlift
    c = h['core']
    du_ = np.maximum(np.maximum(c['u'][0] + c['rnd'] - u, u - (c['u'][1] - c['rnd'])), 0)
    dv_ = np.maximum(av - (c['hv'] - c['rnd']), 0)
    m = np.hypot(du_, dv_) <= c['rnd']
    A('hcore').add(c['w'][0] + dz, c['w'][1] + dz, HSIDE, m, 'hcore')
    hd_ = h['hood']
    k = np.clip((u - hd_['u'][0]) / (hd_['u'][1] - hd_['u'][0]), 0, 1)
    hw = hd_['hw'][0] + (hd_['hw'][1] - hd_['hw'][0]) * k
    m = (u >= hd_['u'][0]) & (u <= hd_['u'][1]) & (av <= hw)
    top = hd_['w'][1] - hd_['ridge'] * av
    A('hood').add(hd_['w'][0] + dz, top + dz, HOOD, m, 'L:hood')
    f = h['face']
    m = (u >= f['u'][0]) & (u <= f['u'][1]) & (av <= f['hv'])
    A('face').add(f['w'][0] + dz, f['w'][1] + dz, HDARK, m, 'face')
    ln = h['lens']
    lo, hi, mm = rod_interval(u, v, (f['u'][1] - 1.0, 0.0, ln['w'] + dz), (f['u'][1] + ln['out'], 0.0, ln['w'] + dz), ln['r'])
    A('lens').add(lo, hi, LENS, mm, 'lens')
    lo, hi, mm = rod_interval(u, v, (f['u'][1] + ln['out'] - 0.6, 0.0, ln['w'] + dz), (f['u'][1] + ln['out'] + 0.4, 0.0, ln['w'] + dz), ln['r'] * 0.45)
    A('lensc').add(lo, hi, LENSC, mm, 'lensc')
    pk = h['pack']
    lo, hi, mm = rod_interval(u, v, (pk['u'][0], 0.0, pk['w'] + dz), (pk['u'][1], 0.0, pk['w'] + dz), pk['r'])
    A('pack').add(lo, hi, HOOD, mm, 'L:pack')
    lo, hi, mm = rod_interval(u, v, (pk['u'][0] - 0.8, 0.0, pk['w'] + dz), (pk['u'][0] + 0.4, 0.0, pk['w'] + dz), pk['port'])
    A('port').add(lo, hi, PORT, mm, 'port')
    lg = h['legs']
    for sgn in (-1.0, 1.0):
        lo, hi, mm = rod_interval(u, v, (lg['u'], sgn * lg['v'], lg['w'][0] + dz), (lg['u'], sgn * (lg['v'] + 1.0), lg['w'][1] + dz), lg['r'])
        A('legs').add(lo, hi, LEG, mm, 'legs')
    pv = h['pivot']
    rr = np.hypot(X, Y)
    A('pivot').add(pv['w'][0], pv['w'][1] + dz, PIVOT, rr <= pv['r'], 'pivot')


HEAD3 = dict(prof=((24.0, 106.0), (-4.0, 141.0), (-32.0, 146.0), (-42.0, 136.0), (-42.0, 96.0), (-20.0, 90.0), (14.0, 92.0)),
             hv=(25.0, 17.0), bev=1.2, bev_w=133.0, gable=14.0, gable_back=True, slit=(121.0, 128.0),
             lens=dict(w=116.0, r=7.0, out=3.0),
             pack=dict(u=(-56.0, -34.0), w=95.0, r=15.0, port=7.0),
             legs=dict(v=17.0, u=2.0, r=3.6, w=(66.0, 92.0)),
             pivot=dict(r=16.0, w=(64.5, 69.0)))


def head3_visor(h=None):
    """the visor (the sloping front plate): its foot and top (u, w) and outward normal (u, w)."""
    h = HEAD3 if h is None else h
    (u0, w0), (u1, w1) = h['prof'][0], h['prof'][1]
    n = np.array([w1 - w0, -(u1 - u0)]); n = n / np.linalg.norm(n)
    return (u0, w0), (u1, w1), n


def add_head_prim3(X, Y, p, fdeg, A, zlift=0.0, h=None):
    """the head: a wedge (a sloping visor at the front carrying the lens, a flat top, a square back), dark sides, a
    rounded pack low on its back with a port, two legs and a turntable ring on the drum (read from NAPULS_A)."""
    h = HEAD3 if h is None else h
    u, v = head_local(X, Y, fdeg)
    av = np.abs(v)
    dz = zlift
    lo, hi, ok = quad_interval(u, list(h['prof']))
    us_ = [q_[0] for q_ in h['prof']]
    k = np.clip((u - min(us_)) / (max(us_) - min(us_)), 0, 1)
    hvu = h['hv'][0] + (h['hv'][1] - h['hv'][0]) * k          # wider at the back, narrower at the front
    cap = h['bev_w'] + (hvu - av) / h['bev']
    # a smooth minimum of the top and the bevel: a plain one switches between two nearly level planes px by px (a
    # cross-hatch on the gabled back)
    kk_ = 1.5
    hi2 = -kk_ * np.logaddexp(-hi / kk_, -cap / kk_)
    hi2 = np.where(np.isfinite(hi2), hi2, np.minimum(hi, cap))
    if h.get('gable', 0.0) > 0:                          # a gabled top: a ridge along the middle, falling to the sides,
        # rising from nothing at the visor's top edge to full at the back (seen from behind, TS's facing 0, the back is
        # peaked; from the front, 16, the visor's top edge is straight)
        u_vis = h['prof'][1][0]; u_back = min(q_[0] for q_ in h['prof'])
        kb = np.clip((u_vis - u) / (u_vis - u_back), 0, 1) if h.get('gable_back', False) else 1.0
        hi2 = hi2 - h['gable'] * kb * np.clip(av / hvu, 0, 1)
    m = ok & (av <= hvu) & (hi2 > lo)
    A('hbody').add(lo + dz, hi2 + dz, HOOD, m, 'L:hbody')
    (u0, w0), (u1, w1), n = head3_visor(h)
    ln = h['lens']
    t_ = (ln['w'] - w0) / (w1 - w0)
    cu = u0 + t_ * (u1 - u0)
    du_, dw_ = n
    a = np.radians(fdeg)
    ex, ey = np.cos(a), np.sin(a)

    def W3(uu, ww):
        return (uu * ex, uu * ey, ww + dz)
    lo, hi, mm = rod_interval(X, Y, W3(cu - du_, ln['w'] - dw_), W3(cu + du_ * ln['out'], ln['w'] + dw_ * ln['out']), ln['r'])
    A('lens').add(lo, hi, LENS, mm, 'lens')
    lo, hi, mm = rod_interval(X, Y, W3(cu + du_ * (ln['out'] - 0.6), ln['w'] + dw_ * (ln['out'] - 0.6)),
                              W3(cu + du_ * (ln['out'] + 0.4), ln['w'] + dw_ * (ln['out'] + 0.4)), ln['r'] * 0.45)
    A('lensc').add(lo, hi, LENSC, mm, 'lensc')
    pk = h['pack']
    lo, hi, mm = rod_interval(X, Y, W3(pk['u'][0], pk['w']), W3(pk['u'][1], pk['w']), pk['r'])
    A('pack').add(lo, hi, PACK, mm, 'L:pack')
    lo, hi, mm = rod_interval(X, Y, W3(pk['u'][0] - 0.8, pk['w']), W3(pk['u'][0] + 0.4, pk['w']), pk['port'])
    A('port').add(lo, hi, PORT, mm, 'port')
    lg = h['legs']
    lx, ly = -ey, ex                                     # the head's left, in the world
    for sgn in (-1.0, 1.0):
        P0 = (lg['u'] * ex + sgn * lg['v'] * lx, lg['u'] * ey + sgn * lg['v'] * ly, lg['w'][0] + dz)
        P1 = (lg['u'] * ex + sgn * (lg['v'] + 1.0) * lx, lg['u'] * ey + sgn * (lg['v'] + 1.0) * ly, lg['w'][1] + dz)
        lo, hi, mm = rod_interval(X, Y, P0, P1, lg['r'])
        A('legs').add(lo, hi, LEG, mm, 'legs')
    pv = h['pivot']
    rr = np.hypot(X, Y)
    A('pivot').add(pv['w'][0], pv['w'][1] + dz, PIVOT, rr <= pv['r'], 'pivot')


# ------------------------------------------------------------------------------------ the head, v2: a cannon on a yoke
# Read from NAPULS_A's 32 facings (their visual hull, coloured by TS's pixels) with Luke's two reference renders: a box
# body with a light top, dark sides and a light back, a round nose standing out of its upper front with the emitter
# disc on its end (TS's light ring; the white disc with dark bars in the first reference), the body held on two slanted
# yoke plates from the drum up its sides (TS's dark slanted bands; the plate in the second reference), a light round
# trunnion boss on each plate, a dark round tank under the back, cables looping off the back down to the drum.
# Head frame: u forward, v to the left, w up, the drum's axis at u = v = 0.  tilt raises the body and nose about the
# trunnions (TS's idle facings are level).
CANNON = dict(
    tilt=15.0,                                             # raised (Luke, 19:25); TS's idle facings are level
    trun=(-20.0, 115.0),                                   # the trunnion axis (u, w): the body tilts about it
    # the body: a box rounded along its length (its corners clipped by a cylinder of radius `round`), its front top
    # edge cut back (a slope from (ch u, top) down to the front at ch w); fitted with the parts below to TS's 32 facings
    # (silhouette IoU 0.84 over all 32 with the tilt, 0.85 level)
    body=dict(u=(-48.0, 6.0), hv=16.0, w=(108.5, 128.0), round=26.0, ch=(-6.0, 122.0)),
    nose=dict(u=(0.0, 18.5), r=9.0, w=116.0, collar=dict(r=10.6, u=(18.5, 23.0), bore=6.4, bore_u=19.6),
              coils=dict(r=10.3, w=1.8, at=(7.0, 12.0))),       # two coil rings round the nose
    yoke=dict(v=(20.5, 27.5), poly=((-6.0, 67.0), (10.0, 67.0), (-18.0, 130.0), (-44.0, 130.0))),
    boss=dict(r=7.5, t=2.4, pin=4.5),
    tank=dict(r=14.0, w=92.0, u=(-45.0, -11.0)),
    cables=dict(r=2.5, v=(10.0,), back=(-42.0, 122.0), pts=((0.0, 0.0), (-10.0, -8.0), (-14.5, -22.0), (-10.0, -37.0),
                                                          (3.0, -48.0), (21.0, -54.1))),
    ttable=None,
)


def cannon_tilted(h, u, w):
    """(u, w) of a point of the tilting part (body, nose, tank) after the tilt about the trunnions."""
    t = np.radians(h['tilt']); tu, tw = h['trun']
    du, dw = u - tu, w - tw
    return tu + du * np.cos(t) - dw * np.sin(t), tw + du * np.sin(t) + dw * np.cos(t)


def cannon_local(x, y, z, fdeg, h=None, zlift=0.0):
    """world (local layout) points -> the head frame (u, v, w) and the body's own (untilted) frame (a, b, c): what
    the point would be with tilt 0."""
    h = CANNON if h is None else h
    u, v = head_local(x, y, fdeg)
    w = z - zlift
    t = np.radians(h['tilt']); tu, tw = h['trun']
    du, dw = u - tu, w - tw
    a = tu + du * np.cos(t) + dw * np.sin(t)
    c = tw - du * np.sin(t) + dw * np.cos(t)
    return u, v, w, a, v, c


def plane_interval(x, y, n, d):
    """the half-space n.P <= d over the ground: (lo, hi, ok) of z."""
    s = x * n[0] + y * n[1]
    if abs(n[2]) < 1e-9:
        return np.full(x.shape, -1e9), np.full(x.shape, 1e9), s <= d
    zb = (d - s) / n[2]
    if n[2] > 0:
        return np.full(x.shape, -1e9), zb, np.ones(x.shape, bool)
    return zb, np.full(x.shape, 1e9), np.ones(x.shape, bool)


def add_head_cannon(X, Y, p, fdeg, A, zlift=0.0, h=None):
    h = CANNON if h is None else h
    a_ = np.radians(fdeg)
    ex, ey = np.cos(a_), np.sin(a_)
    lx, ly = np.sin(a_), -np.cos(a_)
    dz = zlift
    tu, tw = h['trun']
    t = np.radians(h['tilt'])
    eu = np.array([ex * np.cos(t), ey * np.cos(t), np.sin(t)])     # the tilted body's axes in the world
    ev = np.array([lx, ly, 0.0])
    ew = np.array([-ex * np.sin(t), -ey * np.sin(t), np.cos(t)])

    def W3(u, v, w):
        return (u * ex + v * lx, u * ey + v * ly, w + dz)

    def WT(u, v, w):                                       # a point of the tilting part
        u2, w2 = cannon_tilted(h, u, w)
        return W3(u2, v, w2)
    u, v = head_local(X, Y, fdeg)
    # the body: the box's six faces, the rounding cylinder and the front top slope, intersected
    bd = h['body']
    O = np.array(WT(0.0, 0.0, 0.0))
    planes = [(-eu, -bd['u'][0]), (eu, bd['u'][1]), (-ev, bd['hv']), (ev, bd['hv']), (-ew, -bd['w'][0]), (ew, bd['w'][1])]
    if bd.get('ch'):
        cu, cw = bd['ch']                                  # through (cu, top) and (front, cw)
        du_, dw_ = bd['u'][1] - cu, cw - bd['w'][1]
        nn = np.array([-dw_, du_]); nn = nn / np.linalg.norm(nn)            # outward (u, w) normal of the slope
        n3 = nn[0] * eu + nn[1] * ew
        planes.append((n3, nn[0] * cu + nn[1] * bd['w'][1]))
    lo = np.full(X.shape, -1e9); hi = np.full(X.shape, 1e9); ok = np.ones(X.shape, bool)
    for n3, d in planes:
        d3 = d + float(np.dot(n3, O))                      # the plane in world coordinates (O: the frame's origin)
        l_, h_, o_ = plane_interval(X, Y, n3, d3)
        lo = np.maximum(lo, l_); hi = np.minimum(hi, h_); ok &= o_
    if bd.get('round'):
        wc = 0.5 * (bd['w'][0] + bd['w'][1])
        l_, h_, o_ = rod_interval(X, Y, WT(bd['u'][0] - 1.0, 0.0, wc), WT(bd['u'][1] + 1.0, 0.0, wc), bd['round'])
        lo = np.maximum(lo, l_); hi = np.minimum(hi, h_); ok &= o_
    ok &= hi > lo
    A('body').add(lo, hi, HBOX, ok, 'body')
    # the nose and its collar
    nz = h['nose']
    lo, hi, m = rod_interval(X, Y, WT(nz['u'][0], 0.0, nz['w']), WT(nz['u'][1], 0.0, nz['w']), nz['r'])
    A('L:nose').add(lo, hi, BARREL, m, 'L:nose')
    for at in (nz.get('coils') or {}).get('at', ()):
        co = nz['coils']
        lo, hi, m = rod_interval(X, Y, WT(at - co['w'] / 2, 0.0, nz['w']), WT(at + co['w'] / 2, 0.0, nz['w']), co['r'])
        A('L:nose').add(lo, hi, MZHI, m, 'L:nose')
    cl = nz.get('collar')
    if cl:
        # the muzzle: a ring with the bore in it (the bore's floor and the ring under it go with the nose, the ring
        # over the bore in a slab of its own; the bore's back wall is where the nose's slab steps)
        mlo, mhi, mm = rod_interval(X, Y, WT(cl['u'][0], 0.0, nz['w']), WT(cl['u'][1], 0.0, nz['w']), cl['r'])
        if cl.get('bore'):
            blo, bhi, bm = rod_interval(X, Y, WT(cl['bore_u'], 0.0, nz['w']), WT(cl['u'][1] + 4.0, 0.0, nz['w']), cl['bore'])
            cut = mm & bm & (bhi > mlo) & (blo < mhi)
            A('L:nose').add(mlo, mhi, MZLO, mm & ~cut, 'L:nose')
            A('L:nose').add(mlo, np.minimum(blo, mhi), MZLO, cut & (blo > mlo + 0.3), 'L:nose')
            A('L:muzzle').add(np.maximum(bhi, mlo), mhi, MZLO, cut & (mhi > bhi + 0.3), 'L:muzzle')
        else:
            A('L:nose').add(mlo, mhi, MZLO, mm, 'L:nose')
    # the tank under the back
    tk = h['tank']
    lo, hi, m = rod_interval(X, Y, WT(tk['u'][0], 0.0, tk['w']), WT(tk['u'][1], 0.0, tk['w']), tk['r'])
    A('L:tank').add(lo, hi, TANK, m, 'L:tank')
    # the yoke: two slanted plates from the drum up the body's sides
    yk = h['yoke']
    lo, hi, okp = quad_interval(u, list(yk['poly']))
    for sgn in (-1.0, 1.0):
        m = okp & (sgn * v >= yk['v'][0]) & (sgn * v <= yk['v'][1])
        A('yoke').add(lo + dz, hi + dz, YOKE, m, 'yoke')
    # the trunnion bosses on the plates' outer faces, and the pins through to the body
    bs = h['boss']
    for sgn in (-1.0, 1.0):
        lo, hi, m = rod_interval(X, Y, W3(tu, sgn * (yk['v'][1] - 0.5), tw), W3(tu, sgn * (yk['v'][1] + bs['t']), tw), bs['r'])
        A('L:boss').add(lo, hi, BOSS, m, 'L:boss')
        if bs.get('pin'):
            lo, hi, m = rod_interval(X, Y, W3(tu, sgn * (h['body']['hv'] - 1.0), tw), W3(tu, sgn * (yk['v'][0] + 0.5), tw), bs['pin'])
            A('L:pin').add(lo, hi, YOKE, m, 'L:pin')
    # the cables, looping off the back of the body down to the drum
    cb = h['cables']
    bu, bw = cb['back']
    for vv in cb['v']:
        for sgn in (-1.0, 1.0):
            pts = [(bu + du_, bw + dw_) for du_, dw_ in cb['pts']]
            for i in range(len(pts) - 1):
                (u0, w0), (u1, w1) = pts[i], pts[i + 1]
                P0 = WT(u0, sgn * vv, w0) if i == 0 else W3(u0, sgn * vv, w0)
                P1 = W3(u1, sgn * vv, w1)
                lo, hi, m = rod_interval(X, Y, P0, P1, cb['r'])
                A(f'cable{int(vv)}').add(lo, hi, CABLE, m, 'cable')
                rr = np.hypot(X - P1[0], Y - P1[1])          # a ball at each joint closes the gap between the segments
                mj = rr <= cb['r']
                dj = np.sqrt(np.clip(cb['r'] ** 2 - rr ** 2, 0, None))
                A(f'cable{int(vv)}').add(P1[2] - dj, P1[2] + dj, CABLE, mj, 'cable')
    # a turntable hub on the drum (off: TS shows the drum's top clear between the plates)
    tt = h.get('ttable')
    if tt:
        rr = np.hypot(X, Y)
        A('ttable').add(tt['w'][0], tt['w'][1] + dz, TTABLE, rr <= tt['r'], 'ttable')


def scene(X, Y, p=None, layout='ts', prog=None, level=0, head=None, shadow=False, snow=False, zlift=0.0, **kw):
    """head: None (no head: the building frames) or the frame number 0..31 (or a float facing in degrees via
    head=('deg', a))."""
    p = P if p is None else p
    g = dict(DONE); g.update(prog or {})
    x, y = to_local(X, Y, layout)
    H, C = base_field(x, y, p, g)
    r = np.hypot(x, y)
    # the drum: from the crater floor up, its top a shallow dome; it rises out of the crater in the build-up
    dr = p['drum']
    df = float(np.clip(g['drum'], 0, 1))
    if df > 0:
        md = r <= dr['r']
        ztop = p['crater']['z'] + (dr['z'] - p['crater']['z']) * df + dr['dome'] * np.clip(1 - (r / dr['r']) ** 2, 0, 1)
        H = np.where(md, np.maximum(H, ztop), H); C = np.where(md, DRUM, C)
    # the small lamp at the drum's foot
    if g['light'] >= 1:
        lt = p['light']
        lx, ly = lt['at']
        rl = np.hypot(x - lx, y - ly)
        # the lamp: a dome standing out of the cone's slope (its top level, its foot following the slope)
        h0 = float(base_field(np.array([[lx]]), np.array([[ly]]), p, g)[0][0, 0])
        ml = rl <= lt['r']
        dome = h0 + lt['h'] * np.sqrt(np.clip(1 - (rl / lt['r']) ** 2, 0, 1))
        H = np.where(ml, np.maximum(H, dome), H); C = np.where(ml & (dome > H - 1e-3), LIGHT, C)
    pacc = {}

    def A(name):
        if name not in pacc:
            pacc[name] = Acc(X.shape, n=2)
        return pacc[name]
    if head is not None and p['head'].get('mode') == 'cannon':
        from plug import CropAcc, pack_slabs
        cacc = {}

        def AC(name):
            if name not in cacc:
                cacc[name] = CropAcc(X.shape, n=3)
            return cacc[name]
        fdeg = head[1] if isinstance(head, tuple) else facing_deg(head, layout)
        add_head_cannon(x, y, p, fdeg, AC, zlift=zlift, h=kw.get('cannon'))
        return hd.Scene(H.astype(np.float32), C.astype(np.int16), pack_slabs(cacc.values(), X.shape), {})
    if head is not None:
        fdeg = head[1] if isinstance(head, tuple) else facing_deg(head, layout)
        if p['head'].get('mode', 'vox') == 'vox':
            add_head_vox(x, y, p, fdeg, A, zlift=zlift)
        elif p['head'].get('mode') == 'prim2':
            add_head_prim2(x, y, p, fdeg, A, zlift=zlift)
        elif p['head'].get('mode') == 'prim3':
            add_head_prim3(x, y, p, fdeg, A, zlift=zlift)
        else:
            add_head(x, y, p, fdeg, A, layout, zlift=zlift)
    return hd.Scene(H.astype(np.float32), C.astype(np.int16), [s for a_ in pacc.values() for s in a_.slabs()], {})


FLAT = {BASE: (200, 190, 150), ARM: (220, 212, 176), RIM: (180, 176, 150), CRATER: (40, 40, 40), DRUM: (0, 214, 0),
        SEAM: (0, 150, 0), LIGHT: (120, 255, 120), PIVOT: (120, 120, 126), HOOD: (190, 190, 196), HSIDE: (90, 90, 96),
        HDARK: (60, 60, 66), LEG: (90, 90, 96), LENS: (230, 232, 240), LENSC: (40, 40, 50), PACK: (70, 70, 76),
        PORT: (20, 20, 22), SNOW: (240, 244, 255)}
