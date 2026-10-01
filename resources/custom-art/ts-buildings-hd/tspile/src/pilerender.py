"""The Barracks through brender: TS angle at the mod's scale (TS x3.2, TS px (0, 0) at (-26, -96)), RA grid on
256x256."""
import sys, time
import numpy as np
from PIL import Image
import brender as BR, pile as PL, pilemat as PM
try:
    import piledamage as PD
except ImportError:
    PD = None

BLD = BR.Building(PL, PM, PD, iso_k=3.2, iso_o=(-26.0, -96.0), plot=(256, 256), head=0)

if __name__ == '__main__':
    ss = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    level = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    flag = int(sys.argv[3]) if len(sys.argv) > 3 else None
    for name in ('iso', 'ra'):
        t0 = time.time()
        v = BLD.view(name, ss)
        pr = BR.Prep(BLD, v, level=level, **({'flag': flag, 'flag_az': PL.P['flag_az'][name]} if flag is not None else {}))
        img = pr.frame()
        img.save(f'/home/claude/work/scratch/pile/b-{name}{"-d%d" % level if level else ""}{"-f" if flag is not None else ""}.png')
        a = np.array(img)[..., 3]
        ys, xs = np.nonzero(a > 20)
        print(name, img.size, '%.1fs' % (time.time() - t0), 'bbox x', xs.min(), xs.max(), 'y', ys.min(), ys.max())
