"""vdeliver spec: the Mobile War Factory (TSMWAR) v2, rebuilt as clean parts (mwarmodel.py, mwarmat.py,
mwarrender.py): its frames, previews and checks, as v1's."""
import sys
from paths import HANDOFF
import mwarrender as MR
from mwarcam import CANVAS

NAME = 'tsmwar'
FRAMES = 32
INMOD = HANDOFF + '/14-TSMWAR/in-mod/tsmwar/frames/tsmwar-%04d.png'
NO_SHADOW = []
CROP = (50, 50, 334, 320)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
EA_MCV = HANDOFF + '/14-TSMWAR/reference-hd/RA_MCV/frames/mcv-%04d.png'
SHEETS = [('8-facings.png', [('facing %d' % f, [f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ("EA's MCV (RA)", EA_MCV, [24], 1.0),
                        ('Mobile War Factory (HD)', None, [24], 2 / 3)])


def load():
    return MR.model()


def frame(u, k, ss, sky):
    return MR.frame(k, ss, sky, m=u)
