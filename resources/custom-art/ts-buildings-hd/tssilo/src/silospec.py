"""Package spec for the Tiberium Silo (bdeliver.py)."""
import os
from PIL import Image, ImageDraw
import ypreview as P

HAND = '/home/claude/work/ts/ts-buildings-hd-handoff/05-TSSILO'


def readme():
    return """Tiberian Sun GDI Tiberium Silo (GASILO, TSSILO in the mod) rebuilt for Red Alert Remastered (HD).

One 3D model fitted to TS's own sprites (GTSILO, GTSILO_A/B, GTSILOMK), rendered two ways with the same renderer
as the Construction Yard, the Power Plant, the Barracks and the Component Tower: same materials, light, shadow
(baked in at ~75% black) and outline.

FOOTPRINT  TS's own size on its 2x2: the silo is as big as TS's, and on RA's grid it takes a 2x2.
ts-angle/  TS's own camera, lit from TS's side so it reads like the sprite.
           CANVAS 256x256, the mod's canvas and scale (in-mod/tssilo-0000.png: TS's frame x3.73), the silo where
           TS's silo is now.
ra-grid/   On RA's square grid: an orthographic camera 32 degrees above the ground, looking north (the camera of
           the tower, the walls and the other buildings).
           CANVAS 256x256 = the 2x2 plot, the silo centred on it. The plot's south edge is the footprint's south
           edge; everything (shadow too) stays inside the canvas.
COLOUR     Green = house colour (the five blades), exactly the yard's green. Every frame has a -trim.png (white =
           house colour, antialiased). The stored Tiberium (A) is natural Tiberium green and is NOT in the trim.

What it is (read from TS's frames): a dark ribbed drum carrying a wide, shallow dome of blue-grey glass panels in a
dark rim, a small cap on top, in a ring of dark earth (TS's silo has no pad). Five green blades lie on the dome
from the cap outwards to just past the rim, where each has its lamp, then drop to the ground as ridged claws
with stepped edges. A grey slatted loader tower stands on legs at the south corner, a pipe across to the drum;
a striped vent box stands against the drum on the east.

Each view has the same folders:

silo/silo-00.png     healthy, empty
silo/silo-01.png     damaged, as TS breaks it: the west claw broken away below its lamp (bits of it on the
                     ground), the east claw's foot snapped off and lying by it, a hole blown in the dome (the dark
                     inside showing), cracks across the glass, the loader's top torn, soot and rubble. No destroyed
                     frame: RA has healthy and damaged only.

build-up/silo-build-00..23.png
    24 frames, in the order TS's GTSILOMK builds it: the earth ring, and the dome unfolding on the ground from its
    middle out to full size, its first blade on it (00-04, as in TS, before what carries it); the drum rises under
    it, lifting it (05-07); the other four blades go on one by one, in TS's order (07-13); the loader, then the
    vent box (15-19). 23 is the finished silo
    (exactly silo-00). TSSILOMAKE.ZIP has 19 frames: drop five evenly (02, 07, 12, 17, 21) or play all 24 faster.

Overlays, each holds only the pixels it changes, on the silo's canvas, in place:
  A-tiberium/silo-tiberium-00..07.png   GTSILO_A: the stored Tiberium seen through the glass, filling the dome from
                                        the front back: 00 empty (nothing to draw), 01 a third, 02 two thirds,
                                        03 full. 00-03 healthy, 04-07 damaged. Pick the frame by how full the silo
                                        is, as TS does.
  B-lamps/silo-lamps-00..31.png         GTSILO_B: the blades' lamps: a white flash at 00 and 04 fading to pale
                                        blue, then steady pale blue (16-frame loop), as in TS. 00-15 healthy,
                                        16-31 damaged (two lamps dead: TS's damaged set lights 3 of 5).
  DRAW ORDER  the silo, A, B (they don't overlap).
TSSILO.ZIP has 2 frames (no animation baked in), so there is no loop/ folder: silo-00 and silo-01 drop in.

previews/  the silo on its own; both states next to TS's; the mod's frame next to ours; next to the Construction
           Yard, the Power Plant, the Component Tower and a GDI wall run (RA grid); the house colour next to the
           yard's; the four fill levels; the build-up as a strip and a GIF against GTSILOMK; the lamps' loop
           (healthy and damaged) against TS's.
src/       Python 3 (numpy, scipy, Pillow). hd.py is the renderer, brender.py the views. silo.py is the model,
           silomat.py the materials, silodamage.py the damage, silobuild.py the build-up, silorender.py the views
           and their layouts (TS angle: where TS draws it; RA grid: centred).
           python3 silofinal.py states|build iso|ra [ss]   makes the frames (ss 4 = supersampling used here)
           python3 bdeliver.py silospec previews             makes the previews
"""


def fill_preview(pk, out):
    rows = []
    for lv in (0, 1):
        ims = []
        for v in ('iso', 'ra'):
            for k in range(4):
                im = pk.building(v, lv)
                im.alpha_composite(pk.fr(v, 'A-tiberium', f'silo-tiberium-{k + 4 * lv:02d}'))
                ims.append(im)
        S = Image.new('RGBA', (8 * 260, 256 + 22), (30, 30, 30, 255))
        d = ImageDraw.Draw(S)
        for k, im in enumerate(ims):
            S.paste(P.on_bg(im), (k * 260, 22))
            d.text((k * 260 + 4, 4), f"{('TS angle', 'RA grid')[k // 4]} {('healthy', 'damaged')[lv]} fill {k % 4}/3", fill=(255, 255, 0, 255))
        rows.append(S)
    pk.stack(rows).save(f'{out}/tiberium-fill-levels.png')


SPEC = dict(
    name='silo', title='Tiberium Silo', pkg='/home/claude/work/out/ts-gdi-tiberium-silo-hd', hand=HAND, ts='GTSILO',
    K=3.73, O=(-32.0, -137.0), iso_size=(256, 256), ra_size=(256, 256), ra_head=0, cells=(2, 2),
    state_dir='silo',
    overlays=[dict(folder='A-tiberium', prefix='tiberium', n=4, ts_shp='GTSILO_A', ts_frame=lambda t, lv: None, idle=False),
              dict(folder='B-lamps', prefix='lamps', n=16, ts_shp='GTSILO_B', ts_frame=lambda t, lv: t % 16 + 16 * lv)],
    loop=None, inmod=[('tssilo-0000.png', 0, 0)],
    build_n=24, ts_mk_n=19, idle_n=16, idle_label='silo + B (blade-tip lamps)',
    extra_previews=[fill_preview],
    src=['hd.py', 'walls2.py', 'wnoise.py', 'brender.py', 'silo.py', 'silomat.py', 'silodamage.py', 'silobuild.py',
         'silorender.py', 'silofinal.py', 'pfinal.py', 'pdamage.py', 'powr.py', 'pmat.py', 'prender.py', 'panim.py',
         'pbuild.py', 'bdeliver.py', 'silospec.py', 'ypreview.py'],
    readme=readme,
)
