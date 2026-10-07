"""vdeliver spec: the Prism Tank (R2PRIS) v2, rebuilt as clean parts (prismodel.py, prismat.py, prisrender.py): its frames,
previews and checks, as v1's.  The turret frames are drawn at the hull's canvas centre (RA2's turret sits on the unit's
position), so the sheets lay the frames over each other as they are."""
import sys
import numpy as np
from paths import HANDOFF
import prisrender as SR
from priscam import CANVAS

NAME = 'r2pris'
FRAMES = 64
INMOD = HANDOFF + '/28-R2PRIS/in-mod/r2pris/frames/r2pris-%04d.png'
NO_SHADOW = [(32, 63)]
CROP = (20, 10, 366, 272)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
REF = HANDOFF + '/28-R2PRIS/reference-hd/RA_2TNK/frames/2tnk-%04d.png'
SHEETS = [('8-facings.png', [('hull %d + turret %d' % (f, 32 + f), [f, 32 + f]) for f in range(0, 32, 4)]),
          ('hull-8-facings.png', [('hull %d' % f, [f]) for f in range(0, 32, 4)]),
          ('turret-8-facings.png', [('turret %d' % (32 + f), [32 + f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [f, 32 + f]) for f in range(32)], 120),
        ('turret-turning.gif', [('hull 24 + turret %d' % (32 + f), [24, 32 + f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ("EA's medium tank", REF, [24, 56], 1.0),
                        ('Prism Tank (HD)', None, [24, 56], 2 / 3)])


def load():
    return SR.model()


def frame(u, k, ss, sky):
    return SR.frame(k, ss, sky, m=u)
