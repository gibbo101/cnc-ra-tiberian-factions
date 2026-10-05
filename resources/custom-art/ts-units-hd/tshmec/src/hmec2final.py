"""render the Mk. II's 256 frames into PKG/frames/: tshmec-0000..0255.png with -trim.png (x4 supersampling, sky
occlusion).  Frames already there are skipped, so two processes can share the work.

    python3 hmec2final.py part_index n_parts [ss] [sky 0/1]      (PKG= sets the package folder)
"""
import os, sys, time
import hmec2render as HR
from frameio import save

PKG = os.environ.get('PKG', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pkg', 'ts-hmec-hd'))

if __name__ == '__main__':
    part, n = int(sys.argv[1]), int(sys.argv[2])
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    sky = bool(int(sys.argv[4])) if len(sys.argv) > 4 else True
    os.makedirs(f'{PKG}/frames', exist_ok=True)
    for k in list(range(256))[part::n]:
        out = f'{PKG}/frames/tshmec-{k:04d}.png'
        if os.path.exists(out) and os.path.exists(out[:-4] + '-trim.png'):
            continue
        t0 = time.time()
        img, trim = HR.frame(k, ss=ss, sky=sky)
        save(img, trim, out)
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
    print('done', flush=True)
