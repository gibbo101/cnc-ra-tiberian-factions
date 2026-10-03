"""
TS Limpet Mine (the Limpet Drone dug in; Firestorm DLIMPET; TSDLIMP in the mod) as a model for hd.py.

Built in the cell's own frame (x east, y south, z up, origin at the cell's ground centre), read from DLIMPET, DLIMPMK
and DLIMP_A in TS's own camera:
  body    the drone: an egg (house colour), widest a third of the way up, tucked in at the bottom where it sits in its
          ring, narrowing to a grey collar on top with a black knob; an amber lamp low on its front and a small eye
          (DLIMPMK blinks both)
  ring    a grey ring round the body's foot (11.3..19 units, 8 high): a dark hinge slot and a white light over each leg
  legs    four claws (house colour) at north, east, south and west: flat blades with a ridge down the middle (a roof
          cross-section: the slope toward the light bright, the other dark), tapering to a point, hinged in the
          ring's top edge; in flight hanging down (folded in under the body at first), swung out and down when it
          lands, their points dug into the ground
Dug in (DLIMPET): the ring on the ground, the claws out flat with their points in the earth, the body sunk through the
ring until only its top shows inside it (dark, deep in the ring), the collar and knob pulled in.
pose = dict(z = the ring's bottom over the ground, phi = the claws' swing (degrees: 0 hanging straight down, - folded
in under the body, + swung out), sink = how far the body has sunk through the ring (units), knob = 1 out .. 0 pulled in)
for the build-up (DLIMPMK: it hovers, lowers its claws, swings them out, comes down, digs in).
"""
import numpy as np
import hd
from plug import CropAcc, pack_slabs
from fgen import convex_interval

(BODY, COLLAR, KNOB, LAMP, EYE, RING, RLIGHT, SLOT, LEG) = range(1, 10)
HOUSE = {BODY, LEG}

P = dict(
    ring=dict(r=(11.3, 19.0), h=9.0),
    # the body's radius going up from its foot (dz above the ring's bottom, r): tucked into the ring, widest at 12..26,
    # narrowing to the collar
    body=dict(prof=((0.0, 15.0), (6.0, 15.0), (9.0, 18.5), (11.0, 19.0), (26.0, 19.0), (31.0, 17.2), (36.0, 15.0),
                    (40.0, 13.0), (43.0, 11.0))),
    collar=dict(r=10.5, h=4.0),                     # grey, on the body's top
    knob=dict(r=7.5, h=8.0),                        # black dome on the collar
    lamp=dict(az=68.0, dz=17.7, r=2.4),             # the amber lamp, low on the front
    eye=dict(az=62.0, dz=31.0, r=1.6),              # the small eye that glints (DLIMPMK 3, 13, 23, 33)
    lights=dict(dt=11.0, w=4.5, h=3.2, slot=4.0),   # per leg: a dark hinge slot on the leg's line, a white light dt deg on
    # each leg: a sleeve on the hinge and the claw sliding out of it (L: hinge to point, 36 tucked .. 46 out)
    legs=dict(hinge=(16.0, 1.2), sleeve=dict(L=22.0, W0=19.0, W1=17.0, T0=4.6, T1=4.4, te=1.3),
              claw=dict(L=26.0, W0=15.5, W1=7.0, T0=4.8, T1=2.0, te=1.0)),
    settled=dict(z=0.0, phi=88.0, L=44.0, sink=39.0, knob=0.0),
)
# skew: in TS's view the claws are drawn 10 degrees off square, toward the camera's line (the front pair closer to
# south-east, the back pair to north-west), which makes TS's tall X; on the RA grid they are square to the grid
LAYOUTS = {'ts': dict(skew=10.0), 'ra': dict(skew=0.0)}
BROKEN_CLAW, DMG_CUT = 1, 10.0          # damaged: the east claw (k 1) loses its last 10 units
BUILD_KEYS = ('paint',)
DONE = {'paint': 1.0}


def to_local(X, Y, layout='ts'):
    return X, Y


def leg_az(k, layout='ts'):
    """the k-th claw's azimuth (degrees from east toward south): N, E, S, W, skewed toward the TS camera's line."""
    sk = LAYOUTS.get(layout, {}).get('skew', 0.0)
    return (-90.0 - sk, 0.0 + sk, 90.0 - sk, 180.0 + sk)[k]


def body_profile(p):
    """the body's radius every 0.25 units up, and the running maxima from above and below (for the lathe's top and
    bottom at any radius)."""
    pts = np.asarray(p['body']['prof'], float)
    dz = np.arange(0.0, pts[-1, 0] + 1e-6, 0.25)
    r = np.interp(dz, pts[:, 0], pts[:, 1])
    up = np.maximum.accumulate(r[::-1])[::-1]       # max radius at or above dz
    dn = np.maximum.accumulate(r)                   # max radius at or below dz
    return dz, r, up, dn


def lathe(rr, dz, up, dn):
    """top and bottom dz of the lathed body over ground radius rr (nan outside)."""
    inside = rr <= up[0]
    # top: the highest dz whose radius-at-or-above >= rr (up is non-increasing)
    top = np.interp(rr, up[::-1], dz[::-1])
    bot = np.interp(rr, dn, dz)
    return np.where(inside, top, np.nan), np.where(inside, bot, np.nan)


def claw_frame(a, hinge, phi, z0):
    """the claw's axes at azimuth a (degrees), hinged at (R, z) = hinge (z over z0), swung phi degrees out from hanging
    straight down (90: out flat; more: its point down into the ground): d along it (root to point), e its ridged face
    (outward when hanging, up when out flat), tan across it, H the hinge."""
    ar = np.radians(a)
    rad = np.array([np.cos(ar), np.sin(ar), 0.0]); tan = np.array([-np.sin(ar), np.cos(ar), 0.0])
    up = np.array([0.0, 0.0, 1.0])
    f = np.radians(phi)
    d = np.sin(f) * rad - np.cos(f) * up
    e = np.cos(f) * rad + np.sin(f) * up
    H = rad * hinge[0] + up * (hinge[1] + z0)
    return d, e, tan, H


def blade_planes(d, e, tan, H, u0, u1, W0, W1, T0, T1, te):
    """a flat blade from u0 to u1 along d (half-spaces): W0 wide at u0 tapering to W1 at u1, flat underneath, a ridge
    down its middle on the e side (T0 thick at u0, T1 at u1, te at its edges)."""
    L = u1 - u0
    sa = (W0 - W1) / (2.0 * L)
    k = 2.0 * (T0 - te) / W0
    c = (T0 - T1) / L
    A = H + d * u0
    return [(-e, A), (-d, A), (d, H + d * u1),
            (tan + sa * d, A + tan * W0 / 2.0), (-tan + sa * d, A - tan * W0 / 2.0),
            (e + k * tan + c * d, A + e * T0), (e - k * tan + c * d, A + e * T0)]


def scene(X, Y, p=None, layout='ts', prog=None, pose=None, **kw):
    p = P if p is None else p
    g = dict(DONE); g.update(prog or {})
    pz = dict(p['settled']); pz.update(pose or {})
    x, y = to_local(X, Y, layout)
    H = np.zeros_like(X); C = np.zeros(X.shape, np.int16)
    extra = {'paint': np.full(X.shape, g['paint'], np.float32)}
    cacc = {}

    def slab(top, bot, comp, where, name=''):
        key = name.rstrip('0123456789') or 'part'
        if key not in cacc:
            cacc[key] = CropAcc(X.shape, n=3)
        top = np.broadcast_to(np.asarray(top, np.float32), X.shape); bot = np.broadcast_to(np.asarray(bot, np.float32), X.shape)
        cacc[key].add(np.maximum(bot, 0.0), top, comp, where & (top > bot) & (top > 0.0), name)

    rg, lg = p['ring'], p['legs']
    rr = np.hypot(x, y)
    ang = np.degrees(np.arctan2(y, x))
    z0 = float(pz['z'])                                  # the ring's bottom
    sink = float(pz['sink'])
    kn = float(np.clip(pz.get('knob', 1.0), 0, 1))
    zb = z0 - sink                                       # the body's foot
    # ---- the body (lathed); the ring hides what is inside it
    dz, rp, up, dn = body_profile(p)
    top, bot = lathe(rr, dz, up, dn)
    ok = np.isfinite(top)
    tz = np.where(ok, zb + top, -1.0); bz = np.where(ok, zb + bot, 0.0)
    slab(tz, bz, BODY, ok, 'L:body')
    ztop = zb + dz[-1]
    # ---- the collar and the knob (pulled down into the body as knob -> 0)
    cl, kb = p['collar'], p['knob']
    zc = ztop - (cl['h'] + kb['h']) * (1.0 - kn)
    cm = rr <= cl['r']
    slab(np.where(cm, zc + cl['h'], -1.0), zc - 2.0, COLLAR, cm, 'L:collar')
    km = rr <= kb['r']
    kz = zc + cl['h'] + kb['h'] * np.sqrt(np.clip(1 - (rr / kb['r']) ** 2, 0, 1)) ** 0.8
    slab(np.where(km, kz, -1.0), zc, KNOB, km, 'L:knob')
    # ---- the lamp and the eye: small domes on the body's skin
    for comp, q in ((LAMP, p['lamp']), (EYE, p['eye'])):
        u = q['dz'] / dz[-1]
        rs = float(np.interp(q['dz'], dz, rp))
        a = np.radians(q['az'])
        c = np.array([np.cos(a) * (rs - 0.3), np.sin(a) * (rs - 0.3), zb + q['dz']])
        d2 = q['r'] ** 2 - (x - c[0]) ** 2 - (y - c[1]) ** 2
        m = d2 > 0
        h = np.sqrt(np.maximum(d2, 0))
        slab(np.where(m, c[2] + h, -1.0), c[2] - h, comp, m, 'L:lamp')
    # ---- the ring
    ringm = (rr >= rg['r'][0]) & (rr <= rg['r'][1])
    # its top rounded off at the outer edge, a lip at the inner
    edge = np.clip((rr - (rg['r'][1] - 2.0)) / 2.0, 0, 1)
    rtop = z0 + rg['h'] - 1.2 * edge ** 2
    if int(kw.get('dmg', 0)):
        # damaged: a bite out of the ring's top on its south-west
        ang_ = np.degrees(np.arctan2(y, x))
        bite = np.clip(1.0 - np.abs(np.mod(ang_ - 128.0 + 180.0, 360.0) - 180.0) / 16.0, 0, 1)
        rtop = rtop - 3.2 * np.sqrt(bite) * (1.0 + 0.25 * np.sin(ang_ * 0.9 + rr))
    slab(np.where(ringm, rtop, -1.0), z0, RING, ringm, 'ring')
    # ---- the claws
    sv, cw = lg['sleeve'], lg['claw']
    Lt = float(pz.get('L', 46.0))
    dmg = int(kw.get('dmg', 0))
    for k in range(4):
        a = leg_az(k, layout)                             # N, E, S, W
        d, e, tan, Hh = claw_frame(a, lg['hinge'], float(pz['phi']), z0)
        cl = blade_planes(d, e, tan, Hh, Lt - cw['L'], Lt, cw['W0'], cw['W1'], cw['T0'], cw['T1'], cw['te'])
        if dmg and k == BROKEN_CLAW:
            # damaged: the east claw's point snapped off, the break slanting across it
            n_ = d + 0.45 * tan; n_ /= np.linalg.norm(n_)
            cl.append((n_, Hh + d * (Lt - DMG_CUT)))
        for nm, pl in (('sleeve', blade_planes(d, e, tan, Hh, -2.0, sv['L'], sv['W0'], sv['W1'], sv['T0'], sv['T1'], sv['te'])),
                       ('claw', cl)):
            lo, hi, m = convex_interval(x, y, pl)
            slab(np.where(m, hi, -1.0), lo, LEG, m, f'{nm}{k}')
    return hd.Scene(H.astype(np.float32), C, pack_slabs(cacc.values(), X.shape), extra)


COLORS = {BODY: (0, 214, 0), COLLAR: (120, 120, 124), KNOB: (36, 36, 38), LAMP: (255, 160, 0), EYE: (230, 230, 255),
          RING: (130, 130, 134), RLIGHT: (240, 240, 240), SLOT: (24, 24, 26), LEG: (0, 170, 0)}
