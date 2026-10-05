"""t4pkg.py - assemble the Mammoth Mk. I package from its finished frames: README (the version and the checks' numbers
filled in), previews (vdeliver's and the shape sheet), src/, the 3D model in its own folder and zip, and the two zips.

    python3 t4pkg.py PKG_ROOT version
(PKG_ROOT holds ts-4tnk-hd/ with frames/ already rendered.)
"""
import os, sys, shutil, subprocess, zipfile, re
import numpy as np
from PIL import Image
from paths import HANDOFF

HERE = os.path.dirname(os.path.abspath(__file__))
VOX = '/home/claude/units/work/vox'
SRC = ['rc.py', 'rcrender.py', 'rcexport.py', 'glbtools.py', 'qparts.py', 't4v2.py', 't4mat.py', 't4cam.py',
       't4render.py', 't4spec2.py', 't4export.py', 'glbcheck.py', 't4shape.py', 't4vox.py', 't4view.py', 't4look.py',
       'hcls.py', 'frameio.py', 'paths.py', 't4pkg.py']
FROM_VOX = ['vdeliver.py', 'vcheck.py']
RENDERER = ['hd.py', 'walls2.py', 'wnoise.py', 'export3d.py', 'vxl.py']
VALIDATE = '/home/claude/units/tools/validate.js'


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


if __name__ == '__main__':
    root, ver = sys.argv[1], sys.argv[2]
    pkg = os.path.join(root, 'ts-4tnk-hd')
    p3d = os.path.join(root, 'ts-4tnk-hd-3d')
    os.makedirs(p3d, exist_ok=True)
    os.makedirs(os.path.join(HERE, 'logs'), exist_ok=True)
    # checks on the finished frames
    chk = run([sys.executable, os.path.join(VOX, 'vdeliver.py'), 't4spec2', 'check', pkg])
    print(chk)
    final_ov = re.search(r"mod's frames: mean ([0-9.]+)", chk).group(1)
    # previews and the shape sheet (hull and turret, every 4th facing)
    print(run([sys.executable, os.path.join(VOX, 'vdeliver.py'), 't4spec2', 'previews', pkg]))
    import t4shape
    ks = list(range(0, 32, 4)) + list(range(32, 64, 4))
    sc = t4shape.check(ks, os.path.join(pkg, 'previews', 'shape-8-facings.png'))
    shape_ov = '%.2f' % np.mean(sc)
    # the 3D model, checked through its camera over frames 24 and 56, and by Khronos's validator
    glb = os.path.join(p3d, 'ts4tnk.glb')
    run([sys.executable, 't4export.py', glb])
    a = Image.open(os.path.join(pkg, 'frames', 'ts4tnk-0024.png')).convert('RGBA')
    a.alpha_composite(Image.open(os.path.join(pkg, 'frames', 'ts4tnk-0056.png')).convert('RGBA'))
    both = os.path.join(HERE, 'logs', 'frames-24-56.png'); a.save(both)
    g = run([sys.executable, 'glbcheck.py', glb, both, os.path.join(HERE, 'logs', 'glbcheck.png'), '512'])
    glb_ov = g.strip().split()[-1]
    val = subprocess.run(['node', VALIDATE, glb], capture_output=True, text=True).stdout.strip().splitlines()[0]
    val = val.replace(' warnings', ', warnings').replace(' infos', ', infos').replace(' hints', ', hints')
    # README
    txt = open(os.path.join(HERE, 'README_v2.txt')).read()
    txt = (txt.replace('VERSION', ver).replace('SHAPE_OVERLAP', shape_ov).replace('FINAL_OVERLAP', final_ov)
           .replace('GLB_OVERLAP', glb_ov).replace('GLB_VALIDATOR', val))
    head = txt.splitlines()[0]
    txt = head + '\n' + '=' * len(head) + '\n' + '\n'.join(txt.splitlines()[2:]) + '\n'
    open(os.path.join(pkg, 'README.txt'), 'w').write(txt)
    i0 = txt.index('3D model (ts-4tnk-hd-3d/ts4tnk.glb)'); i1 = txt.index('Judgement calls')
    t3 = 'ts-4tnk-hd-3d: the 3D model of ts-4tnk-hd (%s)' % ver
    open(os.path.join(p3d, 'README.txt'), 'w').write(t3 + '\n' + '=' * len(t3) + '\n\n' + txt[i0:i1].rstrip() + '\n')
    # src (the absolute path to the shared scripts taken out: they sit next to the unit's own in src/)
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
        s2 = s2.replace("os.environ.get('V1_FRAMES', 'v1/frames') + '/ts4tnk-%04d.png'",
                        "os.environ.get('V1_FRAMES', 'v1/frames') + '/ts4tnk-%04d.png'")
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
    for name in ('ts-4tnk-hd', 'ts-4tnk-hd-3d'):
        out = os.path.join(root, name + '.zip')
        if os.path.exists(out):
            os.remove(out)
        zipdir(root, name, out)
        print(name + '.zip', '%.1f MB' % (os.path.getsize(out) / 1e6))
    print('shape', shape_ov, 'final', final_ov, 'glb', glb_ov, val)
