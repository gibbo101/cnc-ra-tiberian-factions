"""lpstcam.py - the Mobile Sensor Array's canvas, camera and frames (as v1 and the mod have them): 384 x 384, the RA
grid's camera (orthographic, 32 degrees above the ground, looking north) at 6.24 canvas px a voxel, the unit's
position at canvas (191.5, 191.08); 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E), each with its
shadow."""
import numpy as np
import rc
import rcrender as RR

CANVAS = (384, 384)
PPU = 6.24
ORIGIN = (191.5, 191.08)
ELEV = 32.0


def camera():
    return RR.Cam((0, -1), ELEV, PPU, ORIGIN)


def flat_cam():
    return rc.Cam((0, -1), ELEV, PPU, ORIGIN)


def facing_cw(k, n=32):
    th = 2 * np.pi * k / n
    f = np.array([np.sin(th), -np.cos(th), 0.0]); r = np.array([np.cos(th), np.sin(th), 0.0])
    return np.stack([f, -r, np.array([0, 0, 1.0])], axis=1)


def mod_to_cw(f, n=32):
    return (n - f) % n


def unit_to_world(facing):
    return facing_cw(mod_to_cw(facing))
