"""
lfinish.py - the Limpet Drone's package: the 20 frames (lrender.py), their checks, the previews, the .glb, README, src and
the two zips (ts-limp-hd.zip, ts-limp-hd-3d.zip).

    python3 lfinish.py [render]
"""
import json, os, re, shutil, subprocess, sys, tempfile, time
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
H = HANDOFF + '/15-TSLIMP/'
PKG = os.path.join(HERE, '..', 'pkg', 'ts-limp-hd')
D3 = os.path.join(HERE, '..', 'pkg', 'ts-limp-hd-3d')
NAME = 'tslimp'
INMOD = H + 'in-mod/tslimp/frames/tslimp-%04d.png'
TS = H + 'ts-original/LIMPED/frames/limped-%03d.png'
HD = PKG + '/frames/tslimp-%04d.png'
BG = (96, 108, 72, 255)
VALIDATOR = 'validate.js'

import lrender as R
import limp as L


def render_all(ss=4):
    from frameio import save
    os.makedirs(PKG + '/frames', exist_ok=True)
    P = R.load(); place = json.load(open(os.path.join(HERE, 'place.json')))
    for k in range(20):
        t0 = time.time()
        img, trim = R.frame(k, P, place, ss)
        save(img, trim, HD % k)
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)


def alpha(p):
    return np.asarray(Image.open(p).convert('RGBA'))[..., 3]


def check():
    bad = []; ov_d = []; ov_s = []; shadow_peak = []
    for k in range(20):
        a = alpha(HD % k); t = np.asarray(Image.open(HD[:-4] % k + '-trim.png'))
        if a.shape != (192, 192):
            bad.append((k, 'size'))
        if a[0].any() or a[-1].any() or a[:, 0].any() or a[:, -1].any():
            bad.append((k, 'touches the canvas edge'))
        b = alpha(INMOD % k)
        if k < 10:
            m, n = a > 127, b > 127
            ov_d.append((m & n).sum() / (m | n).sum())
        else:
            if t.any():
                bad.append((k, 'shadow frame with house colour'))
            shadow_peak.append(int(a.max()))
            m, n = a > 40, b > 40
            ov_s.append((m & n).sum() / (m | n).sum())
            if a.max() < 135:
                bad.append((k, 'shadow under alpha 135'))
    return bad, float(np.mean(ov_d)), float(np.mean(ov_s)), min(shadow_peak)


def on_bg(im):
    b = Image.new('RGBA', im.size, BG); b.alpha_composite(im.convert('RGBA'))
    return b


def previews():
    pv = PKG + '/previews'; os.makedirs(pv, exist_ok=True)
    crop = (30, 0, 162, 192)
    # the blink over its shadow, the mod's frames beside HD (2 ticks a frame)
    frames = []
    for k in range(10):
        row = []
        for lab, fmt in (('in-mod', INMOD), ('HD', HD)):
            im = Image.new('RGBA', (192, 192), (0, 0, 0, 0))
            im.alpha_composite(Image.open(fmt % (10 + k)).convert('RGBA'))
            im.alpha_composite(Image.open(fmt % k).convert('RGBA'))
            b = on_bg(im).crop(crop).convert('RGB').resize((264, 384), Image.LANCZOS)
            t = Image.new('RGB', (264, 400), (28, 30, 34)); t.paste(b, (0, 16))
            ImageDraw.Draw(t).text((4, 2), '%s  %d + %d' % (lab, k, 10 + k), fill=(230, 220, 160))
            row.append(t)
        out = Image.new('RGB', (2 * 264 + 6, 400), (20, 22, 26)); out.paste(row[0], (0, 0)); out.paste(row[1], (270, 0))
        frames.append(out.convert('P', palette=Image.ADAPTIVE, colors=255))
    frames[0].save(pv + '/blink.gif', save_all=True, append_images=frames[1:], duration=133, loop=0, disposal=1)
    # TS's sprite (as the mod scales it), the mod's frame and HD, 2x
    K, DX, DY = 6.2, -211.85, -65.35
    ts = Image.open(TS % 0).convert('RGBA'); sh = Image.open(TS % 10).convert('RGBA')
    sa = np.asarray(sh).copy(); sa[..., :3] = 0; sa[..., 3] = (sa[..., 3] > 0) * 128     # TS's shadow: half black
    sh = Image.fromarray(sa, 'RGBA')
    big = Image.new('RGBA', (192, 192), (0, 0, 0, 0))
    for im in (sh, ts):
        up = im.resize((round(im.size[0] * K), round(im.size[1] * K)), Image.NEAREST)
        big.paste(up, (round(DX), round(DY)), up)
    tiles = []
    for lab, im in (("TS's sprite", big), ('in-mod', Image.alpha_composite(Image.open(INMOD % 10).convert('RGBA'),
                                                                            Image.open(INMOD % 0).convert('RGBA'))),
                    ('HD', Image.alpha_composite(Image.open(HD % 10).convert('RGBA'), Image.open(HD % 0).convert('RGBA')))):
        b = on_bg(im).crop(crop).convert('RGB').resize((264, 384), Image.NEAREST if lab != 'HD' else Image.LANCZOS)
        t = Image.new('RGB', (264, 400), (28, 30, 34)); t.paste(b, (0, 16))
        ImageDraw.Draw(t).text((4, 2), lab, fill=(230, 220, 160))
        tiles.append(t)
    out = Image.new('RGB', (3 * 270, 400), (20, 22, 26))
    for i, t in enumerate(tiles):
        out.paste(t, (i * 270, 0))
    out.save(pv + '/drone.png')
    # scale: next to the HD harvester and EA's rifleman, as the game draws them (this canvas at two thirds)
    HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
    E1 = H + 'reference-hd/RA_E1/frames/e1-0004.png'
    items = [('TS Harvester (HD)', Image.open(HARV % 24).convert('RGBA'), 1.0),
             ("EA's rifleman", Image.open(E1).convert('RGBA'), 1.0),
             ('Limpet Drone (HD)', Image.alpha_composite(Image.open(HD % 10).convert('RGBA'),
                                                          Image.open(HD % 0).convert('RGBA')), 2 / 3)]
    crops = []
    for lab, im, sc in items:
        if sc != 1.0:
            im = im.resize((round(im.size[0] * sc), round(im.size[1] * sc)), Image.LANCZOS)
        a = np.array(im); ys, xs = np.nonzero(a[..., 3] > 0)
        crops.append((lab, im.crop((max(xs.min() - 6, 0), 0, min(xs.max() + 7, im.size[0]), im.size[1]))))
    gap = 30; Hs = 260; ground = 215
    Wt = sum(c.size[0] for _, c in crops) + gap * (len(crops) + 1)
    out = Image.new('RGBA', (Wt, Hs), BG); d = ImageDraw.Draw(out); x = gap
    for lab, im in crops:
        a = np.array(im)
        low = np.nonzero((a[..., 3] > 100).any(1))[0].max()
        out.alpha_composite(im, (x, ground - low))
        d.text((x + im.size[0] // 2 - 45, Hs - 20), lab, fill=(240, 232, 190))
        x += im.size[0] + gap
    out.convert('RGB').save(pv + '/scale.png')
    # the shape: TS's sprite as colour classes beside the model's in TS's own camera
    import lfit as F
    js = json.load(open(os.path.join(HERE, 'fit_c.json')))
    P = R.load()
    cl = F.model_cls(L.parts(P), js['ax'], js['y0'])
    cov = (cl > 0).mean(-1)
    maj = np.zeros(cov.shape, int); best = np.zeros(cov.shape, int)
    for c in (1, 2, 5):
        cnt = (cl == c).sum(-1); better = (cnt > best) & (cov >= 0.5)
        maj = np.where(better, c, maj); best = np.maximum(best, np.where(cov >= 0.5, cnt, 0))
    cols = {0: (96, 108, 72), 1: (0, 200, 0), 2: (200, 200, 205), 5: (45, 45, 50)}

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
    return iou


def glb():
    import vexport as VE, rcexport as RX
    from export3d import orient
    os.makedirs(D3, exist_ok=True)
    P = R.load(); place = json.load(open(os.path.join(HERE, 'place.json')))
    cells_px = 192.0; upc = cells_px / R.PPU
    A = VE.A
    ALB = {L.NUB: R.DARK, L.CAP: R.GREY, L.DOME: R.GREEN, L.BAND: R.GREY, L.CONE: R.GREEN, L.LENS: R.DARK,
           L.LAMP: np.array([236, 236, 232.])}
    g = VE.AnimGLB()
    root = g.node('LimpetDrone')
    body = g.node('drone', root, translation=A @ np.array([0, 0, R.HOVER]) / upc)
    for p in L.parts(P):
        m = RX.part_mesh(p)
        if m is None:
            continue
        V, F = m
        Pm, Fi, N = (RX.flat_shaded if p.comp in (L.CONE,) else RX.smooth_shaded)(V, F)
        Pg = (Pm @ A.T) / upc; Ng = N @ A.T
        Fi = orient(Pg, Fi, Ng)
        rgb = np.tile(ALB[p.comp], (len(Pg), 1))
        house = np.full(len(Pg), 1.0 if p.comp in (L.DOME, L.CONE) else 0.0)
        g.node(p.name, body, mesh=(Pg.astype(np.float32), Fi, Ng.astype(np.float32), rgb, house))
    for name, q in zip(('light_left', 'light_right'), L.light_points(P)):
        g.node(name, body, translation=A @ q / upc)
    cam = R.camera(place['origin'])
    gx, gy = cam.ground(np.array([96.0]), np.array([96.0]))
    g.camera('camera_mod', 0.0, 32.0, list(A @ np.array([gx[0], gy[0], 0.0]) / upc), 96.0 / cells_px, 96.0 / cells_px,
             extras=dict(note='orthographic, 32 degrees above the ground, looking north; frames the drone frames\' 192 x '
                              '192 canvas'))
    path = os.path.join(D3, 'tslimp.glb')
    g.save(path, extras=dict(units='1.0 = one cell (192 px on the canvas, 128 px in the game)', hover='%.1f TS px'
                             % R.HOVER))
    val = subprocess.run(['node', VALIDATOR, path], capture_output=True, text=True).stdout.strip().splitlines()[0]
    out = subprocess.run([sys.executable, os.path.join(HERE, 'glbcheck.py'), path, HD % 0,
                          os.path.join(tempfile.gettempdir(), 'limp-check.png'), '192'], capture_output=True, text=True)
    line = [l for l in out.stdout.splitlines() if 'overlap' in l]
    return val, line[-1].split(':')[-1].strip() if line else 'n/a'


SRC = ['limp.py', 'lfit.py', 'lrender.py', 'lplace.py', 'lmap.py', 'lfinish.py', 'fit_c.json', 'place.json']
SHARED = ['/home/claude/units/work/vox/' + f for f in ('rc.py', 'rcrender.py', 'rcexport.py', 'frameio.py', 'glbcheck.py',
                                                       'vexport.py', 'voxrender.py', 'vxlunit.py', 'tsnormals.py')]
RENDERER = ['hd.py', 'walls2.py', 'wnoise.py', 'export3d.py', 'vxl.py']


def package_src():
    S = PKG + '/src'
    shutil.rmtree(S, ignore_errors=True); os.makedirs(S)
    for f in SRC:
        shutil.copy(os.path.join(HERE, f), S)
    for f in SHARED:
        shutil.copy(f, S)
    for f in RENDERER:
        shutil.copy(HANDOFF + '/renderer/' + f, S)
    open(S + '/paths.py', 'w').write(
        '"""where the scripts find Luke\'s hand-off folders: set TS_HANDOFF to the hand-off\'s root folder (the one\n'
        'holding 15-TSLIMP/, 00-TSHARV-example/ and renderer/)."""\nimport os\n'
        "HANDOFF = os.environ.get('TS_HANDOFF', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', "
        "'ts-units-hd-handoff'))\n")
    left = []
    for f in os.listdir(S):
        if not f.endswith('.py') or f == 'paths.py':
            continue
        p = os.path.join(S, f); s = open(p).read()
        s = re.sub(r"sys\.path\.insert\(0, ['\"]/home/claude/units/[^'\"]*['\"]\)\n", '', s)
        if "HANDOFF + '/" in s:
            s = s.replace("HANDOFF + '/", "HANDOFF + '/")
            if 'from paths import HANDOFF' not in s:
                lines = s.split('\n')
                i = max(i for i, l in enumerate(lines) if l.startswith('import ') or l.startswith('from ')) + 1
                lines.insert(i, 'from paths import HANDOFF')
                s = '\n'.join(lines)
        s = s.replace("'validate.js'", "'validate.js'")
        s = s.replace("os.path.join(HERE, 'glbcheck.py')", "os.path.join(HERE, 'glbcheck.py')")
        s = s.replace("os.path.join(HERE, '..', 'pkg', ", "os.path.join(HERE, '..', 'pkg', ")
        open(p, 'w').write(s)
        if '/home/claude' in s and f != 'lfinish.py':        # the packager itself names this machine's folders
            left.append(f)
    # the packaged source must run on its own
    test = tempfile.mkdtemp()
    shutil.copytree(S, test + '/src')
    run = subprocess.run([sys.executable, '-c', 'import json, lrender as R; P = R.load(); pl = json.load(open("place.json")); '
                          'im, tr = R.frame(0, P, pl, 1, False); print("src ok", im.size)'], cwd=test + '/src',
                         capture_output=True, text=True, env=dict(os.environ, TS_HANDOFF='/home/claude/units/ts-units-hd-handoff'))
    shutil.rmtree(test)
    return left, (run.stdout.strip() or run.stderr.strip().splitlines()[-1])


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'render':
        render_all()
    bad, ovd, ovs, peak = check()
    iou = previews()
    val, gov = glb()
    left, srcok = package_src()
    print('problems', bad, '| drone overlap %.2f | shadow overlap %.2f | shadow peak alpha %d | TS-camera overlap %.2f'
          % (ovd, ovs, peak, iou), '|', val, '| glb', gov, '| local paths', left, '|', srcok)
    json.dump(dict(bad=bad, drone_overlap=ovd, shadow_overlap=ovs, shadow_peak=peak, ts_overlap=float(iou), glb=gov,
                   validator=val), open(os.path.join(HERE, 'finish.json'), 'w'), indent=1)


README = """Limpet Drone (Firestorm [LIMPET]) in HD for Tiberian Factions: TSLIMP
=====================================================================

frames/     tslimp-0000.png ... tslimp-0019.png, the mod's 20 frames on its 192 x 192 canvas, each with a -trim.png
            (white = house colour, antialiased):
              0-9     the drone, its light blinking as TS's LIMPED 0-9 (2 ticks a frame)
              10-19   its shadow, the same in every frame (TS's 10-19 are one shadow), drawn under drone 10+n as now
previews/   blink.gif                the drone over its shadow through the blink, the mod's frames beside HD
            drone.png                TS's sprite (scaled as the mod scales it), the mod's frame and HD
            scale.png                next to the HD harvester and EA's rifleman, as the game draws them
            shape.png                TS's sprite as colour classes beside the model's, in TS's own camera
ts-limp-hd-3d/   the 3D model, in its own zip (ts-limp-hd-3d.zip) next to this folder:
            tslimp.glb   the drone in vertex colours, the light's two halves as markers, the mod's camera
src/        the model, its fit, the renderer and the checks (see Rebuilding below)


What it is
----------
One 3D model fitted to Firestorm's own sprite (LIMPED: one shape, no facings), drawn the way the HD buildings and units
are.  TS draws the drone as a solid of revolution, so the model is one: a rounded dark nub standing in a thin grey ring
on top, the house-colour dome (an egg, widest across its middle), the grey band round its waist with its two dark
lenses towards the camera and a white lamp on each lens' left, and the house-colour cone tapering to its tip.  The
light sits on the dome's front two rows over the band, as in TS.
- Sizes: the band, the dome and the cone fitted to the sprite (silhouette and colour classes in TS's own camera,
  30 degrees: overlap {ts:.2f}); the nub, the ring, the lenses and the lamps read straight off TS's pixels.
- The blink: TS lights the two halves of its light in turn through white, yellow, orange, red and dark red, a half at
  a time going dark; each frame takes TS's colour for each half (frame 0: off and red ... frame 9: dark red and
  orange), unshaded, as small as TS's pixels.  TS's glint on the dome above the light in frames 3 and 4 (white, then
  pale blue) is there too, as small.
The drone frames cover the mod's with a silhouette overlap of {od:.2f}.


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.2 canvas px per TS pixel,
  the size and place the mod's drone frames have (found by matching TS's sprite to them, overlap 0.97, and then the
  HD drone to frame 0).  The drone hovers with its tip {hover:.1f} TS px over the ground, as TS's frames have it
  over its shadow.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides facing
  the camera as on the other units.  The game draws this canvas at two thirds (8 canvas px per classic pixel), so the
  outline and the shadow's blur are 1.5 times as wide on the canvas.
- House colour is pure green 0,214,0 x (1 + 1.1 grain) on the dome and the cone (TS's remap pixels), the light left
  out; the -trim masks cover exactly that.  The grey band and ring, the dark nub and lenses: TS's own greys.


Shadow (frames 10-19)
---------------------
The drone's footprint straight under it, as TS draws a hovering unit's shadow: a disc as wide as the drone's widest
part, black at alpha {peak} (the buildings' 75%), blurred as theirs, where the mod's shadow frames have theirs (the
same ground line, about 93 px under the canvas centre).  The README asked for at least alpha 135: today's peak at 112
is now 191.


3D model (ts-limp-hd-3d/)
------------------------
tslimp.glb   the drone in its own colours, with the mod's camera
- Nodes: LimpetDrone > drone (lifted {hover:.1f} TS px off the ground) > nub, cap, dome, band, cone, the lenses and
  lamps, and light_left / light_right (markers at the light's two halves).
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground, under the drone's axis.
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 192 canvas exactly
  (checked by drawing the mesh through it over frame 0: overlap {glb}).
- The file passes Khronos's glTF validator with no errors or warnings ({val}; the infos are the two empty marker
  nodes).
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- The shadow as the drone's footprint straight under it (TS's shape), not cast sideways by the buildings' light:
  a hovering unit's shadow in TS sits under it, and the game draws it under the drone as it bobs.
- The shadow at the buildings' alpha 191, over the README's minimum of 135.
- The dome an egg on the band (TS's dome is widest across its middle and narrows into the band).


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy, Pillow and cma.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are (TS_HANDOFF).
  limp.py                the drone as convex parts;  fit_c.json  its fitted sizes
  lfit.py                the fit to TS's sprite;  lmap.py  how the mod scales and places TS's sprite
  lrender.py             one frame (the drone with its light, or its shadow);  lplace.py  places them as the mod has
                         them -> place.json
  rc.py, rcrender.py     the ray caster and the buildings' look for models made of convex parts
  rcexport.py, vexport.py   the .glb;  glbcheck.py  draws the .glb through its camera to check it
  lfinish.py             renders, checks, previews and packages it all
    python3 lrender.py frames 0,10 4 out      renders frames
"""


def write_readmes(st):
    txt = README.format(ts=st['ts_overlap'], od=st['drone_overlap'], hover=R.HOVER, peak=st['shadow_peak'],
                        glb=st['glb'], val=st['validator'])
    open(PKG + '/README.txt', 'w').write(txt)
    i = txt.index('3D model (ts-limp-hd-3d/)'); j = txt.index('Judgement calls')
    open(D3 + '/README.txt', 'w').write('Limpet Drone (Firestorm [LIMPET]) in HD: the 3D model\n'
                                        '====================================================\n\n' + txt[i:j].rstrip() + '\n')


def zips():
    import pngopt
    pngopt.optimize_folder(PKG)
    shutil.rmtree(PKG + '/src/__pycache__', ignore_errors=True)
    parent = os.path.dirname(PKG)
    for name in ('ts-limp-hd', 'ts-limp-hd-3d'):
        z = os.path.join(parent, name + '.zip')
        if os.path.exists(z):
            os.remove(z)
        subprocess.run(['zip', '-qr', name + '.zip', name], cwd=parent)
        print('zip', z, os.path.getsize(z) // 1024, 'KB')


if __name__ == '__main__':
    st = json.load(open(os.path.join(HERE, 'finish.json')))
    write_readmes(st)
    zips()
