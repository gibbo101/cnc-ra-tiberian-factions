"""final frames for the Titan into PKG/frames/: tstitn-0000..0127.png with -trim.png, at x4 supersampling with
sky occlusion.

    python3 finalrender.py part_index n_parts
"""
import os, sys, time
import titanrender as TR, titan as TN
from frameio import save

PKG = os.environ.get('PKG', __import__('os').path.join(__import__('paths').HERE, '..'))

if __name__ == '__main__':
    part, n = int(sys.argv[1]), int(sys.argv[2])
    order = list(range(96, 128)) + list(range(0, 96))
    mine = order[part::n]
    S, poses = TN.load_legs(); P = TN.load_torso()
    os.makedirs(f'{PKG}/frames', exist_ok=True)
    for k in mine:
        out = f'{PKG}/frames/tstitn-{k:04d}.png'
        if os.path.exists(out) and os.path.exists(out[:-4] + '-trim.png'):
            continue
        t0 = time.time()
        if k < 96:
            img, trim = TR.leg_frame(k, ss=4, S=S, poses=poses, P=P, sky=True)
        else:
            img, trim = TR.torso_frame(k, ss=4, S=S, P=P, sky=True)
        save(img, trim, out)
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
    print('done', flush=True)
