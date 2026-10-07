"""draw tick-tank-dug-in.glb (base + turret, or base-damaged) through its RA-grid / TS-angle camera over the frames, to
check the model lines up with them (silhouette overlap with the frames' solid pixels).
    python3 tickglbcheck.py [out.png]"""
import os, sys, json
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(HERE, 'src'), HERE):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import glbcheck as G
import tickfinal as TF, tickrender as TR

GLB = TF.PKG + '-3d/tick-tank-dug-in.glb'


def cam_named(js, name):
    for n in js['nodes']:
        if n.get('name') == name and 'camera' in n:
            return G.qmat(n['rotation']), np.array(n['translation']), js['cameras'][n['camera']]['orthographic']


def check(out):
    js, binb = G.load_glb(GLB)
    ms = G.world_meshes(js, binb)
    rows = []
    for v, cname in (('ra', 'camera-ra-grid'),):            # RA grid only (6 Oct)
        W, H = TR.CANVAS[v]
        for level, meshes in ((0, ('base', 'turret_mesh')), (1, ('base-damaged', 'turret_mesh'))):
            img, m = G.raster([x for x in ms if x[0] in meshes], cam_named(js, cname), W, H)
            b = Image.open(TF.path(v, 'building', f'{TF.NAME}-{level:02d}')).convert('RGBA')
            b.alpha_composite(Image.open(TF.path(v, 'turret', f'{TF.NAME}-turret-{TF.K.FACING:02d}')).convert('RGBA'))
            ref = np.array(b)[..., 3] > 250
            iou = (m & ref).sum() / (m | ref).sum()
            print(v, level, 'overlap %.3f' % iou)
            vis = np.zeros(img.shape, np.uint8); vis[...] = (30, 30, 40)
            vis[ref & ~m] = (230, 70, 70); vis[m & ~ref] = (70, 120, 240); vis[m & ref] = (210, 210, 210)
            rows.append(np.concatenate([img, vis], 1))
    Wm = max(r.shape[1] for r in rows)
    pad = [np.pad(r, ((0, 0), (0, Wm - r.shape[1]), (0, 0))) for r in rows]
    Image.fromarray(np.concatenate(pad, 0)).save(out)


if __name__ == '__main__':
    check(sys.argv[1] if len(sys.argv) > 1 else '/home/claude/work/tick/glbcheck.png')
