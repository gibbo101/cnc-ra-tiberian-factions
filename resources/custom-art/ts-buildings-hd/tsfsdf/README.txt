Tiberian Sun Firestorm Wall Section (Firestorm GAFSDF; TSFSDF in the mod) rebuilt for Red Alert Remastered (HD).

v2 (2026-10-03): checked frame by frame against TS's own GTFSDF / GTFSDF_A (previews/run-vs-original.gif,
sections-vs-original.gif) and brought closer to them: the live field now glows TS's strong blue and light blue (with
white glints and pure blue studs) over the pad's whole outer band and the whole grating, not a pale lilac; the dish
stays dark when it is on, as TS's; the gratings' rungs are TS's six chunky rungs to a cell, grey on top with
blue-lit faces, over dark gaps, with brackets on the rails; the emitter is TS's trident standing up in the dish
(three prongs, the middle tallest) instead of a flat mark, and GTFSDF_A's frame 02 lights its prongs, as TS's.

One 3D model fitted to TS's own sprites (GTFSDF, GTFSDF_A), one cell, joining its neighbours like a wall, rendered with
the same renderer as the Construction Yard and the rest (materials, light, shadow ~75% black, outline).

CANVAS     176x320 in both views, as the mod's (the Component Tower's): the cell at x 24-152, y 96-224, its ground
           centre at (88, 160).
ra-grid/   RA's wall view, as the GDI wall and the gates: looking north, the ground not foreshortened (a cell is
           128x128 px), heights up 0.6 px per unit; so sections join edge to edge on RA's square grid (see
           previews/firestorm-wall-runs-ra-grid.png).
ts-angle/  TS's own camera, lit from TS's side. TS's frame x3.5 (the cell's diamond 168 px wide, inside the canvas;
           the mod's frame is a placeholder, so there was no scale to keep), TS px (0, 0) at canvas (4, 34). These
           tile on TS's diamond grid (a cell east = +84, +42 px), not on RA's square one.
COLOUR     no house colour (TS's section has none); every frame still has its -trim.png (all black).

What it is (read from TS's frames):
  pad        a low lilac-grey steel pad in the middle of the cell, its rim raised, a light band round a dark dish in
             its middle; the emitter a trident standing in the dish (a short bar with three prongs, the middle
             tallest), facing the camera in each view as TS draws it face-on
  gratings   a grating bridge from the pad to the cell's edge on every side with a neighbour: steel rails with
             brackets on their outer sides, six chunky rungs to a cell (grey on top, their faces lit blue) over dark
             gaps; a section with neighbours on two opposite sides only is all grating, no pad (TS's 05, 10)
  field on   the pad's outer band and rim, the rails, the brackets and the whole grating glow blue and light blue with
             white glints, pure blue studs round the rim; the dish, the band round it and the trident stay as they are
             (TS's 32-47)

wall/firestorm-wall-00..63     TSFSDF.ZIP's layout: frame = the neighbour mask (N1 E2 S4 W8) + 16 damaged + 32 the field on.
                        Damaged (my own: TS's GTFSDF has healthy and rubble only): the pad's south-west corner chipped,
                        a crack across it, scorch round the dish, a dent in each grating (bars knocked down), soot,
                        steel bits. Greys and browns only.
A-pulse/firestorm-wall-pulse-00..07
                        GTFSDF_A: the emitter pulsing (00 as it is, 01 the ring round the dish glowing white with blue
                        studs on its inner edge, 02 the trident's prongs white, 03 the whole dish light blue with the
                        trident white), 04-07 empty, as TS's. Cut against wall-00: draw it over any section with a pad
                        (every mask but 05 and 10, the all-grating ones); it matches the field-on frames too (the dish
                        is the same in both).
No build-up: TS has none for its wall sections.

previews/  every frame of both views; TS's frames next to the HD TS-angle ones; runs on the RA grid (a ring, a T with
           the field on, a damaged cross, a line) next to a GDI wall run and the Component Tower; a ring in TS's angle
           next to TS's own sprites run the same way; pulse-vs-original.gif; run-vs-original.gif (a run three ways:
           TS's own frames on TS's grid, HD TS angle, HD RA grid; the field off, switching on with the pulse, off, then
           damaged); sections-vs-original.gif (every mask, off then on, TS | HD TS angle | HD RA grid at 2x).
3d/        firestorm-wall.glb: one mesh per kind of section (alone, end, straight, corner, T, cross: masks 0, 1, 5, 3,
           7, 15; the rest are these turned), 1.5 cells apart along x, the trident facing south. 3d/stl/: the same as print-ready STL (mm at 1
           cell = 32 mm, Z up, flat on Z = 0, watertight, thin parts thickened to 1 mm; README-stl.txt).
src/       Python 3 (numpy, scipy, Pillow). fsdf.py the model, fsdfmat.py its materials (the field, the pulse),
           fsdfdamage.py the damage, fsdfrender.py the views (the RA wall view: a camera at 59.04 degrees, cos/sin =
           0.6, stretched upright), fsdffinal.py the frames (walls|pulse iso|ra), fsdfexport.py the .glb, stlprint.py
           the STL, fsdfpack.py the previews and this package.

My calls (each easy to change):
  - RA grid in RA's wall view (like the GDI wall), so runs join; the TS-angle set tiles on TS's grid only.
  - The damaged frames are my own (TS has none for it).
  - TS angle at x3.5, so the cell fits the 176 px canvas.
  - The trident turns to face the camera in each view (TS draws it face-on); in the .glb it faces south (the RA grid's
    way).
