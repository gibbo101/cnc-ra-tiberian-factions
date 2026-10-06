"""dshpcam.py - the TS Dropship's canvas and camera (as v1 and the mod have them): 656 x 656 at EA's density (the game
draws it 1:1); frame 0 the ship side-on and level, facing west.  The RA grid's camera (orthographic, 32 degrees above the
ground, looking north) at 6.33 canvas px a voxel, the unit's position (TS's HVA origin) at canvas (279.44, 326.77): v1's
find, by matching TS's voxels to the mod's frame 0 (overlap 0.98), which puts the voxel's own origin on the canvas
centre (TS's HVA origin is 7.7 voxels ahead of it).  The 32 facings (0 N, 8 W, 16 S, 24 E, counter-clockwise from north)
turn the ship about the canvas centre, so facing 8 is frame 0."""
import numpy as np
import rc
import rcrender as RR

CANVAS = (656, 656)
PPU, ORIGIN = 6.33, (279.44, 326.77)
ELEV = 32.0
PX_SCALE = 1.0                       # EA's density: the outline as wide as on the buildings
FRAME0_FACING = 8


def facing_cw(k, n=32):
    th = 2 * np.pi * k / n
    f = np.array([np.sin(th), -np.cos(th), 0.0]); r = np.array([np.cos(th), np.sin(th), 0.0])
    return np.stack([f, -r, np.array([0, 0, 1.0])], axis=1)


def unit_to_world(facing):
    return facing_cw((32 - facing) % 32)


def origin_for(facing):
    """where the unit's position goes on the canvas at this facing: the ship turns about the vertical through the canvas
    centre (frame 0 has the voxel's own origin there, 7.7 voxels behind the HVA origin), so facing 8 is frame 0."""
    if facing % 32 == FRAME0_FACING:
        return ORIGIN
    ax = (CANVAS[0] / 2 - ORIGIN[0]) / PPU
    th = 2 * np.pi * facing / 32
    fwd = np.array([-np.sin(th), -np.cos(th)])
    p = np.array([ax, 0.0]) + ax * fwd
    sE = np.sin(np.deg2rad(ELEV))
    return (ORIGIN[0] + PPU * p[0], ORIGIN[1] + PPU * sE * p[1])


def camera(origin=ORIGIN):
    return RR.Cam((0, -1), ELEV, PPU, origin)


def flat_cam(origin=ORIGIN, look=(0, -1), elev=ELEV, ppu=PPU):
    return rc.Cam(look, elev, ppu, origin)
