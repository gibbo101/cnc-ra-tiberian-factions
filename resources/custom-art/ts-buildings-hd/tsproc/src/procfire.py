"""The flare stack's fire (TS NTREFN_B: 40 frames, the flame on frames 0-19, nothing on 20-39), in HD for both views.

TS's frames are the flame's shape and its brightness (decoded with the unit palette they read dark red and pale
khaki; in game they are drawn with the fire palette: orange with yellow and red, as in the docking video).  Each
frame's shape is TS's own, upscaled and smoothed; its colour runs red -> orange -> yellow with TS's brightness, a
touch of noise for the flicker inside.  It is drawn at the stack's mouth: TS px (77, 47), on the TS-angle canvas at
the mod's scale and place, and on the RA grid where the model's stack top projects."""
import numpy as np
from PIL import Image
from scipy import ndimage
import walls2 as W

TS = '/home/claude/work/ts/ts-buildings-hd-handoff/04-TSPROC/ts-original/NTREFN_B/frames/%02d.png'
MOUTH_TS = (77.0, 47.0)
N_FIRE, N_ALL = 20, 40
RED = np.array([150, 28, 4.])
ORANGE = np.array([246, 112, 18.])
YELLOW = np.array([255, 226, 118.])


def ts_frame(k):
    a = np.asarray(Image.open(TS % k).convert('RGBA')).astype(np.float32)
    return a


def fire_sprite(k, scale, ss=4):
    """frame k as an RGBA float array (0..255 colour, 0..1 alpha) on a grid of TS px x scale; returns the array and
    where TS px (0, 0) lands on it."""
    a = ts_frame(k)
    al = (a[..., 3] > 0).astype(np.float32)
    if al.sum() == 0:
        return None, (0, 0)
    lum = (a[..., 0] * 0.5 + a[..., 1] * 0.35 + a[..., 2] * 0.15) / 255.0
    ys, xs = np.nonzero(al)
    x0, x1, y0, y1 = xs.min() - 3, xs.max() + 4, ys.min() - 3, ys.max() + 4
    al = al[y0:y1, x0:x1]; lum = lum[y0:y1, x0:x1]
    f = scale * ss
    H, Wd = int(round(al.shape[0] * f)), int(round(al.shape[1] * f))
    big = np.asarray(Image.fromarray(al).resize((Wd, H), Image.BILINEAR))
    bl = np.asarray(Image.fromarray(lum * al).resize((Wd, H), Image.BILINEAR))
    big = ndimage.gaussian_filter(big, 0.55 * f)
    bl = ndimage.gaussian_filter(bl, 0.7 * f)
    inten = np.clip(bl / np.maximum(big, 1e-3), 0, 1)
    alpha = np.clip((big - 0.32) / 0.3, 0, 1)
    # inside the flame: brighter towards its core (distance from the edge), TS's brightness, flicker
    core = ndimage.distance_transform_edt(big > 0.45) / (1.6 * f)
    yy, xx = np.mgrid[0:H, 0:Wd] / f
    nz = W.sample(W.NOISE_MOTTLE, xx * 9.0 + 7 * k, yy * 9.0 - 11 * k)
    t = np.clip(0.25 + 0.55 * inten + 0.35 * np.clip(core, 0, 1) + 0.12 * nz - 0.02 * max(0, k - 12), 0, 1)
    col = np.where((t < 0.5)[..., None], RED + (ORANGE - RED) * (t / 0.5)[..., None],
                   ORANGE + (YELLOW - ORANGE) * ((t - 0.5) / 0.5)[..., None])
    alpha = alpha * (0.88 + 0.12 * t)
    return np.dstack([col, alpha]), (-x0 * f, -y0 * f)


def layer(k, canvas, mouth_px, scale, ss=4):
    """the fire's frame k (0..39) on a canvas of `canvas` size, TS's mouth at canvas px mouth_px."""
    out = Image.new('RGBA', canvas, (0, 0, 0, 0))
    if k >= N_FIRE:
        return out
    spr, (ox, oy) = fire_sprite(k, scale, ss)
    if spr is None:
        return out
    # TS px (0, 0) at canvas mouth - MOUTH_TS * scale
    px = mouth_px[0] - MOUTH_TS[0] * scale
    py = mouth_px[1] - MOUTH_TS[1] * scale
    H, Wd = spr.shape[:2]
    # downsample the supersampled sprite (premultiplied)
    pre = spr.copy(); pre[..., :3] *= pre[..., 3:4]
    oxp, oyp = px * ss - ox, py * ss - oy
    # align to the supersampled canvas grid
    can = np.zeros((canvas[1] * ss, canvas[0] * ss, 4), np.float32)
    ix, iy = int(round(oxp)), int(round(oyp))
    xa, ya = max(ix, 0), max(iy, 0)
    xb, yb = min(ix + Wd, can.shape[1]), min(iy + H, can.shape[0])
    can[ya:yb, xa:xb] = pre[ya - iy:yb - iy, xa - ix:xb - ix]
    can = can.reshape(canvas[1], ss, canvas[0], ss, 4).mean(axis=(1, 3))
    a = can[..., 3:4]
    rgb = np.where(a > 1e-4, can[..., :3] / np.maximum(a, 1e-4), 0)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(a * 255, 0, 255)]).round().astype(np.uint8), 'RGBA')
