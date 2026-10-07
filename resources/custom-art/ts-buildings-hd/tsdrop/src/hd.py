"""
hd.py - the shared HD renderer for the Tiberian Sun -> Red Alert Remastered rebuilds.

Generalises the component tower's renderer (ct_ra.py) so one model can be rendered from any camera, with
overhangs you can see under (a vault shell, a leaning crane boom), while keeping the tower's look exactly:
walls2's light, sky and ambient terms, colours, noise, grime, ~75% baked shadow, contact shadow, the 0.9 px
dark outline and x4 supersampling with a premultiplied downsample.

Geometry.  A model is a function of world ground position (X east, Y south, units; 1 cell = 128) returning
a Scene: a ground-attached heightfield H (with component ids C) plus any number of Slabs (a layer from bot
to top over each ground point, with its own component ids).

Camera.  A true orthographic camera looking along a horizontal direction F at an elevation E, with ppu
screen px per world unit:  screen x = ox + ppu (p.R),  screen y = oy + ppu (sinE (p.T) - cosE z),
R = screen right, T = towards the viewer.  RA grid: looking north, E = 32.  TS: looking north-west, E = 30.
Everything is sampled on a ground grid aligned with the screen (screen x, and screen y of the ground point),
so a ray drops one grid row per super-sampled px of screen height - the walls' own march.

Light is defined relative to the camera (from the upper left, as on every RA/TD building), so both views
are lit the same way on screen.  Shadows use a shadow map: the scene rendered from the light.
"""
import numpy as np
from PIL import Image
from scipy import ndimage
import walls2 as W

SS = 4
# walls2's light in camera terms (R, T, z): from the upper left of the screen, above
L_CAM = np.array([-0.45, -0.55, 0.70]); L_CAM = L_CAM / np.linalg.norm(L_CAM)
# the direction the tower/walls' shadows fall on screen (walls2.SHADOW_DIR, per unit of screen height at
# 0.6) expressed as a light for the true 32-degree camera, so shadows land exactly where the tower's do
_s, _c = np.sin(np.deg2rad(32.0)), np.cos(np.deg2rad(32.0))
_sd = np.array(W.SHADOW_DIR) / W.FZ                     # screen px per px of screen height
LS_CAM = np.array([-_sd[0] * _c, -_sd[1] * _c / _s, 1.0]); LS_CAM = LS_CAM / np.linalg.norm(LS_CAM)
BLACK_OUT = 28.0
# TS's own view (looking north-west): TS lights the south faces (lower left) and shades the east faces
# (lower right), so the light comes from the screen's left, a little in front; shadows fall to the right
L_CAM_TS = np.array([-0.62, 0.16, 0.77]); L_CAM_TS = L_CAM_TS / np.linalg.norm(L_CAM_TS)
LS_CAM_TS = np.array([-0.70, -0.05, 0.71]); LS_CAM_TS = LS_CAM_TS / np.linalg.norm(LS_CAM_TS)


def ra_view(size, origin, ppu=1.0, margin=(64, 64), ss=SS):
    """RA grid: a true orthographic camera 32 degrees above the ground, looking north (the tower's)."""
    return View((0, -1), 32.0, ppu, size, origin, margin=margin, ss=ss)


def ts_view(size, origin, ppu, margin=(64, 64), ss=SS):
    """TS's own camera: 30 degrees above the ground, looking north-west."""
    return View((-1, -1), 30.0, ppu, size, origin, margin=margin, ss=ss, light=L_CAM_TS, shadow_light=LS_CAM_TS)


TS_PPU = 24 * np.sqrt(2) / 128              # TS's native px per unit along the screen


def f32(a):
    return np.asarray(a, np.float32)


class Slab:
    """an overhang: solid from bot to top wherever top >= 0 (world units)."""
    def __init__(self, top, bot, comp, name=''):
        self.top, self.bot, self.comp, self.name = top, bot, comp, name


class Scene:
    def __init__(self, H, C, slabs=(), extra=None):
        self.H, self.C, self.slabs = H, C, list(slabs)
        self.extra = dict(extra or {})             # per-ground-position fields for the materials

    def slab(self, name):
        for s in self.slabs:
            if s.name == name:
                return s
        return None


class View:
    def __init__(self, look, elev, ppu, size, origin, margin=(48, 48), zmax=None, ss=SS, light=None, shadow_light=None):
        F = np.array(look, float); F = F / np.linalg.norm(F)
        self.F = F
        self.R = np.array([-F[1], F[0]])                  # screen right
        self.T = -F                                       # towards the viewer
        self.E = np.deg2rad(elev)
        self.sE, self.cE = float(np.sin(self.E)), float(np.cos(self.E))
        self.ppu = float(ppu)
        self.W, self.Hc = size
        self.ox, self.oy = origin
        self.ss = ss
        self.mx, self.my = margin
        self.zmax = zmax                                  # world units; set by the scene if None
        self.L = self.cam_to_world(L_CAM if light is None else np.array(light, float))
        self.Ls = self.cam_to_world(LS_CAM if shadow_light is None else np.array(shadow_light, float))

    def cam_to_world(self, v):
        w = v[0] * np.array([self.R[0], self.R[1], 0]) + v[1] * np.array([self.T[0], self.T[1], 0]) \
            + v[2] * np.array([0, 0, 1.0])
        return w / np.linalg.norm(w)

    # screen <-> world
    def project(self, X, Y, Z):
        pr = X * self.R[0] + Y * self.R[1]
        pt = X * self.T[0] + Y * self.T[1]
        return self.ox + self.ppu * pr, self.oy + self.ppu * (self.sE * pt - self.cE * Z)

    def grid(self, zmax):
        """ground grid (screen-aligned): returns X, Y world coords and grid geometry."""
        ss = self.ss
        zpx = int(np.ceil(zmax * self.ppu * self.cE)) + 2
        self.zpx = zpx
        x0, x1 = -self.mx, self.W + self.mx
        y0, y1 = -self.my, self.Hc + zpx + self.my
        gx = x0 + (np.arange((x1 - x0) * ss) + 0.5) / ss
        gy = y0 + (np.arange((y1 - y0) * ss) + 0.5) / ss
        GX, GY = np.meshgrid(f32(gx), f32(gy))
        pr = (GX - self.ox) / self.ppu
        pt = (GY - self.oy) / (self.ppu * self.sE)
        X = pr * self.R[0] + pt * self.T[0]
        Y = pr * self.R[1] + pt * self.T[1]
        self.g0, self.c0 = self.my * ss, self.mx * ss
        self.GX, self.GY = GX, GY
        return f32(X), f32(Y)

    def zscale(self):
        """world units of height -> super-sampled px of screen height."""
        return self.ppu * self.cE * self.ss


# ----------------------------------------------------------------------------------------------- march
def march(view, Hss, slabs_ss):
    """Hss: ground heights in SS px of screen height on the view's grid; slabs_ss: list of (top, bot) in the
    same units (top < 0 where absent).  Returns hit level k, kind (0 none, 1 ground, 2+s slab s)."""
    ss = view.ss
    NR, NC = view.Hc * ss, view.W * ss
    g0, c0 = view.g0, view.c0
    tops = [t for t, b in slabs_ss]
    env = Hss.copy()
    for t in tops:
        env = np.maximum(env, t)
    rowmax = env[:, c0:c0 + NC].max(axis=1)
    K = int(np.ceil(rowmax.max())) + 1
    hit = np.full((NR, NC), -1, np.int32)
    kind = np.zeros((NR, NC), np.int8)
    for k in range(K, -1, -1):
        # canvas rows whose ground row (i + g0 + k) holds anything this tall
        ok = np.nonzero(rowmax[g0 + k: g0 + k + NR] >= k)[0] if k > 0 else np.arange(NR)
        if ok.size == 0:
            continue
        i0, i1 = ok.min(), ok.max() + 1
        rs = slice(g0 + k + i0, g0 + k + i1)
        free = hit[i0:i1] < 0
        h = Hss[rs, c0:c0 + NC]
        g = free & (h >= k) & (h > 0.5)
        hit[i0:i1][g] = k
        kind[i0:i1][g] = 1
        free &= ~g
        for s, (t, b) in enumerate(slabs_ss):
            tt = t[rs, c0:c0 + NC]
            m = free & (tt >= k) & (b[rs, c0:c0 + NC] <= k)
            if m.any():
                hit[i0:i1][m] = k
                kind[i0:i1][m] = 2 + s
                free &= ~m
    return hit, kind


# ----------------------------------------------------------------------------------------------- helpers
def smooth(a, sig):
    return ndimage.gaussian_filter(a, sig, mode='nearest')


def filled(t, valid):
    """values of t outside `valid` replaced by the nearest valid value (so smoothing/gradients don't dive at
    the edge of a slab)."""
    if valid.all() or not valid.any():
        return t
    idx = ndimage.distance_transform_edt(~valid, return_distances=False, return_indices=True)
    return t[tuple(idx)]


def skirt_comp(Hu, Hm, C, rad):
    """ct_ra.skirt_comp: smoothing spreads each face ~1 px past its footprint; give those skirt cells the
    component of the taller part they came from."""
    raised = Hm > Hu + 0.3
    if not raised.any():
        return C
    n0, n1 = Hu.shape
    Hp = np.pad(Hu, rad, mode='edge'); Cp = np.pad(C, rad, mode='edge')
    best = Hu.copy(); bc = C.copy()
    for oy in range(-rad, rad + 1):
        for ox in range(-rad, rad + 1):
            if oy * oy + ox * ox > rad * rad:
                continue
            h = Hp[rad + oy:rad + oy + n0, rad + ox:rad + ox + n1]
            m = h > best
            best = np.where(m, h, best)
            bc = np.where(m, Cp[rad + oy:rad + oy + n0, rad + ox:rad + ox + n1], bc)
    return np.where(raised, bc, C).astype(C.dtype)


def grad_world(view, F):
    """gradient of a screen-scaled height field (SS px of height on the view grid) -> world slopes
    (dz/dX, dz/dY)."""
    ss = view.ss
    gy, gx = np.gradient(F, 1.0 / ss)                   # per screen px (grid px = 1/ss screen px)
    # F / zscale = world z; one screen px along the grid = 1/ppu units along R, 1/(ppu sinE) along T
    dz_dpr = gx / view.zscale() * view.ppu
    dz_dpt = gy / view.zscale() * view.ppu * view.sE
    dX = dz_dpr * view.R[0] + dz_dpt * view.T[0]
    dY = dz_dpr * view.R[1] + dz_dpt * view.T[1]
    return f32(dX), f32(dY)


# ----------------------------------------------------------------------------------------------- shadows
class ShadowMap:
    """the scene seen from the light: for each light px, how close to the light the first surface is."""
    def __init__(self, model, view, bounds, ppu=1.25, **mk):
        Ls = view.Ls
        look = -Ls[:2]
        elev = np.rad2deg(np.arcsin(Ls[2]))
        (xa, xb), (ya, yb), zt = bounds
        lv = View(look, elev, ppu, (8, 8), (0.0, 0.0), margin=(0, 0), ss=1)
        corners = np.array([(x, y, z) for x in (xa, xb) for y in (ya, yb) for z in (0, zt)], float)
        sx, sy = lv.project(corners[:, 0], corners[:, 1], corners[:, 2])
        pad = 8
        lv.ox = -sx.min() + pad; lv.oy = -sy.min() + pad
        lv.W = int(np.ceil(sx.max() - sx.min())) + 2 * pad
        lv.Hc = int(np.ceil(sy.max() - sy.min())) + 2 * pad
        X, Y = lv.grid(zt)
        sc = model(X, Y, **mk)
        zs = lv.zscale()
        Hss = sc.H * zs
        sl = [(np.where(s.top >= 0, s.top * zs, -1.0), np.where(s.top >= 0, s.bot * zs, 1e9)) for s in sc.slabs]
        hit, kind = march(lv, f32(Hss), [(f32(t), f32(b)) for t, b in sl])
        k = np.maximum(hit, 0)
        rows = np.arange(lv.Hc)[:, None] + lv.g0 + k
        cols = np.arange(lv.W)[None, :] + lv.c0 + 0 * k
        wx, wy = X[rows, cols], Y[rows, cols]
        wz = k / zs
        depth = wx * Ls[0] + wy * Ls[1] + wz * Ls[2]
        # where nothing is hit the ray reaches the ground (z = 0) at the canvas row itself
        gx, gy = X[np.arange(lv.Hc)[:, None] + lv.g0, np.arange(lv.W)[None, :] + lv.c0], \
            Y[np.arange(lv.Hc)[:, None] + lv.g0, np.arange(lv.W)[None, :] + lv.c0]
        dg = gx * Ls[0] + gy * Ls[1]
        self.depth = np.where(hit >= 0, depth, dg).astype(np.float32)
        self.lv, self.Ls = lv, Ls

    def test(self, X, Y, Z, bias=1.2, pcf=1):
        lv = self.lv
        sx, sy = lv.project(X, Y, Z)
        d = X * self.Ls[0] + Y * self.Ls[1] + Z * self.Ls[2]
        acc = np.zeros(np.shape(X), np.float32); n = 0
        # points outside the light's map (ground far from the building) are lit: clipping them to its edge read
        # whatever the edge held (a faint veil, or a full shadow, over the far ground)
        inside = (sx >= 0) & (sx < lv.W) & (sy >= 0) & (sy < lv.Hc)
        for oy in range(-pcf, pcf + 1):
            for ox in range(-pcf, pcf + 1):
                i = np.clip(np.floor(sx + 0.5 * ox).astype(int), 0, lv.W - 1)
                j = np.clip(np.floor(sy + 0.5 * oy).astype(int), 0, lv.Hc - 1)
                acc += (self.depth[j, i] > d + bias)
                n += 1
        return np.where(inside, acc / n, 0.0).astype(np.float32)


# ----------------------------------------------------------------------------------------------- render
def downsample(rgba, ss):
    H, Wd = rgba.shape[0] // ss, rgba.shape[1] // ss
    pre = rgba.copy(); pre[..., :3] *= rgba[..., 3:4]
    pre = pre.reshape(H, ss, Wd, ss, 4).mean(axis=(1, 3))
    a = pre[..., 3:4]
    out = np.where(a > 1e-6, pre[..., :3] / np.maximum(a, 1e-6), 0)
    return Image.fromarray(np.dstack([np.clip(out, 0, 255), np.clip(a * 255, 0, 255)]).round().astype(np.uint8), 'RGBA')


def fade_edges(im, band=14.0):
    """shadows that run past the canvas edge fade out over the last few px instead of a hard cut (shadow
    pixels only)."""
    a = np.array(im).astype(np.float32)
    H, Wd = a.shape[:2]
    fx = np.minimum(np.arange(Wd) + 0.5, Wd - 0.5 - np.arange(Wd)) / band
    fy = np.minimum(np.arange(H) + 0.5, H - 0.5 - np.arange(H)) / band
    f = np.clip(np.minimum(fx[None, :], fy[:, None]), 0, 1)
    f = f * f * (3 - 2 * f)
    shadow = a[..., :3].max(axis=2) < 8
    a[..., 3] = np.where(shadow, a[..., 3] * f, a[..., 3])
    return Image.fromarray(a.round().astype(np.uint8), 'RGBA')


class Render:
    """ray-cast a model in a view; exposes the per-pixel geometry for materials, overlays and masks."""

    def __init__(self, model, view, bounds, zmax, shadow_ppu=1.25, smooth_px=0.5, shadow_mk=None, **mk):
        self.view = v = view
        self.model, self.mk = model, mk
        ss = v.ss
        X, Y = v.grid(zmax)
        self.X, self.Y = X, Y
        sc = model(X, Y, **mk)
        self.scene = sc
        zs = v.zscale()
        Hu = f32(sc.H * zs)
        Hm = f32(smooth(Hu, smooth_px * ss))
        C = skirt_comp(Hu, Hm, sc.C, int(round(1.5 * ss))) if smooth_px > 0 else sc.C
        self.Hss, self.C = Hm, C
        slabs = []
        for s in sc.slabs:
            valid = s.top >= 0
            t = np.where(valid, s.top * zs, -1.0).astype(np.float32)
            b = np.where(valid, s.bot * zs, 1e9).astype(np.float32)
            slabs.append((t, b))
        self.slabs_ss = slabs
        hit, kind = march(v, Hm, slabs)
        self.kind = kind
        self.hitmask = hit >= 0
        k = np.maximum(hit, 0)
        NR, NC = v.Hc * ss, v.W * ss
        rows = np.arange(NR)[:, None] + v.g0 + k
        cols = np.arange(NC)[None, :] + v.c0 + 0 * k
        self.rows, self.cols = rows, cols
        self.x, self.y = X[rows, cols], Y[rows, cols]
        self.z = (k / zs).astype(np.float32)
        # component ids
        comp = C[rows, cols].copy()
        for s_i, s in enumerate(sc.slabs):
            m = kind == 2 + s_i
            comp[m] = s.comp[rows[m], cols[m]]
        self.comp = comp
        self.surface = np.zeros(hit.shape, np.int8)       # 0 top/ground field, 1 slab top, 2 slab bottom, 3 slab side
        self._normals(sc, zs, k)
        # shadow_mk: extra keywords for the light's and the sky's passes (e.g. leave thin masts out of the shadows)
        self.shadow_mk = dict(shadow_mk or {})
        self.sm = ShadowMap(model, v, bounds, ppu=shadow_ppu, **dict(mk, **self.shadow_mk))
        self.bounds = bounds

    def _normals(self, sc, zs, k):
        v = self.view
        rows, cols, kind = self.rows, self.cols, self.kind
        dX, dY = grad_world(v, self.Hss)
        nx, ny = -dX[rows, cols], -dY[rows, cols]
        nz = np.ones_like(nx)
        surf = self.surface
        for s_i, (t, b) in enumerate(self.slabs_ss):
            m = kind == 2 + s_i
            if not m.any():
                continue
            valid = t >= 0
            tf = f32(smooth(filled(t, valid), 0.5 * v.ss))
            bf = f32(smooth(filled(b, valid), 0.5 * v.ss))
            r, c = rows[m], cols[m]
            kk = k[m]
            near_top = np.abs(tf[r, c] - kk) <= 2.0 * 1.0 + 1e-3
            near_bot = (np.abs(bf[r, c] - kk) <= 2.0) & ~near_top
            if sc.slabs[s_i].name.startswith('L:'):
                # a lathed or rounded part (opt-in): inside its outline a hit is on its top or bottom, never a wall
                # (its steep flanks otherwise flicker between top and wall normals in rings)
                inner = ndimage.binary_erosion(valid, iterations=max(1, v.ss))[r, c]
                mid = 0.5 * (tf[r, c] + bf[r, c])
                near_top = near_top | (inner & (kk >= mid))
                near_bot = (near_bot | (inner & (kk < mid))) & ~near_top
            side = ~near_top & ~near_bot
            tX, tY = grad_world(v, tf)
            bX, bY = grad_world(v, bf)
            mask = f32(smooth(valid.astype(np.float32), 0.8 * v.ss))
            mX, mY = grad_world(v, mask * 1.0)
            sx_, sy_ = -mX[r, c], -mY[r, c]
            sl = np.hypot(sx_, sy_) + 1e-9
            nxs = np.where(near_top, -tX[r, c], np.where(near_bot, bX[r, c], sx_ / sl * 50.0))
            nys = np.where(near_top, -tY[r, c], np.where(near_bot, bY[r, c], sy_ / sl * 50.0))
            nzs = np.where(near_top, 1.0, np.where(near_bot, -1.0, 0.0))
            nx[m], ny[m], nz[m] = nxs, nys, nzs
            surf[m] = np.where(near_top, 1, np.where(near_bot, 2, 3))
        nl = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-9
        self.nx, self.ny, self.nz = f32(nx / nl), f32(ny / nl), f32(nz / nl)

    def field(self, name, default=0.0):
        """a scene.extra field sampled at every hit pixel (ground position under it)."""
        f = self.scene.extra.get(name)
        if f is None:
            return np.full(self.x.shape, default, np.float32)
        return f[self.rows, self.cols]

    def sky_occlusion(self, n_az=8, elev=(38.0,), top=True, ppu=0.8):
        """fraction of the sky (the part in front of each surface) hidden by the scene: shadow maps from
        a ring of directions round the sky.  Darkens the inside of the hangar, crevices and wall feet."""
        v = self.view
        dirs = []
        for e in elev:
            for i in range(n_az):
                a = 2 * np.pi * (i + 0.5) / n_az
                dirs.append((np.cos(a) * np.cos(np.deg2rad(e)), np.sin(a) * np.cos(np.deg2rad(e)), np.sin(np.deg2rad(e))))
        if top:
            dirs.append((0.0, 0.2, 0.98))
        blocked = np.zeros(self.x.shape, np.float32)
        count = np.zeros(self.x.shape, np.float32)
        for d in dirs:
            d = np.array(d) / np.linalg.norm(d)
            fake = View(v.F, np.rad2deg(v.E), v.ppu, (v.W, v.Hc), (v.ox, v.oy))
            fake.Ls = d
            sm = ShadowMap(self.model, fake, self.bounds, ppu=ppu, **dict(self.mk, **getattr(self, 'shadow_mk', {})))
            facing = (self.nx * d[0] + self.ny * d[1] + self.nz * d[2]) > 0.05
            b = sm.test(self.x + self.nx * 1.5, self.y + self.ny * 1.5, self.z + self.nz * 1.5, bias=1.5, pcf=0)
            blocked += facing * b
            count += facing
        return np.where(count > 0, blocked / np.maximum(count, 1), 0.0).astype(np.float32)

    def covered(self):
        """how much of the sky above each hit point is blocked by an overhang directly over it (0..1)."""
        v = self.view
        cov = np.zeros(self.x.shape, np.float32)
        zs = v.zscale()
        for s_i, (t, b) in enumerate(self.slabs_ss):
            bb = b[self.rows, self.cols]
            tt = t[self.rows, self.cols]
            above = (tt >= 0) & (bb > self.z * zs + 2.0) & (self.kind != 2 + s_i)
            cov = np.maximum(cov, above.astype(np.float32))
        return cov

    def shade(self, albedo, sky_occ=None, ao=None, shadow_extra=None, normals=None):
        """walls2's lighting: ambient + sky + diffuse (x (1 - 0.8 shadow)), x ao."""
        v = self.view
        L = v.L
        nx, ny, nz = (self.nx, self.ny, self.nz) if normals is None else normals
        ndl = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, None)
        sh = self.sm.test(self.x, self.y, self.z + 0.0, bias=1.5, pcf=1)
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

    def ground_alpha(self, contact_px=7.0, fp_extra=None):
        """shadow on the ground (~75%, blurred 1.5 px) + the soft contact shadow round the foot."""
        v = self.view
        ss = v.ss
        NR, NC = v.Hc * ss, v.W * ss
        gr = np.arange(NR)[:, None] + v.g0 + np.zeros((1, NC), int)
        gc = np.arange(NC)[None, :] + v.c0 + np.zeros((NR, 1), int)
        gx, gy = self.X[gr, gc], self.Y[gr, gc]
        gsh = self.sm.test(gx, gy, np.zeros_like(gx), bias=0.8, pcf=1)
        shadow_a = ndimage.gaussian_filter(gsh.astype(np.float32), 1.5 * ss) * W.SHADOW_ALPHA
        fp = self.scene.H > 0.5
        for s in self.scene.slabs:
            fp |= (s.top >= 0) & (s.bot <= 1.0)
        if fp_extra is not None:
            fp |= fp_extra
        dist = ndimage.distance_transform_edt(~fp) / ss
        contact = np.clip(1 - dist[gr, gc] / contact_px, 0, 1) ** 1.5 * 0.5
        return np.maximum(shadow_a, contact)

    def compose(self, col, ground=True, outline=True, only=None):
        """col: lit colour per pixel.  only: bool mask of hit pixels to keep (overlays)."""
        hit = self.hitmask if only is None else (self.hitmask & only)
        rgba = np.zeros(hit.shape + (4,), np.float32)
        rgba[..., :3] = np.where(hit[..., None], col, 0.0)
        a = np.where(hit, 1.0, self.ground_alpha() if ground else 0.0)
        rgba[..., 3] = a
        if outline:
            ss = self.view.ss
            ring = ndimage.binary_dilation(hit, iterations=int(0.9 * ss)) & ~hit
            if only is not None:
                ring &= ~self.hitmask
            rgba[..., :3] = np.where(ring[..., None], BLACK_OUT, rgba[..., :3])
            rgba[..., 3] = np.where(ring, np.maximum(rgba[..., 3], 0.55), rgba[..., 3])
        return fade_edges(downsample(rgba, self.view.ss))
