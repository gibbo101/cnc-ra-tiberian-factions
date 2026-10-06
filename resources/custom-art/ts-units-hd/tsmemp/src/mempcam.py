"""mempcam.py - the Mobile EMP Cannon's canvas, camera and frames, as v1 and the mod have them: 384 x 384, 32 facings
counter-clockwise from north (0 N, 8 W, 16 S, 24 E), with the unit's shadow.  The RA grid's camera (orthographic, 32
degrees above the ground, looking north) at 6.26 canvas px a voxel, the unit's position (TS's HVA origin) at canvas
(191.0, 190.82): the size and place the mod's frames have (v1's find, by matching TS's voxel to them).  TS's voxel
floats, its lowest voxel GZ = 4.29 voxels above its HVA origin: the model is lowered onto the ground at the unit's
position (as v1), so the frames draw it LOW_PX canvas px lower than in-mod/ (its size and x are in-mod/'s)."""
import numpy as np
import rc
import rcrender as RR

CANVAS = (384, 384)
PPU, ORIGIN = 6.26, (191.0, 190.82)
ELEV = 32.0
GZ = 4.29
LOW_PX = GZ * PPU * np.cos(np.deg2rad(ELEV))


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
