"""ndeliver spec: the Tick Tank (TSTTNK) v3.5, new to the mod: Westwood's own render of it followed closely
(ttnk33hd.py; Luke: the in-game voxel did a poor job; v2 strayed from the render), at TTNK.VXL's size and place on
the ground, with a turret that turns (Luke: TS's couldn't; for RA it should, or the tank is hamstrung).  The way
EA's RA tanks are drawn: frames 0-31 the hull (its shadow baked in), frames 32-63 the turret alone (no shadow), the
turret's pivot on the unit's position, so the game lays a turret frame over a hull frame on the same canvas centre
with no offset. TS's voxels drawn as they are for the previews' left column."""
import os
import numpy as np
from PIL import Image
import nvox as N
import hdv
import ttnk35hd as ttnk3hd

CFG = N.Cfg('03-TTNK', [('TTNK.VXL', None, None)], 'tsttnk')
NAME, FRAMES, CANVAS = CFG.name, 64, CFG.canvas
FOLDER = CFG.folder
NO_SHADOW = [(32, 63)]
CROP = (24, 40, 384, 300)
SHEETS = [('8-facings.png', [('facing %d' % f, [f, 32 + f]) for f in range(0, 32, 4)])]
GIFS = [('turn.gif', [('facing %d' % f, [f, 32 + f]) for f in range(32)], 120),
        ('turret-turn.gif', [('hull facing 20, turret facing %d' % t, [20, 32 + t]) for t in range(32)], 120)]
LINEUP = ('scale.png', [('Tick Tank (HD)', [24, 56])])
SRC = ['ttnk35spec.py', 'ttnk35hd.py', 'ttnk35deploy.py']
SHARED_EXTRA = ['hdv.py']
FLH = (0, 0, 100)
LEPTONS_PER_VOXEL = 256.0 / (192.0 / CFG.ppu)          # 192 canvas px a cell
_VU = None


def vunit():
    global _VU
    if _VU is None:
        _VU = N.load(CFG)
    return _VU


def load():
    u = vunit()
    return ttnk3hd.build_hull(CFG, u), ttnk3hd.build_turret(CFG, u)


def frame(M, k, ss=4, sky=True):
    hull, turret = M
    if k < 32:
        return hdv.frame(hull, CFG, k, ss, sky)
    return hdv.frame(turret, CFG, k - 32, ss, sky, shadow=False)


def ref_frame(M, k):
    if k < 32:
        return N.ref(CFG, vunit(), k)
    return Image.new('RGBA', CANVAS, (0, 0, 0, 0))       # TS has no turret of its own: it is part of TTNK.VXL


def gun():
    return ttnk3hd.muzzle(CFG, vunit())


def muzzle_text():
    g = gun()
    piv = ttnk3hd.turret_pivot(CFG, vunit())
    L = LEPTONS_PER_VOXEL
    lines = ["Tick Tank (TSTTNK): the gun's muzzle on the 384 x 384 canvas for each turret frame (canvas px).  The turret",
             "turns about the unit's position (the canvas centre's ground point, as the hull's), so the table holds for every",
             "hull facing: the muzzle depends only on the turret's facing.",
             "In the turret's own frame the muzzle is %.1f voxels forward of the pivot, %.1f to its right, %.1f above the ground" % (
                 g[0], -g[1], g[2]),
             "(%.0f, %.0f and %.0f leptons at 192 canvas px a cell); the turret ring's seat is %.1f voxels (%.0f leptons) up." % (
                 g[0] * L, -g[1] * L, g[2] * L, piv[2], piv[2] * L),
             "TS's PrimaryFireFLH=0,0,100 (TS fired from the unit's centre, 12 voxels up: TS's gun couldn't turn).",
             "",
             "frame  turret facing         x        y"]
    for t in range(32):
        x, y = N.project(CFG, g, t)
        nm = N.FACING_NAMES[t // 4] if t % 4 == 0 else ''
        lines.append('%5d  %6d %-6s    %8.1f %8.1f' % (32 + t, t, nm, x, y))
    return '\n'.join(lines) + '\n'


def GLB(path):
    u = vunit()
    piv = ttnk3hd.turret_pivot(CFG, u)
    hdv.export(ttnk3hd.build(CFG, u), CFG, path, 'TickTank', markers=[('muzzle', gun(), 'turret')],
               groups={'turret': (piv, ('turret_',))})


GLB_NAME = 'tsttnk.glb'
GLB_FRAMES = [24]
GLB_REF_LAYERS = [24, 56]

WHAT_HD = """One 3D model of the Tick Tank as Westwood drew it in its two renders (the official art Luke sent: TS's
in-game voxel did a poor job of it), clean parts at the in-game voxel's size and place ({vxl}), drawn the way
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
silhouette overlap of {iou} (src/ndeliver.py check), the size and place kept."""


def __getattr__(name):
    if name != 'README':
        raise AttributeError(name)
    vunit()
    n = CFG.name
    return N.readme(
        CFG, 'Tick Tank', 'TTNK', 'TTNK.VXL, posed by its HVA', what=WHAT_HD,
        frames="""frames/     %s-0000.png ... %s-0063.png, 64 frames on the 384 x 384 canvas, each with a -trim.png
            (white = house colour, antialiased), the way EA's RA tanks are drawn:
              0-31   the hull without its turret, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E),
                     each with its shadow
              32-63  the turret alone, 32 facings (frame 32 + facing), no shadow (EA's turrets carry none)
            The turret turns about the unit's position, so a turret frame lies over any hull frame on the same canvas
            centre with no offset (TS's turret couldn't turn; Luke: for RA it should).""" % (n, n),
        previews="""previews/   8-facings.png    TS's voxels drawn as they are, beside HD (hull and turret laid over each other),
                             every 4th facing
            turn.gif         the 32 facings in turn, TS's voxels beside HD
            turret-turn.gif  the hull at facing 20 with the turret turning through its 32 facings
            scale.png        next to the HD harvester and the Devil's Tongue, as the game draws them
            dig-in-concept.gif   the deploy idea (Luke's): the turret runs back up the ramps, the
                                 nose burrows""",
        muzzle_line="muzzle.txt  the gun's muzzle on the canvas for each turret frame, its offsets from the pivot in leptons\n",
        extra="""
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
previews/dig-in-concept.gif shows the idea from the same model: the turret runs back up the ramps while the tank
pitches nose-down about its back end and its nose sinks into a mound of dirt (the dug-in package in the buildings
work goes further: nose-first, almost vertical).  The dug-in frames belong to the buildings hand-off (17-GATICK); the .glb's
turret node is ready for them.

Fire point
----------
muzzle.txt lists, for each turret frame, the tip of the gun on the canvas, and the muzzle's place in the turret's own
frame in voxels and leptons (forward of the pivot, to its right, above the ground).  TS's PrimaryFireFLH=0,0,100 is
the centre of a turret that couldn't turn; the gun now points with the turret.
""",
        glb_nodes="""Nodes: TickTank > unit_facing_east > a node per part of the hull (hulls, skirts, trim, tracks,
  sprockets, lamps, centre body, ramps, groove, drum, claws, pipes) and turret (its pivot on the unit's
  position at the ring's seat: ring, plate, dome, rim, slit, trunnion, gun, hatch, lights, and the empty marker node muzzle,
  the gun's tip); turn turret about y to aim it.""",
        glb_nodes_long="""Nodes: TickTank > unit_facing_east > a node per part of the hull, as in frames 0-31, and turret: a node at the
turret's pivot (the unit's position, at the ring's seat) holding its ring, plate, dome, rim, slit, trunnion, gun, hatch and
lights, as in frames 32-63, and the empty marker node muzzle (the gun's tip, in muzzle.txt).  Turn turret about y to
aim it; run it back along x, up the ramps, to dig in.""",
        glb_what="the HD model (hull and turret as in the frames, the turret its own node), with the mod's camera.",
        glb_mesh="The meshes are exact (each part's convex solid: planes, cylinders and ellipsoids), in each part's colour.",
        glb_mesh3d="The meshes are exact (each part's convex solid), one node per part, curved ones smooth-shaded.",
        glb_ref="frames 24 + 56 (hull, turret)",
        judgement="""- Redesigned from Westwood's render (Luke: the in-game voxel did a poor job); v3 follows it closely, v3.1-v3.5 take
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
""",
        src="""  hdv.py                 the HD parts (boxes, hulls, cylinders, ellipsoids), their materials, the renderer and the .glb
  ttnk35hd.py            the Tick Tank's parts (the render's design): hull, turret and the dig-in;  ttnk35spec.py
                         its place, the hull and turret frames, previews, muzzle.txt, README;  ttnk35deploy.py
                         previews/dig-in-concept.gif
  (nvox.py loads the voxel and places it; tsvox.py draws TS's voxels for the previews)
    python3 nvox.py ttnk33spec frames 0,24,56 4 out        draws frames
    PKG=out python3 ndeliver.py ttnk33spec render 0 1      renders frames/""")
