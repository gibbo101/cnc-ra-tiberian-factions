"""vdeliver spec: the Apocalypse Tank (R2APOC), Red Alert 2's [APOC]."""
import sys
import numpy as np
from paths import HANDOFF
import apocrender as R

NAME = 'r2apoc'
FRAMES = 64
CANVAS = R.CANVAS
INMOD = HANDOFF + '/27-R2APOC/in-mod/r2apoc/frames/r2apoc-%04d.png'
NO_SHADOW = [(32, 63)]
CROP = (40, 50, 408, 306)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
REF = HANDOFF + '/27-R2APOC/reference-hd/RA_4TNK/frames/4tnk-%04d.png'
SHEETS = [('8-facings.png', [('hull %d + turret %d' % (f, 32 + f), [f, 32 + f]) for f in range(0, 32, 4)]),
          ('hull-8-facings.png', [('hull %d' % f, [f]) for f in range(0, 32, 4)]),
          ('turret-8-facings.png', [('turret %d' % (32 + f), [32 + f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [f, 32 + f]) for f in range(32)], 120),
        ('turret-turning.gif', [('hull 24 + turret %d' % (32 + f), [24, 32 + f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ("EA's Mammoth (facing north)", REF, [0, REF.replace('%04d', '0032-0000')], 1.0),
                        ('Apocalypse Tank (HD)', None, [24, 56], 2 / 3)])
SRC = ['apocrender.py', 'apocspec.py', 'apocexport.py']
SHARED_EXTRA = ['ra2normals.py', 'estnormals.py']
load = R.load
frame = R.frame


def GLB(path):
    import vexport as VE
    H, T = R.load()
    VE.export(path, 'ApocalypseTank', [('hull', H, 0), ('turret', T, 0)], R.camera(), R.CANVAS, R.PPU)


def GLB_CHECK(path):
    """the hull alone, for the check against the hull frame (the turret frames are drawn at their own fitted size)."""
    import vexport as VE
    H, T = R.load()
    VE.export(path, 'ApocalypseTank', [('hull', H, 0)], R.camera(), R.CANVAS, R.PPU)


GLB_NAME = 'r2apoc.glb'
GLB_FRAMES = [24]
README = dict(
    title="Apocalypse Tank", ts_name='APOC, Red Alert 2',
    frames="""frames/     r2apoc-0000.png ... r2apoc-0063.png, the mod's 64 frames on its 448 x 448 canvas, each with a -trim.png
            (white = house colour, antialiased):
              0-31    the hull with its shadow, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E)
              32-63   the turret with its twin cannons and tusk launchers (MTNKTUR and MTNKBARL), no shadow, 32 facings, drawn at the hull's canvas centre""",
    previews="""previews/   8-facings.png            hull and turret facing the same way, the mod's frames beside HD
            hull-8-facings.png, turret-8-facings.png   each set on its own, every 4th facing
            turn.gif                 all 32 facings in turn, the mod's frames beside HD
            turret-turning.gif       the turret turning on the hull facing east
            scale.png                next to the HD harvester and EA's Mammoth, as the game draws them""",
    vxl="Red Alert 2's MTNK.VXL, MTNKTUR.VXL, MTNKBARL.VXL, each posed by its own HVA, with RA2's UNITTEM.PAL",
    look="""- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north.  The hull at 5.03 canvas px per
  voxel with the unit's position at canvas (223.66, 223.09), the turret at 4.92 with its pivot at (223.5, 221.32):
  the sizes and places the mod's frames have (found by matching RA2's voxels to them: overlap 0.98 for the hull,
  0.93 for the turret).  RA2's voxels are drawn at RA2's cell size against TS's (0.8 of the TS units' scale), as
  in-mod/ has them.
- RA2's voxels carry RA2's own normals (244 of them, not TS's 36): estimated from the voxels the same way as TS's
  (src/ra2normals.py, src/estnormals.py) and used for the same layer of detail.""",
    extra=[('Fire points', """The model is RA2's voxels exactly (same sections, same places), so the weapon tips you project from RA2's fire
points still land on the cannon and tusk tips: the turret frames keep the mod's size and place.""")],
    judgement="""- The turret at its own fitted size (4.92 px per voxel against the hull's 5.03): the mod's turret frames are
  drawn that much smaller, and the turret frames keep their size and place so your weapon tips still line up.""",
    glb="""r2apoc.glb   the hull and the turret in RA2's own colours, the turret under its own node; the mod's camera
- Nodes: ApocalypseTank > unit_facing_east > hull, turret (at RA2's HVA place and one scale; the mod draws the turret
  frames a little smaller, so the check below draws the hull alone over the hull frame).""",
    src="""  apocrender.py          the frame layout and cameras;  apocspec.py  its frames, previews and README
  apocexport.py          the .glb
    PKG=out python3 vdeliver.py apocspec render 0 1      renders frames/""")
