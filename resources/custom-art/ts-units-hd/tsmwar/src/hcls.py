"""TS's unit palette (UNITTEM.PAL) indices as one-letter colour classes, for reading a voxel's paint as text:
G house (remap 16-31), W white, L light grey, M grey, D dark grey, K near black, o dark olive, b olive, r red,
k khaki, A ochre, a dark ochre, c brown, Y yellow, O orange, P purple, ? anything else."""


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
