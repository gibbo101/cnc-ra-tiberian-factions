"""vdeliver spec: the Hover MLRS (TSHVR)."""
import sys
import numpy as np
from paths import HANDOFF
import hvrrender as R

NAME = 'tshvr'
FRAMES = 96
CANVAS = R.CANVAS
INMOD = HANDOFF + '/07-TSHVR/in-mod/tshvr/frames/tshvr-%04d.png'
NO_SHADOW = [(0, 63)]
CROP = (16, 30, 176, 180)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
SHEETS = [('8-facings.png', [('shadow %d + hull %d + rack %d' % (64 + f, f, 32 + f), [64 + f, f, 32 + f])
                             for f in range(0, 32, 4)]),
          ('hull-8-facings.png', [('hull %d' % f, [f]) for f in range(0, 32, 4)]),
          ('rack-8-facings.png', [('rack %d' % (32 + f), [32 + f]) for f in range(0, 32, 4)]),
          ('shadow-8-facings.png', [('shadow %d' % (64 + f), [64 + f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [64 + f, f, 32 + f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ('Hover MLRS (HD)', None, [88, 24, 56], 4 / 3)])
SRC = ['hvrrender.py', 'hvrspec.py']
load = R.load
frame = R.frame


def GLB(path):
    import vexport as VE
    H, T = R.load()
    VE.export(path, 'HoverMLRS', [('hull', H, 0), ('rack', T, 0)], R.camera(), R.CANVAS, R.PPU)


def GLB_CHECK(path):
    """the hull alone, for the check against the hull frame (the mod seats the rack frames by its own tables)."""
    import vexport as VE
    H, T = R.load()
    VE.export(path, 'HoverMLRS', [('hull', H, 0)], R.camera(), R.CANVAS, R.PPU)


GLB_NAME = 'tshvr.glb'
GLB_FRAMES = [24]
README = dict(
    title='Hover MLRS', ts_name='HVR',
    frames="""frames/     tshvr-0000.png ... tshvr-0095.png, the mod's 96 frames on its 192 x 192 canvas (4 canvas px per classic
            pixel, as the mod has it), each with a -trim.png (white = house colour, antialiased):
              0-31    the hull, no shadow, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E)
              32-63   the missile rack, no shadow, 32 facings: each frame's content centred where the mod's current
                      rack frame has it, so the seat tables you dialled still hold
              64-95   the hull's shadow on its own, drawn first under the hull: the HD hull's silhouette, offset as
                      now (5 px right, 17 px down: it hovers), black at alpha 191, softened""",
    previews="""previews/   8-facings.png            the assembled unit (shadow, hull and rack laid over each other on one canvas;
                                     the engine's seat for the rack not applied), the mod's frames beside HD
            hull-8-facings.png, rack-8-facings.png, shadow-8-facings.png   the three sheets, every 4th facing
            turn.gif                 all 32 facings in turn, the mod's frames beside HD
            scale.png                next to the HD harvester, as the game draws them""",
    vxl="HVR.VXL (the hull) and HVRTUR.VXL (the rack), each posed by its own HVA",
    look="""- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 2.95 canvas px per voxel,
  the hull's position (TS's HVA origin) at canvas (95.5, 106): the size and place the mod's frames have (found by
  matching TS's voxels to them: overlap 0.95).  This canvas has half the other units' density, so the game draws it
  at 4/3: the outline is 0.75 canvas px wide here, so it comes out as wide in the game as on the other units.""",
    extra=[('Fire point', """The rack is TS's voxels exactly; its frames keep the mod's content centres, so TurretOffset=-64 and
PrimaryFireFLH=64,32,128 stand with the seats as dialled.""")],
    judgement="""- The shadow frames are the HD hull's own silhouette at the mod's offset (TS draws a hovering unit's shadow as a
  flat shape under it), softened like the other units' shadows.
- The rack's base ring (HVRTUR.VXL's five lowest voxel layers, the part that sits down in the hull's turret ring) is
  left off the rack frames, as the mod's rack frames have it: drawn over the hull, it would cover the deck, and it
  would pull each frame's centring 3-7 px off the pods.  The .glb leaves it off too.""",
    glb="""tshvr.glb    the hull and the rack in TS's own colours, each under its own node; the mod's camera
- Nodes: HoverMLRS > unit_facing_east > hull, rack (the rack at TS's HVA place; the mod seats it per facing by its own
  tables, so the check below draws the hull alone over the hull frame).""",
    src="""  hvrrender.py           the frame layout, the rack's centring and the shadow frames;  hvrspec.py  previews, README
    PKG=out python3 vdeliver.py hvrspec render 0 1      renders frames/""")
