"""The flare stack's fire in HD (TS NTREFN_B: 40 frames, a burst of flame on frames 0-19, nothing on 20-39).

TS's frames give the burst's timing and size (measured per frame below, in TS px from the stack's mouth): it flickers
up, stands as a full plume leaning a little to the left (frames 5-14), then thins and dies.  Each HD frame is a flame
built at that size: a teardrop plume whose outline is torn into licking tongues by turbulence that rises through it
over the burst, a white-yellow core low in the plume through yellow and orange to deep red at the tips and edges, a
soft rim of heat haze.  Drawn at the stack's mouth on each view's canvas at the view's scale (px per TS px)."""
import numpy as np
from PIL import Image
from scipy import ndimage
import wnoise as WN

MOUTH_TS = (77.0, 47.0)
N_FIRE, N_ALL = 20, 40
# TS's NTREFN_B per frame: height above the mouth, width, and the plume's lean (centre x drift), TS px
TS_H = (6, 11, 13, 15, 16, 18, 19, 18, 19, 20, 21, 22, 25, 26, 25, 26, 23, 22, 20, 16)
TS_W = (5, 8, 11, 11, 12, 12, 14, 14, 13, 13, 11, 10, 10, 12, 11, 9, 7, 6, 5, 3)
TS_CX = (77.0, 77.0, 76.6, 76.5, 76.6, 76.5, 76.6, 76.2, 75.7, 75.2, 75.3, 74.7, 74.7, 74.9, 75.3, 75.0, 74.4, 74.5,
         74.8, 75.4)
# colour ramp by heat (0 cool edge .. 1 the core)
RAMP = ((0.00, (150, 30, 6)), (0.22, (190, 46, 8)), (0.42, (236, 96, 16)), (0.62, (255, 156, 34)),
        (0.80, (255, 208, 92)), (0.93, (255, 240, 176)), (1.00, (255, 252, 226)))


def ramp(t):
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,), np.float32)
    for (t0, c0), (t1, c1) in zip(RAMP[:-1], RAMP[1:]):
        m = (t >= t0) & (t <= t1)
        f = ((t - t0) / (t1 - t0))[..., None]
        out = np.where(m[..., None], np.array(c0, np.float32) * (1 - f) + np.array(c1, np.float32) * f, out)
    return out


def flame(k, scale, ss=4, seed=11):
    """frame k (0..19) as a premultiplied RGBA float array on a grid of screen px x ss, and where the mouth is on it.
    scale = screen px per TS px."""
    H = TS_H[k] * scale
    W = TS_W[k] * scale
    lean = (TS_CX[k] - MOUTH_TS[0]) * scale              # the plume's top drifts left as TS's does
    s = 1.0 / ss
    pad = 0.45 * W + 10 * scale
    x0, x1 = -0.5 * W - pad + min(lean, 0), 0.5 * W + pad + max(lean, 0)
    y0, y1 = -H * 1.25 - pad, 4.0 * scale                 # y up is negative (screen)
    xs = np.arange(x0, x1, s) + 0.5 * s
    ys = np.arange(y0, y1, s) + 0.5 * s
    X, Y = np.meshgrid(xs, ys)
    v = -Y / max(H, 1e-3)                                  # 0 at the mouth, 1 at the plume's top
    t = k / 19.0
    # turbulence rising through the plume over the burst (world-fixed noise, sampled lower as time goes on)
    f1 = 2.2 * scale; f2 = 0.9 * scale
    rise = t * 3.2 * H
    n1 = WN.noise(X, Y + rise, f1 * 2.2, seed, sigma=5.0)
    n2 = WN.noise(X * 1.3, Y + rise * 1.4, f2 * 2.0, seed + 1, sigma=4.0)
    n3 = WN.noise(X * 0.8 + 17, Y + rise * 0.7, f1 * 4.0, seed + 2, sigma=6.0)
    # the plume's centre line leans and sways
    cx = lean * np.clip(v, 0, 1.2) ** 1.3 + 0.10 * W * n3 * np.clip(v, 0, 1)
    u = (X - cx) / max(0.5 * W, 1e-3)                      # -1 .. 1 across the plume
    # a teardrop: widest a quarter of the way up, a point at the top, the mouth's width at the bottom
    prof = np.where(v < 0.25, 0.62 + 0.38 * np.sin(np.clip(v / 0.25, 0, 1) * np.pi / 2),
                    np.clip(1.0 - (v - 0.25) / 0.80, 0, 1) ** 0.75)
    prof = np.where(v < 0, 0.0, prof)
    # torn edges and licking tongues: the outline pushed in and out, more so towards the top
    n4 = WN.noise(X * 1.1, Y + rise * 1.9, f1 * 0.9, seed + 4, sigma=3.0)          # a finer octave
    tear = (0.30 + 0.55 * np.clip(v, 0, 1)) * (0.5 * n1 + 0.3 * n2 + 0.25 * n4)
    edge = prof * (1.0 + 0.55 * tear) - np.abs(u)
    d = np.clip(edge * 4.5 + 0.2, 0, 1)
    # the middle stays whole (no holes), up to where the plume tapers to its tip
    core = np.clip(1.0 - np.abs(u) / np.maximum(prof, 1e-3), 0, 1)
    d = np.maximum(d, np.clip(core * 2.2 - 0.25, 0, 1) * (v < 0.82))
    # the top: tall thin tongues (noise stretched up the flow) licking above the plume, breaking into flicks
    spikes = np.clip(WN.noise(X * 2.4, (Y + rise * 2.2) * 0.38, f1 * 1.6, seed + 5, sigma=3.0), 0, None)
    top = np.clip((1.02 + 0.20 * n1 + 0.30 * spikes - v) * 3.5, 0, 1)
    d = d * top * np.clip(v * 14.0 + 0.6, 0, 1)
    # heat: hottest low in the middle, cooling outwards and upwards, streaked along the flow; the burst's dying
    # frames run cooler
    streak = WN.noise(X * 1.6, (Y + rise * 1.8) * 0.33, 1.4 * scale * 2.0, seed + 3, sigma=3.0)
    heat = (0.55 * core + 0.45 * d) * (1.08 - 0.62 * np.clip(v, 0, 1.3)) + 0.08 * n2 + 0.07 * streak \
        - 0.12 * np.clip(n4, 0, None) * np.clip(v - 0.35, 0, 1)                  # cooler wisps up high
    heat = heat * (0.78 + 0.22 * np.clip(1.0 - abs(t - 0.45) * 2.2, 0, 1)) - (0.18 if k >= 17 else 0.0)
    col = ramp(heat)
    alpha = np.clip(d * 2.2, 0, 1) * np.clip(0.6 + heat, 0, 1) * np.clip((heat - 0.04) / 0.26, 0.25, 1)   # cool edges thin
    # heat haze: a faint warm rim round the flame
    rim = ndimage.gaussian_filter(alpha, 2.2 * scale * ss)
    haze = np.clip(rim * 0.30 - alpha, 0, 1)
    hcol = np.array([255, 120, 30], np.float32)
    pre = np.dstack([col * alpha[..., None] + hcol * haze[..., None], alpha + haze])
    mouth = (-x0 * ss, -y0 * ss)
    return pre.astype(np.float32), mouth


def layer(k, canvas, mouth_px, scale, ss=4):
    """the fire's frame k (0..39) on a canvas of `canvas` size, the stack's mouth at canvas px mouth_px."""
    out = Image.new('RGBA', canvas, (0, 0, 0, 0))
    if k >= N_FIRE:
        return out
    pre, (mx, my) = flame(k, scale, ss)
    Hh, Ww = pre.shape[:2]
    can = np.zeros((canvas[1] * ss, canvas[0] * ss, 4), np.float32)
    ix, iy = int(round(mouth_px[0] * ss - mx)), int(round(mouth_px[1] * ss - my))
    xa, ya = max(ix, 0), max(iy, 0)
    xb, yb = min(ix + Ww, can.shape[1]), min(iy + Hh, can.shape[0])
    can[ya:yb, xa:xb] = pre[ya - iy:yb - iy, xa - ix:xb - ix]
    can = can.reshape(canvas[1], ss, canvas[0], ss, 4).mean(axis=(1, 3))
    a = can[..., 3:4]
    rgb = np.where(a > 1e-4, can[..., :3] / np.maximum(a, 1e-4), 0)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(a * 255, 0, 255)]).round().astype(np.uint8), 'RGBA')
