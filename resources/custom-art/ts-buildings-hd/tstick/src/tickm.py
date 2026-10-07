"""The dug-in Tick Tank (TS [GATICK]) from the units chat's model (src/ttnk3hd.py: Luke's redesigned tank, hull and
turret, built with src/hdv.py), dug in the way TS's GTTICKMK does it (Luke: "the tank burying into the ground and almost
going vertical"): the nose digs in and the tank pitches nose-down to 81 degrees, sinking until only its rear end stands
out of the ground; the turret runs back along its rails (the units chat's design) and ends on top of the upright rear
end, level on a short post.  The pose is fitted to TS's frames (tickfit.py): the dug-in pose to GTTICK 0, the build-up's
timing to GTTICKMK.

  base     the hull dug in, the soil heaped round it where it goes into the ground, the turret's post (part of the base);
           no turret
  turret   the turret alone, upright on its post, at an angle (32 facings: frames of its own)
  build-up t = 0 (the tank as the units hand-off draws it: hull + turret at facing 24) .. 1 (dug in)

Coordinates: the unit frame (voxels: x forward, y left, z up; the ground at z = 0; the origin the unit's position, the
cell's centre), the hull written in TTNK.VXL's index space through hdv.VoxelFrame.  The tank faces east (the mod's facing
24, TS's way round: TS's GTTICKMK starts with the tank facing TS's east)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(HERE, 'src'), HERE):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
from scipy import ndimage
import fakeunit as F
import ttnk3hd as T, hdv, rc
from wnoise import noise

FACING = int(os.environ.get('TICK_FACING', 16))   # the facing it digs in at: 16 south, nose toward the camera (Luke 7 Oct: E)
VOX_PX_BLD = 6.25 * 128.0 / 192.0   # the buildings' scale: 128 px a cell (the units' canvas is 192 px a cell)
POST_R = 2.55                        # the turret's post (index voxels)
RING_R = 3.4 * T.RING_SCALE
FINAL = (81.0, 6.5, 1.0)             # dug in: pitch (degrees nose-down about the unit's position on the ground), sink
                                     # and forward slide (voxels); fitted to GTTICK 0 (tickfit.py final: IoU 0.85)
BUILD_N = 25
RAIL_END = 2.6                       # where the turret's run back along the rails ends (index x)
TOP_ANCHOR = (0.95, T.YC, 6.4 if T.HIGH_BACK else 4.9)       # the middle of the rear plate (index): the top of the upright hull
SCHED = None                         # the pose per build-up frame: _schedule() at the end


def unit():
    return F.FakeUnit()


def ease(a):
    a = float(np.clip(a, 0.0, 1.0))
    return a * a * (3 - 2 * a)


def rot(th):
    a = np.radians(th)
    return np.array([[np.cos(a), 0, np.sin(a)], [0, 1.0, 0], [-np.sin(a), 0, np.cos(a)]])


def pose_params(t):
    """(pitch, sink, slide) at t (0..1) from the per-frame schedule (linear between frames)."""
    x = float(np.clip(t, 0, 1)) * (BUILD_N - 1)
    i = min(int(np.floor(x)), BUILD_N - 2)
    u = x - i
    a, b = np.asarray(SCHED[i], float), np.asarray(SCHED[i + 1], float)
    return tuple(a * (1 - u) + b * u)


def run_phase(t):
    """the turret's run back along the rails: done before the tank gets steep."""
    return ease(t / 0.36)


def swing_phase(th):
    """the turret going over the rear edge onto the rear plate as the tank rears up (by the pitch)."""
    return ease((th - 30.0) / 42.0)


def burial(t):
    """how far the soil has risen (0..1)."""
    return ease((t - 0.12) / 0.8)


class Pose:
    """the tank's pose: turned nose-down by th about the unit's position on the ground, moved f forward, s down."""

    def __init__(self, V, th, s, f):
        self.th, self.s, self.f = th, s, f
        self.R = rot(th)
        self.T = np.array([f, 0.0, -s])
        self.V = V

    def w(self, q):
        """an index-space point (x, y, z) -> the unit frame, posed."""
        return self.R @ self.V.p(*q) + self.T

    def move(self, it):
        return hdv.moved_item(it, self.R, self.T)


def ground_cut(it):
    """keep the part above the ground (tickrender leaves the cut's edge sharp)."""
    hdv.cut(it, np.array([0, 0, -1.0]), np.zeros(3))
    return it


# ------------------------------------------------------------------------------------------------ the turret's seat
def anchor(t, th):
    """where the turret sits on the hull (index space): back along the rails from the deck to the rails' end, then over
    the rear edge onto the rear plate as the tank rears up."""
    x = T.PIVOT_X + (RAIL_END - T.PIVOT_X) * run_phase(t)
    a = np.array([x, T.YC, T.DECK_Z + T.rail_lift(x)])
    b = np.array(TOP_ANCHOR, float)
    k = swing_phase(th)
    return a * (1 - k) + b * k


def top_z(parts, x, y, r):
    """the highest point of parts (unit frame) inside the disc of radius r round (x, y): rays cast straight down."""
    pts = [(x, y)]
    for rho in (0.35, 0.7, 1.0):
        for a in np.linspace(0, 2 * np.pi, 20, endpoint=False):
            pts.append((x + rho * r * np.cos(a), y + rho * r * np.sin(a)))
    P = np.array([(px, py, 80.0) for px, py in pts])
    t, who, _ = rc.cast(parts, P, np.array([0, 0, -1.0]))
    t = t[np.isfinite(t)]
    return float(80.0 - t.min()) if t.size else 0.0


def seat(V, pose, t, hull_parts):
    """the turret's pivot (unit frame), upright, its ring clear of the hull under it.  At t = 0 exactly the units
    hand-off's: the deck at the unit's position."""
    if t <= 0:
        return V.p(T.PIVOT_X, T.YC, T.DECK_Z)
    q = pose.w(anchor(t, pose.th))
    z = top_z(hull_parts, q[0], q[1], 3.4 * T.RING_SCALE * V.sc[0])
    return np.array([q[0], q[1], z + 0.04])


def turret_items_at(V, s, angle):
    """the turret's parts, upright, its pivot at s (unit frame), turned by angle (relative to the hull)."""
    items = T.turret_items(V, at_x=T.PIVOT_X, at_z=T.DECK_Z, angle=angle, lift=0.0)
    d = s - V.p(T.PIVOT_X, T.YC, T.DECK_Z)
    return [hdv.moved_item(it, np.eye(3), d) for it in items]


def post_items(V, s, t):
    """the turret's post under its ring (part of the base), down into the hull."""
    if t <= 0:
        return []
    sx = V.sc[0]
    it = hdv.cyl('gunmetal', s - np.array([0, 0, 4.5]), s - np.array([0, 0, 0.02]), POST_R * sx, 'turret_post', rnd=0.25)
    collar = hdv.cyl('black', s - np.array([0, 0, 0.62]), s - np.array([0, 0, 0.02]), (POST_R + 0.3) * sx,
                     'turret_post_collar', rnd=0.15)
    return [it, collar]


def turret_angle(f):
    """the turret's angle relative to the hull for the mod's facing f (0 N, 8 W, 16 S, 24 E, anticlockwise)."""
    return np.radians((f - FACING) * 11.25)


# ------------------------------------------------------------------------------------------------ the soil
RNG_SEED = 7
GSTEP = 0.25
GX, GY = (-16.0, 22.0), (-18.0, 18.0)
GRID = 1.1
TAU = 0.05


def inside(parts, P):
    """points P (n, 3) inside any of the parts (unit frame)."""
    m = np.zeros(len(P), bool)
    for p in parts:
        if p.sphere is not None:
            c0, R0 = p.sphere
            near = ((P - np.asarray(c0)) ** 2).sum(1) <= R0 * R0
            if not near.any():
                continue
            idx = np.nonzero(near)[0]
        else:
            idx = np.arange(len(P))
        Q = P[idx]
        ins = np.ones(len(Q), bool)
        for c in p.cons:
            if c.kind == 'plane':
                ins &= Q @ c.n <= c.d
            elif c.kind == 'ellip':
                q = (Q - c.c) @ (c.R / c.r[None, :])
                ins &= (q * q).sum(1) <= 1
            elif c.kind == 'cyl':
                q = Q - c.c; qa = q @ c.a
                ins &= ((q - qa[:, None] * c.a) ** 2).sum(1) <= c.r ** 2
            if not ins.any():
                break
        m[idx[ins]] = True
    return m


class Ground:
    """where the hull goes into the ground (its cross-section 1 voxel under the ground) and the signed distance from it
    (unit frame voxels, + outside): the soil is heaped round it."""

    def __init__(self, parts, depth=1.0):
        xs = np.arange(GX[0], GX[1] + 1e-6, GSTEP); ys = np.arange(GY[0], GY[1] + 1e-6, GSTEP)
        X, Y = np.meshgrid(xs, ys, indexing='ij')
        P = np.stack([X.ravel(), Y.ravel(), np.full(X.size, -depth)], 1)
        m = inside(parts, P).reshape(X.shape) if parts else np.zeros(X.shape, bool)
        self.m = m
        self.any = bool(m.any())
        if self.any:
            d = ndimage.distance_transform_edt(~m) * GSTEP - ndimage.distance_transform_edt(m) * GSTEP
            ii, jj = np.nonzero(m)
            self.c = np.array([xs[ii].mean(), ys[jj].mean()])
            self.east = float(xs[ii].max())
        else:
            d = np.full(X.shape, 99.0)
            self.c = np.zeros(2); self.east = 0.0
        self.d = d

    def dist(self, x, y):
        x = np.asarray(x, float); y = np.asarray(y, float)
        fi = (x - GX[0]) / GSTEP; fj = (y - GY[0]) / GSTEP
        return ndimage.map_coordinates(self.d, [np.ravel(fi), np.ravel(fj)], order=1, mode='nearest').reshape(np.shape(x))


def soil_h(G, x, y, g):
    """the soil's height (voxels) at g (0 none .. 1 dug in): a ridge round the hull, higher on the east (the nose went
    in there first), lumpy, loose spoil spread thin at its foot."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    if not G.any or g <= 0:
        return np.zeros(np.shape(x))
    d = G.dist(x, y)
    east = np.clip((x - G.c[0]) / 7.0, -1, 1)
    H = 2.0 + 0.7 * east
    w = 2.6 + 0.8 * np.clip(east, 0, 1)
    dp = 0.7
    u = np.clip((d - dp) / w, 0, 1)
    outer = (1 - u * u * (3 - 2 * u)) ** 1.3
    prof = np.where(d < dp, 1.0, outer)
    n1 = noise(x, y, 2.3, 101); n2 = noise(x + 7.0, y - 3.0, 0.95, 103)
    h = H * prof * (1 + 0.28 * n1) + 0.25 * n2 * np.minimum(H * prof, 1.0)
    spoil = 0.22 * np.exp(-(np.maximum(d - dp, 0) / 3.4) ** 2) * np.clip(0.2 + 1.1 * noise(x - 2.0, y + 5.0, 1.3, 105), 0, 1.6)
    h = np.maximum(h, spoil)
    # it rises from the hull outward as the tank goes in
    lag = 0.35 * np.clip(d / 6.0, 0, 1)
    gg = np.clip((g - lag) / (1 - lag), 0, 1); gg = gg * gg * (3 - 2 * gg)
    return h * gg


def cell_poly(xs, ys, hs):
    """marching squares on one cell: the part of it where h > TAU, as (x, y, top) points (the tops on the boundary
    come down to the ground)."""
    (x0, x1), (y0, y1) = xs, ys
    c = [(x0, y0, hs[0]), (x1, y0, hs[1]), (x1, y1, hs[3]), (x0, y1, hs[2])]
    out = []
    for k in range(4):
        xa, ya, ha = c[k]; xb, yb, hb = c[(k + 1) % 4]
        if ha > TAU:
            out.append((xa, ya, ha))
        if (ha > TAU) != (hb > TAU):
            f = (TAU - ha) / (hb - ha)
            out.append((xa + f * (xb - xa), ya + f * (yb - ya), 0.015))
    return out


def soil_region(G):
    ii, jj = np.nonzero(G.d < 7.5)
    xs_all = np.arange(GX[0], GX[1] + 1e-6, GSTEP); ys_all = np.arange(GY[0], GY[1] + 1e-6, GSTEP)
    return xs_all[ii].min(), xs_all[ii].max(), ys_all[jj].min(), ys_all[jj].max()


def soil_items(V, G, g):
    """the soil as a heightfield of thin columns (convex: each the hull of its outline at the ground and on the surface;
    marching squares at its edge), shaded with the heightfield's own normals (tickrender.frame); clods round it."""
    if g <= 0 or not G.any:
        return []
    x0, x1, y0, y1 = soil_region(G)
    xs = np.arange(x0, x1 + GRID, GRID); ys = np.arange(y0, y1 + GRID, GRID)
    X, Y = np.meshgrid(xs, ys, indexing='ij')
    Hh = soil_h(G, X, Y, g)
    out = []
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            hs = (Hh[i, j], Hh[i + 1, j], Hh[i, j + 1], Hh[i + 1, j + 1])
            if max(hs) <= TAU:
                continue
            poly = cell_poly((xs[i], xs[i + 1]), (ys[j], ys[j + 1]), hs)
            if len(poly) < 3:
                continue
            pts = [(px, py, -0.3) for px, py, _ in poly] + [(px, py, max(pz, 0.015)) for px, py, pz in poly]
            try:
                out.append(ground_cut(hdv.hull('soil', pts, 'soil_col', rnd=0.0)))
            except Exception:
                pass
    # clods round it, landing as it goes in
    rng = np.random.default_rng(RNG_SEED + 1)
    sx = V.sc[0]
    k = 0
    for _ in range(400):
        if k >= 12:
            break
        x, y = rng.uniform(G.c[0] - 13, G.c[0] + 15), rng.uniform(-17, 17)
        d = float(G.dist(x, y))
        r0 = rng.uniform(0.4, 0.8); rot_ = rng.uniform(0, np.pi); lag = 0.4 + 0.55 * rng.random()
        if not (2.6 < d < 5.0):
            continue
        k += 1
        if g < lag:
            continue
        ca, sa = np.cos(rot_), np.sin(rot_)
        Rz = np.array([[ca, -sa, 0], [sa, ca, 0], [0, 0, 1.0]])
        z0 = float(soil_h(G, x, y, 1.0)) * 0.85
        e = hdv.ellip('soil', np.array([x, y, r0 * 0.3 + z0]), np.array([r0 * 1.2, r0, r0 * 0.8]) * sx, R=Rz,
                      name='soil_clod%d' % k, rnd=0.6)
        out.append(ground_cut(e))
    return out


def flying_clods(V, G, t):
    """soil thrown up by the drum while the nose burrows (build-up only): each clod flies for a few frames, out from
    where the hull goes into the ground."""
    if not G.any:
        return []
    rng = np.random.default_rng(RNG_SEED + 2)
    out = []
    sx = V.sc[0]
    for k in range(16):
        t0 = 0.16 + 0.56 * k / 15 + 0.02 * rng.normal()
        dur = 0.11 + 0.02 * rng.random()
        y0 = rng.uniform(-7.0, 7.0)
        out_x = rng.uniform(1.2, 3.2); vy = y0 * rng.uniform(0.1, 0.4) + rng.normal() * 1.4; hz = rng.uniform(2.2, 4.6)
        r0 = rng.uniform(0.45, 0.8)
        u = (t - t0) / dur
        if not (0.0 < u < 1.0):
            continue
        x0 = G.east + 0.5
        p = np.array([x0 + out_x * u, y0 + vy * u, 0.6 + 4 * hz * u * (1 - u)])
        out.append(hdv.ellip('soil', p, np.array([r0 * 1.2, r0, r0 * 0.85]) * sx, name='clod_fly%d' % k, rnd=0.5))
    return out


# ------------------------------------------------------------------------------------------------ the model
def spin_drum(items, V, phi):
    c = V.p(29.6, T.YC, 2.9)
    Ry = rot(np.degrees(phi))
    return [hdv.moved_item(it, Ry, c - Ry @ c) if it.name == 'drum' else it for it in items]


def state(cfg, t, damage=0):
    """the posed hull (items), its pose, the ground cross-section, the turret's seat: what the model and the turret
    layer share at t."""
    u = unit()
    V = hdv.VoxelFrame(cfg, u, 0)
    th, s, f = pose_params(t)
    pose = Pose(V, th, s, f)
    H = T.build_hull(cfg, u)
    items = H.items
    if damage:
        import tickdamage as D
        items = D.hull_items(V, items)
    items = spin_drum(items, V, 5.0 * np.pi * t)
    if t > 0:
        posed = [pose.move(it) for it in items]
        G = Ground([it.part for it in posed])
        items = [ground_cut(it) for it in posed]
    else:
        G = Ground([])
    sp = seat(V, pose, t, [it.part for it in items if not it.name.startswith(('claw', 'drum'))])
    return V, pose, items, G, sp


def model(cfg, t=1.0, turret=None, base=True, damage=0, fly=False, berm=True):
    """t: 0 (the tank as it drives) .. 1 (dug in).  turret: None (no turret) or its angle relative to the hull
    (radians, anticlockwise seen from above, 0 = forward).  base: the hull, its post and the soil (False: the turret
    alone).  damage: 0 healthy, 1 damaged (tickdamage.py).  fly: the clods in the air (build-up frames)."""
    V, pose, items, G, sp = state(cfg, t, damage)
    mats = T.mats()
    mats.update(MATS)
    M = hdv.Model(mats)
    g = burial(t)
    if base:
        M.add(items)
        M.add([ground_cut(it) for it in post_items(V, sp, t)])
        if berm and g > 0:
            M.add(soil_items(V, G, g))
        if fly:
            M.add(flying_clods(V, G, t))
        if damage:
            import tickdamage as D
            M.add(D.debris_items(V, G))
    if turret is not None:
        M.add(turret_items_at(V, sp, turret))
    M.pose, M.V, M.t, M.seat, M.G = pose, V, t, sp, G
    M.berm_h = (lambda x, y, G=G, g=g: soil_h(G, x, y, g)) if (base and berm and g > 0 and G.any) else None
    return M


def muzzle(cfg, t, angle, sp=None):
    """the gun's tip (unit frame) for the turret at angle, at t."""
    V = hdv.VoxelFrame(cfg, unit(), 0)
    if sp is None:
        sp = state(cfg, t)[4]
    mu, mv, mw = T.turret_point(T.MUZZLE_LOCAL)
    ca, sa = np.cos(angle), np.sin(angle)
    q = V.p(T.PIVOT_X + mu * ca - mv * sa, T.YC + mu * sa + mv * ca, T.DECK_Z + mw)
    return q + (sp - V.p(T.PIVOT_X, T.YC, T.DECK_Z))


# ------------------------------------------------------------------------------------------------ materials
def soil(r, m, it):
    """churned loam: dark brown, lighter dry crumbs, darker damp clumps, a few grey stones (world-fixed)."""
    X, Y, Z = r.x[m], r.y[m], r.z[m]
    n1 = noise(X + 0.5 * Z, Y - 0.4 * Z, 2.2, 61) + 0.5 * noise(X - 0.3 * Z, Y + 0.6 * Z, 0.9, 63)
    n2 = noise(X + 1.7, Y - 0.9 + 0.5 * Z, 0.55, 67)
    n3 = noise(X - 2.1 + 0.4 * Z, Y + 1.3, 0.35, 71)
    base = np.array([80, 66, 50], np.float32)
    dark = np.array([54, 44, 34], np.float32)
    dry = np.array([118, 102, 78], np.float32)
    stone = np.array([116, 114, 108], np.float32)
    t1 = np.clip((n1 + 0.2) / 0.9, 0, 1)[:, None]
    c = dark * (1 - t1) + base * t1
    t2 = np.clip((n2 - 0.7) / 0.5, 0, 1)[:, None] * 0.8
    c = c * (1 - t2) + dry * t2
    t3 = np.clip((n3 - 1.45) / 0.25, 0, 1)[:, None]
    return c * (1 - t3) + stone * t3


MATS = {
    'soil': dict(col=(80, 66, 50), spec=0.05, power=8, pattern=soil),
    'scrap': dict(col=(118, 118, 122), spec=0.35, power=30),
    'scorched': dict(col=(46, 44, 42), spec=0.15, power=16),
}


# ------------------------------------------------------------------------------------------------ the schedule
def _schedule():
    """the pose per build-up frame: GTTICKMK's pitch, fitted frame by frame (tickfit.py mk -> mkfit.txt), the frame-00
    mismatch with TS's voxel tank faded out over the build-up (frame 00 is the units' tank exactly), smoothed and made
    monotonic, ending exactly on FINAL; the sink and the slide follow the pitch."""
    p = os.path.join(HERE, 'mkfit.txt')
    rows = np.atleast_2d(np.loadtxt(p)) if os.path.exists(p) else None
    n = BUILD_N
    if rows is None or len(rows) < n:
        th = np.array([FINAL[0] * ease(i / (n - 1.0)) for i in range(n)])
    else:
        raw = rows[:n, 1].copy()
        raw = raw - raw[0] * (1 - np.arange(n) / (n - 1.0))
        raw[-1] = FINAL[0]
        sm = ndimage.gaussian_filter1d(raw, 1.0, mode='nearest')
        sm[0] = 0.0
        sm = np.maximum.accumulate(sm)
        sm = sm * FINAL[0] / max(sm[-1], 1e-6)
        sm[0], sm[-1] = 0.0, FINAL[0]
        th = sm
    k = th / FINAL[0]
    s = FINAL[1] * k ** 1.3
    f = FINAL[2] * k
    return [(float(a), float(b), float(c)) for a, b, c in zip(th, s, f)]


SCHED = _schedule()
