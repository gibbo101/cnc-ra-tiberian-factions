"""connected components of a HMEC section's voxels by colour class: bounding boxes and voxel counts."""
import sys
from paths import HANDOFF
sys.path.insert(0, HANDOFF + '/renderer')
import numpy as np, vxl
from scipy import ndimage
from hcls import cls
D = HANDOFF + '/03-TSHMEC/ts-original/'
SECS = vxl.read_vxl(D + 'HMEC.VXL')


def classes(sec):
    c = SECS[sec]['col']
    f = np.vectorize(lambda v: cls(int(v)) if v >= 0 else '.')
    return f(c)


def comps(sec, chars, min_n=1):
    K = classes(sec)
    m = np.isin(K, list(chars))
    lab, n = ndimage.label(m, structure=np.ones((3, 3, 3)))
    out = []
    for i in range(1, n + 1):
        idx = np.argwhere(lab == i)
        if len(idx) < min_n:
            continue
        lo, hi = idx.min(0), idx.max(0)
        out.append((len(idx), tuple(lo), tuple(hi)))
    out.sort(key=lambda t: (t[1][0], t[1][1]))
    return out


if __name__ == '__main__':
    sec = int(sys.argv[1])
    for chars in sys.argv[2:]:
        print('section', sec, 'classes', chars)
        for n, lo, hi in comps(sec, chars):
            print('   n %4d  x %2d..%2d  y %2d..%2d  z %2d..%2d' % (n, lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
