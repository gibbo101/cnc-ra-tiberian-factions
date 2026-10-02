"""Materials for the Sensor Array: albedo, normal tweaks and glow per pixel of an hd.Render.  House green 0,214,0 x
(1 + 1.1 grain) on the mast's panel and the cab's light panel.  Colours read from GTDPSA (TS lit them: the albedos are
TS's colours / the renderer's shading): a GDI tan-ochre vehicle (the mast a lighter tan), a yellow stripe along the
hull's top edges, dark grey tracks with light road wheels, a blue-grey window, a white-topped pod, light steel
brackets, a dark grey sensor plate with a lighter rim, yellow-ochre outriggers, a black whip antenna.
Overlay (material only, one geometry pass):
  flash=t   GTDPSA_A: the light bar across the sensor plate flashes white-blue and fades (5 frames; TS's damaged half is
            empty: the damaged array's light is out)"""
import numpy as np
from walls2 import sample, smoothstep, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME
import dpsa as M

GREEN = np.array([0, 214, 0.])
OCHRE = np.array([228, 178, 92.])           # the hull (TS 190,145,60 .. 238,174,72 lit)
OCHRE_D = np.array([196, 150, 72.])
WEDGEC = np.array([150, 116, 62.])           # the mast's housing: TS draws it brown (89-153, 72-121, 40-56)
TAN = np.array([226, 188, 116.])            # the mast (TS 198,157,105 / 206,182,113)
STRIPE = np.array([252, 222, 96.])          # TS 255,226,101
TRACKC = np.array([64, 64, 66.])
LINKC = np.array([104, 104, 108.])
WHEELC = np.array([132, 132, 134.])         # TS's road wheels read 121 grey
TYREC = np.array([58, 58, 60.])
HUBC = np.array([86, 86, 90.])
GLASSC = np.array([146, 150, 182.])         # TS 161,161,186
GLASS_H = np.array([214, 218, 240.])
PODW = np.array([234, 234, 230.])
PODD = np.array([74, 74, 78.])
STEEL = np.array([196, 198, 204.])
DARK = np.array([66, 66, 72.])
RAILC = np.array([40, 36, 26.])             # the dark channel up the mast's east side (TS's black line)
DISH_F = np.array([110, 112, 120.])          # the dish's hollow (TS's head: dark grey 60-68, lit to 125-174)
DISH_B = np.array([88, 90, 96.])             # its back
HEADRIM = np.array([172, 172, 154.])        # TS's lighter olive-grey edge
BAROFF = np.array([104, 104, 132.])         # TS 101,101,125
BARON = np.array([220, 224, 255.])
LEGC = np.array([236, 190, 90.])            # TS 255,210,97 / 246,182,80
PADC = np.array([156, 122, 64.])
ANTC = np.array([30, 30, 30.])
DIRT = np.array([118, 98, 66.])

# GTDPSA_A, per frame: the bar's brightness (TS: white, then down through the blues to the plate's grey in 5)
A_LEVELS = (1.0, 0.72, 0.46, 0.22, 0.0)


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


def pose(r):
    """the mast's angle and the plate's unfold, read off the scene (constant fields)."""
    th = r.field('mast_theta', 90.0); un = r.field('head_unfold', 1.0)
    return (float(th.flat[0]) if th.size else 90.0), (float(un.flat[0]) if un.size else 1.0)


def dish_of(r, p):
    """the radar dish's frame for this render (None while the mast isn't up)."""
    th, un = pose(r)
    if th < 89.0:
        return None
    return M.head_pose(p, th, un)


def toward_camera(v):
    return np.array([v.T[0] * v.cE, v.T[1] * v.cE, v.sE])


def materials(r, p=None, occ=None, flash=None, level=0, **kw):
    p = M.P if p is None else p
    lay = r.mk.get('layout', 'ts')
    x, y = M.to_local(r.x, r.y, lay)
    z, comp = r.z, r.comp
    nx, ny, nz = r.nx, r.ny, r.nz
    # normals in the model's own frame (the turned layout swaps them)
    lnx, lny = M.to_local(nx, ny, lay)
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
    low = smoothstep(26.0, 2.0, z)                                # grime up from the ground

    def put(mask, col):
        nonlocal alb
        alb = np.where(mask[..., None], col, alb)

    # ---- tracks: dark belts, the links' edges light; road wheels with dark tyres and hubs
    tr = comp == M.TRACK
    link = phase(x, 7.0, 0.0) < 1.6
    side = np.abs(lny) > 0.7
    tcol = np.where((link & ~side)[..., None] | (side & (phase(x, 7.0, 0.0) < 1.0))[..., None], LINKC * g1, TRACKC * g1)
    put(tr, mix(tcol, DIRT * g1, 0.3 * low * grime))
    bz -= 0.25 * (link & tr & ~side)
    wh = p['wheels']
    wd = np.full(shape, 1e9)
    for xc in wh['xs']:
        wd = np.minimum(wd, np.hypot(x - xc, z - wh['z']))
    put(comp == M.WHEEL, np.where((wd > wh['r'] * 0.78)[..., None], TYREC * g1, WHEELC * g1))
    put(comp == M.HUB, np.where((wd < wh['hub'] * 0.5)[..., None], np.array([170, 170, 172.]) * g1, HUBC * g1))
    # ---- the hull: ochre, panel seams on the deck, grime up the sides; the yellow stripe; the deck plate
    hl = comp == M.HULL
    seam = ((phase(x + 6.0, 30.0, 0.0) < 0.9) | (phase(y + 4.0, 28.0, 0.0) < 0.9)) & top
    hc = mix(OCHRE * g1 * (1 - 0.14 * seam)[..., None], OCHRE_D * g1, 0.25 * smoothstep(0.3, 1.2, mott * 3 + 0.5))
    hc = mix(hc, DIRT * g1, (0.35 * low + 0.12 * grime) * (~top))
    put(hl, hc)
    bz -= 0.25 * seam * hl
    put(comp == M.STRIPE, STRIPE * g1)
    dp = comp == M.DECKP
    tread = (np.abs(phase(x + y, 5.0, 0.0) - 2.5) < 0.7) & (np.abs(phase(x - y, 5.0, 0.0) - 2.5) < 0.7)
    put(dp, OCHRE_D * g1 * (1 - 0.18 * tread)[..., None])
    bz += 0.3 * tread * dp
    # ---- the cab: ochre, the house-green light panel on its east face (a frame line round it), the window
    cb = comp == M.CAB
    put(cb, mix(OCHRE * g1 * 0.96, DIRT * g1, 0.2 * low))
    put(comp == M.CABG, house)
    gl = comp == M.GLASS
    gq = p['cab']['glass']
    hiband = np.abs((x - gq['x'][0]) - (z - gq['z'][0]) * 1.3 - 8.0) < 2.2
    put(gl, np.where(hiband[..., None], GLASS_H * g1, GLASSC * g1))
    # ---- the wedge: ochre, louvres on its slope; the pod white-topped, dark sides; the brackets steel
    wd_ = comp == M.WEDGE
    lv = (lnx > 0.2) & (phase(x, 6.0, 0.0) < 1.6)
    put(wd_, WEDGEC * g1 * (1 - 0.22 * lv)[..., None])
    bz -= 0.3 * lv * wd_
    pd = comp == M.POD
    put(pd, np.where(top[..., None], PODW * g1, PODD * g1))
    put(comp == M.BRACKET, STEEL * g1)
    # the mast's end cap, the head's arm and hub: light steel (TS: the folded head's end white-grey, the arm a light rod)
    put(comp == M.ARMH, np.where(top[..., None], np.array([182, 182, 186.]) * g1, np.array([150, 150, 156.]) * g1))
    # ---- the mast: tan, ring seams, the house-green panel on its south face, a dark channel up its east side
    th, un_ = pose(r)
    ms = comp == M.MAST
    if ms.any():
        pv, u, bot, top_ = M.mast_axis(p, th)
        w = np.array([np.sin(np.radians(th)), 0.0, -np.cos(np.radians(th))])
        dx, dy, dz = x - pv[0], y - pv[1], z - pv[2]
        s = dx * u[0] + dz * u[2]
        ang = np.degrees(np.arctan2(dx * w[0] + dz * w[2], dy))          # 0 south, 90 east
        ring = phase(s + 2.0, 26.0, 0.0) < 1.0
        chan = np.abs(ang - 90.0) < 13.0
        mc = mix(TAN * g1 * (1 - 0.12 * ring)[..., None], DIRT * g1, 0.12 * grime)
        mc = np.where(chan[..., None], RAILC * g1, mc)
        panel = M.mast_panel(x, y, z, th, p)
        pseam = phase(s - p['mast']['green']['s'][0], (p['mast']['green']['s'][1] - p['mast']['green']['s'][0]) / 3.0, 0.0) < 0.9
        mc = np.where(panel[..., None], house * (1 - 0.14 * pseam)[..., None], mc)
        put(ms, mc)
        bz -= 0.25 * ring * ms
    # ---- the radar dish: its hollow dark grey with panel rings and gores, a light rim; its back darker, ribbed; exact
    #      normals from its paraboloid; the light bar (A) up its hollow from the middle to the rim
    hdm = comp == M.HEAD
    df = dish_of(r, p) if hdm.any() else None
    if df is not None:
        n = df['n']; f = df['focal']; Rr = df['R']
        Px, Py, Pz = x - df['C'][0], y - df['C'][1], z - df['C'][2]
        w = Px * n[0] + Py * n[1] + Pz * n[2]
        rho = np.sqrt(np.maximum(Px * Px + Py * Py + Pz * Pz - w * w, 0))
        u1 = np.cross(n, [0, 0, 1.0]); u1 /= np.linalg.norm(u1); u2 = np.cross(n, u1)      # u2 points down the face
        a1 = Px * u1[0] + Py * u1[1] + Pz * u1[2]
        a2 = -(Px * u2[0] + Py * u2[1] + Pz * u2[2])                                    # up the face
        ang = np.arctan2(a2, a1)
        # the surface's gradient (away from the hollow), in the model's frame
        Vx, Vy, Vz = x - df['V'][0], y - df['V'][1], z - df['V'][2]
        wv = Vx * n[0] + Vy * n[1] + Vz * n[2]
        gx = (Vx - wv * n[0]) / (2 * f) - n[0]; gy = (Vy - wv * n[1]) / (2 * f) - n[1]; gz = (Vz - wv * n[2]) / (2 * f) - n[2]
        gl_ = np.sqrt(gx * gx + gy * gy + gz * gz) + 1e-9
        gx, gy, gz = gx / gl_, gy / gl_, gz / gl_
        cam = toward_camera(r.view)
        cx_, cy_ = M.to_local(np.array(cam[0]), np.array(cam[1]), lay)
        front = (-(gx * cx_ + gy * cy_ + gz * cam[2])) > 0                   # the hollow faces the camera here
        ring = np.abs(((rho / Rr) * 4.0) % 1.0 - 0.5) > 0.46
        gore = np.abs(((ang / (2 * np.pi)) * 12.0) % 1.0 - 0.5) > 0.47
        rim = rho > Rr * 0.86
        fc = DISH_F * g1 * (1 - 0.16 * (ring | gore))[..., None]
        bc = DISH_B * g1 * (1 - 0.14 * gore)[..., None]
        dc = np.where(front[..., None], fc, bc)
        dc = np.where(rim[..., None], HEADRIM * g1, dc)
        put(hdm, dc)
        # exact normals, the visible side's, back in the world's frame
        sgn = np.where(front, -1.0, 1.0)
        enx, eny, enz = gx * sgn, gy * sgn, gz * sgn
        wnx, wny = M.to_world(enx, eny, lay)
        bx = np.where(hdm, wnx - nx, bx); by = np.where(hdm, wny - ny, by); bz = np.where(hdm, enz - nz, bz)
        # the light bar
        bw = p['head']['bar']['w']
        barm = hdm & front & (np.abs(a1) <= bw / 2) & (a2 >= 3.0) & (a2 <= Rr * 0.84)
        sb = np.clip((a2 - 3.0) / (Rr * 0.84 - 3.0), 0, 1)
        lev = np.zeros(shape, np.float32)
        if flash is not None and level == 0:
            lev = A_LEVELS[int(flash) % 5] * (0.55 + 0.45 * sb)
        put(barm, mix(BAROFF * g1, BARON, lev))
        emit = np.where(barm[..., None], np.array([110, 118, 200.]) * lev[..., None], emit)
    # ---- the outriggers, the pads, the antenna
    put(comp == M.LEG, LEGC * g1)
    put(comp == M.PAD, mix(PADC * g1, DIRT * g1, 0.3))
    put(comp == M.ANT, ANTC * g1)
    return alb, (bx, by, bz), emit


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, list(M.HOUSE) + [M.MAST, 43])
