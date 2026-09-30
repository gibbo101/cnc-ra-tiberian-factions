"""Render a heightfield (HD px ground grid, heights in HD units) from Tiberian Sun's isometric camera,
so a rebuild can be checked against the TS sprites. TS frame 48x48, cell ground centre at (24, 36)."""
import numpy as np
from PIL import Image

ZS = 29.4     # TS px per cell of height


def render_ts(H, C, x0, y0, cell=128.0, S=4, colours=None, light=(-0.75, -0.25, 0.6), zmax=None, slab=None):
    """H[j, i] at ground (x0 + i/ss, y0 + j/ss) with ss = grid px per HD px (inferred from shape later).
    Returns an RGBA image 48*S square."""
    n = 48 * S
    xs = (np.arange(n) + 0.5) / S
    X, Y = np.meshgrid(xs, xs)
    es = (X - 24) / 24.0
    ny_, nx_ = H.shape
    ss = C['ss']
    top = slab['top'] if slab is not None else None
    zmax = zmax if zmax is not None else max(H.max(), top.max() if top is not None else 0) / cell + 0.05
    dz = 1.0 / (ZS * S * 2)
    hit = np.zeros((n, n), bool)
    slabhit = np.zeros((n, n), bool)
    zh = np.zeros((n, n)); gi = np.zeros((n, n), int); gj = np.zeros((n, n), int)
    for z in np.arange(zmax, -1e-9, -dz):
        ep = (Y - 36 + ZS * z) / 12.0
        e = (ep + es) / 2; s = (ep - es) / 2
        gx = (e + 0.5) * cell; gy = (s + 0.5) * cell          # HD px in the cell
        i = np.round((gx - x0) * ss).astype(int); j = np.round((gy - y0) * ss).astype(int)
        ok = (i >= 0) & (i < nx_) & (j >= 0) & (j < ny_) & ~hit
        h = np.zeros((n, n))
        h[ok] = H[j[ok], i[ok]]
        new = ok & (h >= z * cell) & (h > 0.3)
        if top is not None:
            ts_ = np.full((n, n), -1.0); ts_[ok] = top[j[ok], i[ok]]
            sl = ok & (ts_ >= z * cell) & (z * cell >= slab['lo'])
            new_s = sl & ~new
            new = new | sl
            slabhit[new_s] = True
        hit |= new; zh[new] = z; gi[new] = i[new]; gj[new] = j[new]
    gyh, gxh = np.gradient(H, 1.0 / ss)
    # world normal (x east, y south, z up) -> TS lighting
    nx, ny, nz = -gxh[gj, gi], -gyh[gj, gi], np.ones((n, n))
    if top is not None:
        tt = np.where(top > 0, top, slab['lo'] - 8)
        gyt, gxt = np.gradient(tt, 1.0 / ss)
        nx = np.where(slabhit, -gxt[gj, gi], nx); ny = np.where(slabhit, -gyt[gj, gi], ny)
    nl = np.sqrt(nx * nx + ny * ny + nz * nz)
    L = np.array(light); L = L / np.linalg.norm(L)
    sh = 0.3 + 0.7 * np.clip((nx * L[0] + ny * L[1] + nz * L[2]) / nl, 0, 1)
    comp = np.where(slabhit, slab['comp'][gj, gi], C['comp'][gj, gi]) if top is not None else C['comp'][gj, gi]
    col = np.zeros((n, n, 3))
    for k, c in (colours or {}).items():
        col[comp == k] = c
    col = col * sh[..., None]
    rgba = np.dstack([np.where(hit[..., None], col, 0), hit * 255.0]).clip(0, 255).astype(np.uint8)
    return Image.fromarray(rgba, 'RGBA')
