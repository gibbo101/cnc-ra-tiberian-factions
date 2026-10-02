"""vdeliver spec: the Disruptor (TSSONIC)."""
import sys
from paths import HANDOFF
import sonicrender as R

NAME = 'tssonic'
FRAMES = 64
CANVAS = R.CANVAS
INMOD = HANDOFF + '/08-TSSONIC/in-mod/tssonic/frames/tssonic-%04d.png'
NO_SHADOW = [(32, 63)]
CROP = (64, 50, 384, 350)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
import numpy as np


def seat(f, px=6.0):
    """the turret frame's shift: 6 px aft of centre along the hull's facing, as the mod draws it."""
    th = 2 * np.pi * ((32 - f) % 32) / 32
    v = np.array([np.sin(th), -np.cos(th) * np.sin(np.deg2rad(32.0))])
    v = v / np.linalg.norm(v)
    return (32 + f, -px * v[0], -px * v[1])


SHEETS = [('8-facings.png', [('hull %d + turret %d' % (f, 32 + f), [f, seat(f)]) for f in range(0, 32, 4)]),
          ('hull-8-facings.png', [('hull %d' % f, [f]) for f in range(0, 32, 4)]),
          ('turret-8-facings.png', [('turret %d' % (32 + f), [32 + f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [f, seat(f)]) for f in range(32)], 120),
        ('turn-hull.gif', [('hull %d' % f, [f]) for f in range(32)], 120),
        ('turn-turret.gif', [('turret %d' % (32 + f), [32 + f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ('Disruptor (HD)', None, [24, seat(24)], 2 / 3)])
SRC = ['sonicrender.py', 'sonicspec.py', 'sonicexport.py']
load = R.load
frame = R.frame


def GLB(path):
    import vexport as VE
    H, T = R.load()
    # the turret seated where the mod draws it: 6 px aft of the hull's centre (6 / 6.27 voxels)
    T.extra_pose = [(np.eye(3), np.array([-6.0 / R.PPU, 0.0, 0.0]))] * len(T.sections)
    VE.export(path, 'Disruptor', [('hull', H, 0), ('turret', T, 0)], R.camera(), R.CANVAS, R.PPU)


GLB_NAME = 'tssonic.glb'
GLB_FRAMES = [24, seat(24)]
README = dict(
    title='Disruptor', ts_name='SONIC',
    frames="""frames/     tssonic-0000.png ... tssonic-0063.png, the mod's 64 frames on its 448 x 448 canvas, each with a -trim.png
            (white = house colour, antialiased):
              0-31    the hull with its shadow, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E)
              32-63   the turret (TS's two turret sections), no shadow, 32 facings, its pivot where in-mod/ has it
                      (the mod draws it 6 px aft of centre along the hull's facing)""",
    previews="""previews/   8-facings.png            the assembled unit (the turret 6 px aft, as the mod draws it), the mod's frames
                                     beside HD
            hull-8-facings.png, turret-8-facings.png   each set on its own, every 4th facing
            turn.gif, turn-hull.gif, turn-turret.gif   all 32 facings in turn, the mod's frames beside HD
            scale.png                next to the HD harvester, as the game draws them""",
    vxl="SONIC.VXL and SONICTUR.VXL, each posed by its own HVA (SONICTUR.HVA seats the turret)",
    look="""- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north.  Where the mod's frames have
  them (found by matching TS's voxels to them): the hull at 6.27 canvas px per voxel with the unit's position at
  canvas (222.5, 222.7) (overlap 0.98); the turret at 6.15 px per voxel with its pivot at (224, 221) (overlap 0.94),
  so the horn's tip stays where the sonic wave starts.""",
    extra=[('Fire point', """The turret is TS's voxels exactly, at in-mod/'s size and place, so the horn's tip (PrimaryFireFLH=0,0,150) is
where it is now.""")],
    judgement="""- The turret drawn 2% smaller than the hull, as in-mod/ draws it (TS draws both at one scale), so the horn's tip
  stays where the mod's sonic wave starts.""",
    glb="""tssonic.glb  the hull and the turret in TS's own colours, the turret under its own node; the mod's camera
- Nodes: Disruptor > unit_facing_east > hull, turret (its two sections), the turret seated 6 px aft as the mod draws
  it.  (The .glb keeps TS's single scale.)""",
    src="""  sonicrender.py         the frame layout and cameras;  sonicspec.py  its frames, previews and README
  sonicexport.py         the .glb
    PKG=out python3 vdeliver.py sonicspec render 0 1      renders frames/""")
