MCV (TS [MCV]) in HD for Tiberian Factions: TSMCV
================================================

frames/     tsmcv-0000.png ... tsmcv-0031.png, the mod's 32 frames on its 384 x 384 canvas, each with a -trim.png
            (white = house colour, antialiased).  Facings counter-clockwise from north: 0 N, 8 W, 16 S, 24 E.
previews/   8-facings.png        the mod's current frames (TS's voxel as the mod draws it now) beside HD, every
                                 4th facing
            turn.gif             all 32 facings in turn, the mod's current frames beside HD
            scale.png            next to the HD harvester and EA's RA and TD MCVs, as the game draws them
            shape-8-facings.png  the model drawn flat (a colour per part) in the camera of the mod's voxel render,
                                 beside that render, with the silhouette overlap per facing
3d/         tsmcv.glb            the model in TS's own colours (vertex colours) with the RA-grid camera
src/        the model, the renderer and the checks (see Rebuilding below)


What it is
----------
One 3D model read voxel by voxel from TS's own MCV.VXL (45 x 31 x 15 voxels), drawn the way the HD buildings, the
harvester, the Titan and the Wolverine are.  Every step, gap and detail is where TS's voxel has it: seen from the
top, both sides, the front and the back, the model's surface meets TS's voxels everywhere except a few single
voxels at the ends of the track belts and under the hull (src/vcompare.py checks it).  The silhouette overlap
with the mod's voxel render is 0.90 drawn flat in that render's own camera (shape-8-facings.png), and the
finished frames cover the mod's frames with an overlap of 0.95 (src/mcvcheck.py).

The MCV, from the voxel:
- Tracks: four units, each under a house-colour cover: a plate over the belt, a skirt a voxel in from the outer face
  with gaps where the dark track shows through (TS's notches along the covers' lower edge), end lips, the front lip
  down to the belt.  The belts loop round with sloped ends and links; TS's dark bits stand proud of the skirt where
  it has them.  The left belt's outer face has the recessed band TS gives it (its right belt is flush), with the
  middle wheel's bit standing in it.
- Hull: the lower hull on a dark underside, bumpers front and back.
- Right deck: the rail along its outer edge (with TS's notches), the spine along its inner edge; the orange rear
  block with its house-colour panel on top, a dark hatch at its outer back corner, its back stepped down to the
  rim and open underneath at its front; the house-colour panel block and strip bridging rail and spine with a
  voxel's gap under them; the cab at the front, its front stepped down in TS's three steps, the hatch on its roof.
- Crane: the pedestal in the channel down the middle (tapering at its foot), its saddle with the dark band along
  its right side, the boom: a cap, the housing (dark on top, white along its upper sides, two white bands across),
  the long white main tube, a joint with a slot through its top, the narrower front section; under the boom's
  front, the dark cradle rising in steps to the front.
- Left deck: the shelf of five crates with dark dividers between them and TS's bright studs on them, its inner
  edge dark; short rail pieces along its outer edge; the front-left block; the tow hitch at the front: the orange
  frame and plate, the dark coupling.


Look
----
- Camera: a true orthographic view 32 degrees above the ground, looking north; 6.1 canvas px per voxel, the size the
  mod has now (8 canvas px per classic pixel).  The unit's position (the voxel's HVA origin, on the ground) at canvas
  (192, 194), where the mod's frames have it, so the ground line is in-mod/'s and meets the Construction Yard's.
  (The mod's current frames are TS's 30 degrees; at 32 the MCV stands 2 to 3 px lower on the canvas at its top and
  at its near edge than in-mod/, with the same ground point and the same width.)
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides
  facing the camera as on the harvester, the Titan and the Wolverine; edges are softened in the shading so the
  plates read as pressed metal.  The game draws this canvas at two thirds, so the outline, the shadow's blur and
  the contact shadow are 1.5 times as wide on the canvas (as the Titan's and the Wolverine's).
- Colours are TS's own: every surface takes the palette colour (UNITTEM.PAL) of the voxels just inside it, soft
  across a face where TS speckles ochre and orange, sharper on the boom whose greys TS paints in bands.  The
  palette is TS's albedo; it is brightened by 1.25 so TS's ochre comes out as the HD buildings' ochre, whites held
  at white paint.  Grime rises from the ground on the hull and bumpers.
- House colour is pure green 0,214,0 x (1 + 1.1 grain) on the four track covers and the three deck panels (TS's
  remap voxels); the -trim masks cover exactly those parts.


Shadow
------
Every frame carries the unit's shadow, black at alpha 191 (75%), blurred, falling to the right and a little towards
the camera, as long as the buildings' and the harvester's (the MCV is low).  Within 14 px of the canvas edge it
fades out.


3D model (3d/tsmcv.glb)
-----------------------
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.
- Nodes: MCV > unit_facing_east (the mod's frame 24) > tracks, hull, right_deck, cab, crane, left_deck, hitch, each
  holding its parts.  The meshes are exact (each part cut from its own planes), subdivided so the vertex colours
  carry TS's colours.
- Camera "camera_ra_grid": orthographic, 32 degrees above the ground, looking north; it frames the 384 canvas
  exactly (checked by drawing the mesh through it over frame 24: overlap 0.995).
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- Colours straight from TS's voxels, rather than one colour per part: the orange rear block, the cab's orange
  middle, the shelf's yellow crates, the boom's bands are where TS paints them.  TS's darkest and lightest single
  voxels within a painted part are held within reach of that part's own colour, so its faces read as weathered
  paint rather than voxel speckle.
- Crisp where TS draws a detail with a voxel or two: the cab's roof hatch, the rear block's hatch, the crates'
  dividers (a quarter voxel lower than the crates), the studs on the crates (TS's bright yellow voxels).
- The deck panels plain: TS's stripes on the middle panel come from the shades of its remap voxels (noise, not
  ribs).
- House colour one green everywhere, as on every building: TS draws the track covers in darker remap shades than
  the deck panels.
- The left belt's recessed band kept as TS has it, though the right belt is flush.
- The shadow at the buildings' length (the Titan's and the Wolverine's are shorter so tall walkers' shadows stay
  on their canvases; the MCV is low).


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are (TS's voxel
and palette, the mod's frames, the harvester and EA's MCVs for the previews).
  rc.py, rcrender.py      a ray caster for models made of convex parts, with the buildings' look
  rcexport.py             convex parts to meshes (exact), for the .glb
  mcv.py                  the model's parts, read from the voxel;  mcvmat.py  materials;  tsfield.py  TS's colours
                          on the model's surface;  mcvrender.py  one frame;  mcvfinal.py  all 32
  mcvexport.py            the .glb;  glbcheck.py  draws the .glb through its camera to check it
  mcvcheck.py             checks the finished frames (sizes, trims, house green, shadow, against the mod's)
  mcvpreviews.py, mcvshape.py   the previews and the shape check
  vdump.py, vchars.py, vfaces.py, vcompare.py   the voxel read out layer by layer and face by face, and the model
                          checked against it
    PKG=out python3 mcvfinal.py 0 1      renders frames/
    python3 mcvexport.py tsmcv.glb
