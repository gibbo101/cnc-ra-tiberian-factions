"""Materials for the Helipad: albedo, normal tweaks and glow per pixel of an hd.Render.  House green 0,214,0 x
(1 + 1.1 grain) on the landing circle's ring, the fuel tanks and the stripe at the machinery block's foot.
Colours read from GTHPAD / GTHPADBB: a tan concrete pad, a black landing circle with white markings (a cross, a dashed
ring), pink-tan steps, dark railing posts; tan machinery lit white-pink on its south faces, dark at its foot; green
tanks, grey pipes; the control box white-pink in front, tan, a dark window band.
The approach lights (GTHPAD_A) are grey glass in the frames; lights=t lights them as TS does (8 frames: a light runs
in from the four ends of the cross to the middle; on the damaged pad some are broken)."""
import numpy as np
from walls2 import sample, smoothstep, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME
import hpad as M

GREEN = np.array([0, 214, 0.])
TAN = np.array([180, 160, 108.])
TAN_L = np.array([212, 192, 134.])
TAN_D = np.array([138, 122, 82.])
SEAM = np.array([110, 96, 64.])
BLACKP = np.array([26, 26, 26.])
WHITE = np.array([206, 206, 206.])
PINK = np.array([232, 186, 168.])
PINK_D = np.array([176, 136, 120.])
RAILC = np.array([72, 60, 48.])
WHITEB = np.array([242, 232, 208.])          # the machinery's lit faces (TS: white-pink)
DARKF = np.array([40, 38, 36.])
PIPEC = np.array([120, 122, 126.])
STEEL = np.array([150, 152, 160.])
GLASS = np.array([104, 104, 104.])
LAMP = np.array([255, 255, 250.])
MKGREY = np.array([168, 168, 170.])
GRIME = np.array([110, 100, 72.])

# GTHPAD_A: per frame, the level of the lights on each ring of the cross (4 = the outer ends .. 1, 0 = the middle)
LEVELS = {4: (0, 1, .62, .35, .12, 0, 0, 0), 3: (0, 0, 1, .62, .35, .12, 0, 0), 2: (0, 0, 0, 1, .62, .35, .12, 0),
          1: (0, 0, 0, 0, 1, .62, .35, .12), 0: (0, 0, 0, 0, 0, 1, .7, .45)}
BROKEN = {(3, 'W'), (1, 'E'), (2, 'E'), (3, 'E'), (4, 'E'), (2, 'S')}      # TS's damaged pad: these stay dark


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


def materials(r, p=None, occ=None, lights=None, level=0, **kw):
    p = M.P if p is None else p
    x, y = r.x, r.y
    z, comp = r.z, r.comp
    nx, ny, nz = r.nx, r.ny, r.nz
    top = nz > 0.75
    side = ~top & (nz > -0.5)
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

    def put(mask, col):
        nonlocal alb
        alb = np.where(mask[..., None], col, alb)

    q = p['pad']
    # ---- the pad: tan concrete slabs (seams on a grid), dirt; its sides darker; the landing circle: black, a white
    #      cross and a dashed white ring, a house-green ring round it
    pad = comp == M.PAD
    seam = (phase(x + 3.0, 32.0, 0.0) < 0.9) | (phase(y + 3.0, 32.0, 0.0) < 0.9)
    pc = mix(TAN * g1 * (1 - 0.18 * seam)[..., None], GRIME, 0.3 * rust_n)
    pc = np.where(side[..., None], mix(TAN_D * g1, SEAM * g1, 0.4 * (phase(z, 5.0, 0.0) < 0.8)), pc)
    lc = q['land']
    rr = np.hypot(x - lc['c'][0], y - lc['c'][1])
    landon = r.field('land', 1.0) > 0.5                 # the build-up paints the landing circle last (GTHPADMK 17)
    inner = top & (rr <= lc['r']) & landon
    ring = top & (rr > lc['r']) & (rr <= lc['ring']) & landon
    lx, ly = x - lc['c'][0], y - lc['c'][1]
    cross = ((np.abs(lx) < 2.6) | (np.abs(ly) < 2.6)) & (rr < lc['r'] - 4.0)
    ang = np.degrees(np.arctan2(ly, lx))
    dash = (np.abs(rr - (lc['r'] - 9.0)) < 1.8) & (np.abs(((ang + 360.0) % 22.5) - 11.25) > 4.0)
    rim = np.abs(rr - lc['r']) < 1.6
    land = np.where((cross | dash)[..., None], WHITE * g1, BLACKP * (1 + 2.0 * grain)[..., None])
    land = np.where(rim[..., None], mix(BLACKP * g1, WHITE * g1, 0.35), land)
    pc = np.where(inner[..., None], land, pc)
    pc = np.where(ring[..., None], house, pc)
    put(pad, pc)
    bz -= 0.25 * (seam & pad & top & ~inner)
    # ---- the steps: pink-tan, each tread's edge lighter, risers darker
    st = comp == M.STEPS
    put(st, np.where(top[..., None], PINK * g1, PINK_D * g1))
    put(comp == M.RAIL, RAILC * g1)
    # ---- the machinery block: tan, its south faces lit white-pink, dark at its foot, a green stripe above the foot
    bl = comp == M.BLOCK
    south = ny > 0.5
    foot = z < p['block']['foot']
    stripe = (z >= p['block']['foot']) & (z < p['block']['foot'] + 3.5) & side
    blc = np.where(south[..., None], WHITEB * g1, mix(TAN * g1, TAN_D * g1, 0.4 * side))
    blc = mix(blc, SEAM * g1, 0.3 * (phase(z, 12.0, 0.0) < 0.7) * side)
    blc = np.where(foot[..., None], DARKF * g1, blc)
    blc = np.where(stripe[..., None], house, blc)
    put(bl, blc)
    # ---- the tanks: house green, thin dark seams round them and a darker band at their tops
    tk = comp == M.TANK
    put(tk, house * (1 - 0.16 * (phase(z, 12.0, 4.0) < 0.7))[..., None])
    put(comp == M.PIPE, PIPEC * g1)
    # ---- the control box: white-pink in front (south), tan top and sides, a dark window band, a green lamp; its stand
    bx_ = comp == M.BOX
    b = p['box']
    win = side & (z > b['z'][1] - 22.0) & (z < b['z'][1] - 12.0)
    boc = np.where(south[..., None], WHITEB * g1, np.where(top[..., None], TAN_L * g1, TAN_D * g1))
    boc = np.where(win[..., None], np.array([44, 52, 60.]) * g1, boc)
    put(bx_, boc)
    put(comp == M.STAND, STEEL * g1)
    # ---- the approach lights: grey glass, lit by GTHPAD_A
    li = comp == M.LIGHT
    if li.any():
        pts = np.array(M.light_points(p))
        rings = M.light_rings()
        arms = ['W', 'N', 'S', 'E'] * 4 + ['C']
        d2 = (x[..., None] - pts[:, 0]) ** 2 + (y[..., None] - pts[:, 1]) ** 2
        k = np.argmin(d2, axis=-1)
        if lights is None:
            put(li, GLASS * g1)
        else:
            lev = np.array([0.0 if (level and (rings[i], arms[i]) in BROKEN) else LEVELS[rings[i]][lights % 8]
                            for i in range(len(pts))], np.float32)[k]
            put(li, mix(GLASS * g1, LAMP, lev))
            emit = np.where(li[..., None], np.array([150, 150, 146.]) * lev[..., None], emit)
    # ---- the build-up's pieces: the pyramid of panels and the dome, white-pink as TS's
    sl = comp == M.SLAB
    put(sl, mix(np.array([236, 228, 214.]) * g1, np.array([206, 178, 160.]) * g1, 0.3 * side))
    # ---- the build-up: TS's GTHPADMK is drawn in colour, so the paint is always on
    return alb, (bx, by, bz), emit


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, [M.PAD, M.TANK, M.BLOCK])
