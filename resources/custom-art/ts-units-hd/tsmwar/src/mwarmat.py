"""
mwarmat.py - the Mobile War Factory's materials, per pixel of an rcrender.RCRender whose frames give each hit's q
coordinates in TS's voxel section (r.lu, r.lv, r.lw = q x, y, z).

TS's colours: grey plate (TS 47-49), its chassis and crane dark grey (TS 52-56), black tyres, rails and openings
(TS 59-63), olive boxes (TS 73-76, 117-121), blue-grey joints on the crane (TS 90-92), and TS's house-colour blocks
(pure green 0,214,0 x (1 + 1.1 grain)).  Detail where TS's voxel marks the place: the slots in the rear blocks, the
black and grey panels on the middle section's top, the steps of the nose's hood, the steps of the crane's boom.
"""
import numpy as np
import walls2 as W
from walls2 import smoothstep
import mwarmodel as T

GREEN = np.array([0, 214, 0.])
GREY = np.array([142, 142, 146.])                    # TS 47-49
GREY_D = np.array([78, 78, 82.])                     # TS 52-53
DARK_C = np.array([116, 116, 120.])                  # TS 52 on the rear hatch (TS lights its steps)
CHASSIS_C = np.array([60, 60, 64.])                  # TS 55-56
CRANE_C = np.array([108, 108, 114.])                 # TS 52-56 on top, lit: the crane
BLACK_C = np.array([24, 24, 26.])                    # TS 59-63
TYRE_C = np.array([34, 34, 36.])
OLIVE_C = np.array([86, 82, 54.])                    # TS 73-76, 117-121
BLUE_C = np.array([96, 100, 136.])                   # TS 90-92
CHROME_C = np.array([196, 198, 204.])                # the fenders and the bumper, chrome (Westwood's cameo)
TUBE_C = np.array([176, 176, 182.])                  # the tube on top: TS's grey as TS lights it, toward the cameo's white
GLASS_LO = np.array([28, 34, 42.])                   # the cab's glass: dark, the sky's reflection lighter towards its
GLASS_HI = np.array([84, 98, 116.])                  # top (as the MCV's)
GRIME = np.array([112, 104, 78.])
FILL = 0.32
PPU = 6.26

PAINT = {T.CHASSIS: CHASSIS_C, T.TYRE: TYRE_C, T.HUB: np.array([72, 72, 76.]), T.FENDER: CHROME_C, T.OLIVE: OLIVE_C,
         T.TUBE: TUBE_C, T.CHROME: CHROME_C,
         T.BODY: GREY, T.DARK: DARK_C, T.BLACK: BLACK_C, T.NOSE: GREY, T.CRANE: CRANE_C, T.LIGHT: BLUE_C,
         T.GLASS: (GLASS_LO + GLASS_HI) / 2}
GLOSSY = (T.HUB, T.BLACK, T.LIGHT, T.FENDER, T.CHROME, T.TUBE, T.GLASS)


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
    """small round bumps (bolt heads, rivets) at points of a face's two coordinates."""
    up = np.zeros(a.shape, np.float32)
    for ba, bb in pts:
        d = np.hypot(a - ba, b - bb)
        up += (d < rr) * (1 - d / rr)
    return up


def row(a0, a1, step, b):
    return [(a, b) for a in np.arange(a0, a1 + 1e-6, step)]


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
    side = vert & (np.abs(nv) > 0.7)
    front = vert & (nu > 0.7)
    back = vert & (nu < -0.7)
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])
    is_ = lambda *cs: np.isin(comp, cs) & hm
    name = r.part_names if hasattr(r, 'part_names') else None

    for c, col in PAINT.items():
        put((comp == c) & hm, col * g1)
    house = is_(*T.HOUSE)
    put(house, GREEN * (1 + 1.1 * grain)[..., None])
    seam = np.zeros(sh, bool)
    up = np.zeros(sh, np.float32)

    # ------------------------------------------------------------------ the body
    body = is_(T.BODY)
    if body.any():
        # the rear blocks' black slots (TS: z 8, and z 12 in the frames above them), on their backs
        put(body & back & (x < 4.5) & (((z > 7.9) & (z < 8.8)) | ((z > 11.1) & (z < 12.9))) &
            (np.abs(y - T.YB) > 4.0) & (np.abs(y - T.YB) < 6.0), BLACK_C * g1)
        # panel joints on the middle section's sides, rivets along them
        ms = body & side & (x > 9.9) & (x < 19.1)
        seam |= ms & ((np.abs(z - 12.0) < 0.07) | (np.abs(x - 14.5) < 0.07))
        up += ms * bolts(x, z, row(10.6, 18.4, 0.9, 12.45), 0.14)
        # the cab's walls: the door (a joint round it, its handle, the hinges) and the window ahead of it (a dark
        # frame round the glass)
        cw = body & side & (x > 24.5) & (x < 32.7)
        seam |= cw & rect_seam(x, z, 25.0, 28.0, 4.7, 14.3, 0.07)
        up += cw * bolts(x, z, [(27.45, 9.6), (27.75, 9.6)], 0.16)
        up += cw * bolts(x, z, [(25.25, 6.0), (25.25, 12.9)], 0.2)
        seam |= cw & rect_seam(x, z, 29.2, 32.0, 11.5, 14.1, 0.11)
    gr = is_(T.GREEN)
    if gr.any():
        # the middle section's top: grey panels low on its sides (TS's)
        mt = gr & (x > 13.7) & (x < 19.5) & (z > 12.8) & (z < 18.1) & side
        put(mt & (x < 17.0) & (z < 16.0), GREY * g1)
        house_mt = mt & (x < 17.0) & (z < 16.0)
        house &= ~house_mt
        # seams: the blocks' joints, the roof's plates (round the hatch)
        hz = rect(x, y, 31.2, 34.8, 10.2, 13.8)
        seam |= gr & top & (phase(x, 3.0, 25.5) < 0.06) & (x > 24.5) & (x < 35.5) & ~hz & (z < 18.1)
        blk = gr & (((x > 3.9) & (x < 10.1)) | ((x > 18.9) & (x < 25.1)))
        seam |= blk & side & ((np.abs(z - 16.0) < 0.06) | (np.abs(z - 8.0) < 0.06))
        seam |= blk & top & ((np.abs(x - 7.0) < 0.06) | (np.abs(x - 22.0) < 0.06))
        # a louvred vent in each block's sides, between the joints: a frame, its louvres as ribs
        for xa, xb in ((4.7, 9.3), (19.7, 24.3)):
            v = blk & side & rect(x, z, xa, xb, 9.4, 14.8)
            seam |= blk & side & rect_seam(x, z, xa, xb, 9.4, 14.8, 0.07)
            lv = v & (phase(z, 0.6, 9.7) < 0.09)
            seam |= lv
            up += 0.6 * (v & (phase(z, 0.6, 9.95) < 0.12))
        # the roof hatch: its lid's rim, a handle, two hinges at its back
        rh = gr & top & (z > 18.1) & rect(x, y, 31.3, 34.7, 10.3, 13.7)
        seam |= rh & rect_seam(x, y, 31.75, 34.25, 10.75, 13.25, 0.06)
        up += rh * (rect(x, y, 33.2, 33.5, 11.3, 12.7) * 1.0)
        up += rh * bolts(x, y, [(31.75, 11.0), (31.75, 13.0)], 0.28)
    bl = is_(T.BLACK)
    if bl.any():
        # the black bar behind the middle section's top: louvres across its top, slats down its sides (TS's
        # alternating near-black and dark grey there)
        bar = bl & (x > 9.9) & (x < 14.1) & (z > 12.8)
        put(bar & top & (phase(x, 0.5, 10.25) < 0.09), GREY_D * g1)
        put(bar & side & (phase(x, 1.0, 10.5) < 0.12) & (z > 13.2), GREY_D * 0.8 * g1)
        # bolts along the side rails
        rl = bl & side & (x > 9.9) & (x < 19.1) & (z < 11.1)
        up += rl * bolts(x, z, row(10.7, 18.3, 1.9, 7.0) + row(10.7, 18.3, 1.9, 10.0), 0.17)
    dk = is_(T.DARK)
    if dk.any():
        # the rear hatch: a joint round its back, its steps' joints (TS's), a handle
        seam |= dk & back & rect_seam(y, z, 5.45, 18.55, 14.3, 16.15, 0.07)
        seam |= dk & ~back & ~top & (z > 16.6) & ((np.abs(z - 17.3) < 0.06) | (np.abs(z - 18.1) < 0.06))
        up += (dk & back) * rect(y, z, 10.2, 13.8, 14.75, 15.05)
    # ------------------------------------------------------------------ the nose: its hood's steps (TS's)
    no = is_(T.NOSE)
    if no.any():
        # the grille in the bonnet's front face (the cameo's slatted front): dark behind its slats, framed
        fr = no & front & (x > 43.8)
        gf = fr & rect(y, z, 8.0, 15.0, 5.85, 9.0)
        put(gf, np.array([40, 40, 44.]) * g1)
        slat = gf & (phase(z, 0.45, 6.1) < 0.12)
        put(slat, GREY * 0.85 * g1)
        up += 0.5 * slat
        seam |= fr & rect_seam(y, z, 8.0, 15.0, 5.85, 9.0, 0.07)
        # the bonnet: a joint down its middle and across at the sill
        bon = no & top & (x > 40.75) & (x < 43.5)
        seam |= bon & (np.abs(y - 11.5) < 0.06)
        # a louvred vent in the hood's right side (TS's light voxels there), framed
        nvt = no & side & (y < 8.0) & rect(x, z, 37.6, 41.6, 6.2, 9.4)
        seam |= no & side & (y < 8.0) & rect_seam(x, z, 37.6, 41.6, 6.2, 9.4, 0.07)
        seam |= nvt & (phase(z, 0.55, 6.45) < 0.08)
        up += 0.6 * (nvt & (phase(z, 0.55, 6.7) < 0.12))
        # a joint along the hood's sides where its slats end
        seam |= no & side & (z > 5.9) & (np.abs(z - 5.95) < 0.06) & (x > 33.6)
    # ------------------------------------------------------------------ the crane: the boom's steps, blue-grey joints
    cr = is_(T.CRANE)
    if cr.any():
        # TS's blue-grey clamps at the side plates' tops (TS: x 15..17, z 21..23; dark grey behind them)
        put(cr & (np.abs(y - T.YB) > 2.6) & (x > 15.0) & (x < 18.0) & (z > 21.0), BLUE_C * g1)
        # bolts along the side plates' feet and round the support's sides
        up += (cr & side) * bolts(x, z, row(13.7, 19.3, 0.8, 19.1), 0.15)
        up += (cr & side) * bolts(x, z, [(25.3, 18.1), (29.5, 18.1), (25.3, 19.1), (29.5, 19.1)], 0.16)
    pv = is_(T.LIGHT)
    if pv.any():
        # the pivots: a ring and a pin in the middle
        dp = np.hypot(x - 16.3, z - 22.2)
        seam |= pv & side & (np.abs(dp - 0.5) < 0.06)
        up += (pv & side & (dp < 0.22)) * 1.0
    tu = is_(T.TUBE)
    if tu.any():
        # bands round the tube (the cameo's)
        A = np.subtract(T.TUBE_B, T.TUBE_A); L = np.linalg.norm(A); A = A / L
        s_ = (x - T.TUBE_A[0]) * A[0] + (z - T.TUBE_A[2]) * A[2]
        seam |= tu & ((np.abs(s_ - 2.2) < 0.08) | (np.abs(s_ - 2.6) < 0.08) | (np.abs(s_ - 6.6) < 0.08))
    ol = is_(T.OLIVE)
    if ol.any():
        # the boxes' lids, two straps round each, a handle on their ends
        seam |= ol & side & (np.abs(z - 5.2) < 0.06) & (x < 33.2)
        strap = ol & (x < 33.2) & ((np.abs(x - 29.4) < 0.22) | (np.abs(x - 31.6) < 0.22))
        put(strap, OLIVE_C * 0.72 * g1)
        up += 0.4 * (strap & (np.abs(z - 4.6) < 0.18) & side)
        up += (ol & ~side & ~top & (x < 33.2)) * rect(np.where(y < T.YC, y, 25.0 - y), z, 0.9, 2.3, 4.3, 4.6)
        # the nose's box: its lid's joint, a strap
        nb = ol & (x > 35.5)
        seam |= nb & side & (np.abs(z - 8.6) < 0.06) & (x < 39.6)
        put(nb & (np.abs(x - 39.0) < 0.22), OLIVE_C * 0.72 * g1)
    tyre = is_(T.TYRE)
    if tyre.any():
        # tread across the tyres' running faces: grooves every 20 degrees round each wheel's axle
        xs = np.array(T.WHEELS_OUT + T.WHEELS_FRONT)
        xc = xs[np.argmin(np.abs(x[..., None] - xs), axis=-1)]
        ang = np.degrees(np.arctan2(z - T.Z_WHEEL, x - xc))
        tr = tyre & ~(np.abs(nv) > 0.7) & (phase(ang, 20.0) < 3.5)
        alb[tr] *= 0.6
        # the tyres' side walls: a lighter ring round the hub
        rr = np.hypot(z - T.Z_WHEEL, x - xc)
        alb[tyre & (np.abs(nv) > 0.7) & (np.abs(rr - 1.7) < 0.12)] *= 1.6
    hb = is_(T.HUB)
    if hb.any():
        # the hubs: a rim, six wheel nuts round a cap
        xs = np.array(T.WHEELS_OUT + T.WHEELS_FRONT)
        xc = xs[np.argmin(np.abs(x[..., None] - xs), axis=-1)]
        dh = np.hypot(x - xc, z - T.Z_WHEEL)
        put(hb & (dh > 0.98), np.array([58, 58, 62.]) * g1)
        seam |= hb & (np.abs(dh - 0.98) < 0.06)
        up += hb * bolts(x - xc, z - T.Z_WHEEL,
                         [(0.66 * np.cos(a), 0.66 * np.sin(a)) for a in np.arange(6) * np.pi / 3 + 0.3], 0.15)
        up += 0.8 * (hb & (dh < 0.3))
    # ------------------------------------------------------------------ the cab's windows
    gl = is_(T.GLASS)
    if gl.any():
        ws = gl & (x > 34.0)
        t = np.where(ws, np.clip((z - 11.1) / 3.1, 0, 1), np.clip((z - 11.5) / 2.6, 0, 1))
        gcol = GLASS_LO * (1 - t)[..., None] + GLASS_HI * t[..., None]
        sheen = phase(0.9 * x + y + 1.3 * z, 3.2, 0.0) < 0.35
        put(gl, gcol * (1 + 0.3 * sheen)[..., None])
    house_seam = seam & house
    other = seam & ~house & hm
    put(house_seam, GREEN * 0.62 * (1 + 1.1 * grain)[..., None])
    alb[other] *= 0.62
    bz -= 0.35 * seam
    bz += 0.5 * up * hm

    # ------------------------------------------------------------------ grime from the ground, the fill light
    low = hm & ~house
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
