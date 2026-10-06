"""
jfinal.py - the Juggernaut's 202 HD frames for the mod (TSJUGG, 448 x 448), each with its -trim.png:
    0-119    the walk on the Titan's legs (jtrender.py): frame = mod facing x 15 + step
    120-151  deployed at rest (jdeprender.py), 32 facings counter-clockwise from north
    152-183  deployed and aiming
    184-201  the deploy (jdeploy.py); 184 is walk frame 45 and 201 is rest frame 132, copied, so they match exactly

    PKG=out python3 jfinal.py PART N [ss] [sky]      renders every N-th frame from PART (skips frames already there)
    PKG=out python3 jfinal.py copies                 writes 184 and 201 from 45 and 132
"""
import os, shutil, sys, time
from frameio import save

NAME = 'tsjugg'
HERE = os.path.dirname(os.path.abspath(__file__))
COPIES = {184: 45, 201: 132}


def out_path(pkg, k):
    return '%s/frames/%s-%04d.png' % (pkg, NAME, k)


def render(pkg, part, n, ss=4, sky=True):
    os.makedirs(pkg + '/frames', exist_ok=True)
    todo = [k for k in range(202) if k not in COPIES][part::n]
    walk = dep = deploy = None
    for k in todo:
        out = out_path(pkg, k)
        if os.path.exists(out) and os.path.exists(out[:-4] + '-trim.png'):
            continue
        t0 = time.time()
        if k < 120:
            import jtrender as JT
            walk = walk or JT.load()
            img, trim = JT.frame(k, walk, ss, sky)
        elif k < 184:
            import jdeprender as DR
            dep = dep or DR.load()
            img, trim = DR.frame(k, dep, ss, sky)
        else:
            import jdeploy as JD
            deploy = deploy or JD.setup()
            img, trim = JD.frame(k, deploy, ss, sky)
        save(img, trim, out)
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
    print('done', flush=True)


def copies(pkg):
    for k, src in COPIES.items():
        for suf in ('.png', '-trim.png'):
            shutil.copy(out_path(pkg, src)[:-4] + suf, out_path(pkg, k)[:-4] + suf)
    print('copied', COPIES)


if __name__ == '__main__':
    pkg = os.environ['PKG']
    if sys.argv[1] == 'copies':
        copies(pkg)
    else:
        render(pkg, int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 4,
               bool(int(sys.argv[4])) if len(sys.argv) > 4 else True)
