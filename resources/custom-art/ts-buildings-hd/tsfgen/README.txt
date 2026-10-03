Tiberian Sun Firestorm Generator (Firestorm GAFIRE; TSFGEN in the mod) rebuilt for Red Alert Remastered (HD).

One 3D model fitted to TS's own sprites (GTFIRE, GTFIREMK, GTFIRE_A, _B, _C), rendered two ways with the same renderer
as the Construction Yard, Power Plant, War Factory and the rest: same materials, light, shadow (baked in at ~75%
black) and outline. Fit to TS's frame: silhouette 0.92 (the main masses fitted pixel by pixel in TS's camera).

ts-angle/  TS's own camera, lit from TS's side so it reads like the sprite. CANVAS 384x384: the canvas, scale and place
           the generator has in the mod now (TS's frame x4.04, TS px (0, 0) at canvas (-146, -137), fitted to the mod's
           frames).
ra-grid/   On RA's square grid: RA's camera (orthographic, 32 degrees above the ground, looking north), the same way
           round as TS's (the fins west, the pit east, the hatch towards the camera). CANVAS 384x384: the 3x2 plot
           (384x256) at y 64-320, the foundation's south edge on the plot's, as the mod's canvas; everything (shadow
           included) inside.
COLOUR     Green = house colour: the fins' clamps, the hatch on the drum, the kerb behind it and the collar on the arm.
           Exactly the yard's green; detail on them only as thin seams. Every frame has a -trim.png (white = house
           colour, antialiased). The lamps, the ring's glow and the lightning are not house colour.

What it is (read from TS's frames):
  base       a low earthen slab with TS's outline (GTFIREMK's slab: a notch in its north edge, the corners cut)
  drum       the pit's round drum on the east half: ribbed brown sides, a wide flat grey-lilac steel ring on top, six
             steel struts leaning against it; the pit inside dark, the emitter standing in its middle (a column, a
             collar, four prongs)
  fins       two brown stone fins leaning back on the west half, steel-edged, green clamps round their feet, a lamp on
             each tip (GTFIRE_C)
  hatch      a green hatch lying on the drum's south slope, running out onto the base
  kerb       a green kerb on the base behind the drum
  arm, dome  (GTFIRE_A / _B) a dark crane arm turning in a housing on the back fin, a green collar on it, holding the
             dome (a tan stone lid with a grey cap) over the pit: closed (A 00, the end of the build-up), lifted
             68 units over A 00-19, raised in B

Each view has the same folders. Every frame is on the view's full canvas, in place, with a -trim.png.

building/firestorm-generator-00, -01
                                  healthy and damaged, as GTFIRE 0 and 1: the building without the arm and dome (TS
                                  draws those in GTFIRE_A / _B), the pit open. No destroyed frame (RA: healthy and
                                  damaged only). Damaged, as TS breaks it: the base's west end battered in front of the
                                  fins (bites out of its edge, a shallow crater, soot, rubble), the hatch punched in,
                                  the drum's east flank chipped and cracked, the front clamp sooted. Greys and browns
                                  only.
A-dome/firestorm-generator-dome-00..39
                                  GTFIRE_A: the arm lifting the dome off the pit (00 closed .. 19 raised, TS's pace: a
                                  slow start, steady, held at the top); 20-39 empty, as TS's. Drawn over the building.
B-lightning/firestorm-generator-lightning-00..31
                                  GTFIRE_B: the dome raised; even frames lightning crackling in the pit (blue-white,
                                  eight patterns), odd frames the ring glowing blue, as TS's; 16-31 empty, as TS's.
C-lamps/firestorm-generator-lamps-00..11
                                  GTFIRE_C: the lamps on the fins' tips flashing blue-white by turns (the front fin's
                                  at 05, the back fin's at 02, fading over three frames, TS's levels); 06-11 empty.
loop/firestorm-generator-loop-00..95
                                  TSFGEN.ZIP's layout (96 frames): 00-47 the healthy building with B (t % 16) and C
                                  (t % 6) playing, the dome raised, as the mod's idle; 48-95 the damaged building, as
                                  the mod's (it draws no overlays on it: TS's _A/_B/_C have no damaged frames).
                                  Straight renders, so they match the layers stacked.
build-up/firestorm-generator-build-00..18
    19 frames, as TSFGENMAKE.ZIP has (TS's GTFIREMK has 17), in TS's order: 00-03 the grey slab spreads out from the
    pit (a ring round it first); 04-05 the emitter rises in the pit; 05-07 the fins (grey); 06-08 the drum round the
    pit, 09 the struts and the hatch; 07-10 the colours come in (the house parts red-brown primer first, as TS's);
    11-15 the arm comes over high with the dome and lowers it onto the pit; 16 the house parts go green; 17-18 done,
    the dome closed (18 = building-00 + A-dome-00, as TS's MK ends).

How the layers stack:
  idle (the mod's)          building, B, C (= loop/ 00-47)
  switching on              building, A 00..19, then B, C
  the build-up's end        building + A 00 (the dome closed)
  damaged                   building-01 (= loop/ 48-95)

previews/  the building on its own; both states next to TS's (the idle overlays at 00); the mod's frames
           (tsfgen-0000, -0048, tsfgenmake-0018) next to the same HD frames; next to the Construction Yard, the Power
           Plant, the Component Tower and a GDI wall run (RA grid); the house colour next to the yard's; the build-up as
           a strip and a GIF next to TS's GTFIREMK; the idle loop (B + C, healthy and damaged) against TS's;
           layers-ts-angle.png and layers-ra-grid.png (every layer on its own, and the stacks); dome-vs-original.gif (A
           forward and back next to TS's); lightning-vs-original.gif (loop/ 00-47 next to TS's B + C).
3d/        firestorm-generator.glb, the model itself (glTF 2.0 .glb: Blender, Godot and most engines open it), in its own
           frame. Meshes: "firestorm-generator" and "firestorm-generator-damaged" (no arm or dome, as GTFIRE), "arm-dome"
           (the arm and the dome, closed). Markers: "arm-pivot", "pit" (the emitter's tip), "lamp-1" / "lamp-2". Cameras:
           "camera-ts-angle" and "camera-ra-grid" (384x384 = the frames). Axes: x east, y up, z south; 1.0 = one cell =
           128 units. COLOR_0 = the materials' colours, COLOR_1 = house colour (white).
3d/stl/    the same meshes as print-ready STL (3D printing): mm at 1 cell = 32 mm, Z up, the base flat on Z = 0; each
           one solid, watertight and checked; parts thinner than 1 mm thickened, plates on the bed at least 1.2 mm,
           loose specks dropped (README-stl.txt).
src/       Python 3 (numpy, scipy, Pillow, scikit-image for the 3D export). hd.py is the renderer, brender.py the views.
           fgen.py          the model (the arm and dome: arm = 0 closed .. 1 raised; bolt = the lightning's pattern)
           fgenmat.py       its materials, the ring's glow, the lightning, the lamps
           fgendamage.py    the damage
           fgenbuild.py     the build-up
           fgenrender.py    the views and canvases
           fgenfinal.py     the frames:  python3 fgenfinal.py states|dome|lightning|build iso|ra [ss]  (ss 4 used;
                            states first)
           fgenexport.py    3d/firestorm-generator.glb (export3d.py: marching cubes over the model)
           stlprint.py      3d/stl/ (the print-ready STL files)

My calls (each easy to change):
  - The RA grid version the same way round as TS's (no turn): the hatch faces the camera as it is.
  - The damaged building has no dome, as TS's and the mod's frames (TS's arm-and-dome layers have no damaged frames).
    Say if you want the dome on it too.
  - What TS shows at a few pixels: the arm turning in a housing on the back fin, a stone lid with a grey cap, the
    emitter (a column with four prongs), six struts round the drum, the lamps on the fins' tips.
