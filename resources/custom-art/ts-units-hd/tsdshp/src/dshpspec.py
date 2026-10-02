"""vdeliver spec: the TS Dropship (TSDSHP)."""
import sys
import numpy as np
from PIL import Image
from paths import HANDOFF
import dshprender as R

NAME = 'tsdshp'
FRAMES = 4
CANVAS = R.CANVAS
INMOD = HANDOFF + '/26-TSDSHP/in-mod/tsdshp/frames/tsdshp-%04d.png'
NO_SHADOW = [(0, 3)]
CROP = (0, 120, 656, 380)
C17 = HANDOFF + '/26-TSDSHP/reference-hd/TD_C17/frames/c17-%04d.png'
BADR = HANDOFF + '/26-TSDSHP/reference-hd/RA_BADR/frames/badr-%04d.png'
# GDI's gold where TS's remap voxels are: the gold in-mod/ shows there (its lit quarter (188, 153, 40), its mean
# (124, 100, 26)) over the shading the HD house colour gets on the same faces
GOLD = (245, 200, 52)
SHEETS = [('ship.png', [('frame 0: the ship facing west', [0])]),
          ('shadow-frames.png', [('frame %d' % k, [k]) for k in (1, 2, 3)])]
GIFS = []
LINEUP = ('scale.png', [("EA's C-17 (TD)", C17, [8], 1.0), ("EA's Badger (RA)", BADR, [8], 1.0),
                        ('TS Dropship (HD)', None, [0], 1.0)])
SRC = ['dshprender.py', 'dshpspec.py', 'dshpexport.py', 'dshpfacings.py']
load = R.load


def frame(u, k, ss=4, sky=True):
    img, trim = R.ship(u, ss, sky, house=GOLD)
    black = Image.new('L', CANVAS, 0)
    if k == 0:
        return img, black
    return R.scaled(img, R.SHADOW_SCALES[k - 1]), black


CELL_PX = 128         # EA's density: a cell (24 classic px) is 128 px on this canvas


def GLB(path):
    import vexport as VE
    VE.export(path, 'Dropship', [('hull', R.load(), 0)], R.camera(), R.CANVAS, R.PPU, cells_px=CELL_PX)


def GLB_CHECK(path):
    """the model facing west, as frame 0 draws it, for the check."""
    import vexport as VE
    VE.export(path, 'Dropship', [('hull', R.load(), 0)], R.camera(), R.CANVAS, R.PPU, cells_px=CELL_PX, east=8)


def EXTRA(pkg):
    """the 32 directions (facings/, rendered by dshpfacings.py): their previews and checks."""
    import dshpfacings as F
    F.previews(pkg)
    return F.check(pkg)


GLB_NAME = 'tsdshp.glb'
GLB_FRAMES = [0]
README = dict(
    title='TS Dropship', ts_name='DSHP',
    frames="""frames/     tsdshp-0000.png ... tsdshp-0003.png, the mod's 4 frames on its 656 x 656 canvas (EA's density), each with a
            -trim.png (all black: the dropship never takes house colour):
              0       the ship, side-on and level, facing west, in GDI's gold
              1-3     frame 0 scaled to 55%, 70% and 85% about the canvas centre, as your packer makes the shadow
                      frames (regenerate them from frame 0 as before if you prefer)
facings/    tsdshp-0000.png ... tsdshp-0031.png, the ship in all 32 directions, counter-clockwise from north (0 N, 8 W,
            16 S, 24 E, as your other units), level, on the same 656 x 656 canvas at the same size and in the same gold,
            each with an all-black -trim.png.  It turns about the canvas centre (where the game puts the unit), so
            facing 8 is frames/ frame 0 exactly.  Shadow frames for them come from your packer, as for frame 0.""",
    previews="""previews/   ship.png                 frame 0 beside the mod's current frame 0
            shadow-frames.png        frames 1-3 beside the mod's
            scale.png                next to EA's C-17 and Badger, as the game draws them
            facings.png              every fourth direction (facings/)
            facings-turn.gif         all 32 directions in turn""",
    vxl="DSHP.VXL, posed by its HVA",
    look="""- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north, the ship facing west; 6.33
  canvas px per voxel, the voxel's origin at canvas (279.4, 326.8): the size and place the mod's frame 0 has (found by
  matching TS's voxels to it: overlap 0.98; 32 degrees fits it as well as 30), so the hull's centre is where it is
  now and the ship is as BIG as you signed off.
- GDI's gold where TS's remap voxels are, (245, 200, 52) before the light: the gold the mod's frame shows on the same
  faces, shaded like the HD house colour (so it reads as the same paint, lit).""",
    common_look="""- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides
  facing the camera as on the other units.  This canvas is at EA's density, so the game draws it 1:1 and the
  outline is the buildings' width.
- Colours brightened by 1.25 from TS's palette so its ochre comes out as the HD buildings' ochre; whites held at white
  paint.  It flies, so none of the ground's grime or occlusion that the ground units carry low on the hull.""",
    shadow="""None baked: frames 1-3 are the ship itself, scaled, which the game draws darkened on the ground as it
descends.""",
    extra=[],
    judgement="""- The gold is measured from the mod's current frame (TS's remap voxels as the mod shows them now), not
  picked by eye.
- The 32 directions turn about the canvas centre, the unit's place in the game, where frame 0 has the voxel's own
  origin; TS's HVA origin is 7.7 voxels (49 px) further forward, and turning about it would swing the ship round
  the canvas instead of turning it in place.""",
    glb="""tsdshp.glb   the model in TS's own colours (the remap parts in house colour), with the mod's camera
- Nodes: Dropship > unit_facing_east > hull.  The model faces east like the other units' models; the mod's frame 0
  faces west (the check below turns it west).""",
    src="""  dshprender.py          the frame, the camera and the shadow frames;  dshpspec.py  its frames, previews, README
  dshpexport.py          the .glb
  dshpfacings.py         the 32 directions (facings/), their previews and checks
    PKG=out python3 vdeliver.py dshpspec render 0 1      renders frames/
    PKG=out python3 dshpfacings.py render 0 1           renders facings/""")
