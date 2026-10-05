"""
t4mat.py - the Mammoth Mk. I's materials, per pixel of an rcrender.RCRender whose frames give each hit's q
coordinates in its own section (r.lu, r.lv, r.lw = q x, y, z; r.sec its section: 'hull', 'tur' or 'barl').

TS left the Mk. I in house colour nearly all over (its remap voxels), as EA's HD Mammoths are: pure green 0,214,0 x
(1 + 1.1 grain) on the hull, the track covers and skirts, the turret, the mantlet, the barrels' sleeves and collars,
with detail only as thin seams, bolts and louvres (EA's Mammoths' panel lines).  TS's other colours: dark tracks,
black barrels, tusk pods and antennas, the pods' grey tube fronts with orange missile tips, the orange tail lamps,
the grey headlamps, the white caps on the rear deck, the black rear grille and the black hatch on the turret.  The
tusk pods all black with only their missile tips orange (Luke's call: TS has brown noses round the tips, a grey back
end and a white arm to the turret).
Detail from EA's HD Mammoths and Luke's models of the RA Mammoth (the same tank) where TS has the part: the turret
top's plate line, the hatch plate, the front deck's hex hatch, port, grilles and louvres, the ribs on the mantlet and
the pods, the slots in the covers' fronts.
"""
import numpy as np
import walls2 as W
from walls2 import smoothstep
import t4v2 as T

GREEN = np.array([0, 214, 0.])
DARK = np.array([46, 46, 48.])
STEEL_D = np.array([70, 70, 74.])
STEEL = np.array([118, 118, 124.])
GREY = np.array([142, 142, 148.])
LIGHT = np.array([196, 196, 202.])
CORE_C = np.array([20, 20, 20.])
ORANGE = np.array([238, 128, 34.])            # TS 182-186: the missile tips, the tail lamps
BROWN_R = np.array([141, 93, 76.])            # TS 102-107: the pods' fronts round the missile tips
WHITE = np.array([228, 228, 230.])
LAMP_W = np.array([250, 248, 232.])
GRIME = np.array([112, 104, 78.])
FILL = 0.32

PAINT = {T.BELT: DARK, T.WHEEL: STEEL_D, T.HUB: STEEL, T.CORE: CORE_C, T.RING: STEEL_D, T.GRILLE: np.array([40, 40, 44.]),
         T.TAIL: ORANGE, T.HEAD: LAMP_W, T.VENT: LIGHT, T.CUPOLA: np.array([52, 52, 56.]), T.POD: np.array([52, 52, 56.]),
         T.POD_FRONT: np.array([52, 52, 56.]), T.ARM: np.array([52, 52, 56.]), T.TIP: ORANGE, T.ANTENNA: np.array([36, 36, 38.]), T.ANTBASE: GREY,
         T.BARREL: np.array([62, 62, 66.]), T.MUZZLE: np.array([40, 40, 42.]), T.LAMPHOUSE: STEEL_D, T.HATCH: STEEL_D}
GLOSSY = (T.BARREL, T.MUZZLE, T.POD, T.CUPOLA, T.ANTBASE, T.POD_FRONT, T.VENT, T.HUB)


def grain_of(r, scale=1.0):
    X, Y, Z = r.lu * 6.23 * scale, r.lv * 6.23 * scale, r.lw * 6.23 * scale
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


# the upright slots along the covers' outer sides (q x): two, three and two along each track unit (Luke's models)
SIDE_SLOTS, SIDE_SLOTS_MID = [], []
for _x0, _x1 in ((2.0, 16.0), (20.0, 34.0)):
    for _f, _n in ((0.22, 2), (0.5, 3), (0.78, 2)):
        for _i in range(_n):
            _xs = _x0 + _f * (_x1 - _x0) + (_i - (_n - 1) / 2) * 0.7
            SIDE_SLOTS.append(_xs)
            if _n == 3:
                SIDE_SLOTS_MID.append(_xs)

# the turret top's plate line (q x, y): 0.6 inside the top's edge, round the lobes and the notch between them
INSET = [((3.6, 6.0), (18.44, 6.0)), ((18.44, 6.0), (18.44, 18.0)), ((18.44, 18.0), (3.6, 18.0)),
         ((3.6, 18.0), (3.6, 15.8)), ((3.6, 15.8), (6.2, 15.8)), ((6.2, 15.8), (6.2, 8.2)), ((6.2, 8.2), (3.6, 8.2)),
         ((3.6, 8.2), (3.6, 6.0))]


def seg_dist(x, y, segs):
    d = np.full(x.shape, np.inf, np.float32)
    for (ax_, ay_), (bx_, by_) in segs:
        ux, uy = bx_ - ax_, by_ - ay_
        t = np.clip(((x - ax_) * ux + (y - ay_) * uy) / (ux * ux + uy * uy), 0, 1)
        d = np.minimum(d, np.hypot(x - (ax_ + t * ux), y - (ay_ + t * uy)))
    return d


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
    hull_s, tur_s, barl_s = r.sec == 'hull', r.sec == 'tur', r.sec == 'barl'
    yh = np.where(y > T.HYC, 2 * T.HYC - y, y)              # the hull's halves folded onto its right one
    yt = np.where(y > T.TYC, 2 * T.TYC - y, y)
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])
    is_ = lambda *cs: np.isin(comp, cs) & hm

    for c, col in PAINT.items():
        put((comp == c) & hm, col * g1)
    house = is_(*T.HOUSE)
    put(house, GREEN * (1 + 1.1 * grain)[..., None])
    seam_h = np.zeros(sh, bool)
    up = np.zeros(sh, np.float32)
    seam_o = np.zeros(sh, bool)

    # ------------------------------------------------------------------ the hull (house colour: seams, bolts, louvres)
    cv = is_(T.COVER) & hull_s
    if cv.any():
        t = cv & top
        # Luke's models: a groove along each unit's top near its inner edge, in two lengths; a joint across between the
        # two units (TS's cover runs on over both)
        segs = (((x > 2.6) & (x < 8.6)) | ((x > 9.4) & (x < 15.4)) | ((x > 20.6) & (x < 26.6)) | ((x > 27.4) & (x < 33.4)))
        seam_h |= t & (np.abs(yh - 4.2) < 0.07) & segs
        seam_h |= t & (np.abs(x - 18.0) < 0.07)
        # the outer side (Luke's models): a groove along it near the top, groups of upright slots below (two, three,
        # two along each unit), a small round head under each of the middle three
        s = cv & sidey & (yh < 1.0)
        seam_h |= s & (np.abs(z - 7.15) < 0.07) & (x > 1.0) & (x < 35.4)
        slot = np.zeros(sh, bool)
        for xs in SIDE_SLOTS:
            slot |= s & (np.abs(x - xs) < 0.13) & (z > 4.1) & (z < 6.5)
        seam_h |= slot
        up -= 0.4 * slot
        up += s * bolts(x, z, [(xs, 3.75) for xs in SIDE_SLOTS_MID], 0.17)
        # three slots low in each cover's front and back end (Luke's models)
        fe = cv & sidex & (np.abs(nu) > 0.7) & (z > 3.15) & (z < 4.35)
        slot = fe & ((np.abs(yh - 1.0) < 0.2) | (np.abs(yh - 2.4) < 0.2) | (np.abs(yh - 3.8) < 0.2))
        seam_h |= slot
        up -= 0.4 * slot
    sk = is_(T.SKIRT)
    if sk.any():
        # a row of bolts along the skirts' lower edge (EA's HD Mammoths)
        s = sk & sidey
        up += s * bolts(x, z, [(xx, 2.05) for xx in np.arange(3.0, 34.0, 1.8)], 0.14)
        seam_h |= s & (np.abs(z - 2.75) < 0.06)
    hc = is_(T.HULL_C)
    if hc.any():
        t = hc & top
        # the front deck (Luke's models): grilles along both sides, a rounded panel at the front middle
        gr_ = t & (yh > 5.15) & (yh < 6.75) & (x > 25.4) & (x < 31.0)
        seam_h |= t & rect_seam(x, yh, 25.4, 31.0, 5.15, 6.75)
        rib = gr_ & (phase(yh, 0.4, 5.35) < 0.09)
        seam_h |= rib
        up -= 0.25 * rib
        seam_h |= t & rect_seam(x, y, 30.05, 30.95, 10.6, 13.4)
        # the glacis: louvres across it between the headlamps (Luke's models), a plate joint either side
        g = hc & (nw > 0.3) & (nw < 0.95) & (nu > 0.2)
        lv = g & (yh > 10.35) & (x > 31.6) & (x < 34.9)
        seam_h |= g & rect_seam(x, yh, 31.6, 34.9, 10.35, 13.65) & (x > 31.5)
        seam_h |= lv & (phase(x, 0.55, 31.85) < 0.09)
        up -= 0.2 * (lv & (phase(x, 0.55, 31.85) < 0.09))
        seam_h |= g & (np.abs(yh - 7.4) < 0.06)
        b = hc & sidex & (nu < 0)
        seam_h |= b & (np.abs(z - 3.6) < 0.06)
    dh = is_(T.DHATCH)
    if dh.any():
        # the hex hatch: a handle across it
        handle = dh & top & (np.abs(y - 15.6) < 0.1) & (np.abs(x - 29.8) < 0.5)
        up += 0.7 * handle
    pt = is_(T.PORT)
    if pt.any():
        d = np.hypot(x - 30.0, y - 8.4)
        seam_h |= pt & top & (np.abs(d - 0.55) < 0.07)
        up += 0.3 * (pt & top & (d < 0.48))
    dp = is_(T.DECKPLATE)
    if dp.any():
        # the rear deck (Luke's models): slats along it across its width in a frame, round TS's two caps
        t = dp & top
        seam_h |= t & rect_seam(x, y, 2.25, 12.75, 6.25, 17.75)
        clear = (np.hypot(x - 3.9, y - 9.0) > 1.12) & (np.hypot(x - 3.9, y - 15.0) > 1.12)
        sl = t & (x > 2.25) & (x < 12.75) & (y > 6.4) & (y < 17.6) & (phase(y, 0.9, 6.7) < 0.1) & clear
        seam_h |= sl
        up -= 0.3 * sl
    # ------------------------------------------------------------------ the turret
    tu = is_(T.TURRET) & tur_s
    if tu.any():
        t = tu & top
        # the line round the top plate, inset from its edge, notched at the back between the lobes (Luke's models)
        flat = t & (np.abs(z - 6.0) < 0.1)
        seam_h |= flat & (seg_dist(x, y, INSET) < 0.075)
        # a small panel low on each side in front of the pod, a bolt at the foot of each rear lobe (Luke's models)
        sd = tu & sidey
        seam_h |= sd & rect_seam(x, z, 13.4, 15.8, 1.5, 3.0)
        bk = tu & (nu < -0.5) & (np.abs(nw) < 0.8)
        up += bk * bolts(yt, z, [(6.5, 1.5)], 0.28)
    mt = is_(T.MANTLET)
    if mt.any():
        # ribs across the mantlet's top in front of the turret (Luke's models)
        rib = mt & top & (x > 21.4) & (x < 23.75) & (phase(x, 0.55, 21.8) < 0.09)
        seam_h |= rib
        up -= 0.25 * rib
    cu = is_(T.CUPOLA)
    if cu.any():
        # TS's dark plate as Luke's models' hatch plate: the round hatch (its own part) right of its middle with a tab
        # to the back, two small plates side by side down its left edge
        t = cu & top
        plates = t & (((x > 15.6) & (x < 16.95) & (y > 12.85) & (y < 13.75)) |
                      ((x > 17.25) & (x < 18.6) & (y > 12.85) & (y < 13.75)))
        alb[plates] *= 1.25
        up += 0.4 * plates
        seam_o |= t & (rect_seam(x, y, 15.6, 16.95, 12.85, 13.75, 0.06) | rect_seam(x, y, 17.25, 18.6, 12.85, 13.75, 0.06))
        tab = t & (x > 15.75) & (x < 16.3) & (np.abs(y - 11.55) < 0.17)
        alb[tab] *= 1.35
        up += 0.6 * tab
    ht = is_(T.HATCH)
    if ht.any():
        d = np.hypot(x - 17.2, y - 11.55)
        seam_o |= ht & top & (np.abs(d - 0.66) < 0.07)
        alb[ht & top & (d < 0.6)] *= 1.15
    po = is_(T.POD)
    if po.any():
        # ribbed tops (Luke's models); the launchers all black, only the missile tips orange (Luke)
        seam_o |= po & top & (phase(yt, 0.42) < 0.08)
    tip = is_(T.TIP)
    if tip.any():
        emit += (tip * 0.15)[..., None] * alb
    # ------------------------------------------------------------------ the barrels
    rside = (nv < -0.7) & (np.abs(nw) < 0.35)            # each sleeve's and collar's right side (TS's light band)
    sl_ = is_(T.SLEEVE)
    if sl_.any():
        band = sl_ & rside & (z > 1.0) & (z < 1.9) & (x > 2.8) & (x < 8.8)
        put(band, LIGHT * g1)
    co = is_(T.COLLAR)
    if co.any():
        band = co & rside & (z > 1.0) & (z < 1.9)
        put(band, LIGHT * g1)
    mz = is_(T.MUZZLE)
    if mz.any():
        # the bore at its end
        bore = mz & (nu > 0.7)
        yb = np.where(y < 5.0, 1.5, 8.5)
        d = np.hypot(y - yb, z - 2.0)
        put(bore & (d < 0.75), CORE_C)
    # ------------------------------------------------------------------ the tracks
    belt = is_(T.BELT)
    if belt.any():
        run = belt & ~sidey
        lk = run & (phase(x + 0.6 * z, 0.62) < 0.1)
        alb[lk] *= 0.55; bz -= 0.4 * lk
        sd = belt & sidey
        alb[sd & (phase(x, 0.62) < 0.07)] *= 0.7
    gr = is_(T.GRILLE)
    if gr.any():
        sl2 = gr & sidex & (phase(z, 0.45, 4.0) < 0.1)
        put(sl2, STEEL_D * 1.3 * g1)
    lmp = is_(T.TAIL, T.HEAD)
    if lmp.any():
        lens = lmp & (np.abs(nu) > 0.5)
        emit += (lens * 0.55)[..., None] * alb
    vt = is_(T.VENT)
    if vt.any():
        put(vt & top, LIGHT * 0.9 * g1)
        d = np.hypot(x - 3.9, np.where(y < 12, y - 9.0, y - 15.0))
        put(vt & top & (d < 0.45), STEEL_D * g1)
    put(seam_h & house, GREEN * 0.62 * (1 + 1.1 * grain)[..., None])
    bz -= 0.35 * (seam_h & house)
    bz += 0.5 * up * house
    put(seam_o & ~house & hm, alb * 0.62)
    bz -= 0.3 * (seam_o & ~house & hm)

    # ------------------------------------------------------------------ grime from the ground, the fill light
    low = hm & ~house & ~is_(T.TAIL, T.HEAD, T.TIP)
    dust = smoothstep(3.5, 0.5, r.z) * 0.45
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
