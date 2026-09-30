import json, sys, numpy as np
import tfit as F, rpg as M
ts = F.load_ts('rpg')
old = json.load(open('rpg-fit2.json'))
p0 = dict(M.P0)
p0.update(lf=old['pf'], ll=old['pl'], lz0=old['pz0'], lh=old['ph'], lb=old['pb'], rl=old['rl'], wl=old['wl'],
          sf=old['pf'], sl=old['pl'], sz0=old['pz0'], sh=old['ph'], sb=old['pb'], rr=old['rr'], wr=old['wr'],
          gf=old['gf'], gl=old['gl'], gr=old['gr'], gw=old['gw'], gz0=old['gz0'], gh=old['gh'],
          bR=old['bR'], bh=old['bh'], px=old['px'], py=old['py'], zref=old['zref'])
lut = np.zeros(32, int)
for k, v in M.CLS.items():
    lut[k] = v

def ev(p, merge={4: 1}):
    P, comp = F.voxels(M.parts(p), *M.bounds(p))
    iou, ci = F.score_cls(ts, P, lut[comp], p['px'], p['py'], p['zref'], range(32), merge)
    return iou + ci, iou, ci

if sys.argv[1] == 'scan':
    for pa in (-0.10, 0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30):
        for pv in ((-8.0, 16.0), (0.0, 20.0)):
            q = dict(p0, pa=pa, pvf=pv[0], pvz=pv[1])
            print(pa, pv, [round(x, 4) for x in ev(q)], flush=True)
else:
    p0['pa'] = float(sys.argv[2])
    steps = dict(pa=0.04, pvf=4, pvz=3, lf=2, ll=3, lz0=1.5, lh=2, lb=2, rl=1.5, wl=1.5, sf=2, sl=3, sz0=1.5, sh=2, rr=1.5, wr=1.5)
    limits = dict(pa=(-0.2, 0.5), pvz=(4, 30), pvf=(-25, 20), lh=(14, 40), sh=(14, 40), lb=(0, 12), wl=(12, 40), wr=(12, 40))
    p, best, iou, ci = F.fit2(M, ts, p0, steps, rounds=8, w_cls=1.0, merge={4: 1}, limits=limits,
                              log=lambda s: print(s, flush=True))
    json.dump(p, open(sys.argv[3], 'w'), indent=1)
    print('final', best, iou, ci)
    print({k: round(v, 3) for k, v in p.items()})
