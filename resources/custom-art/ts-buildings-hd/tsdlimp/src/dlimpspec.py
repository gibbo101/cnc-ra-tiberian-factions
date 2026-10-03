"""Package spec for the Limpet Mine (bdeliver.py)."""
import dlimp as M

HAND = '/home/claude/work/ts/ts-buildings-hd-handoff/18-TSDLIMP'
PKG = '/home/claude/work/out/ts-limpet-mine-hd'


def readme():
    return """Tiberian Sun Limpet Mine (the Limpet Drone dug in: Firestorm DLIMPET; TSDLIMP in the mod) rebuilt for Red Alert
Remastered (HD).

One 3D model fitted to TS's own sprites (DLIMPET, DLIMPMK, DLIMP_A), rendered two ways with the same renderer as the
Construction Yard, Power Plant, War Factory and the rest: same materials, light, shadow (baked in at ~75% black) and
outline. Fitted in TS's camera, frame by frame: dug in 0.72, the drone coming down 0.78-0.92 (silhouette overlap with
DLIMPMK's frames; TS's sprite is only 20 pixels across, so a pixel is a lot).

ts-angle/  TS's own camera, lit from TS's side so it reads like the sprite. CANVAS 256x256: the canvas, scale and place
           the mine has in the mod now (TS's frame x3.93, TS px (0, 0) at canvas (-60, -30), fitted to
           in-mod/tsdlimp-0000.png: the cell's ground centre at (128.6, 158.6)).
ra-grid/   On RA's square grid: RA's camera (orthographic, 32 degrees above the ground, looking north). CANVAS 256x256:
           the cell (128x128) centred, at x 64-192, y 64-192 (its ground centre at (128, 128)), as the mod's canvas;
           everything, the hovering drone and its shadow included, inside.
COLOUR     Green = house colour: the body and the four claws. Exactly the yard's green; detail on them only as thin
           seams. The dug-in top inside the ring is house green in the ring's shadow (darker, as TS's), and DLIMP_A's
           green flash is house green too (TS draws both in house colour). Every frame has a -trim.png (white = house
           colour, antialiased). The lamp, the eye, the ring's lights and the white flash are not house colour.

What it is (read from TS's frames):
  body     the drone: an egg in house green, widest a third of the way up, tucked into its ring at the foot, narrowing
           to a grey collar with a black knob on top; a lamp low on its front and a small eye above it (DLIMPMK blinks
           both)
  ring     a grey ring round the body's foot; over each claw a white light with a dark slot beside it (TS's
           white-and-black pairs on the ring's front)
  claws    four claws in house green at north, east, south and west: broad blades with a ridge down the middle,
           tapering to a point, each a sleeve on its hinge under the ring with the claw sliding out of it (DLIMPMK draws
           them longer in flight than dug in)
  dug in   the ring on the ground, the claws out flat with their points on the ground, the body sunk through the ring
           until only its top shows inside it, the collar and knob pulled in

Each view has the same folders. Every frame is on the view's full canvas, in place, with a -trim.png.

building/limpet-mine-00, -01
                                  healthy and damaged. TS draws all three DLIMPET frames the same (no damage shows);
                                  RA needs a damaged frame, so a light one: the east claw's point snapped off (bare
                                  metal at the break), a bite out of the ring's top on its south-west with soot round
                                  it, chips to bare metal along the claws' edges, scorch on the ring. Greys and browns
                                  only, no soot on the house green. No destroyed frame (RA: healthy and damaged only).
A-flash/limpet-mine-flash-00..09
                                  DLIMP_A: the dug-in top flashing: 00 white (lighting the ring's inner rim), 01 bright
                                  house green, 02-06 fading back to its dark green; 07-09 empty (TS's 07-09 draw
                                  nothing new). Cut against building-00; one set for both states (it plays over the
                                  damaged mine too, as the mod's frames have it).
loop/limpet-mine-loop-00..19
                                  TSDLIMP.ZIP's layout (20 frames): 00-09 the healthy mine with A 00-09, 10-19 the
                                  damaged one with A 00-09, as the mod's frames (tsdlimp-0000 and -0010 both flash).
                                  Straight renders, so they match the layers stacked.
build-up/limpet-mine-build-00..41
    42 frames, DLIMPMK frame for frame (the prompt asks for at least TS's 42):
      00-19  the drone hovers, its ring's foot 48 units (0.37 cells) up; the claws, folded in under it, drop (00-06),
             stretch out of their sleeves and swing out (06-19)
      20-30  it comes down a TS pixel a frame, the claws swinging out flat as it comes, so it lands on its ring and
             its points together (30)
      31-38  the body sinks through the ring a pixel a frame
      38-39  the collar and knob pull in; 39-41 dug in (= building-00, as TS's last three frames)
    All the way down the lamp cycles amber, red, dark red (a colour a frame) and the eye glints white then blue-white
    every ten frames (03-04, 13-14, 23-24, 33-34), as TS's.
    The mod's TSDLIMPMAKE.ZIP has 19 frames now: take 00, 02, 04 .. 34 and 41 for 19 (or use all 42).

How the layers stack:
  idle (the mod's)          building + A (t % 10) = loop/ 00-09 (healthy), 10-19 (damaged)
  the build-up's end        build-up 41 = building-00

previews/  the mine on its own; both states next to TS's (A at 00); the mod's frames (tsdlimp-0000, -0010,
           tsdlimpmake-0018) next to the same HD frames; next to the Construction Yard, the Power Plant, the Component
           Tower and a GDI wall run (RA grid); the house colour next to the yard's; the build-up as a strip and a GIF
           next to TS's DLIMPMK; the idle loops (A, healthy and damaged) against TS's.
3d/        limpet-mine.glb, the model itself (glTF 2.0 .glb: Blender, Godot and most engines open it), in its own frame.
           Meshes: "limpet-mine" (dug in), "limpet-mine-damaged", "limpet-drone" (in flight, DLIMPMK 19's pose, its
           ring's foot 48 units up). Markers: "lens" (the dug-in top DLIMP_A flashes), "lamp". Cameras:
           "camera-ts-angle" and "camera-ra-grid" (256x256 = the frames). Axes: x east, y up, z south; 1.0 = one cell =
           128 units. COLOR_0 = the materials' colours, COLOR_1 = house colour (white). The claws are square to the
           grid in it (as the RA frames).
3d/stl/    the same meshes as print-ready STL (3D printing): mm at 1 cell = 32 mm, Z up, the base flat on Z = 0; each
           one solid, watertight and checked; parts thinner than 1 mm thickened, plates on the bed at least 1.2 mm,
           loose specks dropped (README-stl.txt).
src/       Python 3 (numpy, scipy, Pillow, scikit-image for the 3D export). hd.py is the renderer, brender.py the views.
           dlimp.py          the model (pose = the ring's height, the claws' swing and stretch, the sink, the knob)
           dlimpmat.py       its materials, the lamp and eye, DLIMP_A's flash (glow = 0..9)
           dlimpdamage.py    the damage
           dlimpbuild.py     the build-up (DLIMPMK's frames)
           dlimprender.py    the views and canvases
           dlimpfinal.py     the frames:  python3 dlimpfinal.py states|build iso|ra [ss]  (ss 4 used; states first)
           dlimpexport.py    3d/limpet-mine.glb (export3d.py: marching cubes over the model)
           stlprint.py       3d/stl/ (the print-ready STL files)

My calls (each easy to change):
  - TS's sprite draws the claws' X taller than a square cross looks from TS's camera. In the TS-angle frames the claws
    are turned 10 degrees off square toward the camera's line (the front pair toward the south-east, the back pair
    toward the north-west), which gives TS's X; on the RA grid (and in the .glb) they are square to the grid, north,
    east, south and west, as a mine would sit. Say if you want one or the other in both.
  - The damaged frame is light (TS shows none). Say if you want it heavier, or the same as healthy.
  - The claws telescope (DLIMPMK draws them longer in flight than dug in), and the knob and collar pull into the body
    as it digs in (TS's knob vanishes between frames 38 and 39).
  - What TS shows at a pixel or two: the lamp's colours, the eye's glint, the ring's lights and slots.
"""


SPEC = dict(
    name='limpet-mine', title='Limpet Mine', pkg=PKG, hand=HAND,
    ts='DLIMPET', K=3.93, O=(-60.0, -30.0), iso_size=(256, 256), ra_size=(256, 256), ra_head=64, ra_left=64,
    cells=(1, 1), state_dir='building',
    overlays=[dict(folder='A-flash', prefix='flash', n=10, ts_shp='DLIMP_A', ts_frame=lambda t, lv: t % 10, shared=True)],
    loop=dict(n=10),
    inmod=[('tsdlimp-0000.png', 0, 0), ('tsdlimp-0010.png', 1, 0),
           ('tsdlimpmake-0018.png', 0, 0, ('build-up', 'limpet-mine-build-41'))],
    build_n=42, ts_mk='DLIMPMK', ts_mk_n=42, idle_n=10,
    idle_label='building + A (the dug-in top flashing)', idle_ms=110,
    zoom=2, green_zoom=3, gif_zoom=1.0, strip_w=160,
    src=['hd.py', 'walls2.py', 'wnoise.py', 'brender.py', 'pfinal.py', 'pdamage.py', 'radr.py', 'export3d.py',
         'bdeliver.py', 'ypreview.py', 'cleanalpha.py', 'weapdamage.py', 'plug.py', 'plugs.py', 'fgen.py', 'stlprint.py',
         'dlimp.py', 'dlimpmat.py', 'dlimpdamage.py', 'dlimpbuild.py', 'dlimprender.py', 'dlimpfinal.py',
         'dlimpexport.py', 'dlimpspec.py'],
    readme=readme,
)
