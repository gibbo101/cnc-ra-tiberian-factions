"""Materials for the EMP Pulse Cannon: albedo, bump and glow per pixel of an hd.Render.  House green 0,214,0 x
(1 + 1.1 grain) as on every building (the drum and its lamp); the base the mod's khaki-grey concrete (TS's own art is
snowed over: snow=True puts TS's snow back on the ridges and round the foot); the head grey with dark sides."""
import numpy as np
import walls2 as W
from walls2 import sample, smoothstep, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME
import puls as M

GREEN = np.array([0, 214, 0.])
CONC = np.array([188, 180, 146.])           # the mod's art: lit 96-107, 92-106, 68-90; TS (snow) 97-101, 89-101, 64-76
CONC_D = np.array([158, 150, 120.])
RIDGE = np.array([206, 198, 164.])
RIMC = np.array([176, 170, 140.])
CRATERC = np.array([52, 50, 44.])
HOODC = np.array([196, 198, 202.])          # TS 113-170 grey (lit top)
HOODD = np.array([150, 152, 158.])
VISORC = np.array([150, 150, 156.])         # TS's face plate 85-105
HSIDEC = np.array([66, 66, 72.])            # TS 20-46: the head's near-black sides
SIDEC = np.array([92, 92, 100.])            # TS 36-60
DARKC = np.array([62, 62, 68.])             # TS 12-36
LEGC = np.array([104, 104, 112.])           # TS 60-105
PIVC = np.array([128, 128, 136.])
LENSC = np.array([236, 240, 250.])          # TS 153-170 ring
LENSD = np.array([40, 42, 52.])             # TS 76 centre
PORTC = np.array([22, 22, 24.])
SNOWC = np.array([236, 240, 252.])
SNOWD = np.array([170, 182, 214.])
DIRT = np.array([118, 104, 76.])


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


BODYT = np.array([194, 196, 200.])         # the body's top (TS 113-170, the lit grey of the head's top)
BODYB = np.array([160, 162, 168.])         # its back (TS's light back face)
BODYS = np.array([70, 70, 76.])            # its sides and front (TS 20-46)
NOSEC = np.array([200, 202, 208.])         # the nose (the barrel)
RIMC2 = np.array([176, 178, 184.])         # the collar round the emitter
YOKEC = np.array([74, 74, 80.])            # the yoke plates (TS's dark slanted bands)
BOSSC = np.array([186, 186, 192.])         # the trunnion bosses (TS's light spot on the dark side)
TANKC = np.array([58, 58, 64.])
CABLEC = np.array([34, 34, 37.])
HAZY = np.array([206, 164, 44.])           # hazard stripes (the second reference; TS's few yellow pixels on the head)
HAZK = np.array([40, 40, 42.])


def cannon_materials(r, p, x, y, z, fdeg, put, get_alb):
    """the cannon head (puls.CANNON): a light-topped box with dark sides and a light back, a light nose with the
    emitter on its end (a white ring round a dark centre: TS's ring), dark yoke plates, light trunnion bosses, a dark
    tank, black cables, a patch of hazard stripes low on each side at the front."""
    h = r.mk.get('cannon') or M.CANNON
    comp, nx, ny, nz = r.comp, r.nx, r.ny, r.nz
    u, v, w, a, b, c = M.cannon_local(x, y, z, fdeg, h, r.mk.get('zlift', 0.0))
    t = np.radians(h['tilt'])
    fa = np.radians(fdeg)
    nu0 = nx * np.cos(fa) + ny * np.sin(fa)                 # the normal in the head frame (u forward, v left)
    nvv = nx * np.sin(fa) - ny * np.cos(fa)
    na = nu0 * np.cos(t) + nz * np.sin(t)                   # ... and in the body's own (tilted) frame
    nc = -nu0 * np.sin(t) + nz * np.cos(t)
    hm = sample(NOISE_MOTTLE, a * 0.9 + 11.0, b * 0.9 + c * 0.6 + 5.0)
    hf = sample(NOISE_FINE, a * 1.3 + 3.0, b * 1.3 + c * 0.9)
    gh = (1 + 0.05 * hm + 0.025 * hf)[..., None]
    bd = h['body']
    # ---- the body: the top light (panel lines across it, an inset border), the back light, the sides and front dark;
    # the rounded long edges blend from side to top
    top_t = np.clip((nc - 0.35) / 0.4, 0, 1)
    col = mix(BODYS * gh, BODYT * gh, top_t)
    back = na < -0.6
    col = np.where(back[..., None], BODYB * gh, col)
    ontop = nc > 0.55
    seam = ontop & ((np.abs(a + 30.0) < 0.55) | (np.abs(a + 14.0) < 0.55) | (np.abs(np.abs(b) - (bd['hv'] - 3.5)) < 0.5))
    col = np.where(seam[..., None], BODYT * 0.7 * gh, col)
    # the back: a panel with the cables' ports
    bpan = back & ((np.abs(np.abs(b) - (bd['hv'] - 3.0)) < 0.5) | (np.abs(c - bd['w'][1] + 3.0) < 0.5))
    col = np.where(bpan[..., None], BODYB * 0.72 * gh, col)
    # hazard stripes: a patch low on each side at the front
    side = np.abs(nvv) > 0.75
    hz = side & (a > bd['u'][1] - 17.0) & (a < bd['u'][1] - 2.5) & (c > bd['w'][0] + 3.5) & (c < bd['w'][0] + 12.5)
    stripe = phase(a + c, 6.0, 0.0) < 0.5
    col = np.where(hz[..., None], np.where(stripe[..., None], HAZY * gh, HAZK * gh), col)
    put(comp == M.HBOX, col)
    # ---- the nose and its collar; the emitter on the collar's end
    nzp = h['nose']
    rho = np.hypot(b, c - nzp['w'])
    ring = (rho > 3.0) & (rho < 6.6)
    nose_col = mix(NOSEC * gh, NOSEC * 0.82 * gh, 0.5 * np.clip(-nc, 0, 1))
    nseam = (np.abs(a - (nzp['u'][0] + 8.0)) < 0.5) & (na < 0.6)
    nose_col = np.where(nseam[..., None], NOSEC * 0.72 * gh, nose_col)
    put(comp == M.BARREL, nose_col)
    # the muzzle: the collar light; inside the bore dark, its back wall a dark emitter with a pale ring (TS's light ring
    # round a dark middle)
    cl = nzp.get('collar') or {}
    inb = rho < cl.get('bore', 0.0) - 0.15
    bore_back = inb & (a < cl.get('bore_u', 0.0) + 0.8)
    emc = np.where(((rho > 2.6) & (rho < 4.2))[..., None], LENSC * 0.78, LENSD * 0.75)
    mzc = np.where(inb[..., None], np.where(bore_back[..., None], emc, LENSD * 0.55), RIMC2 * gh)
    lip = (na > 0.6) & ~inb & (rho < cl.get('bore', 0.0) + 1.0)
    mzc = np.where(lip[..., None], RIMC2 * 0.8 * gh, mzc)
    put(comp == M.MZLO, mzc)
    put(comp == M.MZHI, np.where((np.abs(na) > 0.6)[..., None], RIMC2 * 0.8 * gh, RIMC2 * gh))   # the coil rings
    # ---- the yoke plates (dark; their edges a touch lighter), the pins
    yedge = (np.abs(nvv) < 0.6)
    # a raised rim round each plate's outer face (TS's plates are dark; the second reference's plate has a rim)
    yk = h['yoke']
    from dept import quad_interval as _qi
    lo_, hi_, ok_ = _qi(u, list(yk['poly']))
    rim = (np.abs(nvv) >= 0.6) & ((w - lo_ < 2.2) | (hi_ - w < 2.2))
    ycol = np.where(yedge[..., None], YOKEC * 1.45 * gh, np.where(rim[..., None], YOKEC * 1.3 * gh, YOKEC * gh))
    rv = (np.abs(nvv) >= 0.6) & (np.hypot(u - (yk['poly'][0][0] + yk['poly'][1][0]) / 2.0 + 2.0, w - 80.0) < 1.3)
    ycol = np.where(rv[..., None], YOKEC * 1.7 * gh, ycol)
    put(comp == M.YOKE, ycol)
    # ---- the trunnion bosses: light, a dark bolt in the middle
    tu, tw = h['trun']
    rb = np.hypot(u - tu, w - tw)
    put(comp == M.BOSS, np.where(((rb < 2.0) & (np.abs(nvv) > 0.6))[..., None], DARKC * gh, BOSSC * gh))
    # ---- the tank: dark, two bands round it
    tk = h['tank']
    band = (np.abs(a - (tk['u'][0] + 8.0)) < 1.2) | (np.abs(a - (tk['u'][1] - 8.0)) < 1.2)
    put(comp == M.TANK, np.where(band[..., None], TANKC * 1.45 * gh, TANKC * gh))
    put(comp == M.CABLE, CABLEC * gh)
    put(comp == M.TTABLE, PIVC * gh)


def materials(r, p=None, occ=None, level=0, **kw):
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
    alb = np.zeros(shape + (3,), np.float32) + 128
    bx = np.zeros(shape, np.float32); by = np.zeros(shape, np.float32); bz = np.zeros(shape, np.float32)
    emit = np.zeros(shape + (3,), np.float32)
    house = GREEN * (1 + 1.1 * grain)[..., None]
    grime = smoothstep(0.15, 1.3, sample(NOISE_GRIME, x * 0.7 + 7, (y + z) * 0.7 + 3))
    low = smoothstep(26.0, 2.0, z)

    def put(mask, col):
        nonlocal alb
        alb = np.where(mask[..., None], col, alb)

    # ---- the base: rough cast concrete, mottled; the arms' top strips a touch lighter; grime rising from the foot
    rough = sample(NOISE_MOTTLE, x * 1.7 + 3, (y + z) * 1.7 + 9)
    bc = mix(CONC * g1, CONC_D * g1, np.clip(0.25 + 0.35 * rough + 0.3 * grime * 0.6, 0, 1))
    base = comp == M.BASE
    # which arm a pixel is on (the nearest ridge line ahead of it): seams across the arms, the cone's radial seams
    am = p['arms']
    best_t = np.full(shape, 1e9, np.float32); s_on = np.zeros(shape, np.float32)
    for k in range(4):
        s_k, t_k = M.arm_frame(x, y, k, am)
        better = (s_k > 0) & (np.abs(t_k) < best_t)
        best_t = np.where(better, np.abs(t_k), best_t); s_on = np.where(better, s_k, s_on)
    rr_ = np.hypot(x, y)
    ang_ = np.degrees(np.arctan2(y, x))
    on_arm = best_t < 30.0
    seam_a = on_arm & (phase(s_on, 22.0, 8.0) < 0.55) & (s_on > 46.0)
    seam_c = ~on_arm & (phase(ang_, 30.0, 15.0) * np.pi / 180.0 * rr_ < 0.6)
    pour = phase(z, 9.0, 2.0) < 0.35                      # the courses the concrete was poured in, faint
    bc = np.where(pour[..., None], bc * 0.95, bc)
    bc = np.where((seam_a | seam_c)[..., None], bc * 0.72, bc)
    put(base, bc)
    rc = mix(RIDGE * g1, CONC_D * g1, 0.25 * grime)
    rc = np.where(seam_a[..., None], rc * 0.75, rc)
    put(comp == M.ARM, rc)
    # the collar: a darker cast ring with a bolt every 15 degrees
    rm = p['rim']
    rmid = 0.5 * (rm['R'] + rm['ri'])
    bolt = (phase(ang_, 15.0, 7.5) * np.pi / 180.0 * rr_ < 1.1) & (np.abs(rr_ - rmid) < 1.1)
    rimc = np.where(bolt[..., None], RIMC * 0.62 * g1, RIMC * g1)
    rimc = np.where((np.abs(rr_ - rm['R'] + 0.8) < 0.6)[..., None], RIMC * 0.8 * g1, rimc)
    put(comp == M.RIM, rimc)
    put(comp == M.CRATER, CRATERC * g1)
    # ---- the drum and its lamp: house colour
    put(np.isin(comp, [M.DRUM, M.SEAM, M.LIGHT]), house)
    # the drum's two seams (thin lines: the only detail the house colour takes)
    dsm = (comp == M.DRUM) & ~top & np.any([np.abs(z - s_) < 0.55 for s_ in p['drum']['seams']], axis=0)
    put(dsm, house * 0.62)
    # ---- the head
    hd_ = r.mk.get('head')
    if hd_ is not None:
        fdeg = hd_[1] if isinstance(hd_, tuple) else M.facing_deg(hd_, lay)
        a = np.radians(fdeg)
        dv = np.array([np.sin(a), -np.cos(a)])
        nv = nx * dv[0] + ny * dv[1]                      # the normal along the head's sideways axis
        side = np.abs(nv) > 0.72
    else:
        side = np.zeros(shape, bool)
    hood = comp == M.HOOD
    if hd_ is not None and p['head'].get('mode') == 'cannon':
        cannon_materials(r, p, x, y, z, fdeg, put, lambda: alb)
    elif hd_ is not None and p['head'].get('mode') == 'prim3':
        hu_, hv_ = M.head_local(x, y, fdeg)
        a_ = np.radians(fdeg)
        nu = nx * np.cos(a_) + ny * np.sin(a_)               # the normal along the head's forward axis
        nvv = nx * np.sin(a_) - ny * np.cos(a_)
        side = np.abs(nvv) > 0.75
        visor = (nu > 0.35) & (nz > 0.25) & ~side
        h3 = M.HEAD3
        us_ = [q_[0] for q_ in h3['prof']]
        kk = np.clip((hu_ - min(us_)) / (max(us_) - min(us_)), 0, 1)
        hvu = h3['hv'][0] + (h3['hv'][1] - h3['hv'][0]) * kk
        # TS's head: a mid-grey hood over near-black sides; the visor a grey plate in a black frame, a dark slit across
        # its top; the back's pack dark
        # (the head's own grain, in its frame: the base's grain, sampled for walls by (x + y, z), streaks its slopes)
        hm_ = sample(NOISE_MOTTLE, hu_ * 0.9 + 11.0, hv_ * 0.9 + z * 0.6 + 5.0)
        gh = (1 + 0.05 * hm_)[..., None]
        col = np.where(side[..., None], HSIDEC * gh, mix(HOODC * gh, HOODD * gh, 0.3 * hm_))
        vc = np.where((np.abs(hv_) > hvu - 2.6)[..., None], DARKC * 0.7 * gh, VISORC * gh)
        col = np.where(visor[..., None], vc, col)
        sl_ = h3.get('slit')
        if sl_:                                              # a dark slit across the visor
            hz_ = z - r.mk.get('zlift', 0.0)
            col = np.where((visor & (hz_ >= sl_[0]) & (hz_ <= sl_[1]))[..., None], DARKC * 0.6 * gh, col)
        seam = ~side & ~visor & (np.abs(hu_ + 18.0) < 0.6)    # one seam across the top
        col = np.where(seam[..., None], HSIDEC * 1.3 * gh, col)
        put(hood, col)
    elif hd_ is not None and p['head'].get('mode') == 'prim2':
        put(hood, HOODC * g1 * (1 - 0.1 * (phase(x + y, 8.0, 0.0) < 0.6) * ~top)[..., None])
        put(comp == M.HSIDE, SIDEC * g1)
        # the face plate: light grey inside a dark frame
        fa = M.HEAD2['face']
        hu_, hv_ = M.head_local(x, y, fdeg)
        inner = (np.abs(hv_) <= fa['hv'] - fa['frame']) & (z >= fa['w'][0] + fa['frame']) & (z <= fa['w'][1] - fa['frame'])
        put(comp == M.HDARK, np.where(inner[..., None], HOODC * 0.92 * g1, SIDEC * 0.8 * g1))
    elif hd_ is not None and p['head'].get('mode', 'vox') == 'vox' and hood.any():
        import pulshead as PH
        hu, hv_ = M.head_local(x[hood], y[hood], fdeg)
        cls, lum = PH.surface_class(hu, hv_, z[hood])
        t = smoothstep(25.0, 110.0, np.nan_to_num(lum, nan=70.0))
        hc = mix(DARKC, HOODC, t) * g1[hood]
        alb[hood] = hc
    else:
        hseam = phase(z, 9.0, 3.0) < 0.7
        put(hood, np.where(side[..., None], SIDEC * g1, HOODC * g1 * (1 - 0.08 * (hseam & ~top))[..., None]))
    put(comp == M.PACK, DARKC * g1)
    put(comp == M.PORT, PORTC)
    put(comp == M.LEG, LEGC * g1)
    put(comp == M.PIVOT, PIVC * g1)
    put(comp == M.LENS, LENSC)
    put(comp == M.LENSC, LENSD)
    # grime at the foot of the base
    gr = smoothstep(0.35, 1.2, sample(NOISE_GRIME, x * 0.8, y * 0.8 + z)) * low * 0.35
    gr = gr * np.isin(comp, [M.BASE, M.ARM])
    alb = mix(alb, DIRT, gr)
    if kw.get('snow'):
        sn = np.isin(comp, [M.BASE, M.ARM, M.RIM]) & ((nz > 0.8) | (comp == M.ARM) | (z < 6.0))
        alb = np.where(sn[..., None], mix(SNOWD, SNOWC, np.clip(nz, 0, 1)), alb)
    return alb, (bx, by, bz), emit


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, list(M.HOUSE) + [40, 42])
