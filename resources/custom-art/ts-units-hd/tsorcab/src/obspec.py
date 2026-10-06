"""vdeliver spec: the Orca Bomber (TSORCAB) v2, rebuilt as clean parts (obmodel.py, obmat.py, obrender.py): its
frames, previews and checks, as v1's."""
import os, sys
from paths import HANDOFF
import obrender as R
from obcam import CANVAS

NAME = 'tsorcab'
FRAMES = 32
INMOD = HANDOFF + '/24-TSORCAB/in-mod/tsorcab/frames/tsorcab-%04d.png'
NO_SHADOW = [(0, 31)]
CROP = (6, 8, 378, 266)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
REF = HANDOFF + '/24-TSORCAB/reference-hd/RA_HIND/frames/hind-%04d.png'
FIGHTER = os.environ.get('FIGHTER_FRAMES', 'ts-orca-hd/frames') + '/tsorca-%04d.png'
SHEETS = [('8-facings.png', [('frame %d' % f, [f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ('Orca Fighter (HD)', FIGHTER, [24], 2 / 3),
                        ('Orca Bomber (HD)', None, [24], 2 / 3), ("EA's Hind", REF, [24], 1.0)])


def load():
    return R.model()


def frame(u, k, ss, sky):
    return R.frame(k, ss, sky, m=u)
