"""seatcheck.py - is the turret seated on the hull the same way in every facing?  The .glb (one 3D scene: the hull and
the turret node seated and scaled as the frames should show it) is turned to each of the 32 facings and drawn through
its camera; the frames are laid as the game lays them (hull frame f, turret frame 32 + f shifted by sonspec.seat(f),
to the whole pixel).  Per facing: the overlap of the turret's pixels and how far the frames' turret sits from the 3D
scene's (centroid, canvas px, + right / + down); with --hull the same for the hull.

    python3 seatcheck.py PKG_ROOT [out.png] [--hull]      (PKG_ROOT holds ts-sonic-hd/ and ts-sonic-hd-3d/)
"""
import os, sys
import importlib.util
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw
import sonspec

# this unit's own glbcheck.py, by its path (it applies the nodes' scale; an older copy elsewhere on the path does not)
HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('glbcheck_unit', os.path.join(HERE, 'glbcheck.py'))
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

_G = {}


def turret_nodes(js):
    idx = [i for i, n in enumerate(js['nodes']) if n.get('name') == 'turret'][0]
    out, todo = set(), [idx]
    while todo:
        i = todo.pop()
        out.add(i)
        todo += js['nodes'][i].get('children', [])
    return out


def meshes_by_group(js, binb):
    """the world meshes (static pose), split into hull and turret by node ancestry (world_meshes keeps node order)."""
    tur = turret_nodes(js)
    mesh_nodes = [i for i, n in enumerate(js['nodes']) if 'mesh' in n]
    hull, turret = [], []
    for i, m in zip(mesh_nodes, G.world_meshes(js, binb)):
        (turret if i in tur else hull).append(m)
    return hull, turret


def turned(meshes, f):
    """the meshes turned about the vertical (glTF y) through the unit's position from facing 24 (east) to facing f."""
    th = np.deg2rad((f - 24) * 11.25)
    R = np.array([[np.cos(th), 0, np.sin(th)], [0, 1, 0], [-np.sin(th), 0, np.cos(th)]])
    return [(nm, V @ R.T, F, C) for nm, V, F, C in meshes]


def alpha(path, dx=0, dy=0, size=448):
    a = np.array(Image.open(path).convert('RGBA'))[..., 3] > 250
    out = np.zeros((size, size), bool)
    ys, xs = np.nonzero(a)
    xs2, ys2 = xs + dx, ys + dy
    ok = (xs2 >= 0) & (xs2 < size) & (ys2 >= 0) & (ys2 < size)
    out[ys2[ok], xs2[ok]] = True
    return out


def stats(a, b):
    iou = (a & b).sum() / max((a | b).sum(), 1)
    ya, xa = np.nonzero(a); yb, xb = np.nonzero(b)
    return iou, xa.mean() - xb.mean(), ya.mean() - yb.mean()


def _init(root, hull):
    js, binb = G.load_glb(os.path.join(root, 'ts-sonic-hd-3d', 'tssonic.glb'))
    _G['cam'] = G.camera(js)
    _G['hull'], _G['tur'] = meshes_by_group(js, binb)
    _G['fmt'] = os.path.join(root, 'ts-sonic-hd', 'frames', 'tssonic-%04d.png')
    _G['do_hull'] = hull


def one(f):
    _, mt = G.raster(turned(_G['tur'], f), _G['cam'], 448, 448)
    k, dx, dy = sonspec.seat(f)
    ft = alpha(_G['fmt'] % k, int(round(dx)), int(round(dy)))
    ts = stats(ft, mt)
    hs = (np.nan, np.nan, np.nan)
    if _G['do_hull']:
        _, mh = G.raster(turned(_G['hull'], f), _G['cam'], 448, 448)
        hs = stats(alpha(_G['fmt'] % f), mh)
    v = np.zeros((448, 448, 3), np.uint8); v[...] = (30, 30, 40)
    v[ft & ~mt] = (230, 70, 70); v[mt & ~ft] = (70, 120, 240); v[mt & ft] = (210, 210, 210)
    return f, ts, hs, v


def check(root, out=None, hull=False, procs=2):
    """per facing (turret overlap, dx, dy[, hull ...]); returns (mean turret overlap, largest turret offset px)."""
    with Pool(procs, initializer=_init, initargs=(root, hull)) as p:
        res = sorted(p.map(one, range(32)))
    for f, ts, hs, _ in res:
        line = 'facing %2d  turret %.3f (%+.2f, %+.2f)' % ((f,) + tuple(ts))
        if hull:
            line += '   hull %.3f (%+.2f, %+.2f)' % tuple(hs)
        print(line, flush=True)
    T = np.array([r[1] for r in res])
    print('turret: overlap mean %.3f min %.3f; offset px mean (%+.2f, %+.2f), largest %.2f' % (
        T[:, 0].mean(), T[:, 0].min(), T[:, 1].mean(), T[:, 2].mean(), np.abs(T[:, 1:]).max()), flush=True)
    if out:
        S = Image.new('RGB', (8 * 186, 4 * 160), (20, 20, 20))
        d = ImageDraw.Draw(S)
        for i, (f, _, _, v) in enumerate(res):
            S.paste(Image.fromarray(v).crop((40, 40, 408, 330)).resize((184, 145)), ((i % 8) * 186, (i // 8) * 160 + 14))
            d.text(((i % 8) * 186 + 2, (i // 8) * 160), 'facing %d' % f, fill=(240, 230, 180))
        S.save(out)
    return float(T[:, 0].mean()), float(np.abs(T[:, 1:]).max())


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    check(args[0], args[1] if len(args) > 1 else None, hull='--hull' in sys.argv)
