"""draw the Mk. II's voxels posed by the HVA (all 13 sections) as shaded cubes from any direction: to read how the
legs hang from the body.  python3 hposed.py out.png hf az el [px] [sections]"""
import sys
from paths import HANDOFF
sys.path.insert(0, HANDOFF + '/renderer')
import numpy as np, vxl
from PIL import Image, ImageDraw, ImageFont

D = HANDOFF + '/03-TSHMEC/ts-original/'
SECS = vxl.read_vxl(D + 'HMEC.VXL')
NAMES, MATS = vxl.read_hva(D + 'HMEC.HVA')
PAL = vxl.read_pal(D + 'UNITTEM.PAL').astype(float)
for i in range(16, 32):
    g = 255 - (i - 16) * 12
    PAL[i] = (0.1 * g, g, 0.1 * g)
FACES = {(1, 0, 0): [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)], (-1, 0, 0): [(0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)],
         (0, 1, 0): [(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)], (0, -1, 0): [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)],
         (0, 0, 1): [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)], (0, 0, -1): [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]}


def sec_affine(i, hf):
    s = SECS[i]
    sc = (np.asarray(s['max']) - np.asarray(s['min'])) / np.asarray(s['size'], float)
    M = MATS[hf, i]
    R = M[:, :3]; t = M[:, 3] * s['det']
    A = R @ np.diag(sc)
    b = R @ np.asarray(s['min']) + t
    return A, b                      # unit = A q + b


def draw(hf, az, el, px=10, secs=None, label=''):
    az, el = np.deg2rad(az), np.deg2rad(el)
    c = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    f = -c
    up = np.array([0, 0, 1.0])
    right = np.cross(f, up); right /= np.linalg.norm(right)
    ups = np.cross(right, f)
    L = np.array([0.35, -0.45, 0.82]); L /= np.linalg.norm(L)
    polys = []
    for i, s in enumerate(SECS):
        if secs is not None and i not in secs:
            continue
        A, b = sec_affine(i, hf)
        col = s['col']; occ = col >= 0
        for n, corners in FACES.items():
            nn = np.array(n, float)
            nw = A @ nn; nw = np.linalg.solve(A.T, nn); nw /= np.linalg.norm(nw)
            if nw @ c <= 1e-6:
                continue
            ax = int(np.argmax(np.abs(nn))); sg = int(nn[ax])
            nb = np.zeros_like(occ)
            sl = [slice(None)] * 3; sl2 = [slice(None)] * 3
            if sg > 0:
                sl[ax] = slice(0, -1); sl2[ax] = slice(1, None)
            else:
                sl[ax] = slice(1, None); sl2[ax] = slice(0, -1)
            nb[tuple(sl)] = occ[tuple(sl2)]
            vis = occ & ~nb
            shade = 0.5 + 0.5 * max(0.0, nw @ L) + 0.12 * nw[2]
            cs = np.array(corners, float)
            for (x, y, z) in zip(*np.nonzero(vis)):
                pts = (cs + (x, y, z)) @ A.T + b
                depth = pts.mean(0) @ f
                rgb = np.clip(PAL[col[x, y, z]] * shade, 0, 255)
                polys.append((depth, pts, tuple(int(v) for v in rgb)))
    polys.sort(key=lambda t: -t[0])
    allp = np.concatenate([p[1] for p in polys])
    sx = allp @ right; sy = -(allp @ ups)
    x0, y0 = sx.min(), sy.min()
    W = int((sx.max() - x0) * px) + 40; H = int((sy.max() - y0) * px) + 50
    im = Image.new('RGB', (W, H), (40, 42, 38))
    d = ImageDraw.Draw(im)
    for depth, pts, rgb in polys:
        q = [((p @ right - x0) * px + 20, (-(p @ ups) - y0) * px + 30) for p in pts]
        d.polygon(q, fill=rgb, outline=tuple(max(0, v - 25) for v in rgb))
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
    d.text((6, 6), label, font=font, fill=(240, 240, 220))
    return im


if __name__ == '__main__':
    out, hf, az, el = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
    px = int(sys.argv[5]) if len(sys.argv) > 5 else 10
    secs = [int(a) for a in sys.argv[6].split(',')] if len(sys.argv) > 6 else None
    draw(hf, az, el, px, secs, 'hf %d az %g el %g' % (hf, az, el)).save(out)
