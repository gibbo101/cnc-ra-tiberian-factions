"""dshppkg.py - assemble the Dropship package from its rendered frames (renderall.sh): previews, the shape sheet, the 3D
model (checked through its camera and by Khronos's validator), README (the version and the checks' numbers filled
in), src/, and the two zips.

    python3 dshppkg.py PKG_ROOT version
(PKG_ROOT holds ts-dshp-hd/ with frames/ and facings/ already rendered.)
"""
import os, sys, shutil, subprocess, zipfile, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from paths import HANDOFF

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = ['dshpmodel.py', 'dshpvox.py', 'dshpnose.py', 'dshpmat.py', 'dshpcam.py', 'dshprender.py', 'renderall.sh',
       'dshpexport.py', 'glbcheck.py', 'dshpcomp.py', 'dshpsheets.py', 'dshplook.py', 'dshppkg.py', 'dshptab.py',
       'dvox.py', 'dreg.py', 'vdump.py', 'hcls.py', 'rc.py', 'rcrender.py', 'qparts.py', 'rcexport.py', 'glbtools.py',
       'frameio.py', 'paths.py']
RENDERER = ['hd.py', 'walls2.py', 'wnoise.py', 'export3d.py', 'vxl.py']
VALIDATE = os.environ.get('VALIDATE', 'validate.js')
FMV = os.environ.get('FMV', 'fmv-front.png')
REF = HANDOFF + '/26-TSDSHP/reference-hd/'
INMOD = HANDOFF + '/26-TSDSHP/in-mod/tsdshp/frames/tsdshp-%04d.png'
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)


def run(cmd, **kw):
    r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, **kw)
    if r.returncode:
        raise RuntimeError(r.stdout + r.stderr)
    return r.stdout


def zipdir(root, name, out):
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        base = os.path.join(root, name)
        z.write(base, name + '/')
        for dp, dn, fn in os.walk(base):
            dn[:] = sorted(d for d in dn if d != '__pycache__')
            for d in dn:
                z.write(os.path.join(dp, d), os.path.relpath(os.path.join(dp, d), root) + '/')
            for f in sorted(fn):
                z.write(os.path.join(dp, f), os.path.relpath(os.path.join(dp, f), root))


def crop(p, box, z, bg=(112, 108, 92)):
    im = Image.open(p).convert('RGBA').crop(box)
    b = Image.new('RGBA', im.size, bg + (255,)); b.alpha_composite(im)
    return b.convert('RGB').resize((int(im.width * z), int(im.height * z)), Image.LANCZOS)


def cockpit(out, fdir):
    import dshpsheets as D
    fmv = Image.open(FMV).convert('RGB')
    fmv = fmv.resize((int(fmv.width * 1.45), int(fmv.height * 1.45)), Image.LANCZOS)
    f16 = crop(fdir + '/tsdshp-0016.png', (250, 300, 410, 440), 2.6)
    f12 = crop(fdir + '/tsdshp-0012.png', (85, 290, 330, 410), 2.0)
    f0 = crop(fdir + '/tsdshp-0008.png', (8, 225, 200, 345), 2.6)
    top = D.stack([D.label(fmv, "Westwood's FMV"), D.label(f16, 'head-on (facing 16)')], vertical=False, gap=6)
    D.stack([top, D.stack([D.label(f0, 'frame 0'), D.label(f12, 'facing 12')], vertical=False, gap=6)],
            gap=8).save(out)


def shadow_frames(out, framedir):
    import dshpsheets as D
    rows = []
    for k in (1, 2, 3):
        a = INMOD % k; b = os.path.join(framedir, 'tsdshp-%04d.png' % k)
        box = D.content_box([a, b])
        rows.append(D.stack([D.label(D.on_bg(Image.open(a), box), 'frame %d - in the mod now' % k),
                             D.label(D.on_bg(Image.open(b), box), 'frame %d - %s' % (k, D.VER))], vertical=False, gap=6))
    D.stack(rows, gap=8).save(out)


def turn_gif(out, fdir, scale=0.4):
    import dshpsheets as D
    paths = [fdir + '/tsdshp-%04d.png' % k for k in range(32)]
    box = D.content_box(paths, pad=6)
    frames = []
    for p in paths:
        t = D.on_bg(Image.open(p), box)
        t = t.resize((int(t.width * scale), int(t.height * scale)), Image.LANCZOS)
        frames.append(t.convert('P', palette=Image.ADAPTIVE, colors=255))
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=120, loop=0, disposal=1)


def scale_sheet(out, frame0):
    bg = (88, 100, 70)
    items = [("EA's C-17 (TD)", REF + 'TD_C17/frames/c17-0008.png'), ("EA's Badger (RA)", REF + 'RA_BADR/frames/badr-0004.png'),
             ('TS Dropship (HD %s)' % D.VER, frame0)]
    tiles = []
    for lab, p in items:
        im = Image.open(p).convert('RGBA')
        a = np.array(im)[..., 3] > 8
        ys, xs = np.nonzero(a)
        im = im.crop((max(xs.min() - 10, 0), max(ys.min() - 10, 0), xs.max() + 11, ys.max() + 11))
        b = Image.new('RGBA', (im.width, im.height + 26), bg + (255,)); b.alpha_composite(im, (0, 0))
        b = b.convert('RGB')
        d = ImageDraw.Draw(b)
        w = d.textlength(lab, font=FONT)
        d.text(((b.width - w) / 2, b.height - 20), lab, font=FONT, fill=(230, 230, 220))
        tiles.append(b)
    H = max(t.height for t in tiles); W = sum(t.width for t in tiles) + 30 * (len(tiles) + 1)
    s = Image.new('RGB', (W, H + 20), bg); x = 30
    for t in tiles:
        s.paste(t, (x, 10 + H - t.height)); x += t.width + 30
    s.save(out)


def iou_alpha(a, b, thr=128):
    A = np.array(Image.open(a).convert('RGBA'))[..., 3] > thr
    B = np.array(Image.open(b).convert('RGBA'))[..., 3] > thr
    return (A & B).sum() / (A | B).sum()


if __name__ == '__main__':
    root, ver = sys.argv[1], sys.argv[2]
    pkg = os.path.join(root, 'ts-dshp-hd')
    p3d = os.path.join(root, 'ts-dshp-hd-3d')
    pv = os.path.join(pkg, 'previews')
    fr, fa = os.path.join(pkg, 'frames'), os.path.join(pkg, 'facings')
    for d in (pv, p3d):
        os.makedirs(d, exist_ok=True)
    import dshpsheets as D
    import dshpcomp
    D.VER = ver
    D.ship(os.path.join(pv, 'ship.png'), fr)
    D.closeups(os.path.join(pv, 'closeups.png'), fr)
    cockpit(os.path.join(pv, 'cockpit.png'), fa)
    shadow_frames(os.path.join(pv, 'shadow-frames.png'), fr)
    D.facings(os.path.join(pv, 'facings.png'), fa)
    turn_gif(os.path.join(pv, 'facings-turn.gif'), fa)
    scale_sheet(os.path.join(pv, 'scale.png'), os.path.join(fr, 'tsdshp-0000.png'))
    ious = dshpcomp.sheet(os.path.join(pv, 'shape.png'), ['game', 'side', 'top', 'front', 'back'])
    shape_game, shape_mean = '%.2f' % ious['game'], '%.2f' % np.mean(list(ious.values()))
    final_f0 = '%.2f' % iou_alpha(INMOD % 0, os.path.join(fr, 'tsdshp-0000.png'))
    print('previews done; shape', shape_game, shape_mean, 'final', final_f0, flush=True)
    # the 3D model, checked through its camera over facing 24, and by Khronos's validator
    glb = os.path.join(p3d, 'tsdshp.glb')
    run([sys.executable, 'dshpexport.py', glb])
    g = run([sys.executable, 'glbcheck.py', glb, os.path.join(fa, 'tsdshp-0024.png'),
             os.path.join(HERE, 'logs', 'glbcheck.png'), '656'])
    glb_ov = g.strip().split()[-1]
    val = subprocess.run(['node', VALIDATE, glb], capture_output=True, text=True).stdout.strip().splitlines()[0]
    val = val.replace(' warnings', ', warnings').replace(' infos', ', infos').replace(' hints', ', hints')
    # README
    txt = open(os.path.join(HERE, 'README_v2.txt')).read()
    txt = (txt.replace('VERSION', ver).replace('SHAPE_GAME', shape_game).replace('SHAPE_MEAN', shape_mean)
           .replace('FINAL_F0', final_f0).replace('GLB_OVERLAP', glb_ov).replace('GLB_VALIDATOR', val))
    head = txt.splitlines()[0]
    txt = head + '\n' + '=' * len(head) + '\n' + '\n'.join(txt.splitlines()[2:]) + '\n'
    open(os.path.join(pkg, 'README.txt'), 'w').write(txt)
    i0 = txt.index('3D model (ts-dshp-hd-3d/tsdshp.glb)'); i1 = txt.index('Judgement calls')
    t3 = 'ts-dshp-hd-3d: the 3D model of ts-dshp-hd (%s)' % ver
    open(os.path.join(p3d, 'README.txt'), 'w').write(t3 + '\n' + '=' * len(t3) + '\n\n' + txt[i0:i1].rstrip() + '\n')
    # src (the absolute paths to the shared scripts taken out: they sit next to the unit's own in src/)
    src = os.path.join(pkg, 'src')
    if os.path.isdir(src):
        shutil.rmtree(src)
    os.makedirs(src)
    for f in SRC:
        shutil.copy(os.path.join(HERE, f), src)
    for f in RENDERER:
        shutil.copy(os.path.join(HANDOFF, 'renderer', f), src)
    for f in os.listdir(src):
        p = os.path.join(src, f)
        s = open(p).read()
        s2 = s.replace("os.environ.get('V1_FRAMES', 'v1/frames') + '/tsdshp-%04d.png'",
                       "os.environ.get('V1_FRAMES', 'v1/frames') + '/tsdshp-%04d.png'")
        s2 = s2.replace("os.environ.get('V1_FACINGS', 'v1/facings') + '/tsdshp-%04d.png'",
                        "os.environ.get('V1_FACINGS', 'v1/facings') + '/tsdshp-%04d.png'")
        s2 = s2.replace("os.environ.get('V2_FRAMES', 'v2/frames') + '/tsdshp-%04d.png'",
                        "os.environ.get('V2_FRAMES', 'v2/frames') + '/tsdshp-%04d.png'")
        s2 = s2.replace("os.environ.get('REVIEW', 'units-review')", "os.environ.get('REVIEW', 'units-review')")
        s2 = s2.replace("os.environ.get('REVIEW', 'units-review') + '/'", "os.environ.get('REVIEW', 'units-review') + '/'")
        s2 = s2.replace("VALIDATE = os.environ.get('VALIDATE', 'validate.js')",
                        "VALIDATE = os.environ.get('VALIDATE', 'validate.js')")
        s2 = s2.replace("FMV = os.environ.get('FMV', 'fmv-front.png')",
                        "FMV = os.environ.get('FMV', 'fmv-front.png')")
        s2 = s2.replace('cd "$(dirname "$0")"', 'cd "$(dirname "$0")"')
        for qt in ('"', "'"):
            s2 = s2.replace('sys.path.insert(0, %s/home/claude/units/ts-units-hd-handoff/renderer%s)' % (qt, qt),
                            'sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))')
        if s2 != s:
            open(p, 'w').write(s2)
    left = [f for f in os.listdir(src) if '/home/claude' in open(os.path.join(src, f)).read() or
            '/root/' in open(os.path.join(src, f)).read()]
    print('src files still naming /home/claude or /root:', left)
    # zips
    for name in ('ts-dshp-hd', 'ts-dshp-hd-3d'):
        out = os.path.join(root, name + '.zip')
        if os.path.exists(out):
            os.remove(out)
        zipdir(root, name, out)
        print(name + '.zip', '%.1f MB' % (os.path.getsize(out) / 1e6))
    print('shape game', shape_game, 'mean', shape_mean, 'final f0', final_f0, 'glb', glb_ov, val)
