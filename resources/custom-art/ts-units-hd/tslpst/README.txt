Mobile Sensor Array (TS [LPST]) in HD for Tiberian Factions: TSLPST  -  v4
==========================================================================

frames/     tslpst-0000.png ... tslpst-0031.png, the mod's 32 frames on its 384 x 384 canvas, each with a -trim.png
            (white = house colour, antialiased), with the unit's shadow; 32 facings counter-clockwise from north
            (0 N, 8 W, 16 S, 24 E)
previews/   8-facings.png            the mod's frames beside HD, every 4th facing
            turn.gif                 all 32 facings in turn, the mod's frames beside HD
            scale.png                next to the HD harvester and EA's Mobile Radar Jammer, as the game draws them
            shape-8-facings.png      the model drawn flat (a colour per part) in the mod's camera beside the mod's
                                     frames, with the silhouette overlap per frame
ts-lpst-hd-3d/   the 3D model, in its own zip (ts-lpst-hd-3d.zip) next to this folder:
            tslpst.glb   the model (vertex colours), with the mod's camera
src/        the model, the renderer and the checks (see Rebuilding below)

v4 replaces v3: same canvas, place, size, ground line and shadow; frame 20 (facing south-east) where the mod has
it, so it still meets the deployed sensor array's build-up frame 0.


What changed from v3
--------------------
Luke: the long box down the right half is the pole that swings up at its back end when the array deploys, and the
grey block at its front end is the radar dish, which only comes out on deploy.  So in v4:
- the pole is its own beam (TS: a box at z 9..15), with a groove between it and the block and the cab beside it,
  where v3 had them fused;
- it rests on TS's layer under it (TS: z 7..9): the hinge it swings up on in the open recess under its back end, a
  dark grey cradle along its back half (v3's louvred band), two dark struts in the middle with open space between
  them (v3's black hatch), and the mount its front end lies in;
- the dish is packed away in its grey casing low on the pole's front end (TS's grey block; v3's grille block), under
  the pole's front end set in a voxel (TS's recess), behind TS's bumper bar on its two brackets.


What changed from v1
--------------------
v1 copied TS's voxel box by box, so it still read as voxels.  v4 is built the way the Titan, the Wolverine, the
MCV, the Mammoths and the APC are: TS's voxel is the blueprint (where every part is and how big), and each part is
modelled clean - flat plates, true slopes, round wheels, bevelled edges - in TS's own colours.  The voxel is the
source of truth: every part, step and colour below was read from it slice by slice.  There is no Westwood art of the
sensor array to hand, so the fan-made HD sensor arrays Luke sent (Tiberium Essence, Tiberian Sun Rising, Tiberian Sun
Redux) are only a guide to how TS's parts read in HD (the cover plates, the pole's straps and panels).

The Mobile Sensor Array, part by part (TS's layout):
- Two track units a side (TS's: the belts on the ground at x 4..15 and 23..33, their ends stepping up, as slopes, to
  x 0..18 and 21..35): black belts with TS's olive-brown tread a voxel in from their outer sides; on each belt's outer
  side three road wheels with grey hubs where TS has them; each belt rising at its ends to TS's dark grey cover, and
  between the ends TS's gap under the cover, in which the belt's top shows; a dark grey lip under the front end of
  each cover (TS's); the covers in plates (the mod renders'), the left ones overhanging their belts by a voxel as TS's
  do.  Between the tracks the keel, its front sloping out under the bumpers, its back the unit's back plate.
- The sensor pole, folded down the right half the whole length (TS's box at z 9..15; Luke: it swings up at its back
  end when the array deploys), its own beam with a groove between it and the block and cab beside it: TS's lighter
  bands across it as raised straps, panel joints between them (the mod renders' segmented housing); TS's house-colour
  strip along its right side, proud of it; its back end's top edge stepped down; its front end set in a voxel under
  its top (TS's recess), and below that the radar dish packed away in its grey casing (TS's grey block; Luke: the
  dish only comes out on deploy).  Under it TS's layer it rests on: the hinge it swings up on, in the open recess
  under its back end (TS's dark grey there); a dark grey cradle along its back half, louvred (TS's dark band); two
  dark struts in the middle, open between them (TS's); and the mount its front end lies in, its right side rising
  beside the pole's front part (TS's).
- On the left half: the tall block at the back, its roof's hatch by the mast (TS's blue-grey voxels there), TS's
  house-colour panel proud of its left side (wider below) and TS's two small red marks; the stairs down from it (TS's
  steps: tops 13, 12, 11, 10, 8), each tread edged; the low deck; the cab at the front: its lower front out to TS's
  house-colour panel with TS's dark recesses under it, the windscreen set back above the panel (TS's blue-grey voxels),
  and round the corner TS's band of side windows along its left side, proud by a voxel; TS's red mark below them.
- TS's dark mast at the back of the block, a grey cap on it; the low rear deck behind the block.
- TS's dark bumpers: a bar on two brackets in front of the dish's casing, and one under the cab's front, out to TS's
  length; TS's yellow: lamps low on the front and a lamp block at the back's left corner.

The model's silhouette overlaps the mod's frames by 0.97 drawn flat in the mod's camera
(shape-8-facings.png); the finished frames by 0.953 (src/vcheck.py).


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.24 canvas px per voxel,
  the unit's position (TS's HVA origin) at canvas (191.5, 191.08), as v1 and the mod's frames have it: the ground
  line is the mod's, so the deployed building's base, placed from it, still meets it.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides
  facing the camera as on the other units; plate edges are bevelled in the shading.  The game draws this canvas at
  two thirds (8 canvas px per classic pixel), so the outline, the shadow's blur and the contact shadow are 1.5 times
  as wide on the canvas.
- Paint: TS's colours, one per part - GDI's ochre on the body (TS 144-152, as the HD buildings' and the Mk. II's
  ochre), darker on the keel and decks; dark grey covers and bumpers, black belts (TS's olive-brown tread) and mast;
  blue-grey glass; yellow lamps; grime rising from the ground on the running gear.
- House colour is pure green 0,214,0 x (1 + 1.1 grain) on TS's three house-colour panels (the strip on the right,
  the panel on the left, the cab's front), detail only as thin seams; the -trim masks cover exactly those.


Shadow
------
Every frame carries the unit's shadow, black at alpha 191 (75%), blurred, falling to the right and a little towards
the camera, as long as the buildings' and the harvester's (v1's).  Within 14 px of the canvas edge it fades out.


3D model (ts-lpst-hd-3d/tslpst.glb)
-----------------------------------
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.  The unit faces east (the mod's facing 24).
- Nodes: MobileSensorArray > unit_facing_east > body, holding its parts (pole, hinge_axle, cradle, mount,
  dish_casing, block, stair, cab, track_cover, belt, mast, ...).  The meshes are exact (each part cut from its own planes and curved surfaces).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 384 canvas exactly
  (checked by drawing the mesh through it over frame 24: overlap 0.978).
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).
- Khronos's glTF validator: errors 0, warnings 0, infos 0, hints 0.


Judgement calls (each one easy to change)
-----------------------------------------
- One paint colour per part (TS's), rather than TS's voxel-by-voxel speckle (v1).
- The mod renders only where TS's voxel has the part: left out are their cab roof lights (Rising, Redux), dish and
  antenna (Rising), markings and red stripes over the housing (Essence), and their track designs (TS's three road
  wheels a side are kept); TS's own small red marks are kept where TS has them.
- The pole kept as TS's box; the deployed building's build-up draws it as a round tube (that building is to be
  matched to this unit once it is signed off).
- The groove between the pole and the block and cab (TS: they touch; Luke: the pole is its own part).
- The dish's casing as TS's grey block, bevelled, with a lid seam (TS shows no more of the packed dish).
- The cab's windscreen raked back a little (TS: upright, a voxel behind the panel).
- The gap under each track cover is in the cover's shadow, so the belt's olive-brown tread in it reads dark (TS lights
  it as if nothing were above it).
- The shadow as v1's: the buildings' length, alpha 191 (the mod ships about 150; at least 128).


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are (TS's voxel,
the mod's frames, the harvester and EA's radar jammer for the previews).
  rc.py, rcrender.py      a ray caster for models made of convex parts, with the buildings' look
  rcexport.py             convex parts to meshes (exact), for the .glb;  glbtools.py  the .glb writer
  qparts.py               parts built in a voxel section's own frame
  lpstmodel.py            the model's parts (the voxel as the blueprint), posed by TS's HVA
  lpstmat.py              materials;  lpstcam.py  canvas, camera, frame layout
  lpstrender.py           one frame;  lpstspec.py  the frames, previews and checks for vdeliver.py
  lpstexport.py           the .glb;  glbcheck.py  draws the .glb through its camera to check it
  vdeliver.py, vcheck.py  renders, previews and checks a unit from its spec
  lpstshape.py            the shape check;  lvox.py, lpstlook.py, hcls.py  TS's voxel, sheets
    PKG=out python3 vdeliver.py lpstspec render 0 1      renders frames/
    python3 lpstexport.py tslpst.glb
