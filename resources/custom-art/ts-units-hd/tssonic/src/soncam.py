"""soncam.py - the Disruptor's canvas, cameras and frames (as v1 and the mod have them): 448 x 448; frames 0-31 the hull
with its shadow, 32-63 the turret (its ring and the dish) without one, 32 facings each counter-clockwise from north
(0 N, 8 W, 16 S, 24 E).  The RA grid's camera (orthographic, 32 degrees above the ground, looking north): the hull at
6.27 canvas px a voxel, the unit's position at canvas (222.5, 222.7); the turret at 6.15 px a voxel (the mod draws it
2% smaller), its pivot at (224, 221), so the horn's tip stays where the mod's sonic wave starts (v1's finds, by
matching TS's voxels to the mod's frames).  TS's hull reaches GZ below its HVA origin: it is raised onto the ground
and the hull camera's origin moved to match, so every pixel stays where the mod's frames have it."""
import numpy as np
import rc
import rcrender as RR

CANVAS = (448, 448)
PPU, ORIGIN = 6.27, (222.5, 222.7)
PPU_T, ORIGIN_T = 6.15, (224.0, 221.0)
ELEV = 32.0
GZ = -0.24


def origin():
    return (ORIGIN[0], ORIGIN[1] - GZ * PPU * np.cos(np.deg2rad(ELEV)))


def camera(turret=False):
    return RR.Cam((0, -1), ELEV, PPU_T, ORIGIN_T) if turret else RR.Cam((0, -1), ELEV, PPU, origin())


def flat_cam(turret=False):
    return rc.Cam((0, -1), ELEV, PPU_T, ORIGIN_T) if turret else rc.Cam((0, -1), ELEV, PPU, origin())


def facing_cw(k, n=32):
    th = 2 * np.pi * k / n
    f = np.array([np.sin(th), -np.cos(th), 0.0]); r = np.array([np.cos(th), np.sin(th), 0.0])
    return np.stack([f, -r, np.array([0, 0, 1.0])], axis=1)


def mod_to_cw(f, n=32):
    return (n - f) % n


def unit_to_world(facing):
    return facing_cw(mod_to_cw(facing))


def frame_of(k):
    """mod frame k -> (sections, facing, turret camera / no shadow)."""
    if k < 32:
        return ['hull'], k, False
    return ['ring', 'tur'], k - 32, True
