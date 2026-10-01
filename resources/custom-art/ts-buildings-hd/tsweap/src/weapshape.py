"""Shape check renders: the model lit in flat colours, both views, beside TS.
  ts-angle: TS's camera at the mod's scale and place (canvas 896x672: TS px x 4.125 + (50, -190))
  ra-grid : RA's camera (32 degrees, looking north), turned so the door faces south, on a 3 x 4 plot
    python3 weapshape.py [ss 2] [out dir]"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw
import hd, weap as M

K, O = 4.125, (50.0, -190.0)
TSG = (108.0, 126.0)
CAN_TS = (896, 672)
CAN_RA = (416, 512)                       # the 3 x 4 plot (384 x 512) + 16 px each side (the slope's foot, its shadow)
PLOT_RA = ((CAN_RA[0] - 384) / 2, 0.0, (CAN_RA[0] + 384) / 2, 512.0)
BOUNDS = {'ts': ((-300, 300), (-300, 300), 260), 'ra': ((-300, 300), (-760, 300), 260)}


def view(name, ss):
    if name == 'ts':
        return hd.ts_view(CAN_TS, (TSG[0] * K + O[0], TSG[1] * K + O[1]), K * hd.TS_PPU, ss=ss)
    oy = PLOT_RA[3] - np.sin(np.deg2rad(32.0)) * 256.0
    return hd.ra_view(CAN_RA, ((PLOT_RA[0] + PLOT_RA[2]) / 2, oy), ss=ss)


def render(name, ss=2, pad=False, **mk):
    v = view(name, ss)
    r = hd.Render(lambda X, Y, **k: M.scene(X, Y, **k), v, bounds=BOUNDS[name], zmax=260, layout=name, pad=pad, **mk)
    alb = np.zeros(r.x.shape + (3,), np.float32) + 128
    for c, rgb in M.FLAT.items():
        alb[r.comp == c] = rgb
    occ = r.sky_occlusion(n_az=6)
    col = r.shade(alb, sky_occ=occ)
    return r.compose(col, ground=not pad, outline=True), r


if __name__ == '__main__':
    ss = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    out = sys.argv[2] if len(sys.argv) > 2 else '/home/claude/work/scratch/weap/shape'
    os.makedirs(out, exist_ok=True)
    for name in ('ts', 'ra'):
        bib, _ = render(name, ss, pad=True)
        for tag, mk in (('', {}), ('-open', dict(door=1.0))):
            bld, _ = render(name, ss, **mk)
            can = Image.new('RGBA', bld.size, (0, 0, 0, 0)); can.alpha_composite(bib); can.alpha_composite(bld)
            can.save(f'{out}/{name}{tag}.png'); bld.save(f'{out}/{name}{tag}-bld.png')
            a = np.array(bld)[..., 3]; ys, xs = np.nonzero(a > 20)
            print(name + tag, bld.size, 'bbox', xs.min(), ys.min(), xs.max(), ys.max())
        bib.save(f'{out}/{name}-bib.png')
