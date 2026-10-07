"""apocpkg.py - assemble the Apocalypse package from its finished frames: README (the version, the checks' numbers and
the weapon tips filled in), previews (vdeliver's, the shape sheet, a close-up), src/, the 3D model in its own folder and
zip, and the two zips.

    python3 apocpkg.py PKG_ROOT version
(PKG_ROOT holds ts-apoc-hd/ with frames/ already rendered.)
"""
import os, sys, shutil, subprocess, zipfile, re
import numpy as np
from PIL import Image, ImageDraw
from paths import HANDOFF

HERE = os.path.dirname(os.path.abspath(__file__))
VOX = os.path.dirname(os.path.abspath(__file__))
SRC = ['rc.py', 'rcrender.py', 'rcexport.py', 'glbtools.py', 'qparts.py', 'apocmodel.py', 'apocmat.py', 'apoccam.py',
       'apocrender.py', 'apocspec.py', 'apocexport.py', 'glbcheck.py', 'apocshape.py', 'shapediff.py', 'avox.py',
       'adump.py', 'cmp.py', 'flh.py', 'hcls.py', 'frameio.py', 'paths.py', 'apocpkg.py', 'apoctab.py']
FROM_VOX = ['vdeliver.py', 'vcheck.py']
RENDERER = ['hd.py', 'walls2.py', 'wnoise.py', 'export3d.py', 'vxl.py']
VALIDATE = os.environ.get('VALIDATE', 'validate.js')
CLOSE_FACINGS = [28, 20, 12, 4]


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


def grid(tiles, labels, out, cols=2):
    from PIL import ImageFont
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    w, h = tiles[0].size
    S = Image.new('RGB', (cols * (w + 6) - 6, ((len(tiles) + cols - 1) // cols) * (h + 6) - 6), (30, 30, 30))
    d = ImageDraw.Draw(S)
    for i, (t, lab) in enumerate(zip(tiles, labels)):
        S.paste(t, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
        d.text(((i % cols) * (w + 6) + 6, (i // cols) * (h + 6) + 4), lab, font=font, fill=(240, 230, 180))
    S.save(out)


def closeup(pkg, out, fs=CLOSE_FACINGS, crop=(70, 70, 380, 300), z=2):
    """the assembled tank (hull frame + turret frame) at 2x in four facings, on the review page's ground."""
    from vdeliver import layered, on_bg
    tiles = []
    for f in fs:
        c = on_bg(layered(os.path.join(pkg, 'frames', 'r2apoc-%04d.png'), [f, 32 + f])).crop(crop)
        tiles.append(c.resize((c.width * z, c.height * z), Image.LANCZOS).convert('RGB'))
    grid(tiles, ['hull %d + turret %d' % (f, 32 + f) for f in fs], out)


if __name__ == '__main__':
    root, ver = sys.argv[1], sys.argv[2]
    pkg = os.path.join(root, 'ts-apoc-hd')
    p3d = os.path.join(root, 'ts-apoc-hd-3d')
    os.makedirs(p3d, exist_ok=True)
    os.makedirs(os.path.join(HERE, 'logs'), exist_ok=True)
    # checks on the finished frames: every frame and trim (vcheck); the hull's frames against the mod's, the turret's
    # against the mod's turret moved onto the drawn turret's base (apocshape.inmod_turret)
    sys.path.insert(0, VOX)
    import vdeliver, apocspec, apocshape
    bad, ious = vdeliver.check(apocspec, pkg)
    final_hull = '%.3f' % np.mean(ious[:32])
    tur = []
    for k in range(32, 64):
        a = np.array(Image.open(os.path.join(pkg, 'frames', 'r2apoc-%04d.png' % k)))[..., 3] > 250
        b = np.array(apocshape.inmod_turret(k))[..., 3] > 250
        tur.append((a & b).sum() / max((a | b).sum(), 1))
    final_tur = '%.3f' % np.mean(tur)
    print('problems', bad, 'hull frames', final_hull, 'turret frames (scaled mod)', final_tur, flush=True)
    # previews, the shape sheet (hull and turret, every 4th facing) and the close-ups
    print(run([sys.executable, os.path.join(VOX, 'vdeliver.py'), 'apocspec', 'previews', pkg]), flush=True)
    sc = apocshape.check(list(range(0, 64, 4)), os.path.join(pkg, 'previews', 'shape-8-facings.png'))
    shape_hull, shape_tur = '%.2f' % np.mean(sc[:8]), '%.2f' % np.mean(sc[8:])
    closeup(pkg, os.path.join(pkg, 'previews', 'closeup.png'))
    print('close-up done', flush=True)
    # the 3D model, checked through its camera over hull frame 24 with turret frame 56 seated, and by Khronos's validator
    glb = os.path.join(p3d, 'r2apoc.glb')
    run([sys.executable, 'apocexport.py', glb])
    from vdeliver import layered
    seated = os.path.join(HERE, 'logs', 'assembled24.png')
    layered(os.path.join(pkg, 'frames', 'r2apoc-%04d.png'), [24, 56]).save(seated)
    g = run([sys.executable, 'glbcheck.py', glb, seated, os.path.join(HERE, 'logs', 'glbcheck.png'), '448'])
    glb_ov = g.strip().split()[-1]
    val = subprocess.run(['node', VALIDATE, glb], capture_output=True, text=True).stdout.strip().splitlines()[0]
    val = val.replace(' warnings', ', warnings').replace(' infos', ', infos').replace(' hints', ', hints')
    import flh
    tips = flh.text()
    # README
    txt = open(os.path.join(HERE, 'README_v2.txt')).read()
    txt = (txt.replace('VERSION', ver).replace('SHAPE_HULL', shape_hull).replace('SHAPE_TUR', shape_tur)
           .replace('FINAL_HULL', final_hull).replace('FINAL_TUR', final_tur)
           .replace('GLB_OVERLAP', glb_ov).replace('GLB_VALIDATOR', val)
           .replace('BARREL_FLH', tips['BARREL_FLH']).replace('POD_FLH', tips['POD_FLH']))
    head = txt.splitlines()[0]
    txt = head + '\n' + '=' * len(head) + '\n' + '\n'.join(txt.splitlines()[2:]) + '\n'
    open(os.path.join(pkg, 'README.txt'), 'w').write(txt)
    i0 = txt.index('3D model (ts-apoc-hd-3d/r2apoc.glb)'); i1 = txt.index('Judgement calls')
    t3 = 'ts-apoc-hd-3d: the 3D model of ts-apoc-hd (%s)' % ver
    open(os.path.join(p3d, 'README.txt'), 'w').write(t3 + '\n' + '=' * len(t3) + '\n\n' + txt[i0:i1].rstrip() + '\n')
    # src (the absolute paths to the shared scripts taken out: they sit next to the unit's own in src/)
    src = os.path.join(pkg, 'src')
    if os.path.isdir(src):
        shutil.rmtree(src)
    os.makedirs(src)
    for f in SRC:
        shutil.copy(os.path.join(HERE, f), src)
    for f in FROM_VOX:
        shutil.copy(os.path.join(VOX, f), src)
    for f in RENDERER:
        shutil.copy(os.path.join(HANDOFF, 'renderer', f), src)
    for f in os.listdir(src):
        p = os.path.join(src, f)
        s = open(p).read()
        s2 = s.replace("sys.path.insert(0, '/home/claude/units/work/vox')\n", '')
        s2 = s2.replace("os.environ.get('V2_FRAMES', 'v2/frames') + '/r2apoc-%04d.png'",
                        "os.environ.get('V2_FRAMES', 'v2/frames') + '/r2apoc-%04d.png'")
        s2 = s2.replace("os.environ.get('REVIEW', 'units-review')", "os.environ.get('REVIEW', 'units-review')")
        s2 = s2.replace("os.environ.get('REVIEW', 'units-review') + '/'", "os.environ.get('REVIEW', 'units-review') + '/'")
        s2 = s2.replace("VOX = os.path.dirname(os.path.abspath(__file__))", "VOX = os.path.dirname(os.path.abspath(__file__))")
        s2 = s2.replace("VALIDATE = os.environ.get('VALIDATE', 'validate.js')",
                        "VALIDATE = os.environ.get('VALIDATE', 'validate.js')")
        for qt in ('"', "'"):
            s2 = s2.replace('sys.path.insert(0, %s/home/claude/units/ts-units-hd-handoff/renderer%s)' % (qt, qt),
                            'sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))')
        if s2 != s:
            if not re.search(r'^import (os|os, sys|sys, os)\b', s2, re.M) and 'os.' in s2:
                if re.search(r'^import sys\n', s2, re.M):
                    s2 = re.sub(r'^import sys\n', 'import os, sys\n', s2, count=1, flags=re.M)
                else:
                    s2 = re.sub(r'^(import [^\n]+\n)', r'import os\n\1', s2, count=1, flags=re.M)
            open(p, 'w').write(s2)
    left = [f for f in os.listdir(src) if '/home/claude' in open(os.path.join(src, f)).read()]
    print('src files still naming /home/claude:', left)
    # zips
    for name in ('ts-apoc-hd', 'ts-apoc-hd-3d'):
        out = os.path.join(root, name + '.zip')
        if os.path.exists(out):
            os.remove(out)
        zipdir(root, name, out)
        print(name + '.zip', '%.1f MB' % (os.path.getsize(out) / 1e6))
    print('shape hull', shape_hull, 'turret', shape_tur, 'final hull', final_hull, 'turret', final_tur, 'glb', glb_ov, val,
          tips)
