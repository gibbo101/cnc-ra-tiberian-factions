"""Materials for the Service Depot (and the Dropship Bay's pad): albedo, normal tweaks and glow per pixel of an
hd.Render.  House green 0,214,0 x (1 + 1.1 grain) on the pad's band, the gantry's base plate, its panel and edges, the
repair arm.  Colours read from GTDEPT / GTDEPTBB (TS lit them: the albedos are TS's colours / the renderer's shading):
the pad lavender-grey concrete inside its band, a tan rim, light concrete sides; dark steel gratings; guide lines of
small lamps; the gantry's wall light grey at its south end, mid grey at its north end, a dark blue-grey top rail with
amber lamps; white hoods, dark inside; a grey box with a red lamp; a rust-brown reel.
Overlays (material only, one geometry pass):
  lights=t  GTDEPT_A: a light running along the guide lines (5 frames)
  glow=t    GTDEPT_B: the south hood's inside lit white, fading (7 frames)
  flash=t   GTDEPT_D: the pad lit white inside its band, fading (7 frames)"""
import numpy as np
from walls2 import sample, smoothstep, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME
import dept as M

GREEN = np.array([0, 214, 0.])
LAV = np.array([118, 118, 146.])            # the pad's concrete (TS 113,113,133 lit)
LAV_D = np.array([98, 98, 124.])
RIMC = np.array([140, 130, 104.])           # the rim (TS 126,121,104 lit)
DIRT = np.array([110, 92, 66.])
SKIRTC = np.array([198, 196, 188.])
GRATEC = np.array([106, 106, 126.])         # TS: only a little darker than the concrete (97-105 lit)
SLOT = np.array([86, 86, 102.])
GAPC = np.array([96, 96, 110.])
LAMPG = np.array([150, 150, 172.])          # a guide lamp, unlit (a little lighter than the concrete)
LAMPL = np.array([214, 216, 240.])
WALL_S = np.array([200, 200, 198.])         # TS 171 lit (the wall faces east, away from TS's light)
WALL_N = np.array([150, 150, 154.])
RAILC = np.array([62, 62, 82.])
STUDC = np.array([214, 172, 100.])
MACHC = np.array([72, 72, 78.])
HOODC = np.array([226, 226, 230.])
HOODIN = np.array([66, 66, 78.])
BOXC = np.array([132, 132, 138.])
REDC = np.array([226, 44, 26.])
BROWNC = np.array([122, 68, 58.])
TOOLC = np.array([138, 138, 160.])
WHITE = np.array([255, 255, 255.])
MKGREY = np.array([168, 168, 170.])

# GTDEPT_D: the pad's flash, per frame (TS: white, then back to the concrete over 7 frames)
D_LEVELS = (1.0, 0.72, 0.5, 0.32, 0.18, 0.08, 0.0)
# GTDEPT_B: the south hood's inside, per frame
B_LEVELS = (1.0, 0.7, 0.45, 0.25, 0.12, 0.04, 0.0)


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


def seg_dist(x, y, x0, y0, x1, y1):
    """distance to a segment, and the position along it (units from its start)"""
    dx, dy = x1 - x0, y1 - y0
    L = np.hypot(dx, dy)
    s = np.clip(((x - x0) * dx + (y - y0) * dy) / max(L * L, 1e-9), 0, 1) * L
    px, py = x0 + dx * s / L, y0 + dy * s / L
    return np.hypot(x - px, y - py), s, L


def lamps(x, y, q):
    """the guide lamps: for each pixel, (distance to the nearest lamp centre, that lamp's index along its line, the
    line's lamp count).  Lamps sit every q['every'] along each guide line (relative to the pad's centre)."""
    cx, cy = q['c']
    lx, ly = x - cx, y - cy
    best = np.full(x.shape, 1e9); idx = np.zeros(x.shape, np.int32); line = np.zeros(x.shape, np.int32)
    for i, (x0, y0, x1, y1) in enumerate(q['lines']):
        d, s, L = seg_dist(lx, ly, x0, y0, x1, y1)
        n = max(int(L // q['every']), 1)
        k = np.clip(np.round(s / (L / n)), 0, n)
        px = x0 + (x1 - x0) * k / n; py = y0 + (y1 - y0) * k / n
        dd = np.hypot(lx - px, ly - py)
        win = dd < best
        best = np.where(win, dd, best); idx = np.where(win, k, idx); line = np.where(win, i, line)
    return best, idx, line


def materials(r, p=None, occ=None, lights=None, glow=None, flash=None, level=0, **kw):
    p = M.P if p is None else p
    lay = r.mk.get('layout', 'ts')
    x, y = M.to_local(r.x, r.y, lay)
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
    house = GREEN * (1 + 1.1 * grain)[..., None]
    grime = smoothstep(0.15, 1.3, sample(NOISE_GRIME, x * 0.7 + 7, (y + z) * 0.7 + 3))

    def put(mask, col):
        nonlocal alb
        alb = np.where(mask[..., None], col, alb)

    q = p['pad']
    cx, cy = q['c']
    # ---- the pad: lavender concrete inside the band (slab joints, mottle), a tan rim with dirt, light sides
    inner = np.isin(comp, [M.PAD, M.GRATE, M.GAP])
    joint = (phase(x - cx + 2.0, 42.0, 0.0) < 0.9) | (phase(y - cy + 2.0, 42.0, 0.0) < 0.9)
    pc = mix(LAV * g1 * (1 - 0.1 * joint)[..., None], LAV_D * g1, 0.35 * smoothstep(0.3, 1.2, mott * 3 + 0.5))
    put(comp == M.PAD, pc)
    bz -= 0.2 * joint * (comp == M.PAD)
    rim = comp == M.RIM
    spots = smoothstep(0.35, 0.8, sample(NOISE_MOTTLE, x * 1.3 + 5, y * 1.3 + 9))
    put(rim, mix(RIMC * g1, DIRT * g1, 0.25 * grime + 0.45 * spots))
    sk = comp == M.SKIRT
    put(sk, mix(SKIRTC * g1, DIRT * g1, 0.25 * grime + 0.15 * smoothstep(6.0, 0.0, z)))
    put(comp == M.BAND, house)
    # the gratings: dark steel, slots across them; the gap between them near black
    gr = comp == M.GRATE
    slot = phase(y - cy, 6.0, 0.0) < 2.2
    put(gr, np.where(slot[..., None], SLOT * g1, GRATEC * g1))
    bz -= 0.25 * slot * gr
    put(comp == M.GAP, GAPC * g1)
    # the guide lamps: small round lamps every few units along the guide lines (TS's dotted lines); A lights them
    dl, li, ln = lamps(x, y, q)
    lampm = (comp == M.PAD) & (dl <= q['lamp_r'])
    lev = np.zeros(shape, np.float32)
    if lights is not None:
        t = int(lights) % 5
        # a light runs along every line: two lamps in five lit, moving one lamp per frame
        ph = (li - t) % 5
        lev = np.where(ph == 0, 1.0, np.where(ph == 1, 0.45, 0.0)).astype(np.float32)
    put(lampm, mix(LAMPG * g1, LAMPL, 0.75 * lev))
    emit = np.where(lampm[..., None], np.array([46, 48, 62.]) * lev[..., None], emit)
    bz += 0.5 * lampm * np.clip(1 - dl / q['lamp_r'], 0, 1)
    # GTDEPT_D: the pad lit white inside its band
    if flash is not None:
        f = D_LEVELS[int(flash) % 7]
        fl = inner | lampm
        alb = np.where(fl[..., None], mix(alb, WHITE, f * 0.85), alb)
        emit = np.where(fl[..., None], emit + np.array([140, 140, 150.]) * f, emit)
    # ---- the gantry: house-green base plate (panel seams), wall (light grey south end, mid grey north end), the
    #      house-green panel in its frame, the green edge, the dark top rail with amber lamps
    base = comp == M.BASE
    bseam = (phase(y + 63.0, 36.0, 0.0) < 1.0) | (phase(x + 187.0, 38.0, 0.0) < 1.0)
    put(base, house * (1 - 0.14 * bseam)[..., None])
    bz -= 0.3 * bseam * base
    wl = p['wall']
    wall = comp == M.WALL
    wc = np.where((y > wl['slope_y'] - 2)[..., None], WALL_S * g1, WALL_N * g1)
    wc = mix(wc, DIRT * g1, 0.25 * grime * smoothstep(30.0, 0.0, z))
    wpl = phase(z, 14.0, 0.0) < 0.9
    put(wall, wc * (1 - 0.12 * wpl)[..., None])
    for c_ in (M.GTRIM, M.FRAME):
        put(comp == c_, house)
    pnl = comp == M.PANEL
    pseam = phase(z - wl['panel']['z'][0], 15.4, 0.0) < 0.9
    put(pnl, house * (1 - 0.14 * pseam)[..., None])
    put(comp == M.RAIL, RAILC * g1 * (1 + 0.1 * top)[..., None])
    put(comp == M.STUD, STUDC * g1)
    emit = np.where((comp == M.STUD)[..., None], np.array([40, 30, 10.]), emit)
    # ---- the machine: dark block, white hoods (panel seams), their dark insides (B lights the south one)
    put(comp == M.MACH, MACHC * g1)
    hood = comp == M.HOOD
    hseam = phase(z, 11.0, 0.0) < 0.8
    put(hood, HOODC * g1 * (1 - 0.08 * hseam)[..., None])
    # the hoods' insides: the machine block's face seen through each opening (B lights the south one)
    hq = p['mach']['hoods']
    r_in = hq['w'] / 2 - hq['t']
    zs_ = hq['z'][1] - hq['w'] / 2                                      # the arches' springing height
    for k_, yc in enumerate(hq['ys']):
        dy_ = np.abs(y - yc)
        under = z <= zs_ + np.sqrt(np.clip(r_in ** 2 - np.minimum(dy_, r_in) ** 2, 0, None)) + 0.6
        op = np.isin(comp, [M.MACH, M.HOODIN, M.HOOD]) & (dy_ <= r_in + 0.6) & (x >= p['mach']['x'][1] - 1.5) & \
            (x <= hq['x'][1] + 0.5) & under
        shade_in = np.clip(0.55 + 0.45 * (z - hq['z'][0]) / (hq['z'][1] - hq['z'][0]), 0.5, 1.0)
        put(op, HOODIN * g1 * shade_in[..., None])
        if glow is not None and k_ == 0:
            gv = B_LEVELS[int(glow) % 7]
            alb = np.where(op[..., None], mix(alb, WHITE, gv), alb)
            emit = np.where(op[..., None], emit + np.array([170, 170, 176.]) * gv, emit)
    put(comp == M.HOODIN, HOODIN * g1)
    put(comp == M.BOX, BOXC * g1)
    put(comp == M.REDL, REDC)
    emit = np.where((comp == M.REDL)[..., None], np.array([90, 10, 4.]), emit)
    br = comp == M.BROWN
    band_ = phase(y, 8.0, 0.0) < 1.6
    put(br, np.where(band_[..., None], np.array([196, 190, 184.]) * g1, BROWNC * g1))
    # ---- the repair arm: a house-green lattice (dark cross members), the grey tool, the spark
    arm = comp == M.ARM
    if arm.any():
        a = p['arm']
        t = r.mk.get('arm')
        ext, ang, tang, spark = M.arm_pose(int(t) % 16) if t is not None else (1.0, 0.0, 0.0, False)
        p0 = np.array(a['p0'])
        u = np.array([np.sin(ang), 0.0, np.cos(ang)])
        s = (x - p0[0]) * u[0] + (z - p0[2]) * u[2] + a['L'] * (1 - ext)       # along the boom from its foot
        v = y - p0[1]
        lat = (np.abs(phase(s, 12.0, 0.0) - 0.0) < 1.4) | (np.abs(phase(s + v, 12.0, 0.0)) < 1.1) | \
              (np.abs(phase(s - v, 12.0, 0.0)) < 1.1)
        put(arm, house * (1 - 0.16 * lat)[..., None])
    tool = comp == M.TOOL
    put(tool, TOOLC * g1 * (1 - 0.18 * (phase(z + x, 7.0, 0.0) < 1.4))[..., None])
    sp = comp == M.SPARK
    put(sp, WHITE)
    emit = np.where(sp[..., None], np.array([255, 255, 255.]), emit)
    # ---- the build-up (GTDEPTMK draws the gantry in colour; the pad stays plain grey until its last frames)
    mk = comp == M.MKFRAME
    if mk.any():
        brace = r.field('brace', 0.0) > 0.5
        # a braced frame: X braces between the uprights (on the plate's face: its local u along y, v up the plate)
        uu = phase(y - p['wall']['y'][0], 40.0, 0.0)
        vv = np.hypot(x - p['wall']['x'][0], z)
        xb = (np.abs(uu - vv % 40.0) < 2.2) | (np.abs(uu - (40.0 - vv % 40.0)) < 2.2) | (uu < 3.0) | (vv % 40.0 < 2.5)
        put(mk, house * (1 - 0.3 * (brace & ~xb))[..., None])
    put(comp == M.SLAB, MKGREY * g1)
    ptex = r.field('padtex', 1.0)
    if np.any(ptex < 1.0):
        pm = np.isin(comp, [M.PAD, M.RIM, M.SKIRT, M.GRATE, M.GAP, M.BAND])
        plain = np.where((comp == M.RIM)[..., None], np.array([188, 186, 182.]) * g1, MKGREY * g1 * 0.82)
        alb = np.where((pm & (ptex < 1.0))[..., None], plain, alb)
        emit = np.where((pm & (ptex < 1.0))[..., None], 0.0, emit)
    return alb, (bx, by, bz), emit


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, list(M.HOUSE) + [M.FRAME, M.MKFRAME, 40, 43])
