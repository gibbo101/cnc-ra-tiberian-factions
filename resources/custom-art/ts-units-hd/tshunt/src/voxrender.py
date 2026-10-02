"""
voxrender.py - render a TS voxel unit (vxlunit.Sections posed by its HVA) with the buildings' look: the RA-grid
style orthographic camera, hd.py's light, sky, ambient, outline and supersampling (rcrender), the camera fill on the
sides facing the camera, TS's own colours on every surface, house colour pure green where TS's remap voxels are.

A Unit describes the voxel model; frame(unit, facing, hva_frame, cam, ...) returns (RGBA image, trim image).
"""
import numpy as np
from PIL import Image
import rc, rcrender as RR
import walls2 as W
from walls2 import smoothstep

GREEN = np.array([0, 214, 0.])
GRIME = np.array([112, 104, 78.])
FILL = 0.32
GAIN = 1.25
WHITE_CAP = 236.0


def facing_cw(k, n=32):
    th = 2 * np.pi * k / n
    f = np.array([np.sin(th), -np.cos(th), 0.0]); r = np.array([np.cos(th), np.sin(th), 0.0])
    # unit frame (x forward, y left, z up) -> world (x east, y south, z up)
    return np.stack([f, -r, np.array([0, 0, 1.0])], axis=1)


def mod_to_cw(f, n=32):
    return (n - f) % n


class Unit:
    """sections: [vxlunit.Section]; mats: one HVA's matrices (frames, sections, 3, 4) for all of them, or a list with
    one (mats, index) per section (sections from several VXL files, each with its own HVA), or None.
    extra_pose: optional per-section (R, t) applied after the HVA (a turret's offset, a pitch)."""

    def __init__(self, sections, mats=None, comps=None, extra_pose=None):
        self.sections = sections
        self.mats = mats
        self.comps = comps or list(range(200, 200 + len(sections)))
        self.extra_pose = extra_pose

    def pose(self, i, hf):
        if self.mats is None:
            R, t = np.eye(3), np.zeros(3)
        elif isinstance(self.mats, list):
            M, j = self.mats[i]
            M = M[min(hf, len(M) - 1), j]
            R, t = M[:, :3], M[:, 3] * self.sections[i].det
        else:
            M = self.mats[hf, i]
            R, t = M[:, :3], M[:, 3] * self.sections[i].det
        if self.extra_pose is not None and self.extra_pose[i] is not None:
            Re, te = self.extra_pose[i]
            R, t = Re @ R, Re @ t + te
        return R, t

    def parts(self, hf, Mx):
        out, owner, poses = [], [], []
        for i, s in enumerate(self.sections):
            R, t = self.pose(i, hf)
            Rw, tw = Mx @ R, Mx @ t
            poses.append((Rw, tw))
            ps = s.parts(Rw, tw, self.comps[i])
            out += ps; owner += [i] * len(ps)
        return out, np.array(owner), poses


def find_window(parts, cam, size, margin=14, step=3):
    W_, H_ = size
    xs = np.arange(0, W_, step) + step / 2; ys = np.arange(0, H_, step) + step / 2
    SX, SY = np.meshgrid(xs, ys)
    O = cam.rays(SX.ravel(), SY.ravel())
    t, who, _ = rc.cast(parts, O, cam.D, want_normals=False)
    hit = np.isfinite(t).reshape(SX.shape)
    yy, xx = np.nonzero(hit)
    return (max(int(xs[xx.min()] - margin), 0), max(int(ys[yy.min()] - margin), 0),
            min(int(xs[xx.max()] + margin), W_), min(int(ys[yy.max()] + margin), H_))


def grain_of(r, P, scale=1.0):
    X, Y, Z = P[..., 0] * 6.0 * scale, P[..., 1] * 6.0 * scale, P[..., 2] * 6.0 * scale
    ax, ay, az = np.abs(r.nx) + 1e-3, np.abs(r.ny) + 1e-3, np.abs(r.nz) + 1e-3
    s_ = ax + ay + az

    def tri(noise, o):
        return (W.sample(noise, Y + o, Z + 2 * o) * ax + W.sample(noise, X + 3 * o, Z + o) * ay +
                W.sample(noise, X + o, Y + 5 * o) * az) / s_
    return tri(W.NOISE_FINE, 0) * 0.035 + tri(W.NOISE_MOTTLE, 17) * 0.05


def round_exposed(r, parts, sigma, unit=None, owner=None, poses=None):
    """rounded edges in the shading: each pixel's normal blends the planes of its part that face the air at that
    place (softmax on their distances): a box face counts where the voxel just across it is empty, so convex edges
    read rounded and the joins between a section's boxes stay invisible."""
    hm = r.hitmask
    who = r.who
    idx_all = np.nonzero(hm)
    W_ = who[idx_all]
    order = np.argsort(W_, kind='stable')
    Ws = W_[order]
    bnd = np.searchsorted(Ws, np.arange(len(parts) + 1))
    nx, ny, nz = r.nx.copy(), r.ny.copy(), r.nz.copy()
    for i, p in enumerate(parts):
        a, b = bnd[i], bnd[i + 1]
        if b <= a:
            continue
        sel = order[a:b]
        yy, xx = idx_all[0][sel], idx_all[1][sel]
        planes = [c for c in p.cons if c.kind == 'plane']
        N = np.array([c.n for c in planes]); d = np.array([c.d for c in planes])
        Q = np.stack([r.x[yy, xx], r.y[yy, xx], r.z[yy, xx]], 1)
        s = Q @ N.T - d[None, :]
        ok = np.ones(s.shape, bool)
        box = getattr(p, 'box', None)
        if box is not None and unit is not None:
            sec = unit.sections[owner[i]]
            Rw, tw = poses[owner[i]]
            I = sec.to_index(Q, Rw, tw)
            i0, i1, j0, j1, k0, k1 = box
            lo = (i0, j0, k0); hi = (i1, j1, k1)
            X, Y, Z = sec.solid.shape
            for f in range(6):
                ax, sgn = f // 2, (-1 if f % 2 == 0 else 1)
                J = np.floor(I).astype(int)
                J[:, ax] = (lo[ax] - 1) if sgn < 0 else (hi[ax] + 1)
                for o in range(3):
                    if o != ax:
                        J[:, o] = np.clip(J[:, o], (lo[o]), (hi[o]))
                inside = np.all((J >= 0) & (J < np.array([X, Y, Z])), axis=1)
                Jc = np.clip(J, 0, np.array([X, Y, Z]) - 1)
                solid_there = inside & sec.solid[Jc[:, 0], Jc[:, 1], Jc[:, 2]]
                ok[:, f] = ~solid_there
        s = np.where(ok, s, -1e3)
        w = np.exp((s - s.max(1, keepdims=True)) / sigma) * ok
        n = w @ N
        n = n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)
        nx[yy, xx], ny[yy, xx], nz[yy, xx] = n[:, 0], n[:, 1], n[:, 2]
    return nx, ny, nz


def frame(unit, facing, hf, cam, size, bounds, ss=4, sky=True, shadow_len=1.0, px_scale=1.5, sharp=None,
          speckle=(0.62, 1.28), grime_z=3.6, extra=None, normals='edges', round_sigma=0.28, with_shadow=True,
          occluders=None, house_detail=True, ts_normals=0.0, ground_ao=True, ts_max_tilt=25.0):
    """one frame: the unit at the mod's facing (counter-clockwise from north, 32), posed at HVA frame hf."""
    Mx = facing_cw(mod_to_cw(facing))
    parts, owner, poses = unit.parts(hf, Mx)
    win = find_window(parts, cam, size)
    r = RR.RCRender(parts, cam, size, win, bounds, ss=ss, shadow_len=shadow_len, px_scale=px_scale,
                    occluders=None if occluders is None else occluders(Mx))
    hm = r.hitmask
    sh = hm.shape
    P = np.stack([r.x, r.y, r.z], -1)
    Ng = np.stack([r.nx, r.ny, r.nz], -1).copy()                    # the boxes' own face normals
    sec = np.full(sh, -1, int)
    sec[hm] = owner[r.who[hm]]
    rgb = np.zeros(sh + (3,), np.float32); wcol = np.zeros(sh, np.float32); whouse = np.zeros(sh, np.float32)
    lmean = np.zeros(sh, np.float32); hshade = np.ones(sh, np.float32)
    tsn = np.zeros(sh + (3,), np.float32)
    Ns = Ng.copy()
    for i, s in enumerate(unit.sections):
        m = sec == i
        if not m.any():
            continue
        Rw, tw = poses[i]
        I = s.to_index(P[m], Rw, tw)
        # the smoothed solid's normal for shading
        if normals == 'field':
            Ns[m] = s.normal(I, Rw)
        # the face normal in index space, for TS's colours
        nI = np.linalg.solve(Rw, Ng[m].T).T * s.scale[None, :]
        shp = (sharp or {}).get(i, 1.0)
        c, wc, wh, lm, hs, tn = s.sample(I, nI, sharp=shp)
        rgb[m] = c; wcol[m] = wc; whouse[m] = wh; lmean[m] = lm; hshade[m] = hs
        tw = (Rw @ (tn / s.scale[None, :]).T).T
        tsn[m] = tw / (np.linalg.norm(tw, axis=1, keepdims=True) + 1e-9)
    if normals == 'field':
        r.nx, r.ny, r.nz = Ns[..., 0], Ns[..., 1], Ns[..., 2]
    else:
        r.nx, r.ny, r.nz = round_exposed(r, parts, round_sigma, unit, owner, poses)
    if ts_normals > 0:
        # TS's own voxel normals as a layer of detail: their difference from the face's own normal added in
        nr = np.stack([r.nx, r.ny, r.nz], -1)
        dv = (tsn - Ng) * (np.linalg.norm(tsn, axis=-1, keepdims=True) > 0.5)
        nn = nr + ts_normals * dv
        nn = nn / (np.linalg.norm(nn, axis=-1, keepdims=True) + 1e-9)
        if ts_max_tilt is not None:
            # the detail may tilt the shading normal by at most ts_max_tilt degrees: TS's single voxels whose normal
            # points far from their face (down, into a seam) shade as a seam, not as a black hole
            c = np.clip((nn * nr).sum(-1, keepdims=True), -1, 1)
            cm = np.cos(np.deg2rad(ts_max_tilt))
            perp = nn - c * nr
            perp = perp / (np.linalg.norm(perp, axis=-1, keepdims=True) + 1e-9)
            nn = np.where(c < cm, cm * nr + np.sqrt(1 - cm * cm) * perp, nn)
        nn[~hm] = 0
        r.nx, r.ny, r.nz = nn[..., 0], nn[..., 1], nn[..., 2]
    occ = r.sky_occlusion() if sky else None
    grain = grain_of(r, P, 1 / 1.5)
    g1 = (1 + 0.45 * grain)[..., None]
    # TS's colours, their darkest and lightest single voxels held near the colour round them
    lum = rgb.mean(-1)
    if speckle is not None:
        k = np.clip(lum, speckle[0] * lmean, speckle[1] * lmean) / np.maximum(lum, 1e-3)
        # TS's near-black and near-white voxels are details (hatches, slots, studs): they keep their colour
        keep = (lum < 70) | (lum > 205)
        rgb = rgb * np.where((wcol > 0.3) & ~keep, k, 1.0)[..., None]
    alb = np.minimum(rgb * GAIN, WHITE_CAP) * g1
    # grime rising from the ground
    zu = r.z
    dust = smoothstep(grime_z, grime_z * 0.18, zu) * 0.35 if grime_z > 0 else np.zeros_like(zu)
    alb = alb * (1 - dust[..., None]) + (GRIME * g1) * dust[..., None]
    house = np.clip((whouse - 0.35) / 0.3, 0, 1) * hm
    hs = hshade if house_detail else 1.0
    alb = alb * (1 - house[..., None]) + house[..., None] * GREEN[None, None, :] * (hs * (1 + 1.1 * grain))[..., None]
    alb[~hm] = 0
    if extra is not None:
        alb = extra(r, alb, sec, P)
    ao = 0.86 + 0.14 * np.clip(r.z / 12.0, 0, 1) if ground_ao else None     # the ground's occlusion low on the hull
    col = r.shade(alb, sky_occ=occ, ao=ao)
    tc = np.array([cam.T[0] * cam.cE, cam.T[1] * cam.cE, cam.sE]); tc = tc / np.linalg.norm(tc)
    nf = np.clip(r.nx * tc[0] + r.ny * tc[1] + r.nz * tc[2], 0, 1) * (1 - np.clip(r.nz, 0, 1))
    if occ is not None:
        nf = nf * (1 - 0.85 * np.clip(occ, 0, 1))
    col = col + alb * (FILL * nf)[..., None]
    g = r.ground_alpha_full(shadow_parts=parts) if with_shadow else None
    img = r.compose(col, ground=g)
    full = np.zeros((r.H * ss, r.W * ss), np.float32)
    x0, y0, x1, y1 = r.win
    full[y0 * ss:y1 * ss, x0 * ss:x1 * ss] = house * hm
    trim = Image.fromarray((full.reshape(r.H, ss, r.W, ss).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L')
    return img, trim
