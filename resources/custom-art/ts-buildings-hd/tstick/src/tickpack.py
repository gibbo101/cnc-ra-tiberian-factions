"""tickpack.py - the dug-in Tick Tank's package, RA grid only (since 6 Oct): muzzle.txt, previews, README, src, the
.glb and its check, the zips.  PKG (env) holds ra-grid/ already (tickfinal.py states | turret | build ra).
    python3 tickpack.py UNITS_PKG"""
import os, sys, glob, shutil, zipfile, subprocess
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tickm as K, tickrender as TR, tickfinal as TF, tickspec as S
import voxrender as VR

PKG = TF.PKG
NAME = TF.NAME
TSO = os.environ.get('TS_ORIG', '/home/claude/units/handovers/tick-dugin/tick-tank-dug-in-handoff/ts-original-and-prompt/ts-original')
BG = (96, 104, 80, 255)
TSK = 3.77                       # TS px -> RA canvas px in the previews (TS's 96 x 48 frame at the buildings' scale)
FACE = {0: 'north', 8: 'west', 16: 'south', 24: 'east'}[K.FACING]


def on(im):
    b = Image.new('RGBA', im.size, BG); b.alpha_composite(im.convert('RGBA')); return b


def fr(sub, name):
    return Image.open(TF.path('ra', sub, name)).convert('RGBA')


def scene(level=0, f=None):
    b = fr('building', f'{NAME}-{level:02d}')
    b.alpha_composite(fr('turret', f'{NAME}-turret-{(K.FACING if f is None else f):02d}'))
    return b


def ts(sub, i):
    fs = sorted(x for x in os.listdir(f'{TSO}/{sub}/frames') if x.endswith('.png'))
    im = Image.open(f'{TSO}/{sub}/frames/{fs[i]}').convert('RGBA')
    im = im.resize((round(im.width * TSK), round(im.height * TSK)), Image.NEAREST)
    W, H = TR.CANVAS['ra']
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); c.paste(im, ((W - im.width) // 2, (H - im.height) // 2 + 20)); return c


def label(im, txt):
    out = Image.new('RGB', (im.width, im.height + 22), (28, 30, 26)); out.paste(on(im).convert('RGB'), (0, 22))
    ImageDraw.Draw(out).text((5, 5), txt, fill=(232, 226, 210)); return out


def row(tiles, gap=8):
    W = sum(t.width for t in tiles) + gap * (len(tiles) - 1); H = max(t.height for t in tiles)
    s = Image.new('RGB', (W, H), (40, 42, 46)); x = 0
    for t in tiles:
        s.paste(t, (x, 0)); x += t.width + gap
    return s


def col(rows, gap=8):
    W = max(r.width for r in rows); H = sum(r.height for r in rows) + gap * (len(rows) - 1)
    s = Image.new('RGB', (W, H), (40, 42, 46)); y = 0
    for r in rows:
        s.paste(r, (0, y)); y += r.height + gap
    return s


def z(im, k=2):
    return im.resize((im.width * k, im.height * k), Image.LANCZOS)


def plot_box(im):
    d = ImageDraw.Draw(im); x0, y0, x1, y1 = TR.PLOT['ra']; d.rectangle((x0, y0, x1 - 1, y1 - 1), outline=(170, 168, 130, 255))
    return im


def unit_two_thirds(units):
    """the unit as its package draws it (hull frame FACING + turret frame 32 + FACING), at two thirds, on this canvas."""
    h = Image.open(f'{units}/frames/tsttnk-{K.FACING:04d}.png').convert('RGBA')
    h.alpha_composite(Image.open(f'{units}/frames/tsttnk-{32 + K.FACING:04d}.png').convert('RGBA'))
    a = np.array(h).astype(np.float64) / 255
    pm = a.copy(); pm[..., :3] *= pm[..., 3:4]
    q = np.array(Image.fromarray((pm * 255).round().astype(np.uint8), 'RGBA').resize((256, 256), Image.LANCZOS)) / 255.0
    al = q[..., 3:4]; q[..., :3] = np.where(al > 1e-4, q[..., :3] / np.maximum(al, 1e-4), 0)
    W, H = TR.CANVAS['ra']
    full = Image.fromarray((np.clip(q, 0, 1) * 255).round().astype(np.uint8), 'RGBA')
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out.paste(full.crop(((256 - W) // 2, 0, (256 - W) // 2 + W, 256)), (0, (H - 256) // 2))
    return out


def previews(units):
    pv = f'{PKG}/previews'; os.makedirs(pv, exist_ok=True)
    W, H = TR.CANVAS['ra']
    # on its own, x2, with the plot
    a = z(plot_box(on(scene())))
    label(a, f'dug in, turret {FACE} (frame 00 + turret {K.FACING:02d}), RA grid x2; the box is the 1x1 plot').save(f'{pv}/{NAME}-on-its-own.png')
    # states beside TS's GTTICK
    rows = [row([label(z(ts('GTTICK', lv)), "TS's GTTICK %d (x%.2f)" % (lv, TSK * 2)),
                 label(z(scene(lv)), 'HD %s, RA grid x2' % ('healthy', 'damaged')[lv])]) for lv in (0, 1)]
    col(rows).save(f'{pv}/{NAME}-states-vs-original.png')
    # build-up strip beside TS's GTTICKMK
    tiles = []
    for i in range(K.BUILD_N):
        tiles.append(col([label(ts('GTTICKMK', i), 'TS %02d' % i), label(fr('build-up', f'{NAME}-build-{i:02d}'), 'HD %02d' % i)], 2))
    rows = [row(tiles[k:k + 7]) for k in range(0, len(tiles), 7)]
    col(rows).save(f'{pv}/build-up-strip-vs-original.png')
    # the deploy: dig in, the turret round, dig out, TS beside HD (x2)
    def pair(a_, b_, txt):
        return row([label(z(a_), "TS (GTTICKMK / GTTICK)"), label(z(b_), 'HD, RA grid x2  ' + txt)])
    frames, durs = [], []
    for i in range(K.BUILD_N):
        frames.append(pair(ts('GTTICKMK', i), fr('build-up', f'{NAME}-build-{i:02d}'), 'dig in %02d' % i)); durs.append(500 if i in (0, K.BUILD_N - 1) else 110)
    for k in range(1, 33):
        f = (K.FACING + k) % 32
        frames.append(pair(ts('GTTICK', 0), scene(0, f), 'turret %02d' % f)); durs.append(90)
    for i in range(K.BUILD_N - 1, -1, -1):
        frames.append(pair(ts('GTTICKMK', i), fr('build-up', f'{NAME}-build-{i:02d}'), 'dig out %02d' % i)); durs.append(110 if i else 700)
    pal = frames[30].quantize(colors=255, method=Image.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]
    q[0].save(f'{pv}/deploy-vs-original.gif', save_all=True, append_images=q[1:], duration=durs, loop=0, disposal=1)
    # the turret's 32 facings
    tl = [label(scene(0, f), 'turret %02d' % f) for f in range(32)]
    col([row(tl[k:k + 8], 4) for k in range(0, 32, 8)], 4).save(f'{pv}/turret-32-facings.png')
    # build-up 00 against the unit's own frames
    u = unit_two_thirds(units); b0 = fr('build-up', f'{NAME}-build-00')
    A = np.array(u).astype(float); B = np.array(b0).astype(float)
    d = np.abs(A - B).max(2) * np.maximum(A[..., 3], B[..., 3]) / 255.0
    sil = ((A[..., 3] > 128) & (B[..., 3] > 128)).sum() / max(1, ((A[..., 3] > 128) | (B[..., 3] > 128)).sum())
    dm = Image.fromarray(np.clip(d * 4, 0, 255).astype(np.uint8), 'L').convert('RGBA')
    row([label(z(u), f'the unit: TSTTNK {K.FACING} + {32 + K.FACING} at two thirds'), label(z(b0), 'build-up 00'),
         label(z(dm), 'difference x4 (silhouette overlap %.3f)' % sil)]).save(f'{pv}/deploy-vs-unit.png')
    print('previews done; build-up 00 vs the unit: overlap %.3f, max colour difference %d' % (sil, d.max()))
    return sil, d


def muzzle_text():
    c = TR.cfg('ra')
    pv = S.pivot()
    Mx = VR.facing_cw(VR.mod_to_cw(K.FACING))
    W, H = TR.CANVAS['ra']
    pr = S.project('ra', pv)
    g0 = K.muzzle(c, 1.0, 0.0, sp=pv); loc = g0 - pv; pw = Mx @ pv; L = S.LEP
    lines = [f"Tick Tank, dug in: the gun's muzzle (the barrel's tip) for each turret frame on the {W} x {H} RA-grid canvas",
             "(canvas px), and as an offset from the cell's centre in leptons (256 a cell): east, south, height above the ground.",
             "The turret turns about its pivot on its post on top of the standing tank: "
             f"{abs(pw[0]) * L:.0f} leptons {'east' if pw[0] >= 0 else 'west'} of the cell's centre, {abs(pw[1]) * L:.0f} "
             f"{'south' if pw[1] >= 0 else 'north'}, {pw[2] * L:.0f} up (canvas ({pr[0]:.1f}, {pr[1]:.1f})).",
             f"In the turret's own frame the muzzle is {np.hypot(loc[0], loc[1]) * L:.0f} leptons from the pivot "
             f"({loc[0] * L:.0f} forward, {-loc[1] * L:.0f} to its right) and {loc[2] * L:.0f} above it.",
             "TS's PrimaryFireFLH=48,0,64 was for TS's own turret (TTNKTUR); Luke's turret replaces it.", "",
             "frame  facing      x       y      east   south  height (leptons)"]
    for f in range(32):
        g = K.muzzle(c, 1.0, K.turret_angle(f), sp=pv)
        x, y = S.project('ra', g); w = Mx @ g
        nm = ('N', 'NW', 'W', 'SW', 'S', 'SE', 'E', 'NE')[f // 4] if f % 4 == 0 else ''
        lines.append(f'{f:5d}  {f:4d} {nm:<3s} {x:7.1f} {y:7.1f}  {w[0] * L:7.0f} {w[1] * L:7.0f} {w[2] * L:7.0f}')
    return '\n'.join(lines) + '\n'


def check_frames():
    """every frame on the canvas, nothing within 3 px of its edge; house pixels only where the trim says."""
    W, H = TR.CANVAS['ra']; bad = []; edge = 0; n = 0
    for f in sorted(glob.glob(f'{PKG}/ra-grid/*/*.png')):
        if f.endswith('-trim.png'):
            continue
        a = np.array(Image.open(f).convert('RGBA'))
        n += 1
        if a.shape[:2] != (H, W):
            bad.append(f)
        al = a[..., 3]
        edge = max(edge, int(max(al[:3].max(), al[-3:].max(), al[:, :3].max(), al[:, -3:].max())))
        if not os.path.exists(f[:-4] + '-trim.png'):
            bad.append(f + ' (no trim)')
    return n, bad, edge


def readme(sil, glb_iou):
    W, H = TR.CANVAS['ra']; px0, py0, px1, py1 = TR.PLOT['ra']
    ex = S.extents('ra')
    pv = S.pivot(); Mx = VR.facing_cw(VR.mod_to_cw(K.FACING)); pw = Mx @ pv; L = S.LEP
    th, sink, slide = K.FINAL
    return f"""Tiberian Sun Tick Tank, dug in (GATICK; art GTTICK, GTTICKMK) for Tiberian Factions, in HD on RA's grid: v3
==============================================================================================================

The deployed Tick Tank, built from the same model as the unit (ts-ttnk-hd v3.5, src/ttnk3hd.py), so the unit, the
deploy and the dug-in building always match.  v1 and v2.1 were made in the buildings chat on the unit's v3.1/v3.2;
v3 (7 Oct) was designed with the unit in one flow here (Luke).

ra-grid/     the frames, RA's square grid only (since 6 Oct: no TS-angle frames; the .glb keeps TS's camera)
  building/  {NAME}-00, -01            the tank dug in, no turret: healthy, damaged
  turret/    {NAME}-turret-00 .. 31     the turret at the mod's 32 facings (00 north, anticlockwise: 08 west, 16 south,
                                        24 east), drawn in place, cut against the healthy base: its own pixels solid, the
                                        shadow it casts as black at the darkening's alpha, so one set lies over either state
  build-up/  {NAME}-build-00 .. {K.BUILD_N - 1:02d}   the deploy, one frame per GTTICKMK frame: 00 is the unit exactly as its package
                                        draws it (hull {K.FACING} + turret {32 + K.FACING}, at two thirds; overlap {sil:.3f}); 01-04 the
                                        turret's shadow fading in; {K.BUILD_N - 1:02d} is building-00 with turret-{K.FACING:02d}.  Played
                                        backwards it is the undeploy.
  every frame has a -trim.png (white = house colour)
muzzle.txt   the gun's tip per turret facing, canvas px and leptons, and the turret's pivot
previews/    on its own; both states beside TS's GTTICK; the build-up strip beside GTTICKMK; deploy-vs-original.gif
             (dig in, the turret turning round, dig out); the 32 turret facings; deploy-vs-unit.png (build-up 00
             against the unit's own frames)
src/         everything that renders it (below)
3D           {os.path.basename(PKG)}-3d/ (zipped on its own): {NAME}.glb

THE DESIGN (Luke, 7 Oct)
  - It digs in facing SOUTH, the nose toward the camera (the mod's facing {K.FACING}): the game turns the tank to face
    south before it deploys.  Standing upright, the hull then shows the camera its wide top (the ramps, the groove,
    the pipes) and sits on its own cell; facing east it read as a thin tower with the turret overhanging it.
  - As TS's GTTICKMK does it (Luke: bury nose-first and go almost vertical): the drum and claws dig in, the tank pitches
    nose-down to {th:g} degrees, sinking {sink:g} voxels and sliding {slide:g} forward, until only its back end stands out
    of the ground.  The build-up's timing follows GTTICKMK's pitch frame by frame (src/mkfit.txt).
  - The turret runs back up the two ramps (its track) while the tank is still shallow, then goes over the back edge
    onto a short post on the ramps' tall flat back face, which is the top once the tank is upright (v3.5 raises the
    middle's back, as TS's tank has it, for that flat top; the side hulls stay lower).
  - The turret: v3.5's high dome in house colour, the gun on a trunnion in a slit so it can elevate.
  - Soil: dark loam heaped round the hull where it goes in, highest on the side the nose went in, spoil and clods
    (TS's desert sand left out, Luke); clods thrown up by the drum during the dig.
  - Damaged: shell holes in the exposed hull, soot, a snapped pipe and a corner box knocked to the ground (TS's
    GTTICK has no damage of its own; kept light).

PLACE AND CANVAS
  - Canvas {W} x {H}, the 1x1 plot at x {px0}-{px1}, y {py0}-{py1}.  The tank stays where the unit stood: its position (the
    cell's centre) on the ground at canvas ({TR.origin('ra')[0]:.1f}, {TR.origin('ra')[1]:.2f}), as the unit's frames have it at
    two thirds, so nothing jumps when it deploys (not the buildings' rule of the foundation's south edge on the plot's).
  - Everything, shadow included, lies within x {ex[0]}-{ex[2]}, y {ex[1]}-{ex[3]}.
  - The turret's pivot: {abs(pw[0]) * L:.0f} leptons {'east' if pw[0] >= 0 else 'west'}, {abs(pw[1]) * L:.0f} {'south' if pw[1] >= 0 else 'north'} of the cell's centre, {pw[2] * L:.0f} up.

LOOK
  The units' renderer (src/hdv.py, src/rcrender.py) at the buildings' scale (128 px a cell, 4.17 px a voxel): the
  RA-grid camera (orthographic, 32 degrees above the ground, looking north), the buildings' light, ~75% shadow baked
  in, house colour exactly (0, 214, 0) x (1 + 1.1 grain), damage in greys and browns.

3D MODEL ({NAME}.glb)
  base, base-damaged (the dug-in hull, its post, the soil, the debris), turret (a node at its pivot, facing the hull's
  way; turn it about up to aim: the mod's facing = {K.FACING} + angle / 11.25 degrees), markers turret-pivot, muzzle (a
  child of turret), cell-centre; cameras camera-ra-grid (frames the canvas exactly: drawn through it the mesh covers
  frame 00 + turret {K.FACING:02d} with an overlap of {glb_iou}) and camera-ts-angle (TS's camera, to rebuild the TS angle
  if ever wanted).  Axes glTF's: x east, y up, z south; 1.0 = one cell; origin the cell's centre on the ground.
  Vertex colours: COLOR_0 albedo, COLOR_1 house colour; the painted detail (soot, holes, caked soil) is in the frames.

SRC
  Python 3 with numpy, scipy and Pillow.  ttnk3hd.py the tank (hull and turret, v3.5); tickm.py the dug-in model and
  the deploy (pose per build-up frame, the turret's run and swing, the post, the soil); tickdamage.py the damage;
  tickrender.py the canvas and place; tickfinal.py the frames; tickexport.py / tickglbcheck.py the .glb and its check;
  tickpack.py this package; fakeunit.py the tank's voxel frame; tickfit.py the TS fits (mkfit.txt).
    PKG=out python3 tickfinal.py states ra 4 && python3 tickfinal.py turret ra 4 && python3 tickfinal.py build ra 4
    PKG=out python3 tickexport.py;  PKG=out python3 tickpack.py UNITS_PACKAGE

JUDGEMENT CALLS
  - Facing south to deploy (Luke picked it from the east and south versions): the frames, the .glb and muzzle.txt
    follow the mod's facing {K.FACING}; TICK_FACING=24 in tickm.py rebuilds the east version.
  - The build-up's pitch timing is GTTICKMK's (fitted facing east); the dug-in pose is v2.1's ({th:g} degrees), which
    was fitted to GTTICK facing east.
  - No scale preview next to the GDI yard and plant this time: those scene files live in the buildings work.
"""


def src():
    d = f'{PKG}/src'; os.makedirs(d, exist_ok=True)
    for f in glob.glob(os.path.join(HERE, '*.py')) + [os.path.join(HERE, 'mkfit.txt')]:
        if os.path.basename(f) in ('ttnk3hd_v32.py',):
            continue
        shutil.copy(f, d)


def zipit():
    out = []
    for folder in (PKG, PKG + '-3d'):
        z = folder + '.zip'
        if os.path.exists(z):
            os.remove(z)
        base = os.path.dirname(folder)
        with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(folder):
                for fn in sorted(files):
                    if fn.startswith('.'):
                        continue
                    p = os.path.join(root, fn); zf.write(p, os.path.relpath(p, base))
        with zipfile.ZipFile(z) as zf:
            assert zf.testzip() is None
            out.append('%s %.1f MB %d files ok' % (os.path.basename(z), os.path.getsize(z) / 1e6, len(zf.namelist())))
    return out


if __name__ == '__main__':
    units = sys.argv[1]
    n, bad, edge = check_frames()
    print('frames', n, 'problems', bad, 'highest alpha within 3 px of the edge', edge)
    assert not bad
    open(f'{PKG}/muzzle.txt', 'w').write(muzzle_text())
    sil, d = previews(units)
    r = subprocess.run([sys.executable, os.path.join(HERE, 'tickexport.py')], capture_output=True, text=True, env=dict(os.environ, PKG=PKG))
    print(r.stdout[-400:], r.stderr[-800:])
    r = subprocess.run([sys.executable, os.path.join(HERE, 'tickglbcheck.py'), f'{PKG}-3d/.glbcheck.png'], capture_output=True,
                       text=True, env=dict(os.environ, PKG=PKG))
    print(r.stdout, r.stderr[-800:])
    import re
    ious = re.findall(r'ra 0 overlap ([0-9.]+)', r.stdout)
    open(f'{PKG}/README.txt', 'w').write(readme(sil, ious[0] if ious else '?'))
    open(f'{PKG}-3d/README.txt', 'w').write(readme(sil, ious[0] if ious else '?').split('3D MODEL')[1].split('SRC')[0].join(
        ['Tick Tank, dug in: the 3D model (' + NAME + '.glb)\n\n3D MODEL', '']))
    src()
    for line in zipit():
        print(line)
