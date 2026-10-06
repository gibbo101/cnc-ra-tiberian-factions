"""
mempmat.py - the Mobile EMP Cannon's materials, per pixel of an rcrender.RCRender whose frames give each hit's q
coordinates in the section (r.lu, r.lv, r.lw = q x, y, z).

TS's colours (UNITTEM.PAL, lifted as the other HD units' are): the dark ochre hull (TS 148-150), the grey emitter tower,
hatch box, conduits and track housings (TS 42-51), near-black belts (TS 57-63) round light grey wheels (TS 42), TS's
khaki and olive machinery (TS 73, 116, 138-140) on the prongs' inner walls and round the tower's foot; house colour
(pure green 0,214,0 x (1 + 1.1 grain)) on TS's house-colour track covers; the emitter's orb pale and glowing
(Westwood's icon; TS's light grey cap).  Panel joints, bolts, louvres, ribs and grousers where TS's paint and voxel have
the parts.
"""
import numpy as np
import walls2 as W
from walls2 import smoothstep
import mempmodel as T

GREEN = np.array([0, 214, 0.])
OCHRE = np.array([210, 165, 78.])                   # TS 148-150 (133, 109, 56), lifted so it renders as the mod's frames show it
OCHRE_D = np.array([176, 138, 64.])
KHAKI = np.array([150, 132, 86.])                   # TS 138-140
OLIVE = np.array([112, 104, 70.])                   # TS 116, 73
BROWN = np.array([104, 86, 54.])                    # TS 159-160
GREY = np.array([128, 128, 132.])                   # TS 49-51
GREY_L = np.array([182, 182, 186.])                 # TS 42-44
GREY_D = np.array([84, 84, 88.])                    # TS 53-56
DARK = np.array([40, 40, 42.])                      # TS 57-63
BLACK_C = np.array([22, 22, 24.])
ORB_C = np.array([196, 232, 246.])                  # the emitter's orb: TS's light grey cap, glowing pale blue (the icon)
GRIME = np.array([112, 104, 78.])
GLASS_LO = np.array([28, 34, 42.])                   # the cockpit slot's glass: the Disruptor's viewport glass, dark,
GLASS_HI = np.array([84, 98, 116.])                  # the sky's reflection lighter towards its top
FILL = 0.32

PAINT = {T.BELT: DARK, T.WHEEL: GREY_L * 0.92, T.HUB: GREY_D, T.HOUSING: GREY, T.FENDER: GREEN, T.DECK: OCHRE,
         T.LEDGE: KHAKI, T.LIP: GREY, T.TOWER: GREY, T.COLLAR: GREY * 1.12, T.ORB: ORB_C, T.CROWN: GREY_L,
         T.PLINTH: OLIVE, T.BOX: GREY * 1.06, T.PIPE: GREY * 0.9, T.MOUNT: GREY_D, T.EMITTER: ORB_C, T.SLOT: BLACK_C,
         T.GLASS: (GLASS_LO + GLASS_HI) / 2}
GLOSSY = (T.ORB, T.EMITTER, T.CROWN, T.PIPE, T.HUB, T.GLASS)
EMIT = {T.ORB: 0.55, T.EMITTER: 0.6}


def grain_of(r, scale=1.0):
    X, Y, Z = r.lu * 6.26 * scale, r.lv * 6.26 * scale, r.lw * 6.26 * scale
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


def rect(a, b, a0, a1, b0, b1):
    return (a > a0) & (a < a1) & (b > b0) & (b < b1)


def rect_seam(a, b, a0, a1, b0, b1, w=0.07):
    inside = (a > a0 - w) & (a < a1 + w) & (b > b0 - w) & (b < b1 + w)
    return inside & ((np.abs(a - a0) < w) | (np.abs(a - a1) < w) | (np.abs(b - b0) < w) | (np.abs(b - b1) < w))


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
    alb = np.zeros(sh + (3,), np.float32)
    emit = np.zeros(sh + (3,), np.float32)
    grain = grain_of(r, scale=1 / 1.5)
    g1 = (1 + 0.45 * grain)[..., None]
    x, y, z = r.lu, r.lv, r.lw
    w = np.abs(y - T.HYC)
    nu, nv, nw = local_normals(r)
    top = nw > 0.7
    vert = np.abs(nw) < 0.35
    side = vert & (np.abs(nv) > 0.7)
    front = vert & (nu > 0.7)
    back = vert & (nu < -0.7)
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])
    is_ = lambda *cs: np.isin(comp, cs) & hm

    for c, col in PAINT.items():
        put((comp == c) & hm, col * g1)
    house = is_(*T.HOUSE)
    put(house, GREEN * (1 + 1.1 * grain)[..., None])
    seam = np.zeros(sh, bool)
    dark = np.zeros(sh, bool)
    up = np.zeros(sh, np.float32)

    # ------------------------------------------------------------------ the tracks
    bl = is_(T.BELT)
    if bl.any():
        # grousers across the runs and round the ends
        run = bl & ~side
        put(run & (phase(x + 0.6 * z, 0.75) < 0.16), DARK * 1.9 * g1)
        up += 0.4 * (run & (phase(x + 0.6 * z, 0.75) < 0.16))
    wh = is_(T.WHEEL)
    if wh.any():
        # the wheels' faces: a rim ring
        for xc, zc, rr in [(T.IDLER, T.END_Z, T.END_R), (T.SPROCKET, T.END_Z, T.END_R)] + \
                          [(xw, T.WHEEL_Z, T.WHEEL_R) for xw in T.WHEELS_X]:
            d = np.hypot(x - xc, z - zc)
            seam |= wh & side & (np.abs(d - (rr - 0.32)) < 0.06)
        # the sprocket's teeth (TS's light grey ends): notches round its rim
        th = np.arctan2(z - T.END_Z, x - T.SPROCKET)
        d = np.hypot(x - T.SPROCKET, z - T.END_Z)
        dark |= wh & side & (d > T.END_R - 0.3) & (phase(th, 2 * np.pi / 10) < 0.12)
    hs = is_(T.HOUSING)
    if hs.any():
        # the housings: a joint along the side, bolts, a louvred vent on the outer side
        sd = hs & side
        seam |= sd & (np.abs(z - 6.9) < 0.06)
        for x0 in (2.0, 27.0):
            v = sd & rect(x, z, x0, x0 + 5.0, 6.1, 6.75)
            dark |= v & (phase(x, 0.55, x0 + 0.25) < 0.1)
            seam |= sd & rect_seam(x, z, x0, x0 + 5.0, 6.1, 6.75, 0.05)
        up += 0.5 * sd * bolts(x, z, [(1.4, 7.5), (9.6, 7.5), (25.3, 7.5), (34.5, 7.5)], 0.16)
    # ------------------------------------------------------------------ the covers (house colour)
    if house.any():
        # joints across the covers where the skirt starts and ends, a joint along the skirt's foot
        seam |= house & top & ((np.abs(x - 10.6) < 0.06) | (np.abs(x - 24.4) < 0.06))
        seam |= house & side & (np.abs(z - 8.0) < 0.06) & (x > 10.6) & (x < 24.4)
        # the right cover's inner edge by the tower's plinth (TS: ochre at x 20..26, y 4..5)
        nt = house & top & (y > 3.95) & (y < 5.2) & (x > 19.8) & (x < 26.2)
        put(nt, OCHRE * g1)
    # ------------------------------------------------------------------ the deck
    dk = is_(T.DECK)
    if dk.any():
        dt = dk & top
        # TS's joints: across at x 18 and 26 and along the middle; a bolted plate under the conduits (TS's khaki at
        # x 12..17)
        seam |= dt & ((np.abs(x - 18.6) < 0.06) | (np.abs(x - 29.6) < 0.06))
        seam |= dt & (np.abs(y - 14.5) < 0.06) & (x > 18.6) & (x < 29.6)
        pl = dt & rect(x, y, 12.3, 18.4, 7.0, 22.0)
        put(pl, OCHRE_D * g1)
        seam |= dt & rect_seam(x, y, 12.3, 18.4, 7.0, 22.0, 0.06)
        up += 0.5 * dt * bolts(x, y, [(12.8, 7.5), (17.9, 7.5), (12.8, 21.5), (17.9, 21.5)], 0.16)
        # a hatch on the deck's front right, its handle; TS's line at x 28 by the box
        seam |= dt & rect_seam(x, y, 29.9, 33.4, 6.4, 11.0, 0.06)
        up += 0.6 * (dt & rect(x, y, 31.4, 31.9, 7.2, 10.2))
        # the front: TS's olive band along its foot, two vents
        fr = dk & front
        put(fr & (z < 4.1), OLIVE * g1)
        seam |= fr & (np.abs(z - 4.1) < 0.06)
        for ya, yb in ((8.0, 12.5), (16.5, 21.0)):
            v = fr & rect(y, z, ya, yb, 5.0, 7.6)
            dark |= v & (phase(z, 0.5, 5.25) < 0.1)
            seam |= fr & rect_seam(y, z, ya, yb, 5.0, 7.6, 0.05)
        # the back - the U's inner end - a door outline (TS's ochre wall between the prongs)
        bk = dk & back
        seam |= bk & rect_seam(y, z, 10.5, 18.5, 3.6, 6.6, 0.06)
        up += 0.5 * bk * bolts(y, z, [(11.0, 4.1), (18.0, 4.1), (11.0, 6.1), (18.0, 6.1)], 0.15)
    lg = is_(T.LEDGE)
    if lg.any():
        # TS's machinery on the prongs' inner walls: olive panels, louvres, brown pipes along them
        inner = lg & side
        put(inner & (z < 4.4), OLIVE * g1)
        seam |= inner & (np.abs(z - 4.4) < 0.06)
        for x0 in (2.0, 7.0):
            v = inner & rect(x, z, x0, x0 + 3.6, 4.8, 6.6)
            dark |= v & (phase(x, 0.5, x0 + 0.25) < 0.1)
            seam |= inner & rect_seam(x, z, x0, x0 + 3.6, 4.8, 6.6, 0.05)
        put(lg & top, KHAKI * 0.9 * g1)
    lp = is_(T.LIP)
    if lp.any():
        seam |= lp & top & (phase(y, 2.3, 9.95) < 0.06)
    # ------------------------------------------------------------------ the emitter
    tw = is_(T.TOWER)
    if tw.any():
        # TS's light and dark stripes up the tower: dark slits on four of its faces, a band at its foot
        th = np.arctan2(y - T.TOWER_C[1], x - T.TOWER_C[0])
        slit = tw & ~top & (phase(th, np.pi / 2, np.pi / 8) < 0.11) & (z > 10.0) & (z < 12.7)
        dark |= slit
        seam |= tw & ~top & (np.abs(z - 9.9) < 0.06)
    co = is_(T.COLLAR)
    if co.any():
        seam |= co & ~top & ((np.abs(z - 13.7) < 0.06) | (np.abs(z - 15.2) < 0.06))
        th = np.arctan2(y - T.TOWER_C[1], x - T.TOWER_C[0])
        up += 0.5 * (co & ~top & (np.abs(z - 14.45) < 0.25) & (phase(th, np.pi / 4, np.pi / 8) < 0.12))
    ob = is_(T.ORB)
    if ob.any():
        # the orb glows pale blue, brighter at its top; facets across it (the icon's crystal)
        t = np.clip((z - 15.9) / 2.0, 0, 1)
        put(ob, (ORB_C * (0.86 + 0.14 * t)[..., None]) * g1)
        th = np.arctan2(y - T.TOWER_C[1], x - T.TOWER_C[0])
        seam |= ob & (phase(th, np.pi / 3) < 0.035) & (z < 17.6)
    pn = is_(T.PLINTH)
    if pn.any():
        th = np.arctan2(y - T.TOWER_C[1], x - T.TOWER_C[0])
        rr = np.hypot(x - T.TOWER_C[0], y - T.TOWER_C[1])
        up += 0.55 * pn * top * (np.abs(rr - 3.85) < 0.22) * (phase(th, np.pi / 4) < 0.14)
    # ------------------------------------------------------------------ the box and the conduits
    bx = is_(T.BOX)
    if bx.any():
        bt = bx & top
        seam |= bt & rect_seam(x, y, 22.0, 28.0, 17.0, 22.6, 0.07)
        up += 0.6 * (bt & rect(x, y, 26.6, 27.1, 18.6, 21.0))
        up += 0.5 * bt * bolts(x, y, [(22.5, 17.5), (27.5, 17.5), (22.5, 22.1), (27.5, 22.1)], 0.15)
        seam |= bx & side & (np.abs(z - 10.0) < 0.06) & (x < 28.85)
    gl = is_(T.GLASS)
    if gl.any():
        # the cockpit slot's glass (the Disruptor's): the sky's reflection lighter towards its top, a soft sheen across it
        t = np.clip((z - T.SLOT_Z[0]) / (T.SLOT_Z[1] - T.SLOT_Z[0]), 0, 1)
        gcol = GLASS_LO * (1 - t)[..., None] + GLASS_HI * t[..., None]
        sheen = phase(0.9 * x + y + 1.3 * z, 3.2, 0.0) < 0.35
        put(gl, gcol * (1 + 0.3 * sheen)[..., None])
    pp = is_(T.PIPE)
    if pp.any():
        # ribbed (the render's hose)
        rib = phase(y, 0.62, 9.7) < 0.14
        seam |= pp & (phase(y, 0.62, 10.01) < 0.05)
        up += 0.45 * (pp & rib)
    mt = is_(T.MOUNT)
    if mt.any():
        up += 0.5 * (mt & top) * bolts(x, y, [(13.2, 8.75), (17.1, 8.75), (13.2, 20.25), (17.1, 20.25)], 0.17)
    em = is_(T.EMITTER)
    if em.any():
        put(em, ORB_C * g1)

    if getattr(r, 'no_fine', False):
        # the 3D model's vertex colours: the paint's areas only (its joints, slots and bolts are finer than the mesh)
        seam[:] = False; dark[:] = False; up[:] = 0
    house_seam = seam & house
    other = seam & ~house & hm
    put(house_seam, GREEN * 0.62 * (1 + 1.1 * grain)[..., None])
    alb[other] *= 0.62
    put(dark & hm & ~house, BLACK_C * g1)
    bz = np.zeros(sh, np.float32)
    bz -= 0.35 * seam
    bz -= 0.25 * dark
    bz += 0.5 * up * hm

    # ------------------------------------------------------------------ grime from the ground, the glow, the fill
    low = hm & ~house & ~is_(T.ORB, T.EMITTER)
    dust = smoothstep(3.5, 0.3, r.z) * 0.5
    d = dust * low
    alb[:] = alb * (1 - d[..., None]) + (GRIME * g1) * d[..., None]
    for c, k in EMIT.items():
        m = is_(c)
        emit[m] += alb[m] * k
    cam = r.cam
    tc = np.array([cam.T[0] * cam.cE, cam.T[1] * cam.cE, cam.sE]); tc = tc / np.linalg.norm(tc)
    nf = np.clip(r.nx * tc[0] + r.ny * tc[1] + r.nz * tc[2], 0, 1) * (1 - np.clip(r.nz, 0, 1))
    if occ is not None:
        nf = nf * (1 - 0.85 * np.clip(occ, 0, 1))
    emit = emit + alb * (FILL * nf)[..., None]
    alb[~hm] = 0
    r.house_px = house_mask(r, alb)
    return alb, (np.zeros(sh, np.float32), np.zeros(sh, np.float32), bz), emit


def house_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, T.HOUSE)


def trim_mask(r, alb):
    return house_mask(r, alb)
