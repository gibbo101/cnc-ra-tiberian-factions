"""flh.py - the weapon tips from the turret's pivot, in leptons (256 a cell), as the frames draw them (the turret at
K_TUR about its base): forward, across (+ left), up."""
import numpy as np
import apocmodel as T
from apoccam import K_TUR, Z_BASE, PPU

LEPTON = 256.0 / (192.0 / PPU)                      # leptons per unit


def drawn(sec, q):
    R, t = T.pose(sec)
    p = R @ T.SECTIONS[sec].p(q) + t
    return np.array([p[0] * K_TUR, p[1] * K_TUR, Z_BASE + (p[2] - Z_BASE) * K_TUR]) * LEPTON


def tips():
    out = {}
    out['barrels'] = [drawn('barl', (27.15, yc, T.BAR_Z)) for yc in T.BAR_Y]
    u, v = T.pod_axis()
    out['pods'] = [drawn('tur', np.array([T.POD_C[0], yc, T.POD_C[1]]) + T.POD_S[1] * u) for yc in T.POD_Y]
    return out


def text():
    t = tips()
    f = lambda p: '%d forward, %d %s, %d up' % (round(p[0]), abs(round(p[1])), 'left' if p[1] > 0 else 'right', round(p[2]))
    return {'BARREL_FLH': '  /  '.join(f(p) for p in t['barrels']), 'POD_FLH': '  /  '.join(f(p) for p in t['pods'])}


if __name__ == '__main__':
    print(text())
