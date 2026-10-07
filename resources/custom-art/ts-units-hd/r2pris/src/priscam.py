"""priscam.py - the Prism Tank's canvas, cameras and frames (as v1 and the mod have them): 384 x 384; frames 0-31 the
hull with its shadow, 32-63 the prism turret without one, 32 facings each counter-clockwise from north (0 N, 8 W, 16 S,
24 E).  The RA grid's camera (orthographic, 32 degrees above the ground, looking north): the hull at 5.03 canvas px per
voxel unit, the unit's position at canvas (191.5, 191.02); the mod draws the turret 2.6% smaller (4.9) - v1's finds, by
matching RA2's voxels to the mod's frames.  SREF reaches 0.18 below its HVA origin: the whole unit (hull and turret, one
frame in RA2) is raised onto the ground and the hull camera's origin moved to match, so every hull pixel stays where the
mod's frames have it.  The turret is drawn at the mod's size about its base (its post's foot, Z_BASE up), its pivot
where the hull frames put the unit's position, and as high as the mod's frames draw it (TUR_LIFT above RA2's HVA place:
the post's foot is hidden in the ring either way), so laid on the hull frame it stands in its ring as the 3D model has it."""
import numpy as np
import rc
import rcrender as RR

CANVAS = (384, 384)
PPU, ORIGIN = 5.03, (191.5, 191.02)
ELEV = 32.0
GZ = -0.18                                          # SREF's lowest voxels against its HVA origin
PPU_T0, ORIGIN_T0 = 4.9, (191.5, 185.96)            # the mod's turret camera (v1's fit)
K_TUR = PPU_T0 / PPU
PPU_T = PPU * K_TUR
_CE = np.cos(np.deg2rad(ELEV))
# the mod draws the turret 0.82 unit higher than RA2's HVA puts it (its post's foot, hidden in the ring either way): the
# prism's head keeps the height the mod's frames give it (v1's turret camera), so the turret is lifted that much
_OY = ORIGIN[1] - GZ * PPU * _CE
TUR_LIFT = (_OY - ORIGIN_T0[1] + 14.96 * PPU_T0 * _CE) / (_CE * PPU) - (14.96 - GZ)
Z_BASE = 14.96 - GZ + TUR_LIFT                      # the turret's foot (SREFTUR's min z), raised with the hull and lifted


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
    return ['tur'], k - 32, True
