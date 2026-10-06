"""
dshprender.py - the TS Dropship's HD frames for the mod (TSDSHP, 656 x 656 at EA's density): frame 0 the ship side-on
and level, facing west, with house colour where TS has it; frames 1-3 its shadow frames, made from frame 0 as the mod's packer makes them
(frame 0 scaled to 55%, 70% and 85% about the canvas centre); and the 32 facings (facings/, 0 N, 8 W, 16 S, 24 E) turned
about the canvas centre so facing 8 is frame 0.  Each with a -trim.png (white = house colour, v3).
It flies: no ground shadow or ground occlusion baked in.

    python3 dshprender.py frames 0,1,2,3 [ss] [outdir] [sky 0/1]
    python3 dshprender.py facings 0,8,16 [ss] [outdir] [sky 0/1]
"""
import os, sys, time
import numpy as np
from PIL import Image
import rc, rcrender as RR
import dshpmodel as T, dshpmat as MM
from dshpcam import CANVAS, ORIGIN, PX_SCALE, camera, unit_to_world, origin_for, FRAME0_FACING
from frameio import save

BOUNDS = ((-62, 62), (-62, 62), (-4, 30))
SHADOW_SCALES = (0.55, 0.70, 0.85)


def find_window(parts, cam, margin=10, step=3):
    W_, H_ = CANVAS
    xs = np.arange(0, W_, step) + step / 2; ys = np.arange(0, H_, step) + step / 2
    SX, SY = np.meshgrid(xs, ys)
    O = cam.rays(SX.ravel(), SY.ravel())
    t, who, _ = rc.cast(parts, O, cam.D, want_normals=False)
    hit = np.isfinite(t).reshape(SX.shape)
    yy, xx = np.nonzero(hit)
    return (max(int(xs[xx.min()] - margin), 0), max(int(ys[yy.min()] - margin), 0),
            min(int(xs[xx.max()] + margin), W_), min(int(ys[yy.max()] + margin), H_))


ROUNDED = {T.TAIL: 0.3, T.NOSE: 0.3, T.TAIL_END: 0.25, T.NOSE_TIP: 0.35, T.DECK: 0.15, T.SPINE: 0.12, T.NOSE_HI: 0.12,
           T.TIP_HI: 0.12, T.HOOD: 0.2, T.CABIN: 0.25, T.NECK: 0.2, T.BLOCK: 0.3, T.BAY: 0.2, T.SKID: 0.2,
           T.SPONSON: 0.35, T.KEEL: 0.2, T.BEAM: 0.35, T.POD: 0.3, T.CAP: 0.15, T.THRUSTER: 0.2, T.COLLAR: 0.15}


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


_GRAD = {}


def field_normals(r):
    """the lofted tail and nose shaded with their smooth bodies' own normals (the tail: TS's smoothed voxels; the nose:
    dshpnose's body, the cockpit's plate in it) where they agree with the facet hit: smooth curves without the lofts'
    facets."""
    import dshpvox as V
    import dshpnose as N
    from scipy.ndimage import map_coordinates
    sc = T.FH.sc
    Rw = np.asarray(r.pose_R, float)
    for comp in (T.TAIL, T.NOSE):
        m = (r.comp == comp) & r.hitmask
        if not m.any():
            continue
        if comp == T.TAIL:
            key = T.G_TAIL
            if key not in _GRAD:
                # the normals from a smoother body than the parts' (TS's single-voxel bumps left out of the shading)
                _GRAD[key] = np.gradient(V.region_smoothed(*key, sig=(1.8, 1.3, 1.3)))
            q = [r.lu[m] - 0.5, r.lv[m] - 0.5, r.lw[m] - 0.5]
            g = -np.stack([map_coordinates(gi, q, order=1) for gi in _GRAD[key]], 1)
        else:
            g = N.normals_q(np.stack([r.lu[m], r.lv[m], r.lw[m]], 1))
        n = (g / sc[None, :]) @ Rw.T
        n = n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)
        own = np.stack([r.gnx[m], r.gny[m], r.gnz[m]], 1)
        ok = (n * own).sum(1) > 0.55
        cur = np.stack([r.nx[m], r.ny[m], r.nz[m]], 1)
        n = np.where(ok[:, None], n, cur)
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


def draw(facing, ss=4, sky=True, m=None):
    m = m if m is not None else model()
    Mx = unit_to_world(facing)
    parts, frames, owner = T.posed(m, ('hull',), Mx)
    cam = camera(origin_for(facing))
    win = find_window(parts, cam)
    r = RR.RCRender(parts, cam, CANVAS, win, BOUNDS, ss=ss, frames=frames, shadow_len=1.0, px_scale=PX_SCALE)
    r.sec = np.where(r.hitmask, 'hull', '')
    r.pose_R = Mx
    r.gnx, r.gny, r.gnz = r.nx.copy(), r.ny.copy(), r.nz.copy()      # the faces' own normals, for the materials
    round_edges(r)
    field_normals(r)
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


def scaled(img, s):
    """frame 0 scaled to s about the canvas centre (the mod's packer's shadow frames)."""
    W_, H_ = CANVAS
    w, h = max(1, int(round(W_ * s))), max(1, int(round(H_ * s)))
    a = np.array(img).astype(np.float32)
    pm = a.copy(); pm[..., :3] *= pm[..., 3:4] / 255.0               # premultiplied, so edges don't pick up black
    sm = np.array(Image.fromarray(pm.round().astype(np.uint8), 'RGBA').resize((w, h), Image.LANCZOS)).astype(np.float32)
    al = sm[..., 3:4]
    sm[..., :3] = np.where(al > 0, sm[..., :3] * 255.0 / np.maximum(al, 1), 0)
    out = Image.new('RGBA', CANVAS, (0, 0, 0, 0))
    out.paste(Image.fromarray(np.clip(sm, 0, 255).round().astype(np.uint8), 'RGBA'), ((W_ - w) // 2, (H_ - h) // 2))
    return out


def frame(k, ss=4, sky=True, m=None, f0=None):
    if k == 0:
        return draw(FRAME0_FACING, ss, sky, m)
    img0 = f0 if f0 is not None else draw(FRAME0_FACING, ss, sky, m)[0]
    return scaled(img0, SHADOW_SCALES[k - 1]), Image.new('L', CANVAS, 0)


if __name__ == '__main__':
    what = sys.argv[1]
    ks = [int(a) for a in sys.argv[2].split(',')] if len(sys.argv) > 2 else [0]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    out = sys.argv[4] if len(sys.argv) > 4 else 'out'
    sky = bool(int(sys.argv[5])) if len(sys.argv) > 5 else True
    os.makedirs(out, exist_ok=True)
    f0 = None
    for k in ks:
        t0 = time.time()
        if what == 'frames':
            img, trim = frame(k, ss, sky, f0=f0)
            if k == 0:
                f0 = img
        else:
            img, trim = draw(k, ss, sky)
        save(img, trim, f'{out}/tsdshp-{k:04d}.png')
        print(what, k, '%.0fs' % (time.time() - t0), flush=True)
