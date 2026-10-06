TS Dropship (TS [DSHP]) in HD for Tiberian Factions: TSDSHP  -  v3
==================================================================

frames/     tsdshp-0000.png ... tsdshp-0003.png, the mod's 4 frames on its 656 x 656 canvas (EA's density: the game
            draws it 1:1), each with a -trim.png (white = house colour, antialiased):
              0       the ship, side-on and level, facing west, in house colour where TS paints house colour
              1-3     frame 0 scaled to 55%, 70% and 85% about the canvas centre, as your packer makes the shadow
                      frames (regenerate them from frame 0 as before if you prefer)
facings/    tsdshp-0000.png ... tsdshp-0031.png, the ship in all 32 directions, counter-clockwise from north (0 N, 8 W,
            16 S, 24 E, as your other units), level, on the same canvas at the same size, each with a -trim.png.  It turns about the canvas centre (where the game puts the unit), so facing 8 is frames/ frame 0.
previews/   ship.png                 frame 0 beside the mod's current frame 0 and v1's
            closeups.png             the nose, the middle and the tail of frame 0 at 3x, the mod's beside v3's
            cockpit.png              the cockpit beside Westwood's FMV: head-on, from the front quarter, frame 0
            shadow-frames.png        frames 1-3 beside the mod's
            facings.png              every fourth direction (facings/)
            facings-turn.gif         all 32 directions in turn
            shape.png                TS's voxels against the model, both drawn flat (red: TS's only, blue: the
                                     model's only), from the game's angle, the side, the top, the front and the back
            scale.png                next to EA's C-17 and Badger, as the game draws them
ts-dshp-hd-3d/   the 3D model, in its own zip (ts-dshp-hd-3d.zip) next to this folder:
            tsdshp.glb   the ship (vertex colours), with the mod's camera
src/        the model, the renderer and the checks (see Rebuilding below)

v3 replaces v2 (and v1): same canvas, size, place, frame layout, directions and shape.


What changed from v2
--------------------
- House colour (Luke: the Dropship takes house colour).  Where TS paints house colour - the cargo door, the sponsons'
  sides, the pods' end frames, the skids and rails, the nav lamps - v2 had GDI's gold with all-black -trim masks;
  v3 has the HD units' house colour there (pure green 0,214,0 x (1 + 1.1 grain)) and every frame's -trim mask
  covers it.  The pods' frames' faces into the intakes are house colour too (v2 darkened them; the light shades them
  now).  Nothing else changed.


What changed from v1 (in v2)
----------------------------
v1 copied TS's voxels box by box, so it still read as voxels.  v3 is built the way the Titan, the Wolverine, the
Disruptor and the Hover MLRS are: TS's voxels (DSHP.VXL) are the blueprint - where every part is and how big - and each
part is modelled clean (flat plates, true slopes, bevelled edges, smooth curves where TS's hull curves) in TS's own
colours, with panel joints, hatches, vents, louvres and bolts.  The voxels are the source of truth: every part, step
and colour below was read from them slice by slice.  Westwood's FMV still and the mods' renders Luke sent are the guide
to how TS's parts read in HD where TS's voxels have the part: the cockpit's window, the slits beside it, the side
windows.

Luke's notes on the way, all in v2 and v3:
- The body: good as it came.
- More detail on the nose and the tail.
- The cockpit: TS's dark band round the front of the nose, made a window - then one window the shape and size of
  Westwood's FMV (smaller than the first wrap-around windscreen), then a little taller.
- The nose and the cockpit smoothed: the nose is one smooth body now, the cockpit's housing running into it.

The Dropship, part by part (TS's layout; q = TS's voxel coordinates, x back to front 0..95, y right to left 0..43,
z up 0..23; the ship is symmetric about y 21.5, TS's centre line):
- The tail (TS: x 0..24): a tapering arch, lofted through TS's own cross-sections (its filled voxels smoothed, so TS's
  steps become curves), its top rising from z 12 at the back to z 22; a raised spine along its top (TS's light strip)
  carrying two vent panels with slots (on TS's dark patch at x 15..20, and a smaller one aft), TS's dark vents either
  side of it (x 12..13); joints round it and along its sides, rivets along the joints, a bolted access hatch above and
  below the side joint, louvres low on each side by the door.  Its back is the cargo door in house colour (TS's
  house-colour voxels): upright at the top, its foot sloping forward to z 3 (TS: x 0..5), framed, ribbed across, a vent in its top,
  hinge blocks along its foot.  A dark keel under the tail (TS: x 15..25, z 3..8).
- The lower body: a landing block at each end (TS: rear x 21..32, front x 59..75, 9.5 out, z 3..12) in TS's ochre,
  the rear one's back sloping and dark, the front one's chin sloping up to the nose, a row of TS's yellow lamps along
  its sides (x 61..70, z 8..9); the grey bay between them (TS: 7 out), ribbed; under the blocks the house-colour skids (TS:
  z 0..3, either side of a grey channel) and house-colour rails between them.
- The sponsons along the bay (TS: x 30..54): house-colour sides bulging out to 12.5 (z 10..13), their tops sloping in; a dark
  underside; on them TS's red-brown deck, a strip raised from the cabin's wall to 9.6 out (TS's red rows at z 15).
- The cabin above: the back half (TS: x 24..46, 11 wide, its roof at z 22) and the front half (x 46..63, 13 wide,
  roof at z 23), TS's brown roofs (a bolted hatch on the front one), bands down the sides (brown under the roof's edge,
  light ochre, browner low down), joints; TS's amber lamps on the sides at the step (x 46, z 19); the brow sloping down
  to the front beam, chamfered along the slope (TS's narrower top voxels).
- The neck forward to the nose (TS: x 66..76): a floor, two pipes along its sides (TS's 3 x 3 tubes at 4 out,
  z 15.5), a gabled roof up to TS's spine, dark inside; TS's amber lamps on its sides and either side of its spine.
- The beams across the top (TS: rear x 29..36, front x 65.5..73, z 18..21): TS's flat planks, their edges rounded,
  TS's two grooves along their tops; dark collars where they meet the pods.
- Four engine pods (TS: rear x 22..45, 15..20 out, z 15..22; front x 60..78, 15.5..19.5 out, z 16..22): ochre
  nacelles with joints, an access panel on the outer side and TS's dark band behind the rear frame; house-colour
  frames at both ends (TS's two-voxel rings) round dark intakes with vanes; under each a dark olive thruster box (TS: rear
  x 24..39, z 11..18; front x 61..74, z 13..18), its lower tier a voxel further out, louvres across it, a grille
  underneath.
- The nose (TS: x 76..95), one smooth body: TS's nose (its filled voxels, smoothed) with the cockpit's housing
  running into it.  TS's light panel along its top, its brown shoulders, TS's brown band round it at the top of its
  lower lip (z 14..15), joints; three small side windows behind the cockpit (the mods' renders); TS's nav lamps in
  house colour either side of the lip's front.  The dark nose-gear keel under it (TS: x 69..87), its bay doors outlined.
- The cockpit (TS's dark band round the front of the nose at z 14..16; Westwood's FMV for its shape): the upper
  nose's front, above TS's lower lip, flat - a plate leaning back 22 degrees, carried up square by the housing
  (Westwood's front is a tall plate; TS's nose narrows to its top there) - with one window in it, the FMV's: a rounded
  rectangle a little wider at its top, about twice as wide as it is tall, nearly the plate's width, framed, dark glass
  with the sky's reflection lighter towards its top, its recess darker at the top and sides; the FMV's two slits
  stacked either side of it on the housing's rounded corners.  It faces forward, so frame 0 (side-on) shows it as a
  sliver at the nose's front.

The model's silhouette overlaps TS's voxels by 0.96 in frame 0's camera (0.95 over the five views of
shape.png), drawn flat; the finished frame 0 overlaps the mod's by 0.96.


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north, the ship facing west; 6.33
  canvas px per voxel, TS's HVA origin at canvas (279.4, 326.8): v1's size and place (found by matching TS's voxels
  to the mod's frame 0), so the hull's centre is where it is now and the ship is as BIG as you signed off.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides facing
  the camera as on the other units; plate edges are bevelled in the shading, and the tail and the nose are shaded
  with their smooth bodies' own normals.  This canvas is at EA's density, so the outline is the buildings' width.
- Paint: TS's colours, one per part - GDI's ochre (TS 144-152) with TS's brown panels (153-162: the cabin's roofs, the
  beams, the nose's shoulders), the pods' dark olive thruster boxes (TS 77), the grey bay (47-56), near-black keels
  and collars (57-60), the sponsons' red-brown decks (108), TS's amber (7) and yellow (181) lamps, dark glass.
- House colour is pure green 0,214,0 x (1 + 1.1 grain) where TS paints house colour - the cargo door, the sponsons'
  sides, the pods' end frames, the skids and rails, the nav lamps - with thin seams and the door's vent slots as
  detail; the -trim masks cover exactly the green (v2: GDI's gold there, all-black trims).
- It flies: no ground shadow, grime or ground occlusion is baked in.


Shadow
------
None baked: frames 1-3 are the ship itself, scaled, which the game draws darkened on the ground as it descends.


3D model (ts-dshp-hd-3d/tsdshp.glb)
-----------------------------------
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (128 px on this canvas and in the game).
  Origin: the point the ship turns about in the game (the canvas centre), 7.67 voxels (0.379 cell) aft of TS's HVA
  origin.  The ship faces east (the mod's facing 24) like the other units' models; turn 'unit_facing_east' about its
  up axis for any other facing.
- Nodes: Dropship > unit_facing_east > hull (its parts: tail, tail_end, tail_spine, keel, the blocks, bay, skids,
  rails, sponsons, decks, the cabin, brow, the neck's floor, pipes and roof, the beams, the pods' nacelles, frames,
  intakes, thruster boxes and collars, the nose, the lamps).  The meshes are exact (each part cut from its own planes
  and curved surfaces); the tail's and the nose's carry their smooth bodies' normals.
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 656 canvas: through it
  the model as delivered is facings/ frame 24 (checked by drawing the mesh through it over that frame: overlap
  0.991), and turned to face west, frames/ frame 0.
- Vertex colours: COLOR_0 albedo (no light or shadow; the paint's areas - its joints, slots and bolts are finer than
  the mesh), COLOR_1 white where TS paints house colour (house green in COLOR_0, as in the frames).
- Khronos's glTF validator: errors 0, warnings 0, infos 1, hints 0.


Judgement calls (each one easy to change)
-----------------------------------------
- One paint colour per part (TS's), rather than TS's voxel-by-voxel speckle (v1).
- The tail and the nose follow TS's cross-sections smoothed (TS's voxel steps made curves); the nose a little more
  (Luke: smoother), which rounds TS's step where the nose widens at x 83 into one flowing shape.
- The cockpit: TS's dark band round the nose's front is one window the shape of Westwood's FMV's, on a flat plate
  leaning back 22 degrees.  To fit it, the plate is carried up square by a small housing that stands at most half a
  voxel proud of TS's nose; TS's band is a brown stripe either side of it.
- The three small side windows (the mods' renders; TS has none).
- The vent panels on the tail's spine sit on TS's dark patch; the slits beside the cockpit are the FMV's.
- The beams as TS's flat planks with rounded edges; Westwood's FMV shows round tubes.
- The nav lamps in house colour, as TS paints them (the FMV's are red), glowing a little.
- Westwood's eagle decal is left off.


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are.
  dshpmodel.py           the model: every part, in TS's voxel section's own frame, posed by its HVA
  dshpvox.py             TS's voxels as data: filled slices, half-widths, the smoothed bodies the tail is lofted through
  dshpnose.py            the nose and the cockpit as one smooth body on a fine grid (the plate, the housing)
  dshpmat.py             the paint and the detail (joints, bolts, louvres, vents, windows), per pixel from each hit's q
  dshpcam.py             the canvas, the camera and the facings
  dshprender.py          frames and facings:  python3 dshprender.py frames 0,1,2,3 [ss] [outdir]
                                              python3 dshprender.py facings 0,4,8 [ss] [outdir];  renderall.sh  all
  dshpexport.py          the .glb;  glbcheck.py  draws the .glb through its camera to check it
  dshpcomp.py            TS's voxels against the model, drawn flat (the shape sheet)
  dshpsheets.py, dshplook.py   the previews and side-by-sides;  dshppkg.py, dshptab.py   the package and the review tab
  dvox.py, dreg.py, vdump.py, hcls.py   TS's voxels drawn (whole or a region), sliced as text, their palette classes
  rc.py, rcrender.py, qparts.py, rcexport.py, glbtools.py, frameio.py   the ray caster, the buildings' look for
                         models made of convex parts, the .glb writer
