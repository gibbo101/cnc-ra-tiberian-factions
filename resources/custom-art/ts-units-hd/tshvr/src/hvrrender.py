"""
hvrrender.py - the Hover MLRS's HD frames for the mod (TSHVR, 192 x 192, 4 canvas px per classic pixel: 0-31 the hull,
no shadow; 32-63 the missile rack, no shadow; 64-95 the hull's shadow on its own; 32 facings counter-clockwise from
north), each with a -trim.png, from the rebuilt model (hvrmodel.py) posed by TS's HVAs.  Camera, size and place as v1
and the mod (hvrcam.py).  Each rack frame (the support and the pods) is drawn turning about the rack's pivot, which
stands on the unit's position on the hull's canvas at the height of the pad on the hull's back deck (Luke: pivot
fixed): the game seats it on the pad's centre, 12.54 voxels aft along the hull's facing and 0.20 to its left
(hvrseat.py).  The pad is the hull's, so only the pods (and their support) move when the game kicks the rack back on
firing.  Each shadow frame is the HD hull's silhouette moved as the mod's shadow is (5 px right,
17 px down: it hovers), black at alpha 191, softened.  This canvas has half the other units' density, so the outline is
0.75 canvas px wide (as wide in the game as on the other units).

    python3 hvrrender.py 0,24,56,88 [ss] [outdir] [sky 0/1]
"""
import os, sys, time
import numpy as np
from PIL import Image
from scipy import ndimage
import rc, rcrender as RR
import hvrmodel as T, hvrmat as MM
from hvrcam import CANVAS, ORIGIN, PX_SCALE, SHADOW_SHIFT, SHADOW_ALPHA, camera, unit_to_world, frame_of
from paths import HANDOFF
from frameio import save

INMOD = HANDOFF + '/07-TSHVR/in-mod/tshvr/frames/tshvr-%04d.png'
BOUNDS = ((-30, 30), (-30, 30), (-2, 30))
OUT = 'out'


def find_window(parts, cam, margin=8, step=2):
    W_, H_ = CANVAS
    xs = np.arange(0, W_, step) + step / 2; ys = np.arange(0, H_, step) + step / 2
    SX, SY = np.meshgrid(xs, ys)
    O = cam.rays(SX.ravel(), SY.ravel())
    t, who, _ = rc.cast(parts, O, cam.D, want_normals=False)
    hit = np.isfinite(t).reshape(SX.shape)
    yy, xx = np.nonzero(hit)
    return (max(int(xs[xx.min()] - margin), 0), max(int(ys[yy.min()] - margin), 0),
            min(int(xs[xx.max()] + margin), W_), min(int(ys[yy.max()] + margin), H_))


ROUNDED = {T.OCHRE: 0.22, T.KHAKI: 0.2, T.SKIRT: 0.15, T.FAN: 0.12, T.COWL: 0.1, T.BUMPER: 0.12, T.DECK_D: 0.15,
           T.DECK: 0.12, T.DECK_L: 0.06, T.HOUSE_C: 0.12, T.POD: 0.2, T.COLLAR: 0.12, T.FACE: 0.08, T.MOUNT: 0.12, T.TURNTABLE: 0.1}


def round_edges(r):
    for i, p in enumerate(r.parts):
        sig = ROUNDED.get(p.comp)
        if sig is None:
            continue
        m = (r.who == i) & r.hitmask
        if not m.any():
            continue
        planes = [c for c in p.cons if c.kind == 'plane']
        if len(planes) < 2:
            continue
        N = np.array([c.n for c in planes]); d = np.array([c.d for c in planes])
        Q = np.stack([r.x[m], r.y[m], r.z[m]], 1)
        s = Q @ N.T - d[None, :]
        w = np.exp((s - s.max(1, keepdims=True)) / sig)
        n = w @ N
        own = np.stack([r.nx[m], r.ny[m], r.nz[m]], 1)
        curved = s.max(1) < -0.02
        n = np.where(curved[:, None], own, n)
        n = n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)
        r.nx[m], r.ny[m], r.nz[m] = n[:, 0], n[:, 1], n[:, 2]


def spec_hl(r, comps, strength=0.2, power=20.0):
    L = r.L; V = -r.cam.D
    Hh = (L + V) / np.linalg.norm(L + V)
    nh = np.clip(r.nx * Hh[0] + r.ny * Hh[1] + r.nz * Hh[2], 0, 1)
    sh = getattr(r, 'inshadow', 0.0)
    m = np.isin(r.comp, comps)
    return (strength * nh ** power * (1 - 0.9 * sh) * m * 255.0)[..., None] * np.array([1.0, 0.92, 0.78])


_MODEL = None


def model():
    global _MODEL
    if _MODEL is None:
        _MODEL = T.model()
    return _MODEL


def bbox_centre(a, thr=250):
    ys, xs = np.nonzero(a > thr)
    return (xs.min() + xs.max() + 1) / 2.0, (ys.min() + ys.max() + 1) / 2.0


def draw(which, facing, origin, ss, sky, m, shift=None, cast=True):
    Mx = unit_to_world(facing)
    parts, frames, owner = T.posed(m, which, Mx, shift)
    cam = camera(origin)
    win = find_window(parts, cam)
    r = RR.RCRender(parts, cam, CANVAS, win, BOUNDS, ss=ss, frames=frames, shadow_len=1.0, px_scale=PX_SCALE)
    if not cast:
        # no cast shadows (the rack: Luke wants no shadow between it and the hull)
        r.shadow = lambda: np.zeros_like(r.nz)
    r.sec = np.where(r.hitmask, owner[np.clip(r.who, 0, len(owner) - 1)], '')
    r.pose_R = Mx
    round_edges(r)
    occ = r.sky_occlusion() if sky else None
    if occ is not None and not cast:
        # the pad and the support under the pods: the pods' cover kept light (no dark band between rack and hull)
        under = np.isin(r.comp, (T.TURNTABLE, T.MOUNT))
        occ = np.where(under, occ * 0.3, occ)
    alb, (bx, by, bz), emit = MM.materials(r, occ=occ)
    ao = 0.84 + 0.16 * np.clip((r.z + 1.0) / 10.0, 0, 1)
    col = r.shade(alb, sky_occ=occ, ao=ao) + emit
    col = col * np.clip(1 + 0.3 * bz, 0.55, 1.35)[..., None]
    col = col + spec_hl(r, MM.GLOSSY)
    img = r.compose(col, ground=None)
    tm = MM.trim_mask(r, alb).astype(np.float32)
    full = np.zeros((r.H * ss, r.W * ss), np.float32)
    x0, y0, x1, y1 = r.win
    full[y0 * ss:y1 * ss, x0 * ss:x1 * ss] = tm
    trim = Image.fromarray((full.reshape(r.H, ss, r.W, ss).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L')
    return img, trim


def rack_origin(f, m):
    """where the rack frame f's origin goes so its content is centred where in-mod/'s is (whole canvas px moves are
    left to the renderer: the shift is fractional)."""
    which = ['rack']
    Mx = unit_to_world(f)
    parts, _, _ = T.posed(m, which, Mx)
    t, who, nrm, O = rc.render_ids(parts, RR.Cam((0, -1), 32.0, camera().ppu, ORIGIN), 0, 0, CANVAS[0], CANVAS[1],
                                    ss=4, zstart=300.0)
    cov = ((who >= 0).reshape(CANVAS[1], 4, CANVAS[0], 4).mean(axis=(1, 3)) * 255)
    cx0, cy0 = bbox_centre(cov, 250)
    tgt = bbox_centre(np.array(Image.open(INMOD % (32 + f)).convert('RGBA'))[..., 3], 250)
    return (ORIGIN[0] + tgt[0] - cx0, ORIGIN[1] + tgt[1] - cy0)


def frame(k, ss=4, sky=True, m=None):
    m = m if m is not None else model()
    which, facing, kind = frame_of(k)
    if kind == 'hull':
        return draw(which, facing, ORIGIN, ss, sky, m)
    if kind == 'rack':
        img, trim = draw(which, facing, ORIGIN, ss, sky, m, shift={'rack': T.FRAME_SHIFT}, cast=False)
        t = np.array(trim); t[np.array(img)[..., 3] < 128] = 0
        return img, Image.fromarray(t, 'L')
    # the hull's shadow on its own: its HD silhouette, moved as in-mod/'s, black, softened
    img, _ = draw(which, facing, ORIGIN, ss, False, m)
    a = np.array(img)[..., 3].astype(np.float32) / 255.0
    sh = np.zeros_like(a)
    dx, dy = SHADOW_SHIFT
    sh[dy:, dx:] = a[:a.shape[0] - dy, :a.shape[1] - dx]
    sh = ndimage.gaussian_filter((sh > 0.5).astype(np.float32), 1.5 * PX_SCALE)
    out = np.zeros(a.shape + (4,), np.uint8)
    out[..., 3] = np.round(np.clip(sh, 0, 1) * SHADOW_ALPHA).astype(np.uint8)
    return Image.fromarray(out, 'RGBA'), Image.new('L', CANVAS, 0)


if __name__ == '__main__':
    ks = [int(a) for a in sys.argv[1].split(',')] if len(sys.argv) > 1 else [0]
    ss = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    out = sys.argv[3] if len(sys.argv) > 3 else OUT
    sky = bool(int(sys.argv[4])) if len(sys.argv) > 4 else True
    os.makedirs(out, exist_ok=True)
    for k in ks:
        t0 = time.time()
        img, trim = frame(k, ss, sky)
        save(img, trim, f'{out}/tshvr-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
