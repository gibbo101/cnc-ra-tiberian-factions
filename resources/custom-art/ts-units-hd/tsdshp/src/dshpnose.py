"""
dshpnose.py - the Dropship's nose as one smooth body, sampled on a fine grid (quarter voxels):

  TS's nose (its filled voxels, x 76..94, without the gear's keel), smoothed;
  joined smoothly by the cockpit's housing, a rounded block carrying the front up square (Westwood's FMV: a tall front
  plate, the window high in it; TS's nose narrows to its top there);
  cut flat above TS's lower lip by the cockpit's plate, leaning back PLATE_TILT degrees from upright;
  smoothed again, so the plate's edges, the housing and TS's shapes run into each other without creases.

dshpmodel lofts the nose through this body's sections; dshprender shades it with the body's own normals.  q coordinates
throughout (voxel i spans i..i+1)."""
import numpy as np
from scipy import ndimage
from scipy.ndimage import map_coordinates
import dshpvox as V

STEP = 0.25
LO = np.array([71.0, 7.0, 5.0])                     # the grid's first point (q)
HI = np.array([97.0, 36.0, 23.0])
HYC = V.HYC

# the cockpit's plate and housing (q)
PLATE_X0, PLATE_Z0, PLATE_TILT = 92.2, 14.3, 22.0   # the plate's foot (at the lip's top) and its lean
HOOD = dict(x=(86.5, 94.5), w=3.3, z=(13.4, 17.45), r=0.6)
SIG_BASE = (1.3, 0.9, 0.9)                          # TS's voxels smoothed (voxels along x, y, z)
SIG_FINAL = 0.4                                     # the whole smoothed again (voxels)
LEVEL = 0.5


def plate_normal():
    t = np.deg2rad(PLATE_TILT)
    return np.array([np.cos(t), 0.0, np.sin(t)])     # (q x, y, z): out of the plate, forward and up


def plate_s(q):
    """signed distance in front of the plate (q units, > 0 in front)."""
    n = plate_normal()
    return (q[..., 0] - PLATE_X0) * n[0] + (q[..., 2] - PLATE_Z0) * n[2]


def plate_v(q):
    """the distance up the plate from its foot."""
    return (q[..., 2] - PLATE_Z0) / np.cos(np.deg2rad(PLATE_TILT))


def _axes():
    return [np.arange(LO[i], HI[i] + 1e-9, STEP) for i in range(3)]


def _smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


_F = None


def field():
    """the nose's body on the fine grid (1 inside, 0 outside, smooth between)."""
    global _F
    if _F is not None:
        return _F
    ax = _axes()
    QX, QY, QZ = np.meshgrid(*ax, indexing='ij')
    # TS's nose: its filled voxels (no keels), x 76..94, the back slice repeated behind so the body ends full there
    f = V.body_fill(True)
    g = np.zeros((f.shape[0] + 3,) + f.shape[1:], f.dtype)
    g[76:95] = f[76:95]
    for k in range(1, 6):
        g[76 - k] = f[76]
    g[95] = f[94] * 0.6                             # the tip: TS's last slice half again, so the smoothing keeps its length
    base = map_coordinates(g, [QX - 0.5, QY - 0.5, QZ - 0.5], order=1, mode='constant')
    base = ndimage.gaussian_filter(base, [s / STEP for s in SIG_BASE], mode='constant')
    # the housing: a rounded block, its density falling from 1 to 0 across its surface
    h = HOOD
    c = np.array([(h['x'][0] + h['x'][1]) / 2, HYC, (h['z'][0] + h['z'][1]) / 2])
    hs = np.array([(h['x'][1] - h['x'][0]) / 2, h['w'], (h['z'][1] - h['z'][0]) / 2])
    d = np.stack([np.abs(QX - c[0]), np.abs(QY - c[1]), np.abs(QZ - c[2])], -1) - (hs - h['r'])
    sdf = np.linalg.norm(np.maximum(d, 0), axis=-1) + np.minimum(d.max(-1), 0) - h['r']
    hood = np.clip(0.5 - sdf / 0.5, 0, 1)
    F = np.maximum(base, hood)
    # the plate: everything in front of it gone, above the lip only
    Q = np.stack([QX, QY, QZ], -1)
    above = _smoothstep(PLATE_Z0 - 0.45, PLATE_Z0 + 0.35, QZ)
    F = F * (1 - above * _smoothstep(-0.12, 0.12, plate_s(Q)))
    F = ndimage.gaussian_filter(F, SIG_FINAL / STEP, mode='constant')
    _F = F
    return F


def sample(F, q, order=1):
    q = np.asarray(q, float)
    idx = [(q[..., i] - LO[i]) / STEP for i in range(3)]
    return map_coordinates(F, idx, order=order, mode='constant')


_G = None


def gradient():
    global _G
    if _G is None:
        _G = [gi / STEP for gi in np.gradient(field())]
    return _G


def normals_q(q):
    """the body's outward normals at q points (in q's axes; divide by the section's scale for the local frame)."""
    g = np.stack([sample(gi, q) for gi in gradient()], -1)
    return -g


def top_bottom(xq, yq=HYC):
    zs = np.arange(LO[2], HI[2], 0.02)
    v = sample(field(), np.stack([np.full_like(zs, xq), np.full_like(zs, yq), zs], -1))
    inside = np.nonzero(v >= LEVEL)[0]
    if not len(inside):
        return None
    return zs[inside[0]], zs[inside[-1]]


def halfwidth(xq, zq):
    ws = np.arange(0.0, 14.0, 0.02)
    out = []
    for sgn in (1, -1):
        v = sample(field(), np.stack([np.full_like(ws, xq), HYC + sgn * ws, np.full_like(ws, zq)], -1))
        if v[0] < LEVEL:
            return None
        k = np.nonzero(v < LEVEL)[0]
        if not len(k):
            return None
        k = k[0]
        out.append(ws[k - 1] + (v[k - 1] - LEVEL) / max(v[k - 1] - v[k], 1e-9) * (ws[k] - ws[k - 1]))
    return float(np.mean(out))


def station(xq, dz=0.35):
    """the section at q x = xq as q points round its outline."""
    tb = top_bottom(xq)
    if tb is None:
        return []
    z0, z1 = tb
    zs = list(np.arange(z0 + 0.03, z1 - 0.03, dz)) + [z1 - 0.03]
    pts = []
    for zq in zs:
        hw = halfwidth(xq, zq)
        if hw is not None:
            pts += [(xq, HYC + hw, zq), (xq, HYC - hw, zq)]
    return pts
