"""vdeliver spec: the Mammoth Mk. I (TS4TNK)."""
import sys
from paths import HANDOFF
import t4render as TR

NAME = 'ts4tnk'
FRAMES = 64
CANVAS = TR.CANVAS
INMOD = HANDOFF + '/05-TS4TNK/in-mod/ts4tnk/frames/ts4tnk-%04d.png'
NO_SHADOW = [(32, 63)]
CROP = (96, 80, 416, 400)
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
MAMMOTH = HANDOFF + '/05-TS4TNK/reference-hd/RA_4TNK/frames/4tnk-%04d.png'
SHEETS = [('8-facings.png', [('hull %d + turret %d' % (f, 32 + f), [f, 32 + f]) for f in range(0, 32, 4)]),
          ('hull-8-facings.png', [('hull %d' % f, [f]) for f in range(0, 32, 4)]),
          ('turret-8-facings.png', [('turret %d' % (32 + f), [32 + f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [f, 32 + f]) for f in range(32)], 120),
        ('turret-turning.gif', [('hull 24 + turret %d' % (32 + f), [24, 32 + f]) for f in range(32)], 120)]
LINEUP = ('scale.png', [('TS Harvester (HD)', HARV, [24], 1.0), ("EA's Mammoth (facing north)", MAMMOTH, [0, MAMMOTH.replace('%04d', '0032-0000')], 1.0),
                        ('Mammoth Mk. I (HD)', None, [24, 56], 2 / 3)])
SRC = ['t4render.py', 't4export.py', 't4spec.py', 't4place.py']
load = TR.load
frame = TR.frame


def GLB(path):
    import vexport as VE
    H, T = TR.load()
    VE.export(path, 'MammothMk1', [('hull', H, 0), ('turret', T, 0)], TR.camera(), TR.CANVAS, TR.PPU)


GLB_NAME = 'ts4tnk.glb'
GLB_FRAMES = [24, 56]
README = dict(
    title='Mammoth Mk. I', ts_name='4TNK',
    frames="""frames/     ts4tnk-0000.png ... ts4tnk-0063.png, the mod's 64 frames on its 512 x 512 canvas, each with a -trim.png
            (white = house colour, antialiased):
              0-31    the hull with its shadow, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E)
              32-63   the turret with its barrels and tusk pods, no shadow, 32 facings, drawn at the hull's canvas
                      centre""",
    previews="""previews/   8-facings.png            the assembled tank (hull + turret facing the same way), the mod's frames beside HD
            hull-8-facings.png, turret-8-facings.png   each set on its own, every 4th facing
            turn.gif                 the assembled tank through all 32 facings, the mod's frames beside HD
            turret-turning.gif       the turret turning on the hull facing east
            scale.png                next to the HD harvester and EA's Mammoth, as the game draws them""",
    vxl="4TNK.VXL, 4TNKTUR.VXL and 4TNKBARL.VXL, each posed by its own HVA",
    look="""- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.23 canvas px per voxel, the
  unit's position (TS's HVA origin) at canvas (255.5, 254.7) for the hull and the turret alike: the size and place the
  mod's frames have (found by matching TS's voxels to them: overlap 0.99 for the hull).  TS's hull sits 1.24 voxels
  above its HVA origin (its tracks' lowest voxels), so the model is lowered onto the ground and the camera raised to
  match: every pixel stays where in-mod/ has it, and the shadow meets the tracks.""",
    extra=[('Fire points', """The model is TS's voxels exactly (same sections, same places), so TS's PrimaryFireFLH=40,32,96,
SecondaryFireFLH=-32,80,120 and PBarrelLength=192 still point at the cannons' and the tusk pods' tips.""")],
    judgement="""- Most of the Mk. I is house colour in TS (it was never finished as a GDI tank); TS's remap shades on it are kept
  as darker and lighter seams, so its panels, vents and edges read as in TS.""",
    glb="""ts4tnk.glb   the model in TS's own colours: the hull, and the turret with its barrels and tusk pods
             under a 'turret' node that turns about the unit's position; the mod's camera
- Nodes: MammothMk1 > unit_facing_east > hull (its section), turret (the turret's section and the barrels').""",
    src="""  t4render.py            the Mk. I's frame layout and camera;  t4spec.py  its frames, previews and README
  t4export.py            the .glb;  t4place.py  the placement search against in-mod/
    PKG=out python3 vdeliver.py t4spec render 0 1      renders frames/""")
