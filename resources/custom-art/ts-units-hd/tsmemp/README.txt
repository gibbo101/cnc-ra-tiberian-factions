Mobile EMP Cannon (TS [MOBILEMP]) in HD for Tiberian Factions: TSMEMP
=====================================================================

frames/     tsmemp-0000.png ... tsmemp-0031.png, the mod's 32 frames on its 384 x 384 canvas, each with a -trim.png
            (white = house colour, antialiased), with the unit's shadow; 32 facings counter-clockwise from north
            (0 N, 8 W, 16 S, 24 E)
fx/         tsmempfx-0000.png ... tsmempfx-0011.png, the blast: the mod's 12 frames on its 1152 x 576 canvas, played
            once at the unit's centre on the ground, each with a -trim.png (all black: the blast takes no house
            colour)
previews/   8-facings.png            the mod's frames beside HD, every 4th facing
            turn.gif                 all 32 facings in turn, the mod's frames beside HD
            scale.png                next to the HD harvester and EA's M.A.D. Tank, as the game draws them
            blast.gif                the blast played, the mod's frames beside HD (100 ms a frame here)
            blast-frames.png         the blast's 12 frames, the mod's beside HD, at a third
            blast-close.png          frame 6's right-hand side at full size, the mod's above HD
ts-memp-hd-3d/   the 3D model, in its own zip (ts-memp-hd-3d.zip) next to this folder:
            tsmemp.glb   the model in TS's own colours, standing on the ground at its position, with the mod's camera
src/        the model builder, the renderer and the checks (see Rebuilding below)


What it is
----------
One 3D model rebuilt straight from TS's own voxels (M_EMP.VXL, posed by its HVA), drawn the way the HD buildings and
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
The finished frames cover the mod's frames with a silhouette overlap of 0.96 (src/vcheck.py).


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.26 canvas px per voxel, the
  unit's position (TS's HVA origin) at canvas (191.0, 190.8): the size and place the mod's frames have (found by
  matching TS's voxels to them: overlap 0.98).
- On the ground: TS's voxel floats, its lowest voxel 4.3 voxels above the unit's position (about 3 classic px), and
  the mod's frames draw it so.  As the hand-off allows, the model sits on the ground at its position, with its shadow
  under its tracks like the other vehicles': the HD frames draw it 23 canvas px (2.8 classic px) lower than in-mod/,
  at in-mod/'s size and x.  The overlap below is measured with in-mod/ moved down by those 23 px.  To keep in-mod/'s
  float instead, memprender.camera(keep_float=True).
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides
  facing the camera as on the other units.  The game draws this canvas at two thirds (8 canvas px per classic
  pixel), so the outline, the shadow's blur and the contact shadow are 1.5 times as wide on the canvas.
- Colours brightened by 1.25 from TS's palette so its ochre comes out as the HD buildings' ochre; whites held at white
  paint; grime rising from the ground on the lower hull.


Shadow
------
Every frame that carries a shadow has the unit's shadow, black at alpha 191 (75%), blurred, falling to the
right and a little towards the camera, as long as the buildings' and the harvester's.  Within 14 px of the canvas
edge it fades out.


The blast (fx/)
---------------
Each HD frame is TS's own frame (Firestorm's MEMPFX, decoded with ANIM.PAL) drawn again at the canvas's
resolution, in place: TS px x 4 at canvas (16, 10), where in-mod/ has it (overlap 0.99), so the ring keeps TS's
size, shape and timing frame by frame and still reaches about 3 cells out on frame 11.
- The ring's outline is TS's, its pixel steps smoothed into a clean antialiased edge.
- The colours are TS's 12 (four lavenders, four maroons, a cream, two oranges and white), each streak and speck
  where TS has it: TS's pixels of each colour family are redrawn as one shape with rounded, antialiased edges
  instead of 4 x 4 blocks, and within a family the shade runs smoothly between TS's own shades.
- A fine grain through the colour, long along x as TS's streaks are (as the units' paint carries one).
- Opaque, as in-mod/'s; nothing added that TS's frames lack (no glow, no new sparks).


3D model (ts-memp-hd-3d/)
-------------------------
- Nodes: MobileEMP > unit_facing_east > hull.
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.  The unit faces east (the mod's facing 24).
- The meshes are exact (each voxel section's boxes), subdivided so the vertex colours carry TS's colours.
- Camera "camera_mod": orthographic, the mod's camera, framing the canvas exactly (checked by drawing the mesh
  through it over frame 24: overlap 0.987).
- The file passes Khronos's glTF validator with no errors or warnings.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- Built straight from TS's voxels (above), not hand-modelled: nothing is interpreted, every detail is where TS
  has it.
- TS's single-voxel speckle held near the colour round it (its paint is speckled voxel by voxel).
- On the ground, 23 canvas px lower than in-mod/'s float (Look, above).
- The blast redrawn from TS's frames rather than repainted (The blast, above): faithful to TS's layout, its
  pixels' blockiness replaced by smooth shapes.  A glow round the ring, or the blast drawn translucent, would each
  be a one-line change if you want the effect to read as light.


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are.
  vxlunit.py, tsnormals.py   a voxel section as boxes, its convex edges, TS's colours and normals across its faces
  voxrender.py           one frame of a voxel unit with the buildings' look
  rc.py, rcrender.py     the ray caster and the buildings' look for models made of convex parts
  vexport.py, rcexport.py   the .glb;  glbcheck.py  draws the .glb through its camera to check it
  vdeliver.py, vcheck.py    renders, previews and checks a unit from its spec
  memprender.py          the frame layout and camera;  mempspec.py  its frames, previews and README
  mempexport.py          the .glb;  mempfx.py  the blast's frames and previews
    PKG=out python3 vdeliver.py mempspec render 0 1      renders frames/
    python3 mempfx.py out; python3 mempfx.py out previews      renders fx/ and the blast's previews

