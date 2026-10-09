"""
infx.py - the infantry's effects in HD, from TS's own pixels frame by frame:

  muzzle flash   TS draws it in the fire frames (fire and fire prone; not every step: TS's own pattern) in three
                 colours (255,255,0 yellow, 255,190,0 amber, 255,125,0 orange).  HD: TS's flash pixels for that frame
                 as a glow field (yellow strongest), its shape kept, drawn smooth and hot (a white-yellow core, amber,
                 orange edges), anchored on the HD rifle's muzzle, hidden where the soldier stands in front of it.
"""
import numpy as np
from PIL import Image
from scipy import ndimage

WEIGHT = {(255, 255, 0): 1.0, (255, 190, 0): 0.72, (255, 125, 0): 0.48}
RAMP = [(0.0, (255, 110, 0)), (0.35, (255, 150, 10)), (0.6, (255, 205, 20)), (0.85, (255, 250, 90)),
        (1.0, (255, 255, 225))]


# the Jumpjet's muzzle flash has red tips (TS's 255,0,0 and 190,0,0 round the yellow star): in his fire frames those
# reds are the flash's, not blood
REDS = {(255, 0, 0): 0.3, (190, 0, 0): 0.2}


def ts_flash(frame, extra=None):
    """TS's flash pixels in a decoded frame (RGBA array): [(x, y, weight)] (extra: more colours: weights)."""
    a = np.asarray(frame).astype(int)
    w = dict(WEIGHT)
    w.update(extra or {})
    out = []
    ys, xs = np.nonzero(a[..., 3] > 0)
    for y, x in zip(ys, xs):
        c = tuple(int(v) for v in a[y, x, :3])
        if c in w:
            out.append((x, y, w[c]))
    return out


def ramp(v):
    v = np.clip(v, 0, 1)
    out = np.zeros(v.shape + (3,))
    for (a, ca), (b, cb) in zip(RAMP, RAMP[1:]):
        m = (v >= a) & (v <= b)
        t = ((v - a) / (b - a))[m][:, None]
        out[m] = np.array(ca) * (1 - t) + np.array(cb) * t
    return out


def flash_layer(pix, K, DX, DY, shift, size, ss=4, blur=1.25, ramp_fn=None):
    """the flash as an RGBA layer (size, at ss): TS's pixels mapped by canvas = TS px x K + (DX, DY) + shift.  blur: the
    glow's width (TS px); ramp_fn: its colours (the flash's yellows by default)."""
    W, H = size
    f = np.zeros((H * ss, W * ss), np.float32)
    for x, y, w in pix:
        cx = ((x + 0.5) * K + DX + shift[0]) * ss; cy = ((y + 0.5) * K + DY + shift[1]) * ss
        xi, yi = int(round(cx)), int(round(cy))
        if 0 <= xi < W * ss and 0 <= yi < H * ss:
            f[yi, xi] += w
    # each TS pixel spreads over its 3 canvas px, the field smoothed to a glow
    g = ndimage.gaussian_filter(f, blur * K * ss / 2.0) * (2 * np.pi * (blur * K * ss / 2.0) ** 2)
    g = g / max(g.max(), 1e-6)
    sharp = np.clip((g - 0.12) / 0.78, 0, 1) ** 0.85
    col = (ramp_fn or ramp)(sharp)
    alpha = np.clip((g - 0.06) / 0.18, 0, 1)
    rgba = np.zeros((H * ss, W * ss, 4), np.float32)
    rgba[..., :3] = col; rgba[..., 3] = alpha
    return rgba


def draw_flash(img, pix, K, DX, DY, shift, occl=None, ss=4, blur=1.25, ramp_fn=None):
    """composite the flash over img (PIL RGBA, canvas size); occl: canvas-size mask (0..1) of the soldier in front."""
    W, H = img.size
    lay = flash_layer(pix, K, DX, DY, shift, (W, H), ss, blur, ramp_fn)
    lay = lay.reshape(H, ss, W, ss, 4).mean(axis=(1, 3))
    if occl is not None:
        lay[..., 3] *= (1 - occl)
    base = np.asarray(img).astype(np.float32)
    a = lay[..., 3:4]
    out = base.copy()
    out[..., :3] = base[..., :3] * (1 - a) + lay[..., :3] * a
    out[..., 3] = np.maximum(base[..., 3], a[..., 0] * 255)
    return Image.fromarray(np.clip(np.round(out), 0, 255).astype(np.uint8), 'RGBA')


# ---------------------------------------------------------------------------------------------- electric arcs
# the Cyborg Commando's death 1: TS draws blue-white arcs crackling over it (pure white, three lavender-blues, pure
# blue).  HD: those pixels, frame by frame, as thin glowing lines - white cores, blue edges - over the body
ARCS = {(255, 255, 255): 1.0, (206, 206, 255): 0.85, (153, 153, 255): 0.65, (101, 101, 255): 0.45, (0, 0, 255): 0.3}
ARC_RAMP = [(0.0, (60, 70, 255)), (0.4, (130, 145, 255)), (0.75, (205, 215, 255)), (1.0, (255, 255, 255))]


def arc_ramp(v):
    v = np.clip(v, 0, 1)
    out = np.zeros(v.shape + (3,))
    for (a, ca), (b, cb) in zip(ARC_RAMP, ARC_RAMP[1:]):
        m = (v >= a) & (v <= b)
        t = ((v - a) / (b - a))[m][:, None]
        out[m] = np.array(ca) * (1 - t) + np.array(cb) * t
    return out


def ts_arcs(frame):
    """TS's arc pixels in a decoded frame: [(x, y, weight)]."""
    return _pick(frame, ARCS)


def _pick(frame, table):
    a = np.asarray(frame).astype(int)
    out = []
    ys, xs = np.nonzero(a[..., 3] > 0)
    for y, x in zip(ys, xs):
        c = tuple(int(v) for v in a[y, x, :3])
        if c in table:
            out.append((x, y, table[c]))
    return out


def draw_arcs(img, pix, K, DX, DY, shift, ss=4):
    """the arcs over img: thin (a narrow glow) and blue-white."""
    return draw_flash(img, pix, K, DX, DY, shift, None, ss, blur=0.6, ramp_fn=arc_ramp)
