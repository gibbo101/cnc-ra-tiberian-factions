"""The Radar through brender, both views:
  TS angle (iso): TS's own layout at the mod's scale and place on the mod's 256x512 canvas (TS frame x3.015, TS px
                  (0, 0) at canvas (-84, 44.75); TS's ground centre at frame px (72, 96)).
  RA grid  (ra):  RA's camera (32 degrees, looking north), TS's layout (no turn), the 2x2 plot centred in the canvas,
                  the foundation's south edge on the plot's.  The radar is tall (its antennas reach z 359): the canvas
                  grows evenly top and bottom to fit them (HEAD px each side).
The dish turns camera-relative: in the RA view it keeps TS's angle to the camera (TS's azimuths + 45 degrees)."""
import os, sys, time
import numpy as np
from PIL import Image
import hd, brender as BR, radr as M

ISO_K, ISO_O, TS_GROUND = 3.015, (-84.0, 44.75), (72.0, 96.0)
HEAD = 40                                  # extra px top and bottom of the RA canvas (256 x 512 -> 256 x 592)
CANVAS = {'iso': (256, 512), 'ra': (256, 512 + 2 * HEAD)}
PLOT = {'iso': (0, 128, 256, 384), 'ra': (0, 128 + HEAD, 256, 384 + HEAD)}
WIN = {'iso': (0, 0, 256, 512), 'ra': (0, 0, 256, 512 + 2 * HEAD)}
BOUNDS = {'iso': ((-180, 180), (-180, 180), 370), 'ra': ((-180, 180), (-180, 180), 370)}
ZMAX = 370.0
LAYOUT = {'iso': 'ts', 'ra': 'ra'}
AZ_OFF = {'iso': 0.0, 'ra': 45.0}         # the dish's azimuth offset per view (camera-relative)


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


def dish_az(vname, t):
    d = M.P['dish']
    return d['az'][0] + (d['az'][1] - d['az'][0]) * t + AZ_OFF[base(vname)]


class Bld(BR.Building):
    def scene_fn(self, level):
        if level and self.damage is not None:
            return self.damage.model(level)
        return lambda X, Y, **k: self.model.scene(X, Y, **k)


try:
    import radrdamage as MD
except ImportError:
    MD = None
try:
    import radrmat as MM
except ImportError:
    MM = None
BLD = {v: Bld(M, MM, MD, bounds=BOUNDS[v], zmax=ZMAX) for v in ('iso', 'ra')}


class RadrPrep(BR.Prep):
    def __init__(self, view_, vname='iso', **kw):
        kw.setdefault('layout', LAYOUT[base(vname)])
        super().__init__(BLD[base(vname)], view_, **kw)


def prep(vname, ss, win=None, dish=0.0, **kw):
    """dish: 0..1 along TS's sweep, or None for no dish (the base frame)."""
    v = view(vname, ss, win)
    if dish is None:
        kw.setdefault('parts', list(M.BASE_PARTS))
    else:
        kw['dish_az'] = dish_az(vname, dish)
    return RadrPrep(v, vname=vname, **kw), v


if __name__ == '__main__':
    ss = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    names = sys.argv[2].split(',') if len(sys.argv) > 2 else ['iso', 'ra']
    out = '/home/claude/work/scratch/radr/render'
    os.makedirs(out, exist_ok=True)
    for name in names:
        t0 = time.time()
        pr, v = prep(name, ss)
        img = pr.frame()
        can = on_canvas(img, name)
        can.save(f'{out}/r-{name}.png')
        a = np.array(can)[..., 3]
        ys, xs = np.nonzero(a > 20)
        print(name, can.size, '%.1fs' % (time.time() - t0), 'bbox x', xs.min(), xs.max(), 'y', ys.min(), ys.max(), flush=True)
