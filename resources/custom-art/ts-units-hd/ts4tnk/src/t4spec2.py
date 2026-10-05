"""vdeliver spec: the Mammoth Mk. I (TS4TNK) v2, rebuilt as clean parts (t4v2.py, t4mat.py, t4render.py): its
frames, previews and checks, as v1's (t4spec.py)."""
import sys
from paths import HANDOFF
import t4render as TR
from t4cam import CANVAS

NAME = 'ts4tnk'
FRAMES = 64
INMOD = HANDOFF + '/05-TS4TNK/in-mod/ts4tnk/frames/ts4tnk-%04d.png'
NO_SHADOW = [(32, 63)]
CROP = (96, 80, 416, 400)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
MAMMOTH = HANDOFF + '/05-TS4TNK/reference-hd/RA_4TNK/frames/4tnk-%04d.png'
SHEETS = [('8-facings.png', [('hull %d + turret %d' % (f, 32 + f), [f, 32 + f]) for f in range(0, 32, 4)]),
          ('hull-8-facings.png', [('hull %d' % f, [f]) for f in range(0, 32, 4)]),
          ('turret-8-facings.png', [('turret %d' % (32 + f), [32 + f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [f, 32 + f]) for f in range(32)], 120),
        ('turret-turning.gif', [('hull 24 + turret %d' % (32 + f), [24, 32 + f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0),
                        ("EA's Mammoth (facing north)", MAMMOTH, [0, MAMMOTH.replace('%04d', '0032-0000')], 1.0),
                        ('Mammoth Mk. I (HD)', None, [24, 56], 2 / 3)])


def load():
    return TR.model()


def frame(u, k, ss, sky):
    return TR.frame(k, ss, sky, m=u)
