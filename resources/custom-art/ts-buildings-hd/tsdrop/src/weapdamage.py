"""
Damage for the War Factory (TS GTWEAP frame 1; RA has healthy and damaged only), as TS breaks it:
  panel    a hole torn in the green slope's middle (its skin gone, the light inside frame showing, torn green edges
           bent in), soot round it, bits of it fallen at its foot
  west     the green block dented all over, a scorched hole punched in its south face at the west end, soot on the
           brown machinery below it
  unit     the green unit on the south fender crumpled (its top pushed in at the front and dented, its edges torn,
           sagging off its bracket; its red band crushed out of sight), scorched
  roof     scorch patches on the machinery and the deck, a housing burnt out
  door     untouched, as TS's (GTWEAP 1 leaves the door and the north fender as they are)
  fenders  soot and a chip knocked out of the south one's foot
  bib      (GTWEAPBB frame 1) cracks all over it, its south and east edges broken away in bites, the hazard stripes worn
Greys and browns only; placed in the building's own frame so both views match.
"""
import numpy as np
import hd, weap as M, wnoise as WN
from walls2 import smoothstep
from pdamage import blob

DEBRIS = 40
SOOT = np.array([30, 29, 28.])
FRESH = np.array([196, 196, 200.])
DUST = np.array([120, 110, 92.])
INSIDE_L = np.array([178, 174, 192.])          # TS: the light lilac-grey inside of the torn panel
IN_GREY = np.array([164, 164, 168.])           # its lit upper right (TS: neutral light grey)
IN_LILAC = np.array([120, 112, 144.])          # its lower left (TS: lilac-grey)
INSIDE_D = np.array([44, 42, 50.])
ROCK = {'steel': np.array([110, 111, 118.]), 'green': np.array([0, 214, 0.]) * 0.8, 'tan': np.array([168, 148, 106.]) * 0.85,
        'conc': np.array([206, 202, 184.]) * 0.84, 'rust': np.array([142, 70, 48.])}

PANEL_HOLE = (-100.0, 150.0, 30.0, 17.0)        # centre x, y (local), half sizes x, y
WEST_HOLE = (-238.0, 104.0, 82.0, 12.0, 7.0)     # at the west block's south-west end, where its rounded top meets its
                                                 # south face (TS's dark hole there): x, y, z, half sizes x, y
UNIT_CRUSH = 14.0


class Chunks:
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
        q = M.P if p is None else p
        if kw.get('pad'):
            sc = M.scene(X, Yy, p=p, **kw)
            return damage_pad(sc, X, Yy, level, q, lay)
        kw = dict(kw); kw['merge'] = False
        sc = M.scene(X, Yy, p=p, **kw)
        return M.merge_slabs(damage_scene(sc, X, Yy, level, q, lay))
    return f


def damage_scene(sc, X, Yy, level, p=M.P, layout='ts'):
    if level < 1:
        return sc
    x, y = M.to_local(X, Yy, layout)
    H = sc.H.copy(); C = sc.C.copy()
    soot = np.zeros_like(H); broken = np.zeros_like(H)
    rock = np.zeros(H.shape + (3,), np.float32)
    # ---- the panel: its skin torn open in the middle, the light frame inside showing (sunk 14 behind the skin),
    #      a ring of torn edge round it
    hx, hy, hrx, hry = PANEL_HOLE
    e = blob(x, y, hx, hy, hrx, hry, 0.18, 901, feat=12.0)
    onpanel = np.isin(C, [M.PANEL, M.FRAME]) & (y > p['hall']['y'][1] + 2) & (H > 4)
    hole = onpanel & (e < 0)
    pn = p['panel']
    zp = pn['s'] * (pn['y0'] - y)
    H = np.where(hole, np.maximum(zp - 7.0, 0.0), H)
    C = np.where(hole, DEBRIS + 1, C)
    torn = onpanel & (e >= 0) & (e < 0.12)
    broken = np.maximum(broken, torn * 0.8)
    soot = np.maximum(soot, 0.65 * np.clip(0.9 - e, 0, 1) * onpanel)
    if M.LAYOUTS[layout].get('sym', False):
        # RA round 2: the twin slope (mirrored on the east) gets soot only: TS's hole stays in the west one
        ty = 2 * M.YC - hy
        twin = (y < 2 * M.YC - p['hall']['y'][1] - 2)
        soot = np.maximum(soot, twin * (0.55 * np.exp(-((x - hx - 14.0) ** 2 / 46.0 ** 2 + (y - ty + 8.0) ** 2 / 30.0 ** 2))
                                        + 0.35 * np.exp(-((x + 150.0) ** 2 + (y - ty - 30.0) ** 2) / 26.0 ** 2)))
        # its fender's foot and the slope's sill sooted like the west side's (no chip: that one is TS's)
        soot = np.maximum(soot, 0.45 * np.exp(-((x - 0.0) ** 2 + (y + 87.0) ** 2) / 30.0 ** 2))
        soot = np.maximum(soot, 0.4 * np.exp(-((x + 70.0) ** 2 / 40.0 ** 2 + (y + 186.0) ** 2 / 14.0 ** 2)))
    # ---- the west block: dented all over (TS's damaged block is lumpy), a scorched hole in its south face (mats)
    wx, wy, wz, ww, wh = WEST_HOLE
    wg = C == M.WESTG
    H = np.where(wg, H + 3.5 * WN.noise(x, y, 16.0, 902) - 1.5, H)
    ew = blob(x, y, wx, wy, ww, wh, 0.3, 907, feat=5.0)
    wb = wg & (ew < 0)
    H = np.where(wb, H - 12.0 * np.clip(-ew * 3, 0, 1), H); C = np.where(wb, DEBRIS + 4, C)
    soot = np.maximum(soot, 0.7 * np.exp(-((x - wx) ** 2 + (y - wy + 8.0) ** 2) / 30.0 ** 2))
    # ---- the green unit crumpled: its top pushed down at the front, dented, scorched
    gb = p['gblock']
    # RA round 2: the unit's mirrored twin on the east fender is dented and sooted, not crushed (TS's crush stays west)
    gsym = M.LAYOUTS[layout].get('sym', False)
    yg = np.where(y < M.YC, 2 * M.YC - y, y) if gsym else y
    gtwin = (y < M.YC) if gsym else np.zeros(y.shape, bool)
    u_ = ((x - gb['c'][0]) + (yg - gb['c'][1])) / np.sqrt(2)
    v_ = ((x - gb['c'][0]) - (yg - gb['c'][1])) / np.sqrt(2)
    front = np.clip((u_ + gb['d'] / 2) / gb['d'], 0, 1)
    lump = WN.noise(x, y, 7.0, 905)
    prox = np.maximum(np.abs(u_) / (gb['d'] / 2), np.abs(v_) / (gb['w'] / 2))      # 1 at the unit's sides
    rag = (prox > 0.93 + 0.05 * WN.noise(x, y, 6.0, 906))                           # its edges torn a little
    push = UNIT_CRUSH * front * (0.8 + 0.2 * np.clip(v_ / 30.0, -1, 1))
    dent = 3.0 * (0.5 + 0.5 * lump) + 12.0 * smoothstep(0.4, 1.0, prox) ** 1.5
    for s in sc.slabs:
        ok = s.top >= 0
        if s.name == 'gblock':
            top = np.where(gtwin, np.maximum(s.top - 0.35 * dent, s.bot + 3.0), np.maximum(s.top - push - dent, s.bot + 3.0))
            bot = np.where(gtwin, s.bot, np.maximum(s.bot - 6.0 * front, 0.0))
            keep = ok & (gtwin | ~rag)
            s.top = np.where(keep, top, -1.0)
            s.bot = np.where(keep, bot, s.bot)
        elif s.name == 'gtop':                       # the small box on top rides down with the crushed top
            drop = np.where(gtwin, 0.35 * dent, push + dent)
            s.top = np.where(ok, s.top - drop - 2.0 * lump * ~gtwin, s.top)
            s.bot = np.where(ok, np.maximum(s.bot - drop - np.where(gtwin, 0.0, 5.0), 0.0), s.bot)
    sc.extra['nostripe'] = np.where(gtwin, 0.0, 1.0).astype(np.float32)    # the twin keeps its red band
    soot = np.maximum(soot, 0.6 * np.exp(-((x - gb['c'][0]) ** 2 + (y - gb['c'][1]) ** 2) / 38.0 ** 2))
    if gsym:
        soot = np.maximum(soot, 0.4 * np.exp(-((x - gb['c'][0] - 6.0) ** 2 + (y - (2 * M.YC - gb['c'][1]) + 4.0) ** 2) / 26.0 ** 2))
    # ---- the roof: scorch patches, a burnt-out housing (sunk, dark); the door's lower half sooted
    htop = H.copy()                                  # the roof's top, slabs included (the roof over the bay is slabs)
    for s_ in sc.slabs:
        htop = np.maximum(htop, np.where(s_.top >= 0, s_.top, 0.0))
    scorch = np.zeros_like(H)                       # TS's damaged roof: black scorch blobs (a few TS px each)
    for (sx, sy, rr) in ((-128.0, 60.0, 22.0), (-200.0, -40.0, 20.0), (-96.0, -84.0, 18.0), (-170.0, 20.0, 15.0),
                         (-84.0, 18.0, 16.0), (-150.0, -50.0, 14.0), (-122.0, -44.0, 15.0)):
        scorch = np.maximum(scorch, np.exp(-((x - sx) ** 2 + (y - sy) ** 2) / rr ** 2) * (htop > 90))
    burnt = (C == M.MACH) & (np.hypot(x + 96.0, y + 84.0) < 14.0)
    H = np.where(burnt, H - 6.0, H); C = np.where(burnt, DEBRIS + 2, C)
    sc.extra['door_soot'] = np.clip((60.0 - 0.0) / 60.0, 0, 1) * np.ones_like(H, np.float32)
    # ---- the south fender: a chip out of its foot
    j = p['jamb']
    ec = blob(x, y, j['xb'] + j['A'] - 4.0, 96.0, 12.0, 9.0, 0.35, 904, feat=5.0)
    chip = (C == M.JAMB) & (ec < 0)
    H = np.where(chip, H * 0.55, H); C = np.where(chip, DEBRIS + 3, C)
    broken = np.maximum(broken, ((C == M.JAMB) & (ec >= 0) & (ec < 0.3)) * 0.7)
    soot = np.maximum(soot, 0.5 * np.exp(-((x - 0.0) ** 2 + (y - 90.0) ** 2) / 30.0 ** 2))
    # ---- rubble: panel bits (green, steel) at the slope's foot, steel and tan bits by the unit and the fender
    chunks = Chunks(910)
    chunks.scatter(7, (hx + 6, pn['y0'] + 10), (0, 22), (2.4, 5.4), ['steel', 'green', 'tan'], [0.45, 0.35, 0.2], [])
    chunks.scatter(5, (8.0, 120.0), (0, 18), (2.2, 4.6), ['steel', 'tan', 'rust'], [0.4, 0.3, 0.3], [])
    floor = np.zeros_like(H)
    H, C, rock = chunks.apply(x, y, H, C, rock, base=floor)
    sc.H, sc.C = H.astype(np.float32), C.astype(np.int16)
    sc.extra.update(soot=soot.astype(np.float32), broken=broken.astype(np.float32), rock=rock,
                    scorch=scorch.astype(np.float32))
    return sc


def damage_pad(sc, X, Yy, level, p=M.P, layout='ts'):
    """GTWEAPBB frame 1: cracks all over, its south and east edges broken away in bites."""
    if level < 1:
        return sc
    x, y = M.to_local(X, Yy, layout)
    if M.LAYOUTS[layout].get('sym', False):
        y = np.where(y < M.YC, 2 * M.YC - y, y)          # RA round 2: the apron's west half mirrored, its damage too
    H = sc.H.copy(); C = sc.C.copy()
    gone = np.zeros(H.shape, bool); near = np.zeros(H.shape, bool)
    for i, (bx_, by_, rx, ry) in enumerate(((60.0, 196.0, 30.0, 16.0), (150.0, 190.0, 22.0, 18.0), (212.0, 128.0, 20.0, 22.0),
                                            (258.0, 30.0, 14.0, 26.0), (-40.0, 186.0, 18.0, 14.0), (200.0, -120.0, 18.0, 16.0))):
        e = blob(x, y, bx_, by_, rx, ry, 0.45, 921 + i, feat=5.0)
        gone |= (e < 0) & (H > 0)
        near |= (e >= 0) & (e < 0.35) & (H > 0)
    H = np.where(gone, 0.0, H); C = np.where(gone, 0, C)
    rock = np.zeros(H.shape + (3,), np.float32)
    chunks = Chunks(930)
    chunks.scatter(5, (60.0, 196.0), (4, 30), (2.2, 4.8), ['conc'], [1.0], [])
    chunks.scatter(4, (212.0, 128.0), (4, 24), (2.2, 4.4), ['conc'], [1.0], [])
    H, C, rock = chunks.apply(x, y, H, C, rock, base=np.zeros_like(H))
    sc.H, sc.C = H.astype(np.float32), C.astype(np.int16)
    sc.extra.update(broken=near.astype(np.float32), rock=rock,
                    soot=(0.45 * np.exp(-((x - 60) ** 2 + (y - 40) ** 2) / 60.0 ** 2)).astype(np.float32))
    return sc


def mix_(a, b, t):
    return a * (1 - t) + b * t


def mats(r, alb, level, p=None):
    if level < 1:
        return alb
    p = M.P if p is None else p
    lay = r.mk.get('layout', 'ts')
    x, y = M.to_local(r.x, r.y, lay)
    z, comp = r.z, r.comp
    if M.LAYOUTS[lay].get('sym', False):
        # RA round 2: on the apron (and its rubble) the west half's damage mirrored onto the east half
        onpad = np.isin(comp, [M.PAD, M.CHEV, DEBRIS]) & (z < 12.0) & (x > -60.0)
        y = np.where(onpad & (y < M.YC), 2 * M.YC - y, y)
    top = r.nz > 0.75
    out = alb.copy()
    grain = WN.noise(x, y + z, 1.2, 951) * 0.05
    g1 = (1 + grain)[..., None]
    house = np.isin(comp, list(M.HOUSE))
    pad = np.isin(comp, [M.PAD, M.CHEV])
    dust = smoothstep(0.3, 1.3, WN.noise(x, y, 14, 952)) * np.where(top, 0.35, 0.18) * ~house
    out = out * (1 - dust[..., None]) + DUST * g1 * dust[..., None]
    s = r.field('soot')
    soot = smoothstep(0.15, 0.7, np.clip(s * (0.65 + 0.35 * WN.noise(x, y + z, 6, 953)), 0, 1)) * 0.85
    # the door stays as it is (TS leaves it untouched)
    soot = soot * np.where(house, 0.22, 1.0) * (comp != M.DOOR)
    out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
    # the roof's scorch blobs: near black, ragged edged
    sc_ = r.field('scorch')
    scb = smoothstep(0.3, 0.6, sc_ * (0.85 + 0.3 * WN.noise(x, y + z, 5, 962))) * 0.88 * np.where(house, 0.3, 1.0)
    out = out * (1 - scb[..., None]) + SOOT * scb[..., None]
    # cracks across the bib, the deck, the fenders and the hall
    cz = np.isin(comp, [M.PAD, M.CHEV, M.HALL, M.JAMB, M.ROOF, M.SILL])
    cn = WN.ridge(x + 0.4 * z, y - 0.6 * z, 7, 955) + 0.12 * np.abs(WN.noise(x, y + z, 1.5, 956))
    cmask = smoothstep(0.4, 1.1, WN.noise(x, y, 26, 957)) + 1.0 * pad
    crack = (1 - smoothstep(0.015, 0.06, cn)) * np.clip(cmask, 0, 1) * cz
    out *= (1 - np.where(pad, 0.75, 0.6) * crack)[..., None]
    brk = np.clip(r.field('broken') * 1.4, 0, 1) * ~house
    out = out * (1 - brk[..., None]) + FRESH * 0.75 * brk[..., None]
    # torn green edges stay green (bent skin), a little darker
    tgreen = np.clip(r.field('broken'), 0, 1) * (comp == M.PANEL)
    out = np.where((tgreen > 0.3)[..., None], np.array([0, 214, 0.]) * 0.82 * g1, out)
    # the panel's inside: a light lilac-grey frame (ribs across it), dark gaps
    ins = comp == DEBRIS + 1
    hx, hy, hrx, hry = PANEL_HOLE
    nbox = (np.abs(x - hx) < hrx * 1.5) & (np.abs(y - hy) < hry * 1.6)
    npan = r.ny * 0.782 + r.nz * 0.623 if not M.LAYOUTS[lay]['turn'] else -r.nx * 0.782 + r.nz * 0.623
    wallp = (comp == M.PANEL) & nbox & (npan < 0.85)
    out = np.where(wallp[..., None], IN_LILAC * 0.55 * g1, out)
    # TS: light grey towards the upper right, lilac-grey towards the lower left, a black void in the middle
    tpos = np.clip(0.4 + 0.55 * ((x - hx) / hrx - (y - hy) / hry), 0, 1)
    lit = np.clip(0.88 + 0.22 * WN.noise(x, y + z, 6.0, 960), 0.6, 1.1)
    ic = mix_(IN_LILAC, IN_GREY, tpos[..., None]) * (lit[..., None] * g1)
    void = blob(x, y, hx + 0.6, hy + 6.6, 9.0, 5.5, 0.35, 961, feat=4.0) < 0
    ic = np.where(void[..., None], INSIDE_D * 0.45 * g1, ic)
    out = np.where(ins[..., None], ic, out)
    # the west block's scorched hole, punched in its south face: dark inside, a burnt rim round it
    wx, wy, wz, ww, wh = WEST_HOLE
    out = np.where((comp == DEBRIS + 4)[..., None], INSIDE_D * 0.7 * g1, out)
    dw = np.sqrt(((x - wx) / (ww + 6.0)) ** 2 + ((y - wy) / (wh + 6.0)) ** 2 + ((z - wz) / 16.0) ** 2)
    rim_w = (comp == M.WESTG) & (dw < 1.0 + 0.25 * WN.noise(x, y + z, 4.0, 903))
    out = np.where(rim_w[..., None], mix_(out, SOOT * 1.3 * g1, 0.75), out)
    burnt = comp == DEBRIS + 2
    out = np.where(burnt[..., None], np.array([36, 30, 28.]) * g1, out)
    chip = comp == DEBRIS + 3
    out = np.where(chip[..., None], np.array([150, 136, 104.]) * g1, out)
    rock = r.field('rock')
    out = np.where((comp == DEBRIS)[..., None], rock * (1 + 1.5 * grain)[..., None], out)
    # the hazard stripes worn on the damaged bib
    wear = (comp == M.CHEV) & (WN.noise(x, y, 6.0, 959) > 0.4)
    out = np.where(wear[..., None], out * 0.55 + np.array([140, 132, 110.]) * 0.45, out)
    return out
