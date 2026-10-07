"""
apocmat.py - the Apocalypse's materials, per pixel of an rcrender.RCRender whose frames give each hit's q coordinates in
its own section (r.lu, r.lv, r.lw = q x, y, z; r.sec names the section: hull, tur or barl).

RA2's colours (UNITTEM.PAL), lifted so the lit model comes out as light as the mod's frames draw them: the hull olive
(RA2 73), the turret's top a lighter olive (RA2 70), dark grey for the grilles, the hatches, the rocket pods and the
barrels (RA2 53-56), black belts and fittings (RA2 57-62, 166-167), grey road wheels (RA2 13, 43-51); house colour (pure
green 0,214,0 x (1 + 1.1 grain)) where RA2's remap voxels are: the four fuel drums and the turret's skirt, plain (Luke:
no grilles, fine detail or black lines on the house colour).
"""
import os, sys
from paths import HANDOFF
sys.path.insert(0, os.path.join(HANDOFF, 'renderer'))
import numpy as np
import walls2 as W
from walls2 import smoothstep
import apocmodel as T

GREEN = np.array([0, 214, 0.])
HULL_C = np.array([152, 152, 116.])                  # RA2 73 (101, 101, 77), lifted to the mod's drawn tone
TUR_C = np.array([212, 212, 174.])                   # RA2 70 (138, 138, 113), likewise
DARK = np.array([70, 70, 74.])                       # RA2 53-56
DARK_D = np.array([46, 46, 50.])
BLACK_C = np.array([30, 30, 32.])                    # RA2 57-62
BELT_C = np.array([42, 42, 44.])
WHEEL_C = np.array([142, 142, 146.])                 # RA2 13, 43-51
HUB_C = np.array([88, 88, 92.])
STEEL = np.array([128, 128, 134.])
AERIAL_C = np.array([36, 36, 38.])
GRIME = np.array([112, 104, 78.])
FILL = 0.32
PPU = 5.03

PAINT = {T.OLIVE: HULL_C, T.BELT: BELT_C, T.WHEEL: WHEEL_C, T.HUB: HUB_C, T.GRILLE: DARK_D, T.BLACK: BLACK_C,
         T.LAMP: BLACK_C * 1.3, T.PLOUGH: np.array([50, 50, 54.]), T.RAM: STEEL, T.TUR: TUR_C, T.HATCH: DARK, T.AERIAL: AERIAL_C,
         T.POD: DARK, T.TUBE: DARK, T.STRAP: DARK * 1.25, T.MOUNT: DARK * 0.85, T.BARREL: DARK * 0.85,
         T.SLEEVE: DARK, T.MUZZLE: DARK * 0.8, T.MANTLET: DARK * 1.15, T.HOOK: STEEL}
GLOSSY = (T.BARREL, T.SLEEVE, T.MUZZLE, T.MANTLET, T.TUBE, T.STRAP, T.HATCH, T.RAM, T.WHEEL, T.AERIAL, T.PLOUGH)


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
    barp = hm & (sec == 'barl')

    for c, col in PAINT.items():
        put((comp == c) & hm, col * g1)
    house = is_(*T.HOUSE)
    put(house, GREEN * (1 + 1.1 * grain)[..., None])
    seam = np.zeros(sh, bool)
    up = np.zeros(sh, np.float32)

    # ------------------------------------------------------------------ the hull
    ol = is_(T.OLIVE) & hullp
    if ol.any():
        body = ol & (y > 7.0) & (y < 25.0)
        deck = body & top & (z > 11.8)
        # the deck in plates: joints across it (ahead of the grilles, mid-deck), round the engine bay; a hatch with
        # hinges ahead of the turret ring's front (none of it on the house colour)
        seam |= deck & ((np.abs(x - 18.2) < 0.07) | (np.abs(x - 41.6) < 0.07))
        seam |= deck & rect_seam(x, y, 7.6, 18.2, 8.2, 23.8, 0.07)
        # the glacis' joint with the deck, a joint across the glacis below the hatches; bolts along the glacis' foot
        gl = body & (nu > 0.25) & (nw > 0.25)
        seam |= body & (np.abs(x - 45.1) < 0.08) & (z > 11.4)
        seam |= gl & (np.abs(x - 51.2) < 0.07)
        up += gl * bolts(y, x, [(yb, 51.9) for yb in np.arange(8.2, 24.0, 1.6)], 0.16)
        # the hull's sides above the belly: a joint along them; the rear face's plate joint round the grille
        seam |= body & side & (np.abs(z - 7.0) < 0.07)
        seam |= body & back & rect_seam(y, z, 8.6, 23.4, 6.6, 11.2, 0.07)
        up += (body & back) * bolts(y, z, [(yb, 11.55) for yb in np.arange(8.0, 24.5, 2.0)], 0.15)
        # the fenders in plates (joints across), bolts along their outer edge
        fen = ol & ((y < 8.3) | (y > 23.7))
        seam |= fen & top & (phase(x, 9.0, 3.0) < 0.07) & (x > 4.0) & (x < 45.0)
        edge = np.where(y < HYC_, y, 2 * HYC_ - y)
        up += (fen & top & (edge < 3.7)) * bolts(x, edge, [(xb, 3.05) for xb in np.arange(4.5, 30.0, 1.5)], 0.14)
        up += (fen & top & (edge > 2.0) & (x > 30.0)) * bolts(x, edge, [(xb, 2.55) for xb in np.arange(31.0, 45.5, 1.5)],
                                                              0.14)
    gr = is_(T.GRILLE) & hullp
    if gr.any():
        # louvres: the deck grilles' slats across the hull, the rear grille's along it (dark, between lighter slats)
        dg = gr & top
        slat = phase(x, 0.8, 9.0) < 0.2
        put(dg & slat, DARK * 1.05 * g1); up += 0.5 * (dg & slat)
        seam |= dg & rect_seam(x, y, 9.15, 16.85, 9.15, 14.85, 0.08) | dg & rect_seam(x, y, 9.15, 16.85, 17.15, 22.85, 0.08)
        rg = gr & ~top
        slat = phase(z, 0.75, 7.4) < 0.18
        put(rg & slat, DARK * 1.0 * g1); up += 0.5 * (rg & slat)
    bl = is_(T.BELT) & hullp
    if bl.any():
        # the belts' grousers (across the bottom run and over the ends)
        run = bl & ~side
        gro = phase(x + 0.6 * z, 0.75) < 0.16
        put(run & gro, BELT_C * 1.9 * g1)
        up += 0.4 * (run & gro)
        put(bl & side & (phase(x, 0.75) < 0.12) & (z < 1.7), BELT_C * 1.6 * g1)
    wh = is_(T.WHEEL)
    if wh.any():
        # the road wheels: a rim round each (a joint), bolts round the hub
        for xc in T.WHEELS_REAR + T.WHEELS_FRONT:
            d = np.hypot(x - xc, z - T.WZ)
            seam |= wh & side & (np.abs(d - 1.12) < 0.06) & (np.abs(x - xc) < 1.7)
    pl = is_(T.PLOUGH)
    if pl.any():
        # v2.1: dark gunmetal (Westwood's black blade), its upper faces worn a little lighter; the edges catch the light
        put(pl & (nw > 0.5), np.array([72, 72, 77.]) * g1)
    hh = is_(T.HATCH) & hullp
    if hh.any():
        # the glacis hatches: a ring joint round their lids, a hinge
        seam |= hh & (nu > 0.2)

    # ------------------------------------------------------------------ the turret
    tu = is_(T.TUR) & turp
    if tu.any():
        tt = tu & top
        yc = T.TYC
        # the top in plates: a joint across behind the hatch and in front of it, bolts along the top's edge
        seam |= tt & ((np.abs(x - 7.6) < 0.07) | (np.abs(x - 18.6) < 0.07))
        up += tt * bolts(x, y, [(xb, yc + s * 6.25) for xb in np.arange(3.5, 20.0, 1.8) for s in (-1, 1)], 0.15)
        # the front: a joint along the top's front edge
        seam |= tu & (nu > 0.4) & (nw < 0.6) & (np.abs(z - 6.0) < 0.07)
    ht = is_(T.HATCH) & turp
    if ht.any():
        # the round hatch: notches round its ring (Westwood's), a joint round its lid
        dx_, dy_ = x - 13.0, y - T.TYC
        rr = np.hypot(dx_, dy_); th = np.arctan2(dy_, dx_)
        ring = ht & top & (rr > 2.15) & (rr < 2.95)
        put(ring & (phase(th, 2 * np.pi / 12) < 0.11), DARK_D * 0.8 * g1)
        seam |= ht & top & (np.abs(rr - 1.55) < 0.07) & (z > 8.0)
    tb = is_(T.TUBE)
    if tb.any():
        # the tubes' mouths (their front ends, up the pods' axis): black inside a thin rim
        u, v = T.pod_axis()
        ue = np.abs(nu * u[0] + nw * u[2]) > 0.8
        put(tb & ue & ((nu * u[0] + nw * u[2]) > 0), BLACK_C * 0.5)
        mouth = tb & ue & ((nu * u[0] + nw * u[2]) > 0)
        # the rim: keep a lighter ring round the black
        for a in (-1, 1):
            for b in (-1, 1):
                for yc in T.POD_Y:
                    o = np.array([T.POD_C[0], yc, T.POD_C[1]]) + a * T.TUBE_D * v + np.array([0.0, b * T.TUBE_D, 0.0])
                    d = np.sqrt((x - o[0]) ** 2 + (y - o[1]) ** 2 + (z - o[2]) ** 2 -
                                ((x - o[0]) * u[0] + (z - o[2]) * u[2]) ** 2)
                    put(mouth & (d > T.TUBE_R - 0.22) & (d < T.TUBE_R + 0.05), DARK * 1.1 * g1)
    st = is_(T.STRAP)
    if st.any():
        up += 0.3 * st
    br = is_(T.BARREL, T.SLEEVE, T.MUZZLE) & barp
    if br.any():
        # the bore (each barrel's muzzle end), the muzzle brake's slots (both sides), a joint round the root's collar
        endf = np.abs(nu) > 0.85
        for yc in T.BAR_Y:
            d = np.hypot(y - yc, z - T.BAR_Z)
            put(br & endf & (nu > 0) & (d < 0.95) & (np.abs(y - yc) < 2), BLACK_C * 0.45)
            mz = is_(T.MUZZLE) & ~endf & (np.abs(y - yc) < 2.2)
            slot = mz & (np.abs(z - T.BAR_Z) < 0.55) & ((phase(x, 0.85, 24.85) < 0.24) & (x > 24.5) & (x < 26.6))
            put(slot, BLACK_C * 0.5); bz -= 0.4 * slot
        seam |= br & ~endf & ((np.abs(x - 9.0) < 0.05) | (np.abs(x - 24.2) < 0.05))
    mt = is_(T.MANTLET) & barp
    if mt.any():
        seam |= mt & ~(np.abs(nu) > 0.85) & (np.abs(x - 3.5) < 0.06)

    house_seam = seam & house
    other = seam & ~house & hm
    put(house_seam, GREEN * (1 + 1.1 * grain)[..., None])          # the house colour stays plain (Luke)
    alb[other] *= 0.62
    bz -= 0.35 * (seam & ~house)
    bz += 0.5 * up * hm * ~house

    # ------------------------------------------------------------------ grime from the ground (the hull), the fill light
    low = hullp & ~house
    dust = smoothstep(4.5, 0.5, r.z) * 0.45
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


HYC_ = T.HYC


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, T.HOUSE)
