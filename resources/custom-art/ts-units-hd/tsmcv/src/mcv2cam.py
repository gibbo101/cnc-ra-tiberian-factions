"""mcv2cam.py - the MCV's canvas, camera and facings (as v1 and the mod have them): 384 x 384, the RA grid's camera
(orthographic, 32 degrees above the ground, looking north) at 6.1 canvas px a voxel, the unit's position (the HVA
origin, on the ground) at canvas (192, 194); 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E)."""
import numpy as np
import rc
import rcrender as RR

CANVAS = (384, 384)
PPU = 6.1
ORIGIN = (192.0, 194.0)


def camera():
    return RR.ra_cam(PPU, ORIGIN)


def inmod_cam():
    """the camera of the mod's current frames (Luke's voxel render): TS's 30 degrees at the same size and place."""
    return rc.Cam((0, -1), 30.0, PPU, ORIGIN)


def facing_cw(k, n=32):
    th = 2 * np.pi * k / n
    f = np.array([np.sin(th), -np.cos(th), 0.0]); r = np.array([np.cos(th), np.sin(th), 0.0])
    return np.stack([f, r, np.array([0, 0, 1.0])], axis=1)


def mod_to_cw(f, n=32):
    return (n - f) % n


def body_to_world(f):
    """the rotation taking the body frame (u forward, v right, w up) to the world for mod frame f."""
    return facing_cw(mod_to_cw(f))
