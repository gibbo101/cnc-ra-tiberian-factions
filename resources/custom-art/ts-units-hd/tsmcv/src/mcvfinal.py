"""render the MCV's 32 frames into PKG/frames/: tsmcv-0000..0031.png with -trim.png (x4 supersampling, sky
occlusion).  Frames already there are skipped, so two processes can share the work.

    python3 mcvfinal.py part_index n_parts [ss] [sky 0/1]      (PKG= sets the package folder)
"""
import os, sys, time
import mcvrender as MR
from frameio import save

PKG = os.environ.get('PKG', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

if __name__ == '__main__':
    part, n = int(sys.argv[1]), int(sys.argv[2])
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    sky = bool(int(sys.argv[4])) if len(sys.argv) > 4 else True
    os.makedirs(f'{PKG}/frames', exist_ok=True)
    for k in list(range(32))[part::n]:
        out = f'{PKG}/frames/tsmcv-{k:04d}.png'
        if os.path.exists(out) and os.path.exists(out[:-4] + '-trim.png'):
            continue
        t0 = time.time()
        img, trim = MR.frame(k, ss=ss, sky=sky)
        save(img, trim, out)
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
    print('done', flush=True)
