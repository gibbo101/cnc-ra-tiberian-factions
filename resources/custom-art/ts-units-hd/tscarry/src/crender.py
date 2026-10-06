"""
crender.py - the Carryall's HD frames for the mod (TSCARRY, 448 x 448, 32 facings counter-clockwise from north, no
shadow: it flies, and the game draws its shadow from the frame), each with a -trim.png, from the rebuilt model
(cmodel.py) posed by TS's HVA.  Camera, size and place as v1 and the mod (ccam.py).  The canvas is drawn at two thirds
in the game, so the outline is 1.5 times as wide (as the other units').  No ground grime or occlusion.

    python3 crender.py 0,12,24 [ss] [outdir] [sky 0/1]
"""
import os, sys, time
import numpy as np
from PIL import Image
import rc, rcrender as RR
import cmodel as T, cmat as MM
from ccam import CANVAS, PX_SCALE, camera, unit_to_world
from frameio import save

BOUNDS = ((-34, 34), (-34, 34), (-2, 22))
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


ROUNDED = {T.SPINE: 0.3, T.POD: 0.3, T.TAILB: 0.35, T.ARM: 0.22, T.CAB: 0.25, T.KEEL: 0.15, T.BRACKET: 0.15,
           T.CLAW: 0.2, T.FINGER: 0.18, T.TIP: 0.12, T.GEAR: 0.15, T.SKID: 0.22, T.STRUT: 0.15, T.STRAP: 0.08}


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


def _set(r, m, n_loc, Mx):
    n = n_loc @ Mx.T
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    r.nx[m], r.ny[m], r.nz[m] = n[:, 0], n[:, 1], n[:, 2]


def ring_normals(r):
    """the round parts made of flat facets shaded with their true normals at each hit, so they read round: the fans'
    rims and straps (radial, inwards on the duct's wall), the hoist's bell (a cone), the engine (a cylinder along x),
    the tail's duct and its lips (radial round the duct's axis, across the fin)."""
    Mx = np.asarray(r.pose_R, float)
    hm = r.hitmask
    own_all = np.stack([r.gnx, r.gny, r.gnz], -1) @ Mx                 # the facets' normals, in the unit's frame
    # the fans
    m = np.isin(r.comp, T.RINGS) & hm
    if m.any():
        x, y = r.lu[m], r.lv[m]
        _, cx, cy = MM.nearest_fan(x, y)
        rad = np.stack([x - cx, y - cy, np.zeros_like(x)], 1)
        rad /= np.linalg.norm(rad, axis=1, keepdims=True) + 1e-9
        own = own_all[m]
        wall = np.abs(own[:, 2]) < 0.6
        sgn = np.sign((own[:, :2] * rad[:, :2]).sum(1))
        n_loc = rad * sgn[:, None] * np.sqrt(np.clip(1 - own[:, 2:3] ** 2, 0, 1)) + np.array([0, 0, 1.0]) * own[:, 2:3]
        n_loc = np.where(wall[:, None], n_loc, own)
        _set(r, m, n_loc, Mx)
    # the bell: a cone (r 5.0 at z 7 to 3.35 at z 10.05)
    m = (r.comp == T.BELL) & hm
    if m.any():
        own = own_all[m]
        x, y = r.lu[m], r.lv[m]
        rad = np.stack([x - T.BELL_C[0], y - T.BELL_C[1], np.zeros_like(x)], 1)
        rad /= np.linalg.norm(rad, axis=1, keepdims=True) + 1e-9
        (r0, z0), (r1, z1) = T.BELL_R
        k = (r0 - r1) / (z1 - z0)
        cone = rad + np.array([0, 0, 1.0]) * k
        cone /= np.linalg.norm(cone, axis=1, keepdims=True)
        side = own[:, 2] > -0.6
        _set(r, m, np.where(side[:, None], cone, own), Mx)
    # the engine: a cylinder along x
    m = (r.comp == T.NACELLE) & hm
    if m.any():
        own = own_all[m]
        rad = np.stack([np.zeros_like(r.lu[m]), r.lv[m] - T.HYC, r.lw[m] - T.NAC_C[0]], 1)
        rad /= np.linalg.norm(rad, axis=1, keepdims=True) + 1e-9
        wall = np.abs(own[:, 0]) < 0.75
        _set(r, m, np.where(wall[:, None], rad, own), Mx)
    # the tail's duct (the fin's pieces' faces round the hole) and its lips
    for comp in (T.FIN, T.LIP):
        m = (r.comp == comp) & hm
        if not m.any():
            continue
        own = own_all[m]
        x, z = r.lu[m], r.lw[m]
        dx, dz = x - T.DUCT_C[0], z - T.DUCT_C[1]
        rd = np.hypot(dx, dz)
        rad = np.stack([dx, np.zeros_like(dx), dz], 1) / (rd[:, None] + 1e-9)
        across = np.abs(own[:, 1]) < 0.6
        if comp == T.FIN:
            sel = across & (rd < T.DUCT_R + 0.08)
            n_loc = np.where(sel[:, None], -rad, own)
        else:
            sgn = np.sign((own[:, [0, 2]] * rad[:, [0, 2]]).sum(1))
            n_loc = np.where(across[:, None], rad * sgn[:, None], own)
        _set(r, m, n_loc, Mx)


def sky_occlusion(r, n_az=8, elev=(38.0,), step_scale=2.0):
    """rcrender's sky occlusion with each direction weighted by how squarely it meets the surface (and the test point
    lifted further off surfaces it meets at a glancing angle), so big flat faces that a direction only grazes (the
    tail fin's sides) carry no banding from the light maps; the other units' formula otherwise."""
    dirs = []
    for e in elev:
        for i in range(n_az):
            a = 2 * np.pi * (i + 0.5) / n_az
            dirs.append((np.cos(a) * np.cos(np.deg2rad(e)), np.sin(a) * np.cos(np.deg2rad(e)), np.sin(np.deg2rad(e))))
    dirs.append((0.0, 0.2, 0.98))
    blocked = np.zeros(r.x.shape, np.float32); count = np.zeros(r.x.shape, np.float32)
    P = np.stack([r.x, r.y, r.z], -1)
    N = np.stack([r.nx, r.ny, r.nz], -1)
    off = 1.5 / r.cam.ppu
    for d in dirs:
        d = np.array(d) / np.linalg.norm(d)
        lm = RR.LightMap(r.occluders, d, r.bounds, r.sm.step * step_scale)
        nd = N @ d
        wgt = np.clip((nd - 0.05) / 0.3, 0, 1)
        lift = off * (1.0 + 2.0 * (1 - np.clip(nd / 0.35, 0, 1)))
        b = lm.test(P + N * lift[..., None], bias=0.25, pcf=0)
        blocked += wgt * b; count += wgt
    occ = np.where(count > 0, blocked / np.maximum(count, 1e-6), 0.0).astype(np.float32)
    occ[~r.hitmask] = 0
    return occ


def shadow_offset(r, k=2.0, bias=0.15):
    """the key light's shadow as rcrender's (its light map, bias and soft edge), tested from each point lifted off its
    face along the face's normal by k light-map steps, so faces the light meets at an angle carry no stripes (shadow
    acne) from the light map's steps."""
    P = np.stack([r.x, r.y, r.z], -1)
    N = np.stack([r.gnx, r.gny, r.gnz], -1)
    return r.sm.test(P + N * (k * r.sm.step), bias=bias, pcf=1)


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
    r.shadow = lambda bias=0.15: shadow_offset(r, bias=bias)
    occ = sky_occlusion(r) if sky else None
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
        save(img, trim, f'{out}/tscarry-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
