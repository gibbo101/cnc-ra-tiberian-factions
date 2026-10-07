"""Fit check for the Dropship Bay (gdrop.py) in TS's own camera over GTDROP's 192x144 frame:
TS | model / model edges on TS | TS edges (magenta) + TS house (cyan) on the model; silhouette and house IoU.
    python3 gdropfit.py [out.png] [scale 4] [shp GTDROP] [frame 0] [module gdrop]"""
import sys, time, importlib
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import hd

TS = '/home/claude/work/ts/ts-buildings-hd-handoff/11b-GTDROP/ts-original/'
BG = (96, 108, 72, 255)
GROUND = (96.0, 108.0)
FW, FH = 192, 144


def view(scale=4, ss=1):
    return hd.ts_view((FW * scale, FH * scale), (GROUND[0] * scale, GROUND[1] * scale), hd.TS_PPU * scale,
                      margin=(16, 16), ss=ss)


def flat(mod, scale=4, ss=1, light=True, **kw):
    v = view(scale, ss)
    r = hd.Render(lambda X, Y, **k: mod.scene(X, Y, **k), v, bounds=((-260, 260), (-260, 260), 200), zmax=200,
                  smooth_px=0.0, **kw)
    alb = np.zeros(r.x.shape + (3,), np.float32) + 128
    for c, rgb in mod.FLAT.items():
        alb[r.comp == c] = rgb
    if hasattr(mod, 'flat_extra'):
        alb = mod.flat_extra(r, alb)
    col = r.shade(alb) if light else alb
    return r.compose(col, ground=False, outline=False), r


def ts_frame(shp='GTDROP', k=0):
    return Image.open(f'{TS}{shp}/frames/{k:02d}.png').convert('RGBA')


def house_ts(shp='GTDROP', k=0):
    return np.array(Image.open(f'{TS}{shp}/house/{k:02d}.png')) > 0


def sheet(img, ts, hts, out, scale=4, r=None, mod=None, crop=(34, 48, 182, 144)):
    tsz = ts.resize((FW * scale, FH * scale), Image.NEAREST)
    a_ts = np.array(ts)[..., 3] > 0
    small = img.resize((FW, FH), Image.BOX)
    a_me = np.array(small)[..., 3] > 128
    iou = (a_ts & a_me).sum() / max((a_ts | a_me).sum(), 1)
    hm = None
    if r is not None and mod is not None:
        ss = r.view.ss
        comp = np.where(r.hitmask, r.comp, 0)
        hm_full = np.isin(comp, list(mod.HOUSE))
        hm = np.array(Image.fromarray((hm_full * 255).astype(np.uint8)).resize((FW, FH), Image.BOX)) > 127
    hiou = (hts & hm).sum() / max((hts | hm).sum(), 1) if hm is not None else 0.0

    def on_bg(im):
        b = Image.new('RGBA', im.size, BG); b.alpha_composite(im); return b.convert('RGB')
    L = on_bg(tsz); R_ = on_bg(img)
    ed = np.array(L).copy()
    if r is not None:
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
    tz = np.array(tsz)[..., 3] > 0
    te = tz & ~ndimage.binary_erosion(tz)
    hz = np.array(Image.fromarray((hts * 255).astype(np.uint8)).resize((FW * scale, FH * scale), Image.NEAREST)) > 0
    he = hz & ~ndimage.binary_erosion(hz)
    ed2 = np.array(R_).copy(); ed2[te] = (255, 0, 255); ed2[he] = (0, 255, 255)
    cr = tuple(v * scale for v in crop)
    W = cr[2] - cr[0]; Hh = cr[3] - cr[1]
    S = Image.new('RGB', (W * 2 + 8, Hh * 2 + 8 + 20), (30, 30, 30))
    d = ImageDraw.Draw(S)
    for i, im in enumerate((L, R_, Image.fromarray(ed), Image.fromarray(ed2))):
        S.paste(im.crop(cr), ((i % 2) * (W + 8), 20 + (i // 2) * (Hh + 8)))
    d.text((4, 4), f'TS | model (TS camera) / model edges on TS | TS edges (magenta) + TS house (cyan) on the model    '
                   f'silhouette {100 * iou:.1f}%  house {100 * hiou:.1f}%', fill=(255, 255, 0))
    S.save(out)
    return iou, hiou


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/-home-claude/7af62279-56cb-5238-8d9f-461835dd6a66/scratchpad/gdrop-fit.png'
    scale = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    shp = sys.argv[3] if len(sys.argv) > 3 else 'GTDROP'
    k = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    mod = importlib.import_module(sys.argv[5] if len(sys.argv) > 5 else 'gdrop')
    t = time.time()
    img, r = flat(mod, scale, level=0)
    iou, hiou = sheet(img, ts_frame(shp, k), house_ts(shp, k), out, scale, r=r, mod=mod)
    print('render %.1fs  silhouette %.3f  house %.3f' % (time.time() - t, iou, hiou))
