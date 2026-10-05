"""t4view.py - the rebuilt Mk. I beside TS's voxels, alike, from any direction.
    python3 t4view.py out.png 'az,el;az,el' [px] [sections: hull,tur,barl]"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import rc
import t4v2 as T
import t4vox as TV

BOX = np.array([[x, y, z] for x in (-22, 26) for y in (-14, 14) for z in (-1, 22)], float)
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
COL = {T.BELT: (40, 40, 42), T.WHEEL: (70, 70, 74), T.HUB: (120, 120, 126), T.CORE: (20, 20, 20), T.RING: (50, 50, 54),
       T.GRILLE: (40, 40, 44), T.TAIL: (255, 150, 40), T.HEAD: (240, 240, 230), T.VENT: (190, 190, 196),
       T.CUPOLA: (40, 40, 44), T.POD: (50, 50, 54), T.POD_FRONT: (50, 50, 54), T.TIP: (255, 140, 30),
       T.ANTENNA: (30, 30, 30), T.ANTBASE: (140, 140, 146), T.BARREL: (50, 50, 54), T.MUZZLE: (30, 30, 32),
       T.HATCH: (60, 60, 64), T.LAMPHOUSE: (60, 60, 64), T.ARM: (50, 50, 54)}


def comp_colour(c):
    if c in T.HOUSE:
        return np.array([40, 200, 40.])
    return np.array(COL.get(c, (255, 0, 255)), float)


def basis(az, el):
    az, el = np.deg2rad(az), np.deg2rad(el)
    c = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    f = -c
    right = np.cross(f, (0, 0, 1.0)); right /= np.linalg.norm(right)
    return c, f, right, np.cross(right, f)


def frame_box(az, el, px):
    c, f, right, ups = basis(az, el)
    sx = BOX @ right; sy = -(BOX @ ups)
    return sx.min(), sy.min(), int((sx.max() - sx.min()) * px) + 40, int((sy.max() - sy.min()) * px) + 40


def render_model(parts, az, el, px, ss=2):
    c, f, right, ups = basis(az, el)
    x0, y0, W, H_ = frame_box(az, el, px)
    xs = (np.arange(W * ss) + 0.5) / ss; ys = (np.arange(H_ * ss) + 0.5) / ss
    SX, SY = np.meshgrid(xs, ys)
    u = (SX - 20) / px + x0; v = (SY - 20) / px + y0
    O = u.ravel()[:, None] * right[None, :] - v.ravel()[:, None] * ups[None, :] + c[None, :] * 200.0
    t, who, nrm = rc.cast(parts, O, f)
    hit = np.isfinite(t)
    L = np.array([0.35, -0.45, 0.82]); L /= np.linalg.norm(L)
    shade = 0.45 + 0.55 * np.clip(nrm @ L, 0, 1) + 0.15 * np.clip(nrm @ c, 0, 1)
    comps = np.array([p.comp for p in parts] + [0])
    col = np.stack([comp_colour(int(k)) for k in comps])
    rgb = col[np.where(hit, who, -1)] * shade[:, None]
    rgb[~hit] = (40, 42, 38)
    img = np.clip(rgb, 0, 255).reshape(H_ * ss, W * ss, 3).reshape(H_, ss, W, ss, 3).mean((1, 3))
    return Image.fromarray(img.astype(np.uint8))


def render_voxels(which, az, el, px):
    c, f, right, ups = basis(az, el)
    x0, y0, W, H_ = frame_box(az, el, px)
    L = np.array([0.35, -0.45, 0.82]); L /= np.linalg.norm(L)
    polys = []
    for k in which:
        s, _ = TV.SECS[k]
        A, b = TV.affine(k)
        b = b - np.array([0, 0, T.GZ])
        col = s['col']; occ = col >= 0
        for n, corners in TV.FACES.items():
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
            shade = 0.45 + 0.55 * max(0.0, nw @ L) + 0.15 * max(0.0, nw @ c)
            cs = np.array(corners, float)
            for (x, y, z) in zip(*np.nonzero(vis)):
                pts = (cs + (x, y, z)) @ A.T + b
                polys.append((pts.mean(0) @ f, pts, tuple(int(v) for v in np.clip(TV.PAL[col[x, y, z]] * shade, 0, 255))))
    polys.sort(key=lambda t: -t[0])
    im = Image.new('RGB', (W, H_), (40, 42, 38))
    d = ImageDraw.Draw(im)
    for depth, pts, rgb in polys:
        d.polygon([((p @ right - x0) * px + 20, (-(p @ ups) - y0) * px + 20) for p in pts], fill=rgb)
    return im


if __name__ == '__main__':
    out = sys.argv[1]
    views = [tuple(float(v) for v in s.split(',')) for s in sys.argv[2].split(';')]
    px = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    which = sys.argv[4].split(',') if len(sys.argv) > 4 else ['hull', 'tur', 'barl']
    m = T.model()
    parts, _, _ = T.posed(m, which)
    rows = []
    for az, el in views:
        a = render_voxels(which, az, el, px); b = render_model(parts, az, el, px)
        row = Image.new('RGB', (a.width + b.width + 6, a.height), (20, 20, 20))
        row.paste(a, (0, 0)); row.paste(b, (a.width + 6, 0))
        ImageDraw.Draw(row).text((6, 4), 'TS  az %g el %g' % (az, el), font=FONT, fill=(230, 230, 210))
        ImageDraw.Draw(row).text((a.width + 12, 4), 'v2 model', font=FONT, fill=(230, 230, 210))
        rows.append(row)
    S = Image.new('RGB', (max(r.width for r in rows), sum(r.height for r in rows)), (20, 20, 20))
    y = 0
    for r in rows:
        S.paste(r, (0, y)); y += r.height
    S.save(out)
