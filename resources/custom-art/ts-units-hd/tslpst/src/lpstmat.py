"""
lpstmat.py - the Mobile Sensor Array's materials, per pixel of an rcrender.RCRender whose frames give each hit's q
coordinates in TS's voxel section (r.lu, r.lv, r.lw = q x, y, z).

TS's colours: GDI's ochre on the body (TS 144-152), darker on the keel and decks; TS's house-colour panels (pure green
0,214,0 x (1 + 1.1 grain)); dark grey track covers and bumpers, black belts, a dark mast; the cab's windows blue-grey
(TS's blue-grey voxels there); yellow lamps; TS's small dark red marks.  Detail where TS's voxel marks the place, from
the fan-made HD sensor arrays Luke sent (Tiberium Essence, Tiberian Sun Rising, Tiberian Sun Redux): the bands across
the sensor pole where TS has its lighter khaki voxels, the panels along it, the plates of the track covers, the
louvres along the dark grey cradle under the pole, the recess in the pole's front end, the lid of the dish's casing, the stair
treads, the hatch on the block's roof.
"""
import numpy as np
import walls2 as W
from walls2 import smoothstep
import lpstmodel as T

GREEN = np.array([0, 214, 0.])
OCHRE = np.array([214, 166, 72.])
OCHRE_D = np.array([176, 138, 62.])
KHAKI = np.array([226, 200, 132.])
COVER_C = np.array([112, 112, 116.])
DARK = np.array([44, 44, 46.])
STEEL_D = np.array([70, 70, 74.])
STEEL = np.array([120, 120, 126.])
GLASS_LO = np.array([60, 72, 104.])
GLASS_HI = np.array([132, 150, 184.])
LAMP_C = np.array([255, 226, 120.])
RED = np.array([150, 52, 36.])
GRIME = np.array([112, 104, 78.])
TREAD_O = np.array([66, 66, 42.])                    # TS's tread: dark olive (76) and brown (155-159)
TREAD_B = np.array([92, 74, 42.])
FILL = 0.32
PPU = 6.24

PAINT = {T.HOUSING: OCHRE, T.BLOCK: OCHRE, T.STAIR: OCHRE, T.CAB: OCHRE, T.DECK: OCHRE_D, T.KEEL: OCHRE_D,
         T.COVER: COVER_C, T.BELT: DARK, T.WHEEL: STEEL_D, T.HUB: np.array([142, 142, 148.]), T.CORE: np.array([20, 20, 20.]),
         T.BUMPER: np.array([82, 82, 86.]), T.MAST: np.array([40, 40, 42.]), T.LAMP: LAMP_C, T.REARLAMP: LAMP_C,
         T.DISH: np.array([150, 152, 158.]), T.HINGE: np.array([64, 64, 68.]), T.MOUNT: OCHRE,
         T.CRADLE: np.array([78, 78, 82.])}
GLOSSY = (T.BUMPER, T.MAST, T.HUB, T.LAMP, T.REARLAMP, T.DISH, T.HINGE)
RIBS = ((6.0, 8.0), (18.0, 20.0), (23.0, 25.0), (31.0, 34.0))     # TS's lighter bands across the pole (q x)


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
    Rw = np.asarray(r.pose_R, float)
    out = N @ Rw
    return out[..., 0], out[..., 1], out[..., 2]


def rect_seam(a, b, a0, a1, b0, b1, w=0.07):
    inside = (a > a0 - w) & (a < a1 + w) & (b > b0 - w) & (b < b1 + w)
    return inside & ((np.abs(a - a0) < w) | (np.abs(a - a1) < w) | (np.abs(b - b0) < w) | (np.abs(b - b1) < w))


def rect(a, b, a0, a1, b0, b1):
    return (a > a0) & (a < a1) & (b > b0) & (b < b1)


def materials(r, occ=None):
    comp = r.comp
    sh = comp.shape
    hm = r.hitmask
    alb = np.zeros(sh + (3,), np.float32)
    emit = np.zeros(sh + (3,), np.float32)
    bz = np.zeros(sh, np.float32)
    grain = grain_of(r, scale=1 / 1.5)
    g1 = (1 + 0.45 * grain)[..., None]
    x, y, z = r.lu, r.lv, r.lw
    nu, nv, nw = local_normals(r)
    top = nw > 0.7
    vert = np.abs(nw) < 0.35
    right = vert & (nv < -0.7)
    left = vert & (nv > 0.7)
    front = vert & (nu > 0.7)
    back = vert & (nu < -0.7)
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])
    is_ = lambda *cs: np.isin(comp, cs) & hm

    for c, col in PAINT.items():
        put((comp == c) & hm, col * g1)
    house = is_(*T.HOUSE)
    put(house, GREEN * (1 + 1.1 * grain)[..., None])
    seam = np.zeros(sh, bool)
    up = np.zeros(sh, np.float32)

    # ------------------------------------------------------------------ the sensor pole
    hs = is_(T.HOUSING)
    if hs.any():
        # TS's lighter bands across it (straps, raised), panel joints between them along its top
        band = hs & np.any([(x > a) & (x < b) for a, b in RIBS], axis=0) & (top | right | (z > 13.6))
        alb[band] *= 1.07
        up += 0.45 * band
        for a, b in RIBS:
            seam |= hs & (top | right) & ((np.abs(x - a) < 0.07) | (np.abs(x - b) < 0.07))
        seam |= hs & top & (np.abs(y - (6.0 + T.POLE_Y) / 2) < 0.07) & (x > 1.6) & (x < 36.6)
        seam |= hs & top & (phase(x, 4.4, 12.9) < 0.07) & ~band
        # its front end set in under its tip (TS's recess), in shadow
        put(hs & front & (x < 36.2) & (z < 12.1), OCHRE_D * 0.8 * g1)
    # the cradle under its back half: TS's dark grey, louvred along its sides
    cr = is_(T.CRADLE)
    if cr.any():
        seam |= cr & vert & (np.abs(nu) < 0.5) & (phase(z, 0.5, 7.25) < 0.08) & (z > 6.6)
    # ------------------------------------------------------------------ the block, the stairs, the cab
    bl = is_(T.BLOCK)
    if bl.any():
        # the hatch on its roof by the mast (TS's blue-grey voxels there), TS's red mark high on its left side
        t = bl & top
        h = t & rect(x, y, 11.6, 14.4, 12.6, 14.4)
        put(h, STEEL_D * g1)
        seam |= t & rect_seam(x, y, 11.6, 14.4, 12.6, 14.4, 0.08)
        put(bl & left & rect(x, z, 5.0, 7.0, 13.0, 14.0), RED * g1)
        put(bl & left & rect(x, z, 12.0, 14.0, 11.05, 12.0), RED * g1)
        seam |= bl & top & (np.abs(x - 9.0) < 0.07)
    st = is_(T.STAIR)
    if st.any():
        tread = st & top & (phase(x, 1.0, 16.0) < 0.08)
        seam |= tread
    cb = is_(T.CAB)
    if cb.any():
        # the windows (TS's blue-grey): the windscreen across its front above the green panel, round the corner onto
        # the band of side windows along its left side
        wf = cb & front & (x > 35.7) & rect(y, z, T.SIDE_Y + 0.15, 17.85, 12.1, 14.9)
        wl = cb & left & (y > 17.8) & rect(x, z, 29.2, 35.8, 12.1, 14.9)
        win = wf | wl
        tg = np.clip((z - 12.0) / 3.0, 0, 1)
        gcol = GLASS_LO * (1 - tg)[..., None] + GLASS_HI * tg[..., None]
        np.copyto(alb, gcol.astype(np.float32), where=win[..., None])
        seam |= wf & ((np.abs(y - 14.3) < 0.07) | (np.abs(y - 17.2) < 0.07))
        seam |= wl & ((np.abs(x - 32.4) < 0.07) | (np.abs(x - 34.6) < 0.07))
        # TS's dark recesses low on its front under the green panel, its red mark on the left side
        put(cb & front & (x > 36.5) & rect(y, z, 12.8, 16.6, 6.8, 8.8), np.array([40, 40, 42.]) * g1)
        put(cb & left & (y < 17.2) & rect(x, z, 29.1, 30.0, 11.0, 12.0), RED * g1)
        seam |= cb & top & rect_seam(x, y, 30.0, 34.2, 11.4, 16.2, 0.08)
    # ------------------------------------------------------------------ the running gear
    cv = is_(T.COVER)
    if cv.any():
        seam |= cv & (top | vert) & (phase(x, 4.6, 2.5) < 0.08) & (x > 1.0) & (x < 36.2)
        seam |= cv & vert & (np.abs(z - 4.35) < 0.07)
    belt = is_(T.BELT)
    if belt.any():
        # the running surface: black, its tread a voxel in from the outer side olive-brown (TS's), in links
        run = belt & ~(np.abs(nv) > 0.7)
        inn = np.where(y < T.YC, y - T.BELTS[0][0], T.BELTS[1][1] - y)          # depth in from the outer side
        tread = run & (inn > 0.95) & (inn < 2.05)
        link = np.floor(x / 0.6).astype(int) % 3
        put(tread, np.where((link == 0)[..., None], TREAD_O, TREAD_B) * g1)
        lk = run & (phase(x + 0.5 * z, 0.6) < 0.1)
        alb[lk] *= 0.55; bz -= 0.4 * lk
    dish = is_(T.DISH)
    if dish.any():
        # the casing's lid: a seam round its front face
        seam |= dish & front & rect_seam(y, z, 6.55, T.POLE_Y - 0.55, 8.35, 9.65, 0.06)
    mast = is_(T.MAST)
    if mast.any():
        put(mast & (z > 22.2), STEEL * g1)
    lamps = is_(T.LAMP, T.REARLAMP)
    if lamps.any():
        lit = lamps & (np.abs(nu) > 0.6)
        emit += (lit * 0.45)[..., None] * alb
        seam |= is_(T.REARLAMP) & back & (np.abs(y - 15.0) < 0.07)
    house_seam = seam & house
    other = seam & ~house & hm
    put(house_seam, GREEN * 0.62 * (1 + 1.1 * grain)[..., None])
    alb[other] *= 0.62
    bz -= 0.35 * seam
    bz += 0.5 * up * hm

    # ------------------------------------------------------------------ grime from the ground, the fill light
    low = hm & ~house & ~is_(T.LAMP, T.REARLAMP)
    dust = smoothstep(4.0, 0.5, r.z) * 0.5
    d = dust * low
    alb[:] = alb * (1 - d[..., None]) + (GRIME * g1) * d[..., None]
    cam = r.cam
    tc = np.array([cam.T[0] * cam.cE, cam.T[1] * cam.cE, cam.sE]); tc = tc / np.linalg.norm(tc)
    nf = np.clip(r.nx * tc[0] + r.ny * tc[1] + r.nz * tc[2], 0, 1) * (1 - np.clip(r.nz, 0, 1))
    if occ is not None:
        nf = nf * (1 - 0.85 * np.clip(occ, 0, 1))
    emit = emit + alb * (FILL * nf)[..., None]
    alb[~hm] = 0
    return alb, (np.zeros(sh, np.float32), np.zeros(sh, np.float32), bz), emit


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, T.HOUSE)
