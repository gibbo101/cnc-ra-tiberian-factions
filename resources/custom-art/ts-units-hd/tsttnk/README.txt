Tick Tank (TS [TTNK]) in HD for Tiberian Factions: TSTTNK
=========================================================

frames/     tsttnk-0000.png ... tsttnk-0063.png, 64 frames on the 384 x 384 canvas, each with a -trim.png
            (white = house colour, antialiased), the way EA's RA tanks are drawn:
              0-31   the hull without its turret, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E),
                     each with its shadow
              32-63  the turret alone, 32 facings (frame 32 + facing), no shadow (EA's turrets carry none)
            The turret turns about the unit's position, so a turret frame lies over any hull frame on the same canvas
            centre with no offset (TS's turret couldn't turn; Luke: for RA it should).
muzzle.txt  the gun's muzzle on the canvas for each turret frame, its offsets from the pivot in leptons
previews/   8-facings.png    TS's voxels drawn as they are, beside HD (hull and turret laid over each other),
                             every 4th facing
            turn.gif         the 32 facings in turn, TS's voxels beside HD
            turret-turn.gif  the hull at facing 20 with the turret turning through its 32 facings
            scale.png        next to the HD harvester and the Devil's Tongue, as the game draws them
            deploy.gif       the deploy, from the dug-in package (ts-nod-tick-tank-dug-in-hd): it faces south, the
                             turret runs back up the ramps, the nose burrows, the tank stands upright; TS beside it
ts-ttnk-hd-3d/   the 3D model, in its own zip (ts-ttnk-hd-3d.zip) next to this folder:
            tsttnk.glb   the model in TS's own colours, with the mod's camera
src/        the model builder, the renderer and the checks (see Rebuilding below)


What it is
----------
One 3D model of the Tick Tank as Westwood drew it in its two renders (the official art Luke sent: TS's
in-game voxel did a poor job of it), clean parts at the in-game voxel's size and place (TTNK.VXL, posed by its HVA), drawn the way
the HD buildings and units are.
- Hull (src/ttnk35hd.py lists the parts): a wedge, low at the front and high at the back (Luke): two long, narrow
  armour hulls over the tracks, their house-colour tops sloping down from the back to the noses, side skirts in a
  darker house colour (the render's dark maroon: its Nod red in shade) with three thin trim lines in the full house
  colour; a black lamp dome with a white lens on each nose, a small dark box at each back corner; khaki tracks
  whose fronts show under the noses with an olive sprocket; between the hulls the wide dark grey centre body: in
  front a flat level deck for the turret (its ring's dark well shows on the hull frames), sloping down to the white
  knurled grinding drum across the whole front; behind it Westwood's two long ramps side by side with a dark groove
  between them, flat-topped with softened edges, rising from the deck to the back and rolling over
  onto a tall flat back face, standing above the side hulls at the back (v3.5: only the middle raised): the track the turret runs up as it digs in; two flat steel claws, one from each end of the
  drum, low at the front and curving in toward each other like mandibles; the twin white pipes on the left hull
  two-thirds of the way back, by its inner edge, with dark bands, grey caps and a clamp.
- Turret (it turns: frames of its own): a high rounded dome in house colour (Luke: TS's is a smaller circle, a higher
  dome), with a dark rim round its foot, on a dark ring and plate; a dark slit up and down the dome's front so the gun
  can elevate, the long grey gun on a trunnion across it, with a dark muzzle, centred; the round dark hatch on top
  toward the back, with two small lights behind it.
- Colours: house colour pure green 0,214,0 x (1 + 1.1 grain), with lighter weathered blotches, where the render is
  Nod red (the hull tops and noses, the trim lines, the pipes' back rings) and on the turret's dome; the skirts at
  half its brightness (the render's dark maroon); the -trim masks cover exactly that; a plain dark grey centre body
  (Luke: simple colours, not the render's camouflage), the white drum, steel claws, khaki tracks.
- Light: the buildings' light, with a soft sheen on paint and metal and ambient occlusion cast from the model
  itself.
TS's voxels (the previews' left column) are a different design; the hull and turret together cover them with a
silhouette overlap of 0.80 (src/ndeliver.py check), the size and place kept.

Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.25 canvas px per voxel, the
  unit's position (TS's HVA origin) at canvas (192, 191) on the ground: the scale and place the hand-off gives (the
  GDI voxel units').  TS's voxels sit 0.09 voxels above the HVA origin (the lowest voxels), so the model is lowered onto the
  ground (by 0.5 px): it stands on the ground and the shadow meets it.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides
  facing the camera as on the other units.  The game draws this canvas at two thirds (8 canvas px per classic
  pixel), so the outline, the shadow's blur and the contact shadow are 1.5 times as wide on the canvas.
- Colours brightened by 1.25 from TS's palette so its ochre comes out as the HD buildings' ochre; whites held at white
  paint; grime rising from the ground on the lower hull.


Shadow
------
Every frame has the unit's shadow, black at alpha 191 (75%), blurred, falling to the right and a little towards the
camera, as long as the buildings', the harvester's and the Devil's Tongue's.  Within 14 px of the canvas edge it fades
out.

The design
----------
v3, after comparing v2 with Westwood's render side by side (Luke): v2 had fat hulls and a narrow centre, a boxy
turret on two rails (not in the render), plain hulls, a small ringed drum with thin spikes and the twin pipes on the
wrong hull.  v3 follows the render: long narrow hulls with darker skirts and bright trim lines, the wide
centre with its two humps, the open gun mount with the two C-shaped brackets, the full-width knurled drum, khaki
track fronts, lamp domes, the pipes on the left hull.  v3.1 (Luke's notes on v3): the drum's spikes made the render's
flat curved claws; a visible track for the turret's run to the back (a rail along each hump's crest and a guide slot
between them); the centre body plain dark grey; the tank low at the front and high at the back, the turret's deck
kept level so it turns true.  v3.2 (Luke, built in the buildings chat for the dug-in tank): the turret 1.75 times
bigger, its seat kept.  v3.3 (Luke's review, 7 Oct, against Westwood's two renders): the turret a low rounded dome
in house colour at v3.2's size, the long gun centred; the claws flat mandibles curving in toward each other, at
the render's size; the humps and rails replaced by the render's two ramps, which are the turret's track.  v3.4
(Luke, 7 Oct, designing the dug-in tank with it): a smaller, higher dome with a slit for the gun to elevate; a
taller back (TS's), so the buried tank has a bigger flat top for the turret.  v3.5 (Luke): v3.3's side hulls kept,
only the middle (the ramps) raised at the back.  TS's size, place and footprint are kept,
so the unit takes the same room in the game; the render's tank is lower than TS's voxel, and so is this one.

The turret
----------
TS's turret couldn't turn (TS drew the gun as part of the hull).  Here it turns, as EA's RA tanks' do: frames 32-63
are the turret alone in 32 facings, with no shadow, its pivot on the unit's position.  The game lays the turret
frame for the turret's facing over the hull frame for the hull's facing, both on the canvas centre: no offset.  The
pivot sits about 2 voxels behind where the render's gun mount stands, so that it needs none (an offset would have to
change with the hull's facing).  The hull frames show the dark well of the turret ring on the deck.
previews/turret-turn.gif shows the turret turning on a hull standing still; laid over each other the two frames
match the hull and turret drawn as one model to within the outline (checked on 8 pairs of facings).

Digging in
----------
Luke: when it deploys, the front burrows into the ground and the turret moves to the back of the tank, forming an
entrenched gun emplacement.  The track for it is part of the hull: Westwood's two ramps
behind the deck, rising from it toward the back, the groove between them.
The deploy was designed with this tank in one flow (Luke, 7 Oct): the game turns the tank to face south, the turret
runs back up the ramps and over the raised back of the middle onto a post, the nose burrows and the tank stands up at
81 degrees, the ramps' tall back face the emplacement's top.  The frames are the dug-in package's
(ts-nod-tick-tank-dug-in-hd, built from this same model: its build-up 00 is frames 16 + 48 here at two thirds);
previews/deploy.gif shows it.

Fire point
----------
muzzle.txt lists, for each turret frame, the tip of the gun on the canvas, and the muzzle's place in the turret's own
frame in voxels and leptons (forward of the pivot, to its right, above the ground).  TS's PrimaryFireFLH=0,0,100 is
the centre of a turret that couldn't turn; the gun now points with the turret.


3D model (ts-ttnk-hd-3d/)
-------------------------
- Nodes: TickTank > unit_facing_east > a node per part of the hull (hulls, skirts, trim, tracks,
  sprockets, lamps, centre body, ramps, groove, drum, claws, pipes) and turret (its pivot on the unit's
  position at the ring's seat: ring, plate, dome, rim, slit, trunnion, gun, hatch, lights, and the empty marker node muzzle,
  the gun's tip); turn turret about y to aim it.
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.  The unit faces east (the mod's facing 24).
- The meshes are exact (each part's convex solid: planes, cylinders and ellipsoids), in each part's colour.
- Camera "camera_mod": orthographic, the mod's camera, framing the canvas exactly (checked by drawing the mesh
  through it over frames 24 + 56 (hull, turret): overlap 0.981).
- The file passes Khronos's glTF validator with no errors or warnings (its note is the empty marker node).
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- Redesigned from Westwood's render (Luke: the in-game voxel did a poor job); v3 follows it closely, v3.1-v3.5 take
  Luke's notes on it.  TS's size, place and footprint kept; low at the front and high at the back, as the render's.
- A turret that turns (Luke), drawn as EA's RA tanks' turrets: separate frames, no shadow, its pivot on the unit's
  position so no offset is needed; about 2 voxels behind the render's gun mount for that.
- The render's Nod red as house colour on the hull tops and noses and the trim lines, the turret's dome too (Luke), and
  its dark maroon skirts as house colour at half brightness (Luke: the maroon is the house colour): in the game they
  take the player's colour in its darker shades, Nod red included.
- The centre body plain dark grey (Luke: simple colours), not the render's camouflage.
- The turret's track as Westwood's two ramps (the turret runs up them as it digs in); no rails.
- The turret a rounded dome (Luke: like the Nod light tank; v3.4 smaller and higher, as TS's), a slit for the
  gun to elevate, its long gun centred (the render's sits
  beside a bracket; centred reads better on a dome).
- The claws as flat steel blades from the drum's ends, curving in toward each other (the renders' mandibles).
- The turret's deck kept level (the hull slopes, the deck doesn't) so the turret turns true.


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folder is (TS_HANDOFF: the
folder holding 03-TTNK/ and examples/).
  rc.py, rcrender.py     the ray caster and the buildings' look for models made of convex parts
  tsvox.py               TS's voxels drawn as they are (the previews' left column)
  vexport.py, rcexport.py   the .glb;  glbcheck.py  draws the .glb through its camera to check it
  ndeliver.py            renders, previews and checks a unit from its spec;  npackage.py  this package
  (vxlunit.py, tsnormals.py and voxrender.py, the voxel builder the GDI units used, come with the shared files; this
  unit's HD model doesn't use them)
  hdv.py                 the HD parts (boxes, hulls, cylinders, ellipsoids), their materials, the renderer and the .glb
  ttnk35hd.py            the Tick Tank's parts (the render's design): hull, turret and the dig-in;  ttnk35spec.py
                         its place, the hull and turret frames, previews, muzzle.txt, README;  ttnk35deploy.py
                         (the old concept preview, no longer packaged)
  (nvox.py loads the voxel and places it; tsvox.py draws TS's voxels for the previews)
    python3 nvox.py ttnk33spec frames 0,24,56 4 out        draws frames
    PKG=out python3 ndeliver.py ttnk33spec render 0 1      renders frames/
