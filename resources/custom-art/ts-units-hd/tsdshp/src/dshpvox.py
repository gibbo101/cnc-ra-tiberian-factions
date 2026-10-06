"""dshpvox.py - TS's DSHP.VXL as data for the model: the section (colours, occupancy), each x slice filled (TS's voxels
are a shell), and the half-widths of the body about its centre line (q y 21.5) per x and z, for lofting the tail and
the nose through TS's own cross-sections."""
import numpy as np
from scipy import ndimage
import dvox

S, M = dvox.SECS['hull']
COL = S['col']
OCC = COL >= 0
X, Y, Z = OCC.shape
HYC = 21.5


def filled_x():
    f = np.zeros_like(OCC)
    for x in range(X):
        f[x] = ndimage.binary_fill_holes(OCC[x])
    return f


FILL = filled_x()


def halfwidths(x, y0=8, y1=35, fill=FILL):
    """per z row of slice x (y0..y1 only): (z, a, b, hw) for rows with voxels; hw = the symmetrized half width about
    HYC (mean of the two sides, q units: voxel b spans b..b+1)."""
    out = []
    for z in range(Z):
        yy = np.nonzero(fill[x, y0:y1 + 1, z])[0] + y0
        if len(yy):
            a, b = yy.min(), yy.max()
            out.append((z, a, b, ((b + 1 - HYC) + (HYC - a)) / 2.0))
    return out


if __name__ == '__main__':
    import sys
    xs = [int(v) for v in sys.argv[1].split(',')] if len(sys.argv) > 1 else range(X)
    for x in xs:
        print(x, ' '.join('%d:%.1f' % (z, hw) for z, a, b, hw in halfwidths(x)))


# ------------------------------------------------------------------------------------- TS's shape, smoothed
def body_fill(keels=True):
    """the filled body (no pods, beams or keels) as floats: TS's slices filled, only q y 9..34 (the beams' rows at z 18..20
    over the pods' inner sides are left to the beams), the keels under the tail and the nose taken off."""
    f = FILL.astype(np.float32).copy()
    f[:, :9, :] = 0; f[:, 35:, :] = 0
    if keels:
        yy = np.abs(np.arange(Y) + 0.5 - HYC)[None, :, None]
        xx = np.arange(X)[:, None, None]; zz = np.arange(Z)[None, None, :]
        # the tail's keel (TS: x 15..25, z 3..7, 6 wide; where the body's bottom is higher than z 6)
        f[(xx >= 15) & (xx <= 20) & (zz <= 7) & (yy <= 3.6) & (FILL.sum(1, keepdims=True) * 0 == 0) &
          (zz < np.where(xx >= 18, 8, 6))] = 0
        f[(xx >= 21) & (xx <= 24) & (zz <= 5) & (yy <= 3.6)] = 0
        # the nose gear's keel (TS: x 68..86 under the nose, 3..5 wide)
        f[(xx >= 73) & (xx <= 75) & (zz <= 12) & (yy <= 3.6)] = 0
        f[(xx >= 76) & (xx <= 82) & (zz <= 11) & (yy <= 3.6)] = 0
        f[(xx >= 83) & (xx <= 87) & (zz <= 10) & (yy <= 3.6)] = 0
    return f


_G = {}


def smoothed(sig=(1.0, 0.7, 0.7), keels=True):
    key = (sig, keels)
    if key not in _G:
        _G[key] = ndimage.gaussian_filter(body_fill(keels), sig, mode='constant')
    return _G[key]


def iso_section(G, xq, zlo, zhi, dz=0.5, level=0.5, wmax=14.0):
    """the cross-section at q x = xq of the smoothed body G: [(z, hw)] where the level surface crosses, sampled every dz
    between zlo and zhi (q z), hw measured out from the centre line (both sides averaged)."""
    from scipy.ndimage import map_coordinates
    out = []
    ws = np.arange(0.0, wmax, 0.05)
    for zq in np.arange(zlo, zhi + 1e-6, dz):
        hws = []
        for sgn in (1, -1):
            yq = HYC + sgn * ws
            v = map_coordinates(G, [np.full_like(ws, xq - 0.5), yq - 0.5, np.full_like(ws, zq - 0.5)], order=1)
            if v[0] < level:
                hws = None
                break
            k = np.nonzero(v < level)[0]
            if not len(k):
                hws = None
                break
            k = k[0]
            w = ws[k - 1] + (v[k - 1] - level) / max(v[k - 1] - v[k], 1e-6) * (ws[k] - ws[k - 1])
            hws.append(w)
        if hws:
            out.append((zq, float(np.mean(hws))))
    return out


def iso_top_bottom(G, xq, yq=HYC, level=0.5):
    """the smoothed body's bottom and top (q z) on the line (xq, yq)."""
    from scipy.ndimage import map_coordinates
    zs = np.arange(0.0, Z, 0.05)
    v = map_coordinates(G, [np.full_like(zs, xq - 0.5), np.full_like(zs, yq - 0.5), zs - 0.5], order=1)
    inside = np.nonzero(v >= level)[0]
    if not len(inside):
        return None
    return zs[inside[0]], zs[inside[-1]]


def region_smoothed(x0, x1, pad_lo=0, pad_hi=0, sig=(1.0, 0.7, 0.7)):
    """the body (no keels) between TS's slices x0..x1 only, smoothed; pad_lo / pad_hi repeat the end slices past the
    ends first, so a section there keeps its full size (a flat end face where the part meets another)."""
    key = ('reg', x0, x1, pad_lo, pad_hi, sig)
    if key not in _G:
        f = body_fill(True)
        g = np.zeros_like(f)
        g[x0:x1 + 1] = f[x0:x1 + 1]
        for k in range(1, pad_lo + 1):
            if x0 - k >= 0:
                g[x0 - k] = f[x0]
        for k in range(1, pad_hi + 1):
            if x1 + k < X:
                g[x1 + k] = f[x1]
        _G[key] = ndimage.gaussian_filter(g, sig, mode='constant')
    return _G[key]
