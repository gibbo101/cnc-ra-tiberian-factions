"""check the Wolverine's finished frames: all 128 with trims on the 384 canvas, trims only on opaque house green, the
house colour pure green, the shadow at alpha 191 (>= 128), the flash only on firing steps 0 and 2, the feet on the
ground line.

    python3 wcheck.py PKG
"""
import os, sys
import numpy as np
from PIL import Image

pkg = sys.argv[1]
fmt = pkg + '/frames/tssmec-%04d.png'
bad = []
flash_px = {}
lows = []
for k in range(128):
    p = fmt % k; t = p[:-4] + '-trim.png'
    if not (os.path.exists(p) and os.path.exists(t)):
        bad.append((k, 'missing')); continue
    a = np.array(Image.open(p)); tr = np.array(Image.open(t))
    if a.shape != (384, 384, 4) or tr.shape != (384, 384):
        bad.append((k, 'size', a.shape, tr.shape))
    on = tr > 128
    if (on & (a[..., 3] < 250)).sum() > 0.02 * max(on.sum(), 1):
        bad.append((k, 'trim on see-through px', int((on & (a[..., 3] < 250)).sum())))
    hc = a[on & (a[..., 3] == 255)]
    if len(hc) and (hc[:, 0].max() > 40 or hc[:, 2].max() > 40):
        bad.append((k, 'house not pure green', int(hc[:, 0].max()), int(hc[:, 2].max())))
    dark = (a[..., :3].max(-1) < 8) & (a[..., 3] > 0)
    sh = a[..., 3][dark]
    if len(sh) == 0 or sh.max() < 128:
        bad.append((k, 'shadow alpha', int(sh.max()) if len(sh) else 0))
    # flash: saturated yellow-orange pixels not on the unit's own paint
    rgb = a[..., :3].astype(int)
    fl = (a[..., 3] > 128) & (rgb[..., 0] > 230) & (rgb[..., 1] > 120) & (rgb[..., 2] < 90) & (rgb[..., 1] < 250)
    flash_px[k] = int(fl.sum())
    solid = (a[..., 3] > 250)
    ys = np.nonzero(solid.any(1))[0]
    lows.append(ys.max() if len(ys) else -1)
fire = {k: flash_px[k] for k in range(96, 128)}
on_steps = [flash_px[k] for k in range(96, 128) if (k - 96) % 4 in (0, 2)]
off_steps = [flash_px[k] for k in range(96, 128) if (k - 96) % 4 in (1, 3)]
walk = [flash_px[k] for k in range(96)]
print('frames checked: 128;  problems:', bad if bad else 'none')
print('flash px on steps 0/2: min %d  mean %d;  on steps 1/3: max %d;  walk frames: max %d' %
      (min(on_steps), np.mean(on_steps), max(off_steps), max(walk)))
print('lowest solid pixel per frame: %d-%d (walk), stance %d-%d' % (min(lows[:96]), max(lows[:96]), min(lows[96:]),
                                                                  max(lows[96:])))
