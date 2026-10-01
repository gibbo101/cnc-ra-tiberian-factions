"""Package spec for the Tiberium Refinery and the Harvester (bdeliver.py)."""
import procpreview as PP

HAND = '/home/claude/work/ts/ts-buildings-hd-handoff/04-TSPROC'


def readme():
    return """Tiberian Sun Tiberium Refinery (PROC, art NAREFN; TSPROC in the mod) rebuilt for Red Alert Remastered (HD),
with the TS Harvester (HARV and HORV; TSHARV in the mod) and the docking.

One 3D model of each, fitted to TS's own sprites and voxels (NTREFN, NTREFNMK, NTREFNBB, NTREFN_A/_B/_C; HARV.VXL,
HORV.VXL) and to how TS docks (OpenTS's code and manual, and your docking video). Rendered two ways with the same
renderer as the Construction Yard, Power Plant, Barracks, Silo, Tech Center and Component Tower: same materials,
light, shadow (baked in at ~75% black) and outline.

ts-angle/  TS's own camera, lit from TS's side so it reads like the sprite. CANVAS 736x928: the canvas, scale and
           place of the refinery in the mod now (in-mod/tsproc-0000.png is TS's frame x4.1). Drops in over the current
           frames.
ra-grid/   On RA's square grid: an orthographic camera 32 degrees above the ground, looking north (the camera of the
           tower, the walls and the other buildings). TS's building the same way round, with the dock on the east side
           as in TS and as your plot keeps it, on the 4x3 plot. CANVAS 736x928 with the plot at x 112-624, y 272-656,
           as now. The foundation's south edge sits on the plot's south edge, and everything (shadow, the fire, the bib,
           the docked harvester) stays inside: x 69-628, y 195-669 (TS angle: x 98-644, y 10-611).
           TS's exact shape on both views: with the harvester at TS's own size (your call) it backs in under TS's deck as
           TS's does, so the deck no longer needs raising.
COLOUR     Green = house colour: the sixteen ribs, the deck's rim and edge band, the two dock lamps, and the harvester's
           cab and the posts at its tank's back. It is exactly the yard's green. Every frame has a -trim.png (white =
           house colour, antialiased). The dock
           lamps are house colour because TS's are (NTREFN_C draws them in remap greens). At their white flashes, the
           hot core is left out of the trim.

What it is (read from TS's frames; NTREFNMK's first frames show how it goes together):
  the umbrella  a round black deck on a skirt that slopes to the ground all round, sixteen green ribs down it, grey
                plates between them; a green edge band and rim round the deck
  the dock      the skirt cut open on the east, between two ribs, from the ground up under the deck: the harvester
                backs in there. A rust-red wall on its north side, dark behind. The two dock lamps on the deck's edge
                band either side of it
  stacks        the flare stack at the back (a copper cone, the light steel stack with two collars, a black pipe beside
                it), two columns on the deck (one flanged, on a gold ring; the tall one with a black pipe bent over to a
                post, two black links between them), thin pipes on the west. The flare stack and both columns are open
                pipes: a light rim round a black hole on top, as TS's
  the sphere    a copper sphere with a white cap on the east, behind the dock
  the bib       (NTREFNBB) a concrete apron over the east half of the plot, round the skirt's foot and in under the
                deck in the dock; hazard stripes on the dock's lane

Each view has the same folders:

building/refinery-00.png   healthy (the dock lamps as at NTREFN_C's frame 0)
building/refinery-01.png   damaged, as TS breaks it: the flanged column snapped above its upper collar and the tall one
                           two thirds of the way down (its pipe a stub, the upper link gone). A hole torn in the sphere's
                           top with the dark inside showing, and its cap knocked off, lying on the skirt in front. The
                           front skirt panels south-west of the dock stove in (torn holes, the ribs over them broken, a
                           piece lying across the panel below) and the deck's rim broken above them. Soot, cracks, rubble
                           round the foot. No destroyed frame: RA has healthy and damaged only.
bib/refinery-bib-00, -01   NTREFNBB: the apron, healthy and damaged (cracks, a hole knocked out of its east end, its
                           south-west corner broken). It is drawn under the building, as TS draws a bib. TSPROC.ZIP's
                           frames have no bib, so it is a separate layer here.
loop/refinery-loop-00..31  Full frames with NTREFN_C (the dock lamps) baked in, laid out like TSPROC.ZIP: 00-15 healthy,
                           16-31 damaged (its 0000 and 0016). Drop-in for TSPROC.ZIP.
build-up/refinery-build-00..23
    24 frames in the order TS's NTREFNMK builds it. 00: the sixteen ribs lying flat on the ground (a starburst). Then
    they are raised, with the deck's green ring on their tops (01-02). The skirt's panels go in and the deck goes on,
    first as spokes and then as a plate from the middle out; the dock's stripes appear and the copper cone rises
    (02-05). The flare stack rises out of the cone, its collars going on as it passes them (05-13), and the thin pipes
    go up on the west (08-10). The flanged column and the tall one rise from the deck (09-17), then the sphere rises
    out of the skirt and its cap goes on (15-18). Last, the bib goes down plain and its concrete and stripes come up,
    with the gold ring, the black pipes and links, and the dock lamps (16-23). 23 is the finished building on its
    bib (refinery-00 over bib-00).
    The bib is in these frames, as in TS's NTREFNMK and in TSPROCMAKE.ZIP now. TSPROCMAKE.ZIP has 19 frames: drop five
    evenly (02, 07, 12, 17, 21) or play all 24 faster.

Overlays: each holds only the pixels it changes, on the building's canvas, in place.
  C-lamps/refinery-lamps-00..31   NTREFN_C, the two dock lamps blinking together (a 16-frame loop: up, a white flash,
                                  fading, dark, up, a flash...). 00-15 are over the healthy building, 16-31 over the
                                  damaged one. In TS it plays all the time.
  B-fire/refinery-fire-00..39     NTREFN_B, a burst of flame out of the flare stack's hole, rebuilt in HD: 00-19 the
                                  flame, 20-39 empty as in TS (its shadow half) and as in TSPROCFR now. TS's timing and
                                  size frame by frame (it flickers up, stands as a full plume leaning a little to the left,
                                  then thins to a last wisp), drawn as real fire: tongues torn by turbulence rising
                                  through it, a white-yellow core low down through yellow and orange to deep red tips, a
                                  faint warm haze round it. Not house colour. In TS it bursts every few seconds at random,
                                  docked or not (your video shows it before, during and after the docking); the mod plays
                                  it while unloading. Either works: each burst is complete.
  A-lid/refinery-lid-00..09       NTREFN_A, the harvester's tank sliding off its bed into the building: 00 the tank on
                                  the truck, then 01-04 sliding back into the dock (a sliver left at 04), 05-09 empty as
                                  in TS and as in TSPROCLD now. It is cut against the building with HORV docked in it, so
                                  HORV + 00 = HARV, to the pixel.
  D-docked/refinery-docked-00..03 The docked harvester drawn by the refinery, in the scene, so that the building hides
                                  its back end as TS's does and their shadows fall on each other. 00 HARV (loaded, as it
                                  arrives), 01 HORV (unloading); 02 and 03 the same over the damaged building.
  ra-grid/A-lid-unit/refinery-lid-unit-00..09
                                  The lid for the other way round (the unit kept visible over the building): HORV with
                                  the tank sliding off it, cut against the HORV sprite alone, where the docked unit's
                                  sprite is (below). Not needed if the refinery draws the docked harvester.

harvester/harvester-00..63.png    The TS Harvester in HD, on the mod's 384x384 unit canvas, laid out like TSHARV.ZIP:
    00-31 are HARV's 32 facings and 32-63 HORV's (the truck with its tank off, which TS draws while it unloads). Frame 0
    faces north, then each frame turns a 32nd counter-clockwise (08 west, 16 south, 24 east), as the mod's do. It uses
    RA's camera (32 degrees, looking north), at TS's own size (your call): 3.46 units per voxel (fitted to your video),
    with 1 cell = 128 units, so it matches the refinery; the mod's TSHARV is drawn 1.32x that. The truck is where TSHARV
    has it on the canvas (its position at (188, 214.5)), so the frames drop in over TSHARV.ZIP (the truck smaller).
    Built voxel by voxel from HARV.VXL / HORV.VXL (their sizes, steps and colours):
      wheels    five a side, dark olive tyres with grey hubs
      tank      (HARV) a box with bevelled top edges, four hoops arched over the middle of its top, a dark panel let
                in along each side between light frames, two house-colour posts either side of a pale door at its back
      neck      grey, a dark olive engine block along its top
      cab       house colour, its front sloping down; a black windscreen across the slope and round the front corners,
                small side windows, a pale panel on the roof
      front     a grey scoop plate and four claws
      bed       (HORV) where the tank was: a tread plate, a lower tailgate at the back, the tank's front frame kept
    House colour: the cab and the tank's back posts (in the trim). Lit like the buildings, plus a soft fill from the
    camera on the sides facing it, as EA's HD units have (the north-west light alone leaves a unit's near side dark).

THE DOCKING (as TS does it, from OpenTS and your video)
  The harvester drives to the foundation's cell (2, 1), counted from its north-west corner: the dock lane, the third
  column of the 4x3. In your video it comes in facing west, then turns round on the spot through south to face east
  (TS: DIR_E, the mod's frame 24), which puts its back end in the dock under the deck's edge. When it starts
  unloading, TS swaps it to HORV and the refinery plays NTREFN_A (the tank slides off into the building). It stays like that while it unloads. When it's done, the refinery plays NTREFN_A
  backwards (TS's NAREFN_AR: the tank slides back out), TS swaps it back to HARV, and it leaves. The harvester waits for
  that reverse to finish.
  One thing your video shows: TS never actually shows NTREFN_A. The tank vanishes the moment HARV turns into HORV
  (video frame 85) and is back the moment HORV turns into HARV (frame 305); TS's depth test hides the anim inside the
  dock. The mod draws TSPROCLD, so there the tank visibly slides in, which is what NTREFN_A was drawn to show. To
  match TS exactly instead, leave A-lid out: D-docked 00 -> 01 -> 00 is TS's swap.

  Where it docks (both views: TS's own spot, the harvester at TS's size, facing east):
    TS angle  6 units east of cell (2, 1)'s centre, in TS's camera.
    RA grid   the same spot, nudged under a unit so the unit's 384x384 sprite lands on whole pixels: (250, 340) on the
              refinery's canvas. Its centre (442, 532) is 74 px east and 68 px south of the plot's centre (368, 464):
              +0.578, +0.531 cells, or +148, +136 leptons, if the mod centres a unit's sprite on its position. The
              truck itself, the sprite's (188, 214.5), is at (438, 554.5). 3d/refinery.glb's "dock" marker is this spot.

  Two ways to play it. Pick one:
    A  The refinery draws the docked harvester (recommended; you're redoing the docking anyway). This is how your TD
       refinery does it: the unit is hidden while it is docked. Both views.
         arrives, turned east  -> hide the unit; draw D-docked 00 (healthy) or 02 (damaged)
         starts unloading      -> D-docked 01 / 03, with A-lid 00..04 over it
         unloading             -> D-docked 01 / 03 alone
         done                  -> A-lid 04..00 over D-docked 01 / 03, then D-docked 00 / 02; show the unit again
       The building hides the truck's back end, as in TS.
    B  The unit stays visible over the building. RA grid only (the mod's harvester is drawn in RA's camera).
         the unit at the dock as above, HARV (frame 24) then HORV (56) while it unloads, with A-lid-unit 00..04 / 04..00
         drawn over the unit
       Here the whole truck is drawn over the building, so its back end shows in front of the skirt.
  In the TS-angle view, D-docked and A-lid show the harvester in TS's camera; the mod's units are drawn in RA's camera,
  so a swap there shows a change of angle. The RA-grid version is the one the mod's harvester frames match.

previews/  the building on its own; both states next to TS's; the mod's frames 0000 and 0016 next to the same loop
           frames; next to the Construction Yard, the Power Plant, the Component Tower and a GDI wall run (RA grid);
           the house colour next to the yard's; the build-up as a strip and a GIF against NTREFNMK; the idle loop
           (healthy and damaged) against TS's own animation;
           docking-ra-grid.gif (both ways side by side: the unit arrives, turns, docks, unloads and leaves) with key
           frames; docking-ts-angle.gif; docked-ts-angle-vs-video.png (the docked harvester next to TS's in your
           video); lid-vs-original.png; fire-vs-original.gif; harvester-sheet.png (all 64); harvester-vs-mod.png
           (the mod's TSHARV next to the same frames); idle-healthy-with-fire.gif and idle-damaged-with-fire.gif (the
           lamps and the flame playing together).
3d/        The models themselves, for placing, docking and rendering your own angles (glTF 2.0 .glb: Blender, Godot and
           most engines open them):
           refinery.glb    "refinery" and "refinery-damaged", each with its bib ("bib", "bib-damaged"); marker nodes
                           "dock" (where the harvester's origin goes, facing east), "fire" (the flare stack's mouth),
                           "lamp-north", "lamp-south" (the dock lamps)
           harvester.glb   "harvester" (HARV), "harvester-unloading" (HORV) and "tank" (the lid: harvester = unloading
                           + tank), facing east (+x), the unit's position at the origin, at TS's size
           Axes: x east, y up, z south (toward the RA camera). Scale: 1.0 = one cell = 128 units = 128 px on the RA grid.
           A building's origin is its foundation's centre on the ground. Meshes: COLOR_0 = the materials' colours
           (albedo: no light, shadow or outline baked in), COLOR_1 = house colour (white), like the -trim masks.
           Suggested cameras (what the frames here use): RA grid, orthographic, 32 degrees above the ground, looking
           north, 128 px per cell, light from the north-west and above; TS angle, orthographic, 30 degrees above the
           ground, looking north-west, at the in-mod scale (TS's frame x4.1). Unit facings: frame f = the model turned
           (f - 24) x 11.25 degrees counter-clockwise seen from above (0 north, 8 west, 16 south, 24 east).
src/       Python 3 (numpy, scipy, Pillow, scikit-image for the 3D export). hd.py is the renderer, brender.py the views.
           proc.py         the refinery model, its layouts and the dock (DOCK, the lid's and the docked truck's args)
           procmat.py      its materials, the lamps
           procdamage.py   the damage
           procbuild.py    the build-up
           procrender.py   the views and canvases
           procfire2.py    the HD flame (procfire.py was the first, TS's shapes upscaled)
           export3d.py     the .glb export (marching cubes over the model, the materials on every vertex);
                           procexport.py writes this building's
           harv.py         the harvester model, with harvmat.py (materials) and harvrender.py (the 384x384 unit canvas)
           vxl.py          reads TS's VXL / HVA
             python3 procfinal.py states|bib|dock|lid|fire|build iso|ra [ss]   makes the refinery's frames (ss 4 used)
             python3 procfinal.py lidunit ra [ss]                              A-lid-unit
             python3 harvfinal.py [ss]                                         the harvester's 64 frames
             python3 procexport.py                                             3d/*.glb
             python3 bdeliver.py procspec previews                             the previews
"""


SPEC = dict(
    name='refinery', title='Tiberium Refinery', pkg='/home/claude/work/out/ts-tiberium-refinery-hd', hand=HAND,
    ts='NTREFN', K=4.1, O=(-69.4, -44.7), iso_size=(736, 928), ra_size=(736, 928), ra_head=272, ra_left=112,
    cells=(4, 3), state_dir='building',
    under=[dict(folder='bib', prefix='bib', ts_shp='NTREFNBB')],
    overlays=[dict(folder='C-lamps', prefix='lamps', n=16, ts_shp='NTREFN_C', ts_frame=lambda t, lv: t % 16)],
    loop=dict(n=16), inmod=[('tsproc-0000.png', 0, 0), ('tsproc-0016.png', 1, 0)],
    build_n=24, ts_mk_n=20, idle_n=16, idle_label='building + C (the dock lamps)', idle_ms=90,
    crop={'iso': (72, 40, 680, 640), 'ra': (50, 220, 664, 688)},
    zoom=1, green_zoom=1, gif_zoom=0.62, strip_w=256,
    extra_previews=PP.EXTRAS,
    src=['hd.py', 'walls2.py', 'wnoise.py', 'brender.py', 'pfinal.py', 'pdamage.py', 'powr.py', 'pmat.py', 'prender.py',
         'panim.py', 'pbuild.py', 'proc.py', 'procmat.py', 'procdamage.py', 'procbuild.py', 'procrender.py', 'procfire.py',
         'procfinal.py', 'harv.py', 'harvmat.py', 'harvrender.py', 'harvfinal.py', 'vxl.py', 'bdeliver.py', 'procspec.py',
         'procpreview.py', 'ypreview.py', 'procfire2.py', 'export3d.py', 'procexport.py', 'export_all.py'],
    readme=readme,
)
