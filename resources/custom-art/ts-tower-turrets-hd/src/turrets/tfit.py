"""
Fit a turret model to TS's own 32 facings (48x48, UNITTEM.PAL) by projecting it with TS's camera: an
orthographic view 30 degrees above the ground, 0.2652 px per unit across (a cell's 181-unit diagonal is 48
px), facing f turned f * 11.25 degrees counter-clockwise from straight up the screen.

For speed the model is voxelised once (its surface shell, 1-unit cells, local frame) and the voxels are
projected per facing: the silhouette is where any voxel lands, the colour class the nearest one's.
"""
import numpy as np
from PIL import Image
import tsdf as T

E_TS, S_TS = np.deg2rad(30.0), 48.0 / (128.0 * np.sqrt(2.0))
EMPTY, KHAKI, GREY, GREEN, DARK = 0, 1, 2, 3, 4
SS = 4                                               # supersampling of the TS frame for the projection


def classes(img):
    """TS pixels -> colour classes."""
    a = np.array(img.convert('RGBA')).astype(int)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    c = np.full(r.shape, KHAKI, np.int8)
    grey = (np.abs(r - g) < 14) & (np.abs(g - b) < 14)
    c = np.where(grey, GREY, c)
    c = np.where(grey & (r < 50), DARK, c)
    c = np.where((r < 40) & (g < 40) & (b < 40), DARK, c)
    c = np.where((g > 1.5 * np.maximum(r, b)) & (g > 60), GREEN, c)
    c = np.where((r > 110) & (g < 95) & (b < 80) & (r > g + 25), DARK, c)     # dark red tube ends
    return np.where(al > 0, c, EMPTY).astype(np.int8)


def load_ts(turret, root='ts-tower-turrets-handoff/ts-original'):
    return np.array([classes(Image.open(f'{root}/{turret}/frame-{f:02d}.png')) for f in range(32)])


def voxels(parts, lo, hi, step=1.0, shell=1.6):
    """surface shell of the model: local points and their colour class (comp -> class via 'cls')."""
    fs = np.arange(lo[0], hi[0] + step, step); rs = np.arange(lo[1], hi[1] + step, step)
    zs = np.arange(lo[2], hi[2] + step, step)
    F, R, Z = np.meshgrid(fs, rs, zs, indexing='ij')
    P = np.stack([F, R, Z], -1).reshape(-1, 3)
    d, comp = T.scene_sdf(parts, P, want_comp=True)
    m = (d <= 0) & (d > -shell)
    return P[m], comp[m]


def project(P, cls, th, px, py, zref, shape=(48, 48)):
    """voxels (local, z relative to the turret base) -> TS frame class map at SS x supersampling."""
    s, c = np.sin(th), np.cos(th)
    x = -P[:, 0] * s + P[:, 1] * c
    y = -P[:, 0] * c - P[:, 1] * s
    z = P[:, 2]
    X = px + S_TS * x
    Y = py + S_TS * (y * np.sin(E_TS) - (z - zref) * np.cos(E_TS))
    depth = y * np.cos(E_TS) + z * np.sin(E_TS)          # bigger = nearer the camera
    H, W = shape[0] * SS, shape[1] * SS
    xi = np.floor(X * SS).astype(int); yi = np.floor(Y * SS).astype(int)
    ok = (xi >= 0) & (xi < W) & (yi >= 0) & (yi < H)
    xi, yi, depth, cl = xi[ok], yi[ok], depth[ok], cls[ok]
    order = np.argsort(depth)
    out = np.zeros(H * W, np.int8)
    out[(yi * W + xi)[order]] = cl[order]                # nearest last, so it wins
    out = out.reshape(H, W)
    # fill pin-holes left by the splatting (a pixel empty but with 3+ filled neighbours)
    filled = out > 0
    nb = sum(np.roll(np.roll(filled, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1)) - filled
    hole = ~filled & (nb >= 6)
    if hole.any():
        src = out.copy()
        for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            sh = np.roll(np.roll(src, dy, 0), dx, 1)
            out = np.where(hole & (out == 0), sh, out)
    return out


def downsample_classes(m):
    """SS x class map -> TS pixels: coverage fraction and the majority class of covered samples."""
    H, W = m.shape[0] // SS, m.shape[1] // SS
    b = m.reshape(H, SS, W, SS).transpose(0, 2, 1, 3).reshape(H, W, SS * SS)
    cov = (b > 0).mean(-1)
    counts = np.stack([(b == k).sum(-1) for k in range(1, 5)], -1)
    maj = counts.argmax(-1) + 1
    return cov, np.where(cov > 0, maj, 0)


def score(ts, P, cls, px, py, zref, frames=range(32), th_of=lambda f: f * np.pi / 16):
    """mean silhouette IoU and mean class agreement over the frames."""
    ious, agree = [], []
    for f in frames:
        cov, maj = downsample_classes(project(P, cls, th_of(f), px, py, zref))
        a = ts[f] > 0
        m = cov >= 0.5
        ious.append((a & m).sum() / max((a | m).sum(), 1))
        both = a & m
        agree.append((ts[f][both] == maj[both]).mean() if both.any() else 0.0)
    return float(np.mean(ious)), float(np.mean(agree))


def compare_sheet(ts_imgs, P, cls, px, py, zref, frames, scale=6):
    """TS frame | model class map | overlap, per frame, for eyeballing."""
    pal = np.array([[90, 100, 80], [180, 160, 100], [140, 140, 150], [0, 200, 0], [30, 30, 30]], np.uint8)
    tiles = []
    for f in frames:
        cov, maj = downsample_classes(project(P, cls, f * np.pi / 16, px, py, zref))
        a = np.array(ts_imgs[f].convert('RGBA'))
        bg = np.full(a.shape[:2] + (3,), (90, 100, 80), np.uint8)
        al = a[..., 3:4] / 255.0
        ts_rgb = (a[..., :3] * al + bg * (1 - al)).astype(np.uint8)
        mod_rgb = pal[np.where(cov >= 0.5, maj, 0)]
        ov = bg.copy()
        tsm, mm = a[..., 3] > 0, cov >= 0.5
        ov[tsm & mm] = (200, 200, 200); ov[tsm & ~mm] = (255, 60, 60); ov[~tsm & mm] = (60, 120, 255)
        row = np.concatenate([ts_rgb, mod_rgb, ov], axis=1)
        tiles.append(np.kron(row, np.ones((scale, scale, 1), np.uint8)))
    return Image.fromarray(np.concatenate(tiles, axis=0))


def fit(model, ts, p0, steps, rounds=6, w_cls=0.35, frames=range(32), log=print, limits=None):
    """coordinate descent on the parameters in `steps` (name -> initial step), maximising
    IoU + w_cls * class agreement. model: module with parts(p), bounds(p), CLS."""
    lut = np.zeros(32, int)
    for k, v in model.CLS.items():
        lut[k] = v

    def evaluate(p):
        P, comp = voxels(model.parts(p), *model.bounds(p))
        iou, ag = score(ts, P, lut[comp], p['px'], p['py'], p['zref'], frames)
        return iou + w_cls * ag, iou, ag
    p = dict(p0)
    best, iou, ag = evaluate(p)
    log(f'start {best:.4f} (IoU {iou:.4f}, class {ag:.4f})')
    st = dict(steps)
    for rnd in range(rounds):
        improved = False
        for k in st:
            for sgn in (1, -1):
                q = dict(p); q[k] = p[k] + sgn * st[k]
                if limits and k in limits:
                    q[k] = float(np.clip(q[k], *limits[k]))
                sc, i2, a2 = evaluate(q)
                if sc > best + 1e-5:
                    p, best, iou, ag = q, sc, i2, a2
                    improved = True
                    break
        log(f'round {rnd}: {best:.4f} (IoU {iou:.4f}, class {ag:.4f})')
        if not improved:
            st = {k: v * 0.5 for k, v in st.items()}
    return p, best, iou, ag


def score_cls(ts, P, cls, px, py, zref, frames=range(32), merge=None, th_of=lambda f: f * np.pi / 16):
    """silhouette IoU and the mean per-class IoU (classes present in the TS frames), over the frames.
    merge: dict class -> class applied to both sides first (e.g. DARK -> GREY for striped barrels)."""
    inter = np.zeros(5); union = np.zeros(5); si = su = 0
    for f in frames:
        cov, maj = downsample_classes(project(P, cls, th_of(f), px, py, zref))
        t = ts[f].copy(); m = np.where(cov >= 0.5, maj, 0)
        if merge:
            for a, b in merge.items():
                t = np.where(t == a, b, t); m = np.where(m == a, b, m)
        si += ((t > 0) & (m > 0)).sum(); su += ((t > 0) | (m > 0)).sum()
        for k in range(1, 5):
            inter[k] += ((t == k) & (m == k)).sum(); union[k] += ((t == k) | (m == k)).sum()
    present = union[1:] > 0
    return si / max(su, 1), float((inter[1:][present] / union[1:][present]).mean())


def fit2(model, ts, p0, steps, rounds=8, w_cls=1.0, frames=range(32), merge=None, log=print, limits=None):
    """coordinate descent maximising silhouette IoU + w_cls * mean per-class IoU."""
    lut = np.zeros(32, int)
    for k, v in model.CLS.items():
        lut[k] = v

    def evaluate(p):
        P, comp = voxels(model.parts(p), *model.bounds(p))
        iou, ci = score_cls(ts, P, lut[comp], p['px'], p['py'], p['zref'], frames, merge)
        return iou + w_cls * ci, iou, ci
    p = dict(p0)
    best, iou, ci = evaluate(p)
    log(f'start {best:.4f} (IoU {iou:.4f}, class IoU {ci:.4f})')
    st = dict(steps)
    for rnd in range(rounds):
        improved = False
        for k in st:
            for sgn in (1, -1):
                q = dict(p); q[k] = p[k] + sgn * st[k]
                if limits and k in limits:
                    q[k] = float(np.clip(q[k], *limits[k]))
                sc, i2, c2 = evaluate(q)
                if sc > best + 1e-5:
                    p, best, iou, ci = q, sc, i2, c2
                    improved = True
                    break
        log(f'round {rnd}: {best:.4f} (IoU {iou:.4f}, class IoU {ci:.4f})')
        if not improved:
            st = {k: v * 0.5 for k, v in st.items()}
    return p, best, iou, ci
