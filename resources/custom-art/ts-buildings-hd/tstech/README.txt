Tiberian Sun GDI Tech Center (GATECH, TSTECH in the mod) rebuilt for Red Alert Remastered (HD).

One 3D model fitted to TS's own sprites (GTTECH, GTTECH_A, GTTECHMK), rendered two ways with the same renderer as
the Construction Yard, the Power Plant, the Barracks, the Silo and the Component Tower: same materials, light,
shadow (baked in at ~75% black) and outline.

ts-angle/  TS's own camera, lit from TS's side so it reads like the sprite.
           CANVAS 384x384, the same canvas, scale and place as the building in the mod now
           (in-mod/tstech-0000.png: TS's frame x3.73). Drops in over the current frames.
ra-grid/   On RA's square grid: an orthographic camera 32 degrees above the ground, looking north (the camera of
           the tower, the walls and the other buildings). TS's own building turned a quarter so it is long and
           thin on a 2x3 (2 wide, 3 deep): its narrow end to the north, its wide east end to the south facing the
           camera; the dome and the fins exactly where TS has them on the building (the dome off to the side, on
           the back face, as TS's).
           TSTECH's foundation in the rules needs to be 2x3 for this version.
           CANVAS 256x512 with the 2x3 plot at x 0-256, y 64-448. The foundation's south edge sits on the plot's
           south edge; everything (shadow too) stays inside.
COLOUR     Green = house colour (the dome's panels and the two fins), exactly the yard's green. Every frame has
           a -trim.png (white = house colour, antialiased).

What it is (read from TS's frames; GTTECHMK's first frames draw its outline): a wedge, triangular in plan (TS's
is a right triangle: the long south face, the east face, and the back face running from the north-east corner to
the narrow west end). Its sides step back in three terraces of louvred bands (sand and brown between grey
frames); a flat sandy roof inside a grey parapet. The east face (the wide end): the same louvred terraces along
its southern part, a short recessed grille of vertical struts in the middle, a plain grey sloping batter into the
sharp north-east corner. A big geodesic dome on the roof's back, partly over its back edge as TS's: green
triangular panels in brown struts. Two green fins straddle the narrow end: each solid and symmetric, TS's shape - straight sides rising
from the ground on either side of the building to a flat top over it - its faces ribbed (in
TS they cross square to the back face, so TS's camera sees them almost edge-on, as two tall narrow shapes).

Each view has the same folders:

building/tech-center-00.png   healthy
building/tech-center-01.png   damaged: TS's hole in the dome - one ragged hole high on the side facing the camera,
                              left of the top, its struts still across it, the inside of the far side dark green
                              through it (house colour, in the trim) - with TS's cracks running out of it; two
                              holes burnt through the roof, soot, the grille buckled (a run of struts gone),
                              cracks, rubble. Each view sees the hole as TS's camera does. No destroyed frame: RA
                              has healthy and damaged only.

loop/tech-center-loop-00..15.png
    Full frames with GTTECH_A baked in, laid out like TSTECH.ZIP (its frame 0000 is healthy and 0008 damaged):
    00-07 healthy, 08-15 damaged. Drop-in for TSTECH.ZIP.

build-up/tech-center-build-00..23.png
    24 frames, in the order TS's GTTECHMK builds it: the wedge rises terrace by terrace (00-05), the grille and
    the roof go on (03-07); the first fin is tipped up from lying over the roof to upright, about the line
    through its feet (08-11), then the second (11-14);
    the dome goes up as bare struts from its base ring to the top, see-through (13-18); its panels go in, green,
    one by one (18-22). 23 is the finished building (exactly tech-center-00). TSTECHMAKE.ZIP has 19 frames:
    drop five evenly (02, 07, 12, 17, 21) or play all 24 faster.

Animation overlay (if you draw it over the building rather than use loop/); it holds only the pixels it changes,
on the building's canvas, in place:
  A-dome/tech-center-dome-00..15.png   GTTECH_A: 00-07 healthy, the dome's panels pulse: all of them brighten
                                       together and fade back (8-frame loop), as TS's do; 08-15 damaged, as
                                       TS's: on every other frame light flashes out of the hole and along its
                                       cracks (08 a few points, mostly blue; 10 all white; 12 white and blue;
                                       14 more blue), quiet in between; the other panels flicker one by one.
                                       The light is not house colour (left out of the trim).

previews/  the building on its own; both states next to TS's; the mod's frames 0000 and 0008 next to the same loop
           frames; next to the Construction Yard, the Power Plant, the Component Tower and a GDI wall run (RA grid);
           the house colour next to the yard's; the build-up as a strip and a GIF against GTTECHMK; the idle loop
           (healthy and damaged) against TS's own animation.
src/       Python 3 (numpy, scipy, Pillow). hd.py is the renderer, brender.py the views. tech.py is the model (and
           its layouts: TS's own, turned 2x3, TS's way round 3x2), techmat.py the materials, techdamage.py the
           damage, techbuild.py the build-up, techrender.py the views.
           TECH_RA=rot|ts3x2 python3 techfinal.py states|build iso|ra [ss]   makes the frames (ss 4 used here)
           TECH_RA=rot|ts3x2 python3 bdeliver.py techspec previews             makes the previews
