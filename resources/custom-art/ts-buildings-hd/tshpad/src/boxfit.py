"""Fit simple solids to a TS sprite region by silhouette IoU (convex hulls of projected corners), in TS's camera.
    fit_box(mask, gx, gy, z0=0, init=(x0, x1, y0, y1, z1)) -> best params"""
import numpy as np
from PIL import Image, ImageDraw
from scipy import optimize
from scipy.spatial import ConvexHull

S = 4


def proj(gx, gy, X, Y, Z):
    return gx + 24 * (X - Y) / 128.0, gy + 12 * (X + Y) / 128.0 - 0.2297 * Z


def hull_mask(pts, size):
    im = Image.new('L', (size[0] * S, size[1] * S), 0)
    try:
        h = ConvexHull(pts)
        poly = [tuple(pts[i] * S) for i in h.vertices]
        ImageDraw.Draw(im).polygon(poly, fill=255)
    except Exception:
        pass
    return np.array(im) > 127


def box_pts(gx, gy, x0, x1, y0, y1, z0, z1):
    P = []
    for X in (x0, x1):
        for Y in (y0, y1):
            for Z in (z0, z1):
                P.append(proj(gx, gy, X, Y, Z))
    return np.array(P)


def cyl_pts(gx, gy, cx, cy, r, z0, z1, n=24):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    P = []
    for Z in (z0, z1):
        for t in a:
            P.append(proj(gx, gy, cx + r * np.cos(t), cy + r * np.sin(t), Z))
    return np.array(P)


def up(mask):
    return np.kron(mask.astype(np.uint8), np.ones((S, S), np.uint8)) > 0


def iou(a, b):
    return (a & b).sum() / max((a | b).sum(), 1)


def fit(mask, make, init, size, tries=12, scale=None, seed=0):
    M = up(mask)
    f = lambda v: -iou(hull_mask(make(*v), size), M)
    rng = np.random.default_rng(seed)
    best = (f(init), np.array(init, float))
    scale = np.array(scale if scale is not None else [10.0] * len(init))
    for k in range(tries):
        x0 = best[1] + (rng.normal(0, 1, len(init)) * scale if k else 0)
        r = optimize.minimize(f, x0, method='Nelder-Mead', options=dict(xatol=0.3, fatol=1e-4, maxiter=600,
                                                                        initial_simplex=None))
        if r.fun < best[0]:
            best = (r.fun, r.x)
    return -best[0], best[1]
