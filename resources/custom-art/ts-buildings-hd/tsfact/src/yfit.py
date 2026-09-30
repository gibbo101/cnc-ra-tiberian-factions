"""Fit check: render the yard model from TS's own camera (x4 of TS's 144x144 frame) and compare it with
GTCNST frame 0: side by side, an edge overlay, and the silhouette overlap."""
import sys, time
import numpy as np
from PIL import Image, ImageDraw
import hd, yard as Y

TS = '/home/claude/work/ts/ts-buildings-hd-handoff/01-TSFACT/ts-original'
BG = (90, 100, 80, 255)
TS_PPU = 24 * np.sqrt(2) / 128           # TS native px per unit along the screen


def ts_view(scale=4, ss=2):
    return hd.View(look=(-1, -1), elev=30.0, ppu=TS_PPU * scale, size=(144 * scale, 144 * scale),
                   origin=(72 * scale, 108 * scale), margin=(16, 16), ss=ss)


def flat_render(model_kw=None, scale=4, ss=2):
    v = ts_view(scale, ss)
    t = time.time()
    r = hd.Render(lambda X, Yy, **k: Y.scene(X, Yy, **k), v, bounds=((-200, 200), (-200, 200), 200), zmax=200,
                  **(model_kw or {}))
    alb = np.zeros(r.x.shape + (3,), np.float32)
    for c, rgb in Y.FLAT.items():
        alb[r.comp == c] = rgb
    p = Y.P
    south = np.isin(r.comp, [Y.ROOF, Y.CORNICE]) & (r.ny > 0.6) & (r.z < p['crown'] - 10)
    alb[south] = Y.FLAT[Y.SWALL]
    cov = r.sky_occlusion()
    col = r.shade(alb, sky_occ=cov)
    img = r.compose(col)
    return img, r, time.time() - t


def compare(img, out, frame=0, scale=4):
    ts = Image.open(f'{TS}/GTCNST/frames/{frame:02d}.png').convert('RGBA')
    ts4 = ts.resize((144 * scale, 144 * scale), Image.NEAREST)
    a_ts = np.array(ts)[..., 3] > 0
    a_me = np.array(img.resize((144, 144), Image.BOX))[..., 3] > 200
    iou = (a_ts & a_me).sum() / max((a_ts | a_me).sum(), 1)

    def on_bg(im):
        b = Image.new('RGBA', im.size, BG); b.alpha_composite(im); return b
    L = on_bg(ts4); R_ = on_bg(img)
    # overlay: TS in the red/blue channel, ours in green edges
    ov = np.array(on_bg(ts4)).astype(float)
    me = np.array(img).astype(float)
    ov[..., :3] = ov[..., :3] * 0.55 + me[..., :3] * 0.45 * (me[..., 3:4] / 255) + ov[..., :3] * 0.45 * (1 - me[..., 3:4] / 255)
    OV = Image.fromarray(ov.clip(0, 255).astype(np.uint8))
    crop = (0, 160, 576, 576)
    W = 576
    sheet = Image.new('RGBA', (W * 3 + 16, 416 + 24), (30, 30, 30, 255))
    d = ImageDraw.Draw(sheet)
    for i, (im, lab) in enumerate(((L, 'TS GTCNST %d (x4)' % frame), (R_, 'model, TS camera'), (OV, 'blend'))):
        sheet.paste(im.crop(crop), (i * (W + 8), 24))
        d.text((i * (W + 8) + 4, 4), lab, fill=(255, 255, 0, 255))
    d.text((W * 2, 4), '   silhouette overlap %.1f%%' % (100 * iou), fill=(255, 255, 255, 255))
    sheet.convert('RGB').save(out)
    return iou


if __name__ == '__main__':
    img, r, dt = flat_render()
    print('render %.1fs' % dt)
    iou = compare(img, sys.argv[1] if len(sys.argv) > 1 else '/home/claude/work/scratch/yfit.png')
    print('overlap %.3f' % iou)
