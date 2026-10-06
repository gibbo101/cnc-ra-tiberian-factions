---
name: "ts-to-ra-hd-art"
description: "Use when rebuilding Tiberian Sun buildings, units, walls or structures as HD art (128 px/cell) for a C&C Remastered Red Alert mod such as Tiberian Factions, on RA's square grid (fitted to TS's sprites in TS's own camera), with their 3D models."
---

# Tiberian Sun -> Red Alert Remastered HD art

Tiberian Factions ports GDI and Nod from Tiberian Sun into Red Alert (C&C Remastered Collection). Each TS asset is
rebuilt as a simple 3D model fitted to the TS sprites (or voxels) and rendered in HD so it matches the Remastered
RA/TD look and the assets already made: the TS GDI wall and TS Nod wall (64-frame BRIK format), the faction gates,
the GDI Component Tower, Construction Yard, Power Plant (+ power pods), Barracks, Tiberium Silo, Tech Center,
Tiberium Refinery and the TS Harvester; and the units: Titan, Wolverine, MCV, Mammoth Mk. I and Mk. II, and the
voxel vehicles and aircraft after them.

Match TS frame by frame: every detail TS shows is expected, and nothing TS doesn't have. Catch differences
yourself first (the inventory, the shape check and the self-review below). The yard and the plant are the
quality bar: buildings made unattended (barracks, tech) came out a dip below it because proportions were
fitted instead of TS's actual shapes being read. Hold every building to the yard's standard, unattended or
not, and never invent a detail or its placement: only what TS's art, TS's voxels or a Westwood render shows.

## Start of a task
- Sessions don't share files. Check for (or ask for) the attachments. The scripts named below (hd.py,
  brender.py, the vox/ pipeline and the rest) travel in each art package's src/; without them, the rules in
  The look and Method still define the result:
  - the building's hand-off folder: ts-original/ (decoded frames/, frames-4x/, sheet.png per TS SHP),
    in-mod/ (the building as it is in the mod now, on its canvas), reference-hd/, PROMPT.txt, README.txt;
  - the latest package zip. Its src/ holds the renderer, lighting and materials; reuse them, don't rewrite.
    hd.py is the general renderer (any camera; heightfield plus named slab pieces; shadow maps; sky
    occlusion; outline; supersampling); brender.py wraps a model + materials + damage module into both views
    (Building, Prep); pfinal.py has overlay() and save(); bdeliver.py builds previews/README/src/zip from a
    small spec module (see pilespec.py, silospec.py, techspec.py, procspec.py: crop/zoom options for big
    canvases, under-layers like a bib, extra_previews, views=('ra',) for an RA-only package); export3d.py
    writes the .glb models. Start new buildings from these. Units: start from the latest unit package's src/
    (the voxel pipeline, or the walkers' rc.py / rcrender.py), see Units below;
  - one or two RA/TD HD frames of a similar asset, as the target for detail (ref/RA and ref/TD hold more,
    e.g. RA TENT, BARR and TD PYLE for barracks).
- PROMPT.txt is the spec: canvas, cell placement, frame list, states. If it doesn't give a building's canvas
  and where its cells sit in it, ask. The building's README gives the mod's frame counts (e.g. TSFACT.ZIP
  60 = 30 healthy + 30 damaged, TSFACTMAKE.ZIP 32): match them. A ZIP's layout can be read off the in-mod
  frames it names (TSPOWR 0000 = healthy 1 pod, 0036 = damaged 2 pods -> blocks of 12: 1H 1D 2H 2D 3H 3D).
- Normally one building at a time, with sign-off before the next. When asked to carry on through a list
  unattended, deliver each package as it is finished and note every judgement call in its README.
- Deliver the RA grid only: render and package the RA-grid version, grid-aligned, the entrance or production
  side facing the camera. Don't render or package the TS angle: the .glb carries TS's own camera (the mod's
  TS-angle canvas, scale and place) and src/ can still render that view if it is ever wanted; say so in the
  README. TS's own camera stays the tool for fitting the model to TS's sprites (the shape check), and the
  previews put TS's sprite beside the RA version (bdeliver spec views=('ra',)). Older packages still carry
  their TS angle.
- RA buildings have two states only: healthy and damaged. No destroyed state, even if the PROMPT lists one.
- Size and footprint: buildings keep TS's own size and shape. Where TS's foundation is bigger than the mod's
  plot (the silo: TS 2x2, mod 2x1), use TS's footprint on RA's grid: buildings that don't match RA's
  size are fine as long as they're built for RA's square grid. Say when the rules' foundation must change.
  Units too are TS-authentic in size (the harvester at TS's size, matching the refinery; it can be shrunk
  later), so don't reshape a building to fit the mod's current, larger unit sprites.
- The RA version may be turned to suit the grid (the tech center: long and thin on a 2x3, the wide end with the
  dome to the front, the fins at the point). RA's bib may force it back, so keep the orientation a switch
  (layouts, below) and show both orientations at the shape check. A building may be wanted symmetrical
  facing south (the Mobile War Factory): the RA layout then mirrors about the door's axis.
- Every package also carries the 3D models, with suggested camera angles, for buildings and units alike: they
  allow the greatest flexibility later. See 3D models and Package below.

## The look (fixed: match the existing assets)
- Scale: 128 px per cell. Model in physical units at TS proportions, 1 cell = 128 units every way.
- Cameras:
  - RA-grid buildings and units: a true orthographic camera 32 degrees above the ground, looking north (the
    unit renders are 32 degrees too). "32 degrees" means elevation above the ground, like TS's 30 - not 32 off
    vertical, which looks too top-down. Ground depth reaches the screen x sin32 (0.530), heights x
    cos32 (0.848). The Mammoth Mk. II is the exception, at 35.
  - Walls and gates: RA's oblique projection, screen_y = ground_y - 0.6 * height; the ground is not
    compressed.
  - TS itself (for fitting, and the .glb's TS camera): orthographic, 30 degrees above the ground, looking
    north-west (0.265 px/unit). A cell is a
    48x24 px diamond: x = gx + 24(X - Y)/128, y = gy + 12(X + Y)/128 - 0.2297 Z (units). Sliding a point
    along TS's view ray (X += 1.225t, Y += 1.225t, Z += t) keeps its pixel: fix depth from ground contacts.
    TS puts the foundation's NORTH corner at the frame's centre: 2x2 in 96x96 -> ground centre (48, 72);
    3x3 in 144x144 -> (72, 108); 3x2 in 192x120 -> (108, 90); 4x3 in 192x168 -> (108, 126).
  - In-mod isometric placement (TS's sprite on the mod's canvas in the previews, and the .glb's TS camera)
    differs per building: find it by an alpha-IoU search of TS's frame scaled
    into the in-mod frame (canvas = TS px x K + offset). Found: plant K 3.36 (-30, -53.5), barracks 3.2
    (-26, -96), silo 3.73 (-32, -137), tech 3.73 (-220, -109.5), refinery 4.1 (-69.4, -44.7). Search coarse
    then fine, with ranges narrowed from the bounding boxes: a brute-force search over a 384 canvas takes too
    long. Sprite units the same way (the Juggernaut's walker: K 6.33, (-76.7, 9.3)).
- RA-grid canvas: the plot is centred in the canvas (the game anchors the canvas centre on the plot centre);
  the foundation's south edge on the plot's south edge. If the building doesn't fit, grow the canvas evenly
  top and bottom and report the new size (yard 384x360; plant 256x272; tech turned 256x512; refinery
  736x928 as the mod has it). Units keep their in-mod canvas, size and place pixel for pixel.
- Light (walls2.py): L = (-0.451, -0.551, 0.702) (x east, y south, z up: from the north-west, above).
  shade = 0.20 + 0.26 (0.5 + 0.5 nz) + 0.62 max(0, n.L) (1 - 0.8 in_shadow); AO 0.8 + 0.2 clip(z / 40).
  The light is camera-relative: a render in TS's camera is lit like TS's sprites (hd.py's L_CAM_TS). A thin
  plate facing away from the light renders dark; where TS's part is bright, give it sloping (ridged) sides.
  Units add a soft fill from the camera on their camera-facing sides (EA's HD units are front-lit; the key
  light alone leaves a unit's near side dark); a unit drawn into a building's frames gets the same fill.
  This light has far less ambient than TS's voxel renderer: any surface whose normal turns away from the light
  goes nearly black, so never let fine per-voxel or per-pixel normal detail turn a face that far (see Units).
- Shadow baked in at ~75% black, blurred ~1.5 px, plus a soft contact shadow within ~5-7 px. TS units' canvases
  are drawn at 2/3 in game (8 canvas px per classic px): outline, blur and contact shadow x1.5 on them.
  Aircraft carry no shadow (the game draws it from the frame).
- Outline: a ~0.9 px dark ring (RGB 28, alpha 0.55) round every silhouette. Supersample x4.
- Colours: concrete (226,226,222); GDI ochre collars (214,166,70); grime (112,104,78) rising from the base;
  GDI khaki (196,176,112); steel (146,148,158); blue-grey plate (150,150,178); dark recesses (74,74,78).
- House colour: EXACTLY GREEN (0,214,0) x (1 + 1.1 grain) on every house part of every building (it must
  match on all buildings or the house colours differ). No darkening, grime, dust or soot tint on it;
  detail only as thin seams or ribs. It also goes out as a -trim.png mask (white = house colour) for every
  frame, overlays included; build the trim from the house components only (plus broken house-coloured bits on
  the ground), so natural Tiberium green (the silo's fill) and lit green lamps never count as house colour.
  The green areas are TS's green areas (TS's remap greens - the refinery's dock lamps are house colour). A
  solid core's side seen where it shouldn't be (in the gap under a raised deck) must not carry the colour of
  the part on top: it showed as a green sliver under the Upgrade Center's deck.
- Flags: on the RA grid a flag flies to the right (east), face-on to the camera, like RA's Allied (TENT) and
  Soviet (BARR) and TD's GDI (PYLE) barracks. A flag flown north-east on the RA grid looks tilted and squashed.
- Open pipes (chimneys, stacks, columns): TS draws a black hole in a light rim on top, not a closed cap. Paint the hole on the flat top (a geometric recess in a heightfield renders as
  a jagged crown); a broken pipe's snapped top is hollow and dark.
- Damage: greys and browns only - scorch, cracks, grime, chipped edges, angular rubble chunks. Build TS's
  damage into the shape first (holes, snapped parts; read which parts TS breaks: the silo's west claw and
  east claw foot, not a made-up one; and which end of a part TS keeps: the Upgrade Center's pipes lose their
  lower halves, their tops hanging from the bends), then texture it, in world space (wnoise.py). Keep
  break colours on the part that broke. Make it as heavy as TS's (strong soot and charred holes are
  right), but keep smashed/sparking areas as small as TS's.

## Method
1. Inventory before modelling: every TS frame (building, damaged, build-up, every overlay) at x6-x10 with a
   pixel grid. Count real frames by non-empty ones: overlay SHPs end in empty shadow frames, and many have a
   healthy then a damaged half (GTPILE_C 7+7, GTSILO_A 4+4, GTTECH_A 8+8; NTREFN_A 5+5, _B 20+20, _C 16+16 are
   frames + empty shadow halves). Diff each overlay frame against the base. Print pixel values of small parts
   (fins, claws, lamps) to read their real shape and shading. A smaller anim SHP (NTREFN_C 144x144 on a
   192x168 building) is drawn centred on the building's frame.
2. Read the geometry from TS's pixels, shape first:
   - the plan: the ..MK SHP's first frames often draw the foundation outline (GTTECHMK: a triangle, not the
     rectangle that the finished sprite suggests); the build-up shows how parts attach (fins raised from
     lying flat = slabs facing the camera; the silo's lid lifted by its drum).
   - heights: fix them from ground contacts (feet, base edges at Z=0) and overlay lamp pixels; a circle fit
     of lamps gives the radius at any height, so the centre's offset sets the height (silo lamps: rim 44).
   - unproject colour classes (tan roofs, green, red) to plan view; map TS's classes onto the model's faces
     (render the model in TS's camera, look up TS's class per pixel) to place hatches and panels.
   - TS's camera can't tell a skewed part from a square one: a line TS draws straight up can run diagonally
     in 3D, and an edge can run off to a corner the footprint doesn't suggest (the Upgrade Center's east hip
     ran out to the deck's north-east corner, its pipes lying on it). Prefer square, grid-aligned readings
     (upright walls, vertical pipes) and check every fitted part from RA's camera too.
   - units: read the .VXL voxel by voxel (vxl.py): dump the top height per (x, y) and the side colours with
     the palette, and build the model to those steps (voxel index i spans i..i+1, so a top voxel at z 16 is a
     surface at 17). A parametric model fitted by silhouette alone came out squat and plain next to the
     current voxel render it is compared with. Base colours come from the palette (house colour = the remap range).
3. Rebuild as a heightfield plus slab pieces (overhangs, masts, fins, flags), a component id per part. Build
   in the building's own frame with layouts (to_local per layout; per-view parameters passed as Prep kwargs
   into scene(), materials read r.mk): TS's own placement for the TS-angle view, centred / turned for RA.
4. Shape check BEFORE materials: flat colours in TS's camera, silhouette overlap >= ~0.88-0.9 and every
   landmark (fins, claws, lamps, entrances, stairs, walls) where TS has it; then shaded renders
   beside TS at 2x, in TS's camera and on the RA grid: every part fitted in TS's camera must read square from
   RA's too. Send that check for review (both RA orientations if the footprint could change) before finals.
5. Frames (RA grid): 0 healthy, 1 damaged; build-up in TS's order (the ..MK SHP) at >= TS's real frame count (24 is a
   good default), driven by progress controls; its last frame is exactly the healthy frame - or, when TS's MK
   bakes in a part that an overlay draws later (the barracks' flag), the healthy frame plus that overlay at
   frame 0, so nothing pops. Follow TS's order and oddities exactly (the silo's lid unfolds on the ground with
   its first blade, the drum lifts it, the other blades go on in TS's order; the tech's fins are raised from
   lying back; its dome goes up as see-through struts, then the panels go in). No construction arm.
   A bib (..BB) is its own layer under the building; TS's MK (and the mod's MAKE zip) include it.
6. Self-review before every checkpoint: the RA version beside TS at 2-4x, and close-ups at 3-5x of the areas
   a reviewer looks at first: a unit's near side facing east (its right side) and south-east, the lower hull,
   tracks and wheels, flat house-colour panels. Look for black specks, squiggles or blotches on flat panels and
   for anything that reads weaker than in-mod/ (tracks, slots, hatches).
7. Previews: the asset alone; states vs TS; next to the yard, plant, Component Tower and a wall run; house green next to the yard's; build-up strip and
   GIF vs TS; idle loops vs TS (healthy and damaged), built from the package's own frames and overlays, with
   every overlay playing (lamps and the flame together). Keep a review page (an artifact with every
   building's build-up and idle GIFs, one tab each) updated, and put any GIF the reviewer asks to see on it
   too: a GIF sent in chat doesn't always play. Units have their own review page (one tab per unit). Check that
   every reference frame a preview uses exists first (the hand-off's RA_4TNK has turret frames facing north
   only).
8. 3D models: export3d.py samples the model's scene on a grid (1.5-2 units; 1.0 where thin masts or poles
   would vanish), makes a solid of it (a truncated distance field: walls come out vertical and subdivided,
   slopes smooth), meshes it by marching cubes and colours every vertex with the building's own materials
   (albedo; COLOR_1 = the house mask). One .glb per building: healthy and damaged nodes (+ the bib, add-ons
   like pods), marker nodes (a dock, a flame's mouth, lamps) and two orthographic camera nodes - the RA-grid
   one framing the delivered canvas exactly (check it: render the mesh through it over the frame), and the
   TS-angle one (TS's camera on the mod's TS-angle canvas: it rebuilds the TS angle, which isn't packaged). Axes x east, y up, z south; 1.0 = one cell; origin = the foundation centre on the ground;
   units at their position, facing east (mod frame 24). Write the cameras and axes into the README.
   export_all.py does the earlier buildings. Voxel units: vexport.py (exact boxes, subdivided by longest-edge
   bisection with shared vertices so the vertex colours carry TS's colours; a node per section; the facing
   node's rotation quat(A @ Mx), sections kept in the unit frame, or improper matrices flip the legs); check
   with Khronos's validator and glbcheck.py.
9. Package (RA grid only, no ts-angle/ folder): README.txt, one folder per frame set, previews/, src/. The 3D models go in a sibling folder named
   <package>-3d, e.g. ts-hmec-hd-3d/, with its own README, zipped on its own as <package>-3d.zip; the main
   zip carries no 3D folder. Where uploads are capped (30 MiB in a claude.ai chat): first recompress the PNGs
   losslessly (oxipng via pyoxipng, colour type, bit depth and every pixel kept,
   checked: about 9% off); if it is still over, part 1 (everything but loop/) and part 2 (loop/), unzipping
   into the same folder. src/ must run on its own: copy it, put only the hand-off on the path, and draw one
   frame before zipping (the Mk. II's src/ once missed tsnormals.py, the Mk. I's an `import os`).

## Units
- Voxel units (most TS vehicles, aircraft, RA2's tanks) are built straight from the VXL by the voxel
  pipeline (vox/: vxlunit.py, voxrender.py, vexport.py, vdeliver.py, vfinish.py; a small spec module per
  unit): each section's voxels merged into boxes, cut at 45 degrees only along the solid's convex exposed
  edges, the shading rounding every air-facing edge; TS's colours sampled across each face (single-voxel
  speckle held within 0.75-1.2 of the local mean, near-black < 70 and near-white > 205 voxels keep their
  colour), x1.25 gain, whites capped at 236; house green on the remap voxels with TS's remap shades kept as
  seams; grime rising from the ground on the lower hull. It beats hand-modelling (compared on the MCV).
- TS's own voxel normals go in as a layer of detail: n = normalize(n_round + 0.6 (n_TS - n_face)), and the
  result may tilt the shading normal by AT MOST 25 degrees (voxrender ts_max_tilt, the default). Uncapped,
  voxels whose TS normal points far from their face (the bottom rows of side skirts, seams) rendered black in
  our light where TS's renderer shows them mid-tone: wiggly black lines along the Mammoth Mk. I's side
  skirts, and a dark band over the tracks that left them reading weaker than the voxel render. Applies to any normal-detail layer: cap it, then check the close-ups (Method 6) before rendering
  every frame. RA2's voxels use normal mode 4: ra2normals.py (244 normals, estimated from the voxels like
  TS's by estnormals.py).
- Placement: fit scale and origin by IoU of the posed voxel centres against in-mod's opaque pixels
  (vplace.py, coarse then fine from a bounding-box estimate). When TS's voxel sits GZ above its HVA origin,
  lower the model onto the ground and raise the camera origin by GZ x ppu x cos(elevation), so every pixel
  stays where in-mod/ has it and the shadow meets the tracks. A big float (the Mobile EMP, 4.3 voxels) may
  instead sit on the ground if the hand-off README allows it: say so in the README. In Tiberian Factions the
  packed vehicle is then centred on its hull, as EA's vehicles are (scripts/unit_centring.py, the
  unit-art-placement skill), so in-mod/ art from before 2 Oct 2026 sits 3-7 classic px higher than today's.
- Turrets, racks and upper bodies are separate frame sets drawn at the hull's canvas centre; fit each set's
  own place when the mod draws it differently (the Disruptor's turret 6 px aft; the Hover MLRS's rack centred
  per frame) and lay them over each other in the previews and the 3D check.
- Aircraft: no baked shadow, no ground grime and no ground occlusion (voxrender with_shadow=False,
  grime_z=0, ground_ao=False); the outline reads as the shadow's edge.
- Sprite units (walkers, infantry, drones): convex parts (rc.py) in TS px units, fitted to TS's frames in
  TS's camera (30 degrees, facings clockwise from screen-up) by silhouette plus colour classes (wfit.py),
  walk poses step by step; rendered with the RA camera at in-mod's K canvas px per TS px. A Westwood render
  beats the 95-px sprite for detail (there is one for the Wolverine): ask for one.
- Effects (the Mobile EMP's blast): keep TS's shape, size, place and timing frame by frame and TS's colours
  in TS's layout; redraw TS's pixels as smooth antialiased shapes rather than inventing glows or sparks, and
  offer a glow as an option.

## Building notes (read from TS)
- Barracks (GTPILE): the entrance is a doorway under the south bunker's roof edge with steps coming DOWN to
  the ground between two walls that stick out past the slope; the east wall's coping is house green; the
  entrance lamps sit on the walls' upper ends.
- Tech Center (GTTECH): a right-triangle wedge (long south face, east face with a dark opening behind a strut
  framework, back face to the narrow west end), three terraces; a geodesic dome (icosahedral, frequency 2,
  hub on top) partly overhanging the back edge in TS; two fins = ribbed leaf blades on stems, side by side at
  the narrow end. GTTECH_A healthy is a uniform pulse; damaged flickers panel by panel with sparks.
- Silo (GTSILO): a dark ribbed drum (to z 40) carrying a shallow glass dome (rim 44, R 80); five blades lie on
  the dome to their lamps just past the rim (R 95), then drop to the ground as ridged claws (to R ~134); a
  slatted loader on legs at the south corner, a striped vent on the east.
- Refinery (NTREFN, 4x3): an umbrella - a black deck (74 up) on a skirt of grey panels and sixteen green ribs
  to the ground; the dock cut into its east side under the deck; the flare stack (copper cone, steel stack,
  two collars) at the back, two columns on the deck, a copper sphere with a white cap; the bib with hazard
  stripes on the dock lane. Its flare stack bursts (NTREFN_B) every few seconds at random; the dock lamps
  (NTREFN_C) blink in house colour.
- Harvester (HARV/HORV.VXL, 49x20x19): five wheels a side, the tank (bevelled, four hoops, let-in side
  panels, house-colour posts at its back), a dark olive engine block, a house-colour cab sloping to a black
  windscreen, a scoop and four claws; HORV is the same truck with a flat bed where the tank was. TS's size
  next to the refinery: 3.46 units per voxel (fitted to a video of TS).
- Upgrade Center (GTPLUG): TS's east end is a hip skewed out to the deck's north-east corner with the pipes
  and light slot lying on it; it reads straight only from TS's camera (on the RA grid, a rectangle morphed into
  a parallelogram). Built square: the block runs on under a low hip to an upright end wall, three vertical
  pipes bend into it, the light runs down an upright post; a wedge behind the block (hidden on the RA grid)
  keeps TS's brown face right of the pipes for TS's camera.

## Animations and add-ons
- "Idle" means every active overlay playing together; specials (the silo's fill level) on their own.
- Read TS's overlay numerically before animating: per-frame mean/std of the changed pixels and their
  correlation with x/y tells a uniform pulse from a sweep (GTTECH_A: 0, .46, .77, .92, 1, .92, .77, .46 on
  the whole dome together). Never invent a motion TS doesn't have (a rotating sweep read as a disco ball).
- Overlays: render the full frame with the effect on and cut it against the frame it is drawn over. Cut with
  pfinal.overlay(): solid pixels copied, see-through pixels (outline, shadow) solved so base + overlay = frame,
  unchanged see-through pixels left out (copying them doubles shadows). Check the stack against straight
  renders; a few antialiased edge pixels can't be matched.
- Fire and other effects TS draws with its fire palette (the decoded frames read dark red/khaki): build them
  in HD procedurally, keeping TS's size and timing frame by frame (procfire2.py: a turbulent plume, white-yellow
  core to deep red tips, flicks at the top, a faint haze); upscaling TS's shapes looked blobby.
- Add-ons that fill in a fixed order (power pods: the plant comes with the east pod, upgrade 1 = middle,
  upgrade 2 = west - never a gap) are cut in that order, each against the frame with the ones before it.
- If the mod's ZIP bakes animations into building frames, also deliver loop/ in exactly that layout from
  straight renders (the stacked overlays are then exact too).
- An add-on's own small canvas (TSTURB 128x128): find where the in-mod piece matches the in-mod building
  (pixel match: (147, 97)) and cut ours from the same window, so it drops in; list offsets per socket.
- Lights: depth-test everything; no flashes, flares or glows TS doesn't have; keep them as small and as
  coloured as TS's; where TS only brightens a touch, leave it out.
- Don't open or move parts TS keeps still.
- Docking (refinery + harvester): render the docked unit INTO the building's scene (D-docked: HARV and HORV,
  healthy and damaged) so the building hides its back end and shadows interact; the refinery draws it while
  the unit is hidden, as the mod's TD refinery does (the docking code is fitted around the art). The lid (the tank
  sliding off) is cut against building + HORV in the scene, with the tank in the heightfield and HORV's bed
  sides coloured like the tank's, so HORV + lid 00 = HARV to the pixel. In TS (seen in a video) the harvester
  comes in facing west, turns round through south to face east and docks; TS never shows NTREFN_A (its depth
  test hides it) - the tank pops off and on at the HARV/HORV swap.

## Walls, and anything that joins them
- Wall format = RA's BRIK: 64 frames of 128x128. 0-15 healthy, 16-31 damaged, 32-47 heavily damaged,
  48-63 rubble (48 empty). Frame index = neighbour mask N1 E2 S4 W8.
- In the oblique view a wall's height pushes its top up into the cell to the north, so each frame also
  draws its southern neighbour's arm in its bottom band (phantom arms).
- GDI wall: 40 units high (24 px), top half-width 10, base 26, an ochre collar at each joint. Nod wall ~41.
- A building in a wall line (the Component Tower): no stubs alone; a coupling overlay per side only when a
  wall is next to it, hugging the building; end pieces per wall kind; walls count it as a neighbour.

## Pitfalls already hit
- A part fitted only in TS's camera can be skewed in 3D (TS's own model may be: the Upgrade Center's east hip
  and its pipes). On the RA grid it showed slanted pipes and walls not flush. Build such parts square, keep
  TS's silhouette with pieces RA's camera can't see, and check the fix loses nothing TS shows.
- Smoothing a heightfield spreads faces ~1 px past their footprint: give skirt cells the taller neighbour's
  component. A part meeting a slab leaves a crease: run it to the ground as one slab, or keep both in one
  solid heightfield core.
- A heightfield can't undercut: a dome that is more than a hemisphere gets a vertical drum below its equator;
  keep the sphere's centre close above its base ring (h ~10).
- Ground-projected fields stretch on vertical faces; use world-space fields.
- Shadows past the canvas edge: fade them over the last ~14 px. Keep parts inside the RA canvas.
- Remove whole parts with everything attached; build-up parts must not float (unless TS does it).
- Renders at ss=1 break the outline (binary_dilation with 0 iterations fills everything): test at ss 2, or
  turn the outline off for fit renders.
- A model's scene(p=P) binds P at definition time: pass p explicitly when searching parameters.
- pdamage.Chunks.scatter rejects |x| or |y| > 150 and loops forever on wider buildings: subclass it.
- Icosahedron faces from vertex triples have mixed winding: orient each face normal outward.
- Material-only frames reuse one geometry pass; anything that changes geometry (a waving flag, a rising pod)
  needs its own pass. Timing at x4 on 2 CPUs: a 256x256 pass ~30-40 s, a material frame ~4-8 s; a building
  package ~30-50 min in background batches. A voxel vehicle frame ~5 s, the Mk. II's 13-section walker ~28 s.
- Memory: a claude.ai sandbox's cgroup is ~6.27 GB. Every slab is three full-grid arrays: merge non-overlapping slabs
  (merge_slabs) and model a unit inside a building on a sub-window of the grid round it; a 4x pass of a big
  building with a truck in it peaks ~4.3 GB, a merged 4x unit frame ~1.2 GB - run big renders one at a time.
  ulimit -v counts virtual memory, well above the resident size: the Upgrade Center's two-plug RA frames
  (~4.2 GB resident) needed ~7.8 GB virtual.
- A claude.ai sandbox's shell tool times out after 2 minutes: start renders with setsid nohup into a log and poll it (sleeps
  under 2 minutes).
- The workspace can restart while renders run and every background job dies with it (uptime shows it). Run
  renders through a resumable queue (frames already on disk skipped, a done marker per unit) and check the
  queue is alive whenever you poll, not just the frame count.
- Don't `pkill -f` a pattern that also matches the shell's own command line (it kills the shell): kill by PID.
- Fitting a unit to a video: build its mask from a background difference with an empty frame, drop the
  shadow (pixels that are the background evenly darkened), and check the fit by drawing the model's outline
  per part (cab, tank, claws) over the frame.
- skimage's marching_cubes normals already point down the field (outward for a positive-inside solid).

## Reviews
- Review feedback tends to be short and visual. Answer with a quick test image of exactly the spot raised,
  and offer two or three visual options when the direction is unclear.
- Follow-ups often arrive while renders run: acknowledge each in a line and fold it into the next render
  rather than restarting per message.
- When quality is said to have dipped, own it plainly, say what was missed, and show the shape check before
  finals. When a renderer problem shows on one unit, fix it in the shared code and re-render every unit it
  touched, delivered ones included.
- Finals can render into a staging copy while a test is under review; nothing replaces a delivered package
  until it is signed off.
- Keep replies short: what changed, the files, one next step.