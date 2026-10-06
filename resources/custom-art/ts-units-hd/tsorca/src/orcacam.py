"""orcacam.py - the Orca Fighter's canvas, camera and frames, as v1 and the mod have them: 384 x 384, 32 facings
counter-clockwise from north (0 N, 8 W, 16 S, 24 E), no shadow (it flies: the game draws its shadow from the frame).
The RA grid's camera (orthographic, 32 degrees above the ground, looking north) at 6.25 canvas px a voxel, the unit's
position (TS's HVA origin) at canvas (192.0, 191.04): the size and place the mod's frames have (v1's find, by matching
TS's voxel to them: overlap 0.91).  The game draws this canvas at two thirds (8 canvas px per classic pixel)."""
import numpy as np
import rc
import rcrender as RR

CANVAS = (384, 384)
PPU, ORIGIN = 6.25, (192.0, 191.04)
ELEV = 32.0
PX_SCALE = 1.5                       # the outline 1.5 times as wide on the canvas (it is drawn at two thirds)


def camera():
    return RR.Cam((0, -1), ELEV, PPU, ORIGIN)


def flat_cam(origin=ORIGIN, look=(0, -1), elev=ELEV, ppu=PPU):
    return rc.Cam(look, elev, ppu, origin)


def facing_cw(k, n=32):
    th = 2 * np.pi * k / n
    f = np.array([np.sin(th), -np.cos(th), 0.0]); r = np.array([np.cos(th), np.sin(th), 0.0])
    return np.stack([f, -r, np.array([0, 0, 1.0])], axis=1)


def mod_to_cw(f, n=32):
    return (n - f) % n


def unit_to_world(facing):
    return facing_cw(mod_to_cw(facing))
