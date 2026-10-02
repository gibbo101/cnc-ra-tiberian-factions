"""The Dropship Bay (TSDROP: the Service Depot's pad alone, as the mod has it) through brender, both views:
  TS angle (iso): TS's own camera at the mod's scale and place on its 768x512 canvas (TS frame x10.47, TS px (0, 0)
                  at canvas (-360, -923), fitted to in-mod/tsdrop-0000.png; TS's ground centre at frame px (72, 108)).
                  The mod draws the bay at 2.36 times the depot's scale, so the pad fills the canvas's width.
  RA grid  (ra):  RA's camera (32 degrees, looking north), the pad turned as the depot's (TS's west at the back) and
                  centred on the 3x3 plot (x 192-576, y 64-448 of the 768x512 canvas)."""
import os, sys, time
import numpy as np
from PIL import Image
import hd, brender as BR, dept as M

ISO_K, ISO_O, TS_GROUND = 10.47, (-360.0, -923.0), (72.0, 108.0)
CANVAS = {'iso': (768, 512), 'ra': (768, 512)}
PLOT = {'iso': (192, 64, 576, 448), 'ra': (192, 64, 576, 448)}
WIN = {'iso': (0, 0, 768, 512), 'ra': (160, 160, 608, 480)}
BOUNDS = {'iso': ((-180, 180), (-180, 180), 40), 'ra': ((-180, 180), (-180, 180), 40)}
ZMAX = 40.0
LAYOUT = {'iso': 'drop-ts', 'ra': 'drop-ra'}


def base(vname):
    return vname.split('-')[0]


def canvas_of(vname):
    return CANVAS[base(vname)]


def origin(vname):
    if base(vname) == 'iso':
        return TS_GROUND[0] * ISO_K + ISO_O[0], TS_GROUND[1] * ISO_K + ISO_O[1]
    x0, y0, x1, y1 = PLOT['ra']
    return (x0 + x1) / 2.0, y1 - np.sin(np.deg2rad(32.0)) * 192.0


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


import deptdamage as MD, deptmat as MM
BLD = {v: Bld(M, MM, MD, bounds=BOUNDS[v], zmax=ZMAX) for v in ('iso', 'ra')}


class DropPrep(BR.Prep):
    def __init__(self, view_, vname='iso', **kw):
        kw.setdefault('layout', LAYOUT[base(vname)])
        kw.setdefault('pad', True)
        super().__init__(BLD[base(vname)], view_, **kw)


def prep(vname, ss, win=None, **kw):
    v = view(vname, ss, win)
    return DropPrep(v, vname=vname, **kw), v


if __name__ == '__main__':
    ss = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    names = sys.argv[2].split(',') if len(sys.argv) > 2 else ['iso', 'ra']
    lv = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    out = '/home/claude/work/scratch/dept/render'
    os.makedirs(out, exist_ok=True)
    for name in names:
        t0 = time.time()
        pr, v = prep(name, ss, level=lv)
        img = on_canvas(pr.frame(), name)
        img.save(f'{out}/drop-{name}-{lv}.png')
        print(name, '%.1fs' % (time.time() - t0), flush=True)
