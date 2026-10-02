"""The Sensor Array through brender, both views:
  TS angle (iso): TS's own layout at the mod's scale and place on the mod's 256x416 canvas (TS frame x4.225, TS px (0, 0)
                  at canvas (-75, -54); TS's ground centre at frame px (48, 60)).
  RA grid  (ra):  RA's camera (32 degrees, looking north), TS's way round (not turned: the vehicle broadside, the mast at
                  its west end), the 1x1 plot x 64-192, y 144-272 of the 256x416 canvas, the foundation's south edge on
                  the plot's."""
import os, sys, time
import numpy as np
from PIL import Image
import hd, brender as BR, dpsa as M

ISO_K, ISO_O, TS_GROUND = 4.225, (-75.0, -54.0), (48.0, 60.0)
CANVAS = {'iso': (256, 416), 'ra': (256, 416)}
PLOT = {'iso': (64, 144, 192, 272), 'ra': (64, 144, 192, 272)}
WIN = {'iso': (0, 0, 256, 416), 'ra': (0, 0, 256, 416)}
BOUNDS = {'iso': ((-160, 160), (-160, 160), 200), 'ra': ((-160, 160), (-160, 160), 200)}
ZMAX = 200.0
LAYOUT = {'iso': 'ts', 'ra': 'ra'}


def base(vname):
    return vname.split('-')[0]


def canvas_of(vname):
    return CANVAS[base(vname)]


def origin(vname):
    if base(vname) == 'iso':
        return TS_GROUND[0] * ISO_K + ISO_O[0], TS_GROUND[1] * ISO_K + ISO_O[1]
    x0, y0, x1, y1 = PLOT['ra']
    return (x0 + x1) / 2.0, y1 - np.sin(np.deg2rad(32.0)) * 64.0


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
    import dpsadamage as MD
except ImportError:
    MD = None
import dpsamat as MM
BLD = {v: Bld(M, MM, MD, bounds=BOUNDS[v], zmax=ZMAX) for v in ('iso', 'ra')}


class DpsaPrep(BR.Prep):
    def __init__(self, view_, vname='iso', **kw):
        kw.setdefault('layout', LAYOUT[base(vname)])
        super().__init__(BLD[base(vname)], view_, **kw)


def prep(vname, ss, win=None, **kw):
    v = view(vname, ss, win)
    return DpsaPrep(v, vname=vname, **kw), v


if __name__ == '__main__':
    ss = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    names = sys.argv[2].split(',') if len(sys.argv) > 2 else ['iso', 'ra']
    level = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    out = '/home/claude/work/scratch/dpsa/render'
    os.makedirs(out, exist_ok=True)
    for name in names:
        t0 = time.time()
        lay = name.split(':')
        pr, v = prep(lay[0], ss, level=level, **({'layout': lay[1]} if len(lay) > 1 else {}))
        img = on_canvas(pr.frame(flash=0), lay[0])
        img.save(f'{out}/s-{name.replace(":", "-")}-{level}.png')
        a = np.array(img)[..., 3]
        ys, xs = np.nonzero(a > 20)
        print(name, '%.1fs' % (time.time() - t0), 'bbox x', xs.min(), xs.max(), 'y', ys.min(), ys.max(), flush=True)
