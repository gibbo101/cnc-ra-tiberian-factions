"""
rcexport.py - export models built from convex parts (rc.py) as glTF meshes, for the units' 3D models.

Every part is convex, so its mesh is exact: a part bounded by planes is their halfspace intersection; a part with
a cylinder or an ellipsoid is the convex hull of points on its curved surface and its cut edges.  Box-shaped parts
also give back their own frame (centre, axes), so a moving part can be exported once in its own frame and posed by
a node transform (the legs' walk as a glTF animation).
"""
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy.spatial import ConvexHull, HalfspaceIntersection
from scipy.optimize import linprog
import rc


def box_frame(part):
    """(R, c, h) of a part made by rc.box / rc.seg_box (its first six planes are the box's faces)."""
    cons = part.cons
    R = np.stack([cons[1].n, cons[3].n, cons[5].n], 1)
    a = np.array([(cons[2 * i + 1].d - cons[2 * i].d) / 2 for i in range(3)])
    h = np.array([(cons[2 * i + 1].d + cons[2 * i].d) / 2 for i in range(3)])
    return R, R @ a, h


def interior_point(planes):
    A = np.array([p.n for p in planes]); b = np.array([p.d for p in planes])
    norm = np.linalg.norm(A, axis=1)
    res = linprog(np.r_[0, 0, 0, -1.0], A_ub=np.c_[A, norm], b_ub=b, bounds=[(None, None)] * 3 + [(0, None)],
                  method='highs')
    return res.x[:3], res.x[3]


def plane_mesh(planes):
    pt, r = interior_point(planes)
    if r <= 1e-6:
        return None
    hs = np.array([np.r_[p.n, -p.d] for p in planes])
    V = HalfspaceIntersection(hs, pt).intersections
    return hull_mesh(V)


def inside(cons, P, tol=1e-6):
    m = np.ones(len(P), bool)
    for c in cons:
        if c.kind == 'plane':
            m &= P @ c.n <= c.d + tol
        elif c.kind == 'ellip':
            q = (P - c.c) @ (c.R / c.r[None, :])
            m &= (q * q).sum(1) <= 1 + 1e-6
        elif c.kind == 'cyl':
            q = P - c.c; qa = q @ c.a
            m &= ((q - qa[:, None] * c.a) ** 2).sum(1) <= c.r ** 2 * (1 + 1e-6)
    return m


def curved_mesh(part, n=48):
    """points on the curved surfaces (and where the planes cut them), kept where inside the part; their hull."""
    pts = []
    planes = [c for c in part.cons if c.kind == 'plane']
    for c in part.cons:
        if c.kind == 'ellip':
            th, ph = np.meshgrid(np.linspace(0, np.pi, n), np.linspace(0, 2 * np.pi, 2 * n, endpoint=False))
            u = np.stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)], -1).reshape(-1, 3)
            pts.append(c.c + (u * c.r) @ c.R.T)
            # each plane's cut through the ellipsoid: the ellipse where they meet
            for p in planes:
                pts.append(plane_ellipsoid_ring(p, c, 2 * n))
        elif c.kind == 'cyl':
            e1 = np.cross(c.a, [0, 0, 1.0])
            if np.linalg.norm(e1) < 1e-6:
                e1 = np.cross(c.a, [1.0, 0, 0])
            e1 /= np.linalg.norm(e1); e2 = np.cross(c.a, e1)
            ang = np.linspace(0, 2 * np.pi, 2 * n, endpoint=False)
            ring = np.cos(ang)[:, None] * e1 + np.sin(ang)[:, None] * e2
            # where each plane cuts the cylinder's surface lines
            for p in planes:
                na = p.n @ c.a
                if abs(na) < 1e-9:
                    continue
                base = c.c + c.r * ring
                t = (p.d - base @ p.n) / na
                pts.append(base + t[:, None] * c.a)
    if not pts:
        return plane_mesh(planes)
    P = np.concatenate(pts, 0)
    P = P[inside(part.cons, P, tol=1e-5)]
    # plane-only corners (a cylinder's caps cut by other planes etc.) are covered by the rings; add the plane
    # polytope's own corners that are inside the curved constraints
    if len(planes) >= 4:
        try:
            pm = plane_mesh(planes)
            if pm is not None:
                V = pm[0]
                P = np.concatenate([P, V[inside(part.cons, V, tol=1e-5)]], 0)
        except Exception:
            pass
    if len(P) < 4:
        return None
    return hull_mesh(P)


def plane_ellipsoid_ring(p, e, n):
    """points where the plane p cuts the ellipsoid e (an ellipse), n of them; empty if they miss."""
    # in the unit-sphere frame: q = R^T (x - c) / r;  plane: n.x = d -> (n R diag(r)) . q = d - n.c
    m = (e.R * e.r[None, :]).T @ p.n
    dd = p.d - p.n @ e.c
    lm = np.linalg.norm(m)
    if lm < 1e-12:
        return np.zeros((0, 3))
    m_ = m / lm; s = dd / lm
    if abs(s) >= 1:
        return np.zeros((0, 3))
    rad = np.sqrt(1 - s * s)
    a1 = np.cross(m_, [0, 0, 1.0])
    if np.linalg.norm(a1) < 1e-6:
        a1 = np.cross(m_, [1.0, 0, 0])
    a1 /= np.linalg.norm(a1); a2 = np.cross(m_, a1)
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    q = s * m_ + rad * (np.cos(ang)[:, None] * a1 + np.sin(ang)[:, None] * a2)
    return e.c + (q * e.r) @ e.R.T


def hull_mesh(P):
    h = ConvexHull(P)
    V = P[h.vertices]
    remap = -np.ones(len(P), int); remap[h.vertices] = np.arange(len(h.vertices))
    F = remap[h.simplices]
    # wind outward
    c = V.mean(0)
    a, b, d = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    fn = np.cross(b - a, d - a)
    flip = ((a - c) * fn).sum(1) < 0
    F[flip] = F[flip][:, [0, 2, 1]]
    return V, F


def part_mesh(part):
    if any(c.kind != 'plane' for c in part.cons):
        return curved_mesh(part)
    return plane_mesh(part.cons)


def flat_shaded(V, F):
    """split vertices per face (crisp facets): positions, faces, normals."""
    P = V[F].reshape(-1, 3)
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    n = np.cross(b - a, c - a); n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)
    N = np.repeat(n, 3, axis=0)
    return P, np.arange(len(P)).reshape(-1, 3), N


def smooth_shaded(V, F, crease_deg=40.0):
    """vertex normals averaged over the faces that meet at a vertex, split where faces meet at a crease."""
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    fn = np.cross(b - a, c - a); area = np.linalg.norm(fn, axis=1, keepdims=True); fn = fn / (area + 1e-12)
    vn = np.zeros_like(V)
    for k in range(3):
        np.add.at(vn, F[:, k], fn * area)
    vn /= (np.linalg.norm(vn, axis=1, keepdims=True) + 1e-12)
    # faces whose normal is far from the averaged vertex normal keep their own (creases)
    P = V[F].reshape(-1, 3); N = vn[F].reshape(-1, 3)
    fnr = np.repeat(fn, 3, axis=0)
    crease = (N * fnr).sum(1) < np.cos(np.deg2rad(crease_deg))
    N[crease] = fnr[crease]
    return P, np.arange(len(P)).reshape(-1, 3), N
