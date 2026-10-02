"""check a voxel unit's finished frames: every frame and trim on the canvas, trims only on house green, the house
colour pure green, the shadow at alpha 191 (>= 128) where the frame carries one, and the frames against the mod's
(silhouette overlap of the opaque pixels, top and bottom of the unit).

    python3 vcheck.py PKG_FRAMES_PATTERN INMOD_PATTERN N_FRAMES W H [no-shadow frames: a-b,c-d]
"""
import os, sys
import numpy as np
from PIL import Image


def _shifted(m, dx, dy):
    """a mask moved by whole pixels (dx right, dy down), empty where it moved in from outside."""
    out = np.zeros_like(m)
    H, W = m.shape
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    out[yd, xd] = m[ys, xs]
    return out


def check(fmt, inmod, n, size, no_shadow=(), shift=(0, 0)):
    """shift: (dx, dy) whole canvas px the HD frames are drawn from in-mod/'s place on purpose (in-mod/ is moved by it
    before comparing)."""
    bad = []; ious = []; dlow = []; dtop = []
    for k in range(n):
        p = fmt % k; t = p[:-4] + '-trim.png'
        if not (os.path.exists(p) and os.path.exists(t)):
            bad.append((k, 'missing')); continue
        a = np.array(Image.open(p).convert('RGBA')).astype(int); tr = np.array(Image.open(t))
        if a.shape != (size[1], size[0], 4) or tr.shape != (size[1], size[0]):
            bad.append((k, 'size'))
        full = (tr == 255) & (a[..., 3] == 255)
        if full.any() and (a[full][:, 0].max() > 0 or a[full][:, 2].max() > 0):
            bad.append((k, 'house not pure green'))
        if ((tr > 0) & (a[..., 3] < 128)).any():
            bad.append((k, 'trim outside the unit'))
        dark = (a[..., :3].max(-1) < 8) & (a[..., 3] > 0) & (a[..., 3] < 250)
        if k not in no_shadow:
            if not dark.any() or a[..., 3][dark].max() < 128:
                bad.append((k, 'shadow alpha'))
        elif (dark & (a[..., 3] > 160)).sum() > 50:
            bad.append((k, 'shadow on a no-shadow frame'))
        if inmod:
            b = np.array(Image.open(inmod % k).convert('RGBA')).astype(int)
            sa = a[..., 3] > 250; sb = _shifted(b[..., 3] > 250, int(shift[0]), int(shift[1]))
            if sa.any() and sb.any():
                ious.append((sa & sb).sum() / max((sa | sb).sum(), 1))
                ya = np.nonzero(sa.any(1))[0]; yb = np.nonzero(sb.any(1))[0]
                dlow.append(ya.max() - yb.max()); dtop.append(ya.min() - yb.min())
    print('frames checked: %d;  problems:' % n, bad[:20] if bad else 'none', '(%d)' % len(bad))
    if ious:
        print('silhouette overlap with the mod\'s frames: mean %.3f (min %.3f, max %.3f)' % (np.mean(ious), min(ious), max(ious)))
        print('lowest solid pixel, HD minus in-mod: mean %.1f (min %d, max %d)' % (np.mean(dlow), min(dlow), max(dlow)))
        print('highest solid pixel, HD minus in-mod: mean %.1f (min %d, max %d)' % (np.mean(dtop), min(dtop), max(dtop)))
    return bad, ious


if __name__ == '__main__':
    fmt, inmod, n, W, H = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    ns = set()
    if len(sys.argv) > 6:
        for r in sys.argv[6].split(','):
            a, b = r.split('-'); ns |= set(range(int(a), int(b) + 1))
    check(fmt, inmod, n, (W, H), ns)
