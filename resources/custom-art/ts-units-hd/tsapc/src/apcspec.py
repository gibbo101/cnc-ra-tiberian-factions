"""vdeliver spec: the Amphibious APC (TSAPC) v2, rebuilt as clean parts (apcmodel.py, apcmat.py, apcrender.py): its
frames, previews and checks, as v1's (the v1 spec's layout)."""
import sys
from paths import HANDOFF
import apcrender as AR
from apccam import CANVAS

NAME = 'tsapc'
FRAMES = 64
INMOD = HANDOFF + '/06-TSAPC/in-mod/tsapc/frames/tsapc-%04d.png'
NO_SHADOW = [(32, 63)]
CROP = (56, 52, 328, 268)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
EA_APC = HANDOFF + '/06-TSAPC/reference-hd/RA_APC/frames/apc-%04d.png'
SHEETS = [('land-8-facings.png', [('land %d' % f, [f]) for f in range(0, 32, 4)]),
          ('water-8-facings.png', [('water %d' % (32 + f), [32 + f]) for f in range(0, 32, 4)])]
GIFS = [('turn-land.gif', [('land %d' % f, [f]) for f in range(32)], 120),
        ('turn-water.gif', [('water %d' % (32 + f), [32 + f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ("EA's APC (RA)", EA_APC, [24], 1.0),
                        ('Amphibious APC (HD)', None, [24], 2 / 3)])


def load():
    return AR.model()


def frame(u, k, ss, sky):
    return AR.frame(k, ss, sky, m=u)
