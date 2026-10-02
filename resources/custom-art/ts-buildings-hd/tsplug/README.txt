Tiberian Sun Upgrade Center (GAPLUG, art GTPLUG; TSPLUG in the mod) and its three plugs (GTPLUG_D Drop Pod Node =
TSPODS, GTPLUG_E Seeker Control = TSSEEK, GTPLUG_F Ion Cannon Uplink = TSPION) rebuilt for Red Alert Remastered (HD).

One 3D model fitted to TS's own sprites (GTPLUG, GTPLUGMK, GTPLUG_A.._F), rendered two ways with the same renderer as
the Construction Yard, Power Plant, Barracks, Silo, Tech Center, Refinery, War Factory, Radar, Helipad, Service Depot,
Sensor Array and Component Tower: same materials, light, shadow (baked in at ~75% black) and outline. Fit to TS's frame
in TS's own camera: silhouette 0.91 (TS's 1 px antennas are most of the misses), house green 0.98.

ts-angle/  TS's own camera, lit from TS's side so it reads like the sprite. CANVAS 384x384: the canvas, scale and place
           the building has in the mod now (TS's frame x3.695, TS px (0, 0) at canvas (-15, -112), fitted to
           in-mod/tsplugmake-0018.png). As in the mod now, the tallest antennas run off the canvas's top.
ra-grid/   On RA's square grid: RA's camera (orthographic, 32 degrees above the ground, looking north). TS stands it on
           2x3 and the plot is 3x2, so it is turned a quarter: TS's east end to the camera (the ramp, the pipes and the
           light slot face front, the green slope faces west into the light, the plugs' socket is the front one).
           CANVAS 384x448: the mod's 384x384 grown 32 px top and bottom so the tallest antenna fits; the 3x2 plot is
           x 0-384, y 96-352, centred, the foundation's south edge on the plot's.
COLOUR     Green = house colour: the green slope (its panes, frames and sill), the sockets' collars and the panel on the
           Drop Pod Node. Exactly the yard's green. Every frame has a -trim.png (white = house colour, antialiased).

What it is (read from TS's frames; GTPLUGMK shows it go up):
  deck       a grey concrete platform raised on square feet (TS draws three: the south-west and south-east corners and
             the middle of the east side), narrower at its north-west; an ochre step along the front edge
  block      a long tan block along the deck's north part: a striped flat roof with the dish's box on its north edge, a
             bright bevel along its south edge, under it a vertical face with the purple band (the band turns the
             south-east corner and runs north along the east face until the ramp covers it), a narrow ledge and a
             brown strip; the upper part runs on west past the deck (TS's notch under the west end)
  slope      TS's greenhouse: a house-green slope from under the ledge down to the deck, framed panes with a sill; at the
             east end it runs on over the ramp to a point
  ramp       a steep brown hip at the east end, from the block's north-east corner down to the deck's north-east corner
             and the east edge, a rust-red rim along its top; a dark slot down it (GTPLUG_C runs a light in it); three
             tall steel pipes with white caps stand on a brown plinth at the deck's east edge
  sockets    two round sockets one cell apart on the deck's south part: house-green collars round grey plates with
             four bolts (the plugs stand in them)
  roof kit   antennas: the tallest at the west end with two lamps (GTPLUG_B), a T-bar one, a fork in the middle and
             three more; a small dish on a post on the box (GTPLUG_A turns it)

Each view has the same folders. Every frame is on the view's full canvas, in place, with a -trim.png.

building/upgrade-center-00, -01   healthy and damaged (TS's GTPLUG 0 and 1; RA has no destroyed state). Like TS's,
                                  they have the dish's box but no dish (GTPLUG_A draws it). Damaged as TS breaks it:
                                  the roof caved in over its east half (burnt out, bare beams across it, the bevel
                                  and band broken along it), the two east antennas knocked off and the tallest bent,
                                  two pipes snapped and the third bent over, a pane knocked in the slope, the west
                                  socket's collar broken on its east side, the east socket's plate scorched, soot,
                                  a few chunks (greys and browns; TS's dark red-brown read as burnt brown).
A-dish/upgrade-center-dish-00..39
                                  GTPLUG_A: the dish turning once in 20 frames, cut against the building: 00-19 over
                                  the healthy building, 20-39 over the damaged one (TS has one set of 20 for both).
B-lamps/upgrade-center-lamps-00..19
                                  GTPLUG_B: the tallest antenna's two lamps (white with a blue-white glow) flicker,
                                  fade through the blues and go out (TS's 10 frames): 00-09 healthy, 10-19 damaged
                                  (on the bent antenna, as TS's move 1 px with it).
C-slot/upgrade-center-slot-00..15
                                  GTPLUG_C: a running light (white, red, dark red, orange, yellow) moving down the
                                  ramp's slot one cell a frame (TS's 8 frames): 00-07 healthy; 08-15 empty, as TS's
                                  (the damaged one's light is out).
build-up/upgrade-center-build-00..23
                                  24 frames in GTPLUGMK's order (TS draws 17; TSPLUGMAKE.ZIP has 19: take 00, 01,
                                  03 .. 23, or play all 24): the deck grows out from its middle (00-04), its painted
                                  outlines come up (04), the block rises out of the deck with its ramp, the slope's
                                  frames bare (05-08), the collars grow round from their fronts (07-16), the antennas
                                  grow up (12-21), the dish's post and dish (14, 15), the plates and bolts (16, 17),
                                  the pipes and grey panes (20), the panes go green (23). 23 = the healthy building
                                  with the dish at its A frame 00 (TS's last MK frame has the dish).
plugs/<plug>/<plug>-00..15        the three plugs (drop-pod-node, seeker-control, ion-cannon-uplink) on their own
                                  128x128 canvases, like the mod's TSPODS / TSSEEK / TSPION: the plug standing in the
                                  right-hand socket (the first plug's; east in TS's frame), lifted off the building (no
                                  shadow of its own; the socket's collar in front of its foot is left to the building).
                                  00-14 healthy, as TS's 15 frames: the Seeker Control turns its camera out towards you,
                                  blinks its lens and turns back; the Ion Cannon Uplink's dish turns from facing
                                  south-south-west to facing you and rises a little; the Drop Pod Node is still (its 15
                                  are the same picture, as TS's); 15 damaged (sooted). window.txt = the 128 canvas's
                                  top-left on the building's canvas. TS angle: cut from the same windows as the mod's
                                  (TSPODS (101, 147), TSSEEK (104, 142), TSPION (104, 118), found by matching them on
                                  TS's frame: IoU 0.98-0.99), so they drop in. RA grid: the same windows moved with the
                                  socket (the socket's centre on the same spot of the 128 canvas): D (11, 183), E (14,
                                  178), F (14, 154); there each plug is turned so it shows you the same faces as on the
                                  TS angle. For the left-hand (second, west) socket move the window by (-87, -44) px on
                                  the TS angle, (+1, -67) px on the RA grid (it is behind the right-hand one there). As
                                  in the mod now, the Ion Cannon Uplink is taller than its 128 canvas: its dish and its
                                  foot run off the top and bottom (the frames in loop/ have it whole).
                                  Redrawn from TS's frames rather than copied pixel for pixel:
                                    drop-pod-node      the beacon that calls the pods down: an armoured casing with a hatch,
                                                       two beacon lights on top (a small one back left, a big one front
                                                       right), the ochre space-uplink dish out on its left side, a house-
                                                       green panel, a pump block with pipes low on its front
                                    seeker-control     the Hunter-Seeker's control lab: a squat round lab (dark below, an
                                                       ochre band round its widest, a khaki shoulder), a small dome in a
                                                       black ring on top with two thick antennas, a camera with a big
                                                       round lens low on its front (it blinks) and an ear muff with a
                                                       grille on each side
                                    ion-cannon-uplink  a dark plinth carrying a round platform low down with railings
                                                       round its edge, a slim pole up through the middle to a wide
                                                       platform at the top; on it the dish's mount (a turntable, the
                                                       machinery housing, a fork and a hub holding the rectangular
                                                       satellite dish in front of the housing), turning with the dish

Stacking: building, then A-dish, B-lamps and C-slot (healthy t = 00..; damaged + 20 / + 10 / + 8), then the plugs.

loop/      TSPLUG.ZIP's 800 frames with the plugs baked in, read as 10 plug combinations x 80 frames (40 healthy +
           40 damaged, the dish / lamps / slot loop playing over each): no plugs, each plug alone (in the right-hand
           socket) and each ordered pair (0000 = no plugs; 0400 = Ion Cannon Uplink right + Seeker Control left, as in
           the mod now). loop/<view>/base/<combo>/ holds the building with its plugs (still, at their frame 0), healthy
           (-00) and damaged (-01), each with its -trim.png; make_tsplug.py stacks the A / B / C frames over them and
           numbers them 0000-0799 in the order its ORDER list gives (as delivered: loop/README.txt; change ORDER to
           match TSPLUG.ZIP): python3 make_tsplug.py ts-angle|ra-grid OUTDIR.

previews/  the building on its own; both states next to TS's; the build-up as a strip and a GIF against GTPLUGMK; the
           idle loops (dish, lamps and slot light together) against TS's; next to the Construction Yard, the Power
           Plant, the Component Tower and a GDI wall run (RA grid); the house colour next to the yard's; the plugs next
           to TS's and the mod's; shape-check.png (the model in TS's own camera over TS's frame, and the RA grid three
           ways: as delivered, turned the other way, and not turned on a 2x3 plot).
3d/        upgrade-center.glb (glTF 2.0 .glb), in its own frame (TS's way round). Meshes: "upgrade-center" /
           "upgrade-center-damaged" (with the dish at its A frame 00), "plug-drop-pod-node", "plug-seeker-control",
           "plug-ion-cannon-uplink" (each standing in the east socket; move it 1.0 west for the west socket). Markers:
           "socket-west", "socket-east", "dish-pivot", "slot-top" / "slot-bottom", "lamp-low" / "lamp-high". Cameras:
           "camera-ts-angle" (384x384) and "camera-ra-grid" (384x448, looking at it from its east, as it stands turned
           on the grid). Axes: x east, y up, z south; 1.0 = one cell = 128 px on the RA grid; origin the foundation's
           centre on the ground. COLOR_0 = the materials' colours, COLOR_1 = house colour (white).
src/       Python 3 (numpy, scipy, Pillow, scikit-image for the 3D export). hd.py is the renderer, brender.py the views.
           plug.py (the model, its damage and build-up controls), plugs.py (the three plugs), plugmat.py (materials,
           the lamps and slot light), plugdamage.py, plugbuild.py (GTPLUGMK's order), plugrender.py (views),
           plugfinal.py (frames), plugexport.py (3d), plugspec.py; plugeo.py / plugfit.py / plugsfit.py / plugplace.py /
           plugshape.py (reading TS's frames, the fits, the mod's placement, the shape check); plugloop.py (loop/).
             python3 plugfinal.py states|dish|plugs|build iso|ra [ss]   the frames (ss 4 used)
             python3 plugloop.py iso|ra [ss] [combo ..]                  loop/'s base frames

My calls (each easy to change):
  - RA grid turned a quarter, TS's east end to the camera (the other way round and not turned are in
    shape-check.png); its canvas grown to 384x448 for the tallest antenna.
  - The deck stands on feet (TS's feet hang below its edges), so there is a dark gap under its edges between them.
  - The dish turns once round in GTPLUG_A's 20 frames, tilted up so it reads as a dish all the way round.
  - A-dish has a damaged half (the dish turning over the damaged building): TS has one set of 20.
  - The build-up keeps TS's order with 24 frames.
  - The plugs are redrawn rather than copied (TS's are a few px each), their shapes, sizes and colours read from TS's
    frames at TS's own size: the Seeker Control's camera, ear muffs and antennas, the Ion Cannon Uplink's rectangular
    dish, the Drop Pod Node's two lights on top and the uplink dish on its side. They turn as TS's frames do.
  - On the RA grid each plug is turned so you see the same faces of it as on the TS angle. One plug alone goes in the
    right-hand socket, a second in the left-hand one.
