"""Fit check for the refinery: render the model in TS's own camera over TS's 192x168 frame at x`scale`, flat
colours, and compare with NTREFN: TS | model / blend | outlines (model magenta on TS; TS's green cyan on the model).

    python3 procfit.py [out.png] [scale 4] [ts frame png]"""
import sys, time, importlib
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import hd

TS = '/home/claude/work/ts/ts-buildings-hd-handoff/04-TSPROC/ts-original/'
BG = (96, 108, 72, 255)
GROUND = (108.0, 126.0)            # the 4x3 foundation's ground centre in TS's frame


def view(scale=4, ss=1, size=(192, 168)):
    return hd.ts_view((size[0] * scale, size[1] * scale), (GROUND[0] * scale, GROUND[1] * scale), hd.TS_PPU * scale,
                      margin=(16, 16), ss=ss)


def flat(mod, scale=4, ss=1, light=True, **kw):
    v = view(scale, ss)
    r = hd.Render(lambda X, Y, **k: mod.scene(X, Y, **k), v, bounds=((-300, 300), (-260, 260), 260), zmax=260,
                  smooth_px=0.0, **kw)
    alb = np.zeros(r.x.shape + (3,), np.float32) + 128
    for c, rgb in mod.FLAT.items():
        alb[r.comp == c] = rgb
    col = r.shade(alb) if light else alb
    return r.compose(col, ground=False, outline=False), r


def green(a):
    a = np.asarray(a).astype(int)
    return (a[..., 3] > 100) & (a[..., 1] > a[..., 0] + 40) & (a[..., 1] > a[..., 2] + 40)


def compare(img, ts_png, out, scale=4, crop=None):
    ts = Image.open(ts_png).convert('RGBA')
    tsz = ts.resize((ts.size[0] * scale, ts.size[1] * scale), Image.NEAREST)
    a_ts = np.array(ts)[..., 3] > 0
    small = img.resize(ts.size, Image.BOX)
    a_me = np.array(small)[..., 3] > 128
    iou = (a_ts & a_me).sum() / max((a_ts | a_me).sum(), 1)
    g_ts, g_me = green(ts), green(small)
    giou = (g_ts & ndimage.binary_dilation(g_me)).sum() / max(g_ts.sum(), 1)

    def on_bg(im):
        b = Image.new('RGBA', im.size, BG); b.alpha_composite(im); return b
    L = on_bg(tsz).convert('RGB'); R_ = on_bg(img).convert('RGB')
    bl = Image.blend(L, R_, 0.5)
    me = np.array(img)[..., 3] > 128
    e = me & ~ndimage.binary_erosion(me)
    ed = np.array(L).copy(); ed[e] = (255, 0, 255)
    gz = green(tsz)
    ge = gz & ~ndimage.binary_erosion(gz)
    ed2 = np.array(R_).copy(); ed2[ge] = (0, 255, 255)
    crop = crop or (30 * scale, 36 * scale, 180 * scale, 162 * scale)
    W = crop[2] - crop[0]; Hh = crop[3] - crop[1]
    sheet = Image.new('RGB', (W * 2 + 8, Hh * 2 + 8 + 20), (30, 30, 30))
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate((L, R_, Image.fromarray(ed), Image.fromarray(ed2))):
        sheet.paste(im.crop(crop), ((i % 2) * (W + 8), 20 + (i // 2) * (Hh + 8)))
    d.text((4, 4), f'TS | model (TS camera) / model outline on TS | TS green on model    silhouette {100 * iou:.1f}%  '
                   f'green hit {100 * giou:.1f}%', fill=(255, 255, 0))
    sheet.save(out)
    return iou, giou


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/work/scratch/proc/fit.png'
    scale = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    ts_png = sys.argv[3] if len(sys.argv) > 3 else TS + 'NTREFN/frames/00.png'
    mod = importlib.import_module('proc')
    t = time.time()
    img, r = flat(mod, scale)
    iou, giou = compare(img, ts_png, out, scale)
    print('render %.1fs  silhouette %.3f  green %.3f' % (time.time() - t, iou, giou))
