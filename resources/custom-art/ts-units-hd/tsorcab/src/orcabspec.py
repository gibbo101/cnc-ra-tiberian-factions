"""vdeliver spec: the Orca Bomber (TSORCAB)."""
import sys
from paths import HANDOFF
import orcabrender as R

NAME = 'tsorcab'
FRAMES = 32
CANVAS = R.CANVAS
INMOD = HANDOFF + '/24-TSORCAB/in-mod/tsorcab/frames/tsorcab-%04d.png'
NO_SHADOW = [(0, 31)]
CROP = (6, 8, 378, 266)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
REF = HANDOFF + '/24-TSORCAB/reference-hd/RA_HIND/frames/hind-%04d.png'
SHEETS = [('8-facings.png', [('frame %d' % f, [f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ("EA's Hind", REF, [24], 1.0),
                        ('Orca Bomber (HD)', None, [24], 2 / 3)])
SRC = ['orcabrender.py', 'orcabspec.py', 'orcabexport.py']
load = R.load
frame = R.frame


def GLB(path):
    import vexport as VE
    VE.export(path, 'OrcaBomber', [('hull', R.load(), 0)], R.camera(), R.CANVAS, R.PPU)


GLB_NAME = 'tsorcab.glb'
GLB_FRAMES = [24]
README = dict(
    title="Orca Bomber", ts_name='ORCAB',
    frames="""frames/     tsorcab-0000.png ... tsorcab-0031.png, the mod's 32 frames on its 384 x 384 canvas, each with a -trim.png
            (white = house colour, antialiased), no shadow; 32 facings counter-clockwise from north (0 N, 8 W, 16 S,
            24 E)""",
    previews="""previews/   8-facings.png            the mod's frames beside HD, every 4th facing
            turn.gif                 all 32 facings in turn, the mod's frames beside HD
            scale.png                next to the HD harvester and EA's Hind, as the game draws them""",
    vxl="ORCAB.VXL, posed by its HVA",
    look="""- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.26 canvas px per voxel, the
  voxel's origin at canvas (191.5, 190.72): the size and place the mod's frames have (found by matching TS's voxels to
  them: overlap 0.92).""",
    common_look="""- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides
  facing the camera as on the other units.  The game draws this canvas at two thirds (8 canvas px per classic
  pixel), so the outline is 1.5 times as wide on the canvas.
- Colours brightened by 1.25 from TS's palette so its ochre comes out as the HD buildings' ochre; whites held at white
  paint.  It flies, so none of the ground's grime or occlusion that the ground units carry low on the hull.""",
    shadow="""None baked: in flight the game lifts the frame by the aircraft's height and draws its shadow from the same
frame, darkened, on the ground.  The outline is the units' dark outline, so the silhouette reads as a shadow too.""",
    extra=[],
    judgement="",
    glb="""tsorcab.glb   the model in TS's own colours, with the mod's camera
- Nodes: OrcaBomber > unit_facing_east > hull.  The model's origin is the voxel's origin (TS's HVA origin), as the mod
  centres it.""",
    src="""  orcabrender.py          the frame layout and camera;  orcabspec.py  its frames, previews and README
  orcabexport.py          the .glb
    PKG=out python3 vdeliver.py orcabspec render 0 1      renders frames/""")
