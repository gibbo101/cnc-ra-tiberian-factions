Tiberian Sun Service Depot (GADEPT, art GTDEPT; TSDEPT in the mod) rebuilt for Red Alert Remastered (HD).

One 3D model fitted to TS's own sprites (GTDEPT, GTDEPTBB, GTDEPTMK, GTDEPT_A to _D), rendered two ways with the same
renderer as the Construction Yard, Power Plant, Barracks, Silo, Tech Center, Refinery, War Factory, Radar, Helipad and
Component Tower: same materials, light, shadow (baked in at ~75% black) and outline. Fit to TS's frame in TS's own
camera: silhouette 0.95 (shape-check.png). Made overnight without your shape check: my calls are listed at the end.

ts-angle/  TS's own camera, lit from TS's side so it reads like the sprite. CANVAS 384x384: the canvas, scale and place
           the depot has in the mod now (TS's frame x4.445, TS px (0, 0) at canvas (-97, -243), fitted to
           in-mod/tsdept-0000.png, IoU 0.99). Drops in over the current frames. (TS's wall touches the canvas's west
           edge in the mod's frames; so does ours.)
ra-grid/   On RA's square grid: RA's camera (orthographic, 32 degrees above the ground, looking north), turned a quarter
           (TS's east is RA's south): the gantry stands along the plot's north edge facing the camera, the pad in front
           of it, the arm swings out over the pad towards you. CANVAS 384x384 = the 3x3 plot, the foundation's south
           edge on the plot's.
COLOUR     Green = house colour: the band on the pad, the gantry's base plate, its panel and the green edge at its south
           end, the repair arm. Exactly the yard's green. Every frame has a -trim.png (white = house colour,
           antialiased).

What it is (read from TS's frames; GTDEPTMK shows how it goes together):
  pad        (GTDEPTBB) a big low platform over the middle of the foundation: an octagon with its corners cut a little,
             10 high, sloped sides; an octagonal house-green band inset on its top; lavender-grey concrete inside it,
             two steel gratings along its west side, painted guide lines of small lamps (GTDEPT_A runs a light along
             them); a tan rim outside the band. As TS draws it, its centre is a little south-east of the foundation's.
  gantry     (GTDEPT) along the foundation's west edge: a green base plate on the ground; a wall on its west edge, light
             grey at its south end, mid grey at its north end, a house-green panel in the middle, a dark top rail with
             amber lamps; its top slopes down at the south end, a green edge there; a brown reel at its foot
  machine    in front of the wall: a dark block with two white arched hoods facing the pad (GTDEPT_B lights the inside
             of the south one); a small box with a red light north of it
  arm        (GTDEPT_C) a green lattice boom that rises out of the machine, swings over towards the pad and lowers a grey
             tool onto the vehicle (a spark), swings back and sinks into the machine again

Each view has the same folders. Every frame is on the view's full canvas, in place, with a -trim.png.

bib/depot-bib-00, -01           GTDEPTBB: the pad, healthy and damaged. Drawn under everything. (TS's 3rd frame is the
                                destroyed state: RA has none.)
building/depot-00, -01          GTDEPT: the gantry and machine (arm folded away), healthy and damaged, cut against the
                                pad (its shadow on the pad included), so bib + building = the whole depot.
                                Damaged, as TS breaks it: the pad cracked all over, a blast in its north-east quarter
                                (its slabs broken, sunk and tilted, scorched, rubble on them), a smaller scorch on the
                                gratings, its west and north-east corners knocked off; the wall's north end broken off
                                at the top (through the rail and its lamps); the north hood dented, a hole in its front;
                                soot. Greys and browns only.
A-lights/depot-lights-00..19    GTDEPT_A: the light running along the pad's guide lines. 00-04 healthy, 05-09 damaged,
                                10-19 empty, as TS's 20.
B-glow/depot-glow-00..13        GTDEPT_B: the south hood's inside lit white and fading. 00-06, 07-13 empty, as TS's 14
                                (TS has one set for both states; so do these).
C-arm/depot-arm-00..31          GTDEPT_C: the repair arm. 00-02 it rises, 03-04 swings over, 05-10 the tool down on the
                                vehicle (06 a spark), 11-12 back up, 13 upright, 14-15 it sinks back; 16-31 empty, as
                                TS's 32 (one set for both states, as TS's). The arm itself is copied; its shadow is a
                                dark see-through layer, so it darkens whatever is under it and plays over the damaged
                                depot too.
D-flash/depot-flash-00..27      GTDEPT_D: the pad lit white inside its band, fading over 7 frames (while it repairs).
                                00-06 healthy, 07-13 damaged, 14-27 empty, as TS's 28.
loop/depot-loop-00..69          the mod's TSDEPT.ZIP layout: 35 healthy + 35 damaged, A and B playing together (frame t:
                                A t mod 5, B t mod 7; 35 = 5 x 7, so it loops seamlessly). That is how tsdept-0000 and
                                -0035 are made (A 00 + B 00, A 05 + B 00 on the damaged depot). Straight renders.
build-up/depot-build-00..18     19 frames in the order TS's GTDEPTMK builds it (TS's 10 frames, spread over 19, as
                                many as the mod's TSDEPTMAKE.ZIP): the
                                base plate and the reel; the pad laid from the gantry's side across to the north-east
                                (plain grey); the wall lying flat in front of its foot, raised (a green plate, then a
                                braced frame); the hoods come up and the box; the wall stands with its panel, rail and
                                lamps (12); the pad coloured, its band painted (14); 18 is the finished depot.

Stacking: bib, building, then the overlays (A, B; C and D while it repairs). bib + building + A t + B t = loop frame t.

previews/  the depot on its own; both states next to TS's; the mod's frames (tsdept-0000, -0035, tsdeptmake-0018) next
           to the same HD frames; next to the Construction Yard, the Power Plant, the Component Tower and a GDI wall run
           (RA grid); the house colour next to the yard's; the build-up as a strip and a GIF against GTDEPTMK; the idle
           loop (A + B, healthy and damaged) against TS's; the arm and the flash against TS's; shape-check.png (the
           model in TS's own camera over TS's frame).
3d/        depot.glb (glTF 2.0 .glb), in its own frame (TS's way round). Meshes: "pad" / "pad-damaged" (the bib),
           "depot" / "depot-damaged" (the gantry), "arm" (the boom and its tool as at C 05-10, tipped 53 degrees towards
           the pad about the "arm-pivot" marker's north-south axis; upright at C 00-02 and 13). Markers: "arm-pivot", "pad-centre". Cameras: "camera-ts-angle" and
           "camera-ra-grid" (384x384 each = the delivered frames; the RA one looks along TS's west, as the RA grid
           frames are turned). Axes: x east, y up, z south; 1.0 = one cell = 128 px on the RA grid; origin the
           foundation's centre on the ground. COLOR_0 = the materials' colours, COLOR_1 = house colour (white).
src/       Python 3 (numpy, scipy, Pillow, scikit-image for the 3D export). hd.py is the renderer, brender.py the views.
           dept.py (the model, the arm's poses, the build-up's stages), deptmat.py (materials, the A/B/D overlays),
           deptdamage.py, deptbuild.py (GTDEPTMK's order), deptrender.py (views), deptfinal.py (frames), deptexport.py
           (3d), deptspec.py, deptgeo.py / deptfit.py (reading TS's frames, the fit).
             python3 deptfinal.py states|arm|build iso|ra [ss]   the frames (ss 4 used)
             python3 cleanalpha.py <package>; python3 deptexport.py; python3 bdeliver.py deptspec previews

My calls (made overnight, without your shape check; each easy to change):
  - RA grid turned a quarter: TS's wall runs north-south, and on RA's camera it would be seen edge-on (its panel
    invisible). Turned, it stands at the back facing the camera, like RA's own service depot's machinery.
  - TS's sprite can't show depth: the pad's top is 10 high, which puts its centre 12 units south-east of the
    foundation's (where TS's ring is centred on screen); the wall stands on the foundation's west edge.
  - The arm's pivot and reach are read off GTDEPT_C (the boom 100 long, the tool 46): it reaches the vehicle's top over
    the pad's west part, as TS's spark does.
  - B has one set for both states, as TS's; the loop is A + B (see loop/); C and D are left to the mod (they play while
    it repairs; TS's D has a damaged half, C doesn't).
