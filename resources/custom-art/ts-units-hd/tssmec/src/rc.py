"""
rc.py - a ray caster for models built from convex parts, for the TS walker units (the Titan first).

hd.py samples a model as a ground heightfield plus slabs, which suits buildings and voxel trucks; a walker's
legs are tilted boxes in every direction, so here each part is a convex solid (an intersection of planes,
ellipsoids and cylinders) and every pixel's ray is cut against it exactly.  The normal at the hit is the
normal of the face (or curved surface) the ray enters through, so tilted plates shade as the plates they are.

World: X east, Y south, Z up (the units are the model's own; the camera's ppu turns them into pixels).
Cameras are orthographic: looking along a horizontal direction F, tilted down by the elevation E.
"""
import numpy as np

EPS = 1e-9


# ------------------------------------------------------------------------------------------- constraints
class Plane:
    """half-space n.p <= d (n outward)."""
    kind = 'plane'

    def __init__(self, n, d):
        n = np.asarray(n, float)
        l = np.linalg.norm(n)
        self.n, self.d = n / l, float(d) / l

    def moved(self, R, t):
        n = R @ self.n
        return Plane(n, self.d + n @ t)


def plane_through(p, n):
    n = np.asarray(n, float); n = n / np.linalg.norm(n)
    return Plane(n, n @ np.asarray(p, float))


class Ellip:
    """solid ellipsoid: centre c, axes = columns of R, radii r."""
    kind = 'ellip'

    def __init__(self, c, R, r):
        self.c = np.asarray(c, float); self.R = np.asarray(R, float); self.r = np.asarray(r, float)

    def moved(self, R, t):
        return Ellip(R @ self.c + t, R @ self.R, self.r)


class Cyl:
    """infinite solid cylinder: a point c on the axis, unit axis a, radius r (cap it with planes)."""
    kind = 'cyl'

    def __init__(self, c, a, r):
        a = np.asarray(a, float)
        self.c = np.asarray(c, float); self.a = a / np.linalg.norm(a); self.r = float(r)

    def moved(self, R, t):
        return Cyl(R @ self.c + t, R @ self.a, self.r)


class Part:
    """a convex solid: the intersection of its constraints.  comp: component id (materials).
    sphere: (centre, radius) enclosing it, for culling rays (optional)."""

    def __init__(self, cons, comp, name='', sphere=None):
        self.cons, self.comp, self.name = list(cons), comp, name
        self.sphere = sphere

    def moved(self, R, t=(0.0, 0.0, 0.0)):
        t = np.asarray(t, float)
        sp = None if self.sphere is None else (R @ np.asarray(self.sphere[0], float) + t, self.sphere[1])
        return Part([c.moved(R, t) for c in self.cons], self.comp, self.name, sp)

    def bounds_pts(self):
        """a few points known to be inside or on the part, for culling (centres of curved constraints)."""
        return [c.c for c in self.cons if c.kind != 'plane']


# --------------------------------------------------------------------------------------------- builders
def rot_z(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])


def rot_x(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1.0, 0, 0], [0, c, -s], [0, s, c]])


def rot_y(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1.0, 0], [-s, 0, c]])


def frame_from(x_axis, z_hint=(0, 0, 1.0)):
    """an orthonormal frame with its first axis along x_axis."""
    x = np.asarray(x_axis, float); x = x / np.linalg.norm(x)
    z = np.asarray(z_hint, float); z = z - (z @ x) * x
    if np.linalg.norm(z) < 1e-6:
        z = np.array([1.0, 0, 0]) - x[0] * x
    z = z / np.linalg.norm(z)
    y = np.cross(z, x)
    return np.stack([x, y, z], axis=1)


def box_planes(c, R, h, chamfer=0.0, chamfer_axes=(0, 1, 2)):
    """an oriented box (centre c, axes = columns of R, half sizes h) with its edges cut at 45 degrees by
    `chamfer` (a scalar, or per edge family (yz, xz, xy) edges)."""
    c = np.asarray(c, float); R = np.asarray(R, float); h = np.asarray(h, float)
    cons = []
    for i in range(3):
        for s in (-1.0, 1.0):
            n = s * R[:, i]
            cons.append(Plane(n, n @ c + h[i]))
    ch = np.broadcast_to(np.asarray(chamfer, float), (3,))
    pairs = ((1, 2), (0, 2), (0, 1))
    for e, (i, j) in enumerate(pairs):
        if ch[e] <= 0:
            continue
        for si in (-1.0, 1.0):
            for sj in (-1.0, 1.0):
                n = si * R[:, i] + sj * R[:, j]
                ln = np.linalg.norm(n); n = n / ln
                # the plane cuts `ch` off each face at the edge: distance from centre = (h_i + h_j - ch) / sqrt2
                cons.append(Plane(n, n @ c + (h[i] + h[j] - ch[e]) / np.sqrt(2.0)))
    return cons


def box(c, R, h, comp, chamfer=0.0, name=''):
    return Part(box_planes(c, R, h, chamfer), comp, name, sphere=(np.asarray(c, float), float(np.linalg.norm(h)) + 1e-3))


def seg_box(p0, p1, w, d, comp, up=(0, 0, 1.0), chamfer=0.0, ext=0.0, name=''):  # noqa: sphere set by box()
    """a box from p0 to p1 (its length axis), w across (the frame's second axis), d deep (third axis);
    ext lengthens it past both ends."""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    L = np.linalg.norm(p1 - p0)
    R = frame_from(p1 - p0, up)
    return box((p0 + p1) / 2, R, (L / 2 + ext, w / 2, d / 2), comp, chamfer, name)


def cylinder(p0, p1, r, comp, name='', extra=()):
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    a = (p1 - p0) / np.linalg.norm(p1 - p0)
    cons = [Cyl(p0, a, r), Plane(a, a @ p1), Plane(-a, -a @ p0)] + list(extra)
    L = np.linalg.norm(p1 - p0)
    return Part(cons, comp, name, sphere=((p0 + p1) / 2, float(np.hypot(L / 2, r)) + 1e-3))


# ------------------------------------------------------------------------------------------ intersection
def intersect(part, O, D):
    """rays O (n,3) + t D (D (3,) shared): returns tin, tout (n,), the entering normal (n,3).  A miss has
    tin >= tout."""
    n = O.shape[0]
    tin = np.full(n, -np.inf); tout = np.full(n, np.inf)
    nin = np.zeros((n, 3))
    for c in part.cons:
        if c.kind == 'plane':
            nd = c.n @ D
            no = O @ c.n
            if abs(nd) < EPS:
                miss = no > c.d
                tin = np.where(miss, np.inf, tin)
                continue
            t = (c.d - no) / nd
            if nd < 0:                                  # entering through this plane
                better = t > tin
                tin = np.where(better, t, tin)
                nin[better] = c.n
            else:
                tout = np.minimum(tout, t)
        elif c.kind == 'ellip':
            Ri = c.R.T / c.r[:, None]                   # world -> unit sphere
            a = (O - c.c) @ Ri.T
            b = Ri @ D
            A = b @ b; B = 2 * a @ b; C = (a * a).sum(1) - 1.0
            disc = B * B - 4 * A * C
            ok = disc > 0
            sq = np.sqrt(np.where(ok, disc, 0.0))
            t0 = (-B - sq) / (2 * A); t1 = (-B + sq) / (2 * A)
            t0 = np.where(ok, t0, np.inf); t1 = np.where(ok, t1, -np.inf)
            better = ok & (t0 > tin)
            if better.any():
                p = O[better] + t0[better, None] * D
                g = (p - c.c) @ (c.R / c.r[None, :] ** 2) @ c.R.T   # gradient of the quadric
                g = g / (np.linalg.norm(g, axis=1, keepdims=True) + EPS)
                nin[better] = g
            tin = np.where(ok, np.maximum(tin, t0), np.inf)
            tout = np.minimum(tout, t1)
        elif c.kind == 'cyl':
            q = O - c.c
            qa = q @ c.a; Da = D @ c.a
            qp = q - qa[:, None] * c.a; Dp = D - Da * c.a
            A = Dp @ Dp
            if A < EPS:
                miss = (qp * qp).sum(1) > c.r * c.r
                tin = np.where(miss, np.inf, tin)
                continue
            B = 2 * qp @ Dp; C = (qp * qp).sum(1) - c.r * c.r
            disc = B * B - 4 * A * C
            ok = disc > 0
            sq = np.sqrt(np.where(ok, disc, 0.0))
            t0 = (-B - sq) / (2 * A); t1 = (-B + sq) / (2 * A)
            t0 = np.where(ok, t0, np.inf); t1 = np.where(ok, t1, -np.inf)
            better = ok & (t0 > tin)
            if better.any():
                p = qp[better] + t0[better, None] * Dp
                nin[better] = p / (np.linalg.norm(p, axis=1, keepdims=True) + EPS)
            tin = np.where(ok, np.maximum(tin, t0), np.inf)
            tout = np.minimum(tout, t1)
    return tin, tout, nin


def cast(parts, O, D, want_normals=True):
    """nearest hit over all parts: t (inf where none), part index, normal (n,3).  Parts with a bounding sphere
    are only tested against the rays that pass through it."""
    n = O.shape[0]
    best = np.full(n, np.inf); who = np.full(n, -1, np.int32); nrm = np.zeros((n, 3))
    D = np.asarray(D, float)
    for i, p in enumerate(parts):
        if p.sphere is not None:
            c, R = p.sphere
            q = O - c
            perp = q - (q @ D)[:, None] * D
            sel = np.nonzero((perp * perp).sum(1) <= R * R)[0]
            if sel.size == 0:
                continue
            tin, tout, nin = intersect(p, O[sel], D)
            hit = (tin < tout) & (tin < best[sel])
            idx = sel[hit]
            best[idx] = tin[hit]; who[idx] = i
            if want_normals:
                nrm[idx] = nin[hit]
            continue
        tin, tout, nin = intersect(p, O, D)
        hit = (tin < tout) & (tin < best)
        best = np.where(hit, tin, best)
        who = np.where(hit, i, who)
        if want_normals:
            nrm[hit] = nin[hit]
    return best, who, nrm


# ---------------------------------------------------------------------------------------------- cameras
class Cam:
    """orthographic: looking along the horizontal direction look (X, Y), tilted down by elev degrees.
    screen x = ox + ppu (p . R),  screen y = oy + ppu (sinE (p . T) - cosE z)."""

    def __init__(self, look, elev, ppu, origin):
        F = np.array(look, float); F = F / np.linalg.norm(F)
        self.F = F
        self.R = np.array([-F[1], F[0]])
        self.T = -F
        self.E = np.deg2rad(elev); self.sE, self.cE = np.sin(self.E), np.cos(self.E)
        self.ppu = float(ppu); self.ox, self.oy = origin
        # ray direction into the scene: along F horizontally and down
        self.D = np.array([F[0] * self.cE, F[1] * self.cE, -self.sE])

    def project(self, P):
        P = np.asarray(P, float)
        pr = P[..., 0] * self.R[0] + P[..., 1] * self.R[1]
        pt = P[..., 0] * self.T[0] + P[..., 1] * self.T[1]
        return self.ox + self.ppu * pr, self.oy + self.ppu * (self.sE * pt - self.cE * P[..., 2])

    def rays(self, sx, sy, zstart=400.0):
        """ray origins for screen points (arrays): on the line of sight, at height zstart."""
        pr = (np.asarray(sx, float) - self.ox) / self.ppu
        q = (np.asarray(sy, float) - self.oy) / self.ppu          # = sE pt - cE z
        z = np.full(np.shape(pr), zstart)
        pt = (q + self.cE * z) / self.sE
        X = pr * self.R[0] + pt * self.T[0]
        Y = pr * self.R[1] + pt * self.T[1]
        return np.stack([X, Y, z], axis=-1)

    def depth(self, P):
        """distance along the view direction (bigger = further from the camera)."""
        return P @ self.D


def render_ids(parts, cam, x0, y0, W, H, ss=4, zstart=400.0):
    """cast a W x H window (top-left x0, y0) at ss x ss rays per pixel: returns t, part index (H ss, W ss)."""
    xs = x0 + (np.arange(W * ss) + 0.5) / ss
    ys = y0 + (np.arange(H * ss) + 0.5) / ss
    SX, SY = np.meshgrid(xs, ys)
    O = cam.rays(SX.ravel(), SY.ravel(), zstart)
    t, who, nrm = cast(parts, O, cam.D)
    return t.reshape(SX.shape), who.reshape(SX.shape), nrm.reshape(SX.shape + (3,)), O.reshape(SX.shape + (3,))
