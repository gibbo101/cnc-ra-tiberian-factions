"""
TS Radar (GARADR / GTRADR; TSRADR in the mod) as a model for hd.py.

Built in its own frame ("local": X east, Y south as TS draws it, units 1 cell = 128, Z up, origin at the centre of TS's
2x2 foundation, X -128..128, Y -128..128), read from GTRADR / GTRADRMK / GTRADR_A in TS's own camera:
  plinth   a low tan base over most of the foundation (TS's MK 01 outline: the north-west corner and a notch in the
           south edge left out)
  swblock  a tan block at the south-west with a green top
  sbox     a green box south of the tower, between the block and the rotunda
  rotunda  a stepped square pedestal at the south-east corner, a ring of posts, a dome
  ramp     a green ramped panel along the east side with a hoop at its south end
  tower    the core: a frame of legs and machinery up to a deep deck; on the deck a raised back part, the antennas
           (GTRADR_A draws them) and the dish's turret
  dish     GTRADR_A: a big shallow dish (rim radius 88) on an arm from the turret, tilted 59 degrees up, sweeping in
           azimuth (TS frames 0-14: from facing almost due south to south-south-east); six struts from the rim to the
           feed in front of it, a feed rod

Geometry helpers turn any solid with a simple vertical cross-section (tilted rods, the dish shell) into slabs: the
interval(s) of Z it fills over each ground point.
"""
import numpy as np
import hd
import wnoise as WN

(PLINTH, TAN, GREEN, DARK, GREY, ROT, DOME, POST, RAMP, HOOP, DECK, DECKS, LEG, MACH, TURRET, MAST, MASTTIP, DISH,
 STRUT, FEED, ROD, ARM, GTOP, SBOX, RAMPG, PIPE, SLAB, RED, LIFT) = range(1, 30)
DEBRIS, DEB_IN, DEB_BURNT = 40, 41, 42              # damage: rubble, the dark inside of a hole, burnt
HOUSE = {GREEN, GTOP, SBOX, RAMPG}

P = dict(
    plinth=dict(poly=((-128.0, -54.0), (-128.0, 92.0), (-96.0, 128.0), (-42.0, 128.0), (-14.0, 98.0), (6.0, 100.0),
                      (10.0, 128.0), (104.0, 128.0), (128.0, 104.0), (128.0, -88.0), (-72.0, -88.0), (-72.0, -54.0)),
                h=5.0),
    swblock=dict(x=(-112.0, -28.0), y=(30.0, 112.0), z=40.0, cham=6.0,
                 gtop=dict(half=23.0, z=55.0, bevel=4.0)),
    sbox=dict(x=(-22.0, -1.0), y=(44.0, 101.0), z=35.0),
    rotunda=dict(c=(66.5, 80.0), ped=((45.0, 22.0), (36.0, 30.0)), posts=dict(r=22.0, n=8, w=2.6, z=(30.0, 61.0)),
                 dome=dict(r=24.5, rz=29.0, zc=61.0)),
    # the east ramp: a concave chute rising to the north, its east rim a light metal arc (TS's hoop)
    # the east ramp: level on top at its north end, rounding down to the ground at its south end (a quarter ellipse,
    # like the war factory's fenders); a light rail along its east edge; green panels on top
    ramp=dict(x=(60.0, 108.0), y=(-76.0, 22.0), z=29.0, ycurve=-36.0, rail=2.6),
    eastbase=dict(x=(14.0, 60.0), y=(-84.0, -12.0), z=40.0),
    tower=dict(legs=((-65.0, -72.0), (5.0, -72.0), (-65.0, 30.0), (-4.5, -47.0)), leg=6.5, z=112.0,
               core=dict(x=(-56.0, -20.0), y=(-78.0, -22.0)),
               tank=dict(c=(-38.0, -8.0), r=13.0, z=(5.0, 96.0)),
               rbox=dict(x=(-14.0, 8.0), y=(-44.0, -18.0), z=(30.0, 84.0)),
               box=dict(x=(-100.0, -70.0), y=(0.0, 40.0), z=(55.0, 80.0)),
               ledge=dict(x=(-80.0, -30.0), y=(0.0, 45.0), z=(92.0, 112.0)),
               pipe=dict(x=-27.0, y=(-15.0, 22.0), z=75.0, r=8.0)),
    deck=dict(x=(-77.0, 17.0), y=(-84.0, 42.0), z=(112.0, 140.0),
              # v2 (Luke 4 Oct): the deck is the command room: walls with a big dark window band all round (TS's black
              # line round it), a flat roof (v1's ribbed top read as a wooden pallet)
              window=(117.0, 132.0), mullion=12.0),
    # v2 (Luke 4 Oct): under the command room pillars and supports and a lift going up to it, in place of v1's
    # machinery (the dark core, the tank, the boxes, the ledge, the pipe): six steel pillars, X-bracing between them
    # on every side in two tiers with a ring beam, and an open lift shaft (corner posts, frames) with its car
    frame=dict(pillars=((-70.0, -77.0), (-30.0, -77.0), (10.0, -77.0), (-70.0, 35.0), (-30.0, 35.0), (10.0, 35.0)),
               pw=5.0, brace_r=1.9, tiers=(0.38, 0.97),
               # the lift: an enclosed shaft from the plinth up into the command room, behind the south bracing; a glass
               # slot up its south face shows the car; a door at its foot
               lift=dict(x=(-24.0, -4.0), y=(12.0, 30.0), car=(58.0, 76.0), slot=5.0, door=(5.0, 24.0))),
    upper=dict(x=(-77.0, -10.0), y=(-84.0, -20.0), z=163.0),
    upperw=dict(x=(-77.0, -52.0), y=(-22.0, 34.0), z=180.0),
    turret=dict(c=(8.0, -67.0), r=14.0, z=(105.0, 148.0)),
    # antennas: (x, y, base z, thick-body top z, thin top z, thick radius)
    # v2 (Luke 4 Oct: the antennas clipped through the dish as it swept): each antenna the dish passed through slid
    # back along TS's view ray (x, y -1.225 s, z -s: the same TS pixels) until the dish clears it by >= 4 units over
    # its whole sweep (radrclear.py): 0 by 18, 1 and 2 by 12, 5 by 6, 6 by 10; 3 and 4 were clear. The west three
    # stand on a bracket off the tower's west side, the north two on one off its back (mbrackets). v1's:
    # ((-70, 26, 180, 308, 348, 4.6), (-76, -7, 180, 0, 275, 0), (-75, -16, 180, 0, 294, 0), (-64, -80, 163, 285, 359, 4.6),
    #  (-56, -82, 163, 0, 322, 0), (-20, -84, 163, 290, 330, 4.6), (-5, -80, 163, 0, 313, 0))
    masts=dict(pts=((-92.0, 4.0, 162.0, 290.0, 330.0, 4.6), (-90.7, -21.7, 162.0, 0.0, 263.0, 0.0),
                    (-89.7, -30.7, 162.0, 0.0, 282.0, 0.0), (-64.0, -80.0, 163.0, 285.0, 359.0, 4.6),
                    (-56.0, -82.0, 163.0, 0.0, 322.0, 0.0), (-27.4, -91.4, 153.0, 284.0, 324.0, 4.6),
                    (-17.2, -92.2, 153.0, 0.0, 303.0, 0.0)), r=2.2),
    # the antennas' brackets: steel platforms bolted to the tower's west side and its back, (x0, x1), (y0, y1), (z0, z1)
    mbrackets=(((-98.0, -76.0), (-37.0, 10.0), (155.0, 162.0)), ((-33.0, -11.0), (-98.0, -83.0), (146.0, 153.0))),
    # the dish: rim centre orbits the turret axis at rho, at height zc; tilt (elevation of its axis), azimuth per frame
    dish=dict(rho=59.7, zc=253.0, R=88.2, depth=23.0, t=4.5, elev=59.0, az=(92.3, 62.5), feed=77.0,
              strut_r=1.6, nstruts=6, rod=dict(elev=70.0, L=80.0, r=1.8), hub_r=6.0, arm_r=5.0),
)

LAYOUTS = {'ts': dict(turn=False), 'ra': dict(turn=False)}


def to_local(X, Y, layout='ts'):
    if LAYOUTS[layout]['turn']:
        return Y, -X
    return X, Y


def to_world(x, y, layout='ts'):
    if LAYOUTS[layout]['turn']:
        return -y, x
    return x, y


def in_poly(x, y, poly):
    inside = np.zeros(np.shape(x), bool)
    pts = list(poly)
    for i in range(len(pts)):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
        c = ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1)
        inside ^= c
    return inside


def inbox(x, y, bx, by):
    return (x >= bx[0]) & (x <= bx[1]) & (y >= by[0]) & (y <= by[1])


# ------------------------------------------------------------------------------------- solids as vertical intervals
def grid_window(x, y, xr, yr, pad=2.0):
    """the (row, col) window of the ground grid x, y (affine in its indices: hd's screen-aligned grid) that holds the
    world box xr x yr (padded), or None if it is off the grid."""
    if x.ndim != 2 or x.shape[0] < 2 or x.shape[1] < 2:
        return (slice(None), slice(None))
    x00, y00 = float(x[0, 0]), float(y[0, 0])
    A = np.array([[x[1, 0] - x00, x[0, 1] - x00], [y[1, 0] - y00, y[0, 1] - y00]], float)
    try:
        Ai = np.linalg.inv(A)
    except np.linalg.LinAlgError:
        return (slice(None), slice(None))
    xs_ = (xr[0] - pad, xr[1] + pad); ys_ = (yr[0] - pad, yr[1] + pad)
    rc = np.array([Ai @ np.array([cx - x00, cy - y00]) for cx in xs_ for cy in ys_])
    r0 = int(np.floor(rc[:, 0].min())) - 1; r1 = int(np.ceil(rc[:, 0].max())) + 2
    c0 = int(np.floor(rc[:, 1].min())) - 1; c1 = int(np.ceil(rc[:, 1].max())) + 2
    r0, c0 = max(r0, 0), max(c0, 0); r1, c1 = min(r1, x.shape[0]), min(c1, x.shape[1])
    if r1 <= r0 or c1 <= c0:
        return None
    return (slice(r0, r1), slice(c0, c1))


def add_rod(acc, x, y, p0, p1, r, comp, name=''):
    """rod_interval + acc.add over just the rod's own window of the grid."""
    w = grid_window(x, y, (min(p0[0], p1[0]) - r, max(p0[0], p1[0]) + r), (min(p0[1], p1[1]) - r, max(p0[1], p1[1]) + r))
    if w is None:
        return
    lo, hi, m = rod_interval(x[w], y[w], p0, p1, r)
    acc.add(lo, hi, comp, m, name, win=w)


def rod_interval(x, y, p0, p1, r):
    """a cylinder of radius r from p0 to p1 (3D, local frame): (bot, top, mask) of Z over each ground point."""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    d = p1 - p0; L = np.linalg.norm(d); d = d / L
    ax, ay = x - p0[0], y - p0[1]                        # P - p0 = (ax, ay, Z - p0z)
    if abs(d[2]) > 0.9999:                               # vertical
        m = ax * ax + ay * ay <= r * r
        zlo, zhi = min(p0[2], p1[2]), max(p0[2], p1[2])
        return np.full(x.shape, zlo), np.full(x.shape, zhi), m
    # q(Z) = |P-p0|^2 - ((P-p0).d)^2 <= r^2 with w = Z - p0z:  (1 - dz^2) w^2 + 2 w (-(c) dz) + (ax^2 + ay^2 - c^2)
    c = ax * d[0] + ay * d[1]
    A = 1.0 - d[2] ** 2
    B = -2.0 * c * d[2]
    C = ax * ax + ay * ay - c * c - r * r
    disc = B * B - 4 * A * C
    ok = disc >= 0
    sq = np.sqrt(np.maximum(disc, 0))
    w1 = (-B - sq) / (2 * A); w2 = (-B + sq) / (2 * A)
    # along the axis: 0 <= c + w dz <= L
    if abs(d[2]) < 1e-9:
        ok &= (c >= 0) & (c <= L)
        lo, hi = w1, w2
    else:
        wa = (0 - c) / d[2]; wb = (L - c) / d[2]
        lo = np.maximum(w1, np.minimum(wa, wb)); hi = np.minimum(w2, np.maximum(wa, wb))
        ok &= hi > lo
    return lo + p0[2], hi + p0[2], ok


def dish_frame(p, az_deg, layout='ts'):
    """the dish's geometry for a frame: dict of vertex V, axis n, rim centre C, feed F, rod tip, turret axis."""
    d = p['dish']; tu = p['turret']
    e = np.radians(d['elev']); a = np.radians(az_deg)
    n = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    ax_ = np.array([tu['c'][0], tu['c'][1], 0.0])
    C = ax_ + np.array([d['rho'] * np.cos(a), d['rho'] * np.sin(a), d['zc']])
    V = C - d['depth'] * n
    F = C + d['feed'] * n
    er = np.radians(d['rod']['elev'])
    rdir = np.array([np.cos(er) * np.cos(a), np.cos(er) * np.sin(a), np.sin(er)])
    focal = d['R'] ** 2 / (4.0 * d['depth'])
    return dict(n=n, C=C, V=V, F=F, tip=F + d['rod']['L'] * rdir, axis=ax_, focal=focal, a=a)


def dish_intervals(x, y, df, R, t):
    """the dish shell (a paraboloid cap, vertex V, axis n, focal length f, rim radius R, thickness t behind the
    surface) over each ground point: up to two Z intervals [(bot, top, mask), (bot, top, mask)]."""
    V, n, f = df['V'], df['n'], df['focal']
    px, py = x - V[0], y - V[1]                 # P - V = (px, py, Z - Vz) ; write w = Z - Vz
    pn0 = px * n[0] + py * n[1]                 # (P - V).n = pn0 + w nz
    nz = n[2]
    # rho^2 = |P-V|^2 - ((P-V).n)^2 = (1 - nz^2) w^2 + 2 w (-pn0 nz) + (px^2 + py^2 - pn0^2)
    a2 = 1.0 - nz * nz
    b2 = -2.0 * pn0 * nz
    c2 = px * px + py * py - pn0 * pn0
    # g(w) = rho^2/(4f) - (pn0 + w nz): the surface is g = 0, the shell 0 <= g <= t (behind it along the axis)
    A = a2 / (4 * f); B = b2 / (4 * f) - nz; C0 = c2 / (4 * f) - pn0

    def roots(Cc):
        disc = B * B - 4 * A * Cc
        ok = disc >= 0
        sq = np.sqrt(np.maximum(disc, 0))
        return (-B - sq) / (2 * A), (-B + sq) / (2 * A), ok
    o1, o2, ook = roots(C0 - t)                 # g <= t  -> [o1, o2]
    i1, i2, iok = roots(C0)                     # g < 0   -> (i1, i2): carved out
    # rim: rho^2 <= R^2
    disc = b2 * b2 - 4 * a2 * (c2 - R * R)
    rok = disc >= 0
    sq = np.sqrt(np.maximum(disc, 0))
    r1, r2 = (-b2 - sq) / (2 * a2), (-b2 + sq) / (2 * a2)
    lo1 = np.maximum(o1, r1); hi1 = np.minimum(np.where(iok, i1, o2), r2)
    lo2 = np.maximum(np.where(iok, i2, o2), r1); hi2 = np.minimum(o2, r2)
    m1 = ook & rok & (hi1 > lo1)
    m2 = ook & rok & iok & (hi2 > lo2)
    return [(lo1 + V[2], hi1 + V[2], m1), (lo2 + V[2], hi2 + V[2], m2)]


def dish_normal(X, Y, Z, df):
    """outward-ish normal of the dish surface at a point (the gradient of g), not yet faced to the camera."""
    P = np.stack([X - df['V'][0], Y - df['V'][1], Z - df['V'][2]], -1)
    n = df['n']
    w = P @ n
    g = (P - w[..., None] * n) / (2 * df['focal']) - n
    return g / (np.linalg.norm(g, axis=-1, keepdims=True) + 1e-9)


def dish_rods(p, df):
    """the struts (rim -> feed), the feed rod and the arm (turret -> dish back) as (p0, p1, r, comp)."""
    d = p['dish']
    n = df['n']
    u1 = np.cross(n, [0, 0, 1.0]); u1 /= np.linalg.norm(u1); u2 = np.cross(n, u1)
    out = []
    for k in range(d['nstruts']):
        a = 2 * np.pi * (k + 0.5) / d['nstruts']
        rim = df['C'] + d['R'] * 0.97 * (np.cos(a) * u1 + np.sin(a) * u2)
        out.append((rim, df['F'], d['strut_r'], STRUT))
    out.append((df['F'], df['tip'], d['rod']['r'], ROD))
    out.append((df['F'] - 9.0 * n, df['F'] + 5.0 * n, d['hub_r'], FEED))          # the feed horn
    tu = p['turret']
    top = df['axis'] + np.array([0, 0, tu['z'][1] - 6.0])
    back = df['V'] - 4.0 * n
    out.append((top, back, d['arm_r'], ARM))
    return out


# damaged masts: (lean degrees, lean direction degrees from east towards south, fraction of the length left)
MAST_DMG = ((38.0, 160.0, 0.78), (34.0, 150.0, 0.62), (0.0, 0.0, 0.22), (10.0, 175.0, 1.0), (0.0, 0.0, 0.08),
            (0.0, 0.0, 1.0), (7.0, 20.0, 0.85))
# the RA grid view leans them less and further back (TS's leans would carry the west masts out of the RA canvas)
MAST_DMG_RA = ((24.0, 232.0, 0.62), (22.0, 228.0, 0.62), (0.0, 0.0, 0.22), (8.0, 190.0, 1.0), (0.0, 0.0, 0.08),
               (0.0, 0.0, 1.0), (6.0, 20.0, 0.85))      # v2: the west two lean further back (they stand further west now)
BROKEN_PHI = (-80.0, 52.0)                      # the dish's broken-away part, degrees round its rim (0 = its right)


def dish_phi(P, df):
    n = df['n']
    u1 = np.cross(n, [0, 0, 1.0]); u1 /= np.linalg.norm(u1); u2 = np.cross(n, u1)
    d = np.asarray(P, float) - df['C']
    return float(np.degrees(np.arctan2(d @ u2, d @ u1)))


def dish_phi_field(x, y, z, df):
    n = df['n']
    u1 = np.cross(n, [0, 0, 1.0]); u1 /= np.linalg.norm(u1); u2 = np.cross(n, u1)
    dx, dy, dz = x - df['C'][0], y - df['C'][1], z - df['C'][2]
    return np.degrees(np.arctan2(dx * u2[0] + dy * u2[1] + dz * u2[2], dx * u1[0] + dy * u1[1] + dz * u1[2]))


def dish_broken(x, y, z, df, R):
    """TS 01's dish: a big piece of its right side broken away (ragged), a bite out of its left rim."""
    n = df['n']
    u1 = np.cross(n, [0, 0, 1.0]); u1 /= np.linalg.norm(u1); u2 = np.cross(n, u1)
    dx, dy, dz = x - df['C'][0], y - df['C'][1], z - df['C'][2]
    a = dx * u1[0] + dy * u1[1] + dz * u1[2]
    b = dx * u2[0] + dy * u2[1] + dz * u2[2]
    ph = np.degrees(np.arctan2(b, a)); rho = np.hypot(a, b)
    # ragged in the dish's own plane (noise over its face, not along its rings: no specks or fingers)
    rag = WN.noise(a * 1.0 + 300.0, b * 1.0 + 300.0, 10.0, 751)
    lo, hi = BROKEN_PHI
    mid = np.radians(0.5 * (lo + hi)); half = np.radians(0.5 * (hi - lo))
    # the broken part: past a ragged line across the dish (its far side towards the sector's middle)
    along = a * np.cos(mid) + b * np.sin(mid)
    dph = np.abs(((ph - np.degrees(mid) + 180.0) % 360.0) - 180.0)
    gone = (along > R * (0.10 + 0.13 * rag)) & (dph < np.degrees(half) + 25.0)
    # the rim goes with the skin: near where the break line meets the rim (nearly tangent there) it would leave thin
    # slivers of rim hanging over the gap, so a band along the rim breaks away a little further round
    lim = np.degrees(np.arccos(np.clip(0.165, -1, 1))) + 13.0 + 6.0 * rag
    gone |= (rho > R * (0.74 + 0.06 * rag)) & (dph < lim)
    bite = (np.abs(((ph - 190.0 + 180.0) % 360.0) - 180.0) < 18.0 + 6.0 * rag) & (rho > R * (0.80 + 0.05 * rag))
    return gone | bite


def smoothstep_(e0, e1, v):
    t = np.clip((v - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def dblob(X, Y, cx, cy, rx, ry, rough, seed, feat=7.0):
    e = np.sqrt(((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2)
    return e - 1.0 - rough * WN.noise(X, Y, feat, seed)


# ------------------------------------------------------------------------------------- the scene
PARTS = ('plinth', 'swblock', 'sbox', 'rotunda', 'ramp', 'tower', 'deck', 'upper', 'turret', 'masts', 'dish')
BASE_PARTS = tuple(k for k in PARTS if k not in ('masts', 'dish'))     # GTRADR: no antennas, no dish (GTRADR_A draws them)
BUILD_KEYS = ('slab', 'swblock', 'rotunda', 'tower', 'lift', 'upper', 'masts', 'sbox', 'eastbase', 'ramp', 'turret',
              'dish', 'paint')
DONE = {k: 1.0 for k in BUILD_KEYS}


class Acc:
    """per-ground-point Z intervals in a few layers (slabs): an interval that overlaps (or nearly touches) one already
    in a layer is merged into it, else it goes into the first free layer."""
    def __init__(self, shape, n=6):
        self.top = [np.full(shape, -1.0, np.float32) for _ in range(n)]
        self.bot = [np.zeros(shape, np.float32) for _ in range(n)]
        self.comp = [np.zeros(shape, np.int16) for _ in range(n)]
        self.names = [[] for _ in range(n)]

    def add(self, bot, top, comp, mask, name='', win=None):
        """win: (row slice, col slice) when bot/top/mask cover only that window of the grid (a small part: fast)."""
        bot = np.broadcast_to(np.asarray(bot, np.float32), mask.shape)
        top = np.broadcast_to(np.asarray(top, np.float32), mask.shape)
        left = mask & (top > bot)
        W_ = win if win is not None else (slice(None), slice(None))
        for i in range(len(self.top)):
            if not left.any():
                break
            T_, B_, C_ = self.top[i][W_], self.bot[i][W_], self.comp[i][W_]
            have = T_ >= 0
            ov = left & have & (bot <= T_ + 1.0) & (top >= B_ - 1.0)
            if ov.any():
                # merged: the comp of whichever reaches higher (the one seen from above)
                hi = top > T_
                C_[...] = np.where(ov & hi, comp, C_).astype(np.int16)
                B_[...] = np.where(ov, np.minimum(bot, B_), B_)
                T_[...] = np.where(ov, np.maximum(top, T_), T_)
                left &= ~ov
            free = left & ~have
            if free.any():
                T_[...] = np.where(free, top, T_); B_[...] = np.where(free, bot, B_)
                C_[...] = np.where(free, comp, C_).astype(np.int16)
                self.names[i].append(name)
                left &= ~free

    def slabs(self):
        return [hd.Slab(np.where(t >= 0, t, -1.0), np.maximum(b, 0.0), c, '+'.join(nm) or f'acc{i}')
                for i, (t, b, c, nm) in enumerate(zip(self.top, self.bot, self.comp, self.names)) if (t >= 0).any()]


def build_params(p, g):
    """the model part way through TS's build-up (GTRADRMK): a copy of the parameters and the parts there so far.
    The deck is built low on the tower's base with its machinery and jacked up as the tower grows under it (lift);
    the antennas grow on it; the dish goes up last, its struts first, then its skin, round from one side."""
    import copy
    q = copy.deepcopy(p)
    parts = ['plinth']
    # the construction slab: TS's MK 00-01 (the plinth's outline growing out from the middle)
    q['plinth']['grow'] = float(np.clip(g['slab'], 0, 1))
    if g['swblock'] > 0:
        parts.append('swblock')
        sb = q['swblock']
        f = float(np.clip(g['swblock'], 0, 1))
        top = sb['z']
        sb['z'] = p['plinth']['h'] + (top - p['plinth']['h']) * max(f, 0.12)
        sb['cham'] = min(sb['cham'], max(sb['z'] - p['plinth']['h'] - 1, 0.5))
        if f < 0.95:
            sb['gtop']['z'] = -1.0                     # the green top goes on when the block is up
        else:
            sb['gtop']['z'] = sb['z'] + (p['swblock']['gtop']['z'] - top)
    if g['rotunda'] > 0:
        parts.append('rotunda')
        ro = q['rotunda']; f = float(g['rotunda'])
        ped0 = p['rotunda']['ped']
        zf = np.clip(f / 0.45, 0, 1)
        ro['ped'] = tuple((h_, p['plinth']['h'] + (z_ - p['plinth']['h']) * max(zf, 0.08)) for h_, z_ in ped0)
        pz0 = ro['ped'][-1][1]
        pf = np.clip((f - 0.45) / 0.3, 0, 1)
        ro['posts']['z'] = (pz0, pz0 + (p['rotunda']['posts']['z'][1] - p['rotunda']['posts']['z'][0]) * pf)
        df_ = np.clip((f - 0.75) / 0.25, 0, 1)
        ro['dome']['zc'] = ro['posts']['z'][1]
        ro['dome']['rz'] = p['rotunda']['dome']['rz'] * df_
        ro['dome']['r'] = p['rotunda']['dome']['r'] * (df_ > 0)
        ro['posts']['n'] = p['rotunda']['posts']['n'] if pf > 0 else 0
    # the deck and all on it ride up as the tower grows (lift 0: the tray on the tower's low base)
    lift = float(np.clip(g['lift'], 0, 1))
    dz = -(1.0 - lift) * (p['deck']['z'][0] - 14.0)
    if g['tower'] > 0:
        parts.append('tower')
        tw = q['tower']
        base_top = 14.0 * min(1.0, g['tower'] / 0.4)
        tw['z'] = base_top if g['upper'] <= 0 else p['deck']['z'][0] + dz
        k = tw['z'] / p['tower']['z']
        tw['box']['z'] = tuple(v * k for v in p['tower']['box']['z'])
        tw['ledge']['z'] = tuple(v + dz for v in p['tower']['ledge']['z'])
        tw['pipe']['z'] = p['tower']['pipe']['z'] * k
        tw['tank']['z'] = (5.0, max(6.0, p['tower']['tank']['z'][1] * k))
        tw['rbox']['z'] = tuple(v * k for v in p['tower']['rbox']['z'])
        tw['pipe']['r'] = p['tower']['pipe']['r'] * (k > 0.4)
    if g['upper'] > 0:
        parts += ['deck', 'upper']
        q['deck']['z'] = tuple(v + dz for v in p['deck']['z'])
        for k_ in ('upper', 'upperw'):
            q[k_]['z'] = p['deck']['z'][1] + dz + (p[k_]['z'] - p['deck']['z'][1]) * float(np.clip(g['upper'], 0, 1))
    if g['masts'] > 0:
        parts.append('masts')
        f = float(np.clip(g['masts'], 0, 1))
        q['masts']['pts'] = tuple((mx, my, zb + dz, (zb + dz + (zt - zb) * f) if zt > 0 else 0.0, zb + dz + (zt2 - zb) * f, rt)
                                  for (mx, my, zb, zt, zt2, rt) in p['masts']['pts'])
        # their brackets ride up with the deck
        q['mbrackets'] = tuple((bx_, by_, (bz_[0] + dz, bz_[1] + dz)) for (bx_, by_, bz_) in p.get('mbrackets', ()))
    if g['sbox'] > 0:
        parts.append('sbox')
        q['sbox']['z'] = p['plinth']['h'] + (p['sbox']['z'] - p['plinth']['h']) * float(np.clip(g['sbox'], 0.1, 1))
    if g['eastbase'] > 0:
        q['eastbase']['z'] = p['plinth']['h'] + (p['eastbase']['z'] - p['plinth']['h']) * float(np.clip(g['eastbase'], 0.1, 1))
    else:
        q['eastbase']['z'] = -1.0
    if g['ramp'] > 0 or g['eastbase'] > 0:
        parts.append('ramp')
        q['ramp']['z'] = p['plinth']['h'] + (p['ramp']['z'] - p['plinth']['h']) * float(np.clip(g['ramp'], 0, 1))
        q['ramp']['off'] = g['ramp'] <= 0
    if g['turret'] > 0:
        parts.append('turret')
        q['turret']['z'] = tuple(v + dz for v in p['turret']['z'])
    if g['dish'] > 0:
        parts.append('dish')
        q['dish']['zc'] = p['dish']['zc'] + dz
    return q, parts


def scene(X, Y, p=None, layout='ts', prog=None, dish_t=0.0, dish_az=None, merge=True, parts=None, dmg=0):
    """dish_t: 0..1 along TS's sweep (GTRADR_A 0..14); dish_az overrides the azimuth (degrees, local frame).
    parts: if given, only these parts (fit checks).  dmg 1: TS's damaged frame (GTRADR 01 + GTRADR_A 15-29), built in
    here part by part (radrdamage adds the soot and the colours)."""
    p = P if p is None else p
    g = dict(DONE); g.update(prog or {})
    if prog:
        p, bparts = build_params(p, g)
        parts = bparts if parts is None else [k for k in parts if k in bparts]
    x, y = to_local(X, Y, layout)
    H = np.zeros_like(X); C = np.zeros(X.shape, np.int16)
    acc = Acc(X.shape)
    extra = {}
    want = (lambda k: True) if parts is None else (lambda k: k in parts)

    def put(h, comp, where=None):
        nonlocal H, C
        if where is not None:
            h = np.where(where, h, 0.0)
        win = h > H + 1e-6
        H = np.where(win, h, H); C = np.where(win, comp, C)

    pl = p['plinth']
    if want('plinth'):
        gr = pl.get('grow', 1.0)
        if gr < 1.0:
            # the build-up's slab spreading out from the middle (TS MK 00), thin until it is whole
            put(np.where(in_poly(x / max(gr, 1e-3), y / max(gr, 1e-3), pl['poly']) & (gr > 0), 2.0, 0.0), PLINTH)
        else:
            put(np.where(in_poly(x, y, pl['poly']), pl['h'], 0.0), PLINTH)
    z0 = pl['h']
    # ---- the south-west block: tan, chamfered top edges, a green top with bevelled edges
    if want('swblock'):
        sb = p['swblock']
        dx = np.minimum(x - sb['x'][0], sb['x'][1] - x); dy = np.minimum(y - sb['y'][0], sb['y'][1] - y)
        dd = np.minimum(dx, dy)
        zt = sb['z'] - np.clip(sb['cham'] - dd, 0, None)
        put(np.where(dd >= 0, zt, 0.0), TAN)
        gt = sb['gtop']
        cx, cy = (sb['x'][0] + sb['x'][1]) / 2, (sb['y'][0] + sb['y'][1]) / 2
    if want('swblock') and gt['z'] > 0:
        dg = gt['half'] - np.maximum(np.abs(x - cx), np.abs(y - cy))
        zg = gt['z'] - np.clip(gt['bevel'] - dg, 0, None)
        if dmg:
            # TS 01: the green top smashed: lumpy, a hole torn in its south-east side, its corner broken off
            zg = zg + 3.5 * WN.noise(x, y, 9.0, 701) - 2.0
            e = dblob(x, y, cx + 10.0, cy + 14.0, 15.0, 11.0, 0.3, 702, feat=5.0)
            hole = (dg >= 0) & (e < 0)
            put(np.where((dg >= 0) & ~hole, zg, 0.0), GTOP)
            put(np.where(hole, gt['z'] - 16.0, 0.0), DEB_IN)
            extra['broken'] = np.maximum(extra.get('broken', 0 * X), ((dg >= 0) & (e >= 0) & (e < 0.25)) * 0.9)
            extra['soot'] = np.maximum(extra.get('soot', 0 * X), 0.75 * np.exp(-((x - cx - 10) ** 2 + (y - cy - 14) ** 2) / 26.0 ** 2))
        else:
            put(np.where(dg >= 0, zg, 0.0), GTOP)
    if want('sbox'):
        s = p['sbox']
        sbm = inbox(x, y, s['x'], s['y'])
        if dmg:
            # TS 01: its south face torn open (a dark hole, the green edges bent), its top dented
            e = dblob(x, y, -10.0, s['y'][1] - 4.0, 13.0, 16.0, 0.3, 711, feat=5.0)
            hole = sbm & (e < 0)
            put(np.where(sbm & ~hole, s['z'] + 2.5 * WN.noise(x, y, 7.0, 712) - 1.5, 0.0), SBOX)
            put(np.where(hole, 9.0, 0.0), DEB_IN)
            extra['broken'] = np.maximum(extra.get('broken', 0 * X), (sbm & (e >= 0) & (e < 0.3)) * 0.9)
            extra['soot'] = np.maximum(extra.get('soot', 0 * X), 0.7 * np.exp(-((x + 10) ** 2 + (y - s['y'][1]) ** 2) / 24.0 ** 2))
        else:
            put(np.where(sbm, s['z'], 0.0), SBOX)
    # ---- the rotunda: stepped pedestal, posts, dome
    if want('rotunda'):
        ro = p['rotunda']
        cx, cy = ro['c']
        for half, zz in ro['ped']:
            put(np.where(inbox(x, y, (cx - half, cx + half), (cy - half, cy + half)), zz, 0.0), ROT)
        po = ro['posts']
        for k in range(po['n']):
            a = 2 * np.pi * (k + 0.5) / po['n']
            px_, py_ = cx + po['r'] * np.cos(a), cy + po['r'] * np.sin(a)
            put(np.where(np.hypot(x - px_, y - py_) <= po['w'], po['z'][1], 0.0), POST)
        rr = np.hypot(x - cx, y - cy)
        put(np.where(rr <= po['r'] - 5.0, po['z'][1] - 1.0, 0.0), DARK)          # the dark core inside the posts
        dm = ro['dome']
        zd = dm['zc'] + dm['rz'] * np.sqrt(np.clip(1 - (rr / max(dm['r'], 1e-3)) ** 2, 0, None))
        dmask = (rr <= dm['r']) & (dm['r'] > 0) & (dm['rz'] > 0.5)
        if dmg:
            # TS 01: a hole knocked in the dome's crown, towards the front
            e = dblob(x, y, cx + 6.0, cy + 4.0, 11.0, 9.0, 0.35, 721, feat=4.0)
            notch = dmask & (e < 0)
            zd = np.where(notch, zd - 14.0 * np.clip(-e * 2.5, 0, 1) - 4.0, zd)
            acc.add(np.full(X.shape, dm['zc'] - 2.0), zd, DOME, dmask & ~notch, 'dome')
            acc.add(np.full(X.shape, dm['zc'] - 2.0), zd, DEB_IN, notch, 'dome')
            extra['soot'] = np.maximum(extra.get('soot', 0 * X), 0.55 * np.exp(-((x - cx - 6) ** 2 + (y - cy - 4) ** 2) / 20.0 ** 2))
        else:
            acc.add(np.full(X.shape, dm['zc'] - 2.0), zd, DOME, dmask, 'dome')
    # ---- the east ramp: level at its north end, a quarter ellipse down to the ground at its south end; the rail
    if want('ramp') and not p['ramp'].get('off', False):
        ra = p['ramp']
        m = inbox(x, y, ra['x'], ra['y'])
        u = np.clip((y - ra['ycurve']) / (ra['y'][1] - ra['ycurve']), 0, 1)
        zr = z0 + (ra['z'] - z0) * np.sqrt(np.clip(1 - u * u, 0, None))
        if dmg:
            # TS 01: two of its panels blown out (burnt, sunk), the rest dented
            seg = np.floor((y - ra['y'][0]) / 16.0)
            out_ = m & np.isin(seg, [2, 4]) & (x < ra['x'][1] - 8) & (WN.noise(x, y, 6.0, 731) > -0.5)
            zr = zr + np.where(m, 1.6 * WN.noise(x, y, 8.0, 732), 0.0)
            put(np.where(m & ~out_, zr, 0.0), RAMPG)
            put(np.where(out_, zr - 4.0, 0.0), DEB_BURNT)
            extra['soot'] = np.maximum(extra.get('soot', 0 * X), 0.5 * out_)
        else:
            put(np.where(m, zr, 0.0), RAMPG)
        rail = m & (x >= ra['x'][1] - ra['rail'])
        put(np.where(rail, zr + 2.5, 0.0), HOOP)
    if want('ramp') and p['eastbase']['z'] > 0:
        eb = p['eastbase']
        put(np.where(inbox(x, y, eb['x'], eb['y']), eb['z'], 0.0), TAN)
    if want('tower') and p.get('frame'):
        # v2: pillars, bracing, the lift
        tw = p['tower']; fr = p['frame']
        ztop = tw['z']
        z0 = 4.0
        pw = fr['pw']
        for (lx, ly) in fr['pillars']:
            put(np.where(inbox(x, y, (lx - pw, lx + pw), (ly - pw, ly + pw)), ztop, 0.0), LEG)
        if ztop > 30.0:
            pil = fr['pillars']
            # the four sides' bays (neighbouring pillars along x at each y, and along y at each x)
            bays = []
            for yy in sorted({q[1] for q in pil}):
                xs_ = sorted(q[0] for q in pil if q[1] == yy)
                bays += [((xa, yy), (xb, yy)) for xa, xb in zip(xs_[:-1], xs_[1:])]
            for xx in sorted({q[0] for q in pil}):
                ys_ = sorted(q[1] for q in pil if q[0] == xx)
                bays += [((xx, ya), (xx, yb)) for ya, yb in zip(ys_[:-1], ys_[1:])]
            zt = [z0 + (ztop - 6.0 - z0) * f for f in fr['tiers']]
            for (a, b) in bays:
                for k in range(len(zt) - 1):
                    for (za, zb) in ((zt[k], zt[k + 1]), (zt[k + 1], zt[k])):
                        add_rod(acc, x, y, (a[0], a[1], za), (b[0], b[1], zb), fr['brace_r'], LEG, 'brace')
                for zb_ in zt[1:]:
                    add_rod(acc, x, y, (a[0], a[1], zb_), (b[0], b[1], zb_), fr['brace_r'] + 0.6, LEG, 'beam')
        # the lift: an enclosed shaft from the plinth up to the command room (materials draw its glass slot, the car
        # seen through it, its door)
        lf = fr['lift']
        put(np.where(inbox(x, y, lf['x'], lf['y']), ztop, 0.0), LIFT)
    if want('tower') and not p.get('frame'):
        tw = p['tower']
        for (lx, ly) in tw['legs']:
            put(np.where(inbox(x, y, (lx - tw['leg'], lx + tw['leg']), (ly - tw['leg'], ly + tw['leg'])), tw['z'], 0.0), LEG)
        co = tw['core']
        put(np.where(inbox(x, y, co['x'], co['y']), tw['z'], 0.0), DARK)
        tk = tw['tank']
        rr_ = np.hypot(x - tk['c'][0], y - tk['c'][1])
        put(np.where(rr_ <= tk['r'], tk['z'][1] - 4.0 + 4.0 * np.sqrt(np.clip(1 - (rr_ / tk['r']) ** 2, 0, None)), 0.0), PIPE)
        rb = tw['rbox']
        acc.add(np.full(X.shape, rb['z'][0]), np.full(X.shape, rb['z'][1]), MACH, inbox(x, y, rb['x'], rb['y']), 'rbox')
        bx = tw['box']
        acc.add(np.full(X.shape, bx['z'][0]), np.full(X.shape, bx['z'][1]), MACH, inbox(x, y, bx['x'], bx['y']), 'tbox')
        le = tw['ledge']
        acc.add(np.full(X.shape, le['z'][0]), np.full(X.shape, le['z'][1]), DECKS, inbox(x, y, le['x'], le['y']), 'ledge')
        pp_ = tw['pipe']
        lo, hi, m = rod_interval(x, y, (pp_['x'], pp_['y'][0], pp_['z']), (pp_['x'], pp_['y'][1], pp_['z']), pp_['r'])
        acc.add(lo, hi, PIPE, m, 'tpipe')
    de = p['deck']
    if want('deck'):
        dtop = np.full(X.shape, de['z'][1])
        if dmg:
            # TS 01: the deck's top broken up into tilted plates, a corner knocked off its south-west
            cell = np.floor((x + 300.0) / 34.0) * 7.0 + np.floor((y + 300.0) / 30.0) * 13.0
            tilt = np.sin(cell * 12.9898) * 0.08 * (x - np.floor(x / 34.0) * 34.0 - 17.0) + np.cos(cell * 78.233) * 3.0
            dtop = dtop + np.clip(tilt, -4.0, 4.0) + 1.2 * WN.noise(x, y, 5.0, 741)
            corner = dblob(x, y, de['x'][0] + 6.0, de['y'][1] - 6.0, 22.0, 18.0, 0.35, 742, feat=6.0) < 0
            dtop = np.where(corner, dtop - 12.0, dtop)
        acc.add(np.full(X.shape, de['z'][0]), dtop, DECK, inbox(x, y, de['x'], de['y']), 'deck')
    if want('upper'):
        for k_ in ('upper', 'upperw'):
            up = p[k_]
            acc.add(np.full(X.shape, de['z'][1] - 1), np.full(X.shape, up['z']), MACH, inbox(x, y, up['x'], up['y']), k_)
    if want('turret'):
        tu = p['turret']
        acc.add(np.full(X.shape, tu['z'][0]), np.full(X.shape, tu['z'][1]), TURRET,
                np.hypot(x - tu['c'][0], y - tu['c'][1]) <= tu['r'], 'turret')
    if want('masts'):
        ms = p['masts']
        for (bx_, by_, bz_) in p.get('mbrackets', ()):
            acc.add(np.full(X.shape, bz_[0]), np.full(X.shape, bz_[1]), MACH, inbox(x, y, bx_, by_), 'mbracket')
        for i, (mx, my, zb, zt, ztop, rt) in enumerate(ms['pts']):
            if dmg:
                # TS 01: the two west masts snapped and leaning far over to the west, the tall one leaning a little,
                # two stubs; (lean degrees, direction degrees from east towards south, length kept)
                lean, dirn, keep = (MAST_DMG_RA if layout == 'ra' else MAST_DMG)[i]
                Lb = (zt - zb) if zt > 0 else 0.0
                Lt = (ztop - zb) * keep
                d3 = np.array([np.sin(np.radians(lean)) * np.cos(np.radians(dirn)),
                               np.sin(np.radians(lean)) * np.sin(np.radians(dirn)), np.cos(np.radians(lean))])
                p0 = np.array([mx, my, zb])
                if Lb > 0:
                    lo, hi, mm = rod_interval(x, y, p0, p0 + d3 * min(Lb, Lt), rt)
                    acc.add(lo, hi, MAST, mm, 'mastb')
                lo, hi, mm = rod_interval(x, y, p0, p0 + d3 * Lt, ms['r'])
                acc.add(lo, hi, MAST, mm, 'mast')
                continue
            rr = np.hypot(x - mx, y - my)
            if zt > 0:
                acc.add(np.full(X.shape, zb), np.full(X.shape, zt), MAST, rr <= rt, 'mastb')
            acc.add(np.full(X.shape, zb), np.full(X.shape, ztop), MAST, rr <= ms['r'], 'mast')
    # ---- the dish
    if want('dish'):
        az = dish_az if dish_az is not None else p['dish']['az'][0] + (p['dish']['az'][1] - p['dish']['az'][0]) * dish_t
        df = dish_frame(p, az, layout)
        R = p['dish']['R']
        dprog = float(g['dish'])
        for k, (lo, hi, m) in enumerate(dish_intervals(x, y, df, R, p['dish']['t'])):
            if dmg:
                gone = dish_broken(x, y, 0.5 * (lo + hi), df, R)
                m = m & ~gone
            if dprog < 1.0:
                # the build-up: its skin goes on round from one side (TS MK 13-15), after the struts
                ph = dish_phi_field(x, y, 0.5 * (lo + hi), df)
                m = m & (((ph + 200.0) % 360.0) < 360.0 * np.clip((dprog - 0.3) / 0.65, 0, 1))
            acc.add(lo, hi, DISH, m, f'dish{k}')
        for (a0, a1, r, comp) in dish_rods(p, df):
            if dprog < 1.0 and comp in (ROD, FEED) and dprog < 0.95:
                continue
            if dprog < 0.15 and comp == STRUT:
                continue
            if dmg:
                if comp == ROD:
                    continue                               # TS 01: the feed rod is gone
                if comp == STRUT:
                    # struts whose rim end is in the broken part are snapped near the feed
                    ph = dish_phi(a0, df)
                    if BROKEN_PHI[0] <= ph <= BROKEN_PHI[1]:
                        a0 = a1 + (a0 - a1) * 0.3
            lo, hi, m = rod_interval(x, y, a0, a1, r)
            acc.add(lo, hi, comp, m, 'rod')
        hub = np.hypot(x - df['F'][0], y - df['F'][1])
        extra['dish_az'] = np.full(X.shape, az, np.float32)
    extra['paint'] = np.full(X.shape, g['paint'], np.float32)
    return hd.Scene(H, C, acc.slabs(), extra)


FLAT = {PLINTH: (150, 120, 80), TAN: (190, 160, 110), GREEN: (0, 200, 0), DARK: (40, 40, 40), GREY: (120, 120, 125),
        ROT: (170, 140, 90), DOME: (200, 170, 100), POST: (110, 110, 115), RAMP: (150, 130, 90), HOOP: (200, 200, 200),
        DECK: (180, 150, 100), DECKS: (90, 70, 50), LEG: (100, 100, 110), MACH: (140, 110, 80), TURRET: (90, 90, 95),
        MAST: (120, 120, 150), MASTTIP: (180, 120, 60), DISH: (210, 200, 170), STRUT: (50, 45, 40), FEED: (60, 60, 60),
        ROD: (40, 40, 40), ARM: (80, 80, 85), GTOP: (0, 220, 0), SBOX: (0, 200, 0), RAMPG: (0, 190, 0), PIPE: (150, 150, 150),
        SLAB: (150, 150, 150), RED: (200, 40, 20), LIFT: (200, 196, 170)}
