"""mpkg.py - assemble the Mobile EMP Cannon package from its finished frames: README (the version and the checks' numbers
filled in), previews (vdeliver's, the shape sheet, the close-ups, v1's blast previews), fx/ (v1's blast, unchanged),
src/, the 3D model in its own folder and zip, and the two zips.

    python3 mpkg.py PKG_ROOT version
(PKG_ROOT holds ts-memp-hd/ with frames/ already rendered.)
"""
import os, sys, shutil, subprocess, zipfile, re
import numpy as np
from PIL import Image
from paths import HANDOFF

HERE = os.path.dirname(os.path.abspath(__file__))
VOX = os.path.dirname(os.path.abspath(__file__))
V1PKG = os.environ.get('V1_PKG', 'v1')
SRC = ['rc.py', 'rcrender.py', 'rcexport.py', 'glbtools.py', 'qparts.py', 'mempmodel.py', 'mempmat.py', 'mempcam.py',
       'memprender.py', 'mempspec.py', 'mempexport.py', 'glbcheck.py', 'mempshape.py', 'mempclose.py', 'mvox.py',
       'mdump.py', 'hcls.py', 'frameio.py', 'paths.py', 'mempfx.py', 'mpkg.py', 'mtab.py']
FROM_VOX = ['vdeliver.py', 'vcheck.py']
RENDERER = ['hd.py', 'walls2.py', 'wnoise.py', 'export3d.py', 'vxl.py']
VALIDATE = os.environ.get('VALIDATE', 'validate.js')
CLOSE_FRAMES, CLOSE_CROP = [4, 20], (110, 70, 290, 230)
SLOT_FRAMES = [12, 16, 20, 24]                      # the cockpit slot at 4x (v3 on)

EMITTER_NOTE = ("- The track covers carry Westwood's glowing emitters (Luke): five small pale blue capsules along each "
                "cover's top,\n  on dark bases (Westwood's icon and the render have them; TS's covers are plain).")
JUDGE_EMITTERS = ("- The emitters along the covers (Westwood's icon, the render), five a side on dark bases; TS's covers are "
                  "plain.")


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
    pkg = os.path.join(root, 'ts-memp-hd')
    p3d = os.path.join(root, 'ts-memp-hd-3d')
    pv = os.path.join(pkg, 'previews')
    for d in (p3d, pv, os.path.join(HERE, 'logs')):
        os.makedirs(d, exist_ok=True)
    sys.path.insert(0, VOX)
    import vdeliver, mempspec, mempshape, mempclose
    import mempmodel as T
    # checks on the finished frames (vcheck: every frame and trim; the overlap with the mod's frames moved onto the
    # ground)
    bad, ious = vdeliver.check(mempspec, pkg)
    final_ov = '%.3f' % np.mean(ious)
    print('problems', bad, 'final', final_ov, flush=True)
    # previews: vdeliver's, the shape sheet, the close-ups, v1's blast previews
    vdeliver.previews(mempspec, pkg)
    sc = mempshape.check(list(range(0, 32, 4)), os.path.join(pv, 'shape-8-facings.png'))
    shape_ov = '%.2f' % np.mean(sc)
    mempclose.grid([mempclose.close(k, 3, 2, CLOSE_CROP) for k in CLOSE_FRAMES], ['frame %d' % k for k in CLOSE_FRAMES],
                   os.path.join(pv, 'closeups.png'))
    mempclose.slot_closeups(SLOT_FRAMES, os.path.join(pv, 'slot-closeup.png'))
    for f in ('blast.gif', 'blast-frames.png', 'blast-close.png'):
        shutil.copy(os.path.join(V1PKG, 'previews', f), pv)
    print('previews done', flush=True)
    # the blast: v1's frames, unchanged
    fx = os.path.join(pkg, 'fx')
    if os.path.isdir(fx):
        shutil.rmtree(fx)
    shutil.copytree(os.path.join(V1PKG, 'fx'), fx)
    # the 3D model, checked through its camera over frame 24 and by Khronos's validator
    glb = os.path.join(p3d, 'tsmemp.glb')
    run([sys.executable, 'mempexport.py', glb])
    g = run([sys.executable, 'glbcheck.py', glb, os.path.join(pkg, 'frames', 'tsmemp-0024.png'),
             os.path.join(HERE, 'logs', 'glbcheck.png'), '384'])
    glb_ov = g.strip().split()[-1]
    val = subprocess.run(['node', VALIDATE, glb], capture_output=True, text=True).stdout.strip().splitlines()[0]
    val = val.replace(' warnings', ', warnings').replace(' infos', ', infos').replace(' hints', ', hints')
    # README
    txt = open(os.path.join(HERE, 'README_v2.txt')).read()
    txt = (txt.replace('VERSION', ver).replace('SHAPE_OVERLAP', shape_ov).replace('FINAL_OVERLAP', final_ov)
           .replace('GLB_OVERLAP', glb_ov).replace('GLB_VALIDATOR', val))
    if T.EMITTERS:
        txt = txt.replace('EMITTER_NOTE', EMITTER_NOTE).replace('JUDGE_EMITTERS', JUDGE_EMITTERS)
    else:
        txt = txt.replace('EMITTER_NOTE\n', '').replace('JUDGE_EMITTERS\n', '')
    head = txt.splitlines()[0]
    txt = head + '\n' + '=' * len(head) + '\n' + '\n'.join(txt.splitlines()[2:]) + '\n'
    open(os.path.join(pkg, 'README.txt'), 'w').write(txt)
    i0 = txt.index('3D model (ts-memp-hd-3d/tsmemp.glb)'); i1 = txt.index('Judgement calls')
    t3 = 'ts-memp-hd-3d: the 3D model of ts-memp-hd (%s)' % ver
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
        s2 = s2.replace("V1PKG = os.environ.get('V1_PKG', 'v1')", "V1PKG = os.environ.get('V1_PKG', 'v1')")
        s2 = s2.replace("os.environ.get('V1_PKG', 'v1') + '/frames/tsmemp-%04d.png'",
                        "os.environ.get('V1_PKG', 'v1') + '/frames/tsmemp-%04d.png'")
        s2 = s2.replace("os.environ.get('REVIEW', 'units-review')", "os.environ.get('REVIEW', 'units-review')")
        s2 = s2.replace("os.environ.get('PREV_PKG', 'v2') + '/frames/tsmemp-%04d.png'",
                        "os.environ.get('PREV_PKG', 'v2') + '/frames/tsmemp-%04d.png'")
        s2 = s2.replace("VOX = os.path.dirname(os.path.abspath(__file__))", "VOX = os.path.dirname(os.path.abspath(__file__))")
        s2 = s2.replace("VALIDATE = os.environ.get('VALIDATE', 'validate.js')",
                        "VALIDATE = os.environ.get('VALIDATE', 'validate.js')")
        s2 = s2.replace("os.environ.get('REVIEW', 'units-review') + '/'", "os.environ.get('REVIEW', 'units-review') + '/'")
        for qt in ('"', "'"):
            s2 = s2.replace('sys.path.insert(0, %s/home/claude/units/ts-units-hd-handoff/renderer%s)' % (qt, qt),
                            'sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))')
        if s2 != s:
            if not re.search(r'^import [^\n]*\bos\b', s2, re.M) and 'os.' in s2:
                if re.search(r'^import sys\n', s2, re.M):
                    s2 = re.sub(r'^import sys\n', 'import os, sys\n', s2, count=1, flags=re.M)
                else:
                    s2 = re.sub(r'^(import [^\n]+\n)', r'import os\n\1', s2, count=1, flags=re.M)
            open(p, 'w').write(s2)
    left = [f for f in os.listdir(src) if '/home/claude' in open(os.path.join(src, f)).read()]
    print('src files still naming /home/claude:', left)
    for name in ('ts-memp-hd', 'ts-memp-hd-3d'):
        out = os.path.join(root, name + '.zip')
        if os.path.exists(out):
            os.remove(out)
        zipdir(root, name, out)
        print(name + '.zip', '%.1f MB' % (os.path.getsize(out) / 1e6))
    print('shape', shape_ov, 'final', final_ov, 'glb', glb_ov, val)
