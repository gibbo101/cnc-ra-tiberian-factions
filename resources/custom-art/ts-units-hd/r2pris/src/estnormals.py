"""estimate a VXL normal table from voxels: each normal index's average outward direction (from a voxel towards its
empty neighbours, over the 26 round it) across every surface voxel that uses it.  Used for RA2's 244 normals (mode 4);
checked by estimating TS's 36 (mode 2) the same way against tsnormals.py.

    python3 estnormals.py MODE out.py VXL [VXL ...]
"""
import sys
import os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vxl

OFFS = np.array([(i, j, k) for i in (-1, 0, 1) for j in (-1, 0, 1) for k in (-1, 0, 1) if (i, j, k) != (0, 0, 0)], float)
UNIT = OFFS / np.linalg.norm(OFFS, axis=1, keepdims=True)


def accumulate(paths, n):
    acc = np.zeros((n, 3)); cnt = np.zeros(n)
    for p in paths:
        for s in vxl.read_vxl(p):
            filled = s['col'] >= 0
            pad = np.pad(filled, 1)
            X, Y, Z = filled.shape
            out = np.zeros(filled.shape + (3,))
            for o, u in zip(OFFS.astype(int), UNIT):
                empty = ~pad[1 + o[0]:1 + o[0] + X, 1 + o[1]:1 + o[1] + Y, 1 + o[2]:1 + o[2] + Z]
                out += empty[..., None] * u
            nrm = s['nrm']
            surf = filled & (np.linalg.norm(out, axis=-1) > 0.5)
            d = out[surf]; d = d / np.linalg.norm(d, axis=1, keepdims=True)
            idx = np.clip(nrm[surf], 0, n - 1)
            np.add.at(acc, idx, d); np.add.at(cnt, idx, 1)
    return acc, cnt


if __name__ == '__main__':
    mode, out, paths = int(sys.argv[1]), sys.argv[2], sys.argv[3:]
    n = {2: 36, 4: 244}[mode]
    acc, cnt = accumulate(paths, n)
    tab = acc / np.maximum(np.linalg.norm(acc, axis=1, keepdims=True), 1e-9)
    print('indices used: %d of %d; voxels per index: median %d, min %d' % ((cnt > 0).sum(), n, np.median(cnt[cnt > 0]),
                                                                          cnt[cnt > 0].min()))
    if mode == 2:
        from tsnormals import TS_NORMALS
        ang = np.degrees(np.arccos(np.clip((tab * TS_NORMALS).sum(1), -1, 1)))
        print('against tsnormals.py: median %.1f deg, max %.1f deg' % (np.median(ang[cnt > 0]), ang[cnt > 0].max()))
    with open(out, 'w') as f:
        f.write('"""the VXL normal table for mode %d (%d normals), estimated by estnormals.py from %d VXL files (each\n'
                'index\'s average outward direction); COUNT is how many surface voxels each estimate rests on (0 = unused:\n'
                'its direction is 0, so the detail layer leaves those voxels to the geometry)."""\n' % (mode, n, len(paths)))
        f.write('import numpy as np\n\nNORMALS = np.array([\n')
        for v in tab:
            f.write('    (%.4f, %.4f, %.4f),\n' % tuple(v))
        f.write('])\nCOUNT = np.array([%s])\n' % ', '.join('%d' % c for c in cnt))
    print('written', out)
