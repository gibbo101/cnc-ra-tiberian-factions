"""
obmat.py - the Orca Bomber's materials, per pixel of an rcrender.RCRender whose frames give each hit's q coordinates
in the section (r.lu, r.lv, r.lw = q x, y, z).  Faces are told apart by their geometric normals (r.gn*, before the edges
are rounded).

TS's colours (UNITTEM.PAL, lifted as the other HD units' are): GDI's ochre body, booms and keel (TS 144-147, the
Dropship's ochre), TS's browns on the fans' rims and the tail fan's housing (TS 153-161), light grey fan blades (TS
41-50) on dark hubs, the fans' black throats and TS's black bays in the front faces (TS 57-62), the glazed nose in TS's
blue (TS 197) as dark blue glass, TS's red lamp behind it (TS 6) as a beacon, red glass glowing a little; house colour (pure green 0,214,0 x
(1 + 1.1 grain)) where TS paints house colour: the fins and the panels on the body's top.  Panel joints, vents and the
booms' segment joints where TS's voxels have the parts.
"""
import numpy as np
import walls2 as W
import obmodel as T

GREEN = np.array([0, 214, 0.])
OCHRE = np.array([214, 166, 72.])                   # TS 144-147 (190, 145, 60), as the Dropship's
OCHRE_D = np.array([186, 145, 66.])                 # TS 148-152
BROWN = np.array([150, 116, 60.])                   # TS 153-157 (the fans' rims)
BROWN_D = np.array([118, 94, 54.])                  # TS 158-161
OLIVE = np.array([74, 72, 40.])                     # TS 76-78
GREY_L = np.array([178, 178, 182.])                 # TS 41-46 (the blades)
GREY_D = np.array([84, 84, 88.])                    # TS 53-56
HUB_C = np.array([66, 66, 70.])
DARK_C = np.array([34, 34, 36.])                    # TS 57-62
BLACK_C = np.array([20, 20, 22.])
BOMB_C = np.array([112, 108, 68.])                  # the bombs in the bays: olive drab
GLASS_LO = np.array([34, 38, 86.])                  # the glazed nose: TS's blue (64, 64, 133) as blue glass, the sky's
GLASS_HI = np.array([108, 122, 188.])               # reflection lighter towards its top
LAMP_C = np.array([200, 30, 24.])                   # TS 6 (255, 85, 85): the beacon's red glass
LAMP_HOT = np.array([255, 150, 120.])               # its lit top
FILL = 0.32

PAINT = {T.RIM: BROWN, T.THROAT: DARK_C, T.BLADE: GREY_L, T.HUB: HUB_C, T.BODY: OCHRE, T.SPINE: OCHRE,
         T.PANEL: GREEN, T.BLOCK: OCHRE_D, T.BAY: BLACK_C, T.BOMB: BOMB_C, T.KEEL: OCHRE, T.CANOPY: GLASS_LO,
         T.LAMP: LAMP_C, T.BOOM: OCHRE, T.COLLAR: BROWN_D, T.STAB: OCHRE, T.HOUSING: BROWN, T.FIN: GREEN,
         T.FLOOR: DARK_C, T.RACK: DARK_C * 1.15}
GLOSSY = (T.HUB, T.LAMP, T.BOMB)
EMIT = {T.LAMP: 0.5}


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


def local_normals(r, geometric=True):
    if geometric and hasattr(r, 'gnx'):
        N = np.stack([r.gnx, r.gny, r.gnz], -1)
    else:
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
    top = nw > 0.6
    side = (np.abs(nw) < 0.5) & (np.abs(nv) > 0.6)
    front = (np.abs(nw) < 0.6) & (nu > 0.6)
    back = (np.abs(nw) < 0.6) & (nu < -0.6)
    out_ = np.sign(y - T.HYC) * nv > 0.6
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])
    is_ = lambda *cs: np.isin(comp, cs) & hm

    for c, col in PAINT.items():
        put((comp == c) & hm, col * g1)
    house_c = (GREEN * (1 + 1.1 * grain)[..., None]).astype(np.float32)
    for c in T.HOUSE:
        np.copyto(alb, house_c, where=((comp == c) & hm)[..., None])
    seam = np.zeros(sh, bool)
    dark = np.zeros(sh, bool)
    up = np.zeros(sh, np.float32)
    glass = np.zeros(sh, bool)
    frame_px = np.zeros(sh, bool)

    # ------------------------------------------------------------------ the fans
    rm = is_(T.RIM)
    if rm.any():
        cy = np.where(y > T.HYC, T.FAN_C[1][1], T.FAN_C[0][1])
        rr = np.hypot(x - T.FAN_C[0][0], y - cy)
        inner = rm & (rr < T.FAN_RI + 0.12) & ~top
        put(inner, BROWN_D * g1)                                      # the duct's wall, in its shade
        seam |= rm & top & (np.abs(rr - (T.FAN_RO - 0.5)) < 0.06)
        # joints round the rim, and TS's olive band low on it
        th = np.arctan2(y - cy, x - T.FAN_C[0][0])
        seam |= rm & ~top & (rr > T.FAN_RO - 0.1) & (phase(th, np.pi / 6) < 0.012 * 6)
        seam |= rm & ~top & (rr > T.FAN_RO - 0.1) & (np.abs(z - 7.0) < 0.06)
    hb = is_(T.HUB)
    if hb.any():
        put(hb & top, GREY_D * g1)
    # ------------------------------------------------------------------ the body
    bd = is_(T.BODY)
    if bd.any():
        # joints across the top and down the sides, the front blocks' top seams, a hatch on each side of the back
        seam |= bd & top & ((np.abs(x - 22.4) < 0.07) | (np.abs(x - 28.0) < 0.07))
        seam |= bd & top & (np.abs(w - 1.95) < 0.06) & (x > 32.5)
        seam |= bd & side & ((np.abs(x - 24.0) < 0.07) | (np.abs(x - 30.0) < 0.07))
        seam |= bd & side & (np.abs(z - 5.5) < 0.06) & (x > 20.5)
        # louvres on the back (the fans' and the engines' outlets: TS's darker back)
        bk = bd & (nu < -0.3) & (w < 7.5)
        lv = bk & (z > 4.3) & (z < 8.6)
        seam |= lv & (phase(z, 0.55, 4.6) < 0.06)
        up += 0.45 * (lv & (phase(z, 0.55, 4.88) < 0.16))
        # the front faces: a frame round each pair of bays
        fr = bd & front
        for (w0, w1) in T.BAY_W:
            ya, yb = sorted((T.Y(w0), T.Y(w1)))
            seam |= fr & rect_seam(y, z, ya - 0.3, yb + 0.3, T.BAY_Z[0][0] - 0.3, T.BAY_Z[1][1] + 0.3, 0.06)
    pn = is_(T.PANEL)
    if pn.any():
        seam |= pn & top & (np.abs(x - 27.6) < 0.07)
    sp = is_(T.SPINE)
    if sp.any():
        seam |= sp & top & (phase(x, 3.2, 27.0) < 0.06) & (x > 25.8)
        up += 0.5 * (sp & top) * bolts(x, y, [(26.4, T.Y(-1.1)), (26.4, T.Y(1.1)), (33.2, T.Y(-1.1)),
                                               (33.2, T.Y(1.1))], 0.15)
    bl = is_(T.BLOCK)
    if bl.any():
        # vents (TS's raised blocks by the booms)
        tp = bl & top
        seam |= tp & (phase(x, 0.5, 26.2) < 0.06) & (x > 26.1) & (x < 27.9)
    rk = is_(T.RACK)
    if rk.any():
        # TS's black blocks at the fans' inner front corners: racks, framed, slotted across their fronts
        f = rk & front
        seam |= f & (phase(z, 0.9, 4.7) < 0.08) & (z > 4.3) & (z < 7.7)
        up += 0.4 * (f & (phase(z, 0.9, 5.15) < 0.25) & (z > 4.3) & (z < 7.7))
        seam |= rk & (np.abs(nu) < 0.5) & (np.abs(x - 33.2) < 0.07)
    bb = is_(T.BOMB)
    if bb.any():
        # a band round each bomb behind its nose
        seam |= bb & (np.abs(x - 35.1) < 0.05)
    # ------------------------------------------------------------------ the nose
    kl = is_(T.KEEL)
    if kl.any():
        sd = kl & side
        seam |= sd & ((np.abs(x - 33.2) < 0.07) | (np.abs(x - 39.6) < 0.07))
        seam |= sd & (np.abs(z - 2.0) < 0.06) & (x > 30.0) & (x < 42.6)
        # an access panel on each side under the canopy
        seam |= sd & rect_seam(x, z, 34.4, 38.6, 2.6, 5.4, 0.06)
        up += 0.5 * sd * bolts(x, z, [(34.8, 3.0), (38.2, 3.0), (34.8, 5.0), (38.2, 5.0)], 0.14)
    cp = is_(T.CANOPY)
    glass |= cp
    if cp.any():
        # the faceted canopy's frames: the ridge, a bow at the top's front edge, the sill
        frame_px |= cp & (w < 0.1) & (nw > 0.3)
        frame_px |= cp & (np.abs(x - 39.6) < 0.09)
        frame_px |= cp & (np.abs(x - 37.6) < 0.08) & (nw > 0.6)
    lp = is_(T.LAMP)
    if lp.any():
        # the beacon: deep red glass, lit from within towards its top (TS's bright red)
        t = np.clip((z - 11.18) / 0.78, 0, 1)
        tt = (t ** 1.5)[..., None]
        put(lp, LAMP_C * (1 - tt) + LAMP_HOT * tt)
    # ------------------------------------------------------------------ the booms and the tail
    bm = is_(T.BOOM)
    if bm.any():
        # segment joints along the booms (the renders' segmented booms)
        seam |= bm & (phase(x, 3.6, 4.4) < 0.06) & (x > 1.5) & (x < 19.5)
    hs = is_(T.HOUSING)
    if hs.any():
        rr = np.hypot(x - T.TAIL_C[0], y - T.TAIL_C[1])
        put(hs & (rr < T.TAIL_RI + 0.15), OLIVE * g1)
        seam |= hs & top & (np.abs(rr - (T.TAIL_RO - 0.55)) < 0.06)
    st = is_(T.STAB)
    if st.any():
        seam |= st & top & (np.abs(x - 3.6) < 0.07)
    fi = is_(T.FIN)
    if fi.any():
        seam |= fi & (np.abs(nv) > 0.5) & (np.abs(x - (1.7 + 0.05 * (z - 6))) < 0.07) & (z > 10.4)

    if getattr(r, 'no_fine', False):
        # the 3D model's vertex colours: the paint's areas only (its joints, slots and bolts are finer than the mesh)
        seam[:] = False; dark[:] = False; up[:] = 0; frame_px[:] = False
    house = r.hitmask & np.isin(comp, T.HOUSE) & (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2]))
    put(seam & house & ~glass, GREEN * 0.62 * (1 + 1.1 * grain)[..., None])
    alb[seam & ~house & hm & ~glass] *= 0.62
    put(dark & hm & ~glass, BLACK_C * g1)
    if glass.any():
        # dark blue glass, the sky's reflection lighter towards the top; the frames dark grey metal
        gt = 0.72 * np.clip((z - 4.4) / 5.6, 0, 1)
        gcol = GLASS_LO[None, :] * (1 - gt[glass][:, None]) + GLASS_HI[None, :] * gt[glass][:, None]
        gcol = gcol * (1 + 0.25 * np.clip(r.nz[glass], 0, 1))[:, None]
        alb[glass] = gcol
        put(frame_px & glass, GREY_D * 1.25 * g1)
        L = r.L; V_ = -r.cam.D
        Hh = (L + V_) / np.linalg.norm(L + V_)
        nh = np.clip(r.nx * Hh[0] + r.ny * Hh[1] + r.nz * Hh[2], 0, 1)
        emit[glass] += (0.45 * nh[glass] ** 40 * 255.0)[:, None] * np.array([0.95, 0.97, 1.0])
    r.glass_px = glass
    for c, k in EMIT.items():
        m = is_(c)
        emit[m] += alb[m] * k
    bz = -0.35 * seam - 0.25 * dark + 0.5 * up * hm
    cam = r.cam
    tc = np.array([cam.T[0] * cam.cE, cam.T[1] * cam.cE, cam.sE]); tc = tc / np.linalg.norm(tc)
    nf = np.clip(r.nx * tc[0] + r.ny * tc[1] + r.nz * tc[2], 0, 1) * (1 - np.clip(r.nz, 0, 1))
    if occ is not None:
        nf = nf * (1 - 0.85 * np.clip(occ, 0, 1))
    emit = emit + alb * (FILL * nf)[..., None]
    alb[~hm] = 0
    r.house_px = house_mask(r, alb)
    return alb, (np.zeros(sh, np.float32), np.zeros(sh, np.float32), bz.astype(np.float32)), emit


def house_mask(r, alb):
    """the house-colour pixels: green on the house parts (their seams too)."""
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, T.HOUSE)


def trim_mask(r, alb):
    return house_mask(r, alb)
