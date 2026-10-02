"""vdeliver spec: the Mobile War Factory (TSMWAR)."""
import sys
from paths import HANDOFF
import mwarrender as R

NAME = 'tsmwar'
FRAMES = 32
CANVAS = R.CANVAS
INMOD = HANDOFF + '/14-TSMWAR/in-mod/tsmwar/frames/tsmwar-%04d.png'
NO_SHADOW = []
CROP = (50, 50, 334, 320)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
REF = HANDOFF + '/14-TSMWAR/reference-hd/RA_MCV/frames/mcv-%04d.png'
SHEETS = [('8-facings.png', [('frame %d' % f, [f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ("EA's MCV", REF, [24], 1.0),
                        ('Mobile War Factory (HD)', None, [24], 2 / 3)])
SRC = ['mwarrender.py', 'mwarspec.py', 'mwarexport.py']
load = R.load
frame = R.frame


def GLB(path):
    import vexport as VE
    VE.export(path, 'MobileWarFactory', [('hull', R.load(), 0)], R.camera(), R.CANVAS, R.PPU)


GLB_NAME = 'tsmwar.glb'
GLB_FRAMES = [24]
README = dict(
    title='Mobile War Factory', ts_name='MOBWARG',
    frames="""frames/     tsmwar-0000.png ... tsmwar-0031.png, the mod's 32 frames on its 384 x 384 canvas, each with a -trim.png
            (white = house colour, antialiased), with the unit's shadow; 32 facings counter-clockwise from north
            (0 N, 8 W, 16 S, 24 E)""",
    previews="""previews/   8-facings.png            the mod's frames beside HD, every 4th facing
            turn.gif                 all 32 facings in turn, the mod's frames beside HD
            scale.png                next to the HD harvester and EA's MCV, as the game draws them""",
    vxl="MWAR_NOD.VXL, posed by its HVA",
    look="""- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.26 canvas px per voxel, the
  unit's position (TS's HVA origin) at canvas (191.65, 190.25): the size and place the mod's frames have (found by
  matching TS's voxels to them: overlap 0.98).  TS's hull sits 1.04 voxels above its HVA origin, so the model is
  lowered onto the ground and the camera raised to match: every pixel stays where in-mod/ has it, and the shadow
  meets the tracks.  Frame 12 (facing south-west) is where in-mod/ has it, so it still matches the deployed War
  Factory's build-up frame 0.""",
    extra=[],
    judgement="",
    glb="""tsmwar.glb   the model in TS's own colours, with the mod's camera
- Nodes: MobileWarFactory > unit_facing_east > hull.""",
    src="""  mwarrender.py          the frame layout and camera;  mwarspec.py  its frames, previews and README
  mwarexport.py          the .glb
    PKG=out python3 vdeliver.py mwarspec render 0 1      renders frames/""")
