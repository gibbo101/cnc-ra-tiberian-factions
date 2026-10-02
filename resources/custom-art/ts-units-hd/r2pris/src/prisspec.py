"""vdeliver spec: the Prism Tank (R2PRIS), Red Alert 2's [SREF]."""
import sys
import numpy as np
from paths import HANDOFF
import prisrender as R

NAME = 'r2pris'
FRAMES = 64
CANVAS = R.CANVAS
INMOD = HANDOFF + '/28-R2PRIS/in-mod/r2pris/frames/r2pris-%04d.png'
NO_SHADOW = [(32, 63)]
CROP = (20, 10, 366, 272)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
REF = HANDOFF + '/28-R2PRIS/reference-hd/RA_2TNK/frames/2tnk-%04d.png'
SHEETS = [('8-facings.png', [('hull %d + turret %d' % (f, 32 + f), [f, 32 + f]) for f in range(0, 32, 4)]),
          ('hull-8-facings.png', [('hull %d' % f, [f]) for f in range(0, 32, 4)]),
          ('turret-8-facings.png', [('turret %d' % (32 + f), [32 + f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [f, 32 + f]) for f in range(32)], 120),
        ('turret-turning.gif', [('hull 24 + turret %d' % (32 + f), [24, 32 + f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ("EA's medium tank", REF, [24, 56], 1.0),
                        ('Prism Tank (HD)', None, [24, 56], 2 / 3)])
SRC = ['prisrender.py', 'prisspec.py', 'prisexport.py']
SHARED_EXTRA = ['ra2normals.py', 'estnormals.py']
load = R.load
frame = R.frame


def GLB(path):
    import vexport as VE
    H, T = R.load()
    VE.export(path, 'PrismTank', [('hull', H, 0), ('turret', T, 0)], R.camera(), R.CANVAS, R.PPU)


def GLB_CHECK(path):
    """the hull alone, for the check against the hull frame (the turret frames are drawn at their own fitted size)."""
    import vexport as VE
    H, T = R.load()
    VE.export(path, 'PrismTank', [('hull', H, 0)], R.camera(), R.CANVAS, R.PPU)


GLB_NAME = 'r2pris.glb'
GLB_FRAMES = [24]
README = dict(
    title="Prism Tank", ts_name='SREF, Red Alert 2',
    frames="""frames/     r2pris-0000.png ... r2pris-0063.png, the mod's 64 frames on its 384 x 384 canvas, each with a -trim.png
            (white = house colour, antialiased):
              0-31    the hull with its shadow, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E)
              32-63   the prism turret (SREFTUR), no shadow, 32 facings, drawn at the hull's canvas centre""",
    previews="""previews/   8-facings.png            hull and turret facing the same way, the mod's frames beside HD
            hull-8-facings.png, turret-8-facings.png   each set on its own, every 4th facing
            turn.gif                 all 32 facings in turn, the mod's frames beside HD
            turret-turning.gif       the turret turning on the hull facing east
            scale.png                next to the HD harvester and EA's medium tank, as the game draws them""",
    vxl="Red Alert 2's SREF.VXL, SREFTUR.VXL, each posed by its own HVA, with RA2's UNITTEM.PAL",
    look="""- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north.  The hull at 5.03 canvas px per
  voxel with the unit's position at canvas (191.5, 191.02), the turret at 4.9 with its pivot at (191.5, 185.96):
  the sizes and places the mod's frames have (found by matching RA2's voxels to them: overlap 0.99 for the hull,
  0.94 for the turret).  RA2's voxels are drawn at RA2's cell size against TS's (0.8 of the TS units' scale), as
  in-mod/ has them.
- RA2's voxels carry RA2's own normals (244 of them, not TS's 36): estimated from the voxels the same way as TS's
  (src/ra2normals.py, src/estnormals.py) and used for the same layer of detail.""",
    extra=[('Fire points', """The model is RA2's voxels exactly (same sections, same places), so the emitter's tip you project from RA2's fire
point is where the beam starts: the turret frames keep the mod's size and place.""")],
    judgement="""- The turret at its own fitted size (4.9 px per voxel against the hull's 5.03): the mod's turret frames are
  drawn that much smaller, and the turret frames keep their size and place so your weapon tips still line up.""",
    glb="""r2pris.glb   the hull and the turret in RA2's own colours, the turret under its own node; the mod's camera
- Nodes: PrismTank > unit_facing_east > hull, turret (at RA2's HVA place and one scale; the mod draws the turret
  frames a little smaller, so the check below draws the hull alone over the hull frame).""",
    src="""  prisrender.py          the frame layout and cameras;  prisspec.py  its frames, previews and README
  prisexport.py          the .glb
    PKG=out python3 vdeliver.py prisspec render 0 1      renders frames/""")
