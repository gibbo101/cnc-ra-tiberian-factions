"""vdeliver spec: the Mobile EMP Cannon (TSMEMP), and its blast (TSMEMPFX, mempfx.py)."""
import sys
from paths import HANDOFF
import memprender as R

NAME = 'tsmemp'
FRAMES = 32
CANVAS = R.CANVAS
INMOD = HANDOFF + '/13-TSMEMP/in-mod/tsmemp/frames/tsmemp-%04d.png'
NO_SHADOW = []
# the HD frames stand on the ground, LOW_PX lower than in-mod/'s float: the check moves in-mod/ down by as much
CHECK_SHIFT = (0, int(round(R.LOW_PX)))
CROP = (50, 50, 334, 320)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
REF = HANDOFF + '/13-TSMEMP/reference-hd/RA_QTNK/frames/qtnk-%04d.png'
SHEETS = [('8-facings.png', [('frame %d' % f, [f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ("EA's M.A.D. Tank", REF, [24], 1.0),
                        ('Mobile EMP Cannon (HD)', None, [24], 2 / 3)])
SRC = ['memprender.py', 'mempspec.py', 'mempexport.py', 'mempfx.py']
load = R.load
frame = R.frame


def GLB(path):
    import vexport as VE
    VE.export(path, 'MobileEMP', [('hull', R.load(), 0)], R.camera(), R.CANVAS, R.PPU)


GLB_NAME = 'tsmemp.glb'
GLB_FRAMES = [24]
README = dict(
    title='Mobile EMP Cannon', ts_name='MOBILEMP',
    frames="""frames/     tsmemp-0000.png ... tsmemp-0031.png, the mod's 32 frames on its 384 x 384 canvas, each with a -trim.png
            (white = house colour, antialiased), with the unit's shadow; 32 facings counter-clockwise from north
            (0 N, 8 W, 16 S, 24 E)
fx/         tsmempfx-0000.png ... tsmempfx-0011.png, the blast: the mod's 12 frames on its 1152 x 576 canvas, played
            once at the unit's centre on the ground, each with a -trim.png (all black: the blast takes no house
            colour)""",
    previews="""previews/   8-facings.png            the mod's frames beside HD, every 4th facing
            turn.gif                 all 32 facings in turn, the mod's frames beside HD
            scale.png                next to the HD harvester and EA's M.A.D. Tank, as the game draws them
            blast.gif                the blast played, the mod's frames beside HD (100 ms a frame here)
            blast-frames.png         the blast's 12 frames, the mod's beside HD, at a third
            blast-close.png          frame 6's right-hand side at full size, the mod's above HD""",
    vxl="M_EMP.VXL, posed by its HVA",
    look="""- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.26 canvas px per voxel, the
  unit's position (TS's HVA origin) at canvas (191.0, 190.8): the size and place the mod's frames have (found by
  matching TS's voxels to them: overlap 0.98).
- On the ground: TS's voxel floats, its lowest voxel 4.3 voxels above the unit's position (about 3 classic px), and
  the mod's frames draw it so.  As the hand-off allows, the model sits on the ground at its position, with its shadow
  under its tracks like the other vehicles': the HD frames draw it 23 canvas px (2.8 classic px) lower than in-mod/,
  at in-mod/'s size and x.  The overlap below is measured with in-mod/ moved down by those 23 px.  To keep in-mod/'s
  float instead, memprender.camera(keep_float=True).""",
    extra=[('The blast (fx/)', """Each HD frame is TS's own frame (Firestorm's MEMPFX, decoded with ANIM.PAL) drawn again at the canvas's
resolution, in place: TS px x 4 at canvas (16, 10), where in-mod/ has it (overlap 0.99), so the ring keeps TS's
size, shape and timing frame by frame and still reaches about 3 cells out on frame 11.
- The ring's outline is TS's, its pixel steps smoothed into a clean antialiased edge.
- The colours are TS's 12 (four lavenders, four maroons, a cream, two oranges and white), each streak and speck
  where TS has it: TS's pixels of each colour family are redrawn as one shape with rounded, antialiased edges
  instead of 4 x 4 blocks, and within a family the shade runs smoothly between TS's own shades.
- A fine grain through the colour, long along x as TS's streaks are (as the units' paint carries one).
- Opaque, as in-mod/'s; nothing added that TS's frames lack (no glow, no new sparks).""")],
    judgement="""- On the ground, 23 canvas px lower than in-mod/'s float (Look, above).
- The blast redrawn from TS's frames rather than repainted (The blast, above): faithful to TS's layout, its
  pixels' blockiness replaced by smooth shapes.  A glow round the ring, or the blast drawn translucent, would each
  be a one-line change if you want the effect to read as light.""",
    glb="""tsmemp.glb   the model in TS's own colours, standing on the ground at its position, with the mod's camera
- Nodes: MobileEMP > unit_facing_east > hull.""",
    src="""  memprender.py          the frame layout and camera;  mempspec.py  its frames, previews and README
  mempexport.py          the .glb;  mempfx.py  the blast's frames and previews
    PKG=out python3 vdeliver.py mempspec render 0 1      renders frames/
    python3 mempfx.py out; python3 mempfx.py out previews      renders fx/ and the blast's previews""")
