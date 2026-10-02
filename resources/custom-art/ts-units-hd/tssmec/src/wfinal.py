"""render the Wolverine's frames into PKG/frames/: tssmec-0000..0127.png with -trim.png (x4 supersampling, sky
occlusion).  Frames already there are skipped, so two processes can share the work.

    python3 wfinal.py part_index n_parts [ss] [sky 0/1]      (PKG= sets the package folder, MODEL= the model)
"""
import os, sys, time
import wolfhd as WH, wolfrender as WR
from frameio import save

PKG = os.environ.get('PKG', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

if __name__ == '__main__':
    part, n = int(sys.argv[1]), int(sys.argv[2])
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    sky = bool(int(sys.argv[4])) if len(sys.argv) > 4 else True
    model = WH.load(os.environ['MODEL']) if 'MODEL' in os.environ else WH.load()
    order = list(range(128))
    mine = order[part::n]
    os.makedirs(f'{PKG}/frames', exist_ok=True)
    for k in mine:
        out = f'{PKG}/frames/tssmec-{k:04d}.png'
        if os.path.exists(out) and os.path.exists(out[:-4] + '-trim.png'):
            continue
        t0 = time.time()
        img, trim = WR.frame(k, model, ss=ss, sky=sky)
        save(img, trim, out)
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
    print('done', flush=True)
