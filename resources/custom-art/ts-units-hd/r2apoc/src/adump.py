"""adump.py - the Apocalypse's voxel sections as text, one character per voxel coding RA2's palette (UNITTEM.PAL):
G house (remap 16-31), O light olive 70-71 (the turret), o olive 73-74 (the hull), d dark olive 122-125, L light grey
43, @ grey 13, M grey 50-51, D dark grey 53-56, K near black 57-62/166/167, ? other.
    python3 adump.py SECTION top|bottom|right|left|front|back
    python3 adump.py SECTION x|y|z i0[,i1..]"""
import sys
import numpy as np
import avox


def code(i):
    i = int(i)
    if i < 0: return '.'
    if 16 <= i <= 31: return 'G'
    if i in (70, 71): return 'O'
    if i in (72, 73, 74, 75): return 'o'
    if 122 <= i <= 125: return 'd'
    if i == 43: return 'L'
    if i == 13: return '@'
    if i in (50, 51, 52): return 'M'
    if 53 <= i <= 56: return 'D'
    if 57 <= i <= 62 or i in (166, 167): return 'K'
    return '?'


def dch(d):
    return chr(48 + d) if d < 10 else chr(55 + d) if d < 36 else '#'


def face(k, view):
    col = avox.SECS[k][0]['col']; X, Y, Z = col.shape
    f = col >= 0
    rows = []
    if view in ('top', 'bottom'):
        d = np.where(f.any(2), (Z - 1 - np.argmax(f[:, :, ::-1], axis=2)) if view == 'top' else np.argmax(f, axis=2), -1)
        for y in range(Y):
            rows.append('%3d ' % y + ''.join(code(col[x, y, d[x, y]]) if d[x, y] >= 0 else '.' for x in range(X)) +
                        '  ' + ''.join(dch(d[x, y]) if d[x, y] >= 0 else '.' for x in range(X)))
    elif view in ('right', 'left'):
        d = np.where(f.any(1), np.argmax(f, axis=1) if view == 'right' else Y - 1 - np.argmax(f[:, ::-1], axis=1), -1)
        for z in range(Z - 1, -1, -1):
            rows.append('%3d ' % z + ''.join(code(col[x, d[x, z], z]) if d[x, z] >= 0 else '.' for x in range(X)) +
                        '  ' + ''.join(dch(d[x, z]) if d[x, z] >= 0 else '.' for x in range(X)))
    else:
        d = np.where(f.any(0), (X - 1 - np.argmax(f[::-1], axis=0)) if view == 'front' else np.argmax(f, axis=0), -1)
        for z in range(Z - 1, -1, -1):
            rows.append('%3d ' % z + ''.join(code(col[d[y, z], y, z]) if d[y, z] >= 0 else '.' for y in range(Y)) +
                        '  ' + ''.join(dch(d[y, z]) if d[y, z] >= 0 else '.' for y in range(Y)))
    n = X if view in ('top', 'bottom', 'right', 'left') else Y
    hdr = '    ' + ''.join(str(i // 10) if i % 10 == 0 else ' ' for i in range(n))
    hdr2 = '    ' + ''.join(str(i % 10) for i in range(n))
    return '\n'.join(['%s %s' % (k, view), hdr, hdr2] + rows)


def sl(sec, axis, i):
    col = avox.SECS[sec][0]['col']
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
    if len(sys.argv) < 4:
        print(face(sec, axis))
    else:
        for i in [int(a) for a in sys.argv[3].split(',')]:
            print(sl(sec, axis, i)); print()
