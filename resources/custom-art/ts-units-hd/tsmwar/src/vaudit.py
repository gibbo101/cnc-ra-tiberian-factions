"""vaudit.py - which of TS's surface voxels each part of the model holds, and their palette colours: a check that
every part is painted as TS paints it, and a list of the surface voxels no part holds (missing parts).
    python3 vaudit.py [tolerance in voxels]"""
import sys
from collections import Counter, defaultdict
import numpy as np
from scipy.ndimage import binary_erosion
import mwarmodel as T
import mvox
from hcls import cls


def inside(part, P, eps):
    ok = np.ones(len(P), bool)
    for c in part.cons:
        if c.kind == 'plane':
            ok &= P @ c.n <= c.d + eps
        elif c.kind == 'cyl':
            v = P - c.c
            v = v - np.outer(v @ c.a, c.a)
            ok &= np.linalg.norm(v, axis=1) <= c.r + eps
        elif c.kind == 'ellip':
            u = ((P - c.c) @ c.R) / c.r
            ok &= np.linalg.norm(u, axis=1) <= 1 + eps / c.r.min()
    return ok


if __name__ == '__main__':
    tol = float(sys.argv[1]) if len(sys.argv) > 1 else 0.35
    s, _ = mvox.SECS['mwar']
    col = s['col']
    occ = col >= 0
    surf = occ & ~binary_erosion(occ, border_value=0)
    idx = np.argwhere(surf)
    Q = idx + 0.5
    P = np.array([T.F.p(q) for q in Q])
    eps = tol * float(np.mean(T.F.sc))
    m = T.model()
    held = np.zeros(len(P), bool)
    per = defaultdict(Counter)
    comp_of = {}
    for p in m:
        k = inside(p, P, eps)
        held |= k
        for i in np.nonzero(k)[0]:
            per[p.name][int(col[tuple(idx[i])])] += 1
        comp_of[p.name] = p.comp
    names = {v: k for k, v in vars(T).items() if isinstance(v, int) and 81 <= v <= 94 and k.isupper()}
    for nm, c in sorted(per.items(), key=lambda t: -sum(t[1].values())):
        tot = sum(c.values())
        cl = Counter()
        for i, n in c.items():
            cl[cls(i)] += n
        print('%-15s %-8s %4d  %s   | %s' % (nm, names.get(comp_of[nm], '?'), tot,
              ' '.join('%s%.0f%%' % (k, 100 * v / tot) for k, v in cl.most_common(5)),
              ' '.join('%d:%d' % (k, v) for k, v in c.most_common(6))))
    miss = idx[~held]
    print('\nsurface voxels no part holds: %d of %d' % (len(miss), len(idx)))
    cm = Counter(cls(int(col[tuple(v)])) for v in miss)
    print(' by class:', dict(cm.most_common()))
    # cluster the missing ones coarsely by region
    reg = Counter((v[0] // 4 * 4, v[1] // 4 * 4, v[2] // 4 * 4) for v in miss)
    for (x, y, z), n in reg.most_common(25):
        sel = [v for v in miss if v[0] // 4 * 4 == x and v[1] // 4 * 4 == y and v[2] // 4 * 4 == z]
        print('  x %2d..%2d y %2d..%2d z %2d..%2d: %3d  %s' % (x, x + 3, y, y + 3, z, z + 3, n,
              ' '.join('%s%d' % (k, v) for k, v in Counter(cls(int(col[tuple(u)])) for u in sel).most_common(4))))
