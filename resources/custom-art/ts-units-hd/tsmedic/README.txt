Medic (TS [MEDIC]) in HD for Tiberian Factions: TSMEDIC
=======================================================

frames/     tsmedic-0000.png ... tsmedic-0306.png, the mod's 307 frames on its 267 x 208 canvas, each with a -trim.png
            (white = house colour, antialiased), numbered as TS's own sequence (the mod keeps it):
              0-7      standing, one a facing; facings counter-clockwise from north (0 N, 1 NW, 2 W, 3 SW, 4 S, 5 SE,
                       6 E, 7 NE)
              8-55     the run: 6 steps a facing (frame = 8 + facing x 6 + step), 2 ticks a step, looping
              56-70    idle 1 (TS draws it facing south-west);  71-84  idle 2 (facing south-east);  85 (unused by
                       the game): TS's own frame 85, him taking his case up again
              86-133   the crawl: 6 steps a facing, looping; its first step is the prone pose
              134-148  death 1;  149-163  death 2; both end lying flat
              164-259  fire and fire prone: empty.  He is unarmed: TS's frames there are empty and his fire is the heal
              260-275  lying down, 2 frames a facing;  276-291  getting up: the same two backwards (TS's are)
              292-306  the heal: one strip whatever the facing (TS draws it facing south-east), 2 ticks a frame
previews/   run-8-facings.gif, crawl-8-facings.gif      every facing at once, TS's sprite (as the mod scales it) above
                                  HD
            run-west.gif, run-south.gif, crawl-west.gif, crawl-south.gif
                                  TS's sprite | the mod's frame | HD, at the game's speed
            heal.gif, idle-1.gif, idle-2.gif, death-1.gif, death-2.gif      the same for the one-facing sequences
            lie-down-get-up-W.gif, lie-down-get-up-SE.gif         standing -> down -> prone -> up -> standing
            standing-8-facings.png    TS's sprite, the mod's frame, HD and EA's HD Field Medic, each facing
            masks.png                 the head close up in 8 facings: TS, the mod, HD
            animation-sheet.png, death-1-sheet.png, death-2-sheet.png, crawl-sheet.png
                                  the frame-by-frame check sheets: each frame as the mod draws it now (TS's
                                  sprite and shadow) beside HD
            shape-run.png, shape-crawl.png    TS's frames as colour classes beside the model's, in TS's own camera
ts-medic-hd-3d/   the 3D model in its own zip (ts-medic-hd-3d.zip) next to this folder
src/        the model, its fits, the renderer and the checks (see Rebuilding below)


What it is
----------
The posable soldier of the Light Infantry (inf.py, shared by the six infantry units) with the Medic's own sizes,
gear and colours (infunit.py), fitted to TS's own MEDIC frames in TS's camera (silhouette and colour classes, the red
crosses and blood left out) and drawn the way the HD buildings and the other units are.
- His gear, read from TS's frames: a grey helmet with a red cross on its crown and a dark glass faceplate; grey
  armour, darker at the front; house green shoulder pads and thigh fronts (TS's remap areas); orange armbands and knee
  pads; his hips and the backs of his thighs orange (TS's back views: orange across the hips and down both thighs;
  its front view: green thighs, orange knees); a grey medical case in his right hand (TS's south and east views: a
  grey box at his side) with a red cross on each broad face; a red cross on his upper back (TS's back view: 3 x 3 px
  between the shoulder blades).  The crosses are TS's pure red, painted flat (lit only a little, as TS draws them
  bright).
- The helmet's cross: TS draws its red blurred into the helmet's grey (flesh-coloured pixels, as round his other
  crosses' edges) on the crown in every facing, standing, running and crawling; it goes edge-on and out of sight when
  he lies on his back and shows more as he bends over to heal, so it lies flat on the crown.
- The faceplate: TS draws it dark grey looking ahead and blue-grey lying face up, so it is dark glass that shows the
  sky as it turns up.
- The orange is drawn on TS's own orange ramp, as E2's.
- Standing: one pose fitted to the 8 standing frames together, then each facing's arms and head to its own frame.
  Overlap with TS's frames in TS's camera: 0.84.
- The run is one smooth loop (every joint on a short smooth curve through the 6 steps, nothing jumps back to a start
  pose), fitted to TS's 48 run frames together, each facing's arms and head on their own smooth loop on top.  Overlap
  0.71; the furthest any landmark moves from one step to the next is 6.8 TS px.
- The crawl is rebuilt from TS's own crawl frames (your notes: "view how og is doing it", "research how a body crawls
  prone"). It is a real prone crawl, done the way the army's low crawl and the leopard crawl are: flat and low on his
  front, up on his forearms with his head up to see. One forearm goes forward with the opposite knee, which is drawn
  up while the other leg lies straight back, and his body rolls a little towards that knee; then the other pair. TS
  drew this crawl only facing N, NW, W, SW and S, and its NE, E and SE crawl frames are those sprites flipped, pixel
  for pixel. One pose can't match both sides, which is what made the earlier crawls flail, so the crawl is fitted to
  the five facings TS drew and the flipped facings get the same pose mirrored, as TS's do. The case stays in his
  right hand, standing on the ground square to him, and only moves when his hand does (lying down and getting up
  carry it from his hand to the ground and back). One stroke drives every joint, so the loop runs on with nothing
  jumping back. How far he is propped up, where he looks and how far each part moves are fitted to TS's crawl frames.
  Overlap 0.67, landmarks at most 4.0 TS px a step.
- The heal: each frame fitted to its TS frame starting from the one before, then the whole run of poses relaxed
  together, starting and ending on his standing pose facing south-east, as TS's does (0.81).
- His case: in his hand standing, running and in idle 1 (TS: he turns it to look at it); upright on the ground ahead
  of his hand as he crawls, pushed along; set down beside him for idle 2 and the heal and taken up again at the end
  (TS: frames 72-84 and 294-304 it stands still on the ground, its cross to the camera); dropped in the deaths, where
  it then stays (death 1 from frame 137, death 2 from 156).  Where it stands is read off TS's frames: the model's case
  and its cross put where TS's cross is in every one of those frames (casespot.py).
- Lying down, getting up, the idles and deaths: as the other infantry (0.72; idles 0.86 and
  0.83, deaths 0.65 and 0.68).
- The blood in TS's red (255,0,0), each red pixel drawn on the ground it covers in TS's view.  TS's crosses are the
  same red: red where the fitted soldier shows a cross, his case or his back is the cross (drawn by the model), the
  rest is blood.
Against the mod's current frames the silhouettes overlap by 0.54 (standing 0.58, run 0.53, crawl 0.56): those frames
are TS's sprites scaled up 3.085 times, so this is the difference in TS's own camera above, scaled up with them, plus
the 32-degree camera.


Keep (from the hand-off README)
-------------------------------
- The 267 x 208 canvas; every frame of the layout in TS's order (85, unused, and the empty fire frames included).
- The feet: the soldier's ground point lands where the mod's frames put TS's (TS's sprite x 3.085 at (37.53, 11.06));
  standing, the boots' lowest pixel is on canvas row 108-115 by facing, as the mod's own frames have it
  on 108-115 (the README: feet on 111).
- The heal strip at 292-306.
- He stands as tall as the mod's frames (EA's Field Medic: see standing-8-facings.png).
- The shadow baked in at alpha 128 (50% black, blurred): the README's minimum, lighter than the buildings' 75%, as
  the mod's frames carry TS's at about 25% (your note: at 75% the falling deaths looked like floating).


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 3.085 canvas px per TS pixel
  (the mod's frames are TS's sprite x 3.085), the soldier drawn 8% bigger about his feet, as E1.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the units' camera fill; each part
  as light as TS draws it under that light (infcalib.py).
- House colour: exactly 0,214,0 x (1 + 1.1 grain) on the shoulder pads and thighs; the -trim masks cover exactly those.


3D model (ts-medic-hd-3d/)
--------------------------
tsmedic.glb   the soldier in vertex colours, every sequence as a glTF animation (the heal too), the mod's camera
- Nodes: Medic > pelvis, belt, abdomen, chest, vest, back_cross_v, back_cross_h, pouch, medkit,
  case_cross_r_v, case_cross_r_h, case_cross_l_v, case_cross_l_h, helmet, mask (his face), jaw,
  and left_/right_ thigh, shin, knee, boot, shoulder_pad, upper_arm, forearm, hand.
  Each part is one rigid solid, posed per frame by its node's translation and rotation; the case and its crosses are
  posed with his right hand.
- Animations, facing east (the 8-facing sequences use the east facing's frames; the idles, deaths and the heal play
  facing east too), at the game's speed (15 ticks a second); the looping ones end on their first frame again (no fire
  animations: he has none):
    "stand"      frame 6
    "walk"       frames 44-49, 2 ticks a frame, loops
    "idle1"      frames 56-70, 2 ticks a frame
    "idle2"      frames 71-85, 2 ticks a frame
    "crawl"      frames 122-127, 2 ticks a frame, loops
    "death1"     frames 134-148, 2 ticks a frame
    "death2"     frames 149-163, 2 ticks a frame
    "lie_down"   frames 272-273, 2 ticks a frame
    "get_up"     frames 288-289, 3 ticks a frame
    "heal"       frames 292-306, 2 ticks a frame
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (30.3 TS px, as the other TS units' models).
  Origin: the soldier's position on the ground.  He faces east (the mod's facing 6).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 267 x 208 canvas
  exactly (checked by drawing the mesh through it over frame 6: overlap 0.907).
- The file passes Khronos's glTF validator: errors 0 warnings 0 infos 0 hints 0.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- His crawl pushes along the ground with his legs, a knee drawn up to the side in turn and the leg driving back
  (your note on the Disc Thrower's crawl: "isnt kicking their legs against the floor").  The first crawls' legs were
  bent up in the air: the fit could only turn the thigh out a little at the hip, so every bend of the knee lifted the
  foot off the ground.  With the thigh turned out, the knee bends along the ground; the stroke is fitted to TS's crawl
  frames, lying on the ground.
- The deaths, crawl and prone frames are fitted to TS's shadow as well as its outline (your notes: "leg in the air
  way above the shadow", "ours are hovering above the ground").  From TS's camera a leg raised in the air and a leg
  lying further back look the same, and the first fits took the floating one.  TS's own shadow, which the mod's
  frames carry, tells them apart: its light (from the north-north-west, 50 degrees up) is read off all six units' standing
  frames, and each frame's shadow is fitted to TS's.  Wherever TS shows him down, his hips, chest, knees and feet lie
  on the ground (propped on his forearms when prone), and each death is fitted from its last frame, lying flat,
  back to its first, so he falls the way TS's does.
- A dying soldier's shadow follows TS's, frame by frame (your note: "on the og's the shadow disappears as the unit
  falls"): TS's shrinks as he goes down and is all but gone once he lies on the ground.  Each death frame's shadow is
  drawn in under him (its light raised, so it shortens) and then faded, to show as much of it as TS shows round its
  frame (deathshadow.py; the lengths and strengths are in src/medic_shadow_w.json).  Once he is down only a faint
  shadow hugs him, which the game drops (under alpha 128), as TS has none.
- TS drew his crawl only facing N, NW, W, SW and S; its NE, E and SE crawl frames are those sprites flipped, pixel
  for pixel.  The HD crawl there is the same pose mirrored (his left and right swapped, so the case is in his
  left hand there), as TS's is.
- His fire and fire-prone frames (164-259) are empty: he is unarmed, TS's frames there are empty and his fire is the
  heal (292-306, the hand-off README).
- TS's orange across the backs of his hips and down the backs of his thighs is read as his hips' and thighs' own
  colour behind (green plates on the thighs' fronts), not a pouch; the orange on his upper arms as armbands (EA's
  Field Medic wears white ones).
- The red cross on his helmet's crown is read from TS's blurred red there (see What it is); at TS's size it is a pixel
  or two of flesh colour, so its size is read off that (its arms a half of the helmet's width).
- His armour's greys are matched to all of TS's grey and dark pixels on each part (TS shades the front of his armour
  dark: matched to the light greys alone, he came out nearly white).
- The red crosses are drawn on the model where TS has them (his upper back, the case's faces) in TS's pure red, lit
  only a little.
- TS draws idle 1 facing south-west and idle 2 facing south-east, the heal facing south-east (their first frames match
  those standing frames); the hand-off README says west and east for the idles.  They're drawn as TS's frames are.
- Frame 85 (unused) is a copy of 84.


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy, Pillow and cma.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are (TS_HANDOFF: the
folder holding 22-TSMEDIC/ and renderer/).
  inf.py                 the posable soldier (shape S, pose Q) as convex solids (the Medic's case, crosses and pouch:
                         kit 'medic');  rc.py  the ray caster
  infunit.py             each unit's own data (the Medic: his kit, colour classes, sizes, colours, the ramps)
  inffit.py              the fit's loss in TS's camera, and the shape + standing fit (medic_shape.json); infrefine.py
                         each facing's own arms and head (medic_stand_frames.json); infcalib.py  the colours
  infcycle.py            the run as a smooth loop (medic_walk_cyc.json, medic_walk_faces.json, medic_walk_frames.json)
  crawlbio.py            the crawl, a real prone crawl fitted to TS's crawl frames (medic_crawlfit.json,
                         medic_crawl_frames.json); crawlfit.py  which facings TS drew, and the mirror
  infliedown.py          lying down and getting up;  infsmooth.py  the idles, deaths and the heal
  infrender.py           an HD frame;  infall.py  all 307 frames with the blood (and the empty fire frames)
  infexport.py           the .glb;  infpreview.py  the previews;  infreport.py  the numbers above
  infcheck.py, infmasks.py, infgif.py, hdgrid.py, cyclesheet.py, infshow.py, motion.py   the checks used along the way
  infpackage.py          this package (frames, previews, model, src)
  tsshadow.py            TS's own shadow, read off the mod's frames, and its light (ts_light.json: fitted on
                         all six units' standing frames); the fits count it with SHADOW=w
  ground.py              how far a soldier TS shows on the ground floats off it (deaths, crawl, prone)
  deathfit2.py           a death fitted to TS's frames and shadow, from its last frame back to its first
  deathshadow.py         a death's shadow drawn in and faded as TS's own frames have it (UNIT_shadow_w.json)
  firepair.py, gunpass.py, gunline.py   fire as TS's alternating poses; a gun laid along TS's gun
  fitcheck.py, checksheet.py   the check sheets: a fit and its shadow in TS's camera; TS beside HD
e.g.  python3 infall.py medic medic_shape.json out/          (every frame; or a list: out/ 8,9,10)
