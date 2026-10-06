"""otproj.py - TS's own voxel colours projected onto the model (each hit takes the colour of the first of TS's voxels
found stepping in from it against its face's normal, else its nearest coloured voxel): a check of where TS's paint falls
on the rebuilt parts.  House colour shown as the HD green."""
import numpy as np
import otvox as V
import otvoxd as VD

PAL = V.PAL.copy()
for _i in range(16, 32):
    PAL[_i] = (0, 214 - (_i - 16) * 6, 0)
COL = VD.COL
SH = COL >= 0


def ts_index(q, n):
    """q: (N, 3) hit points (voxel coordinates), n: (N, 3) their faces' normals (unit frame ~ q axes)."""
    X, Y, Z = COL.shape
    out = np.full(len(q), -1, np.int32)
    todo = np.ones(len(q), bool)
    for t in (0.15, 0.45, 0.75, 1.05, 1.4, 1.8):
        p = np.floor(q - n * t).astype(int)
        ok = todo & (p[:, 0] >= 0) & (p[:, 0] < X) & (p[:, 1] >= 0) & (p[:, 1] < Y) & (p[:, 2] >= 0) & (p[:, 2] < Z)
        idx = np.nonzero(ok)[0]
        c = COL[p[idx, 0], p[idx, 1], p[idx, 2]]
        hit = c >= 0
        out[idx[hit]] = c[hit]
        todo[idx[hit]] = False
    if todo.any():
        idx = np.nonzero(todo)[0]
        base = np.floor(q[idx]).astype(int)
        best = np.full(len(idx), 1e9)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    p = base + np.array([dx, dy, dz])
                    ok = (p[:, 0] >= 0) & (p[:, 0] < X) & (p[:, 1] >= 0) & (p[:, 1] < Y) & (p[:, 2] >= 0) & (p[:, 2] < Z)
                    c = np.full(len(idx), -1)
                    c[ok] = COL[p[ok, 0], p[ok, 1], p[ok, 2]]
                    d = np.linalg.norm(q[idx] - (p + 0.5), axis=1)
                    better = (c >= 0) & (d < best)
                    out[idx[better]] = c[better]; best[better] = d[better]
    return out


def ts_albedo(r):
    import otmat as MM
    hm = r.hitmask
    q = np.stack([r.lu[hm], r.lv[hm], r.lw[hm]], 1)
    nu, nv, nw = MM.local_normals(r)
    n = np.stack([nu[hm], nv[hm], nw[hm]], 1)
    idx = ts_index(q, n)
    alb = np.zeros(r.comp.shape + (3,), np.float32)
    c = np.where(idx[:, None] >= 0, PAL[np.maximum(idx, 0)], np.array([255, 0, 255.]))
    alb[hm] = c
    return alb
