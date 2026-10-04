"""
infshow.py - TS's frames as colour classes beside the fitted soldier's (TS's camera), one pair per frame.

    python3 infshow.py UNIT shape.json out.png FRAMES [pose.json]     FRAMES like 0,1,2 (each frame's facing: k % 8
                                                                      unless pose.json lists the frames it was fitted on)
"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
import rc
import inf as I
import inffit as F

COL = {0: (96, 104, 72), 1: (0, 200, 0), 2: (60, 60, 96), 3: (150, 150, 230), 4: (150, 150, 150), 5: (28, 28, 28),
       6: (240, 160, 40), 7: (255, 110, 10), 8: (250, 215, 60)}


def img(c, Z):
    a = np.zeros(c.shape + (3,), np.uint8)
    for k, v in COL.items():
        a[c == k] = v
    return Image.fromarray(a).resize((c.shape[1] * Z, c.shape[0] * Z), Image.NEAREST)


def sheet(unit, S, Q, ax, y0, frames, facings, out, Z=8):
    tiles = []
    for k, f in zip(frames, facings):
        t = F.Target(unit, k, f, margin=4)
        parts, dz = I.grounded(S, Q, I.facing_angle(f))
        cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
        cl = F.model_cls(parts, cam, t.win)
        cov = (cl > 0).mean(-1)
        maj = np.zeros(cov.shape, int); best = np.zeros(cov.shape, int)
        for c in range(1, 9):
            n = (cl == c).sum(-1); better = (n > best) & (cov >= 0.5)
            maj = np.where(better, c, maj); best = np.maximum(best, np.where(cov >= 0.5, n, 0))
        A, B = img(t.cls, Z), img(maj, Z)
        # TS's outline dotted over the model's
        d = ImageDraw.Draw(B)
        m = t.mask
        for y in range(m.shape[0]):
            for x in range(m.shape[1]):
                if m[y, x] and (x == 0 or not m[y, x - 1] or x == m.shape[1] - 1 or not m[y, x + 1] or y == 0 or
                                not m[y - 1, x] or y == m.shape[0] - 1 or not m[y + 1, x]):
                    d.point((x * Z + Z // 2, y * Z + Z // 2), fill=(255, 255, 0))
        T = Image.new('RGB', (A.width * 2 + 4, A.height + 14), (30, 30, 30))
        T.paste(A, (0, 14)); T.paste(B, (A.width + 4, 14))
        ImageDraw.Draw(T).text((2, 1), '%d  iou %.2f' % (k, F.iou(S, Q, t, ax, y0)), fill=(255, 255, 0))
        tiles.append(T)
    W = sum(t.width + 6 for t in tiles); H = max(t.height for t in tiles)
    out_im = Image.new('RGB', (W, H), (20, 20, 20)); x = 0
    for t in tiles:
        out_im.paste(t, (x, 0)); x += t.width + 6
    out_im.save(out)


if __name__ == '__main__':
    unit = sys.argv[1]
    import infunit; infunit.use(unit)
    js = json.load(open(sys.argv[2]))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    Q = dict(js['Q'])
    frames = [int(v) for v in sys.argv[4].split(',')]
    facings = [k % 8 for k in frames]
    if len(sys.argv) > 5:
        pj = json.load(open(sys.argv[5])); Q.update(pj['Q'])
        facings = [pj['frames'].index(k) for k in frames]
    sheet(unit, S, Q, js['ax'], js['y0'], frames, facings, sys.argv[3])
