"""
prismat.py - the Prism Tank's materials, per pixel of an rcrender.RCRender whose frames give each hit's q coordinates in
its own section (r.lu, r.lv, r.lw = q x, y, z; r.sec names the section: hull or tur).

RA2's colours (UNITTEM.PAL), lifted so the lit model comes out as light as the mod's frames draw them: the hull's light
blue-grey (RA2 88) on its body and rear deck, the darker blue-greys (RA2 90-94) on the fenders, the armour plates, the
front deck, the coolers, the ring's steps and the prism's housing, ribs and hubs, the post dark grey (RA2 55), black
belts and mudguards (RA2 57-59), the olive bearing on the ring (RA2 70, 73), the emitter's face white (RA2 15) and lit;
house colour (pure green 0,214,0 x (1 + 1.1 grain)) where RA2's remap voxels are: the sponsons' bands, the ring's drum and
its buttresses, the prism's fan and the emitter's frame, plain (Luke: no grilles, fine detail or black lines on the house
colour).
"""
import os, sys
from paths import HANDOFF
sys.path.insert(0, os.path.join(HANDOFF, 'renderer'))
import numpy as np
import walls2 as W
from walls2 import smoothstep
import prismodel as T

GREEN = np.array([0, 214, 0.])
LIGHT = np.array([150, 150, 184.])                   # RA2 88 (125, 125, 149), lifted to the mod's drawn tone
MID = np.array([104, 104, 134.])                     # RA2 91-92
FRONT_C = np.array([128, 128, 158.])                 # RA2 90-91: the front deck (the mod draws it nearly as light as the rear)
DARK = np.array([70, 70, 98.])                       # RA2 93-94
GREY = np.array([70, 70, 74.])                       # RA2 55
BLACK_C = np.array([32, 32, 38.])
BELT_C = np.array([42, 42, 48.])
WHEEL_C = np.array([104, 104, 116.])
HUB_C = np.array([66, 66, 76.])
OLIVE = np.array([176, 176, 146.])                   # RA2 70
GLOW = np.array([226, 240, 255.])                    # the emitter's face (RA2 15), lit from inside
GLOW_EDGE = np.array([150, 196, 238.])
GRIME = np.array([96, 94, 92.])
FILL = 0.32
PPU = 5.03

PAINT = {T.BELT: BELT_C, T.WHEEL: WHEEL_C, T.HUB: HUB_C, T.GUARD: BLACK_C, T.FENDER: MID, T.ARMOUR: MID, T.BODY: LIGHT,
         T.DECK: LIGHT, T.COOLER: DARK, T.FIN: DARK * 1.18, T.FAN: BLACK_C * 1.2, T.RING: MID * 0.9, T.BEARING: OLIVE,
         T.PERISCOPE: MID * 1.08, T.CUPOLA: MID, T.POST: GREY, T.CRADLE: MID, T.SIDEHUB: DARK * 1.1, T.RIB: DARK,
         T.HOUSING: DARK * 0.8, T.EMITTER: GLOW}
GLOSSY = (T.WHEEL, T.COOLER, T.FIN, T.POST, T.SIDEHUB, T.RIB, T.HOUSING, T.CUPOLA, T.PERISCOPE, T.RING)


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
    HYC = T.HYC

    for c, col in PAINT.items():
        put((comp == c) & hm, col * g1)
    house = is_(*T.HOUSE)
    put(house, GREEN * (1 + 1.1 * grain)[..., None])
    seam = np.zeros(sh, bool)
    up = np.zeros(sh, np.float32)

    # ------------------------------------------------------------------ the hull
    bd = is_(T.BODY) & hullp
    if bd.any():
        # the front deck a little darker (SREF's 90-91 ahead of the ring), a hatch on the glacis between the periscope and the
        # cupola (SREF's grey there), its joint; joints along the sides and across the glacis; bolts along the glacis' foot
        fd = bd & top & (x > 36.5)
        put(fd, FRONT_C * g1)
        gl = bd & (nu > 0.3) & (nw > 0.3)
        put(gl, MID * 0.95 * g1)
        hatch = gl & rect(y, x, 15.2, 17.8, 44.6, 47.4)
        put(hatch, np.array([128, 128, 134.]) * g1)
        seam |= gl & rect_seam(y, x, 15.2, 17.8, 44.6, 47.4, 0.07)
        up += hatch * bolts(y, x, [(16.5, 46.9)], 0.22)
        seam |= bd & side & (np.abs(z - 10.6) < 0.07)
        seam |= bd & side & ((np.abs(x - 21.2) < 0.07) | (np.abs(x - 36.5) < 0.07))
        up += gl * bolts(y, x, [(yb, 48.6) for yb in np.arange(9.0, 24.5, 1.5)], 0.15)
        # the rear face: a joint across, bolts along the top
        seam |= bd & back & (np.abs(z - 11.4) < 0.07)
        up += (bd & back) * bolts(y, z, [(yb, 13.3) for yb in np.arange(9.0, 24.5, 1.5)], 0.15)
    dk = is_(T.DECK) & hullp
    if dk.any():
        # the rear deck in plates round the fan, an access plate between the coolers, bolts along its edges
        dt = dk & top & (np.hypot(x - T.FAN_C[0], y - T.FAN_C[1]) > T.FAN_R + 0.5)
        seam |= dt & ((np.abs(x - 15.0) < 0.07) | (np.abs(y - 11.6) < 0.07) | (np.abs(y - 2 * HYC + 11.6) < 0.07))
        seam |= dt & rect_seam(x, y, 15.6, 20.6, 13.0, 20.0, 0.07)
        up += dt * bolts(x, y, [(xb, yb) for xb in (16.1, 20.1) for yb in (13.5, 19.5)], 0.17)
        rim = dk & top & (np.abs(np.hypot(x - T.FAN_C[0], y - T.FAN_C[1]) - (T.FAN_R + 0.22)) < 0.25)
        put(rim, LIGHT * 0.92 * g1)
    fn = is_(T.FAN)
    if fn.any():
        # the fan: its blades (Westwood's round fan), the guard's rings over them
        dx, dy = x - T.FAN_C[0], y - T.FAN_C[1]
        rr = np.hypot(dx, dy); th = np.arctan2(dy, dx)
        blade = phase(th + 0.25 * rr, 2 * np.pi / 7) < 0.32
        put(fn & blade & (rr > 0.9), DARK * 0.9 * g1)
        ringg = fn & top & (phase(rr, 0.85, 0.4) < 0.1) & (rr > 1.0)
        put(ringg, MID * 0.85 * g1); up += 0.4 * ringg
    fe = is_(T.FENDER, T.ARMOUR) & hullp
    if fe.any():
        # the fenders and the armour plates: joints across, bolts along the armour's edges
        seam |= fe & top & (phase(x, 8.0, 5.0) < 0.07) & (x > 6.0) & (x < 45.0)
        ar = is_(T.ARMOUR) & top
        e = np.where(y < HYC, y, 2 * HYC - y)
        up += ar * bolts(x, e, [(xb, eb) for xb in np.arange(7.0, 26.0, 1.6) for eb in (2.55, 7.45)], 0.15)
    co = is_(T.COOLER, T.FIN)
    if co.any():
        seam |= is_(T.COOLER) & (np.abs(nu) > 0.85) & False
    gu = is_(T.GUARD)
    if gu.any():
        put(gu & top, BLACK_C * 1.4 * g1)
    bl = is_(T.BELT) & hullp
    if bl.any():
        run = bl & ~side
        gro = phase(x + 0.6 * z, 0.8) < 0.17
        put(run & gro, BELT_C * 1.8 * g1); up += 0.4 * (run & gro)
        put(bl & side & (phase(x, 0.8) < 0.13) & (z < 1.5), BELT_C * 1.5 * g1)
    wh = is_(T.WHEEL)
    if wh.any():
        # the road wheels: a rim joint round each, six bolts round the hub
        for xc in T.WHEELS:
            d = np.hypot(x - xc, z - T.WZ); a = np.arctan2(z - T.WZ, x - xc)
            ok = wh & side & (np.abs(x - xc) < T.WR + 0.2)
            seam |= ok & (np.abs(d - 1.9) < 0.07)
            up += ok * (d < 1.35) * (d > 1.05) * (phase(a, np.pi / 3) < 0.25)
    rg = is_(T.RING) & hullp
    if rg.any():
        # the ring's steps: bolts round their tops
        dx, dy = x - T.RING_C[0], y - T.RING_C[1]
        rr = np.hypot(dx, dy); th = np.arctan2(dy, dx)
        for rb in (6.8, 5.7):
            up += (rg & top & (np.abs(rr - rb) < 0.2) & (phase(th, 2 * np.pi / 24) < 0.06)) * 0.8
    br = is_(T.BEARING)
    if br.any():
        dx, dy = x - T.RING_C[0], y - T.RING_C[1]
        rr = np.hypot(dx, dy)
        seam |= br & top & (np.abs(rr - 3.9) < 0.07)
    cu = is_(T.CUPOLA)
    if cu.any():
        # the cupola: vision slots round it (Westwood's), a joint round its lid, a handle
        dx, dy = x - 41.6, y - 20.5
        rr = np.hypot(dx, dy); th = np.arctan2(dy, dx)
        slot = cu & ~top & (z > 15.2) & (z < 15.75) & (phase(th, 2 * np.pi / 8) < 0.22) & (rr > 2.0)
        put(slot, BLACK_C * 0.8); bz -= 0.3 * slot
        seam |= cu & top & (np.abs(rr - 1.25) < 0.06)
    pe = is_(T.PERISCOPE)
    if pe.any():
        gl_ = pe & (x > 42.5) & (nu > 0.5) & (z > 14.0)
        put(gl_, np.array([40, 52, 70.]) * (1 + 0.5 * (z > 14.5))[..., None])

    # ------------------------------------------------------------------ the prism
    rb = is_(T.RIB)
    if rb.any():
        # the ribs' outer faces lighter at their edges (they catch the light; the gaps between them are dark)
        up += 0.25 * rb
    hb = is_(T.SIDEHUB)
    if hb.any():
        d = np.hypot(x - T.HUB_C[0], z - T.HUB_C[1]); a = np.arctan2(z - T.HUB_C[1], x - T.HUB_C[0])
        seam |= hb & (np.abs(d - 2.5) < 0.07)
        up += hb * (np.abs(d - 2.05) < 0.16) * (phase(a, np.pi / 4) < 0.18)
    po = is_(T.POST)
    if po.any():
        seam |= po & ((np.abs(z - 3.0) < 0.06) | (np.abs(z - 6.4) < 0.06))
    cr = is_(T.CRADLE)
    if cr.any():
        seam |= cr & side & (np.abs(z - 10.1) < 0.06)
        up += (cr & top) * bolts(x, y, [(xb, yb) for xb in (6.3, 12.3) for yb in (1.6, 6.4)], 0.2)
    em = is_(T.EMITTER)
    if em.any():
        # the emitter's face: glowing white, bluer towards its edges, three horizontal bars across it (Westwood's
        # lens), lit from inside (no light from it falls on anything)
        x0, x1, y0, y1, z0, z1 = T.EMIT
        e = np.minimum(np.minimum(y - y0, y1 - y), np.minimum(z - z0, z1 - z))
        t = np.clip(e / 0.9, 0, 1)[..., None]
        c = GLOW_EDGE * (1 - t) + GLOW * t
        bar = em & (nu > 0.5) & (phase(z, (z1 - z0) / 4, z0) < 0.09) & (z > z0 + 0.4) & (z < z1 - 0.4)
        put(em, c)
        put(bar, GLOW_EDGE * 0.85)

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


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, T.HOUSE)
