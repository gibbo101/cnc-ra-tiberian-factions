"""layer dumps of the Mk. II's sections (class letters as vchars.py; rows y, cols x, per z)."""
import sys
import numpy as np
import hvox as H


def cls(i):
    if i < 0: return '.'
    if 16 <= i <= 31: return 'G'
    if i == 15 or 33 <= i <= 38: return 'W'
    if i == 14 or 39 <= i <= 41: return 'L'
    if 42 <= i <= 51: return 'M'
    if i == 13 or 52 <= i <= 56: return 'D'
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
    return '?'


def dump(si, zs=None):
    s = H.SECS[si]; col = s['col']; X, Y, Z = col.shape
    print('section %d %s  size %s' % (si, s['name'], (X, Y, Z)))
    for z in (zs if zs is not None else range(Z)):
        rows = []
        for y in range(Y):
            line = ''.join(cls(col[x, y, z]) for x in range(X))
            if line.strip('.'):
                rows.append('  %2d %s' % (y, line))
        if rows:
            print(' z=%d' % z)
            print('     ' + ''.join(str(i // 10) if i % 10 == 0 else ' ' for i in range(X)))
            print('\n'.join(rows))


if __name__ == '__main__':
    for a in sys.argv[1:]:
        dump(int(a))
