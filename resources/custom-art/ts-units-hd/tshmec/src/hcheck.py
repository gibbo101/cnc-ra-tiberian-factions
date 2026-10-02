"""check the Mk. II's finished frames: all 256 with trims on the 576 canvas, trims only on house green, the house
colour pure green, the shadow at alpha 191 (>= 128), and the frames against the mod's (silhouette overlap, top and
bottom of the unit).

    python3 hcheck.py PKG
"""
import os, sys
import numpy as np
from PIL import Image
from paths import HANDOFF

INMOD = HANDOFF + '/03-TSHMEC/in-mod/tshmec/frames/tshmec-%04d.png'

if __name__ == '__main__':
    pkg = sys.argv[1]
    fmt = pkg + '/frames/tshmec-%04d.png'
    bad = []; ious = []; dlow = []; dtop = []
    for k in range(256):
        p = fmt % k; t = p[:-4] + '-trim.png'
        if not (os.path.exists(p) and os.path.exists(t)):
            bad.append((k, 'missing')); continue
        a = np.array(Image.open(p).convert('RGBA')).astype(int); tr = np.array(Image.open(t))
        if a.shape != (576, 576, 4) or tr.shape != (576, 576):
            bad.append((k, 'size'))
        full = (tr == 255) & (a[..., 3] == 255)
        if full.any() and (a[full][:, 0].max() > 0 or a[full][:, 2].max() > 0):
            bad.append((k, 'house not pure green'))
        if ((tr > 0) & (a[..., 3] < 128)).any():
            bad.append((k, 'trim outside the unit'))
        dark = (a[..., :3].max(-1) < 8) & (a[..., 3] > 0)
        if not dark.any() or a[..., 3][dark].max() < 128:
            bad.append((k, 'shadow alpha'))
        b = np.array(Image.open(INMOD % k).convert('RGBA')).astype(int)
        sa = a[..., 3] > 250; sb = b[..., 3] > 250
        ious.append((sa & sb).sum() / max((sa | sb).sum(), 1))
        ya = np.nonzero(sa.any(1))[0]; yb = np.nonzero(sb.any(1))[0]
        dlow.append(ya.max() - yb.max()); dtop.append(ya.min() - yb.min())
    print('frames checked: 256;  problems:', bad[:20] if bad else 'none', '(%d)' % len(bad))
    print('silhouette overlap with the mod\'s frames: mean %.3f (min %.3f, max %.3f)' % (np.mean(ious), min(ious), max(ious)))
    print('lowest solid pixel, HD minus in-mod: mean %.1f (min %d, max %d)' % (np.mean(dlow), min(dlow), max(dlow)))
    print('highest solid pixel, HD minus in-mod: mean %.1f (min %d, max %d)' % (np.mean(dtop), min(dtop), max(dtop)))
