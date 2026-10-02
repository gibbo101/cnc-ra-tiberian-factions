"""SMECH colour classes by palette ramp."""
import numpy as np
from wpal import load, index_map

# class ids
NONE, TAN, KHAKI, OLIVE, GREY, DARK, HOUSE, FLASH, ORANGE, BRIGHT = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
NAMES = {TAN: 'tan(144-167)', KHAKI: 'khaki(128-143)', OLIVE: 'olive(76-79,112-127)', GREY: 'grey(33-51,13-15,64-73,242-244)',
         DARK: 'dark(52-62,0)', HOUSE: 'house', FLASH: 'flash(246-248,16,20)', ORANGE: 'orange(185-189,96-107)',
         BRIGHT: 'bright tan(176-184)'}
CCOL = {NONE: (96, 108, 72), TAN: (200, 150, 60), KHAKI: (210, 190, 130), OLIVE: (70, 70, 30), GREY: (170, 170, 175),
        DARK: (40, 40, 44), HOUSE: (0, 200, 0), FLASH: (255, 255, 0), ORANGE: (255, 90, 0), BRIGHT: (255, 225, 110)}


def classes(f):
    a = load(f); im, _ = index_map(a)
    c = np.zeros(im.shape, int)
    r = lambda lo, hi: (im >= lo) & (im <= hi)
    c[r(144, 167)] = TAN
    c[r(176, 184)] = BRIGHT
    c[r(128, 143)] = KHAKI
    c[r(76, 79) | r(112, 127)] = OLIVE
    c[r(33, 51) | r(13, 15) | r(64, 73) | r(242, 244)] = GREY
    c[r(52, 62) | (im == 0)] = DARK
    c[im >= 1000] = HOUSE
    c[r(246, 248) | (im == 16) | (im == 20)] = FLASH
    c[r(185, 189) | r(96, 107)] = ORANGE
    c[im < 0] = NONE
    return c, im, a


def class_img(c):
    out = np.zeros(c.shape + (3,), np.uint8)
    for k, col in CCOL.items():
        out[c == k] = col
    return out
