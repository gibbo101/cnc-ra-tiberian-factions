"""
Damage for the Tech Center (TS GTTECH frame 1; RA has healthy and damaged only), placed in the building's own
frame so it turns with the layout.
  dome    TS's hole: one ragged hole high on the side facing the camera, left of the top, its struts still across
          it, the backs of the far side's panels dark green through it; cracks running out of it. GTTECH_A's
          damaged frames: light flashes out of the hole and along the cracks on every other frame, the other
          panels flicker
  roof    scorched, two holes burnt through it, soot
  east    the framework buckled: a run of its struts gone, soot
  ground  rubble round the front and the east end
"""
import numpy as np
from scipy import ndimage
from scipy.special import ndtri
import hd, tech as TC, wnoise as WN
from walls2 import smoothstep
from pdamage import Chunks, blob
import techmat as TM

DEBRIS = 40
SOOT = np.array([30, 29, 28.])
FRESH = np.array([206, 198, 180.])
DUST = np.array([120, 110, 92.])
INSIDE = np.array([24, 28, 30.])
ROCK = {'sand': np.array([200, 174, 116.]) * 0.85, 'steel': np.array([110, 112, 120.]),
        'green': np.array([0, 214, 0.]) * 0.8, 'conc': np.array([218, 212, 194.]) * 0.84}
# holes burnt through the roof, per layout: local x, y, rx, ry, seed
HOLES = {'ts': ((-48.0, 60.0, 15.0, 10.0, 801), (78.0, 48.0, 13.0, 10.0, 802))}
HOLES['rot'] = HOLES['ts']
HOLES['ts3'] = HOLES['ts']


class TechChunks(Chunks):
    def scatter(self, n, centre, rad, sizes, kinds, weights=None, avoid=()):
        cx0, cy0 = centre
        k = 0
        tries = 0
        while k < n and tries < 2000:
            tries += 1
            a = self.rng.uniform(0, 2 * np.pi); rr_ = self.rng.uniform(*rad)
            cx, cy = cx0 + rr_ * np.cos(a), cy0 + rr_ * np.sin(a)
            if any(np.hypot(cx - ax, cy - ay) < ar for (ax, ay, ar) in avoid):
                continue
            if abs(cx) > 186 or abs(cy) > 126:
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

    def apply(self, X, Y, H, C, rock, base_h=0.0):
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


def model(level, p=TC.P):
    def f(X, Yy, **kw):
        sc = TC.scene(X, Yy, p=p, **kw)
        return damage_scene(sc, X, Yy, level, p, kw.get('layout', 'ts'))
    return f


# ---- the dome as TS has it damaged, read off GTTECH frame 1 and GTTECH_A 08-15 in TS's own frame (native px of
# its 192x120 canvas, TS's camera; the dome's middle at about (121, 70)): one ragged hole high on the side facing
# the camera, left of the top, its struts still across it, dark green inside; cracks run out of it. On every
# other frame of GTTECH_A's damaged loop light flashes out of the hole and along the cracks.
# It goes onto our dome by the direction from the dome's centre, turned so the view's camera sits where TS's
# does: each view sees it as TS's camera does.
TS_HOLE_RUNS = {64: (118, 122), 65: (117, 123), 66: (116, 122), 67: (116, 122), 68: (115, 122),
                69: (113, 122), 70: (113, 121), 71: (112, 120), 72: (112, 120), 73: (112, 118), 74: (112, 116)}
# the cracks: TS px polylines from where they start; True: they light up with the hole
TS_CRACKS = (
    (((122.8, 64.6), (123.8, 63.6), (125.9, 62.4)), False),                       # up from the hole's top
    (((112.2, 71.4), (110.5, 71.5), (108.4, 72.6)), False),                        # left
    (((120.6, 72.2), (123.0, 72.6), (125.2, 73.0), (126.8, 73.6), (128.4, 73.1), (130.1, 72.8)), True),  # right
    (((122.6, 72.9), (122.9, 74.8)), True),
    (((110.9, 76.6), (113.0, 76.4), (115.0, 76.6)), True),                         # the gash below
    (((112.4, 76.6), (112.6, 77.8)), True),
    (((126.0, 77.4), (123.6, 77.8), (123.6, 79.5), (123.7, 80.6), (124.7, 81.8)), True),   # lower right
    (((124.3, 78.6), (125.7, 79.8)), True),
    (((116.0, 81.4), (117.5, 82.0), (118.6, 83.0), (119.6, 83.6), (120.5, 84.6), (120.6, 85.9)), True),  # down
    (((110.2, 64.2), (110.8, 64.9)), False), (((110.2, 67.3), (110.8, 67.8)), False),
    (((127.2, 82.2), (127.8, 82.9)), False),
)
TSV = hd.ts_view((192, 120), (108.0, 90.0), hd.TS_PPU, ss=1)
FACE = {'ts': 45.0, 'ts3': 90.0, 'rot': 0.0}        # local azimuth of the side each view looks at (TS's: 45)
HOUSE = np.array([0, 214, 0.])
STRUT_IN = np.array([30, 22, 15.])


def _hole_sdf():
    """signed distance (TS px) to the hole's edge, negative inside, on a fine grid over TS's frame."""
    S, u0, v0, n = 8, 98, 50, 48
    m = np.zeros((n * S, n * S), np.float32)
    for row, (a, b) in TS_HOLE_RUNS.items():
        m[(row - v0) * S:(row - v0 + 1) * S, (a - u0) * S:(b + 1 - u0) * S] = 1.0
    m = ndimage.gaussian_filter(m, 0.55 * S)
    inside = m > 0.5
    sd = (ndimage.distance_transform_edt(~inside) - ndimage.distance_transform_edt(inside)) / S
    return sd.astype(np.float32), (u0, v0, S)


HOLE_SD, HOLE_GRID = _hole_sdf()


def ts_frame_px(x, y, z, lay, p=TC.P):
    """where points on the dome (local coordinates) sit in TS's own frame, the dome turned so this view's camera
    is where TS's is."""
    (cx, cy), R, zc, rb = TC.dome_geo(TC.LAYOUTS[lay], p)
    a = np.deg2rad(45.0 - FACE[lay])
    ca, sa = np.cos(a), np.sin(a)
    dx, dy = x - cx, y - cy
    return TSV.project(cx + dx * ca - dy * sa, cy + dx * sa + dy * ca, z)


def hole_sd(u, v):
    u0, v0, S = HOLE_GRID
    return ndimage.map_coordinates(HOLE_SD, [(v - v0) * S - 0.5, (u - u0) * S - 0.5], order=1, mode='nearest')


def polyline_d(u, v, pts):
    """distance (TS px) to a polyline and how far along it (0..1) the nearest point is."""
    pts = np.asarray(pts, np.float32)
    seg = np.hypot(*np.diff(pts, axis=0).T)
    tot = seg.sum()
    d = np.full(u.shape, 1e9, np.float32)
    t = np.zeros(u.shape, np.float32)
    acc = 0.0
    for (ax, ay), (bx, by), l in zip(pts[:-1], pts[1:], seg):
        vx, vy = bx - ax, by - ay
        s = np.clip(((u - ax) * vx + (v - ay) * vy) / (l * l), 0, 1)
        dd = np.hypot(u - ax - s * vx, v - ay - s * vy)
        b = dd < d
        d = np.where(b, dd, d)
        t = np.where(b, (acc + s * l) / tot, t)
        acc += l
    return d, t


def dome_damage(r, x, y, z, dome, strut, lay):
    """TS's hole and cracks on the dome's visible pixels: sets r.dome_hole (panel gone: the inside shows),
    r.dome_rim (the broken panels' edges), r.dome_crack (dark crack lines), r.hole_sd / r.crack_lit (for the
    light) and r.ts_uv; returns those masks and the shards of panel left along the struts in the hole."""
    shape = z.shape
    hole = np.zeros(shape, bool); rim = np.zeros(shape, bool); crack = np.zeros(shape, bool)
    shards = np.zeros(shape, bool)
    sdf = np.full(shape, 99.0, np.float32); clit = np.full(shape, 99.0, np.float32)
    uu = np.zeros(shape, np.float32); vv = np.zeros(shape, np.float32)
    idx = np.nonzero(dome)
    if len(idx[0]):
        xs, ys, zs = x[idx], y[idx], z[idx]
        u, v = ts_frame_px(xs, ys, zs, lay)
        u, v = np.asarray(u, np.float32), np.asarray(v, np.float32)
        uu[idx], vv[idx] = u, v
        # the hole's ragged edge: a fine jag and a coarser wander
        jag = 0.26 * WN.noise(u * 8, v * 8, 2.2, 861) + 0.22 * WN.noise(u * 8, v * 8, 9.0, 862)
        sd = hole_sd(u, v) + jag
        st = strut[idx]
        # shards of the broken panels left along the struts round the hole
        (cx, cy), R, zc, rb = TC.dome_geo(TC.LAYOUTS[lay])
        near, _ = TC.geodesic_dir(xs - cx, ys - cy, zs - zc, w=0.12)
        shard = near & (WN.noise(xs * 2, ys * 2 + zs, 3.0, 863) > 0.25) & (sd > -1.2)
        h = (sd < 0) & ~st & ~shard
        hole[idx] = h
        rim[idx] = ~st & ~h & (sd >= 0) & (sd < 0.28)           # the panels' broken edges
        shards[idx] = ~st & ~h & (sd < 0)
        sdf[idx] = sd
        # the cracks: thin jagged lines, tapering away from where they start
        ju = u + 0.12 * WN.noise(u * 8, v * 8, 3.6, 864)
        jv = v + 0.12 * WN.noise(u * 8 + 50, v * 8, 3.6, 865)
        cr = np.zeros(len(u), bool)
        cl = np.full(len(u), 99.0, np.float32)
        for pts, lit in TS_CRACKS:
            d, t = polyline_d(ju, jv, pts)
            w = 0.25 - 0.13 * t
            cr |= d < w
            if lit:
                cl = np.minimum(cl, d / w)
        crack[idx] = cr & ~st & ~h
        clit[idx] = cl
    r.dome_hole, r.dome_rim, r.dome_crack = hole, rim, crack
    r.hole_sd, r.crack_lit, r.ts_uv = sdf, clit, (uu, vv)
    return hole, rim, shards, crack


def hole_interior(r, view, p=TC.P):
    """what shows through the hole: the inside of the dome's far side (the backs of its panels, dark green, and
    its struts), in the dark. Returns the hole's mask and colours."""
    m = getattr(r, 'dome_hole', None)
    if m is None or not m.any():
        return None, None
    lay = TM.layout_of(r)
    L = TC.LAYOUTS[lay]
    x, y = TC.to_local(r.x, r.y, lay)
    px, py, pz = x[m], y[m], r.z[m]
    (cx, cy), R, zc, rb = TC.dome_geo(L, p)
    Dw = np.array([view.F[0] * view.cE, view.F[1] * view.cE, -view.sE])      # the view's ray, into the scene
    Lw = view.L
    if L['rot']:
        D = np.array([Dw[1], -Dw[0], Dw[2]]); Ll = np.array([Lw[1], -Lw[0], Lw[2]])
    else:
        D, Ll = Dw, np.asarray(Lw)
    # the far side of the dome's shell, from inside (TS shows it dark green through the hole)
    s = -2.0 * ((px - cx) * D[0] + (py - cy) * D[1] + (pz - zc) * D[2])
    fx, fy, fz = px + s * D[0], py + s * D[1], pz + s * D[2]
    st, pid = TC.geodesic_dir(fx - cx, fy - cy, fz - zc, w=0.06)
    nin = -np.stack([fx - cx, fy - cy, fz - zc], -1) / R
    lit = np.clip(nin @ Ll, 0, 1)
    k = 0.22 + 0.1 * lit + 0.03 * np.sin(pid * 2.3) + 0.02 * WN.noise(fx, fy + fz, 6.0, 866)
    col = HOUSE[None, :] * k[:, None]
    col = np.where(st[:, None], STRUT_IN[None, :] * (0.8 + 0.4 * lit)[:, None], col)
    # darker near the hole's edge (the shell's shadow)
    edge = np.clip(1.0 - (-r.hole_sd[m]) / 1.6, 0, 1)
    col = col * (1 - 0.35 * edge)[:, None]
    return m, col.astype(np.float32)


def damage_scene(sc, X, Yy, level, p=TC.P, layout='ts'):
    if level < 1:
        return sc
    L = TC.LAYOUTS[layout]
    x, y = TC.to_local(X, Yy, layout)
    H = sc.H.copy(); C = sc.C.copy()
    soot = np.zeros_like(H); broken = np.zeros_like(H)
    rock = np.zeros(H.shape + (3,), np.float32)
    rz = p['roof_z']
    jag = WN.noise(x, y, 2.6, 811)
    for (cx, cy, rx, ry, seed) in HOLES[layout]:
        e = blob(x, y, cx, cy, rx, ry, 0.5, seed, feat=5.0)
        hole = (e < 0) & (C == TC.ROOF)
        H = np.where(hole, rz - 10.0 + 2.0 * jag, H)
        C = np.where(hole, DEBRIS + 1, C)
        broken = np.maximum(broken, ((e >= 0) & (e < 0.35)) * 0.8)
        soot = np.maximum(soot, 0.95 * np.exp(-(((x - cx) / (rx * 2.4)) ** 2 + ((y - cy) / (ry * 2.6)) ** 2)))
    # the east framework: a run of struts gone, the rest buckled
    for s in sc.slabs:
        if s.name in ('frame', 'rail'):
            run = (s.top >= 0) & (y > -50.0) & (y < -25.0)
            bent = np.clip(14.0 + 10.0 * jag + 0.3 * np.abs(y + 10.0), 4.0, None)
            s.top = np.where(run, np.where(s.name == 'rail', -1.0, np.minimum(s.top, bent)), s.top)
    soot = np.maximum(soot, 0.7 * np.exp(-(((x - 160) / 30.0) ** 2 + ((y + 38) / 30.0) ** 2)))
    # soot on the dome's camera side and round the foot
    (dcx, dcy), R, zc, rb = TC.dome_geo(L, p)
    face = {'ts': (0.6, 0.8), 'ts3': (0.0, 1.0), 'rot': (1.0, 0.0)}[layout]
    sx_, sy_ = dcx + face[0] * R * 0.5, dcy + face[1] * R * 0.5
    soot = np.maximum(soot, 0.55 * np.exp(-(((x - sx_) / 50.0) ** 2 + ((y - sy_) / 40.0) ** 2)))
    for (sx, sy, rr) in ((-120, 96, 24.0), (40, 108, 24.0), (165, -60, 22.0)):
        soot = np.maximum(soot, 0.55 * np.exp(-((x - sx) ** 2 + (y - sy) ** 2) / rr ** 2))
    chunks = TechChunks(830)
    a = TC.arch_dims(L, p)
    avoid = []
    for (cxy, dd, e_) in L['arches']:
        for sgn in (-1, 1):
            avoid.append((cxy[0] + sgn * dd[0] * a['span'] / 2, cxy[1] + sgn * dd[1] * a['span'] / 2, 16.0))
    chunks.scatter(8, (-20.0, 112.0), (4, 30), (2.4, 5.4), ['sand', 'steel', 'green', 'conc'], [0.4, 0.25, 0.15, 0.2], avoid)
    chunks.scatter(6, (172.0, -10.0), (2, 14), (2.4, 5.0), ['steel', 'sand'], [0.6, 0.4], avoid)
    # keep the rubble inside the canvas (the turned layout runs close to the plot's sides)
    lim = 118.0 if layout == 'rot' else 1e9
    chunks.items = [it for it in chunks.items if abs(TC.to_world(it[0], it[1], layout)[0]) + it[2] * 1.6 < lim]
    H, C, rock = chunks.apply(x, y, H, C, rock, 0.0)
    sc.H, sc.C = H.astype(np.float32), C.astype(np.int16)
    sc.extra.update(soot=soot.astype(np.float32), broken=broken.astype(np.float32), rock=rock)
    return sc


def mats(r, alb, level, p=TC.P):
    if level < 1:
        return alb
    lay = TM.layout_of(r)
    L = TC.LAYOUTS[lay]
    x, y = TC.to_local(r.x, r.y, lay)
    z, comp = r.z, r.comp
    top = r.nz > 0.75
    out = alb.copy()
    grain = WN.noise(x, y + z, 1.2, 841) * 0.05
    g1 = (1 + grain)[..., None]
    house = np.isin(comp, list(TC.HOUSE))
    dust = smoothstep(0.3, 1.3, WN.noise(x, y, 14, 842)) * np.where(top, 0.45, 0.2) * ~house
    out = out * (1 - dust[..., None]) + DUST * g1 * dust[..., None]
    s = r.field('soot')
    soot = smoothstep(0.15, 0.65, np.clip(s * (0.65 + 0.35 * WN.noise(x, y + z, 6, 843)), 0, 1)) * 0.88
    soot = soot * np.where(house, 0.5, 1.0)
    out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
    cz = np.isin(comp, [TC.BAND, TC.ROOF, TC.SLAB, TC.PARAPET])
    cn = WN.ridge(x + 0.4 * z, y - 0.6 * z, 8, 844) + 0.12 * np.abs(WN.noise(x, y + z, 1.5, 845))
    cmask = smoothstep(0.55, 1.25, WN.noise(x, y, 30, 846))
    crack = (1 - smoothstep(0.015, 0.055, cn)) * cmask * cz
    out *= (1 - 0.6 * crack)[..., None]
    # TS's hole in the dome (what shows through it is drawn in TechPrep.shade: the backs of the far side's
    # panels), the broken panels' edges and shards round it, the cracks running out of it
    dome = comp == TC.DOME
    strut, pid, az, el = TC.dome_lattice(x, y, z, L, p)
    hole, rim, shards, crack = dome_damage(r, x, y, z, dome, strut, lay)
    out = np.where(hole[..., None], HOUSE * 0.3, out)
    out = np.where(shards[..., None], HOUSE * (0.74 + 0.1 * WN.noise(x, y + z, 1.5, 869))[..., None] * g1, out)
    out = np.where(rim[..., None], HOUSE * (0.5 + 0.1 * WN.noise(x, y + z, 1.5, 868))[..., None] * g1, out)
    out = np.where(crack[..., None], HOUSE * 0.26, out)
    brk = np.clip(r.field('broken') * 1.4, 0, 1) * (comp == TC.ROOF)
    out = out * (1 - brk[..., None]) + FRESH * brk[..., None]
    out = np.where((comp == DEBRIS + 1)[..., None], INSIDE * g1, out)
    rock = r.field('rock')
    out = np.where((comp == DEBRIS)[..., None], rock * (1 + 1.5 * grain)[..., None], out)
    return out


# GTTECH_A's damaged loop, read off its frames 08-15: on the even frames light flashes out of the hole and along
# the lit cracks, quiet on the odd ones (08: a few points, mostly blue; 10: all white; 12: half white, half blue;
# 14: more blue than white). frame: (how much of the hole lights up, how much of that is white, strength)
LIGHT = {0: (0.35, 0.3, 0.85), 2: (1.0, 1.0, 1.0), 4: (1.0, 0.5, 1.0), 6: (0.95, 0.38, 0.95)}
BLUE = np.array([92.0, 100.0, 255.0])
LBLUE = np.array([156.0, 164.0, 255.0])
WHITE = np.array([238.0, 240.0, 255.0])


def _above(f):
    """the level a smooth unit noise is above over a fraction f of its area."""
    return -9.0 if f >= 0.999 else float(ndtri(1.0 - max(f, 1e-3)))


def hole_lights(r, t, ss):
    """GTTECH_A, damaged, frame t of 8: (flicker, alpha, rgb). The intact panels flicker (added light); on the
    even frames the light out of the hole and along the lit cracks is drawn over the top (alpha, colour)."""
    shape = r.z.shape
    flick = np.zeros(shape + (3,), np.float32)
    panel = getattr(r, 'dome_panel', None)
    hole = getattr(r, 'dome_hole', None)
    if panel is None or hole is None:
        return flick, np.zeros(shape, np.float32), np.zeros(shape + (3,), np.float32)
    # the intact panels flicker: each one up or down a little, frame by frame
    pid = r.dome_pid
    fl = np.sin(pid * 3.17 + t * 2.39) * np.sin(pid * 1.31 + t * 4.1)
    m = panel & ~hole & ~r.dome_rim & ~r.dome_crack
    flick[m] = np.array([0.0, 46.0, 0.0])[None, :] * np.clip(fl[m], 0, 1)[:, None]
    A = np.zeros(shape, np.float32)
    C = np.zeros(shape + (3,), np.float32)
    if t not in LIGHT:
        return flick, A, C
    cov, wf, k = LIGHT[t]
    dome = r.comp == TC.DOME
    u, v = r.ts_uv
    sd = r.hole_sd
    # sparkle: noise in TS's frame, new each frame (TS px x 8: features of about TS's own pixel)
    n1 = WN.noise(u * 8 + 31.0 * t, v * 8 - 17.0 * t, 5.0, 880 + t)
    n2 = WN.noise(u * 8 - 23.0 * t, v * 8 + 11.0 * t, 7.0, 890 + t)
    n3 = WN.noise(u * 8 + 7.0 * t, v * 8 + 29.0 * t, 4.0, 900 + t)
    th = _above(cov)
    on = np.ones(shape, np.float32) if th < -8 else smoothstep(th - 0.3, th + 0.3, n1)
    tw = _above(wf)
    white = np.ones(shape, np.float32) if tw < -8 else smoothstep(tw - 0.35, tw + 0.35, n2)
    deep = np.clip(-sd / 1.3, 0, 1)

    def over(alpha, col):
        nonlocal A, C
        alpha = np.clip(alpha, 0, 1).astype(np.float32)
        C = C * (1 - alpha)[..., None] + col * alpha[..., None]
        A = A + alpha * (1 - A)

    # a soft glow on the panels round the hole's edge
    bloom = np.clip(1.0 - sd / 0.9, 0, 1) * (sd >= 0) * dome * 0.45 * k * (0.6 + 0.4 * on)
    over(bloom, np.broadcast_to(LBLUE, shape + (3,)))
    # the lit cracks: a bright core and a glow either side
    cl = r.crack_lit
    thc = _above(min(1.0, cov + 0.2))
    onc = np.ones(shape, np.float32) if thc < -8 else smoothstep(thc - 0.3, thc + 0.3, n3)
    glow = np.clip(1.0 - cl / 3.0, 0, 1) * 0.5 * k * onc * dome
    over(glow, np.broadcast_to(LBLUE, shape + (3,)))
    core = np.clip(1.5 - cl, 0, 1) * k * onc * dome
    cw = np.clip(white + 0.3, 0, 1)[..., None]
    over(core, BLUE * (1 - cw) + WHITE * cw)
    # the struts across the hole catch a little of it
    over((r.dome_strut & (sd < 0)) * 0.16 * k, np.broadcast_to(LBLUE * 0.6, shape + (3,)))
    # the hole: filled with light behind the struts, whiter deeper in
    wh = np.clip(white * (0.6 + 0.4 * deep) + (0.25 * deep if wf > 0.3 else 0.0), 0, 1)[..., None]
    over(hole * on * k, BLUE * (1 - wh) + WHITE * wh)
    rgb = np.where(A[..., None] > 1e-4, C / np.maximum(A, 1e-4)[..., None], 0)
    return flick, A, rgb.astype(np.float32)
