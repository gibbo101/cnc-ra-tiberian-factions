"""the Orca Bomber's voxel (ORCAB.VXL, one section, posed by its HVA, frame 0), drawn as shaded cubes from any
direction, and its faces as
colour-class text.
    python3 mvox.py out.png 'az,el;az,el' [px]"""
import sys
from paths import HANDOFF
sys.path.insert(0, HANDOFF + '/renderer')
import numpy as np, vxl
from PIL import Image, ImageDraw, ImageFont
from hcls import cls

D = HANDOFF + '/24-TSORCAB/ts-original/'
PAL = vxl.read_pal(D + 'UNITTEM.PAL').astype(float)
for _i in range(16, 32):
    _g = 255 - (_i - 16) * 12
    PAL[_i] = (0.1 * _g, _g, 0.1 * _g)
FILES = {'hull': ('ORCAB', 0)}
SECS = {}
for k, (n, i) in FILES.items():
    s = vxl.read_vxl(D + n + '.VXL')[i]
    names, mats = vxl.read_hva(D + n + '.HVA')
    SECS[k] = (s, mats[0, i])
FACES = {(1, 0, 0): [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)], (-1, 0, 0): [(0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)],
         (0, 1, 0): [(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)], (0, -1, 0): [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)],
         (0, 0, 1): [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)], (0, 0, -1): [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]}


def affine(k):
    s, M = SECS[k]
    sc = (np.asarray(s['max']) - np.asarray(s['min'])) / np.asarray(s['size'], float)
    R = M[:, :3]; t = M[:, 3] * s['det']
    return R @ np.diag(sc), R @ np.asarray(s['min']) + t


def draw(parts, az, el, px=12, label=''):
    az, el = np.deg2rad(az), np.deg2rad(el)
    c = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    f = -c
    right = np.cross(f, (0, 0, 1.0)); right /= np.linalg.norm(right)
    ups = np.cross(right, f)
    L = np.array([0.35, -0.45, 0.82]); L /= np.linalg.norm(L)
    polys = []
    for k in parts:
        s, _ = SECS[k]
        A, b = affine(k)
        col = s['col']; occ = col >= 0
        for n, corners in FACES.items():
            nn = np.array(n, float)
            nw = np.linalg.solve(A.T, nn); nw /= np.linalg.norm(nw)
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
                polys.append((pts.mean(0) @ f, pts, tuple(int(v) for v in np.clip(PAL[col[x, y, z]] * shade, 0, 255))))
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
    d.text((6, 6), label, font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14), fill=(240, 240, 220))
    return im


def dch(d):
    return chr(48 + d) if d < 10 else chr(55 + d) if d < 36 else chr(61 + d) if d < 62 else '#'


def face(k, view):
    col = SECS[k][0]['col']; X, Y, Z = col.shape
    f = col >= 0
    rows = []
    if view in ('top', 'bottom'):
        d = np.where(f.any(2), (Z - 1 - np.argmax(f[:, :, ::-1], axis=2)) if view == 'top' else np.argmax(f, axis=2), -1)
        for y in range(Y):
            rows.append('%3d ' % y + ''.join(cls(col[x, y, d[x, y]]) if d[x, y] >= 0 else '.' for x in range(X)) +
                        '  ' + ''.join(dch(d[x, y]) if d[x, y] >= 0 else '.' for x in range(X)))
    elif view in ('right', 'left'):
        d = np.where(f.any(1), np.argmax(f, axis=1) if view == 'right' else Y - 1 - np.argmax(f[:, ::-1], axis=1), -1)
        for z in range(Z - 1, -1, -1):
            rows.append('%3d ' % z + ''.join(cls(col[x, d[x, z], z]) if d[x, z] >= 0 else '.' for x in range(X)) +
                        '  ' + ''.join(dch(d[x, z]) if d[x, z] >= 0 else '.' for x in range(X)))
    else:
        d = np.where(f.any(0), (X - 1 - np.argmax(f[::-1], axis=0)) if view == 'front' else np.argmax(f, axis=0), -1)
        for z in range(Z - 1, -1, -1):
            rows.append('%3d ' % z + ''.join(cls(col[d[y, z], y, z]) if d[y, z] >= 0 else '.' for y in range(Y)) +
                        '  ' + ''.join(dch(d[y, z]) if d[y, z] >= 0 else '.' for y in range(Y)))
    n = X if view in ('top', 'bottom', 'right', 'left') else Y
    hdr = '    ' + ''.join(str(i // 10) if i % 10 == 0 else ' ' for i in range(n))
    hdr2 = '    ' + ''.join(str(i % 10) for i in range(n))
    return '\n'.join(['%s %s' % (k, view), hdr, hdr2] + rows)


if __name__ == '__main__':
    out = sys.argv[1]
    views = [tuple(float(v) for v in s.split(',')) for s in sys.argv[2].split(';')]
    px = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    parts = ['hull']
    ims = [draw(parts, az, el, px, 'az %g el %g' % (az, el)) for az, el in views]
    W = sum(i.width for i in ims); H = max(i.height for i in ims)
    s = Image.new('RGB', (W, H), (40, 42, 38)); x = 0
    for i in ims:
        s.paste(i, (x, 0)); x += i.width
    s.save(out)
