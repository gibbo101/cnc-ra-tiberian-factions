"""the Juggernaut's colour classes by palette ramp (UNITTEM.PAL; house remap as green)."""
import numpy as np
from jpal import load, index_map

NONE, HOUSE, LGREY, DGREY, KHAKI, TAN, BRIGHT, OLIVE, BLUE, OTHER = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
NAMES = {HOUSE: 'house', LGREY: 'light grey 13-15,33-51', DGREY: 'dark grey 53-62,0', KHAKI: 'khaki 128-143',
         TAN: 'tan/brown 144-167', BRIGHT: 'bright tan 176-185', OLIVE: 'olive 76-79,112-127', BLUE: 'blue-grey 90-95,196-199'}
CCOL = {NONE: (96, 108, 72), HOUSE: (0, 200, 0), LGREY: (200, 200, 205), DGREY: (45, 45, 50), KHAKI: (230, 205, 140),
        TAN: (170, 120, 50), BRIGHT: (255, 230, 90), OLIVE: (80, 80, 30), BLUE: (60, 60, 140), OTHER: (255, 0, 255)}


def classes_of(a):
    im, _ = index_map(a)
    c = np.full(im.shape, OTHER, int)
    r = lambda lo, hi: (im >= lo) & (im <= hi)
    c[r(13, 15) | r(33, 51)] = LGREY
    c[r(52, 62) | (im == 0)] = DGREY
    c[r(128, 143)] = KHAKI
    c[r(144, 167)] = TAN
    c[r(176, 185)] = BRIGHT
    c[r(64, 79) | r(112, 127)] = OLIVE
    c[r(90, 95) | r(196, 199)] = BLUE
    c[im >= 1000] = HOUSE
    c[im < 0] = NONE
    return c, im


def classes(kind, f):
    return classes_of(load(kind, f))


def class_img(c):
    out = np.zeros(c.shape + (3,), np.uint8)
    for k, col in CCOL.items():
        out[c == k] = col
    return out
