"""Fit check for the radar: the model in TS's own camera over TS's 144x144 frame at x`scale`, flat colours (lit),
against GTRADR 00 + GTRADR_A <k>: TS | model / model edges on TS | TS's edges on the model, plus IoU.
    python3 radrfit.py [out.png] [scale 4] [dish frame 0] [parts comma list or all]"""
import sys, time, importlib
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import hd

TS = '/home/claude/work/ts/ts-buildings-hd-handoff/08-TSHPAD/ts-original/'
BG = (96, 108, 72, 255)
GROUND = (48.0, 72.0)


def view(scale=4, ss=1):
    return hd.ts_view((96 * scale, 96 * scale), (GROUND[0] * scale, GROUND[1] * scale), hd.TS_PPU * scale,
                      margin=(16, 16), ss=ss)


def flat(mod, scale=4, ss=1, light=True, **kw):
    v = view(scale, ss)
    r = hd.Render(lambda X, Y, **k: mod.scene(X, Y, **k), v, bounds=((-200, 200), (-200, 200), 330), zmax=330,
                  smooth_px=0.0, **kw)
    alb = np.zeros(r.x.shape + (3,), np.float32) + 128
    for c, rgb in mod.FLAT.items():
        alb[r.comp == c] = rgb
    col = r.shade(alb) if light else alb
    return r.compose(col, ground=False, outline=False), r


def ts_frame(lights=None, base=0, bib=True, bld=True):
    im = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
    if bib:
        im.alpha_composite(Image.open(f'{TS}GTHPADBB/frames/{base:02d}.png').convert('RGBA'))
    if bld:
        im.alpha_composite(Image.open(f'{TS}GTHPAD/frames/{base:02d}.png').convert('RGBA'))
    if lights is not None:
        im.alpha_composite(Image.open(f'{TS}GTHPAD_A/frames/{lights:02d}.png').convert('RGBA'))
    return im


def green(a):
    a = np.asarray(a).astype(int)
    return (a[..., 3] > 100) & (a[..., 1] > a[..., 0] + 40) & (a[..., 1] > a[..., 2] + 40)


def sheet(img, ts, out, scale=4, crop=None, r=None, mod=None):
    tsz = ts.resize((96 * scale, 96 * scale), Image.LANCZOS)
    a_ts = np.array(ts)[..., 3] > 0
    small = img.resize((96, 96), Image.BOX)
    a_me = np.array(small)[..., 3] > 128
    iou = (a_ts & a_me).sum() / max((a_ts | a_me).sum(), 1)
    g_ts, g_me = green(ts), green(small)
    giou = (g_ts & ndimage.binary_dilation(g_me)).sum() / max(g_ts.sum(), 1)

    def on_bg(im):
        b = Image.new('RGBA', im.size, BG); b.alpha_composite(im); return b.convert('RGB')
    L = on_bg(tsz); R_ = on_bg(img)
    ed = np.array(L).copy()
    if r is not None:
        # every component's edges in its own colour
        ss = r.view.ss
        comp = np.where(r.hitmask, r.comp, 0)[ss // 2::ss, ss // 2::ss][:96 * scale, :96 * scale]
        pal = np.array([(255, 0, 255), (0, 255, 255), (255, 255, 0), (255, 128, 0), (255, 255, 255), (255, 60, 60),
                        (60, 160, 255), (160, 255, 60)])
        e = np.zeros(comp.shape, bool)
        for k in np.unique(comp):
            if k == 0:
                continue
            m = comp == k
            em = m & ~ndimage.binary_erosion(m)
            ed[em] = pal[k % len(pal)]
    else:
        me = np.array(img)[..., 3] > 128
        e = me & ~ndimage.binary_erosion(me)
        ed[e] = (255, 0, 255)
    gz = green(tsz)
    ge = gz & ~ndimage.binary_erosion(gz)
    tz = np.array(tsz)[..., 3] > 0
    te = tz & ~ndimage.binary_erosion(tz)
    ed2 = np.array(R_).copy(); ed2[te] = (255, 0, 255); ed2[ge] = (0, 255, 255)
    crop = crop or (0, 24 * scale, 92 * scale, 94 * scale)
    if isinstance(crop, str):
        crop = tuple(int(v) * scale for v in crop.split(','))
    W = crop[2] - crop[0]; Hh = crop[3] - crop[1]
    S = Image.new('RGB', (W * 2 + 8, Hh * 2 + 8 + 20), (30, 30, 30))
    d = ImageDraw.Draw(S)
    for i, im in enumerate((L, R_, Image.fromarray(ed), Image.fromarray(ed2))):
        S.paste(im.crop(crop), ((i % 2) * (W + 8), 20 + (i // 2) * (Hh + 8)))
    d.text((4, 4), f'TS | model (TS camera) / model edges on TS | TS edges (magenta) + TS green (cyan) on model    '
                   f'silhouette {100 * iou:.1f}%  green {100 * giou:.1f}%', fill=(255, 255, 0))
    S.save(out)
    return iou, giou


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/work/scratch/hpad/fit.png'
    scale = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    dk = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    parts = None if len(sys.argv) <= 4 or sys.argv[4] == 'all' else sys.argv[4].split(',')
    crop = sys.argv[5] if len(sys.argv) > 5 else None
    mod = importlib.import_module('hpad')
    t = time.time()
    kw = dict(level=dk)
    if parts:
        kw['parts'] = parts
    img, r = flat(mod, scale, **kw)
    ts = ts_frame(None, base=dk, bib=(not parts) or ('pad' in parts), bld=(not parts) or any(p_ != 'pad' for p_ in parts))
    iou, giou = sheet(img, ts, out, scale, crop=crop, r=r, mod=mod)
    print('render %.1fs  silhouette %.3f  green %.3f' % (time.time() - t, iou, giou))
