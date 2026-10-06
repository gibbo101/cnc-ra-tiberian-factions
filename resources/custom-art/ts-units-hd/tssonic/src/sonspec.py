"""vdeliver spec: the Disruptor (TSSONIC) v5, rebuilt as clean parts (sonmodel.py, sonmat.py, sonrender.py): its frames,
previews and checks, as v1's, with the turret's pad on the green rear deck at its back (Luke: it stays on the green, not
over the back or the sides; v5: the dish at its size, only the pad smaller)."""
import sys
import numpy as np
from paths import HANDOFF
import sonrender as SR
from soncam import CANVAS

NAME = 'tssonic'
FRAMES = 64
INMOD = HANDOFF + '/08-TSSONIC/in-mod/tssonic/frames/tssonic-%04d.png'
NO_SHADOW = [(32, 63)]
CROP = (64, 50, 384, 350)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
TURRET_OFFSET_PX = 82.68         # v5: the turret's pad on the deck, as far back as its sides: 0.51 voxel inside the deck's
                                 # back and side edges (Luke: centred, not over the edges): 13.19 voxels, 0.43 cell,
                                 # TurretOffset=-110 (v4: 83.4 px, -111; v3: 88.1 px, its ring's back on the hull's back;
                                 # TS's own TurretOffset=-64 is a quarter cell: 48 canvas px)


def seat(f, px=TURRET_OFFSET_PX):
    """the turret frame's shift against the hull's: 13.19 voxels aft of the unit's position along the hull's facing (its
    pad on the green deck, 0.51 voxel inside its back edge as inside its sides), on the ground, so foreshortened as the
    camera draws the ground (83 px aft facing east or west, 44 px north or south)."""
    th = 2 * np.pi * ((32 - f) % 32) / 32
    v = np.array([np.sin(th), -np.cos(th) * np.sin(np.deg2rad(32.0))])
    return (32 + f, -px * v[0], -px * v[1])


SHEETS = [('8-facings.png', [('hull %d + turret %d' % (f, 32 + f), [f, seat(f)]) for f in range(0, 32, 4)]),
          ('hull-8-facings.png', [('hull %d' % f, [f]) for f in range(0, 32, 4)]),
          ('turret-8-facings.png', [('turret %d' % (32 + f), [32 + f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [f, seat(f)]) for f in range(32)], 120),
        ('turn-hull.gif', [('hull %d' % f, [f]) for f in range(32)], 120),
        ('turn-turret.gif', [('turret %d' % (32 + f), [32 + f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ('Disruptor (HD)', None, [24, seat(24)], 2 / 3)])


def load():
    return SR.model()


def frame(u, k, ss, sky):
    return SR.frame(k, ss, sky, m=u)
