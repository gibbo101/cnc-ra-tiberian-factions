"""hview.py - the rebuilt Mk. II beside TS's voxels, posed alike, from any direction (shape and layout checks while
modelling).  python3 hview.py out.png hf 'az,el;az,el;...' [px] [sections]"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import rc
import hmec2 as H
import hposed as HP

BOX = np.array([[x, y, z] for x in (-30, 36) for y in (-17, 17) for z in (-1, 32)], float)
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
PALETTE = {}


def comp_colour(c):
    if c in H.HOUSE:
        return np.array([40, 200, 40.])
    named = {H.HULL: (214, 168, 74), H.KEEL: (190, 150, 66), H.RBOX: (214, 168, 74), H.HOUSING: (214, 168, 74),
             H.BAY: (150, 150, 156), H.BAYPOST: (200, 156, 70), H.HATCH: (120, 96, 56), H.RPOD_IN: (40, 40, 44),
             H.SPOD_IN: (140, 140, 146), H.HIPBRG: (60, 60, 64), H.HIPCAP: (150, 150, 156), H.RHIP: (150, 150, 156),
             H.RAILBED: (110, 88, 50), H.RAIL: (220, 220, 226), H.GROOVE: (50, 44, 34), H.BREECH: (150, 150, 156),
             H.FLANGE: (190, 150, 66), H.SIDEREC: (150, 150, 156), H.MUZZLE: (170, 170, 176), H.CHIN: (150, 150, 156),
             H.CHINTIP: (40, 40, 44), H.THIGH: (112, 90, 50), H.KNEEPIN: (70, 70, 74), H.SHIN: (150, 150, 156),
             H.GUARD_A: (214, 168, 74), H.ANKLE: (60, 60, 64), H.TOE: (214, 168, 74), H.HUB: (180, 140, 60),
             H.PISTON: (190, 190, 196), H.SLEEVE: (110, 110, 116), H.BOLT: (70, 70, 74),
             H.VISOR: (214, 168, 74), H.TURRET: (150, 150, 156), H.LAMPHOUSE: (70, 70, 74),
             H.LAMP: (255, 246, 214)}
    return np.array(named.get(c, (255, 0, 255)), float)


def basis(az, el):
    az, el = np.deg2rad(az), np.deg2rad(el)
    c = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    f = -c
    right = np.cross(f, (0, 0, 1.0)); right /= np.linalg.norm(right)
    ups = np.cross(right, f)
    return c, f, right, ups


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


def render_voxels(hf, az, el, px, secs=None):
    c, f, right, ups = basis(az, el)
    x0, y0, W, H_ = frame_box(az, el, px)
    L = np.array([0.35, -0.45, 0.82]); L /= np.linalg.norm(L)
    polys = []
    for i, s in enumerate(HP.SECS):
        if secs is not None and i not in secs:
            continue
        A, b = HP.sec_affine(i, hf)
        col = s['col']; occ = col >= 0
        for n, corners in HP.FACES.items():
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
                polys.append((pts.mean(0) @ f, pts, tuple(int(v) for v in np.clip(HP.PAL[col[x, y, z]] * shade, 0, 255))))
    polys.sort(key=lambda t: -t[0])
    im = Image.new('RGB', (W, H_), (40, 42, 38))
    d = ImageDraw.Draw(im)
    for depth, pts, rgb in polys:
        q = [((p @ right - x0) * px + 20, (-(p @ ups) - y0) * px + 20) for p in pts]
        d.polygon(q, fill=rgb)
    return im


def sheet(hf, views, px=8, secs=None, m=None):
    m = m if m is not None else H.model()
    if secs is not None:
        m = {k: v for k, v in m.items() if k in secs}
    parts, _, _ = H.posed(m, hf)
    rows = []
    for az, el in views:
        a = render_voxels(hf, az, el, px, secs); b = render_model(parts, az, el, px)
        row = Image.new('RGB', (a.width + b.width + 6, a.height), (20, 20, 20))
        row.paste(a, (0, 0)); row.paste(b, (a.width + 6, 0))
        ImageDraw.Draw(row).text((6, 4), 'TS voxels  hf %d  az %g el %g' % (hf, az, el), font=FONT, fill=(230, 230, 210))
        ImageDraw.Draw(row).text((a.width + 12, 4), 'v2 model', font=FONT, fill=(230, 230, 210))
        rows.append(row)
    W = max(r.width for r in rows); Ht = sum(r.height for r in rows)
    out = Image.new('RGB', (W, Ht), (20, 20, 20))
    y = 0
    for r in rows:
        out.paste(r, (0, y)); y += r.height
    return out


if __name__ == '__main__':
    out, hf = sys.argv[1], int(sys.argv[2])
    views = [tuple(float(v) for v in s.split(',')) for s in sys.argv[3].split(';')]
    px = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    secs = [int(a) for a in sys.argv[5].split(',')] if len(sys.argv) > 5 else None
    sheet(hf, views, px, secs).save(out)
