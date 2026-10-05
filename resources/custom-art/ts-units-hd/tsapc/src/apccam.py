"""apccam.py - the APC's canvas, camera and frames (as v1 and the mod have them): 384 x 384, the RA grid's camera
(orthographic, 32 degrees above the ground, looking north) at 6.25 canvas px a voxel; the land hull's position at
canvas (191, 190.35), the water hull's at (191.5, 158); frames 0-31 on land (with the shadow), 32-63 on water (none),
32 facings each counter-clockwise from north (0 N, 8 W, 16 S, 24 E)."""
import numpy as np
import rc
import rcrender as RR

CANVAS = (384, 384)
PPU = 6.25
ORIGIN_LAND = (191.0, 190.35)
ORIGIN_WATER = (191.5, 158.0)
ELEV = 32.0


def origin(which):
    return ORIGIN_LAND if which == 'land' else ORIGIN_WATER


def camera(which='land'):
    return RR.Cam((0, -1), ELEV, PPU, origin(which))


def flat_cam(which='land'):
    return rc.Cam((0, -1), ELEV, PPU, origin(which))


def facing_cw(k, n=32):
    th = 2 * np.pi * k / n
    f = np.array([np.sin(th), -np.cos(th), 0.0]); r = np.array([np.cos(th), np.sin(th), 0.0])
    return np.stack([f, -r, np.array([0, 0, 1.0])], axis=1)


def mod_to_cw(f, n=32):
    return (n - f) % n


def unit_to_world(facing):
    return facing_cw(mod_to_cw(facing))


def frame_of(k):
    """mod frame k -> (which hull, facing, with shadow)."""
    if k < 32:
        return 'land', k, True
    return 'water', k - 32, False
