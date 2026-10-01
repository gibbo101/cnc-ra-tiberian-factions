"""The Tech Center through brender.
  TS angle: TS's own layout at the mod's scale (TS x3.73, TS px (0, 0) at (-220, -109.5); TS's ground centre at
            frame px (108, 90)), canvas 384x384.
  RA grid:  'rot' (default): turned long and thin on a 2x3, the plot at y 64-448 of a 256x512 canvas;
            'ts3x2': TS's way round on the 3x2, the plot at y 64-320 of a 384x384 canvas."""
import os, sys, time
import numpy as np
import hd
import brender as BR, tech as TC, techmat as TM, techdamage as TD

BLD = BR.Building(TC, TM, TD, iso_k=3.73, iso_o=(-220.0, -109.5), ts_ground=(108, 90), plot=(384, 256), head=64,
                  plot_cells=(3, 2), iso_size=(384, 384), bounds=((-260, 260), (-200, 200), 240), zmax=240.0)
BLD_ROT = BR.Building(TC, TM, TD, plot=(256, 384), head=64, plot_cells=(2, 3),
                      bounds=((-200, 200), (-260, 260), 240), zmax=240.0)
RA = os.environ.get('TECH_RA', 'rot')            # 'rot' (2x3) or 'ts3x2'
LAYOUT = {'iso': 'ts', 'ra': 'rot' if RA == 'rot' else 'ts3', 'ra31': 'ts3', 'ra31t': 'ts3'}


# TS's way round on RA's grid as a 3x1 with the bib row in front: the plot centred in the canvas,
# the wedge's nearest corner on the plot's south edge; (yaw, scale, sideways shift) per view.
SEAT31 = {'ra31': (0.0, 1.0, 0.0), 'ra31t': (25.0, 0.99, -4.9)}
CANVAS31 = (416, 368)


def seat31_view(vname, ss):
    yaw, scale, shift = SEAT31[vname]
    th = np.deg2rad(yaw)
    T = (np.sin(th), np.cos(th))
    W, H = CANVAS31
    near = np.sin(np.deg2rad(32.0)) * (abs(T[0]) * 192.0 + abs(T[1]) * 128.0)
    return hd.View((-T[0], -T[1]), 32.0, scale, (W, H), (W / 2 + shift, H / 2 + 64 - scale * near),
                   margin=(64, 64), ss=ss)


def view(vname, ss):
    if vname in SEAT31:
        return seat31_view(vname, ss)
    if vname == 'iso':
        return BLD.view('iso', ss)
    return (BLD_ROT if RA == 'rot' else BLD).view('ra', ss)


class TechPrep(BR.Prep):
    """the layout per view; damaged: what shows through the dome's hole and GTTECH_A's light out of it."""
    def __init__(self, bld, view_, vname='iso', **kw):
        super().__init__(bld, view_, layout=LAYOUT[vname], **kw)

    def shade(self, sparks=None, **kw):
        col, tm = super().shade(sparks=sparks, **kw)
        if self.level:
            # what shows through TS's hole in the dome, then (GTTECH_A) the light out of it
            m, inner = TD.hole_interior(self.r, self.view)
            if m is not None:
                col[m] = inner
            if sparks is not None:
                flick, a, rgb = TD.hole_lights(self.r, sparks, self.view.ss)
                col = (col + flick) * (1 - a)[..., None] + rgb * a[..., None]
                tm = tm * (1 - a)
        return col, tm


if __name__ == '__main__':
    ss = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    level = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    names = sys.argv[3].split(',') if len(sys.argv) > 3 else ['iso', 'ra']
    os.makedirs('/home/claude/work/scratch/tech', exist_ok=True)
    for name in names:
        t0 = time.time()
        v = view(name, ss)
        pr = TechPrep(BLD, v, vname=name, level=level)
        img = pr.frame(**({'sparks': 2} if level else {}))
        img.save(f'/home/claude/work/scratch/tech/t-{name}{"-" + RA if name == "ra" else ""}{"-d%d" % level if level else ""}.png')
        a = np.array(img)[..., 3]
        ys, xs = np.nonzero(a > 20)
        print(name, img.size, '%.1fs' % (time.time() - t0), 'bbox x', xs.min(), xs.max(), 'y', ys.min(), ys.max())
