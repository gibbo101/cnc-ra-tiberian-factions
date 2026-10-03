"""The Firestorm Wall Section (GAFSDF) through brender, both views on the mod's 176x320 canvas (the Component Tower's:
the cell at x 24-152, y 96-224, its ground centre at (88, 160)):
  TS angle (iso): TS's own camera; TS's frame x3.5 (the cell's diamond 168 px wide, inside the canvas), TS px (0, 0) at
                  canvas (4, 34) (TS's cell centre (24, 36) on the canvas's (88, 160)).
  RA grid  (ra):  RA's wall view (the GDI wall's and the gates': looking north, the ground not foreshortened, heights
                  up 0.6 px per unit), so sections join edge to edge on RA's square grid; the cell's ground centre on
                  (88, 160).  Rendered with a true camera at 59.04 degrees (cos/sin = 0.6) and stretched upright by
                  1/sin, which is exactly that projection."""
import os, sys, time
import numpy as np
from PIL import Image
import hd, brender as BR, fsdf as M, fsdfmat as MM

ISO_K, ISO_O, TS_GROUND = 3.5, (4.0, 34.0), (24.0, 36.0)
CANVAS = {'iso': (176, 320), 'ra': (176, 320)}
WIN = {'iso': (0, 0, 176, 320), 'ra': (0, 0, 176, 320)}
BOUNDS = {'iso': ((-90, 90), (-90, 90), 40), 'ra': ((-90, 90), (-90, 90), 40)}
ZMAX = 40.0
OBL = np.degrees(np.arctan2(1.0, 0.6))          # the oblique wall view: cos/sin = 0.6
SOBL = float(np.sin(np.radians(OBL)))
LAYOUT = {'iso': 'ts', 'ra': 'ra'}


def base(vname):
    return vname.split('-')[0]


def canvas_of(vname):
    return CANVAS[base(vname)]


def origin(vname):
    if base(vname) == 'iso':
        return TS_GROUND[0] * ISO_K + ISO_O[0], TS_GROUND[1] * ISO_K + ISO_O[1]
    return 88.0, 160.0


def view(vname, ss=hd.SS, win=None):
    x0, y0, x1, y1 = win or WIN[vname]
    ox, oy = origin(vname)
    if base(vname) == 'iso':
        return hd.ts_view((x1 - x0, y1 - y0), (ox - x0, oy - y0), ISO_K * hd.TS_PPU, ss=ss)
    h = int(round((y1 - y0) * SOBL))
    return hd.View((0, -1), OBL, 1.0, (x1 - x0, h), (ox - x0, (oy - y0) * SOBL), margin=(48, 48), ss=ss)


def on_canvas(img, vname, win=None):
    x0, y0, x1, y1 = win or WIN[vname]
    if base(vname) == 'ra' and img.size[1] != y1 - y0:
        img = img.resize((x1 - x0, y1 - y0), Image.LANCZOS)          # upright: the oblique wall view
    can = Image.new(img.mode, canvas_of(vname), (0,) * len(img.getbands()))
    can.paste(img, (x0, y0))
    return can


class Bld(BR.Building):
    def scene_fn(self, level):
        if level and self.damage is not None:
            return self.damage.model(level)
        return lambda X, Y, **k: self.model.scene(X, Y, **k)


try:
    import fsdfdamage as MD
except ImportError:
    MD = None
BLD = {v: Bld(M, MM, MD, bounds=BOUNDS[v], zmax=ZMAX) for v in ('iso', 'ra')}


class FsdfPrep(BR.Prep):
    def __init__(self, view_, vname='iso', **kw):
        kw.setdefault('layout', LAYOUT[base(vname)])
        super().__init__(BLD[base(vname)], view_, **kw)


def prep(vname, ss, win=None, **kw):
    v = view(vname, ss, win)
    return FsdfPrep(v, vname=vname, **kw), v
