Mobile EMP Cannon (TS [MOBILEMP], Firestorm) in HD for Tiberian Factions: TSMEMP  -  v3
=======================================================================================

frames/     tsmemp-0000.png ... tsmemp-0031.png, the mod's 32 frames on its 384 x 384 canvas, each with a -trim.png
            (white = house colour, antialiased), with the unit's shadow; 32 facings counter-clockwise from north
            (0 N, 8 W, 16 S, 24 E)
fx/         tsmempfx-0000.png ... tsmempfx-0011.png, the blast: the mod's 12 frames on its 1152 x 576 canvas, played
            once at the unit's centre on the ground, each with a -trim.png (all black: the blast takes no house
            colour) - v1's, unchanged
previews/   8-facings.png            the mod's frames beside HD, every 4th facing
            turn.gif                 all 32 facings in turn, the mod's frames beside HD
            scale.png                next to the HD harvester and EA's M.A.D. Tank, as the game draws them
            shape-8-facings.png      the model drawn flat (a colour per part) in the mod's camera beside the mod's
                                     frames, every 4th facing, with the silhouette overlap
            closeups.png             the emitter, the conduits and the deck at 3x in two facings
            slot-closeup.png         the grey box's cockpit slot at 4x in four facings
            blast.gif, blast-frames.png, blast-close.png   the blast (v1's)
ts-memp-hd-3d/   the 3D model, in its own zip (ts-memp-hd-3d.zip) next to this folder:
            tsmemp.glb   the unit (vertex colours), standing on the ground at its position, with the mod's camera
src/        the model, the renderer and the checks (see Rebuilding below)

v3 replaces v2 (and v1): v2's canvas, size, place, facings, look, shadow and blast, with a cockpit slot on the
grey box.


What changed from v2
--------------------
- A cockpit slot across the front of TS's grey box on the deck (Luke: "Put a cockpit slot on the right grey box?
  Similar to the disruptor?" - the box to the right of the emitter as the unit faces you): the Disruptor's viewport,
  dark glass lighter towards its top in a grey frame standing a little proud of the face, made long and low to fit
  the box's front (TS's box is only 2 voxels high): the glass 4.6 x 0.8 voxels, about 60% of the box's width, high
  on its front.  TS's box front is plain grey (Judgement calls).  It faces forward, so it shows in the facings that
  look at the unit's front (about 10 to 22); facing east (24) it turns edge-on behind the tower.
- Nothing else changed: every other part, the paint, the house colour, the camera and the blast are v2's.


What changed from v1 (in v2)
----------------------------
v1 copied TS's voxel box by box, so it still read as voxels.  v2 on are built the way the Titan, the Wolverine, the
Disruptor and the Dropship are: TS's voxel (M_EMP.VXL) is the blueprint - where every part is and how big - and each
part is modelled clean (flat plates, true slopes, round wheels and pipes, bevelled edges) in TS's own colours, with
panel joints, hatches, vents, louvres, ribs and bolts.  The voxel is the source of truth: every part, step and colour
below was read from it slice by slice.  Westwood's Firestorm icon and the HD render Luke sent (a GDI-badged render of
the unit) are the guide to how TS's parts read in HD where TS's voxel has the part: the emitter's glowing orb on its
plinth, the ribbed conduits, the hatch box.  House colour stays where TS has it (Luke): the track covers.

The Mobile EMP Cannon, part by part (TS's layout; q = TS's voxel coordinates, x back to front 0..36, y right to left
0..29, z up 0..18; a U - two track pods the whole length joined by the hull at the front, open at the back):
- Two track pods (TS: y 0..5 and 24..29): near-black belts with grousers round an idler at the back and a sprocket
  at the front (TS's light grey faces at x 1..5 and 30..35), the bottom run along z 0..1, the top run at z 5..6; six
  light grey road wheels between the runs (TS's pairs at x 6..30, seen through the open side), dark hubs; grey
  housings at both ends above the belt (TS: x 0..10 and 25..36, z 6..8) with a joint, bolts and a louvred vent.
- The track covers in house colour (TS: z 8..9 the whole length x 2..34, a skirt down to z 7 over the middle, x 11..24
  on the outer side), joints across where the skirt starts and ends; the right cover's inner edge ochre by the
  emitter's plinth (TS's).
- The hull between the pods (TS: x 12..34, y 5..24, z 3..9, dark ochre), flush with the covers: TS's joints across
  and along its top, a bolted plate under the conduits (TS's darker patch at x 12..17), a hatch with a handle on its
  front right, TS's olive band along its front's foot and two louvred vents in its front; at its back - the U's
  inner end - a bolted door, and TS's grey lip along its top (x 9..12, z 7..9).
- The prongs' inner walls aft of the hull (TS's khaki, olive and brown machinery at x 1..12, z 3..7): olive panels
  low down, louvred vents.
- The emitter (TS's tower on the hull's right front: an octagon x 20..27, y 6..13, z 9..16, a little wider at z
  13..16): the grey octagonal tower with TS's dark slits up four of its faces, a collar with bolts, a crown, and the
  orb on top (TS's light grey cap at z 16..18), pale blue and glowing (Westwood's icon), faceted; on TS's olive ring
  round its foot, a bolted octagonal plinth (the render's).
- TS's grey box on the hull's left front (x 21..29, y 16..24, z 9..11): a hatch in its lid, a handle, bolts, and a
  cockpit slot across its front (Luke's; the Disruptor's viewport): dark glass in a grey frame.
- TS's two conduits across the hull by the U's inner end (x 14 to z 12, x 15..17 to z 11, y 9..20), ribbed (the
  render's hose), on dark mounts at their ends (TS: x 12..16, y 8..10 and 18..21).

The model's silhouette overlaps the mod's frames by 0.92 drawn flat in the mod's camera
(shape-8-facings.png); the finished frames by 0.923 (src/vcheck.py).  Both with the mod's frames moved down 23
px: they float, the HD unit stands on the ground (Look, below).


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.26 canvas px per voxel, the
  unit's position (TS's HVA origin) at canvas (191.0, 190.8): the size and place the mod's frames have (v1's find).
- On the ground: TS's voxel floats, its lowest voxel 4.3 voxels above the unit's position (about 3 classic px), and
  the mod's frames draw it so.  As the hand-off allows (and v1), the model sits on the ground at its position, with
  its shadow under its tracks like the other vehicles': the frames draw it 23 canvas px (2.8 classic px) lower than
  in-mod/, at in-mod/'s size and x.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides facing
  the camera as on the other units; plate edges are bevelled in the shading.  The game draws this canvas at two thirds
  (8 canvas px per classic pixel), so the outline, the shadow's blur and the contact shadow are 1.5 times as wide on
  the canvas.
- Paint: TS's colours, one per part - the dark ochre hull (TS 148-150, lifted so it renders as the mod's frames show
  it), grey tower, box, conduits and housings (TS 42-56), near-black belts (TS 57-63) round light grey wheels (TS 42),
  TS's khaki and olive machinery (TS 73, 116, 138-140); the orb pale blue, glowing a little; the cockpit slot's glass
  the Disruptor's, dark and lighter towards its top with a soft sheen.  Grime rises from the
  ground on the running gear.
- House colour is pure green 0,214,0 x (1 + 1.1 grain) on TS's house-colour track covers, thin joints as detail; the
  -trim masks cover exactly the green.


Shadow
------
Every frame carries the unit's shadow, black at alpha 191 (75%), blurred, falling to the right and a little towards
the camera, as long as the buildings' and the harvester's.  Within 14 px of the canvas edge it fades out.


The blast (fx/)
---------------
v1's, unchanged: TS's own frames (Firestorm's MEMPFX, decoded with ANIM.PAL) drawn again at the canvas's resolution,
in place, so the ring keeps TS's size, shape and timing frame by frame and still reaches about 3 cells out on frame 11
(src/mempfx.py).


3D model (ts-memp-hd-3d/tsmemp.glb)
-----------------------------------
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.  The unit faces east (the mod's facing 24).
- Nodes: MobileEMP > unit_facing_east > hull (its parts: belt_top, belt_bottom, belt_core, belt_end, sprocket,
  road_wheel, hub, housing, cover, cover_skirt, deck, lip, ledge, plinth, tower, collar, crown, orb, hatch_box,
  conduit, mount, cockpit_slot, cockpit_slot_frame...).  The meshes are exact (each part cut from its own planes and curved surfaces).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 384 canvas exactly
  (checked by drawing the mesh through it over frame 24: overlap 0.984).
- Vertex colours: COLOR_0 albedo (no light or shadow; the paint's areas - its joints, slots and bolts are finer than
  the mesh), COLOR_1 house colour (white = house colour).
- Khronos's glTF validator: errors 0, warnings 0, infos 0, hints 0.


Judgement calls (each one easy to change)
-----------------------------------------
- One paint colour per part (TS's), rather than TS's voxel-by-voxel speckle (v1).
- The hull's ochre lifted from TS 149 so it renders as light as the mod's frames show it.
- The tracks as belts round six road wheels, a sprocket and an idler: TS's light grey wheel pairs and end faces.
- The emitter's orb pale blue and glowing (Westwood's icon; TS's cap is light grey); its plinth octagonal (the
  render's is hexagonal; TS's ring round the tower's foot follows the tower's eight sides).
- The conduits ribbed (the render's hose; TS's are plain grey bars).
- The cockpit slot on the grey box's front (Luke: "similar to the disruptor"; TS's box front is plain grey): the
  Disruptor's viewport glass and frame, 4.6 x 0.8 voxels, high on the box's front.
- On the ground, 23 canvas px lower than in-mod/'s float (as v1).


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are.
  mempmodel.py           the model: every part, in TS's voxel section's own frame, posed by its HVA
  mempmat.py             the paint and the detail (joints, bolts, louvres, ribs, grousers), per pixel from each hit's q
  mempcam.py             the canvas, the camera and the facings
  memprender.py          one frame:  python3 memprender.py 0,12,24 [ss] [outdir]
  mempspec.py            the frames, previews and checks for vdeliver.py
  mempexport.py          the .glb;  glbcheck.py  draws the .glb through its camera to check it
  mempshape.py           the shape sheet;  mempclose.py  close-ups of any frame at any scale
  mvox.py, mdump.py, hcls.py   TS's voxel drawn, sliced as text, and its palette classes
  mempfx.py              the blast (v1's)
  mpkg.py, mtab.py       the package (checks, previews, README, 3D model, zips) and the review page's tab
  rc.py, rcrender.py, qparts.py, rcexport.py, glbtools.py, frameio.py   the ray caster, the buildings' look for
                         models made of convex parts, the .glb writer
  vdeliver.py, vcheck.py    renders, previews and checks a unit from its spec
    PKG=out python3 vdeliver.py mempspec render 0 1      renders frames/
