"""Materials for the Radar: albedo, normal tweaks and glow per pixel of an hd.Render.  House green 0,214,0 x
(1 + 1.1 grain) on the south-west block's top, the south box and the east ramp's panels, as on every building.
Colours read from GTRADR / GTRADR_A: a dark khaki-brown building (tan plinth and blocks with dark grooves, a ribbed deck
with rust, blue-grey steel legs and posts, a gold-tan dome, a cream dish blotched with rust, lavender-grey antennas
with tan tips, a light rail along the ramp, dark red machinery under it).
The dish, its struts and rods and the antennas get exact normals (they are thin or curved: the heightfield's normals
can't follow them).
Build-up (GTRADRMK): TS draws the building grey, fades its colours in over its frames 15-17 and adds the house green at
18 (paint 0 grey .. 1 coloured; green only at paint 1)."""
import numpy as np
from walls2 import sample, smoothstep, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME
import radr as M

GREEN = np.array([0, 214, 0.])
TAN = np.array([176, 166, 110.])
TAN_L = np.array([182, 172, 120.])
TAN_D = np.array([128, 120, 82.])
KHAKI = np.array([166, 156, 106.])
GROOVE = np.array([46, 40, 30.])
RUST = np.array([132, 94, 58.])
RUST_D = np.array([92, 66, 44.])
STEEL = np.array([176, 178, 192.])           # blue-grey steel (legs, posts, trim)
STEEL_L = np.array([200, 202, 214.])
DARKC = np.array([170, 160, 132.])
BLACK = np.array([26, 24, 22.])
MACHC = np.array([206, 198, 166.])           # the light machinery box
PIPEC = np.array([214, 212, 206.])
DOMEC = np.array([188, 166, 106.])
DOMED = np.array([130, 110, 68.])
CREAM = np.array([140, 134, 104.])
CREAM_D = np.array([130, 122, 94.])
MASTC = np.array([196, 194, 226.])           # lavender-grey
MASTTIPC = np.array([204, 154, 84.])
STRUTC = np.array([124, 116, 92.])
RAIL = np.array([176, 176, 168.])
REDM = np.array([84, 40, 30.])
MKGREY = np.array([168, 168, 170.])
GRIME = np.array([96, 88, 64.])


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


def _dish(r):
    az = r.field('dish_az', np.nan)
    ok = np.isfinite(az)
    if not ok.any():
        return None
    a = float(np.median(az[ok]))
    return M.dish_frame(M.P, a, r.mk.get('layout', 'ts'))


def toward_camera(v):
    return np.array([v.T[0] * v.cE, v.T[1] * v.cE, v.sE])


def materials(r, p=None, occ=None, **kw):
    p = M.P if p is None else p
    x, y = M.to_local(r.x, r.y, r.mk.get('layout', 'ts'))
    z, comp = r.z, r.comp
    nx, ny, nz = r.nx, r.ny, r.nz
    top = nz > 0.75
    fine = sample(NOISE_FINE, np.where(top, x, x + y), np.where(top, y, z))
    mott = sample(NOISE_MOTTLE, np.where(top, x, x + y) * 0.7 + 31, np.where(top, y, z) * 0.7 + 17)
    grain = fine * 0.035 + mott * 0.05
    g1 = (1 + grain)[..., None]
    shape = x.shape
    alb = np.zeros(shape + (3,), np.float32)
    bx = np.zeros(shape, np.float32); by = np.zeros(shape, np.float32); bz = np.zeros(shape, np.float32)
    emit = np.zeros(shape + (3,), np.float32)
    rust_n = smoothstep(0.15, 1.3, sample(NOISE_GRIME, x * 0.7 + 7, (y + z) * 0.7 + 3))
    house = GREEN * (1 + 1.1 * grain)[..., None]
    side = ~top & (nz > -0.5)
    cam = toward_camera(r.view)

    def put(mask, col):
        nonlocal alb
        alb = np.where(mask[..., None], col, alb)

    def set_normal(mask, n):
        nonlocal bx, by, bz
        # face the camera (a thin shell or rod is seen from whichever side faces it)
        f = np.sign(n[..., 0] * cam[0] + n[..., 1] * cam[1] + n[..., 2] * cam[2])
        f = np.where(f == 0, 1.0, f)
        n = n * f[..., None]
        bx = np.where(mask, n[..., 0] - nx, bx); by = np.where(mask, n[..., 1] - ny, by); bz = np.where(mask, n[..., 2] - nz, bz)

    # ---- the plinth: tan concrete, dark seams on a grid, a blue-grey steel trim round its foot
    pl = comp == M.PLINTH
    seam = (phase(x, 32.0, 0.0) < 0.9) | (phase(y, 32.0, 0.0) < 0.9)
    pc = mix(TAN * g1 * (1 - 0.2 * (seam & top))[..., None], GRIME, 0.25 * rust_n)
    put(pl, np.where(side[..., None], mix(np.array([118, 120, 136.]) * g1, TAN_D * g1, 0.3), pc))
    # ---- tan blocks (south-west block, east base): khaki sides with horizontal grooves, a light lip at the top,
    #      grime at the foot; the tops tan with panel seams
    tb = comp == M.TAN
    groove = phase(z, 9.0, 2.0) < 1.0
    lip = smoothstep(0.92, 0.55, nz) * (nz > 0.3)                              # the chamfer
    wall = mix(KHAKI * g1 * (1 - 0.55 * groove)[..., None], GRIME, smoothstep(22.0, 5.0, z) * 0.5)
    topc = mix(TAN * g1 * (1 - 0.25 * (seam & top))[..., None], RUST * g1, 0.25 * rust_n)
    put(tb, np.where(side[..., None], wall, np.where((lip > 0.2)[..., None], TAN_L * g1, topc)))
    bz -= 0.3 * groove * tb * side
    # ---- house green: the south-west block's top (bevelled), the south box, the ramp's panels (seams between them)
    put(comp == M.GTOP, house)
    sb = comp == M.SBOX
    sseam = (phase(z, 11.0, 2.0) < 0.6) & side
    put(sb, house * (1 - 0.14 * sseam)[..., None])
    rg = comp == M.RAMPG
    ra = p['ramp']
    rseam = (phase(y - ra['y'][0], 16.0, 0.0) < 1.0)
    put(rg, np.where(side[..., None], REDM * g1, house * (1 - 0.16 * rseam)[..., None]))
    bz -= 0.25 * rseam * rg
    # the rail along the ramp's east edge: light steel
    hp = comp == M.HOOP
    q_ = p['ramp']
    u_ = np.clip((y - q_['ycurve']) / (q_['y'][1] - q_['ycurve']), 0, 1)
    zr_ = 5.0 + (q_['z'] - 5.0) * np.sqrt(np.clip(1 - u_ * u_, 0, None))
    railtop = z > zr_ - 1.5
    put(hp, np.where(railtop[..., None], RAIL * g1, REDM * g1))
    # ---- the rotunda: a tan stepped pedestal (a dark band under each tier's lip, steel trim), steel posts, a dark
    #      core inside them, a gold dome with ribs
    ro = comp == M.ROT
    band = side & (phase(z, 8.0, 0.0) < 1.2)
    put(ro, np.where(side[..., None], mix(TAN_D * g1, STEEL * g1, 0.3 * band), mix(TAN * g1, RUST * g1, 0.2 * rust_n)))
    put(comp == M.POST, STEEL * g1)
    dm = comp == M.DOME
    if dm.any():
        q = p['rotunda']
        ang = np.arctan2(y - q['c'][1], x - q['c'][0])
        rib = np.abs(((ang / (2 * np.pi) * 16.0) % 1.0) - 0.5) > 0.42
        put(dm, mix(DOMEC * g1, DOMED * g1, 0.5 * rib + 0.2 * rust_n))
    # ---- the tower: blue-grey legs, a dark core with panel lines, the light machinery box, a grey pipe
    put(comp == M.LEG, mix(STEEL * g1, BLACK, 0.25 * (phase(z, 14.0, 0.0) < 1.0)))
    # the deck's shade lies on the tower's middle: TS draws it lit, so its parts are a touch lighter
    dk = comp == M.DARK
    rib = phase(x - y, 10.0, 0.0) < 1.6
    put(dk, np.array([150, 146, 132.]) * 1.2 * g1 * (1 - 0.3 * (phase(z, 12.0, 0.0) < 1.0) - 0.25 * rib)[..., None])
    mc = comp == M.MACH
    # machinery: the light box under the deck's west end; the blocks on the deck dark olive with steel bits
    ondeck = z > p['deck']['z'][1] - 2.0
    pline = (phase(z, 11.0, 3.0) < 1.0) | (phase(x + y, 26.0, 0.0) < 1.2)
    light = mix(MACHC * g1, RUST_D * g1, 0.25 * rust_n) * (1 - 0.3 * pline)[..., None]
    olive = mix(np.array([150, 144, 104.]) * g1, STEEL * g1, 0.35 * (phase(x - y, 18.0, 0.0) < 4.0)) * (1 - 0.35 * pline)[..., None]
    put(mc, np.where(ondeck[..., None], olive, light))
    put(comp == M.PIPE, PIPEC * g1)
    # ---- the deck: a ribbed khaki top (rails along x, plates), rust; its sides banded, its underside dark
    de = comp == M.DECK
    rails = phase(y, 8.0, 0.0) < 2.0
    plates = (phase(x, 31.0, 0.0) < 1.2) | (phase(y, 42.0, 0.0) < 1.2)
    dtop = mix(TAN * 1.2 * g1 * (1 - 0.38 * rails - 0.35 * plates)[..., None], RUST * 1.2 * g1, 0.45 * rust_n)
    lipd = smoothstep(p['deck']['z'][1] - 7.0, p['deck']['z'][1] - 3.0, z)                 # a light lip along the top
    dsid = mix(KHAKI * g1 * (1 - 0.6 * (phase(z, 6.0, 0.0) < 1.2))[..., None], DARKC * g1, smoothstep(126.0, 112.0, z) * 0.7)
    dsid = mix(dsid, TAN_L * g1, 0.8 * lipd)
    put(de, np.where(top[..., None], dtop, np.where(side[..., None], dsid, DARKC * 0.8 * g1)))
    bz -= 0.25 * rails * de * top
    put(comp == M.DECKS, mix(TAN_D * g1, STEEL * g1, 0.3))
    put(comp == M.TURRET, mix(np.array([186, 184, 180.]) * g1, BLACK, 0.4 * (phase(z, 10.0, 0.0) < 1.2)))
    # ---- the antennas: lavender-grey, dark joints, tan tips; exact cylinder normals
    ma = comp == M.MAST
    if ma.any():
        ms = p['masts']
        pts = np.array([(q[0], q[1]) for q in ms['pts']])
        d2 = (x[..., None] - pts[:, 0]) ** 2 + (y[..., None] - pts[:, 1]) ** 2
        k = np.argmin(d2, axis=-1)
        cx, cy = pts[k, 0], pts[k, 1]
        tipz = np.array([q[4] for q in ms['pts']])[k]
        joint = phase(z, 26.0, 0.0) < 1.5
        tip = z > tipz - 9.0
        put(ma, np.where(tip[..., None], MASTTIPC * g1, np.where(joint[..., None], BLACK, MASTC * g1)))
        rx, ry = x - cx, y - cy
        rl = np.hypot(rx, ry) + 1e-6
        n = np.stack([rx / rl, ry / rl, np.zeros_like(rx)], -1)
        set_normal(ma & ~top, n)
    # ---- the dish: cream, blotched with rust, a darker band at its rim, panel seams (rings and gores); exact
    #      normals from its paraboloid; struts and rods dark brown with exact normals
    df = _dish(r)
    ds = comp == M.DISH
    if df is not None and ds.any():
        P = np.stack([x - df['C'][0], y - df['C'][1], z - df['C'][2]], -1)
        n = df['n']
        w = P @ n
        rho = np.sqrt(np.maximum((P * P).sum(-1) - w * w, 0))
        R = p['dish']['R']
        u1 = np.cross(n, [0, 0, 1.0]); u1 /= np.linalg.norm(u1); u2 = np.cross(n, u1)
        ang = np.arctan2(P @ u2, P @ u1)
        ring = np.abs(((rho / R) * 5.0) % 1.0 - 0.5) > 0.47
        gore = np.abs(((ang / (2 * np.pi)) * 18.0) % 1.0 - 0.5) > 0.46
        rim = rho > R - 7.0
        blot = smoothstep(0.1, 1.2, sample(NOISE_GRIME, rho * 1.3 + 11, ang * 40.0))
        blot2 = smoothstep(0.35, 1.0, sample(NOISE_MOTTLE, rho * 0.9 + 3, ang * 28.0 + 5))
        dc = mix(CREAM * g1, np.array([104, 92, 58.]) * g1, 0.55 * blot + 0.4 * blot2)
        dc = mix(dc, CREAM_D * g1, 0.5 * (ring | gore))
        dc = np.where(rim[..., None], mix(dc, RUST_D * g1, 0.6), dc)
        put(ds, dc)
        set_normal(ds, M.dish_normal(x, y, z, df))
    rods = np.isin(comp, [M.STRUT, M.ROD, M.ARM, M.FEED])
    if df is not None and rods.any():
        put(comp == M.STRUT, STRUTC * g1)
        put(comp == M.ROD, BLACK * 1.4 * g1)
        put(comp == M.FEED, mix(np.array([170, 164, 140.]) * g1, BLACK, 0.4 * (phase(z, 5.0, 0.0) < 1.0)))
        put(comp == M.ARM, mix(np.array([186, 184, 180.]) * g1, BLACK, 0.3))
        segs = M.dish_rods(p, df)
        best = np.full(shape, 1e9, np.float32); nn = np.zeros(shape + (3,), np.float32)
        Pp = np.stack([x, y, z], -1)
        for (a0, a1, rr, c) in segs:
            dvec = a1 - a0; L = np.linalg.norm(dvec); dvec = dvec / L
            t = np.clip((Pp - a0) @ dvec, 0, L)
            foot = a0 + t[..., None] * dvec
            rad = Pp - foot
            dist = np.linalg.norm(rad, axis=-1)
            better = dist < best
            best = np.where(better, dist, best)
            nn = np.where(better[..., None], rad / (dist[..., None] + 1e-6), nn)
        set_normal(rods, nn)
    # ---- the build-up's grey: TS's GTRADRMK is plain grey until its colours fade in (paint < 1); house green only at 1
    paint = r.field('paint', 1.0)
    if np.any(paint < 1):
        hs = np.isin(comp, list(M.HOUSE))
        pnt = np.where(hs, (paint >= 1.0).astype(np.float32), np.clip(paint, 0, 1))
        alb = mix(MKGREY * g1, alb, pnt)
    return alb, (bx, by, bz), emit


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, list(M.HOUSE))
