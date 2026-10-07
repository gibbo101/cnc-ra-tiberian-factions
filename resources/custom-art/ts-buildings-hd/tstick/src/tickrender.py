"""The dug-in Tick Tank's views and canvases, rendered with the units chat's renderer (src/hdv.py, src/rcrender.py: the
buildings' light, outline and ~75% shadow, for models made of convex parts) at the buildings' scale (128 px a cell,
4.17 px a voxel; the units' own canvas is 192 px a cell, which the game draws at two thirds):
  RA grid  (ra):  RA's camera (32 degrees, looking north), the 1x1 plot centred.  The tank stays where the unit stands:
                  its position (TS's HVA origin, the cell's centre) on the canvas centre's ground point, as the units
                  hand-off draws it (192, 191 on its 384 x 384 canvas = 128, 127.33 at two thirds), so it doesn't move
                  when it deploys.  Facing east (TS's way round).
  TS angle (iso): TS's camera (30 degrees, looking north-west), TS's frame x3.77 (TS px (0, 0) at canvas (0, 0)),
                  the cell's centre where TS's 96x48 GTTICK frames put it.  Optional."""
import os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(HERE, 'src'), HERE):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import fakeunit as F
import tickm as K
import nvox as N, rcrender as RR, hdv
import voxrender as VR

RA_LEFT, RA_HEAD = int(os.environ.get('RA_LEFT', 64)), int(os.environ.get('RA_HEAD', 64))
CANVAS = {'ra': (128 + 2 * RA_LEFT, 128 + 2 * RA_HEAD), 'iso': (int(os.environ.get('ISO_W', 368)), int(os.environ.get('ISO_H', 208)))}
PLOT = {'ra': (RA_LEFT, RA_HEAD, RA_LEFT + 128, RA_HEAD + 128)}
ISO_K = 1.0 / 0.265165
TS_GROUND = (48.0, 24.0 + 6.0 * 2)         # TS's 96x48 frames: the cell's centre at (W/2, H/2 + 12)
UNIT_Y = 191.0 * 2.0 / 3.0 - 128.0         # the unit's ground point below the canvas centre, at two thirds (-0.67)


def origin(v):
    if v == 'iso':
        return TS_GROUND[0] * ISO_K, TS_GROUND[1] * ISO_K
    W, H = CANVAS['ra']
    return W / 2.0, H / 2.0 + UNIT_Y


_orig_camera = N.camera


def _camera(cfg):
    return getattr(cfg, 'cam', None) or _orig_camera(cfg)


N.camera = _camera


def cfg(v):
    c = F.cfg(canvas=CANVAS[v], ppu=K.VOX_PX_BLD, origin=origin(v), px_scale=1.0)
    c.bounds = ((-60, 60), (-60, 60), (-25, 35))
    c.cam = None
    if v == 'iso':
        c.cam = RR.Cam((-np.sqrt(0.5), -np.sqrt(0.5)), 30.0, K.VOX_PX_BLD, origin(v))
    return c


def round_normals(r, items, parts_w, skip_ground=False, default=0.35):
    """hdv.round_normals, leaving the cut at the ground sharp (a part going into the ground has no rounded edge
    there) when skip_ground."""
    for i, (it, p) in enumerate(zip(items, parts_w)):
        sig = it.rnd if it.rnd is not None else default
        if sig <= 0:
            continue
        m = (r.who == i) & r.hitmask
        if not m.any():
            continue
        Q = np.stack([r.x[m], r.y[m], r.z[m]], 1)
        S, Ns = [], []
        for c in p.cons:
            if c.kind == 'plane':
                if skip_ground and c.n[2] < -0.9999 and abs(c.d) < 1e-6:
                    continue
                S.append(Q @ c.n - c.d); Ns.append(np.broadcast_to(c.n, Q.shape))
            elif c.kind == 'cyl':
                q = Q - c.c; perp = q - (q @ c.a)[:, None] * c.a
                ln = np.linalg.norm(perp, axis=1)
                S.append(ln - c.r); Ns.append(perp / (ln[:, None] + 1e-9))
            elif c.kind == 'ellip':
                q = (Q - c.c) @ c.R / c.r[None, :]
                ln = np.linalg.norm(q, axis=1)
                g = (q / c.r[None, :]) @ c.R.T
                S.append((ln - 1) * c.r.min()); Ns.append(g / (np.linalg.norm(g, axis=1, keepdims=True) + 1e-9))
        if not S:
            continue
        S = np.stack(S, 1); Ns = np.stack(Ns, 1)
        w = np.exp((S - S.max(1, keepdims=True)) / sig)
        n = (w[..., None] * Ns).sum(1)
        n = n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)
        r.nx[m], r.ny[m], r.nz[m] = n[:, 0], n[:, 1], n[:, 2]


def berm_normals(r, items, h, Mx, eps=0.2, bump=0.32):
    """the berm's columns shaded with the heightfield's own normals (smooth), plus a fine crumbly bump."""
    from wnoise import noise
    idx = [i for i, it in enumerate(items) if it.name == 'soil_col']
    m = np.isin(np.where(r.hitmask, r.who, -1), idx)
    if not m.any():
        return
    Q = np.stack([r.x[m], r.y[m], r.z[m]], 1) @ Mx                 # world -> unit frame
    x, y = Q[:, 0], Q[:, 1]
    hx = (h(x + eps, y) - h(x - eps, y)) / (2 * eps)
    hy = (h(x, y + eps) - h(x, y - eps)) / (2 * eps)
    e2 = 0.12
    bx = (noise(x + e2, y, 0.45, 111) - noise(x - e2, y, 0.45, 111)) / (2 * e2)
    by = (noise(x, y + e2, 0.45, 111) - noise(x, y - e2, 0.45, 111)) / (2 * e2)
    n = np.stack([-hx - bump * 0.25 * bx, -hy - bump * 0.25 * by, np.ones_like(x)], 1)
    n = n / np.linalg.norm(n, axis=1, keepdims=True)
    nw = n @ Mx.T                                                     # unit frame -> world
    r.nx[m], r.ny[m], r.nz[m] = nw[:, 0], nw[:, 1], nw[:, 2]


def frame(M, c, ss=4, sky=True, shadow=True, decal=None, skip_ground=None, return_r=False, shadow_from=None):
    """hdv.frame for the tank facing east, with a decal hook (paint over the materials: soil on the nose, damage) and
    the ground cut left sharp once the tank pitches.  shadow_from: names' prefixes of the parts that cast the ground
    shadow (None: all)."""
    if skip_ground is None:
        skip_ground = getattr(M, 't', 0.0) > 0
    Mx = VR.facing_cw(VR.mod_to_cw(K.FACING))
    items = M.items
    parts_w, frames = [], []
    for it in items:
        parts_w.append(it.part.moved(Mx))
        frames.append((Mx @ it.R, Mx @ it.c))
    cam = N.camera(c)
    win = hdv.find_window(parts_w, cam, c.canvas)
    r = RR.RCRender(parts_w, cam, c.canvas, win, c.bounds, ss=ss, frames=frames, shadow_len=c.shadow_len,
                    px_scale=getattr(c, 'px_scale', 1.0))
    r.frames_w = frames
    round_normals(r, items, parts_w, skip_ground)
    if getattr(M, 'berm_h', None) is not None:
        berm_normals(r, items, M.berm_h, Mx)
    occ = hdv.sky_occlusion_rt(r, parts_w) if sky else None
    alb, emit, spec, house = hdv.materials(M, r, items, ground=True)
    if decal is not None:
        decal(r, alb, emit, spec, house, M, Mx)
    ao = 0.86 + 0.14 * np.clip(r.z / 12.0, 0, 1)
    col = r.shade(alb, sky_occ=occ, ao=ao)
    tc = np.array([cam.T[0] * cam.cE, cam.T[1] * cam.cE, cam.sE]); tc = tc / np.linalg.norm(tc)
    nf = np.clip(r.nx * tc[0] + r.ny * tc[1] + r.nz * tc[2], 0, 1) * (1 - np.clip(r.nz, 0, 1))
    if occ is not None:
        nf = nf * (1 - 0.85 * np.clip(occ, 0, 1))
    col = col + alb * (hdv.FILL * nf)[..., None] + emit
    L = r.L; Vv = -cam.D
    Hh = (L + Vv) / np.linalg.norm(L + Vv)
    nh = np.clip(r.nx * Hh[0] + r.ny * Hh[1] + r.nz * Hh[2], 0, 1)
    shd = getattr(r, 'inshadow', 0.0)
    s = spec[..., 0] * nh ** np.maximum(spec[..., 1], 1.0) * (1 - 0.9 * shd)
    tint = np.where(house[..., None] > 0.5, np.array([0.0, 1.0, 0.0]), np.array([1.0, 0.98, 0.94]))
    col = col + (s * 255.0)[..., None] * tint
    col[~r.hitmask] = 0
    g = None
    if shadow:
        sp = parts_w if shadow_from is None else [p for p, it in zip(parts_w, items)
                                                   if (it.name or '').startswith(tuple(shadow_from))]
        g = r.ground_alpha_full(shadow_parts=sp)
    img = r.compose(col, ground=g)
    full = np.zeros((r.H * ss, r.W * ss), np.float32)
    x0, y0, x1, y1 = r.win
    full[y0 * ss:y1 * ss, x0 * ss:x1 * ss] = house * r.hitmask
    trim = Image.fromarray((full.reshape(r.H, ss, r.W, ss).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L')
    if return_r:
        return img, trim, r
    return img, trim


def coverage(r, items, prefixes):
    """the fraction of each output pixel covered by parts whose names start with prefixes (full canvas)."""
    ss = r.ss
    idx = [i for i, it in enumerate(items) if (it.name or '').startswith(tuple(prefixes))]
    m = np.isin(np.where(r.hitmask, r.who, -1), idx).astype(np.float32)
    full = np.zeros((r.H * ss, r.W * ss), np.float32)
    x0, y0, x1, y1 = r.win
    full[y0 * ss:y1 * ss, x0 * ss:x1 * ss] = m
    return full.reshape(r.H, ss, r.W, ss).mean(axis=(1, 3))


def unit_frame(c, ss=4, sky=True):
    """the tank as the units hand-off draws it (its hull frame with the hull's shadow, its turret frame laid over it
    with no shadow, EA's way), at this canvas's scale: build-up frame 00."""
    u = K.unit()
    import ttnk3hd as T
    hull = T.build_hull(c, u)
    tur = T.build_turret(c, u)
    a, at = hdv.frame(hull, c, K.FACING, ss, sky)
    b, bt = hdv.frame(tur, c, K.FACING, ss, sky, shadow=False)
    img = a.copy(); img.alpha_composite(b)
    ta = np.array(at).astype(np.float32); tb = np.array(bt).astype(np.float32)
    ab = np.array(b)[..., 3].astype(np.float32) / 255.0
    trim = Image.fromarray(np.clip(tb + ta * (1 - ab), 0, 255).round().astype(np.uint8), 'L')
    return img, trim
