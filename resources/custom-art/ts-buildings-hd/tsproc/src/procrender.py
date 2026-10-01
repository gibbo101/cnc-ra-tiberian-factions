"""The Tiberium Refinery through brender, both views on the mod's 736x928 canvas (the plot at x 112-624, y 272-656):
  TS angle: TS's own layout at the mod's scale and place (TS frame x4.1, TS px (0, 0) at canvas (-69.4, -44.7); TS's
            ground centre at frame px (108, 126)).
  RA grid:  RA's camera (32 degrees, looking north), TS's building the same way round on the 4x3 plot (the dock to
            the east), the foundation's south edge on the plot's south edge.
Both are rendered in a window of the canvas that holds the building and its shadow, then placed on the canvas."""
import os, sys, time
import numpy as np
from PIL import Image
import hd, brender as BR, proc as PR, procmat as PM, procdamage as PD

CANVAS = (736, 928)
PLOT = (112, 272, 624, 656)
ISO_K, ISO_O, TS_GROUND = 4.1, (-69.4, -44.7), (108.0, 126.0)
WIN = {'iso': (88, 128, 604, 552), 'ra': (66, 292, 594, 672),      # x0, y0, x1, y1 on the canvas
       'iso-bib': (200, 380, 664, 624), 'ra-bib': (340, 440, 648, 672),
       'ra22': (90, 230, 640, 670), 'ra22-bib': (280, 430, 640, 670)}
# RA grid turned 22.5 degrees like EA's refineries (two of the harvester's 32 facings, so a docked truck faces on one
# of its own frames): scaled to keep the skirt and bib inside the plot's columns, the bib's south edge on the plot's.
RA22 = dict(yaw=22.5, scale=0.935, origin=(369.0, 534.5))
BOUNDS = ((-300, 300), (-230, 230), 270)
ZMAX = 270.0


def origin(vname):
    if vname == 'ra22':
        return RA22['origin']
    if vname == 'iso':
        return TS_GROUND[0] * ISO_K + ISO_O[0], TS_GROUND[1] * ISO_K + ISO_O[1]
    return (PLOT[0] + PLOT[2]) / 2.0, PLOT[3] - np.sin(np.deg2rad(32.0)) * 192.0


def view(vname, ss=hd.SS, win=None):
    x0, y0, x1, y1 = win or WIN[vname]
    ox, oy = origin(vname.split('-')[0])
    if vname.startswith('iso'):
        return hd.ts_view((x1 - x0, y1 - y0), (ox - x0, oy - y0), ISO_K * hd.TS_PPU, ss=ss)
    if vname.startswith('ra22'):
        th = np.deg2rad(RA22['yaw'])
        return hd.View((-np.sin(th), -np.cos(th)), 32.0, RA22['scale'], (x1 - x0, y1 - y0), (ox - x0, oy - y0),
                       margin=(64, 64), ss=ss)
    return hd.ra_view((x1 - x0, y1 - y0), (ox - x0, oy - y0), ss=ss)


def on_canvas(img, vname, win=None):
    x0, y0, x1, y1 = win or WIN[vname]
    can = Image.new(img.mode, CANVAS, (0,) * len(img.getbands()))
    can.paste(img, (x0, y0))
    return can


LAYOUT = {'iso': 'ts', 'ra': 'ra', 'iso-bib': 'ts', 'ra-bib': 'ra', 'ra22': 'ra', 'ra22-bib': 'ra'}
BLD = BR.Building(PR, PM, PD, bounds=BOUNDS, zmax=ZMAX)


class ProcPrep(BR.Prep):
    def __init__(self, bld, view_, vname='iso', **kw):
        kw.setdefault('layout', LAYOUT[vname])
        super().__init__(bld, view_, **kw)

    def shade(self, **kw):
        col, tm = super().shade(**kw)
        core = getattr(self.r, 'lamp_core', None)
        if core is not None:
            tm = tm * (1.0 - 0.85 * core)
        return col, tm


if __name__ == '__main__':
    ss = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    names = sys.argv[2].split(',') if len(sys.argv) > 2 else ['iso', 'ra']
    os.makedirs('/home/claude/work/scratch/proc', exist_ok=True)
    for name in names:
        t0 = time.time()
        v = view(name, ss)
        pr = ProcPrep(BLD, v, vname=name)
        img = pr.frame()
        can = on_canvas(img, name)
        can.save(f'/home/claude/work/scratch/proc/p-{name}.png')
        pb = ProcPrep(BLD, v, vname=name, pad=True)
        bib = on_canvas(pb.frame(ground=False, outline=False) if False else pb.r.compose(pb.shade()[0], ground=False, outline=False), name)
        bib.save(f'/home/claude/work/scratch/proc/p-{name}-bib.png')
        a = np.array(can)[..., 3]
        ys, xs = np.nonzero(a > 20)
        print(name, can.size, '%.1fs' % (time.time() - t0), 'bbox x', xs.min(), xs.max(), 'y', ys.min(), ys.max())
