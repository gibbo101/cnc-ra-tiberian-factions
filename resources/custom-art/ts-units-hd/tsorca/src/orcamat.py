"""
orcamat.py - the Orca Fighter's materials, per pixel of an rcrender.RCRender whose frames give each hit's q coordinates
in the section (r.lu, r.lv, r.lw = q x, y, z).  Faces are told apart by their geometric normals (r.gn*, before the edges
are rounded).

TS's colours (UNITTEM.PAL, lifted as the other HD units' are): GDI's ochre hull (TS 149, the Mobile EMP Cannon's
ochre), TS's browns on the nose's tip (TS 154-161), the spine's grey hatch (TS 51), black cheeks on the nose (TS 61-62),
the tail duct's dark walls (TS 77-79, 160); house colour (pure green 0,214,0 x (1 + 1.1 grain)) where TS paints house
colour: the fins, the fans' rings, the panels on the pods' tops - not the nose's sides (v3, Luke), which TS paints
house colour too: GDI's ochre there.  The FMV's dark glass on the canopy; the FMV's red rocket noses in the tubes (v4, Luke); the fans' blades grey on a dark floor (TS: a dark hub and grey cross in each ring).  Panel joints, hatches,
vents and bolts where TS's voxels have the parts.
"""
import os
import numpy as np
import walls2 as W
import orcamodel as T

GREEN = np.array([0, 214, 0.])
OCHRE = np.array([210, 165, 78.])                   # TS 149 (133, 109, 56), as the Mobile EMP Cannon's hull
BROWN = np.array([150, 116, 60.])                   # TS 154-157
BROWN_D = np.array([112, 92, 56.])                  # TS 158-161
OLIVE = np.array([74, 72, 40.])                     # TS 77-79
GREY = np.array([132, 132, 136.])                   # TS 51 (the spine's hatch)
GREY_D = np.array([84, 84, 88.])                    # TS 13, 56
BLADE_C = np.array([150, 150, 156.])                # the fans' blades (TS's grey cross, TS 13)
HUB_C = np.array([72, 72, 76.])
DARK_C = np.array([40, 40, 42.])                    # TS 58-62
BLACK_C = np.array([22, 22, 24.])
GLASS_LO = np.array([26, 32, 40.])                  # the canopy: dark glass, the sky's reflection lighter towards its top
GLASS_HI = np.array([92, 108, 128.])                # (the Dropship's, the MCV's, the Hover MLRS's)
ROCKET_C = np.array([196, 46, 34.])                 # the rockets' noses (the FMV's red tips; v4, Luke)
FILL = 0.32

PAINT = {T.POD: OCHRE, T.COVER: GREEN, T.TUBE: OCHRE, T.BODY: OCHRE, T.DECK: OCHRE, T.HUMP: OCHRE, T.HATCH: GREY,
         T.KEEL: OCHRE, T.NOSE: OCHRE, T.TIP: OCHRE, T.CHIN: OCHRE, T.CANOPY: GLASS_LO, T.BULKHEAD: OCHRE,
         T.FAN: GREEN, T.HUB: HUB_C, T.BLADE: BLADE_C, T.FLOOR: DARK_C, T.BOOM: OCHRE, T.STAB: OCHRE,
         T.HOUSING: OCHRE, T.FIN: GREEN, T.CONE: OCHRE, T.ROCKET: ROCKET_C}
GLOSSY = (T.HUB, T.HATCH)
MOUTH = os.environ.get('ORCA_MOUTH', '0') == '1'    # the FMV's shark mouth on the nose (not in TS's voxel)
ROCKETS = os.environ.get('ORCA_ROCKETS', '1') == '1'  # the FMV's red rocket noses in the tubes (v4, Luke: "Add the
#                                                       red tips"; TS's tubes are black)
TOOTH_C = np.array([238, 234, 224.])
GUM_C = np.array([150, 24, 26.])
EYE_C = np.array([236, 232, 220.])


def shark_mouth(x, z):
    """the FMV's shark mouth on the nose's side (x, z: q on a side face): (teeth, gums, lips, eye white, pupil).
    It opens from its corner under the cockpit (x 33) to the snout (x 40.9), widest at the front."""
    t = np.clip((x - 33.0) / 7.9, 0, 1)
    on = (x > 33.0) & (x < 41.1)
    h = 0.85 * t ** 0.6
    zc = 2.75 - 0.25 * t
    zu, zl = zc + h, zc - h
    inside = on & (z < zu) & (z > zl)
    L = 0.8 * h
    p = 0.62
    tri_u = 1 - np.abs(2 * np.mod((x - 33.0) / p, 1.0) - 1)
    tri_l = 1 - np.abs(2 * np.mod((x - 33.0) / p + 0.5, 1.0) - 1)
    teeth = inside & ((z > zu - L * tri_u) | (z < zl + L * tri_l))
    lips = on & ((np.abs(z - zu) < 0.08) | (np.abs(z - zl) < 0.08)) & (t > 0.02)
    gums = inside & ~teeth
    e = ((x - 34.35) / 0.46) ** 2 + ((z - 4.2) / 0.3) ** 2
    eye = e < 1.0
    pupil = (x - 34.5) ** 2 + (z - 4.18) ** 2 < 0.17 ** 2
    eye_rim = (e >= 1.0) & (e < 1.45)
    return teeth, gums, lips | eye_rim, eye & ~pupil, pupil


def grain_of(r, scale=1.0):
    X, Y, Z = r.lu * 6.25 * scale, r.lv * 6.25 * scale, r.lw * 6.25 * scale
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
    bot = nw < -0.5
    side = (np.abs(nw) < 0.5) & (np.abs(nv) > 0.6)
    front = (np.abs(nw) < 0.6) & (nu > 0.6)
    back = (np.abs(nw) < 0.6) & (nu < -0.6)
    out_ = np.sign(y - T.HYC) * nv > 0.6                # facing away from the centre line
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])
    is_ = lambda *cs: np.isin(comp, cs) & hm

    for c, col in PAINT.items():
        put((comp == c) & hm, col * g1)
    house_c = (GREEN * (1 + 1.1 * grain)[..., None]).astype(np.float32)
    for c in (T.COVER, T.FAN, T.FIN):
        np.copyto(alb, house_c, where=((comp == c) & hm)[..., None])
    seam = np.zeros(sh, bool)
    dark = np.zeros(sh, bool)
    up = np.zeros(sh, np.float32)
    glass = np.zeros(sh, bool)
    frame_px = np.zeros(sh, bool)                      # the canopy's frames
    cheek = np.zeros(sh, bool)
    slat = np.zeros(sh, bool)

    # ------------------------------------------------------------------ the pods
    pd = is_(T.POD)
    if pd.any():
        sd = pd & side & out_
        # joints round the pod (TS's plain box: a band at mid height, two joints across), an access hatch on the outer
        # side with its bolts
        seam |= pd & (np.abs(nu) < 0.5) & (np.abs(x - 25.6) < 0.07) & (z < 7.9)
        seam |= pd & (np.abs(nu) < 0.5) & (np.abs(x - 31.2) < 0.07) & (z < 7.9)
        seam |= sd & (np.abs(z - 4.6) < 0.06) & (x > 23.4) & (x < 32.6)
        seam |= sd & rect_seam(x, z, 26.6, 30.2, 5.15, 7.3, 0.06)
        up += 0.5 * sd * bolts(x, z, [(27.0, 5.55), (29.8, 5.55), (27.0, 6.9), (29.8, 6.9)], 0.15)
        # louvres low on the outer side behind the hatch (vents for the rockets' bay)
        lv = sd & rect(x, z, 26.6, 30.2, 2.7, 4.1)
        seam |= lv & (phase(x, 0.6, 26.9) < 0.07)
        up += 0.45 * (lv & (phase(x, 0.6, 27.2) < 0.18))
        # the back: a joint round its face
        seam |= pd & back & rect_seam(np.where(y > T.HYC, y - 15.0, 10.0 - y), z, 0.9, 9.0, 3.0, 5.6, 0.06)
    cv = is_(T.COVER)
    if cv.any():
        # the house-colour panel: one joint across it, the lip's edge
        seam |= cv & top & (np.abs(x - 28.6) < 0.07)
    tb = is_(T.TUBE)
    if tb.any():
        # the rocket tubes' mouths: an ochre rim round a black bore, darker to its middle (TS's black squares)
        yy = np.where(y > T.HYC, y, y)
        best = np.full(sh, 9.0, np.float32)
        for yt in T.TUBE_Y:
            for yc in (yt, 2 * T.HYC - yt):
                for zt in T.TUBE_Z:
                    best = np.minimum(best, np.hypot(y - yc, z - zt))
        mouth = tb & (nu > 0.6)
        bore = mouth & (best < T.BORE_R)
        put(mouth & ~bore, OCHRE * 0.86 * g1)                      # the rims, a shade darker than the face
        seam |= mouth & (np.abs(best - (T.TUBE_R - 0.05)) < 0.05)
        t = np.clip(best / T.BORE_R, 0, 1)
        put(bore, ((0.65 + 0.5 * t)[..., None] * BLACK_C) * g1)
        # the tube's lower inner wall, seen from above as a crescent at the bore's foot
        dz = np.full(sh, 9.0, np.float32)
        for zt in T.TUBE_Z:
            dz = np.where(np.abs(z - zt) < np.abs(dz), z - zt, dz)
        cres = bore & (dz < -0.3) & (best > 0.42)
        put(cres, OLIVE * 0.9 * g1)
        if ROCKETS:
            # a rocket in each tube, its red nose cone seen head-on: lit from the top left, a dark ring round it
            nose = bore & (best < 0.5)
            dy_ = np.full(sh, 9.0, np.float32)
            for yt in T.TUBE_Y:
                for yc in (yt, 2 * T.HYC - yt):
                    dy_ = np.where(np.abs(y - yc) < np.abs(dy_), y - yc, dy_)
            lit = np.clip(0.72 + 0.42 * dz / 0.5 - 0.12 * np.abs(dy_) / 0.5, 0.42, 1.2)
            put(nose, ROCKET_C * lit[..., None] * g1)
            hl = nose & ((dy_ + 0.12) ** 2 + (dz - 0.2) ** 2 < 0.13 ** 2)
            put(hl, ROCKET_C * 1.45 * g1)
    # ------------------------------------------------------------------ the body
    dk = is_(T.DECK)
    if dk.any():
        seam |= dk & top & ((np.abs(x - 27.05) < 0.07) | (np.abs(x - 23.4) < 0.07))
        seam |= dk & top & rect_seam(x, w, 24.6, 27.4, -1, 1.15, 0.06)
    bd = is_(T.BODY)
    if bd.any():
        seam |= bd & side & ((np.abs(x - 19.4) < 0.07) | (np.abs(x - 27.05) < 0.07))
        seam |= bd & side & (np.abs(z - 7.4) < 0.06) & (x < 23.0)
        # a louvred vent on the rear body's top between the fans (the lift engines' intake)
        vt = bd & top & rect(x, w, 17.4, 21.6, -1, 1.55)
        seam |= bd & top & rect_seam(x, w, 17.4, 21.6, -1, 1.55, 0.06)
        seam |= vt & (phase(x, 0.6, 17.7) < 0.07)
        up += 0.45 * (vt & (phase(x, 0.6, 18.0) < 0.18))
    hp = is_(T.HUMP)
    if hp.any():
        # the FMV's vents in the fairing behind the canopy: two slots a side
        hs = hp & (np.abs(nw) < 0.75) & (np.abs(nv) > 0.3)
        for x0, x1 in ((28.0, 29.1), (29.5, 30.6)):
            dark |= hs & rect(x, z, x0, x1, 10.2, 10.75)
        seam |= hp & top & (np.abs(x - 29.3) < 0.06)
    ht = is_(T.HATCH)
    if ht.any():
        up += 0.6 * (ht & top) * bolts(x, y, [(25.35, 12.1), (26.65, 12.1), (25.35, 12.9), (26.65, 12.9)], 0.14)
    kl = is_(T.KEEL)
    if kl.any():
        seam |= kl & (np.abs(nv) > 0.5) & (np.abs(x - 20.6) < 0.07)
    bh = is_(T.BULKHEAD)
    if bh.any():
        # its slope behind the canopy: the canopy's rear pane (TS's dark step), framed
        sl = bh & (nu > 0.35) & (nw > 0.35) & (w < 2.2)
        glass |= sl
        frame_px |= sl & (np.abs(w - 2.1) < 0.1)
    # ------------------------------------------------------------------ the nose
    ns = is_(T.NOSE)
    if ns.any():
        lower = ns & (z < 5.02) & (w > 2.6)
        flank = lower & side & out_ & (x < 36.25)                  # TS's house-colour sides: ochre (v3, Luke)
        cheek = lower & (nu > 0.35) & ~flank                       # TS's black cheeks where it narrows to the tip:
        dark |= cheek                                              # intakes, slatted
        slat = cheek & (phase(z, 0.62, 1.75) < 0.1) & (z > 1.7) & (z < 4.7)
        seam |= flank & ((np.abs(z - 4.75) < 0.07) | (np.abs(x - 32.75) < 0.07))
    tp = is_(T.TIP)
    if tp.any():
        put(tp & top, BROWN * g1)                                    # TS's browns on its top
        seam |= tp & (np.abs(nu) < 0.6) & (np.abs(x - 39.2) < 0.06)
    cn = is_(T.CHIN)
    if cn.any():
        seam |= cn & side & (np.abs(x - 34.0) < 0.07)
    cp = is_(T.CANOPY)
    glass |= cp
    if cp.any():
        # the FMV's canopy: its panes framed (the ridge, two bows across)
        fr = cp & ((np.abs(w - 0.0) < 0.1) & (nw > 0.5))
        fr |= cp & (np.abs(x - 35.6) < 0.09)
        fr |= cp & (np.abs(x - 38.2) < 0.08)
        frame_px |= fr
    # ------------------------------------------------------------------ the fans and the tail
    fn = is_(T.FAN)
    if fn.any():
        c_y = np.where(y > T.HYC, T.FAN_C[1][1], T.FAN_C[0][1])
        rr = np.hypot(x - T.FAN_C[0][0], y - c_y)
        seam |= fn & top & (np.abs(rr - (T.FAN_RO - 0.36)) < 0.06)
    fl = is_(T.FLOOR)
    if fl.any():
        # struts across the floor
        pass
    hs_ = is_(T.HOUSING)
    if hs_.any():
        rr = np.hypot(x - T.TAIL_C[0], y - T.TAIL_C[1])
        inner = hs_ & (rr < T.TAIL_RI + 0.12)
        put(inner, OLIVE * g1)                                      # TS's dark walls round the duct
        seam |= hs_ & top & (np.abs(rr - (T.TAIL_RO - 0.45)) < 0.06)
    st = is_(T.STAB)
    if st.any():
        seam |= st & top & (np.abs(x - 3.3) < 0.07) & (w > 3.1)
    bm = is_(T.BOOM)
    if bm.any():
        seam |= bm & ((np.abs(x - 9.6) < 0.07) | (np.abs(x - 13.2) < 0.07))
    fi = is_(T.FIN)
    if fi.any():
        seam |= fi & side & (np.abs(x - (1.55 + 0.0 * z)) < 0.07) & (z > 9.4)

    if MOUTH:
        # the FMV's shark mouth and eye on the nose's sides: over the flank, the cheeks, the tip's and the chin's sides
        sides = is_(T.NOSE, T.TIP, T.CHIN) & (np.abs(nw) < 0.6) & (np.abs(nu) < 0.85) & out_
        sides |= is_(T.NOSE) & cheek
        teeth, gums, lines, eye, pupil = shark_mouth(x, z)
        tz = np.clip((z - 1.6) / 1.8, 0, 1)
        put(sides & gums, GUM_C * (0.75 + 0.25 * tz)[..., None] * g1)
        put(sides & teeth, TOOTH_C * g1)
        put(sides & lines, DARK_C * g1)
        put(sides & eye, EYE_C * g1)
        put(sides & pupil, BLACK_C * g1)
        mouth_px = sides & (teeth | gums | lines | eye | pupil)
        seam[mouth_px] = False; dark[mouth_px] = False; up[mouth_px] = 0
        if ns.any():
            slat &= ~mouth_px

    if getattr(r, 'no_fine', False):
        # the 3D model's vertex colours: the paint's areas only (its joints, slots and bolts are finer than the mesh)
        seam[:] = False; dark[:] = False; up[:] = 0
    house = r.hitmask & np.isin(comp, T.HOUSE) & (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2]))
    put(seam & house & ~glass, GREEN * 0.62 * (1 + 1.1 * grain)[..., None])
    alb[seam & ~house & hm & ~glass] *= 0.62
    if not MOUTH:
        put(dark & hm & ~glass, BLACK_C * g1)
    else:
        put(dark & hm & ~glass & ~mouth_px, BLACK_C * g1)
    if ns.any():
        put(slat, GREY_D * 0.8 * g1)
    if glass.any():
        # dark glass, the sky's reflection lighter towards the top of each pane; the frames grey metal
        gt = 0.55 * np.clip((z - 5.6) / 2.4, 0, 1)
        gcol = GLASS_LO[None, :] * (1 - gt[glass][:, None]) + GLASS_HI[None, :] * gt[glass][:, None]
        gcol = gcol * (1 + 0.25 * np.clip(r.nz[glass], 0, 1))[:, None]
        alb[glass] = gcol
        put(frame_px & glass, GREY * 0.78 * g1)
        L = r.L; V_ = -r.cam.D
        Hh = (L + V_) / np.linalg.norm(L + V_)
        nh = np.clip(r.nx * Hh[0] + r.ny * Hh[1] + r.nz * Hh[2], 0, 1)
        emit[glass] += (0.45 * nh[glass] ** 40 * 255.0)[:, None] * np.array([0.95, 0.97, 1.0])
    r.glass_px = glass
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
    """the house-colour pixels: green on the house parts (their seams too; not their other faces)."""
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, T.HOUSE)


def trim_mask(r, alb):
    return house_mask(r, alb)
