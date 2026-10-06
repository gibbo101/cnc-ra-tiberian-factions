"""vdeliver spec: the Orca Fighter (TSORCA) v2, rebuilt as clean parts (orcamodel.py, orcamat.py, orcarender.py): its
frames, previews and checks, as v1's."""
import sys
from paths import HANDOFF
import orcarender as R
from orcacam import CANVAS

NAME = 'tsorca'
FRAMES = 32
INMOD = HANDOFF + '/23-TSORCA/in-mod/tsorca/frames/tsorca-%04d.png'
NO_SHADOW = [(0, 31)]
CROP = (6, 8, 378, 266)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
REF = HANDOFF + '/23-TSORCA/reference-hd/TD_ORCA/frames/orca-%04d.png'
SHEETS = [('8-facings.png', [('frame %d' % f, [f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ("EA's TD Orca", REF, [24], 1.0),
                        ('Orca Fighter (HD)', None, [24], 2 / 3)])


def load():
    return R.model()


def frame(u, k, ss, sky):
    return R.frame(k, ss, sky, m=u)
