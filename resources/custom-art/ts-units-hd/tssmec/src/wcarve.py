"""visual hull of the Wolverine from TS's 8 standing frames (96-103), facings clockwise from screen-up."""
import numpy as np
from wpal import load


def masks(frames):
    return [load(f)[..., 3] > 0 for f in frames]


def project(u, v, w, k, nfac, ax, y0, elev=30.0):
    th = 2 * np.pi * k / nfac
    X = u * np.sin(th) + v * np.cos(th)
    Y = -u * np.cos(th) + v * np.sin(th)
    return ax + X, y0 + np.sin(np.deg2rad(elev)) * Y - np.cos(np.deg2rad(elev)) * w


def carve(ms, nfac, ax=48.0, y0=50.5, res=0.25, ext=((-12, 12), (-12, 12), (-1, 36))):
    us = np.arange(ext[0][0], ext[0][1], res) + res / 2
    vs = np.arange(ext[1][0], ext[1][1], res) + res / 2
    ws = np.arange(ext[2][0], ext[2][1], res) + res / 2
    U, V, Wz = np.meshgrid(us, vs, ws, indexing='ij')
    keep = np.ones(U.shape, bool)
    for k, m in enumerate(ms):
        sx, sy = project(U, V, Wz, k, nfac, ax, y0)
        ix = np.floor(sx).astype(int); iy = np.floor(sy).astype(int)
        ok = (ix >= 0) & (ix < m.shape[1]) & (iy >= 0) & (iy < m.shape[0])
        hitm = np.zeros(U.shape, bool)
        hitm[ok] = m[iy[ok], ix[ok]]
        keep &= hitm
    return keep, (us, vs, ws)


def reproject_iou(keep, grid, ms, nfac, ax, y0):
    us, vs, ws = grid
    U, V, Wz = np.meshgrid(us, vs, ws, indexing='ij')
    pts = (U[keep], V[keep], Wz[keep])
    ious = []
    for k, m in enumerate(ms):
        sx, sy = project(*pts, k, nfac, ax, y0)
        r = np.zeros(m.shape, bool)
        ix = np.floor(sx).astype(int); iy = np.floor(sy).astype(int)
        ok = (ix >= 0) & (ix < m.shape[1]) & (iy >= 0) & (iy < m.shape[0])
        r[iy[ok], ix[ok]] = True
        ious.append((r & m).sum() / max((r | m).sum(), 1))
    return np.array(ious)
