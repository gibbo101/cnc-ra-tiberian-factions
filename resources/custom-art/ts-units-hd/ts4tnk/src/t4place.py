import sys
import os
from paths import HANDOFF
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, vxl, vplace as VP
D = HANDOFF + '/05-TS4TNK/'
def pts(name):
    out = []
    secs = vxl.read_vxl(D + 'ts-original/%s.VXL' % name); n, m = vxl.read_hva(D + 'ts-original/%s.HVA' % name)
    for i, s in enumerate(secs):
        v = np.argwhere(s['col'] >= 0).astype(float)
        sc = (np.asarray(s['max']) - np.asarray(s['min'])) / np.asarray(s['size'], float)
        R = m[0, i][:, :3]; t = m[0, i][:, 3] * s['det']
        out.append((np.asarray(s['min']) + (v + 0.5) * sc) @ R.T + t)
    return np.concatenate(out)
hull = pts('4TNK'); tur = np.concatenate([pts('4TNKTUR'), pts('4TNKBARL')])
INM = D + 'in-mod/ts4tnk/frames/ts4tnk-%04d.png'
el = float(sys.argv[1]) if len(sys.argv) > 1 else 32.0
data = [VP.world(hull, f) + (VP.opaque(INM % f),) for f in (0, 8, 16, 24)]
print('hull est', VP.estimate(data, el)); print('hull', VP.fit(data, (512, 512), el))
data = [VP.world(tur, f) + (VP.opaque(INM % (32 + f)),) for f in (0, 8, 16, 24)]
print('turret est', VP.estimate(data, el)); print('turret', VP.fit(data, (512, 512), el))
