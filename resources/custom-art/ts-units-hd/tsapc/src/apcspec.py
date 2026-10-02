"""vdeliver spec: the Amphibious APC (TSAPC)."""
import sys
from paths import HANDOFF
import arender as AR

NAME = 'tsapc'
FRAMES = 64
CANVAS = AR.CANVAS
INMOD = HANDOFF + '/06-TSAPC/in-mod/tsapc/frames/tsapc-%04d.png'
NO_SHADOW = [(32, 63)]
CROP = (60, 60, 324, 300)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
RA_APC = HANDOFF + '/06-TSAPC/reference-hd/RA_APC/frames/apc-%04d.png'
SHEETS = [('land-8-facings.png', [('land %d' % f, [f]) for f in range(0, 32, 4)]),
          ('water-8-facings.png', [('water %d' % (32 + f), [32 + f]) for f in range(0, 32, 4)])]
GIFS = [('turn-land.gif', [('land %d' % f, [f]) for f in range(32)], 120),
        ('turn-water.gif', [('water %d' % (32 + f), [32 + f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ("EA's RA APC", RA_APC, [24], 1.0),
                        ('Amphibious APC (HD)', None, [24], 2 / 3)])
SRC = ['arender.py', 'apcspec.py', 'aplace.py', 'aexport.py']
load = AR.load
frame = AR.frame


def GLB(path):
    import vexport as VE
    land, water = AR.load()
    VE.export(path, 'AmphibiousAPC', [('land_hull', land, 0)], AR.camera(), AR.CANVAS, AR.PPU)
    VE.export(path.replace('.glb', '-water.glb'), 'AmphibiousAPC_water', [('water_hull', water, 0)],
              AR.camera(AR.ORIGIN_WATER), AR.CANVAS, AR.PPU)


GLB_NAME = 'tsapc.glb'
GLB_FRAMES = [24]
README = dict(
    title='Amphibious APC', ts_name='APC',
    frames="""frames/     tsapc-0000.png ... tsapc-0063.png, the mod's 64 frames on its 384 x 384 canvas, each with a -trim.png
            (white = house colour, antialiased):
              0-31    on land, with its shadow, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E)
              32-63   on water: the water hull TS swaps in (APCW.VXL), no shadow, 32 facings""",
    previews="""previews/   land-8-facings.png, water-8-facings.png   the mod's frames beside HD, every 4th facing
            turn-land.gif, turn-water.gif   all 32 facings in turn, the mod's frames beside HD
            scale.png                next to the HD harvester and EA's APC, as the game draws them""",
    vxl="APC.VXL (on land) and APCW.VXL (on water), each posed by its own HVA",
    look="""- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.25 canvas px per voxel.
  The land hull's position (TS's HVA origin) at canvas (191, 190.35), the water hull's at (191.5, 158): where the
  mod's frames have them (found by matching TS's voxels to them: overlap 0.98 on land, 0.91 on water, where the
  mod's water frames have gaps in their hull).""",
    extra=[],
    judgement="""- Most of the APC is house colour in TS; TS's remap shades on it are kept as darker and lighter seams.
- The water hull drawn complete (the mod's current water frames show gaps through it).""",
    glb="""tsapc.glb, tsapc-water.glb   the land hull and the water hull, each in TS's own colours,
                             with the mod's camera
- Nodes: AmphibiousAPC > unit_facing_east > land_hull; AmphibiousAPC_water > unit_facing_east > water_hull.""",
    src="""  arender.py             the APC's frame layout and cameras;  apcspec.py  its frames, previews and README
  aexport.py             the .glb;  aplace.py  the placement search against in-mod/
    PKG=out python3 vdeliver.py apcspec render 0 1      renders frames/""")
