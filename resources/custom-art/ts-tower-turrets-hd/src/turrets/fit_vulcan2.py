import json, numpy as np
import tfit as F, vulcan as V
ts = F.load_ts('vulcan')
steps = dict(bf=3, L=4, Wd=4, Hb=3, bt=2, bs=2, bb=2, gs=2, gz=2, gr=1, gtip=4, hr=1.5, hl=3,
             pf=3, pl=4, prad=2, po=2, pz=2, px=0.3, py=0.3, zref=2)
limits = dict(Wd=(36, 60), L=(30, 60), Hb=(18, 40), bt=(0, 14), bs=(0, 14), bb=(0, 10), prad=(4, 14),
              po=(0, 14), gr=(3, 9), hr=(5, 14), pl=(12, 40))
p, best, iou, ci = F.fit2(V, ts, V.P0, steps, rounds=10, w_cls=1.0, merge={4: 2}, limits=limits,
                          log=lambda s: print(s, flush=True))
json.dump(p, open('vulcan-fit2.json', 'w'), indent=1)
print('final', best, iou, ci)
print({k: round(v, 2) for k, v in p.items()})
