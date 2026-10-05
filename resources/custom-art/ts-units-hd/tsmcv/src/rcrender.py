"""
rcrender.py - hd.py's look (walls2's light, sky and ambient, the ~75% blurred ground shadow, the contact
shadow, the 0.9 px dark outline, x4 supersampling with a premultiplied downsample, fading shadows at the
canvas edge) for models made of convex parts (rc.py), cast ray by ray.

The camera may stretch heights differently from depths (cE_eff): the Titan keeps the in-mod frames' heights
(TS's 30 degree view scaled x6.4) while its depths foreshorten like the 32 degree RA camera.
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
import rc
import hd
import walls2 as W


class Cam:
    """screen x = ox + ppu (p.R);  screen y = oy + ppu (sE (p.T) - cE z).  Light vectors are given in
    camera terms (R, T, z) as hd.py's are, and turned into world vectors."""

    def __init__(self, look, elev, ppu, origin, cE=None):
        F = np.array(look, float); F = F / np.linalg.norm(F)
        self.F = F; self.R = np.array([-F[1], F[0]]); self.T = -F
        E = np.deg2rad(elev)
        self.sE = float(np.sin(E)); self.cE = float(np.cos(E)) if cE is None else float(cE)
        self.ppu = float(ppu); self.ox, self.oy = origin
        d = np.array([F[0] * self.cE, F[1] * self.cE, -self.sE])
        self.D = d / np.linalg.norm(d)

    def cam_to_world(self, v):
        w = v[0] * np.array([self.R[0], self.R[1], 0]) + v[1] * np.array([self.T[0], self.T[1], 0]) + v[2] * np.array([0, 0, 1.0])
        return w / np.linalg.norm(w)

    def project(self, P):
        P = np.asarray(P, float)
        pr = P[..., 0] * self.R[0] + P[..., 1] * self.R[1]
        pt = P[..., 0] * self.T[0] + P[..., 1] * self.T[1]
        return self.ox + self.ppu * pr, self.oy + self.ppu * (self.sE * pt - self.cE * P[..., 2])

    def rays(self, sx, sy, zstart=300.0):
        pr = (np.asarray(sx, float) - self.ox) / self.ppu
        q = (np.asarray(sy, float) - self.oy) / self.ppu
        z = np.full(np.shape(pr), zstart)
        pt = (q + self.cE * z) / self.sE
        X = pr * self.R[0] + pt * self.T[0]
        Y = pr * self.R[1] + pt * self.T[1]
        return np.stack([X, Y, z], axis=-1)

    def ground(self, sx, sy):
        """the ground point (z = 0) seen at each screen point."""
        pr = (np.asarray(sx, float) - self.ox) / self.ppu
        pt = (np.asarray(sy, float) - self.oy) / (self.ppu * self.sE)
        return pr * self.R[0] + pt * self.T[0], pr * self.R[1] + pt * self.T[1]


def ra_cam(ppu, origin, cE=None):
    return Cam((0, -1), 32.0, ppu, origin, cE=cE)


L_CAM = hd.L_CAM
LS_CAM = hd.LS_CAM


class LightMap:
    """the scene seen along a light direction Ls (pointing towards the light): depth of the first surface
    for each light-grid point; test() says how much each point is shadowed (pcf)."""

    def __init__(self, parts, Ls, bounds, step):
        Ls = np.asarray(Ls, float); Ls = Ls / np.linalg.norm(Ls)
        self.Ls = Ls
        # an orthonormal basis: e1, e2 across the light, Ls along it
        e1 = np.cross(Ls, [0, 0, 1.0])
        if np.linalg.norm(e1) < 1e-6:
            e1 = np.array([1.0, 0, 0])
        e1 = e1 / np.linalg.norm(e1); e2 = np.cross(Ls, e1)
        self.e1, self.e2 = e1, e2
        (xa, xb), (ya, yb), (za, zb) = bounds
        corners = np.array([(x, y, z) for x in (xa, xb) for y in (ya, yb) for z in (za, zb)], float)
        a = corners @ e1; b = corners @ e2; c = corners @ Ls
        self.a0, self.b0, self.step = a.min() - 2 * step, b.min() - 2 * step, step
        na = int(np.ceil((a.max() - a.min()) / step)) + 4; nb = int(np.ceil((b.max() - b.min()) / step)) + 4
        A, B = np.meshgrid(self.a0 + (np.arange(na) + 0.5) * step, self.b0 + (np.arange(nb) + 0.5) * step)
        start = c.max() + 10.0
        O = A.ravel()[:, None] * e1 + B.ravel()[:, None] * e2 + start * Ls
        t, who, _ = rc.cast(parts, O, -Ls, want_normals=False)
        # depth: how far towards the light the first surface is (along Ls)
        self.depth = np.where(np.isfinite(t), start - t, -np.inf).reshape(A.shape).astype(np.float32)
        self.na, self.nb = na, nb

    def test(self, P, bias=0.15, pcf=1):
        P = np.asarray(P, float)
        a = P @ self.e1; b = P @ self.e2; d = P @ self.Ls
        acc = np.zeros(P.shape[:-1], np.float32); n = 0
        for ob in range(-pcf, pcf + 1):
            for oa in range(-pcf, pcf + 1):
                ia = np.floor((a - self.a0) / self.step + 0.5 * oa).astype(int)
                ib = np.floor((b - self.b0) / self.step + 0.5 * ob).astype(int)
                inside = (ia >= 0) & (ia < self.na) & (ib >= 0) & (ib < self.nb)
                ia = np.clip(ia, 0, self.na - 1); ib = np.clip(ib, 0, self.nb - 1)
                acc += inside & (self.depth[ib, ia] > d + bias)
                n += 1
        return acc / n


class RCRender:
    """parts: world-space rc.Parts; frames: per part (M, t) mapping its local frame to the world (for
    texturing in the part's own frame); window: (x0, y0, x1, y1) canvas px to cast (the rest is ground)."""

    def __init__(self, parts, cam, size, window, bounds, ss=hd.SS, frames=None, light_step=None, occluders=None,
                 shadow_len=1.0, px_scale=1.0):
        # px_scale: canvas px per on-screen px (1.5 for a canvas the game draws at 2/3, as the mod's TS units), so
        # the outline and the shadow's softness come out as wide in the game as on the buildings
        self.px_scale = px_scale
        self.parts, self.cam, self.ss = parts, cam, ss
        self.occluders = parts if occluders is None else occluders
        self.W, self.H = size
        self.bounds = bounds
        x0, y0, x1, y1 = [int(v) for v in window]
        x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, self.W), min(y1, self.H)
        self.win = (x0, y0, x1, y1)
        xs = x0 + (np.arange((x1 - x0) * ss) + 0.5) / ss
        ys = y0 + (np.arange((y1 - y0) * ss) + 0.5) / ss
        SX, SY = np.meshgrid(xs, ys)
        self.SX, self.SY = SX, SY
        O = cam.rays(SX.ravel(), SY.ravel())
        t, who, nrm = rc.cast(parts, O, cam.D)
        hit = np.isfinite(t)
        P = O + np.where(hit, t, 0.0)[:, None] * cam.D
        sh = SX.shape
        self.hitmask = hit.reshape(sh)
        self.who = who.reshape(sh)
        self.x, self.y, self.z = [P[:, i].reshape(sh).astype(np.float32) for i in range(3)]
        nrm = nrm / (np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9)
        self.nx, self.ny, self.nz = [nrm[:, i].reshape(sh).astype(np.float32) for i in range(3)]
        comps = np.array([p.comp for p in parts] + [0])
        self.comp = comps[self.who].astype(np.int32)
        self.comp[~self.hitmask] = 0
        # local coordinates per hit (the part's own frame)
        self.lu = np.zeros(sh, np.float32); self.lv = np.zeros(sh, np.float32); self.lw = np.zeros(sh, np.float32)
        if frames is not None:
            for i, (M, tt) in enumerate(frames):
                m = self.who == i
                if not m.any():
                    continue
                Q = np.stack([self.x[m], self.y[m], self.z[m]], 1) - np.asarray(tt, float)
                L = Q @ np.asarray(M, float)                 # M columns = local axes in world
                self.lu[m], self.lv[m], self.lw[m] = L[:, 0], L[:, 1], L[:, 2]
        step = light_step or 0.8 / (cam.ppu)
        self.L = cam.cam_to_world(L_CAM)
        Ls = cam.cam_to_world(LS_CAM)
        # shadow_len < 1 steepens the shadow light (same direction, shorter shadows), e.g. so a tall unit's
        # shadow stays on its canvas
        Ls = np.array([Ls[0] * shadow_len, Ls[1] * shadow_len, Ls[2]])
        self.Ls = Ls / np.linalg.norm(Ls)
        self.sm = LightMap(self.occluders, self.Ls, bounds, step)

    # ------------------------------------------------------------------ lighting (hd.Render's formulas)
    def sky_occlusion(self, n_az=8, elev=(38.0,), top=True, step_scale=2.0):
        dirs = []
        for e in elev:
            for i in range(n_az):
                a = 2 * np.pi * (i + 0.5) / n_az
                dirs.append((np.cos(a) * np.cos(np.deg2rad(e)), np.sin(a) * np.cos(np.deg2rad(e)), np.sin(np.deg2rad(e))))
        if top:
            dirs.append((0.0, 0.2, 0.98))
        blocked = np.zeros(self.x.shape, np.float32); count = np.zeros(self.x.shape, np.float32)
        P = np.stack([self.x, self.y, self.z], -1)
        N = np.stack([self.nx, self.ny, self.nz], -1)
        off = 1.5 / self.cam.ppu * 1.0
        for d in dirs:
            d = np.array(d) / np.linalg.norm(d)
            lm = LightMap(self.occluders, d, self.bounds, self.sm.step * step_scale)
            facing = (N @ d) > 0.05
            b = lm.test(P + N * off, bias=0.25, pcf=0)
            blocked += facing * b; count += facing
        occ = np.where(count > 0, blocked / np.maximum(count, 1), 0.0).astype(np.float32)
        occ[~self.hitmask] = 0
        return occ

    def shadow(self, bias=0.15):
        P = np.stack([self.x, self.y, self.z], -1)
        return self.sm.test(P, bias=bias, pcf=1)

    def shade(self, albedo, sky_occ=None, ao=None, shadow_extra=None, normals=None):
        L = self.L
        nx, ny, nz = (self.nx, self.ny, self.nz) if normals is None else normals
        ndl = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, None)
        sh = self.shadow()
        if shadow_extra is not None:
            sh = np.maximum(sh, shadow_extra)
        self.inshadow = sh
        sky = W.SKY * (0.5 + 0.5 * nz)
        if sky_occ is not None:
            sky = sky * (1 - sky_occ)
        amb = W.AMBIENT * (np.ones_like(nz) if sky_occ is None else (1 - 0.55 * sky_occ))
        shade = amb + sky + W.DIFFUSE * ndl * (1 - 0.8 * sh)
        if ao is not None:
            shade = shade * ao
        return albedo * shade[..., None]

    # ------------------------------------------------------------------ ground and compositing
    def ground_alpha_full(self, shadow_parts=None, contact_px=7.0, footprint_z=1.0, blur=1.5):
        contact_px = contact_px * self.px_scale; blur = blur * self.px_scale
        """the ground shadow over the whole canvas (at ss), from this render's light map (or another made
        from shadow_parts) + the contact shadow round the footprint."""
        ss = self.ss
        xs = (np.arange(self.W * ss) + 0.5) / ss; ys = (np.arange(self.H * ss) + 0.5) / ss
        SX, SY = np.meshgrid(xs, ys)
        gx, gy = self.cam.ground(SX, SY)
        sm = self.sm if shadow_parts is None else LightMap(shadow_parts, self.Ls, self.bounds, self.sm.step)
        P = np.stack([gx, gy, np.zeros_like(gx)], -1)
        g = sm.test(P, bias=0.05, pcf=1)
        shadow_a = ndimage.gaussian_filter(g.astype(np.float32), blur * ss) * W.SHADOW_ALPHA
        # footprint: ground points inside a part just above the ground (only inside the cast window)
        fp = np.zeros(gx.shape, bool)
        parts = self.occluders if shadow_parts is None else shadow_parts
        x0, y0, x1, y1 = self.win
        sl = (slice(y0 * ss, y1 * ss), slice(x0 * ss, x1 * ss))
        gxw, gyw = gx[sl], gy[sl]
        Pz = np.stack([gxw.ravel(), gyw.ravel(), np.full(gxw.size, footprint_z)], 1)
        fw = np.zeros(gxw.size, bool)
        # only the points under each part's bounding sphere are tested against it (sorted along x)
        order = np.argsort(Pz[:, 0], kind='stable'); xs_sorted = Pz[order, 0]
        for p in parts:
            if p.sphere is not None:
                c0, R0 = p.sphere
                if abs(c0[2] - footprint_z) > R0:
                    continue
                lo, hi = np.searchsorted(xs_sorted, c0[0] - R0), np.searchsorted(xs_sorted, c0[0] + R0, side='right')
                if hi <= lo:
                    continue
                cand = order[lo:hi]
                cand = cand[np.abs(Pz[cand, 1] - c0[1]) <= R0]
            else:
                cand = np.arange(len(Pz))
            if cand.size == 0:
                continue
            Q = Pz[cand]
            inside = np.ones(len(Q), bool)
            for c in p.cons:
                if c.kind == 'plane':
                    inside &= Q @ c.n <= c.d
                elif c.kind == 'ellip':
                    q = (Q - c.c) @ (c.R / c.r[None, :])
                    inside &= (q * q).sum(1) <= 1
                elif c.kind == 'cyl':
                    q = Q - c.c; qa = q @ c.a
                    inside &= ((q - qa[:, None] * c.a) ** 2).sum(1) <= c.r ** 2
                if not inside.any():
                    break
            fw[cand[inside]] = True
        fw = fw.reshape(gxw.shape)
        fp[sl] = fw
        if fp.any():
            dist = ndimage.distance_transform_edt(~fp) / ss
            contact = np.clip(1 - dist / contact_px, 0, 1) ** 1.5 * 0.5
        else:
            contact = np.zeros(gx.shape, np.float32)
        return np.maximum(shadow_a, contact)

    def compose(self, col, ground=None, outline=True, only=None):
        """col: lit colour per hit (window grid).  ground: full-canvas ground alpha (ss grid) or None.
        Returns the full canvas RGBA image."""
        ss = self.ss
        Hs, Ws = self.H * ss, self.W * ss
        x0, y0, x1, y1 = self.win
        hit = np.zeros((Hs, Ws), bool)
        rgb = np.zeros((Hs, Ws, 3), np.float32)
        hm = self.hitmask if only is None else (self.hitmask & only)
        hit[y0 * ss:y1 * ss, x0 * ss:x1 * ss] = hm
        rgb[y0 * ss:y1 * ss, x0 * ss:x1 * ss] = np.where(hm[..., None], col, 0.0)
        rgba = np.zeros((Hs, Ws, 4), np.float32)
        rgba[..., :3] = rgb
        a = np.where(hit, 1.0, ground if ground is not None else 0.0)
        rgba[..., 3] = a
        if outline:
            ring = ndimage.binary_dilation(hit, iterations=max(1, int(round(0.9 * ss * self.px_scale)))) & ~hit
            if only is not None:
                full = np.zeros((Hs, Ws), bool); full[y0 * ss:y1 * ss, x0 * ss:x1 * ss] = self.hitmask
                ring &= ~full
            rgba[..., :3] = np.where(ring[..., None], hd.BLACK_OUT, rgba[..., :3])
            rgba[..., 3] = np.where(ring, np.maximum(rgba[..., 3], 0.55), rgba[..., 3])
        return hd.fade_edges(hd.downsample(rgba, ss))
