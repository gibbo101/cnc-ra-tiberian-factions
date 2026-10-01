import numpy as np
from PIL import Image
from scipy import ndimage

def render_hull(keep, grid, yaw_deg, elev_deg, scale=8, cols=None, light=(-0.5, -0.6, 0.7)):
    """orthographic render of a voxel hull: camera yaw (0 = looking north at the body facing north), elev."""
    us, vs, ws = grid
    res = us[1] - us[0]
    idx = np.argwhere(keep)
    U = us[idx[:, 0]]; V = vs[idx[:, 1]]; Wz = ws[idx[:, 2]]
    # body frame (u fwd, v right) -> world with body facing north: X = v, Y = -u
    X = V; Y = -U
    th = np.deg2rad(yaw_deg)
    Xr = X * np.cos(th) - Y * np.sin(th); Yr = X * np.sin(th) + Y * np.cos(th)
    sE, cE = np.sin(np.deg2rad(elev_deg)), np.cos(np.deg2rad(elev_deg))
    sx = Xr; sy = sE * Yr - cE * Wz; depth = cE * Yr + sE * Wz
    # normals from occupancy gradient (smoothed)
    occ = ndimage.gaussian_filter(keep.astype(np.float32), 1.2)
    gu, gv, gw = np.gradient(occ)
    nU = -gu[tuple(idx.T)]; nV = -gv[tuple(idx.T)]; nW = -gw[tuple(idx.T)]
    nX = nV; nY = -nU
    nXr = nX * np.cos(th) - nY * np.sin(th); nYr = nX * np.sin(th) + nY * np.cos(th)
    nl = np.sqrt(nXr ** 2 + nYr ** 2 + nW ** 2) + 1e-9
    L = np.array(light) / np.linalg.norm(light)
    shade = 0.35 + 0.65 * np.clip((nXr * L[0] + nYr * L[1] + nW * L[2]) / nl, 0, 1)
    x0, x1 = sx.min() - 1, sx.max() + 1; y0, y1 = sy.min() - 1, sy.max() + 1
    Wd = int((x1 - x0) / res) + 2; Hd = int((y1 - y0) / res) + 2
    ix = ((sx - x0) / res).astype(int); iy = ((sy - y0) / res).astype(int)
    zb = np.full((Hd, Wd), -1e9); img = np.zeros((Hd, Wd, 3))
    order = np.argsort(depth)
    for o in [order]:
        zb[iy[o], ix[o]] = depth[o]
        base = cols[o] if cols is not None else np.full((len(o), 3), 200.0)
        img[iy[o], ix[o]] = base * shade[o, None]
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    return im.resize((Wd * scale // 4, Hd * scale // 4), Image.NEAREST)
