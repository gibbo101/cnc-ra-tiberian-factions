"""dreg.py - a region of the Dropship's voxels drawn as shaded cubes from several directions (dvox.draw on a copy of
the section with everything outside the box removed).
    python3 dreg.py out.png x0,x1,y0,y1,z0,z1 'az,el;az,el' [px]      (inclusive voxel index ranges)"""
import sys
import numpy as np
from PIL import Image
import dvox


def draw_region(box, views, px=14):
    s, M = dvox.SECS['hull']
    col0 = s['col']
    x0, x1, y0, y1, z0, z1 = box
    col = np.full_like(col0, -1)
    col[x0:x1 + 1, y0:y1 + 1, z0:z1 + 1] = col0[x0:x1 + 1, y0:y1 + 1, z0:z1 + 1]
    s2 = dict(s); s2['col'] = col
    dvox.SECS['hull'] = (s2, M)
    try:
        ims = [dvox.draw(['hull'], az, el, px, 'az %g el %g  x%d-%d y%d-%d z%d-%d' % ((az, el) + tuple(box)))
               for az, el in views]
    finally:
        dvox.SECS['hull'] = (s, M)
    W = sum(i.width for i in ims); H = max(i.height for i in ims)
    out = Image.new('RGB', (W, H), (40, 42, 38)); x = 0
    for i in ims:
        out.paste(i, (x, 0)); x += i.width
    return out


if __name__ == '__main__':
    box = tuple(int(v) for v in sys.argv[2].split(','))
    views = [tuple(float(v) for v in s.split(',')) for s in sys.argv[3].split(';')]
    px = int(sys.argv[4]) if len(sys.argv) > 4 else 14
    draw_region(box, views, px).save(sys.argv[1])
