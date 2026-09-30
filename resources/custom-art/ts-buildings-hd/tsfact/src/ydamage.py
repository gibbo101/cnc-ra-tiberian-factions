"""
Damage for the Construction Yard: 1 damaged, 2 destroyed (TS GTCNST frames 1 and 2).

Greys and browns only: soot, cracks, dust, pale fresh breaks, torn cladding, angular rubble. Everything is
placed in world space (wnoise, seeded chunk lists), so the TS-angle and RA-grid versions show exactly the same
damage in the same places.

  1  damaged    lamps out; two holes torn in the grey roof panels; a gash in the east cladding by the north
                fan; the window box's north end smashed; the north fan wrecked and the middle one missing blades;
                the thin stack snapped; chipped rib and coping edges; scorch; rubble along the east kerb
  2  destroyed  most of the grey panels gone (the green ribs stand over the dark hangar, two of them snapped);
                the east cladding torn open; the window box collapsed; fans and stacks gone; a hole in the south
                wall; the crane toppled onto the apron with its claw beside it; heavy scorch; rubble everywhere
"""
import numpy as np
import hd, yard as Y, wnoise as WN
import walls2 as W
from walls2 import smoothstep

DEBRIS = 40
SOOT = np.array([30, 29, 28.])
FRESH = np.array([206, 198, 180.])
DUST = np.array([120, 110, 92.])
BARE = np.array([138, 140, 146.])        # torn metal
RUST = np.array([120, 86, 56.])
ROCK = {'conc': W.CONCRETE * 0.84, 'panel': np.array([158, 156, 148.]) * 0.85, 'green': np.array([0, 214, 0.]) * 0.8,
        'steel': np.array([146, 148, 158.]) * 0.9, 'dark': np.array([72, 72, 76.]), 'rust': RUST}


def blob(X, Y, cx, cy, rx, ry, rough, seed, feat=7.0):
    """signed field of an irregular blob: < 0 inside."""
    e = np.sqrt(((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2)
    return e - 1.0 - rough * WN.noise(X, Y, feat, seed)


class Chunks:
    """angular rubble chunks at fixed world positions (seeded, so every view gets the same ones)."""
    def __init__(self, seed):
        self.rng = np.random.default_rng(seed)
        self.items = []

    def scatter(self, n, area, sizes, kinds, weights=None, on_top=False):
        (x0, x1), (y0, y1) = area
        for _ in range(n):
            cx, cy = self.rng.uniform(x0, x1), self.rng.uniform(y0, y1)
            rr = self.rng.uniform(*sizes)
            kind = kinds[self.rng.choice(len(kinds), p=weights)]
            nf = int(self.rng.integers(5, 8))
            ang = np.sort(self.rng.uniform(0, 2 * np.pi, nf))
            dk = rr * self.rng.uniform(0.7, 1.1, nf)
            topz = rr * self.rng.uniform(0.5, 0.85)
            tilt = self.rng.normal(0, 0.18, 2)
            steep = self.rng.uniform(1.3, 2.4)
            shade = self.rng.uniform(0.9, 1.08)
            self.items.append((cx, cy, rr, kind, ang, dk, topz, tilt, steep, shade, on_top))

    def apply(self, X, Y, H, C, rock):
        for (cx, cy, rr, kind, ang, dk, topz, tilt, steep, shade, on_top) in self.items:
            win = (np.abs(X - cx) < 2 * rr + 2) & (np.abs(Y - cy) < 2 * rr + 2)
            if not win.any():
                continue
            ddx, ddy = X[win] - cx, Y[win] - cy
            g = np.max([np.cos(a) * ddx + np.sin(a) * ddy - d for a, d in zip(ang, dk)], axis=0)
            h = np.clip(-g * steep, 0, None)
            h = np.minimum(h, np.clip(topz + tilt[0] * ddx + tilt[1] * ddy, 0.4, None)) * (g < 0)
            base = H[win] * 0.96 if on_top else Y_pad(H[win])
            hh = np.where(h > 0, h + base, 0)
            full = np.zeros_like(H); full[win] = hh
            m = full > H
            H[m] = full[m]; C[m] = DEBRIS
            rock[m] = ROCK[kind] * shade
        return H, C, rock


def Y_pad(h):
    return np.minimum(h, Y.P['pad_h'])


def crane_fallen(p=Y.P):
    cr = p['crane']
    px, py = cr['pivot']
    return dict(pivot_h=13.0, tip=(-26.0, 164.0, 9.0), tail=18.0, claw_at=(-44.0, 128.0, -6.0))


def model(level, p=Y.P):
    """a model function for hd.Render: the yard with damage `level` applied."""
    def f(X, Yy, **kw):
        if level == 2:
            kw = dict(kw); kw['crane_pose'] = crane_fallen(p)
        sc = Y.scene(X, Yy, p=p, **kw)
        return damage_scene(sc, X, Yy, level, p)
    return f


def damage_scene(sc, X, Yy, level, p=Y.P):
    H = sc.H.copy(); C = sc.C.copy()
    broken = np.zeros_like(H); soot = np.zeros_like(H); tear = np.zeros_like(H)
    rock = np.zeros(H.shape + (3,), np.float32)
    zo = Y.roof_z(X, p)
    yS, yN = p['yS'], p['yN']
    drib, k, yk = Y.rib_index(Yy, p)
    on_rib = drib <= p['rib_w'] / 2
    jag = WN.noise(X, Yy, 2.6, 101)
    shell = sc.slab('shell')
    closed = (Yy >= yN) & (Yy <= yS - 4) & (X >= p['x_open'] - 6) & (zo > 0)

    def chip(Harr, where, depth, thr, seed):
        n = WN.noise(X, Yy, 3.0, seed)
        c = smoothstep(thr, thr + 0.5, n) * where
        return np.where(c > 0, np.maximum(Harr - depth * c, 0), Harr), c

    # ---------------------------------------------------------------- chipped rib and coping edges
    b = p['box']
    rib_edge = (np.abs(drib - p['rib_w'] / 2) < 2.2)
    if level == 1:
        H, c1 = chip(H, closed & rib_edge & (X < p['xc'] + 12), 3.0, 1.0, 102)
        box_edge = closed & (Yy >= b['y0']) & (Yy <= b['y1']) & (np.abs(X - b['x1']) < 3.5)
        H, c2 = chip(H, box_edge, 4.0, 0.9, 103)
        broken = np.maximum(broken, 0.6 * smoothstep(0.3, 0.7, c2))
        st, c3 = chip(shell.top, (shell.top >= 0) & rib_edge, 3.0, 1.0, 104)
        shell.top = np.where(shell.top >= 0, np.maximum(st, shell.bot + 0.5), shell.top)

    chunks = Chunks(200 + level)
    if level == 1:
        # (as TS GTCNST 1) scorched holes among the grey panels, near the crown and the north-east
        f = np.minimum.reduce([blob(X, Yy, -30, -98, 26, 18, 0.4, 11), blob(X, Yy, 6, -34, 20, 15, 0.45, 12),
                               blob(X, Yy, -70, 10, 18, 13, 0.45, 15), blob(X, Yy, 14, -140, 16, 12, 0.45, 16)])
        panel = (shell.top >= 0) & (shell.comp == Y.PANEL)
        hole = (f < 0) & panel & (shell.bot > p['pad_h'] + 8)
        shell.top = np.where(hole, -1.0, shell.top)
        wp = closed & (X < p['xc'] - 1.5) & (drib > p['rib_w'] / 2) & (f < 0)
        H = np.where(wp, np.minimum(H, 24 + 6 * np.abs(jag)), H); C = np.where(wp, Y.INSIDE, C)
        tear = np.maximum(tear, (np.abs(f) < 0.07) * (panel | closed))
        sc.extra['void'] = (closed & (f < 0.1) & (X < p['xc'])).astype(np.float32)
        for (cx, cy, rr) in ((-30, -98, 52.0), (6, -34, 42.0), (-70, 10, 36.0), (14, -140, 34.0), (-110, -60, 30.0)):
            soot = np.maximum(soot, 0.95 * np.exp(-((X - cx) ** 2 + (Yy - cy) ** 2) / rr ** 2))
        # the flat diagonal under the window box torn along its length: ragged gaps in the cladding (dark
        # behind) and bent pieces of it lifting off, as TS draws it
        xj = Y.x_join(p); xe = p['diag'][2]
        b = p['box']
        boxfp = (Yy >= b['y0'] - 1) & (Yy <= b['y1'] + 1) & (X >= b['x0'] - 1) & (X <= b['xf'] + 1.5)
        dg = closed & (X > xj + 2) & (X < xe - 3) & ~boxfp
        t = WN.noise(X, Yy, 11, 31) + 0.3 * WN.noise(X, Yy, 3.5, 32)
        rip = dg & (t > 0.5)
        H = np.where(rip, np.maximum(H - (3.5 + 1.5 * np.abs(jag)), p['pad_h']), H)   # shallow: panels gone
        C = np.where(rip, Y.INSIDE, C)
        flap = dg & (t > 0.2) & (t <= 0.5) & (WN.noise(X, Yy, 6, 35) > 0.4)
        H = np.where(flap, H + 1.5 + 1.5 * smoothstep(0.2, 0.5, t), H)              # cladding lifting off
        sc.extra['bent'] = (dg & (t > 0.1) & ~rip).astype(np.float32)
        soot = np.maximum(soot, dg * smoothstep(0.1, 0.6, t) * 0.5)
        # the window box: its coping cracked and chipped along the front, a few panes out, the north end smashed
        b = p['box']
        inb_ = closed & (Yy >= b['y0']) & (Yy <= b['y1']) & (X >= b['x0']) & (X <= b['xf'])
        rough = inb_ & (X <= b['x1'] + 0.5)
        H = np.where(rough, H - 1.2 * np.abs(WN.noise(X, Yy, 3, 36)), H)
        bitez = WN.noise(X, Yy, 7, 33)
        bite = inb_ & (X > b['x1'] - 4) & (bitez > 0.95)
        H = np.where(bite, np.minimum(H, b['z1'] - 2.5 - 1.5 * np.abs(jag)), H)
        broken = np.maximum(broken, bite * 0.5)
        sc.extra['rubbly'] = rough.astype(np.float32)
        bn = closed & (Yy >= b['y0']) & (Yy < -96 + 8 * WN.noise(X, Yy, 6, 14)) & (X >= b['x0']) & (X <= b['xf'])
        H = np.where(bn, np.minimum(H, zo + 3 + 7 * np.abs(jag)), H)
        broken = np.maximum(broken, bn * 0.6)
        soot = np.maximum(soot, inb_ * smoothstep(0.3, 1.2, bitez) * 0.35 + bn * 0.45)
        pane = np.floor((Yy - b['y0']) / 22.0)                       # whole panes between the mullions
        hsh = np.mod(np.sin(pane * 12.9898 + 4.1) * 43758.5453, 1.0)
        sc.extra['panes'] = (hsh > 0.62).astype(np.float32)
        # rubble: green cladding and grey pieces along the east kerb, a few round the crane base
        chunks.scatter(12, ((160, 182), (-150, 90)), (2.4, 5.6), ['green', 'conc', 'steel', 'dark'], [0.55, 0.2, 0.15, 0.1])
        chunks.scatter(5, ((140, 170), (-150, -96)), (3.0, 6.0), ['conc', 'green', 'steel'], [0.4, 0.4, 0.2])
        chunks.scatter(5, ((92, 160), (130, 176)), (2.2, 4.6), ['green', 'conc', 'dark'], [0.4, 0.4, 0.2])
        chunks.scatter(6, ((40, 110), (150, 182)), (2.2, 4.8), ['green', 'conc', 'dark', 'steel'], [0.4, 0.3, 0.15, 0.15])
        chunks.scatter(4, ((-150, -60), (104, 150)), (2.0, 4.0), ['conc', 'panel', 'dark'], [0.4, 0.4, 0.2])
        # a chunk knocked out of the south arch rib, low on its west side
        r0 = sc.slab('rib0')
        ch = blob(X, Yy, -150, 96, 16, 10, 0.4, 37) < 0
        r0.top = np.where(ch & (r0.top >= 0), np.maximum(r0.top - 5.0 - 2 * np.abs(jag), r0.bot + 1.0), r0.top)
        broken = np.maximum(broken, ch * 0.9)
    else:
        # most of the grey panels gone: only ragged strips near the foot and a few scraps stay
        panel = (shell.top >= 0) & (shell.comp == Y.PANEL)
        k1 = shell.bot - (26 + 10 * WN.noise(X, Yy, 9, 21))       # < 0: the strip along the foot stays
        k2 = np.full_like(X, -1.0)
        keep = (k1 <= 0)
        gone = panel & ~keep
        shell.top = np.where(gone, -1.0, shell.top)
        # torn metal only along the ragged edges of what is left
        near = np.minimum(np.where(k1 <= 0, np.abs(k1) / 4.0, 9), np.where(k2 > 0, k2 / 0.06, 9))
        tear = np.maximum(tear, (panel & keep) * (1 - smoothstep(0.6, 1.4, near)))
        # two ribs snapped
        for kk, (x0, x1) in ((2, (-64.0, -2.0)), (5, (8.0, 44.0))):
            yk_ = Y.rib_y(kk, p)
            snap = (shell.top >= 0) & (np.abs(Yy - yk_) <= p['rib_w'] / 2 + 0.5) & (X > x0 + 6 * jag) & (X < x1 + 6 * jag)
            shell.top = np.where(snap, -1.0, shell.top)
            Hm = closed & (np.abs(Yy - yk_) <= p['rib_w'] / 2 + 0.5) & (X > x0) & (X < x1)
            H = np.where(Hm, np.minimum(H, zo), H)
            near = (np.abs(Yy - yk_) <= p['rib_w'] / 2 + 1) & ((np.abs(X - x0) < 5) | (np.abs(X - x1) < 5))
            broken = np.maximum(broken, near * 1.0)
        # the grey panels between the ribs west of the crown (the solid part) fall in too
        wp = closed & (X < p['xc'] - 1.5) & (drib > p['rib_w'] / 2) & (X > p['x_open'] - 6)
        H = np.where(wp, np.minimum(H, 18 + 6 * np.abs(jag)), H); C = np.where(wp, Y.INSIDE, C)
        # the east cladding torn open (big pieces), the fans with it
        t = WN.noise(X, Yy, 34, 23) + 0.18 * WN.noise(X, Yy, 10, 24)
        for fy in p['fans_y']:
            t = np.maximum(t, 0.4 * (np.hypot(X - p['fan_x'], Yy - fy) < p['fan_r'] + 6) + 0.0)
        torn = closed & (t > 0.15) & (X > p['xc'] - 4) & (X < p['diag'][2] - 10) & ~((drib <= p['rib_w'] / 2) & (X < p['xc'] + 10))
        floor = 22 + 10 * np.abs(jag)
        H = np.where(torn, np.minimum(H, floor), H); C = np.where(torn, Y.INSIDE, C)
        tear = np.maximum(tear, closed * (np.abs(t - 0.15) < 0.05))
        sc.extra['void'] = (closed & ((t > 0.15 - 0.12) | wp)).astype(np.float32)   # hole sides: the dark inside
        # the window box collapsed onto the slope
        inb = closed & (Yy >= b['y0']) & (Yy <= b['y1']) & (X >= b['x0']) & (X <= b['xf'])
        H = np.where(inb & ~torn, np.minimum(H, zo + 2 + 8 * np.abs(jag)), H)
        broken = np.maximum(broken, inb * smoothstep(0.55, 1.1, np.abs(WN.noise(X, Yy, 5, 26))) * 0.8)
        soot = np.maximum(soot, inb * 0.8)
        # fans gone (their holes torn open), stacks down to stumps
        for (sx, sy, sr, sh) in p['stacks']:
            zb = float(Y.roof_z(np.array([sx]), p)[0])
            m = np.hypot(X - sx, Yy - sy) <= sr + 3.5
            H = np.where(m, np.minimum(H, zb + (9 if sr > 5 else 14) + 3 * jag), H)
            broken = np.maximum(broken, m * 0.7)
        # a hole in the south wall's east part (the roof over it caved in)
        sh_ = blob(X, Yy, 98, 80, 34, 24, 0.3, 25)
        sw = (sh_ < 0) & closed
        H = np.where(sw, np.minimum(H, 16 + 8 * np.abs(jag)), H); C = np.where(sw, Y.INSIDE, C)
        tear = np.maximum(tear, closed * (np.abs(sh_) < 0.06))
        sc.extra['void'] = np.maximum(sc.extra.get('void', 0 * H), (closed & (sh_ < 0.12)).astype(np.float32))
        # scorch everywhere
        for (cx, cy, rr) in ((-60, -60, 70.0), (60, -90, 60.0), (0, 40, 60.0), (-80, 150, 50.0), (120, 120, 40.0),
                             (150, -40, 40.0)):
            soot = np.maximum(soot, np.exp(-((X - cx) ** 2 + (Yy - cy) ** 2) / rr ** 2))
        # rubble: apron in front of the arch, inside the hangar, along the east, on the torn roof
        chunks.scatter(12, ((-150, 30), (108, 178)), (2.6, 7.0), ['conc', 'panel', 'green', 'steel', 'dark', 'rust'],
                       [0.3, 0.2, 0.2, 0.1, 0.1, 0.1])
        chunks.scatter(7, ((-150, 10), (-140, 80)), (3.0, 7.5), ['dark', 'rust', 'green', 'panel'],
                       [0.4, 0.25, 0.2, 0.15])
        chunks.scatter(8, ((148, 180), (-150, 90)), (2.6, 6.0), ['conc', 'green', 'steel'], [0.4, 0.4, 0.2])
    H, C, rock = chunks.apply(X, Yy, H, C, rock)
    if level == 2:
        sc.slabs = [s_ for s_ in sc.slabs if s_.name not in ('lamps',)]
    sc.H, sc.C = H.astype(np.float32), C.astype(np.int16)
    sc.extra.update(broken=broken.astype(np.float32), soot=soot.astype(np.float32),
                    tear=tear.astype(np.float32), rock=rock)
    return sc


def mats(r, alb, level, p=Y.P):
    """damage on top of the yard's materials: dust, soot, cracks, fresh breaks, torn metal, rubble colours,
    lamps out, wrecked fans."""
    x, y, z, comp = r.x, r.y, r.z, r.comp
    top = r.nz > 0.75
    out = alb.copy()
    grain = WN.noise(x, y + z, 1.2, 301) * 0.05
    g1 = (1 + grain)[..., None]
    not_green = ~((alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40))
    # dust on tops
    dust = smoothstep(0.5, 1.4, WN.noise(x, y, 14, 302)) * np.where(top, 0.45, 0.2) * (0.6 if level == 1 else 1.0)
    out = out * (1 - dust[..., None]) + DUST * g1 * dust[..., None]
    # soot
    s = r.field('soot')
    soot = smoothstep(0.2, 0.8, np.clip(s * (0.6 + 0.4 * WN.noise(x, y + z, 6, 303)), 0, 1)) * (0.65 if level == 1 else 0.85)
    out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
    if level == 1:
        south = (r.ny > 0.6) & (r.nz < 0.6)
        sw = np.exp(-(((x - 84) / 30.0) ** 2 + ((z - 38) / 24.0) ** 2)) + 0.8 * np.exp(-(((x + 120) / 26.0) ** 2 + ((z - 60) / 26.0) ** 2))
        s2 = smoothstep(0.15, 0.8, np.clip(sw * (0.6 + 0.4 * WN.noise(x, z, 5, 312)), 0, 1)) * 0.7 * south
        out = out * (1 - s2[..., None]) + SOOT * s2[..., None]
    # cracks on concrete and walls
    conc = np.isin(comp, [Y.PAD, Y.KERB, Y.BOX]) | ((comp == Y.ROOF) & (r.ny > 0.6))
    cn = WN.ridge(x + 0.3 * z, y - 0.7 * z, 9, 304) + 0.12 * np.abs(WN.noise(x, y + z, 1.5, 308))
    cmask = smoothstep(1.0 if level == 1 else 0.4, 1.5, WN.noise(x, y, 40, 305))
    crack = (1 - smoothstep(0.015, 0.045, cn)) * cmask * conc
    out *= (1 - 0.45 * crack)[..., None]
    # fresh breaks (concrete / box) and torn metal (panels, cladding)
    brk = np.clip(r.field('broken') * 1.5, 0, 1)
    brk = brk * np.where(np.isin(comp, [Y.PAD, Y.KERB, Y.BOX]) | (r.nz > 0.45), 1.0, 0.0)   # breaks show on tops
    fresh = FRESH * np.clip(0.84 + 0.1 * WN.noise(x, y + z, 1.5, 306), 0.6, 1.0)[..., None]
    out = out * (1 - brk[..., None]) + fresh * brk[..., None]
    tr = np.clip(r.field('tear') * 1.4, 0, 1)
    torn = np.where((WN.noise(x, y + z, 2, 307) > 0.3)[..., None], RUST * g1, BARE * g1)
    out = out * (1 - tr[..., None]) + torn * tr[..., None]
    # the sides of holes torn in the east part: the dark inside below the cladding's thickness
    void = r.field('void') > 0.5
    zo = Y.roof_z(x, p)
    side = void & (r.nz < 0.6) & (z < zo - 2.5) & ~np.isin(comp, [DEBRIS])
    out = np.where(side[..., None], np.array([46, 45, 43.]) * g1, out)
    # the cracked coping: a rough grey rubble texture over the brown-grey
    rb = (r.field('rubbly') > 0.5) & (comp == Y.BOX) & (r.nz > 0.45)
    rt = np.clip(0.5 + 0.5 * WN.noise(x, y, 1.6, 310), 0, 1)
    rcol = np.array([150, 146, 136.]) * (0.62 + 0.45 * rt)[..., None]
    out = np.where(rb[..., None], out * 0.35 + rcol * 0.65, out)
    # bent cladding round the tears: darker, dirtier green
    bent = (r.field('bent') > 0.5) & (comp == Y.ROOF)
    out = np.where(bent[..., None], out * (0.62 + 0.25 * np.clip(WN.noise(x, y, 3, 309), -1, 1))[..., None], out)
    g0, g1_ = p['box']['glass']
    panes = (r.field('panes') > 0.5) & (comp == Y.BOX) & (r.nx > 0.5) & (z > g0 + 1) & (z < g1_ - 1)
    shard = np.clip(WN.noise(x, y + 2 * z, 2.0, 311), 0, 1) * 0.5
    out = np.where(panes[..., None], np.array([16, 18, 18.]) * g1 + np.array([60, 70, 66.]) * shard[..., None], out)
    # rubble
    rock = r.field('rock')
    deb = comp == DEBRIS
    out = np.where(deb[..., None], rock * (1 + 1.5 * grain)[..., None], out)
    inside_zone = (x < p['x_open']) & (y < p['yS']) & (y > p['yN']) & (x > p['xw'] + 6)
    out = np.where((deb & inside_zone)[..., None], out * 0.55, out)
    # the hangar's insides where the roof is gone
    ins = comp == Y.INSIDE
    out = np.where(ins[..., None], np.array([44, 42, 40.]) * g1, out)
    # lamps out
    out = np.where(np.isin(comp, [Y.LAMP, Y.DLAMP])[..., None], np.array([70, 52, 34.]) * g1, out)
    # fans: level 1 the north one wrecked, the middle one missing blades; level 2 all dark
    hub = comp == Y.FANHUB
    for j, fy in enumerate(p['fans_y']):
        d = np.hypot(x - p['fan_x'], y - fy)
        mine = hub & (d <= p['fan_r'] + 1)
        if j >= 1:                                       # TS: the middle and north fans wrecked
            ang = np.mod(np.arctan2(y - fy, x - p['fan_x']), 2 * np.pi)
            gone = ((ang > 0.9) & (ang < 4.4) & (d > 3.5)) if j == 1 else (d >= 0)
            out = np.where((mine & gone)[..., None], np.array([30, 30, 32.]) * g1, out)
    return out
