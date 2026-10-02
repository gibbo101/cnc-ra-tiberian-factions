"""
hsfinish.py - the Hunter-Seeker's package: the 8 frames (hsrender.py), their checks, the previews, the .glb, README, src
and the two zips (ts-hunt-hd.zip, ts-hunt-hd-3d.zip).

    python3 hsfinish.py [render]
"""
import json, os, re, shutil, subprocess, sys, tempfile, time
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
H = HANDOFF + '/16-TSHUNT/'
PKG = os.path.join(HERE, 'pkg', 'ts-hunt-hd')
D3 = os.path.join(HERE, 'pkg', 'ts-hunt-hd-3d')
INMOD = H + 'in-mod/tshunt/frames/tshunt-%04d.png'
TS = H + 'ts-original/GGHUNT/frames/gghunt-%03d.png'
HD = PKG + '/frames/tshunt-%04d.png'
BG = (96, 108, 72, 255)
VALIDATOR = '/home/claude/units/tools/validate.js'

import hsrender as R
import hseek as S


def render_all(ss=4):
    from frameio import save
    os.makedirs(PKG + '/frames', exist_ok=True)
    P = R.load(); place = json.load(open(os.path.join(HERE, 'place.json')))
    for k in range(8):
        t0 = time.time()
        img, trim = R.frame(k, P, place, ss)
        save(img, trim, HD % k)
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)


def check():
    bad = []; ov = []
    for k in range(8):
        a = np.asarray(Image.open(HD % k).convert('RGBA'))
        t = np.asarray(Image.open(HD[:-4] % k + '-trim.png'))
        al = a[..., 3]
        if al.shape != (384, 384):
            bad.append((k, 'size'))
        if al[0].any() or al[-1].any() or al[:, 0].any() or al[:, -1].any():
            bad.append((k, 'touches the canvas edge'))
        if t.any():
            bad.append((k, 'house colour'))
        # no shadow: every see-through pixel is the outline ring (dark, at most 0.55) or an edge
        sh = (al > 0) & (al < 250) & (a[..., :3].max(-1) < 10) & (al > 150)
        if sh.sum() > 40:
            bad.append((k, 'shadow-like pixels %d' % sh.sum()))
        b = np.asarray(Image.open(INMOD % k))[..., 3]
        m, n = al > 127, b > 127
        ov.append((m & n).sum() / (m | n).sum())
    return bad, float(np.mean(ov))


def on_bg(im):
    b = Image.new('RGBA', im.size, BG); b.alpha_composite(im.convert('RGBA'))
    return b


def previews():
    pv = PKG + '/previews'; os.makedirs(pv, exist_ok=True)
    crop = (112, 100, 272, 290)
    frames = []
    for k in range(8):
        row = []
        for lab, fmt in (('in-mod', INMOD), ('HD', HD)):
            b = on_bg(Image.open(fmt % k)).crop(crop).convert('RGB').resize((320, 380), Image.LANCZOS)
            t = Image.new('RGB', (320, 396), (28, 30, 34)); t.paste(b, (0, 16))
            ImageDraw.Draw(t).text((4, 2), '%s  frame %d' % (lab, k), fill=(230, 220, 160))
            row.append(t)
        out = Image.new('RGB', (2 * 320 + 6, 396), (20, 22, 26)); out.paste(row[0], (0, 0)); out.paste(row[1], (326, 0))
        frames.append(out.convert('P', palette=Image.ADAPTIVE, colors=255))
    frames[0].save(pv + '/spin.gif', save_all=True, append_images=frames[1:], duration=200, loop=0, disposal=1)
    # TS's sprite (x 4, as the mod has it), the mod's frame and HD, 2x
    ts = Image.open(TS % 4).convert('RGBA')
    big = Image.new('RGBA', (384, 384), (0, 0, 0, 0))
    up = ts.resize((ts.size[0] * 4, ts.size[1] * 4), Image.NEAREST)
    big.paste(up, (46, 108), up)
    tiles = []
    for lab, im in (("TS's sprite", big), ('in-mod', Image.open(INMOD % 4)), ('HD', Image.open(HD % 4))):
        b = on_bg(im).crop(crop).convert('RGB').resize((320, 380), Image.NEAREST if lab != 'HD' else Image.LANCZOS)
        t = Image.new('RGB', (320, 396), (28, 30, 34)); t.paste(b, (0, 16))
        ImageDraw.Draw(t).text((4, 2), lab, fill=(230, 220, 160))
        tiles.append(t)
    out = Image.new('RGB', (3 * 326, 396), (20, 22, 26))
    for i, t in enumerate(tiles):
        out.paste(t, (i * 326, 0))
    out.save(pv + '/droid.png')
    # scale: next to the HD harvester and EA's TD Orca, as the game draws them (this canvas 1:1, as the mod has it)
    HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
    ORCA = H + 'reference-hd/TD_ORCA/frames/orca-0024.png'
    items = [('TS Harvester (HD)', Image.open(HARV % 24).convert('RGBA')), ("EA's TD Orca", Image.open(ORCA).convert('RGBA')),
             ('Hunter-Seeker (HD)', Image.open(HD % 4).convert('RGBA'))]
    crops = []
    for lab, im in items:
        a = np.array(im); ys, xs = np.nonzero(a[..., 3] > 0)
        crops.append((lab, im.crop((max(xs.min() - 6, 0), max(ys.min() - 6, 0), min(xs.max() + 7, im.size[0]),
                                    min(ys.max() + 7, im.size[1])))))
    gap = 30; Hs = max(c.size[1] for _, c in crops) + 40
    Wt = sum(c.size[0] for _, c in crops) + gap * (len(crops) + 1)
    out = Image.new('RGBA', (Wt, Hs), BG); d = ImageDraw.Draw(out); x = gap
    for lab, im in crops:
        out.alpha_composite(im, (x, Hs - 30 - im.size[1]))
        d.text((x + im.size[0] // 2 - 45, Hs - 20), lab, fill=(240, 232, 190))
        x += im.size[0] + gap
    out.convert('RGB').save(pv + '/scale.png')
    # the shape: TS's sprite as colour classes beside the model's in TS's own camera
    import hsfit as F
    js = json.load(open(os.path.join(HERE, R.FIT)))
    P = R.load()
    cl = F.model_cls(S.parts(P), js['ax'], js['y0'])
    cov = (cl > 0).mean(-1)
    maj = np.zeros(cov.shape, int); best = np.zeros(cov.shape, int)
    for c in (2, 4, 5, 6):
        cnt = (cl == c).sum(-1); better = (cnt > best) & (cov >= 0.5)
        maj = np.where(better, c, maj); best = np.maximum(best, np.where(cov >= 0.5, cnt, 0))
    cols = {0: (96, 108, 72), 2: (200, 200, 205), 4: (170, 120, 50), 5: (45, 45, 50), 6: (170, 60, 50)}

    def img(c):
        o = np.zeros(c.shape + (3,), np.uint8)
        for k, v in cols.items():
            o[c == k] = v
        return o
    iou = ((cov >= 0.5) & F.TM).sum() / ((cov >= 0.5) | F.TM).sum()
    a = np.concatenate([img(F.TC * F.TM), np.full((F.TC.shape[0], 1, 3), 255, np.uint8), img(maj)], 1)
    im = Image.fromarray(a).resize((a.shape[1] * 12, a.shape[0] * 12), Image.NEAREST)
    ImageDraw.Draw(im).text((4, 4), "TS's sprite  |  the model, TS's camera  (overlap %.2f)" % iou, fill=(255, 255, 0))
    im.save(pv + '/shape.png')
    return float(iou)


def glb():
    import vexport as VE, rcexport as RX
    from export3d import orient
    os.makedirs(D3, exist_ok=True)
    P = R.load(); place = json.load(open(os.path.join(HERE, 'place.json')))
    # one cell is 30.3 TS px (the TS units: 192 canvas px a cell at 6.33 px a TS px); this canvas draws 4 px a TS px
    cells_px = R.PPU * 192.0 / 6.33
    upc = cells_px / R.PPU
    A = VE.A
    ALB = {S.BODY: R.BRONZE, S.CHEST: R.BRONZE, S.SHOULDER: R.BRONZE, S.LOBE: R.BRONZE, S.LUG: R.BRONZE,
           S.NECK: R.BRONZE, S.BAND: R.BRONZE, S.COLLAR: R.MAST, S.MAST: R.MAST, S.TIP: R.TIP, S.STAR: R.STAR,
           S.SPIKE: R.SPIKE, S.STUB: R.STUB, S.WING: R.STEEL, S.SLOT: R.SLOT, S.STRUT: R.STEEL, S.FIN: R.STEEL,
           S.STRIP: R.STRIP, S.MARK: R.MARK}
    ROUND = (S.BODY, S.CHEST, S.SHOULDER, S.LOBE, S.LUG, S.NECK, S.BAND, S.COLLAR, S.MAST, S.TIP, S.STAR, S.MARK)
    g = VE.AnimGLB()
    root = g.node('HunterSeeker')
    for p in S.parts(P):
        m = RX.part_mesh(p)
        if m is None:
            continue
        V, F = m
        Pm, Fi, N = (RX.smooth_shaded if p.comp in ROUND else RX.flat_shaded)(V, F)
        Pg = (Pm @ A.T) / upc; Ng = N @ A.T
        Fi = orient(Pg, Fi, Ng)
        g.node(p.name, root, mesh=(Pg.astype(np.float32), Fi, Ng.astype(np.float32), np.tile(ALB[p.comp], (len(Pg), 1)),
                                   np.zeros(len(Pg))))
    g.node('star_light', root, translation=A @ S.star_light(P, R.ELEV) / upc)
    cam = RR_cam = R.RR.ra_cam(R.PPU, place['origin'])
    gx, gy = cam.ground(np.array([192.0]), np.array([192.0]))
    g.camera('camera_mod', 0.0, 32.0, list(A @ np.array([gx[0], gy[0], 0.0]) / upc), 192.0 / cells_px,
             192.0 / cells_px, extras=dict(note='orthographic, 32 degrees above the ground, looking north; frames the '
                                                '384 x 384 canvas'))
    path = os.path.join(D3, 'tshunt.glb')
    g.save(path, extras=dict(units='1.0 = one cell (30.3 TS px, as the other TS units; 121 px on this canvas, '
                                   'which draws the droid at 4 px a TS px)'))
    val = subprocess.run(['node', VALIDATOR, path], capture_output=True, text=True).stdout.strip().splitlines()[0]
    out = subprocess.run([sys.executable, '/home/claude/units/work/vox/glbcheck.py', path, HD % 4,
                          os.path.join(tempfile.gettempdir(), 'hunt-check.png'), '384'], capture_output=True, text=True)
    line = [l for l in out.stdout.splitlines() if 'overlap' in l]
    return val, line[-1].split(':')[-1].strip() if line else 'n/a'


SRC = ['hseek.py', 'hsfit.py', 'hsrender.py', 'hsplace.py', 'hsmap.py', 'hsfinish.py', 'fit_h.json', 'place.json']
SHARED = ['/home/claude/units/work/vox/' + f for f in ('rc.py', 'rcrender.py', 'rcexport.py', 'frameio.py', 'glbcheck.py',
                                                       'vexport.py', 'voxrender.py', 'vxlunit.py', 'tsnormals.py')]
RENDERER = ['hd.py', 'walls2.py', 'wnoise.py', 'export3d.py', 'vxl.py']


def package_src():
    Sd = PKG + '/src'
    shutil.rmtree(Sd, ignore_errors=True); os.makedirs(Sd)
    for f in SRC:
        shutil.copy(os.path.join(HERE, f), Sd)
    for f in SHARED:
        shutil.copy(f, Sd)
    for f in RENDERER:
        shutil.copy(HANDOFF + '/renderer/' + f, Sd)
    open(Sd + '/paths.py', 'w').write(
        '"""where the scripts find Luke\'s hand-off folders: set TS_HANDOFF to the hand-off\'s root folder (the one\n'
        'holding 16-TSHUNT/, 00-TSHARV-example/ and renderer/)."""\nimport os\n'
        "HANDOFF = os.environ.get('TS_HANDOFF', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', "
        "'ts-units-hd-handoff'))\n")
    left = []
    for f in os.listdir(Sd):
        if not f.endswith('.py') or f == 'paths.py':
            continue
        p = os.path.join(Sd, f); s = open(p).read()
        s = re.sub(r"sys\.path\.insert\(0, ['\"]/home/claude/units/[^'\"]*['\"]\)\n", '', s)
        if "HANDOFF + '/" in s:
            s = s.replace("HANDOFF + '/", "HANDOFF + '/")
            if 'from paths import HANDOFF' not in s:
                lines = s.split('\n')
                i = max(i for i, l in enumerate(lines) if l.startswith('import ') or l.startswith('from ')) + 1
                lines.insert(i, 'from paths import HANDOFF')
                s = '\n'.join(lines)
        open(p, 'w').write(s)
        if '/home/claude' in s and f != 'hsfinish.py':
            left.append(f)
    test = tempfile.mkdtemp()
    shutil.copytree(Sd, test + '/src')
    run = subprocess.run([sys.executable, '-c', 'import json, hsrender as R; P = R.load(); pl = json.load(open("place.json")); '
                          'im, tr = R.frame(0, P, pl, 1, False); print("src ok", im.size)'], cwd=test + '/src',
                         capture_output=True, text=True, env=dict(os.environ, TS_HANDOFF='/home/claude/units/ts-units-hd-handoff'))
    shutil.rmtree(test)
    return left, (run.stdout.strip() or run.stderr.strip().splitlines()[-1])


README = """Hunter-Seeker (TS [GHUNTER]) in HD for Tiberian Factions: TSHUNT
================================================================

frames/     tshunt-0000.png ... tshunt-0007.png, the mod's 8 frames on its 384 x 384 canvas, each with a -trim.png (all
            black: it never takes house colour), one facing, 3 ticks a frame, no shadow (the game draws it from the
            frame)
previews/   spin.gif                 the 8 frames, the mod's beside HD
            droid.png                TS's sprite (x 4, as the mod has it), the mod's frame and HD
            scale.png                next to the HD harvester and EA's TD Orca, as the game draws them
            shape.png                TS's sprite as colour classes beside the model's, in TS's own camera
ts-hunt-hd-3d/   the 3D model, in its own zip (ts-hunt-hd-3d.zip) next to this folder:
            tshunt.glb   the droid in vertex colours, a marker at the star's light, the mod's camera
src/        the model, its fit, the renderer and the checks (see Rebuilding below)


What it is
----------
One 3D model built from TS's own sprite (GGHUNT: TS draws the droid from one side only; its 8 frames differ just in
the star's light and the fins' flash), every part read off TS's pixels (frame 4) and then fitted to them in TS's own
camera (30 degrees; silhouette and colour classes, overlap {ts:.2f}), drawn the way the HD buildings and units are.
Top to bottom, with the pixels each part comes from (columns and rows of TS's 73 x 73 frame):
- the mast: 1 px, blue-grey (rows 8-9), with a bronze band (row 7) and a grey tip (row 6)
- the star (rows 10-12): a blue core 3 px across with a spike either side (columns 34 and 38); its light on the centre
  pixel (36, 11), and the dark grey stub just under the light (36, 12)
- the neck (columns 35-37): bronze, with a dark collar under its top (row 16)
- the strut (row 19): a steel bar from column 32 to 40, behind the neck, between the wings' inner edges
- the wings (rows 16-20, columns 27-32 and 40-45): thin steel blades, wider at the bottom and leaning in at the top,
  each with a dark slot one pixel in from its outer edge ((30, 17)-(29, 18) and (42, 17)-(43, 18)); a red-brown mark on
  the left one's inner top corner (32, 16)
- the shoulder (rows 21-24): 13 px across but only 3-4 rows tall, so a bar across the body, not a disc (a disc that
  wide would stand 7 rows tall in TS's camera, and its back half would show over the bar); its ends rise into two
  rounded lobes (their tops on row 21 at columns 31 and 41, the row empty between them and the middle)
- the chest: TS's highlight (white at (35, 23)-(36, 23), yellow at (35, 22), pink round them) sits on the shoulder's
  middle where the surface faces the camera, so the body's top there is a round mass standing out in front of the bar
- the body: 7 px across (columns 33-39) from row 25 down, a lug either side at rows 27-28 (columns 32 and 40), the blue
  strip down its front (column 36, rows 27-29), its bottom on row 34
- three steel fins round the bottom, alike: one towards the camera (columns 35-37, rows 32-35: 1 px at its top and 3
  below, so a ridged wedge) and two to the sides (columns 31-33 and 39-41, rows 31-34), with red-brown marks at their
  roots ((33, 31), its twin (39, 31) in shadow)
The frames differ as TS's do: the star's light pulses blue to white (frame 3) and back, in TS's colours; at frame 0 the
fins' upper faces flash white (their undersides stay as they are, as in TS's frame 0) and they stay a little brighter
through frames 1-3, as TS's shades there are.
The finished frames cover the mod's with a silhouette overlap of {ov:.2f}.


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 4 canvas px per TS pixel, the
  size the mod has now (its frames are TS's sprite x 4 exactly), placed by matching the HD droid to frame 4.  The
  README said to keep this size unless you say to grow it: one number (PPU in hsrender.py) and the place follows.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides facing
  the camera as on the other units.
- The bronze shines as TS's does: TS's sprite has a white highlight on the shoulder's front, so the bronze takes a
  highlight from the light TS lit its sprites with (front left of the camera, hd.py's L_CAM_TS); it lands on the chest,
  as TS's does.
- Colours: TS's bronze on the body (its be913c lit, a58538 mid); the mod's steel on TS's remap parts (wings, strut,
  fins: as light on average as the mod's frames have them, 148, 153, 166 on the wings); TS's blues on the star and the
  strip and its blue-grey on the mast and collar (each as dark on average as TS's pixels for it); TS's red-brown marks.
  No house colour (the -trim masks are black).


3D model (ts-hunt-hd-3d/)
------------------------
tshunt.glb   the droid in its own colours, with the mod's camera
- Nodes: HunterSeeker > body, chest, shoulder and lobes, lugs, neck and collar, mast, band and tip, the star with its
  spikes and stub, strut, wings and their slots, fins, strip, marks, and star_light (a marker at the star's light).
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (30.3 TS px, as the other TS units' models; 121 px
  on this canvas, which draws the droid at 4 px a TS px).  Origin: the body's bottom on its axis.
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 384 canvas exactly
  (checked by drawing the mesh through it over frame 4: overlap {glb}).
- The file passes Khronos's glTF validator with no errors or warnings ({val}; the info is the empty marker node).
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (none).


Judgement calls (each one easy to change)
-----------------------------------------
- This is the second version.  The first read the droid as round all the way (a disc for a shoulder, a drum for a
  belt): from 32 degrees those showed as a saucer and a second rim TS doesn't have.  Now every part is read off TS's
  pixels first (the list above) and the fit only moves them a pixel or so.  A fit with the camera height left free came
  back to 28-29 degrees, so TS did draw it from its usual 30.
- TS's single view can't show depth.  The shoulder bar and its lobes are as deep as they are tall.  The wings are thin
  blades lying back (85 degrees from upright): from TS's camera any lean looks the same, and lying back they catch the
  light the way TS's do (its brightest remap shade).  The side fins sit 101 degrees round from the front one, as the
  fit put them.
- The red-brown marks are where TS has them: the left wing only (the right wing's corner is plain remap), and both fin
  roots.
- Kept at the mod's current size (4 canvas px a TS pixel, smaller than the other TS units' 6.4), as the README said.


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy, Pillow and cma.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are (TS_HANDOFF).
  hseek.py               the droid as convex parts, with the pixels each part is read from;  fit_h.json  its fit
  hsfit.py               the fit to TS's sprite;  hsmap.py  how the mod scales and places TS's sprite (x 4 at 46, 108)
  hsrender.py            one frame;  hsplace.py  places it as the mod has it -> place.json
  rc.py, rcrender.py     the ray caster and the buildings' look for models made of convex parts
  rcexport.py, vexport.py   the .glb;  glbcheck.py  draws the .glb through its camera to check it
  hsfinish.py            renders, checks, previews and packages it all
    python3 hsrender.py frames 0,3 4 out      renders frames
"""


def write_readmes(st):
    txt = README.format(ts=st['ts_overlap'], ov=st['overlap'], glb=st['glb'], val=st['validator'])
    open(PKG + '/README.txt', 'w').write(txt)
    i = txt.index('3D model (ts-hunt-hd-3d/)'); j = txt.index('Judgement calls')
    open(D3 + '/README.txt', 'w').write('Hunter-Seeker (TS [GHUNTER]) in HD: the 3D model\n'
                                        '================================================\n\n' + txt[i:j].rstrip() + '\n')


def zips():
    import pngopt
    pngopt.optimize_folder(PKG)
    shutil.rmtree(PKG + '/src/__pycache__', ignore_errors=True)
    parent = os.path.dirname(PKG)
    for name in ('ts-hunt-hd', 'ts-hunt-hd-3d'):
        z = os.path.join(parent, name + '.zip')
        if os.path.exists(z):
            os.remove(z)
        subprocess.run(['zip', '-qr', name + '.zip', name], cwd=parent)
        print('zip', z, os.path.getsize(z) // 1024, 'KB')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'render':
        render_all()
    bad, ov = check()
    iou = previews()
    val, gov = glb()
    left, srcok = package_src()
    st = dict(bad=bad, overlap=ov, ts_overlap=iou, glb=gov, validator=val)
    json.dump(st, open(os.path.join(HERE, 'finish.json'), 'w'), indent=1)
    write_readmes(st)
    zips()
    print('problems', bad, '| overlap %.2f | TS-camera overlap %.2f' % (ov, iou), '|', val, '| glb', gov,
          '| local paths', left, '|', srcok)
