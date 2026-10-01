"""The War Factory through brender, both views:
  TS angle (iso): TS's own layout at the mod's scale and place on the mod's 896x672 canvas (TS frame x4.125, TS px
                  (0, 0) at canvas (50, -190); TS's ground centre at frame px (108, 126)).
  RA grid  (ra):  RA's camera (32 degrees, looking north), the building turned a quarter so the door faces south, on a
                  3 x 4 plot (384 x 512) centred in a 416 x 512 canvas, the foundation's south edge on the plot's.
Both are rendered in a window of the canvas that holds the building and its shadow, then placed on the canvas."""
import os, sys, time
import numpy as np
from PIL import Image
import hd, brender as BR, weap as M, weapmat as MM

ISO_K, ISO_O, TS_GROUND = 4.125, (50.0, -190.0), (108.0, 126.0)
CANVAS = {'iso': (896, 672), 'ra': (416, 512)}
PLOT = {'iso': (128, 144, 768, 528), 'ra': (16, 0, 400, 512)}
WIN = {'iso': (150, 56, 790, 476), 'ra': (0, 96, 416, 512),          # x0, y0, x1, y1 on the canvas
       'iso-bib': (290, 220, 800, 476), 'ra-bib': (0, 230, 416, 512)}
BOUNDS = {'iso': ((-300, 300), (-260, 260), 270), 'ra': ((-280, 280), (-580, 320), 270)}
ZMAX = 270.0
LAYOUT = {'iso': 'ts', 'ra': 'ra'}


def base(vname):
    return vname.split('-')[0]


def canvas_of(vname):
    return CANVAS[base(vname)]


def origin(vname):
    if base(vname) == 'iso':
        return TS_GROUND[0] * ISO_K + ISO_O[0], TS_GROUND[1] * ISO_K + ISO_O[1]
    x0, y0, x1, y1 = PLOT['ra']
    return (x0 + x1) / 2.0, y1 - np.sin(np.deg2rad(32.0)) * 256.0


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
    import weapdamage as MD
except ImportError:
    MD = None
BLD = {v: Bld(M, MM, MD, bounds=BOUNDS[v], zmax=ZMAX) for v in ('iso', 'ra')}


class WeapPrep(BR.Prep):
    def __init__(self, view_, vname='iso', **kw):
        kw.setdefault('layout', LAYOUT[base(vname)])
        super().__init__(BLD[base(vname)], view_, **kw)


def prep(vname, ss, win=None, **kw):
    v = view(vname, ss, win)
    return WeapPrep(v, vname=vname, **kw), v


if __name__ == '__main__':
    ss = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    names = sys.argv[2].split(',') if len(sys.argv) > 2 else ['iso', 'ra']
    out = '/home/claude/work/scratch/weap/render'
    os.makedirs(out, exist_ok=True)
    for name in names:
        t0 = time.time()
        pr, v = prep(name, ss)
        img = pr.frame()
        can = on_canvas(img, name)
        can.save(f'{out}/w-{name}.png')
        pb, vb = prep(name + '-bib', ss, pad=True)
        col, tm = pb.shade()
        bib = on_canvas(pb.r.compose(col, ground=False, outline=False), name + '-bib')
        bib.save(f'{out}/w-{name}-bib.png')
        full = bib.copy(); full.alpha_composite(can); full.save(f'{out}/w-{name}-full.png')
        a = np.array(can)[..., 3]
        ys, xs = np.nonzero(a > 20)
        print(name, can.size, '%.1fs' % (time.time() - t0), 'bbox x', xs.min(), xs.max(), 'y', ys.min(), ys.max(), flush=True)
