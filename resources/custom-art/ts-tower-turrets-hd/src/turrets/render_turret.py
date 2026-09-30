"""Render a turret's frames in place on the tower canvas.

    python3 render_turret.py <vulcan|rpg|sam> <state> [first last]
state: healthy | damaged | recoil | damaged-recoil (recoil: Vulcan only)
-> out/<turret>/turret[-state]-NN.png and turret[-state]-NN-trim.png (house colour mask), and the aim
points of every frame in out/<turret>/aim-<state>.json
"""
import os, sys, json, importlib, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tren, tdamage
import tsdf as T

FIT = {'vulcan': 'vulcan-fit2.json', 'rpg': 'rpg-fit3.json', 'sam': 'sam-fit5.json'}
ZP = (160.0 - 83.7) / np.cos(np.deg2rad(32.0))       # height of the pivot the in-mod sprites turn about


def facing(f):
    """frame f -> the model's heading, matched to TS's own facing f as it lands on screen (in-mod)."""
    a = f * np.pi / 16
    return float(np.arctan2(np.sin(a), np.cos(a) * 0.5 / np.sin(np.deg2rad(32.0))))


def project(pts, th, z0):
    """local points -> canvas (x, y) (pixel-edge coordinates)."""
    pts = np.atleast_2d(np.array(pts, float))
    fdir, rdir = T.local_dirs(th)
    W = pts[:, :1] * fdir + pts[:, 1:2] * rdir
    x, y, z = W[:, 0], W[:, 1], pts[:, 2] + z0
    return np.stack([88.0 + x, 160.0 + y * tren.SE - z * tren.CE], -1)


def main(name, state, first=0, last=31):
    M = importlib.import_module(name)
    p = json.load(open(FIT[name]))
    z0 = ZP - p['zref']
    damaged = state.startswith('damaged')
    recoil = 4.0 if state.endswith('recoil') else 0.0
    tower = tren.TowerScene(1 if damaged else 0)
    kw = dict(damaged=damaged)
    if recoil:
        kw['recoil'] = recoil
    parts = M.parts_hd(p, **kw)
    chips = tdamage.chips(M.chip_points(p), seed=7) if damaged else []
    wear = tdamage.Wear(seed=11, scorch=M.scorch(p)) if damaged else None
    out = f'out/{name}'
    os.makedirs(out, exist_ok=True)
    tag = '' if state == 'healthy' else '-' + state
    aims = {}
    for f in range(first, last + 1):
        th = facing(f)
        t = time.time()
        img, trim = tren.render(parts + chips, th, z0, lambda *a: M.albedo(*a, p=p), tower, wear=wear, chips=chips)
        img.save(f'{out}/turret{tag}-{f:02d}.png'); trim.save(f'{out}/turret{tag}-{f:02d}-trim.png')
        aims[f] = project(M.aim_points(p, recoil), th, z0).round(1).tolist()
        print(name, state, f, round(time.time() - t, 1), 's', flush=True)
    path = f'{out}/aim-{state}.json'
    old = json.load(open(path)) if os.path.exists(path) else {}
    old.update({str(k): v for k, v in aims.items()})
    json.dump(old, open(path, 'w'), indent=0)


if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], a[1], *(int(x) for x in a[2:4]))
