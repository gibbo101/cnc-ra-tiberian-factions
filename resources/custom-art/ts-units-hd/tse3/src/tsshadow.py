"""
tsshadow.py - TS's own shadow, read off the mod's frames (TS's sprite scaled x K with TS's shadow baked in, black at
alpha ~64): per TS pixel, whether TS's shadow lies there (where the soldier doesn't cover it).

    import tsshadow; sh = tsshadow.ts_shadow(unit, k)     # bool (h, w) on TS's frame grid
"""
import numpy as np
from paths import HANDOFF
from PIL import Image
import infunit

ROOT = HANDOFF + '/'


def inmod_frame(unit, k):
    u = infunit.UNITS[unit]
    return np.asarray(Image.open(ROOT + '%s/in-mod/ts%s/frames/ts%s-%04d.png' % (
        u['dir'], u['name'].lower(), u['name'].lower(), k)).convert('RGBA')).astype(float)


def ts_shadow(unit, k, shape=None, thr=0.5):
    """TS's shadow on TS's frame grid: the fraction of each TS pixel's in-mod area that is shadow (dark, half see-through)
    > thr, outside the soldier."""
    import inffit as F
    u = infunit.UNITS[unit]
    K, DX, DY = u['K'], u['DX'], u['DY']
    a = inmod_frame(unit, k)
    al = a[..., 3]; lum = a[..., :3].mean(-1)
    sh = (al > 25) & (al < 120) & (lum < 8)            # (TS's shadow: pure black at alpha ~64)
    ts = F.ts_frame(unit, k)
    h, w = ts.shape[:2] if shape is None else shape
    out = np.zeros((h, w), float)
    H, W = al.shape
    for y in range(h):
        v0, v1 = int(round(y * K + DY)), int(round((y + 1) * K + DY))
        if v1 <= 0 or v0 >= H:
            continue
        for x in range(w):
            u0, u1 = int(round(x * K + DX)), int(round((x + 1) * K + DX))
            if u1 <= 0 or u0 >= W:
                continue
            blk = sh[max(v0, 0):min(v1, H), max(u0, 0):min(u1, W)]
            if blk.size:
                out[y, x] = blk.mean()
    body = ts[..., 3] > 0
    return (out > thr) & ~body


def light_dir(az, el):
    """the direction towards TS's shadow light: the shadow falls along plan angle az (degrees from east, towards south
    positive: screen right = 0, screen down = 90), the light el degrees above the ground."""
    a, e = np.deg2rad(az), np.deg2rad(el)
    return np.array([-np.cos(a) * np.cos(e), -np.sin(a) * np.cos(e), np.sin(e)])


def model_shadow(parts, cam, win, Ls, ss=2, off=(0.0, 0.0)):
    """how much of each TS pixel of the window (x0, y0, x1, y1) is ground in the soldier's shadow (light Ls); off: TS's
    shadow sits that far (TS px) from where the light puts it (the mod's frames: a pixel or two lower)."""
    import rc
    x0, y0, x1, y1 = win
    w, h = x1 - x0, y1 - y0
    xs = x0 + (np.arange(w * ss) + 0.5) / ss
    ys = y0 + (np.arange(h * ss) + 0.5) / ss
    SX, SY = np.meshgrid(xs, ys)
    O = cam.rays(SX.ravel() - off[0], SY.ravel() - off[1], 60.0)
    t = O[:, 2] / -cam.D[2]
    G = O + t[:, None] * cam.D                       # the ground point under each ray
    G[:, 2] = 0.0
    Ls = np.asarray(Ls, float) / np.linalg.norm(Ls)
    S0 = G + Ls[None, :] * (60.0 / Ls[2])            # back up the light ray to height 60
    tt, who, _ = rc.cast(parts, S0, -Ls, want_normals=False)
    hit = np.isfinite(tt).reshape(SX.shape)
    return hit.reshape(h, ss, w, ss).mean(axis=(1, 3))


def shadow_window(unit, k, margin=3):
    """a window on TS's frame round the soldier and his shadow."""
    import inffit as F
    ts = F.ts_frame(unit, k)
    sh = ts_shadow(unit, k)
    m = (ts[..., 3] > 0) | sh
    ys, xs = np.nonzero(m)
    return (max(xs.min() - margin, 0), max(ys.min() - margin, 0), min(xs.max() + margin + 1, ts.shape[1]),
            min(ys.max() + margin + 1, ts.shape[0]))


# TS's shadow light (fitlight: the 8 standing frames of all six units): the shadow falls along AZ, the light EL above the
# ground; OFF per unit: where the mod's frames put TS's shadow from where that light casts it
import json as _json
import os as _os
_L = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'ts_light.json')))
AZ, EL, OFF = _L['az'], _L['el'], {u: tuple(v) for u, v in _L['off'].items()}
LS = light_dir(AZ, EL)


class ShadowTarget:
    """TS's shadow in frame k: a window round the soldier and his shadow, TS's visible shadow there, and the pixels it
    can't show (TS's soldier over it, TS's blood and flashes)."""

    def __init__(self, unit, k, margin=4):
        import inffit as F
        ts = F.ts_frame(unit, k)
        cls = F.ts_classes(ts)
        self.win = shadow_window(unit, k, margin)
        x0, y0, x1, y1 = self.win
        self.sh = ts_shadow(unit, k)[y0:y1, x0:x1].astype(float)
        self.hidden = (ts[y0:y1, x0:x1, 3] > 0)
        self.off = OFF.get(unit, (0.0, 0.0))
        self.norm = max(float(((cls > 0) & (cls != F.FX)).sum()), 1.0)

    def loss(self, parts, cam, ss=2):
        """our shadow where TS's ground shows none counts most (a part raised that TS has down), TS's shadow we don't
        cast less (TS's light is only near ours)."""
        ms = model_shadow(parts, cam, self.win, LS, ss, self.off)
        d = W_EXCESS * np.clip(ms - self.sh, 0, None) + W_MISSING * np.clip(self.sh - ms, 0, None)
        return float(d[~self.hidden].sum()) / self.norm


W_EXCESS = float(_os.environ.get('SH_EXCESS', 2.0))
W_MISSING = float(_os.environ.get('SH_MISSING', 0.5))
