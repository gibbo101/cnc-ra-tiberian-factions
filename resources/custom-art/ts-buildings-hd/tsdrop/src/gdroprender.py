"""The Dropship Bay (GTDROP) through brender, both views, on the 768x512 canvas the mod's TSDROP has (the 3x3 plot at
x 192-576, y 64-448, its ground centre at (384, 256)):
  TS angle (iso): TS's own camera at the Upgrade Center's scale (TS frame x3.695: the block the two share comes out the
                  same size), the foundation's ground centre (TS px (96, 108)) on the canvas centre
  RA grid  (ra):  RA's camera (32 degrees, looking north), TS's way round (the ramp, the pad and the house-green slope
                  face the camera), the 3x3 plot centred"""
import os, sys
import numpy as np
from PIL import Image
import hd, brender as BR, gdrop as M

ISO_K, TS_GROUND = 3.695, (96.0, 108.0)
CANVAS = {'iso': (768, 512), 'ra': (768, 512)}
PLOT = {'iso': (192, 64, 576, 448), 'ra': (192, 64, 576, 448)}
ISO_O = (384.0 - TS_GROUND[0] * ISO_K, 256.0 - TS_GROUND[1] * ISO_K)
# the render windows: the building and its shadow with ~32 px to spare (measured: TS angle x 181-678, y 46-375; RA grid
# x 192-613, y 98-453, and the damaged one's bent pipe's shadow out to ~x 650), pasted onto the full canvas (on_canvas):
# about half the pixels, time and memory
WIN = {'iso': (150, 14, 712, 408), 'ra': (160, 66, 700, 486)}
BOUNDS = {'iso': ((-280, 280), (-280, 280), 220), 'ra': ((-280, 280), (-280, 280), 220)}
ZMAX = 220.0


def base(vname):
    return vname.split('-')[0]


def origin(vname):
    if base(vname) == 'iso':
        return TS_GROUND[0] * ISO_K + ISO_O[0], TS_GROUND[1] * ISO_K + ISO_O[1]
    x0, y0, x1, y1 = PLOT['ra']
    return (x0 + x1) / 2.0, y1 - np.sin(np.deg2rad(32.0)) * 192.0


def view(vname, ss=hd.SS, win=None):
    x0, y0, x1, y1 = win or WIN[base(vname)]
    ox, oy = origin(vname)
    if base(vname) == 'iso':
        return hd.ts_view((x1 - x0, y1 - y0), (ox - x0, oy - y0), ISO_K * hd.TS_PPU, ss=ss)
    return hd.ra_view((x1 - x0, y1 - y0), (ox - x0, oy - y0), ss=ss)


def on_canvas(img, vname, win=None):
    x0, y0, x1, y1 = win or WIN[base(vname)]
    can = Image.new(img.mode, CANVAS[base(vname)], (0,) * len(img.getbands()))
    can.paste(img, (x0, y0))
    return can


_BLD = {}


def bld(mats=None, damage=None):
    if mats is None:
        import gdropmat as mats
    if damage is None:
        import gdropdamage as damage
    key = (mats.__name__, damage.__name__)
    if key not in _BLD:
        _BLD[key] = {v: BR.Building(M, mats, damage, bounds=BOUNDS[v], zmax=ZMAX) for v in ('iso', 'ra')}
    return _BLD[key]


class DPrep(BR.Prep):
    def __init__(self, view_, vname='iso', mats=None, damage=None, level=0, **kw):
        kw.setdefault('layout', 'ts')
        kw.setdefault('shadow_mk', {'shadow': True})
        kw['dmg_level'] = level                   # (the materials read it: B's smashed bars)
        super().__init__(bld(mats, damage)[base(vname)], view_, level=level, **kw)


def prep(vname, ss, win=None, **kw):
    v = view(vname, ss, win)
    return DPrep(v, vname=vname, **kw), v
