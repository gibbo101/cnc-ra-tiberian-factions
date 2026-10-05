"""hvrcam.py - the Hover MLRS's canvas, camera and frames (as v1 and the mod have them): 192 x 192 (4 canvas px per
classic pixel: half the other units' density); frames 0-31 the hull without a shadow, 32-63 the missile rack without
one, 64-95 the hull's shadow on its own; 32 facings each counter-clockwise from north (0 N, 8 W, 16 S, 24 E).  The RA
grid's camera (orthographic, 32 degrees above the ground, looking north) at 2.95 canvas px a voxel, the hull's position
(TS's HVA origin) at canvas (95.5, 106) (v1's find, by matching TS's voxels to the mod's frames: overlap 0.95).  Each
rack frame is drawn with its content centred where the mod's rack frame has its content (the mod's seat tables cancel
today's per-frame drift); each shadow frame is the HD hull's silhouette moved 5 px right and 17 px down (it hovers)."""
import numpy as np
import rc
import rcrender as RR

CANVAS = (192, 192)
PPU, ORIGIN = 2.95, (95.5, 106.0)
ELEV = 32.0
PX_SCALE = 0.75                     # the game draws this canvas at 4/3: the outline 0.75 canvas px wide comes out as
                                    # wide in the game as on the other units
SHADOW_SHIFT = (5, 17)
SHADOW_ALPHA = 191


def camera(origin=ORIGIN):
    return RR.Cam((0, -1), ELEV, PPU, origin)


def flat_cam(origin=ORIGIN):
    return rc.Cam((0, -1), ELEV, PPU, origin)


def facing_cw(k, n=32):
    th = 2 * np.pi * k / n
    f = np.array([np.sin(th), -np.cos(th), 0.0]); r = np.array([np.cos(th), np.sin(th), 0.0])
    return np.stack([f, -r, np.array([0, 0, 1.0])], axis=1)


def unit_to_world(facing):
    return facing_cw((32 - facing) % 32)


def frame_of(k):
    """mod frame k -> (sections, facing, kind: 'hull', 'rack' or 'shadow')."""
    if k < 32:
        return ['hull'], k, 'hull'
    if k < 64:
        return ['rack'], k - 32, 'rack'
    return ['hull'], k - 64, 'shadow'
