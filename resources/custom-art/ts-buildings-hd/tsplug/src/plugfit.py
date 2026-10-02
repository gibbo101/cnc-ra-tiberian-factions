"""Fit check for the Upgrade Center: the model in TS's own camera over TS's 144x120 frame at x`scale`, flat colours (lit),
against GTPLUG 00 (or GTPLUGMK <k>): TS | model / model edges on TS | TS's edges on the model, plus IoU; and a
silhouette difference image.
    python3 plugfit.py [out.png] [scale 6] [mk frame or -]"""
import sys, time
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import hd, plug as M
from deptfit import green, BG

TS = '/home/claude/work/ts/ts-buildings-hd-handoff/12-TSPLUG/ts-original/'
GROUND = (60.0, 90.0)
FW, FH = 144, 120


def view(scale=6, ss=1):
    return hd.ts_view((FW * scale, FH * scale), (GROUND[0] * scale, GROUND[1] * scale), hd.TS_PPU * scale,
                      margin=(16, 16), ss=ss)


def flat(scale=6, ss=1, light=True, **kw):
    v = view(scale, ss)
    r = hd.Render(lambda X, Y, **k: M.scene(X, Y, **k), v, bounds=((-260, 260), (-260, 260), 270), zmax=270,
                  smooth_px=0.0, **kw)
    alb = np.zeros(r.x.shape + (3,), np.float32) + 128
    for c, rgb in M.FLAT.items():
        alb[r.comp == c] = rgb
    col = r.shade(alb) if light else alb
    return r.compose(col, ground=False, outline=False), r


def sheet(img, ts, out, scale, r, crop=None):
    tsz = ts.resize((FW * scale, FH * scale), Image.NEAREST)
    a_ts = np.array(ts)[..., 3] > 0
    small = img.resize((FW, FH), Image.BOX)
    a_me = np.array(small)[..., 3] > 128
    iou = (a_ts & a_me).sum() / max((a_ts | a_me).sum(), 1)
    g_ts, g_me = green(ts), green(small)
    giou = (g_ts & ndimage.binary_dilation(g_me)).sum() / max(g_ts.sum(), 1)

    def on_bg(im):
        b = Image.new('RGBA', im.size, BG); b.alpha_composite(im); return b.convert('RGB')
    L = on_bg(tsz); R_ = on_bg(img)
    ed = np.array(L).copy()
    ss = r.view.ss
    comp = np.where(r.hitmask, r.comp, 0)[ss // 2::ss, ss // 2::ss][:FH * scale, :FW * scale]
    pal = np.array([(255, 0, 255), (0, 255, 255), (255, 255, 0), (255, 128, 0), (255, 255, 255), (255, 60, 60),
                    (60, 160, 255), (160, 255, 60)])
    for k in np.unique(comp):
        if k == 0:
            continue
        m = comp == k
        em = m & ~ndimage.binary_erosion(m)
        ed[em] = pal[k % len(pal)]
    gz = green(tsz)
    ge = gz & ~ndimage.binary_erosion(gz)
    tz = np.array(tsz)[..., 3] > 0
    te = tz & ~ndimage.binary_erosion(tz)
    ed2 = np.array(R_).copy(); ed2[te] = (255, 0, 255); ed2[ge] = (0, 255, 255)
    crop = crop or (0, 14 * scale, 112 * scale, 120 * scale)
    W = crop[2] - crop[0]; Hh = crop[3] - crop[1]
    S = Image.new('RGB', (W * 2 + 8, Hh * 2 + 8 + 20), (30, 30, 30))
    d = ImageDraw.Draw(S)
    for i, im in enumerate((L, R_, Image.fromarray(ed), Image.fromarray(ed2))):
        S.paste(im.crop(crop), ((i % 2) * (W + 8), 20 + (i // 2) * (Hh + 8)))
    d.text((4, 4), f'TS | model (TS camera) / model edges on TS | TS edges (magenta) + TS green (cyan) on model    '
                   f'silhouette {100 * iou:.1f}%  green {100 * giou:.1f}%', fill=(255, 255, 0))
    S.save(out)
    return iou, giou


def diff_img(img, ts, out, scale=6):
    a_ts = np.array(ts)[..., 3] > 0
    a_me = np.array(img.resize((FW, FH), Image.BOX))[..., 3] > 128
    g_ts = green(ts); g_me = green(img.resize((FW, FH), Image.BOX))
    rgb = np.zeros((FH, FW, 3), np.uint8) + np.array(BG[:3], np.uint8)
    rgb[a_ts & a_me] = (150, 150, 150); rgb[a_ts & ~a_me] = (230, 40, 40); rgb[~a_ts & a_me] = (40, 90, 230)
    rgb[g_ts & g_me] = (0, 200, 0); rgb[g_ts & ~g_me] = (240, 240, 0); rgb[~g_ts & g_me] = (0, 120, 60)
    im = Image.fromarray(rgb).resize((FW * scale, FH * scale), Image.NEAREST)
    d = ImageDraw.Draw(im)
    for k in range(0, FW, 5):
        d.line([(k * scale, 0), (k * scale, FH * scale)], fill=(70, 70, 70))
    for k in range(0, FH, 5):
        d.line([(0, k * scale), (FW * scale, k * scale)], fill=(70, 70, 70))
    for k in range(0, FW, 10):
        d.text((k * scale + 1, 1), str(k), fill=(255, 255, 0))
    for k in range(0, FH, 10):
        d.text((1, k * scale + 1), str(k), fill=(255, 255, 0))
    im.crop((0, 14 * scale, 112 * scale, 120 * scale)).save(out)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/work/scratch/plug/fit.png'
    scale = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    mk = sys.argv[3] if len(sys.argv) > 3 else '-'
    t = time.time()
    img, r = flat(scale, prog=dict(dish=0.0))
    ts = Image.open(f'{TS}GTPLUGMK/frames/{int(mk):02d}.png' if mk != '-' else f'{TS}GTPLUG/frames/00.png').convert('RGBA')
    iou, giou = sheet(img, ts, out, scale, r)
    diff_img(img, ts, out.replace('.png', '-diff.png'), scale)
    print('render %.1fs  silhouette %.3f  green %.3f' % (time.time() - t, iou, giou))
