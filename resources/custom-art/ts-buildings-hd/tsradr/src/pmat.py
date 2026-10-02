"""Materials for the Power Plant and its turbine: albedo, bump and glow per pixel of an hd.Render.
Colours follow the component tower and the yard (house green 0,214,0; blue-grey plate 150,150,178; dark
recess 74,74,78), with the tower's cone in TS's warmer khaki."""
import numpy as np
import walls2 as W
from walls2 import sample, smoothstep, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME
import powr as PW

GREEN = np.array([0, 214, 0.])
CONC = np.array([218, 212, 194.])
KHAKI_CONE = np.array([200, 166, 100.])
RUST = np.array([124, 78, 48.])
EARTH = np.array([188, 162, 112.])
STEEL_D = np.array([96, 97, 104.])
DECK_C = np.array([88, 88, 92.])
PLATE_C = np.array([150, 150, 178.])
HOLE_C = np.array([26, 26, 32.])
DOOR_C = np.array([30, 30, 34.])
T_GREY = np.array([156, 156, 166.])
T_FRAME = np.array([128, 58, 40.])


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


def materials(r, p=PW.P, occ=None, turb_angle=0.0, lamp=1.0, lights=None, lights_ok=None):
    """returns albedo, (dnx, dny, dnz) bump, emissive colour."""
    x, y, z, comp = r.x, r.y, r.z, r.comp
    nx, ny, nz = r.nx, r.ny, r.nz
    top = nz > 0.75
    tx, ty = p['tower']
    dxt, dyt = x - tx, y - ty
    az = np.arctan2(dyt, dxt)
    dt = np.hypot(dxt, dyt)
    # texture coordinates: round things get (arc length, z), flat things (x, y)
    u = np.where(top, x, az * 48.0)
    v = np.where(top, y, z)
    fine = sample(NOISE_FINE, u, v)
    mott = sample(NOISE_MOTTLE, u * 0.7 + 31, v * 0.7 + 17)
    grime_n = sample(NOISE_GRIME, u, v)
    grain = fine * 0.035 + mott * 0.05
    g1 = (1 + grain)[..., None]
    shape = x.shape
    alb = np.zeros(shape + (3,), np.float32)
    bx = np.zeros(shape, np.float32); by = np.zeros(shape, np.float32); bz = np.zeros(shape, np.float32)
    emit = np.zeros(shape + (3,), np.float32)

    def put(mask, col):
        nonlocal alb
        alb = np.where(mask[..., None], col, alb)

    # ---------------------------------------------------------------- slab: light concrete, conduit grooves
    slab = comp == PW.SLAB
    joint = (phase(x, 64.0, 0.0) < 0.5) | (phase(y, 64.0, 0.0) < 0.5)
    stain = smoothstep(0.6, 1.6, sample(NOISE_GRIME, x * 0.5 + 40, y * 0.5)) * 0.2
    sc = CONC * 0.93 * g1 * (1 - 0.12 * joint)[..., None]
    sc = mix(sc, np.array([150, 138, 112.]), stain)
    # dark conduits from the door across the middle to each socket
    groove = np.zeros(shape, bool)
    lx, ly = p['lamp'][0], p['lamp'][1]
    for (cx, cy) in p['sockets']:
        ux, uy = cx - lx, cy - ly
        L = np.hypot(ux, uy); ux, uy = ux / L, uy / L
        al = (x - lx) * ux + (y - ly) * uy
        ac = -(x - lx) * uy + (y - ly) * ux
        groove |= (al > 4) & (al < L - p['mound_r0'] + 6) & (np.abs(ac) < 2.2)
    sc = np.where(groove[..., None], np.array([70, 70, 74.]) * g1, sc)
    put(slab, sc)

    # ---------------------------------------------------------------- socket mounds, rims, rings, plates
    mound = comp == PW.MOUND
    ma = np.arctan2(y - np.round(y / 128.0 - 0.5) * 128 - 64, x - np.round(x / 128.0 - 0.5) * 128 - 64)
    flat = r.nz > 0.8                                          # tops of mounds still going up: no strata
    rock = np.where(flat, sample(NOISE_MOTTLE, x * 0.5 + 11, y * 0.5), sample(NOISE_MOTTLE, ma * 60.0 + 11, z * 0.9))
    rock2 = np.where(flat, sample(NOISE_FINE, x * 1.2 + 5, y * 1.2), sample(NOISE_FINE, ma * 140.0 + 5, z * 2.2))
    # sandstone strata: uneven horizontal layers with dark seams between them
    lay = np.where(flat, 0.5, z * 0.13 + 0.6 * sample(NOISE_MOTTLE, ma * 12.0, z * 0.05))
    seam_m = phase(lay, 1.0, 0.0) < 0.07
    mc = EARTH * (1 + 0.5 * grain)[..., None] * (1 + 0.14 * rock + 0.03 * rock2 + 0.06 * np.sin(np.floor(lay) * 2.3))[..., None]
    mc = mc * (1 - 0.25 * seam_m)[..., None]
    big = np.where(flat, sample(NOISE_MOTTLE, x * 0.2 + 40, y * 0.2), sample(NOISE_MOTTLE, ma * 9.0 + 40, z * 0.12))
    mc = mc * (1 + 0.12 * big)[..., None]
    dark_patch = smoothstep(0.45, 1.3, np.where(flat, sample(NOISE_GRIME, x * 0.4 + 3, y * 0.4), sample(NOISE_GRIME, ma * 30.0 + 3, z * 0.5))) * 0.45
    mc = mix(mc, np.array([112, 90, 58.]), np.maximum(dark_patch, np.clip(1 - (z - 1) / 12.0, 0, 1) * 0.4))
    put(mound, mc)
    mb = mound.astype(np.float32)
    bz += 0.35 * (seam_m.astype(np.float32) - 0.12) * mb
    bx += 0.18 * rock * mb; by += 0.06 * rock2 * mb
    put(comp == PW.MRIM, np.array([104, 104, 110.]) * (1 + 0.3 * grain)[..., None])
    put(comp == PW.RING, GREEN * (1 + 1.1 * grain)[..., None])
    plate = comp == PW.PLATE
    pc = PLATE_C * g1
    hole = np.zeros(shape, bool)
    for (cx, cy) in p['sockets']:
        for hx, hy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            hole |= np.hypot(x - cx - hx * p['hole_at'], y - cy - hy * p['hole_at']) <= p['hole_r'] + 0.3
    pc = np.where(hole[..., None], HOLE_C, pc)
    put(plate, pc)

    # ---------------------------------------------------------------- decks and fairings
    deck = comp == PW.DECK
    seam = phase(x + y, 18.0, 0.0) < 0.6
    put(deck, DECK_C * g1 * (1 - 0.18 * seam)[..., None])
    fair = comp == PW.FAIR
    put(fair, np.array([226, 222, 204.]) * g1)

    # ---------------------------------------------------------------- the drum and the door
    drum = comp == PW.DRUM
    vseam = phase(az * p['drum_r'], 16.0, 0.0) < 0.7
    rivet = (np.abs(z - 38.0) < 0.9) & (phase(az * p['drum_r'], 5.0, 0.0) < 1.2)
    put(drum, STEEL_D * g1 * (1 - 0.2 * vseam - 0.25 * rivet)[..., None])
    put(comp == PW.DOOR, DOOR_C * g1)

    # ---------------------------------------------------------------- collar and pipes (house colour)
    collar = comp == PW.COLLAR
    # house colour exactly as on the yard and the tower (GREEN x (1 + 1.1 grain)); detail only as thin seams
    rib = phase(az * p['collar_r'], 14.0, 0.0) < 1.0
    lipline = np.abs(z - (p['collar_z'][0] + 6.0)) < 0.7
    cc = GREEN * (1 + 1.1 * grain)[..., None]
    cc = cc * (1 - 0.28 * ((rib | lipline) & ~top))[..., None]
    put(collar, cc)
    cb = (collar & ~top).astype(np.float32)
    rb = np.sin(az * p['collar_r'] * 2 * np.pi / 14.0)
    bx += 0.22 * rb * np.cos(az + np.pi / 2) * cb; by += 0.22 * rb * np.sin(az + np.pi / 2) * cb
    put(comp == PW.PIPE, GREEN * (1 + 1.1 * grain)[..., None])
    put(comp == PW.LAMP, GREEN * (1 + 1.1 * grain)[..., None])
    emit = np.where((comp == PW.LAMP)[..., None], np.array([0, 60, 0.]) * lamp, emit)

    # ---------------------------------------------------------------- the cone
    cone = comp == PW.CONE
    z0, z1 = p['cone_z']
    t = np.clip((z - z0) / (z1 - z0), 0, 1)
    ck = np.floor(t * p['courses'] - 1e-6)
    within = t * p['courses'] - ck
    tint = 1 + 0.07 * np.sin(ck * 2.7 + 1.3)                        # each course a slightly different tone
    edge = within > 0.9                                              # the ledge at the top of each course
    streak = smoothstep(0.45, 1.3, sample(NOISE_GRIME, az * 16.0, z * 0.22)) * 0.3
    blot = smoothstep(0.45, 1.3, sample(NOISE_MOTTLE, az * 22.0 + 9, z * 0.28)) * 0.4
    kc = KHAKI_CONE * g1 * (tint + 0.14 * mott)[..., None]
    kc = mix(kc, np.array([146, 110, 64.]), np.maximum(streak, blot))
    rust = smoothstep(0.66, 0.9, t + 0.14 * sample(NOISE_GRIME, az * 22.0 + 5, z * 0.35) + 0.05 * fine)
    kc = mix(kc, RUST * g1, rust * 0.9)
    kc = kc * (1 + 0.12 * edge)[..., None] * (1 - 0.35 * (within < 0.06))[..., None]
    put(cone, kc)
    cb = cone.astype(np.float32)
    bz += 0.0 * cb
    bx += 0.18 * mott * cb; by += 0.18 * fine * cb
    # the tower's lights: small lenses on the cone.  lights: None (off: the building frame) or a level per ring
    # (0 = lit green, >0 = the white-blue flash fading 1 .. 0.25, TS's GTPOWR_A); lights_ok[ring][i]: working
    lens_id = np.full(shape, -1, np.int16)
    for ri, lz in enumerate(p['lights_z']):
        for ai, la in enumerate(p['lights_az']):
            rr = PW.cone_radius(np.array([lz]), p)[0]
            lx_, ly_ = tx + rr * np.cos(la), ty + rr * np.sin(la)
            on = np.sqrt((x - lx_) ** 2 + (y - ly_) ** 2 + (z - lz) ** 2) <= p['light_r']
            lens_id = np.where(on & cone, ri * 16 + ai, lens_id)
    lensm = lens_id >= 0
    alb = np.where(lensm[..., None], alb * 0.78, alb)
    r.lens = lensm
    r.flash = np.zeros(shape, np.float32)
    if lights is not None:
        for ri in range(len(p['lights_z'])):
            for ai in range(len(p['lights_az'])):
                ok = True if lights_ok is None else lights_ok[ri][ai]
                if not ok:
                    continue
                mk = lens_id == ri * 16 + ai
                L = lights[ri]
                if L <= 0:
                    alb = np.where(mk[..., None], GREEN, alb)
                    emit = np.where(mk[..., None], np.array([0, 90, 0.]), emit)
                else:
                    # TS: white (255,255,255) -> (206,206,255) -> (153,153,255) -> (101,101,255)
                    c = np.array([255, 255, 255.]) if L >= 1 else np.array([255 * L, 255 * L, 255.]) * np.array([0.81, 0.81, 1.0])
                    alb = np.where(mk[..., None], np.array([200, 200, 230.]), alb)
                    emit = np.where(mk[..., None], c, emit)
                    r.flash = np.where(mk, max(L, 0.0), r.flash)
    # the window: a dark square opening on the south face, with a lighter frame
    wa, wz, ww, wh = p['window']
    rw = PW.cone_radius(z, p)
    waz = np.angle(np.exp(1j * (az - wa)))
    wu, wv = np.abs(waz) * rw, np.abs(z - wz)
    wframe = cone & (wu <= ww / 2 + 1.6) & (wv <= wh / 2 + 1.6)
    whole = cone & (wu <= ww / 2) & (wv <= wh / 2)
    alb = np.where(wframe[..., None], np.array([150, 132, 96.]) * g1, alb)
    alb = np.where(whole[..., None], np.array([30, 28, 28.]), alb)
    r.lens = lensm & cone
    put(comp == PW.CONEIN, np.array([46, 38, 34.]) * g1)

    # ---------------------------------------------------------------- the turbine
    th = comp == PW.THOUSE
    ang = np.arctan2(y - _slot_y(p, x, y), x - _slot_x(p, x, y))
    rot = ang - turb_angle
    tp = phase(rot * 40.0, 2 * np.pi * 40.0 / 3.0, 0.0)               # three lighter panels round it
    panel = tp < 14.0
    tvs = phase(rot * 30.0, 2 * np.pi * 30.0 / 6.0, 0.0) < 0.7        # six seams
    zp = z + r.field('pod_drop')                                         # the pod's own height (it rises in the build-up)
    tblot = sample(NOISE_MOTTLE, rot * 30.0 + 7, zp * 0.6)
    tc = T_GREY * g1 * (1 + 0.14 * panel + 0.08 * tblot)[..., None] * (1 - 0.16 * tvs)[..., None]
    # three service hatches round the housing (a light panel with a brown port), turning with it
    ha, hw, hhh = p['turb']['hatch']
    hrel = np.angle(np.exp(1j * ((rot - ha) * 3.0))) / 3.0
    zrel = zp - (p['sock_z'] + 0.4 + p['turb']['h'] * 0.42)
    hatch = (np.abs(hrel) * 28.0 <= hw / 2) & (np.abs(zrel) <= hhh / 2) & ~top
    port = (np.abs(hrel) * 28.0 <= 2.2) & (np.abs(zrel - 0.5) <= 2.0) & ~top
    tc = np.where(hatch[..., None], np.array([214, 214, 220.]) * g1, tc)
    tc = np.where(port[..., None], np.array([150, 108, 70.]) * g1, tc)
    put(th, tc)
    tb = comp == PW.TBAND
    wpos = phase(rot, 2 * np.pi / 6.0, 0.0) / (2 * np.pi / 6.0)       # six windows
    winm = (wpos > 0.1) & (wpos < 0.78) & ~top
    put(tb, np.where(winm[..., None], GREEN * (1 + 1.1 * grain)[..., None], T_FRAME * g1))
    put(comp == PW.TCAP, T_GREY * 0.95 * g1)

    # grime rising from the foot of everything standing on the slab
    gr = smoothstep(0.35, 1.2, grime_n) * np.clip(1 - (z - p['slab_h']) / 22.0, 0, 1) * 0.35
    gr = gr * ~np.isin(comp, [PW.RING, PW.PLATE, PW.LAMP, PW.SLAB, PW.COLLAR, PW.PIPE, PW.TBAND])
    alb = mix(alb, W.GRIME if hasattr(W, 'GRIME') else np.array([112, 104, 78.]), gr)
    return alb, (bx, by, bz), emit


def _nearest_slot(p, x, y):
    d = np.stack([np.hypot(x - sx, y - sy) for (sx, sy) in p['slots']])
    return np.argmin(d, axis=0)


def _slot_x(p, x, y):
    """x of the nearest turbine slot (for the turbine's own angle)."""
    return np.array([sx for sx, sy in p['slots']])[_nearest_slot(p, x, y)]


def _slot_y(p, x, y):
    return np.array([sy for sx, sy in p['slots']])[_nearest_slot(p, x, y)]


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g
