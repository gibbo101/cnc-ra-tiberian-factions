"""vdeliver spec: the Carryall (TSCARRY) v2, rebuilt as clean parts (cmodel.py, cmat.py, crender.py): its frames,
previews and checks, as v1's."""
import os, sys
from paths import HANDOFF
import crender as R
from ccam import CANVAS

NAME = 'tscarry'
FRAMES = 32
INMOD = HANDOFF + '/25-TSCARRY/in-mod/tscarry/frames/tscarry-%04d.png'
NO_SHADOW = [(0, 31)]
CROP = (24, 40, 424, 330)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
REF = HANDOFF + '/25-TSCARRY/reference-hd/RA_TRAN/frames/tran-%04d.png'
BOMBER = os.environ.get('BOMBER_FRAMES', 'ts-orcab-hd/frames') + '/tsorcab-%04d.png'
SHEETS = [('8-facings.png', [('frame %d' % f, [f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ('Orca Bomber (HD)', BOMBER, [24], 2 / 3),
                        ('Carryall (HD)', None, [24], 2 / 3), ("EA's RA Chinook", REF, [24], 1.0)])


def load():
    return R.model()


def frame(u, k, ss, sky):
    return R.frame(k, ss, sky, m=u)
