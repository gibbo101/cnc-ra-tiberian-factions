"""
Damage for the Tiberium Refinery (TS NTREFN frame 1; RA has healthy and damaged only), as TS breaks it:
  columns  the flanged column snapped above its upper collar, the tall one snapped two thirds of the way down, its
           pipe gone (a short stub left), the upper link gone with them
  sphere   a hole torn in its top towards the north-east (the dark inside showing); its white cap knocked off and
           lying on the skirt in front of it
  skirt    the front panels south-west of the dock stove in (a crumpled hole, the dark inside), the rib between
           them broken and bent
  deck     cracked from the flanged column out to the front, its rim broken over the stove-in panels, rubble on it
  ground   soot and scorch, rubble round the foot (steel, house-green bits of the broken rib, concrete)
  bib      (NTREFNBB frame 1) cracks across it, a hole knocked out of its east end, its south-west corner broken
"""
import numpy as np
import hd, proc as PR, wnoise as WN
from walls2 import smoothstep
from pdamage import blob

DEBRIS = 40
SOOT = np.array([30, 29, 28.])
FRESH = np.array([170, 168, 164.])
DUST = np.array([120, 110, 92.])
INSIDE = np.array([30, 30, 34.])
ROCK = {'steel': np.array([120, 121, 128.]), 'green': np.array([0, 214, 0.]) * 0.8, 'deck': np.array([52, 52, 54.]),
        'conc': np.array([214, 208, 190.]) * 0.84, 'copper': np.array([132, 74, 58.])}

MID_CUT = 146.0              # the flanged column's broken top
TALL_CUT = 132.0             # the tall column's
TPIPE_STUB = 104.0
SPHERE_HOLE = (0.62, -0.55, 0.62, 0.42)      # the hole's direction from the sphere's centre (x, y, z), its size
CAP_FALLEN = (5.0, -88.0, 0.35)             # where the cap lies, its tilt (radians)
STOVE = (100.0, 132.0, 36.0, 30.0)           # the stove-in skirt: azimuth (deg), radius, half-widths (deg, units)
BROKEN_RIB = 103.1
BROKEN_RIBS = (80.6, 103.1, 125.6)


class ProcChunks:
    """angular rubble chunks at fixed local positions (seeded: every view gets the same ones)."""
    def __init__(self, seed):
        self.rng = np.random.default_rng(seed)
        self.items = []

    def scatter(self, n, centre, rad, sizes, kinds, weights=None, avoid=()):
        cx0, cy0 = centre
        k = 0
        tries = 0
        while k < n and tries < 400:
            tries += 1
            a = self.rng.uniform(0, 2 * np.pi); rr_ = self.rng.uniform(*rad)
            cx, cy = cx0 + rr_ * np.cos(a), cy0 + rr_ * np.sin(a)
            if any(np.hypot(cx - ax, cy - ay) < ar for (ax, ay, ar) in avoid):
                continue
            if abs(cx) > 280 or abs(cy) > 210:
                continue
            k += 1
            rr = self.rng.uniform(*sizes)
            kind = kinds[self.rng.choice(len(kinds), p=weights)]
            nf = int(self.rng.integers(5, 8))
            ang = np.sort(self.rng.uniform(0, 2 * np.pi, nf))
            dk = rr * self.rng.uniform(0.7, 1.1, nf)
            topz = rr * self.rng.uniform(0.5, 0.85)
            tilt = self.rng.normal(0, 0.18, 2)
            steep = self.rng.uniform(1.3, 2.4)
            shade = self.rng.uniform(0.9, 1.08)
            self.items.append((cx, cy, rr, kind, ang, dk, topz, tilt, steep, shade))

    def apply(self, x, y, H, C, rock, base=None):
        for (cx, cy, rr, kind, ang, dk, topz, tilt, steep, shade) in self.items:
            win = (np.abs(x - cx) < 2 * rr + 2) & (np.abs(y - cy) < 2 * rr + 2)
            if not win.any():
                continue
            ddx, ddy = x[win] - cx, y[win] - cy
            g = np.max([np.cos(a) * ddx + np.sin(a) * ddy - d for a, d in zip(ang, dk)], axis=0)
            h = np.clip(-g * steep, 0, None)
            h = np.minimum(h, np.clip(topz + tilt[0] * ddx + tilt[1] * ddy, 0.4, None)) * (g < 0)
            b0 = H[win] if base is None else base[win]
            hh = np.where(h > 0, h + b0, 0)
            full = np.zeros_like(H); full[win] = hh
            m = full > H
            H[m] = full[m]; C[m] = DEBRIS
            rock[m] = ROCK[kind] * shade
        return H, C, rock


def model(level, p=None):
    def f(X, Yy, **kw):
        lay = kw.get('layout', 'ts')
        q = PR.params(lay, p)
        if kw.get('pad'):
            sc = PR.scene(X, Yy, p=p, **kw)
            return damage_pad(sc, X, Yy, level, q, lay)
        kw = dict(kw); kw['merge'] = False
        sc = PR.scene(X, Yy, p=p, **kw)
        return PR.merge_slabs(damage_scene(sc, X, Yy, level, q, lay))
    return f


def damage_scene(sc, X, Yy, level, p=PR.P, layout='ts'):
    if level < 1:
        return sc
    x, y = PR.to_local(X, Yy, layout)
    H = sc.H.copy(); C = sc.C.copy()
    soot = np.zeros_like(H); broken = np.zeros_like(H)
    rock = np.zeros(H.shape + (3,), np.float32)
    jag = WN.noise(x, y, 2.4, 811)
    cx, cy = p['c']
    dx, dy = x - cx, y - cy
    r = np.hypot(dx, dy)
    phi = np.degrees(np.arctan2(dy, dx)) % 360.0
    # ---- the columns snapped, the tall one's pipe gone but a stub, the upper link gone
    lift = PR.LAYOUTS[layout]['lift']
    m_ = p['mid']
    midcol = (r <= m_['r'] + 0.5) & np.isin(C, [PR.COLUMN, PR.HOLE])
    cut = MID_CUT + lift + 3.0 * jag
    H = np.where(midcol & (H > cut), cut, H)
    hollow = midcol & (r <= m_['r'] - PR.RIM_W)              # broken open: the pipe's dark inside shows
    H = np.where(hollow, np.minimum(H, cut - PR.HOLE_D), H); C = np.where(hollow, PR.HOLE, C)
    t_ = p['tall']
    tr = np.hypot(x - t_['c'][0], y - t_['c'][1])
    tallcol = (tr <= t_['r'] + 0.5) & np.isin(C, [PR.COLUMN, PR.HOLE])
    cut2 = TALL_CUT + lift + 3.0 * jag
    H = np.where(tallcol & (H > cut2), cut2, H)
    hollow = tallcol & (tr <= t_['r'] - PR.RIM_W)
    H = np.where(hollow, np.minimum(H, cut2 - PR.HOLE_D), H); C = np.where(hollow, PR.HOLE, C)
    tp = p['tpipe']
    tpr = np.hypot(x - tp['c'][0], y - tp['c'][1])
    pipe = (tpr <= tp['r'] + 0.5) & (C == PR.PIPE)
    H = np.where(pipe & (H > TPIPE_STUB + lift), TPIPE_STUB + lift + 4.0 * jag, H)
    keep = []
    for s in sc.slabs:
        if s.name in ('tarm',):
            continue
        if s.name == 'link':
            if np.nanmax(np.where(s.top >= 0, s.top, -1)) > 140 + lift:
                continue
        if s.name == 'mcollar':
            if np.nanmax(np.where(s.top >= 0, s.top, -1)) > MID_CUT + lift:
                continue
        keep.append(s)
    sc.slabs = keep
    soot = np.maximum(soot, 0.55 * np.exp(-(r ** 2) / 22.0 ** 2) * (H > MID_CUT + lift - 30))
    soot = np.maximum(soot, 0.5 * np.exp(-(tr ** 2) / 20.0 ** 2) * (H > TALL_CUT + lift - 26))
    # ---- the sphere: a hole torn in its top towards the north-east, the cap knocked off and lying in front
    sph = p['sphere']
    qx, qy, qz = sph['c']
    hdx, hdy, hdz, hsz = SPHERE_HOLE
    hn = np.array([hdx, hdy, hdz]); hn /= np.linalg.norm(hn)
    for s in sc.slabs:
        if s.name == 'sphere':
            ok = s.top >= 0
            ddx, ddy, ddz = x - qx, y - qy, s.top - qz
            dn = (ddx * hn[0] + ddy * hn[1] + ddz * hn[2]) / sph['r']
            e = (1 - dn) / hsz + 0.35 * WN.noise(x, y, 6.0, 812)
            hole = ok & (e < 1.0)
            # through the hole: the sphere's far inside (dark), drawn as the shell's lower surface
            s.top = np.where(hole, s.bot + 2.0 + 0.6 * (qz - s.bot) * 0.0, s.top)
            s.comp = np.where(hole, DEBRIS + 1, s.comp).astype(np.int16)
            broken = np.maximum(broken, (ok & (e >= 1.0) & (e < 1.25)) * 0.9)
        if s.name == 'cap':
            s.top = np.full_like(s.top, -1.0)
    soot = np.maximum(soot, 0.7 * np.exp(-((x - qx - 18) ** 2 + (y - qy + 16) ** 2) / 34.0 ** 2))
    # the cap lying tilted on the skirt
    fx, fy, ftilt = CAP_FALLEN
    capr, caph = sph['cap']
    u = (x - fx) * np.cos(0.6) + (y - fy) * np.sin(0.6)
    v = -(x - fx) * np.sin(0.6) + (y - fy) * np.cos(0.6)
    lying = (np.abs(u) <= caph * 1.1) & (np.abs(v) <= capr)          # on its side: a short drum seen side-on
    drum = np.sqrt(np.clip(capr ** 2 - v ** 2, 0, None))
    base_z = PR.skirt_z(np.hypot(fx - cx, fy - cy), p)
    H = np.where(lying, np.maximum(H, base_z + drum * 0.9 + 0.3 * u * np.tan(ftilt)), H)
    C = np.where(lying, DEBRIS + 2, C)
    # ---- the skirt stove in south-west of the dock: panels dented, holes torn through them (dark inside, bright
    #      torn edges), the ribs over them broken into pieces with gaps, one piece lying across the panel below
    az, rad, haz, hr = STOVE
    da = ((phi - az + 180.0) % 360.0) - 180.0
    e2 = np.sqrt((da / haz) ** 2 + ((r - rad) / hr) ** 2) - 1.0 - 0.18 * WN.noise(x, y, 14.0, 813)
    sk = np.isin(C, [PR.SKIRT, PR.RIB]) & (r > p['deck_r'] + 2)
    region = sk & (e2 < 0.0)
    dent = 7.0 * np.clip(-e2 * 2.0, 0, 1) * (0.6 + 0.4 * WN.noise(x, y, 18.0, 814))
    H = np.where(region, H - dent, H)
    tear = WN.noise(x, y, 11.0, 815) + 0.9 * np.clip(-e2, 0, 1)
    hole = (C == PR.SKIRT) & region & (tear > 0.72)
    H = np.where(hole, np.maximum(H * 0.2, 2.0), H)
    C = np.where(hole, DEBRIS + 1, C)
    edge_t = (C == PR.SKIRT) & region & (tear > 0.45) & ~hole
    broken = np.maximum(broken, edge_t * 0.9)
    soot = np.maximum(soot, 0.5 * np.clip(0.3 - e2, 0, 1))
    for k_, br in enumerate(BROKEN_RIBS):
        db = ((phi - br + 180.0) % 360.0) - 180.0
        rl = (C == PR.RIB) & (np.abs(db) < 4.5) & (e2 < 0.15)
        gap = rl & (np.sin(r * 0.11 + k_ * 1.9) + 0.4 * WN.noise(x, y, 9.0, 816 + k_) > 0.35)
        H = np.where(gap, np.maximum(PR.skirt_z(r, p) - dent, 0.0), H)
        C = np.where(gap, np.where(hole, DEBRIS + 1, PR.SKIRT), C)
    bx_, by_ = cx + (rad + 34) * np.cos(np.radians(BROKEN_RIB + 7)), cy + (rad + 34) * np.sin(np.radians(BROKEN_RIB + 7))
    pu = (x - bx_) * np.cos(np.radians(BROKEN_RIB - 35)) + (y - by_) * np.sin(np.radians(BROKEN_RIB - 35))
    pv = -(x - bx_) * np.sin(np.radians(BROKEN_RIB - 35)) + (y - by_) * np.cos(np.radians(BROKEN_RIB - 35))
    piece = (np.abs(pu) < 20.0) & (np.abs(pv) < p['rib_w'] / 2 + 0.5)
    H = np.where(piece, np.maximum(H, PR.skirt_z(np.hypot(x - cx, y - cy), p) + 2.5 + 1.2 * np.sin(pu * 0.15)), H)
    C = np.where(piece, DEBRIS + 3, C)
    # ---- the deck: its rim broken over the stove-in panels, a crack from the column to the front, rubble
    rim_gone = np.isin(C, [PR.RIM]) & (np.abs(((phi - (az + 6) + 180) % 360) - 180) < 14.0 + 6.0 * jag)
    for s in sc.slabs:
        if s.name == 'deck':
            rg = (s.top >= 0) & (np.abs(((phi - (az + 6) + 180) % 360) - 180) < 13.0 + 6.0 * jag) & \
                 (r > p['deck_r'] - 9.0 - 6.0 * np.abs(jag))
            s.top = np.where(rg, s.top - 6.0, s.top)
            s.comp = np.where(rg, DEBRIS + 4, s.comp).astype(np.int16)
            broken = np.maximum(broken, rg * 0.7)
    soot = np.maximum(soot, 0.75 * np.exp(-((phi - az) / 25.0) ** 2) * (r < p['deck_r']) * np.clip(r / 80.0, 0, 1))
    # ---- soot on the skirt and stack, scorch on the ground round the foot
    for (sx, sy, rr) in ((-60.0, 120.0, 30.0), (-170.0, 90.0, 34.0)):
        soot = np.maximum(soot, 0.6 * np.exp(-((x - sx) ** 2 + (y - sy) ** 2) / rr ** 2))
    # ---- rubble: steel, green bits of the rib, deck, round the stove-in panels and the dock's mouth
    chunks = ProcChunks(820)
    bxa, bya = cx + (p['foot_r'] + 10) * np.cos(np.radians(az)), cy + (p['foot_r'] + 10) * np.sin(np.radians(az))
    chunks.scatter(10, (bxa, bya), (2, 34), (2.6, 6.0), ['steel', 'green', 'deck'], [0.55, 0.2, 0.25], [])
    chunks.scatter(6, (cx + 120, cy + 120), (0, 30), (2.2, 4.6), ['steel', 'conc'], [0.6, 0.4], [])
    floor = np.zeros_like(H)
    H, C, rock = chunks.apply(x, y, H, C, rock, base=floor)
    sc.H, sc.C = H.astype(np.float32), C.astype(np.int16)
    sc.extra.update(soot=soot.astype(np.float32), broken=broken.astype(np.float32), rock=rock)
    return sc


def damage_pad(sc, X, Yy, level, p=PR.P, layout='ts'):
    """NTREFNBB frame 1: cracks, a hole knocked out of its east end, its south-west corner broken."""
    if level < 1:
        return sc
    x, y = PR.to_local(X, Yy, layout)
    H = sc.H.copy(); C = sc.C.copy()
    e = blob(x, y, 236.0, -16.0, 30.0, 22.0, 0.45, 831, feat=5.0)
    hole = (e < 0) & (H > 0)
    H = np.where(hole, 0.0, H); C = np.where(hole, 0, C)
    e2 = blob(x, y, 10.0, 192.0, 34.0, 20.0, 0.5, 832, feat=5.0)
    corner = (e2 < 0) & (H > 0)
    H = np.where(corner, 0.0, H); C = np.where(corner, 0, C)
    broken = (((e >= 0) & (e < 0.35)) | ((e2 >= 0) & (e2 < 0.3))) & (H > 0)
    rock = np.zeros(H.shape + (3,), np.float32)
    chunks = ProcChunks(840)
    chunks.scatter(7, (236.0, -16.0), (0, 30), (2.4, 5.2), ['conc'], [1.0], [])
    chunks.scatter(4, (14.0, 186.0), (0, 22), (2.2, 4.4), ['conc'], [1.0], [])
    H, C, rock = chunks.apply(x, y, H, C, rock, base=np.zeros_like(H))
    sc.H, sc.C = H.astype(np.float32), C.astype(np.int16)
    sc.extra.update(broken=broken.astype(np.float32), rock=rock,
                    soot=(0.7 * np.exp(-((x - 236) ** 2 + (y + 16) ** 2) / 46.0 ** 2)).astype(np.float32))
    return sc


def mats(r, alb, level, p=None):
    if level < 1:
        return alb
    p = PR.params(r.mk.get('layout', 'ts'), p)
    x, y = PR.to_local(r.x, r.y, r.mk.get('layout', 'ts'))
    z, comp = r.z, r.comp
    top = r.nz > 0.75
    out = alb.copy()
    grain = WN.noise(x, y + z, 1.2, 851) * 0.05
    g1 = (1 + grain)[..., None]
    house = np.isin(comp, list(PR.HOUSE))
    pad = np.isin(comp, [PR.PAD, PR.STRIPE])
    dust = smoothstep(0.3, 1.3, WN.noise(x, y, 14, 852)) * np.where(top, 0.35, 0.18) * ~house
    out = out * (1 - dust[..., None]) + DUST * g1 * dust[..., None]
    s = r.field('soot')
    soot = smoothstep(0.15, 0.7, np.clip(s * (0.65 + 0.35 * WN.noise(x, y + z, 6, 853)), 0, 1)) * 0.85
    soot = soot * np.where(house, 0.45, 1.0)
    out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
    # cracks across the skirt, the deck and the bib
    cz = np.isin(comp, [PR.SKIRT, PR.DECK, PR.PAD, PR.STRIPE, PR.CONE])
    cn = WN.ridge(x + 0.4 * z, y - 0.6 * z, 7, 854) + 0.12 * np.abs(WN.noise(x, y + z, 1.5, 855))
    cmask = smoothstep(0.4, 1.1, WN.noise(x, y, 26, 856)) + 0.5 * pad
    crack = (1 - smoothstep(0.015, 0.06, cn)) * np.clip(cmask, 0, 1) * cz
    out *= (1 - 0.6 * crack)[..., None]
    brk = np.clip(r.field('broken') * 1.4, 0, 1) * ~house
    out = out * (1 - brk[..., None]) + FRESH * 0.75 * brk[..., None]
    ins = comp == DEBRIS + 1
    out = np.where(ins[..., None], INSIDE * (0.8 + 0.3 * WN.noise(x, y, 2.0, 857))[..., None] * g1, out)
    cap = comp == DEBRIS + 2
    out = np.where(cap[..., None], np.array([206, 206, 202.]) * g1, out)
    rib = comp == DEBRIS + 3
    out = np.where(rib[..., None], np.array([0, 214, 0.]) * 0.85 * g1, out)
    rim = comp == DEBRIS + 4
    out = np.where(rim[..., None], np.array([60, 60, 62.]) * g1, out)
    rock = r.field('rock')
    out = np.where((comp == DEBRIS)[..., None], rock * (1 + 1.5 * grain)[..., None], out)
    # the docked harvester and its tank are a unit, not the building: no damage on them
    out = np.where((comp >= PR.LID_BASE)[..., None], alb, out)
    return out
