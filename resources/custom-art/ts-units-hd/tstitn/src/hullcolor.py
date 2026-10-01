"""colour the visual hull from TS's views: per surface voxel, the mean colour over the views that see it."""
import numpy as np
from carve import *
from tspal import load

def surface_colours(keep, grid, frames, nfac, ax, y0, elev, res):
    us, vs, ws = grid
    idx = np.argwhere(keep)
    U = us[idx[:, 0]]; V = vs[idx[:, 1]]; Wz = ws[idx[:, 2]]
    acc = np.zeros((len(idx), 3)); cnt = np.zeros(len(idx))
    sE, cE = np.sin(np.deg2rad(elev)), np.cos(np.deg2rad(elev))
    for k, f in enumerate(frames):
        a = load(f)
        th = 2 * np.pi * k / nfac
        X = U * np.sin(th) + V * np.cos(th)
        Y = -U * np.cos(th) + V * np.sin(th)
        sx = ax + X; sy = y0 + sE * Y - cE * Wz
        depth = Y * cE + Wz * sE                      # towards the camera (bigger = nearer)
        ix = np.floor(sx).astype(int); iy = np.floor(sy).astype(int)
        # z-buffer at 4x sub-pixel to pick visible voxels
        sub = 4
        jx = np.floor(sx * sub).astype(int); jy = np.floor(sy * sub).astype(int)
        key = jy * 10000 + jx
        order = np.lexsort((-depth, key))
        first = np.ones(len(order), bool); first[1:] = key[order][1:] != key[order][:-1]
        vis = np.zeros(len(idx), bool); vis[order[first]] = True
        ok = vis & (ix >= 0) & (ix < a.shape[1]) & (iy >= 0) & (iy < a.shape[0])
        col = a[iy[ok], ix[ok], :3]; al = a[iy[ok], ix[ok], 3] > 0
        sel = np.nonzero(ok)[0][al]
        acc[sel] += col[al]; cnt[sel] += 1
    return idx, acc, cnt
