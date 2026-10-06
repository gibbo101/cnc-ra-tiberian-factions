"""soncam.py - the Disruptor's canvas, cameras and frames (as v1 and the mod have them): 448 x 448; frames 0-31 the hull
with its shadow, 32-63 the turret (its ring and the dish) without one, 32 facings each counter-clockwise from north
(0 N, 8 W, 16 S, 24 E).  The RA grid's camera (orthographic, 32 degrees above the ground, looking north): the hull at
6.27 canvas px a voxel, the unit's position at canvas (222.5, 222.7); the turret at 6.15 px a voxel (the mod draws it
2% smaller), its pivot at (224, 221), so the horn's tip stays where the mod's sonic wave starts (v1's finds, by
matching TS's voxels to the mod's frames).  TS's hull reaches GZ below its HVA origin: it is raised onto the ground
and the hull camera's origin moved to match, so every pixel stays where the mod's frames have it.

v4 drew the whole turret at 0.69 of the hull's scale, shrunk about its base (the turntable's foot, Z_BASE up), so its
ring stayed on the green deck.  v5 draws the turret at the mod's size again (Luke: the dish back to its size, only the
circular pad smaller): K_TUR is the mod's turret scale, and the pad alone is made smaller in the model
(sonmodel.PAD_K).

v5 also seats the turret exactly (Luke: the pad was off-centre side to side and over the deck's right edge): the turret
frames' pivot is drawn where the hull frames' unit position is (origin()), so laid on the hull frame and shifted by
the seat, the turret sits where the 3D model puts it in every facing.  v1-v4 kept the mod's turret camera, its pivot at
(224, 221): 1.5 px right of and 2 px above where it belongs, harmless under TS's big turntable but enough to push the
small pad off-centre.  The pad now stands on the deck (Z_BASE = the deck's top; TS's turntable floats 0.6 voxel above
it)."""
import numpy as np
import rc
import rcrender as RR

CANVAS = (448, 448)
PPU, ORIGIN = 6.27, (222.5, 222.7)
ELEV = 32.0
GZ = -0.24
PPU_T0, ORIGIN_T0 = 6.15, (224.0, 221.0)            # v1-v4's turret camera (the mod's): TS's size, 2% smaller
K_TUR_V4 = 0.69                                     # v4: the whole turret at 0.69 of the hull's scale
K_TUR = PPU_T0 / PPU                                # v5: the turret at the mod's size again (0.98 of the hull's scale)
Z_BASE_TS = 10.08                                   # TS's turntable foot above the ground (voxels; v1-v4's turret base)
Z_BASE = 9.5045                                     # v5: the turret's base (the turntable's foot) on the deck's top
PPU_T = PPU * K_TUR


def origin():
    return (ORIGIN[0], ORIGIN[1] - GZ * PPU * np.cos(np.deg2rad(ELEV)))


# v5: the turret camera's world origin (the pivot on the ground) where the hull camera's is, the turret scaled K_TUR
# about its base (Z_BASE up), so its base is drawn exactly where the hull camera draws that point
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
    return ['ring', 'tur'], k - 32, True
