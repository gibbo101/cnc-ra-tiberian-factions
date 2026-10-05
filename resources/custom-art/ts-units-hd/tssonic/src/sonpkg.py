"""sonpkg.py - assemble the Disruptor package from its finished frames: README (the version and the checks' numbers
filled in), previews (vdeliver's, the shape sheet, the arm's and the viewport's close-ups), src/, the 3D model in its own
folder and zip, and the two zips.

    python3 sonpkg.py PKG_ROOT version
(PKG_ROOT holds ts-sonic-hd/ with frames/ already rendered.)
"""
import os, sys, shutil, subprocess, zipfile, re
import numpy as np
from PIL import Image, ImageDraw
from paths import HANDOFF

HERE = os.path.dirname(os.path.abspath(__file__))
VOX = os.path.dirname(os.path.abspath(__file__))
SRC = ['rc.py', 'rcrender.py', 'rcexport.py', 'glbtools.py', 'qparts.py', 'sonmodel.py', 'sonmat.py', 'soncam.py',
       'sonrender.py', 'sonspec.py', 'sonexport.py', 'glbcheck.py', 'sonshape.py', 'sonvcomp.py', 'svox.py', 'vdump.py',
       'sonlook.py', 'sonclose.py', 'hcls.py', 'frameio.py', 'paths.py', 'sonpkg.py', 'sontab.py']
FROM_VOX = ['vdeliver.py', 'vcheck.py']
RENDERER = ['hd.py', 'walls2.py', 'wnoise.py', 'export3d.py', 'vxl.py']
VALIDATE = os.environ.get('VALIDATE', 'validate.js')
ARM_FRAMES = [44, 48, 52, 56]
VIEWPORT_FACINGS = [12, 16, 20, 24]


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
    import sonclose as C
    w, h = tiles[0].size
    S = Image.new('RGB', (cols * (w + 6) - 6, ((len(tiles) + cols - 1) // cols) * (h + 6) - 6), (30, 30, 30))
    d = ImageDraw.Draw(S)
    for i, (t, lab) in enumerate(zip(tiles, labels)):
        S.paste(t, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
        d.text(((i % cols) * (w + 6) + 6, (i // cols) * (h + 6) + 4), lab, font=C.FONT, fill=(240, 230, 180))
    S.save(out)


def closeups(pv):
    """the arm (turret frames) and the ochre box's viewport (hull frames) at 4x, from the model with the frames' look."""
    import sonclose as C, sonmodel as T
    from soncam import camera, unit_to_world, GZ
    grid([C.close(k, 4, 2, (165, 100, 315, 200)) for k in ARM_FRAMES], ['frame %d' % k for k in ARM_FRAMES],
         pv + '/arm-closeup.png')
    tiles = []
    for f in VIEWPORT_FACINGS:
        R, t = T.FH.pose(); t = t + np.array([0, 0, -GZ])
        sx, sy = camera(False).project(unit_to_world(f) @ (R @ T.FH.p((38.0, 17.0, 9.0)) + t))
        tiles.append(C.close(f, 4, 2, (int(sx - 44), int(sy - 36), int(sx + 44), int(sy + 30))))
    grid(tiles, ['frame %d' % f for f in VIEWPORT_FACINGS], pv + '/viewport-closeup.png')


if __name__ == '__main__':
    root, ver = sys.argv[1], sys.argv[2]
    pkg = os.path.join(root, 'ts-sonic-hd')
    p3d = os.path.join(root, 'ts-sonic-hd-3d')
    os.makedirs(p3d, exist_ok=True)
    os.makedirs(os.path.join(HERE, 'logs'), exist_ok=True)
    # checks on the finished frames
    chk = run([sys.executable, os.path.join(VOX, 'vdeliver.py'), 'sonspec', 'check', pkg])
    print(chk, flush=True)
    final_ov = re.search(r"mod's frames: mean ([0-9.]+)", chk).group(1)
    # previews, the shape sheet (hull and turret, every 4th facing) and the close-ups
    print(run([sys.executable, os.path.join(VOX, 'vdeliver.py'), 'sonspec', 'previews', pkg]), flush=True)
    import sonshape
    sc = sonshape.check(list(range(0, 64, 4)), os.path.join(pkg, 'previews', 'shape-8-facings.png'))
    shape_ov = '%.2f' % np.mean(sc)
    closeups(os.path.join(pkg, 'previews'))
    print('close-ups done', flush=True)
    # the 3D model, checked through its camera over hull frame 24 with turret frame 56 seated, and by Khronos's validator
    glb = os.path.join(p3d, 'tssonic.glb')
    run([sys.executable, 'sonexport.py', glb])
    sys.path.insert(0, VOX)
    import sonspec
    from vdeliver import layered
    k, dx, dy = sonspec.seat(24)
    seated = os.path.join(HERE, 'logs', 'seated24.png')
    layered(os.path.join(pkg, 'frames', 'tssonic-%04d.png'), [24, (k, dx, dy)]).save(seated)
    g = run([sys.executable, 'glbcheck.py', glb, seated, os.path.join(HERE, 'logs', 'glbcheck.png'), '448'])
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
    i0 = txt.index('3D model (ts-sonic-hd-3d/tssonic.glb)'); i1 = txt.index('Judgement calls')
    t3 = 'ts-sonic-hd-3d: the 3D model of ts-sonic-hd (%s)' % ver
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
        s2 = s2.replace("os.environ.get('V1_FRAMES', 'v1/frames') + '/tssonic-%04d.png'",
                        "os.environ.get('V1_FRAMES', 'v1/frames') + '/tssonic-%04d.png'")
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
    for name in ('ts-sonic-hd', 'ts-sonic-hd-3d'):
        out = os.path.join(root, name + '.zip')
        if os.path.exists(out):
            os.remove(out)
        zipdir(root, name, out)
        print(name + '.zip', '%.1f MB' % (os.path.getsize(out) / 1e6))
    print('shape', shape_ov, 'final', final_ov, 'glb', glb_ov, val)
