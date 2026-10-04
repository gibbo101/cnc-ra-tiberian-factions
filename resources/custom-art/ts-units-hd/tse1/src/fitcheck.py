"""
fitcheck.py - a check sheet for fitted frames against TS, shadows included: per frame, TS's frame as the mod draws it
(TS's shadow in it), the HD frame, and the fitted soldier in TS's own camera with his shadow (TS's light) over TS's -
grey where both have shadow, blue TS's shadow only, orange ours only.

    python3 fitcheck.py UNIT POSES.json FRAMES out.png [label]
        FRAMES: 134,135,... or 134-148
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
import rc
import infunit
import inf as I
import inffit as F
import infrender as R
import tsshadow as T
from paths import HANDOFF

ROOT = HANDOFF + '/'
BG = np.array([96, 100, 72], float)


def frames_arg(s):
    out = []
    for part in s.split(','):
        if '-' in part:
            a, b = part.split('-'); out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def on_bg(img):
    a = np.asarray(img.convert('RGBA')).astype(float)
    al = a[..., 3:4] / 255.0
    return Image.fromarray(np.clip(a[..., :3] * al + BG * (1 - al), 0, 255).astype(np.uint8))


def model_view(unit, S, Q, f, js, k, Z=4):
    ts = F.ts_frame(unit, k)
    h, w = ts.shape[:2]
    parts, dz = I.grounded(S, Q, I.facing_angle(f))
    cam = rc.Cam((0, -1), 30.0, 1.0, (js['ax'], js['y0']))
    ms = T.model_shadow(parts, cam, (0, 0, w, h), T.LS, 2, T.OFF.get(unit, (0, 0))) >= 0.5
    tss = T.ts_shadow(unit, k)
    t, who, nrm, O = rc.render_ids(parts, cam, 0, 0, w, h, ss=2, zstart=80.0)
    comps = np.array([0] + [p.comp for p in parts])[who + 1].reshape(h, 2, w, 2).transpose(0, 2, 1, 3).reshape(h, w, 4)
    body = (comps > 0).mean(-1) >= 0.5
    cl = F.model_cls(parts, cam, (0, 0, w, h), ss=2)
    img = np.zeros((h, w, 3), float) + 205
    tsb = ts[..., 3] > 0
    img[tss & ms] = (70, 70, 70)
    img[tss & ~ms] = (60, 60, 230)
    img[ms & ~tss & ~tsb] = (235, 130, 50)
    # TS's outline faint, the model's classes over
    pal = {I.GREEN: (0, 200, 0), I.NAVY: (60, 60, 120), I.LBLUE: (150, 150, 240), I.GREY: (150, 150, 150),
           I.DARK: (45, 45, 50), F.FX: (255, 200, 0), I.ORANGE: (230, 120, 20), I.YELLOW: (230, 210, 40),
           I.SKIN: (220, 160, 130)}
    mc = np.zeros((h, w), int)
    for i in range(h):
        for j in range(w):
            v = cl[i, j][cl[i, j] > 0]
            if v.size * 2 >= cl.shape[-1]:
                mc[i, j] = np.bincount(v).argmax()
    for c, col in pal.items():
        img[mc == c] = col
    edge = tsb & ~np.pad(tsb, 1)[2:, 1:-1] | tsb & ~np.pad(tsb, 1)[:-2, 1:-1] | tsb & ~np.pad(tsb, 1)[1:-1, 2:] | \
        tsb & ~np.pad(tsb, 1)[1:-1, :-2]
    img[edge & (mc == 0)] = (255, 0, 255)
    return Image.fromarray(img.astype(np.uint8)).resize((w * Z, h * Z), Image.NEAREST)


def main():
    unit, poses, fr, out = sys.argv[1:5]
    label = sys.argv[5] if len(sys.argv) > 5 else ''
    u = infunit.use(unit)
    import infall as A
    js = json.load(open('%s_shape.json' % unit))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    res = json.load(open(poses))
    rows = []
    for k in frames_arg(fr):
        v = res[str(k)]
        Q = dict(js['Q'], **v['Q']); f = int(v['facing'])
        stem = 'ts' + u['name'].lower()
        inmod = Image.open(ROOT + '%s/in-mod/%s/frames/%s-%04d.png' % (u['dir'], stem, stem, k))
        img, trim = A.render_frame(unit, S, js, k, Q, f)
        a, b = on_bg(inmod), on_bg(img)
        box = (50, 20, 230, 160)
        a = a.crop(box).resize((360, 280), Image.LANCZOS); b = b.crop(box).resize((360, 280), Image.LANCZOS)
        m = model_view(unit, S, Q, f, js, k)
        row = Image.new('RGB', (360 * 2 + m.size[0] + 20, max(280, m.size[1])), (30, 30, 30))
        row.paste(a, (0, 0)); row.paste(b, (360, 0)); row.paste(m, (740, 0))
        d = ImageDraw.Draw(row)
        d.text((4, 4), 'TS (in-mod) %d' % k, fill=(255, 255, 0)); d.text((364, 4), 'HD %d %s' % (k, label), fill=(255, 255, 0))
        d.text((744, 4), 'fit in TS cam + shadows  iou %.2f' % v.get('iou', 0), fill=(255, 255, 0))
        rows.append(row)
        print('frame', k, flush=True)
    W = max(r.size[0] for r in rows)
    sheet = Image.new('RGB', (W, sum(r.size[1] for r in rows)), (30, 30, 30))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y)); y += r.size[1]
    sheet.save(out)
    print(out, sheet.size)


if __name__ == '__main__':
    main()
