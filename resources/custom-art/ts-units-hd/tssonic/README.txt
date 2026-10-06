Disruptor (TS [SONIC]) in HD for Tiberian Factions: TSSONIC  -  v5
==================================================================

frames/     tssonic-0000.png ... tssonic-0063.png, the mod's 64 frames on its 448 x 448 canvas, each with a -trim.png
            (white = house colour, antialiased):
              0-31    the hull with its shadow, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E)
              32-63   the turret (the turntable, the dish and its arm), no shadow, 32 facings, drawn lined up with
                      the hull frames' unit position (v1-v4: the mod's turret pivot, 1.5 px right of and 2 px above
                      it); the game seats it on the green rear deck (see The turret's seat below)
previews/   8-facings.png            the assembled unit, the mod's frames beside HD, both with the turret seated on
                                     the rear deck
            hull-8-facings.png, turret-8-facings.png   each set on its own, every 4th facing
            turn.gif, turn-hull.gif, turn-turret.gif   all 32 facings in turn, the mod's frames beside HD
            scale.png                next to the HD harvester, as the game draws them
            shape-8-facings.png      the model drawn flat (a colour per part) in the mod's cameras beside the mod's
                                     frames, the hull's and the turret's every 4th facing, with the silhouette overlap
                                     (v5's turret pad is smaller than TS's on purpose)
            arm-closeup.png          the turret's arm at 4x in four facings
            viewport-closeup.png     the ochre box's viewport at 4x in four facings
ts-sonic-hd-3d/   the 3D model, in its own zip (ts-sonic-hd-3d.zip) next to this folder:
            tssonic.glb  the hull and the turret (vertex colours), the turret under its own node, with the mod's camera
src/        the model, the renderer and the checks (see Rebuilding below)

v5 replaces v4 (and v3, v2, v1): v4's canvas and look; the turret at the mod's size again with only its circular
pad smaller, the pad centred on the green deck and standing on it in every facing.  The rules' TurretOffset becomes
-110 (v4: -111) and the sonic wave's start (the horn's tip) moves out again: see The turret's seat.


What changed from v4
--------------------
- The dish and the rest of the turret are back at their size, the mod's (Luke: v4 made the dish smaller too; only the
  circular pad should be smaller).  Only the pad - the turntable and its rim - stays smaller: 0.70 of TS's radius, its
  height TS's, so on screen it is v4's pad.  The turret's dark base blocks under the dish's ends, the dish, and the arm
  with its brackets and pistons reach past the smaller pad, as TS's arm reaches past its ring.
- The pad is centred on the deck side to side and stands on it, in every facing (Luke: it was off-centre and over the
  deck's right edge).  Three things moved it:
  - the turret frames are drawn lined up with the hull frames' unit position.  v1-v4 kept the mod's turret camera,
    whose pivot sits 1.5 px right of and 2 px above where the hull frames put it: harmless under TS's big turntable,
    enough to push the small pad toward the deck's far edge;
  - the hull is centred side to side on the unit's position (TS's hull sits 0.11 voxel left of it; the hull frames move
    0.7 px);
  - the turret is lowered 0.58 voxel so the pad stands on the deck's top (TS's turntable floats that far above it, which
    showed the pad hovering toward the far edge).
  The pad is now 0.51 voxel inside the deck's edges on both sides, and seated 0.51 voxel inside its back edge too
  (13.19 voxels aft; TurretOffset -110, v4 -111).  Checked in all 32 facings against the 3D model (src/seatcheck.py).
- The turntable's and the brackets' stripes are v3's again (the turret is v3's size).


What changed from v3 (in v4)
----------------------------
- The turret stays on the green rear deck (Luke: it overhung the back and the sides; it should stay on the green).
  TS's turntable is 17 voxels across and the deck 13, so the turret is drawn at 0.69 of the hull's scale (v1-v3: 0.98,
  TS's size as the mod draws it), shrunk about its base so it sits on the deck as v3's did.  Its ring now sits inside
  the deck at every facing: its back at the deck's back edge, its sides a third of a voxel inside the deck's.  Its two
  sections are centred on the pivot (TS's turntable sits half a voxel off the turret's rim, and the turret a third of
  a voxel right of the pivot), so the ring turns on the spot.
- The house colour is plain (Luke: the grilles, detail and black lines on the house-colour areas look fuzzy in the
  game as the unit moves).  The rear deck's joints, hatch and louvred vents, the louvred blocks' ribs, and the front
  box's joints, side louvres and hatch are gone, and so are the dark gaps between the rear grille's fins (Luke, again
  with the game's screenshot: grilles too); the shapes and their bevelled edges carry those parts.
- TS's green rear deck and front box were a voxel to the left in v1-v3 (the deck at TS's y 7..20 instead of 6..19,
  the front box 6.6..13.4 instead of 6..12 and its base 5.6..14 instead of 5..13).  They are now where TS's voxels
  have them, centred on the hull, and the left louvred block is TS's two voxels wide (v3: three).
- The turntable's hazard stripes and the brackets' stripes keep v3's width on screen (their spacing grows as the
  turret shrinks), so they don't get finer.


What changed from v2 (in v3)
----------------------------
Luke: a viewport, not a full cockpit.  v2 rebuilt the ochre box on the front left as a cab (a windscreen raked down
from its roof in two panes, a rear window).  v3 keeps the box as the first look had it - its raised front part,
the hatch on top, the joint round it - and puts one viewport across its front, where TS has its dark voxels (TS:
x 41..42, y 15..19, z 8..10): dark glass in an ochre frame.  Everything else was v2's: the turret on the hull's back,
the arm, the striped zig-zag brackets.


What changed from v1 (in v2)
----------------------------
v1 copied TS's voxels box by box, so it still read as voxels.  v2 on are built the way the Titan, the Wolverine, the
MCV, the Mammoths, the APC and the War Factory are: TS's voxels (SONIC.VXL the hull, SONICTUR.VXL the turntable and
the turret) are the blueprint - where every part is and how big - and each part is modelled clean (flat plates, true
slopes, round tubes, bevelled edges) in TS's own colours, with panel joints, hatches, louvres, vents, bolts and straps
to the Titan's and the Wolverine's standard.  The voxels are the source of truth: every part, step and colour below
was read from them slice by slice.  Westwood's art of the Disruptor is the guide to how TS's parts read in HD where
TS's voxels have the part: the dish's white panels, the hazard stripes round the turntable, and (Luke sent it) the FMV
close-up of the emitter arm - its caps, fins, straps, the trunnion through its front, the zig-zag brackets under it and
the spring pistons beside it.

The Disruptor, part by part (TS's layout; q = TS's voxel coordinates, x back to front, y right to left, z up):
- Four track pods (TS's: the rear pair q x 2..22, the front pair x 23..45): black belts with rounded ends and
  grousers, under GDI's ochre covers whose skirts come down to z 3 and whose ends slope (TS's); the covers in plates,
  a joint along each skirt, bolts along its foot.
- The dark hull between the pods (TS: z 3..8), TS's light grey floor in the trench beside the front box (joints
  across it) and TS's ochre band across the hull ahead of the rear deck.
- The rear deck in house colour (TS: x 3..21, y 6..19, up to z 10), plain, the turret on it; its back a grille
  stepping down to the rear plate (TS's house colour y 6..18), plain; TS's blocks on the rear pods' inner edges (TS:
  x 6..14, y 3..6 and 19..21), plain house colour, with their black posts.
- The long house-colour box on the front right (TS: x 26..46, y 6..12, up to z 11, its back end a step lower), plain,
  on its black base (TS: y 5..13), coming down at the front to z 5.
- GDI's ochre box on the front left (TS: x 34..41, y 14..20, z 4..10, its front higher, z 11): a viewport across its
  front (Luke), where TS has its dark voxels (x 41..42, z 8..10), dark glass in an ochre frame; a hatch with a
  handle on top, a joint round its middle.
- The olive plate across the front's left (TS: x 44..46) with two vent grilles.
- The turret (SONICTUR, TS's two sections, posed by SONICTUR.HVA, each centred on the pivot and lowered 0.58 voxel so
  the pad stands on the deck; drawn at the mod's size, its pad - the turntable and rim - at 0.70 of TS's radius): the
  turntable in TS's ochre and black (Westwood's
  hazard stripes) inside TS's grey rim (bolted); the dark base - a block each side under the dish's ends with grey
  rails on top, a post under the dish's middle stepping down in front of it (TS's); the dish, TS's curved shell
  standing across the turret, concave forward, grey with TS's white band across its face, in Westwood's panels;
  behind it the post holding it (blue-grey at its top) and a blue-grey brace each side; olive fittings at its four
  corners.
- The emitter arm (Luke: work on the arm pointing to the dish; the FMV close-up): TS's rod two voxels thick on the
  turret's middle (q x 15 to the tip at x 22), rising toward the dish at TS's 12 degrees (TS: its tip at z 2..4, its
  back end at z 4..5), so it points back into the dish.  Back to front: a white end cap (TS 37) and lip, the light
  grey body (TS 41-43) with TS's raised band (bolted) and a strap, the dark sleeve (TS 53-58) with a strap, four fins
  behind the tip, a collar and TS's grey tip (TS 48-51).  The trunnion runs through it at the fins (the FMV's), its
  nuts outside a zig-zag bracket each side (TS's dark supports at y 7 and 10, x 15..20, down to the turntable); a
  plate ties the brackets' feet under the arm's front.  A spring piston each side (TS's dark side members, y 5..7
  and 11..13) runs from a beam across the turret in front of the dish (TS: x 11..12, black at its right end) to the
  brackets.  Under the arm's back half TS is open to the turntable (TS: x 13..15), and so is v5.
- The arm in TS's colours (Luke: stick to TS's); the zig-zag brackets striped across as the FMV's, in TS's ochre and
  black (the turntable's) (Luke: keep the stripes and zig-zags).

The model's silhouette overlaps the mod's frames drawn flat in the mod's cameras (shape-8-facings.png): the hull by
0.95, the turret by 0.76 against the mod's turret (v5's pad is smaller on purpose, so they can't match
there).  The finished frames: the hull's by 0.950 against the mod's (src/vcheck.py), the turret's by 0.747
against the mod's turret.


The turret's seat
-----------------
Luke: the turret stays on the green rear deck, at the back of the unit (v2 and v3 put its ring on the hull's back,
over the grille; Luke: it overhung the back and the sides), centred on it (v5).  Its pivot is 13.19 voxels aft of
the unit's position along the hull's facing - 0.43 cell, 82.7 px on this canvas, in TS's terms TurretOffset=-110 (v4:
-111; v3: -117; TS's own -64, a quarter cell) - so its pad sits 0.51 voxel inside the deck's back edge, as it does
inside the deck's sides.  The turret's frames are drawn about the turret's own pivot (the game turns the turret on its
own, so its frames can't carry the offset), lined up with the hull frames' unit position: the game draws frame 32 + f
that far aft of the unit along the hull's facing, on the ground, so foreshortened as the camera draws the ground -
82.7 canvas px aft when the hull faces east or west, 43.8 px when it faces north or south, in between elsewhere
(dx = 82.7 sin a, dy = -43.8 cos a for the hull's facing a clockwise from north; previews/ draw it so).  Laid that
way, the turret sits where the 3D model puts it in all 32 facings: src/seatcheck.py draws the .glb turned to each
facing and compares (turret overlap 0.972 on average, its frames within 0.8 px of the model's).

The sonic wave starts at the horn's tip.  From the turret's pivot (on the ground under its middle), in leptons:
v5  107 forward, 0 across, 113 up;  v4  75 forward, 0 across, 108 up;  v3  107 forward, 3 right, 118 up.
So against v4 the weapon's fire point (FLH) moves 32 leptons out and 5 up; against v3 it is 3 to the left (the turret
is centred on its pivot; TS's sits a third of a voxel off it) and 5 down (the turret lowered onto the deck).


Look
----
- Cameras: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; as v1 and the mod's frames
  have them: the hull at 6.27 canvas px per voxel with the unit's position at canvas (222.5, 222.7) (TS's hull reaches
  0.24 voxels below its HVA origin, so the model is raised onto the ground and the camera moved to match; v5
  centres it side to side on that position, 0.11 voxel); the turret at 6.15 px per voxel (the mod draws it 2%
  smaller than the hull; v4: 4.33, 0.69 of the hull's), scaled about its base on the deck and lined up with the hull's
  camera (v1-v4: the mod's turret pivot at (224, 221), 1.5 px right and 2 px up); its pad at 0.70 of TS's radius.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides
  facing the camera as on the other units; plate edges are bevelled in the shading, the rim shaded round.  The game
  draws this canvas at two thirds (8 canvas px per classic pixel), so the outline, the shadow's blur and the contact
  shadow are 1.5 times as wide on the canvas.
- Paint: TS's colours, one per part - GDI's ochre pod covers and box (TS 144-152), black belts, posts and frames
  (TS 59-63), the dark hull (TS 54-58) and TS's light grey trench floor (TS 47-51), the olive plate (TS 72-79); the
  turret's dark base, beam, brackets and pistons (TS 57-59, 166), its grey rim (TS 49), the dish grey with TS's white
  band (TS 32-43), blue-grey braces (TS 88-90), olive fittings, the arm as above.  Grime rises from the ground on the
  hull's running gear.
- House colour is pure green 0,214,0 x (1 + 1.1 grain) on TS's house-colour parts (the rear deck and its grille, the
  blocks on the rear pods, the front box), plain: no seams, louvres, vents, hatches or grille gaps on it (Luke: they
  look fuzzy in the game as the unit moves); the -trim masks cover exactly the green.


Shadow
------
Every hull frame carries the unit's shadow, black at alpha 191 (75%), blurred, falling to the right and a little
towards the camera, as long as the buildings' and the harvester's (v1's).  Within 14 px of the canvas edge it fades
out.  The turret's frames have none (in-mod/'s).


3D model (ts-sonic-hd-3d/tssonic.glb)
-------------------------------------
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.  The unit faces east (the mod's facing 24).
- Nodes: Disruptor > unit_facing_east > hull (its parts: track_cover, belt, body, rear_deck, rear_grille,
  side_louvre, post, box_base, front_box, front_low, ochre_box, viewport, viewport_frame, front_plate) and turret,
  seated 0.43 cell aft on the rear deck (its pad 0.51 voxel inside the deck's edges), scaled 0.98 about the turret's
  base (the mod's turret frames' size) and turning about its own local z axis > turntable (hazard_ring), turret_body
  (rim, base_side,
  rail, base_post, base_step, beam, arm_cap, arm_body, arm_band, arm_strap, arm_sleeve, arm_fin, arm_tip, trunnion,
  bracket, bracket_foot, bracket_plate, piston, piston_rod, spring, dish, dish_post, brace, fitting, ...).
  The meshes are exact (each part cut from its own planes and curved surfaces), in TS's sections' own frames (the
  turret's centred on the pivot and lowered onto the deck, the hull centred side to side); the turret node's scale
  (0.98) makes it the frames' size; the pad is 0.70 of TS's radius in the mesh.
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 448 canvas exactly
  (checked by drawing the mesh through it over hull frame 24 with turret frame 56 seated as above: overlap
  0.989).
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).
- Khronos's glTF validator: errors 0, warnings 0, infos 0, hints 0.


Judgement calls (each one easy to change)
-----------------------------------------
- One paint colour per part (TS's), rather than TS's voxel-by-voxel speckle (v1).
- Westwood's art where TS's voxels have the part: the dish's white panels (TS: a light band across a grey shell), the
  hazard stripes round the turntable (TS: its ochre and black).
- The arm from the FMV close-up where TS has the parts: the caps, fins, straps and trunnion on TS's rod; the zig-zag
  brackets and the spring pistons as TS's dark supports and side members.  TS's voxels fill the space round them
  (a solid dark mass at z 1..3); v5 keeps the brackets open, as the FMV's, so the turntable shows between them.
- The brackets' stripes are the FMV's (Luke: keep them); TS's brackets are dark.
- The turret at TS's size (as the mod draws it) with only its circular pad - the turntable and rim - at 0.70 of TS's
  radius, so the pad sits on the green deck at every facing (Luke): TS's turntable (17 voxels across) is wider than
  TS's deck (13).  The base blocks, the dish and the arm reach past the smaller pad.  Seated at the deck's back, 0.51
  voxel inside its edge as at its sides (0.43 cell aft; TurretOffset=-110) rather than TS's quarter cell.  Its two
  sections centred on the pivot (TS's are a third to half a voxel off it), so the pad turns on the spot.
- The pad stands on the deck: the turret lowered 0.58 voxel (TS's turntable floats that far above its deck), and the
  hull centred side to side on the unit's position (TS's sits 0.11 voxel left of it), so the pad is centred on the
  green in every facing (Luke).  The turret frames are lined up with the hull's unit position, not the mod's turret
  pivot (1.5 px right and 2 px up of it).
- The house colour plain (Luke), the rear grille included: TS draws it as four fins with dark gaps between them;
  here it is one plain green slope over TS's house colour (y 6..18), the dark hull beyond.  TS's blocks on the rear
  pods are plain house colour and keep their black posts (separate parts, not lines).
- The turntable's stripes at v3's width on the smaller pad.
- The viewport: TS's dark voxels across the ochre box's front as one framed window on the box's front face (TS
  rakes them a voxel forward at their foot).  TS also has dark voxels at the box's back end; they are left ochre
  (Luke: one viewport, not a cockpit).


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are.
  sonmodel.py            the model: every part, in TS's voxel sections' own frames, posed by their HVAs
  sonmat.py              the paint and the detail (joints, bolts, louvres, stripes), per pixel from each hit's q
  soncam.py              the canvas, the two cameras (the turret's scale, K_TUR) and the frame layout
  sonrender.py           one frame:  python3 sonrender.py 0,24,56 [ss] [outdir]
  sonspec.py             the frames, previews and checks for vdeliver.py (the turret's seat)
  sonexport.py           the .glb;  glbcheck.py  draws the .glb through its camera to check it
  sonshape.py            the shape sheet;  sonvcomp.py  TS's voxels against the model, frame by frame
  sonclose.py            close-ups of any frame at any scale;  sonlook.py  the assembled unit against the mod's
  sonpkg.py, sontab.py   the package (checks, previews, README, 3D model, zips) and the review page's tab
  svox.py, vdump.py, hcls.py   TS's voxels drawn, sliced as text, and their palette classes
  rc.py, rcrender.py, qparts.py, rcexport.py, glbtools.py, frameio.py   the ray caster, the buildings' look for
                         models made of convex parts, the .glb writer
  vdeliver.py, vcheck.py    renders, previews and checks a unit from its spec
    PKG=out python3 vdeliver.py sonspec render 0 1      renders frames/
