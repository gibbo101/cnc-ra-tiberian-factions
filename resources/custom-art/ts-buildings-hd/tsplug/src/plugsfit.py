"""Fit check for the plugs: the building with plug K in the east socket, flat colours in TS's own camera, against GTPLUG 00
with GTPLUG_K frame t over it; crops round the socket at 10x.    python3 plugsfit.py K [t] [out.png]"""
import sys
import numpy as np
from PIL import Image, ImageDraw
import hd, plug as M, plugfit as F

T = F.TS


def run(kind, t=0, out=None, scale=10):
    v = F.view(scale, 1)
    r = hd.Render(lambda X, Y, **k: M.scene(X, Y, **k), v, bounds=((-260, 260), (-260, 260), 270), zmax=270,
                  smooth_px=0.0, prog=dict(dish=0.0), plugs=(None, kind), plug_t=t)
    alb = np.zeros(r.x.shape + (3,), np.float32) + 128
    for c, rgb in M.FLAT.items():
        alb[r.comp == c] = rgb
    img = r.compose(r.shade(alb), ground=False, outline=False)
    base = Image.open(f'{T}GTPLUG/frames/00.png').convert('RGBA')
    ov = Image.open(f'{T}GTPLUG_{kind}/frames/{t:02d}.png').convert('RGBA')
    ts = base.copy(); ts.alpha_composite(ov)
    a_ov = np.array(ov)[..., 3] > 0
    box = (30, 52, 68, 104)
    tsz = ts.resize((144 * scale, 120 * scale), Image.NEAREST)
    bg = (96, 108, 72, 255)

    def onbg(im):
        b = Image.new('RGBA', im.size, bg); b.alpha_composite(im); return b
    A = onbg(tsz).crop(tuple(c * scale for c in box))
    B = onbg(img).crop(tuple(c * scale for c in box))
    # TS's plug outline on the model
    edge = a_ov & ~np.roll(a_ov, 1, 0) | a_ov & ~np.roll(a_ov, -1, 0) | a_ov & ~np.roll(a_ov, 1, 1) | a_ov & ~np.roll(a_ov, -1, 1)
    Bd = ImageDraw.Draw(B)
    ys, xs = np.nonzero(edge)
    for y_, x_ in zip(ys, xs):
        if box[0] <= x_ < box[2] and box[1] <= y_ < box[3]:
            X0 = (x_ - box[0]) * scale; Y0 = (y_ - box[1]) * scale
            Bd.rectangle((X0 + scale // 2 - 1, Y0 + scale // 2 - 1, X0 + scale // 2 + 1, Y0 + scale // 2 + 1), fill=(255, 0, 255))
    W = Image.new('RGB', (A.width * 2 + 8, A.height), (30, 30, 30))
    W.paste(A.convert('RGB'), (0, 0)); W.paste(B.convert('RGB'), (A.width + 8, 0))
    W.save(out or f'/home/claude/work/scratch/plug/plugfit-{kind}{t}.png')


if __name__ == '__main__':
    k = sys.argv[1]; t = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    run(k, t, sys.argv[3] if len(sys.argv) > 3 else None)
