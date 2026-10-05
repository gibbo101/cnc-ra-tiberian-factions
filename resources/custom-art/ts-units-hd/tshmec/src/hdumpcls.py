"""print a HMEC section's voxels as colour classes: slices across the unit (y-z at given x) and along it."""
import sys
from paths import HANDOFF
sys.path.insert(0, HANDOFF + '/renderer')
import numpy as np, vxl
from hcls import cls
D = HANDOFF + '/03-TSHMEC/ts-original/'
SECS = vxl.read_vxl(D + 'HMEC.VXL')


def yz(sec, x):
    c = SECS[sec]['col']; X, Y, Z = c.shape
    print('section %d x=%d  (y across 0..%d, z up)' % (sec, x, Y - 1))
    for z in range(Z - 1, -1, -1):
        print('%3d ' % z + ''.join(cls(c[x, y, z]) if c[x, y, z] >= 0 else '.' for y in range(Y)))


def xz(sec, y):
    c = SECS[sec]['col']; X, Y, Z = c.shape
    print('section %d y=%d  (x along 0..%d, z up)' % (sec, y, X - 1))
    for z in range(Z - 1, -1, -1):
        print('%3d ' % z + ''.join(cls(c[x, y, z]) if c[x, y, z] >= 0 else '.' for x in range(X)))


def xy(sec, z):
    c = SECS[sec]['col']; X, Y, Z = c.shape
    print('section %d z=%d  (x along, y down)' % (sec, z))
    for y in range(Y):
        print('%3d ' % y + ''.join(cls(c[x, y, z]) if c[x, y, z] >= 0 else '.' for x in range(X)))


if __name__ == '__main__':
    kind, sec = sys.argv[1], int(sys.argv[2])
    for v in sys.argv[3:]:
        {'yz': yz, 'xz': xz, 'xy': xy}[kind](sec, int(v))
