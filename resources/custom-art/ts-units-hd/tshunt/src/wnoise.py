"""World-space noise: the same damage lands in the same place in every view (each view samples the model on
its own grid, so grid-based random noise would differ between the isometric and RA renders)."""
import numpy as np
from scipy import ndimage

_T = {}
N = 512


def _tex(seed, sigma=6.0):
    key = (seed, sigma)
    if key not in _T:
        rng = np.random.default_rng(seed)
        t = ndimage.gaussian_filter(rng.standard_normal((N, N)), sigma, mode='wrap')
        _T[key] = ((t - t.mean()) / t.std()).astype(np.float32)
    return _T[key]


def noise(X, Y, feat, seed, sigma=6.0):
    """smooth noise (mean 0, sd ~1) with features about `feat` units across, periodic every
    N / (2 sigma) * feat units (~40 features)."""
    t = _tex(seed, sigma)
    k = 2.0 * sigma / feat                       # texture px per world unit
    u = np.asarray(X, np.float32) * k + 0.37 * seed
    v = np.asarray(Y, np.float32) * k + 0.61 * seed
    i0 = np.floor(u).astype(np.int64); j0 = np.floor(v).astype(np.int64)
    fu = (u - i0).astype(np.float32); fv = (v - j0).astype(np.float32)
    i0 %= N; j0 %= N
    i1 = (i0 + 1) % N; j1 = (j0 + 1) % N
    a = t[j0, i0] * (1 - fu) + t[j0, i1] * fu
    b = t[j1, i0] * (1 - fu) + t[j1, i1] * fu
    return a * (1 - fv) + b * fv


def ridge(X, Y, feat, seed):
    """thin crack lines: where a smooth noise crosses zero (|n| small)."""
    return np.abs(noise(X, Y, feat, seed, sigma=4.0))
