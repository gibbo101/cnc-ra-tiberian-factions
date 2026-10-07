"""flh.py - the emitter's tip (the middle of its glowing face, where the beam starts) from the turret's pivot, in leptons
(256 a cell), as the frames draw it (the turret at K_TUR about its base): forward, across (+ left), up."""
import numpy as np
import prismodel as T
from priscam import K_TUR, Z_BASE, PPU

LEPTON = 256.0 / (192.0 / PPU)                      # leptons per unit


def drawn(sec, q):
    R, t = T.pose(sec)
    p = R @ T.SECTIONS[sec].p(q) + t
    return np.array([p[0] * K_TUR, p[1] * K_TUR, Z_BASE + (p[2] - Z_BASE) * K_TUR]) * LEPTON


def tips():
    x0, x1, y0, y1, z0, z1 = T.EMIT
    return {'emitter': drawn('tur', (x1, (y0 + y1) / 2, (z0 + z1) / 2))}


def text():
    p = tips()['emitter']
    a = round(p[1])
    across = '0 across' if a == 0 else '%d %s' % (abs(a), 'left' if a > 0 else 'right')
    return {'EMITTER_FLH': '%d forward, %s, %d up' % (round(p[0]), across, round(p[2]))}


if __name__ == '__main__':
    print(text())
