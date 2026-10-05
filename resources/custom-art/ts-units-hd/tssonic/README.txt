Disruptor (TS [SONIC]) in HD for Tiberian Factions: TSSONIC  -  v3
==================================================================

frames/     tssonic-0000.png ... tssonic-0063.png, the mod's 64 frames on its 448 x 448 canvas, each with a -trim.png
            (white = house colour, antialiased):
              0-31    the hull with its shadow, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E)
              32-63   the turret (the turntable, the dish and its arm), no shadow, 32 facings, its pivot where in-mod/
                      has it (224, 221); the game seats it at the hull's back (see The turret's seat below)
previews/   8-facings.png            the assembled unit, the mod's frames beside HD, both with the turret seated at
                                     the hull's back
            hull-8-facings.png, turret-8-facings.png   each set on its own, every 4th facing
            turn.gif, turn-hull.gif, turn-turret.gif   all 32 facings in turn, the mod's frames beside HD
            scale.png                next to the HD harvester, as the game draws them
            shape-8-facings.png      the model drawn flat (a colour per part) in the mod's cameras beside the mod's
                                     frames, the hull's and the turret's every 4th facing, with the silhouette overlap
            arm-closeup.png          the turret's arm at 4x in four facings
            viewport-closeup.png     the ochre box's viewport at 4x in four facings
ts-sonic-hd-3d/   the 3D model, in its own zip (ts-sonic-hd-3d.zip) next to this folder:
            tssonic.glb  the hull and the turret (vertex colours), the turret under its own node, with the mod's camera
src/        the model, the renderer and the checks (see Rebuilding below)

v3 replaces v2 (and v1): same canvas, sizes, pivot and shadow, the horn's tip where it was (the sonic wave
starts there).


What changed from v2
--------------------
Luke: a viewport, not a full cockpit.  v2 rebuilt the ochre box on the front left as a cab (a windscreen raked down
from its roof in two panes, a rear window).  v3 keeps the box as the first look had it - its raised front part,
the hatch on top, the joint round it - and puts one viewport across its front, where TS has its dark voxels (TS:
x 41..42, y 15..19, z 8..10): dark glass in an ochre frame.  Everything else is v2's: the turret on the hull's back,
the arm, the striped zig-zag brackets.


What changed from v1 (in v2)
----------------------------
v1 copied TS's voxels box by box, so it still read as voxels.  v3 is built the way the Titan, the Wolverine, the
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
- The rear deck in house colour (TS: x 3..21, up to z 10), joints across it, a hatch with a handle and two louvred
  vents (under the turret, which sits over it); its back a louvred grille stepping down to the rear plate
  (TS's dark gaps between the fins); TS's louvred blocks on the rear pods' inner edges with their black posts.
- The long house-colour box on the front right (TS: x 26..46, y 6..14, up to z 11, its back end a step lower) on its
  black base, coming down at the front to z 5: joints across its top, louvres down its sides, a hatch on its top.
- GDI's ochre box on the front left (TS: x 34..41, y 14..20, z 4..10, its front higher, z 11): a viewport across its
  front (Luke), where TS has its dark voxels (x 41..42, z 8..10), dark glass in an ochre frame; a hatch with a
  handle on top, a joint round its middle.
- The olive plate across the front's left (TS: x 44..46) with two vent grilles.
- The turret (SONICTUR, TS's two sections, posed by SONICTUR.HVA): the turntable in TS's ochre and black (Westwood's
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
  brackets.  Under the arm's back half TS is open to the turntable (TS: x 13..15), and so is v3.
- The arm in TS's colours (Luke: stick to TS's); the zig-zag brackets striped across as the FMV's, in TS's ochre and
  black (the turntable's) (Luke: keep the stripes and zig-zags).

The model's silhouette overlaps the mod's frames by 0.93 drawn flat in the mod's cameras
(shape-8-facings.png); the finished frames by 0.926 (src/vcheck.py).


The turret's seat
-----------------
Luke: the turret sits on the back of the unit, touching its back.  So the turret's ring reaches the hull's back (the
rear grille's foot, q x 0): its pivot 14.0 voxels aft of the unit's position along the hull's facing - 0.46 cell, 11
classic px, 88 px on this canvas (in TS's terms TurretOffset=-117; TS's own -64, a quarter cell, leaves a gap of 6
voxels behind it).  The turret's frames stay centred on its pivot, as in-mod/'s and v1's (the game turns the turret on
its own, so its frames can't carry the offset): the game draws frame 32 + f that far aft of the unit along the hull's
facing, on the ground, so foreshortened as the camera draws the ground - 88 canvas px aft when the hull faces east or
west, 47 px when it faces north or south, in between elsewhere (dx = 88 sin a, dy = -47 cos a for the hull's facing a
clockwise from north; previews/ draw it so).  v1's previews drew it 6 canvas px aft, over the hull's middle.


Look
----
- Cameras: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; as v1 and the mod's frames
  have them: the hull at 6.27 canvas px per voxel with the unit's position at canvas (222.5, 222.7) (TS's hull reaches
  0.24 voxels below its HVA origin, so the model is raised onto the ground and the camera moved to match); the turret
  at 6.15 px per voxel (the mod draws it 2% smaller) with its pivot at (224, 221).  The horn's tip (the arm's tip)
  is where TS has it (within 1.5 px), so the sonic wave still starts there.
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
  louvred blocks, the front box), detail only as thin seams; the -trim masks cover exactly those.


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
  seated 0.46 cell aft (its ring's back on the hull's back) and turning about its own local z axis > turntable
  (hazard_ring), turret_body (rim, base_side,
  rail, base_post, base_step, beam, arm_cap, arm_body, arm_band, arm_strap, arm_sleeve, arm_fin, arm_tip, trunnion,
  bracket, bracket_foot, bracket_plate, piston, piston_rod, spring, dish, dish_post, brace, fitting, ...).
  The meshes are exact (each part cut from its own planes and curved surfaces).  One scale for the hull and the turret
  (TS's): the mod's turret frames are 2% smaller.
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 448 canvas exactly
  (checked by drawing the mesh through it over hull frame 24 with turret frame 56 seated as above: overlap
  0.987).
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).
- Khronos's glTF validator: errors 0, warnings 0, infos 0, hints 0.


Judgement calls (each one easy to change)
-----------------------------------------
- One paint colour per part (TS's), rather than TS's voxel-by-voxel speckle (v1).
- Westwood's art where TS's voxels have the part: the dish's white panels (TS: a light band across a grey shell), the
  hazard stripes round the turntable (TS: its ochre and black).
- The arm from the FMV close-up where TS has the parts: the caps, fins, straps and trunnion on TS's rod; the zig-zag
  brackets and the spring pistons as TS's dark supports and side members.  TS's voxels fill the space round them
  (a solid dark mass at z 1..3); v3 keeps the brackets open, as the FMV's, so the turntable shows between them.
- The brackets' stripes are the FMV's (Luke: keep them); TS's brackets are dark.
- The turret seated with its ring on the hull's back (Luke), 0.46 cell aft, rather than TS's quarter cell.
- The viewport: TS's dark voxels across the ochre box's front as one framed window on the box's front face (TS
  rakes them a voxel forward at their foot).  TS also has dark voxels at the box's back end; they are left ochre
  (Luke: one viewport, not a cockpit).
- The turret drawn 2% smaller than the hull, as in-mod/ draws it (TS draws both at one scale), so the horn's tip
  stays where the mod's sonic wave starts.
- The rear deck's hatch and vents are under the turret in the game; they show in the hull's own frames.


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are.
  sonmodel.py            the model: every part, in TS's voxel sections' own frames, posed by their HVAs
  sonmat.py              the paint and the detail (joints, bolts, louvres, stripes), per pixel from each hit's q
  soncam.py              the canvas, the two cameras and the frame layout
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
