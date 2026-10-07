Tiberian Sun Upgrade Center (GAPLUG, art GTPLUG; TSPLUG in the mod) and its three plugs (GTPLUG_D Drop Pod Node =
TSPODS, GTPLUG_E Seeker Control = TSSEEK, GTPLUG_F Ion Cannon Uplink = TSPION) rebuilt for Red Alert Remastered (HD).

One 3D model fitted to TS's own sprites (GTPLUG, GTPLUGMK, GTPLUG_A.._F), rendered on RA's square grid with the same
renderer as the Construction Yard, Power Plant, Barracks, Silo, Tech Center, Refinery, War Factory, Radar, Helipad,
Service Depot, Sensor Array and Component Tower: same materials, light, shadow (baked in at ~75% black) and outline. Fit
to TS's frame in TS's own camera: silhouette 0.88 (TS's 1 px antennas are most of the misses), house green 0.96.

v6 (Luke, 7 Oct 2026, from the game: "the roof on the left is a hard cutoff. Can we mirror the slope on the right?"):
the roof's west end hips down to the end wall as its east end does (a rust-red rim on its edges); the antennas there
stand on the slope.

RA grid only (Luke, 6 Oct 2026: "RA grid is the way we will go", "dont even package the ts angle", "We can rebuild it
using the 3d model"): no ts-angle/ folder. The .glb carries TS's own camera ("camera-ts-angle", the mod's TS-angle
canvas, scale and place), and src's plugfinal.py / plugloop.py render that view (iso) if it is ever wanted.

v2 (Luke's review, 5 Oct 2026): the three pipes run up the east side wall (the ramp) from the deck's edge and turn
into the building at the top, as TS's (v1 stood them free in front of it on a brown plinth, now gone); TS's purple
band wraps round the block's south-east corner onto its east face; the sockets' four bolts are holes for the plugs to
slot into, in lower, round-topped collars; the green slope's panes are separate panels with dark joints between them
(v1: raised green ribs); the roof is ridged along its length, browner and streakier; the deck's strip along the front
is a plain tan bar (v1: a ribbed orange grille); the antennas are a lighter blue-grey. Damaged: the whole middle pane
is knocked in (v1: a small hole), the roof's east half burnt fairly flat in TS's dark red-brown with the bare beams
across it (v1: a deeper crater over less of it), the west two pipes snapped near their feet and a length bent out of
the middle one's stump, the east one whole.

v3 (Luke, 6 Oct 2026: 'upgrade center id like the plugs facing south'): on the RA grid the building now stands TS's
way round, the sockets and their plugs to the south (the camera), the block and its green slope behind them, the ramp
and pipes at the east end; the plugs turned so they face you as on the TS angle. TS stands it on 2x3, so the RA plot
is 2x3 now (v1-v2 turned it a quarter onto a 3x2 plot): the rules' foundation becomes 2x3. Same 384x448 canvas.
The TS angle and the 3D model are unchanged.

v5 (Luke, 6 Oct 2026, the RA grid: "pipes and lights on the right in ts angle all straight, in ra angle walls suddenly
not flush with the building and whats the gap on the left?"): TS's east end is a hip skewed out to the deck's
north-east corner, with the pipes and the light slot lying on it; it only reads straight from TS's camera (v1-v3 fitted
it from there, so on the RA grid it came out as a parallelogram with slanted pipes). Rebuilt square for both views:
the block runs on east under a low hip to an upright end wall, flush with the block from front to back; the three
pipes stand straight up in front of it and turn into it at the top; GTPLUG_C's light runs down an upright lamp column
beside them. The end wall's face runs on north of the block, its top falling to the deck's north-east corner: a wedge
hidden on the RA grid that keeps TS's brown face right of the pipes on the TS angle. The pipes and the lamp column
stand where TS draws them. Damaged as TS's frame 1: the two left-hand (south) pipes lose their lower parts, their tops
left hanging from the bends; the broken length leans on the right-hand one, which is whole. The west end is flush
(v1-v3: TS's notch under the roof's west end, the gap on the left). The frames and the 3D model are new.

ra-grid/   On RA's square grid: RA's camera (orthographic, 32 degrees above the ground, looking north), TS's way round
           (v3): the sockets and plugs to the south, facing you; the block with its green slope behind them; the end
           wall, pipes and lamp column at the east end. CANVAS 384x448 with TS's 2x3 foundation as a 2x3 plot (256x384) at
           x 64-320, y 32-416, centred, the foundation's south edge on the plot's; the tallest antenna fits inside.
COLOUR     Green = house colour: the green slope (its panes, frames and sill), the sockets' collars and the panel on the
           Drop Pod Node. Exactly the yard's green. Every frame has a -trim.png (white = house colour, antialiased).

What it is (read from TS's frames; GTPLUGMK shows it go up):
  deck       a grey concrete platform raised on square feet (TS draws three: the south-west and south-east corners and
             the middle of the east side); an ochre step along the front edge
  block      a long tan block along the deck's north part: a ridged, streaky flat roof with the dish's box on its north
             edge, a
             bright bevel along its south edge, under it a vertical face with the purple band (the band turns the
             south-east corner), a narrow ledge and a brown strip; flush with the deck's west end (v5)
  slope      TS's greenhouse: a house-green slope from under the ledge down to the deck, separate panes with dark joints
             between them, a frame round them and a sill; it runs on to the end wall
  east end   (v5) the block's whole cross-section runs on east under a low brown hip to an upright brown end wall,
             flush with the block from front to back, a rust-red rim along the hip's top edges; behind the block the
             wall's face runs on north to the deck's north-east corner, its top falling to the deck (TS's brown face
             right of the pipes; hidden on the RA grid). Three steel pipes stand straight up from the deck in front of
             the wall and turn into it at the top (their bends step down northwards, so their tops line up as TS's do
             from TS's angle); a dark lamp column beside them (GTPLUG_C runs a light down it)
  sockets    two round sockets one cell apart on the deck's south part: low, round-topped house-green collars round grey
             plates with four holes for the plugs to slot into (the plugs stand in them)
  roof kit   antennas: the tallest at the west end with two lamps (GTPLUG_B), a T-bar one, a fork in the middle and
             three more; a small dish on a post on the box (GTPLUG_A turns it)

Every frame is on the RA grid's full canvas, in place, with a -trim.png.

building/upgrade-center-00, -01   healthy and damaged (TS's GTPLUG 0 and 1; RA has no destroyed state). Like TS's,
                                  they have the dish's box but no dish (GTPLUG_A draws it). Damaged as TS breaks it:
                                  the roof's east half burnt (dark red-brown, fairly flat with a few deeper pits, bare
                                  beams across it, the bevel and band broken along it), the two east antennas knocked
                                  off and the tallest bent, the two left-hand (south) pipes broken off low down, their
                                  tops left hanging from the bends, the broken length leaning on the right-hand one
                                  (whole), the middle pane knocked in the slope, the west
                                  socket's collar broken on its east side, the east socket's plate scorched, soot,
                                  a few chunks (greys and browns; the burnt roof in TS's dark red-brown).
A-dish/upgrade-center-dish-00..39
                                  GTPLUG_A: the dish turning once in 20 frames, cut against the building: 00-19 over
                                  the healthy building, 20-39 over the damaged one (TS has one set of 20 for both).
B-lamps/upgrade-center-lamps-00..19
                                  GTPLUG_B: the tallest antenna's two lamps (white with a blue-white glow) flicker,
                                  fade through the blues and go out (TS's 10 frames): 00-09 healthy, 10-19 damaged
                                  (on the bent antenna, as TS's move 1 px with it).
C-slot/upgrade-center-slot-00..15
                                  GTPLUG_C: a running light (white, red, dark red, orange, yellow) moving down the
                                  lamp column one cell a frame (TS's 8 frames): 00-07 healthy; 08-15 empty, as TS's
                                  (the damaged one's light is out).
build-up/upgrade-center-build-00..23
                                  24 frames in GTPLUGMK's order (TS draws 17; TSPLUGMAKE.ZIP has 19: take 00, 01,
                                  03 .. 23, or play all 24): the deck grows out from its middle (00-04), its painted
                                  outlines come up (04), the block rises out of the deck with its end wall, the slope's
                                  frames bare (05-08), the collars grow round from their fronts (07-16), the antennas
                                  grow up (12-21), the dish's post and dish (14, 15), the plates and holes (16, 17),
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
                                  top-left on the building's canvas: the mod's windows (TSPODS (101, 147), TSSEEK (104,
                                  142), TSPION (104, 118) on its TS-angle frames) moved with the socket (the socket's
                                  centre on the same spot of the 128 canvas): D (182, 241), E (185, 236), F (185, 212);
                                  each plug is turned so it shows you the same faces as TS's. For the left-hand (second,
                                  west) socket move the window by (-127, -1) px. As
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
           match TSPLUG.ZIP): python3 make_tsplug.py ra-grid OUTDIR.

previews/  the building on its own; both states next to TS's; the build-up as a strip and a GIF against GTPLUGMK; the
           idle loops (dish, lamps and slot light together) against TS's; next to the Construction Yard, the Power
           Plant, the Component Tower and a GDI wall run; the house colour next to the yard's; the plugs next to TS's
           and the mod's; the loop's plug combinations.
3d/        upgrade-center.glb (glTF 2.0 .glb), in its own frame (TS's way round). Meshes: "upgrade-center" /
           "upgrade-center-damaged" (with the dish at its A frame 00), "plug-drop-pod-node", "plug-seeker-control",
           "plug-ion-cannon-uplink" (each standing in the east socket; move it 1.0 west for the west socket). Markers:
           "socket-west", "socket-east", "dish-pivot", "slot-top" / "slot-bottom" (the lamp column's light runs between
           them), "lamp-low" / "lamp-high". Cameras: "camera-ra-grid" (384x448, looking north: TS's way round, as it
           stands on the grid) and "camera-ts-angle" (TS's own camera on a 384x384 canvas at the mod's TS-angle scale
           and place: render it to rebuild the TS angle). Axes: x east, y up, z south; 1.0 = one cell = 128 px on the
           RA grid; origin the foundation's centre on the ground. COLOR_0 = the materials' colours, COLOR_1 = house
           colour (white).
src/       Python 3 (numpy, scipy, Pillow, scikit-image for the 3D export). hd.py is the renderer, brender.py the views.
           plug.py (the model, its damage and build-up controls), plugs.py (the three plugs), plugmat.py (materials,
           the lamps and slot light), plugdamage.py, plugbuild.py (GTPLUGMK's order), plugrender.py (views),
           plugfinal.py (frames), plugexport.py (3d), plugspec.py; plugeo.py / plugfit.py / plugsfit.py / plugplace.py /
           plugshape.py (reading TS's frames, the fits, the mod's placement, the shape check); plugloop.py (loop/).
             python3 plugfinal.py states|dish|plugs|build ra [ss]   the frames (ss 4 used; iso = the TS angle)
             python3 plugloop.py ra [ss] [combo ..]                  loop/'s base frames

My calls (each easy to change):
  - RA grid TS's way round (v3, as you asked: the plugs to the south) on a 2x3 plot in the 384x448 canvas.
  - v5: the east end square in both views (an upright end wall, straight pipes and lamp column) rather than TS's
    skewed hip; the wedge behind the block keeps TS's brown face right of the pipes on the TS angle. The pipes' bends
    step down northwards so their tops line up from TS's camera as TS's do. The west end flush (no notch).
  - The deck stands on feet (TS's feet hang below its edges), so there is a dark gap under its edges between them.
  - The dish turns once round in GTPLUG_A's 20 frames, tilted up so it reads as a dish all the way round.
  - A-dish has a damaged half (the dish turning over the damaged building): TS has one set of 20.
  - The build-up keeps TS's order with 24 frames.
  - The plugs are redrawn rather than copied (TS's are a few px each), their shapes, sizes and colours read from TS's
    frames at TS's own size: the Seeker Control's camera, ear muffs and antennas, the Ion Cannon Uplink's rectangular
    dish, the Drop Pod Node's two lights on top and the uplink dish on its side. They turn as TS's frames do.
  - On the RA grid each plug is turned so you see the same faces of it as TS's. One plug alone goes in the
    right-hand socket, a second in the left-hand one.
