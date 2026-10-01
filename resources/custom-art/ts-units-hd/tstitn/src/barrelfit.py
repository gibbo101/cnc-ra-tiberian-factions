import numpy as np
from PIL import Image
from scipy import ndimage
import rc, barrel as B
from tspal import load

def inmod(f):
    return np.array(Image.open(__import__('paths').HANDOFF + '/01-TSTITN/in-mod/tstitn/frames/tstitn-%04d.png' % f)).astype(int)

def ts_up(k):
    """TS torso frame (CW k) scaled x6.4 onto the 448 canvas (nearest)."""
    m = load(120 + k)[..., 3] > 0
    ys, xs = np.mgrid[0:448, 0:448]
    tx = np.floor((xs + 0.5 - 224) / 6.4 + 47.5).astype(int); ty = np.floor((ys + 0.5 - 386) / 6.4 + 55).astype(int)
    ok = (tx >= 0) & (tx < 95) & (ty >= 0) & (ty < 95)
    out = np.zeros((448, 448), bool); out[ok] = m[ty[ok], tx[ok]]
    return out

def barrel_pixels(f):
    """in-mod frame 96+f: pixels that belong to the composited cannon (not TS's sprite)."""
    a = inmod(96 + f); k = (32 - f) % 32
    op = a[..., 3] > 128
    t = ndimage.binary_dilation(ts_up(k), iterations=3)
    return op & ~t

def model_mask(f, off, s=1.0, ss=1, win=None):
    k = (32 - f) % 32
    th = 2 * np.pi * k / 32
    fv = np.array([np.sin(th), -np.cos(th), 0.0]); rv = np.array([np.cos(th), np.sin(th), 0.0])
    M = np.stack([fv, rv, [0, 0, 1.0]], 1)
    parts = [p.moved(M) for p in B.body_parts(off, s)]
    cam = rc.Cam((0, -1), 30.0, 6.4, (224.0, 386.0))
    x0, y0, x1, y1 = win or (0, 0, 448, 448)
    t, who, nrm, O = rc.render_ids(parts, cam, x0, y0, x1 - x0, y1 - y0, ss=ss, zstart=300.0)
    m = np.zeros((448, 448), bool); m[y0:y1, x0:x1] = (who >= 0)
    return m

def target_ts(f):
    """in-mod barrel pixels as coverage on TS's pixel grid (x 10-85, y 0-55)."""
    bp = barrel_pixels(f).astype(float)
    ys, xs = np.mgrid[0:448, 0:448]
    tx = np.floor((xs + 0.5 - 224) / 6.4 + 47.5).astype(int); ty = np.floor((ys + 0.5 - 386) / 6.4 + 55).astype(int)
    cov = np.zeros((55, 75)); cnt = np.zeros((55, 75))
    ok = (tx >= 10) & (tx < 85) & (ty >= 0) & (ty < 55)
    np.add.at(cov, (ty[ok], tx[ok] - 10), bp[ok]); np.add.at(cnt, (ty[ok], tx[ok] - 10), 1)
    return cov / np.maximum(cnt, 1)

def model_ts(f, off, s=1.0, ss=4):
    k = (32 - f) % 32
    th = 2 * np.pi * k / 32
    fv = np.array([np.sin(th), -np.cos(th), 0.0]); rv = np.array([np.cos(th), np.sin(th), 0.0])
    M = np.stack([fv, rv, [0, 0, 1.0]], 1)
    parts = [p.moved(M) for p in B.body_parts(off, s)]
    cam = rc.Cam((0, -1), 30.0, 1.0, (47.5, 55.0))
    t, who, nrm, O = rc.render_ids(parts, cam, 10, 0, 75, 55, ss=ss, zstart=300.0)
    return (who >= 0).reshape(55, ss, 75, ss).mean(axis=(1, 3))

def torso_ts(f):
    k = (32 - f) % 32
    m = load(120 + k)[0:55, 10:85, 3] > 0
    return ndimage.binary_dilation(m, iterations=1)
