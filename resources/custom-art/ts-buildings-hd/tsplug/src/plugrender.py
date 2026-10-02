"""The Upgrade Center through brender, both views:
  TS angle (iso): TS's own layout at the mod's scale and place on the mod's 384x384 canvas (TS frame x3.695, TS px (0, 0)
                  at canvas (-15, -112); TS's ground centre at frame px (60, 90)).  Like the mod's frames now, the
                  tallest antennas run off the canvas's top.
  RA grid  (ra):  RA's camera (32 degrees, looking north), turned a quarter (TS east -> RA south: the ramp and pipes to the
                  camera) to sit on the 3x2 plot; the plot x 0-384, its south edge HEAD + 256 px down the canvas; the
                  canvas grown by HEAD px top and bottom so the tallest antenna fits."""
import os, sys, time
import numpy as np
from PIL import Image
import hd, brender as BR, plug as M

ISO_K, ISO_O, TS_GROUND = 3.695, (-15.0, -112.0), (60.0, 90.0)
HEAD = int(os.environ.get('PLUG_HEAD', '32'))
CANVAS = {'iso': (384, 384), 'ra': (384, 256 + 2 * HEAD)}
PLOT = {'iso': (0, 64, 384, 320), 'ra': (0, HEAD, 384, HEAD + 256)}
WIN = {'iso': (0, 0, 384, 384), 'ra': (0, 0, 384, 256 + 2 * HEAD)}
BOUNDS = {'iso': ((-280, 280), (-280, 280), 270), 'ra': ((-280, 280), (-280, 280), 270)}
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
    return (x0 + x1) / 2.0, y1 - np.sin(np.deg2rad(32.0)) * 128.0


def view(vname, ss=hd.SS, win=None):
    x0, y0, x1, y1 = win or WIN[base(vname)]
    ox, oy = origin(vname)
    if base(vname) == 'iso':
        return hd.ts_view((x1 - x0, y1 - y0), (ox - x0, oy - y0), ISO_K * hd.TS_PPU, ss=ss)
    return hd.ra_view((x1 - x0, y1 - y0), (ox - x0, oy - y0), ss=ss)


def on_canvas(img, vname, win=None):
    x0, y0, x1, y1 = win or WIN[base(vname)]
    can = Image.new(img.mode, canvas_of(vname), (0,) * len(img.getbands()))
    can.paste(img, (x0, y0))
    return can


class Bld(BR.Building):
    def scene_fn(self, level):
        if level and self.damage is not None:
            return self.damage.model(level)
        return lambda X, Y, **k: self.model.scene(X, Y, **k)


try:
    import plugdamage as MD
except ImportError:
    MD = None
import plugmat as MM
BLD = {v: Bld(M, MM, MD, bounds=BOUNDS[v], zmax=ZMAX) for v in ('iso', 'ra')}


class PlugPrep(BR.Prep):
    def __init__(self, view_, vname='iso', **kw):
        kw.setdefault('layout', LAYOUT[base(vname)])
        kw.setdefault('shadow_mk', {'shadow': True})
        super().__init__(BLD[base(vname)], view_, **kw)


def prep(vname, ss, win=None, **kw):
    v = view(vname, ss, win)
    return PlugPrep(v, vname=vname, **kw), v


if __name__ == '__main__':
    ss = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    names = sys.argv[2].split(',') if len(sys.argv) > 2 else ['iso', 'ra']
    level = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    out = '/home/claude/work/scratch/plug/render'
    os.makedirs(out, exist_ok=True)
    for name in names:
        t0 = time.time()
        lay = name.split(':')
        pr, v = prep(lay[0], ss, level=level, **({'layout': lay[1]} if len(lay) > 1 else {}))
        img = on_canvas(pr.frame(), lay[0])
        img.save(f'{out}/s-{name.replace(":", "-")}-{level}.png')
        a = np.array(img)[..., 3]
        ys, xs = np.nonzero(a > 20)
        print(name, '%.1fs' % (time.time() - t0), 'bbox x', xs.min(), xs.max(), 'y', ys.min(), ys.max(), flush=True)
