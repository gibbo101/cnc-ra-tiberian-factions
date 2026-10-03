"""The EMP Pulse Cannon through brender, both views:
  TS angle (iso): TS's own camera at the mod's scale and place on its 256x256 canvas (TS frame x3.475, TS px (0, 0) at
                  canvas (-44, -51), fitted to in-mod/tspuls-0000.png; TS's ground centre at frame px (48, 72)).
  RA grid  (ra):  RA's camera (32 degrees, looking north) on the 2x2 plot: x 0-256, its south edge HEAD + 256 px down
                  the canvas; the canvas grown by HEAD px top and bottom so the head fits."""
import os, sys, time
import numpy as np
from PIL import Image
import hd, brender as BR, puls as M

ISO_K, ISO_O, TS_GROUND = 3.475, (-44.0, -51.0), (48.0, 72.0)
HEAD = int(os.environ.get('PULS_HEAD', '32'))
CANVAS = {'iso': (256, 256), 'ra': (256, 256 + 2 * HEAD)}
PLOT = {'iso': (0, 0, 256, 256), 'ra': (0, HEAD, 256, HEAD + 256)}
WIN = {'iso': (0, 0, 256, 256), 'ra': (0, 0, 256, 256 + 2 * HEAD)}
BOUNDS = {'iso': ((-200, 200), (-200, 200), 170), 'ra': ((-200, 200), (-200, 200), 170)}
ZMAX = 170.0
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
    import pulsdamage as MD
except ImportError:
    MD = None
import pulsmat as MM
BLD = {v: Bld(M, MM, MD, bounds=BOUNDS[v], zmax=ZMAX) for v in ('iso', 'ra')}


class PulsPrep(BR.Prep):
    def __init__(self, view_, vname='iso', **kw):
        kw.setdefault('layout', LAYOUT[base(vname)])
        super().__init__(BLD[base(vname)], view_, **kw)


def prep(vname, ss, win=None, **kw):
    v = view(vname, ss, win)
    return PulsPrep(v, vname=vname, **kw), v


if __name__ == '__main__':
    ss = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    names = sys.argv[2].split(',') if len(sys.argv) > 2 else ['iso', 'ra']
    head = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] != '-' else None
    level = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    out = '/home/claude/work/scratch/puls/render'
    os.makedirs(out, exist_ok=True)
    for name in names:
        t0 = time.time()
        pr, v = prep(name, ss, level=level, head=head)
        img = on_canvas(pr.frame(), name)
        img.save(f'{out}/s-{name}-{head}-{level}.png')
        a = np.array(img)[..., 3]
        ys, xs = np.nonzero(a > 20)
        print(name, '%.1fs' % (time.time() - t0), 'bbox x', xs.min(), xs.max(), 'y', ys.min(), ys.max(), flush=True)
