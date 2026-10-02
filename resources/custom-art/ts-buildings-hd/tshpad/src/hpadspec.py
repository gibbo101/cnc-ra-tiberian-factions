"""Package spec for the Helipad (bdeliver.py)."""
import hpadfit as F

HAND = '/home/claude/work/ts/ts-buildings-hd-handoff/08-TSHPAD'


def shape_check(pk, out):
    import os
    import hpad as M
    from PIL import Image
    import ypreview as P
    rows = []
    for lv in (0, 1):
        img, r = F.flat(M, 6, level=lv)
        tmp = f'{out}/_shape{lv}.png'
        F.sheet(img, F.ts_frame(None, lv), tmp, 6, r=r, mod=M)
        im = Image.open(tmp).convert('RGBA')
        R = Image.new('RGBA', (im.width, im.height + 24), (30, 30, 30, 255))
        R.paste(im, (0, 24))
        P.label(R, f"{('healthy: GTHPADBB 00 + GTHPAD 00', 'damaged: GTHPADBB 01 + GTHPAD 01')[lv]}  (TS's own camera, 6x)", (6, 4))
        rows.append(R)
        os.remove(tmp)
    pk.stack(rows, 8).save(f'{out}/shape-check.png')


def readme():
    return """Tiberian Sun Helipad (GAHPAD, art GTHPAD; TSHPAD in the mod) rebuilt for Red Alert Remastered (HD).

One 3D model fitted to TS's own sprites (GTHPAD, GTHPADBB, GTHPADMK, GTHPAD_A), rendered two ways with the same renderer
as the Construction Yard, Power Plant, Barracks, Silo, Tech Center, Refinery, War Factory, Radar and Component Tower:
same materials, light, shadow (baked in at ~75% black) and outline. Fit to TS's frame in TS's own camera: silhouette
0.87 (TS's machinery is a clutter of small parts; the model keeps its masses). Made overnight without your shape check:
my calls are listed at the end.

ts-angle/  TS's own camera, lit from TS's side so it reads like the sprite. CANVAS 256x256: the canvas, scale and place
           the helipad has in the mod now (TS's frame x3.55, TS px (0, 0) at canvas (-28, -92), fitted to
           in-mod/tshpadmake-0018.png, IoU 0.99). Drops in over the current frames. (The mod's frames cut TS's sprite
           at the canvas's left edge; so do these.)
ra-grid/   On RA's square grid: RA's camera (orthographic, 32 degrees above the ground, looking north), TS's way round
           (not turned: the machinery down the west side, the control box at the back, the steps at the front right).
           CANVAS 256x256: the 2x2 plot is the whole canvas, the foundation's south edge on the plot's.
COLOUR     Green = house colour: the ring round the landing circle, the fuel tanks and the stripe at the machinery
           block's foot. Exactly the yard's green. Every frame has a -trim.png (white = house colour, antialiased).

What it is (read from TS's frames; GTHPADMK shows how it goes together):
  the pad      (GTHPADBB) a low octagonal platform over the east of the foundation: tan concrete slabs, a black landing
               circle with a white cross and a dashed white ring, a house-green ring round it, a flight of pink-tan
               steps down its south-east side, a railing of dark posts along its south edge
  lights       (GTHPAD_A) approach lights in a cross in front of the landing circle, four on each arm and one in the
               middle: a light runs in from the four ends to the middle and flashes there (TS's 8 frames, its levels)
  machinery    (GTHPAD) down the west side: a tan machinery block lit white-pink on its south face, dark at its foot,
               a house-green stripe; four green fuel tanks on a rack; grey pipes; the control box at the north-west on
               a stand, a dark window band

Each view has the same folders. Every frame is on the view's full canvas, in place, with a -trim.png.

bib/helipad-bib-00, -01         GTHPADBB: the pad, healthy and damaged. Drawn under everything. TS's has 3 frames (3
                                states); RA has no destroyed state.
building/helipad-00, -01        GTHPAD: the machinery, healthy and damaged, cut against the pad (its shadow on the
                                pad included), so bib + building = the whole helipad.
                                Damaged, as TS breaks it: a patch of the pad's west part broken up, rubble on it,
                                cracks; the control box's top smashed in; the tanks dented; soot. Greys and browns.
A-lights/helipad-lights-00..31  GTHPAD_A: 00-07 healthy, 08-15 damaged (six of the lights broken, dark, as TS's), 16-31
                                empty, as TS's 32. Cut against bib + building.
loop/helipad-loop-00..15        the mod's TSHPAD.ZIP layout (0000 healthy, 0008 damaged): 8 healthy + 8 damaged with
                                the lights running, straight renders (pad, machinery and lights in one).
build-up/helipad-build-00..23   24 frames in the order TS's GTHPADMK builds it (TS's 19 frames, spread over 24), in
                                colour as TS's: a pyramid of panels stands up in the middle and the pad's rim frame
                                goes round, the steps (00-05); the pyramid opens out and folds away (05-07); the deck
                                is laid in from the rim round a square hole, the tanks and pipes (07-11); a white dome
                                rises in the hole, the machinery block and the control box go up (12-17); the dome
                                sinks back and a hatch slides over the hole (17-21); the landing circle is painted
                                (22); 23 is the finished helipad (bib + building, lights dark).
                                TSHPADMAKE.ZIP has 19 frames: drop 03, 08, 13, 17, 20 or play all 24 faster.

Stacking: bib, building, A-lights (healthy t = 00-07; damaged 08-15). That matches loop frame t.

previews/  the helipad on its own; both states next to TS's; the mod's frames (tshpad-0000, -0008, tshpadmake-0018)
           next to the same HD frames; next to the Construction Yard, the Power Plant, the Component Tower and a GDI
           wall run (RA grid); the house colour next to the yard's; the build-up as a strip and a GIF against GTHPADMK;
           the lights' loop (healthy and damaged) against TS's; shape-check.png (the model in TS's own camera over
           TS's frame).
3d/        helipad.glb (glTF 2.0 .glb), in its own frame (TS's way round, as the RA grid version). Meshes: "pad" /
           "pad-damaged" (the bib, with the lights), "helipad" / "helipad-damaged" (the machinery). Markers: "landing"
           (the landing circle's centre on the pad), "light-1".."light-17". Cameras: "camera-ts-angle" and
           "camera-ra-grid" (256x256 each = the delivered frames). Axes: x east, y up, z south; 1.0 = one cell = 128
           px on the RA grid; origin the foundation's centre on the ground. COLOR_0 = the materials' colours, COLOR_1 =
           house colour (white).
src/       Python 3 (numpy, scipy, Pillow, scikit-image for the 3D export). hd.py is the renderer, brender.py the views.
           hpad.py (the model, its build-up stages), hpadmat.py (materials, the lights), hpaddamage.py, hpadbuild.py
           (GTHPADMK's order), hpadrender.py (views), hpadfinal.py (frames), hpadexport.py (3d), hpadspec.py,
           hpadgeo.py / hpadfit.py / hpadcmp.py / boxfit.py (reading TS's frames, the fit).
             python3 hpadfinal.py states|build iso|ra [ss]   the frames (ss 4 used)
             python3 cleanalpha.py <package>; python3 hpadexport.py; python3 bdeliver.py hpadspec previews

My calls (made overnight, without your shape check; each easy to change):
  - RA grid: TS's way round, not turned (a 2x2 pad with no door: the machinery stays down the west side).
  - TS's sprite can't show depth; the machinery stands beside the pad on the foundation's west strip, inside the
    plot so nothing is cut off on the RA canvas.
  - TS's machinery is a clutter of small parts at 1-3 TS px each; the model keeps its masses and colours (the white-lit
    block, the green tank cluster, the pipes, the box on its stand) rather than inventing detail TS doesn't show.
  - The loop assumes TSHPAD.ZIP plays the lights' 8 frames per state (it has 16 = 8 + 8).
"""


SPEC = dict(
    name='helipad', title='Helipad', pkg='/home/claude/work/out/ts-helipad-hd', hand=HAND,
    ts='GTHPAD', K=3.55, O=(-28.0, -92.0), iso_size=(256, 256), ra_size=(256, 256), ra_head=0, ra_left=0,
    cells=(2, 2), state_dir='building',
    under=[dict(folder='bib', prefix='bib', ts_shp='GTHPADBB')],
    overlays=[dict(folder='A-lights', prefix='lights', n=8, ts_shp='GTHPAD_A', ts_frame=lambda t, lv: t % 8 + 8 * lv)],
    loop=None,
    inmod=[('tshpad-0000.png', 0, 0, ('loop', 'helipad-loop-00')),
           ('tshpad-0008.png', 1, 0, ('loop', 'helipad-loop-08')),
           ('tshpadmake-0018.png', 0, 0, ('build-up', 'helipad-build-23'))],
    build_n=24, ts_mk_n=19, idle_n=16, idle_label='bib + building + A (the approach lights running in to the middle)',
    idle_ms=110,
    crop={'iso': (0, 20, 256, 236), 'ra': (0, 0, 256, 256)},
    zoom=1.5, green_zoom=1.5, gif_zoom=1.0, strip_w=160,
    extra_previews=[shape_check],
    src=['hd.py', 'walls2.py', 'wnoise.py', 'brender.py', 'pfinal.py', 'pdamage.py', 'powr.py', 'pmat.py', 'prender.py',
         'panim.py', 'pbuild.py', 'export3d.py', 'bdeliver.py', 'ypreview.py', 'procfit.py', 'weapdamage.py', 'weap.py',
         'weapplace.py', 'tsgeo.py', 'cleanalpha.py', 'radr.py', 'radrfit.py', 'radrmat.py', 'radrrender.py',
         'radrdamage.py', 'radrfinal.py', 'radrbuild.py', 'radrpreview.py',
         'hpad.py', 'hpadmat.py', 'hpaddamage.py', 'hpadbuild.py', 'hpadrender.py', 'hpadfinal.py', 'hpadexport.py',
         'hpadspec.py', 'hpadgeo.py', 'hpadfit.py', 'hpadcmp.py', 'boxfit.py', 'glbview.py'],
    readme=readme,
)
