TS Dropship (TS [DSHP]) in HD for Tiberian Factions: TSDSHP
===========================================================

frames/     tsdshp-0000.png ... tsdshp-0003.png, the mod's 4 frames on its 656 x 656 canvas (EA's density), each with a
            -trim.png (all black: the dropship never takes house colour):
              0       the ship, side-on and level, facing west, in GDI's gold
              1-3     frame 0 scaled to 55%, 70% and 85% about the canvas centre, as your packer makes the shadow
                      frames (regenerate them from frame 0 as before if you prefer)
previews/   ship.png                 frame 0 beside the mod's current frame 0
            shadow-frames.png        frames 1-3 beside the mod's
            scale.png                next to EA's C-17 and Badger, as the game draws them
ts-dshp-hd-3d/   the 3D model, in its own zip (ts-dshp-hd-3d.zip) next to this folder:
            tsdshp.glb   the model in TS's own colours (the remap parts in house colour), with the mod's camera
src/        the model builder, the renderer and the checks (see Rebuilding below)


What it is
----------
One 3D model rebuilt straight from TS's own voxels (DSHP.VXL, posed by its HVA), drawn the way the HD buildings and
units are.
- Shape: every voxel's step is TS's.  Each voxel section's voxels are merged into boxes and cut at 45 degrees along
  the solid's convex edges (so its corners read as pressed plate); where two boxes of a section meet, nothing
  shows.  The shading rounds every edge that faces the air, and carries TS's own voxel normals as a layer of detail
  (the bevels, seams, vents and slots TS shades into its voxels).
- Colours: TS's own.  Every surface takes the palette colour (UNITTEM.PAL) of the voxels just inside it; TS's single
  voxels of darker or lighter speckle are held near the colour round them, while its near-black and near-white
  voxels (slots, hatches, highlights) keep their colour.  House colour is pure green 0,214,0 x (1 + 1.1 grain)
  wherever TS's remap voxels are, with TS's remap shades kept as darker and lighter seams; the -trim masks cover
  exactly that.
The finished frames cover the mod's frames with a silhouette overlap of 0.97 (src/vcheck.py).


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north, the ship facing west; 6.33
  canvas px per voxel, the voxel's origin at canvas (279.4, 326.8): the size and place the mod's frame 0 has (found by
  matching TS's voxels to it: overlap 0.98; 32 degrees fits it as well as 30), so the hull's centre is where it is
  now and the ship is as BIG as you signed off.
- GDI's gold where TS's remap voxels are, (245, 200, 52) before the light: the gold the mod's frame shows on the same
  faces, shaded like the HD house colour (so it reads as the same paint, lit).
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides
  facing the camera as on the other units.  This canvas is at EA's density, so the game draws it 1:1 and the
  outline is the buildings' width.
- Colours brightened by 1.25 from TS's palette so its ochre comes out as the HD buildings' ochre; whites held at white
  paint.  It flies, so none of the ground's grime or occlusion that the ground units carry low on the hull.


Shadow
------
None baked: frames 1-3 are the ship itself, scaled, which the game draws darkened on the ground as it
descends.


3D model (ts-dshp-hd-3d/)
-------------------------
- Nodes: Dropship > unit_facing_east > hull.  The model faces east like the other units' models; the mod's frame 0
  faces west (the check below turns it west).
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (128 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.  The unit faces east (the mod's facing 24).
- The meshes are exact (each voxel section's boxes), subdivided so the vertex colours carry TS's colours.
- Camera "camera_mod": orthographic, the mod's camera, framing the canvas exactly (checked by drawing the mesh
  through it over frame 0: overlap 0.991).
- The file passes Khronos's glTF validator with no errors or warnings.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- Built straight from TS's voxels (above), not hand-modelled: nothing is interpreted, every detail is where TS
  has it.
- TS's single-voxel speckle held near the colour round it (its paint is speckled voxel by voxel).
- The gold is measured from the mod's current frame (TS's remap voxels as the mod shows them now), not
  picked by eye.


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are.
  vxlunit.py, tsnormals.py   a voxel section as boxes, its convex edges, TS's colours and normals across its faces
  voxrender.py           one frame of a voxel unit with the buildings' look
  rc.py, rcrender.py     the ray caster and the buildings' look for models made of convex parts
  vexport.py, rcexport.py   the .glb;  glbcheck.py  draws the .glb through its camera to check it
  vdeliver.py, vcheck.py    renders, previews and checks a unit from its spec
  dshprender.py          the frame, the camera and the shadow frames;  dshpspec.py  its frames, previews, README
  dshpexport.py          the .glb
    PKG=out python3 vdeliver.py dshpspec render 0 1      renders frames/

