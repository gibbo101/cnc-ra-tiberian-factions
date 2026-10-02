"""vdeliver spec: the Mobile Sensor Array (TSLPST)."""
import sys
from paths import HANDOFF
import lpstrender as R

NAME = 'tslpst'
FRAMES = 32
CANVAS = R.CANVAS
INMOD = HANDOFF + '/12-TSLPST/in-mod/tslpst/frames/tslpst-%04d.png'
NO_SHADOW = []
CROP = (50, 50, 334, 320)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
REF = HANDOFF + '/12-TSLPST/reference-hd/RA_MRJ/frames/mrj-%04d.png'
SHEETS = [('8-facings.png', [('frame %d' % f, [f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ("EA's Mobile Radar Jammer", REF, [24], 1.0),
                        ('Mobile Sensor Array (HD)', None, [24], 2 / 3)])
SRC = ['lpstrender.py', 'lpstspec.py', 'lpstexport.py']
load = R.load
frame = R.frame


def GLB(path):
    import vexport as VE
    VE.export(path, 'MobileSensorArray', [('hull', R.load(), 0)], R.camera(), R.CANVAS, R.PPU)


GLB_NAME = 'tslpst.glb'
GLB_FRAMES = [24]
README = dict(
    title='Mobile Sensor Array', ts_name='LPST',
    frames="""frames/     tslpst-0000.png ... tslpst-0031.png, the mod's 32 frames on its 384 x 384 canvas, each with a -trim.png
            (white = house colour, antialiased), with the unit's shadow; 32 facings counter-clockwise from north
            (0 N, 8 W, 16 S, 24 E)""",
    previews="""previews/   8-facings.png            the mod's frames beside HD, every 4th facing
            turn.gif                 all 32 facings in turn, the mod's frames beside HD
            scale.png                next to the HD harvester and EA's Mobile Radar Jammer, as the game draws them""",
    vxl="LPST.VXL, posed by its HVA",
    look="""- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.24 canvas px per voxel, the
  unit's position (TS's HVA origin) at canvas (191.5, 191.1): the size and place the mod's frames have (found by
  matching TS's voxels to them: overlap 0.98), so the ground line is in-mod/'s and the deployed building's base,
  placed from it, still meets it.  Frame 20 (facing south-east) is where in-mod/ has it, so it still matches the
  deployed building's build-up frame 0.""",
    extra=[],
    judgement="",
    glb="""tslpst.glb   the model in TS's own colours, with the mod's camera
- Nodes: MobileSensorArray > unit_facing_east > hull.""",
    src="""  lpstrender.py          the frame layout and camera;  lpstspec.py  its frames, previews and README
  lpstexport.py          the .glb
    PKG=out python3 vdeliver.py lpstspec render 0 1      renders frames/""")
