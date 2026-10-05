"""TS's voxel drawn flat in the mod's camera against the model drawn flat: extents and overlap per frame, and a sheet
of the differences (red: the voxel's only, blue: the model's only).
    python3 vcomp.py ext [frames]
    python3 vcomp.py diff out.png [frames] [zoom]"""
import sys, numpy as np
from PIL import Image, ImageDraw
from scipy.spatial import ConvexHull
import mwarmodel as T
import vxl
from mwarcam import flat_cam, unit_to_world, GZ
from mwarshape import flat, INMOD
SS = 2
F = T.F
s = vxl.read_vxl(T.D + 'MWAR_NOD.VXL')[0]
occ = s['col'] >= 0
p = np.pad(occ, 1)
inner = p[2:, 1:-1, 1:-1] & p[:-2, 1:-1, 1:-1] & p[1:-1, 2:, 1:-1] & p[1:-1, :-2, 1:-1] & p[1:-1, 1:-1, 2:] & p[1:-1, 1:-1, :-2]
V = np.argwhere(occ & ~inner).astype(float)
C = np.array([[a, b, c] for a in (0, 1) for b in (0, 1) for c in (0, 1)], float)
R, t = F.pose()
cam = flat_cam()


def vox_cov(k):
    Mx = unit_to_world(k)
    Rw, tw = Mx @ R, Mx @ t + np.array([0.0, 0.0, -GZ])

    def scr(q):
        w = (F.mn + q * F.sc) @ Rw.T + tw
        x, y = cam.project(w)
        return np.stack([x, y], -1)
    c0 = scr(C)
    hv = ConvexHull(c0).vertices
    base = scr(V)
    off = c0[hv] - scr(np.zeros((1, 3)))
    im = Image.new('L', (384 * SS, 384 * SS), 0)
    d = ImageDraw.Draw(im)
    for b in base:
        d.polygon([tuple(q) for q in (b[None, :] + off) * SS], fill=255)
    return np.array(im).reshape(384, SS, 384, SS).mean(axis=(1, 3)) >= 127.5


def ext(a):
    ys, xs = np.nonzero(a)
    return ys.min(), ys.max(), xs.min(), xs.max()


def extents(ks):
    m = T.model()
    rows = []
    for k in ks:
        va = vox_cov(k)
        parts, _ = T.posed(m, unit_to_world(k))
        _, cov = flat(parts, flat_cam())
        mod = np.array(Image.open(INMOD % k).convert('RGBA'))[..., 3] > 250
        e = ext(mod) + ext(va) + ext(cov)
        iou = (va & cov).sum() / (va | cov).sum()
        rows.append((k,) + e + (iou,))
        print('%2d mod %3d..%3d x %3d..%3d | voxel %3d..%3d x %3d..%3d | model %3d..%3d x %3d..%3d | model~voxel %.3f'
              % rows[-1], flush=True)
    Rr = np.array(rows, float)
    for nm, i in (('top', 1), ('bottom', 2), ('left', 3), ('right', 4)):
        d = Rr[:, 8 + i] - Rr[:, 4 + i]
        print('%-6s voxel-mod %+.1f   model-voxel %+.1f (min %+d max %+d)' % (nm, (Rr[:, 4 + i] - Rr[:, i]).mean(),
                                                                          d.mean(), d.min(), d.max()))
    print('mean model~voxel overlap %.3f' % Rr[:, -1].mean())


def diff(out, ks, Z=2, crop=(30, 20, 354, 320)):
    m = T.model()
    tiles = []
    for k in ks:
        parts, _ = T.posed(m, unit_to_world(k))
        fl, cov = flat(parts, flat_cam())
        va = vox_cov(k)
        a = np.array(fl).astype(float)
        al = a[..., 3:4] / 255
        img = a[..., :3] * al + np.array([96, 108, 72.]) * (1 - al)
        miss = va & ~cov; extra = cov & ~va
        img[miss] = (255, 40, 40); img[extra] = (60, 120, 255)
        im = Image.fromarray(img.clip(0, 255).astype(np.uint8)).crop(crop)
        im = im.resize((im.width * Z, im.height * Z), Image.NEAREST)
        ImageDraw.Draw(im).text((4, 2), 'frame %d  missing %d  extra %d' % (k, miss.sum(), extra.sum()),
                                fill=(255, 255, 200))
        tiles.append(im)
    W, H = tiles[0].size
    S = Image.new('RGB', (2 * (W + 4), ((len(tiles) + 1) // 2) * (H + 4)), (20, 20, 20))
    for i, t in enumerate(tiles):
        S.paste(t, ((i % 2) * (W + 4), (i // 2) * (H + 4)))
    S.save(out)


if __name__ == '__main__':
    if sys.argv[1] == 'ext':
        extents([int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else range(0, 32, 2))
    else:
        diff(sys.argv[2], [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else [0, 4, 8, 12, 16, 20, 24, 28],
             int(sys.argv[4]) if len(sys.argv) > 4 else 2)
