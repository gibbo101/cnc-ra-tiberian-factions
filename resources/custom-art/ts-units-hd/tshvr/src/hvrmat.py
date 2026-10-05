"""
hvrmat.py - the Hover MLRS's materials, per pixel of an rcrender.RCRender whose frames give each hit's q coordinates in
its own section (r.lu, r.lv, r.lw = q x, y, z; r.sec names the section: hull or rack).

TS's colours: GDI's ochre pontoons (TS 144-152, as the HD buildings' and the other units' ochre) with TS's lighter khaki
end plates (TS 128-135), their rubber skirts TS's dark red-brown (TS 106-109), the front intakes and the humps' vents
dark inside (khaki louvres across the intakes), black hover fans (TS 59-61), TS's light-pink lamps (TS 96); the deck between them grey (TS 44-56) with TS's dark engine deck
at the back (TS 52-58), TS's light grey plate at the front (TS 35-43) and blue-grey bars across both ends (TS 92-95);
the cockpit's frame and the missile pods in house colour (pure green 0,214,0 x (1 + 1.1 grain)), the cockpit's glass
dark; the pods' ochre collars and back bands (TS 144-152), their dark faces (TS 57-60), black antennas.
"""
import numpy as np
import walls2 as W
from walls2 import smoothstep
import hvrmodel as T

GREEN = np.array([0, 214, 0.])
OCHRE = np.array([214, 166, 72.])
KHAKI = np.array([212, 188, 122.])                  # TS 128-133
SKIRT_C = np.array([92, 48, 34.])                   # TS 106-109
BLACK_C = np.array([30, 30, 32.])                   # TS 59-61
DUCT_C = np.array([22, 22, 24.])
LAMP_C = np.array([238, 200, 186.])                 # TS 96 (238, 190, 174)
BUMPER_C = np.array([80, 82, 112.])                 # TS 92-95
DECK_D_C = np.array([82, 82, 86.])                  # TS 52-58
DECK_C = np.array([136, 136, 140.])                 # TS 44-51
DECK_L_C = np.array([200, 200, 202.])               # TS 35-43
SLOT_C = np.array([40, 40, 42.])
FACE_C = np.array([36, 36, 38.])                    # TS 57-60
TUBE_C = np.array([62, 62, 66.])
TIP_C = np.array([196, 48, 36.])                    # the missiles' red tips (the references'; Luke's call: TS's faces are dark)
MAST_C = np.array([34, 34, 36.])
MOUNT_C = np.array([92, 92, 96.])                   # TS 57-60, 79 (lifted: grey metal, not a dark band)
TURN_C = np.array([168, 168, 172.])                 # the pad: light grey (Westwood's white ring) (TS's ring is 57-60, near black: Luke wants no
                                                    # dark band between the rack and the hull)
GLASS_LO = np.array([28, 34, 42.])                  # the canopy: dark, the sky's reflection lighter towards its top
GLASS_HI = np.array([84, 98, 116.])                 # (the MCV's, the War Factory's)
GRIME = np.array([112, 104, 78.])
FILL = 0.32
PPU = 2.95

PAINT = {T.OCHRE: OCHRE, T.KHAKI: KHAKI, T.SKIRT: SKIRT_C, T.FAN: BLACK_C * 1.15, T.DUCT: DUCT_C, T.COWL: BLACK_C,
         T.LAMP: LAMP_C, T.BUMPER: BUMPER_C, T.DECK_D: DECK_D_C, T.DECK: DECK_C, T.DECK_L: DECK_L_C, T.SLOT: SLOT_C,
         T.GLASS: (GLASS_LO + GLASS_HI) / 2, T.COLLAR: OCHRE, T.FACE: FACE_C, T.TUBE: TUBE_C, T.TIP: TIP_C,
         T.MAST: MAST_C, T.MOUNT: MOUNT_C, T.TURNTABLE: TURN_C}
GLOSSY = (T.COWL, T.LAMP, T.BUMPER, T.GLASS, T.TUBE, T.TIP, T.MAST, T.FAN)


def grain_of(r, scale=1.0):
    X, Y, Z = r.lu * 6.0 * scale, r.lv * 6.0 * scale, r.lw * 6.0 * scale
    ax, ay, az = np.abs(r.nx) + 1e-3, np.abs(r.ny) + 1e-3, np.abs(r.nz) + 1e-3
    s_ = ax + ay + az

    def tri(noise, k):
        return (W.sample(noise, Y + k, Z + 2 * k) * ax + W.sample(noise, X + 3 * k, Z + k) * ay +
                W.sample(noise, X + k, Y + 5 * k) * az) / s_
    return tri(W.NOISE_FINE, 0) * 0.035 + tri(W.NOISE_MOTTLE, 17) * 0.05


def phase(v, per, off=0.0):
    return np.abs(np.mod(v - off + per / 2, per) - per / 2)


def local_normals(r):
    N = np.stack([r.nx, r.ny, r.nz], -1)
    out = N @ np.asarray(r.pose_R, float)
    return out[..., 0], out[..., 1], out[..., 2]


def rect_seam(a, b, a0, a1, b0, b1, w=0.07):
    inside = (a > a0 - w) & (a < a1 + w) & (b > b0 - w) & (b < b1 + w)
    return inside & ((np.abs(a - a0) < w) | (np.abs(a - a1) < w) | (np.abs(b - b0) < w) | (np.abs(b - b1) < w))


def rect(a, b, a0, a1, b0, b1):
    return (a > a0) & (a < a1) & (b > b0) & (b < b1)


def bolts(a, b, pts, rr=0.17):
    up = np.zeros(a.shape, np.float32)
    for ba, bb in pts:
        d = np.hypot(a - ba, b - bb)
        up += (d < rr) * (1 - d / rr)
    return up


def materials(r, occ=None):
    comp = r.comp
    sh = comp.shape
    hm = r.hitmask
    sec = getattr(r, 'sec', np.full(sh, 'hull'))
    alb = np.zeros(sh + (3,), np.float32)
    emit = np.zeros(sh + (3,), np.float32)
    grain = grain_of(r)
    g1 = (1 + 0.45 * grain)[..., None]
    x, y, z = r.lu, r.lv, r.lw
    nu, nv, nw = local_normals(r)
    top = nw > 0.7
    vert = np.abs(nw) < 0.35
    side = vert & (np.abs(nv) > 0.7)
    front = vert & (nu > 0.7)
    back = vert & (nu < -0.7)
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])
    is_ = lambda *cs: np.isin(comp, cs) & hm
    hullp = hm & (sec == 'hull')
    rackp = hm & (sec == 'rack')

    for c, col in PAINT.items():
        put((comp == c) & hm, col * g1)
    house = is_(*T.HOUSE)
    put(house, GREEN * (1 + 1.1 * grain)[..., None])
    seam = np.zeros(sh, bool)
    up = np.zeros(sh, np.float32)

    # ------------------------------------------------------------------ the pontoons
    pt = is_(T.OCHRE) & hullp
    if pt.any():
        yi = np.where(y < T.HYC, y, 2 * T.HYC - y)                 # across the pontoon from its outer side (0..5)
        # TS's khaki end plates on the tops (back x 0..7, front x 31..36) and its khaki strip along the inner edge of
        # the back half
        tp = pt & top
        put(tp & ((x < 7.0) | ((x > 31.0) & (x < 38.1))), KHAKI * g1)
        put(tp & (x > 7.0) & (x < 13.0) & (yi > 4.0), KHAKI * g1)
        # the plates' joints across the tops, the hump's louvres (ribs across it, framed), a hatch on the back plate
        seam |= tp & ((np.abs(x - 7.0) < 0.06) | (np.abs(x - 31.0) < 0.06) | (np.abs(x - 20.2) < 0.06) & (z < 7.6))
        hp = pt & top & (z > 7.6) & (x > 13.0) & (x < 25.2)
        lv = hp & rect(x, yi, 14.4, 23.8, 1.1, 3.9)
        seam |= hp & rect_seam(x, yi, 14.4, 23.8, 1.1, 3.9, 0.06)
        seam |= lv & (phase(x, 0.62, 14.4) < 0.07)
        up += 0.5 * (lv & (phase(x, 0.62, 14.71) < 0.12))
        seam |= tp & (z < 7.6) & rect_seam(x, yi, 1.6, 5.2, 1.0, 3.4, 0.06)
        up += (tp & (z < 7.6)) * rect(x, yi, 2.4, 4.4, 2.05, 2.35)
        # the sides: TS's brown band along their foot, a joint along them, plates (joints down them at the hump's ends
        # and between), bolts along the band
        sd = pt & side
        put(sd & (z < 3.25) & (x > 1.0), OCHRE * 0.7 * g1)
        seam |= sd & (np.abs(z - 3.25) < 0.05) & (x > 1.2) & (x < 36.2)
        seam |= sd & (np.abs(z - 4.6) < 0.06) & (x > 1.5) & (x < 36.0)
        seam |= sd & (z > 3.25) & ((np.abs(x - 7.0) < 0.06) | (np.abs(x - 13.0) < 0.06) | (np.abs(x - 20.2) < 0.06) |
                                   (np.abs(x - 25.2) < 0.06) | (np.abs(x - 31.0) < 0.06) | (np.abs(x - 35.25) < 0.06))
        up += sd * bolts(x, z, [(xb, 2.75) for xb in np.arange(6.0, 35.0, 1.6)], 0.14)
    sk = is_(T.SKIRT)
    if sk.any():
        seam |= sk & (phase(x, 1.2, 29.4) < 0.06)
    fn = is_(T.FAN)
    if fn.any():
        # the hover fans: a grille down their sides
        g = fn & vert & (z > 0.4) & (z < 1.9)
        put(g & (phase(x + y, 0.42) < 0.12), DUCT_C * g1)
    dc = is_(T.COWL)
    if dc.any():
        seam |= dc & top & (np.abs(x - 36.6) < 0.06)
    # ------------------------------------------------------------------ the front intakes, the hump vents
    yo_ = np.where(y < T.HYC, y, 2 * T.HYC - y)                 # across the pontoon from its outer side
    inside = (yo_ > T.INTAKE_Y[0] - 0.03) & (yo_ < T.INTAKE_Y[1] + 0.03)
    fx = T.face_x(z)
    # inside the intake dark (the walls' and frames' faces round it, its back); the louvres stay khaki, in its shade
    ik = (hullp & inside & (z > T.INTAKE_Z[0] - 0.03) & (z < T.INTAKE_Z[1] + 0.03) & (x > fx - T.INTAKE_D - 0.08) &
          (x < fx + 0.02) & ~np.isin(comp, (T.KHAKI,)))
    put(ik, DUCT_C * g1)
    # the hump vents: louvres across the slot (Westwood's, the mods')
    hv = is_(T.DUCT) & hullp & (x < 26.0) & front
    put(hv & (phase(z - T.HUMP_VENT[1] - 0.18, 0.31, 0.155) < 0.06), OCHRE * 0.42 * g1)
    # ------------------------------------------------------------------ the deck
    ed = is_(T.DECK_D) & hullp
    if ed.any():
        # the engine deck: TS's dark grille, slats across between a frame
        g = ed & top & rect(x, y, 2.5, 8.4, 5.6, 14.4)
        seam |= ed & top & rect_seam(x, y, 2.5, 8.4, 5.6, 14.4, 0.07)
        put(g & (phase(x, 0.45, 2.5) < 0.12), DECK_D_C * 0.62 * g1)
        up += 0.5 * (g & (phase(x, 0.45, 2.725) < 0.1))
    dk = is_(T.DECK) & hullp
    if dk.any():
        tp = dk & top
        # the mid deck in plates (joints across at x 15.5 and 21.6, along y 10), a hatch at its back (TS's olive patch)
        seam |= tp & ((np.abs(x - 15.5) < 0.06) | (np.abs(x - 21.6) < 0.06) | (np.abs(x - 30.4) < 0.06) |
                      (np.abs(y - 10.0) < 0.06) & (x < 21.6))
        seam |= tp & rect_seam(x, y, 10.8, 14.6, 10.8, 14.2, 0.06)
        up += tp * rect(x, y, 11.4, 11.7, 11.8, 13.2)
        up += tp * bolts(x, y, [(xb, yb) for xb in (16.0, 21.1) for yb in (5.6, 9.4, 10.6, 14.4)], 0.16)
        # the front's slope: louvres across it
        fr = dk & (nu > 0.3) & (x > 33.0)
        seam |= fr & (phase(z, 0.5, 2.0) < 0.06)
    dl = is_(T.DECK_L)
    if dl.any():
        seam |= dl & top & rect_seam(x, y, 22.2, 29.6, 10.9, 14.1, 0.06)
        up += dl * rect(x, y, 28.4, 28.9, 11.8, 13.2)
    bm = is_(T.BUMPER)
    if bm.any():
        up += bm * bolts(y, z, [(yb, 5.5) for yb in (6.0, 8.0, 12.0, 14.0)], 0.16) * (np.abs(nu) > 0.7)
    gl = is_(T.GLASS)
    if gl.any():
        t = np.clip((z - 6.5) / 0.85, 0, 1)
        gcol = GLASS_LO * (1 - t)[..., None] + GLASS_HI * t[..., None]
        sheen = phase(0.9 * x + 1.4 * y, 3.0, 0.0) < 0.4
        put(gl, gcol * (1 + 0.3 * sheen)[..., None])
    cp = is_(T.HOUSE_C) & hullp
    if cp.any():
        seam |= cp & side & (np.abs(z - 6.55) < 0.06)
        seam |= cp & front & (np.abs(y - 7.5) < 0.06)
    # ------------------------------------------------------------------ the rack
    pd = is_(T.POD) & rackp
    if pd.any():
        # the ochre band across the pod's back (TS: its top half and the top's back edge)
        band = pd & ((back & (z > 7.0)) | (top & (x < 0.9)))
        put(band, OCHRE * g1)
        house &= ~band
        # an access panel on the top and on the outer side, joints across the top
        yo = np.where(y < 9.25, y + 0.15, 18.65 - y)
        tp = pd & top
        seam |= tp & rect_seam(x, yo, 4.6, 9.0, 1.2, 6.2, 0.06)
        seam |= tp & (np.abs(x - 2.4) < 0.06)
        up += tp * bolts(x, yo, [(5.1, 1.7), (8.5, 1.7), (5.1, 5.7), (8.5, 5.7)], 0.16)
        os_ = pd & side & (yo < 0.4)
        seam |= os_ & rect_seam(x, z, 3.6, 8.8, 5.6, 8.4, 0.06)
    cl = is_(T.COLLAR)
    if cl.any():
        up += cl * bolts(np.where(np.abs(nv) > 0.7, x, y), z, [(10.47, 5.4), (10.47, 8.6)], 0.15) * side
        seam |= cl & top & (np.abs(x - 10.47) < 0.05)
    fc = is_(T.FACE)
    if fc.any():
        seam |= fc & front & (np.abs(z - 7.52) < 0.05)
    tt = is_(T.TURNTABLE) & hullp
    if tt.any():
        # the pad (the hull's): its top darker inside the step's rim, bolts round the rim, a joint round its side
        sc = T.FH.sc
        dx, dy = (x - T.PAD_C[0]) * sc[0], (y - T.PAD_C[1]) * sc[1]
        rr, th = np.hypot(dx, dy), np.arctan2(dy, dx)
        r0, r1 = T.PAD_R[1], T.PAD_R[0]
        put(tt & top & (rr < r0 - 0.05), TURN_C * 0.78 * g1)
        up += 0.6 * (tt & top & (phase(th, 2 * np.pi / 24) < 0.06) & (np.abs(rr - (r0 + r1) / 2) < 0.14))
        seam |= tt & top & (np.abs(rr - (r0 - 0.05)) < 0.06)
        seam |= tt & ~top & (np.abs(z - (T.PAD_Z[0] + T.PAD_Z[1]) / 2 - 0.1) < 0.05)
    mt = is_(T.MOUNT)
    if mt.any():
        up += mt * top * bolts(x, y, [(3.6, 7.35), (6.6, 7.35), (3.6, 11.15), (6.6, 11.15)], 0.16)

    house_seam = seam & house
    other = seam & ~house & hm
    put(house_seam, GREEN * 0.62 * (1 + 1.1 * grain)[..., None])
    alb[other] *= 0.62
    bz = -0.35 * seam + 0.5 * up * hm

    # ------------------------------------------------------------------ grime from below (the hull), the fill light
    low = hullp & ~house & ~is_(T.LAMP, T.GLASS)
    dust = smoothstep(4.0, 1.0, z) * 0.45
    d = dust * low
    alb[:] = alb * (1 - d[..., None]) + (GRIME * g1) * d[..., None]
    cam = r.cam
    tc = np.array([cam.T[0] * cam.cE, cam.T[1] * cam.cE, cam.sE]); tc = tc / np.linalg.norm(tc)
    nf = np.clip(r.nx * tc[0] + r.ny * tc[1] + r.nz * tc[2], 0, 1) * (1 - np.clip(r.nz, 0, 1))
    if occ is not None:
        nf = nf * (1 - 0.85 * np.clip(occ, 0, 1))
    emit = emit + alb * (FILL * nf)[..., None]
    alb[~hm] = 0
    r.house_px = house
    return alb, (np.zeros(sh, np.float32), np.zeros(sh, np.float32), bz.astype(np.float32)), emit


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, T.HOUSE) & r.house_px
