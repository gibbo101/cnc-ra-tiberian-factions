import numpy as np
from scipy import ndimage
from carve import *
res = 0.25

def leg_blobs(step, ax=47.4, y0=55.0):
    ms = masks([k * 15 + step for k in range(8)])
    keep, g = carve(ms, 8, ax=ax, y0=y0, elev=30.0, res=res, ext=((-18, 18), (-18, 18), (-4, 36)))
    us, vs, ws = g
    rows = []
    for w in np.arange(0.5, 24.0, 0.5):
        k = int((w + 4) / res)
        sl = keep[:, :, k]
        lab, n = ndimage.label(sl)
        blobs = []
        if n:
            sizes = ndimage.sum(sl, lab, range(1, n + 1))
            for o in np.argsort(-sizes)[:3]:
                if sizes[o] < 6:
                    continue
                ii, jj = np.nonzero(lab == o + 1)
                blobs.append(dict(u=us[ii].mean(), v=vs[jj].mean(), n=int(sizes[o]),
                                  u0=us[ii].min(), u1=us[ii].max(), v0=vs[jj].min(), v1=vs[jj].max()))
        rows.append((w, blobs))
    return rows, keep, g
