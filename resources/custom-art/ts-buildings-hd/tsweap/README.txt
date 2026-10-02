Tiberian Sun War Factory (GAWEAP, art GTWEAP; TSWEAP in the mod) rebuilt for Red Alert Remastered (HD).

One 3D model fitted to TS's own sprites (GTWEAP, GTWEAPMK, GTWEAPBB, GTWEAP_1, _2, _A, _B, _C, _D), rendered two ways
with the same renderer as the Construction Yard, Power Plant, Barracks, Silo, Tech Center, Refinery and Component
Tower: same materials, light, shadow (baked in at ~75% black) and outline. Fit to TS's frame: silhouette 0.94, house
green 0.96; the lamps within a pixel of TS's.

ROUND 2 (your play test, 2026-10-02): the RA grid version reworked to your brief (art-chat-round-2/PROMPT.txt), all of
it built into the model (its 'ra' layout), so the frames come out that way without the mod touching them:
  1  the green slope on the west, with its frame, poles, roof beam, sill and its fender beside the door, mirrored onto
     the east side about the door's centre line, in place of the north fender, its vent and its green cap; lit as the
     model's own east-facing surface (so darker than the west one); the apron tucks in under both slopes; the door,
     its jambs, the lintel and the beam over the door as they were; the west block and the roof's machinery stay where
     they are. The green unit (the box with the red band on the fender between the slope and the door) is mirrored
     too, onto the east fender (your note this morning). Damaged: TS's hole stays in the west slope and TS's crushed
     unit stays west; the east slope gets soot and cracks, the east unit dents and soot (its red band kept).
     Also this morning: one rust housing on the roof's north edge sat over the east twin of the green strip along the
     slope's top; it is pulled in off the edge, so that strip runs unbroken on both sides too.
  2  four lamps on the beam over the door (the east one gone), the light run as the mod reordered it (TS's frames 0 1 2
     3 4 5 5 9 10 11 12 13 14 15 0 0, the fifth lamp left out); 16 empty for the damaged state as before. The four sit
     where they were: their middle is 3.5 px east of the door's centre line.
  3  the apron symmetric about the door's centre line (its west half mirrored, its texture and its damage too), TS's
     grey patch gone; the lane's stripes run as before (house green: the mod turns them gold). The build-up's slab is
     the apron's own outline (plus the hall's footprint, hidden under the hall once it stands), so nothing changes
     shape when the building completes.
  4  nothing clipped: the canvas is 480x512 (the plot x 48-432, y 0-512, centred). The build-up's poles now lie along
     each slope's foot (the back one pointing north, the front one south) and stand up there (TS's lie out sideways,
     132 px past the old canvas's edge); round 1's window also cut their tops in frames 12-14: fixed. Only the long
     shadows of the east poles, standing in build-up 07-13, fade out over the canvas's last 14 px, as you chose.
  1-under-door: only the doorway, the shut door's outline 2 px wider (as the mod cut it).
  Same layers, names and frame counts as round 1. The TS-angle frames are unchanged except the build-up: round 1's
  render windows cut the poles (03-14) and the construction slab (03-08) there; 03-19 are re-rendered whole.

ts-angle/  TS's own camera, lit from TS's side so it reads like the sprite. CANVAS 896x672: the canvas, scale and place
           the war factory has in the mod now (TS's frame x4.125, TS px (0, 0) at canvas (50, -190), fitted to
           in-mod/tsweapmake-0018.png). Drops in over the current frames. The door opening is where the mod's art has
           it (TS's own door and fenders at the mod's place, within about 2 TS px), so the exit seat you measured off
           the left door jamb still holds. The model's door, at the floor:
             exit (489.7, 328.0), left jamb (432.1, 356.8), right jamb (547.3, 299.2)  (canvas px)
ra-grid/   On RA's square grid: RA's camera (orthographic, 32 degrees above the ground, looking north), the building
           turned a quarter clockwise so the door faces south, to the camera, as RA's and TD's war factories do (your
           call). TS's door size is kept (the Titan doesn't have to fit: the door draws over it).
           Round 2: symmetric about the door's centre line (see above).
           CANVAS 480x512: TS's 4x3 foundation turned is 3 wide x 4 deep, a 384x512 plot, centred, 48 px spare each
           side. The foundation's south edge is on the plot's south edge; everything (shadow included) is inside.
           RA's camera squashes depth (x0.53, as on every building so far), so the 4-deep foundation draws 271 px
           deep: counting the 3x4 plot's rows from the back, the roof is drawn on row 2, the walls, door and fenders
           on row 3, the apron on row 4, and row 1 (the top 128 px) is empty in every frame. So the same frames also
           fit RA's own WEAP plot, 3x3: crop y 128-512 (canvas 480x384): the hall on the back 2 rows, the apron on
           the front row, the exit at the top of the bottom-middle cell, as RA's WEAP. Your call;
           previews/exit-and-jambs.png shows both.
             3x4, canvas 480x512 (plot centre (240, 256)):
               exit (238.5, 373.2), left jamb (164.0, 373.2), right jamb (313.0, 373.2)
               in leptons from the plot centre (2 per px): exit -3, +234, left jamb -152, +234, right jamb +146, +234
             3x3, canvas 480x384 (frames cropped to y 128-512; plot centre (240, 192)):
               exit (238.5, 245.2), left jamb (164.0, 245.2), right jamb (313.0, 245.2)
               in leptons from the plot centre: exit -3, +106, left jamb -152, +106, right jamb +146, +106
           Units roll out of the door straight down the screen (south), over the apron and off the plot.
           To put a frame on the mod's 896x672 canvas instead, paste it at (208, 80) (3x4) or (208, 144) (3x3): the
           plot stays centred on the canvas.
COLOUR     Green = house colour: the sloped panel on the south side and the fascia over it, the west block, the north
           fender's cap, the band along the roof's north edge, the green unit on the south fender, the small green
           strip on the roof, and the hazard stripes in the lane in front of the door (RA grid, round 2: the twin
           slope and fascia on the east too; no north fender cap; the band only behind the twin slope). Exactly the yard's green. Every
           frame has a -trim.png (white = house colour, antialiased). The lamps are not house colour.

What it is (read from TS's frames; GTWEAPMK shows how it goes together):
  the hall     a long tan hall with the door bay at its east end (its south end on the RA grid)
  the door     a grey ribbed roll-up door with a diagonal brace, between two quarter-round fenders (olive-tan, a dark
               vent in the north one). It rolls straight up its track, then round a quarter circle back into the
               roof: GTWEAP_D goes straight up over 00-04 and round the curve over 04-08, leaving a strip under the
               lintel, as TS's
  the bay      behind it, a dark brown hall, olive rails on the floor, red lights
  south side   a big green panel sloping to the ground between two dark poles, a green fascia over it, a sill at its
               foot. The west pole runs on over the roof as a beam; the east one carries the beam over the door with
               the five lamps (GTWEAP_A). A green unit turned 45 degrees on a bracket on the south fender's face, a red
               band round it
  north side   the north fender's green cap; a green band along the roof's north edge
  the roof     a tan deck with dark beams: a frame of tan ridges, rust-red housings, dark machinery and pipes, the three
               small lamps (GTWEAP_B), and at the west end a platform with the two fans in raised rings (GTWEAP_C)
  west end     the green block with its rounded top; brown machinery and a pipe loop at the south-west corner
  the bib      (GTWEAPBB) a concrete apron fanning out from the door: seams radiating from the lane's end and a ring
               round it, sand towards its edges, a grey patch at its north-west, the house-green and black hazard
               stripes down the lane in front of the door. The lane is the door's width, jamb to jamb, and the lane,
               the ring and the seams are centred on the door (your call: TS's run a little off towards the north
               fender)

Each view has the same folders. Every frame is on the view's full canvas, in place, with a -trim.png.

building/war-factory-00, -01      healthy and damaged, as GTWEAP 0 and 1: the whole building, the door shut, the
                                  lamps dark and the fans still. No destroyed frame (RA: healthy and damaged only).
                                  Damaged, as TS breaks it (GTWEAP 1): a hole torn in the green slope (its skin gone,
                                  the inside showing light grey and lilac-grey round a black void, as TS's; torn green
                                  edges bent in, bits fallen at its foot, soot round it); the west block dented all
                                  over, a scorched hole knocked into its south-west end, soot on the machinery below;
                                  the green unit on the south fender crumpled into a lump (its red band crushed out of
                                  sight) and scorched; scorch on the roof's machinery and deck, a housing burnt out; a
                                  chip knocked out of the south fender's foot. The door and the north fender are
                                  untouched, as in TS. Greys and browns only.
building-bay/war-factory-bay-00, -01
                                  The door bay alone, with the building's ground shadow: what TSWEAP.ZIP's frames are
                                  now (0000 healthy, 0032 damaged, i.e. GTWEAP less GTWEAP_2), drawn under units. TS
                                  angle: the door, the north fender and its cap (a unit leaving passes in front of
                                  them) and the floor's edge at the door's foot; RA grid: the door and the floor's
                                  edge.
2-over-units/war-factory-over-00..03
                                  GTWEAP_2: the rest of the building, drawn over units while one rolls out. 00
                                  healthy, 01 damaged, 02-03 empty as TS's. building-bay + 2-over-units = building,
                                  to the pixel (each pixel is in one of them).
1-under-door/war-factory-under-00, -01
                                  GTWEAP_1: the bay as it shows with the door rolled away (its floor, rails, walls and
                                  red lights; in the TS angle the north fender and its cap, as TS's), on a copy of the
                                  bib as TS's, with the building's ground shadow on that bib exactly as building-bay
                                  draws it. So it goes over building-bay without losing or doubling the shadow. Drawn
                                  at ground level, under units. RA grid (round 2): only the doorway (the shut door's
                                  outline 2 px wider), as the mod cut it.
D-door/war-factory-door-00..08    GTWEAP_D, the door: 00 shut .. 08 rolled up (TS's 9 frames). Drawn over everything,
                                  as TS's. One set for both states: TS's damaged building leaves the door as it is.
A-lamps/war-factory-lamps-00..31  GTWEAP_A, the five white lamps on the beam over the door: a light runs along them
                                  and back (00-15, TS's levels). 16-31 empty, as TS's: the damaged building's lamps are
                                  dark. RA grid (round 2): four lamps, the run as the mod reordered it.
B-lamps/war-factory-lamps-b-00..15
                                  GTWEAP_B, the three small lamps on the roof: the outer two and the middle one blink
                                  in turn, orange to red (00-07). 08-15 empty, as TS's.
C-fans/war-factory-fans-00..07    GTWEAP_C, the two roof fans turning (00-03). 04-07 empty, as TS's.
bib/war-factory-bib-00, -01       GTWEAPBB: the apron, healthy and damaged (cracks all over, its south and east edges
                                  broken away in bites, the stripes worn). Drawn under everything. TS's has 6 frames (3
                                  states + 3 empty); RA has no destroyed state.
build-up/war-factory-build-00..25
    26 frames in the order TS's GTWEAPMK builds it (TS's 20 real frames, spread over 26), plain MK grey like TS's
    until the end, all but the lamps, which glow as in TS's. 00-06: a grey construction slab spreads out from the
    middle of the foundation and the hall rises out of it with the door and its fenders. 07-11: the apron goes down
    and its lane stripes appear (08, black and white); the panel's frame rises up the slope, ribs in threes; the two
    poles lie at the south-west and are raised. 12-14: as TS does, the poles stand up tall at the top of the slope
    and tip back over the hall; the three small lamps (14). 15-20: the poles become the slope's edges and the roof
    beams, the roof goes on (the frame, the ridges and housings, the north band), the five lamps on the beam one by
    one, the north fender's cap, the green unit, and the panel's skin fills its frame (20). 21-23: the west block,
    then the fan platform with its fans. 24: the apron gets its colour; 25: the building (no frame is half grey, half
    house colour: the trim couldn't carry it). 25 is the finished building on its bib (bib-00 + building-00).
    TSWEAPMAKE.ZIP has 19 frames: drop 02, 05, 09, 13, 16, 20, 23 or play all 26 faster.
    RA grid (round 2): the poles lie along each slope's foot (north and south) and stand up there, both slopes' poles
    at once; the slab is the apron's outline.

How the layers stack (TS's order; the shadows are baked into building-bay, so keep it drawn under 1-under-door):
  idle                      bib, building-bay, A, B, C, with 2-over-units over units (or bib, building, A, B, C)
  door going up / down      bib, building-bay, 1-under-door, 2-over-units, D-door 00..08 / 08..00, A, B, C
  a unit rolling out        bib, building-bay, 1-under-door, the unit, 2-over-units, D-door 08, A, B, C
  With the door shut (D-door 00) that stack matches bib + building (previews/layers-*.png shows the check).

previews/  the building on its own; both states next to TS's; the mod's frames (tsweap-0000, -0032, tsweapmake-0018)
           next to the same HD frames; next to the Construction Yard, the Power Plant, the Component Tower and a GDI
           wall run (RA grid); the house colour next to the yard's; the build-up as a strip and a GIF against
           GTWEAPMK; the idle loop (A + B + C, healthy and damaged) against TS's; layers-ts-angle.png and
           layers-ra-grid.png (every layer on its own, and the stacks); door-vs-original.gif (the door going up and
           down over the bay, next to TS's own layers doing the same); exit-and-jambs.png (the exit and jambs on both
           views, on the mod's frame now, and the RA grid as 3x4 and 3x3).
3d/        war-factory.glb, the model itself (glTF 2.0 .glb: Blender, Godot and most engines open it), in its own frame
           (TS's way round: the door faces east, +x; the RA grid version is it turned a quarter clockwise seen from
           above). Meshes: "war-factory" and "war-factory-damaged" (without the door, so the bay shows), "door"
           (shut; both states), "bib" and "bib-damaged". Markers: "exit" (the door's middle at the floor), "bay-
           inside", "jamb-left" / "jamb-right" (seen from outside: left = TS's south fender, the west one on the RA
           grid), "lamp-a1".."lamp-a5", "lamp-b1".."lamp-b3", "fan-1", "fan-2". Cameras: "camera-ts-angle" (renders
           896x672 = the ts-angle frames) and "camera-ra-grid" (416x512 = round 1's ra-grid frames; RA's camera looks at
           the door). The .glb is round 1's model: TS's sides (the RA grid's round 2 mirror is a switch in weap.py's
           'ra' layout). The door's track is in the file's extras: straight up 40 units, then round a quarter circle of
           radius 49 centred 49 behind the door's face at height 40, into the roof.
           Axes: x east, y up, z south. 1.0 = one cell = 128 units = 128 px on the RA grid. Origin: the foundation's
           centre on the ground. COLOR_0 = the materials' colours (no light, shadow or outline baked in), COLOR_1 =
           house colour (white), like the -trim masks.
src/       Python 3 (numpy, scipy, Pillow, scikit-image for the 3D export). hd.py is the renderer, brender.py the views.
           weap.py         the model, its layouts ('ts', and 'ra' turned), the door's track, the build-up's parts
           weapmat.py      its materials and the lamps
           weapdamage.py   the damage
           weapbuild.py    the build-up (GTWEAPMK's order)
           weaprender.py   the views and canvases
           weapexport.py   3d/war-factory.glb (export3d.py: marching cubes over the model, colours on every vertex)
           tsgeo.py, weapplace.py, weapfit.py, weapcmp.py, weapshape.py: reading TS's frames, the in-mod placement
             fit, the fit and the shape check
             python3 weapfinal.py states|door|bib|under|build iso|ra [ss]   the frames (ss 4 used; states and bib
                                                                           before under)
             python3 cleanalpha.py <package>                               clears the faint ground haze (alpha < 8)
             python3 weapexport.py                                         3d/war-factory.glb
             python3 bdeliver.py weapspec previews                         the previews
