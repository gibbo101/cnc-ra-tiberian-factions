"""place the Hunter-Seeker as the mod has it: the origin (the body's bottom on the axis) by alpha overlap with in-mod frame
4 (its sprite is TS's x 4 at (46, 108)).  -> place.json"""
import json, sys
import numpy as np
from PIL import Image
import hsrender as R
from paths import HANDOFF

INMOD = HANDOFF + '/16-TSHUNT/in-mod/tshunt/frames/tshunt-%04d.png'
js = json.load(open(R.FIT))
P = R.load()
o0 = np.array([46 + 4 * js['ax'], 108 + 4 * js['y0']])
tgt = np.asarray(Image.open(INMOD % 4))[..., 3] > 127
best = None
for dx in np.arange(-4, 4.01, 1.0):
    for dy in np.arange(-6, 6.01, 1.0):
        img, _ = R.render(P, 4, (o0[0] + dx, o0[1] + dy), ss=1, sky=False)
        m = np.asarray(img)[..., 3] > 127
        s = (m & tgt).sum() / (m | tgt).sum()
        if best is None or s > best[0]:
            best = (s, dx, dy)
s, bx, by = best
for dx in np.arange(bx - 0.75, bx + 0.76, 0.25):
    for dy in np.arange(by - 0.75, by + 0.76, 0.25):
        img, _ = R.render(P, 4, (o0[0] + dx, o0[1] + dy), ss=2, sky=False)
        m = np.asarray(img)[..., 3] > 127
        s2 = (m & tgt).sum() / (m | tgt).sum()
        if s2 > best[0]:
            best = (s2, dx, dy)
s, bx, by = best
origin = [float(o0[0] + bx), float(o0[1] + by)]
print('origin', origin, 'overlap %.3f' % s)
json.dump(dict(origin=origin, overlap=float(s)), open('place.json', 'w'), indent=1)
