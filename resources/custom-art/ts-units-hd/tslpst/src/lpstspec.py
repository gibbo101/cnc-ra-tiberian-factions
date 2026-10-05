"""vdeliver spec: the Mobile Sensor Array (TSLPST) v2, rebuilt as clean parts (lpstmodel.py, lpstmat.py,
lpstrender.py): its frames, previews and checks, as v1's."""
import sys
from paths import HANDOFF
import lpstrender as LR
from lpstcam import CANVAS

NAME = 'tslpst'
FRAMES = 32
INMOD = HANDOFF + '/12-TSLPST/in-mod/tslpst/frames/tslpst-%04d.png'
NO_SHADOW = []
CROP = (56, 52, 328, 300)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
EA_MRJ = HANDOFF + '/12-TSLPST/reference-hd/RA_MRJ/frames/mrj-%04d.png'
SHEETS = [('8-facings.png', [('facing %d' % f, [f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ("EA's Radar Jammer (RA)", EA_MRJ, [24], 1.0),
                        ('Mobile Sensor Array (HD)', None, [24], 2 / 3)])


def load():
    return LR.model()


def frame(u, k, ss, sky):
    return LR.frame(k, ss, sky, m=u)
