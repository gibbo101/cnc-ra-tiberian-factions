"""otqdiff.py - TS's voxels against the model in TS's own q axes, drawn flat along x, y or z, as an image with a grid
every voxel (labels every 5): red the voxels' only, blue the model's only, grey both.
    python3 otqdiff.py out.png top|side|front [px per voxel] [x0,x1,y0,y1,z0,z1]"""
import sys
import numpy as np
from PIL import Image, ImageDraw
import rc
import otmodel as T
import otvoxd as V

S = 4                                               # samples per voxel


def model_occ(axis, m, box):
    """the model's silhouette along an axis (q), sampled S per voxel over the box's other two axes."""
    F = T.FH
    parts = [p for p in m['hull']]
    x0, x1, y0, y1, z0, z1 = box
    ax = 'xyz'.index(axis)
    other = [k for k in range(3) if k != ax]
    rng = [(x0, x1), (y0, y1), (z0, z1)]
    a0, a1 = rng[other[0]]; b0, b1 = rng[other[1]]
    ua = (np.arange((a1 - a0) * S) + 0.5) / S + a0
    ub = (np.arange((b1 - b0) * S) + 0.5) / S + b0
    A, Bq = np.meshgrid(ua, ub, indexing='ij')
    Q = np.zeros(A.shape + (3,))
    Q[..., other[0]] = A; Q[..., other[1]] = Bq
    Q[..., ax] = rng[ax][1] + 5.0                    # start beyond the box's far side, looking back along -axis
    O = F.p(Q.reshape(-1, 3))
    d = np.zeros(3); d[ax] = -1.0
    Dl = F.p(d) - F.p(np.zeros(3)); Dl /= np.linalg.norm(Dl)
    t, who, _ = rc.cast(parts, O, Dl, want_normals=False)
    return np.isfinite(t).reshape(A.shape)


def vox_occ(axis, box):
    x0, x1, y0, y1, z0, z1 = box
    O = V.OCC[x0:x1, y0:y1, z0:z1]
    ax = 'xyz'.index(axis)
    pl = O.any(ax)
    return np.repeat(np.repeat(pl, S, 0), S, 1)


def draw(out, axis, px=12, box=None):
    X, Y, Z = V.OCC.shape
    box = box or (0, X, 0, Y, 0, Z)
    m = T.model()
    mo = model_occ(axis, m, box); vo = vox_occ(axis, box)
    iou = (mo & vo).sum() / (mo | vo).sum()
    rgb = np.full(mo.shape + (3,), 36, np.uint8)
    rgb[mo & vo] = (150, 150, 150); rgb[vo & ~mo] = (230, 60, 50); rgb[mo & ~vo] = (60, 120, 240)
    # rows: the second axis; columns: the first (x along, or y for 'front'); flip so z / y grow upwards
    im = rgb.transpose(1, 0, 2)[::-1]
    k = max(px // S, 1)
    px = k * S
    im = np.repeat(np.repeat(im, k, 0), k, 1)
    H, W = im.shape[:2]
    img = Image.new('RGB', (W + 40, H + 30), (20, 20, 20))
    img.paste(Image.fromarray(im), (30, 6))
    d = ImageDraw.Draw(img)
    other = [a for a in 'xyz' if a != axis]
    x0, x1, y0, y1, z0, z1 = box
    rng = {'x': (x0, x1), 'y': (y0, y1), 'z': (z0, z1)}
    (ua, ub), (va, vb) = rng[other[0]], rng[other[1]]
    for u in range(ua, ub + 1):
        X_ = 30 + (u - ua) * px
        d.line([(X_, 6), (X_, 6 + H)], fill=(60, 60, 60) if u % 5 else (110, 110, 110))
        if u % 5 == 0:
            d.text((X_ - 4, H + 10), str(u), fill=(220, 220, 200))
    for v in range(va, vb + 1):
        Y_ = 6 + H - (v - va) * px
        d.line([(30, Y_), (30 + W, Y_)], fill=(60, 60, 60) if v % 5 else (110, 110, 110))
        if v % 5 == 0:
            d.text((4, Y_ - 6), str(v), fill=(220, 220, 200))
    d.text((W - 160, H + 16), '%s view: %s across, %s up   overlap %.3f' % (axis, other[0], other[1], iou),
           fill=(230, 220, 160))
    img.save(out)
    return iou


if __name__ == '__main__':
    out, axis = sys.argv[1], {'top': 'z', 'side': 'y', 'front': 'x'}.get(sys.argv[2], sys.argv[2])
    px = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    box = tuple(int(v) for v in sys.argv[4].split(',')) if len(sys.argv) > 4 else None
    print('%.3f' % draw(out, axis, px, box))
