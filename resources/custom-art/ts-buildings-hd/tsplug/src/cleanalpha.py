"""Clear the faint ground haze from a package's frames: pixels with alpha below a threshold (default 8 of 255, ~3%)
go fully transparent (and out of the trim).  The renderer's ground shadow test leaves a 1-3% veil over the whole
render window in the RA view: invisible in game, but it stretches every frame's bounding box to the window.

    python3 cleanalpha.py <package dir> [threshold 8]"""
import os, sys
import numpy as np
from PIL import Image


def clean(path, thr=8):
    im = Image.open(path)
    if im.mode != 'RGBA':
        return 0
    a = np.array(im)
    m = (a[..., 3] > 0) & (a[..., 3] < thr)
    n = int(m.sum())
    if n:
        a[m] = 0
        Image.fromarray(a, 'RGBA').save(path)
        tp = path[:-4] + '-trim.png'
        if os.path.exists(tp):
            t = np.array(Image.open(tp).convert('L'))
            t[m] = 0
            Image.fromarray(t, 'L').save(tp)
    return n


if __name__ == '__main__':
    root = sys.argv[1]
    thr = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    tot, nf = 0, 0
    for dp, _, fs in os.walk(root):
        if '/previews' in dp or '/src' in dp or '/3d' in dp:
            continue
        for f in sorted(fs):
            if f.endswith('.png') and not f.endswith('-trim.png'):
                n = clean(os.path.join(dp, f), thr)
                tot += n; nf += n > 0
    print(f'cleared {tot} faint px in {nf} frames')
