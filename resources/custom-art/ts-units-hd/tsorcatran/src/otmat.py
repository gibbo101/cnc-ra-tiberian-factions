"""
otmat.py - the Orca Transport's materials, per pixel of an rcrender.RCRender whose frames give each hit's q coordinates
in the section (r.lu, r.lv, r.lw = q x, y, z).  Faces are told apart by their geometric normals (r.gn*, before the edges
are rounded).

TS's colours (UNITTEM.PAL, lifted as the other HD units' are), placed where TS's voxels paint them:
  GDI's ochre (TS 144-147) on the body, the roof panel, the hump and the strakes, TS's darker ochre and browns (148-163)
  on the panel's bevels, the rear block's dirty lower band and the back slope's frames, TS's khaki (128-137) on the
  bumper, the band along the back slope's top and the hull's shoulders; house colour (pure green 0,214,0 x (1 + 1.1
  grain)) where TS remaps: the wing's slopes, tips and belly band, the front section's flanks, front frame and bottom,
  the nose, the strips under the hull;
  TS's black vents in the back slope (three triangles: either side, and one pointing up between them) as the
  engines' exhausts: dark vanes across them, heat-darkened lips, soot round them where TS paints dark browns;
  TS's grey hatch (44-51) in a dark grey frame (53-56), TS's dark grey rails (53-56) along the deck's edges;
  the cockpit dark grey (53-56) with TS's two black windows (57-62) as dark glass either side of a grey bar, running
  down the hump's dark front; the nose's panes TS's lavender (90) as blue-grey glass;
  the fans: TS's khaki drums (133-137) with a dark olive foot (77-79), olive lips (116-121), light khaki-grey blades
  (69-71), grey hubs (44-51) with dark centres;
  dark olive legs (77-79, 122-127); TS's amber marks (183-184) as small amber lamps where TS has them in pairs (the rear
  block's shoulders, the hull's flanks) and the strip on the belly door.
Panel joints and bolts where TS's parts meet.
"""
import numpy as np
import walls2 as W
import otmodel as T

GREEN = np.array([0, 214, 0.])
OCHRE = np.array([214, 166, 72.])                   # TS 144-147 (190, 145, 60), as the Dropship's, the Orcas' and the
OCHRE_D = np.array([186, 145, 66.])                 # Carryall's; TS 148-152
BROWN = np.array([150, 116, 60.])                   # TS 153-157
BROWN_D = np.array([112, 90, 52.])                  # TS 158-163
KHAKI = np.array([204, 182, 118.])                  # TS 129-131 (206, 182, 113 / 190, 165, 105): the bumper, the band
#                                                     along the back slope's top
SHOULDER = np.array([136, 118, 74.])                # TS 138-139 / 115 (121, 105, 64 ..): the hull's shoulders
DRUM_C = np.array([162, 146, 100.])                 # TS 135-136 / 112 / 72 (149, 133, 80 / 141, 121, 80) on the drums
OLIVE = np.array([100, 92, 70.])                    # TS 118-120 / 143 / 54-55 (97, 89, 64 .. 60, 60, 60): the lips
OLIVE_D = np.array([64, 62, 38.])                   # TS 77-79 / 122-127 (the legs, the drums' feet)
BLADE_C = np.array([166, 164, 136.])                # TS 69-71 (149, 149, 125 .. 125, 125, 101)
HUB_C = np.array([170, 170, 174.])                  # TS 44-46 (153 .. 137), the hubs (the white ring in TS's renders)
GREY = np.array([150, 150, 156.])                   # TS 45-49 (the hatch, the struts)
GREY_D = np.array([84, 84, 88.])                    # TS 13 / 53-56 (the rails, the face plate)
GREY_DD = np.array([66, 66, 70.])                   # TS 53-56 (76 .. 52) on the intake block and the hump's front
DARK_C = np.array([38, 38, 40.])                    # TS 57-62
BLACK_C = np.array([16, 16, 18.])
DUCT_C = np.array([46, 42, 32.])                    # the fans' floors, under the blades
AMBER = np.array([246, 178, 70.])                   # TS 183-184 (246, 182, 80 / 238, 174, 72)
GLASS_LO = np.array([22, 26, 40.])                  # TS's black windows as dark glass, the sky's blue in its reflection
GLASS_HI = np.array([88, 104, 146.])
PANE_LO = np.array([62, 64, 92.])                   # TS's lavender panes (90: 101, 101, 125) as blue-grey glass
PANE_HI = np.array([150, 154, 196.])
FILL = 0.32

PAINT = {T.REAR: OCHRE, T.CORE: OCHRE, T.PANEL: OCHRE, T.BUMPER: KHAKI, T.WING: GREEN, T.HULL: OCHRE,
         T.STRAKE: OCHRE, T.HATCH: GREY, T.HUMP: OCHRE, T.FRONT: GREEN, T.CANOPY: GREY_DD, T.FACE: GREY_D,
         T.NOSE: GREEN, T.DRUM: DRUM_C, T.LIP: OLIVE, T.BLADE: BLADE_C, T.HUB: HUB_C, T.FLOOR: DUCT_C,
         T.STRUT: GREY, T.LEGM: OLIVE_D, T.LEG: OLIVE_D, T.FOOT: OLIVE_D, T.RAIL: GREY_D, T.BELLY: GREEN,
         T.DOOR: OCHRE}
GLOSSY = (T.HUB, T.STRUT, T.RAIL)


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


def poly_sd(a, b, poly):
    """the signed distance (negative inside) from the points (a, b) to a convex polygon's edges: the largest of the
    distances outside each edge's line."""
    P = np.asarray(poly, float)
    c = P.mean(0)
    sd = np.full(np.shape(a), -1e9, np.float32)
    for k in range(len(P)):
        p, q = P[k], P[(k + 1) % len(P)]
        e = q - p
        n = np.array([e[1], -e[0]]) / np.hypot(*e)
        if n @ (c - p) > 0:
            n = -n
        sd = np.maximum(sd, (a - p[0]) * n[0] + (b - p[1]) * n[1])
    return sd


SOOT = np.array([50, 43, 35.])                      # exhaust soot
BURNT = np.array([86, 72, 58.])                     # the exhausts' heat-darkened lips
VANE_C = np.array([56, 52, 47.])                    # the exhausts' vanes, dark heat-stained metal
VANE_P = 0.68                                       # the vanes' spacing (voxels) and half thickness
VANE_T = 0.1


def exhaust(r, alb, w, z, sootable, slope, g1, grain, seam, up):
    """TS's three black vents in the back slope as the engines' exhausts: the opening black, vanes across it (dark metal
    lit along their tops), a burnt lip round it, soot fading out from it over the slope and the bumper below."""
    s_all = np.zeros(w.shape, np.float32)
    for poly in T.VENT_POLYS:
        sd = poly_sd(w, z, poly)
        v = slope & (sd < 0)
        np.copyto(alb, (BLACK_C * g1).astype(np.float32), where=v[..., None])          # TS's black (57-62)
        zb = min(p[1] for p in poly)
        o = np.mod(z - zb - 0.3, VANE_P) - VANE_P / 2                  # offset from the nearest vane's middle
        vane = v & (np.abs(o) < VANE_T) & (sd < -0.12)
        np.copyto(alb, (VANE_C * g1).astype(np.float32), where=vane[..., None])
        lit = vane & (o > 0.035)
        np.copyto(alb, (VANE_C * 1.4 * g1).astype(np.float32), where=lit[..., None])
        up += 0.25 * lit
        seam |= v & (o < -VANE_T) & (o > -VANE_T - 0.07) & (sd < -0.12)  # each vane's shadow on the dark below it
        lip = slope & (sd >= 0) & (sd < 0.22)
        np.copyto(alb, (BURNT * g1).astype(np.float32), where=lip[..., None])
        seam |= slope & (np.abs(sd) < 0.05)
        s = 0.62 * np.clip(1 - sd / 1.35, 0, 1) ** 1.4 * (sd >= 0.22)
        s_all = np.maximum(s_all, s)
    s_all = s_all * sootable * (1 + 0.5 * grain)
    alb[:] = alb * (1 - s_all[..., None]) + SOOT[None, None, :] * s_all[..., None]


def back_slope_z(x):
    """the back slope's height at x (q): the plane through TS's steps (otmodel.BACK)."""
    (x0, z0), (x1, z1) = T.BACK
    return z0 + (x - x0) * (z1 - z0) / (x1 - x0)


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
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])
    is_ = lambda *cs: np.isin(comp, cs) & hm

    for c, col in PAINT.items():
        put((comp == c) & hm, col * g1)
    house_c = (GREEN * (1 + 1.1 * grain)[..., None]).astype(np.float32)
    for c in (T.WING, T.FRONT, T.NOSE, T.BELLY):
        np.copyto(alb, house_c, where=((comp == c) & hm)[..., None])
    seam = np.zeros(sh, bool)
    dark = np.zeros(sh, bool)
    up = np.zeros(sh, np.float32)
    glass = np.zeros(sh, bool)
    pane = np.zeros(sh, bool)
    lamp = np.zeros(sh, bool)
    slot = np.zeros(sh, bool)

    # ------------------------------------------------------------------ the rear block, its bumper and roof panel
    rb = is_(T.REAR)
    if rb.any():
        slope = rb & (nu < -0.35) & (nw > 0.2)
        flank = rb & side
        # TS: the sides' two lowest rows brown (153-163, dark olive at the very bottom), the back's edge browner
        put(flank & (z < 4.9), OCHRE_D * g1)
        put(flank & (z < 4.0), BROWN_D * g1)
        put(flank & (z >= 4.9) & (x < back_slope_z_inv(z) + 1.2), BROWN * g1)
        put(rb & bottom, BROWN_D * g1)
        # the back slope: TS's khaki band along its top (z 9..11), its frames dark ochre, three black vents
        put(slope, OCHRE * g1)                                          # TS: ochre struts and pillars (144-148)
        put(slope & (aw > 11.6) & (z < 8.0), BROWN * g1)               # TS's browns at its outer ends (152-162)
        put(slope & (z > 9.05), KHAKI * g1)
        seam |= slope & (np.abs(z - 9.05) < 0.06) & (aw < 14.6)
        # the vents are the engines' exhausts (Luke): TS's black openings with exhaust vanes across them, a burnt lip,
        # and soot round them on the slope (TS's dark browns there) and down onto the bumper
        exhaust(r, alb, w, z, slope | (is_(T.BUMPER) & ~bottom), slope, g1, grain, seam, up)
        # TS's amber marks on the shoulders (x 7, z 9, either side)
        lamp |= rb & (nw > 0.2) & (np.abs(nv) > 0.3) & (np.abs(x - 7.5) < 0.34) & (np.abs(z - 9.5) < 0.26) & (aw > 11.0)
        # the joint where the block meets the core, the shoulders' crease
        seam |= rb & (np.abs(x - 10.0) < 0.06) & ~slope
    co = is_(T.CORE)
    if co.any():
        put(co & side & (z < 4.0), OCHRE_D * g1)
        put(co & bottom, BROWN_D * g1)
        seam |= co & side & (np.abs(z - 4.6) < 0.05)
    bp = is_(T.BUMPER)
    if bp.any():
        put(bp & bottom, BROWN_D * g1)
        seam |= bp & back & (np.abs(z - 4.0) < 0.05)
        up += 0.45 * (bp & back) * bolts(w, z, [(s * ww, 4.45) for s in (-1, 1) for ww in (2.0, 7.0, 12.4)], 0.16)
    pn = is_(T.PANEL)
    if pn.any():
        flat = pn & (nw > 0.95)
        put(pn & ~flat, OCHRE_D * g1)                                   # TS's darker bevels (148-152)
        put(pn & ~flat & (np.abs(nw) < 0.3), BROWN * g1)                # its upright sides browner
        seam |= flat & (np.abs(x - T.PANEL_A[0]) < 0.06)                # where its two parts meet
        seam |= flat & rect_seam(x, w, 7.2, 17.6, -4.2, 4.2, 0.06)     # a hatch in its top
        up += 0.45 * flat * bolts(x, w, [(7.6, -3.8), (7.6, 3.8), (17.2, -3.8), (17.2, 3.8)], 0.15)

    # ------------------------------------------------------------------ the wing
    wg = is_(T.WING)
    if wg.any():
        # TS: green from x 19 on its slopes, tips and bottom (the belly band); its back edge ochre and brown
        put(wg & (x < 18.95) & ~back, OCHRE_D * g1)
        put(wg & back, BROWN * g1)
        put(wg & back & (z > 8.0), OCHRE_D * g1)
        put(wg & bottom & (x < 19.6), BROWN_D * g1)
        seam |= wg & (np.abs(x - 18.95) < 0.06) & ~back
        seam |= wg & side & (np.abs(z - 4.0) < 0.05)

    # ------------------------------------------------------------------ the hull, its strakes, hatch, hump, rails
    hl = is_(T.HULL)
    if hl.any():
        flank = hl & side & (z < 8.3)
        # TS: the sides' lowest row green from x 28 (the belly strips' tops), brown ahead of the wing
        np.copyto(alb, house_c, where=(flank & (z < 4.0) & (x > 28.0))[..., None])
        put(flank & (z < 4.0) & (x <= 28.0), BROWN * g1)
        put(hl & bottom, OCHRE_D * g1)
        # the shoulders khaki (TS z 9, 128-137) behind the strakes' end, the deck's edges dark grey (the rails' sides)
        shoulder = hl & (nw > 0.3) & (nw < 0.95) & (np.abs(nv) > 0.3)
        put(shoulder & (x > 28.6), SHOULDER * g1)
        put(hl & (np.abs(nv) > 0.6) & (z > 9.25) & (x > T.RAIL_X[0]) & (x < T.RAIL_X[1]), GREY_D * g1)
        # the amber marks on the flanks (TS: x 36..38, z 8, either side)
        lamp |= hl & (np.abs(nv) > 0.3) & (nw < 0.95) & rect(x, z, 36.25, 38.75, 7.95, 8.95) & (aw > 10.2)
        # joints: across the sides behind the wing's front, between the strake panels, along the flanks
        for xj in (28.6, 36.4):
            seam |= flank & (np.abs(x - xj) < 0.06) & (z > 4.0)
        seam |= flank & (np.abs(z - 4.0) < 0.05) & (x > 23.6)
        seam |= hl & top & (np.abs(aw - 7.6) < 0.06) & (x > 29.0) & (x < 43.0)     # the hump's footprint
    sk = is_(T.STRAKE)
    if sk.any():
        put(sk & bottom, OCHRE_D * g1)
        seam |= sk & (np.abs(nw) < 0.5) & ((np.abs(z - 5.05) < 0.05) | (np.abs(z - 6.95) < 0.05))
    ht = is_(T.HATCH)
    if ht.any():
        (hx0, hx1), hw, _ = T.HATCH_BOX
        inner = ht & top & rect(x, w, hx0 + 1.3, hx1 - 0.9, -hw + 1.6, hw - 1.6)
        put(ht & ~inner, GREY_D * g1)                                   # TS's dark grey frame (53-56)
        put(ht & ~top, DARK_C * 1.3 * g1)                               # its edges black (TS's K)
        seam |= ht & top & rect_seam(x, w, hx0 + 1.3, hx1 - 0.9, -hw + 1.6, hw - 1.6, 0.06)
        seam |= inner & (np.abs(w) < 0.05)
        up += 0.45 * (ht & top & ~inner) * bolts(x, w, [(hx0 + 0.7, s * (hw - 0.75)) for s in (-1, 1)] +
                                                  [(hx1 - 0.5, s * (hw - 0.75)) for s in (-1, 1)], 0.15)
    hp = is_(T.HUMP)
    if hp.any():
        (fx0, fz0), (fx1, fz1) = T.HUMP_FRONT
        fslope = hp & (nu > 0.3) & (nw > 0.6) & (x > fx0 - 0.3)
        put(fslope, GREY_DD * g1)                                       # TS: its front dark (53-62)
        put(hp & (np.abs(nw) < 0.5) & (x > fx0 + 0.2), GREY_DD * g1)
        put(hp & (nw > 0.3) & (nw < 0.9) & (np.abs(nv) > 0.3) & (x < fx0), OCHRE_D * g1)   # its bevels
        # TS's two black slots run down its front (y 15..17 and 20..21) onto the intake block
        (gx0, gx1), (gw0, gw1) = T.WINDOWS
        slot |= fslope & (x > gx0) & (aw > gw0) & (aw < gw1)
        seam |= hp & top & (np.abs(x - 34.6) < 0.06)
        seam |= hp & (np.abs(nw) < 0.5) & (np.abs(nu) < 0.5) & (np.abs(z - 12.0) < 0.05) & (x < fx0)
    rl = is_(T.RAIL)
    if rl.any():
        seam |= rl & top & (phase(x, 4.8, 22.0) < 0.05)                 # its sections' joints
        up += 0.4 * (rl & top) * (phase(x, 4.8, 24.4) < 0.16) * (np.abs(aw - 9.0) < 0.22)   # a bolt mid-section

    # ------------------------------------------------------------------ the front section, cockpit, face plate
    fr = is_(T.FRONT)
    if fr.any():
        # TS: green up to w 8, the deck ochre; the front leg's mount dark olive low on the sides (x 50..54, z 3..5)
        deck = fr & (nw > 0.5) & (aw < 8.0)
        put(deck, OCHRE * g1)
        put(deck & (aw < T.COCKPIT_W[1] + 0.5) & (aw > T.COCKPIT_W[1] - 0.1), DARK_C * 1.5 * g1)   # the block's foot
        # TS: dark grey (53-56) in the block's notch and along the face plate's back (x 50..54)
        put(deck & (((x > T.COCKPIT_X[1] - 0.2) & (aw < T.COCKPIT_W[0] + 0.1)) | (x > 52.8)), GREY_DD * g1)
        mount = fr & (x > 50.0) & (x < 54.0) & (z < 5.0) & (aw > 7.6) & ~top
        put(mount, OLIVE_D * g1)
        seam |= fr & (np.abs(aw - 8.0) < 0.05) & (nw > 0.3)
        seam |= fr & ~front & (np.abs(x - 48.4) < 0.06) & (aw > 8.0)
        seam |= fr & front & (np.abs(aw - 11.15) < 0.06)
    cp = is_(T.CANOPY)
    if cp.any():
        (gx0, gx1), (gw0, gw1) = T.WINDOWS
        ctop = cp & top
        slot |= ctop & (x < gx1) & (aw > gw0) & (aw < gw1)
        # TS's grey (44-51) frames: the bar between the windows, strips along their outer sides
        put(ctop & (x < gx1 + 0.4) & (aw < gw0), GREY * g1)
        put(ctop & (x < gx1 + 0.4) & (aw > gw1) & (aw < gw1 + 0.45), GREY * 0.85 * g1)
        seam |= ctop & (np.abs(x - (gx1 + 0.4)) < 0.05) & (aw < gw1 + 0.45)
        seam |= ctop & (np.abs(x - 50.6) < 0.05) & (aw > 3.0)
        up += 0.45 * ctop * bolts(x, w, [(52.0, s * 4.5) for s in (-1, 1)], 0.15)
    fp = is_(T.FACE)
    if fp.any():
        seam |= fp & front & rect_seam(w, z, -9.6, 9.6, 5.8, 9.6, 0.06)
        up += 0.45 * (fp & front) * bolts(w, z, [(s * 10.2, zz) for s in (-1, 1) for zz in (5.5, 9.4)], 0.15)
    st = is_(T.STRUT)
    if st.any():
        post = st & (x < 56.05) & (aw > 6.1)
        put(post, GREY_D * g1)                                          # TS's dark grey frame (x 55)
        seam |= st & ~post & top & (np.abs(x - 57.4) < 0.05)

    # ------------------------------------------------------------------ the nose and its panes
    ns = is_(T.NOSE)
    if ns.any():
        (px0, px1), pw = T.PANES
        fslope = ns & (nu > 0.35) & (nw > 0.35)
        # TS's two lavender bands on the front slope (x 65 at z 10; x 67..68 at z 8..9) between green bars
        band1 = fslope & (x > 65.55) & (x < 66.45) & (aw < 2.75)
        band2 = fslope & (x > 67.05) & (x < 69.05) & (aw < 3.6)
        pane |= band1 | band2
        # the frames: a bar down the middle (the FMV's glazing), green round them
        bar = (band1 | band2) & (aw < 0.11)
        pane &= ~bar
        put(bar, GREEN * 0.62 * (1 + 1.1 * grain)[..., None])
        put(ns & (x < 55.0) & top, GREY_D * g1)                         # its root under the face plate's top
        seam |= ns & ~fslope & (np.abs(x - 55.0) < 0.06) & ~(top & (x < 55.2))
        seam |= ns & side & (np.abs(z - 7.4) < 0.05) & (x > 56.0) & (x < 65.0)

    # ------------------------------------------------------------------ the fans
    dm = is_(T.DRUM)
    if dm.any():
        k, cx, cy = nearest_fan(x, y)
        rr = np.hypot(x - cx, y - cy)
        put(dm & (z < 5.75), OLIVE_D * g1)                               # TS's dark olive foot
        put(dm & bottom, OLIVE_D * 0.8 * g1)
        ang = np.degrees(np.arctan2(y - cy, x - cx))
        seam |= dm & (np.abs(z - 5.75) < 0.05)
        seam |= dm & ~bottom & (np.abs(z - 7.1) < 0.05)                   # where the cup's flare meets its band
        up += 0.4 * dm * ~bottom * (phase(ang, 30.0, 15.0) < 2.6) * (np.abs(z - 8.9) < 0.2)   # bolts round the band
    lp = is_(T.LIP)
    if lp.any():
        k, cx, cy = nearest_fan(x, y)
        rr = np.hypot(x - cx, y - cy)
        inner = lp & (rr < T.LIP_RI + 0.3) & (nw < 0.6)
        put(inner, DUCT_C * 1.3 * g1)                                    # the duct's wall, in its shade
        seam |= lp & ~inner & (np.abs(z - 9.6) < 0.05)
        seam |= lp & top & (np.abs(rr - (T.LIP_RI + 0.95)) < 0.05)
    hb = is_(T.HUB)
    if hb.any():
        k, cx, cy = nearest_fan(x, y)
        rr = np.hypot(x - cx, y - cy)
        dark |= hb & (nw > 0.35) & (rr < 0.55)                          # TS's dark centre
        seam |= hb & (nw > 0.35) & (np.abs(rr - 0.95) < 0.05)
    bl = is_(T.BLADE)

    # ------------------------------------------------------------------ the legs, the belly
    lg = is_(T.LEG, T.FOOT, T.LEGM)
    if lg.any():
        seam |= is_(T.FOOT) & side & (np.abs(z - 0.5) < 0.05)
        up += 0.4 * is_(T.FOOT) * top * bolts(x, w, [(xx, s * ww) for (x0, ww, hw) in T.LEGS for s in (-1, 1)
                                                      for xx in (x0 + 0.6, x0 + 5.4)], 0.15)
    bs = is_(T.BELLY)
    if bs.any():
        seam |= bs & (np.abs(nw) < 0.5) & (phase(x, 4.0, 30.0) < 0.05)
    dr = is_(T.DOOR)
    if dr.any():
        lamp |= dr & bottom & rect(x, y, 12.1, 16.0, 10.05, 10.95)        # TS's amber strip (184, x 12..15, y 10)
        seam |= dr & bottom & rect_seam(x, y, 10.0, 19.0, 8.6, 11.4, 0.06)

    # ------------------------------------------------------------------ the intake's slots (TS's black, 57-62)
    if slot.any():
        (gx0, gx1), (gw0, gw1) = T.WINDOWS
        put(slot, BLACK_C * g1)
        edge = slot & ((np.abs(aw - gw0) < 0.07) | (np.abs(aw - gw1) < 0.07) | (np.abs(x - gx1) < 0.07))
        seam |= edge

    # ------------------------------------------------------------------ finishing
    if getattr(r, 'no_fine', False):
        # the 3D model's vertex colours: the paint's areas only (its joints and bolts are finer than the mesh)
        seam[:] = False; dark[:] = False; up[:] = 0
    house = r.hitmask & np.isin(comp, T.HOUSE) & (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2]))
    put(seam & house & ~glass & ~pane, GREEN * 0.62 * (1 + 1.1 * grain)[..., None])
    alb[seam & ~house & hm & ~glass & ~pane] *= 0.62
    put(dark & hm & ~glass, BLACK_C * g1)
    put(lamp & hm, AMBER * (1 + 0.2 * grain)[..., None])
    L = r.L; V_ = -r.cam.D
    Hh = (L + V_) / np.linalg.norm(L + V_)
    nh = np.clip(r.nx * Hh[0] + r.ny * Hh[1] + r.nz * Hh[2], 0, 1)
    if glass.any():
        # dark glass, the sky's blue in its reflection lighter where it faces up
        gt = 0.32 * np.clip(r.nz[glass], 0, 1) ** 2
        gcol = GLASS_LO[None, :] * (1 - gt[:, None]) + GLASS_HI[None, :] * gt[:, None]
        alb[glass] = gcol
        emit[glass] += (0.45 * nh[glass] ** 40 * 255.0)[:, None] * np.array([0.95, 0.97, 1.0])
    if pane.any():
        gt = np.clip((z[pane] - 8.0) / 3.0, 0, 1)
        alb[pane] = PANE_LO[None, :] * (1 - gt[:, None]) + PANE_HI[None, :] * gt[:, None]
        emit[pane] += (0.4 * nh[pane] ** 40 * 255.0)[:, None] * np.array([0.95, 0.97, 1.0])
    if lamp.any():
        emit[lamp & hm] += np.array([40.0, 22.0, 4.0])                  # a touch of glow, no more than TS's colour
    r.glass_px = glass | pane
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


def back_slope_z_inv(z):
    """the back slope's x at height z (q)."""
    (x0, z0), (x1, z1) = T.BACK
    return x0 + (z - z0) * (x1 - x0) / (z1 - z0)


def house_mask(r, alb):
    """the house-colour pixels: green on the house parts (their seams too)."""
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, T.HOUSE)


def trim_mask(r, alb):
    return house_mask(r, alb)
