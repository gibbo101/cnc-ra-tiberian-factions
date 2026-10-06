"""
cmat.py - the Carryall's materials, per pixel of an rcrender.RCRender whose frames give each hit's q coordinates in the
section (r.lu, r.lv, r.lw = q x, y, z).  Faces are told apart by their geometric normals (r.gn*, before the edges are
rounded).

TS's colours (UNITTEM.PAL, lifted as the other HD units' are): GDI's ochre beam, tail, cab, arms and fan rims (TS
144-147, the Dropship's and the Orcas' ochre), TS's darker ochre and browns on the straps, the rims' undersides and the
duct's lip (TS 148-161), TS's grey hoist bell and claw fingers (TS 44-51), black upper arms and pivots (TS 57-62),
light grey hubs and gear struts (TS 39-43), dark grey gear (TS 53-56); TS's black windows as dark glass, blue as the
cameo's; TS's rust red (TS 106) on the pods' domes and the cab's lamps; house colour (pure green 0,214,0 x (1 + 1.1
grain)) where TS paints house colour: the pods along the spine, the engine under the cab and the outer quarter of each
fan's rim.  Panel joints, vents and bolts where TS's voxels have the parts.
"""
import numpy as np
import walls2 as W
import cmodel as T

GREEN = np.array([0, 214, 0.])
OCHRE = np.array([214, 166, 72.])                   # TS 144-147 (190, 145, 60), as the Dropship's and the Orcas'
OCHRE_D = np.array([186, 145, 66.])                 # TS 148-152
BROWN = np.array([150, 116, 60.])                   # TS 153-157 (the duct's lip, the tail's side strips)
BROWN_D = np.array([112, 90, 52.])                  # TS 158-161 (the rims' undersides)
DUCT_C = np.array([58, 50, 38.])                    # TS 57-62 / 72-79 inside the ducts
OLIVE_G = np.array([112, 104, 76.])                 # TS 116-121 (the windscreen's frame bar)
KHAKI = np.array([170, 152, 98.])                   # TS 133-137 (the pods' vents)
GREY = np.array([138, 138, 144.])                   # TS 44-51 (the bell, the fingers)
HUB_C = np.array([158, 158, 164.])                  # TS 44-46 (the hubs)
GREY_L = np.array([182, 182, 186.])                 # TS 39-43 (the hubs' tops, the gear's struts)
GREY_D = np.array([82, 82, 86.])                    # TS 52-56 (the gear, the claws' tips)
DARK_C = np.array([36, 36, 38.])                    # TS 57-62 (the upper arms, the pivots)
BLACK_C = np.array([18, 18, 20.])
BLADE_C = np.array([80, 80, 86.])
RUST = np.array([136, 78, 60.])                     # TS 106 (117, 68, 52)
GLASS_LO = np.array([24, 30, 50.])                  # TS's black windows as dark glass; the cameo's blue in its
GLASS_HI = np.array([92, 112, 160.])                # reflection, lighter towards the top
FILL = 0.32

PAINT = {T.RIM: OCHRE, T.STRAP: OCHRE_D, T.BLADE: BLADE_C, T.HUB: HUB_C, T.FLOOR: BLACK_C, T.SPINE: OCHRE,
         T.POD: GREEN, T.DOME: RUST, T.TAILB: OCHRE, T.FIN: OCHRE, T.LIP: BROWN, T.ARM: OCHRE, T.CAB: OCHRE,
         T.NACELLE: GREEN, T.BELL: GREY, T.BRACKET: OCHRE_D, T.PIVOT: DARK_C, T.CLAW: DARK_C, T.FINGER: GREY,
         T.TIP: GREY_D, T.GEAR: GREY_D, T.SKID: GREY_D, T.STRUT: GREY_L, T.KEEL: OCHRE_D, T.LAMP: RUST,
         T.TBLADE: DARK_C}
GLOSSY = (T.HUB, T.DOME, T.LAMP, T.STRUT, T.FINGER, T.PIVOT, T.CLAW)


def grain_of(r, scale=1.0):
    X, Y, Z = r.lu * 6.3 * scale, r.lv * 6.3 * scale, r.lw * 6.3 * scale
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


def nearest_fan(x, y):
    """per hit: the index of the nearest fan, its centre's q x and y."""
    cs = np.array([f[1] for f in T.FANS])
    d = np.stack([np.hypot(x - c[0], y - c[1]) for c in cs], 0)
    k = np.argmin(d, 0)
    return k, cs[k, 0], cs[k, 1]


def fan_t(x, y):
    """per hit: the angle round its fan (degrees) from the outward point towards the fan's end, and the radius."""
    k, cx, cy = nearest_fan(x, y)
    o = np.array([f[2] for f in T.FANS], float)[k]; e = np.array([f[3] for f in T.FANS], float)[k]
    vx, vy = x - cx, y - cy
    t = np.degrees(np.arctan2(vx * e, vy * o))
    return t, np.hypot(vx, vy), k


def materials(r, occ=None):
    comp = r.comp
    sh = comp.shape
    hm = r.hitmask
    alb = np.zeros(sh + (3,), np.float32)
    emit = np.zeros(sh + (3,), np.float32)
    grain = grain_of(r, scale=1 / 1.5)
    g1 = (1 + 0.45 * grain)[..., None]
    x, y, z = r.lu, r.lv, r.lw
    w = y - T.HYC
    aw = np.abs(w)
    nu, nv, nw = local_normals(r)
    top = nw > 0.6
    bottom = nw < -0.6
    side = (np.abs(nw) < 0.5) & (np.abs(nv) > 0.6)
    front = (np.abs(nw) < 0.6) & (nu > 0.6)
    back = (np.abs(nw) < 0.6) & (nu < -0.6)
    outward = np.sign(w) * nv > 0.5
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])
    is_ = lambda *cs: np.isin(comp, cs) & hm

    for c, col in PAINT.items():
        put((comp == c) & hm, col * g1)
    house_c = (GREEN * (1 + 1.1 * grain)[..., None]).astype(np.float32)
    for c in (T.POD, T.NACELLE):
        np.copyto(alb, house_c, where=((comp == c) & hm)[..., None])
    seam = np.zeros(sh, bool)
    dark = np.zeros(sh, bool)
    up = np.zeros(sh, np.float32)
    glass = np.zeros(sh, bool)
    frame_px = np.zeros(sh, bool)

    # ------------------------------------------------------------------ the fans
    rm = is_(T.RIM)
    if rm.any():
        t, rr, k = fan_t(x, y)
        outer = rm & ~top & (rr > T.FAN_RO * 1.0 - 0.25)
        inner = rm & ~top & (rr < T.FAN_RI + 0.2) & (nw < 0.6)
        band = outer & (t > T.BAND_T[0]) & (t < T.BAND_T[1]) & (z < 14.6)
        put(outer & (z < 10.85), BROWN_D * g1)                        # TS's dark row under the rims
        put(inner, DUCT_C * g1)                                       # the duct's wall, in its shade
        put(rm & top & (rr < T.FAN_RI + 0.5), OCHRE_D * g1)           # the lip into the duct
        np.copyto(alb, house_c, where=band[..., None])                # TS's house colour on the outer quarter
        seam |= rm & top & (np.abs(rr - (T.FAN_RO - 0.62)) < 0.06)
        seam |= outer & (np.abs(z - 10.85) < 0.05) & ~band
        seam |= band & (np.abs(z - 14.55) < 0.05)
    st = is_(T.STRAP)
    if st.any():
        # the straps: a bolt top and bottom
        t, rr, k = fan_t(x, y)
        up += 0.5 * st * ((np.abs(z - 14.1) < 0.18) | (np.abs(z - 10.5) < 0.18))
        seam |= st & (np.abs(nw) > 0.5)
    hb = is_(T.HUB)
    if hb.any():
        put(hb & (nw > 0.35), GREY_L * g1)                           # the spinners' tops (TS's light grey)
        seam |= hb & (nw < 0.35) & ((np.abs(z - 13.3) < 0.05) | (np.abs(z - 11.4) < 0.05)) & (z > 9.0)
    # ------------------------------------------------------------------ the beam and the pods
    sp = is_(T.SPINE)
    if sp.any():
        # joints across the beam, a row of bolts along its top
        for xj in (11.2, 16.6, 31.7, 37.2):
            seam |= sp & (np.abs(x - xj) < 0.06)
        seam |= sp & top & (aw > 1.0) & (aw < 1.12) & (x > 10.8) & (x < 43.0)
        bx = [(xx, T.Y(s * 0.55)) for xx in np.arange(12.2, 43.0, 2.4) if not (16.0 < xx < 32.0)
              for s in (-1, 1)]
        up += 0.45 * (sp & top) * bolts(x, y, bx, 0.13)
    pd = is_(T.POD)
    if pd.any():
        # a joint across where its bottom steps up, a joint along its top's edge, TS's khaki vents on the outer
        # bevel, a hatch on the outer face
        seam |= pd & (np.abs(x - 24.9) < 0.06) & ~top
        seam |= pd & (nw > 0.2) & (nw < 0.9) & (np.abs(aw - 4.3) < 0.06) & (x > 21.2) & (x < 30.0)
        vt = pd & (x > T.VENT_X[0]) & (x < T.VENT_X[1]) & (aw > 3.9) & (nw > 0.2) & (z > 13.2)
        put(vt, KHAKI * g1)
        seam |= vt & (phase(x, 0.68, T.VENT_X[0] + 0.34) < 0.1)
        seam |= pd & rect_seam(x, z, T.VENT_X[0] - 0.05, T.VENT_X[1] + 0.05, 13.15, 15.2, 0.05) & (aw > 3.8) & (nw > 0.2)
        of = pd & outward & (np.abs(nw) < 0.5)
        seam |= of & rect_seam(x, z, 25.4, 29.6, 12.4, 13.9, 0.05)
        up += 0.5 * of * bolts(x, z, [(25.7, 12.7), (29.3, 12.7), (25.7, 13.6), (29.3, 13.6)], 0.12)
    # ------------------------------------------------------------------ the tail
    tb = is_(T.TAILB)
    if tb.any():
        # TS's brown strip along the tail's upper sides (z 11..13), joints
        put(tb & (nw > 0.3) & (nw < 0.9) & (aw > 2.95) & (aw < 3.75) & (x > 1.6) & (x < 13.4), BROWN * g1)
        seam |= tb & (np.abs(x - 11.2) < 0.06)
        seam |= tb & (np.abs(nv) > 0.5) & (np.abs(z - 9.0) < 0.05) & (x > 3.6) & (x < 11.6)
        seam |= tb & rect_seam(x, z, 5.4, 9.6, 7.3, 8.6, 0.05) & (np.abs(nv) > 0.5)
    fi = is_(T.FIN)
    if fi.any():
        rd = np.hypot(x - T.DUCT_C[0], z - T.DUCT_C[1])
        duct = fi & (rd < T.DUCT_R + 0.06) & (np.abs(nv) < 0.6)
        put(duct, DUCT_C * g1)
        seam |= fi & (np.abs(nv) > 0.5) & (np.abs(x - 8.4 - 0.0 * z) < 0.06) & (z > 13.0)
        up += 0.5 * fi * (np.abs(nv) > 0.5) * bolts(x, z, [(1.0, 13.4), (5.2, 13.4), (1.0, 18.0), (4.6, 18.4)], 0.13)
    am = is_(T.ARM)
    if am.any():
        put(am & bottom, OCHRE_D * g1)
        seam |= am & top & ((np.abs(x - 6.2) < 0.05) | (np.abs(x - 8.8) < 0.05)) & (x < 12)
    # ------------------------------------------------------------------ the cab and its engine
    cb = is_(T.CAB)
    if cb.any():
        x0g, x1g = T.ROOF_GLASS
        s0, s1 = T.SCREEN_GLASS
        (wx0, wz0), (wx1, wz1) = T.WINDSCREEN
        slope = cb & (nu > 0.3) & (nw > 0.3)
        roof = cb & top
        g_roof = roof & (x > x0g) & (x < x1g) & (aw < T.CAB_W - 0.42)
        g_screen = slope & (x > s0) & (x < s1) & (aw < T.CAB_W - 0.5)
        zedge = np.where(x < wx0, 14.0, 14.0 - (x - wx0) * (wz0 - wz1) / (wx1 - wx0))
        g_side = cb & (np.abs(nv) > 0.6) & (x > x0g) & (x < T.SIDE_GLASS[1]) & (z > T.SIDE_GLASS[2]) & \
            (z < zedge - 0.5)
        glass |= g_roof | g_screen | g_side
        # the frames: behind the roof glass (TS's grey strip), the olive bar between it and the windscreen
        put(roof & (x > 45.0) & (x <= x0g) & (aw < T.CAB_W - 0.42), GREY_D * 1.2 * g1)
        put(cb & (nu > 0.0) & (nw > 0.3) & (x >= x1g) & (x <= s0) & (aw < T.CAB_W - 0.42), OLIVE_G * g1)
        # joints: round the cab behind the spine's step, the nose's face, a door on each side
        seam |= cb & (np.abs(x - 43.25) < 0.06) & (z > 10.0)
        seam |= cb & (np.abs(nv) > 0.6) & rect_seam(x, z, 41.0, 44.4, 6.7, 12.2, 0.06)
        up += 0.45 * cb * (np.abs(nv) > 0.6) * bolts(x, z, [(43.9, 9.4)], 0.18)
        seam |= cb & front & (np.abs(z - 9.0) < 0.06)
        seam |= cb & (np.abs(nv) > 0.6) & (np.abs(z - 7.2) < 0.05) & (x > 41.0)
        up += 0.4 * cb * front * bolts(y, z, [(T.Y(-1.6), 8.1), (T.Y(1.6), 8.1), (T.Y(-1.6), 10.0), (T.Y(1.6), 10.0)],
                                       0.13)
    nc = is_(T.NACELLE)
    if nc.any():
        # the intake in its front (TS's hole, brown inside), bands round it
        rn = np.hypot(w, z - T.NAC_C[0])
        cap = nc & (nu > 0.7)
        put(cap & (rn < 1.36), DUCT_C * 0.8 * g1)
        dark |= cap & (rn < 0.42)
        vane = cap & (rn > 0.42) & (rn < 1.36) & (phase(np.degrees(np.arctan2(z - T.NAC_C[0], w)), 30.0) < 3.0)
        put(vane, BROWN * 0.8 * g1)
        seam |= cap & (np.abs(rn - 1.36) < 0.06)
        seam |= nc & ~cap & ((np.abs(x - 44.2) < 0.06) | (np.abs(x - 49.2) < 0.06))
    # ------------------------------------------------------------------ the hoist and the claws
    bl = is_(T.BELL)
    if bl.any():
        rb = np.hypot(x - T.BELL_C[0], y - T.BELL_C[1])
        bt = bl & bottom
        seam |= bt & ((np.abs(rb - 1.9) < 0.06) | (np.abs(rb - 3.7) < 0.06))
        dark |= bt & (rb < 0.75)
        ang = np.degrees(np.arctan2(y - T.BELL_C[1], x - T.BELL_C[0]))
        seam |= bl & ~bt & (phase(ang, 30.0, 15.0) < 0.9)
        up += 0.45 * bt * (phase(ang, 45.0, 22.5) < 3.0) * (np.abs(rb - 2.8) < 0.2)
    br = is_(T.BRACKET)
    if br.any():
        seam |= br & (np.abs(z - 9.7) < 0.05)
    fg = is_(T.FINGER)
    if fg.any():
        seam |= fg & (np.abs(z - 3.6) < 0.05)
    sk = is_(T.SKID)
    if sk.any():
        put(sk & top, GREY * g1)                                      # TS's lighter line along the skids
    lp = is_(T.LAMP, T.DOME)

    if getattr(r, 'no_fine', False):
        # the 3D model's vertex colours: the paint's areas only (its joints, slots and bolts are finer than the mesh)
        seam[:] = False; dark[:] = False; up[:] = 0; frame_px[:] = False
    house = r.hitmask & np.isin(comp, T.HOUSE) & (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2]))
    put(seam & house & ~glass, GREEN * 0.62 * (1 + 1.1 * grain)[..., None])
    alb[seam & ~house & hm & ~glass] *= 0.62
    put(dark & hm & ~glass, BLACK_C * g1)
    if glass.any():
        # dark glass, the sky's blue reflection lighter towards the top; the frames dark grey
        gt = 0.75 * np.clip((z - 11.2) / 2.9, 0, 1)
        gcol = GLASS_LO[None, :] * (1 - gt[glass][:, None]) + GLASS_HI[None, :] * gt[glass][:, None]
        gcol = gcol * (1 + 0.25 * np.clip(r.nz[glass], 0, 1))[:, None]
        alb[glass] = gcol
        if not getattr(r, 'no_fine', False):
            # the frames between the panes: down the roof glass's middle, the side windows' posts
            fm = glass & (((aw < 0.08) & (nw > 0.3)) | ((np.abs(nv) > 0.6) & (np.abs(x - 47.2) < 0.08)))
            put(fm, GREY_D * 1.2 * g1)
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
    """the house-colour pixels: green on the house parts (their seams too)."""
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, T.HOUSE)


def trim_mask(r, alb):
    return house_mask(r, alb)
