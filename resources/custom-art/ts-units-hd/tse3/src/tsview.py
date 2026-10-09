"""
tsview.py - a pose beside TS's frame at TS's own size, enlarged: TS's sprite, the model in its fitting colours (lit), the
model's parts each in its own colour (to read which part lands where), and the overlap (TS only red, model only blue).

    python3 tsview.py UNIT FRAMES POSE.json OUT.png [Z]      FRAMES: 98,99 (8-facing sequences: the facing from the frame)
    POSE.json: {frame: Q} or one Q for all (merged over the unit's standing pose)
"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
import rc
import inf as I

CLS_RGB = {0: (96, 104, 72), 1: (0, 200, 0), 2: (90, 100, 150), 3: (150, 190, 255), 4: (170, 170, 170), 5: (52, 52, 52),
           6: (255, 0, 0), 7: (230, 120, 30), 8: (255, 210, 95), 9: (230, 170, 140)}
PART_RGB = {'head': (255, 60, 60), 'helmet': (255, 60, 60), 'visor': (255, 160, 160), 'face': (255, 160, 160),
            'pack': (255, 150, 0), 'chest': (60, 60, 255), 'vest': (90, 90, 255), 'abdomen': (40, 40, 160),
            'pelvis': (120, 0, 160), 'belt': (200, 200, 200), 'thigh': (0, 200, 200), 'shin': (0, 120, 120),
            'knee': (0, 160, 160), 'boot': (20, 20, 20), 'uarm': (255, 0, 255), 'farm': (255, 120, 255),
            'hand': (255, 200, 255), 'toolbox': (255, 255, 0), 'lid': (200, 200, 0), 'pad': (0, 255, 0)}


def part_rgb(p, side):
    n = p.name
    for k, v in PART_RGB.items():
        if n.startswith(k):
            c = np.array(v, float)
            return tuple(int(t) for t in (c * (0.65 if side == 'r' else 1.0)))
    return (128, 128, 128)


def model_views(S, Q, f, ax, y0, win, ss=4):
    parts, dz = I.grounded(S, Q, I.facing_angle(f))
    cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
    x0, y0_, x1, y1 = win
    w, h = x1 - x0, y1 - y0_
    t, who, nrm, O = rc.render_ids(parts, cam, x0, y0_, w, h, ss=ss, zstart=80.0)
    L = np.array([-0.451, -0.551, 0.702]); L = L / np.linalg.norm(L)
    sh = 0.55 + 0.45 * np.clip(nrm @ L, 0, 1)
    cls_of = np.array([0] + [I.CLASS[p.comp] for p in parts])
    cl = cls_of[who + 1]
    rgb = np.array([CLS_RGB.get(int(c), (255, 0, 255)) for c in range(10)], float)[cl]
    rgb = np.where((cl > 0)[..., None], rgb * sh[..., None], rgb)
    # which side each part is on: its centre against the body's left-right axis (body y: to his right)
    Pz = I.Pose(S, Q, I.facing_angle(f))
    P0, B = Pz.pelvis
    P0 = P0 + np.array([0, 0, dz])
    prgb = np.zeros(who.shape + (3,), float) + np.array(CLS_RGB[0], float)
    for i, p in enumerate(parts):
        m = who == i
        if m.any():
            c = np.asarray(p.frame[0] if getattr(p, 'frame', None) is not None else p.sphere[0], float)
            side = 'r' if float((c - P0) @ B[:, 1]) > 0.3 else 'l'
            prgb[m] = np.array(part_rgb(p, side), float) * sh[m][:, None]
    def down(a):
        return a.reshape(h, ss, w, ss, -1).mean((1, 3))
    cov = down((cl > 0).astype(float)[..., None])[..., 0]
    return down(rgb), down(prgb), cov


def main():
    unit, frames, posef, out = sys.argv[1], [int(v) for v in sys.argv[2].split(',')], sys.argv[3], sys.argv[4]
    Z = int(sys.argv[5]) if len(sys.argv) > 5 else 8
    import infunit; infunit.use(unit)
    import inffit as F, infseq as SQ
    js = json.load(open('%s_shape.json' % unit))
    S = dict(F.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    P = json.load(open(posef))
    fac = {}
    for name in SQ.SEQ.get(unit, SQ.SEQ['e1']):
        try:
            for s, ks in SQ.frames_of(unit, name):
                if isinstance(ks, list):
                    for f, k in enumerate(ks):
                        fac[k] = f
        except Exception:
            pass
    rows = []
    for k in frames:
        Q = dict(js['Q']); Q.update(P.get(str(k), P) if isinstance(P, dict) and str(k) in P else P)
        f = fac[k] if k in fac else int(__import__('os').environ.get('FACING', '0'))
        a = F.ts_frame(unit, k)
        ys, xs = np.nonzero(a[..., 3] > 0)
        win = (xs.min() - 6, ys.min() - 6, xs.max() + 7, ys.max() + 7)
        x0, y0, x1, y1 = win
        ts = a[y0:y1, x0:x1]
        tsrgb = np.where((ts[..., 3] > 0)[..., None], ts[..., :3], np.array(CLS_RGB[0]))
        m_rgb, p_rgb, cov = model_views(S, Q, f, js['ax'], js['y0'], win)
        tm = ts[..., 3] > 0
        mm = cov >= 0.3
        ov = np.zeros(tm.shape + (3,)) + np.array(CLS_RGB[0])
        ov[tm & mm] = (150, 150, 150); ov[tm & ~mm] = (255, 40, 40); ov[~tm & mm] = (60, 120, 255)
        iou = (tm & mm).sum() / max((tm | mm).sum(), 1)
        tiles = []
        for img, lab in ((tsrgb, 'TS #%d f%d' % (k, f)), (m_rgb, 'model'), (p_rgb, 'parts'), (ov, 'iou %.2f' % iou)):
            im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((img.shape[1] * Z, img.shape[0] * Z),
                                                                                Image.NEAREST)
            d = ImageDraw.Draw(im)
            for x in range(0, im.size[0], Z):
                d.line([(x, 0), (x, im.size[1])], fill=(80, 86, 60))
            for y in range(0, im.size[1], Z):
                d.line([(0, y), (im.size[0], y)], fill=(80, 86, 60))
            d.text((3, 2), lab, fill=(255, 255, 0))
            tiles.append(im)
        rows.append(tiles)
    W = max(sum(t.size[0] + 4 for t in r) for r in rows)
    H = sum(max(t.size[1] for t in r) + 4 for r in rows)
    sheet = Image.new('RGB', (W, H), (20, 20, 24))
    y = 0
    for r in rows:
        x = 0
        for t in r:
            sheet.paste(t, (x, y)); x += t.size[0] + 4
        y += max(t.size[1] for t in r) + 4
    sheet.save(out)
    print(out, sheet.size)


if __name__ == '__main__':
    main()
