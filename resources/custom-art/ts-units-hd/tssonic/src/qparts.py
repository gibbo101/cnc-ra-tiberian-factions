"""qparts.py - convex parts built in a voxel section's own frame: q, continuous voxel coordinates (voxel i spans
i..i+1), mapped to the section's local frame as min + q * scale (per axis, TS's).  From hmec2.py (the Mammoth Mk. II)."""
import numpy as np
from scipy.spatial import ConvexHull
import rc


class Frame:
    """a section's q space -> its local frame (min + q * sc), and its HVA pose (frame 0)."""

    def __init__(self, s, M=None):
        self.mn = np.asarray(s['min'], float)
        self.sc = (np.asarray(s['max'], float) - self.mn) / np.asarray(s['size'], float)
        self.det = s['det']
        self.size = np.asarray(s['size'])
        self.M = M

    def p(self, q):
        return self.mn + np.asarray(q, float) * self.sc

    def q(self, local):
        return (np.asarray(local, float) - self.mn) / self.sc

    def pose(self):
        M = self.M
        return M[:, :3], M[:, 3] * self.det

    def r(self, r, axis=None):
        if axis is None:
            return r * float(np.mean(self.sc))
        k = [a for a in range(3) if a != axis]
        return r * float(np.mean(self.sc[k]))


# ------------------------------------------------------------------------------------------------ builders (q space)
def B(F, x0, x1, y0, y1, z0, z1, comp, ch=0.0, name=''):
    """a box over q coordinates; ch: chamfer (local units), a scalar or (edges along x, along y, vertical)."""
    a = F.p((x0, y0, z0)); b = F.p((x1, y1, z1))
    c = (a + b) / 2; h = np.abs(b - a) / 2
    return rc.box(c, np.eye(3), h, comp, ch, name)


def _convex(P):
    n = len(P)
    s = 0.0
    for k in range(n):
        a, b, c = P[k], P[(k + 1) % n], P[(k + 2) % n]
        cr = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if abs(cr) < 1e-12:
            continue
        if s == 0.0:
            s = np.sign(cr)
        elif np.sign(cr) != s:
            raise ValueError('not convex: %s' % (np.asarray(P).tolist(),))


def prism(F, axis, pts, a0, a1, comp, ch=0.0, name='', edges=None, ends=(True, True)):
    """a convex polygon in the two axes other than `axis` (in their order: x-axis -> (y, z), y -> (x, z),
    z -> (x, y)), q coordinates, extruded along `axis` from a0 to a1.  ch chamfers the polygon's edges against the
    two end faces (edges: per polygon edge, whether it is chamfered; ends: which end faces get the chamfers)."""
    ax = [k for k in range(3) if k != axis]
    P = np.array([[F.mn[ax[0]] + u * F.sc[ax[0]], F.mn[ax[1]] + v * F.sc[ax[1]]] for u, v in pts], float)
    _convex(P)
    e0, e1 = F.mn[axis] + a0 * F.sc[axis], F.mn[axis] + a1 * F.sc[axis]
    lo, hi = min(e0, e1), max(e0, e1)
    cen = P.mean(0)

    def vec(n2, na):
        v = np.zeros(3); v[ax[0]], v[ax[1]] = n2[0], n2[1]; v[axis] = na
        return v
    cons = [rc.Plane(vec((0, 0), 1.0), hi), rc.Plane(vec((0, 0), -1.0), -lo)]
    for k in range(len(P)):
        a, b = P[k], P[(k + 1) % len(P)]
        d = b - a
        n = np.array([d[1], -d[0]]); n = n / np.linalg.norm(n)
        if n @ (cen - a) > 0:
            n = -n
        cons.append(rc.Plane(vec(n, 0.0), n @ a))
        if ch > 0 and (edges is None or edges[k]):
            for s, on in ((1.0, ends[1]), (-1.0, ends[0])):
                if not on:
                    continue
                m = vec(n, s); m = m / np.linalg.norm(m)
                ee = hi if s > 0 else -lo
                cons.append(rc.Plane(m, (n @ a + ee - ch) / np.sqrt(2.0)))
    c = vec(cen, (lo + hi) / 2)
    r = float(np.max(np.linalg.norm(P - cen, axis=1)))
    return rc.Part(cons, comp, name, sphere=(c, float(np.hypot(r, (hi - lo) / 2)) + 1e-3))


def hull(F, pts, comp, name=''):
    """the convex hull of q points as a part."""
    P = np.array([F.p(q) for q in pts], float)
    h = ConvexHull(P)
    cons = []
    seen = []
    for eq in h.equations:
        n, d = eq[:3], -eq[3]
        if any(np.allclose(n, n2, atol=1e-6) and abs(d - d2) < 1e-6 for n2, d2 in seen):
            continue
        seen.append((n, d))
        cons.append(rc.Plane(n, d))
    c = P.mean(0)
    return rc.Part(cons, comp, name, sphere=(c, float(np.max(np.linalg.norm(P - c, axis=1))) + 1e-3))


def cyl(F, q0, q1, r, comp, name='', extra=()):
    """a cylinder between two q points; r in q units."""
    p0, p1 = F.p(q0), F.p(q1)
    a = p1 - p0
    ax = int(np.argmax(np.abs(a)))
    return rc.cylinder(p0, p1, F.r(r, ax), comp, name, extra)


def ball(F, c, r, ztop, comp, name=''):
    """an ellipsoid (centre c, radii r, q units) cut flat at q z = ztop."""
    cl = F.p(c)
    rl = np.asarray(r, float) * F.sc
    top = F.p((c[0], c[1], ztop))[2]
    cons = [rc.Ellip(cl, np.eye(3), rl), rc.Plane((0, 0, 1.0), top)]
    return rc.Part(cons, comp, name, sphere=(cl, float(rl.max()) + 1e-3))


