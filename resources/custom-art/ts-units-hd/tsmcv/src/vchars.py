"""MCV.VXL faces as character grids: the class of the first voxel seen from each side, and its depth."""
import numpy as np
from vdump import col, X, Y, Z


def cls(i):
    if i < 0: return '.'
    if 16 <= i <= 31: return 'G'
    if i == 15 or 33 <= i <= 38: return 'W'
    if i == 14 or 39 <= i <= 41: return 'L'
    if 44 <= i <= 51: return 'M'
    if i == 13 or 53 <= i <= 56: return 'D'
    if 57 <= i <= 62 or i in (166, 167): return 'K'
    if 72 <= i <= 79 or 122 <= i <= 127: return 'o'
    if 116 <= i <= 121: return 'b'
    if i in (108, 109): return 'r'
    if 128 <= i <= 143 or 112 <= i <= 115: return 'k'
    if 144 <= i <= 147: return 'A'
    if 148 <= i <= 152: return 'a'
    if 153 <= i <= 165: return 'c'
    if i == 5 or 176 <= i <= 181: return 'Y'
    if 182 <= i <= 186 or i == 7: return 'O'
    if i == 96: return 'P'
    return '?'


def face(view):
    f = col >= 0
    rows = []
    if view == 'top':
        d = np.where(f.any(2), Z - 1 - np.argmax(f[:, :, ::-1], axis=2), -1)
        for y in range(Y):
            rows.append('%3d ' % y + ''.join(cls(col[x, y, d[x, y]]) if d[x, y] >= 0 else '.' for x in range(X)) +
                        '   ' + ''.join('%x' % min(d[x, y], 15) if d[x, y] >= 0 else '.' for x in range(X)))
    elif view in ('right', 'left'):
        if view == 'right':
            d = np.where(f.any(1), np.argmax(f, axis=1), -1)
        else:
            d = np.where(f.any(1), Y - 1 - np.argmax(f[:, ::-1], axis=1), -1)
        for z in range(Z - 1, -1, -1):
            rows.append('%3d ' % z + ''.join(cls(col[x, d[x, z], z]) if d[x, z] >= 0 else '.' for x in range(X)) +
                        '   ' + ''.join(chr(48 + d[x, z]) if d[x, z] >= 0 else '.' for x in range(X)))
    else:
        if view == 'front':
            d = np.where(f.any(0), X - 1 - np.argmax(f[::-1], axis=0), -1)
        else:
            d = np.where(f.any(0), np.argmax(f, axis=0), -1)
        for z in range(Z - 1, -1, -1):
            rows.append('%3d ' % z + ''.join(cls(col[d[y, z], y, z]) if d[y, z] >= 0 else '.' for y in range(Y)) +
                        '   ' + ''.join(chr(48 + d[y, z]) if d[y, z] >= 0 else '.' for y in range(Y)))
    hdr = '    ' + ''.join(str(i // 10) if i % 10 == 0 else ' ' for i in range(X if view in ('top', 'right', 'left') else Y))
    hdr2 = '    ' + ''.join(str(i % 10) for i in range(X if view in ('top', 'right', 'left') else Y))
    return '\n'.join([view, hdr, hdr2] + rows)


if __name__ == '__main__':
    import sys
    for v in (sys.argv[1:] or ('top', 'right', 'left', 'front', 'back')):
        print(face(v)); print()
