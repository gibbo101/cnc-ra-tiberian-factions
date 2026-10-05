"""sonvcomp.py - TS's voxels drawn flat in the mod's cameras against the model drawn flat: extents and overlap per frame,
and a sheet of the differences (red: the voxels' only, blue: the model's only), the hull frames (0-31) and the
turret's (32-63).
    python3 sonvcomp.py ext [frames]
    python3 sonvcomp.py diff out.png [frames] [zoom]"""
import sys, numpy as np
from PIL import Image, ImageDraw
from scipy.spatial import ConvexHull
import rc
import sonmodel as T
import vxl
from soncam import flat_cam, unit_to_world, frame_of, GZ, CANVAS

SS = 2
C = np.array([[a, b, c] for a in (0, 1) for b in (0, 1) for c in (0, 1)], float)
VOX = {}
for k, (n, i) in {'hull': ('SONIC', 0), 'ring': ('SONICTUR', 0), 'tur': ('SONICTUR', 1)}.items():
    s = vxl.read_vxl(T.D + n + '.VXL')[i]
    occ = s['col'] >= 0
    p = np.pad(occ, 1)
    inner = (p[2:, 1:-1, 1:-1] & p[:-2, 1:-1, 1:-1] & p[1:-1, 2:, 1:-1] & p[1:-1, :-2, 1:-1] & p[1:-1, 1:-1, 2:] &
             p[1:-1, 1:-1, :-2])
    VOX[k] = np.argwhere(occ & ~inner).astype(float)


def vox_cov(k):
    which, facing, tur = frame_of(k)
    Mx = unit_to_world(facing)
    cam = flat_cam(tur)
    im = Image.new('L', (CANVAS[0] * SS, CANVAS[1] * SS), 0)
    d = ImageDraw.Draw(im)
    for name in which:
        F = T.SECTIONS[name]
        R, t = F.pose()
        if name == 'hull':
            t = t + np.array([0.0, 0.0, -GZ])
        Rw, tw = Mx @ R, Mx @ t

        def scr(q):
            w = (F.mn + q * F.sc) @ Rw.T + tw
            x, y = cam.project(w)
            return np.stack([x, y], -1)
        c0 = scr(C)
        hv = ConvexHull(c0).vertices
        base = scr(VOX[name])
        off = c0[hv] - scr(np.zeros((1, 3)))
        for b in base:
            d.polygon([tuple(q) for q in (b[None, :] + off) * SS], fill=255)
    return np.array(im).reshape(CANVAS[1], SS, CANVAS[0], SS).mean(axis=(1, 3)) >= 127.5


def model_cov(k, m):
    which, facing, tur = frame_of(k)
    parts, _, _ = T.posed(m, which, unit_to_world(facing))
    t, who, nrm, O = rc.render_ids(parts, flat_cam(tur), 0, 0, CANVAS[0], CANVAS[1], ss=SS, zstart=300.0)
    cov = (who >= 0).reshape(CANVAS[1], SS, CANVAS[0], SS).mean(axis=(1, 3)) >= 0.5
    return cov, who, nrm, parts


def ext(a):
    ys, xs = np.nonzero(a)
    return ys.min(), ys.max(), xs.min(), xs.max()


def extents(ks):
    m = T.model()
    rows = []
    for k in ks:
        va = vox_cov(k)
        cov = model_cov(k, m)[0]
        e = ext(va) + ext(cov)
        iou = (va & cov).sum() / (va | cov).sum()
        rows.append((k,) + e + (iou,))
        print('%2d voxel %3d..%3d x %3d..%3d | model %3d..%3d x %3d..%3d | overlap %.3f' % rows[-1], flush=True)
    Rr = np.array(rows, float)
    for nm, i in (('top', 1), ('bottom', 2), ('left', 3), ('right', 4)):
        d = Rr[:, 4 + i] - Rr[:, i]
        print('%-6s model-voxel %+.1f (min %+d max %+d)' % (nm, d.mean(), d.min(), d.max()))
    print('mean overlap %.3f' % Rr[:, -1].mean())


def diff(out, ks, Z=2, crop=(40, 40, 408, 380)):
    m = T.model()
    tiles = []
    for k in ks:
        va = vox_cov(k)
        cov, who, nrm, parts = model_cov(k, m)
        img = np.zeros(cov.shape + (3,)) + np.array([96, 108, 72.])
        img[cov] = (170, 170, 170)
        miss = va & ~cov; extra = cov & ~va
        img[miss] = (255, 40, 40); img[extra] = (60, 120, 255)
        im = Image.fromarray(img.clip(0, 255).astype(np.uint8)).crop(crop)
        im = im.resize((im.width * Z, im.height * Z), Image.NEAREST)
        ImageDraw.Draw(im).text((4, 2), 'frame %d  voxel only %d  model only %d' % (k, miss.sum(), extra.sum()),
                                fill=(255, 255, 200))
        tiles.append(im)
    W, H = tiles[0].size
    S = Image.new('RGB', (2 * (W + 4), ((len(tiles) + 1) // 2) * (H + 4)), (20, 20, 20))
    for i, t in enumerate(tiles):
        S.paste(t, ((i % 2) * (W + 4), (i // 2) * (H + 4)))
    S.save(out)


if __name__ == '__main__':
    if sys.argv[1] == 'ext':
        extents([int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else range(0, 32, 4))
    else:
        diff(sys.argv[2], [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else [0, 4, 8, 12, 16, 20, 24, 28],
             int(sys.argv[4]) if len(sys.argv) > 4 else 2)
