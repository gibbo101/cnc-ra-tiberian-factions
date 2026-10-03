"""
Damage for the Power Plant (TS GTPOWR frame 1; RA has healthy and damaged only) and its turbine.

Mapped from TS's damaged frame, part by part (greys and browns only, placed in world space so both views match):
  cone     the top broken: a jagged V torn out of the front of the rim (down to ~150), the dark inside showing;
           a blast hole on its south face (az ~78, z ~86-128) swallowing the window, soot and cracks round it
  collar   one of the three west pipes snapped off
  sockets  the south plate cracked and a chunk knocked out of the front of its ring and mound; cracks across
           the west and east plates; chunks out of the west mound's west side and the east mound's east side
  ground   cracks in the slab, rubble at the foot of the mounds and the tower
  turbine  (damaged version) soot, a dented, scorched housing, two of the band's windows dark
"""
import numpy as np
import hd, powr as PW, wnoise as WN
import walls2 as W
from walls2 import smoothstep

DEBRIS = 40
SOOT = np.array([30, 29, 28.])
FRESH = np.array([206, 198, 180.])
DUST = np.array([120, 110, 92.])
INSIDE = np.array([58, 60, 72.])              # TS: the dark blue-grey inside of the broken tower
ROCK = {'conc': np.array([218, 212, 194.]) * 0.84, 'earth': np.array([188, 162, 112.]) * 0.85,
        'khaki': np.array([200, 166, 100.]) * 0.85, 'green': np.array([0, 214, 0.]) * 0.8,
        'steel': np.array([96, 97, 104.]), 'plate': np.array([150, 150, 178.]) * 0.85}

HOLE = (np.deg2rad(78.0), 108.0, 10.0, 15.0)          # azimuth, z, half-width (units of arc), half-height


def blob(X, Y, cx, cy, rx, ry, rough, seed, feat=7.0):
    e = np.sqrt(((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2)
    return e - 1.0 - rough * WN.noise(X, Y, feat, seed)


class Chunks:
    """angular rubble chunks at fixed world positions (seeded: every view gets the same ones)."""
    def __init__(self, seed):
        self.rng = np.random.default_rng(seed)
        self.items = []

    def scatter(self, n, centre, rad, sizes, kinds, weights=None, avoid=()):
        cx0, cy0 = centre
        k = 0
        while k < n:
            a = self.rng.uniform(0, 2 * np.pi); rr_ = self.rng.uniform(*rad)
            cx, cy = cx0 + rr_ * np.cos(a), cy0 + rr_ * np.sin(a)
            if any(np.hypot(cx - ax, cy - ay) < ar for (ax, ay, ar) in avoid):
                continue
            if max(abs(cx), abs(cy)) > 150:
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

    def apply(self, X, Y, H, C, rock):
        for (cx, cy, rr, kind, ang, dk, topz, tilt, steep, shade) in self.items:
            win = (np.abs(X - cx) < 2 * rr + 2) & (np.abs(Y - cy) < 2 * rr + 2)
            if not win.any():
                continue
            ddx, ddy = X[win] - cx, Y[win] - cy
            g = np.max([np.cos(a) * ddx + np.sin(a) * ddy - d for a, d in zip(ang, dk)], axis=0)
            h = np.clip(-g * steep, 0, None)
            h = np.minimum(h, np.clip(topz + tilt[0] * ddx + tilt[1] * ddy, 0.4, None)) * (g < 0)
            base = np.minimum(H[win], PW.P['slab_h'])
            hh = np.where(h > 0, h + base, 0)
            full = np.zeros_like(H); full[win] = hh
            m = full > H
            H[m] = full[m]; C[m] = DEBRIS
            rock[m] = ROCK[kind] * shade
        return H, C, rock


def model(level, p=PW.P):
    def f(X, Yy, **kw):
        sc = PW.scene(X, Yy, p=p, **kw)
        return damage_scene(sc, X, Yy, level, p, turbines=kw.get('turbines', ()))
    return f


def damage_scene(sc, X, Yy, level, p=PW.P, turbines=()):
    H = sc.H.copy(); C = sc.C.copy()
    broken = np.zeros_like(H); soot = np.zeros_like(H)
    rock = np.zeros(H.shape + (3,), np.float32)
    if level < 1:
        return sc
    tx, ty = p['tower']
    dx, dy = X - tx, Yy - ty
    d = np.hypot(dx, dy); az = np.arctan2(dy, dx)
    jag = WN.noise(X, Yy, 2.6, 401)

    # ---- the cone's top broken: a jagged V torn out of the front of the rim, the inside showing
    cone = np.isin(C, [PW.CONE, PW.CONEIN])
    da = np.angle(np.exp(1j * (az - np.deg2rad(52.0))))
    v = np.clip(1 - np.abs(da) / np.deg2rad(62.0), 0, 1)                   # 1 at the V's bottom
    rough = 3.0 * WN.noise(np.cos(az) * 60, np.sin(az) * 60, 4.0, 402) + 2.0 * np.sin(az * 9.0)
    back = 5.0 * np.clip(-np.cos(az - np.deg2rad(-150.0)), 0, 1)           # the back of the rim ragged too
    cut = p['cone_z'][1] - 2.0 - 21.0 * v ** 1.3 - np.abs(rough) - back
    inner_r = PW.cone_radius(np.array([p['cone_z'][1]]), p)[0] - p['wall']
    top_lost = cone & (H > cut)
    H = np.where(top_lost & (d > inner_r), cut, H)
    # the inside of the tower: deeper and dark, visible through the break
    ins = cone & (d <= PW.cone_radius(cut, p) - p['wall'] * 0.8)
    H = np.where(ins, np.minimum(H, cut - 36.0), H)
    C = np.where(ins, PW.CONEIN, C)
    rim_edge = top_lost & (d > inner_r) & (d > PW.cone_radius(cut, p) - 1.2)
    broken = np.maximum(broken, rim_edge * 0.8)
    sc.extra['shell_break'] = (top_lost & (d > inner_r) & ~rim_edge).astype(np.float32)
    soot = np.maximum(soot, cone * smoothstep(p['cone_z'][1] - 45, p['cone_z'][1] - 5, H) * 0.55)

    # ---- the blast hole (painted in the materials: its position goes to the scene extras), soot round it
    ha, hz, hw, hh = HOLE
    rr = PW.cone_radius(np.clip(H, p['cone_z'][0], p['cone_z'][1]), p)
    hu = np.angle(np.exp(1j * (az - ha))) * rr
    hv = H - hz
    soot = np.maximum(soot, cone * 0.95 * np.exp(-((hu / (hw * 2.4)) ** 2 + (hv / (hh * 2.0)) ** 2)))

    # ---- one west pipe snapped: drop its slab above a jagged break
    for s in sc.slabs:
        if s.name == 'pipe':
            a_ = p['pipes'][2]
            px_, py_ = tx + p['pipe_r'] * np.cos(a_), ty + p['pipe_r'] * np.sin(a_)
            mine = (s.top >= 0) & (np.hypot(X - px_, Yy - py_) <= p['pipe_w'] + 0.5)
            s.top = np.where(mine, 44.0 + 3 * jag, s.top)

    # ---- the sockets: a chunk out of the south ring and mound, chunks out of the west and east mounds
    (swx, swy), (sex, sey), (nex, ney) = p['sockets']
    zt = p['sock_z']
    for (cx, cy, rx, ry, depth, seed) in ((sex + 26, sey + 26, 14, 11, 9.0, 411),     # south: the front of its ring
                                          (swx - 44, swy + 6, 12, 16, 10.0, 412),     # west mound, west side
                                          (nex + 40, ney - 14, 12, 15, 9.0, 413)):    # east mound, east side
        b = blob(X, Yy, cx, cy, rx, ry, 0.45, seed) < 0
        m = b & (H > p['slab_h'] + 1) & np.isin(C, [PW.MOUND, PW.MRIM, PW.RING, PW.PLATE])
        H = np.where(m, np.maximum(H - depth * (0.7 + 0.3 * np.abs(jag)), p['slab_h'] + 2.0), H)
        broken = np.maximum(broken, m * 0.9)
        soot = np.maximum(soot, 0.5 * np.exp(-((X - cx) ** 2 + (Yy - cy) ** 2) / (2.2 * rx) ** 2))

    for (cx, cy, rr_) in ((-64, -20, 40.0), (40, 90, 34.0), (-100, 40, 30.0), (90, -40, 28.0), (-30, 100, 22.0), (110, 70, 20.0), (-110, 90, 20.0), (60, -100, 22.0)):
        soot = np.maximum(soot, 0.55 * np.exp(-((X - cx) ** 2 + (Yy - cy) ** 2) / rr_ ** 2))
    # ---- rubble at the foot of the mounds and round the tower
    chunks = Chunks(420)
    avoid = [(x_, y_, 50.0) for (x_, y_) in p['sockets']] + [(tx, ty, 54.0)]
    chunks.scatter(7, (sex, sey), (54, 70), (2.2, 5.0), ['conc', 'earth', 'plate', 'green'], [0.35, 0.35, 0.15, 0.15], avoid)
    chunks.scatter(6, (swx, swy), (54, 70), (2.2, 5.0), ['earth', 'conc', 'steel'], [0.45, 0.35, 0.2], avoid)
    chunks.scatter(4, (nex, ney), (54, 68), (2.2, 4.6), ['earth', 'conc', 'khaki'], [0.4, 0.3, 0.3], avoid)
    chunks.scatter(6, (tx, ty), (56, 70), (2.4, 5.6), ['khaki', 'steel', 'conc', 'green'], [0.4, 0.25, 0.2, 0.15], avoid)
    H, C, rock = chunks.apply(X, Yy, H, C, rock)

    sc.H, sc.C = H.astype(np.float32), C.astype(np.int16)
    sc.extra.update(broken=broken.astype(np.float32), soot=soot.astype(np.float32), rock=rock)
    return sc


def mats(r, alb, level, p=PW.P):
    """damage on top of the plant's materials: dust, soot, cracks, the blast hole, fresh breaks, rubble."""
    if level < 1:
        return alb
    x, y, z, comp = r.x, r.y, r.z, r.comp
    top = r.nz > 0.75
    out = alb.copy()
    grain = WN.noise(x, y + z, 1.2, 501) * 0.05
    g1 = (1 + grain)[..., None]
    tx, ty = p['tower']
    az = np.arctan2(y - ty, x - tx)
    cone = comp == PW.CONE
    house = np.isin(comp, list(PW.HOUSE))
    # dust on tops (not on the house colour)
    dust = smoothstep(0.3, 1.3, WN.noise(x, y, 14, 502)) * np.where(top, 0.5, 0.22) * ~house
    out = out * (1 - dust[..., None]) + DUST * g1 * dust[..., None]
    # soot
    s = r.field('soot')
    soot = smoothstep(0.2, 0.8, np.clip(s * (0.6 + 0.4 * WN.noise(x, y + z, 6, 503)), 0, 1)) * 0.7
    out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
    # cracks: on the cone, the mounds, the slab and the plates
    cz = np.isin(comp, [PW.CONE, PW.MOUND, PW.SLAB, PW.PLATE, PW.DRUM, PW.FAIR])
    cn = WN.ridge(x + 0.4 * z, y - 0.6 * z, 8, 504) + 0.12 * np.abs(WN.noise(x, y + z, 1.5, 505))
    cmask = smoothstep(0.7, 1.4, WN.noise(x, y, 36, 506))
    rr = PW.cone_radius(np.clip(z, p['cone_z'][0], p['cone_z'][1]), p)
    ha, hz, hw, hh = HOLE
    hu = np.angle(np.exp(1j * (az - ha))) * rr
    hv = z - hz
    near_hole = np.exp(-((hu / (hw * 2.4)) ** 2 + (hv / (hh * 2.0)) ** 2))
    near_top = smoothstep(p['cone_z'][1] - 50, p['cone_z'][1] - 10, z) * cone
    plates = comp == PW.PLATE
    cmask = np.maximum(cmask, np.maximum(near_hole * cone, near_top) * 0.9)
    cmask = np.maximum(cmask, plates * 1.0)
    cmask = np.maximum(cmask, (comp == PW.MOUND) * 0.7 * smoothstep(-0.2, 0.8, WN.noise(x, y, 20, 513)))
    crack = (1 - smoothstep(0.015, 0.055, cn)) * cmask * cz
    out *= (1 - 0.6 * crack)[..., None]
    # the blast hole: a jagged dark opening with a pale broken rim
    edge = np.sqrt((hu / hw) ** 2 + (hv / hh) ** 2) - 1.0 - 0.18 * WN.noise(hu * 1.0 + 300, hv * 1.0, 4.0, 507)
    hole = cone & (edge < 0)
    rim = cone & (edge >= 0) & (edge < 0.18)
    out = np.where(rim[..., None], FRESH * np.clip(0.8 + 0.1 * WN.noise(x, z, 1.5, 508), 0.6, 1)[..., None], out)
    deep = np.clip(-edge * 3.0, 0, 1)
    out = np.where(hole[..., None], INSIDE * (0.75 - 0.35 * deep)[..., None] * g1, out)
    # fresh breaks
    brk = np.clip(r.field('broken') * 1.4, 0, 1) * ~house
    fresh = FRESH * np.clip(0.84 + 0.1 * WN.noise(x, y + z, 1.5, 509), 0.6, 1.0)[..., None]
    out = out * (1 - brk[..., None]) + fresh * brk[..., None]
    # the tower's dark inside, and the torn top of its shell
    out = np.where((comp == PW.CONEIN)[..., None], INSIDE * 0.8 * g1, out)
    sb = (r.field('shell_break') > 0.5) & cone
    out = np.where(sb[..., None], INSIDE * (0.95 + 0.25 * WN.noise(x, y, 2.0, 512))[..., None] * g1, out)
    # rubble
    rock = r.field('rock')
    deb = comp == DEBRIS
    out = np.where(deb[..., None], rock * (1 + 1.5 * grain)[..., None], out)
    # the turbine, damaged: scorched housing, two of the band's windows dark
    th = np.isin(comp, [PW.THOUSE, PW.TCAP])
    tsoot = smoothstep(-0.2, 1.4, WN.noise(x, y + z, 9, 510)) * 0.35 * th
    tsoot = np.maximum(tsoot, 0.45 * th * np.exp(-((z - (p['sock_z'] + 6.0)) / 8.0) ** 2))      # sooty at the foot
    out = out * (1 - tsoot[..., None]) + SOOT * tsoot[..., None]
    tb = comp == PW.TBAND
    dead = tb & (WN.noise(x, y, 6, 511) > 0.25) & (out[..., 1] > 1.6 * np.maximum(out[..., 0], out[..., 2]))
    out = np.where(dead[..., None], np.array([34, 40, 34.]) * g1, out)
    return out
