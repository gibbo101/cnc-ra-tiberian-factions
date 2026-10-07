"""vdeliver spec: the Apocalypse Tank (R2APOC) v2, rebuilt as clean parts (apocmodel.py, apocmat.py, apocrender.py): its
frames, previews and checks, as v1's.  The turret frames are drawn at the hull's canvas centre (RA2's turret sits on
the unit's position), so the sheets lay the frames over each other as they are."""
import sys
import numpy as np
from paths import HANDOFF
import apocrender as SR
from apoccam import CANVAS

NAME = 'r2apoc'
FRAMES = 64
INMOD = HANDOFF + '/27-R2APOC/in-mod/r2apoc/frames/r2apoc-%04d.png'
NO_SHADOW = [(32, 63)]
CROP = (40, 50, 408, 306)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
REF = HANDOFF + '/27-R2APOC/reference-hd/RA_4TNK/frames/4tnk-%04d.png'
SHEETS = [('8-facings.png', [('hull %d + turret %d' % (f, 32 + f), [f, 32 + f]) for f in range(0, 32, 4)]),
          ('hull-8-facings.png', [('hull %d' % f, [f]) for f in range(0, 32, 4)]),
          ('turret-8-facings.png', [('turret %d' % (32 + f), [32 + f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [f, 32 + f]) for f in range(32)], 120),
        ('turret-turning.gif', [('hull 24 + turret %d' % (32 + f), [24, 32 + f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0),
                        ("EA's Mammoth (facing north)", REF, [0, REF.replace('%04d', '0032-0000')], 1.0),
                        ('Apocalypse Tank (HD)', None, [24, 56], 2 / 3)])


def load():
    return SR.model()


def frame(u, k, ss, sky):
    return SR.frame(k, ss, sky, m=u)
