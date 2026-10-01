Tiberian Sun GDI Power Plant (GAPOWR, TSPOWR in the mod) and its power pods (the Power Turbine, TSTURB in the
mod) rebuilt for Red Alert Remastered (HD).

One 3D model fitted to TS's own sprites (GTPOWR, GTPOWR_A, GTPOWR_B, GTPOWRMK), rendered two ways with the same
renderer as the Construction Yard and the Component Tower: same materials, light, shadow (baked in at ~75% black)
and outline.

ts-angle/  TS's own camera, lit from TS's side so it reads like the sprite.
           CANVAS 256x256, the same canvas, scale and place as the building in the mod now
           (in-mod/tspowr-0000.png: TS's frame x3.36). Drops in over the current frames.
ra-grid/   Turned to sit on RA's square grid: an orthographic camera 32 degrees above the ground, looking north
           (the tower's, the walls' and the yard's camera). The cooling tower stands on the north-west cell, the
           three pod sockets on the other three.
           CANVAS 256x272: the 256 px of the plot plus 8 px top and bottom. The 2x2 plot is x 0-256, y 8-264, so
           its centre is the canvas centre (128, 136) and the game's centre-on-plot anchoring puts it right. The
           foundation's south edge sits on the plot's south edge; everything (shadow too) stays inside the canvas.
COLOUR     Green = house colour, kept green, exactly the yard's green (same colour and grain on every building,
           so the house colours come out the same). Every frame has a -trim.png (white = house colour,
           antialiased), the same as the tower's and the yard's.

PODS       The plant fills east to west: it comes with the east pod, the first Power Turbine upgrade fills the
           middle socket, the second the west one. So there are three looks: 1 pod (east), 2 (east, middle),
           3 (east, middle, west).
             east    TS angle: the right-hand socket   RA grid: the north-east cell (back right)
             middle  TS angle: the front socket        RA grid: the south-east cell (front right)
             west    TS angle: the left-hand socket    RA grid: the south-west cell (front left)

Each view has the same folders:

plant/power-plant-00.png       healthy, with its east pod (the turbine at rest, frame 00 of its turn).
plant/power-plant-01.png       damaged: the top of the cooling tower broken open with a scorched notch, a hole
                               burnt through the tower's side, soot streaks, cracks in the slab and the mounds,
                               chunks knocked off the middle socket's ring and the east and west mounds, one of
                               the west pipes snapped, rubble on the slab; the east pod sooted, its window band
                               dead. Greys and browns only. No destroyed frame: RA has healthy and damaged only.

loop/power-plant-loop-00..71.png
    Full frames with the animations baked in, laid out like TSPOWR.ZIP (its frame 0000 is the healthy plant
    with one pod and 0036 the damaged plant with two, which is this layout):
        00-11 1 pod healthy   12-23 1 pod damaged
        24-35 2 pods healthy  36-47 2 pods damaged
        48-59 3 pods healthy  60-71 3 pods damaged
    Each 12-frame block is one loop of the tower lights and the pods turning. Straight renders, so the pods'
    shadows on each other are exact. Drop-in for TSPOWR.ZIP.

build-up/power-plant-build-00..23.png
    24 frames, in the order TS's GTPOWRMK builds it, without TS's construction arm: the middle of the slab
    spreads, then the round pads (00-04); the dark drum rises on the tower's site (05-08); the east mound (it
    stays hollow), the green pipes and the decks (07-10); the cooling tower goes up course by course while the
    west mound and then the middle one rise (10-19); the east pod rises out of its mound, cap first, and its
    green ring comes round it (13-18), as in TS; the green collar (17-19); the rings and plates on the other two
    sockets (20-22). 23 is the finished plant (exactly power-plant-00). TSPOWRMAKE.ZIP has 13 frames: for 13,
    take 00, 02, 04 ... 22 and 23, or play all 24 faster.

Animation overlays, if you draw them over the plant rather than use loop/. Each holds only the pixels it
changes, on the plant's canvas, in place:
  A-lights/power-plant-lights-00..23.png         GTPOWR_A: the tower's lamps. Four rings of six lamps, lit
                                                 house green; a white-blue flash runs up the tower ring by ring
                                                 (bottom ring at frame 09, then 00, 03, 06), each fading over
                                                 three frames (12-frame loop). 00-11 healthy, 12-23 damaged (the
                                                 bottom ring works, one lamp left on the second ring and one on
                                                 the top ring, the third ring dead).
  B-pods/east/power-plant-pod-east-00..23.png    GTPOWR_B: the east pod turning (the window band and the
                                                 housing's hatches, 10 degrees a frame, 12-frame loop). Only its
                                                 moving parts. 00-11 healthy, 12-23 damaged (still turning; TS
                                                 has no damaged pod, so this one matches the damaged plant).
  B-pods/middle/power-plant-pod-middle-00..23.png  the middle pod (upgrade 1), whole, turning, with its shadow.
  B-pods/west/power-plant-pod-west-00..23.png      the west pod (upgrade 2), whole, turning, with its shadow.
  DRAW ORDER  the plant, B east, B middle (1+ upgrades), B west (2 upgrades), then A; all at the same frame
              number. Each pod is cut against the plant with the pods before it, so drawn in this order they
              give back the straight render (checked against loop/: the same but for a few antialiased edge
              pixels where the tower's lamps sit on its outline). The lights never overlap a pod.

pod-128/power-pod-00.png, power-pod-01.png
    The pod on its own 128x128 canvas, like the mod's TSTURB (2 frames: 00 healthy, 01 damaged): the turbine and
    its socket's green ring and plate, no shadow. The damaged one is sooted with its window band dead, on an
    intact ring. The TS-angle piece is cut from the plant's canvas at (147, 97), the window where the
    mod's tsturb-0000 matches the east pod on tspowr-0000, so it sits exactly where TSTURB sits now (socket
    centre at (64.9, 72.1) on the 128 canvas). The RA-grid piece has its socket centre on the same spot.
    Top-left of the 128 canvas on the plant's canvas, per socket:
      TS angle: east (147, 97), middle (66, 137), west (-14, 97)
      RA grid:  east (127, 69), middle (127, 137), west (-1, 137)
    (for the west socket the window starts left of the plant's canvas; the pod itself stays inside it.)
pod-128/turning/power-pod-turn-00..23.png
    The same piece turning (00-11 healthy, 12-23 damaged), if you'd rather animate TSTURB.

previews/  the plant on its own; both states next to TS's; the mod's frames 0000 and 0036 next to the same loop
           frames; next to the Construction Yard, the Component Tower and a GDI wall run (RA grid); the house
           colour next to the yard's; the pod piece vs the mod's TSTURB (and on the middle socket vs the
           overlay); the build-up as a strip and a GIF against GTPOWRMK; the idle loop (healthy and damaged)
           against TS's own animations; one, two and three pods (healthy and damaged). The GIFs are built from
           this package's frames and overlays, drawn the way the game draws them.
src/       Python 3 (numpy, scipy, Pillow). hd.py is the renderer (walls2.py gives the light and materials).
           powr.py is the model, pmat.py the materials, pdamage.py the damage, panim.py the animations,
           pbuild.py the build-up.
           python3 pfinal.py states|piece|build iso|ra [ss]   makes the frames (ss 4 = supersampling used here)
           python3 pdeliver.py previews                        makes the previews
           python3 pcheck.py                                   checks the package
