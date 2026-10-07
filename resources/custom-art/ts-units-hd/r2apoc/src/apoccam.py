"""apoccam.py - the Apocalypse's canvas, cameras and frames (as v1 and the mod have them): 448 x 448; frames 0-31 the
hull with its shadow, 32-63 the turret (with its barrels and tusk pods) without one, 32 facings each counter-clockwise
from north (0 N, 8 W, 16 S, 24 E).  The RA grid's camera (orthographic, 32 degrees above the ground, looking north): the
hull at 5.03 canvas px per voxel unit, the unit's position at canvas (223.66, 223.09); the mod draws the turret 2%
smaller (4.92) - v1's finds, by matching RA2's voxels to the mod's frames.  MTNK reaches GZ below its HVA origin: the
whole unit (hull and turret, which RA2 places in one frame) is lowered onto the ground and the hull camera's origin
moved to match, so every hull pixel stays where the mod's frames have it.  The turret is drawn at the mod's size about
its base (its foot on the deck, Z_BASE up), its pivot where the hull frames put the unit's position, so laid on the
hull frame it sits on the deck exactly (the mod's turret pivot is 0.2 px left of and 0.7 px above that)."""
import numpy as np
import rc
import rcrender as RR

CANVAS = (448, 448)
PPU, ORIGIN = 5.03, (223.66, 223.09)
ELEV = 32.0
GZ = 0.34                                           # MTNK's lowest voxels above its HVA origin
PPU_T0, ORIGIN_T0 = 4.92, (223.5, 221.32)           # the mod's turret camera (v1's fit)
K_TUR = PPU_T0 / PPU
PPU_T = PPU * K_TUR
Z_BASE = 11.61 - GZ                                 # the turret's foot (MTNKTUR's min z), lowered with the hull: the deck


def origin():
    return (ORIGIN[0], ORIGIN[1] - GZ * PPU * np.cos(np.deg2rad(ELEV)))


ORIGIN_T = (origin()[0], origin()[1] - Z_BASE * np.cos(np.deg2rad(ELEV)) * (PPU - PPU_T))


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
    return ['tur', 'barl'], k - 32, True
