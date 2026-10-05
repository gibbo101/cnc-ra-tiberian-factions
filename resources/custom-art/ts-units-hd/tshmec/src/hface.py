"""print a HMEC section's faces as colour classes with the depth of the first voxel seen (like vchars.face)."""
import sys
from paths import HANDOFF
sys.path.insert(0, HANDOFF + '/renderer')
import numpy as np, vxl
from hcls import cls
D = HANDOFF + '/03-TSHMEC/ts-original/'
SECS = vxl.read_vxl(D + 'HMEC.VXL')


def dch(d):
    return chr(48 + d) if d < 10 else chr(55 + d) if d < 36 else chr(61 + d) if d < 62 else '#'


def face(sec, view):
    col = SECS[sec]['col']; X, Y, Z = col.shape
    f = col >= 0
    rows = []
    if view == 'top':
        d = np.where(f.any(2), Z - 1 - np.argmax(f[:, :, ::-1], axis=2), -1)
        for y in range(Y):
            rows.append('%3d ' % y + ''.join(cls(col[x, y, d[x, y]]) if d[x, y] >= 0 else '.' for x in range(X)) +
                        '  ' + ''.join(dch(d[x, y]) if d[x, y] >= 0 else '.' for x in range(X)))
    elif view == 'bottom':
        d = np.where(f.any(2), np.argmax(f, axis=2), -1)
        for y in range(Y):
            rows.append('%3d ' % y + ''.join(cls(col[x, y, d[x, y]]) if d[x, y] >= 0 else '.' for x in range(X)) +
                        '  ' + ''.join(dch(d[x, y]) if d[x, y] >= 0 else '.' for x in range(X)))
    elif view in ('right', 'left'):
        if view == 'right':
            d = np.where(f.any(1), np.argmax(f, axis=1), -1)
        else:
            d = np.where(f.any(1), Y - 1 - np.argmax(f[:, ::-1], axis=1), -1)
        for z in range(Z - 1, -1, -1):
            rows.append('%3d ' % z + ''.join(cls(col[x, d[x, z], z]) if d[x, z] >= 0 else '.' for x in range(X)) +
                        '  ' + ''.join(dch(d[x, z]) if d[x, z] >= 0 else '.' for x in range(X)))
    else:
        if view == 'front':
            d = np.where(f.any(0), X - 1 - np.argmax(f[::-1], axis=0), -1)
        else:
            d = np.where(f.any(0), np.argmax(f, axis=0), -1)
        for z in range(Z - 1, -1, -1):
            rows.append('%3d ' % z + ''.join(cls(col[d[y, z], y, z]) if d[y, z] >= 0 else '.' for y in range(Y)) +
                        '  ' + ''.join(dch(d[y, z]) if d[y, z] >= 0 else '.' for y in range(Y)))
    n = X if view in ('top', 'bottom', 'right', 'left') else Y
    hdr = '    ' + ''.join(str(i // 10) if i % 10 == 0 else ' ' for i in range(n))
    hdr2 = '    ' + ''.join(str(i % 10) for i in range(n))
    return '\n'.join(['section %d %s' % (sec, view), hdr, hdr2] + rows)


if __name__ == '__main__':
    sec = int(sys.argv[1])
    for v in sys.argv[2:]:
        print(face(sec, v)); print()
