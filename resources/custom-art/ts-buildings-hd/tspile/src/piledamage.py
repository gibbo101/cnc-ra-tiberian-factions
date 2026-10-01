"""
Damage for the Barracks (TS GTPILE frame 1; RA has healthy and damaged only).

Mapped from TS's damaged frame (greys and browns only, in world space so both views match):
  roofs     every slab holed: a collapse through the middle of the north-west slab, a hole in the north-east
            one, the south slabs broken open either side of the gap (charred, the dark inside showing)
  masts     the west mast snapped half-way, its top bent over; the east one broken off short
  machinery scorched; the air handler's fan housing blackened
  slopes    two of the east ends' green hatches smashed, soot streaks under the holes, cracks in the blocks
  ground    rubble round the east end and the front, soot on the pad
The flag is torn (GTPILE_C's damaged frames): pile.scene(damaged=True).
"""
import numpy as np
import hd, pile as PL, wnoise as WN
from walls2 import smoothstep
from pdamage import Chunks, blob

DEBRIS = 40
SOOT = np.array([30, 29, 28.])
FRESH = np.array([206, 198, 180.])
DUST = np.array([120, 110, 92.])
INSIDE = np.array([30, 28, 27.])
ROCK = {'conc': np.array([218, 212, 194.]) * 0.84, 'sand': np.array([196, 170, 118.]) * 0.85,
        'roof': np.array([210, 186, 134.]) * 0.85, 'red': np.array([128, 58, 40.]) * 0.9,
        'steel': np.array([110, 112, 120.]), 'green': np.array([0, 214, 0.]) * 0.8}

# roof holes: centre x, y, radii, seed
HOLES = ((-66.0, -50.0, 27.0, 15.0, 601), (30.0, -50.0, 23.0, 13.0, 602),
         (-45.0, 52.0, 19.0, 16.0, 603), (-4.0, 56.0, 18.0, 15.0, 604), (60.0, 60.0, 15.0, 11.0, 605))
SMASHED = (('n', 'e', -80.0, -55.0), ('s', 'e', 53.0, 78.0))       # hatches broken open


class PileChunks(Chunks):
    def apply(self, X, Y, H, C, rock, base_h=3.0):
        for (cx, cy, rr, kind, ang, dk, topz, tilt, steep, shade) in self.items:
            win = (np.abs(X - cx) < 2 * rr + 2) & (np.abs(Y - cy) < 2 * rr + 2)
            if not win.any():
                continue
            ddx, ddy = X[win] - cx, Y[win] - cy
            g = np.max([np.cos(a) * ddx + np.sin(a) * ddy - d for a, d in zip(ang, dk)], axis=0)
            h = np.clip(-g * steep, 0, None)
            h = np.minimum(h, np.clip(topz + tilt[0] * ddx + tilt[1] * ddy, 0.4, None)) * (g < 0)
            base = np.minimum(H[win], base_h)
            hh = np.where(h > 0, h + base, 0)
            full = np.zeros_like(H); full[win] = hh
            m = full > H
            H[m] = full[m]; C[m] = DEBRIS
            rock[m] = ROCK[kind] * shade
        return H, C, rock


def model(level, p=PL.P):
    def f(X, Yy, **kw):
        kw = dict(kw)
        if 'flag' in kw and kw['flag'] is not None:
            kw['damaged'] = True
        sc = PL.scene(X, Yy, p=p, **kw)
        return damage_scene(sc, X, Yy, level, p)
    return f


def damage_scene(sc, X, Yy, level, p=PL.P):
    H = sc.H.copy(); C = sc.C.copy()
    broken = np.zeros_like(H); soot = np.zeros_like(H)
    rock = np.zeros(H.shape + (3,), np.float32)
    if level < 1:
        return sc
    zr = p['zr']
    jag = WN.noise(X, Yy, 2.6, 611)
    # ---- roof holes: take the slabs away, sink the body under them (dark inside), charred rims
    hole_any = np.zeros(H.shape, bool)
    rimf = np.zeros_like(H)
    for (cx, cy, rx, ry, seed) in HOLES:
        e = blob(X, Yy, cx, cy, rx, ry, 0.5, seed, feat=5.0)
        hole = e < 0
        rim = (e >= 0) & (e < 0.35)
        hole_any |= hole
        for s in sc.slabs:
            if s.name == 'roof':
                s.top = np.where(hole & (s.top >= 0), -1.0, s.top)
                # the broken edge sags a little
                s.top = np.where(rim & (s.top >= 0), s.top - 1.5 * (1 - e / 0.35), s.top)
        body = hole & (C == PL.BERM) & (H > zr - 2)
        deep = np.clip(-e * 2.0, 0, 1)
        H = np.where(body, zr - 6.0 - 14.0 * deep + 2.0 * jag, H)
        C = np.where(body, DEBRIS + 1, C)                          # the dark inside
        rimf = np.maximum(rimf, rim * 0.7)
        soot = np.maximum(soot, 1.0 * np.exp(-(((X - cx) / (rx * 2.3)) ** 2 + ((Yy - cy) / (ry * 2.9)) ** 2)))
    # ---- masts: the west one snapped (its lamp housing, the beacon, left on the stump), the east one broken off
    (m0x, m0y, m0z0, m0z1), (m1x, m1y, m1z0, m1z1) = p['masts']
    snap0 = m0z0 + 0.6 * (m0z1 - m0z0)
    snap1 = m1z0 + 12.0
    for s in sc.slabs:
        if s.name not in ('mast', 'lamp', 'aerial', 'arm', 'armlamp'):
            continue
        on = s.top >= 0
        near0 = on & (np.hypot(X - m0x, Yy - m0y) < 12)
        near1 = on & (np.hypot(X - m1x, Yy - m1y) < 12)
        if s.name == 'mast':
            s.top = np.where(near0, snap0 + 1.5 * jag, s.top)
            s.top = np.where(near1, snap1 + 1.5 * jag, s.top)
        elif s.name == 'lamp':
            s.top = np.where(near0, snap0 + 4.0, np.where(near1, -1.0, s.top))
            s.bot = np.where(near0, snap0 - 2.0, s.bot)
        else:
            s.top = np.where(near0 | near1, -1.0, s.top)
    # ---- chunks out of the slopes: the south bunker's west end, the north bunker's east end
    for (cx, cy, rx, ry, depth, seed) in ((-118.0, 92.0, 16.0, 13.0, 12.0, 621), (104.0, -60.0, 12.0, 16.0, 10.0, 622)):
        b = blob(X, Yy, cx, cy, rx, ry, 0.45, seed) < 0
        m = b & (C == PL.BERM) & (H > p['slab_h'] + 1)
        H = np.where(m, np.maximum(H - depth * (0.7 + 0.3 * np.abs(jag)), p['slab_h'] + 1.0), H)
        broken = np.maximum(broken, m * 0.8)
        soot = np.maximum(soot, 0.5 * np.exp(-((X - cx) ** 2 + (Yy - cy) ** 2) / (2.0 * rx) ** 2))
    # ---- soot on the machinery and the pad
    for (cx, cy, rr_) in ((-55.0, -5.0, 26.0), (53.0, -9.0, 20.0), (100.0, 40.0, 26.0), (-20.0, 100.0, 22.0), (90.0, 95.0, 20.0)):
        soot = np.maximum(soot, 0.6 * np.exp(-((X - cx) ** 2 + (Yy - cy) ** 2) / rr_ ** 2))
    # ---- rubble round the east end and the front
    chunks = PileChunks(630)
    avoid = [(x_, y_, 6.0) for (x_, y_, _, _) in (p['masts'])] + [(p['pole'][0], p['pole'][1], 8.0)]
    chunks.scatter(9, (112.0, 10.0), (4, 22), (2.2, 5.0), ['sand', 'roof', 'red', 'steel'], [0.35, 0.3, 0.2, 0.15], avoid)
    chunks.scatter(6, (-20.0, 106.0), (2, 16), (2.2, 4.6), ['sand', 'conc', 'roof'], [0.4, 0.3, 0.3], avoid)
    chunks.scatter(5, (-118.0, 60.0), (2, 14), (2.2, 4.6), ['sand', 'red', 'roof'], [0.4, 0.3, 0.3], avoid)
    H, C, rock = chunks.apply(X, Yy, H, C, rock, p['slab_h'])
    sc.H, sc.C = H.astype(np.float32), C.astype(np.int16)
    sc.extra.update(broken=broken.astype(np.float32), soot=soot.astype(np.float32), rock=rock,
                    hole=hole_any.astype(np.float32), rimbreak=rimf.astype(np.float32))
    return sc


def mats(r, alb, level, p=PL.P):
    """damage on top of the Barracks' materials: dust, soot, cracks, smashed hatches, fresh breaks, rubble."""
    if level < 1:
        return alb
    x, y, z, comp = r.x, r.y, r.z, r.comp
    top = r.nz > 0.75
    out = alb.copy()
    grain = WN.noise(x, y + z, 1.2, 641) * 0.05
    g1 = (1 + grain)[..., None]
    house = np.isin(comp, list(PL.HOUSE))
    dust = smoothstep(0.3, 1.3, WN.noise(x, y, 14, 642)) * np.where(top, 0.45, 0.2) * ~house
    out = out * (1 - dust[..., None]) + DUST * g1 * dust[..., None]
    s = r.field('soot')
    soot = smoothstep(0.12, 0.6, np.clip(s * (0.65 + 0.35 * WN.noise(x, y + z, 6, 643)), 0, 1)) * 0.92
    soot = soot * np.where(house, 0.5, 1.0)
    out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
    # cracks in the blocks, the roofs and the pad
    cz = np.isin(comp, [PL.BERM, PL.ROOF, PL.SLAB, PL.SPINE])
    cn = WN.ridge(x + 0.4 * z, y - 0.6 * z, 8, 644) + 0.12 * np.abs(WN.noise(x, y + z, 1.5, 645))
    cmask = smoothstep(0.6, 1.3, WN.noise(x, y, 30, 646))
    crack = (1 - smoothstep(0.015, 0.055, cn)) * cmask * cz
    out *= (1 - 0.6 * crack)[..., None]
    # smashed hatches: broken open, dark behind, bent green slats
    import pilemat as PM
    key, side, along = PM.face_coords(x, y, z, p)
    for (bk, sd, a0, a1) in SMASHED:
        m = (comp == PL.BERM) & (key == bk) & (side == sd) & (along >= a0) & (along <= a1) & (z > 8) & (z < 28)
        hole = m & (WN.noise(along * 1.0 + 30, z * 1.3, 5.0, 647) > -0.25)
        out = np.where(hole[..., None], INSIDE * g1, out)
    # fresh breaks: chunks knocked out of the slopes; the roofs' broken rims (on the roofs only)
    brk = np.clip(r.field('broken') * 1.4, 0, 1) * ~house * (comp == PL.BERM)
    brk = np.maximum(brk, np.clip(r.field('rimbreak'), 0, 1) * (comp == PL.ROOF))
    fresh = FRESH * np.clip(0.84 + 0.1 * WN.noise(x, y + z, 1.5, 648), 0.6, 1.0)[..., None]
    out = out * (1 - brk[..., None]) + fresh * brk[..., None]
    # the dark inside under the roof holes
    ins = comp == DEBRIS + 1
    out = np.where(ins[..., None], INSIDE * (0.8 + 0.3 * WN.noise(x, y, 2.0, 649))[..., None] * g1, out)
    rock = r.field('rock')
    deb = comp == DEBRIS
    out = np.where(deb[..., None], rock * (1 + 1.5 * grain)[..., None], out)
    return out
