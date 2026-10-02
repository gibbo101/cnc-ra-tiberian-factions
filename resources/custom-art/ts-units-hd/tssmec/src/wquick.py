"""quick preview frames of the Wolverine (for the shape check's sheets and GIFs): every walk step and firing step for
some facings, plus walk step 0 for all 8.

    python3 wquick.py model.json out_dir facings(e.g. 6,4,5,1) [ss] [sky 0/1]
"""
import os, sys, time
import wolfhd as WH, wolfrender as WR
from frameio import save

if __name__ == '__main__':
    model = WH.load(sys.argv[1]); out = sys.argv[2]
    fs = [int(a) for a in sys.argv[3].split(',')]
    ss = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    sky = bool(int(sys.argv[5])) if len(sys.argv) > 5 else True
    os.makedirs(out, exist_ok=True)
    ks = sorted(set([f * 12 for f in range(8)] + [f * 12 + s for f in fs for s in range(12)] +
                    [96 + f * 4 + s for f in fs for s in range(4)]))
    t0 = time.time()
    for k in ks:
        img, trim = WR.frame(k, model, ss, sky=sky)
        save(img, trim, f'{out}/tssmec-{k:04d}.png')
    print('%d frames %.0fs' % (len(ks), time.time() - t0), flush=True)
