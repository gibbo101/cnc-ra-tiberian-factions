"""
vplace.py - find where the mod's frames put a voxel unit: render the unit's posed voxel centres as small squares
through an orthographic camera (elevation, px per voxel, origin) and match the mod's opaque pixels (IoU), coarse
then fine.  The facings run counter-clockwise from north (32); the unit frame is x forward, y left, z up.
"""
import numpy as np
from PIL import Image


def world(P, facing, n=32):
    k = (n - facing) % n
    th = 2 * np.pi * k / n
    fw = np.array([np.sin(th), -np.cos(th)]); rt = np.array([np.cos(th), np.sin(th)])
    X = P[:, 0] * fw[0] - P[:, 1] * rt[0]
    Y = P[:, 0] * fw[1] - P[:, 1] * rt[1]
    return X, Y, P[:, 2]


def raster(X, Y, Z, sc, ox, oy, el, size, rr=0.6):
    sx = ox + X * sc
    sy = oy + (np.sin(np.deg2rad(el)) * Y - np.cos(np.deg2rad(el)) * Z) * sc
    m = np.zeros((size[1], size[0]), bool)
    r = int(round(sc * rr))
    cx = np.round(sx).astype(int); cy = np.round(sy).astype(int)
    for dy in range(-r, r + 1):
        yy = np.clip(cy + dy, 0, size[1] - 1)
        for dx in range(-r, r + 1):
            m[yy, np.clip(cx + dx, 0, size[0] - 1)] = True
    return m


def opaque(path, thr=250):
    return np.array(Image.open(path).convert('RGBA'))[..., 3] > thr


def score(data, sc, ox, oy, el, size):
    s = []
    for X, Y, Z, a in data:
        m = raster(X, Y, Z, sc, ox, oy, el, size)
        s.append((m & a).sum() / max((m | a).sum(), 1))
    return float(np.mean(s))


def search(data, size, el=30.0, sc_range=(5.0, 8.0), ox_range=None, oy_range=None, coarse=(0.2, 4, 4)):
    W, H = size
    ox_range = ox_range or (W / 2 - 16, W / 2 + 16)
    oy_range = oy_range or (H / 2 - 60, H / 2 + 120)
    best = None
    for sc in np.arange(sc_range[0], sc_range[1] + 1e-6, coarse[0]):
        for ox in np.arange(ox_range[0], ox_range[1] + 1e-6, coarse[1]):
            for oy in np.arange(oy_range[0], oy_range[1] + 1e-6, coarse[2]):
                s = score(data[:2], sc, ox, oy, el, size)
                if best is None or s > best[0]:
                    best = (s, sc, ox, oy)
    s0, sc0, ox0, oy0 = best
    best = None
    for sc in np.arange(sc0 - 0.2, sc0 + 0.201, 0.05):
        for ox in np.arange(ox0 - 4, ox0 + 4.01, 0.5):
            for oy in np.arange(oy0 - 4, oy0 + 4.01, 0.5):
                s = score(data, sc, ox, oy, el, size)
                if best is None or s > best[0]:
                    best = (s, sc, ox, oy)
    return best


def estimate(data, el):
    """scale and origin from the bounding boxes: the opaque pixels' extent against the points' extent."""
    scs, oxs, oys = [], [], []
    for X, Y, Z, a in data:
        ys, xs = np.nonzero(a)
        Sy = np.sin(np.deg2rad(el)) * Y - np.cos(np.deg2rad(el)) * Z
        sc = (xs.max() - xs.min()) / max(X.max() - X.min() + 1.0, 1e-3)
        scs.append(sc)
    sc = float(np.median(scs))
    for X, Y, Z, a in data:
        ys, xs = np.nonzero(a)
        Sy = np.sin(np.deg2rad(el)) * Y - np.cos(np.deg2rad(el)) * Z
        oxs.append((xs.max() + xs.min()) / 2 - sc * (X.max() + X.min()) / 2)
        oys.append((ys.max() + ys.min()) / 2 - sc * (Sy.max() + Sy.min()) / 2)
    return sc, float(np.median(oxs)), float(np.median(oys))


def fit(data, size, el, span=(0.3, 6, 6), steps=(0.05, 0.5, 0.5)):
    sc0, ox0, oy0 = estimate(data, el)
    best = None
    for sc in np.arange(sc0 - span[0], sc0 + span[0] + 1e-6, steps[0] * 2):
        for ox in np.arange(ox0 - span[1], ox0 + span[1] + 1e-6, 1.0):
            for oy in np.arange(oy0 - span[2], oy0 + span[2] + 1e-6, 1.0):
                s = score(data[:2], sc, ox, oy, el, size)
                if best is None or s > best[0]:
                    best = (s, sc, ox, oy)
    s0, sc1, ox1, oy1 = best
    best = None
    for sc in np.arange(sc1 - 0.1, sc1 + 0.1001, steps[0]):
        for ox in np.arange(ox1 - 1, ox1 + 1.001, steps[1]):
            for oy in np.arange(oy1 - 1, oy1 + 1.001, steps[2]):
                s = score(data, sc, ox, oy, el, size)
                if best is None or s > best[0]:
                    best = (s, sc, ox, oy)
    return best
