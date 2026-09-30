"""
Gates for Red Alert Remastered in the style of the TS walls (HD, 128 px per cell),
plus the wall end pieces that join a gate (or later the tower) to a wall.

Gate bodies, with plain ends:
  horizontal 3x1 -> 384x128, vertical 1x3 -> 128x384
  gdi  TS GTGATE: ribbed panel in a trim frame that slides down into a slot
       0-9 closed -> open, 10-19 the same damaged, 20 destroyed
  nod  TS NTGATE: a thick wall section that lowers into the ground
       0-6 closed -> open, 7-13 the same damaged, 14 destroyed

End pieces (128x128, one cell), per wall type and side:
  a stub of that wall from the cell edge 28 px in, carrying the other half of its collar.
  W / E go on the end cells of a horizontal gate, N / S on the end cells of a vertical one.
  The S piece also draws the first bit of the wall continuing south, which that wall can't.
  Draw order: the N piece before the gate, the W / E / S pieces after it.

The gate is modelled in its own (u, v) frame: u along the gate, v across it (v = 0 is the
line the walls run along). Horizontal: u = x, v = y - 64. Vertical: u = y, v = x - 64.
The ray-cast is RA's view (screen_y = ground_y - FZ * z), lit and shadowed like the walls.
"""
import numpy as np
from PIL import Image
from scipy import ndimage
import walls2 as W
from walls2 import smoothstep, trap, phase, sample, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME

SS = 4
FZ = W.FZ
M = 40                      # ground margin (px) around the canvas
INF = 1e6
NONE, BASE, STUB, PANEL, DEBRIS = 0, 1, 2, 3, 4

COMMON = dict(U=384.0, L=28.0, base_half=47.0, strip_h=1.2)
FACTIONS = {
    'gdi': dict(open_frames=10, frames=21, sink_steps=8, base='gravel',
                curb_half=15.0, curb_h=2.2, slot_half=7.8, slot_depth=40.0,
                hp=46.0, frame_half=6.6, infill_half=4.0, rib_amp=1.3, ribs=24,
                bar=6.0, end_bar=10.0, bolt_every=11.0),
    'nod': dict(open_frames=7, frames=15, sink_steps=6, base='hazard',
                curb_half=14.8, curb_h=2.0, slot_half=11.3, slot_depth=64.0,
                hp=51.0, hp_mid=29.0, frame_half=10.0, stripe=11.0, shape='saddle'),
}

TRIM_GOLD = np.array([224, 178, 56.])      # placeholder house colour
# gdi
DIRT = np.array([170, 154, 118.])
GRAVEL = np.array([172, 170, 162.])
RIB_HI = np.array([222, 186, 146.])
RIB_LO = np.array([150, 145, 126.])
RAIL = np.array([170, 138, 96.])
# nod
SLAB = np.array([188, 188, 186.])
PANEL_DK = np.array([84, 84, 86.])
HZ_Y = np.array([200, 168, 92.])
HZ_D = np.array([58, 56, 46.])
LIP = np.array([160, 160, 156.])
EARTH = np.array([112, 90, 62.])
# shared
BARE = np.array([150, 148, 142.])
SOOT = np.array([34, 32, 30.])
BOLT = np.array([46, 42, 36.])

FILL = np.array([-0.25, 0.80, 0.55]); FILL /= np.linalg.norm(FILL)
FILL_I = 0.42                               # soft front light on the gate so its face reads


def frame_state(faction, frame):
    """-> (state, opening stage, stages to fully open)."""
    f = FACTIONS[faction]
    n = f['open_frames']
    if frame < n:
        return 'ok', frame, f['sink_steps']
    if frame < 2 * n:
        return 'damaged', frame - n, f['sink_steps']
    return 'destroyed', n - 1, f['sink_steps']


class Render:
    """Shared ray-cast and shading. Subclasses fill in the components."""

    def setup_grid(self, Wc, Hc):
        self.Wc, self.Hc = Wc, Hc
        xs = (np.arange(-M * SS, (Wc + M) * SS) + 0.5) / SS
        ys = (np.arange(-M * SS, (Hc + 3 * M) * SS) + 0.5) / SS
        self.X, self.Y = np.meshgrid(xs, ys)
        shape = self.X.shape
        # components (heights in units); masks say where each exists
        self.Hb = np.zeros(shape); self.base_mask = np.zeros(shape, bool); self.slot = np.zeros(shape, bool)
        self.Hs = np.zeros(shape); self.Cs = np.zeros(shape, np.int8); self.stub_mask = np.zeros(shape, bool)
        self.stub_along = np.zeros(shape)
        self.Hd = np.full(shape, -INF); self.rock_col = np.zeros(shape + (3,))
        self.frame_m = np.zeros(shape, bool)
        self.zoff = 0.0

    def mask_normals(self, m, sigma=0.6):
        f = ndimage.gaussian_filter(m.astype(float), sigma * SS)
        gy, gx = np.gradient(f)
        n = np.hypot(gx, gy) + 1e-9
        return -gx / n, -gy / n

    def finish_geometry(self):
        self.Hb_n = ndimage.gaussian_filter(np.maximum(self.Hb, -4.0), 0.6 * SS, mode='nearest')
        self.Hb = ndimage.gaussian_filter(self.Hb, 0.3 * SS, mode='nearest')
        self.Hs = ndimage.gaussian_filter(self.Hs, 0.8 * SS, mode='nearest')
        self.stub_mask = self.Hs > 0.3
        self.deb_mask = self.Hd > -INF / 2
        env = np.where(self.base_mask, np.maximum(self.Hb, 0), 0.0)
        env = np.maximum(env, np.where(self.stub_mask, self.Hs, 0))
        if self.frame_m.any():
            env = np.maximum(env, np.where(self.frame_m, self.zoff + self.ptop, 0))
        env = np.maximum(env, np.where(self.deb_mask, self.Hd, 0))
        self.env = env
        self.env_blur = ndimage.gaussian_filter(env, 5.0 * SS, mode='nearest')

    # ------------------------------------------------------------------ ray-cast
    def raycast(self):
        Wc, Hc = self.Wc, self.Hc
        WS, HS = Wc * SS, Hc * SS
        n0 = M * SS
        zmax = int(np.ceil(max(self.env.max(), 1.0) * SS)) + 8
        zmin = -int(self.slot_depth * SS) if self.slot.any() else 0
        Hb_s, Hs_s, Hd_s = self.Hb * SS, self.Hs * SS, self.Hd * SS
        has_panel = self.frame_m.any()
        if has_panel:
            hi1, lo2, hi2 = self.hi1 * SS, self.lo2 * SS, self.hi2 * SS
            zoff = self.zoff * SS
        hit_z = np.full((HS, WS), -INF)
        comp = np.zeros((HS, WS), np.int8)
        ptop_hit = np.zeros((HS, WS), bool)
        cols = slice(n0, n0 + WS)
        for zs in range(zmax, zmin - 1, -1):
            j0 = n0 + int(round(FZ * zs))
            sl = (slice(j0, j0 + HS), cols)
            free = hit_z <= -INF / 2
            if not free.any():
                break
            tests = []
            if has_panel:
                pz = zs - zoff
                pan = self.frame_m[sl] & (((pz >= 0) & (pz <= hi1[sl])) | ((pz >= lo2[sl]) & (pz <= hi2[sl])))
                tests.append((pan, PANEL))
            tests += [(self.stub_mask[sl] & (Hs_s[sl] >= zs), STUB),
                      (self.deb_mask[sl] & (Hd_s[sl] >= zs), DEBRIS),
                      (self.base_mask[sl] & (Hb_s[sl] >= zs), BASE)]
            for m, cid in tests:
                new = free & m
                if new.any():
                    hit_z[new] = zs
                    comp[new] = cid
                    if cid == PANEL:
                        top1 = pz > hi1[sl] - 1.5
                        top2 = (pz >= lo2[sl]) & (pz > hi2[sl] - 1.5)
                        ptop_hit[new] = (top1 | top2)[new]
                    free = free & ~new
            if zs <= 0:
                ended = free & ~self.slot[sl]     # met the terrain: nothing more to see
                hit_z[ended] = -INF / 4
        hit = hit_z > -INF / 8
        zh = np.where(hit, hit_z, 0) / SS
        rows = np.arange(HS)[:, None]
        gj = np.clip((rows + n0 + np.round(FZ * zh * SS)).astype(int), 0, self.X.shape[0] - 1)
        gi = np.broadcast_to(np.arange(n0, n0 + WS)[None, :], (HS, WS))
        return hit, zh, comp, ptop_hit, gj, gi, rows

    def hf_normals(self, Hf, gj, gi):
        gy, gx = np.gradient(Hf, 1.0 / SS)
        nx, ny = -gx[gj, gi], -gy[gj, gi]
        nl = np.sqrt(nx * nx + ny * ny + 1)
        return nx / nl, ny / nl, 1 / nl

    def shadows(self, hit, zh, gj, gi):
        kx, ky = W.SHADOW_DIR
        E = self.env * SS
        zst = zh * SS
        shadowed = np.zeros(hit.shape, bool)
        steps = int((self.env.max() - min(zh.min(), 0)) * SS) + 4
        for t in range(3, steps, 2):
            si = np.clip(np.round(gi - kx * t).astype(int), 0, E.shape[1] - 1)
            sj = np.clip(np.round(gj - ky * t).astype(int), 0, E.shape[0] - 1)
            shadowed |= hit & (E[sj, si] > zst + t + 1.5)
        return ndimage.gaussian_filter(shadowed.astype(float), 0.6 * SS)

    def ground_alpha(self, rows, gi, clip_mask=None):
        kx, ky = W.SHADOW_DIR
        E = self.env * SS
        n0 = M * SS
        gr = rows + n0 + 0 * gi
        gshadow = np.zeros(gi.shape, bool)
        for t in range(1, int(self.env.max() * SS) + 2, 2):
            si = np.clip(np.round(gi - kx * t).astype(int), 0, E.shape[1] - 1)
            sj = np.clip(np.round(gr - ky * t).astype(int), 0, E.shape[0] - 1)
            gshadow |= E[sj, si] >= t
        gsh = ndimage.gaussian_filter(gshadow.astype(float), 1.5 * SS) * W.SHADOW_ALPHA
        solid = self.base_mask | self.stub_mask | self.deb_mask
        dist = ndimage.distance_transform_edt(~solid) / SS
        contact = np.clip(1 - dist[gr, gi] / 5.0, 0, 1) ** 1.5 * 0.35
        ga = np.maximum(gsh, contact)
        if clip_mask is not None:
            ga = ga * clip_mask[gr, gi]
        return ga

    def stub_albedo(self, gj, gi, zh, grain, tu, tv):
        along = self.stub_along[gj, gi]
        cs = self.Cs[gj, gi]
        conc = W.CONCRETE * (1 + grain)[..., None] * 0.96
        rib_c = 1 - smoothstep(0.0, 0.9, phase(along, W.P['rib_every']))
        och = W.OCHRE * (1 + 0.8 * grain)[..., None] * (1 - 0.18 * rib_c)[..., None]
        s_alb = np.where((cs == 2)[..., None], och, conc)
        grime = np.clip(1 - zh / 15.0, 0, 1) ** 1.5 * np.clip(0.55 + 0.35 * sample(NOISE_GRIME, tu, tv), 0, 1)
        return s_alb * (1 - grime[..., None]) + W.GRIME * grime[..., None]

    def compose(self, hit, col, ground_a, trim_m, ring_alpha=0.45, glow=None):
        """glow (optional): alpha of emitted light over pixels the ray missed; its colour is taken from col."""
        HS, WS = hit.shape
        rgba = np.zeros((HS, WS, 4))
        rgba[..., :3] = np.where(hit[..., None], np.clip(col, 0, 255), 0.0)
        rgba[..., 3] = np.where(hit, 1.0, ground_a)
        ring = ndimage.binary_dilation(hit, iterations=int(0.9 * SS)) & ~hit
        rgba[..., :3] = np.where(ring[..., None], 28.0, rgba[..., :3])
        rgba[..., 3] = np.where(ring, np.maximum(rgba[..., 3], ring_alpha), rgba[..., 3])
        if glow is not None:                       # light drawn over the (transparent) ground: 'over' blend
            g = np.clip(glow, 0, 1) * ~hit
            a0 = rgba[..., 3]
            a = g + a0 * (1 - g)
            c = np.clip(col, 0, 255) * g[..., None] + rgba[..., :3] * (a0 * (1 - g))[..., None]
            rgba[..., :3] = np.where(a[..., None] > 1e-6, c / np.maximum(a, 1e-6)[..., None], rgba[..., :3])
            rgba[..., 3] = a
        pre = rgba.copy(); pre[..., :3] *= rgba[..., 3:4]
        pre = pre.reshape(self.Hc, SS, self.Wc, SS, 4).mean(axis=(1, 3))
        al = pre[..., 3:4]
        out = np.where(al > 1e-6, pre[..., :3] / np.maximum(al, 1e-6), 0)
        img = np.dstack([np.clip(out, 0, 255), np.clip(al * 255, 0, 255)]).round().astype(np.uint8)
        tm = (trim_m * hit).reshape(self.Hc, SS, self.Wc, SS).mean(axis=(1, 3))
        return Image.fromarray(img, 'RGBA'), Image.fromarray((tm * 255).round().astype(np.uint8), 'L')

    # noise helpers (deterministic per seed)
    def noise1d(self, u, sigma, seed):
        r = np.random.default_rng(seed)
        n = ndimage.gaussian_filter1d(r.standard_normal(2048), sigma * 2)
        n /= n.std()
        return n[np.clip(((u + 200) * 2).astype(int), 0, 2047)]

    def noise2d(self, u, v, sigma, seed):
        r = np.random.default_rng(seed)
        n = ndimage.gaussian_filter(r.standard_normal((260, 1100)), sigma, mode='wrap')
        n /= n.std()
        return n[np.clip((v + 130).astype(int), 0, 259), np.clip((u + 200).astype(int), 0, 1099)]

    def weather_stub(self, out, comp, top_like, grain, tu, tv, extra_mask=None, heavy=False):
        import damage as D
        rng = np.random.default_rng(99)
        S_rust, S_crack, S_cmask, S_rough = D.Sampler(rng, 4.0), D.Sampler(rng, 8.0), D.Sampler(rng, 12.0), D.Sampler(rng, 1.2)
        bu, bv = tu % 256, tv % 256
        concrete = comp == STUB
        if extra_mask is not None:
            concrete = concrete | extra_mask
        nr = S_rust(bu, np.where(top_like, bv, bv * 0.3))
        rust = smoothstep(0.95 if not heavy else 0.6, 1.45, nr) * concrete * 0.7
        out = out * (1 - rust[..., None]) + D.RUST * (1 + grain)[..., None] * rust[..., None]
        cn = S_crack(bu, bv) + 0.10 * S_rough(bu, bv)
        crack = (1 - smoothstep(0.015, 0.06, np.abs(cn))) * smoothstep(0.55 if not heavy else 0.2, 0.85, S_cmask(bu, bv)) * concrete
        return out * (1 - 0.7 * crack)[..., None]


# =============================================================================== gate bodies
class Gate(Render):
    def __init__(self, faction, orient, frame, trim=TRIM_GOLD, seed=7):
        self.fac, self.o, self.frame = faction, orient, frame
        self.g = dict(COMMON, **FACTIONS[faction])
        self.trim = np.asarray(trim, float)
        self.state, stage, steps = frame_state(faction, frame)
        self.ztop = self.g['hp'] * (1 - stage / steps)
        self.zoff = self.ztop - self.g['hp']
        self.rng = np.random.default_rng(seed)
        self.setup_grid(*((384, 128) if orient == 'h' else (128, 384)))
        self.zoff = self.ztop - self.g['hp']
        if orient == 'h':
            self.Uc, self.Vc = self.X, self.Y - 64.0
        else:
            self.Uc, self.Vc = self.Y, self.X - 64.0
        self.slot_depth = self.g['slot_depth']
        self.build()
        self.finish_geometry()

    def build(self):
        g, U, V = self.g, self.Uc, self.Vc
        a = np.abs(V)
        Ul, L = g['U'], g['L']
        in_u = (U >= 0) & (U <= Ul)
        strip = trap(a, g['base_half'] - 2.5, g['base_half'], g['strip_h'])
        Hb = np.where(a <= g['curb_half'], g['curb_h'], strip)
        slot = (a <= g['slot_half']) & (U >= L) & (U <= Ul - L)
        self.base_mask = in_u & (a <= g['base_half'])

        plen = Ul - 2 * L
        pu = U - L
        in_len = (pu >= 0) & (pu <= plen)
        self.pu, self.plen = pu, plen
        notch = np.zeros_like(U)
        hole_lo = np.full(U.shape, INF); hole_hi = np.full(U.shape, -INF)
        self.soot_u = np.zeros_like(U)
        panel_on = self.state != 'destroyed'

        if self.state == 'damaged':
            jag = self.noise1d(pu, 3.0, 11)
            if self.fac == 'gdi':
                cuts = ((0.21, 15, 17), (0.52, 21, 25), (0.80, 12, 15))
            else:
                cuts = ((0.12, 12, 16), (0.33, 20, 22), (0.55, 9, 12), (0.74, 17, 20), (0.92, 11, 13))
            for c, d, w in cuts:
                t = np.clip(1 - ((pu - c * plen) / w) ** 2, 0, 1)
                notch = np.maximum(notch, (d + 3.0 * jag) * t ** 0.55)
            notch = np.where(notch > 0.8, notch, 0)
            if self.fac == 'gdi':
                jag2 = self.noise1d(pu, 2.0, 12)
                for c, cz, ru, rz in ((0.36, 24, 10, 7.5), (0.67, 20, 12, 7)):
                    t = 1 - ((pu - c * plen) / ru) ** 2
                    hh = np.where(t > 0, rz * np.sqrt(np.clip(t, 0, 1)) + 1.5 * jag2, -INF)
                    hole_lo = np.where(hh > 0.5, np.minimum(hole_lo, cz - hh), hole_lo)
                    hole_hi = np.where(hh > 0.5, np.maximum(hole_hi, cz + hh), hole_hi)
                spots = (0.21, 0.36, 0.52, 0.67, 0.80)
            else:
                spots = (0.12, 0.33, 0.55, 0.74, 0.92, 0.45)
            s = np.zeros_like(U)
            for c in spots:
                s = np.maximum(s, np.exp(-((pu - c * plen) / 26.0) ** 2))
            self.soot_u = s

        # ---- panel / slab columns (panel-local height pz, 0 = its bottom)
        prof = np.full(U.shape, g['hp'])
        if self.fac == 'nod' and g.get('shape') == 'saddle':
            # saddle top: tall at both ends, dipping to about 0.57 of that in the middle
            dn = np.clip(np.abs(pu - plen / 2) / (plen / 2), 0, 1)
            prof = g['hp_mid'] + (g['hp'] - g['hp_mid']) * np.clip(dn / 0.96, 0, 1) ** 2.2
        elif self.fac == 'nod':
            # level top, with a sloping facet cut into the upper corners of each end (both faces),
            # starting a third of the way up at the very end and running out along the top edge
            low, rise, w = g['hp'] * 0.34, plen * 0.36, g['frame_half']
            e = np.minimum(pu, plen - pu)
            facet = low + (g['hp'] - low) * (e / rise + (g['frame_half'] - a) / w)
            prof = np.minimum(prof, np.maximum(facet, low))
        ptop = np.maximum(prof - notch, 9.0)
        self.top_grad = np.gradient(ndimage.gaussian_filter(ptop, 0.5 * SS), 1.0 / SS)
        notched = notch > 0.5
        if self.fac == 'gdi':
            eb, fh, ih, bar = g['end_bar'], g['frame_half'], g['infill_half'], g['bar']
            endbar = in_len & ((pu <= eb) | (pu >= plen - eb))
            period = (plen - 2 * eb) / g['ribs']
            rib = g['rib_amp'] * np.cos(2 * np.pi * (pu - eb) / period)
            frame_m = in_len & (a <= fh)
            inf_m = in_len & ~endbar & (a <= ih + rib)
            has_hole = hole_lo < INF / 2
            hi1 = np.where(endbar | inf_m, np.where(inf_m & has_hole, hole_lo, ptop), bar)
            lo2 = np.where(endbar, INF, np.where(inf_m, np.where(has_hole, hole_hi, INF),
                                                 np.where(notched, INF, ptop - bar)))
            self.endbar, self.period = endbar, period
            self.inf_m = inf_m & panel_on
            self.n_inf = self.mask_normals(self.inf_m)
        else:
            frame_m = in_len & (a <= g['frame_half'])
            hi1 = ptop.copy()
            lo2 = np.full(U.shape, INF)
        self.frame_m = frame_m & panel_on
        self.ptop, self.notched, self.hi1, self.lo2, self.hi2 = ptop, notched, hi1, lo2, ptop
        self.n_frame = self.mask_normals(self.frame_m)
        self.fm_blur = ndimage.gaussian_filter(self.frame_m.astype(float), 0.7 * SS)

        Hd = np.full(U.shape, -INF)
        if self.state == 'destroyed':
            n = self.noise2d(U, V, 3.0, 21)
            breaks = np.zeros_like(U)
            for c in (0.18, 0.45, 0.62, 0.86):
                breaks = np.maximum(breaks, np.exp(-((U - c * Ul) / 16.0) ** 2))
            curb_hit = (a <= g['curb_half']) & (a > g['slot_half']) & (breaks * (1 + 0.4 * n) > 0.55)
            Hb = np.where(curb_hit, np.minimum(Hb, 0.4 + 1.5 * np.clip(n, 0, 1)), Hb)
            slot = slot | (curb_hit & (a < g['slot_half'] + 4 + 2 * n) & (U > L) & (U < Ul - L))
            self.soot_u = np.exp(-(V / 14.0) ** 2) * (0.6 + 0.4 * np.clip(n, 0, 1))
            Hd = self.scatter_rocks(Hd, in_slot=True)
        elif self.state == 'damaged':
            Hd = self.scatter_rocks(Hd, in_slot=False, count=6)

        if self.fac == 'nod' and self.state == 'destroyed':
            # the slot is filled in with earth and broken slab
            self.earth = slot.copy()
            Hb = np.where(slot, -2.5 + 0.8 * self.noise2d(U, V, 2.0, 41), Hb)
            self.slot = np.zeros_like(slot)
        else:
            self.earth = np.zeros_like(slot)
            Hb = np.where(slot, -g['slot_depth'], Hb)
            self.slot = slot
        if self.fac == 'nod' and self.state == 'destroyed':
            # earth sits below ground level: let rays into it
            self.slot = self.earth & True
        self.Hb, self.Hd = Hb, Hd

    def scatter_rocks(self, Hd, in_slot, count=None):
        g, U, V, rng = self.g, self.Uc, self.Vc, self.rng
        rj = self.noise2d(U, V, 1.5, 31)
        rocks = []
        L = g['L']
        if in_slot:
            n_in = 46 if self.fac == 'gdi' else 40
            lo, hi = (-9, 2.5) if self.fac == 'gdi' else (-3, 3.5)
            for _ in range(n_in):
                rocks.append((rng.uniform(L + 4, g['U'] - L - 4), rng.normal(0, g['slot_half'] * 0.45),
                              rng.uniform(3.5, 7.5), rng.uniform(lo, hi)))
            for _ in range(16):
                side = rng.choice([-1, 1])
                rocks.append((rng.uniform(20, g['U'] - 20), side * rng.uniform(16, 42), rng.uniform(2.4, 4.8), None))
        else:
            for _ in range(count):
                side = rng.choice([-1, 1], p=[0.35, 0.65])
                rocks.append((rng.uniform(40, g['U'] - 40), side * rng.uniform(g['slot_half'] + 3, 30),
                              rng.uniform(2.2, 4.2), None))
        if self.fac == 'gdi':
            palette = [W.CONCRETE * 0.9, W.CONCRETE * 0.72, DIRT, np.array([196, 164, 128.])]
        else:
            palette = [SLAB * 0.95, SLAB * 0.75, PANEL_DK, HZ_Y * 0.9]
        for cu, cv, r, ztop in rocks:
            sx, sy = rng.uniform(0.8, 1.3), rng.uniform(0.8, 1.3)
            d = np.hypot((U - cu) / sx, (V - cv) / sy)
            rr = r * (1 + 0.15 * rj)
            z0 = ztop if ztop is not None else g['strip_h']
            h = np.where(d < rr, z0 + 0.95 * r * np.sqrt(np.clip(1 - (d / rr) ** 2, 0, 1)), -INF)
            win = h > Hd
            colr = palette[rng.choice(4, p=[0.42, 0.28, 0.15, 0.15])]
            if rng.random() < 0.12:
                colr = self.trim * 0.85
            Hd = np.where(win, h, Hd)
            self.rock_col[win] = colr
        return Hd

    # ------------------------------------------------------------------ render
    def render(self):
        g = self.g
        hit, zh, comp, ptop_hit, gj, gi, rows = self.raycast()
        HS, WS = hit.shape
        x, y = self.X[gj, gi], self.Y[gj, gi]
        u, v = self.Uc[gj, gi], self.Vc[gj, gi]
        a = np.abs(v)
        isp = comp == PANEL

        nb, nd = self.hf_normals(self.Hb_n, gj, gi), self.hf_normals(np.maximum(self.Hd, 0), gj, gi)
        nx = np.select([comp == BASE, comp == DEBRIS], [nb[0], nd[0]], 0.0)
        ny = np.select([comp == BASE, comp == DEBRIS], [nb[1], nd[1]], 0.0)
        nz = np.select([comp == BASE, comp == DEBRIS], [nb[2], nd[2]], 1.0)

        pz = zh - self.zoff
        ptop = self.ptop[gj, gi]
        pu = self.pu[gj, gi]
        notched = self.notched[gj, gi]
        # on sloping tops the ray can land on a riser of the sub-pixel staircase: still the top
        tgy_, tgx_ = self.top_grad
        slope = np.hypot(tgx_[gj, gi], tgy_[gj, gi])
        ptop_hit = ptop_hit | (isp & (ptop - pz < 0.45 + 0.4 * slope) & (slope > 0.15))
        at_top = ptop_hit & (pz > ptop - 0.8 - 0.4 * slope)
        fmb = self.fm_blur[gj, gi]
        topn = np.clip((fmb - 0.55) / 0.4, 0, 1)

        if self.fac == 'gdi':
            bar = g['bar']
            on_inf = self.inf_m[gj, gi]
            endb = self.endbar[gj, gi]
            between = on_inf & (pz > bar) & (pz < ptop - bar)
            use_inf = between | (notched & on_inf)
            sx_ = np.where(use_inf, self.n_inf[0][gj, gi], self.n_frame[0][gj, gi])
            sy_ = np.where(use_inf, self.n_inf[1][gj, gi], self.n_frame[1][gj, gi])
            is_bar_face = ~between & ~ptop_hit & ~endb
            in_top_bar = pz >= ptop - bar
            edge_up = np.where(in_top_bar, np.clip(1 - (ptop - pz) / 1.4, 0, 1), np.clip(1 - np.abs(bar - pz) / 1.4, 0, 1))
            edge_dn = np.where(in_top_bar, np.clip(1 - np.abs(pz - (ptop - bar)) / 1.2, 0, 1), np.clip(1 - pz / 1.2, 0, 1))
            tz = np.where(is_bar_face, 0.9 * edge_up - 0.7 * edge_dn, 0.0)
            tz = np.where(endb & ~ptop_hit, 0.9 * np.clip(1 - (ptop - pz) / 1.4, 0, 1), tz)
        else:
            sx_, sy_ = self.n_frame[0][gj, gi], self.n_frame[1][gj, gi]
            # bevel along the top edge of the slab faces
            tz = np.where(~ptop_hit, 0.8 * np.clip(1 - (ptop - pz) / 1.6, 0, 1), 0.0)
        pnx, pny, pnz = sx_ * (1 - np.abs(tz)), sy_ * (1 - np.abs(tz)), tz
        tgy, tgx = self.top_grad
        tnx, tny = -tgx[gj, gi], -tgy[gj, gi]
        tl = np.sqrt(tnx ** 2 + tny ** 2 + 1)
        tnx, tny, tnz = tnx / tl, tny / tl, 1 / tl
        pnx = np.where(ptop_hit, tnx * topn + sx_ * (1 - topn) * 0.7, pnx)
        pny = np.where(ptop_hit, tny * topn + sy_ * (1 - topn) * 0.7, pny)
        pnz = np.where(ptop_hit, tnz * topn + 0.7 * (1 - topn), pnz)
        l = np.sqrt(pnx ** 2 + pny ** 2 + pnz ** 2) + 1e-9
        nx = np.where(isp, pnx / l, nx); ny = np.where(isp, pny / l, ny); nz = np.where(isp, pnz / l, nz)

        sh = self.shadows(hit, zh, gj, gi)
        ndl = np.clip(nx * W.LIGHT[0] + ny * W.LIGHT[1] + nz * W.LIGHT[2], 0, None)
        shade = W.AMBIENT + W.SKY * (0.5 + 0.5 * nz) + W.DIFFUSE * ndl * (1 - 0.85 * sh)
        ndf = np.clip(nx * FILL[0] + ny * FILL[1] + nz * FILL[2], 0, None)
        shade = np.where(isp, shade + FILL_I * ndf, shade)

        top_like = nz > 0.75
        ew_face = np.abs(ny) >= np.abs(nx)
        tu = np.where(top_like | ew_face, x, y)
        tv = np.where(top_like, y, zh)
        grain = sample(NOISE_FINE, tu, tv) * 0.035 + sample(NOISE_MOTTLE, tu, tv) * 0.05
        albedo = np.zeros((HS, WS, 3))
        trim_m = np.zeros((HS, WS))

        # ---- base
        fine = sample(NOISE_FINE, x * 1.6, y * 1.6)
        mot = sample(NOISE_MOTTLE, x * 1.3, y * 1.3)
        if g['base'] == 'gravel':
            grav = np.clip(0.55 + 0.30 * mot + 0.45 * fine, 0, 1)
            ground = DIRT * (1 + 0.06 * fine)[..., None] * (1 - grav[..., None]) + GRAVEL * (1 + 0.05 * fine)[..., None] * grav[..., None]
            curb = W.CONCRETE * 0.93 * (1 + grain)[..., None]
            b_alb = np.where((a <= g['curb_half'] + 0.5)[..., None], curb, ground)
            joint = (1 - smoothstep(0.3, 1.1, np.abs(a - g['curb_half'] - 0.5))) * 0.45
            b_alb = b_alb * (1 - joint)[..., None]
        else:
            w = (u + v) / g['stripe']
            stripe = np.abs(np.mod(w, 2.0) - 1.0)             # 0..1 triangle wave
            yel = smoothstep(0.46, 0.54, stripe)
            ground = HZ_D * (1 - yel[..., None]) + HZ_Y * yel[..., None]
            wear = np.clip(0.5 + 0.5 * mot, 0, 1) * 0.25
            ground = ground * (1 + 0.08 * fine)[..., None] * (1 - wear[..., None]) + np.array([120, 112, 92.]) * wear[..., None]
            lip = (a <= g['curb_half'] + 0.5)
            b_alb = np.where(lip[..., None], LIP * (1 + grain)[..., None], ground)
            joint = (1 - smoothstep(0.3, 1.1, np.abs(a - g['curb_half'] - 0.5))) * 0.5
            b_alb = b_alb * (1 - joint)[..., None]
        slotw = W.CONCRETE * 0.62 * (1 + grain)[..., None]
        deep = (zh < g['curb_h'] - 1.5) & (a <= g['slot_half'] + 4)
        b_alb = np.where(deep[..., None], slotw, b_alb)
        if self.earth.any():
            e = self.earth[gj, gi]
            b_alb = np.where(e[..., None], EARTH * (1 + 1.5 * grain)[..., None], b_alb)
        albedo = np.where((comp == BASE)[..., None], b_alb, albedo)

        # ---- panel / slab
        if self.fac == 'gdi':
            plen, eb = self.plen, g['end_bar']
            rim = ptop_hit & ~at_top & on_inf
            ribph = np.cos(2 * np.pi * (pu - eb) / self.period)
            ribc = (RIB_LO + (RIB_HI - RIB_LO) * (0.5 + 0.5 * ribph)[..., None]) * (1 + 1.2 * grain)[..., None]
            is_trim = endb | (~between & ~ptop_hit & ~(on_inf & notched))
            top_trim = at_top & ~notched & (a > 2.4)
            top_rail = at_top & ~notched & (a <= 2.4)
            is_trim = (is_trim & ~ptop_hit) | top_trim | (at_top & endb) | (ptop_hit & ~at_top & ~on_inf)
            p_alb = np.where(is_trim[..., None], self.trim * (1 + 0.6 * grain)[..., None], ribc)
            p_alb = np.where((top_rail & ~endb)[..., None], RAIL * (1 + grain)[..., None], p_alb)
            p_alb = np.where(rim[..., None], BARE * 0.7 * (1 + 2 * grain)[..., None], p_alb)
            rec = between & ((pz < bar + 1.6) | (pz > ptop - bar - 1.6))
            p_alb = np.where(rec[..., None], p_alb * 0.72, p_alb)
            bu = phase(pu - eb, g['bolt_every'], g['bolt_every'] / 2)
            bolts = ((~endb) & ~between & ~ptop_hit & (bu < 1.25) & ~notched &
                     ((np.abs(pz - bar / 2) < 1.4) | (np.abs(pz - (ptop - bar / 2)) < 1.4)))
            bolts |= endb & ~ptop_hit & (np.abs(np.minimum(pu, plen - pu) - eb / 2) < 1.25) & (phase(pz, 9.0, 4.5) < 1.4)
            bolts |= top_trim & (np.abs(a - 4.6) < 0.9) & (phase(pu, g['bolt_every']) < 1.1)
            p_alb = np.where(bolts[..., None], BOLT, p_alb)
            ptrim = is_trim & ~bolts
        else:
            p_alb, ptrim = self.nod_slab(pu, pz, ptop, a, at_top, ptop_hit, notched, sx_, sy_, grain)
        albedo = np.where(isp[..., None], p_alb, albedo)
        trim_m = np.where(isp & ptrim, 1.0, 0.0)

        albedo = np.where((comp == DEBRIS)[..., None], self.rock_col[gj, gi] * (1 + 1.5 * grain)[..., None], albedo)

        if self.state in ('damaged', 'destroyed'):
            albedo, trim_m = self.weather(albedo, trim_m, comp, x, y, v, zh, tu, tv, grain, top_like, gj, gi)

        eb_ = self.env_blur[gj, gi]
        ao = np.clip(1 - 0.02 * (eb_ - zh), 0.4, 1.0)
        ao = np.where(isp, np.clip(ao, 0.75, 1.0), ao)
        col = albedo * (shade * ao)[..., None]
        ga = self.ground_alpha(rows, gi)
        return self.compose(hit, col, ga, trim_m)

    def nod_slab(self, pu, pz, ptop, a, at_top, ptop_hit, notched, sx_, sy_, grain):
        """Light concrete slab; dark panel with a raised middle, trim round it; trim on the top edges."""
        g, plen, hp = self.g, self.plen, self.g['hp']
        # which face was hit: long faces look across the gate, end faces along it
        if self.o == 'h':
            along_n = np.abs(sx_)
        else:
            along_n = np.abs(sy_)
        end_face = ~ptop_hit & (along_n > 0.7)
        s = np.where(end_face, np.where(pu < plen / 2, 0.0, plen), pu)       # position along the face
        low, rise = hp * 0.34, plen * 0.36
        dist_end = np.minimum(s, plen - s)
        edge = low + (hp - low) * np.clip(dist_end / rise, 0, 1)
        edge = np.minimum(edge, ptop)
        if g.get('shape') == 'chamfer':
            edge = ptop                      # the face ends where the facet begins
        tw = 4.6                                                             # trim width
        in_panel = pz < edge
        trim = (pz < tw) | (np.abs(pz - edge) < tw * 0.55) | (in_panel & (dist_end < 3.0) & ~end_face)
        seam = (phase(s - 10.0, 20.0) < 0.9) & in_panel & ~trim
        face = np.where(in_panel[..., None], PANEL_DK * (1 + 1.4 * grain)[..., None], SLAB * (1 + grain)[..., None])
        face = np.where(seam[..., None], face * 0.62, face)
        face_trim = trim & ~ptop_hit & ~(notched & (pz > ptop - 2.5))
        face = np.where(face_trim[..., None], self.trim * (1 + 0.6 * grain)[..., None], face)
        # top: concrete with a trim line along both edges
        top = SLAB * 0.97 * (1 + grain)[..., None]
        top_trim = at_top & ~notched & (a > g["frame_half"] - 3.0)
        if g.get('shape') == 'chamfer':
            top_trim = at_top & ~notched & (np.abs(ptop - hp) < 0.6) & (a > g["frame_half"] - 3.0)
        top = np.where(top_trim[..., None], self.trim * (1 + 0.6 * grain)[..., None], top)
        broken = ptop_hit & notched
        top = np.where(broken[..., None], SLAB * 0.8 * (1 + 2 * grain)[..., None], top)
        alb = np.where(ptop_hit[..., None], top, face)
        return alb, np.where(ptop_hit, top_trim, face_trim)

    def weather(self, albedo, trim_m, comp, x, y, v, zh, tu, tv, grain, top_like, gj, gi):
        import damage as D
        rng = np.random.default_rng(99)
        S_wear, S_soot = D.Sampler(rng, 3.0), D.Sampler(rng, 5.0)
        bu, bv = tu % 256, tv % 256
        isp = comp == PANEL
        near_slot = (comp == BASE) & (np.abs(v) < self.g['curb_half'] + 2)
        out = self.weather_stub(albedo, comp, top_like, grain, tu, tv, extra_mask=near_slot)
        # panel: chipped paint and cracks, soot around the breaks
        chip = smoothstep(0.55, 0.95, S_wear(bu * 1.3, bv * 1.3)) * (trim_m > 0)
        out = out * (1 - chip[..., None]) + BARE * (1 + grain)[..., None] * chip[..., None]
        trim_m = trim_m * (1 - chip)
        if self.fac == 'nod':
            out = self.weather_stub(out, np.where(isp, STUB, NONE), top_like, grain, tu, tv)
        s_u = self.soot_u[gj, gi]
        soot = smoothstep(0.25, 0.9, np.clip(s_u * (0.55 + 0.45 * S_soot(bu, bv)), 0, 1))
        if self.state == 'destroyed':
            w = np.select([near_slot, comp == DEBRIS, comp == BASE], [0.6, 0.45, 0.2], 0.0)
        else:
            w = np.select([isp, near_slot], [0.7, 0.35], 0.0)
        soot = soot * w
        out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
        trim_m = trim_m * (1 - soot)
        if self.state == 'damaged':
            brk = isp & self.notched[gj, gi] & top_like
            out = np.where(brk[..., None], BARE * 0.8 * (1 + 2 * grain)[..., None], out)
            trim_m = np.where(brk, 0, trim_m)
        return out, trim_m


# =============================================================================== end pieces
class EndPiece(Render):
    """A wall stub in one cell: from the cell edge on `side` 28 px in, with the other half of the collar."""

    def __init__(self, side, state='ok', wall='gdi', length=28.0, seed=5):
        assert wall == 'gdi', 'only the TS GDI wall so far'
        self.side, self.state, self.length = side, state, length
        self.setup_grid(128, 128)
        X, Y = self.X, self.Y
        P = W.P
        if side in 'WE':
            v = Y - 64.0
            d_edge = X if side == 'W' else 128.0 - X          # distance in from the joining edge
            self.stub_along = X + 64.0 if side == 'W' else X - 128.0 - 64.0
        else:
            v = X - 64.0
            d_edge = Y if side == 'N' else 128.0 - Y
            self.stub_along = Y + 64.0 if side == 'N' else Y - 128.0 - 64.0
        a = np.abs(v)
        arm = trap(a, P['top'], P['base'], P['h'])
        o = P['collar_out']
        col = trap(a, P['top'] + o, P['base'] + o, P['h'] + o)
        in_stub = d_edge <= length
        collar = np.abs(d_edge) <= P['collar_half']
        Hs = np.where(in_stub, arm, 0.0)
        Cs = np.where(in_stub, 1, 0).astype(np.int8)
        win = collar & (col > Hs)
        Hs = np.where(win, col, Hs); Cs = np.where(win, 2, Cs).astype(np.int8)
        if state == 'destroyed':
            n = self.noise2d(d_edge, v, 3.0, 23)
            k = length - d_edge                                   # distance back from the inner end
            keep = smoothstep(2, 14, k + 5 * n - 4)
            Hs = np.where(in_stub & (k < 22), Hs * (0.45 + 0.55 * keep), Hs)
        self.Hs, self.Cs = Hs, Cs
        self.d_edge, self.vv = d_edge, v
        self.slot_depth = 0.0
        self.finish_geometry()

    def render(self):
        hit, zh, comp, ptop_hit, gj, gi, rows = self.raycast()
        x, y = self.X[gj, gi], self.Y[gj, gi]
        nx, ny, nz = self.hf_normals(self.Hs, gj, gi)
        sh = self.shadows(hit, zh, gj, gi)
        ndl = np.clip(nx * W.LIGHT[0] + ny * W.LIGHT[1] + nz * W.LIGHT[2], 0, None)
        shade = W.AMBIENT + W.SKY * (0.5 + 0.5 * nz) + W.DIFFUSE * ndl * (1 - 0.85 * sh)
        top_like = nz > 0.75
        ew_face = np.abs(ny) >= np.abs(nx)
        tu = np.where(top_like | ew_face, x, y)
        tv = np.where(top_like, y, zh)
        grain = sample(NOISE_FINE, tu, tv) * 0.035 + sample(NOISE_MOTTLE, tu, tv) * 0.05
        albedo = self.stub_albedo(gj, gi, zh, grain, tu, tv)
        if self.state in ('damaged', 'destroyed'):
            albedo = self.weather_stub(albedo, comp, top_like, grain, tu, tv, heavy=self.state == 'destroyed')
            if self.state == 'destroyed':
                import damage as D
                S = D.Sampler(np.random.default_rng(98), 5.0)
                k = self.length - self.d_edge[gj, gi]
                soot = smoothstep(0.2, 0.9, np.clip(np.exp(-(k / 14.0) ** 2) * (0.6 + 0.4 * S(tu % 256, tv % 256)), 0, 1)) * 0.7
                albedo = albedo * (1 - soot[..., None]) + SOOT * soot[..., None]
        ao = 0.8 + 0.2 * np.clip(zh / W.P['h'], 0, 1)
        col = albedo * (shade * ao)[..., None]
        # keep the cast shadow to the stub's own strip so it never darkens the gate next to it
        band = (self.d_edge <= self.length + 3)
        ga = self.ground_alpha(rows, gi, clip_mask=band.astype(float))
        img, _ = self.compose(hit, col, ga, np.zeros(hit.shape), ring_alpha=0.55)
        return img


def render_gate(faction, orient, frame, trim=TRIM_GOLD):
    return Gate(faction, orient, frame, trim).render()


if __name__ == '__main__':
    import sys, os, time
    what = sys.argv[1]
    os.makedirs('gates/out2', exist_ok=True)
    if what == 'ends':
        for side in 'NESW':
            for st in ('ok', 'damaged', 'destroyed'):
                EndPiece(side, st).render().save(f'gates/out2/end-gdi-{side}-{st}.png')
                print('end', side, st, flush=True)
    else:
        fac, orients = what, sys.argv[2]
        frames = [int(f) for f in sys.argv[3:]] or list(range(FACTIONS[fac]['frames']))
        for o in orients:
            for f in frames:
                t = time.time()
                img, mask = render_gate(fac, o, f)
                img.save(f'gates/out2/{fac}-gate-{o}-{f:02d}.png')
                mask.save(f'gates/out2/{fac}-gate-{o}-{f:02d}-trim.png')
                print(fac, o, f, '%.1fs' % (time.time() - t), flush=True)
