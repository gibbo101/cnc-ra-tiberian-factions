Tiberian Sun Radar (GARADR, art GTRADR; TSRADR in the mod) rebuilt for Red Alert Remastered (HD).

One 3D model fitted to TS's own sprites (GTRADR, GTRADRMK, GTRADR_A), rendered two ways with the same renderer as the
Construction Yard, Power Plant, Barracks, Silo, Tech Center, Refinery, War Factory and Component Tower: same materials,
light, shadow (baked in at ~75% black) and outline. Fit to TS's frame in TS's own camera: silhouette 0.91 (the thin
antennas cost the most), house green 0.95. The dish is fitted to all 15 of GTRADR_A's frames at once (its rim within
0.4 TS px on average): a shallow dish 1.4 cells across, tilted 59 degrees up, turning 30 degrees about the turret.
Made overnight without your shape check: my calls are listed at the end.

ts-angle/  TS's own camera, lit from TS's side so it reads like the sprite. CANVAS 256x512: the canvas, scale and place
           the radar has in the mod now (TS's frame x3.015, TS px (0, 0) at canvas (-84, 44.75), fitted to
           in-mod/tsradrmake-0019.png, IoU 0.99). Drops in over the current frames.
ra-grid/   On RA's square grid: RA's camera (orthographic, 32 degrees above the ground, looking north), TS's way round
           (not turned: the rotunda at the front right, the green-topped block at the front left, the ramp down the
           east side, the tower and antennas behind).
           CANVAS 256x592: the 2x2 plot (256x256) is y 168-424, centred, the foundation's south edge on the plot's.
           That is the mod's 256x512 canvas grown 40 px top and bottom: the antennas are tall (TS's reach the top of
           its frame) and on RA's camera their tips come to canvas y 8. Cropping to y 40-552 gives the mod's 256x512
           but cuts the antenna tips.
COLOUR     Green = house colour: the south-west block's top, the south box and the panels on the east ramp. Exactly the
           yard's green. Every frame has a -trim.png (white = house colour, antialiased).

What it is (read from TS's frames; GTRADRMK shows how it goes together):
  plinth       a low tan base over most of the foundation (TS's outline: the north-west corner and a notch in the south
               edge left out), steel-grey trim round its foot
  south-west   a tan block with grooved sides and a light lip, a bevelled green top
  south        a green box between the block and the rotunda
  rotunda      at the south-east corner: a two-step tan pedestal, a ring of steel posts round a dark core, a ribbed gold
               dome
  east ramp    level at its north end, rounding down to the ground at its south end, green panels on top, a light
               rail along its east edge curving down with it, dark red-brown side
  tower        steel legs, a tank and a pipe, machinery, carrying a deep ribbed deck with a light lip; on the deck a
               raised block at its west end and machinery at its back, the dish's turret at its north-east corner
  antennas     seven, lavender-grey with dark joints and tan tips: three tall lattice masts (one at the west block,
               two at the back) and four thin ones
  dish         a big shallow dish (rim radius 88 units) on a boom from the turret, tilted 59 degrees up, cream with
               rust; six struts from its rim to the feed horn in front of it, a feed rod. It turns about the turret
               as TS's: GTRADR_A 00-14 from facing nearly due south to south-south-east (30 degrees), and back. On the
               RA grid it turns the same way relative to the camera (TS's angles + 45 degrees), so it reads as TS's.

Each view has the same folders. Every frame is on the view's full canvas, in place, with a -trim.png.

building/radar-00, -01          healthy and damaged, as GTRADR 0 and 1: the building without its antennas and dish
                                (GTRADR_A draws those). No destroyed frame (RA: healthy and damaged only).
                                Damaged, as TS breaks it: the deck's top broken up into tilted plates, a corner
                                knocked off, scorch; the south-west block's green top smashed (a hole torn in it);
                                the south box's front torn open; two of the ramp's panels blown out; a hole in the
                                dome's crown; soot, cracks, a little rubble. Greys and browns only.
A-dish/radar-dish-00..59        GTRADR_A: the antennas and the dish, cut against the building. 00-14 healthy, the dish
                                turning (TS's 15 frames); 15-29 damaged (a big piece of the dish's right side broken
                                away, a bite out of its left rim, struts snapped, the feed rod gone; the two west
                                antennas snapped and leaning far over, the tall one leaning a little, two stubs; the
                                dish still turns, as TS's); 30-59 empty, as TS's 60.
loop/radar-loop-00..55          the mod's TSRADR.ZIP layout (0000 healthy, 0028 damaged): 28 healthy + 28 damaged,
                                the dish turning there and back (A frames 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 13..1),
                                straight renders (building + antennas + dish in one). If TSRADR.ZIP runs another
                                order, build it from building/ + A-dish/ (they stack exactly).
build-up/radar-build-00..25     26 frames in the order TS's GTRADRMK builds it (TS's 20 real frames, spread over 26),
                                plain MK grey like TS's until its colours fade in: 00-02 the grey slab spreads over the
                                foundation; 03-06 the tower's first frame stands up in the middle, the south-west block
                                lies on the ground and is raised, a ring on the ground where the rotunda goes; 07 the
                                deck is built low on the tower's base with its machinery; 08-12 the deck is jacked up
                                as the tower grows under it, the antennas grow on it, the rotunda's pedestal and posts,
                                the east base and its ramp, the south box; 13-14 the dome, the turret; 15-20 the dish:
                                its struts, then its skin round from one side; 19-23 the colours fade in; 24 the house
                                green (no frame is half grey, half house colour: the trim couldn't carry it). 25 is the
                                finished building with its dish at A frame 00 (= loop 00).
                                TSRADRMAKE.ZIP has 20 frames: drop 02, 06, 10, 14, 18, 22 or play all 26 faster.

Stacking: building, then A-dish (healthy t = 00-14 there and back; damaged 15-29). With A frame t that matches loop
frame t (previews/in-mod-vs-hd.png and the idle GIFs are built from building + A).

previews/  the building on its own; both states next to TS's; the mod's frames (tsradr-0000, -0028, tsradrmake-0019)
           next to the same HD frames; next to the Construction Yard, the Power Plant, the Component Tower and a GDI
           wall run (RA grid); the house colour next to the yard's; the build-up as a strip and a GIF against GTRADRMK;
           the idle loop (the dish turning there and back, healthy and damaged) against TS's; shape-check.png (the
           model in TS's own camera over TS's frame).
3d/        radar.glb, the model itself (glTF 2.0 .glb: Blender, Godot and most engines open it), in its own frame (TS's
           way round, as the RA grid version). Meshes: "radar" / "radar-damaged" (the building without its antennas
           and dish), "antennas" / "antennas-damaged", "dish" / "dish-damaged" (the dish with its boom, struts, feed
           and rod, at A frame 00; it turns about the "dish-pivot" marker's vertical axis). Markers: "dish-pivot",
           "dish-centre". Cameras: "camera-ts-angle" (256x512 = the ts-angle frames) and "camera-ra-grid" (256x592 =
           the ra-grid frames). The dish's sweep is in the file's extras.
           Axes: x east, y up, z south. 1.0 = one cell = 128 units = 128 px on the RA grid. Origin: the foundation's
           centre on the ground. COLOR_0 = the materials' colours, COLOR_1 = house colour (white), like the -trim masks.
src/       Python 3 (numpy, scipy, Pillow, scikit-image for the 3D export). hd.py is the renderer, brender.py the views.
           radr.py         the model (its parts, the dish's geometry, the damage's shapes, the build-up's stages)
           radrmat.py      its materials;  radrdamage.py  the damage's soot, cracks and colours
           radrbuild.py    the build-up (GTRADRMK's order);  radrrender.py  the views and canvases
           radrexport.py   3d/radar.glb;   radrfinal.py   the frames
           radrgeo.py, radrplace.py, radrfit.py, radrtone.py, radrcmp.py, radrwire.py: reading TS's frames, the in-mod
             placement, the fit, the tone check, comparisons
             python3 radrfinal.py states|build iso|ra [ss]   the frames (ss 4 used)
             python3 cleanalpha.py <package>                 clears the faint ground haze (alpha < 8)
             python3 radrexport.py                           3d/radar.glb
             python3 bdeliver.py radrspec previews           the previews

My calls (made overnight, without your shape check; each easy to change):
  - RA grid: TS's way round, not turned. A 2x2 square with no door, so I kept TS's layout (the rotunda front right).
  - The RA canvas grows to 256x592 (40 px top and bottom) for the antennas.
  - The dish turns camera-relative on the RA grid (as the Tech Center's dome lights did), so it reads like TS's.
  - TS's sprite can't show depth: I put the tower at the back of the plot (its deck's north edge on the plinth's), the
    lowest the deck can sit. The antennas are as tall as TS draws them.
  - The antennas go in A-dish with the dish, as in TS's GTRADR_A (building/ has none).
  - The loop assumes TSRADR.ZIP plays the dish there and back (0..14..1 = 28 frames per state, which fits its 56).
  - On the RA grid the damaged west antennas lean a little less (24 and 22 degrees instead of TS's 38 and 34) and a
    bit further back, so they stay inside the canvas.
