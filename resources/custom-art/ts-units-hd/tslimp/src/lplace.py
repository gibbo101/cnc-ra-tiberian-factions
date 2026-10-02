"""place the Limpet's frames as the mod has them: the drone frames by alpha overlap with in-mod frame 0 (the origin, the
ground point under the drone's axis), the shadow frames by overlap with in-mod frame 10 (a shift).  -> place.json"""
import json, sys
import numpy as np
from PIL import Image
import lrender as R
from paths import HANDOFF

INMOD = HANDOFF + '/15-TSLIMP/in-mod/tslimp/frames/tslimp-%04d.png'


def alpha(img, thr):
    return np.asarray(img)[..., 3] > thr


def iou(a, b):
    return (a & b).sum() / max((a | b).sum(), 1)


P = R.load()
tip = (48.0 * 6.2 - 211.85, 32.35 * 6.2 - 65.35)
o0 = np.array([tip[0], tip[1] + R.HOVER * np.cos(np.deg2rad(32)) * R.PPU])
tgt = alpha(Image.open(INMOD % 0), 127)
best = None
for dx in np.arange(-3, 3.01, 1.0):
    for dy in np.arange(-6, 6.01, 1.0):
        img, _ = R.render(P, 0, (o0[0] + dx, o0[1] + dy), ss=1, sky=False)
        s = iou(alpha(img, 127), tgt)
        if best is None or s > best[0]:
            best = (s, dx, dy)
s, bx, by = best
for dx in np.arange(bx - 0.75, bx + 0.76, 0.25):
    for dy in np.arange(by - 0.75, by + 0.76, 0.25):
        img, _ = R.render(P, 0, (o0[0] + dx, o0[1] + dy), ss=2, sky=False)
        s = iou(alpha(img, 127), tgt)
        if s > best[0]:
            best = (s, dx, dy)
s, bx, by = best
origin = [float(o0[0] + bx), float(o0[1] + by)]
print('drone: origin', origin, 'overlap %.3f' % s)
sh, _ = R.render(P, 0, origin, ss=2, sky=False, shadow_only=True)
a = alpha(sh, 40); t = alpha(Image.open(INMOD % 10), 40)
best = None
for dx in range(-40, 41):
    for dy in range(-40, 41):
        s2 = iou(np.roll(np.roll(a, dy, 0), dx, 1), t)
        if best is None or s2 > best[0]:
            best = (s2, dx, dy)
print('shadow: shift', best[1:], 'overlap %.3f' % best[0])
json.dump(dict(origin=origin, drone_overlap=float(s), shadow_shift=[best[1], best[2]], shadow_overlap=float(best[0])),
          open('place.json', 'w'), indent=1)
