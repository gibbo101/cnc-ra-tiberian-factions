"""
hdv.py - a TS vehicle rebuilt as a clean HD model: convex parts (rc.py) fitted to the voxel's exact shapes (boxes,
hulls of corner points, cylinders, wheels), each with a material (paint, house colour, rubber, metal, glass, lights),
rendered with the buildings' look (hd.py's light, sky, outline, supersampling, the ~75% ground shadow) plus soft
rounded edges on every part, a specular sheen on paint and metal, and the camera fill the units have.  This is the
Titan's and the Wolverine's way, for vehicles: the voxel gives the shapes and the colours; the HD model gives clean
surfaces instead of the voxel's steps and speckle.

Coordinates: the unit frame of nvox (x forward, y left, z up, voxels, the ground at z = 0).  A VoxelFrame turns the
VXL's index space (voxel i spans i..i+1) into it, so parts are written with the numbers the voxel dumps show.

    import hdv
    V = hdv.VoxelFrame(cfg, unit, section=0)
    M = hdv.Model(mats)
    M.add(V.box('paint', (0, 8), (0, 3), (8, 13), ch=0.4), 'pod_r')
    img, trim = hdv.frame(M, cfg, facing)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from scipy.spatial import ConvexHull
import rc, rcrender as RR, hd
import walls2 as W
from walls2 import smoothstep
import voxrender as VR
import nvox as N

GREEN = np.array([0, 214, 0.])
GRIME = np.array([112, 104, 78.])
FILL = 0.32


# ------------------------------------------------------------------------------------------------ parts
class Item:
    """a part with its material and its own frame (R: local axes in the unit frame, c: origin), half sizes h."""

    def __init__(self, part, mat, R, c, h, kind, name='', rnd=None, extra=None):
        self.part, self.mat, self.R, self.c, self.h, self.kind, self.name = part, mat, R, c, np.asarray(h, float), kind, name
        self.rnd = rnd
        self.extra = extra or {}


def moved_item(it, R, t=(0.0, 0.0, 0.0)):
    """a copy of the item turned by R and moved by t (its part, its own frame for patterns, and its centre)."""
    R = np.asarray(R, float); t = np.asarray(t, float)
    return Item(it.part.moved(R, t), it.mat, R @ it.R, R @ np.asarray(it.c, float) + t, it.h, it.kind, it.name, it.rnd,
                dict(it.extra))


def _sphere(pts):
    c = pts.mean(0)
    return c, float(np.sqrt(((pts - c) ** 2).sum(1)).max()) + 1e-3


def box(mat, c, h, R=None, ch=0.0, name='', rnd=None):
    R = np.eye(3) if R is None else np.asarray(R, float)
    p = rc.box(np.asarray(c, float), R, np.asarray(h, float), 0, chamfer=ch, name=name)
    return Item(p, mat, R, np.asarray(c, float), h, 'box', name, rnd)


def hull(mat, pts, name='', rnd=None, R=None):
    """the convex hull of points (unit frame) as a part bounded by planes."""
    pts = np.asarray(pts, float)
    hh = ConvexHull(pts)
    cons = []
    seen = []
    for eq in hh.equations:
        n, off = eq[:3], eq[3]
        key = np.round(np.r_[n, off], 6)
        if any(np.allclose(key, s_, atol=1e-6) for s_ in seen):
            continue
        seen.append(key)
        cons.append(rc.Plane(n, -off))
    c, rad = _sphere(pts[hh.vertices])
    p = rc.Part(cons, 0, name, sphere=(c, rad))
    lo, hi = pts.min(0), pts.max(0)
    return Item(p, mat, np.eye(3) if R is None else R, (lo + hi) / 2, (hi - lo) / 2, 'hull', name, rnd)


def cyl(mat, p0, p1, r, name='', rnd=None, extra_planes=()):
    """a cylinder from p0 to p1 of radius r; its frame: u along the axis, v and w across."""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    p = rc.cylinder(p0, p1, r, 0, name, extra=list(extra_planes))
    a = (p1 - p0) / np.linalg.norm(p1 - p0)
    R = rc.frame_from(a, (0, 0, 1.0) if abs(a[2]) < 0.9 else (1.0, 0, 0))
    L = np.linalg.norm(p1 - p0)
    return Item(p, mat, R, (p0 + p1) / 2, (L / 2, r, r), 'cyl', name, rnd)


def ellip(mat, c, radii, R=None, name='', rnd=None, extra_planes=()):
    R = np.eye(3) if R is None else np.asarray(R, float)
    e = rc.Ellip(np.asarray(c, float), R, np.asarray(radii, float))
    p = rc.Part([e] + list(extra_planes), 0, name, sphere=(np.asarray(c, float), float(max(radii)) + 1e-3))
    return Item(p, mat, R, np.asarray(c, float), radii, 'ellip', name, rnd)


def cut(item, n, point):
    """cut a part by the plane through point with outward normal n (keeps the side n points away from)."""
    n = np.asarray(n, float); n = n / np.linalg.norm(n)
    item.part.cons.append(rc.Plane(n, n @ np.asarray(point, float)))
    return item


class VoxelFrame:
    """index space of one VXL section -> the unit frame (after nvox's lowering)."""

    def __init__(self, cfg, unit, section=0):
        s = unit.sections[section]
        self.R, self.t = unit.pose(section, 0)
        self.mn, self.sc = s.mn, s.scale

    def p(self, i, j, k):
        return self.R @ (self.mn + np.array([i, j, k], float) * self.sc) + self.t

    def box(self, mat, xr, yr, zr, ch=0.0, name='', rnd=None, inset=0.0):
        """the voxels xr = (i0, i1) etc. (inclusive) as one box; inset shrinks it on every side (voxels)."""
        lo = self.p(xr[0], yr[0], zr[0]) + inset
        hi = self.p(xr[1] + 1, yr[1] + 1, zr[1] + 1) - inset
        return box(mat, (lo + hi) / 2, (hi - lo) / 2, R=self.R, ch=ch, name=name, rnd=rnd)

    def hull(self, mat, idx_pts, name='', rnd=None):
        return hull(mat, [self.p(*q) for q in idx_pts], name, rnd)

    def slab(self, mat, x0, x1, y0, y1, z0, z1, ch=0.0, name='', rnd=None):
        """a box between exact index-space bounds (not voxel ranges: x0..x1 is the span itself)."""
        lo = self.p(x0, y0, z0)
        hi = self.p(x1, y1, z1)
        return box(mat, (lo + hi) / 2, np.abs(hi - lo) / 2, R=self.R, ch=ch, name=name, rnd=rnd)

    def prism_span(self, mat, poly, y0, y1, name='', rnd=None):
        """a side profile (x, z index pairs, convex) extruded between the exact index-space bounds y0..y1."""
        pts = [(x, y0, z) for x, z in poly] + [(x, y1, z) for x, z in poly]
        return self.hull(mat, pts, name, rnd)

    def prism_xz(self, mat, poly, yr, name='', rnd=None):
        """a side profile (x, z index pairs, convex) extruded over the voxels yr = (j0, j1) inclusive."""
        pts = [(x, yr[0], z) for x, z in poly] + [(x, yr[1] + 1, z) for x, z in poly]
        return self.hull(mat, pts, name, rnd)

    def prism_xy(self, mat, poly, zr, name='', rnd=None):
        pts = [(x, y, zr[0]) for x, y in poly] + [(x, y, zr[1] + 1) for x, y in poly]
        return self.hull(mat, pts, name, rnd)

    def prism_yz(self, mat, poly, xr, name='', rnd=None):
        pts = [(xr[0], y, z) for y, z in poly] + [(xr[1] + 1, y, z) for y, z in poly]
        return self.hull(mat, pts, name, rnd)

    def cyl_y(self, mat, xc, zc, r, yr, name='', rnd=None):
        """a cylinder across the unit (axis along y): centre (xc, zc) in index units, radius r in voxels, over the
        index range yr = (j0, j1) (faces at j0 and j1 + 1)."""
        return cyl(mat, self.p(xc, yr[0], zc), self.p(xc, yr[1] + 1, zc), r * self.sc[0], name, rnd)

    def cyl_x(self, mat, yc, zc, r, xr, name='', rnd=None):
        return cyl(mat, self.p(xr[0], yc, zc), self.p(xr[1] + 1, yc, zc), r * self.sc[1], name, rnd)

    def cyl_z(self, mat, xc, yc, r, zr, name='', rnd=None):
        return cyl(mat, self.p(xc, yc, zr[0]), self.p(xc, yc, zr[1] + 1), r * self.sc[0], name, rnd)

    def rod(self, mat, a, b, r, name='', rnd=None):
        """a thin rod between two index-space points (an aerial), radius r voxels."""
        return cyl(mat, self.p(*a), self.p(*b), r * self.sc[0], name, rnd)

    def seg(self, mat, a, b, w, d, name='', rnd=None, up=(0, 0, 1.0), ch=0.0):
        """a box from index point a to index point b (its length axis), w voxels across (y) and d deep."""
        pa, pb = self.p(*a), self.p(*b)
        L = np.linalg.norm(pb - pa)
        R = rc.frame_from(pb - pa, up)
        sc = self.sc[0]
        return box(mat, (pa + pb) / 2, (L / 2, w * sc / 2, d * sc / 2), R=R, ch=ch, name=name, rnd=rnd)

    def wheel(self, xc, zc, r, yr, name='wheel', hub_r=0.55, hub_mat='rim', tyre_mat='rubber', cap_mat='hub',
              side='both', dish=0.18):
        """a wheel across the unit: the tyre (a cylinder), a rim disc set into each open side (hub_r of the radius,
        dish voxels proud of the tyre's wall) and a small hub cap."""
        out = [self.cyl_y(tyre_mat, xc, zc, r, yr, name + '_tyre')]
        y0 = self.p(xc, yr[0], zc); y1 = self.p(xc, yr[1] + 1, zc)
        a = (y1 - y0) / np.linalg.norm(y1 - y0)
        rr = r * hub_r * self.sc[0]
        sides = (('lo', y0, -a), ('hi', y1, a)) if side == 'both' else ((side, y0 if side == 'lo' else y1, -a if side == 'lo' else a),)
        for nm, base, outw in sides:
            out.append(cyl(hub_mat, base - outw * 0.25, base + outw * dish, rr, name + '_rim_' + nm))
            out.append(cyl(cap_mat, base, base + outw * (dish + 0.22), rr * 0.38, name + '_cap_' + nm))
        return out


class Model:
    """the parts and the materials: mats = {name: dict(col=(r, g, b), spec=0.2, power=24, house=False, emit=0,
    pattern=callable or None, round=0.35)}."""

    def __init__(self, mats, house=('house',)):
        self.items = []
        self.mats = mats
        self.house = set(house)
        self.markers = {}

    def add(self, *items):
        for it in items:
            if isinstance(it, (list, tuple)):
                self.add(*it)
            else:
                self.items.append(it)
        return self


# ------------------------------------------------------------------------------------------------ shading
def round_normals(r, items, parts_w, default=0.35):
    """soft rounded edges on every part: each hit's normal blends the normals of the part's surfaces near it (a
    softmax on their distances: planes, cylinder walls, ellipsoids), so edges read as rounded and the silhouette
    stays exact."""
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
        S = np.stack(S, 1); Ns = np.stack(Ns, 1)
        w = np.exp((S - S.max(1, keepdims=True)) / sig)
        n = (w[..., None] * Ns).sum(1)
        n = n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)
        r.nx[m], r.ny[m], r.nz[m] = n[:, 0], n[:, 1], n[:, 2]


def grain_of(r, scale=1.0):
    X, Y, Z = r.lu * 6.0 * scale, r.lv * 6.0 * scale, r.lw * 6.0 * scale
    ax, ay, az = np.abs(r.nx) + 1e-3, np.abs(r.ny) + 1e-3, np.abs(r.nz) + 1e-3
    s_ = ax + ay + az

    def tri(noise, o):
        return (W.sample(noise, Y + o, Z + 2 * o) * ax + W.sample(noise, X + 3 * o, Z + o) * ay +
                W.sample(noise, X + o, Y + 5 * o) * az) / s_
    return tri(W.NOISE_FINE, 0) * 0.035 + tri(W.NOISE_MOTTLE, 17) * 0.05


def local_normal(r, m, it):
    """the hits' normals in the part's own frame (its u, v, w axes), whatever the facing."""
    Mw = r.frames_w[it.idx][0]
    return np.stack([r.nx[m], r.ny[m], r.nz[m]], 1) @ Mw


def phase(v, per, off=0.0):
    return np.abs(np.mod(v - off + per / 2, per) - per / 2)


def tread(r, m, it, count=34, depth=0.28):
    """a tyre's tread: grooves across its running surface, and a dark ring on its side walls near the rim; returns a
    brightness factor per hit."""
    rad = np.hypot(r.lv[m], r.lw[m]); R0 = it.h[1]
    ang = np.arctan2(r.lw[m], r.lv[m])
    along = r.lu[m]; half = it.h[0]
    run = rad > 0.9 * R0
    f = np.ones(m.sum(), np.float32)
    groove = run & (phase(ang * count / (2 * np.pi), 1.0) < 0.17) & (np.abs(along) < half * 0.78)
    f[groove] = 1 - depth
    ring = ~run & (np.abs(rad - 0.8 * R0) < 0.12)
    f[ring] *= 0.8
    return f


def rings(r, m, it, at=(0.62,), width=0.1, k=0.7):
    """concentric rings on a disc (a wheel's rim, a hub): darker lines at fractions of its radius."""
    rad = np.hypot(r.lv[m], r.lw[m]) / max(it.h[1], 1e-6)
    f = np.ones(m.sum(), np.float32)
    for a in at:
        f[np.abs(rad - a) < width] = k
    return f


def materials(M, r, items, ground=True):
    sh = r.x.shape
    alb = np.zeros(sh + (3,), np.float32)
    emit = np.zeros(sh + (3,), np.float32)
    spec = np.zeros(sh + (2,), np.float32)          # strength, power
    house = np.zeros(sh, np.float32)
    grain = grain_of(r, scale=1 / 1.5)
    g1 = (1 + 0.45 * grain)
    who = np.where(r.hitmask, r.who, -1)
    for i, it in enumerate(items):
        m = who == i
        if not m.any():
            continue
        mt = M.mats[it.mat]
        if mt.get('house'):
            c = GREEN[None, :] * (1 + 1.1 * grain[m])[:, None]
            house[m] = 1.0
        else:
            c = np.asarray(mt['col'], np.float32)[None, :] * g1[m][:, None]
        f = mt.get('pattern')
        it.idx = i
        if f is not None:
            k = f(r, m, it)
            if k is not None:
                c = c * np.asarray(k, np.float32).reshape(-1, 1) if np.ndim(k) <= 1 else k
        alb[m] = c
        e = mt.get('emit', 0.0)
        if e:
            emit[m] = np.asarray(mt['col'], np.float32)[None, :] * e
        spec[m, 0] = mt.get('spec', 0.18); spec[m, 1] = mt.get('power', 24.0)
    if ground:
        # grime rising from the ground on the lower hull (not on the house colour)
        dust = smoothstep(3.0, 0.4, r.z) * 0.35 * (house < 0.5)
        alb = alb * (1 - dust[..., None]) + (GRIME * g1[..., None]) * dust[..., None]
    alb[~r.hitmask] = 0
    return alb, emit, spec, house


def blocked(parts, O, D):
    """True for rays (origins O, one direction D) that pass through any part ahead of their origin."""
    D = np.asarray(D, float)
    out = np.zeros(len(O), bool)
    e1 = np.cross(D, (0.0, 0.0, 1.0) if abs(D[2]) < 0.9 else (1.0, 0.0, 0.0)); e1 /= np.linalg.norm(e1)
    e2 = np.cross(D, e1)
    ra = O @ e1; rb = O @ e2
    order = np.argsort(ra, kind='stable'); ra_s = ra[order]
    for p in parts:
        c, R = p.sphere
        ca, cb = float(np.asarray(c) @ e1), float(np.asarray(c) @ e2)
        lo, hi = np.searchsorted(ra_s, ca - R), np.searchsorted(ra_s, ca + R, side='right')
        if hi <= lo:
            continue
        cand = order[lo:hi]
        da = ra[cand] - ca; db = rb[cand] - cb
        sel = cand[(da * da + db * db <= R * R) & ~out[cand]]
        if sel.size == 0:
            continue
        tin, tout = rc.intersect(p, O[sel], D)[:2]
        out[sel[(tin < tout) & (tout > 1e-3)]] = True
    return out


def sky_occlusion_rt(r, parts_w, n_az=12, elev=(28.0, 58.0), top=True, off=0.06, stride=2, blur=0.8):
    """the sky's occlusion by ray casting (exact, no shadow-map acne on thin or touching parts): the fraction of the
    sky directions a surface faces that the model blocks; computed on every stride-th supersampled pixel with many
    directions, then spread and softened (blur, in output px) so it reads as soft ambient occlusion, not as the
    hard shadows of a few directions."""
    from scipy import ndimage
    dirs = []
    for e in elev:
        for i in range(n_az):
            a = 2 * np.pi * (i + 0.5 + (0.5 if e != elev[0] else 0.0)) / n_az
            dirs.append((np.cos(a) * np.cos(np.deg2rad(e)), np.sin(a) * np.cos(np.deg2rad(e)), np.sin(np.deg2rad(e))))
    if top:
        dirs.append((0.0, 0.2, 0.98))
    hm = r.hitmask
    sub = np.zeros_like(hm); sub[::stride, ::stride] = True
    sel = hm & sub
    P = np.stack([r.x[sel], r.y[sel], r.z[sel]], 1).astype(float)
    Nn = np.stack([r.nx[sel], r.ny[sel], r.nz[sel]], 1).astype(float)
    blk = np.zeros(len(P), np.float32); cnt = np.zeros(len(P), np.float32)
    for d in dirs:
        d = np.array(d) / np.linalg.norm(d)
        facing = (Nn @ d) > 0.05
        if not facing.any():
            continue
        O = P[facing] + Nn[facing] * off + d * off
        b = blocked(parts_w, O, d)
        w = (Nn[facing] @ d)                      # cosine-weighted
        blk[facing] += b * w; cnt[facing] += w
    occ_s = np.full(hm.shape, np.nan, np.float32)
    occ_s[sel] = np.where(cnt > 0, blk / np.maximum(cnt, 1e-6), 0.0)
    # spread to every hit pixel from the nearest sample of the same part, then soften within each part
    who = np.where(hm, r.who, -1)
    occ = np.zeros(hm.shape, np.float32)
    have = ~np.isnan(occ_s)
    idx = ndimage.distance_transform_edt(~have, return_distances=False, return_indices=True)
    occ = occ_s[idx[0], idx[1]]
    occ = np.nan_to_num(occ)
    sig = blur * r.ss
    if sig > 0:
        num = np.zeros_like(occ); den = np.zeros_like(occ)
        for i in np.unique(who[hm]):
            m = (who == i).astype(np.float32)
            num += ndimage.gaussian_filter(occ * m, sig) * m
            den += ndimage.gaussian_filter(m, sig) * m
        occ = np.where(den > 1e-6, num / np.maximum(den, 1e-6), occ)
    occ[~hm] = 0
    return occ


def find_window(parts, cam, size, margin=14, step=3):
    return VR.find_window(parts, cam, size, margin, step)


def frame(M, cfg, facing, ss=4, sky=True, shadow=None, return_r=False):
    """one HD frame of the model at the mod's facing (counter-clockwise from north, 32)."""
    shadow = (not cfg.aircraft) if shadow is None else shadow
    Mx = VR.facing_cw(VR.mod_to_cw(facing))
    items = M.items
    parts_w = []
    frames = []
    for it in items:
        p = it.part.moved(Mx)
        parts_w.append(p)
        frames.append((Mx @ it.R, Mx @ it.c))
    cam = N.camera(cfg)
    win = find_window(parts_w, cam, cfg.canvas)
    r = RR.RCRender(parts_w, cam, cfg.canvas, win, cfg.bounds, ss=ss, frames=frames, shadow_len=cfg.shadow_len,
                    px_scale=getattr(cfg, 'px_scale', 1.5))
    r.frames_w = frames
    round_normals(r, items, parts_w)
    occ = sky_occlusion_rt(r, parts_w) if sky else None
    alb, emit, spec, house = materials(M, r, items, ground=not cfg.aircraft)
    ao = (0.86 + 0.14 * np.clip(r.z / 12.0, 0, 1)) if not cfg.aircraft else None
    col = r.shade(alb, sky_occ=occ, ao=ao)
    # the fill light from the camera on the sides that face it (EA's HD units are front-lit)
    tc = np.array([cam.T[0] * cam.cE, cam.T[1] * cam.cE, cam.sE]); tc = tc / np.linalg.norm(tc)
    nf = np.clip(r.nx * tc[0] + r.ny * tc[1] + r.nz * tc[2], 0, 1) * (1 - np.clip(r.nz, 0, 1))
    if occ is not None:
        nf = nf * (1 - 0.85 * np.clip(occ, 0, 1))
    col = col + alb * (getattr(cfg, 'fill', FILL) * nf)[..., None] + emit
    # an exposure (cfg.gain, the infantry's: EA's HD infantry are drawn brighter than its vehicles): the luminance
    # lifted along a curve that keeps white at white, the hue kept (house pixels keep R = B = 0)
    gain = getattr(cfg, 'gain', 1.0)
    if gain != 1.0:
        lum = col[..., 0] * 0.299 + col[..., 1] * 0.587 + col[..., 2] * 0.114
        f = lum * gain / (1.0 + (gain - 1.0) * np.clip(lum, 0, 255) / 255.0)
        col = col * (f / np.maximum(lum, 1e-3))[..., None]
    # a specular sheen (Blinn) from the key light, dimmed in shadow
    L = r.L; V = -cam.D
    Hh = (L + V) / np.linalg.norm(L + V)
    nh = np.clip(r.nx * Hh[0] + r.ny * Hh[1] + r.nz * Hh[2], 0, 1)
    shd = getattr(r, 'inshadow', 0.0)
    s = spec[..., 0] * nh ** np.maximum(spec[..., 1], 1.0) * (1 - 0.9 * shd)
    # the sheen on house colour stays in the green channel (house pixels keep R = B = 0)
    tint = np.where(house[..., None] > 0.5, np.array([0.0, 1.0, 0.0]), np.array([1.0, 0.98, 0.94]))
    col = col + (s * 255.0)[..., None] * tint
    col[~r.hitmask] = 0
    g = r.ground_alpha_full(shadow_parts=parts_w) if shadow else None
    img = r.compose(col, ground=g)
    full = np.zeros((r.H * ss, r.W * ss), np.float32)
    x0, y0, x1, y1 = r.win
    full[y0 * ss:y1 * ss, x0 * ss:x1 * ss] = house * r.hitmask
    trim = Image.fromarray((full.reshape(r.H, ss, r.W, ss).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L')
    if return_r:
        return img, trim, r
    return img, trim


# ------------------------------------------------------------------------------------------------ checks
def flat_ids(M, cfg, facing, ss=1):
    """the model's silhouette (bool) at a facing, no shading: for checking it against TS's voxels."""
    Mx = VR.facing_cw(VR.mod_to_cw(facing))
    parts_w = [it.part.moved(Mx) for it in M.items]
    cam = N.camera(cfg)
    W_, H_ = cfg.canvas
    t, who, nrm, O = rc.render_ids(parts_w, rc.Cam((0, -1), 32.0, cfg.ppu, cfg.origin), 0, 0, W_, H_, ss=ss)
    return np.isfinite(t), who


# ------------------------------------------------------------------------------------------------ 3D model
def export(M, cfg, path, name, markers=(), cells_px=192.0, east=24, groups=None):
    """the model as a .glb: a node per part (grouped under unit_facing_east), each mesh exact (the part's convex
    solid), vertex colours = the part's material colour (TS's colours brightened as in the frames), COLOR_1 = house;
    marker nodes; the mod's camera framing the canvas."""
    import rcexport as RX
    from export3d import orient
    import vexport as VE
    upc = cells_px / cfg.ppu
    glb = VE.AnimGLB()
    root = glb.node(name)
    Mx = VR.facing_cw(VR.mod_to_cw(east))
    face = glb.node('unit_facing_east', root, rotation=VE.quat(VE.A @ Mx))
    gnode = {}
    for gname, (pivot, prefixes) in (groups or {}).items():
        gnode[gname] = (glb.node(gname, face, translation=np.asarray(pivot, float) / upc), np.asarray(pivot, float),
                        tuple(prefixes))
    for it in M.items:
        m = RX.part_mesh(it.part)
        if m is None:
            continue
        V_, F = m
        smooth = it.kind in ('cyl', 'ellip')
        P, Fi, Nn = (RX.smooth_shaded if smooth else RX.flat_shaded)(V_, F)
        parent, off = face, np.zeros(3)
        for gname, (gn, pivot, prefixes) in gnode.items():
            if (it.name or '').startswith(prefixes):
                parent, off = gn, pivot
        Pg = (P - off) / upc
        Fi = orient(Pg, Fi, Nn)
        mt = M.mats[it.mat]
        col = GREEN if mt.get('house') else np.asarray(mt['col'], float)
        rgb = np.tile(np.minimum(col, 255.0), (len(Pg), 1))
        hs = np.full(len(Pg), 1.0 if mt.get('house') else 0.0)
        glb.node(it.name or it.mat, parent, mesh=(Pg.astype(np.float32), Fi, Nn.astype(np.float32), rgb, hs))
    for mk in markers:
        mname, p = mk[0], np.asarray(mk[1], float)
        if len(mk) > 2 and mk[2] in gnode:                 # a marker that moves with a group (a turret's muzzle)
            gn, pivot, _ = gnode[mk[2]]
            glb.node(mname, gn, translation=(p - pivot) / upc)
        else:
            glb.node(mname, face, translation=p / upc)
    cam = N.camera(cfg)
    W_, H_ = cfg.canvas
    gx, gy = cam.ground(np.array([W_ / 2.0]), np.array([H_ / 2.0]))
    elev = float(np.degrees(np.arcsin(cam.sE)))
    glb.camera('camera_mod', 0.0, elev, list(VE.A @ np.array([gx[0], gy[0], 0.0]) / upc), W_ / 2.0 / cells_px,
               H_ / 2.0 / cells_px, extras=dict(note='orthographic, %g degrees above the ground, looking north; frames '
                                                     'the %d x %d canvas' % (round(elev, 2), W_, H_)))
    glb.save(path, extras=dict(units='1.0 = one cell (128 px in the game; %d px on the canvas)' % cells_px, facing='east'))
    return path
