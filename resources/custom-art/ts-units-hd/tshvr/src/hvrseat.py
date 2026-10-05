"""hvrseat.py - where the game seats the rack (Luke: pivot fixed).  Every rack frame is drawn with the rack's pivot (the
support's and the pods' middle) standing on the unit's position on the hull's canvas, so the rack turns about it frame
by frame.  The pad it turns on is the hull's (hvrmodel.pad()): its centre is SEAT_U in the unit's frame, 12.54 voxels aft
of the unit's position along the hull's facing and 0.20 voxels to its left (TS's hull runs 0.2 voxels left of its HVA
origin; the rack is centred across the hull, Luke).  So the game draws rack frame 32 + g shifted by seat(f) for the
hull's facing f, whatever g is: on the ground, so foreshortened as the camera draws the ground - 37.0 canvas px aft
(9.2 classic px) when the hull faces east or west, 19.6 px (4.9 classic px) north or south; in TS's terms about
TurretOffset=-99 (TS's own -64), with the 0.2 voxels to the left on top.
    python3 hvrseat.py        the shift per facing (canvas px and classic px)"""
import numpy as np
import hvrmodel as T
from hvrcam import PPU, ELEV, unit_to_world

SIN = np.sin(np.deg2rad(ELEV))


def shift_of(f, u):
    """a point u (x forward, y left, on the ground) of the unit's frame, the hull facing f: its shift on the canvas."""
    w = unit_to_world(f) @ np.array([u[0], u[1], 0.0])            # world: x east, y south
    return w[0] * PPU, w[1] * SIN * PPU


def seat(f):
    """(rack frame, dx, dy): rack frame 32 + f's shift on the hull's canvas when the hull faces f (for any rack facing g,
    the shift is the hull's: seat(f)[1:])."""
    dx, dy = shift_of(f, T.SEAT_U)
    return (32 + f, dx, dy)


if __name__ == '__main__':
    print('pad centre %.2f voxels aft, %.2f left; E/W %.1f canvas px aft, N/S %.1f; TurretOffset about %d leptons'
          % (-T.SEAT_U[0], T.SEAT_U[1], -T.SEAT_U[0] * PPU, -T.SEAT_U[0] * PPU * SIN, round(T.SEAT_U[0] * 64 / 8.14)))
    for f in range(32):
        k, dx, dy = seat(f)
        print('facing %2d  dx %+6.2f dy %+6.2f canvas px   (%+5.2f, %+5.2f classic px)' % (f, dx, dy, dx / 4, dy / 4))
