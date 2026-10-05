Mammoth Mk. I (TS [4TNK]) in HD for Tiberian Factions: TS4TNK  -  v4
====================================================================

frames/     ts4tnk-0000.png ... ts4tnk-0063.png, the mod's 64 frames on its 512 x 512 canvas, each with a -trim.png
            (white = house colour, antialiased):
              0-31    the hull with its shadow, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E)
              32-63   the turret with its barrels and tusk pods, no shadow, 32 facings, drawn at the hull's canvas
                      centre
previews/   8-facings.png            the assembled tank (hull + turret facing the same way), the mod's frames beside HD
            hull-8-facings.png, turret-8-facings.png   each set on its own, every 4th facing
            turn.gif                 the assembled tank through all 32 facings, the mod's frames beside HD
            turret-turning.gif       the turret turning on the hull facing east
            scale.png                next to the HD harvester and EA's Mammoth, as the game draws them
            shape-8-facings.png      the model drawn flat (a colour per part) in the mod's camera beside the mod's
                                     frames, hull and turret, with the silhouette overlap per frame
ts-4tnk-hd-3d/   the 3D model, in its own zip (ts-4tnk-hd-3d.zip) next to this folder:
            ts4tnk.glb   the model (vertex colours): the hull, and the turret with its barrels and tusk pods under a
                         'turret' node that turns about the unit's position; the mod's camera
src/        the model, the renderer and the checks (see Rebuilding below)

v4 replaces v1, v2 and v3: same canvas, place, frame layout and shadow.  v2 rebuilt the model; v3 (Luke: the
missile pod launchers all black, just the missile tips orange) repainted the tusk pods; v4 adds the detail of
Luke's photos of his yellow model, turret on and off: the covers' grooves and slots, the slatted rear deck, the hatch
plate's layout, a panel low on the turret's sides and a bolt at the foot of each rear lobe.


What changed from v1
--------------------
v1 copied TS's voxels box by box, so it still read as voxels.  v4 is built the way the Titan, the Wolverine, the
MCV and the Mammoth Mk. II are: TS's voxels are the blueprint (where every part is and how big), and each part is
modelled clean - flat plates, true slopes, round wheels, barrels and antennas, bevelled edges - in TS's own colours.
The detail the voxels lose comes from EA's HD Mammoths and Luke's models of the RA Mammoth (the same tank), where TS
has the part.

The Mk. I, part by part:
- Hull: four track units (TS's: two a side, front and back), each a belt round two end wheels and three road wheels
  under a green skirt with a row of bolts along its lower edge (EA's); over each side one long cover back to front
  (TS's): along its top a groove near the inner edge in two lengths over each unit and a joint across between the
  units, along its outer side a groove near the top and upright slots in twos and threes (a small round head under
  each middle one), three slots low in its front and back ends (Luke's models).  Between the covers the hull: its glacis down to the nose with TS's two grey
  headlamps in hoods and louvres between them (Luke's models), its back with TS's black grille between the orange
  tail lamps; the raised rear deck, slatted along its length round TS's two white caps (Luke's models); the turret
  ring; on the
  front deck a raised hex hatch, a round port, grilles along both sides and a panel at the front middle (Luke's
  models).
- Turret (TS's: wide and low, its front a blunt chevron, its sides tapering back, its back notched between two
  lobes): the line round its top plate (Luke's models); the raised hatch block with TS's dark plate at its front,
  on it a round hatch just right of its middle with a tab to the back and two small plates down its left edge
  (Luke's models); the mantlet between the barrels with ribs across its top, a small panel low on each side in front
  of the pod, a bolt at the foot of each rear lobe (Luke's models); TS's two black antennas on grey bases at the
  back.
- The tusk pods either side: all black (Luke), arm and all, ribbed on top (Luke's models), with TS's two by two
  orange missile tips at their fronts.
- The barrels: TS's square sleeves and square collars in house colour, with TS's light band along their right side;
  dark barrels with a ring at the muzzle (Luke's models).

The model's silhouette overlaps the mod's frames by 0.91 drawn flat in the mod's camera
(shape-8-facings.png); the finished frames by 0.906 (src/vcheck.py).


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.23 canvas px per voxel, the
  unit's position (TS's HVA origin) at canvas (255.5, 254.7) for the hull and the turret alike: the size and place the
  mod's frames have (v1's).  TS's hull sits 1.24 voxels above its HVA origin (its tracks' lowest voxels), so the
  model is lowered onto the ground and the camera raised to match: every pixel stays where in-mod/ has it, and the
  shadow meets the tracks.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides
  facing the camera as on the other units; plate edges are bevelled in the shading.  The game draws this canvas at
  two thirds (8 canvas px per classic pixel), so the outline, the shadow's blur and the contact shadow are 1.5 times
  as wide on the canvas.
- House colour is pure green 0,214,0 x (1 + 1.1 grain) over nearly all of the tank, as TS has it (its remap
  voxels): the hull, covers and skirts, the turret, its hatch block and mantlet, the barrels' sleeves and collars;
  detail only as thin seams, ribs and bolts.  The -trim masks cover exactly those parts.
- The rest in TS's colours: dark tracks and road wheels, black antennas, grille and barrels, the hatch plate dark
  grey, orange missile tips and tail lamps, white headlamps and caps; the tusk pods all black (Luke); grime rising
  from the ground on the running gear.


Shadow
------
The hull frames (0-31) carry the unit's shadow, black at alpha 191 (75%), blurred, falling to the right and a little
towards the camera, as long as the buildings' and the harvester's (v1's).  Within 14 px of the canvas edge it fades
out.  The turret frames (32-63) carry none (the mod draws them over the hull).


Fire points
-----------
The layout is TS's (same sections, same places), so TS's PrimaryFireFLH=40,32,96, SecondaryFireFLH=-32,80,120 and
PBarrelLength=192 still point at the cannons' and the tusk pods' tips.


3D model (ts-4tnk-hd-3d/ts4tnk.glb)
-----------------------------------
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.
- Nodes: MammothMk1 > unit_facing_east (the mod's facing 24) > hull (TS's hull section), turret > turret_body,
  barrels (TS's turret and barrel sections), each holding its parts (cover, belt_end, road, pod, sleeve, ...).  The
  'turret' node turns about the unit's position (its local z axis is up: the unit's frame is x forward, y left,
  z up).  The meshes are exact (each part cut from its own planes and curved surfaces).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 512 canvas exactly
  (checked by drawing the mesh through it over frames 24 and 56 laid over each other: overlap 0.991).
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).
- Khronos's glTF validator: errors 0, warnings 0, infos 0, hints 0.


Judgement calls (each one easy to change)
-----------------------------------------
- One paint colour per part (TS's), rather than TS's voxel-by-voxel speckle (v1).
- TS's turret sits 0.6 voxel right of the hull's middle: kept as TS.
- From Luke's models of the RA Mammoth (TS's Mk. I is the same tank, lower and longer): the turret top's plate line,
  the round hatch and small plates on TS's dark plate, the square collars (TS's are square too), the ribbed pod tops,
  the front deck's hex hatch, port, grilles, panel and louvres, the covers' grooves and slots, the rear deck's slats,
  the turret's side panels and lobe bolts, the ring at the muzzles.  From EA's HD Mammoths: the bolts along the
  skirts.  Kept as TS where the models differ: two by two missile tips per pod (the models have three by two),
  orange (the models' are red), TS's two antennas, house colour all over.
- Luke's model (the RA Mammoth) has separate covers over the front and back track units; TS's Mk. I has one cover
  the whole length: kept as TS, with a joint across where the model's covers part.
- The tusk pods all black with only the missile tips orange (Luke): TS has brown noses round the tips, a grey back
  end and a white arm to the turret.
- TS's light band on the barrels is on each sleeve's and collar's right side (the left barrel's faces the right
  barrel): kept as TS.
- The shadow as v1's: the buildings' length, alpha 191 (the mod ships about 150; at least 128).


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are (TS's voxels,
the mod's frames, the harvester and EA's Mammoth for the previews).
  rc.py, rcrender.py      a ray caster for models made of convex parts, with the buildings' look
  rcexport.py             convex parts to meshes (exact), for the .glb;  glbtools.py  the .glb writer
  qparts.py               parts built in a voxel section's own frame
  t4v2.py                 the model's parts per TS section (the voxels as the blueprint), posed by TS's HVAs
  t4mat.py                materials;  t4cam.py  canvas, camera, frame layout
  t4render.py             one frame;  t4spec2.py  the frames, previews and checks for vdeliver.py
  t4export.py             the .glb;  glbcheck.py  draws the .glb through its camera to check it
  vdeliver.py, vcheck.py  renders, previews and checks a unit from its spec
  t4shape.py              the shape check;  t4vox.py, t4view.py, t4look.py, hcls.py  TS's voxels, views, sheets
    PKG=out python3 vdeliver.py t4spec2 render 0 1      renders frames/
    python3 t4export.py ts4tnk.glb
