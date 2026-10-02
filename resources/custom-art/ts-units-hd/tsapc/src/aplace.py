import sys
import os
from paths import HANDOFF
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, vxl, vplace as VP
D = HANDOFF + '/06-TSAPC/'
def pts(name):
    out = []
    secs = vxl.read_vxl(D + 'ts-original/%s.VXL' % name); n, m = vxl.read_hva(D + 'ts-original/%s.HVA' % name)
    for i, s in enumerate(secs):
        v = np.argwhere(s['col'] >= 0).astype(float)
        sc = (np.asarray(s['max']) - np.asarray(s['min'])) / np.asarray(s['size'], float)
        R = m[0, i][:, :3]; t = m[0, i][:, 3] * s['det']
        out.append((np.asarray(s['min']) + (v + 0.5) * sc) @ R.T + t)
        print(name, s['name'], s['size'], 'z range', round(out[-1][:, 2].min(), 2), round(out[-1][:, 2].max(), 2))
    return np.concatenate(out)
land = pts('APC'); water = pts('APCW')
INM = D + 'in-mod/tsapc/frames/tsapc-%04d.png'
for el in (30.0, 32.0):
    data = [VP.world(land, f) + (VP.opaque(INM % f),) for f in (0, 8, 16, 24)]
    print(el, 'land', VP.fit(data, (384, 384), el))
    data = [VP.world(water, f) + (VP.opaque(INM % (32 + f)),) for f in (0, 8, 16, 24)]
    print(el, 'water', VP.fit(data, (384, 384), el))
