"""
hmec2mat.py - the Mk. II's materials, per pixel of an rcrender.RCRender whose frames give each hit's q coordinates
in its own section (r.lu, r.lv, r.lw = q x, y, z) and r.sec its section (hmec2: q x forward, y from the unit's right
to its left, z up; the body symmetric about q y = 15).

Paint as the Titan's and the Wolverine's: each part one clean colour, TS's own (HMEC.VXL's palette colours, lifted to
the walkers' HD ochre), with the buildings' grain, grime rising from the ground and a camera fill on the sides facing
it.  TS's colours: ochre on the hull, the housing, the rear boxes, the keel and the toes; brown thighs (their knee
ends TS's darker ochre); grey shins, bays, hips, breech and chin; light grey rails on a brown bed; dark bearings and
ankles.  House colour apart: pure green 0,214,0 x (1 + 1.1 grain) on the four pods, the pods' mounts, the front hip
covers and the front shins' guards (TS's remap voxels), with detail only as thin seams.
Details from Westwood's art of the Mk. II where TS's voxels mark the place: plated panels with seams and bolts, the
pods' tube mouths (two round ones in each side pod, as the render's, six in each rear pod), the front's two window
slots, louvres, the feet's treads.
"""
import numpy as np
import walls2 as W
from walls2 import smoothstep
import hmec2 as H
from hmec2 import ZS

GREEN = np.array([0, 214, 0.])
OCHRE = np.array([218, 171, 76.])            # TS 144-147, the walkers' yellow-brown (TS draws the Mk. II as the
                                             # walkers, a touch darker than the MCV)
OCHRE_D = np.array([178, 140, 64.])          # TS 148-152 (the thighs' knee ends, collars, the hub)
BROWN = np.array([110, 88, 50.])             # TS 153-156 (the thighs, the rail bed)
BROWN_D = np.array([76, 62, 38.])
KHAKI = np.array([146, 128, 82.])            # TS 133-135 (the bays' hatches, the housing's slot)
GREY = np.array([150, 150, 155.])            # TS 44-46
GREY_L = np.array([192, 192, 198.])          # TS 39-41
GREY_S = np.array([166, 166, 172.])          # the shins: TS's 44-45 as its render shows them, a light grey
WHITE = np.array([234, 234, 238.])           # TS 33-35
STEEL_D = np.array([72, 72, 76.])            # TS 53-55
DARK = np.array([30, 30, 32.])               # TS 57-60
LAMP_C = np.array([255, 246, 214.])          # the front's lamps (the FMV's searchlight)
GLASS_LO = np.array([58, 104, 168.])         # the front's lit window bands (Westwood's blue), dark at the plate's
GLASS_HI = np.array([138, 188, 236.])        # seam to light under the brow
GRIME = np.array([112, 104, 78.])
FILL = 0.32

PAINT = {H.HULL: OCHRE, H.KEEL: OCHRE, H.RBOX: OCHRE, H.HOUSING: OCHRE, H.HULLFRONT: OCHRE, H.BAYPOST: OCHRE,
         H.TOE: OCHRE, H.GUARD_A: OCHRE, H.FLANGE: OCHRE_D, H.HUB: OCHRE_D, H.THIGH: BROWN, H.RAILBED: BROWN,
         H.HATCH: KHAKI, H.GROOVE: BROWN_D, H.BAY: GREY, H.RHIP: GREY, H.BREECH: GREY, H.CHIN: GREY,
         H.SIDEREC: GREY, H.MUZZLE: GREY, H.SPOD_IN: GREY, H.HIPCAP: GREY_L, H.RAIL: GREY_L, H.PISTON: GREY_L,
         H.SHIN: GREY_S,
         H.HIPBRG: GREY * 0.94, H.KNEEPIN: STEEL_D, H.ANKLE: STEEL_D, H.SLEEVE: STEEL_D, H.BOLT: STEEL_D,
         H.RPOD_IN: DARK, H.CHINTIP: DARK, H.HIPPIN: STEEL_D, H.SHIN_K: KHAKI, H.VISOR: OCHRE, H.TURRET: GREY,
         H.LAMPHOUSE: STEEL_D, H.LAMP: LAMP_C}
GLOSSY = (H.HULL, H.KEEL, H.RBOX, H.HOUSING, H.BAYPOST, H.TOE, H.GUARD_A, H.FLANGE, H.HUB, H.RAIL, H.PISTON,
          H.BREECH, H.MUZZLE, H.CHIN, H.SHIN, H.BAY, H.RHIP, H.VISOR, H.TURRET)


def grain_of(r, scale=1.0):
    X, Y, Z = r.lu * 6.8 * scale, r.lv * 6.8 * scale, r.lw * 6.8 * scale
    ax, ay, az = np.abs(r.nx) + 1e-3, np.abs(r.ny) + 1e-3, np.abs(r.nz) + 1e-3
    s_ = ax + ay + az
    o = r.sec.astype(np.float32) * 37.0          # each section its own grain

    def tri(noise, k):
        return (W.sample(noise, Y + k + o, Z + 2 * k) * ax + W.sample(noise, X + 3 * k, Z + k + o) * ay +
                W.sample(noise, X + k + o, Y + 5 * k) * az) / s_
    return tri(W.NOISE_FINE, 0) * 0.035 + tri(W.NOISE_MOTTLE, 17) * 0.05


def phase(v, per, off=0.0):
    """distance to the nearest line of a set every `per` (offset off)."""
    return np.abs(np.mod(v - off + per / 2, per) - per / 2)


def local_normals(r):
    """each hit's normal in its section's own axes (x forward, y left, z up)."""
    N = np.stack([r.nx, r.ny, r.nz], -1)
    out = np.zeros_like(N)
    for i, (Rw, tw) in enumerate(r.poses):
        m = r.sec == i
        if m.any():
            out[m] = N[m] @ np.asarray(Rw, float)
    return out[..., 0], out[..., 1], out[..., 2]


def rect_seam(x, y, x0, x1, y0, y1, w=0.07):
    """a thin line round the rectangle x0..x1, y0..y1."""
    inside = (x > x0 - w) & (x < x1 + w) & (y > y0 - w) & (y < y1 + w)
    return inside & ((np.abs(x - x0) < w) | (np.abs(x - x1) < w) | (np.abs(y - y0) < w) | (np.abs(y - y1) < w))


def bolts(x, y, pts, r=0.17):
    """(raised, ring) masks and the raise for bolt heads at pts."""
    up = np.zeros(x.shape, np.float32); ring = np.zeros(x.shape, bool)
    for bx, by in pts:
        d = np.hypot(x - bx, y - by)
        up += (d < r) * (1 - d / r)
        ring |= (d >= r) & (d < r + 0.07)
    return up, ring


def materials(r, occ=None):
    comp = r.comp
    sh = comp.shape
    hm = r.hitmask
    alb = np.zeros(sh + (3,), np.float32)
    emit = np.zeros(sh + (3,), np.float32)
    bz = np.zeros(sh, np.float32)                      # shading offset: seams and grooves < 0, raised edges > 0
    grain = grain_of(r, scale=1 / 1.5)
    g1 = (1 + 0.45 * grain)[..., None]
    x, y, z = r.lu, r.lv, r.lw
    sec = r.sec
    nu, nv, nw = local_normals(r)
    top = nw > 0.7
    vert = np.abs(nw) < 0.35
    sidey = vert & (np.abs(nv) > 0.7)                   # faces looking across the unit
    sidex = vert & (np.abs(nu) > 0.7)                   # faces looking along it
    body = sec == H.BODY
    ym = np.where(y > H.BODY_YC, 2 * H.BODY_YC - y, y)  # the body's halves folded onto the right one
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])
    is_ = lambda *cs: np.isin(comp, cs) & hm

    for c, col in PAINT.items():
        put((comp == c) & hm, col * g1)

    seam_o = np.zeros(sh, bool)                         # seams on ochre/grey/brown parts: the part's colour darkened
    # ------------------------------------------------------------------ house colour: pods, mounts, hip covers, guards
    house = is_(*H.HOUSE)
    put(house, GREEN * (1 + 1.1 * grain)[..., None])
    seam_h = np.zeros(sh, bool)
    up = np.zeros(sh, np.float32)
    rp = is_(H.RPOD)
    if rp.any():
        # the rear pods: an inset panel on top with four bolts, a seam along the sides
        t = rp & top & (z > 18.5 + ZS)
        seam_h |= t & rect_seam(x, ym, 3.0, 8.7, 0.8, 5.2)
        u, _ = bolts(x, ym, [(2.55, 0.45), (2.55, 5.55), (8.8, 0.45), (8.8, 5.55)])
        up += u * t
        seam_h |= rp & sidey & (np.abs(z - 17.0 - ZS) < 0.07) & (x < 9.3)
    sp = is_(H.SPOD)
    if sp.any():
        t = sp & top & (z > 15.5 + ZS)
        seam_h |= t & (rect_seam(x, ym, 21.6, 26.6, 0.7, 3.3) | rect_seam(x, ym, 27.4, 32.4, 0.7, 3.3))
        u, _ = bolts(x, ym, [(21.1, 0.4), (21.1, 3.6), (32.9, 0.4), (32.9, 3.6), (27.0, 0.4), (27.0, 3.6)])
        up += u * t
        s = sp & sidey & (x > 20.6) & (x < 33.4)
        seam_h |= s & ((np.abs(z - 12.5 - ZS) < 0.07) | (np.abs(x - 27.0) < 0.07))
    hc = is_(H.HIPCOV)
    if hc.any():
        seam_h |= hc & sidey & (np.abs(z - (np.where(y > 15, 6.23, 6.38) + 0.2)) < 0.06)
        seam_h |= hc & top & (phase(x, 1.4, 29.6) < 0.06)
    gg = is_(H.GUARD_G)
    if gg.any():
        # the front shins' guards: two ribs across
        seam_h |= gg & sidey & ((np.abs(z - 7.6) < 0.08) | (np.abs(z - 9.6) < 0.08))
    put(seam_h & house, GREEN * 0.62 * (1 + 1.1 * grain)[..., None])
    bz -= 0.35 * (seam_h & house)
    bz += 0.5 * up

    # ------------------------------------------------------------------ the hull
    hu = is_(H.HULL)
    if hu.any():
        t = hu & (nw > 0.35)
        # two plated panels each side of the rails, a joint across their middle
        s = t & (rect_seam(x, ym, 5.4, 25.6, 6.4, 11.5) | ((np.abs(x - 15.5) < 0.07) & (ym > 6.4) & (ym < 11.5)))
        seam_o |= s
        u, _ = bolts(x, ym, [(5.9, 6.9), (5.9, 11.0), (25.1, 6.9), (25.1, 11.0), (15.5, 6.9), (15.5, 11.0)], 0.16)
        up2 = u * t
        bz += 0.5 * up2
        # the back face: an inset panel each side of the breech
        b = hu & sidex & (nu < 0)
        seam_o |= b & (rect_seam(ym, z, 5.8, 11.6, 10.0, 15.6))
        # the front face beside the housing
        f = hu & sidex & (nu > 0)
        seam_o |= f & rect_seam(ym, z, 5.8, 10.8, 10.0, 15.4)
        sd = hu & sidey
        seam_o |= sd & (np.abs(z - 12.5) < 0.07)
    kl = is_(H.KEEL)
    if kl.any():
        s = kl & sidey & ((np.abs(z - 6.0) < 0.06) | (np.abs(x - 16.0) < 0.06) | (np.abs(x - 25.0) < 0.06))
        seam_o |= s
    # ------------------------------------------------------------------ the rails, the breech
    rl = is_(H.RAIL)
    put(rl & (nw > 0.6), WHITE * g1)
    rb = is_(H.RAILBED)
    if rb.any():
        u, _ = bolts(x, ym, [(xx, 12.45) for xx in np.arange(2.0, 26.0, 2.0)], 0.14)
        bz += 0.6 * u * (rb & top)
        put(rb & top & (u > 0), BROWN * 1.5 * g1)
    br = is_(H.BREECH)
    if br.any():
        seam_o |= br & (np.abs(x - 2.4) < 0.07) & ~(sidex & (nu < 0))
        cap = br & sidex & (nu < 0)
        d = np.hypot(y - H.BODY_YC, z - 15.2)
        put(cap & (d < 1.6), STEEL_D * g1); put(cap & (d < 1.0), GREY * 0.8 * g1)
    # ------------------------------------------------------------------ the front housing
    ho = is_(H.HOUSING)
    if ho.any():
        sd = ho & sidey
        # plate joints down its sides (TS's darker lines), a joint along it, a louvred vent at its front top
        seam_o |= sd & ((np.abs(x - 31.0) < 0.07) | (np.abs(x - 44.6) < 0.07) | (np.abs(x - 48.2) < 0.07) |
                        ((np.abs(z - 12.8) < 0.07) & (x < 39.0)) | ((np.abs(z - 12.8) < 0.07) & (x > 44.0) & (x < 48.2)))
        vent = sd & (x > 45.2) & (x < 47.7) & (z > 13.5) & (z < 15.9)
        put(vent, BROWN_D * g1)
        sl = vent & (phase(z, 0.42, 13.5) < 0.1)
        put(sl, OCHRE * 0.8 * g1); bz += 0.25 * sl
        tp = ho & top
        # TS's dark slot along the top (x 28..39), a lighter rim; joints across
        slot = tp & (x > 27.6) & (x < 39.4) & (np.abs(y - H.HYC) < 0.5)
        put(slot, KHAKI * 0.55 * g1); bz -= 0.3 * slot
        rim = tp & (x > 27.4) & (x < 39.6) & (np.abs(np.abs(y - H.HYC) - 0.6) < 0.1)
        put(rim, OCHRE * 1.08 * g1)
        seam_o |= tp & ((np.abs(x - 31.0) < 0.07) | (np.abs(x - 44.6) < 0.07)) & (np.abs(y - H.HYC) > 0.7)
        u, _ = bolts(x, y, [(xx, yy) for xx in (28.0, 38.2, 40.0, 46.6) for yy in (H.HY0 + 0.8, H.HY1 - 0.8)], 0.16)
        bz += 0.5 * u * tp
    fl = is_(H.FLANGE)
    if fl.any():
        u, _ = bolts(x, z, [(xx, zz) for xx in (39.6, 43.4) for zz in (12.1, 15.7)], 0.17)
        bz += 0.5 * u * (fl & sidey)
    srec = is_(H.SIDEREC)
    if srec.any():
        # the recess low on each side: vertical cooling ribs (TS's grey with darker lines)
        rib = srec & sidey & (phase(x, 0.7, 35.0) < 0.12)
        put(rib, GREY * 0.62 * g1); bz -= 0.25 * rib
    mz = is_(H.MUZZLE)
    vi = is_(H.VISOR)
    if mz.any() or vi.any():
        # the front's two bays (Westwood's FMV and render): a lit blue window band along the top of each visor plate,
        # running on up the bay's back wall under the brow; the plates TS's ochre below it, a seam between
        for zb, zt in H.FRONT_BAYS:
            ztop = zt - 0.75
            band = (vi & (nu > 0.3) & (z > ztop - 1.1) & (z < ztop + 0.05)) | (mz & sidex & (nu > 0) & (z > ztop - 0.1) &
                                                                                (z < zt + 0.05))
            t = np.clip((z - (ztop - 1.1)) / 1.15, 0, 1)
            gcol = GLASS_LO * (1 - t)[..., None] + GLASS_HI * t[..., None]
            sheen = phase(y + 1.4 * z, 2.2, 0.0) < 0.22
            put(band, gcol * (1 + 0.18 * sheen)[..., None])
            emit += (band * 0.55)[..., None] * gcol
            edge = vi & (nu > 0.3) & (np.abs(z - (ztop - 1.15)) < 0.07)
            put(edge, STEEL_D * 1.1 * g1); bz -= 0.25 * edge
        put(mz & ~sidex, STEEL_D * g1)
        # the visors' front lips and the bays' corners: bolts
        lip = vi & (nu > 0.7) & (np.abs(nw) < 0.3)
        put(lip, OCHRE_D * g1)
    lp = is_(H.LAMP)
    if lp.any():
        lens = lp & sidex & (nu > 0)
        emit += (lens * 0.7)[..., None] * alb
        put(lp & ~lens, STEEL_D * 1.2 * g1)
    ch = is_(H.CHIN)
    if ch.any():
        seam_o |= ch & sidey & (np.abs(z - 3.8) < 0.06)
    # ------------------------------------------------------------------ the rear boxes, the bays, the pods' tubes
    rx = is_(H.RBOX)
    if rx.any():
        seam_o |= rx & sidey & rect_seam(x, z, 3.0, 9.0, 10.0 + ZS, 14.2 + ZS)
        seam_o |= rx & sidex & (nu < 0) & rect_seam(ym, z, 0.8, 4.2, 10.0 + ZS, 14.2 + ZS)
        u, _ = bolts(x, z, [(xx, zz) for xx in (2.55, 9.45) for zz in (9.6 + ZS, 14.5 + ZS)], 0.16)
        bz += 0.5 * u * (rx & sidey)
    bp = is_(H.BAYPOST)
    if bp.any():
        seam_o |= bp & sidey & (np.abs(z - 12.3 - ZS) < 0.07)
    ba = is_(H.BAY)
    if ba.any():
        seam_o |= ba & (top | sidey) & ((np.abs(x - 13.2) < 0.07) | (np.abs(x - 19.3) < 0.07))
    ht = is_(H.HATCH)
    if ht.any():
        f = ht & sidey
        seam_o |= f & rect_seam(x, z, 14.25, 18.35, 10.5 + ZS, 13.9 + ZS)
        handle = f & (np.abs(z - 12.2 - ZS) < 0.13) & (np.abs(x - 16.3) < 0.75)
        put(handle, STEEL_D * 1.4 * g1); bz += 0.4 * handle
    tb = is_(H.SPOD_IN)
    if tb.any():
        # each side pod's end faces: two round tube mouths, stacked (Westwood's twin lenses), a rim round each
        e = tb & sidex
        for zc in (11.25 + ZS, 13.75 + ZS):
            d = np.hypot(ym - 2.0, z - zc)
            put(e & (d < 0.92), GREY_L * 0.95 * g1)
            put(e & (d < 0.74), DARK * g1)
            put(e & (d < 0.5), DARK * 0.6)
            bz += 0.3 * (e & (d >= 0.74) & (d < 0.92))
    rt = is_(H.RPOD_IN)
    if rt.any():
        # each rear pod's front: six tube mouths (two rows of three, as the render's missile pod)
        e = rt & sidex
        for yc in (1.68, 3.0, 4.32):
            for zc in (16.5 + ZS, 17.5 + ZS):
                d = np.hypot(ym - yc, z - zc)
                put(e & (d < 0.43), STEEL_D * 1.2 * g1)
                put(e & (d < 0.3), DARK * 0.45)
    # ------------------------------------------------------------------ the hips
    hb = is_(H.HIPBRG)
    if hb.any():
        # TS's grey bearing plate in its dark frame (a rim round its face), a ring of bolts round the axle cap
        f = hb & sidey
        for name in ('RF', 'LF'):
            px, py, pz = H.J[name]['hip_b']
            m = f & (np.abs(y - py) < 6)
            rim = m & ~((x > px - 3.35) & (x < px + 1.75) & (z > pz - 3.95) & (z < pz + 2.15))
            put(rim, STEEL_D * 1.1 * g1)
            ang = np.arctan2(z - pz, x - px)
            d = np.hypot(x - px, z - pz)
            ring = m & (d > 2.5) & (d < 2.8) & (phase(ang, np.pi / 3, 0.0) < 0.12)
            put(ring, STEEL_D * 1.3 * g1); bz += 0.4 * ring
    hcap = is_(H.HIPCAP)
    if hcap.any():
        f = hcap & sidey
        for name in ('RF', 'LF', 'RR', 'LR'):
            px, py, pz = H.J[name]['hip_b']
            m = f & (np.abs(y - py) < 6) & (np.abs(x - px) < 3)
            d = np.hypot(x - px, z - pz)
            put(m & (d < 0.7), STEEL_D * g1)
            put(m & (d >= 0.7) & (d < 0.85), GREY * 0.8 * g1)
            seam_o |= m & (np.abs(d - 1.45) < 0.07)
    rh = is_(H.RHIP)
    if rh.any():
        seam_o |= rh & sidey & (np.abs(z - 6.0) < 0.06)
    # ------------------------------------------------------------------ the legs
    th = is_(H.THIGH)
    if th.any():
        # TS's darker ochre at each thigh's knee end: a round plate round the knee pin; a seam along the thigh
        for name, (u_, l_, f_, left) in H.LEGS.items():
            kx, ky, kz = H.J[name]['knee_t']
            m = th & (sec == u_)
            d = np.hypot(x - kx, z - kz)
            put(m & (d < 3.1), OCHRE_D * g1)
            seam_o |= m & sidey & (np.abs(d - 3.1) < 0.08)
            hx, hy, hz = H.J[name]['hip_t']
            # a seam from the hip towards the knee plate, down the plate's middle
            a = np.array([kx - hx, kz - hz]); a = a / np.linalg.norm(a)
            nrm = np.array([-a[1], a[0]])
            off = (x - hx) * nrm[0] + (z - hz) * nrm[1]
            along = (x - hx) * a[0] + (z - hz) * a[1]
            seam_o |= m & sidey & (np.abs(np.abs(off) - 1.6) < 0.07) & (along > 1.2) & (d > 3.1)
    kp = is_(H.KNEEPIN, H.ANKLE)
    if kp.any():
        put(kp & sidey, STEEL_D * 1.15 * g1)
    sn = is_(H.SHIN)
    if sn.any():
        # a grille on each shin's front, seams across
        fr = sn & sidex & (nu > 0)
        gr = fr & (z > 3.0) & (z < 7.0) & (phase(z, 0.5, 3.0) < 0.12)
        put(gr, STEEL_D * 1.1 * g1); bz -= 0.25 * gr
        seam_o |= sn & sidey & ((np.abs(z - 4.0) < 0.06) | (np.abs(z - 8.4) < 0.06))
    ga = is_(H.GUARD_A)
    if ga.any():
        seam_o |= ga & sidey & ((np.abs(z - 8.0) < 0.08) | (np.abs(z - 10.0) < 0.08))
    to = is_(H.TOE)
    if to.any():
        # treads across the toes' tops; a seam round each toe's end
        tt = to & top
        tr = tt & (((x < 4.6) | (x > 9.4)) & (phase(x, 0.8, 0.4) < 0.08) | ((y < 5.0) | (y > 9.4)) & (x > 5.0) &
                   (x < 9.0) & (phase(y, 0.8, 0.4) < 0.08))
        put(tr, OCHRE * 0.78 * g1); bz -= 0.12 * tr
        put(tt & ~tr, OCHRE * 1.06 * g1)
    pi = is_(H.PISTON)
    if pi.any():
        put(pi, GREY_L * g1)

    put(seam_o & ~house & hm, (alb * 0.62))
    bz -= 0.3 * (seam_o & ~house & hm)

    # ------------------------------------------------------------------ grime from the ground, the fill light
    low = hm & ~house & ~is_(H.RPOD_IN, H.LAMP)
    dust = smoothstep(4.0, 0.6, r.z) * 0.45
    dust = np.where(is_(H.TOE, H.HUB), dust * 0.3, dust)          # TS's feet stay bright
    d = dust * low
    alb[:] = alb * (1 - d[..., None]) + (GRIME * g1) * d[..., None]
    cam = r.cam
    tc = np.array([cam.T[0] * cam.cE, cam.T[1] * cam.cE, cam.sE]); tc = tc / np.linalg.norm(tc)
    nf = np.clip(r.nx * tc[0] + r.ny * tc[1] + r.nz * tc[2], 0, 1) * (1 - np.clip(r.nz, 0, 1))
    if occ is not None:
        # under the body the legs keep more of the camera's fill (TS's legs read light under it)
        nf = nf * (1 - np.where(body, 0.85, 0.45) * np.clip(occ, 0, 1))
    emit = emit + alb * (FILL * nf)[..., None]
    alb[~hm] = 0
    return alb, (np.zeros(sh, np.float32), np.zeros(sh, np.float32), bz), emit


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, H.HOUSE)
