import json, sys, numpy as np
from PIL import Image
import tfit as F, sam as M
ts = F.load_ts('sam')
lut = np.zeros(32, int)
for k, v in M.CLS.items():
    lut[k] = v

def ev(p):
    P, comp = F.voxels(M.parts(p), *M.bounds(p))
    iou, ci = F.score_cls(ts, P, lut[comp], p['px'], p['py'], p['zref'], range(32))
    return round(iou + ci, 4), round(iou, 4), round(ci, 4)

def sheet(p, path, frames=(0, 4, 8, 12, 16, 20, 24, 28)):
    P, comp = F.voxels(M.parts(p), *M.bounds(p))
    imgs = [Image.open(f'ts-tower-turrets-handoff/ts-original/sam/frame-{f:02d}.png') for f in range(32)]
    F.compare_sheet(imgs, P, lut[comp], p['px'], p['py'], p['zref'], frames, scale=5).save(path)

if __name__ == '__main__':
    if sys.argv[1] == 'eval':
        p = dict(M.P0); p.update(json.loads(sys.argv[2]) if len(sys.argv) > 2 else {})
        print(ev(p))
        sheet(p, '/tmp/claude-0/-home-claude/d8d7e55c-9962-5588-8e0f-2782c3ff0a20/scratchpad/tt/s5.png')
    elif sys.argv[1] == 'scan':
        for tb in (0.5, 0.7, 0.85, 1.0, 1.1, 1.2):
            for Lf in (30, 40, 50):
                p = dict(M.P0, tb=tb, Lf=Lf)
                print(tb, Lf, ev(p), flush=True)
    else:
        p0 = dict(M.P0); p0.update(json.load(open(sys.argv[2])) if len(sys.argv) > 2 and sys.argv[2] != '-' else {})
        steps = dict(tb=0.06, Lf=3, hv=2, hb=2, L=3, W=2, bf=2, bz0=1.5, tf=2, tz=2, tr=1.5, tw=1.5,
                     sf=3, sr=2, cl=2, cw=2, gh=1, pw=2, phh=2, pt=0.1, ms=1.5, zref=1.5, py=0.3, px=0.2)
        limits = dict(tb=(0.3, 1.35), Lf=(15, 70), hv=(0, 25), hb=(4, 40), L=(40, 100), W=(30, 64), tr=(3, 16),
                      tw=(0, 12), cl=(6, 30), cw=(6, 30), gh=(2, 8), pw=(8, 36), phh=(5, 26), pt=(-0.3, 0.9),
                      ms=(0, 12), bz0=(0, 24))
        p, best, iou, ci = F.fit2(M, ts, p0, steps, rounds=10, w_cls=1.0, limits=limits, log=lambda s: print(s, flush=True))
        json.dump(p, open(sys.argv[3], 'w'), indent=1)
        print('final', best, iou, ci)
        print({k: round(v, 3) for k, v in p.items()})
