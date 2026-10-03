"""Materials for the Firestorm Wall Section (GAFSDF): albedo, bump and glow per pixel of an hd.Render.  No house colour
(TS's section has none).  Colours read from GTFSDF's pixels:
  off       a lilac-grey steel pad (137,137,161) with a lighter rim, its sides dirty brown-grey; the dish dark (40-80)
            with the trident light in it; the gratings' rungs grey on top with blue-lit faces (125,125,206 /
            149,149,230) over dark gaps (dark olive 56,56,40 and black); grey rails and brackets
  live      (TS 32-47, the field on) the pad's rim, the rails, the brackets and the whole grating glow: blue
            (101,101,255) and light blue (153,153,255) with white glints and pure blue (0,0,255) studs round the rim;
            the dish, the ring round it and the trident stay as they are (TS's do)
  pulse=k   (GTFSDF_A, 4 frames): 0 as it is, 1 the ring round the dish glowing white with blue studs on its inner edge,
            2 the trident's prongs white, 3 the whole dish light blue with the trident white"""
import numpy as np
from walls2 import sample, smoothstep, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME
import wnoise as WN
import fsdf as M

STEEL = np.array([128, 128, 146.])
STEEL_L = np.array([150, 150, 172.])
BAND = np.array([170, 170, 192.])
STEEL_D = np.array([96, 96, 112.])
RIMC = np.array([150, 150, 176.])
DIRT = np.array([89, 80, 60.])
DISHC = np.array([50, 50, 54.])
DISH_D = np.array([30, 30, 32.])
RINGC = np.array([134, 134, 142.])
HUBC = np.array([118, 118, 126.])
PRONGC = np.array([214, 214, 226.])
RUNG = np.array([158, 158, 164.])
RUNG_F = np.array([125, 125, 206.])
RUNG_FL = np.array([149, 149, 230.])
GAP = np.array([48, 48, 36.])
BLACK = np.array([16, 16, 14.])
RAILC = np.array([150, 150, 156.])
GRIME = np.array([96, 90, 72.])
MKGREY = np.array([168, 168, 170.])
BLUE = np.array([101, 101, 255.])
BLUE_L = np.array([153, 153, 255.])
BLUE_D = np.array([85, 85, 157.])
BLUE_W = np.array([206, 206, 255.])
PURE = np.array([0, 0, 255.])
WHITE = np.array([255, 255, 255.])


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


def materials(r, p=None, occ=None, level=0, **kw):
    lay = r.mk.get('layout', 'ts')
    p = M.P if p is None else p
    x, y = M.to_local(r.x, r.y, lay)
    z, comp = r.z, r.comp
    nx, ny, nz = r.nx, r.ny, r.nz
    top = nz > 0.75
    fine = sample(NOISE_FINE, np.where(top, x, x + y), np.where(top, y, z))
    mott = sample(NOISE_MOTTLE, np.where(top, x, x + y) * 0.7 + 31, np.where(top, y, z) * 0.7 + 17)
    grain = fine * 0.035 + mott * 0.05
    g1 = (1 + grain)[..., None]
    shape = x.shape
    alb = np.zeros(shape + (3,), np.float32) + 128
    bx = np.zeros(shape, np.float32); by = np.zeros(shape, np.float32); bz = np.zeros(shape, np.float32)
    emit = np.zeros(shape + (3,), np.float32)
    live = bool(kw.get('live', r.mk.get('live', False)))
    mask = int(r.mk.get('mask', 0))

    def put(m, col):
        nonlocal alb
        alb = np.where(m[..., None], col, alb)

    def glow(m, col, k):
        nonlocal emit
        emit = np.where(m[..., None], emit + col * k, emit)

    rr = np.hypot(x, y)
    q, dq, am = p['pad'], p['dish'], p['arm']
    side = nz < 0.55
    # ---- the pad: lilac-grey steel, a seam round the dish, its sides dirty brown-grey
    pad = comp == M.PAD
    seam = np.abs(rr - dq['r'] - 1.5) < 0.6
    box = np.maximum(np.abs(x), np.abs(y))
    band = (rr <= dq['band'] + 2.0)
    put(pad, mix(np.where(band[..., None], BAND * g1, STEEL * g1), STEEL_D * g1, np.clip(0.5 * seam, 0, 1)))
    put(pad & side, mix(DIRT * g1, STEEL_D * g1, 0.35))
    # ---- the rim (the pad's raised rim and the ring round the dish)
    rim = comp == M.RIM
    ring = rim & (rr <= dq['ring']['r'][1] + 1.0)
    outer = rim & ~ring
    put(outer, np.where(top[..., None], STEEL_L * g1, mix(STEEL_D * g1, DIRT * g1, 0.5)))
    put(ring, RINGC * g1)
    # ---- the dish and the trident
    dish = comp == M.DISH
    put(dish, mix(DISHC * g1, DISH_D * g1, smoothstep(dq['r'] - 4.0, dq['r'], rr)))
    put(comp == M.HUB, mix(HUBC * g1, DISH_D * g1, 0.35 * smoothstep(0.9, 0.3, nz)))
    prong = comp == M.PRONG
    put(prong, mix(PRONGC * g1, STEEL_D * g1, 0.2 * smoothstep(0.5, -0.2, nx * 0.7 + ny * 0.7)))
    glow(prong, PRONGC, 0.18)                     # TS draws the trident light on the dark dish
    # ---- the gratings: rungs grey on top with blue-lit faces, dark gaps between (dark olive, black in the shadows)
    grate = comp == M.GRATE
    run = np.where(np.abs(y) > np.abs(x), y, x)
    if mask == 5:
        run = y
    elif mask == 10:
        run = x
    rung = M.rung_mask(run, am['bars'])
    hi = z > am['base_h'] + 0.8
    gap = grate & ~hi
    face = grate & hi & ~top
    rtop = grate & hi & top
    # the rungs' tops: grey, their camera-side half lit blue (TS's grey-and-blue rungs)
    eb = am['bars']['every']
    ph = np.mod(run + eb / 2.0, eb) - eb / 2.0
    put(rtop, np.where((ph > am['bars']['w'] * 0.05)[..., None], RUNG_F * g1, RUNG * g1))
    put(face, np.where((WN.noise(x, y, 3.0, 1701) > 0.2)[..., None], RUNG_FL * g1, RUNG_F * g1))
    gdark = smoothstep(0.1, 0.9, WN.noise(x * 0.7, y * 0.7, 4.0, 1702) * 0.5 + 0.5)
    put(gap, mix(GAP * g1, BLACK, 0.3 + 0.3 * gdark))
    # the rails and their brackets: grey steel
    rail = comp == M.RAIL
    put(rail, np.where(top[..., None], RAILC * g1, mix(STEEL_D * g1, DIRT * g1, 0.4)))
    # ---- live: the field is on - the rim, the rails, the brackets and the grating glow; the dish stays dark
    if live:
        # TS's live colours in blocks: light blue and blue by turns along the rim and the rails (4 units a block),
        # the rungs' tops light blue with white glints, their faces blue, the gaps deep blue; studs of pure blue round
        # the rim's outer edge
        per = np.where(np.abs(x) > np.abs(y), y, x)
        block = np.mod(np.floor(per / 4.0) + np.floor(np.where(np.abs(x) > np.abs(y), x, y) / 4.0), 2.0) < 1.0
        lit = outer | rail | (pad & top & (box >= dq['band']) & ~band)
        col = np.where(block[..., None], BLUE_L, BLUE)
        col = np.where(((~top) & (nz < 0.3))[..., None], BLUE_D, col)
        col = np.where((top & (WN.noise(x * 1.2, y * 1.2, 2.0, 1704) > 1.25))[..., None], BLUE_W, col)
        put(lit, col); glow(lit, col, 0.4)
        put(rtop, np.where((WN.noise(x * 1.2, y * 1.2, 2.0, 1705) > 1.0)[..., None], BLUE_W, BLUE_L))
        glow(rtop, BLUE_L, 0.45)
        put(rtop & (WN.noise(x * 1.5, y * 1.5, 1.4, 1706) > 1.8), WHITE)
        put(face, BLUE); glow(face, BLUE, 0.4)
        put(gap, mix(BLUE, BLUE_D, 0.5)); glow(gap, BLUE, 0.25)
        am_ = np.maximum(np.abs(x), np.abs(y))
        stud = (outer | pad) & top & (am_ > q['a'] - 3.2) & (am_ <= q['a'] - 0.4) & (np.mod(per + 4.0, 13.0) < 3.0)
        put(stud, PURE); glow(stud, PURE, 0.5)
    # ---- GTFSDF_A: the emitter pulsing
    k = kw.get('pulse')
    if k is not None:
        dr = dq['ring']['r']
        tri = np.isin(comp, [M.HUB, M.PRONG])
        if k % 4 == 1:
            rg = ring | (dish & (rr >= dq['r'] - 3.0))
            put(rg, np.where((rr > dr[0] - 0.5)[..., None], WHITE, BLUE_W)); glow(rg, BLUE_W, 0.8)
            st = dish & (rr >= dq['r'] - 3.0) & (np.mod(np.degrees(np.arctan2(y, x)) + 360.0, 30.0) < 9.0)
            put(st, PURE); glow(st, PURE, 0.6)
        elif k % 4 == 2:
            put(prong, WHITE); glow(prong, BLUE_W, 0.9)
        elif k % 4 == 3:
            put(dish | (comp == M.HUB), BLUE_L); glow(dish | (comp == M.HUB), BLUE_L, 0.45)
            put(ring, WHITE); glow(ring, BLUE_W, 0.5)
            put(prong, WHITE); glow(prong, WHITE, 0.6)
    # the build-up grey
    paint = r.field('paint', 1.0)
    if np.any(paint < 1):
        alb = np.where(r.hitmask[..., None], mix(MKGREY * g1, alb, np.clip(paint, 0, 1)), alb)
    if not live:
        gr = smoothstep(0.35, 1.2, sample(NOISE_GRIME, x * 0.8, y * 0.8 + z)) * 0.15 * np.isin(comp, [M.PAD, M.RAIL])
        alb = mix(alb, GRIME, gr)
    return alb, (bx, by, bz), emit


def trim_mask(r, alb):
    return np.zeros(r.hitmask.shape, bool)
