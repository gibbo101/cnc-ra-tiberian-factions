"""vdump.py - slices of the Dropship's voxel section as text, one character per voxel coding TS's palette shade:
G house 26, g 24, h 25/27/28.., . grey 49, + 48, * 47, @ 44-46, - 50, = 51, % 52, d 53, D 54-56, k 57-58, K 59-62,
# 63/166/167, A ochre 144-147, a dark ochre 148-152, c brown 153-165, o olive 72-79/116-127, y khaki 128-143,
b blue-grey 88-95, W white/light 14-15/33-43, r red, ? other.
    python3 vdump.py SECTION x|y|z i0[,i1..]  (slices across that axis)"""
import sys
import numpy as np
import dvox as svox


def code(i):
    i = int(i)
    if i < 0: return ' '
    if i == 26: return 'G'
    if i == 24: return 'g'
    if 16 <= i <= 31: return 'h'
    if i == 49: return '.'
    if i == 48: return '+'
    if i == 47: return '*'
    if 44 <= i <= 46: return '@'
    if i == 50: return '-'
    if i == 51: return '='
    if i == 52: return '%'
    if i == 53: return 'd'
    if 54 <= i <= 56: return 'D'
    if 57 <= i <= 58: return 'k'
    if 59 <= i <= 62: return 'K'
    if i in (63, 166, 167): return '#'
    if 144 <= i <= 147: return 'A'
    if 148 <= i <= 152: return 'a'
    if 153 <= i <= 165: return 'c'
    if 72 <= i <= 79 or 116 <= i <= 127: return 'o'
    if 128 <= i <= 143: return 'y'
    if 88 <= i <= 95: return 'b'
    if i in (14, 15) or 33 <= i <= 43: return 'W'
    if i in (108, 109): return 'r'
    return '?'


def sl(sec, axis, i):
    col = svox.SECS[sec][0]['col']
    X, Y, Z = col.shape
    out = ['%s %s=%d' % (sec, axis, i)]
    if axis == 'x':
        out.append('    ' + ''.join(str(y % 10) for y in range(Y)))
        for z in range(Z - 1, -1, -1):
            out.append('%3d ' % z + ''.join(code(col[i, y, z]) for y in range(Y)))
    elif axis == 'y':
        out.append('    ' + ''.join(str(x % 10) for x in range(X)))
        for z in range(Z - 1, -1, -1):
            out.append('%3d ' % z + ''.join(code(col[x, i, z]) for x in range(X)))
    else:
        out.append('    ' + ''.join(str(x % 10) for x in range(X)))
        for y in range(Y):
            out.append('%3d ' % y + ''.join(code(col[x, y, i]) for x in range(X)))
    return '\n'.join(out)


if __name__ == '__main__':
    sec, axis = sys.argv[1], sys.argv[2]
    for i in [int(a) for a in sys.argv[3].split(',')]:
        print(sl(sec, axis, i)); print()
