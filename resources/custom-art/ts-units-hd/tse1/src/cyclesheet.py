"""
cyclesheet.py - a sequence's fit at a glance: one row a facing, one column a step; each cell TS's frame as colour
classes beside the soldier's (TS's camera), TS's outline dotted over his, the IoU.

    python3 cyclesheet.py UNIT shape.json poses.json SEQ out.png [facings] [Z]
        poses.json: the steps' poses {step: {Q, frames}} or every frame's {frame: {Q, facing}}
"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
import rc
import inf as I
import inffit as F
import infseq as SQ
import infcheck as C
from infshow import img


def cell(unit, S, Q, ax, y0, k, f, Z, win=None):
    t = F.Target(unit, k, f, margin=4)
    if win is not None:
        t.win = win
        a = F.ts_frame(unit, k); c = F.ts_classes(a)
        x0, y0w, x1, y1 = win
        t.cls = c[y0w:y1, x0:x1]; t.mask = (t.cls > 0) & (t.cls != F.FX)
    parts, dz = I.grounded(S, Q, I.facing_angle(f))
    cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
    cl = F.model_cls(parts, cam, t.win)
    cov = (cl > 0).mean(-1)
    maj = np.zeros(cov.shape, int); best = np.zeros(cov.shape, int)
    for c in range(1, 9):
        n = (cl == c).sum(-1); better = (n > best) & (cov >= F.COVER)
        maj = np.where(better, c, maj); best = np.maximum(best, np.where(cov >= F.COVER, n, 0))
    A, B = img(t.cls, Z), img(maj, Z)
    d = ImageDraw.Draw(B)
    m = t.mask
    H, W = m.shape
    for y in range(H):
        for x in range(W):
            if m[y, x] and (x == 0 or not m[y, x - 1] or x == W - 1 or not m[y, x + 1] or y == 0 or
                            not m[y - 1, x] or y == H - 1 or not m[y + 1, x]):
                d.point((x * Z + Z // 2, y * Z + Z // 2), fill=(255, 255, 0))
    T = Image.new('RGB', (A.width * 2 + 2, A.height + 12), (30, 30, 30))
    T.paste(A, (0, 12)); T.paste(B, (A.width + 2, 12))
    iu = F.iou(S, Q, t, ax, y0)
    ImageDraw.Draw(T).text((2, 0), '%d  %.2f' % (k, iu), fill=(255, 255, 0))
    return T, iu


def main():
    unit, shape, steps, seq, out = sys.argv[1:6]
    import infunit; infunit.use(unit)
    facings = [int(v) for v in sys.argv[6].split(',')] if len(sys.argv) > 6 and sys.argv[6] != '-' else list(range(8))
    Z = int(sys.argv[7]) if len(sys.argv) > 7 else 5
    js = json.load(open(shape))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    st = json.load(open(steps))
    rows = []
    allw = []
    win = (12, 6, 48, 36)
    for f in facings:
        row = []
        for s, frames in SQ.frames_of(unit, seq):
            Q, ff = C.pose_for(frames[f], st, js['Q'])
            T, iu = cell(unit, S, Q, js['ax'], js['y0'], frames[f], f, Z, win)
            row.append(T); allw.append(iu)
        rows.append(row)
    cw, ch = rows[0][0].width, rows[0][0].height
    im = Image.new('RGB', (len(rows[0]) * (cw + 4), len(rows) * (ch + 4) + 14), (12, 12, 12))
    for r, row in enumerate(rows):
        for c, T in enumerate(row):
            im.paste(T, (c * (cw + 4), 14 + r * (ch + 4)))
    ImageDraw.Draw(im).text((2, 1), '%s  mean IoU %.3f' % (steps, np.mean(allw)), fill=(255, 255, 255))
    im.save(out)
    print('mean iou %.3f' % np.mean(allw))


if __name__ == '__main__':
    main()
