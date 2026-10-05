"""vdeliver spec: the Disruptor (TSSONIC) v2, rebuilt as clean parts (sonmodel.py, sonmat.py, sonrender.py): its frames,
previews and checks, as v1's, with the turret seated at the back of the hull (Luke: it touches the unit's back)."""
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
TURRET_OFFSET_PX = 88.1          # the turret's ring touching the hull's back (Luke): 14.0 voxels, 0.46 cell, 11 classic px
                                 # (TS's own TurretOffset=-64 is a quarter cell: 48 canvas px)


def seat(f, px=TURRET_OFFSET_PX):
    """the turret frame's shift against the hull's: 14.0 voxels aft of the unit's position along the hull's facing (its
    ring's back on the hull's back), on the ground, so foreshortened as the camera draws the ground (88 px aft facing
    east or west, 47 px north or south)."""
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
