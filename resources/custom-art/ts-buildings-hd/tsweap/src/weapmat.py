"""Materials for the War Factory: albedo, bump and glow per pixel of an hd.Render.  House green 0,214,0 x (1 + 1.1 grain)
on the green panel, the west block, the fascia, the north band, the north fender's cap, the green unit and the lane's
hazard stripes, as on every building.  Textured in the building's own frame (weap.to_local), so it turns with the
layout.  Colours read from GTWEAP: a tan roof deck with dark beams, tan ridges, rust-red housings, dark machinery, two
fans, olive-tan fenders (a dark vent in the north one), a grey ribbed roll-up door with a diagonal brace, dark poles,
light grey pipes; inside the bay a dark brown hall with red lights and olive rails on the floor.
The lamps (GTWEAP_A white, GTWEAP_B orange/red) are dark glass in the building frames; lamps= lights them as TS does.
Build-up (GTWEAPMK): TS draws the building plain grey until its last two frames (paint 0 grey .. 1 coloured)."""
import numpy as np
import walls2 as W
from walls2 import sample, smoothstep, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME
import weap as M

GREEN = np.array([0, 214, 0.])
TAN = np.array([152, 132, 96.])
TAN_L = np.array([158, 140, 102.])
TAN_D = np.array([128, 110, 80.])
KHAKI = np.array([168, 150, 106.])
RUST = np.array([142, 70, 48.])
RUST_D = np.array([96, 46, 34.])
DARKM = np.array([70, 68, 66.])
BEAMC = np.array([58, 54, 50.])
FRAMEC = np.array([64, 64, 66.])
OLIVE = np.array([222, 200, 146.])
OLIVE_D = np.array([176, 156, 112.])
STEEL = np.array([236, 236, 240.])
STEEL_D = np.array([160, 160, 166.])
PIPEC = np.array([176, 178, 182.])
INSIDE = np.array([100, 86, 66.])
RAIL = np.array([128, 122, 96.])
FLOORC = np.array([62, 60, 56.])
GLASS_A = np.array([78, 78, 76.])
GLASS_B = np.array([86, 86, 86.])
FANC = np.array([84, 78, 68.])
LBEAM = np.array([104, 66, 48.])          # the lamp beam over the door: rust brown, as TS's ridge
GREYM = np.array([86, 82, 74.])
MACHC = np.array([146, 92, 62.])          # the roof's rust housings, a browner rust (TS's read khaki-brown there)           # the roof's grey machinery (TS: grey-brown, not near black)
PADC = np.array([206, 202, 184.])
SAND = np.array([200, 172, 118.])
PATCH = np.array([118, 118, 120.])
SEAMC = np.array([150, 128, 92.])
BLACK = np.array([28, 28, 26.])
REDC = np.array([150, 34, 22.])
SLABC = np.array([156, 156, 158.])
MKGREY = np.array([168, 168, 170.])        # TS's build-up grey
GRIME = np.array([112, 104, 78.])

# GTWEAP_A: five white lamps, a light running up and down them (16 frames), levels 0 (off) .. 4
A_LEVELS = (0.0, 0.21, 0.4, 0.71, 1.0)
A_SEQ = ((0, 0, 0, 1, 3), (0, 0, 0, 4, 2), (0, 0, 1, 3, 1), (0, 0, 4, 2, 0), (0, 1, 3, 1, 0), (0, 4, 2, 0, 0),
         (1, 3, 1, 0, 0), (4, 2, 0, 0, 0), (3, 1, 0, 0, 0), (2, 4, 0, 0, 0), (1, 3, 1, 0, 0), (0, 2, 4, 0, 0),
         (0, 1, 3, 1, 0), (0, 0, 2, 4, 0), (0, 0, 1, 3, 1), (0, 0, 0, 2, 4))
# RA round 2 (Luke): four lamps (the end one over the old north fender gone), the light run as the mod reordered TS's
# 16 frames for them: TS frames 0 1 2 3 4 5 5 9 10 11 12 13 14 15 0 0 (lamp 0 left out)
A_MAP_SYM = (0, 1, 2, 3, 4, 5, 5, 9, 10, 11, 12, 13, 14, 15, 0, 0)
# GTWEAP_B: three lamps, the outer two against the middle one (8 frames): off, dim, mid, bright, hot
B_COL = (np.array([86, 86, 86.]), np.array([129, 43, 24.]), np.array([190, 40, 0.]), np.array([244, 73, 0.]),
         np.array([255, 179, 42.]))
B_OUT = (4, 3, 2, 1, 0, 1, 2, 3)
B_MID = (0, 1, 2, 3, 4, 3, 2, 1)
FAN_BLADES = 6


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


def layout_of(r):
    return r.mk.get('layout', 'ts')


def materials(r, p=None, occ=None, lampsA=None, lampsB=None, fans=0, **kw):
    lay = layout_of(r)
    p = M.P if p is None else p
    x, y = M.to_local(r.x, r.y, lay)
    sym = M.LAYOUTS[lay].get('sym', False)
    ym = np.where(y < M.YC, 2 * M.YC - y, y) if sym else y           # RA round 2: the mirrored side's coordinates
    z, comp = r.z, r.comp
    nx, ny, nz = r.nx, r.ny, r.nz
    # local normals (the layout turns the building)
    if M.LAYOUTS[lay]['turn']:
        lnx, lny = ny, -nx
    else:
        lnx, lny = nx, ny
    top = nz > 0.75
    fine = sample(NOISE_FINE, np.where(top, x, x + y), np.where(top, y, z))
    mott = sample(NOISE_MOTTLE, np.where(top, x, x + y) * 0.7 + 31, np.where(top, y, z) * 0.7 + 17)
    grain = fine * 0.035 + mott * 0.05
    g1 = (1 + grain)[..., None]
    shape = x.shape
    alb = np.zeros(shape + (3,), np.float32)
    bx = np.zeros(shape, np.float32); by = np.zeros(shape, np.float32); bz = np.zeros(shape, np.float32)
    emit = np.zeros(shape + (3,), np.float32)

    def put(mask, col):
        nonlocal alb
        alb = np.where(mask[..., None], col, alb)

    house = GREEN * (1 + 1.1 * grain)[..., None]
    rust_n = smoothstep(0.2, 1.4, sample(NOISE_GRIME, x * 0.6 + 7, (y + z) * 0.6 + 3))
    # ---- the hall: its roof deck tan, dark beams on a grid, rust streaks; its walls khaki, grime up from the foot
    hall = comp == M.HALL
    beam = (phase(x + 250.0, 48.0, 0.0) < 3.0) | (phase(y + 108.0, 54.0, 0.0) < 3.0)
    dplate = (phase(x + 17.0, 40.0, 0.0) < 9.0) & (phase(y + 5.0, 46.0, 0.0) < 10.0)
    deck = mix(TAN * g1 * (1 - 0.06 * beam)[..., None], RUST * g1, 0.55 * rust_n)
    deck = np.where(dplate[..., None], mix(deck, DARKM * g1, 0.6), deck)
    deck = np.where(beam[..., None] & top[..., None], BEAMC * g1, deck)
    wall = mix(KHAKI * g1 * (1 - 0.08 * (phase(z, 26.0, 0.0) < 1.2))[..., None], GRIME, smoothstep(30.0, 2.0, z) * 0.6)
    put(hall, np.where(top[..., None], deck, wall))
    bz -= 0.25 * (beam & top & hall)
    # ---- the roof's frame and ridges: lighter tan, a dark line along each ridge's foot
    roof = comp == M.ROOF
    put(roof, mix(mix(TAN_L * g1, TAN_D * g1, smoothstep(0.55, 0.15, nz) * 0.6), RUST * g1, 0.3 * rust_n))
    # ---- rust housings: rust red, darker edges and a panel line; the north-west housing too
    mach = comp == M.MACH
    edge = (phase(x, 18.0, 0.0) < 1.2) | (phase(y, 18.0, 0.0) < 1.2) | (phase(z, 18.0, 0.0) < 1.2)
    west = (x < -160.0) & (y > 100.0)
    mc = mix(MACHC * g1, RUST_D * g1, 0.35 * edge + 0.25 * rust_n)
    wc = mix(np.array([206, 160, 122.]) * g1, RUST * g1, 0.3 * rust_n + 0.25 * edge)
    put(mach, np.where(west[..., None], wc, mc))
    # ---- dark machinery: dark grey, a few lighter bolted plates
    grey = comp == M.GREY
    plate = (phase(x, 22.0, 3.0) < 5.5) & (phase(y, 16.0, 5.0) < 4.0)
    put(grey, GREYM * g1 * (1 + 0.18 * plate * top)[..., None])
    # ---- the fan housings (tan rings) and the fans: six dark blades turning (GTWEAP_C), a light hub
    put(comp == M.FANBOX, mix(TAN * g1, TAN_D * g1, smoothstep(0.6, 0.2, nz) * 0.5))
    fan = comp == M.FAN
    if fan.any():
        fc = np.zeros(shape, np.float32)
        for (fx, fy) in p['fans']['pts']:
            ddx, ddy = x - fx, y - fy
            near = np.hypot(ddx, ddy) < p['fans']['r'] + 1
            ang = np.arctan2(ddy, ddx) + (fans % 4) * (2 * np.pi / FAN_BLADES) / 4.0
            blade = (np.cos(ang * FAN_BLADES) > 0.35)
            fc = np.where(near, np.where(blade, 1.0, 0.0), fc)
        put(fan, mix(FANC * 0.75 * g1, FANC * 1.7 * g1, fc))
    # ---- beams and poles: dark steel
    put(comp == M.BEAM, mix(LBEAM * g1, RUST_D * g1, 0.4 * rust_n))
    put(comp == M.FRAME, FRAMEC * g1 * (1 + 0.15 * top)[..., None])
    put(comp == M.PLINTH, BEAMC * 0.9 * g1)
    put(comp == M.PIPE, PIPEC * g1)
    put(comp == M.SILL, mix(KHAKI * g1, GRIME, 0.3))
    # ---- the fenders: olive tan, darker towards the foot, seams round their curve; a dark vent in the north one
    jamb = comp == M.JAMB
    j = p['jamb']
    tcurve = np.arctan2(z, np.maximum(x - j['xb'], 1e-3))
    jseam = (np.abs(((tcurve / (np.pi / 2)) * 5.0) % 1.0 - 0.5) > 0.46)
    jc = mix(OLIVE * g1, OLIVE_D * g1, smoothstep(40.0, 0.0, z) * 0.5 + 0.3 * jseam)
    v = j['vent']
    vent = jamb & (y >= v['y'][0]) & (y <= v['y'][1]) & (z >= v['z'][0]) & (z <= v['z'][1]) & (lnx > 0.3) & (not sym)
    jc = np.where(vent[..., None], np.where((phase(z, 4.0, 0.0) < 1.6)[..., None], BLACK * g1, REDC * 0.6 * g1), jc)
    put(jamb, jc)
    # ---- the door: grey steel slats across it (they roll up with it), a diagonal brace over its straight part
    door = comp == M.DOOR
    if door.any():
        d = p['door']
        s = M.track_s(x, z, d)
        s0 = r.field('door_s0', 0.0)
        u = s - s0                                    # position on the sheet (from its bottom edge)
        slat = phase(u, d['rib'], 0.0) < 1.0
        # the brace: on the sheet's lower 40 units, corner to corner across the door's width
        yy0, yy1 = p['bay']['y']
        yt = (y - yy0) / (yy1 - yy0)
        brace = (u < d['zc'] - 2) & ((np.abs(u - (1 - yt) * (d['zc'] - 4)) < 2.6) | (np.abs(u - yt * (d['zc'] - 4)) < 2.6))
        dc = mix(STEEL * g1, STEEL_D * g1, 0.32 * slat)
        dc = np.where(brace[..., None], mix(dc, STEEL_D * 0.85 * g1, 0.6), dc)
        put(door, dc)
        bz -= 0.35 * slat * door
        # TS's door shines: a soft highlight where it faces the light
        L = r.view.L
        hl = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1) ** 6
        emit = np.where(door[..., None], emit + np.array([120, 120, 124.]) * hl[..., None] * (1 - 0.5 * slat)[..., None], emit)
    # ---- inside the bay: dark brown walls and ceiling, a dark floor with olive rails along it, red lights
    b = p['bay']
    inbay = (x >= b['x'][0]) & (x <= -6.0) & (y >= b['y'][0]) & (y <= b['y'][1]) & (z < b['ceil'] - 0.5) & \
        np.isin(comp, [M.HALL, M.BAYIN, M.BAYCEIL, M.FLOOR, M.JAMB])
    inner = inbay & (comp != M.FLOOR)
    put(inner, INSIDE * g1 * (1 - 0.12 * (phase(z, 20.0, 0.0) < 1.5))[..., None])
    flo = comp == M.FLOOR
    rails = (phase(y - b['y'][0], 18.6, 4.0) < 4.0)
    put(flo, np.where(rails[..., None], RAIL * g1, FLOORC * g1))
    # red lights along the bay's back wall and side walls, up under the ceiling
    rl = inner & (z > 58) & (z < 68) & (phase(x + y, 34.0, 0.0) < 5.0)
    put(rl, REDC * 1.4 * g1)
    emit = np.where(rl[..., None], np.array([90, 16, 8.]), emit)
    bc = comp == M.BAYCEIL
    out_ = bc & (nz > -0.5)                         # all but its underside: roof deck, its face over the door wall
    lint = out_ & ~top & (x > b['x'][1] - 60.0) & (z > b['ceil'] - 1.0)
    put(bc & ~out_, INSIDE * 0.8 * g1)
    put(out_ & ~lint, deck)
    put(lint, wall)
    # the bay is lit inside (TS's _1 shows its rails and back wall): a warm fill on its floor and walls, stronger
    # towards the back where the lamps are
    fill = np.clip((-6.0 - x) / 160.0, 0, 1) * 0.35 + 0.15
    lit_in = (inbay | flo) & ~rl
    emit = np.where(lit_in[..., None], emit + alb * fill[..., None] * np.array([1.0, 0.92, 0.8]), emit)
    # ---- house green: the panel (two seams across it), the west block (a seam), the fascia, the north band, the
    #      cap, the roof strip, the green unit (a red band round it, a dark vent on its top box)
    pn = p['panel']
    pseam = (np.abs(((pn['y0'] - ym) % 34.0) - 17.0) > 16.4)
    put(comp == M.PANEL, house * (1 - 0.14 * pseam)[..., None])
    w = p['west']
    wseam = np.abs(x - w['seam']) < 1.0
    put(comp == M.WESTG, house * (1 - 0.14 * wseam)[..., None])
    for c_ in (M.FASCIA, M.NSTRIP, M.NCAP, M.GREEN):
        put(comp == c_, house)
    gb = comp == M.GBLOCK
    if gb.any():
        q = p['gblock']
        band = (z >= q['stripe'][0]) & (z <= q['stripe'][1]) & (r.field('nostripe', 0.0) < 0.5)   # crushed when damaged
        put(gb, np.where(band[..., None], REDC * g1, house))
    # ---- the lamps: dark glass (lit by GTWEAP_A / _B).  In the build-up they glow as TS's GTWEAPMK draws them (the A
    #      lamps white, the B lamps orange-red) while all else is grey
    paint = r.field('paint', 1.0)
    building_up = bool(np.any(paint < 1))
    la = comp == M.LAMPA
    put(la, GLASS_A * g1)
    if building_up and lampsA is None and la.any():
        put(la, np.array([236, 236, 240.]))
        emit = np.where(la[..., None], np.array([120, 120, 126.]), emit)
    if lampsA is not None and la.any():
        q = p['lampsA']
        k_ = np.clip(np.round((y - q['y0']) / q['dy']), 0, 4).astype(int)
        seq = A_SEQ[A_MAP_SYM[lampsA % 16]] if sym else A_SEQ[lampsA % 16]
        lev = np.array([A_LEVELS[v_] for v_ in seq], np.float32)[k_]
        lit = mix(GLASS_A * g1, np.array([236, 236, 240.]), lev)
        put(la, lit)
        emit = np.where(la[..., None], np.array([120, 120, 126.]) * lev[..., None], emit)
    lbm = comp == M.LAMPB
    put(lbm, GLASS_B * g1)
    if building_up and lampsB is None and lbm.any():
        put(lbm, B_COL[3])
        emit = np.where(lbm[..., None], B_COL[3] * 0.45, emit)
    if lampsB is not None and lbm.any():
        q = p['lampsB']
        xs_ = np.array([pt[0] for pt in q['pts']])
        k_ = np.argmin(np.abs(x[..., None] - xs_), axis=-1)
        cols = np.stack([B_COL[B_OUT[lampsB % 8]], B_COL[B_MID[lampsB % 8]], B_COL[B_OUT[lampsB % 8]]])
        lc = cols[k_]
        lc = np.where((lc == B_COL[0]).all(-1)[..., None], GLASS_B * g1, lc)
        put(lbm, lc)
        hot = lc.max(axis=-1) > 100
        emit = np.where((lbm & hot)[..., None], lc * 0.45, emit)
    # ---- the build-up's grey (TS's GTWEAPMK is untextured grey until its last frames, all but its lamps)
    if building_up:
        grey_ = r.hitmask & ~(la | lbm)
        alb = np.where(grey_[..., None], mix(MKGREY * g1, alb, np.clip(paint, 0, 1)), alb)
        emit = np.where((la | lbm)[..., None], emit, emit * np.clip(paint, 0, 1)[..., None])
    # ---- the bib: cream concrete slabs, seams fanning out from the end of the exit lane, sand dirt towards its
    #      edges, a grey patch at its north-west; house-green and black hazard stripes in the lane
    pad = (comp == M.PAD) | (comp == M.CHEV)
    if pad.any():
        q = p['pad']
        fxc, fyc = q['fan']
        yl = y                                       # the lane's stripes keep their own (unmirrored) run
        if sym:
            # RA round 2: the apron's west half mirrored onto its east half (its texture too), as the mod made it
            y = ym
            pfine = sample(NOISE_FINE, x, y)
            pmott = sample(NOISE_MOTTLE, x * 0.7 + 31, y * 0.7 + 17)
            g1 = (1 + pfine * 0.035 + pmott * 0.05)[..., None]
        ang = np.degrees(np.arctan2(y - fyc, x - fxc))
        rr = np.hypot(x - fxc, y - fyc)
        fan_ = (ang > -75.0) & (ang < 135.0)                                    # the seams fan out away from the door
        seam_r = ((15.0 - np.abs(((ang + 90.0) % 30.0) - 15.0)) * np.radians(1) * rr < 1.1) & (rr > 30) & fan_
        seam_c = np.abs(rr - 30.0) < 1.0
        crack = np.abs(sample(NOISE_GRIME, x * 0.9 + 3, y * 0.9 + 11)) < 0.03
        edge_d = smoothstep(60.0, 150.0, rr) * 0.55
        dirt = np.clip(smoothstep(0.0, 1.3, sample(NOISE_MOTTLE, x * 0.8 + 50, y * 0.8 + 7)) * 0.6 + edge_d * 0.7, 0, 0.9)
        pc = mix(PADC * g1 * (1 - 0.12 * seam_r - 0.12 * seam_c - 0.2 * crack)[..., None], SAND * g1, dirt)
        pc = np.where((seam_r | seam_c)[..., None], mix(pc, SEAMC * g1, 0.35), pc)
        if not sym:
            grey_ = M.in_poly(x, y, q['grey'])
            pc = np.where(grey_[..., None], PATCH * g1, pc)
        ln = q['lane']
        cs = comp == M.CHEV
        stripe = phase(x + yl, ln['period'], 0.0) < ln['period'] / 4
        sc = np.where(stripe[..., None], house, BLACK * g1)
        tex = r.field('padtex', 1.0)
        plain = SLABC * g1
        pc = mix(plain, pc, tex)
        sc = mix(np.where(stripe[..., None], np.array([236, 236, 236.]) * g1, BLACK * g1), sc, np.clip(tex, 0, 1))
        put(pad, np.where(cs[..., None], sc, pc))
        bz -= 0.3 * (seam_r | seam_c) * pad * tex
    put(comp == M.SLAB, SLABC * g1)
    return alb, (bx, by, bz), emit


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & (np.isin(r.comp, list(M.HOUSE)) | np.isin(r.comp, [40, 43]))
