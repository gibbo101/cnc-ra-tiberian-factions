"""Turned RA-grid previews of the refinery: the building with a docked HARV, and its bib, on the 736x928 canvas,
the foundation centred on the plot centre and its nearest corner on the plot's south edge.
    python3 procyaw.py <yaw> <scale> <shift_x> <ss> <out>"""
import sys, numpy as np
from PIL import Image
import hd, proc as PR, procrender as PRR, harv as HV

yaw, scale, shift, ss, out = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
oy_set = float(sys.argv[6]) if len(sys.argv) > 6 else None
th = np.deg2rad(yaw)
T = (np.sin(th), np.cos(th))
W, H = PRR.CANVAS
x0, y0, x1, y1 = PRR.PLOT
near = np.sin(np.deg2rad(32.0)) * (abs(T[0]) * 256.0 + abs(T[1]) * 192.0)
origin = ((x0 + x1) / 2.0 + shift, y1 - scale * near if oy_set is None else oy_set)
v = hd.View((-T[0], -T[1]), 32.0, scale, (W, H), origin, margin=(64, 64), ss=ss)
import os
notruck = os.environ.get('NOTRUCK') == '1'
pr = PRR.ProcPrep(PRR.BLD, v, vname='ra', **({} if notruck else dict(truck=PR.truck_args('ra', False, HV))))
img = pr.frame(want_trim=False, lights=0)
img = img[0] if isinstance(img, tuple) else img
img.save(f'{out}-building.png')
del pr
pb = PRR.ProcPrep(PRR.BLD, v, vname='ra', pad=True)
col, tm = pb.shade()
pb.r.compose(col, ground=False, outline=False).save(f'{out}-bib.png')
a = np.asarray(img).astype(int)
solid = (a[..., 3] >= 235) & (a[..., :3].max(axis=2) >= 30)
ys, xs = np.nonzero(solid)
gx, gy = v.project(np.array(PR.DOCK['ra']['pos'][0]), np.array(PR.DOCK['ra']['pos'][1]), np.array(0.0))
print('dock ground point', float(gx), float(gy), 'origin', origin)
print(yaw, scale, shift, 'solid x', xs.min(), xs.max() + 1, 'y', ys.min(), ys.max() + 1, '(plot x 112-624, y 272-656)', flush=True)
