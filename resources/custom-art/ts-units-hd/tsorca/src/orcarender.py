"""
orcarender.py - the Orca Fighter's HD frames for the mod (TSORCA, 384 x 384, 32 facings counter-clockwise from north,
no shadow: it flies, and the game draws its shadow from the frame), each with a -trim.png, from the rebuilt model
(orcamodel.py) posed by TS's HVA.  Camera, size and place as v1 and the mod (orcacam.py).  The canvas is drawn at two
thirds in the game, so the outline is 1.5 times as wide (as the other units').  No ground grime or occlusion.

    python3 orcarender.py 0,12,24 [ss] [outdir] [sky 0/1]
"""
import os, sys, time
import numpy as np
from PIL import Image
import rc, rcrender as RR
import orcamodel as T, orcamat as MM
from orcacam import CANVAS, PX_SCALE, camera, unit_to_world
from frameio import save

BOUNDS = ((-30, 30), (-30, 30), (-2, 18))
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


ROUNDED = {T.POD: 0.3, T.COVER: 0.15, T.BODY: 0.25, T.DECK: 0.2, T.HUMP: 0.3, T.HATCH: 0.08, T.KEEL: 0.25,
           T.NOSE: 0.22, T.TIP: 0.3, T.CHIN: 0.3, T.BULKHEAD: 0.15, T.BOOM: 0.3, T.STAB: 0.25, T.FIN: 0.18,
           T.CONE: 0.25, T.CANOPY: 0.04}


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


def ring_normals(r):
    """the rings (the fans', the tail fan's housing) are made of flat sectors: their walls shaded with the true radial
    normal at each hit (inwards on the inner walls), so they read round."""
    Mx = np.asarray(r.pose_R, float)
    for comp in T.RINGS:
        m = (r.comp == comp) & r.hitmask
        if not m.any():
            continue
        x, y = r.lu[m], r.lv[m]
        if comp == T.FAN:
            cy = np.where(y > T.HYC, T.FAN_C[1][1], T.FAN_C[0][1]); cx = np.full_like(x, T.FAN_C[0][0])
        else:
            cx = np.full_like(x, T.TAIL_C[0]); cy = np.full_like(y, T.TAIL_C[1])
        rad = np.stack([x - cx, y - cy, np.zeros_like(x)], 1)
        rad /= np.linalg.norm(rad, axis=1, keepdims=True) + 1e-9
        own = np.stack([r.gnx[m], r.gny[m], r.gnz[m]], 1) @ Mx           # the facet's normal, in the unit's frame
        wall = np.abs(own[:, 2]) < 0.6
        sgn = np.sign((own[:, :2] * rad[:, :2]).sum(1))
        n_loc = rad * sgn[:, None] * np.sqrt(np.clip(1 - own[:, 2:3] ** 2, 0, 1)) + np.array([0, 0, 1.0]) * own[:, 2:3]
        n_loc = np.where(wall[:, None], n_loc, own)
        n = n_loc @ Mx.T
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
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


def frame(k, ss=4, sky=True, m=None):
    Mx = unit_to_world(k)
    parts, frames, owner = T.posed(m if m is not None else model(), ('hull',), Mx)
    cam = camera()
    win = find_window(parts, cam)
    r = RR.RCRender(parts, cam, CANVAS, win, BOUNDS, ss=ss, frames=frames, shadow_len=1.0, px_scale=PX_SCALE)
    r.sec = np.where(r.hitmask, 'hull', '')
    r.pose_R = Mx
    r.gnx, r.gny, r.gnz = r.nx.copy(), r.ny.copy(), r.nz.copy()      # the faces' own normals, for the materials
    round_edges(r)
    ring_normals(r)
    occ = r.sky_occlusion() if sky else None
    alb, (bx, by, bz), emit = MM.materials(r, occ=occ)
    col = r.shade(alb, sky_occ=occ, ao=None) + emit
    col = col * np.clip(1 + 0.3 * bz, 0.55, 1.35)[..., None]
    col = col + spec_hl(r, MM.GLOSSY)
    img = r.compose(col, ground=None)
    tm = MM.trim_mask(r, alb).astype(np.float32)
    full = np.zeros((r.H * ss, r.W * ss), np.float32)
    x0, y0, x1, y1 = r.win
    full[y0 * ss:y1 * ss, x0 * ss:x1 * ss] = tm
    trim = Image.fromarray((full.reshape(r.H, ss, r.W, ss).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L')
    return img, trim


if __name__ == '__main__':
    ks = [int(a) for a in sys.argv[1].split(',')] if len(sys.argv) > 1 else [24]
    ss = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    out = sys.argv[3] if len(sys.argv) > 3 else OUT
    sky = bool(int(sys.argv[4])) if len(sys.argv) > 4 else True
    os.makedirs(out, exist_ok=True)
    for k in ks:
        t0 = time.time()
        img, trim = frame(k, ss, sky)
        save(img, trim, f'{out}/tsorca-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
