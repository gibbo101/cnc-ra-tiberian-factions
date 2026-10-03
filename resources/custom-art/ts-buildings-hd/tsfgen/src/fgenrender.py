"""The Firestorm Generator (GAFIRE) through brender, both views on the mod's 384x384 canvas:
  TS angle (iso): TS's own layout at the mod's scale and place (TS frame x4.04, TS px (0, 0) at canvas (-146, -137);
                  TS's ground centre at frame px (84, 90)).
  RA grid  (ra):  RA's camera (32 degrees, looking north), the same way round (the fins west, the pit east), on the 3 x 2
                  plot (384 x 256) at y 64-320, the foundation's south edge on the plot's.
Both are rendered in a window of the canvas that holds the building and its shadow, then placed on the canvas."""
import os, sys, time
import numpy as np
from PIL import Image
import hd, brender as BR, fgen as M, fgenmat as MM

ISO_K, ISO_O, TS_GROUND = 4.04, (-146.0, -137.0), (84.0, 90.0)
CANVAS = {'iso': (384, 384), 'ra': (384, 384)}
PLOT = {'iso': (0, 64, 384, 320), 'ra': (0, 64, 384, 320)}
WIN = {'iso': (0, 0, 384, 384), 'ra': (0, 0, 384, 384)}
BOUNDS = {'iso': ((-240, 240), (-200, 200), 260), 'ra': ((-240, 240), (-200, 200), 260)}
ZMAX = 260.0
LAYOUT = {'iso': 'ts', 'ra': 'ra'}


def base(vname):
    return vname.split('-')[0]


def canvas_of(vname):
    return CANVAS[base(vname)]


def origin(vname):
    if base(vname) == 'iso':
        return TS_GROUND[0] * ISO_K + ISO_O[0], TS_GROUND[1] * ISO_K + ISO_O[1]
    x0, y0, x1, y1 = PLOT['ra']
    return (x0 + x1) / 2.0, y1 - np.sin(np.deg2rad(32.0)) * 128.0


def view(vname, ss=hd.SS, win=None):
    x0, y0, x1, y1 = win or WIN[vname]
    ox, oy = origin(vname)
    if base(vname) == 'iso':
        return hd.ts_view((x1 - x0, y1 - y0), (ox - x0, oy - y0), ISO_K * hd.TS_PPU, ss=ss)
    return hd.ra_view((x1 - x0, y1 - y0), (ox - x0, oy - y0), ss=ss)


def on_canvas(img, vname, win=None):
    x0, y0, x1, y1 = win or WIN[vname]
    can = Image.new(img.mode, canvas_of(vname), (0,) * len(img.getbands()))
    can.paste(img, (x0, y0))
    return can


class Bld(BR.Building):
    def scene_fn(self, level):
        if level and self.damage is not None:
            return self.damage.model(level)
        return lambda X, Y, **k: self.model.scene(X, Y, **k)


try:
    import fgendamage as MD
except ImportError:
    MD = None
BLD = {v: Bld(M, MM, MD, bounds=BOUNDS[v], zmax=ZMAX) for v in ('iso', 'ra')}


class FgenPrep(BR.Prep):
    def __init__(self, view_, vname='iso', **kw):
        kw.setdefault('layout', LAYOUT[base(vname)])
        super().__init__(BLD[base(vname)], view_, **kw)


def prep(vname, ss, win=None, **kw):
    v = view(vname, ss, win)
    return FgenPrep(v, vname=vname, **kw), v


if __name__ == '__main__':
    ss = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    names = sys.argv[2].split(',') if len(sys.argv) > 2 else ['iso', 'ra']
    arm = float(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] != '-' else None
    out = '/home/claude/work/scratch/fgen/render'
    os.makedirs(out, exist_ok=True)
    for name in names:
        t0 = time.time()
        pr, v = prep(name, ss, arm=arm)
        img = pr.frame()
        can = on_canvas(img, name)
        tag = '' if arm is None else f'-arm{arm:g}'
        can.save(f'{out}/f-{name}{tag}.png')
        a = np.array(can)[..., 3]
        ys, xs = np.nonzero(a > 20)
        print(name, can.size, '%.1fs' % (time.time() - t0), 'bbox x', xs.min(), xs.max(), 'y', ys.min(), ys.max(), flush=True)
