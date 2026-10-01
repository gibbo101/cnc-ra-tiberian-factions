"""The Silo through brender: TS angle at the mod's scale and place (in-mod/tssilo-0000.png: TS's frame x3.73,
TS px (0, 0) at canvas (-32, -137)), canvas 256x256; RA grid: the 2x2 plot on a 256x256 canvas."""
import sys, time
import numpy as np
import brender as BR, silo as SL, silomat as SM, silodamage as SD

BLD = BR.Building(SL, SM, SD, iso_k=3.73, iso_o=(-32.0, -137.0), plot=(256, 256), head=0, plot_cells=(2, 2),
                  iso_size=(256, 256), bounds=((-180, 180), (-180, 180), 120), zmax=120.0)
LAYOUT = {'iso': 'ts', 'ra': 'ra'}


class SiloPrep(BR.Prep):
    """the layout per view: where TS draws it (TS angle), centred on the 2x2 (RA grid)."""
    def __init__(self, bld, view_, vname='iso', **kw):
        super().__init__(bld, view_, layout=LAYOUT[vname], **kw)

if __name__ == '__main__':
    ss = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    level = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    fill = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    for name in ('iso', 'ra'):
        t0 = time.time()
        v = BLD.view(name, ss)
        pr = SiloPrep(BLD, v, vname=name, level=level)
        img = pr.frame(fill=fill)
        img.save(f'/home/claude/work/scratch/silo-{name}{"-d%d" % level if level else ""}{"-f" if fill else ""}.png')
        a = np.array(img)[..., 3]
        ys, xs = np.nonzero(a > 20)
        print(name, img.size, '%.1fs' % (time.time() - t0), 'bbox x', xs.min(), xs.max(), 'y', ys.min(), ys.max())
