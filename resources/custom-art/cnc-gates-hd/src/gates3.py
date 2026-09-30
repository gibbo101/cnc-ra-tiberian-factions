"""
Faction gates for Red Alert Remastered (HD, 128 px per cell). Each has plain ends, so the wall
end pieces from gates2.py join it to walls exactly like the TS gates.

  allies  RA Allies    retractable steel security bollards that sink flush into sleeves
  soviet  RA Soviets   three riveted armour plates on a hinge beam that fall flat like drawbridges
  tdgdi   TD GDI       hydraulic wedge barriers: chevron ramps that lower flat
  tdnod   TD Nod       laser gate: black emitter pylons with three red beams that power down

horizontal 3x1 -> 384x128, vertical 1x3 -> 128x384
frames 0-9 closed -> open, 10-19 the same damaged, 20 destroyed; *-trim.png = house-colour mask.
The gate is modelled in (u, v): u along the gate, v across it. Horizontal: u = x, v = y - 64.
Vertical: u = y, v = x - 64. The end 28 px at each end are left for the wall end pieces.
Anything near the north end of a vertical gate stays under ~46 units so it doesn't poke above the frame.
"""
import numpy as np
from PIL import Image
from scipy import ndimage
import walls2 as W
import gates2 as G2
from walls2 import smoothstep, phase, sample, NOISE_FINE, NOISE_MOTTLE

SS, FZ, M, INF = G2.SS, G2.FZ, G2.M, G2.INF
BASE, OBJ = G2.BASE, G2.DEBRIS
UL, LE = 384.0, 28.0                   # gate length, end space for the wall pieces
U0, U1 = LE, UL - LE                   # usable span

# default trim (house colour) per faction for the baked frames; the masks allow any colour
TRIMS = {'allies': np.array([62, 112, 222.]), 'soviet': np.array([206, 42, 30.]),
         'tdgdi': np.array([224, 178, 56.]), 'tdnod': np.array([206, 36, 30.])}

# part ids
P_NONE, P_BODY, P_SLEEVE, P_PYLON, P_PLATE, P_HINGE, P_RUBBLE, P_RAIL, P_TOPEDGE = range(9)


def lerp(a, b, t):
    return a + (b - a) * t


class FactionGate(G2.Render):
    faction = None

    def __init__(self, orient, frame, trim=None, seed=11):
        self.o, self.frame = orient, frame
        self.trim = np.asarray(trim if trim is not None else TRIMS[self.faction], float)
        self.state = 'ok' if frame < 10 else ('damaged' if frame < 20 else 'destroyed')
        self.stage = frame % 10 if frame < 20 else 9
        self.rng = np.random.default_rng(seed)
        self.setup_grid(*((384, 128) if orient == 'h' else (128, 384)))
        if orient == 'h':
            self.Uc, self.Vc = self.X, self.Y - 64.0
        else:
            self.Uc, self.Vc = self.Y, self.X - 64.0
        self.slot_depth = 0.0
        self.part = np.zeros(self.X.shape, np.int8)
        self.scorch_pts = []                      # (u, v, radius) scorch spots
        self.beams = []                           # (z, intensity) for the laser gate
        self.build()
        self.finish_geometry()
        self.Hd_n = ndimage.gaussian_filter(np.where(self.deb_mask, self.Hd, np.maximum(self.Hb, 0)), 0.5 * SS)

    # ------------------------------------------------------------------ helpers
    def put(self, h, part):
        win = h > self.Hd
        self.Hd = np.where(win, h, self.Hd)
        self.part = np.where(win, part, self.part)
        return win

    def apron(self, half=48.0, h=1.0):
        a = np.abs(self.Vc)
        inu = (self.Uc >= 0) & (self.Uc <= UL)
        self.base_mask = inu & (a <= half)
        self.Hb = np.where(self.base_mask, h * np.clip((half - a) / 2.0, 0, 1), 0.0)

    def rubble(self, n, u_rng, v_rng, r_rng, z0=1.0, palette=None):
        rng, U, V = self.rng, self.Uc, self.Vc
        rj = self.noise2d(U, V, 1.5, 31)
        palette = palette or [W.CONCRETE * 0.85, W.CONCRETE * 0.65, np.array([90, 88, 84.])]
        for _ in range(n):
            cu, cv = rng.uniform(*u_rng), rng.uniform(*v_rng)
            r = rng.uniform(*r_rng)
            sx, sy = rng.uniform(0.8, 1.3), rng.uniform(0.8, 1.3)
            d = np.hypot((U - cu) / sx, (V - cv) / sy)
            rr = r * (1 + 0.15 * rj)
            h = np.where(d < rr, z0 + 0.95 * r * np.sqrt(np.clip(1 - (d / rr) ** 2, 0, 1)), -INF)
            win = self.put(h, P_RUBBLE)
            self.rock_col[win] = palette[rng.integers(len(palette))]

    # ------------------------------------------------------------------ render
    def render(self):
        hit, zh, comp, _, gj, gi, rows = self.raycast()
        HS, WS = hit.shape
        nb = self.hf_normals(self.Hb_n, gj, gi)
        no = self.hf_normals(self.Hd_n, gj, gi)
        isobj = comp == OBJ
        nx = np.where(isobj, no[0], nb[0]); ny = np.where(isobj, no[1], nb[1]); nz = np.where(isobj, no[2], nb[2])
        nx, ny, nz = self.adjust_normals(nx, ny, nz, gj, gi, zh, comp)
        sh = self.shadows(hit, zh, gj, gi)
        ndl = np.clip(nx * W.LIGHT[0] + ny * W.LIGHT[1] + nz * W.LIGHT[2], 0, None)
        shade = W.AMBIENT + W.SKY * (0.5 + 0.5 * nz) + W.DIFFUSE * ndl * (1 - 0.85 * sh)
        ndf = np.clip(nx * G2.FILL[0] + ny * G2.FILL[1] + nz * G2.FILL[2], 0, None)
        shade = np.where(isobj, shade + G2.FILL_I * ndf, shade)
        x, y = self.X[gj, gi], self.Y[gj, gi]
        u, v = self.Uc[gj, gi], self.Vc[gj, gi]
        top_like = nz > 0.75
        ew_face = np.abs(ny) >= np.abs(nx)
        tu = np.where(top_like | ew_face, x, y)
        tv = np.where(top_like, y, zh)
        grain = sample(NOISE_FINE, tu, tv) * 0.035 + sample(NOISE_MOTTLE, tu, tv) * 0.05
        ctx = dict(gj=gj, gi=gi, x=x, y=y, u=u, v=v, zh=zh, comp=comp, part=self.part[gj, gi],
                   nx=nx, ny=ny, nz=nz, top_like=top_like, grain=grain, tu=tu, tv=tv, hit=hit)
        albedo, trim_m, emit = self.materials(ctx)
        albedo = np.where((isobj & (ctx['part'] == P_RUBBLE))[..., None],
                          self.rock_col[gj, gi] * (1 + 1.5 * grain)[..., None], albedo)
        if self.state != 'ok':
            albedo, trim_m = self.weather(albedo, trim_m, ctx)
        eb_ = self.env_blur[gj, gi]
        ao = np.clip(1 - 0.02 * (eb_ - zh), 0.45, 1.0)
        ao = np.where(isobj, np.clip(ao, 0.78, 1.0), ao)
        col = albedo * (shade * ao)[..., None] + emit
        ga = self.ground_alpha(rows, gi)
        self.glow_a = None
        col, ga = self.overlay(col, ga, hit, zh)
        return self.compose(hit, col, ga, trim_m, ring_alpha=0.4, glow=self.glow_a)

    def adjust_normals(self, nx, ny, nz, gj, gi, zh, comp):
        return nx, ny, nz

    def overlay(self, col, ga, hit, zh):
        return col, ga

    def weather(self, albedo, trim_m, c):
        import damage as D
        rng = np.random.default_rng(97)
        S_wear, S_soot = D.Sampler(rng, 3.0), D.Sampler(rng, 5.0)
        bu, bv = c['tu'] % 256, c['tv'] % 256
        heavy = self.state == 'destroyed'
        out = self.weather_stub(albedo, np.where(c['comp'] == OBJ, G2.STUB, G2.NONE), c['top_like'],
                                c['grain'], c['tu'], c['tv'], heavy=heavy)
        chip = smoothstep(0.5 if heavy else 0.62, 0.95, S_wear(bu * 1.3, bv * 1.3)) * (trim_m > 0)
        out = out * (1 - chip[..., None]) + G2.BARE * (1 + c['grain'])[..., None] * chip[..., None]
        trim_m = trim_m * (1 - chip)
        s = np.zeros_like(c['u'])
        for (su, sv, sr) in self.scorch_pts:
            s = np.maximum(s, np.exp(-(((c['u'] - su) ** 2 + (c['v'] - sv) ** 2) / sr ** 2)))
        soot = smoothstep(0.2, 0.85, np.clip(s * (0.55 + 0.45 * S_soot(bu, bv)), 0, 1)) * (0.8 if heavy else 0.65)
        out = out * (1 - soot[..., None]) + G2.SOOT * soot[..., None]
        return out, trim_m * (1 - soot)

    def scorch_default(self):
        if self.state == 'damaged':
            for c in (0.22, 0.55, 0.8):
                self.scorch_pts.append((lerp(U0, U1, c), self.rng.uniform(-6, 10), 22))
        elif self.state == 'destroyed':
            for c in np.linspace(0.1, 0.9, 6):
                self.scorch_pts.append((lerp(U0, U1, c), self.rng.uniform(-10, 10), 30))


# =============================================================================== Allies
class Allies(FactionGate):
    """Retractable steel security bollards in sleeves on a clean concrete apron."""
    faction = 'allies'
    N, R, HB = 9, 10.0, 40.0

    def build(self):
        U, V = self.Uc, self.Vc
        a = np.abs(V)
        self.apron(48.0, 1.0)
        # dark steel strip carrying the bollards
        strip = (a <= 15) & (U >= U0) & (U <= U1)
        self.Hb = np.where(strip, 1.15, self.Hb)
        self.strip = strip
        top = max(self.HB * (1 - self.stage / 8.0), 1.6)      # flush with the steel strip when open
        sp = (U1 - U0) / self.N
        self.centres = [U0 + sp * (i + 0.5) for i in range(self.N)]
        tops = [top] * self.N
        jag = self.noise2d(U, V, 1.2, 5)
        if self.state == 'damaged':
            tops[3] = min(top, 13.0)              # sheared off
            tops[6] = max(top - 7.0, 1.6)         # rammed down
            self.scorch_default()
            self.rubble(5, (U0 + 20, U1 - 20), (14, 30), (2.0, 3.5), 1.0)
        if self.state == 'destroyed':
            tops = [float(self.rng.uniform(3, 12)) for _ in range(self.N)]
            self.scorch_default()
            self.rubble(16, (U0, U1), (-30, 30), (2.2, 4.6), 1.0)
        self.bollard_top = np.full(U.shape, -INF)
        for cu, t in zip(self.centres, tops):
            d = np.hypot(U - cu, V)
            # sleeve ring
            ring = (d < self.R + 3.5) & (d >= self.R - 0.3)
            self.put(np.where(ring, 1.7, -INF), P_SLEEVE)
            broken = self.state == 'destroyed' or (self.state == 'damaged' and t < top - 0.5)
            tt = t + (np.where(d < self.R, 1.8 * jag, 0) if broken else 0)
            h = np.where(d < self.R, tt - 0.8 * np.clip((d - (self.R - 1.2)) / 1.2, 0, 1), -INF)
            win = self.put(h, P_BODY)
            self.bollard_top = np.where(win, t, self.bollard_top)
        self.broken = np.full(U.shape, False)
        for cu, t in zip(self.centres, tops):
            if self.state == 'destroyed' or t < top - 0.5:
                self.broken |= np.hypot(U - cu, V) < self.R + 0.5

    def materials(self, c):
        gj, gi, u, v, zh, part, g = c['gj'], c['gi'], c['u'], c['v'], c['zh'], c['part'], c['grain']
        a = np.abs(v)
        isobj = c['comp'] == OBJ
        HS, WS = u.shape
        alb = np.zeros((HS, WS, 3)); trim = np.zeros((HS, WS)); emit = np.zeros((HS, WS, 3))
        # apron: clean concrete slabs, joints, yellow edge lines
        conc = np.array([204, 204, 200.]) * (1 + g)[..., None]
        joint = (phase(u, 32.0) < 0.7) | (phase(v, 32.0, 16.0) < 0.7)
        conc = np.where(joint[..., None], conc * 0.78, conc)
        line = np.abs(a - 42.5) < 1.6
        conc = np.where(line[..., None], np.array([226, 186, 52.]) * (1 + g)[..., None], conc)
        steel = np.array([112, 116, 122.]) * (1 + g)[..., None]
        bolts = (phase(u, 12.0, 6.0) < 1.0) & (np.abs(a - 12.5) < 1.0)
        steel = np.where(bolts[..., None], steel * 0.55, steel)
        on_strip = self.strip[gj, gi]
        alb = np.where(on_strip[..., None], steel, conc)
        # bollards
        bt = self.bollard_top[gj, gi]
        body = np.array([188, 192, 198.]) * (1 + 0.8 * g + 0.04 * np.sin(u * 2.1))[..., None]
        band = (zh > bt - 14) & (zh < bt - 8) & ~c['top_like']
        body = np.where(band[..., None], np.array([236, 236, 228.]) * (1 + g)[..., None], body)
        cap = c['top_like'] & (zh > bt - 1.2)
        r_c = np.min([np.hypot(u - cu, v) for cu in self.centres], axis=0)
        capc = np.where((r_c < self.R - 2.6)[..., None], self.trim * (1 + 0.6 * g)[..., None],
                        np.array([80, 84, 90.]) * (1 + g)[..., None])
        brk = self.broken[gj, gi]
        capm = cap & (r_c < self.R - 2.6) & ~brk
        capc = np.where(brk[..., None], np.array([150, 150, 152.]) * (1 + 3 * g)[..., None], capc)
        body = np.where(cap[..., None], capc, body)
        sleeve = np.array([70, 72, 78.]) * (1 + g)[..., None]
        o = np.where((part == P_SLEEVE)[..., None], sleeve, body)
        alb = np.where(isobj[..., None], o, alb)
        trim = np.where(isobj & (part == P_BODY) & capm, 1.0, 0.0)
        return alb, trim, emit


# =============================================================================== Soviets
class Soviet(FactionGate):
    """Three riveted armour plates hinged on a heavy beam; they fall flat to the north / west."""
    faction = 'soviet'
    T, HP, GAP = 10.0, 44.0, 5.0
    ANG = [0, 3, 9, 19, 32, 47, 62, 76, 86, 90]

    def build(self):
        U, V = self.Uc, self.Vc
        a = np.abs(V)
        self.apron(50.0, 1.0)
        # steel landing pad where the plates come down (north / west of the hinge)
        pad = (V <= -5) & (V >= -52 + 4) & (U >= U0) & (U <= U1)
        self.pad = pad
        th = np.radians(self.ANG[self.stage] if self.state != 'destroyed' else 90)
        self.theta = th
        T, Hp = self.T, self.HP
        plen = (U1 - U0 - 2 * self.GAP) / 3
        self.plates = [(U0 + i * (plen + self.GAP), U0 + i * (plen + self.GAP) + plen) for i in range(3)]
        dv = V + T / 2                                             # from the hinge (north face, bottom)
        # corners after rotating towards -v by th about the hinge
        c, s = np.cos(th), np.sin(th)
        Ax, Az = 0.0, 0.0
        Bx, Bz = T * c, T * s
        Cx, Cz = -Hp * s, Hp * c
        Dx, Dz = T * c - Hp * s, T * s + Hp * c

        def seg(x, x0, z0, x1, z1):
            t = np.clip((x - x0) / (x1 - x0 + 1e-9), 0, 1)
            return z0 + (z1 - z0) * t
        upper = np.where(dv <= Dx, seg(dv, Cx, Cz, Dx, Dz), seg(dv, Dx, Dz, Bx, Bz))
        lower = np.where(dv <= Ax, seg(dv, Cx, Cz, Ax, Az), seg(dv, Ax, Az, Bx, Bz))
        inside = (dv >= Cx - 1e-6) & (dv <= Bx + 1e-6)
        # plate-local height along the front face (the face that ends up on top)
        self.face_h = np.where(dv >= Dx, Hp * (Bx - dv) / max(Bx - Dx, 1e-6), Hp)
        self.on_topedge = dv < Dx
        self.lower = lower
        notch = np.zeros_like(U)
        if self.state == 'damaged':
            jag = self.noise1d(U, 2.5, 7)
            for cu, d, w in ((0.25, 9, 16), (0.58, 13, 20), (0.83, 7, 12)):
                t = np.clip(1 - ((U - lerp(U0, U1, cu)) / w) ** 2, 0, 1)
                notch = np.maximum(notch, (d + 2 * jag) * t ** 0.6)
            self.scorch_default()
            self.rubble(5, (U0 + 20, U1 - 20), (12, 30), (2.0, 3.6), 1.0)
        self.notch = notch
        for (p0, p1) in self.plates:
            inu = (U >= p0) & (U <= p1)
            h = upper
            if self.state == 'damaged' and th < np.radians(60):
                h = h - notch * c                       # dents in the top edge while upright
            if self.state == 'destroyed':
                n = self.noise2d(U, V, 2.0, 9)
                holes = n > 0.9
                h = np.where(holes, -INF, h)
            self.put(np.where(inu & inside, np.maximum(h, 0.5), -INF), P_PLATE)
        # heavy hinge beam in front (south / east) of the plates
        beam = (V >= T / 2 + 0.5) & (V <= T / 2 + 9) & (U >= U0 - 2) & (U <= U1 + 2)
        knuck = phase(U - U0, 22.0) < 4.0
        self.put(np.where(beam, np.where(knuck, 8.0, 6.0), -INF), P_HINGE)
        if self.state == 'destroyed':
            self.scorch_default()
            self.rubble(18, (U0, U1), (-44, 30), (2.4, 5.0), 1.0,
                        palette=[np.array([128, 52, 40.]), np.array([90, 86, 82.]), W.CONCRETE * 0.7])

    def adjust_normals(self, nx, ny, nz, gj, gi, zh, comp):
        return nx, ny, nz

    def materials(self, c):
        gj, gi, u, v, zh, part, g = c['gj'], c['gi'], c['u'], c['v'], c['zh'], c['part'], c['grain']
        a = np.abs(v)
        isobj = c['comp'] == OBJ
        HS, WS = u.shape
        emit = np.zeros((HS, WS, 3))
        # apron: dark concrete, hazard stripes on the outer edges
        conc = np.array([150, 148, 144.]) * (1 + 1.2 * g)[..., None]
        edge = a > 41
        hz = np.abs(np.mod((u + v) / 9.0, 2.0) - 1.0)
        hzc = lerp(np.array([40, 38, 34.]), np.array([214, 176, 44.]), smoothstep(0.45, 0.55, hz)[..., None])
        base = np.where(edge[..., None], hzc * (1 + g)[..., None], conc)
        pad = self.pad[gj, gi]
        dp = (phase(u + v, 7.0) < 1.2) ^ (phase(u - v, 7.0) < 1.2)       # diamond plate
        padc = np.array([118, 116, 112.]) * (1 + g)[..., None] * np.where(dp, 1.12, 0.94)[..., None]
        base = np.where(pad[..., None], padc, base)
        # plates: plate-local coordinates of each hit (s across the plate, fh up the plate)
        th = self.theta
        dvh = v + self.T / 2
        s_loc = dvh * np.cos(th) + zh * np.sin(th)
        fh = np.clip(-dvh * np.sin(th) + zh * np.cos(th), 0, self.HP)
        topedge = (fh > self.HP - 0.9) & (s_loc < self.T - 0.9)
        below = zh < self.lower[gj, gi] - 0.6                            # the dark gap under a tilted plate
        paint = np.array([146, 58, 44.])
        pu = np.zeros_like(u)
        for p0, p1 in self.plates:
            pu = np.where((u >= p0) & (u <= p1), u - p0, pu)
        seam = (phase(pu, 26.5, 13.25) < 0.8) | (np.abs(fh - self.HP / 3) < 0.7) | (np.abs(fh - 2 * self.HP / 3) < 0.7)
        rivet = ((phase(pu, 26.5, 13.25) < 2.2) & (phase(fh, 4.0) < 0.9)) | \
                (((np.abs(fh - self.HP / 3) < 2.0) | (np.abs(fh - 2 * self.HP / 3) < 2.0)) & (phase(pu, 5.0) < 0.9))
        plate = paint * (1 + 1.4 * g)[..., None]
        plate = np.where(seam[..., None], plate * 0.62, plate)
        plate = np.where(rivet[..., None] & ~seam[..., None], plate * 1.25, plate)
        stripe = (fh > self.HP * 0.44) & (fh < self.HP * 0.58)
        stripe_edge = (np.abs(fh - self.HP * 0.44) < 0.8) | (np.abs(fh - self.HP * 0.58) < 0.8)
        plate = np.where(stripe[..., None], self.trim * (1 + 0.6 * g)[..., None], plate)
        plate = np.where(stripe_edge[..., None], np.array([30, 28, 26.]), plate)
        hzb = fh > self.HP - 6.5
        hz2 = np.abs(np.mod((pu + fh) / 6.0, 2.0) - 1.0)
        plate = np.where(hzb[..., None], lerp(np.array([34, 32, 30.]), np.array([218, 180, 46.]),
                                              smoothstep(0.45, 0.55, hz2)[..., None]), plate)
        # top edge: house colour and black stripes, so a closed gate reads from straight above
        hz3 = np.abs(np.mod((pu + s_loc * 1.5) / 7.0, 2.0) - 1.0)
        on_edge_col = smoothstep(0.45, 0.55, hz3)
        edgec = lerp(np.array([34, 32, 30.]), self.trim, on_edge_col[..., None])
        plate = np.where(topedge[..., None], edgec * (1 + g)[..., None], plate)
        plate = np.where(below[..., None], np.array([26, 22, 20.]), plate)
        hinge = np.array([84, 82, 80.]) * (1 + g)[..., None]
        o = np.where((part == P_PLATE)[..., None], plate, hinge)
        alb = np.where(isobj[..., None], o, base)
        trim = np.where(isobj & (part == P_PLATE) & ~below &
                        ((stripe & ~stripe_edge & ~topedge) | (topedge & (on_edge_col > 0.5))), 1.0, 0.0)
        return alb, trim, emit


# =============================================================================== TD GDI
class TDGDI(FactionGate):
    """Hydraulic wedge barriers: three chevron ramps that rise out of the apron and lower flat."""
    faction = 'tdgdi'
    D, HB, GAP = 52.0, 34.0, 7.0

    def build(self):
        U, V = self.Uc, self.Vc
        a = np.abs(V)
        self.apron(48.0, 1.0)
        # the ramp faces the light: rises to the north on a horizontal gate, to the east on a vertical one
        rise_sign = 1.0                      # back edge south (h) / east (v)
        r = (V * rise_sign + self.D / 2) / self.D                   # 0 at the hinge, 1 at the back edge
        self.r = r
        plen = (U1 - U0 - 2 * self.GAP) / 3
        self.segs = [(U0 + i * (plen + self.GAP), U0 + i * (plen + self.GAP) + plen) for i in range(3)]
        hb = self.HB * max(1 - self.stage / 8.0, 0.0)
        pit = (a <= self.D / 2 + 3) & (U >= U0) & (U <= U1)
        self.pit = pit
        self.Hb = np.where(pit, 0.9, self.Hb)
        notch = np.zeros_like(U)
        if self.state == 'damaged':
            jag = self.noise1d(U, 2.0, 3)
            for cu, d, w in ((0.3, 8, 14), (0.7, 11, 18)):
                t = np.clip(1 - ((U - lerp(U0, U1, cu)) / w) ** 2, 0, 1)
                notch = np.maximum(notch, (d + 2 * jag) * t ** 0.6)
            self.scorch_default()
            self.rubble(5, (U0 + 20, U1 - 20), (-30, 30), (2.0, 3.4), 1.0)
        for (p0, p1) in self.segs:
            inu = (U >= p0) & (U <= p1) & (r >= 0) & (r <= 1)
            h = 2.0 + hb * r - notch * r
            if self.state == 'destroyed':
                n = self.noise2d(U, V, 2.2, 13)
                h = np.where(n > 0.75, -INF, 2.0 + 6 * r * np.clip(n + 0.5, 0, 1))
            self.put(np.where(inu, h, -INF), P_PLATE)
        # low guide rails in the gaps between segments
        for (p0, p1) in self.segs[:-1]:
            gap = (U > p1 + 1) & (U < p1 + self.GAP - 1) & (np.abs(V) <= self.D / 2)
            self.put(np.where(gap, 4.0, -INF), P_RAIL)
        if self.state == 'destroyed':
            self.scorch_default()
            self.rubble(16, (U0, U1), (-34, 34), (2.4, 4.8), 1.0,
                        palette=[np.array([96, 104, 74.]), np.array([60, 58, 52.]), np.array([196, 180, 140.])])

    def materials(self, c):
        gj, gi, u, v, zh, part, g = c['gj'], c['gi'], c['u'], c['v'], c['zh'], c['part'], c['grain']
        a = np.abs(v)
        isobj = c['comp'] == OBJ
        HS, WS = u.shape
        emit = np.zeros((HS, WS, 3))
        sand = np.array([198, 182, 142.]) * (1 + 1.2 * g)[..., None]
        joint = (phase(u, 40.0) < 0.7) | (phase(v, 40.0, 20.0) < 0.7)
        sand = np.where(joint[..., None], sand * 0.8, sand)
        pitc = np.array([104, 108, 88.]) * (1 + g)[..., None]
        base = np.where(self.pit[gj, gi][..., None], pitc, sand)
        # ramp tops: chevrons (house colour and black), olive frame
        r = self.r[gj, gi]
        pu = np.zeros_like(u); plen = self.segs[0][1] - self.segs[0][0]
        for p0, p1 in self.segs:
            pu = np.where((u >= p0) & (u <= p1), u - p0, pu)
        chev = np.abs(np.mod((np.abs(pu - plen / 2) + r * self.D * 0.9) / 9.0, 2.0) - 1.0)
        on_col = smoothstep(0.45, 0.55, chev)
        frame = (pu < 3.0) | (pu > plen - 3.0) | (r < 0.06) | (r > 0.94)
        top = c['top_like'] | (c['nz'] > 0.45)
        rampc = lerp(np.array([30, 30, 28.]), self.trim, on_col[..., None]) * (1 + 0.8 * g)[..., None]
        olive = np.array([96, 104, 74.]) * (1 + g)[..., None]
        # back face: olive with a narrow warning band near the top edge
        back = ~top & (r > 0.9)
        hb_now = self.HB * max(1 - self.stage / 8.0, 0.0) + 2.0
        wb = back & (zh > hb_now - 6) & (zh < hb_now - 2)
        hzw = np.abs(np.mod((pu + zh) / 6.0, 2.0) - 1.0)
        warn = lerp(np.array([30, 30, 28.]), np.array([222, 184, 50.]), smoothstep(0.45, 0.55, hzw)[..., None])
        olive = np.where(wb[..., None], warn, olive)
        plate = np.where((top & ~frame)[..., None], rampc, olive)
        rail = np.array([70, 74, 66.]) * (1 + g)[..., None]
        o = np.where((part == P_PLATE)[..., None], plate, rail)
        alb = np.where(isobj[..., None], o, base)
        trim = np.where(isobj & (part == P_PLATE) & top & ~frame & (on_col > 0.5), 1.0, 0.0)
        return alb, trim, emit


# =============================================================================== TD Nod
class TDNod(FactionGate):
    """Laser gate: black faceted emitter pylons at both ends, three red beams that power down."""
    faction = 'tdnod'
    HP = 46.0
    BEAM_Z = (9.0, 21.0, 33.0)
    POWER = [1.0, 1.0, 0.75, 0.9, 0.55, 0.3, 0.45, 0.12, 0.0, 0.0]      # flicker, then off
    FLICK = [(1, 1, 1), (1, 1, 1), (1, 0, 1), (1, 1, 1), (1, 1, 0), (0, 1, 0), (1, 0, 0), (0, 0, 1), (0, 0, 0), (0, 0, 0)]

    def build(self):
        U, V = self.Uc, self.Vc
        self.apron(46.0, 1.0)
        self.pylons = [(U0, U0 + 24.0), (U1 - 24.0, U1)]
        hp = self.HP
        n = self.noise2d(U, V, 1.5, 17)
        for i, (p0, p1) in enumerate(self.pylons):
            du = np.minimum(U - p0, p1 - U)
            dv = 12.0 - np.abs(V)
            d = np.minimum(du, dv)
            h = np.where((du >= 0) & (dv >= 0), np.minimum(hp, 2 + d * 9.0), -INF)
            # stepped cap
            h = np.where((du > 5) & (dv > 5), np.minimum(hp + 3, 2 + d * 9.0), h)
            if self.state == 'destroyed':
                h = np.minimum(h, 14 + 5 * n)
            if self.state == 'damaged' and i == 1:
                h = np.where(h > hp - 8, h - np.clip(6 + 3 * n, 0, 9), h)
            self.put(h, P_PYLON)
        p = self.POWER[self.stage]
        fl = self.FLICK[self.stage]
        if self.state == 'damaged':
            p *= 0.8
            fl = tuple(f if i != 1 else 0 for i, f in enumerate(fl))    # the middle emitter is dead
        if self.state != 'destroyed':
            self.beams = [(z, p * f) for z, f in zip(self.BEAM_Z, fl)]
        self.power = p if self.state != 'destroyed' else 0.0
        self.scorch_default()
        if self.state == 'damaged':
            self.rubble(4, (U0 + 30, U1 - 30), (10, 28), (2.0, 3.2), 1.0,
                        palette=[np.array([52, 52, 58.]), np.array([90, 90, 96.])])
        if self.state == 'destroyed':
            self.rubble(16, (U0, U1), (-30, 30), (2.2, 4.8), 1.0,
                        palette=[np.array([52, 52, 58.]), np.array([34, 34, 38.]), np.array([120, 118, 116.])])

    def materials(self, c):
        gj, gi, u, v, zh, part, g = c['gj'], c['gi'], c['u'], c['v'], c['zh'], c['part'], c['grain']
        a = np.abs(v)
        isobj = c['comp'] == OBJ
        HS, WS = u.shape
        # floor: black steel plates, bolts, thin red guide lines, a faint red track under the beams
        floor = np.array([54, 54, 60.]) * (1 + 1.6 * g)[..., None]
        seams = (phase(u, 24.0) < 0.7) | (phase(v, 24.0, 12.0) < 0.7)
        floor = np.where(seams[..., None], floor * 0.6, floor)
        bolt = (phase(u, 24.0, 12.0) < 1.1) & (phase(v, 24.0) < 1.1)
        floor = np.where(bolt[..., None], floor * 1.5, floor)
        guide = np.abs(a - 38.0) < 1.2
        red = np.array([200, 30, 26.])
        floor = np.where(guide[..., None], red * 0.8, floor)
        emit = np.zeros((HS, WS, 3))
        emit += (guide * 0.35)[..., None] * red * (0.4 + 0.6 * self.power)
        track = (a < 1.6) & (u > U0 + 24) & (u < U1 - 24)
        floor = np.where(track[..., None], np.array([70, 20, 18.]), floor)
        emit += (track * self.power * 0.6)[..., None] * red
        # pylons: gunmetal facets, a house-colour band, red lenses at the beam heights
        pyl = np.array([58, 58, 66.]) * (1 + 1.2 * g)[..., None]
        band = (zh > self.HP - 11) & (zh < self.HP - 6) & ~c['top_like']
        pyl = np.where(band[..., None], self.trim * (1 + 0.6 * g)[..., None], pyl)
        lens = np.zeros_like(u, bool)
        for z in self.BEAM_Z:
            lens |= (np.abs(zh - z) < 1.6) & ~c['top_like']
        lens_on = self.power if self.state != 'destroyed' else 0.0
        pyl = np.where(lens[..., None], lerp(np.array([60, 10, 10.]), np.array([255, 90, 70.]), lens_on), pyl)
        emit += (lens * lens_on * 0.6)[..., None] * np.array([255, 60, 40.])
        alb = np.where(isobj[..., None], pyl, floor)
        trim = np.where(isobj & (part == P_PYLON) & band, 1.0, 0.0)
        return alb, trim, np.where((c['hit'])[..., None], emit, 0)

    def overlay(self, col, ga, hit, zh):
        """Draw the beams in screen space with a depth test against what the ray hit."""
        if not self.beams or max(b for _, b in self.beams) <= 0:
            return col, ga
        HS, WS = hit.shape
        core = np.zeros((HS, WS)); glow = np.zeros((HS, WS))
        u0, u1 = (U0 + 24) * SS, (U1 - 24) * SS
        for z, inten in self.beams:
            if inten <= 0:
                continue
            m = np.zeros((HS, WS))
            if self.o == 'h':
                r = int(round((64.0 - FZ * z) * SS))
                m[max(r - 3, 0):r + 3, int(u0):int(u1)] = 1.0
            else:
                cc = int(round(64.0 * SS))
                r0, r1 = int(u0 - FZ * z * SS), int(u1 - FZ * z * SS)
                m[max(r0, 0):r1, cc - 3:cc + 3] = 1.0
            # depth test: the beam shows where it is above whatever the ray hit
            vis = ~hit | (zh <= z + 0.5)
            m = m * vis
            core = np.maximum(core, m * inten)
            glow = np.maximum(glow, ndimage.gaussian_filter(m, 3.0 * SS) * 3.0 * inten)
        glow = np.clip(glow, 0, 1)
        core_c = np.array([255, 214, 200.]); glow_c = np.array([255, 40, 30.])
        a_g = glow * 0.75
        col = col * (1 - a_g[..., None]) + glow_c * a_g[..., None]
        col = col * (1 - core[..., None]) + core_c * core[..., None]
        ga = np.maximum(ga, np.maximum(a_g, core))
        # where there was only ground, the colour is the beam's
        col = np.where(~hit[..., None] & (np.maximum(a_g, core) > 0)[..., None],
                       np.where((core > 0.3)[..., None], core_c, glow_c), col)
        return col, ga


DESIGNS = {'allies': Allies, 'soviet': Soviet, 'tdgdi': TDGDI, 'tdnod': TDNod}


def render(fac, orient, frame, trim=None):
    return DESIGNS[fac](orient, frame, trim).render()


if __name__ == '__main__':
    import sys, os, time
    os.makedirs('gates/out3', exist_ok=True)
    fac, orients = sys.argv[1], sys.argv[2]
    frames = [int(f) for f in sys.argv[3:]] or list(range(21))
    for o in orients:
        for f in frames:
            t = time.time()
            img, mask = render(fac, o, f)
            img.save(f'gates/out3/{fac}-gate-{o}-{f:02d}.png')
            mask.save(f'gates/out3/{fac}-gate-{o}-{f:02d}-trim.png')
            print(fac, o, f, '%.1fs' % (time.time() - t), flush=True)
