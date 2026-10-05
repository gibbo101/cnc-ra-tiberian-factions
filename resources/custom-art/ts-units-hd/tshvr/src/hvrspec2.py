"""vdeliver spec: the Hover MLRS (TSHVR) v2, rebuilt as clean parts (hvrmodel.py, hvrmat.py, hvrrender.py): its frames,
previews and checks.  The rack is drawn seated on the hull's pad (hvrseat.py: Luke, pivot fixed) in the HD previews;
the mod's own frames are laid over each other as they lie on their canvas (the engine's seat tables not applied)."""
import sys
import numpy as np
from paths import HANDOFF
import hvrrender as HR
import hvrseat as HS
from hvrcam import CANVAS

NAME = 'tshvr'
FRAMES = 96
INMOD = HANDOFF + '/07-TSHVR/in-mod/tshvr/frames/tshvr-%04d.png'
NO_SHADOW = [(0, 63)]
CROP = (16, 6, 176, 176)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'


def seat(f):
    return HS.seat(f)


def unit(f, seated=True):
    """shadow, hull and rack laid over each other: the rack seated on the pad (HD) or as it lies (the mod's frames)."""
    return [64 + f, f, seat(f) if seated else 32 + f]


SHEETS = [('hull-8-facings.png', [('hull %d' % f, [f]) for f in range(0, 32, 4)]),
          ('rack-8-facings.png', [('rack %d' % (32 + f), [32 + f]) for f in range(0, 32, 4)]),
          ('shadow-8-facings.png', [('shadow %d' % (64 + f), [64 + f]) for f in range(0, 32, 4)])]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ('Hover MLRS (HD)', None, unit(24), 4 / 3)])


def load():
    return HR.model()


def frame(u, k, ss, sky):
    return HR.frame(k, ss, sky, m=u)
