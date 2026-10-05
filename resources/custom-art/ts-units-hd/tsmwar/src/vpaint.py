"""vpaint.py - the paint check: TS's voxel drawn flat in the mod's camera in its palette classes (face by face, far
to near) against the model's albedo (mwarmat's paint, before light) in the same classes, per pixel: a table of how
TS's classes come out in the model, and a sheet of TS's classes beside the model's with the mismatches marked.
    python3 vpaint.py out.png [frames] [zoom]"""
import sys
from collections import Counter
import numpy as np
from PIL import Image, ImageDraw
import rc, rcrender as RR
import mwarmodel as T, mwarmat as MM
from mwarcam import flat_cam, camera, unit_to_world, GZ, CANVAS
from mwarrender import find_window, BOUNDS
import mvox

SS = 2
F = T.F
s = mvox.SECS['mwar'][0]
col = s['col']
occ = col >= 0
R0, t0 = F.pose()
DIRS = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
CORN = {(1, 0, 0): [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)], (-1, 0, 0): [(0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)],
        (0, 1, 0): [(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)], (0, -1, 0): [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)],
        (0, 0, 1): [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)], (0, 0, -1): [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]}

# coarse classes, by TS palette index (and the model's albedo by brightness and hue, the paint scaled as TS's x1.257)
CLS = ['house', 'light', 'grey', 'dark', 'black', 'olive', 'blue', 'other']
SHOW = {'house': (40, 200, 40), 'light': (225, 225, 225), 'grey': (150, 150, 150), 'dark': (90, 90, 90),
        'black': (20, 20, 20), 'olive': (130, 120, 60), 'blue': (110, 110, 190), 'other': (255, 0, 255)}


def ts_class(i):
    if 16 <= i <= 31: return 'house'
    if i in (14, 15) or 33 <= i <= 47: return 'light'
    if 48 <= i <= 51: return 'grey'
    if i == 13 or 52 <= i <= 56: return 'dark'
    if 57 <= i <= 63 or i in (166, 167): return 'black'
    if 72 <= i <= 79 or 116 <= i <= 143: return 'olive'
    if 88 <= i <= 95: return 'blue'
    return 'other'


def alb_class(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = (r + g + b) / 3
    out = np.full(a.shape[:2], 'other', dtype=object)
    out[lum >= 152] = 'light'
    out[(lum >= 112) & (lum < 152)] = 'grey'
    out[(lum >= 58) & (lum < 112)] = 'dark'
    out[lum < 58] = 'black'
    out[(b - r > 18)] = 'blue'
    out[(r - b > 18) & (g > b)] = 'olive'
    out[(g > 1.6 * np.maximum(r, b)) & (g > 40)] = 'house'
    return out


def ts_map(k):
    Mx = unit_to_world(k)
    Rw, tw = Mx @ R0, Mx @ t0 + np.array([0.0, 0.0, -GZ])
    cam = flat_cam()
    D = cam.D
    polys = []
    P = np.pad(occ, 1)
    for n in DIRS:
        nw = Rw @ (np.array(n, float) / F.sc); nw /= np.linalg.norm(nw)
        if nw @ D >= -1e-6:
            continue
        sl = tuple(slice(1 + d, P.shape[a] - 1 + d) for a, d in enumerate(n))
        vis = occ & ~P[sl]
        cs = np.array(CORN[n], float)
        for v in np.argwhere(vis):
            q = cs + v
            w = (F.mn + q * F.sc) @ Rw.T + tw
            x, y = cam.project(w)
            polys.append((w.mean(0) @ D, list(zip(x * SS, y * SS)), CLS.index(ts_class(int(col[tuple(v)])))))
    polys.sort(key=lambda t: -t[0])
    im = Image.new('L', (CANVAS[0] * SS, CANVAS[1] * SS), 255)
    d = ImageDraw.Draw(im)
    for _, q, c in polys:
        d.polygon(q, fill=c)
    return np.array(im)[SS // 2::SS, SS // 2::SS]


def model_map(k, m):
    Mx = unit_to_world(k)
    parts, frames = T.posed(m, Mx)
    cam = camera()
    win = find_window(parts, cam)
    r = RR.RCRender(parts, cam, CANVAS, win, BOUNDS, ss=1, frames=frames, shadow_len=1.0, px_scale=1.5)
    r.pose_R = Mx @ R0
    alb, _, _ = MM.materials(r)
    cl = alb_class(alb)
    out = np.full((CANVAS[1], CANVAS[0]), 255, np.uint8)
    x0, y0, x1, y1 = r.win
    sub = np.vectorize(CLS.index)(cl).astype(np.uint8)
    sub[~r.hitmask] = 255
    out[y0:y1, x0:x1] = sub
    return out


def colourise(a):
    img = np.zeros(a.shape + (3,), np.uint8); img[:] = (96, 108, 72)
    for i, c in enumerate(CLS):
        img[a == i] = SHOW[c]
    return img


if __name__ == '__main__':
    out = sys.argv[1]
    ks = [int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else [0, 4, 8, 12, 16, 20, 24, 28]
    Z = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    m = T.model()
    tab = Counter()
    tiles = []
    crop = (40, 20, 344, 300)
    for k in ks:
        a, b = ts_map(k), model_map(k, m)
        both = (a != 255) & (b != 255)
        for i, j in zip(a[both], b[both]):
            tab[(CLS[i], CLS[j])] += 1
        ia, ib = colourise(a), colourise(b)
        mis = both & (a != b)
        ic = ib.copy(); ic[mis] = (255, 40, 40)
        row = []
        for x in (ia, ib, ic):
            im = Image.fromarray(x).crop(crop)
            row.append(im.resize((im.width * Z, im.height * Z), Image.NEAREST))
        W, H = row[0].size
        t = Image.new('RGB', (3 * W + 8, H + 16), (20, 20, 20))
        for j, im in enumerate(row):
            t.paste(im, (j * (W + 4), 16))
        ImageDraw.Draw(t).text((4, 2), 'frame %d: TS | model | mismatches (red) %.1f%%' % (k, 100 * mis.sum() / both.sum()),
                               fill=(255, 255, 200))
        tiles.append(t)
    W, H = tiles[0].size
    S = Image.new('RGB', (W, len(tiles) * (H + 4)), (20, 20, 20))
    for i, t in enumerate(tiles):
        S.paste(t, (0, i * (H + 4)))
    S.save(out)
    print('TS class -> model class (pixels, all frames):')
    for c in CLS:
        row = {j: tab[(c, j)] for j in CLS if tab[(c, j)]}
        tot = sum(row.values())
        if tot:
            print('  %-6s %6d  ' % (c, tot) + '  '.join('%s %.0f%%' % (j, 100 * v / tot) for j, v in
                                                     sorted(row.items(), key=lambda t: -t[1])))
