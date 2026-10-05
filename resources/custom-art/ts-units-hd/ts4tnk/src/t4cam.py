"""t4cam.py - the Mk. I's canvas, camera and frames (as v1 and the mod have them): 512 x 512, the RA grid's camera
(orthographic, 32 degrees above the ground, looking north) at 6.23 canvas px a voxel, the unit's position at canvas
(255.5, 254.7); frames 0-31 the hull, 32-63 the turret with its barrels, 32 facings each counter-clockwise from north
(0 N, 8 W, 16 S, 24 E).  The model is lowered by GZ onto the ground (TS's hull floats over its HVA origin) and the
camera's origin raised to match, so every pixel stays where the mod's frames have it."""
import numpy as np
import rc
import rcrender as RR
from t4v2 import GZ

CANVAS = (512, 512)
PPU = 6.23
ORIGIN = (255.5, 254.7)
ELEV = 32.0


def origin():
    return (ORIGIN[0], ORIGIN[1] - GZ * PPU * np.cos(np.deg2rad(ELEV)))


def camera():
    return RR.Cam((0, -1), ELEV, PPU, origin())


def flat_cam():
    return rc.Cam((0, -1), ELEV, PPU, origin())


def facing_cw(k, n=32):
    th = 2 * np.pi * k / n
    f = np.array([np.sin(th), -np.cos(th), 0.0]); r = np.array([np.cos(th), np.sin(th), 0.0])
    return np.stack([f, -r, np.array([0, 0, 1.0])], axis=1)


def mod_to_cw(f, n=32):
    return (n - f) % n


def unit_to_world(facing):
    return facing_cw(mod_to_cw(facing))


def frame_of(k):
    """mod frame k -> (which sections, facing, with shadow)."""
    if k < 32:
        return ['hull'], k, True
    return ['tur', 'barl'], k - 32, False
