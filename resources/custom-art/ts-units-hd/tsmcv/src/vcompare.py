"""compare the MCV model with MCV.VXL voxel by voxel: which voxels the model fills that the VXL leaves empty, and
which filled voxels the model misses, grouped into connected regions with their bounding boxes and colour classes.

    python3 vcompare.py [min_region_size]
"""
import sys
import numpy as np
from scipy import ndimage
import mcv as M
from vdump import col, X, Y, Z
from vchars import cls


def inside(part, P):
    m = np.ones(len(P), bool)
    for c in part.cons:
        if c.kind == 'plane':
            m &= P @ c.n <= c.d + 1e-9
        elif c.kind == 'ellip':
            q = (P - c.c) @ c.R / c.r
            m &= (q * q).sum(1) <= 1.0
        else:
            d = P - c.c
            d = d - np.outer(d @ c.a, c.a)
            m &= (d * d).sum(1) <= c.r * c.r
    return m


def model_grid(parts):
    xs, ys, zs = np.meshgrid(np.arange(X), np.arange(Y), np.arange(Z), indexing='ij')
    P = np.stack([xs.ravel() + 0.5 - M.CX, M.CY - (ys.ravel() + 0.5), zs.ravel() + 0.5], 1)
    occ = np.zeros(len(P), bool)
    which = np.full(len(P), -1)
    for i, p in enumerate(parts):
        m = inside(p, P)
        which[m & (which < 0)] = i
        occ |= m
    return occ.reshape(X, Y, Z), which.reshape(X, Y, Z)


def regions(mask, label, min_size=1):
    lab, n = ndimage.label(mask)
    out = []
    for i in range(1, n + 1):
        idx = np.argwhere(lab == i)
        if len(idx) < min_size:
            continue
        lo, hi = idx.min(0), idx.max(0)
        cl = ''.join(sorted(set(cls(col[tuple(v)]) for v in idx))) if label == 'miss' else ''
        out.append((len(idx), lo, hi, cl))
    return sorted(out, key=lambda r: -r[0])


if __name__ == '__main__':
    ms = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    parts = M.parts()
    occ, which = model_grid(parts)
    vox = col >= 0
    fp = occ & ~vox
    miss = vox & ~occ
    print('VXL voxels %d, model fills %d of them; misses %d; model fills %d empty voxels' %
          (vox.sum(), (occ & vox).sum(), miss.sum(), fp.sum()))
    print('\nmodel fills, VXL empty (by part):')
    names = {}
    for v in np.argwhere(fp):
        p = parts[which[tuple(v)]]
        names.setdefault((p.name, p.comp), []).append(v)
    for (nm, cp), vs in sorted(names.items(), key=lambda kv: -len(kv[1])):
        vs = np.array(vs)
        print('  %-10s %3d   x %d-%d  y %d-%d  z %d-%d' % (nm, len(vs), *np.ravel(np.stack([vs.min(0), vs.max(0)], 1))))
    print('\nVXL filled, model misses (regions of %d+):' % ms)
    for n, lo, hi, cl in regions(miss, 'miss', ms):
        print('  %3d   x %d-%d  y %d-%d  z %d-%d   classes %s' % (n, lo[0], hi[0], lo[1], hi[1], lo[2], hi[2], cl))


def exterior():
    """empty voxels connected to the outside of the grid (a voxel model is a shell: its inside is empty too)."""
    vox = col >= 0
    pad = np.pad(~vox, 1, constant_values=True)
    lab, n = ndimage.label(pad)
    ext = lab == lab[0, 0, 0]
    return ext[1:-1, 1:-1, 1:-1]


def report_exterior(ms=3):
    parts = M.parts()
    occ, which = model_grid(parts)
    vox = col >= 0
    ext = exterior()
    fp = occ & ext
    print('model fills %d voxels that are open air outside the VXL (interior hollows ignored)' % fp.sum())
    names = {}
    for v in np.argwhere(fp):
        p = parts[which[tuple(v)]]
        names.setdefault(p.name, []).append(v)
    for nm, vs in sorted(names.items(), key=lambda kv: -len(kv[1])):
        vs = np.array(vs)
        lab, n = ndimage.label(np.isin(np.arange(X * Y * Z).reshape(X, Y, Z),
                                       np.ravel_multi_index(vs.T, (X, Y, Z))))
        print('  %-10s %3d' % (nm, len(vs)))
        for i in range(1, n + 1):
            idx = np.argwhere(lab == i)
            if len(idx) >= ms:
                lo, hi = idx.min(0), idx.max(0)
                print('        %3d   x %d-%d  y %d-%d  z %d-%d' % (len(idx), lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))


def first_hit(g, view):
    """index of the first filled voxel seen from a side (-1 none): top (x, y) -> z; right (x, z) -> y from 0;
    left (x, z) -> y from max; front (y, z) -> x from max; back (y, z) -> x from 0."""
    if view == 'top':
        return np.where(g.any(2), Z - 1 - np.argmax(g[:, :, ::-1], axis=2), -1)
    if view == 'right':
        return np.where(g.any(1), np.argmax(g, axis=1), -1)
    if view == 'left':
        return np.where(g.any(1), Y - 1 - np.argmax(g[:, ::-1], axis=1), -1)
    if view == 'front':
        return np.where(g.any(0), X - 1 - np.argmax(g[::-1], axis=0), -1)
    return np.where(g.any(0), np.argmax(g, axis=0), -1)


def depth_report():
    parts = M.parts()
    occ, which = model_grid(parts)
    vox = col >= 0
    for view in ('top', 'right', 'left', 'front', 'back'):
        a = first_hit(vox, view); b = first_hit(occ, view)
        sign = {'top': 1, 'right': -1, 'left': 1, 'front': 1, 'back': -1}[view]   # + = model sticks out
        d = np.where((a >= 0) & (b >= 0), (b - a) * sign, 0)
        only_v = (a >= 0) & (b < 0); only_m = (b >= 0) & (a < 0)
        print('%-6s  pixels %d: model out of the VXL by >=1: %d, in by >=1: %d; VXL only %d; model only %d' %
              (view, (a >= 0).sum(), (d >= 1).sum(), (d <= -1).sum(), only_v.sum(), only_m.sum()))
        rows = []
        A, B = a.shape
        names = ('x', 'y') if view == 'top' else (('x', 'z') if view in ('right', 'left') else ('y', 'z'))
        txt = []
        for j in range(B - 1, -1, -1) if view != 'top' else range(B):
            line = ''
            for i in range(A):
                if only_v[i, j]: ch = 'v'
                elif only_m[i, j]: ch = 'm'
                elif a[i, j] < 0: ch = '.'
                elif d[i, j] >= 1: ch = '+' if d[i, j] < 2 else '#'
                elif d[i, j] <= -1: ch = '-' if d[i, j] > -2 else '='
                else: ch = 'o'
                line += ch
            txt.append('%3d %s' % (j, line))
        print('\n'.join(txt))


if __name__ == '__main__' and len(sys.argv) > 2 and sys.argv[2] == 'depth':
    depth_report()
