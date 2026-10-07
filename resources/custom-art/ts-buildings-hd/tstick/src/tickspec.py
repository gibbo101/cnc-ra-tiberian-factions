"""Package spec for the dug-in Tick Tank (nodeliver.py, run through tickdeliver.py), its README and muzzle.txt."""
import os, sys, glob
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(HERE, 'src'), HERE):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import tickm as K, tickrender as TR, tickfinal as TF
import voxrender as VR

HAND = '/home/claude/work/ts/ts-nod-buildings-hd-handoff/17-GATICK'
UNITS = '/home/claude/work/out/ts-ttnk-hd'       # the units package, v3.2 (turret x1.75)
PKG = TF.PKG
NAME = TF.NAME
LEP = 256.0 / (128.0 / K.VOX_PX_BLD)          # leptons per voxel (8.33)


def extents(vn, subs=('building', 'turret', 'build-up')):
    x0 = y0 = 10 ** 6; x1 = y1 = -1
    for sub in subs:
        for f in glob.glob(f"{PKG}/{TF.VIEWS[vn]}/{sub}/*.png"):
            if f.endswith('-trim.png'):
                continue
            a = np.array(Image.open(f))[..., 3]
            ys, xs = np.nonzero(a > 0)
            if xs.size:
                x0, x1, y0, y1 = min(x0, xs.min()), max(x1, xs.max()), min(y0, ys.min()), max(y1, ys.max())
    return int(x0), int(y0), int(x1), int(y1)


def project(v, p_unit):
    c = TR.cfg(v)
    Mx = VR.facing_cw(VR.mod_to_cw(K.FACING))
    x, y = TR.N.camera(c).project(Mx @ np.asarray(p_unit, float))
    return float(x), float(y)


def pivot():
    c = TR.cfg('ra')
    M = K.model(c, t=1.0, turret=None, base=False)
    return M.seat


def muzzle_text():
    c = TR.cfg('ra')
    pv = pivot()
    Mx = VR.facing_cw(VR.mod_to_cw(K.FACING))
    W, H = TR.CANVAS['ra']; Wi, Hi = TR.CANVAS['iso']
    pr = project('ra', pv); pi = project('iso', pv)
    g0 = K.muzzle(c, 1.0, 0.0, sp=pv)
    loc = g0 - pv
    pw = Mx @ pv
    lines = [f"Tick Tank, dug in: the gun's muzzle (the barrel's tip) for each turret frame, on the {W} x {H} RA-grid canvas and",
             f"the {Wi} x {Hi} TS-angle canvas (canvas px), and as an offset from the cell's centre in leptons (256 a cell):",
             "east, south, and height above the ground.  The turret turns about its pivot on its post on top of the",
             f"standing tank: {abs(pw[0]) * LEP:.0f} leptons {'east' if pw[0] >= 0 else 'west'} of the cell's centre, "
             f"{abs(pw[1]) * LEP:.0f} {'south' if pw[1] >= 0 else 'north'}, {pw[2] * LEP:.0f} up "
             f"(RA grid ({pr[0]:.1f}, {pr[1]:.1f}), TS angle ({pi[0]:.1f}, {pi[1]:.1f})).",
             f"In the turret's own frame the muzzle is {np.hypot(loc[0], loc[1]) * LEP:.0f} leptons from the pivot "
             f"({loc[0] * LEP:.0f} forward, {-loc[1] * LEP:.0f} to its right) and {loc[2] * LEP:.0f} above it.",
             "TS's PrimaryFireFLH=48,0,64 was for TS's own turret (TTNKTUR); Luke's turret replaces it.",
             "",
             "frame  facing      RA grid x      y   TS angle x      y      east   south  height (leptons)"]
    for f in range(32):
        g = K.muzzle(c, 1.0, K.turret_angle(f), sp=pv)
        x, y = project('ra', g); xi, yi = project('iso', g)
        w = Mx @ g
        nm = ('N', 'NW', 'W', 'SW', 'S', 'SE', 'E', 'NE')[f // 4] if f % 4 == 0 else ''
        lines.append(f'{f:5d}  {f:4d} {nm:<3s}  {x:9.1f} {y:6.1f}  {xi:10.1f} {yi:6.1f}  {w[0] * LEP:7.0f} {w[1] * LEP:7.0f} '
                     f'{w[2] * LEP:7.0f}')
    return '\n'.join(lines) + '\n'


def write_muzzle():
    open(f'{PKG}/muzzle.txt', 'w').write(muzzle_text())


def fly_frames():
    """the build-up frames with soil in the air, as 'aa-bb'."""
    c = TR.cfg('ra')
    fr = []
    for i in range(K.BUILD_N):
        t = i / (K.BUILD_N - 1.0)
        if 0 < t < 1:
            V, pose, items, G, sp = K.state(c, t)
            if K.flying_clods(V, G, t):
                fr.append(i)
    return f'{fr[0]:02d}-{fr[-1]:02d}' if fr else 'none'


def readme():
    W, H = TR.CANVAS['ra']
    px0, py0, px1, py1 = TR.PLOT['ra']
    ex0, ey0, ex1, ey1 = extents('ra')
    iw, ih = TR.CANVAS['iso']
    ox, oy = TR.origin('ra')
    pv = pivot()
    Mx = VR.facing_cw(VR.mod_to_cw(K.FACING))
    pw = Mx @ pv
    bx0, by0, bx1, by1 = extents('ra', ('building', 'turret'))
    fx0, fy0, fx1, fy1 = extents('ra', ('build-up',))
    FLY = fly_frames()
    return f"""Tiberian Sun Tick Tank, dug in (GATICK; art GTTICK, GTTICKMK; TS's turret TTNKTUR + TTNKBARL) rebuilt for Red Alert
Remastered (HD) from Luke's redesigned Tick Tank (the units hand-off: ts-ttnk-hd, TSTTNK).

One 3D model: the units chat's Tick Tank (src/ttnk3hd.py: Westwood's render followed closely, with Luke's notes), dug
in as Luke described the deploy (the front burrows into the ground and the turret moves to the back of the tank,
forming an entrenched gun emplacement), rendered with the units chat's renderer (src/hdv.py, src/rcrender.py: the
buildings' light, outline, house colour and shadow baked in at ~75% black) at the buildings' scale (128 px a cell,
4.17 px a voxel; the units' canvas is 192 px a cell, which the game draws at two thirds).

WHAT IT IS
  - the tank, facing east (TS's way round: TS's GTTICKMK starts with the tank facing TS's east), dug in the way TS's
    GTTICKMK does it (Luke): the nose digs in and the tank pitches nose-down to 81 degrees, sinking until only its
    rear third stands out of the ground (the drum, the claws and the front under it). The pose is fitted to TS's
    GTTICK (0.85 of its silhouette in TS's camera at TS's size, src/tickfit.py), the build-up's pitch to GTTICKMK
    frame by frame;
  - the soil: heaped round the hull where it goes into the ground, higher on the east where the nose went in first,
    loose spoil at its foot, a few clods; dark loam with lighter dry crumbs and a few stones; soil caked on the hull
    where it meets the ground;
  - the turret on top: it runs back along the rails on the humps' crests (the units' design) and, as the tank rears
    up, goes over the rear edge onto the rear plate, the top once the tank stands; it sits level on a short dark post
    and turns true. The empty ring well shows on the deck where it stood. v2.1 (Luke): the turret 1.75 times the
    size above its ring and plate; the ring and plate kept as they were, so the seat still fits the rear plate.
  TS's GTTICK is the same idea drawn from TS's own tank (its rear end standing out of the ground, TS's voxel turret on
  it); here Luke's tank does it.

VIEWS
  ra-grid/   On RA's square grid: an orthographic camera 32 degrees above the ground, looking north. TS's way round
             (the tank facing east, its south side to the camera).
             PLOT 1x1 (128x128). CANVAS {W}x{H}: the plot at x {px0}-{px1}, y {py0}-{py1}, so its centre is the canvas
             centre ({W // 2}, {H // 2}). From the 128x256 start, grown {px0} px left and right
             ({px0 // 16} steps of 16): the standing tank is tall, so its shadow reaches {bx1 - ox:.0f} px east of the
             cell's centre (the building and turret frames span x {bx0}-{bx1}, y {by0}-{by1}); the tank also drives
             up longer than a cell (the build-up reaches {ox - fx0:.0f} px west of the cell's centre). Up and down the
             start's 64 px hold. Everything drawn: x {ex0}-{ex1}, y {ey0}-{ey1}.
             PLACE: the tank stays where the unit stands: its position (the cell's centre, TS's HVA origin) on the
             ground at ({ox:.1f}, {oy:.2f}), exactly where the units hand-off draws it (192, 191 on its 384 x 384 canvas
             = 128, 127.33 at two thirds, both canvases centred on the cell's centre), so nothing moves when it
             deploys: build-up frame 00 matches TSTTNK frames 24 + 56 drawn at two thirds to 0.995 of the silhouette,
             colours within 2/255 on average. (The buildings' rule, the foundation's south edge on the plot's, would
             put it 31 px lower than the unit stands, and it would jump down as it deploys.)
  ts-angle/  TS's own camera (30 degrees, looking north-west), lit from TS's side, at the RA view's scale (TS's frame
             x3.77; TS px (0, 0) at canvas (0, 0)), the cell's centre where TS's 96x48 GTTICK frames put it. CANVAS
             {iw}x{ih} (TS's 96x48 frame is 362x181 at this scale; 16 px taller so the soil and the debris at the
             front fit). Optional.
COLOUR     Green = house colour, exactly the yard's green (0,214,0) x (1 + 1.1 grain) as the units hand-off has it: the
           hull tops and noses, the trim lines, the pipes' back rings, the turret's brackets and hatch; the side skirts
           at half its brightness (the render's dark maroon: Luke). Every frame has a -trim.png (white = house colour,
           antialiased).

FOLDERS (each view has the same; every frame on the view's full canvas, in place, with a -trim.png)
  building/{NAME}-00, -01   healthy and damaged (RA's two states), dug in, without the turret.
                                  TS's GTTICK draws no damage (its frames 0 and 1 are the same picture), so the damage
                                  is mine, kept light, greys and browns, on the part standing out of the ground: soot
                                  on the rear plate (the top), the south skirt, the hull tops and the humps' back (on
                                  the house colour it comes in specks: a pixel is house colour or soot, never darkened
                                  house colour); four shell holes (two in the south skirt, one in the south hull top,
                                  one in the rear plate: black core, scorched ring, bright ragged rim); paint scraped
                                  off the south hull top's edge and streaked down the south skirt; the skirt's first
                                  trim line shot away; the front pipe snapped, its front half lying on the ground south
                                  of the tank; the south rear corner box knocked off, lying on the ground; steel
                                  fragments.
  turret/{NAME}-turret-00..31
                                  the turret at the mod's 32 facings (00 north, anticlockwise: 08 west, 16 south,
                                  24 east), drawn in place on its post, each cut against the healthy base: the turret
                                  solid, and the shadow it casts on the base and the ground (and the sky it hides) as
                                  black at the darkening's alpha, so the same set darkens either state correctly.
                                  One set over both states (TS's turret has none of its own either).
  build-up/{NAME}-build-00..24
                                  25 frames, one per GTTICKMK frame: 00 the tank as the units hand-off draws it (TSTTNK
                                  hull 24 with its shadow, turret 56 over it casting none, EA's way: see PLACE);
                                  the turret runs back along its rails (01-09), its shadow fading in (01-04); the nose
                                  digs in and the tank rears up, pitching nose-down at GTTICKMK's pace (about 3
                                  degrees a frame, the last push to 81 degrees in 20-24) and sinking; the turret goes
                                  over the rear edge onto the rear plate as it steepens (09-22); soil flies out
                                  ({FLY}) and heaps up round the hull. 24 is exactly building-00 with turret-24.
  muzzle.txt                      the barrel's tip per turret facing: canvas px on both views, and leptons from the
                                  cell's centre; the turret's pivot.
  DRAW ORDER: the building, then turret/ (any facing).

previews/  the dug-in tank on its own (turret east); both states next to TS's; next to the GDI Construction Yard, Power
           Plant, Component Tower and a Nod wall run (RA grid); the house colour next to the yard's; the build-up as a
           strip and a GIF against GTTICKMK; the turret turning over both states (TS draws its turret from a voxel, so
           its column stays still); deploy-vs-unit.png (TSTTNK at two thirds next to build-up 00, and their
           difference); turret-32-facings.png (all 32 over the healthy base, the muzzle marked).
src/       Python 3 (numpy, scipy, Pillow, scikit-image for the 3D export). The units chat's model and renderer
           (ttnk3hd.py, hdv.py, rc.py, rcrender.py, hd.py ...) with: tickm.py the dug-in model (the pitch, the turret's
           run and post, the berm, the build-up's timing), tickdamage.py the soil and damage paint and the damaged
           geometry, tickrender.py the views and canvases, tickfinal.py the frames, tickexport.py the 3D model,
           tickspec.py the README and muzzle.txt, tickfit.py the fit to TS's frames (mkfit.txt: its numbers per
           GTTICKMK frame); fakeunit.py the voxel frame recovered from the units' .glb.
             python3 tickfinal.py states|turret|build ra|iso [ss]   the frames (ss 4 used; states first)
             python3 tickexport.py                                 the 3D model
3D         {os.path.basename(PKG)}-3d/ (zipped on its own): {NAME}.glb, see its README.

JUDGEMENT CALLS (each easy to change)
  - TS's way of digging in (Luke): the tank rears up nose-down to 81 degrees and sinks until its rear third stands
    out of the ground, fitted to GTTICK and GTTICKMK (tickm.py FINAL and SCHED). (The first version followed the
    units chat's concept: 9 degrees nose-down, the nose in a berm; it sprawled over 1.3 cells.)
  - Luke's tank and turret (the units hand-off), not TS's tank and TTNKTUR voxel; TS's turret offsets
    (TurretAnimX=4, TurretAnimY=10, TurretAnimZAdjust=-20) and PrimaryFireFLH=48,0,64 were for TS's turret: the
    turret's place and its muzzle are in muzzle.txt.
  - The turret ends on the rear plate, on top of the standing tank (where TS puts its own turret), level on a short
    post so it turns true; it gets there along the units' rails and over the rear edge as the tank rears up.
  - The place: where the unit stands, not the buildings' rule (see PLACE), so the deploy doesn't jump. tickrender.py
    origin() moves it.
  - Not turned: the tank faces east, TS's way round.
  - The soil round the hull: in dark loam (not TS's desert sand, which you asked to leave out).
  - The damaged state is mine (TS has none), kept light; the turret is the same set for both states.
  - The turret 1.75 times the units' first design above its seat (Luke); its ring and plate the size they were (a
    ring 1.5 times bigger overhung the standing tank's top). The units package (ts-ttnk-hd) is redone to match:
    its turret frames 32-63, muzzle.txt and tsttnk.glb (src/ttnk3hd.py TURRET_SCALE and RING_SCALE).
"""


README_3D = f"""Tick Tank, dug in: 3D model (glTF 2.0 binary), from the same model that renders the frames.

{NAME}.glb   (TS's way round: the tank faces east, as on the RA grid)
  nodes    TickTankDugIn > dug_in_facing_east (the unit frame: x forward, y left, z up) >
             base, base-damaged   building frames 00 / 01: the hull dug in (pitched 81 degrees nose-down and sunk, cut
                                  at the ground), the turret's post on top, the soil round it (a heightfield surface),
                                  and for 01 the debris on the ground
             turret               a node at the turret's pivot on its post on top, the turret facing east: turn it about its
                                  local up axis to aim (anticlockwise seen from above; the mod's facing = 24 + angle /
                                  11.25 degrees); its child "muzzle" is the gun's tip
             turret-pivot, cell-centre   markers (the cell's centre on the ground = the unit's position)
  colours  COLOR_0 = the materials' base colours (no light or shadow), COLOR_1 = house colour (white), like the -trim
           masks. The painted detail (soot, shell holes, soil caked on the hull, the soil's mottling) is in the frames
           only.
  cameras  camera-ra-grid: orthographic, 32 degrees above the ground, looking north; frames exactly the ra-grid canvas.
           camera-ts-angle: TS's camera (30 degrees, looking north-west); the ts-angle canvas.
  axes     glTF's: x east, y up, z south (towards the RA camera). 1.0 = one cell (128 px on the RA grid). Origin = the
           cell's centre on the ground.
"""


# ------------------------------------------------------------------------------------------------ extra previews
def unit_two_thirds():
    h = Image.open(f'{UNITS}/frames/tsttnk-0024.png').convert('RGBA')
    h.alpha_composite(Image.open(f'{UNITS}/frames/tsttnk-0056.png').convert('RGBA'))
    a = np.array(h).astype(np.float64) / 255
    pm = a.copy(); pm[..., :3] *= pm[..., 3:4]
    q = np.array(Image.fromarray((pm * 255).round().astype(np.uint8), 'RGBA').resize((256, 256), Image.LANCZOS)) / 255.0
    al = q[..., 3:4]
    q[..., :3] = np.where(al > 1e-4, q[..., :3] / np.maximum(al, 1e-4), 0)
    W, H = TR.CANVAS['ra']
    full = Image.fromarray((np.clip(q, 0, 1) * 255).round().astype(np.uint8), 'RGBA')
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out.paste(full.crop(((256 - W) // 2, 0, (256 - W) // 2 + W, 256)), (0, (H - 256) // 2))
    return out


def deploy_vs_unit(pk, out):
    import ypreview as P
    u = unit_two_thirds()
    b0 = pk.fr('ra', 'build-up', f'{NAME}-build-00')
    b24 = pk.fr('ra', 'build-up', f'{NAME}-build-24')
    A = np.array(u).astype(float); B = np.array(b0).astype(float)
    d = np.abs(A - B).max(2) * np.maximum(A[..., 3], B[..., 3]) / 255.0
    dm = Image.fromarray(np.clip(d * 4, 0, 255).astype(np.uint8), 'L').convert('RGBA')
    z = 2
    tiles = [(u, 'TSTTNK 24 + 56 (the units hand-off) at two thirds'), (b0, 'build-up 00'),
             (dm, 'difference x4'), (b24, 'build-up 24 (dug in)')]
    c = pk.crop('ra', u)
    w, h = c.width * z, c.height * z
    S = Image.new('RGBA', (len(tiles) * (w + 12), h + 34), (30, 30, 30, 255))
    dr = ImageDraw.Draw(S)
    for k, (im, t) in enumerate(tiles):
        im = pk.crop('ra', im)
        tile = (P.on_bg(im) if k != 2 else im).resize((w, h), Image.LANCZOS)
        S.paste(tile, (k * (w + 12), 34))
        dr.text((k * (w + 12) + 4, 6), t, fill=(255, 255, 0, 255))
    S.save(f'{out}/deploy-vs-unit.png')


def turret_sheet(pk, out):
    import ypreview as P
    base = pk.building('ra', 0)
    c = TR.cfg('ra')
    z = 2
    tiles = []
    for f in range(32):
        im = base.copy(); im.alpha_composite(pk.fr('ra', 'turret', f'{NAME}-turret-{f:02d}'))
        im = P.on_bg(im)
        x, y = project('ra', K.muzzle(c, 1.0, K.turret_angle(f)))
        dr = ImageDraw.Draw(im)
        dr.ellipse([x - 1.5, y - 1.5, x + 1.5, y + 1.5], outline=(255, 40, 40, 255))
        im = pk.crop('ra', im).resize((pk.crop('ra', im).width * z, pk.crop('ra', im).height * z), Image.LANCZOS)
        ImageDraw.Draw(im).text((4, 4), f'{f:02d}', fill=(255, 255, 0, 255))
        tiles.append(im)
    w, h = tiles[0].size
    S = Image.new('RGBA', (8 * (w + 4), 4 * (h + 4)), (30, 30, 30, 255))
    for k, t in enumerate(tiles):
        S.paste(t, ((k % 8) * (w + 4), (k // 8) * (h + 4)))
    S.save(f'{out}/turret-32-facings.png')


SPEC = dict(
    name=NAME, title='Tick Tank (dug in)', pkg=PKG, hand=HAND,
    ts='GTTICK', K=TR.ISO_K, O=(0.0, 0.0), iso_size=TR.CANVAS['iso'], ra_size=TR.CANVAS['ra'], ra_head=TR.RA_HEAD,
    ra_left=TR.RA_LEFT, cells=(1, 1), state_dir='building', own_scene=True,
    overlays=[dict(folder='turret', prefix='turret', n=32, shared=True, ts_shp=None, ts_frame=lambda t, lv: None,
                   index=lambda t: (24 + t) % 32)],
    build_n=TF.BUILD_N, ts_mk_n=25, ts_mk='GTTICKMK', ts_of=list(range(25)), idle_n=32,
    idle_label="the turret turning (TS draws its turret from a voxel: no frames)", idle_ms=110,
    crop={'iso': (64, 24, 304, 200), 'ra': (16, 30, 224, 190)},
    zoom=2.0, green_zoom=2.5, gif_zoom=2.0, strip_w=170, build_pick=(0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 21, 24),
    extra_previews=[deploy_vs_unit, turret_sheet],
    src=[os.path.join(HERE, f) for f in ('tickm.py', 'tickdamage.py', 'tickrender.py', 'tickfinal.py', 'tickexport.py',
                                          'tickspec.py', 'tickdeliver.py', 'tickglbcheck.py', 'tickfit.py', 'mkfit.txt',
                                          'fakeunit.py')] +
        [os.path.join(HERE, 'src', f) for f in ('ttnk3hd.py', 'hdv.py', 'rc.py', 'rcrender.py', 'hd.py', 'walls2.py',
                                                 'wnoise.py', 'voxrender.py', 'nvox.py', 'vxl.py', 'vxlunit.py',
                                                 'tsnormals.py', 'paths.py', 'export3d.py', 'vexport.py',
                                                 'rcexport.py', 'glbcheck.py')] +
        ['nodeliver.py', 'bdeliver.py', 'ypreview.py'],
    readme=readme, readme_3d=README_3D,
)
