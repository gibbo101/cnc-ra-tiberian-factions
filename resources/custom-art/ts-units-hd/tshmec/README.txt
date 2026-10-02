Mammoth Mk. II (TS [HMEC]) in HD for Tiberian Factions: TSHMEC
=============================================================

frames/     tshmec-0000.png ... tshmec-0255.png, the mod's 256 frames on its 576 x 576 canvas, each with a -trim.png
            (white = house colour, antialiased).  frame = facing x 8 + step: 32 facings counter-clockwise from north
            (0 N, 8 W, 16 S, 24 E), 8 walk steps (TS's HVA frames 0, 2, 4, 6, 8, 11, 13, 15), 8 ticks a step.
previews/   8-facings.png              the mod's current frames beside HD, step 0, every 4th facing
            walk-east-southeast.gif, walk-south-northwest.gif   the walk, the mod's current frames beside HD
            scale.png                  next to the HD harvester, the HD Titan and EA's Mammoth, as the game draws them
ts-hmec-hd-3d/   the 3D model, in its own zip (ts-hmec-hd-3d.zip) next to this folder:
            tshmec.glb                 the model in TS's own colours, a node per voxel section, the walk as an
                                       animation, the mod's camera
src/        the model builder, the renderer and the checks (see Rebuilding below)


What it is
----------
TS's own model, rebuilt: HMEC.VXL's 13 sections (the body; each leg's upper leg, lower leg and foot) posed by
HMEC.HVA exactly as TS poses them, drawn the way the HD buildings and units are.
- Shape: every voxel's step is TS's.  Each section's voxels are merged into boxes and cut at 45 degrees along the
  solid's convex edges (so its corners read as pressed plate); where two boxes of a section meet, nothing shows.
  The shading rounds every edge that faces the air, and carries TS's own voxel normals as a layer of detail (the
  bevels, seams and slots TS shades into its voxels), so the pods' bevelled edges and the body's seams read as in
  TS; each voxel's normal tilts the shading 25 degrees at most, so TS's odd single voxels shade as seams, not as
  black specks.
- Colours: TS's own.  Every surface takes the palette colour (UNITTEM.PAL) of the voxels just inside it; TS's
  single voxels of darker or lighter speckle are held near the colour round them, while its near-black and
  near-white voxels (slots, rails, highlights) keep their colour.  House colour is pure green 0,214,0 x
  (1 + 1.1 grain) wherever TS's remap voxels are (the four missile pods, the green on the front legs); the -trim
  masks cover exactly that.
- The walk: TS's own HVA frames, so the legs and the body's sway are TS's step for step; the feet stand where TS
  puts them.
The finished frames cover the mod's frames with a silhouette overlap of 0.96 (src/hcheck.py).

This is a different way of building than the MCV's (hand-modelled part by part from the voxel): it takes TS's
voxels as they are, so nothing is interpreted and every detail is where TS has it.  Side by side the two read
alike (I rendered the MCV both ways to compare); say if you want the hand-modelled finish for this one.


Look
----
- Camera: orthographic, 35 degrees above the ground (your choice for this unit), looking north; 6.8 canvas px per
  voxel, the unit's position (TS's HVA origin, on the ground) at canvas (287.5, 374): the size and place the mod's
  frames have (found by matching TS's voxels to them: overlap 0.96), so the body sits centred on the canvas.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides facing
  the camera as on the other units.  The game draws this canvas at two thirds, so the outline, the shadow's blur
  and the contact shadow are 1.5 times as wide on the canvas.
- Colours brightened by 1.25 from TS's palette so its ochre comes out as the HD buildings' ochre; whites held at
  white paint; grime rising from the ground on the feet and lower legs.


Shadow
------
Every frame carries the unit's shadow, black at alpha 191 (75%), blurred, falling to the right (east) and a little
towards the camera, 62% as long as the buildings' (the walkers' length, as the Titan's and the Wolverine's), so it
stays on the canvas.  Within 14 px of the canvas edge it fades out.


Fire points
-----------
The model is TS's voxel exactly (same sections, same places), so TS's PrimaryFireFLH=80,100,158 and
SecondaryFireFLH=-60,100,158 still point at the rail and the tusk launchers.


3D model (ts-hmec-hd-3d/tshmec.glb)
-----------------------------------
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.
- Nodes: MammothMk2 > unit_facing_east (the mod's facing 24) > one node per voxel section (body, foot_r_front,
  leg_r_front_low, leg_r_front_upp, ...), each in TS's own place for the step.  The meshes are exact (each section's
  boxes), subdivided so the vertex colours carry TS's colours.
- Animation "walk": the mod's 8 steps (TS's HVA frames 0, 2, 4, 6, 8, 11, 13, 15), 0.533 s each (8 ticks at 15 a
  second), looping.
- Camera "camera_mod": orthographic, 35 degrees above the ground, looking north; it frames the 576 canvas exactly
  (checked by drawing the mesh through it over frame 192: overlap 0.988).  The file passes Khronos's glTF
  validator with no errors or warnings.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- Built straight from TS's voxels (above), not hand-modelled.
- TS's single-voxel speckle held near the colour round it (its paint is speckled voxel by voxel).
- The shadow at the walkers' length (62% of the buildings'), alpha 191 (the mod ships about 150; at least 128).
- The legs carry the body's shadow where the body hangs over them (TS's renderer casts no shadows on the unit).


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are.
  vxlunit.py             a voxel section as boxes, its convex edges, TS's colours across its faces
  voxrender.py           one frame of a voxel unit with the buildings' look
  rc.py, rcrender.py     the ray caster and the buildings' look for models made of convex parts
  rcexport.py            convex parts to meshes, for the .glb
  hvox.py, hdump.py      HMEC's sections and HVA; its voxels dumped layer by layer
  hrender.py             the Mk. II's frame layout and camera;  hfinal.py  all 256 frames
  hexport.py             the .glb;  glbcheck.py  draws the .glb through its camera to check it
  hpreviews.py, hcheck.py   the previews and the checks
    PKG=out python3 hfinal.py 0 1      renders frames/
    python3 hexport.py tshmec.glb
