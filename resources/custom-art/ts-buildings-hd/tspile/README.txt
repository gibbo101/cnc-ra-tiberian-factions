Tiberian Sun GDI Barracks (GAPILE, TSPILE in the mod) rebuilt for Red Alert Remastered (HD).

One 3D model fitted to TS's own sprites (GTPILE, GTPILE_A/B/C, GTPILEMK), rendered two ways with the same
renderer as the Construction Yard, the Power Plant and the Component Tower: same materials, light, shadow (baked
in at ~75% black) and outline.

ts-angle/  TS's own camera, lit from TS's side so it reads like the sprite.
           CANVAS 256x256, the same canvas, scale and place as the building in the mod now
           (in-mod/tspile-0000.png: TS's frame x3.2). Drops in over the current frames.
ra-grid/   On RA's square grid: an orthographic camera 32 degrees above the ground, looking north (the camera
           of the tower, the walls, the yard and the plant). The bunkers run east-west, the entrance faces the
           camera (south), the flagpole stands at the east end, as in TS. The flag flies to the right (east),
           facing the camera, like RA's Allied and Soviet barracks and TD's GDI barracks; in the TS-angle frames
           it flies to the right as TS's does.
           CANVAS 256x256 with the 2x2 plot at x 0-256, y 0-256 (no headroom needed: the masts and the flag fit).
           The foundation's south edge sits on the plot's south edge; everything (shadow too) stays inside.
COLOUR     Green = house colour, exactly the yard's and the plant's green (same colour and grain on every
           building). Every frame has a -trim.png (white = house colour, antialiased). The flag is house colour
           with a dark emblem.

What it is (read from TS's frames): two earth-sheltered bunkers running east-west either side of a narrow yard,
their battered sides faced with sand-coloured blocks, red-brown corrugated panels part-way up, green hatches set
into the slopes (the east ends almost all green, as in TS); each bunker roofed by two sandstone slabs with a gap.
A lower spine with two green hatches joins them; grey plant at either end of it (an air handler with a fan and a
tank in the west, a vent housing and stack in the east). The entrance, as TS's: a dark doorway in the south
bunker's face under the roof's edge, a flight of steps down from it to the ground between two walls that stick
out past the slope's foot, their tops falling with the steps (the east wall's coping house green), a lamp on
each wall's upper end. Two lamp masts (the west one carries the beacon) and a tall flagpole at the east end of
the yard.

Each view has the same folders:

building/barracks-00.png     healthy (no flag: GTPILE_C draws it)
building/barracks-01.png     damaged: every roof slab holed and charred (the north-west one caved in), soot
                             streaks down the slopes, the west mast snapped (its beacon left on the stump),
                             the east one broken off short, two of the east ends' hatches smashed, chunks out of
                             the south-west and north-east corners, rubble round the east end and the front.
                             Greys and browns only. No destroyed frame: RA has healthy and damaged only.

loop/barracks-loop-00..55.png
    Full frames with the animations baked in, laid out like TSPILE.ZIP (its frame 0000 is healthy and 0028 the
    damaged building): 00-27 healthy, 28-55 damaged. A and B loop every 8 frames, C every 7, as in TS.
    Straight renders. Drop-in for TSPILE.ZIP.

build-up/barracks-build-00..23.png
    24 frames, in the order TS's GTPILEMK builds it: the pad spreads into its H (00-03); the south bunker, then
    the north one, go up in bare grey block, the west mast and the spine (04-08); the blocks are faced and the
    entrance's steps and walls go in (08-09); the roof slabs, the east mast, the flagpole and the machinery (10-14); the flag is run up
    the pole (15-19); the hatches turn green last (22-23), as in TS. 23 is the finished building with its flag
    (= barracks-00 + C frame 00), because TS's and the mod's build-up end with the flag up.
    TSPILEMAKE.ZIP has 19 frames: drop five evenly (01, 06, 11, 16, 21) or play all 24 faster.

Animation overlays, if you draw them over the building rather than use loop/. Each holds only the pixels it
changes, on the building's canvas, in place (see-through pixels solved, so building + overlay = the straight
render):
  C-flag/barracks-flag-00..13.png       GTPILE_C: the flag waving (7-frame loop). 00-06 healthy, 07-13 damaged
                                        (torn, as in TS). It holds the flag and its shadow.
  A-lamps/barracks-lamps-00..15.png     GTPILE_A: the entrance's two lamps. The east one flashes white and fades
                                        over 00-03, then the west one over 04-07 (8-frame loop). 00-07 healthy,
                                        08-15 the same on the damaged building (TS has one set).
  B-beacon/barracks-beacon-00..15.png   GTPILE_B: the west mast's beacon: a white flash, then green, fading
                                        (8-frame loop). 00-07 healthy, 08-15 on the damaged building (on the
                                        stump).
  DRAW ORDER  the building, C, A, B (they don't overlap).

previews/  the building on its own; both states next to TS's; the mod's frames 0000 and 0028 next to the same loop
           frames; next to the Construction Yard, the Power Plant, the Component Tower and a GDI wall run (RA grid);
           the house colour next to the yard's; the build-up as a strip and a GIF against GTPILEMK; the idle loop
           (healthy and damaged) against TS's own animations. The GIFs are built from this package's frames and
           overlays, drawn the way the game draws them.
src/       Python 3 (numpy, scipy, Pillow). hd.py is the renderer (walls2.py gives the light and materials),
           brender.py the views. pile.py is the model, pilemat.py the materials, piledamage.py the damage,
           pilebuild.py the build-up.
           python3 pilefinal.py states|build iso|ra [ss]   makes the frames (ss 4 = supersampling used here)
           python3 bdeliver.py pilespec previews             makes the previews
