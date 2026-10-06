"""obdump.py - slices of the Orca Bomber's voxel as text, one character per voxel (hcls classes; G house colour, '.'
empty) with the palette index where asked.
    python3 obdump.py x|y|z i0[,i1..] [idx]"""
import sys
import numpy as np
import obvox as mvox
from hcls import cls

col = mvox.SECS['hull'][0]['col']


def code(v, idx=False):
    if v < 0:
        return ' .' if idx else '.'
    if idx:
        return '%2s' % ('%d' % (v % 100) if v != 63 else '##')
    return {42: 'L', 43: 'L', 52: 'd', 63: '#'}.get(int(v), cls(v))


def sl(axis, i, idx=False):
    X, Y, Z = col.shape
    out = ['%s=%d' % (axis, i)]
    w = 2 if idx else 1
    if axis == 'x':
        out.append('    ' + ''.join(('%' + str(w) + 'd') % (y % 10) for y in range(Y)))
        for z in range(Z - 1, -1, -1):
            out.append('%3d ' % z + ''.join(code(col[i, y, z], idx) for y in range(Y)))
    elif axis == 'y':
        out.append('    ' + ''.join(('%' + str(w) + 'd') % (x % 10) for x in range(X)))
        for z in range(Z - 1, -1, -1):
            out.append('%3d ' % z + ''.join(code(col[x, i, z], idx) for x in range(X)))
    else:
        out.append('    ' + ''.join(('%' + str(w) + 'd') % (x % 10) for x in range(X)))
        for y in range(Y):
            out.append('%3d ' % y + ''.join(code(col[x, y, i], idx) for x in range(X)))
    return '\n'.join(out)


if __name__ == '__main__':
    idx = len(sys.argv) > 3
    for i in [int(a) for a in sys.argv[2].split(',')]:
        print(sl(sys.argv[1], i, idx)); print()
