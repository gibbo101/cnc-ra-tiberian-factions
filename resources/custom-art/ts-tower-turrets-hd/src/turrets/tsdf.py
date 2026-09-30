"""
Signed-distance models and a ray-marcher for the component tower's turrets.

The tower and walls are heightfields; a turret has overhangs (barrels over nothing) and turns through 32
facings, so it is modelled as a union of simple solids (boxes, cylinders, convex blocks cut by planes),
turned about the tower's vertical axis and sphere-traced with the same orthographic cameras.

World (physical units, 1 cell = 128): x east, y south, z up; the turret turns about the vertical line
x = y = 0 (the tower's middle). Turret-local frame: f forward (where it points), r to its right, z up.
Facing angle th (radians) runs counter-clockwise on the map from north: forward = (-sin th, -cos th).
"""
import numpy as np

# ----------------------------------------------------------------------------- parts
# every part is a dict: kind, comp (material id), plus its shape; 'sub' parts cut the parts before them
# that share their group ('grp').


def box(c, h, rd=0.0, comp=1, **kw):
    """axis-aligned (local) box: centre c=(f, r, z), half sizes h, edges rounded by rd."""
    return dict(kind='box', c=np.array(c, float), h=np.array(h, float), rd=rd, comp=comp, **kw)


def cyl(axis, c, lo, hi, R, comp=1, **kw):
    """capped cylinder along a local axis ('f', 'r' or 'z'): c = its centre in the other two coordinates
    (in f, r, z order with the axis one dropped), running lo..hi along the axis, radius R."""
    return dict(kind='cyl', axis=axis, c=np.array(c, float), lo=lo, hi=hi, R=R, comp=comp, **kw)


def poly(planes, comp=1, **kw):
    """convex block: the intersection of half-spaces n . p <= d, planes = [(n, d), ...] (n need not be unit)."""
    ns = np.array([np.array(n, float) / np.linalg.norm(n) for n, d in planes])
    ds = np.array([d / np.linalg.norm(n) for n, d in planes])
    return dict(kind='poly', n=ns, d=ds, comp=comp, **kw)


def slab_box(c, h, bevel_top=0.0, bevel_side=0.0, comp=1, top_axes='fr', **kw):
    """a box (centre c, half sizes h) with its top edges chamfered by bevel_top and its vertical edges by
    bevel_side - the usual TS 'machined' block. top_axes: which top edges are chamfered ('f' front/back,
    'r' left/right; 'r' alone gives a ridge running fore and aft)."""
    cf, cr, cz = c; hf, hr, hz = h
    pl = [((1, 0, 0), cf + hf), ((-1, 0, 0), -(cf - hf)), ((0, 1, 0), cr + hr), ((0, -1, 0), -(cr - hr)),
          ((0, 0, 1), cz + hz), ((0, 0, -1), -(cz - hz))]
    if bevel_top > 0:
        edges = [e for e, ax in (((1, 0), 'f'), ((-1, 0), 'f'), ((0, 1), 'r'), ((0, -1), 'r')) if ax in top_axes]
        for sf, sr in edges:
            # plane through the top edge pulled in by bevel_top: sf*f + sr*r + z <= (edge) - bevel
            e = (cf * sf + hf * abs(sf)) + (cr * sr + hr * abs(sr)) if (sf or sr) else 0
            pl.append(((sf, sr, 1), e + cz + hz - bevel_top))
    if bevel_side > 0:
        for sf in (1, -1):
            for sr in (1, -1):
                pl.append(((sf, sr, 0), sf * cf + hf + sr * cr + hr - bevel_side))
    return poly(pl, comp=comp, **kw)


def sph(c, R, comp=1, **kw):
    return dict(kind='sph', c=np.array(c, float), R=R, comp=comp, **kw)


def sd_part(p, P):
    if p.get('pitch') is not None:                    # the part pitched up by a about the r axis through (f0, z0)
        a, f0, z0 = p['pitch']
        ca, sa = np.cos(a), np.sin(a)
        df, dz = P[..., 0] - f0, P[..., 2] - z0
        P = np.stack([f0 + df * ca + dz * sa, P[..., 1], z0 - df * sa + dz * ca], -1)
    f, r, z = P[..., 0], P[..., 1], P[..., 2]
    k = p['kind']
    if k == 'box':
        q = np.abs(P - p['c']) - (p['h'] - p['rd'])
        out = np.linalg.norm(np.maximum(q, 0), axis=-1) + np.minimum(q.max(axis=-1), 0)
        return out - p['rd']
    if k == 'cyl':
        ax = p['axis']
        if ax == 'f':
            a, u, v = f, r - p['c'][1], z - p['c'][2]
        elif ax == 'r':
            a, u, v = r, f - p['c'][0], z - p['c'][2]
        else:
            a, u, v = z, f - p['c'][0], r - p['c'][1]
        d2 = np.hypot(u, v) - p['R']
        da = np.maximum(p['lo'] - a, a - p['hi'])
        return np.hypot(np.maximum(d2, 0), np.maximum(da, 0)) + np.minimum(np.maximum(d2, da), 0)
    if k == 'sph':
        return np.linalg.norm(P - p['c'], axis=-1) - p['R']
    if k == 'poly':
        return (P[..., None, :] * p['n']).sum(-1).__sub__(p['d']).max(axis=-1)
    raise ValueError(k)


def scene_sdf(parts, P, want_comp=False):
    """union of the parts; 'sub' parts are cut out of everything before them (in list order)."""
    d = np.full(P.shape[:-1], 1e9)
    comp = np.zeros(P.shape[:-1], np.int16)
    for p in parts:
        dp = sd_part(p, P)
        if p.get('sub'):
            cut = -dp > d
            d = np.maximum(d, -dp)
            if want_comp and p.get('comp_in') is not None:        # the inside of the cut gets its own colour
                comp = np.where(cut & (np.abs(d) < 1.5), p['comp_in'], comp)
            continue
        win = dp < d
        d = np.where(win, dp, d)
        if want_comp:
            comp = np.where(win, p['comp'], comp)
    return (d, comp) if want_comp else d


def to_local(x, y, z, th, z0=0.0):
    """world -> turret-local (f, r, z - z0) for facing th."""
    s, c = np.sin(th), np.cos(th)
    return np.stack([-x * s - y * c, x * c - y * s, z - z0], axis=-1)


def local_dirs(th):
    """world vectors of the local f, r axes."""
    s, c = np.sin(th), np.cos(th)
    return np.array([-s, -c, 0.0]), np.array([c, -s, 0.0])


# ----------------------------------------------------------------------------- ray-marching
def march(parts, th, X, Y, cam, z0, zlo, zhi, steps=110, eps=0.02):
    """orthographic rays through screen points X, Y (arrays). cam = (elevation, px per unit, ax, ay, zref):
    X = ax + s x ;  Y = ay + s (y sin e - (z - zref) cos e), i.e. (ax, ay) is where the axis point at world
    height zref lands. The turret's local origin is on the axis at world height z0. Rays start at world
    height zhi and stop below zlo. Returns hit mask and world hit points."""
    e, s, ax, ay, zref = cam
    se, ce = np.sin(e), np.cos(e)
    x = (X - ax) / s
    ys = ((Y - ay) / s + (zhi - zref) * ce) / se          # the ray's y at z = zhi
    vy, vz = -ce, -se                                    # march direction (north and down)
    tmax = (zhi - zlo) / se
    t = np.zeros_like(x, dtype=float)
    hit = np.zeros(x.shape, bool)
    alive = np.ones(x.shape, bool)
    for _ in range(steps):
        idx = np.flatnonzero(alive)
        if idx.size == 0:
            break
        ti = t.flat[idx]
        d = scene_sdf(parts, to_local(x.flat[idx], ys.flat[idx] + vy * ti, zhi + vz * ti, th, z0))
        h = d < eps
        tn = ti + np.maximum(d, 0.25 * eps)
        t.flat[idx] = np.where(h, ti, tn)
        hit.flat[idx[h]] = True
        alive.flat[idx[h | (tn > tmax)]] = False
    W = np.stack([x, ys + vy * t, zhi + vz * t], -1)
    return hit, W


def normals(parts, th, W, z0, h=0.15):
    """world-space normals by central differences of the SDF."""
    n = np.zeros_like(W)
    for i in range(3):
        o = np.zeros(3); o[i] = h
        A, B = W + o, W - o
        n[..., i] = (scene_sdf(parts, to_local(A[..., 0], A[..., 1], A[..., 2], th, z0))
                     - scene_sdf(parts, to_local(B[..., 0], B[..., 1], B[..., 2], th, z0)))
    return n / np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-9)


def occluded(parts, th, W, z0, L, tmax=200.0, steps=80, eps=0.05, start=0.6):
    """is the ray from world points W towards L (unit) blocked by the turret? (hard shadow)"""
    flat = W.reshape(-1, 3)
    t = np.full(flat.shape[0], start)
    blocked = np.zeros(flat.shape[0], bool)
    alive = np.ones(flat.shape[0], bool)
    for _ in range(steps):
        idx = np.flatnonzero(alive)
        if idx.size == 0:
            break
        P = flat[idx] + L * t[idx][:, None]
        d = scene_sdf(parts, to_local(P[:, 0], P[:, 1], P[:, 2], th, z0))
        b = d < eps
        blocked[idx[b]] = True
        t[idx] += np.maximum(d, 0.1)
        alive[idx[b | (t[idx] > tmax)]] = False
    return blocked.reshape(W.shape[:-1])
