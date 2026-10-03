"""
TS Firestorm Generator (Firestorm GAFIRE; TSFGEN in the mod) as a model for hd.py.

Built in its own frame ("local": x east, y south as TS draws it, units 1 cell = 128, z up, origin at the centre of TS's
3x2 foundation, x -192..192, y -128..128), read from GTFIRE / GTFIREMK / GTFIRE_A / _B / _C in TS's own camera (TS's
ground centre at frame px (84, 90)):
  base     a low brown earthen slab with TS's outline (GTFIREMK's slab: a notch in the north edge, the corners cut)
  drum     the pit's round drum on the east half: ribbed brown sides, a wide flat grey-lilac ring on top, the pit inside
           going down dark, the emitter standing in its middle; struts leaning against the drum's sides
  fins     two tall brown fins leaning back on the west half, metal-edged, green clamps round their feet, a lamp at
           each tip (GTFIRE_C)
  hatch    a green hatch sloping from the ground up against the drum's south side
  strip    a green kerb on the base behind the drum, along its north-east edge
  arm      (GTFIRE_A / _B) a dark crane arm from the back fin's top holding the dome (a tan lid with a grey cap) over
           the pit: closed (A 00, the end of the build-up), lifting (A 00-19), raised (B: lightning in the pit)
Layouts: 'ts' TS's own placement (the TS-angle view); 'ra' the same way round on RA's grid (3 x 2: the fins west, the
pit east, the hatch towards the camera).
"""
import numpy as np
import hd
from radr import rod_interval
from plugs import obox_interval
from plug import CropAcc, pack_slabs

(BASE, DRUM, RING, PIT, PITF, MECH, EMIT, STRUT, FIN, FINE, CLAMP, HATCH, STRIP, ARM, ARMG, DOME, DOMEC, LAMP,
 SLAB, HATCHF) = range(1, 21)
HOUSE = {CLAMP, HATCH, STRIP, ARMG}

P = dict(
    # GTFIREMK's slab outline (local x, y), the base's top h, its edge sloping down over `edge` units
    base=dict(poly=((-168.0, -85.0), (-53.0, -85.0), (8.0, -125.0), (120.0, -125.0), (189.0, -56.0), (189.0, 35.0),
                    (96.0, 128.0), (-128.0, 128.0), (-168.0, 88.0)), h=6.0, edge=8.0),
    # the drum: centre, radius at its foot r0 and at its top r1 (the ring's outer edge), the ring's top h; the pit
    # inside the ring (radius rp) down to its floor; ribs round the side
    drum=dict(c=(68.0, 1.0), r0=100.0, r1=66.0, h=37.0, rp=43.0, floor=10.0, ribs=24, lip=1.5, bulge=0.70),
    # the emitter in the pit: a column, a collar, four prongs out to the pit's wall
    mech=dict(r=9.0, h=30.0, collar=(14.0, 18.0, 23.0), prongs=4, pr=3.0, plen=34.0, pz=20.0),
    # struts leaning against the drum: azimuths (deg, 0 = east, 90 = south), from the ring's edge (z top) out to the
    # base (R out)
    struts=dict(az=(-10.0, 35.0, 80.0, 150.0, 200.0, 250.0), top=39.0, rtop=66.0, out=112.0, r=3.4),
    # the fins: foot centre (x, y) on the base, lean azimuth (deg) and tilt from vertical (deg), length, width,
    # thickness; the tip's lamp (GTFIRE_C)
    # (the width tapers from w at the foot to w1 at the tip; `face` turns the broad face about the fin's axis, deg)
    fins=(dict(foot=(-100.0, 34.7), az=186.7, tilt=19.5, L=110.0, w=60.0, w1=26.0, t=16.0, face=70.0, bevel=9.0),
          dict(foot=(-78.0, -30.0), az=172.0, tilt=24.0, L=124.0, w=60.0, w1=28.0, t=16.0, face=70.0, bevel=9.0)),
    # the clamps round the fins' feet: height, how far they stand out of the fin
    clamps=dict(h=30.0, out=7.0),
    # the hatch: its foot along the ground (x from, x to, y), it slopes up to (y, z) against the drum
    # the hatch: a panel on the drum's sloping side: its azimuth (deg, 90 = south), width, from the ring (r 0) out
    # to r 1 (over the drum's foot onto the base), standing t proud
    hatch=dict(az=94.0, w=47.5, r=(66.0, 116.5), t=2.5),
    # the strip: along y at x from..to on the base
    strip=dict(x=(37.0, 97.0), y=(-109.0, -104.0), h=4.0),
    lamps=dict(r=5.5, down=3.0),
    # the dome (GTFIRE_A / _B): its rim on the ring (radius R, z0), the lid rising h above it, a grey cap (a frustum
    # r0 -> r1, up to z top over the rim); lifted `lift` at A 19 and in B
    dome=dict(R=63.0, z0=38.5, h=30.0, cap=dict(r0=40.0, r1=27.0, top=40.0), lift=68.0, under=7.0),
    # the crane arm: pinned at the back fin's top (pivot), a thick inner boom out to a green collar (Lc from the
    # pivot), a thinner outer boom sliding out of it to the hanger over the dome's cap (hang above the cap)
    arm=dict(pivot=(-96.0, -8.0, 104.0), w_in=28.0, d_in=22.0, w_out=22.0, d_out=17.0, Lc=78.0,
             collar=dict(out=3.5, len=24.0), hang=8.0, hanger=7.0, hinge=(13.0, 34.0), hook=-22.0,
             housing=dict(size=(32.0, 34.0, 26.0), drop=8.0)),
)

LAYOUTS = {'ts': dict(turn=False), 'ra': dict(turn=False)}
BUILD_KEYS = ('slab', 'base', 'drum', 'mech', 'fins', 'struts', 'arm', 'hatch', 'paint', 'green')
DONE = {k: 1.0 for k in BUILD_KEYS}


def to_local(X, Y, layout='ts'):
    return X, Y


def to_world(x, y, layout='ts'):
    return x, y


def inbox(x, y, bx, by):
    return (x >= bx[0]) & (x <= bx[1]) & (y >= by[0]) & (y <= by[1])


def poly_sdf(x, y, poly):
    """signed distance to a convex-or-not simple polygon (negative inside), in the ground plane."""
    pts = np.asarray(poly, float)
    n = len(pts)
    d = np.full(x.shape, np.inf)
    inside = np.zeros(x.shape, bool)
    for i in range(n):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
        ex, ey = x2 - x1, y2 - y1
        t = np.clip(((x - x1) * ex + (y - y1) * ey) / (ex * ex + ey * ey), 0, 1)
        d = np.minimum(d, np.hypot(x - x1 - t * ex, y - y1 - t * ey))
        cond = ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1)
        inside ^= cond
    return np.where(inside, -d, d)


def fin_axes(q):
    th, ph = np.radians(q['tilt']), np.radians(q['az'])
    el = np.array([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)])     # along the fin, up
    ew = np.array([-np.sin(ph), np.cos(ph), 0.0])                                      # across, level
    et = np.cross(el, ew)                                                              # through its thickness
    fa = np.radians(q.get('face', 0.0))                                                # the broad face turned
    ew, et = ew * np.cos(fa) + et * np.sin(fa), -ew * np.sin(fa) + et * np.cos(fa)
    return el, ew, et


def convex_interval(x, y, planes):
    """the z interval inside a convex solid given as half-spaces n.(P - P0) <= 0 over each ground point: (lo, hi, mask)."""
    lo = np.full(x.shape, -1e9); hi = np.full(x.shape, 1e9); ok = np.ones(x.shape, bool)
    for n, p0 in planes:
        n = np.asarray(n, float); p0 = np.asarray(p0, float)
        base = n[0] * (x - p0[0]) + n[1] * (y - p0[1]) - n[2] * p0[2]       # n.(P - P0) = base + n_z z
        if abs(n[2]) < 1e-9:
            ok &= base <= 0
        elif n[2] > 0:
            hi = np.minimum(hi, -base / n[2])
        else:
            lo = np.maximum(lo, -base / n[2])
    ok &= hi > lo
    return np.where(ok, lo, 0.0), np.where(ok, hi, 0.0), ok


def fin_planes(q, foot, L, grow=0.0, h=None):
    """a fin as half-spaces: thickness t, width tapering from w (foot) to w1 (tip) over L, from its foot up to L (or h);
    grow: stand that much out all round (the clamps)."""
    el, ew, et = fin_axes(q)
    W0, W1 = q['w'] / 2.0 + grow, q['w1'] / 2.0 + grow
    k = (W0 - W1) / max(q['L'], 1e-3)
    T = q['t'] / 2.0 + grow
    top = L if h is None else h
    pl = [(et, foot + et * T), (-et, foot - et * T),
          (ew + k * el, foot + ew * W0), (-ew + k * el, foot - ew * W0),
          (el, foot + el * top), (-el, foot - el * 2.0)]
    bv = q.get('bevel', 0.0)
    if bv > 0 and h is None:
        # the tip's corners cut off at 45 degrees (a bevel bv units back from the corner), across and through
        wt = W0 - k * top
        for sgn in (1, -1):
            n_ = (el + sgn * ew) / np.sqrt(2.0)
            pl.append((n_, foot + el * top + ew * sgn * (wt - bv)))
            n_ = (el + sgn * et) / np.sqrt(2.0)
            pl.append((n_, foot + el * top + et * sgn * (T - bv * 0.5)))
    return pl


def sphere_interval(x, y, c, r):
    d2 = r * r - (x - c[0]) ** 2 - (y - c[1]) ** 2
    ok = d2 > 0
    dz = np.sqrt(np.maximum(d2, 0))
    return np.where(ok, c[2] - dz, 0.0), np.where(ok, c[2] + dz, 0.0), ok


def fin_tip(q, zb):
    el, ew, et = fin_axes(q)
    return np.array([q['foot'][0], q['foot'][1], zb - 4.0]) + el * q['L']


def bolts(p, k, z_dome):
    """GTFIRE_B frame 2k's lightning as segments (p0, p1, radius): 6 jagged arcs from the emitter's tip, some to the
    ring's inner edge, some up to the dome's underside (z_dome: its rim), seeded so every view draws the same ones."""
    rng = np.random.default_rng(1700 + 37 * k)
    d = p['drum']; m = p['mech']
    cx, cy = d['c']
    tip = np.array([cx, cy, m['h'] + 2.0])
    segs = []
    for j in range(8):
        a = rng.uniform(0, 2 * np.pi)
        if j % 3 == 2:
            rr_ = rng.uniform(10.0, d['rp'] - 8.0)
            end = np.array([cx + rr_ * np.cos(a), cy + rr_ * np.sin(a), z_dome + p['dome']['under'] * 0.6])
        else:
            rr_ = d['rp'] - 1.0
            end = np.array([cx + rr_ * np.cos(a), cy + rr_ * np.sin(a), d['h'] - rng.uniform(0.0, 6.0)])
        n = int(rng.integers(4, 7))
        pts = [tip]
        for i in range(1, n):
            t = i / n
            q = tip + (end - tip) * t
            jit = rng.normal(0, 4.5, 3); jit[2] *= 0.6
            pts.append(q + jit * np.sin(np.pi * t))
        pts.append(end)
        w = rng.uniform(1.2, 1.9)
        for a_, b_ in zip(pts[:-1], pts[1:]):
            segs.append((tuple(a_), tuple(b_), w))
        # a branch off the middle
        if rng.uniform() < 0.6:
            q = pts[len(pts) // 2]
            b2 = q + np.array([rng.normal(0, 10), rng.normal(0, 10), rng.uniform(-4, 8)])
            segs.append((tuple(q), tuple(b2), w * 0.7))
    return segs


def dome_lift(t):
    """GTFIRE_A's lift over its 20 frames (t = frame / 19): a slow start, steady, and a hold at the top (read from the
    arm's green collar rising 68 -> 51 px)."""
    t = float(np.clip(t, 0, 1))
    return float(np.clip((t * 19.0 - 1.0) / 16.0, 0, 1)) ** 1.0


def scene(X, Y, p=None, layout='ts', prog=None, arm=None, **kw):
    """arm: None (no arm or dome: GTFIRE), or the dome's lift 0 (closed) .. 1 (raised, GTFIRE_A 19 / _B)."""
    p = P if p is None else p
    g = dict(DONE); g.update(prog or {})
    x, y = to_local(X, Y, layout)
    H = np.zeros_like(X); C = np.zeros(X.shape, np.int16)
    slabs = []
    extra = {'paint': np.full(X.shape, g['paint'], np.float32), 'green': np.full(X.shape, g['green'], np.float32)}

    def put(h, comp, where=None):
        nonlocal H, C
        if where is not None:
            h = np.where(where, h, 0.0)
        win = h > H + 1e-6
        H = np.where(win, h, H); C = np.where(win, comp, C)

    cacc = {}

    def slab(top, bot, comp, where, name=''):
        # each part's intervals kept over its own box only, then packed into as few full-grid slabs as can be
        # (plug.CropAcc / pack_slabs: the same render, a fraction of the memory)
        key = name.rstrip('0123456789') or 'part'
        if key not in cacc:
            cacc[key] = CropAcc(X.shape, n=3)
        top = np.broadcast_to(np.asarray(top, np.float32), X.shape); bot = np.broadcast_to(np.asarray(bot, np.float32), X.shape)
        cacc[key].add(np.maximum(bot, 0.0), top, comp, where & (top > bot), name)

    # ---- the base: TS's outline, its edge sloping down
    b = p['base']
    cx0, cy0 = p['drum']['c']
    k = max(float(g['slab']), 1e-3)
    # the build-up's slab spreads out from the pit (scaled about it), a hole where the drum will stand until it rises
    sd = poly_sdf(cx0 + (x - cx0) / k, cy0 + (y - cy0) / k, b['poly']) * k
    gb = float(np.clip(g['base'], 0, 1))
    if gb > 0 and g['slab'] > 0:
        hb = b['h'] * gb * np.clip(-sd / b['edge'], 0, 1) ** 0.6
        hole = (np.hypot(x - cx0, y - cy0) < b.get('hole', 66.0) * min(k, 1.0)) & (g['drum'] <= 0)
        put(np.where((sd < 0) & ~hole, np.maximum(hb, 0.4), 0.0), BASE)
    zb = b['h'] * gb
    # ---- the drum, its ring and the pit
    d = p['drum']
    cx, cy = d['c']
    rr = np.hypot(x - cx, y - cy)
    gd = float(np.clip(g['drum'], 0, 1))
    if gd > 0:
        hd_ = d['h'] * gd
        # the sloping side from r0 (the foot) up to r1 (the ring's outer edge)
        side = (rr <= d['r0']) & (rr > d['r1'])
        zs = hd_ * np.clip((d['r0'] - rr) / max(d['r0'] - d['r1'], 1e-3), 0, 1) ** d.get('bulge', 1.0)
        put(np.where(side, zs, 0.0), DRUM)
        ring = (rr <= d['r1']) & (rr > d['rp'])
        put(np.where(ring, hd_ + d['lip'] * gd * (rr > d['r1'] - 4.0), 0.0), RING)
        # the pit: its wall (the ring's inner face) down to the floor; the floor
        pit = rr <= d['rp']
        put(np.where(pit, max(d['floor'], zb) * gd, 0.0), PITF)
    # ---- the emitter in the pit
    m = p['mech']
    gm = float(np.clip(g['mech'], 0, 1))
    if gm > 0:
        put(np.where(rr <= m['r'], m['h'] * gm, 0.0), MECH)
        c0, c1, cz = m['collar']
        put(np.where((rr <= c0), cz * gm, 0.0), MECH)
        ang = np.arctan2(y - cy, x - cx)
        for k in range(m['prongs']):
            a = np.radians(45.0 + 90.0 * k)
            p0 = (cx, cy, m['pz'] * gm); p1 = (cx + np.cos(a) * m['plen'], cy + np.sin(a) * m['plen'], m['pz'] * gm - 4.0)
            lo, hi, mm = rod_interval(x, y, p0, p1, m['pr'])
            slab(hi, lo, MECH, mm, 'prong')
    # ---- the struts against the drum
    s = p['struts']
    if g['struts'] > 0:
        for az in s['az']:
            a = np.radians(az)
            top = (cx + np.cos(a) * s.get('rtop', d['r1'] - 2.0), cy + np.sin(a) * s.get('rtop', d['r1'] - 2.0), s['top'])
            foot = (cx + np.cos(a) * s['out'], cy + np.sin(a) * s['out'], zb)
            t = float(np.clip(g['struts'], 0, 1))
            tip = tuple(np.array(foot) + t * (np.array(top) - np.array(foot)))
            lo, hi, mm = rod_interval(x, y, foot, tip, s['r'])
            slab(hi, lo, STRUT, mm, 'strut')
    # ---- the fins and their clamps
    gf = float(np.clip(g['fins'], 0, 1))
    if gf > 0:
        for i, q in enumerate(p['fins']):
            L = q['L'] * gf
            foot = np.array([q['foot'][0], q['foot'][1], zb - 4.0])
            lo, hi, mm = convex_interval(x, y, fin_planes(q, foot, L))
            slab(hi, lo, FIN, mm, f'fin{i}')
            cq = p['clamps']
            lo, hi, mm = convex_interval(x, y, fin_planes(q, foot, L, grow=cq['out'], h=min(cq['h'], L)))
            slab(hi, lo, CLAMP, mm, f'clamp{i}')
    # ---- the hatch: a panel on the drum's sloping side, running out over its foot onto the base
    h_ = p['hatch']
    if g['hatch'] > 0 and gd > 0:
        a = np.radians(h_['az'])
        along = (x - cx) * np.cos(a) + (y - cy) * np.sin(a)                # out from the drum's axis
        across = -(x - cx) * np.sin(a) + (y - cy) * np.cos(a)
        on = (np.abs(across) <= h_['w'] / 2.0) & (along >= h_['r'][0]) & (along <= h_['r'][1])
        zsd = d['h'] * gd * np.clip((d['r0'] - rr) / max(d['r0'] - d['r1'], 1e-3), 0, 1) ** d.get('bulge', 1.0)
        zsd = np.where(rr <= d['r1'], d['h'] * gd, zsd)
        put(np.where(on, np.maximum(zsd, zb) + h_['t'] * float(np.clip(g['hatch'], 0, 1)), 0.0), HATCH)
    # ---- the strip behind the drum
    st = p['strip']
    put(np.where(inbox(x, y, st['x'], st['y']), zb + st['h'], 0.0), STRIP, where=np.full(X.shape, g['hatch'] >= 1.0))
    # ---- the lamps at the fins' tips (GTFIRE_C)
    if gf >= 1.0:
        for i, q in enumerate(p['fins']):
            tip = fin_tip(q, zb)
            lo, hi, mm = sphere_interval(x, y, tip - np.array([0, 0, p['lamps']['down']]), p['lamps']['r'])
            slab(hi, lo, LAMP, mm, f'lamp{i}')
    # ---- the dome and the crane arm (GTFIRE_A / _B; none on GTFIRE itself)
    if arm is not None and g['arm'] > 0:
        dm = p['dome']
        lift = dm['lift'] * float(arm)
        z0 = dm['z0'] + lift
        R = dm['R']
        inl = rr <= R
        lid = z0 + dm['h'] * np.sqrt(np.clip(1.0 - (rr / R) ** 2, 0, 1))
        cq = dm['cap']
        zt = z0 + cq['top']
        capz = zt - (zt - (z0 + dm['h'] * np.sqrt(np.clip(1 - (cq['r0'] / R) ** 2, 0, 1)))) * \
            np.clip((rr - cq['r1']) / (cq['r0'] - cq['r1']), 0, 1)
        capm = rr <= cq['r0']
        bot = z0 + dm['under'] * np.clip(1.0 - (rr / (R - 6.0)) ** 2, 0, 1)
        slab(np.where(capm, np.maximum(capz, lid), lid), bot, np.where(capm & (capz >= lid), DOMEC, DOME), inl, 'L:dome')
        # the arm: a box beam from the pivot, the inner section out to the green collar, the outer section sliding
        # out of it to the dome's cap, where it hangs on a short hanger
        a_ = p['arm']
        P0 = np.array(a_['pivot'], float)
        Hk = np.array([cx + a_.get('hook', 0.0), cy, zt + a_['hang']])          # over the cap's west side
        u = Hk - P0; Lh = np.linalg.norm(u); u = u / Lh
        side = np.cross(u, [0, 0, 1.0]); side = side / max(np.linalg.norm(side), 1e-6)
        upv = np.cross(side, u)
        Lc = min(a_['Lc'], Lh - 4.0)

        def beam(p0, p1, w, dpt, comp, name):
            c_ = (p0 + p1) / 2.0; L_ = np.linalg.norm(p1 - p0)
            lo, hi, mm = obox_interval(x, y, c_, (u, side, upv), (L_ / 2.0, w / 2.0, dpt / 2.0))
            slab(hi, lo, comp, mm, name)
        beam(P0 - u * 6.0, P0 + u * Lc, a_['w_in'], a_['d_in'], ARM, 'boom')
        beam(P0 + u * (Lc - 8.0), Hk + u * 4.0, a_['w_out'], a_['d_out'], ARM, 'boom2')
        cl = a_['collar']
        beam(P0 + u * (Lc - cl['len']), P0 + u * Lc, a_['w_in'] + 2 * cl['out'], a_['d_in'] + 2 * cl['out'], ARMG, 'collar')
        lo, hi, mm = rod_interval(x, y, Hk, np.array([Hk[0], Hk[1], zt - 2.0]), a_['hanger']); slab(hi, lo, ARM, mm, 'L:hanger')
        # the hinge at the pivot: a short thick drum across the arm
        hr, hl = a_['hinge']
        lo, hi, mm = rod_interval(x, y, P0 - side * hl / 2.0, P0 + side * hl / 2.0, hr); slab(hi, lo, ARM, mm, 'L:hinge')
        # the housing the arm turns in, on the back fin's top (it doesn't turn)
        hs = a_.get('housing')
        if hs:
            uh = np.array([u[0], u[1], 0.0]); uh /= max(np.linalg.norm(uh), 1e-6)
            sh = np.array([-uh[1], uh[0], 0.0])
            lo, hi, mm = obox_interval(x, y, P0 - np.array([0, 0, hs['drop']]), (uh, sh, np.array([0, 0, 1.0])),
                                       (hs['size'][0] / 2, hs['size'][1] / 2, hs['size'][2] / 2))
            slab(hi, lo, ARM, mm, 'housing')
        # ---- GTFIRE_B's lightning (bolt = 0..7): crackling arcs from the emitter's tip out to the ring's inner edge
        #      and up to the raised dome's underside
        if kw.get('bolt') is not None:
            for seg in bolts(p, int(kw['bolt']), z0):
                lo, hi, mm = rod_interval(x, y, seg[0], seg[1], seg[2]); slab(hi, lo, EMIT, mm, 'bolt')
    return hd.Scene(H, C, pack_slabs(cacc.values(), X.shape), extra)


COLORS = {BASE: (150, 110, 70), DRUM: (130, 100, 60), RING: (160, 160, 190), PIT: (40, 40, 44), PITF: (40, 40, 44),
          MECH: (90, 90, 96), EMIT: (200, 200, 255), STRUT: (170, 170, 200), FIN: (140, 105, 65), FINE: (160, 160, 190),
          CLAMP: (0, 214, 0), HATCH: (0, 214, 0), STRIP: (0, 214, 0), ARM: (70, 70, 74), ARMG: (0, 214, 0),
          DOME: (170, 140, 90), DOMEC: (130, 130, 136), LAMP: (200, 200, 255), SLAB: (170, 170, 170), HATCHF: (60, 60, 60)}
