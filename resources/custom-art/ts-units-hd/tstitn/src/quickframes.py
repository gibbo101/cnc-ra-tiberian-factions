"""render quick preview frames of the Titan (legs for some facings x 12 steps, the upper body for the same
facings) into a folder, for the shape check GIFs and sheets.

    python3 quickframes.py out_dir facings(e.g. 6,3) [ss] [sky 0/1]
"""
import os, sys, time
import titanrender as TR, titan as TN
from frameio import save

if __name__ == '__main__':
    out = sys.argv[1]; f8s = [int(a) for a in sys.argv[2].split(',')]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    sky = bool(int(sys.argv[4])) if len(sys.argv) > 4 else False
    steps = [int(a) for a in sys.argv[5].split(',')] if len(sys.argv) > 5 else range(12)
    os.makedirs(out, exist_ok=True)
    S, poses = TN.load_legs(); P = TN.load_torso()
    for f8 in f8s:
        t0 = time.time()
        img, trim = TR.torso_frame(96 + f8 * 4, ss=ss, S=S, P=P, sky=sky)
        save(img, trim, f'{out}/tstitn-{96 + f8 * 4:04d}.png')
        for st in steps:
            k = f8 * 12 + st
            img, trim = TR.leg_frame(k, ss=ss, S=S, poses=poses, P=P, sky=sky)
            save(img, trim, f'{out}/tstitn-{k:04d}.png')
        print('facing', f8, '%.0fs' % (time.time() - t0), flush=True)
