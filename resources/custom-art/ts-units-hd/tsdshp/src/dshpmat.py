"""
dshpmat.py - the TS Dropship's materials, per pixel of an rcrender.RCRender whose frames give each hit's q coordinates
(r.lu, r.lv, r.lw = q x, y, z).  Faces are told apart by their geometric normals (r.gn*, before the edges are rounded).

TS's colours: GDI's ochre hull (TS 144-152, as the HD buildings' and the other units' ochre) with TS's brown panels
(TS 153-162: the cabin's roofs, the beams, the nose's shoulders), the engine pods' dark olive thruster boxes (TS 77), the
bay grey (TS 47-56), near-black keels and collars (TS 57-60), the sponsons' red-brown decks (TS 108), TS's amber and
yellow lamps; house colour (pure green 0,214,0 x (1 + 1.1 grain), as every HD unit's; v3, Luke: the Dropship takes
house colour) where TS paints house colour: the cargo door, the sponsons' sides, the pods' end frames, the skids and
rails, the nav lamps (v2 painted them GDI's gold, 245, 200, 52, with all-black trims).  Panel seams, vents and louvres
where TS's paint and voxels have them (and the FMV's vents on the tail's spine).
"""
import numpy as np
import walls2 as W
from walls2 import smoothstep
import dshpmodel as T

GOLD = np.array([245, 200, 52.])                    # v2's paint where TS has house colour
GREEN = np.array([0, 214, 0.])                      # v3: house colour there
OCHRE = np.array([214, 166, 72.])                   # TS 144-147
OCHRE_L = np.array([226, 180, 86.])                 # TS 144 (the spines' light panels)
OCHRE_D = np.array([186, 145, 66.])                 # TS 148-152
BROWN = np.array([150, 116, 60.])                   # TS 153-157
BROWN_D = np.array([122, 96, 54.])                  # TS 158-162 (the cabin's roofs)
OLIVE = np.array([74, 72, 40.])                     # TS 77 (52, 52, 28) lifted as the ochre is
GREY = np.array([136, 136, 140.])                   # TS 47-51
GREY_D = np.array([84, 84, 88.])                    # TS 53-56
DARK_C = np.array([40, 40, 42.])                    # TS 57-60
RED_C = np.array([112, 56, 38.])                    # TS 108
INTAKE_C = np.array([20, 20, 22.])
GLASS_LO = np.array([26, 32, 40.])                  # the cockpit's glass: dark, the sky's reflection lighter towards its
GLASS_HI = np.array([92, 108, 128.])                # top (the MCV's, the War Factory's, the Hover MLRS's)
MARK_C = np.array([176, 40, 32.])                   # the FMV's red markers
VANE_C = np.array([58, 58, 62.])
LAMP_C = np.array([255, 150, 40.])                  # TS 7 (170, 85, 0)
LAMP_Y_C = np.array([255, 214, 110.])               # TS 181 (255, 210, 97)
FILL = 0.32

PAINT = {T.TAIL: OCHRE, T.NOSE: OCHRE, T.TAIL_END: GREEN, T.NOSE_TIP: OCHRE, T.DECK: RED_C, T.SPINE: OCHRE_L,
         T.NOSE_HI: OCHRE, T.TIP_HI: OCHRE, T.HOOD: OCHRE, T.CABIN: OCHRE_D, T.NECK: OCHRE_D, T.PIPE: BROWN, T.BLOCK: OCHRE_D,
         T.BAY: GREY, T.SKID: GREEN, T.SPONSON: GREEN, T.KEEL: DARK_C, T.BEAM: BROWN, T.POD: OCHRE, T.CAP: GREEN,
         T.INTAKE: INTAKE_C, T.THRUSTER: OLIVE, T.COLLAR: DARK_C, T.LAMP: LAMP_C, T.LAMP_Y: LAMP_Y_C, T.NAV: GREEN,
         T.CORE: DARK_C}
HOUSE = (T.TAIL_END, T.SKID, T.SPONSON, T.CAP, T.NAV)    # the parts that carry TS's house colour (some only in part)
GLOSSY = (T.LAMP, T.LAMP_Y, T.NAV)
EMIT = {T.LAMP: 0.55, T.LAMP_Y: 0.5, T.NAV: 0.35}


def grain_of(r, scale=1.0):
    X, Y, Z = r.lu * 4.0 * scale, r.lv * 4.0 * scale, r.lw * 4.0 * scale
    ax, ay, az = np.abs(r.nx) + 1e-3, np.abs(r.ny) + 1e-3, np.abs(r.nz) + 1e-3
    s_ = ax + ay + az

    def tri(noise, k):
        return (W.sample(noise, Y + k, Z + 2 * k) * ax + W.sample(noise, X + 3 * k, Z + k) * ay +
                W.sample(noise, X + k, Y + 5 * k) * az) / s_
    return tri(W.NOISE_FINE, 0) * 0.035 + tri(W.NOISE_MOTTLE, 17) * 0.06


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
    grain = grain_of(r)
    g1 = (1 + 0.45 * grain)[..., None]
    x, y, z = r.lu, r.lv, r.lw
    w = np.abs(y - T.HYC)                              # out from the centre line
    nu, nv, nw = local_normals(r)
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])
    is_ = lambda *cs: np.isin(comp, cs) & hm
    top = nw > 0.6
    bot = nw < -0.4
    side = (np.abs(nw) < 0.5) & (np.abs(nv) > 0.6)
    front = (np.abs(nw) < 0.6) & (nu > 0.6)
    back = (np.abs(nw) < 0.6) & (nu < -0.6)

    for c, col in PAINT.items():
        put((comp == c) & hm, col * g1)
    # house colour where v2 had gold (the parts below then paint their other faces in their own colours)
    house_c = (GREEN * (1 + 1.1 * grain)[..., None]).astype(np.float32)
    for c in HOUSE:
        np.copyto(alb, house_c, where=((comp == c) & hm)[..., None])
    seam = np.zeros(sh, bool)
    dark = np.zeros(sh, bool)                          # recessed slots (near black)
    up = np.zeros(sh, np.float32)

    # ------------------------------------------------------------------ the tail
    te = is_(T.TAIL_END)
    if te.any():
        # the cargo door: gold on the back faces (TS's gold voxels), framed, ribbed across, a vent in its top, hinge
        # blocks along its foot; the sides ochre
        door = te & (nu < -0.35)
        put(te & ~door, OCHRE * g1)
        dw = np.where(z > 8.4, 3.5, 3.5 + (8.4 - z) * 0.04)
        seam |= door & rect_seam(w, z, -1, dw, 3.7, 11.7, 0.07)
        seam |= door & (np.abs(z - 8.4) < 0.06)
        seam |= door & (phase(z, 1.3, 4.65) < 0.05) & (z < 8.2) & (z > 4.0) & (w < dw)
        dark |= door & rect(w, z, -1, 1.6, 9.0, 10.8) & (phase(w, 0.8, 0.0) < 0.18)
        up += door * bolts(w, z, [(1.2, 4.1), (2.8, 4.1)], 0.3)
    tl = is_(T.TAIL)
    if tl.any():
        sd = tl & (np.abs(nv) > 0.5)
        # ring seams round the tail, a chine seam along each side
        for xs in (6.8, 13.4, 19.8):
            seam |= tl & (np.abs(x - xs) < 0.07)
        seam |= sd & (np.abs(z - 10.6) < 0.06) & (x > 4.5)
        # TS's dark vents either side of the spine (x 12..13)
        dark |= tl & (nw > 0.5) & rect(x, w, 11.9, 13.5, 2.4, 3.6)
        # rivets along the joints on the sides
        for xs in (6.8, 13.4, 19.8):
            up += 0.45 * (sd & (np.abs(x - xs - 0.2) < 0.09) & (phase(z, 0.6, 0.0) < 0.09))
        # access hatches on the sides, bolted (below the chine aft, above it forward), louvres low near the door
        for (a0, a1, b0, b1) in ((8.0, 11.6, 7.4, 9.9), (15.2, 19.0, 11.6, 14.6)):
            seam |= sd & rect_seam(x, z, a0, a1, b0, b1, 0.06)
            up += 0.5 * sd * bolts(x, z, [(a0 + 0.35, b0 + 0.35), (a1 - 0.35, b0 + 0.35), (a0 + 0.35, b1 - 0.35),
                                         (a1 - 0.35, b1 - 0.35)], 0.15)
        lv = sd & rect(x, z, 4.8, 8.6, 5.2, 7.0)
        seam |= sd & rect_seam(x, z, 4.8, 8.6, 5.2, 7.0, 0.06)
        dark |= lv & (phase(z, 0.45, 5.45) < 0.08)
        up += 0.5 * (lv & (phase(z, 0.45, 5.65) < 0.12))
    spn = is_(T.SPINE)
    if spn.any():
        # the spine: TS's light strip, the vent panel on it (TS's brown patch, x 15..20; the FMV's slots), a second row of
        # slots aft (the FMV's), joints
        st = spn & (nw > 0.5)
        vp = st & rect(x, w, 14.6, 20.6, -1, 2.0)
        put(vp, BROWN * g1)
        seam |= st & ((np.abs(x - 14.6) < 0.06) | (np.abs(x - 20.6) < 0.06))
        dark |= vp & (phase(x, 1.1, 15.4) < 0.22) & (x > 15.0) & (x < 20.2) & (w < 0.8)
        vp2 = st & rect(x, w, 7.4, 10.6, -1, 2.0)
        seam |= st & ((np.abs(x - 7.4) < 0.06) | (np.abs(x - 10.6) < 0.06))
        dark |= vp2 & (phase(x, 0.8, 7.8) < 0.16) & (x > 7.7) & (x < 10.3) & (w < 0.7)
        seam |= spn & (np.abs(x - 3.4) < 0.06)
    # ------------------------------------------------------------------ the nose
    ns = is_(T.NOSE, T.NOSE_TIP, T.NOSE_HI, T.TIP_HI, T.HOOD)
    import dshpnose as N
    glass = np.zeros(sh, bool)
    if ns.any():
        sd = ns & (np.abs(nv) > 0.45)
        # the cockpit window (Westwood's FMV): on the nose's flat plate (dshpnose), a rounded trapezoid a little wider at
        # its top, nearly the plate's width, framed, its recess darker at the top and sides
        Q = np.stack([x, y, z], -1)
        sp_ = N.plate_s(Q)
        v = N.plate_v(Q)                                                                # up the plate from its foot
        u = y - T.HYC
        on_plate = ns & (np.abs(sp_) < 0.16) & (v > 0.12)
        V0, V1, UB, UT, RC = 0.2, 2.78, 2.5, 2.68, 0.42
        half = UB + (UT - UB) * np.clip((v - V0) / (V1 - V0), 0, 1)
        du = np.abs(u) - (half - RC); dv = np.maximum(V0 + RC - v, v - (V1 - RC))
        inside = (np.abs(u) < half) & (v > V0) & (v < V1) & ~((du > 0) & (dv > 0) & (np.hypot(du, dv) > RC))
        glass = on_plate & inside
        frame = on_plate & ~glass & (np.abs(u) < half + 0.22) & (v > V0 - 0.22) & (v < V1 + 0.22)
        rim = glass & ((v > V1 - 0.28) | (np.abs(u) > half - 0.22))
        # the plate's foot, the FMV's two slits stacked either side of the window on the housing's rounded corners
        seam |= ns & (np.abs(sp_) < 0.4) & (np.abs(v - 0.05) < 0.07) & (np.abs(u) < 3.0)
        dark |= ns & (sp_ > -0.9) & (sp_ < 0.1) & (v > 1.05) & (v < 2.45) & (phase(v, 0.75, 1.42) > 0.12) & \
            (np.abs(np.abs(u) - 3.02) < 0.14)
        # TS's light panel along the top (x 79..87), its brown shoulders and front
        lp = ns & (nw > 0.45) & rect(x, w, 78.6, 88.4, -1, 4.6) & ~glass & ~frame
        put(lp, OCHRE_L * g1)
        seam |= ns & (nw > 0.4) & rect_seam(x, w, 78.6, 88.4, -1, 4.6, 0.07)
        put(ns & ~lp & ~glass & ~frame & (nw > 0.3) & ((x < 78.6) | (x > 89.0)), BROWN * g1)
        # TS's brown band round the nose at the chin's top (z 14..15), back to the cabin
        band = ns & ~glass & ~frame & (z > 13.9) & (z < 14.75)
        put(band, BROWN * g1)
        seam |= ns & ~glass & ~frame & ((np.abs(z - 13.9) < 0.06) | (np.abs(z - 14.75) < 0.06))
        put(frame, OCHRE_D * 0.85 * g1)
        seam |= frame & ((np.abs(v - (V0 - 0.22)) < 0.07) | (np.abs(v - (V1 + 0.22)) < 0.07) |
                         (np.abs(np.abs(u) - (half + 0.22)) < 0.07))
        # windows along the top of the sides (the mods' renders): three a side behind the windscreen
        win = sd & (z > 16.55) & (z < 17.4) & ((phase(x, 1.6, 78.6) < 0.5) & (x > 77.6) & (x < 82.6))
        seam |= sd & (z > 16.4) & (z < 17.55) & (phase(x, 1.6, 78.6) < 0.62) & (x > 77.5) & (x < 82.7) & ~win
        glass_w = win
        # a joint along the upper sides framing the windows, joints round the nose, the tip's
        seam |= sd & ~glass & (np.abs(z - 17.85) < 0.06) & (x > 76.5) & (x < 84.0)
        seam |= sd & ~glass & (np.abs(z - 16.1) < 0.06) & (x > 76.5) & (x < 86.0)
        for xs in (79.4, 83.8):
            seam |= ns & ~glass & (np.abs(x - xs) < 0.07) & (z < 13.9)
        seam |= ns & ~glass & (np.abs(x - 93.6) < 0.07)
        glass |= glass_w
        gt = np.where(glass_w, np.clip((z - 16.55) / 0.85, 0, 1), np.clip((v - 0.32) / 2.0, 0, 1))
        gcol = GLASS_LO[None, :] * (1 - gt[glass][:, None]) + GLASS_HI[None, :] * gt[glass][:, None]
        gcol = gcol * (1 + 0.35 * np.clip(r.nz[glass], 0, 1))[:, None]
        gcol = gcol * np.where(rim[glass], 0.5, 1.0)[:, None]
        alb[glass] = gcol
    kl = is_(T.KEEL)
    if kl.any():
        # the nose gear's bay doors, the tail keel's joint
        seam |= kl & ((np.abs(x - 20.0) < 0.07) | (np.abs(x - 78.0) < 0.07) | (np.abs(x - 72.5) < 0.07))
        seam |= kl & (x > 69.0) & (np.abs(nv) > 0.6) & (np.abs(z - 9.6) < 0.06)
    # ------------------------------------------------------------------ the cabin and the neck
    cb = is_(T.CABIN)
    if cb.any():
        rf = cb & top
        put(rf, BROWN_D * g1)
        for xs in (30.2, 38.6):
            seam |= rf & (np.abs(x - xs) < 0.07) & (x < 46.0)
        seam |= rf & rect_seam(x, w, 49.2, 59.6, -1, 3.4, 0.07)               # a hatch on the front roof
        up += 0.5 * (rf & rect(x, w, 49.2, 59.6, -1, 3.4)) * bolts(x, w, [(49.8, 2.8), (59.0, 2.8)], 0.16)
        sd = cb & side
        # TS's bands down the cabin's sides: brown under the roof's edge, light ochre, then browner low down
        put(sd & (z > np.where(x > 46.1, 21.6, 20.6)), BROWN * g1)
        put(sd & (z < 18.4) & (z > 15.0), (OCHRE_D * 0.6 + BROWN * 0.4) * g1)
        seam |= sd & (np.abs(z - 18.4) < 0.06)
        seam |= sd & (np.abs(z - np.where(x > 46.1, 21.6, 20.6)) < 0.06)
        for xs in (30.2, 38.6, 54.4):
            seam |= sd & (np.abs(x - xs) < 0.07) & (z > 15.5)
    nk = is_(T.NECK)
    if nk.any():
        seam |= nk & (np.abs(x - 70.8) < 0.07)
    pp = is_(T.PIPE)
    if pp.any():
        seam |= pp & ((np.abs(x - 68.3) < 0.08) | (np.abs(x - 72.2) < 0.08))
        up += 0.4 * pp * ((np.abs(x - 68.3) < 0.25) | (np.abs(x - 72.2) < 0.25))
    # ------------------------------------------------------------------ the lower body
    bl = is_(T.BLOCK)
    if bl.any():
        put(bl & (np.abs(nv) > 0.6), OCHRE * 0.94 * g1)                          # TS's lighter ochre sides
        put(bl & (nu < -0.3) & (x < 25), GREY_D * g1)                           # the rear block's back (TS black)
        sd = bl & side
        seam |= sd & (np.abs(z - 7.6) < 0.06)
        for xs in (27.0, 63.6, 69.6):
            seam |= sd & (np.abs(x - xs) < 0.07)
        put(bl & bot, GREY_D * g1)
    by = is_(T.BAY)
    if by.any():
        put(by & (z < 3.4), GREY_D * g1)
        sd = by & (np.abs(nv) > 0.6)
        seam |= sd & (phase(x, 2.4, 33.0) < 0.07)
        up += 0.5 * (sd & (phase(x, 2.4, 34.2) < 0.25))                            # ribs (TS's grey shades)
    sk = is_(T.SKID)
    if sk.any():
        seam |= sk & (np.abs(z - 1.9) < 0.06) & (np.abs(nv) > 0.5)
        for xs in (30.0, 59.8):
            seam |= sk & (np.abs(x - xs) < 0.07)
    sp = is_(T.SPONSON)
    if sp.any():
        put(sp & (z < 9.1), GREY_D * g1)
        gs = sp & (z >= 9.1)
        seam |= gs & (np.abs(z - 11.5) < 0.06)
        for xs in (36.4, 42.4, 48.4):
            seam |= gs & (np.abs(x - xs) < 0.07)
    dk = is_(T.DECK)
    if dk.any():
        seam |= dk & (nw > 0.6) & (phase(x, 3.0, 31.5) < 0.06)                    # deck plates
    # ------------------------------------------------------------------ the beams and the pods
    bm = is_(T.BEAM)
    if bm.any():
        # TS's ribbed top: two grooves along each beam, joints at the cabin's sides
        for x0 in (29.0, 65.6):
            seam |= bm & top & ((np.abs(x - (x0 + 2.4)) < 0.07) | (np.abs(x - (x0 + 4.7)) < 0.07))
        seam |= bm & ((np.abs(w - 7.0) < 0.07) | (np.abs(w - 11.0) < 0.07))
    pd = is_(T.POD)
    if pd.any():
        rear = x < 50
        x0 = np.where(rear, 22.0, 60.0); x1 = np.where(rear, 45.0, 78.0)
        L = x1 - x0
        # TS's dark band behind the rear frame on the top (x 24..26), joints across, a seam along the sides, an access
        # panel on the outer side
        put(pd & top & (x > x0 + 1.6) & (x < x0 + 4.2), OLIVE * g1)
        for f in (0.36, 0.64):
            seam |= pd & (np.abs(x - (x0 + f * L)) < 0.07)
        seam |= pd & side & (np.abs(z - np.where(rear, 18.2, 18.8)) < 0.06)
        outer = pd & side & (w > 18.5)
        seam |= outer & rect_seam(x, z, x0 + 0.40 * L, x0 + 0.60 * L, np.where(rear, 18.8, 19.3), 21.0, 0.06)
    cp = is_(T.CAP)
    if cp.any():
        # the frames' faces into the intakes: house colour too, their depth left to the light (v2 darkened them)
        rear = x < 50
        hw0 = np.where(rear, 16.3, 16.5); hw1 = np.where(rear, 18.7, 18.5)
        hz0 = np.where(rear, 17.0, 17.8); hz1 = np.where(rear, 20.2, 20.3)
        seam |= cp & (np.abs(nu) > 0.6) & rect_seam(w, z, hw0 - 0.3, hw1 + 0.3, hz0 - 0.3, hz1 + 0.3, 0.06)
    it = is_(T.INTAKE)
    if it.any():
        put(it & (phase(w, 0.6, 16.0) < 0.1), VANE_C * g1)
    th = is_(T.THRUSTER)
    if th.any():
        # louvres across its outer side and ends (TS's stepped dark boxes), a grille underneath
        sd = th & (np.abs(nw) < 0.5)
        seam |= sd & (phase(z, 0.75, 11.4) < 0.07)
        up += 0.6 * (sd & (phase(z, 0.75, 11.75) < 0.2))
        seam |= th & bot & (phase(x, 0.8, 24.2) < 0.08)
    cl = is_(T.COLLAR)
    if cl.any():
        up += cl * bolts(x, z, [(29.4, 18.2), (35.6, 18.2), (29.4, 20.8), (35.6, 20.8),
                                (66.0, 18.2), (73.0, 18.2), (66.0, 20.8), (73.0, 20.8)], 0.18)

    if getattr(r, 'no_fine', False):
        # the 3D model's vertex colours: the paint's areas only (its seams, slots and bolts are finer than the mesh)
        seam[:] = False; dark[:] = False; up[:] = 0
    alb[seam & hm & ~glass] *= 0.62
    put(dark & hm & ~glass, INTAKE_C * g1)
    if glass.any():
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
    """the house-colour pixels: green on the house parts (their seams too; not the dark slots, not their other faces)."""
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, HOUSE)


def trim_mask(r, alb):
    return house_mask(r, alb)
