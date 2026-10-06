"""
sonrender.py - the Disruptor's HD frames for the mod (TSSONIC, 448 x 448: 0-31 the hull with its shadow, 32-63 the
turret - its ring and the dish - without one, its pivot where the mod has it; 32 facings counter-clockwise from north),
each with a -trim.png, from the rebuilt model (sonmodel.py) posed by TS's HVAs.  Cameras, sizes and places as v1 and the
mod (soncam.py).  The canvas is drawn at two thirds in the game, so the outline, the shadow's blur and the contact
shadow are 1.5 times as wide (as the other units').

    python3 sonrender.py 0,24,56 [ss] [outdir] [sky 0/1]
"""
import os, sys, time
import numpy as np
from PIL import Image
import rc, rcrender as RR
import sonmodel as T, sonmat as MM
from soncam import CANVAS, camera, unit_to_world, frame_of
from frameio import save

SHADOW_LEN = 1.0
PX_SCALE = 1.5
BOUNDS = ((-36, 36), (-36, 36), (-1, 30))
OUT = 'out'


def find_window(parts, cam, margin=14, step=3):
    W_, H_ = CANVAS
    xs = np.arange(0, W_, step) + step / 2; ys = np.arange(0, H_, step) + step / 2
    SX, SY = np.meshgrid(xs, ys)
    O = cam.rays(SX.ravel(), SY.ravel())
    t, who, _ = rc.cast(parts, O, cam.D, want_normals=False)
    hit = np.isfinite(t).reshape(SX.shape)
    yy, xx = np.nonzero(hit)
    return (max(int(xs[xx.min()] - margin), 0), max(int(ys[yy.min()] - margin), 0),
            min(int(xs[xx.max()] + margin), W_), min(int(ys[yy.max()] + margin), H_))


ROUNDED = {T.OCHRE: 0.3, T.BODY: 0.2, T.GREEN: 0.25, T.BLACK: 0.15, T.OLIVE: 0.15, T.BASE: 0.2,
           T.HOUSING: 0.2, T.DISH: 0.15, T.STRUT: 0.1, T.BRACE: 0.12, T.KHAKI: 0.1, T.BELT: 0.2,
           T.CROSS: 0.2, T.BRACKET: 0.05, T.GLASS: 0.03}


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


def smooth_rim(r, Mx):
    """the rim's segments shaded as one round ring: its upright faces' normals turned to point straight out from (or in
    to) the turret's axis."""
    m = (r.comp == T.RIM) & r.hitmask
    if not m.any():
        return
    R, t = T.pose('tur')
    c = Mx @ (R @ T.FT.p((T.TC[0], T.TC[1], 0.0)) + t)
    d = np.stack([r.x[m] - c[0], r.y[m] - c[1]], 1)
    d = d / (np.linalg.norm(d, axis=1, keepdims=True) + 1e-9)
    nz = r.nz[m]
    up = np.abs(nz) < 0.6
    sgn = np.sign(r.nx[m] * d[:, 0] + r.ny[m] * d[:, 1])
    h = np.sqrt(np.clip(1 - nz ** 2, 0, 1))
    r.nx[m] = np.where(up, sgn * d[:, 0] * h, r.nx[m])
    r.ny[m] = np.where(up, sgn * d[:, 1] * h, r.ny[m])


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


def frame(k, ss=4, sky=True, m=None):
    which, facing, tur = frame_of(k)
    Mx = unit_to_world(facing)
    parts, frames, owner = T.posed(m if m is not None else model(), which, Mx)
    cam = camera(tur)
    win = find_window(parts, cam)
    r = RR.RCRender(parts, cam, CANVAS, win, BOUNDS, ss=ss, frames=frames, shadow_len=SHADOW_LEN, px_scale=PX_SCALE)
    r.sec = np.where(r.hitmask, owner[np.clip(r.who, 0, len(owner) - 1)], '')
    r.pose_R = Mx
    round_edges(r)
    smooth_rim(r, Mx)
    occ = r.sky_occlusion() if sky else None
    alb, (bx, by, bz), emit = MM.materials(r, occ=occ)
    ao = 0.84 + 0.16 * np.clip(r.z / 12.0, 0, 1)
    col = r.shade(alb, sky_occ=occ, ao=ao) + emit
    col = col * np.clip(1 + 0.3 * bz, 0.55, 1.35)[..., None]
    col = col + spec_hl(r, MM.GLOSSY)
    g = None if tur else r.ground_alpha_full(shadow_parts=parts)
    img = r.compose(col, ground=g)
    tm = MM.trim_mask(r, alb).astype(np.float32)
    full = np.zeros((r.H * ss, r.W * ss), np.float32)
    x0, y0, x1, y1 = r.win
    full[y0 * ss:y1 * ss, x0 * ss:x1 * ss] = tm
    trim = Image.fromarray((full.reshape(r.H, ss, r.W, ss).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L')
    return img, trim


if __name__ == '__main__':
    ks = [int(a) for a in sys.argv[1].split(',')] if len(sys.argv) > 1 else [0]
    ss = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    out = sys.argv[3] if len(sys.argv) > 3 else OUT
    sky = bool(int(sys.argv[4])) if len(sys.argv) > 4 else True
    os.makedirs(out, exist_ok=True)
    for k in ks:
        t0 = time.time()
        img, trim = frame(k, ss, sky)
        save(img, trim, f'{out}/tssonic-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
