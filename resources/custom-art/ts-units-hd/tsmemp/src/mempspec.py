"""vdeliver spec: the Mobile EMP Cannon (TSMEMP) v2, rebuilt as clean parts (mempmodel.py, mempmat.py, memprender.py):
its frames, previews and checks, as v1's (the blast, fx/, is v1's: mempfx.py there)."""
import sys
from paths import HANDOFF
import memprender as R
from mempcam import CANVAS, LOW_PX

NAME = 'tsmemp'
FRAMES = 32
INMOD = HANDOFF + '/13-TSMEMP/in-mod/tsmemp/frames/tsmemp-%04d.png'
NO_SHADOW = []
# the HD frames stand on the ground, LOW_PX lower than in-mod/'s float: the check moves in-mod/ down by as much
CHECK_SHIFT = (0, int(round(LOW_PX)))
CROP = (50, 50, 334, 320)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
REF = HANDOFF + '/13-TSMEMP/reference-hd/RA_QTNK/frames/qtnk-%04d.png'
SHEETS = [('8-facings.png', [('frame %d' % f, [f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ("EA's M.A.D. Tank", REF, [24], 1.0),
                        ('Mobile EMP Cannon (HD)', None, [24], 2 / 3)])


def load():
    return R.model()


def frame(u, k, ss, sky):
    return R.frame(k, ss, sky, m=u)
