"""vdeliver spec: the Devil's Tongue (TSSUBTANK)."""
import sys
from paths import HANDOFF
import subrender as R

NAME = 'tssubtank'
FRAMES = 113
CANVAS = R.CANVAS
INMOD = HANDOFF + '/09-TSSUBTANK/in-mod/tssubtank/frames/tssubtank-%04d.png'
NO_SHADOW = [(32, 112)]
CROP = (24, 20, 360, 340)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
SHEETS = [('8-driving-facings.png', [('driving %d' % f, [f]) for f in range(0, 32, 4)]),
          ('dive-east.png', [('dive %d' % (32 + 6 * 5 + s), [32 + 6 * 5 + s]) for s in range(5)] +
                            [('emerge %d' % (72 + 6 * 5 + s), [72 + 6 * 5 + s]) for s in range(5)])]
GIFS = [('dive-east.gif', [('driving 24', [24])] + [('dive %d' % (62 + s), [62 + s]) for s in range(5)], 260),
        ('emerge-south.gif', [('emerge %d' % (92 + s), [92 + s]) for s in range(5)] + [('driving 16', [16])], 260),
        ('dive-southwest.gif', [('driving 12', [12])] + [('dive %d' % (47 + s), [47 + s]) for s in range(5)], 260),
        ('turn.gif', [('driving %d' % f, [f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ("Devil's Tongue (HD)", None, [24], 2 / 3)])
SRC = ['subrender.py', 'subspec.py']
load = R.load
frame = R.frame


def GLB(path):
    import vexport as VE
    VE.export(path, 'DevilsTongue', [('hull', R.load(), 0)], R.camera(), R.CANVAS, R.PPU)


GLB_NAME = 'tssubtank.glb'
GLB_FRAMES = [24]
README = dict(
    title="Devil's Tongue", ts_name='SUBTANK',
    frames="""frames/     tssubtank-0000.png ... tssubtank-0112.png, the mod's 113 frames on its 384 x 384 canvas, each
            with a -trim.png (white = house colour, antialiased):
              0-31     driving, with its shadow, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E)
              32-71    diving: 8 facings x 5 steps (frame = 32 + facing x 5 + step; facing 0 N, 1 NW ... 7 NE, each
                       facing the driving frame facing x 4), nose pitched down 8, 16, 24, 32, 40 degrees; no shadow
              72-111   emerging: the same, nose pitched up 40, 32, 24, 16, 8 degrees; no shadow
              112      the disturbed-earth marker, the mod's own (already smooth), as it is""",
    previews="""previews/   8-driving-facings.png    the mod's frames beside HD, every 4th facing
            dive-east.png            the dive and the emerge facing east, step by step
            dive-east.gif, dive-southwest.gif, emerge-south.gif   a dive and an emerge, the mod's frames beside HD
            turn.gif                 the 32 driving facings in turn
            scale.png                next to the HD harvester, as the game draws them""",
    vxl="SUBTANK.VXL, posed by its HVA",
    look="""- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.256 canvas px per voxel, the
  unit's position (TS's HVA origin) at canvas (192.0, 190.8): the size, place and ground line the mod's frames have
  (found by matching TS's voxels to them).  The dive and emerge frames pitch the model about the unit's position on
  the ground, as the mod's frames do (the same match on the dive frames: overlap 0.97).""",
    extra=[('Fire point', """The model is TS's voxels exactly, so PrimaryFireFLH=128,0,40 still points at the flame nozzles.""")],
    judgement="""- The marker (frame 112) kept as the mod draws it: it is already a smooth drawing, not TS art.""",
    glb="""tssubtank.glb   the model in TS's own colours, with the mod's camera
- Nodes: DevilsTongue > unit_facing_east > hull.  (The dive and emerge are the same model pitched about its position.)""",
    src="""  subrender.py          the frame layout (driving, dive, emerge, marker) and camera;  subspec.py  previews, README
    PKG=out python3 vdeliver.py subspec render 0 1      renders frames/""")
