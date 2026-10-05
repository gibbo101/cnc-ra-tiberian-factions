"""hmec2cam.py - the Mk. II's canvas, camera and frames (as v1 and the mod have them): 576 x 576, the RA grid's camera
at 35 degrees above the ground (Luke's choice for this unit), looking north, 6.8 canvas px a voxel, the unit's
position (the HVA origin, on the ground) at canvas (287.5, 374); frame = facing x 8 + step, 32 facings
counter-clockwise from north (0 N, 8 W, 16 S, 24 E), 8 walk steps (HVA frames 0, 2, 4, 6, 8, 11, 13, 15)."""
import numpy as np
import rc
import rcrender as RR
from hmec2 import STEPS

CANVAS = (576, 576)
PPU = 6.8
ORIGIN = (287.5, 374.0)
ELEV = 35.0


def camera():
    return RR.Cam((0, -1), ELEV, PPU, ORIGIN)


def flat_cam():
    return rc.Cam((0, -1), ELEV, PPU, ORIGIN)


def facing_cw(k, n=32):
    th = 2 * np.pi * k / n
    f = np.array([np.sin(th), -np.cos(th), 0.0]); r = np.array([np.cos(th), np.sin(th), 0.0])
    # unit frame (x forward, y left, z up) -> world (x east, y south, z up)
    return np.stack([f, -r, np.array([0, 0, 1.0])], axis=1)


def mod_to_cw(f, n=32):
    return (n - f) % n


def unit_to_world(facing):
    return facing_cw(mod_to_cw(facing))


def frame_of(k):
    """mod frame k -> (facing, HVA frame)."""
    f, step = divmod(k, 8)
    return f, STEPS[step]
