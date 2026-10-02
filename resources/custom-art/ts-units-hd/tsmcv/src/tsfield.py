"""
tsfield.py - TS's own colours on the model: for a surface point (voxel coordinates) and its normal, the palette
colour of the voxels just inside that face of MCV.VXL, sampled across the face (bilinear, or sharper for parts
whose colours are painted bands rather than speckle), so every colour sits where TS's voxel has it.
"""
import sys
import numpy as np
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vdump as V

COL = V.col
X, Y, Z = COL.shape
PAL = np.asarray(V.PAL, np.float32)
FILLED = COL >= 0
HOUSE = (COL >= 16) & (COL <= 31)
RGB = np.where(FILLED[..., None], PAL[np.clip(COL, 0, 255)], 0.0).astype(np.float32)
SOLID = (FILLED & ~HOUSE).astype(np.float32)          # house voxels carry no colour here (house green is set apart)


def _sharp(f, s):
    if s <= 1.0:
        return f
    return np.clip((f - 0.5) * s + 0.5, 0.0, 1.0)


def sample(x, y, z, nx, ny, nz, sharp=1.0, depth=3):
    """x, y, z: points in voxel coordinates; nx, ny, nz: normals in the voxel frame.  Returns (rgb, weight):
    the palette colour across the face and how much of the sample found coloured voxels (0 where none)."""
    P = np.stack([x, y, z], -1).astype(np.float32)
    N = np.stack([nx, ny, nz], -1).astype(np.float32)
    k = np.argmax(np.abs(N), axis=-1)
    s = np.sign(np.take_along_axis(N, k[..., None], -1)[..., 0])
    s[s == 0] = 1
    out = np.zeros(P.shape, np.float32)
    wsum = np.zeros(P.shape[:-1], np.float32)
    todo = np.ones(P.shape[:-1], bool)
    dims = np.array([X, Y, Z])
    for d in range(depth):
        if not todo.any():
            break
        idx = np.nonzero(todo)
        p = P[idx]; kk = k[idx]; ss = s[idx]
        lay = np.floor(np.take_along_axis(p, kk[:, None], 1)[:, 0] - ss * (0.35 + d)).astype(int)
        # the two in-plane axes
        a1 = (kk + 1) % 3; a2 = (kk + 2) % 3
        u = np.take_along_axis(p, a1[:, None], 1)[:, 0] - 0.5
        v = np.take_along_axis(p, a2[:, None], 1)[:, 0] - 0.5
        u0 = np.floor(u).astype(int); v0 = np.floor(v).astype(int)
        fu = _sharp(u - u0, sharp); fv = _sharp(v - v0, sharp)
        acc = np.zeros((len(p), 3), np.float32); wacc = np.zeros(len(p), np.float32)
        for du, wu in ((0, 1 - fu), (1, fu)):
            for dv, wv in ((0, 1 - fv), (1, fv)):
                I = np.zeros((len(p), 3), int)
                rows = np.arange(len(p))
                I[rows, kk] = lay; I[rows, a1] = u0 + du; I[rows, a2] = v0 + dv
                ok = np.all((I >= 0) & (I < dims[None, :]), axis=1)
                Ic = np.clip(I, 0, dims[None, :] - 1)
                w = wu * wv * ok * SOLID[Ic[:, 0], Ic[:, 1], Ic[:, 2]]
                acc += w[:, None] * RGB[Ic[:, 0], Ic[:, 1], Ic[:, 2]]
                wacc += w
        got = wacc > 0.15
        sel = tuple(a[got] for a in idx)
        out[sel] = acc[got] / wacc[got][:, None]
        wsum[sel] = np.minimum(wacc[got] * 2.0, 1.0)
        todo[sel] = False
    return out, wsum


def nearest_class(x, y, z, nx, ny, nz):
    """the palette index of the voxel just inside the face at each point (-1 where empty)."""
    P = np.stack([x, y, z], -1)
    N = np.stack([nx, ny, nz], -1)
    Q = np.floor(P - 0.35 * np.sign(N) * (np.abs(N) == np.abs(N).max(-1, keepdims=True))).astype(int)
    ok = np.all((Q >= 0) & (Q < np.array([X, Y, Z])), axis=-1)
    Qc = np.clip(Q, 0, np.array([X, Y, Z]) - 1)
    c = COL[Qc[..., 0], Qc[..., 1], Qc[..., 2]]
    return np.where(ok, c, -1)
