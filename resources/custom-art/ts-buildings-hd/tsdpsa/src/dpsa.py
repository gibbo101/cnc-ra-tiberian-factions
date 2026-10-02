"""
TS Sensor Array (GADPSA / GTDPSA; TSDPSA in the mod): the Mobile Sensor Array vehicle deployed, as a model for hd.py.

Built in its own frame (X east, Y south as TS draws it, units 1 cell = 128, Z up, origin at the centre of TS's 1x1
foundation), read from GTDPSA / GTDPSAMK / GTDPSA_A in TS's own camera (TS's ground centre at frame px (48, 60)):
  tracks   two track units along the vehicle's length (east-west), their ends raised (idlers), a row of road wheels
           on each outer face
  hull     a tan-ochre hull on and between the tracks, deck at z 34, a yellow stripe along its long top edges
  cab      a raised block at the east end, north side: a house-green light on its east face, a window on its south face
  wedge    a sloped housing on the deck, north of the mast: tall next to the mast, down to the deck at the east
  pod      a small white-topped box at the wedge's east foot
  mast     a tan cylinder (house-green panel on its south face) on a pivot near the west end: it lies along the deck
           pointing east (stowed) and swings up to stand (GTDPSAMK 15-28); brackets either side of its foot
  head     a radar dish on a turntable at the mast's top, facing south-east and up, a feed on a tripod at its focus;
           folded down to the east, it swings up and opens (GTDPSAMK 29-35); GTDPSA_A flashes a light bar across it
  legs     four outriggers from the hull's corners to pads on the ground (GTDPSAMK 1-14)
  antenna  a thin black whip behind the mast (TS shows it while the mast is down)
"""
import numpy as np
import hd
from radr import Acc, rod_interval, inbox
from dept import quad_interval

(TRACK, WHEEL, HUB, HULL, STRIPE, CAB, CABG, GLASS, WEDGE, POD, MAST, MASTG, BRACKET, ARMH, HEAD, HEADRIM, HEADL,
 LEG, PAD, ANT, LAMP, DECKP) = range(1, 23)
DEBRIS, DEB_IN, DEB_BURNT = 40, 41, 42
HOUSE = {CABG, MASTG}

P = dict(
    # track side profile in the x-z plane (the ends rise to the idlers); the two units' y spans (outer faces at +-46)
    track=dict(prof=((-41.0, 0.0), (48.0, 0.0), (60.0, 13.0), (56.0, 26.0), (-61.0, 26.0), (-66.0, 14.0)),
               y=(24.0, 46.0)),
    wheels=dict(xs=(-36.0, -16.5, 3.0, 22.5, 42.0), z=11.0, r=9.5, out=1.6, hub=3.6),
    hull=dict(x=(-58.0, 54.0), y=42.0, z=34.0, cham=3.5, stripe=3.2, plate=dict(x=(-26.0, 4.0), y=(10.0, 34.0))),
    cab=dict(x=(20.0, 53.0), y=(-34.0, -6.0), z=44.0, cham=3.0,
             light=dict(y=(-29.0, -11.0), z=(26.0, 41.0)), glass=dict(x=(32.0, 50.0), z=(35.0, 42.0))),
    wedge=dict(x=(-42.0, 9.0), y=(-22.0, 2.0), z=(57.0, 34.0), flat=-14.0, cham=2.5),
    pod=dict(x=(6.0, 18.0), y=(-27.0, -13.0), z=41.0),
    # mast: pivot (x, y, z), radius, length below / above the pivot; the green panel's span along the axis and its
    # half-width (degrees round the axis from due south)
    mast=dict(pivot=(-37.5, 19.0, 48.0), r=14.0, below=26.0, above=102.0, green=dict(s=(6.0, 50.0), half=38.0),
              brackets=dict(x=(-46.0, -29.0), ys=((34.0, 41.0), (-2.0, 4.0)), z=41.0, r=7.0)),
    # the head: a radar dish (a paraboloid: rim radius R, depth, shell t) on a turntable and a short post on the mast's
    # top; it faces south-east (towards TS's camera) at `el` degrees up; pivot = the post's top, relative to the mast's
    # top (x east, y south, z up); folded (build-up 28) it hangs pointing down to the east, then swings up and opens
    head=dict(R=21.0, depth=6.5, t=2.2, el=35.0, az=10.0, pivot=(2.0, 1.0, 12.0), back=2.0,
              fold=dict(el=-60.0, az=0.0), table=dict(r=9.0, h=4.0), post_r=3.4,
              feed=dict(r=1.0, knob=2.6, nstruts=3, strut_r=0.75), bar=dict(w=2.6)),
    legs=dict(hinge=((-56.0, 36.0, 20.0), (-56.0, -36.0, 20.0), (52.0, 36.0, 20.0), (52.0, -36.0, 20.0)),
              foot=((-69.5, 45.0), (-70.0, -50.0), (62.0, 42.0), (60.0, -50.0)), r=3.2, pad=6.5, padh=3.0),
    ant=dict(c=(-48.0, -4.0), r=1.5, z=(34.0, 91.0)),
)

LAYOUTS = {'ts': dict(turn=False), 'ra': dict(turn=False), 'ra1': dict(turn=True)}


def to_local(X, Y, layout='ts'):
    """'ra1': turned a quarter (TS east -> RA south: the cab towards the camera, the mast at the back)."""
    return (Y, -X) if LAYOUTS[layout]['turn'] else (X, Y)


def to_world(x, y, layout='ts'):
    return (-y, x) if LAYOUTS[layout]['turn'] else (x, y)


def mast_axis(p, theta):
    """theta: 0 stowed (along the deck, pointing east), 90 standing.  -> pivot, unit axis, bottom, top."""
    m = p['mast']
    th = np.radians(theta)
    u = np.array([np.cos(th), 0.0, np.sin(th)])
    pv = np.array(m['pivot'])
    return pv, u, pv - m['below'] * u, pv + m['above'] * u


def smooth01(t):
    t = float(np.clip(t, 0, 1))
    return t * t * (3 - 2 * t)


def head_pose(p, theta, unfold):
    """the radar dish's frame on the upright mast (the head is only out once the mast stands): dict of the axis n (the
    way its hollow faces), vertex V, rim centre C, feed F (its focus), focal length, rim radius R, the post's top
    (pivot) and the turntable's top.  unfold 0: folded (pointing down to the east, its rim drawn in); 1: open."""
    h = p['head']
    pv, u, bot, top = mast_axis(p, theta)
    s = smooth01(unfold)
    el = np.radians(h['fold']['el'] + (h['el'] - h['fold']['el']) * s)
    az = np.radians(h['fold']['az'] + (h['az'] - h['fold']['az']) * s)
    n = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    table = top + np.array([0.0, 0.0, h['table']['h']])
    piv = top + np.array(h['pivot'])
    f = h['R'] ** 2 / (4.0 * h['depth'])
    R = h['R'] * (0.45 + 0.55 * s)
    V = piv + h['back'] * n
    C = V + (R * R / (4.0 * f)) * n
    F = V + f * n
    return dict(n=n, V=V, C=C, F=F, focal=f, R=R, pivot=piv, table=table, top=top)


def head_struts(p, df):
    """the feed's tripod (rim -> feed) and the feed knob, as (p0, p1, r)."""
    h = p['head']; fd = h['feed']; n = df['n']
    u1 = np.cross(n, [0, 0, 1.0]); u1 /= np.linalg.norm(u1); u2 = np.cross(n, u1)
    out = []
    for k in range(fd['nstruts']):
        a = 2 * np.pi * (k + 0.25) / fd['nstruts']
        rim = df['C'] + df['R'] * 0.95 * (np.cos(a) * u1 + np.sin(a) * u2)
        out.append((rim, df['F'], fd['strut_r']))
    out.append((df['F'] - 2.0 * n, df['F'] + 2.5 * n, fd['knob']))
    return out


def leg_pose(p, i, k):
    """outrigger i at deployment k: 0 folded (tucked into the hull's end, lying across it), 0.55 swung out level, 1
    down on its pad (TS: GTDPSAMK 1-10 the legs swing out, 11-14 they come down).  -> hinge, foot."""
    lg = p['legs']
    hx, hy, hz = lg['hinge'][i]
    fx, fy = lg['foot'][i]
    k = float(np.clip(k, 0, 1))
    D = np.array([fx - hx, fy - hy, lg['padh'] - hz])
    L = np.linalg.norm(D)
    O = np.array([fx - hx, fy - hy, 0.0]); O = O / np.linalg.norm(O)
    F = np.array([0.0, -np.sign(hy), 0.0])
    D = D / L

    def slerp(a, b, t):
        om = np.arccos(np.clip(np.dot(a, b), -1, 1))
        if om < 1e-6:
            return a
        return (np.sin((1 - t) * om) * a + np.sin(t * om) * b) / np.sin(om)
    v = slerp(F, O, k / 0.55) if k < 0.55 else slerp(O, D, (k - 0.55) / 0.45)
    return np.array([hx, hy, hz]), np.array([hx, hy, hz]) + L * v


def mast_panel(x, y, z, theta, p=None):
    """True where a mast surface point is on its house-green panel: s (along the axis from the pivot) in the panel's
    span, within `half` degrees round the axis from due south."""
    p = P if p is None else p
    m = p['mast']
    pv, u, bot, top = mast_axis(p, theta)
    dx, dy, dz = x - pv[0], y - pv[1], z - pv[2]
    s = dx * u[0] + dz * u[2]
    w = np.array([np.sin(np.radians(theta)), 0.0, -np.cos(np.radians(theta))])
    a = dy; b = dx * w[0] + dz * w[2]
    ang = np.degrees(np.arctan2(b, a))
    return (s >= m['green']['s'][0]) & (s <= m['green']['s'][1]) & (np.abs(ang) <= m['green']['half'])


BUILD_KEYS = ('legs_e', 'legs_w', 'theta', 'unfold', 'wheel')
DONE = dict(legs_e=1.0, legs_w=1.0, theta=90.0, unfold=1.0)


def scene(X, Y, p=None, layout='ts', prog=None, parts=None, level=0, merge=True):
    p = P if p is None else p
    g = dict(DONE); g.update(prog or {})
    x, y = to_local(X, Y, layout)
    H = np.zeros_like(X); C = np.zeros(X.shape, np.int16)
    acc = Acc(X.shape, n=8)
    extra = {}

    def put(h, comp, where=None):
        nonlocal H, C
        if where is not None:
            h = np.where(where, h, 0.0)
        win = h > H + 1e-6
        H = np.where(win, h, H); C = np.where(win, comp, C)

    # ------------------------------------------------------------------------------------------------- tracks
    t = p['track']
    lo, hi, ok = quad_interval(x, list(t['prof']))
    ya, yb = t['y']
    for sgn in (1, -1):
        m = ok & (sgn * y >= ya) & (sgn * y <= yb)
        acc.add(lo, hi, TRACK, m, 'track')
        # road wheels on the outer face, a hub in each
        wh = p['wheels']
        for xc in wh['xs']:
            rr = (x - xc) ** 2
            hh = np.sqrt(np.clip(wh['r'] ** 2 - rr, 0, None))
            mw = (rr <= wh['r'] ** 2) & (sgn * y > yb) & (sgn * y <= yb + wh['out'])
            acc.add(wh['z'] - hh, wh['z'] + hh, WHEEL, mw, 'wheel')
            hh2 = np.sqrt(np.clip(wh['hub'] ** 2 - rr, 0, None))
            mh = (rr <= wh['hub'] ** 2) & (sgn * y > yb + wh['out']) & (sgn * y <= yb + wh['out'] + 1.2)
            acc.add(wh['z'] - hh2, wh['z'] + hh2, HUB, mh, 'hub')
    extra['track_x'] = x.astype(np.float32)
    # -------------------------------------------------------------------------------------------------- hull
    hl = p['hull']
    m = inbox(x, y, hl['x'], (-hl['y'], hl['y']))
    e = np.minimum(np.minimum(x - hl['x'][0], hl['x'][1] - x), hl['y'] - np.abs(y))
    put(np.where(m, hl['z'] - np.clip(hl['cham'] - e, 0, None), 0.0), HULL)
    # the yellow stripe on the long top edges (the chamfer and a band on the deck's edge)
    C = np.where(m & (C == HULL) & (hl['y'] - np.abs(y) <= hl['stripe'] + 0.5) & (x > hl['x'][0] + 2.0) &
                 (x < hl['x'][1] - 2.0), STRIPE, C)
    # a raised deck plate south of the wedge (the stowed mast lies on it)
    pl = hl['plate']
    put(np.where(inbox(x, y, pl['x'], pl['y']), hl['z'] + 1.5, 0.0), DECKP)
    # ---------------------------------------------------------------------------------------------- cab, wedge, pod
    cb = p['cab']
    m = inbox(x, y, cb['x'], cb['y'])
    e = np.minimum(np.minimum(x - cb['x'][0], cb['x'][1] - x), np.minimum(y - cb['y'][0], cb['y'][1] - y))
    put(np.where(m, cb['z'] - np.clip(cb['cham'] - e, 0, None), 0.0), CAB)
    lt = cb['light']
    acc.add(np.full(X.shape, lt['z'][0]), np.full(X.shape, lt['z'][1]), CABG,
            inbox(x, y, (cb['x'][1], cb['x'][1] + 1.2), lt['y']), 'cabg')
    gl = cb['glass']
    acc.add(np.full(X.shape, gl['z'][0]), np.full(X.shape, gl['z'][1]), GLASS,
            inbox(x, y, gl['x'], (cb['y'][1], cb['y'][1] + 1.2)), 'glass')
    wd = p['wedge']
    m = inbox(x, y, wd['x'], wd['y'])
    zt = wd['z'][0] + (wd['z'][1] - wd['z'][0]) * np.clip((x - wd['flat']) / (wd['x'][1] - wd['flat']), 0, 1)
    e = np.minimum(np.minimum(x - wd['x'][0], wd['x'][1] - x), np.minimum(y - wd['y'][0], wd['y'][1] - y))
    put(np.where(m, zt - np.clip(wd['cham'] - e, 0, None), 0.0), WEDGE)
    pd = p['pod']
    put(np.where(inbox(x, y, pd['x'], pd['y']), pd['z'], 0.0), POD)
    # ----------------------------------------------------------------------------------------------- the mast
    mt = p['mast']
    theta = float(g['theta'])
    pv, u, bot, top = mast_axis(p, theta)
    lo, hi, ok = rod_interval(x, y, bot, top, mt['r'])
    acc.add(lo, hi, MAST, ok, 'mast')
    # a dark cap on its top end
    lo2, hi2, ok2 = rod_interval(x, y, top - 3.0 * u, top + 2.0 * u, mt['r'] - 1.5)
    acc.add(lo2, hi2, ARMH, ok2, 'cap')
    bk = mt['brackets']
    for (b0, b1) in bk['ys']:
        mb = inbox(x, y, bk['x'], (b0, b1))
        # a plate rising to a round top round the pivot
        cx_ = pv[0]
        zb = np.where(np.abs(x - cx_) <= bk['r'], pv[2] + np.sqrt(np.clip(bk['r'] ** 2 - (x - cx_) ** 2, 0, None)),
                      pv[2] - (np.abs(x - cx_) - bk['r']) * 1.2)
        put(np.where(mb, np.clip(np.minimum(zb, bk['z']), hl['z'], None), 0.0), BRACKET)
    extra['mast_theta'] = np.full(X.shape, theta, np.float32)
    extra['head_unfold'] = np.full(X.shape, float(g['unfold']), np.float32)
    # ------------------------------------------------------------------------------------------------ the head
    hd_ = p['head']
    unfold = float(g['unfold'])
    # (its own slab layers: merged into the mast's they would carry the dish's component down the mast's side)
    acc_h = Acc(X.shape, n=4)
    if theta >= 89.0:
        df = head_pose(p, theta, unfold)
        # the turntable on the mast's top, the post up to the dish's pivot
        lo, hi, ok = rod_interval(x, y, top - 1.0 * u, df['table'], hd_['table']['r'])
        acc.add(lo, hi, ARMH, ok, 'table')
        lo, hi, ok = rod_interval(x, y, df['table'] - 1.0 * u, df['pivot'] + 1.0 * df['n'], hd_['post_r'])
        acc_h.add(lo, hi, ARMH, ok, 'post')
        # the dish shell (a paraboloid cap: up to two Z intervals over a ground point)
        from radr import dish_intervals
        for k, (lo, hi, ok) in enumerate(dish_intervals(x, y, df, df['R'], hd_['t'])):
            acc_h.add(lo, hi, HEAD, ok, f'head{k}')
        if unfold >= 0.75:
            for (a0, a1, r_) in head_struts(p, df):
                lo, hi, ok = rod_interval(x, y, a0, a1, r_)
                acc_h.add(lo, hi, ARMH, ok, 'feed')
    # -------------------------------------------------------------------------------------------- the outriggers
    lg = p['legs']
    for i in range(4):
        k = g['legs_w'] if lg['hinge'][i][0] < 0 else g['legs_e']
        a, b = leg_pose(p, i, k)
        lo, hi, ok = rod_interval(x, y, a, b, lg['r'])
        acc.add(np.maximum(lo, 0.0), hi, LEG, ok & (hi > 0), 'leg')
        # the pad: a short disc at the leg's end (level on the ground when down)
        rr = (x - b[0]) ** 2 + (y - b[1]) ** 2
        mp = rr <= lg['pad'] ** 2
        acc.add(np.full(X.shape, max(b[2] - lg['padh'], 0.0)), np.full(X.shape, b[2] + 0.5), PAD, mp, 'pad')
    # ------------------------------------------------------------------------------------------------ antenna
    an = p['ant']
    rr = (x - an['c'][0]) ** 2 + (y - an['c'][1]) ** 2
    put(np.where(rr <= an['r'] ** 2, an['z'][1], 0.0), ANT)
    return hd.Scene(H, C, acc.slabs() + acc_h.slabs(), extra)


FLAT = {TRACK: (60, 60, 60), WHEEL: (121, 121, 121), HUB: (40, 40, 40), HULL: (198, 157, 105), STRIPE: (255, 226, 101),
        CAB: (190, 145, 60), CABG: (0, 170, 0), GLASS: (170, 170, 196), WEDGE: (165, 133, 89), POD: (230, 230, 230),
        MAST: (198, 157, 105), MASTG: (0, 190, 0), BRACKET: (200, 200, 200), ARMH: (60, 60, 60), HEAD: (68, 68, 68),
        HEADRIM: (140, 140, 120), HEADL: (101, 101, 125), LEG: (230, 180, 80), PAD: (150, 120, 60), ANT: (20, 20, 20),
        LAMP: (255, 255, 255), DECKP: (190, 145, 60)}
