"""
Faction gates, second pass: designed from each faction's own buildings (RA1 / TD sprites) rather than
real-world barrier types. Same system as gates3.py: plain ends for the wall end pieces, 3x1 / 1x3,
frames 0-9 closed -> open, 10-19 damaged, 20 destroyed, house-colour masks.

  allies  RA1 Allies  perimeter gate: a steel panel with house-colour geometric lines and a hazard top edge
                      that sinks into a reinforced trench, between two sensor pylons styled on the Gap
                      Generator (round concrete plinth with a house-colour ring, slim dark column, white fin)
                      whose status lights are solid blue when shut, blink amber while moving, green when open
  soviet  RA1 Soviets Tesla gate: two Tesla-coil pylons (rust concrete base with red panels, copper coil
                      windings, a steel electrode ball) throwing lightning across the gap; the arcs crackle,
                      falter and die as it opens; rusty concrete apron with a checkered hazard border
  tdgdi   TD GDI      a corrugated quonset-style barrier in GDI gold that sinks into a hazard-striped trench,
                      between two white domed silo towers with gold bands (the power plant / barracks look)
  tdnod   TD Nod      unchanged (gates3.TDNod)
"""
import numpy as np
from scipy import ndimage
import walls2 as W
import gates2 as G2
import gates3 as G3
from walls2 import smoothstep, phase
from gates3 import (FactionGate, SS, FZ, INF, OBJ, U0, U1, lerp,
                    P_BODY, P_SLEEVE, P_PYLON, P_PLATE, P_HINGE, P_RUBBLE, P_RAIL)

TRIMS = {'allies': np.array([62, 112, 222.]), 'soviet': np.array([206, 42, 30.]),
         'tdgdi': np.array([224, 178, 56.]), 'tdnod': np.array([206, 36, 30.])}
P_FIN, P_COIL, P_TOWER, P_BARRIER = 20, 21, 22, 23


def disc(U, V, cu, r):
    return np.hypot(U - cu, V) <= r


def screen_of(o, u, v, z):
    """ground (u, v, z) -> screen (x, y) in px."""
    if o == 'h':
        return u, 64.0 + v - FZ * z
    return 64.0 + v, u - FZ * z


class Glow:
    """Screen-space glowing strokes with a depth test against the ray-cast."""

    def __init__(self, gate, hit, zh):
        self.g, self.hit, self.zh = gate, hit, zh
        HS, WS = hit.shape
        self.core = np.zeros((HS, WS)); self.halo = np.zeros((HS, WS))

    def polyline(self, pts, intensity, width=1.0):
        """pts: list of (u, v, z)."""
        HS, WS = self.hit.shape
        m = np.zeros((HS, WS))
        pts = np.asarray(pts, float)
        for a, b in zip(pts[:-1], pts[1:]):
            n = int(max(np.abs(b - a)[:2].max() * SS * 2, 2))
            for t in np.linspace(0, 1, n):
                u, v, z = a + (b - a) * t
                x, y = screen_of(self.g.o, u, v, z)
                xi, yi = int(x * SS), int(y * SS)
                r = max(int(width * SS / 2), 1)
                y0, y1, x0, x1 = max(yi - r, 0), min(yi + r + 1, HS), max(xi - r, 0), min(xi + r + 1, WS)
                if y0 >= y1 or x0 >= x1:
                    continue
                vis = ~self.hit[y0:y1, x0:x1] | (self.zh[y0:y1, x0:x1] <= z + 0.8)
                m[y0:y1, x0:x1] = np.maximum(m[y0:y1, x0:x1], vis * 1.0)
        self.core = np.maximum(self.core, m * intensity)
        self.halo = np.maximum(self.halo, np.clip(ndimage.gaussian_filter(m, 3.0 * SS) * 3.2, 0, 1) * intensity)

    def apply(self, col, ga, core_c, halo_c, halo_alpha=0.7):
        a_h = np.clip(self.halo * halo_alpha, 0, 1)
        a_c = np.clip(self.core, 0, 1)
        # on surfaces: tinted by the halo, the core on top
        col = col * (1 - a_h[..., None]) + halo_c * a_h[..., None]
        col = col * (1 - a_c[..., None]) + core_c * a_c[..., None]
        # over the bare ground: the stroke carries its own colour and alpha (core over halo), see compose(glow=)
        a = a_c + a_h * (1 - a_c)
        gc = (core_c * a_c[..., None] + halo_c * (a_h * (1 - a_c))[..., None]) / np.maximum(a, 1e-6)[..., None]
        off = ~self.hit
        col = np.where((off & (a > 0))[..., None], gc, col)
        prev = self.g.glow_a if getattr(self.g, 'glow_a', None) is not None else 0.0
        self.g.glow_a = np.maximum(prev, np.where(off, a, 0.0))
        return col, ga


# =============================================================================== Allies
class AlliesPerimeter(FactionGate):
    faction = 'allies'
    HP = 40.0                        # panel height above the apron when shut
    APRON = 1.5
    PY = ((U0 + 12.0), (U1 - 12.0))  # pylon centres

    def build(self):
        U, V = self.Uc, self.Vc
        a = np.abs(V)
        self.apron(46.0, self.APRON)
        p0, p1 = U0 + 26, U1 - 26
        trench = (a <= 11) & (U >= p0) & (U <= p1)
        lips = (a > 11) & (a <= 14.5) & (U >= p0 - 3.5) & (U <= p1 + 3.5)
        self.trench, self.lips = trench, lips
        self.Hb = np.where(lips, 2.3, self.Hb)
        self.Hb = np.where(trench, 0.4, self.Hb)
        top = self.APRON + self.HP * max(1 - self.stage / 8.0, 0.0)
        notch = np.zeros_like(U)
        if self.state == 'damaged':
            jag = self.noise1d(U, 2.5, 21)
            for cu, d, w in ((0.3, 9, 16), (0.62, 14, 22)):
                t = np.clip(1 - ((U - lerp(U0, U1, cu)) / w) ** 2, 0, 1)
                notch = np.maximum(notch, (d + 2 * jag) * t ** 0.6)
            self.scorch_default()
            self.rubble(5, (U0 + 40, U1 - 40), (14, 30), (2.0, 3.4), self.APRON)
        self.top = top
        panel = (a <= 9) & (U >= p0 + 2) & (U <= p1 - 2)
        h = np.maximum(top - notch * (top > self.APRON + 2), 0.9)
        if self.state == 'destroyed':
            n = self.noise2d(U, V, 2.0, 5)
            h = np.where(n > 0.5, -INF, 2.0 + 5 * np.clip(n + 1, 0, 1))
        self.put(np.where(panel, h, -INF), P_PLATE)
        self.panel_top = top
        # sensor pylons after the Gap Generator
        n = self.noise2d(U, V, 1.4, 8)
        for i, cu in enumerate(self.PY):
            r = np.hypot(U - cu, V)
            plinth = np.where(r <= 12.5, 7.0 - 1.2 * np.clip((r - 11) / 1.5, 0, 1), -INF)
            self.put(plinth, P_SLEEVE)
            colh = 50.0
            fin_top = 63.0
            if self.state == 'destroyed':
                colh, fin_top = 18 + 4 * n, 0
            if self.state == 'damaged' and i == 1:
                fin_top = 54.0
            self.put(np.where(r <= 7.0, colh, -INF), P_PYLON)
            if fin_top > 0:
                if self.o == 'h':
                    fin = (np.abs(U - cu) <= 6.5) & (np.abs(V) <= 1.8)
                else:
                    fin = (np.abs(V) <= 6.5) & (np.abs(U - cu) <= 1.8)
                self.put(np.where(fin, fin_top, -INF), P_FIN)
        if self.state == 'destroyed':
            self.scorch_default()
            self.rubble(16, (U0, U1), (-30, 30), (2.2, 4.6), self.APRON,
                        palette=[np.array([176, 182, 190.]), np.array([90, 94, 100.]), W.CONCRETE * 0.8])
        # status lights: blue shut, amber blinking while moving, green open
        s = self.stage
        if self.state == 'destroyed':
            self.light, self.light_on = np.array([40, 40, 40.]), 0.0
        elif s == 0:
            self.light, self.light_on = np.array([70, 150, 255.]), 1.0
        elif s >= 9:
            self.light, self.light_on = np.array([80, 255, 110.]), 1.0
        else:
            self.light, self.light_on = np.array([255, 170, 40.]), 1.0 if s % 2 else 0.25

    def materials(self, c):
        gj, gi, u, v, zh, part, g = c['gj'], c['gi'], c['u'], c['v'], c['zh'], c['part'], c['grain']
        a = np.abs(v)
        isobj = c['comp'] == OBJ
        HS, WS = u.shape
        emit = np.zeros((HS, WS, 3))
        # apron: pale poured concrete in square slabs, steel lips along the trench
        conc = np.array([206, 206, 202.]) * (1 + g)[..., None]
        joint = (phase(u, 32.0) < 0.7) | (phase(v, 32.0, 16.0) < 0.7)
        conc = np.where(joint[..., None], conc * 0.8, conc)
        lip = self.lips[gj, gi]
        conc = np.where(lip[..., None], np.array([130, 136, 146.]) * (1 + g)[..., None], conc)
        tr = self.trench[gj, gi]
        conc = np.where(tr[..., None], np.array([60, 62, 66.]) * (1 + g)[..., None], conc)
        # panel: brushed steel, vertical seams, house-colour geometric lines, hazard top edge
        top = self.panel_top
        steel = np.array([188, 194, 202.]) * (1 + 0.8 * g)[..., None]
        seam = phase(u - U0, 46.0) < 0.8
        steel = np.where(seam[..., None], steel * 0.7, steel)
        fz = zh - self.APRON                                   # height up the panel face
        H = self.HP
        # chevrons pointing along the gate, riding with the panel
        pz = fz + (H - (top - self.APRON))                      # panel-local height (0 bottom .. H top)
        chev = np.abs(np.mod((u - U0) / 23.0 + np.abs(pz - H * 0.45) / 9.0, 1.0) - 0.5) < 0.12
        chev &= np.abs(pz - H * 0.45) < 8.0
        line = np.abs(pz - H * 0.45) < 1.3
        geo = (chev | line) & ~c['top_like']
        hz_face = (pz > H - 5.0) & ~c['top_like']
        on_top = c['top_like'] & (zh > top - 0.6)
        blue_top = on_top & (a <= 3.2)                                   # house-colour spine along the top
        hz_top = on_top & (top > self.APRON + 1) & ~blue_top
        hz = np.abs(np.mod((u + v + zh) / 6.0, 2.0) - 1.0)
        hzc = lerp(np.array([30, 30, 30.]), np.array([226, 190, 46.]), smoothstep(0.45, 0.55, hz)[..., None])
        panel = np.where((geo | blue_top)[..., None], self.trim * (1 + 0.6 * g)[..., None], steel)
        panel = np.where((hz_face | hz_top)[..., None], hzc, panel)
        # pylons
        plinth = np.array([196, 196, 190.]) * (1 + g)[..., None]
        ring = (zh > 3.2) & (zh < 5.8) & ~c['top_like']
        plinth = np.where(ring[..., None], self.trim * (1 + 0.6 * g)[..., None], plinth)
        col = np.array([122, 128, 140.]) * (1 + 1.2 * g)[..., None]
        lights = (np.abs(zh - 30) < 1.4) | (np.abs(zh - 38) < 1.4)
        col = np.where(lights[..., None] & ~c['top_like'][..., None],
                       lerp(np.array([30, 30, 34.]), self.light, self.light_on), col)
        emit += (isobj & (part == P_PYLON) & lights & ~c['top_like'])[..., None] * self.light * 0.55 * self.light_on
        fin = np.array([228, 230, 234.]) * (1 + g)[..., None]
        o = np.select([(part == P_PLATE)[..., None], (part == P_SLEEVE)[..., None], (part == P_PYLON)[..., None],
                       (part == P_FIN)[..., None]], [panel, plinth, col, fin], panel)
        alb = np.where(isobj[..., None], o, conc)
        trim = np.where(isobj & (((part == P_PLATE) & ((geo & ~hz_face) | blue_top) & ~hz_top) | ((part == P_SLEEVE) & ring)),
                        1.0, 0.0)
        return alb, trim, emit

    def overlay(self, col, ga, hit, zh):
        """a soft halo round the status lights so they read at game scale."""
        if self.light_on < 0.5 or self.state == 'destroyed':
            return col, ga
        gl = Glow(self, hit, zh)
        for cu in self.PY:
            for z in (30.0, 38.0):
                if self.o == 'h':                               # on the column's camera-facing (south) side
                    pts = [(cu - 1.5, 7.4, z), (cu + 1.5, 7.4, z)]
                else:
                    pts = [(cu + 7.4, -1.5, z), (cu + 7.4, 1.5, z)]
                gl.polyline(pts, 0.55, width=1.2)
        return gl.apply(col, ga, self.light * 1.0, self.light * 0.9, halo_alpha=0.35)


# =============================================================================== Soviets
class SovietTesla(FactionGate):
    faction = 'soviet'
    APRON = 1.2
    PY = ((U0 + 16.0), (U1 - 16.0))
    BALL_Z = 52.0
    POWER = [1.0, 1.0, 0.8, 0.95, 0.55, 0.35, 0.3, 0.1, 0.0, 0.0]
    BOLTS = [3, 3, 2, 3, 2, 1, 1, 1, 0, 0]

    def build(self):
        U, V = self.Uc, self.Vc
        a = np.abs(V)
        self.apron(48.0, self.APRON)
        n = self.noise2d(U, V, 1.4, 12)
        # copper ground rail with ceramic insulators between the pylons
        rail = (a <= 2.2) & (U >= self.PY[0] + 16) & (U <= self.PY[1] - 16)
        self.rail = rail
        self.Hb = np.where(rail, 1.9, self.Hb)
        studs = np.zeros_like(U, bool)
        for cu in np.arange(self.PY[0] + 28, self.PY[1] - 20, 24.0):
            studs |= disc(U, V, cu, 3.0)
        self.put(np.where(studs, 4.6, -INF), P_SLEEVE)
        for i, cu in enumerate(self.PY):
            du, r = np.abs(U - cu), np.hypot(U - cu, V)
            base = (du <= 15) & (a <= 15)
            self.put(np.where(base, 10.0, -INF), P_HINGE)
            top_col, top_ball = 40.0, self.BALL_Z + 6
            if self.state == 'destroyed':
                top_col, top_ball = 16 + 5 * n, 0
            if self.state == 'damaged' and i == 1:
                top_ball = self.BALL_Z + 1
            self.put(np.where(r <= 9.5, top_col, -INF), P_COIL)
            if top_ball > 0:
                self.put(np.where(r <= 3.2, self.BALL_Z, -INF), P_PYLON)
                ball = np.where(r < 7.5, self.BALL_Z - 2 + np.sqrt(np.clip(56 - r ** 2, 0, None)), -INF)
                self.put(np.minimum(ball, top_ball), P_FIN)
        p = self.POWER[self.stage]
        nb = self.BOLTS[self.stage]
        if self.state == 'damaged':
            p, nb = p * 0.8, max(nb - 1, 0)
        if self.state == 'destroyed':
            p, nb = 0.0, 0
        self.power, self.nbolts = p, nb
        self.scorch_default()
        if self.state == 'damaged':
            self.rubble(5, (U0 + 40, U1 - 40), (12, 30), (2.0, 3.4), self.APRON,
                        palette=[np.array([140, 112, 92.]), np.array([90, 84, 80.])])
        if self.state == 'destroyed':
            self.rubble(16, (U0, U1), (-30, 30), (2.2, 4.8), self.APRON,
                        palette=[np.array([140, 112, 92.]), np.array([176, 104, 60.]), np.array([70, 66, 64.])])

    def materials(self, c):
        gj, gi, u, v, zh, part, g = c['gj'], c['gi'], c['u'], c['v'], c['zh'], c['part'], c['grain']
        a = np.abs(v)
        isobj = c['comp'] == OBJ
        HS, WS = u.shape
        emit = np.zeros((HS, WS, 3))
        # apron: rust-stained Soviet concrete, black/white checker border like the SAM pad
        mot = G3.sample(G3.NOISE_MOTTLE, u * 1.4, v * 1.4)
        conc = lerp(np.array([150, 126, 106.]), np.array([122, 98, 80.]), np.clip(0.5 + 0.5 * mot, 0, 1)[..., None])
        conc = conc * (1 + 1.4 * g)[..., None]
        joint = (phase(u, 26.0) < 0.7) | (phase(v, 26.0, 13.0) < 0.7)
        conc = np.where(joint[..., None], conc * 0.78, conc)
        chk = ((np.floor(u / 6.0) + np.floor(v / 6.0)) % 2 == 0)
        border = a > 41
        conc = np.where(border[..., None], np.where(chk[..., None], np.array([210, 208, 200.]), np.array([34, 32, 30.])), conc)
        copper = np.array([184, 108, 58.])
        conc = np.where(self.rail[gj, gi][..., None], copper * (1 + 1.5 * g)[..., None], conc)
        # pylons
        base = np.array([140, 114, 94.]) * (1 + 1.2 * g)[..., None]
        panel = (zh > 2.5) & (zh < 8.5) & ~c['top_like']
        cu = np.where(u < 192, self.PY[0], self.PY[1])
        rim = c['top_like'] & (np.maximum(np.abs(u - cu), a) > 11.0) & (zh > 9.0)   # painted rim on the base top
        panel = panel | rim
        base = np.where(panel[..., None], self.trim * (1 + 0.6 * g)[..., None], base)
        wind = phase(zh, 3.4) < 1.1                               # coil windings
        coil = np.where(wind[..., None], copper * 1.15, copper * 0.55) * (1 + g)[..., None]
        coil = np.where(c['top_like'][..., None], np.array([70, 64, 60.]), coil)
        neck = np.array([90, 92, 98.]) * (1 + g)[..., None]
        ball = np.array([176, 180, 188.]) * (1 + 0.6 * g)[..., None]
        glow = self.power
        ball = lerp(ball, np.array([200, 230, 255.]), 0.5 * glow)
        emit += (isobj & (part == P_FIN))[..., None] * np.array([120, 170, 255.]) * 0.5 * glow
        emit += (isobj & (part == P_COIL) & wind)[..., None] * np.array([90, 140, 255.]) * 0.25 * glow
        stud = np.array([226, 224, 214.]) * (1 + g)[..., None]
        o = np.select([(part == P_HINGE)[..., None], (part == P_COIL)[..., None], (part == P_PYLON)[..., None],
                       (part == P_FIN)[..., None], (part == P_SLEEVE)[..., None]], [base, coil, neck, ball, stud], base)
        alb = np.where(isobj[..., None], o, conc)
        trim = np.where(isobj & (part == P_HINGE) & panel, 1.0, 0.0)
        return alb, trim, emit

    VLIM, ZLIM = 15.0, 8.0            # arcs stay within this band round the line between the balls

    def tame(self, pts):
        """soft-clamp a bolt so it stays inside the frame and near the electrodes' line."""
        pts = np.array(pts, float)
        pts[:, 0] = np.clip(pts[:, 0], self.PY[0] + 5, self.PY[1] - 5)
        pts[:, 1] = self.VLIM * np.tanh(pts[:, 1] / self.VLIM)
        zc = self.BALL_Z + 1
        pts[:, 2] = zc + self.ZLIM * np.tanh((pts[:, 2] - zc) / self.ZLIM)
        return list(pts)

    def bolt(self, rng, a, b, rough=12.0, depth=6):
        pts = [np.array(a, float), np.array(b, float)]
        for d in range(depth):
            new = [pts[0]]
            amp = rough / (1.7 ** d)
            for p, q in zip(pts[:-1], pts[1:]):
                m = (p + q) / 2
                m[1] += rng.normal(0, amp)
                m[2] += rng.normal(0, amp * 0.6)
                new += [m, q]
            pts = new
        return self.tame(pts)

    def overlay(self, col, ga, hit, zh):
        if self.nbolts == 0 or self.power <= 0:
            return col, ga
        seed = 1000 + self.frame * 7 + (0 if self.o == 'h' else 3) + 7919 * getattr(self, 'variant', 0)
        rng = np.random.default_rng(seed)
        gl = Glow(self, hit, zh)
        a = (self.PY[0] + 6.5, 0.0, self.BALL_Z + 1)
        b = (self.PY[1] - 6.5, 0.0, self.BALL_Z + 1)
        for k in range(self.nbolts):
            pts = self.bolt(rng, a, b, rough=11.0 + 3 * k)
            inten = self.power * (1.0 if k == 0 else 0.8)
            gl.polyline(pts, inten, width=1.3 if k == 0 else 0.9)
            # a short branch off the main bolt
            j = rng.integers(len(pts) // 4, 3 * len(pts) // 4)
            end = np.array(pts[j]) + np.array([rng.normal(0, 14), rng.normal(0, 10), rng.normal(-5, 4)])
            gl.polyline(self.bolt(rng, pts[j], end, rough=5.0, depth=4), inten * 0.7, width=0.8)
        return gl.apply(col, ga, np.array([236, 244, 255.]), np.array([90, 150, 255.]), halo_alpha=0.75)


# =============================================================================== TD GDI
class TDGDIQuonset(FactionGate):
    faction = 'tdgdi'
    APRON = 1.3
    R, HB = 22.0, 30.0              # barrier half-width, crest height
    PY = ((U0 + 17.0), (U1 - 17.0))

    def build(self):
        U, V = self.Uc, self.Vc
        a = np.abs(V)
        # rounded concrete pad like GDI building bibs
        self.apron(50.0, self.APRON)
        corner = np.hypot(np.clip(np.minimum(U, 384 - U) - 12, None, 0), np.clip(a - 38, 0, None))
        self.base_mask &= corner <= 12
        self.Hb = np.where(self.base_mask, self.Hb, 0.0)
        p0, p1 = self.PY[0] + 17, self.PY[1] - 17
        trench = (a <= self.R + 1) & (U >= p0) & (U <= p1)
        self.trench = trench
        self.hz = (a > self.R + 1) & (a <= self.R + 7) & (U >= p0 - 2) & (U <= p1 + 2)
        self.Hb = np.where(trench, 0.4, self.Hb)
        rise = max(1 - self.stage / 8.0, 0.0)
        crest = self.APRON + 0.3 + (self.HB - 0.3) * rise
        prof = crest - self.HB * (1 - np.sqrt(np.clip(1 - (V / self.R) ** 2, 0, 1)))
        amp = 0.7 * smoothstep(0.0, 0.2, rise)                                     # corrugation
        prof = prof + amp * np.cos(2 * np.pi * U / 8.0) * (a < self.R - 1)
        notch = np.zeros_like(U)
        if self.state == 'damaged':
            jag = self.noise1d(U, 2.5, 31)
            for cu, d, w in ((0.28, 8, 18), (0.66, 11, 22)):
                t = np.clip(1 - ((U - lerp(U0, U1, cu)) / w) ** 2, 0, 1)
                notch = np.maximum(notch, (d + 2 * jag) * t ** 0.6)
            self.scorch_default()
            self.rubble(5, (U0 + 40, U1 - 40), (-40, 40), (2.0, 3.4), self.APRON)
        prof = prof - notch
        inb = (a <= self.R) & (U >= p0 + 1) & (U <= p1 - 1)
        self.bar_ends = (p0 + 1, p1 - 1)
        if self.state == 'destroyed':
            n = self.noise2d(U, V, 2.2, 15)
            prof = np.where(n > 0.55, -INF, 1.0 + 6 * np.clip(n + 0.8, 0, 1))
        self.put(np.where(inb & (prof > 0.6), prof, -INF), P_BARRIER)
        self.crest = crest
        n = self.noise2d(U, V, 1.4, 16)
        for i, cu in enumerate(self.PY):
            r = np.hypot(U - cu, V)
            cyl, dome = 36.0, 11.0
            if self.state == 'destroyed':
                cyl, dome = 15 + 5 * n, 0.0
            h = np.where(r <= 15, cyl + dome * np.sqrt(np.clip(1 - (r / 15) ** 2, 0, 1)), -INF)
            if self.state == 'damaged' and i == 0:
                h = np.where(r < 9, h - 5 * np.clip(n + 0.6, 0, 1.5), h)
            self.put(h, P_TOWER)
        if self.state == 'destroyed':
            self.scorch_default()
            self.rubble(16, (U0, U1), (-34, 34), (2.4, 4.8), self.APRON,
                        palette=[np.array([214, 172, 60.]), np.array([220, 220, 214.]), np.array([150, 150, 146.])])

    def materials(self, c):
        gj, gi, u, v, zh, part, g = c['gj'], c['gi'], c['u'], c['v'], c['zh'], c['part'], c['grain']
        a = np.abs(v)
        isobj = c['comp'] == OBJ
        HS, WS = u.shape
        emit = np.zeros((HS, WS, 3))
        conc = np.array([176, 176, 170.]) * (1 + 1.2 * g)[..., None]
        joint = (phase(u, 40.0) < 0.7) | (phase(v, 40.0, 20.0) < 0.7)
        conc = np.where(joint[..., None], conc * 0.8, conc)
        hz = np.abs(np.mod((u + v) / 8.0, 2.0) - 1.0)
        hzc = lerp(np.array([32, 30, 28.]), np.array([226, 186, 50.]), smoothstep(0.45, 0.55, hz)[..., None])
        conc = np.where(self.hz[gj, gi][..., None], hzc, conc)
        conc = np.where(self.trench[gj, gi][..., None], np.array([64, 64, 60.]) * (1 + g)[..., None], conc)
        # barrier: corrugated GDI-gold armour with grey hoops, hazard stripes on its ends
        rib = np.cos(2 * np.pi * u / 8.0)
        gold = self.trim * (1 + 0.8 * g)[..., None] * (0.9 + 0.1 * rib)[..., None]
        hoop = phase(u - U0, 44.0) < 1.6
        bar = np.where(hoop[..., None], np.array([120, 120, 116.]) * (1 + g)[..., None], gold)
        endcap = ~c['top_like'] & (np.abs(c['nx'] if self.o == 'h' else c['ny']) > 0.6)
        endcap &= np.minimum(np.abs(u - self.bar_ends[0]), np.abs(u - self.bar_ends[1])) < 2.5
        hz2 = np.abs(np.mod((v + zh) / 5.0, 2.0) - 1.0)
        bar = np.where(endcap[..., None], lerp(np.array([32, 30, 28.]), np.array([226, 186, 50.]),
                                               smoothstep(0.45, 0.55, hz2)[..., None]), bar)
        # towers: white domed silos with a gold band and a dark hatch
        tw = np.array([224, 224, 218.]) * (1 + g)[..., None]
        band = (zh > 24) & (zh < 30) & ~c['top_like']
        tw = np.where(band[..., None], self.trim * (1 + 0.6 * g)[..., None], tw)
        cx = np.where(u < 192, self.PY[0], self.PY[1]) if self.o == 'h' else 64.0
        hatch = (zh > 4) & (zh < 16) & ~c['top_like'] & (c['ny'] > 0.35) & (np.abs(c['x'] - cx) < 4.5)
        tw = np.where(hatch[..., None], np.array([54, 56, 60.]), tw)
        o = np.select([(part == P_BARRIER)[..., None], (part == P_TOWER)[..., None]], [bar, tw], bar)
        alb = np.where(isobj[..., None], o, conc)
        trim = np.where(isobj & (((part == P_BARRIER) & ~hoop & ~endcap) | ((part == P_TOWER) & band)), 1.0, 0.0)
        return alb, trim, emit


DESIGNS = {'allies': AlliesPerimeter, 'soviet': SovietTesla, 'tdgdi': TDGDIQuonset, 'tdnod': G3.TDNod}


def render(fac, orient, frame, trim=None, variant=0):
    g = DESIGNS[fac](orient, frame, trim if trim is not None else TRIMS[fac])
    g.variant = variant
    return g.render()


if __name__ == '__main__':
    import sys, os, time
    os.makedirs('gates/out4', exist_ok=True)
    fac, orients = sys.argv[1], sys.argv[2]
    if fac == 'soviet-idle':
        # optional idle loop for the shut Tesla gate: frame 0 (or 10) then these three, arcs re-rolled each time
        for o in orients:
            for base, name in ((0, 'ok'), (10, 'damaged')):
                for k in (1, 2, 3):
                    t = time.time()
                    img, mask = render('soviet', o, base, variant=k)
                    img.save(f'gates/out4/soviet-gate-{o}-idle-{name}-{k}.png')
                    print('idle', o, name, k, '%.1fs' % (time.time() - t), flush=True)
        sys.exit()
    frames = [int(f) for f in sys.argv[3:]] or list(range(21))
    for o in orients:
        for f in frames:
            t = time.time()
            img, mask = render(fac, o, f)
            img.save(f'gates/out4/{fac}-gate-{o}-{f:02d}.png')
            mask.save(f'gates/out4/{fac}-gate-{o}-{f:02d}-trim.png')
            print(fac, o, f, '%.1fs' % (time.time() - t), flush=True)
