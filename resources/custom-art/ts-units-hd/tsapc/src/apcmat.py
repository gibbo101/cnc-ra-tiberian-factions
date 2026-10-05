"""
apcmat.py - the Amphibious APC's materials, per pixel of an rcrender.RCRender whose frames give each hit's q
coordinates in the land hull's section (r.lu, r.lv, r.lw = q x, y, z; both hulls are built in it).

TS left the APC in house colour all over (its remap voxels): pure green 0,214,0 x (1 + 1.1 grain) on the hull, its
roof, cupola, hatch, vents, bow and the panels between the wheels, with detail only as thin seams where TS's darker
remap shades draw its panel lines (the joints across the roof and down the sides at x 5, 12, 19, 24 and 31, the side
door between the wheels and the panel over the front wheel, the rear door, the louvred vents on the rear shoulders,
the slot at the front of the roof).  TS's other colours: the dark cupola blocks, the dark block on the roof's front,
the dark bumper across the back, black tyres on grey hubs.
"""
import numpy as np
import walls2 as W
from walls2 import smoothstep
import apcmodel as T

GREEN = np.array([0, 214, 0.])
DARK = np.array([38, 38, 40.])
STEEL_D = np.array([72, 72, 76.])
STEEL = np.array([118, 118, 124.])
GREY = np.array([150, 150, 156.])
GLASS_LO = np.array([34, 44, 56.])
GLASS_HI = np.array([92, 118, 140.])
LAMP_C = np.array([255, 236, 178.])
GRIME = np.array([112, 104, 78.])
FILL = 0.32
PPU = 6.25

PAINT = {T.PERI: np.array([34, 34, 36.]), T.BLOCK: np.array([40, 40, 44.]), T.BUMPER: np.array([42, 42, 44.]),
         T.TYRE: DARK, T.HUB: np.array([176, 176, 182.]), T.CAP: np.array([196, 196, 200.]), T.LAMP: np.array([30, 30, 32.]),
         T.LIGHTHOUSE: np.array([88, 88, 92.]), T.LENS: np.array([255, 214, 150.])}
GLOSSY = (T.PERI, T.BLOCK, T.HUB, T.CAP, T.LAMP, T.LIGHTHOUSE, T.LENS)


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
    out = np.zeros_like(N)
    for k, (Rw, tw) in r.poses.items():
        m = r.sec == k
        if m.any():
            out[m] = N[m] @ np.asarray(Rw, float)
    return out[..., 0], out[..., 1], out[..., 2]


def rect_seam(a, b, a0, a1, b0, b1, w=0.07):
    inside = (a > a0 - w) & (a < a1 + w) & (b > b0 - w) & (b < b1 + w)
    return inside & ((np.abs(a - a0) < w) | (np.abs(a - a1) < w) | (np.abs(b - b0) < w) | (np.abs(b - b1) < w))


def bolts(a, b, pts, rr=0.17):
    up = np.zeros(a.shape, np.float32)
    for ba, bb in pts:
        d = np.hypot(a - ba, b - bb)
        up += (d < rr) * (1 - d / rr)
    return up


JOINTS = (5.0, 12.0, 19.0, 24.0, 31.0)      # TS's panel joints across the roof and down the sides (q x)
CUP = (15.2, 10.8)                           # the cupola's middle (q x, y)


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
    sidey = vert & (np.abs(nv) > 0.7)
    sidex = vert & (np.abs(nu) > 0.7)
    yh = np.where(y > T.YC, 2 * T.YC - y, y)              # folded onto the right half
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])
    is_ = lambda *cs: np.isin(comp, cs) & hm

    for c, col in PAINT.items():
        put((comp == c) & hm, col * g1)
    house = is_(*T.HOUSE)
    put(house, GREEN * (1 + 1.1 * grain)[..., None])
    seam_h = np.zeros(sh, bool)
    up = np.zeros(sh, np.float32)
    seam_o = np.zeros(sh, bool)

    # ------------------------------------------------------------------ the hull (house colour: TS's panel lines)
    hl = is_(T.HULL, T.SKIRT, T.REAR, T.BOW)
    if hl.any():
        cupola_clear = np.hypot(x - CUP[0], y - CUP[1]) > 3.4
        # the joints across the roof and its shoulders, and down the sides
        for xj in JOINTS:
            seam_h |= hl & ~sidex & (np.abs(x - xj) < 0.07) & cupola_clear & (z > 7.6)
        # the side door between the wheel pair and the front wheel, the panel over the front wheel (TS's darker
        # shades there), a handle on the door
        s = hl & sidey & (yh < 1.2)
        seam_h |= s & rect_seam(x, z, 19.35, 23.65, 4.25, 9.75)
        seam_h |= s & rect_seam(x, z, 24.0, 31.6, 7.75, 9.75)
        up += s * bolts(x, z, [(22.9, 7.0)], 0.3)
        # the rear door between TS's lines at y 5 and 17, over the bumper; its handle
        b = hl & sidex & (nu < -0.7)
        seam_h |= b & rect_seam(y, z, 5.0, 17.0, 6.1, 10.8)
        up += b * bolts(y, z, [(11.0, 8.6)], 0.32)
        # the bow's plates (TS's lines at y 5 and 17 across its front)
        f = hl & (nu > 0.3)
        seam_h |= f & ((np.abs(y - 5.0) < 0.07) | (np.abs(y - 17.0) < 0.07)) & (z > 7.0)
        # a row of small plates along the top of the sides, under the shoulders (Westwood's FMV)
        s2 = hl & sidey & (yh < 1.2) & (z > 10.05) & (z < 10.8)
        tab = s2 & (phase(x, 1.6, 2.4) < 0.2) & (x > 1.8) & (x < 37.4)
        up += 0.7 * tab
        alb[tab & house] *= 1.2
        seam_h |= s2 & (phase(x, 1.6, 2.4) > 0.2) & (phase(x, 1.6, 2.4) < 0.27) & (x > 1.8) & (x < 37.4)
        # the side door's ladder: rungs across it (the reference art's)
        rung = s & (x > 19.85) & (x < 23.15) & ((np.abs(z - 5.0) < 0.13) | (np.abs(z - 6.15) < 0.13) |
                                                (np.abs(z - 7.3) < 0.13) | (np.abs(z - 8.45) < 0.13))
        up += 0.8 * rung
        alb[rung & house] *= 1.3
        seam_h |= s & (x > 19.85) & (x < 23.15) & ((np.abs(z - 4.8) < 0.06) | (np.abs(z - 5.95) < 0.06) |
                                                   (np.abs(z - 7.1) < 0.06) | (np.abs(z - 8.25) < 0.06))
        # the panel over the front wheel (TS's darker shade there): a mesh grille (Westwood's FMV)
        mesh = s & (x > 24.25) & (x < 31.35) & (z > 8.0) & (z < 9.5)
        put(mesh, np.array([34, 34, 36.]) * g1)
        grid = mesh & ((phase(x, 0.42, 24.25) < 0.06) | (phase(z, 0.42, 8.0) < 0.06))
        put(grid, np.array([70, 74, 70.]) * g1)
        # the bow's front: a plain panel between TS's lines at y 5 and 17 (Westwood's lamps on it are their own parts)
        stem = hl & (nu > 0.9)
        seam_h |= stem & rect_seam(y, z, 5.3, 16.7, 8.25, 10.75)
        # the troop ramp in the bow's sloping underside (Westwood's FMV: the troops come out at the front), ribs
        # across it, its hinge at the foot
        ramp = hl & (nu > 0.4) & (nw < -0.4)
        seam_h |= ramp & ((np.abs(y - 5.0) < 0.07) | (np.abs(y - 17.0) < 0.07)) & (z > 2.3) & (z < 7.7)
        rib = ramp & (y > 5.3) & (y < 16.7) & (phase(z, 0.75, 3.0) < 0.09)
        seam_h |= rib
        up += 0.25 * rib
        seam_h |= ramp & (np.abs(z - 2.45) < 0.08) & (y > 5.0) & (y < 17.0)
    vt = is_(T.VENT)
    if vt.any():
        # louvres across the vents on the rear shoulders, a frame round each
        lv = vt & (nw > 0.5) & (phase(x, 0.55, 6.275) < 0.11)
        seam_h |= lv
        up -= 0.3 * lv
    cu = is_(T.CUPOLA, T.HATCH)
    if cu.any():
        d = np.hypot(x - CUP[0], y - CUP[1])
        # the hatch's rim and its handle
        seam_h |= is_(T.HATCH) & top & (np.abs(d - 1.45) < 0.07)
        up += is_(T.HATCH) & top & (np.abs(y - CUP[1]) < 0.12) & (np.abs(x - (CUP[0] - 0.5)) < 0.55)
    cb = is_(T.CAB)
    if cb.any():
        # the windscreen: dark glass across the cab's sloping front, in a frame, a lighter band along its top
        ws = cb & (nu > 0.3) & (nw > 0.3) & (y > 9.0) & (y < 13.8)
        tg = np.clip((z - 13.0) / 0.9, 0, 1)
        gcol = GLASS_LO * (1 - tg)[..., None] + GLASS_HI * tg[..., None]
        np.copyto(alb, gcol.astype(np.float32), where=ws[..., None])
        seam_o |= ws & ((np.abs(y - 11.4) < 0.07))
    ln = is_(T.LENS)
    if ln.any():
        # the lamps lit (Westwood's FMV: the bow's lamps glow orange)
        emit += (ln * 0.55)[..., None] * alb
    bk = is_(T.BLOCK)
    if bk.any():
        seam_o |= bk & top & rect_seam(x, y, 29.45, 30.8, 9.35, 12.8, 0.07)
    # ------------------------------------------------------------------ the wheels
    ty = is_(T.TYRE)
    if ty.any():
        ang = np.arctan2(z - T.Z_WHEEL, x - np.select([np.abs(x - w) < 4.0 for w in T.WHEELS], T.WHEELS, 0.0))
        tread = ty & (np.abs(nv) < 0.5) & (phase(ang, 2 * np.pi / 24) < 0.06)
        alb[tread] *= 0.6; bz -= 0.4 * tread
        side = ty & (np.abs(nv) > 0.5)
        dd = np.hypot(x - np.select([np.abs(x - w) < 4.0 for w in T.WHEELS], T.WHEELS, 0.0), z - T.Z_WHEEL)
        seam_o |= side & (np.abs(dd - 2.5) < 0.06)
    hb = is_(T.HUB)
    if hb.any():
        # TS's hubs: light in the middle, darker to the rim; six wheel nuts
        xw = np.select([np.abs(x - w) < 4.0 for w in T.WHEELS], T.WHEELS, 0.0)
        dh = np.hypot(x - xw, z - T.Z_WHEEL)
        put(hb & (dh > 1.75), np.array([96, 96, 100.]) * g1)
        seam_o |= hb & (np.abs(dh - 1.75) < 0.07)
        up += hb * bolts(x - xw, z - T.Z_WHEEL, [(1.2 * np.cos(a), 1.2 * np.sin(a)) for a in np.arange(6) * np.pi / 3],
                         0.2)
    put(seam_h & house, GREEN * 0.62 * (1 + 1.1 * grain)[..., None])
    bz -= 0.35 * (seam_h & house)
    bz += 0.5 * up * hm
    put(seam_o & ~house & hm, alb * 0.6)
    bz -= 0.3 * (seam_o & ~house & hm)

    # ------------------------------------------------------------------ grime from the ground, the fill light
    low = hm & ~house
    dust = smoothstep(3.0, 0.4, r.z) * 0.45
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
