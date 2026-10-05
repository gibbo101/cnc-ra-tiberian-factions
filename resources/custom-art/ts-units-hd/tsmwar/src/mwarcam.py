"""mwarcam.py - the Mobile War Factory's canvas, camera and frames (as v1 and the mod have them): 384 x 384, the RA
grid's camera (orthographic, 32 degrees above the ground, looking north) at 6.26 canvas px a voxel, the unit's position
(TS's HVA origin) at canvas (191.65, 190.24); 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E), each with
its shadow.  TS's voxel sits GZ above its HVA origin: the model is lowered onto the ground and the camera's origin
raised to match, so every pixel stays where the mod's frames have it and the shadow meets the wheels (v1's)."""
import numpy as np
import rc
import rcrender as RR

CANVAS = (384, 384)
PPU = 6.26
ORIGIN = (191.65, 190.24)
ELEV = 32.0
GZ = 1.04
CAM_ORIGIN = (ORIGIN[0], ORIGIN[1] - GZ * PPU * np.cos(np.deg2rad(ELEV)))


def camera():
    return RR.Cam((0, -1), ELEV, PPU, CAM_ORIGIN)


def flat_cam():
    return rc.Cam((0, -1), ELEV, PPU, CAM_ORIGIN)


def facing_cw(k, n=32):
    th = 2 * np.pi * k / n
    f = np.array([np.sin(th), -np.cos(th), 0.0]); r = np.array([np.cos(th), np.sin(th), 0.0])
    return np.stack([f, -r, np.array([0, 0, 1.0])], axis=1)


def mod_to_cw(f, n=32):
    return (n - f) % n


def unit_to_world(facing):
    return facing_cw(mod_to_cw(facing))
