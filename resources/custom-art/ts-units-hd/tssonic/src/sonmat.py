"""
sonmat.py - the Disruptor's materials, per pixel of an rcrender.RCRender whose frames give each hit's q coordinates in
its own section (r.lu, r.lv, r.lw = q x, y, z; r.sec names the section: hull, ring or tur).

TS's colours: GDI's ochre track covers and box (TS 144-152, as the HD buildings' and the other units' ochre), black
belts, a dark hull (TS 54-58) with a light grey floor in the trench beside the front box (TS 47-51), TS's house-colour
decks (pure green 0,214,0 x (1 + 1.1 grain)), black posts and frames (TS 59-63), an olive plate at the front (TS
72-79, 128-143), the ochre box's viewport dark glass (TS's dark voxels across its front); the turret dark (TS 57-58) on a grey rim (TS 49), its dish grey with TS's white band across its face
(TS 32-43; Westwood's art: a white dish in panels), blue-grey braces behind it (TS 88-90), olive fittings at its corners,
the emitter arm light grey at the back with a white cap (TS 37-43), dark from its trunnion forward (TS 53-58), its tip
grey (TS 48-51), on zig-zag brackets striped in TS's ochre and black (the FMV's stripes), dark pistons and a dark beam
black at its right end (TS 58-59, 166), the turntable in TS's ochre and black (Westwood's hazard stripes).
"""
import numpy as np
import walls2 as W
from walls2 import smoothstep
import sonmodel as T
from soncam import K_TUR, PPU as PPU_HULL, PPU_T0

GREEN = np.array([0, 214, 0.])
OCHRE = np.array([214, 166, 72.])
OCHRE_D = np.array([176, 138, 62.])
DARK = np.array([44, 44, 46.])
BODY_C = np.array([62, 62, 66.])
TRENCH_C = np.array([142, 142, 146.])
GREY = np.array([142, 142, 146.])
GREY_L = np.array([176, 176, 180.])
WHITE = np.array([208, 208, 206.])                   # TS's light band (TS 32-43, mostly 39-43)
BLACK_C = np.array([24, 24, 26.])
OLIVE_C = np.array([108, 100, 68.])
BLUE_C = np.array([112, 116, 150.])
STRUT_C = np.array([122, 122, 126.])
EMIT_C = np.array([226, 226, 220.])
TIP_C = np.array([52, 52, 56.])
ARM_CAP_C = np.array([214, 214, 210.])              # TS 37 (210) at the arm's back end
ARM_C = np.array([170, 170, 172.])                  # TS 41-43 (161-178)
ARM_TIP_C = np.array([112, 112, 116.])              # TS 48-51 (97-121)
GLASS_LO = np.array([28, 34, 42.])                   # the viewport's glass (TS's dark voxels across the box's front): dark,
GLASS_HI = np.array([84, 98, 116.])                  # the sky's reflection lighter towards its top (the MCV's, the War Factory's)
COIL_C = np.array([62, 62, 66.])                    # TS 53-58 (36-76)
STEEL = np.array([124, 124, 128.])
BRACKET_C = np.array([46, 46, 50.])                 # TS 57-58
PISTON_C = np.array([44, 44, 48.])
HAZ_Y = np.array([214, 166, 72.])
HAZ_K = np.array([30, 28, 26.])
GRIME = np.array([112, 104, 78.])
FILL = 0.32
PPU = 6.27
KS = K_TUR / (PPU_T0 / PPU_HULL)                     # v4's turret on screen against v3's: its stripes keep v3's width

PAINT = {T.OCHRE: OCHRE, T.BELT: DARK, T.BODY: BODY_C, T.BLACK: BLACK_C, T.OLIVE: OLIVE_C, T.TRENCH: TRENCH_C,
         T.RING: OCHRE, T.HAZARD: HAZ_Y, T.RIM: GREY, T.BASE: np.array([50, 50, 54.]),
         T.HOUSING: np.array([50, 50, 54.]), T.DISH: GREY_L, T.DISH_W: WHITE, T.STRUT: STRUT_C, T.BRACE: BLUE_C,
         T.EMIT: EMIT_C, T.EMIT_TIP: TIP_C, T.KHAKI: OLIVE_C, T.ARM_CAP: ARM_CAP_C, T.ARM: ARM_C, T.ARM_BAND: ARM_C * 1.05,
         T.COIL: COIL_C, T.ARM_TIP: ARM_TIP_C, T.AXLE: STEEL, T.BRACKET: BRACKET_C, T.PISTON: PISTON_C,
         T.ROD: STEEL * 0.62, T.SPRING: COIL_C * 1.2, T.CROSS: np.array([50, 50, 54.]), T.GLASS: (GLASS_LO + GLASS_HI) / 2}
GLOSSY = (T.EMIT, T.EMIT_TIP, T.BLACK, T.RIM, T.BRACE, T.ARM_CAP, T.ARM, T.ARM_BAND, T.COIL, T.ARM_TIP, T.AXLE,
          T.PISTON, T.ROD, T.SPRING, T.GLASS)


def grain_of(r, scale=1.0):
    X, Y, Z = r.lu * PPU * scale, r.lv * PPU * scale, r.lw * PPU * scale
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
    bz = np.zeros(sh, np.float32)
    grain = grain_of(r, scale=1 / 1.5)
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
    turp = hm & (sec == 'tur')

    for c, col in PAINT.items():
        put((comp == c) & hm, col * g1)
    house = is_(*T.HOUSE)
    put(house, GREEN * (1 + 1.1 * grain)[..., None])
    seam = np.zeros(sh, bool)
    up = np.zeros(sh, np.float32)

    # ------------------------------------------------------------------ the hull
    oc = is_(T.OCHRE) & hullp
    if oc.any():
        # the track covers in plates (joints across their tops and skirts), a joint along the skirt, bolts along its
        # foot
        pod = oc & ((y < 6.2) | (y > 18.8)) & ~((x > 31.8) & (x < 43.2) & (z > 7.05) & (y < 20.2))
        seam |= pod & (top | side) & (phase(x, 4.6, 2.3) < 0.07) & (x > 3.0) & (x < 43.5) & (np.abs(x - 22.5) > 1.0)
        seam |= pod & side & (np.abs(z - 4.6) < 0.07)
        up += (pod & side) * bolts(x, z, [(xb, 3.55) for xb in list(np.arange(6.0, 20.0, 1.15)) +
                                          list(np.arange(27.0, 41.5, 1.15))], 0.15)
        # the ochre box: a hatch on its top, its handle; a joint round its middle
        ob = oc & (x > 33.0) & (x < 41.5) & (y > 13.5)
        seam |= ob & top & (z > 10.8) & rect_seam(x, y, 37.5, 40.5, 15.3, 18.7, 0.07)
        up += (ob & top & (z > 10.8)) * rect(x, y, 38.2, 39.8, 16.8, 17.2)
        seam |= ob & side & (np.abs(z - 7.5) < 0.07)
    gl = is_(T.GLASS)
    if gl.any():
        # the viewport's glass: the sky's reflection lighter towards its top, a soft sheen across it
        t = np.clip((z - 8.6) / 1.4, 0, 1)
        gcol = GLASS_LO * (1 - t)[..., None] + GLASS_HI * t[..., None]
        sheen = phase(0.9 * x + y + 1.3 * z, 3.2, 0.0) < 0.35
        put(gl, gcol * (1 + 0.3 * sheen)[..., None])
    bl = is_(T.BELT)
    if bl.any():
        # the belts' grousers
        run = bl & ~side
        put(run & (phase(x + 0.6 * z, 0.75) < 0.16), DARK * 1.9 * g1)
        up += 0.4 * (run & (phase(x + 0.6 * z, 0.75) < 0.16))
    ol = is_(T.OLIVE) & hullp
    if ol.any():
        # two vent grilles in the front plate (Westwood's front)
        for ya, yb in ((13.6, 16.4), (17.0, 19.8)):
            v = ol & front & rect(y, z, ya, yb, 5.6, 7.6)
            put(v, BLACK_C * 1.6 * g1)
            put(v & (phase(z, 0.4, 5.8) < 0.08), OLIVE_C * 0.9 * g1)
            seam |= ol & front & rect_seam(y, z, ya, yb, 5.6, 7.6, 0.06)
    bd = is_(T.BODY) & hullp
    if bd.any():
        # TS's light grey floor in the trench beside the front box; TS's ochre band across behind it
        put(bd & top & (y > 13.0) & (x > 24.0) & (x < 44.0), TRENCH_C * g1)
        seam |= bd & top & (y > 13.0) & (x > 24.0) & (x < 44.0) & (phase(x, 3.0, 25.0) < 0.07)
        put(bd & top & (x > 21.0) & (x < 24.8) & (y < 12.0), OCHRE * g1)
        put(bd & top & (x > 21.0) & (x < 24.8) & (y >= 12.0), OCHRE_D * 0.8 * g1)
    # v4: the house colour is plain, the rear grille's fins too (Luke: grilles, detail and black lines on the
    # house-colour areas look fuzzy in the game as the unit moves); its shapes and bevels carry it
    # ------------------------------------------------------------------ the turret
    hz = is_(T.HAZARD)
    if hz.any():
        # Westwood's hazard stripes round the turntable (TS's ochre and black)
        put(hz & (phase(x - y, 1.7 / KS) < 0.42 / KS), HAZ_K * g1)
    bs = is_(T.BASE) & turp
    if bs.any():
        # the base's plates: a joint across the side blocks
        seam |= bs & top & (np.abs(x - 12.0) < 0.06) & ((y < 5.2) | (y > 12.8))
    bm = is_(T.CROSS) & turp
    if bm.any():
        # the beam across in front of the dish: black at its right end (TS's), a joint in its top, bolts along it
        put(bm & (y < 6.0), BLACK_C * 1.2 * g1)
        seam |= bm & top & (np.abs(y - 9.0) < 0.06)
        up += (bm & top) * bolts(x, y, [(xb, yb) for xb in (11.35, 12.45) for yb in (6.4, 7.8, 10.2, 11.6)], 0.16)
        seam |= bm & (nu > 0.7) & (np.abs(z - 3.4) < 0.06)
    am = is_(T.ARM_CAP, T.ARM, T.ARM_BAND, T.COIL, T.ARM_TIP) & turp
    if am.any():
        # the arm: s along it from its back end, a the angle round it (0 on its right side, up at pi/2)
        P0, U = T.ARM_P0, T.ARM_U
        dx, dy, dz = x - P0[0], y - P0[1], z - P0[2]
        s = dx * U[0] + dy * U[1] + dz * U[2]
        e2 = np.cross(U, (0.0, 1.0, 0.0)); e2 = -e2 if e2[2] < 0 else e2
        a = np.arctan2(dx * e2[0] + dy * e2[1] + dz * e2[2], dy)
        endf = np.abs(nu * U[0] + nw * U[2]) > 0.8
        # the cap's joint, the band's bolts (on its top half), the trunnion band's joint, the tip's seam and its end's
        # ring
        seam |= am & ~endf & (np.abs(s - 0.18) < 0.05)
        band = is_(T.ARM_BAND) & ~endf & (s > 0.9) & (s < 1.7)
        up += band * bolts(s, a * 1.1, [(1.3, aa * 1.1) for aa in np.deg2rad([25, 70, 110, 155])], 0.13)
        seam |= is_(T.ARM_BAND, T.COIL) & ~endf & ((np.abs(s - 2.45) < 0.04) | (np.abs(s - 2.72) < 0.04) |
                                                  (np.abs(s - 3.55) < 0.04) | (np.abs(s - 3.82) < 0.04))
        tp_ = is_(T.ARM_TIP)
        seam |= tp_ & ~endf & (np.abs(s - 6.3) < 0.05)
        rr = np.sqrt(np.maximum((dx - s * U[0]) ** 2 + (dy - s * U[1]) ** 2 + (dz - s * U[2]) ** 2, 0))
        seam |= tp_ & endf & (s > 6.9) & (np.abs(rr - 0.36) < 0.05)
    bk = is_(T.BRACKET) & turp
    if bk.any():
        # the zig-zag brackets striped across, as the FMV's, in TS's ochre and black (the turntable's)
        put(bk, HAZ_Y * g1)
        put(bk & (phase(x + 0.55 * z, 0.62 / KS) < 0.16 / KS), HAZ_K * g1)
    ds = is_(T.DISH)
    if ds.any():
        # its face (concave, forward): TS's white band across the middle (Westwood's white panels), grey frame above and
        # below; panel joints between its panels and along the band's edges
        fr = ds & (nu > 0.3)
        put(ds, GREY * g1)
        put(fr & (z > 6.6) & (z < 10.6), WHITE * g1)
        seam |= fr & ((np.abs(z - 6.6) < 0.07) | (np.abs(z - 10.6) < 0.07))
        ys = np.linspace(0.2, 18.6, 13)[1:-1]
        seam |= ds & (np.min(np.abs(y[..., None] - ys), axis=-1) < 0.06) & ~top
        put(ds & (nu < -0.3), GREY * g1)
    sp = is_(T.STRUT) & turp
    if sp.any():
        # the dish's post: blue-grey at its top (TS's)
        put(sp & (z > 9.6) & (x < 8.4), BLUE_C * g1)
    ri = is_(T.RIM)
    if ri.any():
        th = np.arctan2(y - T.TC[1], x - T.TC[0])
        up += 0.5 * (ri & top & (phase(th, 2 * np.pi / 16) < 0.05))
    house_seam = seam & house
    other = seam & ~house & hm
    put(house_seam, GREEN * 0.62 * (1 + 1.1 * grain)[..., None])
    alb[other] *= 0.62
    bz -= 0.35 * seam
    bz += 0.5 * up * hm

    # ------------------------------------------------------------------ grime from the ground (the hull), the fill light
    low = hullp & ~house
    dust = smoothstep(4.5, 0.5, r.z) * 0.5
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
    return alb, (np.zeros(sh, np.float32), np.zeros(sh, np.float32), bz), emit


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, T.HOUSE)
