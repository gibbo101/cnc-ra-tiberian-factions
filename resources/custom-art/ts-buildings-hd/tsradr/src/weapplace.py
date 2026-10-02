"""Find where the mod puts TS's war factory on its 896x672 canvas: canvas = TS px * K + O, by alpha IoU of TS's
finished build-up frame (GTWEAPMK 19 = building + bib) against the mod's TSWEAPMAKE 0018.
    python3 weapplace.py"""
import numpy as np
from PIL import Image
from scipy.signal import fftconvolve

H = '/home/claude/work/ts/ts-buildings-hd-handoff/06-TSWEAP/'


def alpha(p):
    return np.array(Image.open(p).convert('RGBA'))[..., 3].astype(np.float32) / 255.0


def search(ts_png, mod_png, Ks, show=True):
    mod = alpha(mod_png) > 0.5
    ts = Image.open(ts_png).convert('RGBA')
    best = None
    for K in Ks:
        w, h = int(round(ts.size[0] * K)), int(round(ts.size[1] * K))
        a = np.array(ts.resize((w, h), Image.BILINEAR))[..., 3] > 127
        # intersection for every integer offset: correlate mod with a
        inter = fftconvolve(mod.astype(np.float32), a[::-1, ::-1].astype(np.float32), mode='full')
        # offset (ox, oy) of a's (0,0) in mod coords: index (oy + h - 1, ox + w - 1)
        iy, ix = np.unravel_index(np.argmax(inter), inter.shape)
        I = inter[iy, ix]
        iou = I / (mod.sum() + a.sum() - I)
        oy, ox = iy - (h - 1), ix - (w - 1)
        if best is None or iou > best[0]:
            best = (iou, K, ox, oy)
        if show:
            print(f'K {K:.3f}  offset ({ox}, {oy})  IoU {iou:.4f}')
    return best


if __name__ == '__main__':
    ts = H + 'ts-original/GTWEAPMK/frames/19.png'
    mod = H + 'in-mod/tsweapmake-0018.png'
    b = search(ts, mod, np.arange(3.90, 4.40, 0.05), show=True)
    print('coarse best', b)
    b = search(ts, mod, np.arange(b[1] - 0.05, b[1] + 0.051, 0.005), show=False)
    print('fine best', b)
    # sub-pixel offset: TS px (0,0) lands at canvas O; with resize, pixel centre (x+0.5)K - 0.5 + off
    iou, K, ox, oy = b
    print('canvas = TS px * %.3f + (%.1f, %.1f)' % (K, ox + 0.5 * K - 0.5 - 0.5 * K + 0.0, oy))
