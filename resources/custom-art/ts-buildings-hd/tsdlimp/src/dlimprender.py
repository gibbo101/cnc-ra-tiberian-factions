"""The Limpet Mine (DLIMPET) through brender, both views on the mod's 256x256 canvas (the cell at x 64-192, y 64-192,
its ground centre at (128, 128)):
  TS angle (iso): TS's own layout at the mod's scale and place (TS frame x3.93, TS px (0, 0) at canvas (-60, -30):
                  TS's cell centre (48, 48) on (128.6, 158.6); fitted to in-mod/tsdlimp-0000 (0.873))
  RA grid  (ra):  RA's camera (32 degrees, looking north), the cell's ground centre on (128, 128)."""
import os, sys, time
import numpy as np
from PIL import Image
import hd, brender as BR, dlimp as M, dlimpmat as MM

ISO_K, ISO_O, TS_GROUND = 3.93, (-60.0, -30.0), (48.0, 48.0)
CANVAS = {'iso': (256, 256), 'ra': (256, 256)}
WIN = {'iso': (0, 0, 256, 256), 'ra': (0, 0, 256, 256)}
BOUNDS = {'iso': ((-140, 140), (-140, 140), 140), 'ra': ((-140, 140), (-140, 140), 140)}
ZMAX = 140.0
LAYOUT = {'iso': 'ts', 'ra': 'ra'}


def base(vname):
    return vname.split('-')[0]


def canvas_of(vname):
    return CANVAS[base(vname)]


def origin(vname):
    if base(vname) == 'iso':
        return TS_GROUND[0] * ISO_K + ISO_O[0], TS_GROUND[1] * ISO_K + ISO_O[1]
    return 128.0, 128.0


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
    import dlimpdamage as MD
except ImportError:
    MD = None
BLD = {v: Bld(M, MM, MD, bounds=BOUNDS[v], zmax=ZMAX) for v in ('iso', 'ra')}


class DlimpPrep(BR.Prep):
    def __init__(self, view_, vname='iso', **kw):
        kw.setdefault('layout', LAYOUT[base(vname)])
        super().__init__(BLD[base(vname)], view_, **kw)


def prep(vname, ss, win=None, **kw):
    v = view(vname, ss, win)
    return DlimpPrep(v, vname=vname, **kw), v
