"""vdeliver spec: the Orca Transport (TSORCATRAN) v2, rebuilt as clean parts (otmodel.py, otmat.py, otrender.py): its
frames, previews and checks, on v1's canvas.  The mod has no frames of it yet, so the previews' left column is TS's
voxel drawn in the mod's camera (ref/, as v1's)."""
import os, sys
from paths import HANDOFF, HERE
import otrender as R
from otcam import CANVAS

NAME = 'tsorcatran'
FRAMES = 32
INMOD = os.path.join(HERE, 'ref', 'tsorcatran-%04d.png')
INMOD_LABEL = "TS's voxels"
NO_SHADOW = [(0, 31)]
CROP = (10, 60, 486, 380)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
REF = HANDOFF + '/25-TSCARRY/reference-hd/RA_TRAN/frames/tran-%04d.png'
ORCA = os.environ.get('ORCA_FRAMES', 'ts-orca-hd/frames') + '/tsorca-%04d.png'
CARRY = os.environ.get('CARRY_FRAMES', 'ts-carry-hd/frames') + '/tscarry-%04d.png'
SHEETS = [('8-facings.png', [('facing %d' % f, [f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ('Orca Fighter (HD)', ORCA, [24], 2 / 3),
                        ('Orca Transport (HD)', None, [24], 2 / 3), ('Carryall (HD)', CARRY, [24], 2 / 3),
                        ("EA's RA Chinook", REF, [24], 1.0)])


def load():
    return R.model()


def frame(u, k, ss, sky):
    return R.frame(k, ss, sky, m=u)
