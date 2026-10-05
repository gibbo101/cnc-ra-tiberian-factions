"""
mcv2mat.py - the MCV's materials, per pixel of an rcrender.RCRender (r.lu, r.lv, r.lw: the body frame, u forward, v right,
w up, in voxels; the voxel frame is x = u + CX, y = CY - v, z = w; r.Mb maps body to world).

Paint as the Titan's and the Wolverine's: each part one clean colour, TS's own (MCV.VXL's palette colours, lifted to the
HD ochre as the Titan's), with the buildings' grain, grime rising from the ground and a camera fill on the sides facing
it.  TS's colours: ochre on the hull, the decks, the cab and the pedestal; orange on the rear block's back, the cab's
roof panel, the crate lids, the front-left block's top and the hitch; a light grey spine with a darker housing and
white ribs; dark tracks, bumpers, ramp and coupling.  House colour apart: pure green 0,214,0 x (1 + 1.1 grain) on the
four pod covers and the three deck panels (TS's remap voxels), with detail only as thin seams.
Details from Westwood's renders where TS's voxels mark the place: the covers' inset panels and corner bolts, the track's
links, the spine's segments, the cab's visor slats and grille, the ramp's louvres, the crates' lids and frames, lamps.
"""
import numpy as np
import walls2 as W
from walls2 import smoothstep
import mcv2 as M

GREEN = np.array([0, 214, 0.])
OCHRE = np.array([226, 180, 82.])            # TS 144-147, the Titan's yellow-brown a touch lighter: TS draws the MCV
                                             # brighter and yellower than the walkers (its in-mod paint averages 154,122,54)
OCHRE_D = np.array([192, 154, 76.])          # TS 148-150 (rails, frames)
ORANGE = np.array([238, 164, 62.])           # TS 184-185
ORANGE_L = np.array([240, 172, 76.])
BROWN = np.array([112, 90, 50.])             # TS 153-156
OLIVE = np.array([62, 62, 34.])              # TS 76-77 (hatches, steps)
DARK = np.array([46, 46, 48.])               # TS 57-58 (belt, bumpers, ramp)
STEEL_D = np.array([70, 70, 72.])
CORE_C = np.array([20, 20, 20.])
GREY = np.array([142, 142, 146.])            # TS 45-46: the spine's housing
LIGHT = np.array([196, 196, 200.])           # TS 39-40: the spine's sides
WHITE = np.array([234, 234, 238.])           # TS 33-35: its top and ribs
HUB_C = np.array([206, 164, 80.])
GRIME = np.array([112, 104, 78.])
LAMP_Y = np.array([255, 236, 110.])
LAMP_W = np.array([255, 255, 248.])
FILL = 0.32

PAINT = {M.HULL: OCHRE, M.DECK: OCHRE, M.WALL: OCHRE, M.RAIL: OCHRE_D, M.BLOCK: OCHRE, M.CAB: OCHRE, M.NOSE: OCHRE,
         M.PED: OCHRE, M.SADDLE: OCHRE_D, M.LDECK: OCHRE_D, M.FLBLOCK: OCHRE, M.CRATE: OCHRE, M.ROOF: ORANGE,
         M.LID: ORANGE, M.FLTOP: ORANGE, M.HITCH: ORANGE, M.VISOR: OCHRE, M.DIVIDER: BROWN, M.LRAIL: OLIVE,
         M.HATCH: OLIVE, M.STEP: OLIVE, M.VENT: OLIVE, M.BELT: DARK, M.BUMPER: STEEL_D, M.RAMP: DARK,
         M.COUPLING: DARK, M.PULLEY: DARK, M.CABIN: OCHRE, M.CPLATE: OCHRE_D, M.TIP: DARK, M.CAP: STEEL_D, M.UNDER: np.array([74, 66, 44.]),
         M.CORE: CORE_C, M.OPENING: CORE_C, M.WHEEL: STEEL_D, M.HUB: HUB_C, M.HOUSING: GREY, M.BOOM_G: GREY,
         M.BOOM_W: LIGHT, M.JOINT: WHITE, M.LAMP_Y: LAMP_Y, M.LAMP_W: LAMP_W}
GLOSSY = (M.HULL, M.DECK, M.WALL, M.RAIL, M.BLOCK, M.CAB, M.NOSE, M.PED, M.SADDLE, M.LDECK, M.FLBLOCK, M.CRATE, M.ROOF,
          M.LID, M.FLTOP, M.HITCH, M.FRAME, M.HOUSING, M.BOOM_G, M.BOOM_W, M.JOINT, M.GLASS, M.CABIN, M.CPLATE)


def grain_of(r, scale=1.0):
    X, Y, Z = r.lu * 6.1 * scale, r.lv * 6.1 * scale, r.lw * 6.1 * scale
    ax, ay, az = np.abs(r.nx) + 1e-3, np.abs(r.ny) + 1e-3, np.abs(r.nz) + 1e-3
    s_ = ax + ay + az

    def tri(noise, o):
        return (W.sample(noise, Y + o, Z + 2 * o) * ax + W.sample(noise, X + 3 * o, Z + o) * ay +
                W.sample(noise, X + o, Y + 5 * o) * az) / s_
    return tri(W.NOISE_FINE, 0) * 0.035 + tri(W.NOISE_MOTTLE, 17) * 0.05


def mottle(r, scale=1.0):
    X, Y, Z = r.lu * 6.1 * scale, r.lv * 6.1 * scale, r.lw * 6.1 * scale
    return (W.sample(W.NOISE_MOTTLE, X + 2 * Y, Z + 7) + W.sample(W.NOISE_MOTTLE, Y + 11, X + Z)) * 0.5


def phase(v, per, off=0.0):
    """distance to the nearest line of a set every `per` (offset off)."""
    return np.abs(np.mod(v - off + per / 2, per) - per / 2)


def body_normals(r):
    N = np.stack([r.nx, r.ny, r.nz], -1)
    B = N @ np.asarray(r.Mb, float)
    return B[..., 0], B[..., 1], B[..., 2]


def materials(r, occ=None):
    comp = r.comp
    sh = comp.shape
    hm = r.hitmask
    alb = np.zeros(sh + (3,), np.float32)
    emit = np.zeros(sh + (3,), np.float32)
    bz = np.zeros(sh, np.float32)                      # shading offset: seams and grooves < 0, raised edges > 0
    grain = grain_of(r, scale=1 / 1.5)
    g1 = (1 + 0.45 * grain)[..., None]
    x = r.lu + M.CX; y = M.CY - r.lv; z = r.lw
    nu, nv, nw = body_normals(r)
    top = nw > 0.7
    vert = np.abs(nw) < 0.35
    sidey = vert & (np.abs(nv) > 0.7)                   # faces looking across the unit
    sidex = vert & (np.abs(nu) > 0.7)                   # faces looking along it
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])
    is_ = lambda *cs: np.isin(comp, cs) & hm

    for c, col in PAINT.items():
        put((comp == c) & hm, col * g1)

    # ------------------------------------------------------------------ house colour: covers and deck panels
    house = is_(*M.HOUSE)
    hc = GREEN * (1 + 1.1 * grain)[..., None]
    put(house, hc)
    seam = np.zeros(sh, bool)
    cov = is_(M.COVER) & top
    if cov.any():
        # each pod cover's top: an inset panel (a groove 0.75 in from its edges, as the renders' pods), four bolts
        for P in M.PODS:
            for left in (False, True):
                ya, yb = (0.0, 6.0) if not left else (M.YW - 6.0, M.YW)
                m = cov & (x > P['x0'] - 0.1) & (x < P['x1'] + 0.1) & (y > ya - 0.1) & (y < yb + 0.1)
                if not m.any():
                    continue
                ix0, ix1, iy0, iy1 = P['x0'] + 0.85, P['x1'] - 0.85, ya + 0.85, yb - 0.85
                gx = (np.abs(x - ix0) < 0.09) | (np.abs(x - ix1) < 0.09)
                gy = (np.abs(y - iy0) < 0.09) | (np.abs(y - iy1) < 0.09)
                inside = (x > ix0 - 0.1) & (x < ix1 + 0.1) & (y > iy0 - 0.1) & (y < iy1 + 0.1)
                g = m & inside & ((gx & (y > iy0 - 0.1) & (y < iy1 + 0.1)) | (gy & (x > ix0 - 0.1) & (x < ix1 + 0.1)))
                seam |= g
                for bx in (P['x0'] + 0.42, P['x1'] - 0.42):
                    for by in (ya + 0.42, yb - 0.42):
                        d = np.hypot(x - bx, y - by)
                        bolt = m & (d < 0.17)
                        bz += 0.5 * bolt * (1 - d / 0.17)
                        bz -= 0.25 * (m & (d >= 0.17) & (d < 0.24))
    hp = is_(M.HPANEL) & top
    if hp.any():
        # the deck panels: a seam round each, and cross seams on the long one (TS's panels as the renders' plating)
        e = ((np.abs(x - 20.55) < 0.08) | (np.abs(x - 27.45) < 0.08) | (np.abs(y - 6.55) < 0.08) |
             (np.abs(y - 13.45) < 0.08)) & (x > 20.4) & (x < 27.6) & (y > 6.4) & (y < 13.6)
        e |= ((np.abs(x - 22.3) < 0.07) | (np.abs(x - 24.0) < 0.07) | (np.abs(x - 25.7) < 0.07)) & (y > 6.5) & (y < 13.5)
        e |= ((np.abs(x - 5.55) < 0.08) | (np.abs(x - 12.45) < 0.08) | (np.abs(y - 8.55) < 0.08) |
              (np.abs(y - 13.45) < 0.08)) & (x > 5.4) & (x < 12.6) & (y > 8.4) & (y < 13.6)
        e |= (np.abs(y - 10.0) < 0.07) & (x > 29.4) & (x < 30.6) & (z > 8.5)
        seam |= hp & e
    put(seam & house, GREEN * 0.62 * (1 + 1.1 * grain)[..., None])
    bz -= 0.35 * (seam & house)

    # ------------------------------------------------------------------ the track
    belt = is_(M.BELT)
    if belt.any():
        # links: on the running surfaces a groove every 0.62 voxel across the belt, on the outer side the link plates
        run = belt & ~sidey
        lk = run & (phase(x + 0.6 * z, 0.62) < 0.1)
        alb[lk] *= 0.55; bz -= 0.4 * lk
        sd = belt & sidey
        lk2 = sd & (phase(x, 0.62) < 0.07)
        alb[lk2] *= 0.7
        # the links' edges catch a little light
        put(run & (phase(x + 0.6 * z, 0.62) > 0.25) & (phase(x + 0.6 * z, 0.62) < 0.31), DARK * 1.45 * g1)
    wh = is_(M.WHEEL)
    if wh.any():
        put(wh & ~sidey, DARK * 1.1 * g1)                 # the tyres' running faces darker than the wheel discs
    hub = is_(M.HUB)
    if hub.any():
        # a hub cap with a ring of bolts
        put(hub, HUB_C * g1)
    # ------------------------------------------------------------------ hull, decks, walls
    hull = is_(M.HULL, M.UNDER, M.BUMPER, M.LDECK)
    dust = smoothstep(4.2, 0.8, z) * 0.45
    deck = is_(M.DECK) & top
    if deck.any():
        # deck plates: seams across every 6.5 voxels and along the middle of the right deck; a non-slip tread
        ds = deck & ((phase(x, 6.5, 1.0) < 0.07) | ((np.abs(y - 10.0) < 0.06) & (y < 14)))
        put(ds, OCHRE * 0.66 * g1); bz -= 0.3 * ds
        tread = deck & (y < 14) & ((phase(x + y, 0.55) < 0.06) | (phase(x - y, 0.55) < 0.06))
        alb[tread] *= 0.93
    rail = is_(M.RAIL, M.WALL) & top
    put(rail, OCHRE * 1.06 * g1)
    hs = is_(M.HULL) & sidey
    if hs.any():
        # the hull's side: a seam along it, and panel joints
        s2 = hs & ((np.abs(z - 3.0) < 0.06) | (phase(x, 6.5, 1.0) < 0.06))
        put(s2, OCHRE * 0.62 * g1); bz -= 0.3 * s2
    bump = is_(M.BUMPER)
    if bump.any():
        # vent teeth along the bumpers (the renders' teeth low at the ends)
        teeth = bump & vert & (phase(y, 1.0, 0.5) < 0.18)
        put(teeth, STEEL_D * 0.55 * g1); bz -= 0.3 * teeth

    # ------------------------------------------------------------------ the rear block, the cab
    blk = is_(M.BLOCK)
    if blk.any():
        # TS paints its back third orange
        put(blk & (x < 5.6), ORANGE * g1)
        put(blk & (x >= 5.6) & (x < 5.75), OCHRE * 0.6 * g1)
        # louvres on its outer side, under the top's edge (TS's olive vent bits there)
        lv = blk & sidey & (nv > 0) & (x > 6.2) & (x < 12.6) & (z > 8.3) & (z < 9.5)
        sl = lv & (phase(z, 0.3, 8.3) < 0.08)
        put(lv, OLIVE * 1.2 * g1); put(sl, OLIVE * 0.55 * g1); bz -= 0.3 * sl
        lv2 = blk & sidey & (nv > 0) & (x > 5.3) & (x < 8.7) & (z > 6.15) & (z < 7.6)
        put(lv2, OLIVE * g1); put(lv2 & (phase(x, 0.5, 5.3) < 0.1), OLIVE * 0.5 * g1)
        # the top's edge seam
        e = blk & top & ((np.abs(x - 13.6) < 0.07) | (np.abs(x - 2.4) < 0.07))
        put(e, OCHRE * 0.62 * g1)
    hat = is_(M.HATCH)
    if hat.any():
        # hatches: a frame, a handle
        fr = hat & top
        cx_ = np.where(x > 20, 34.5, 7.0); cy_ = np.where(x > 20, 7.18, 7.12)
        handle = fr & (np.abs(x - cx_) < 0.45) & (np.abs(y - cy_) < 0.11)
        put(handle, STEEL_D * 1.6 * g1); bz += 0.4 * handle
    cab = is_(M.CAB)
    if cab.any():
        # a door on the front block's outer side, a seam round it
        door = cab & sidey & (nv > 0) & (((np.abs(x - 32.1) < 0.07) | (np.abs(x - 35.0) < 0.07)) & (z > 6.3) & (z < 9.5) |
                                         (np.abs(z - 9.5) < 0.07) & (x > 32.1) & (x < 35.0))
        put(door, OCHRE * 0.6 * g1); bz -= 0.3 * door
        # TS's orange band across the step's front under the vent
        put(cab & sidex & (nu > 0) & (x > 38.95) & (z > 5.95) & (z < 7.45), ORANGE * g1)
    vis = is_(M.VISOR)
    if vis.any():
        # the vent's louvres: TS's orange and ochre alternating, a shadowed gap between them
        s = phase(y, 1.0, 6.95) < 0.3
        put(vis & s, ORANGE * g1)
        put(vis & ~s, OCHRE * 0.55 * g1); bz -= 0.25 * (vis & ~s)
    glass = is_(M.GLASS)
    if glass.any():
        # dark glass, the sky's reflection lighter towards its top, a soft diagonal sheen
        t = np.clip((z - 5.15) / 2.45, 0, 1)
        gcol = np.array([28, 34, 42.]) * (1 - t)[..., None] + np.array([80, 94, 110.]) * t[..., None]
        sheen = (phase(y + 1.2 * x, 3.0, 0.0) < 0.3)
        put(glass, gcol * (1 + 0.25 * sheen)[..., None])
    put(is_(M.FRAME), ORANGE * g1)
    gr = is_(M.GRILLE)
    if gr.any():
        put(gr, BROWN * 0.55 * g1)
        chin = gr & (x > 44.0)
        slat = (chin & (phase(y, 0.5, 19.7) < 0.14)) | (gr & ~chin & (phase(z, 0.3, 4.4) < 0.08))
        put(slat, OCHRE * 0.7 * g1); bz += 0.25 * slat
    cp = is_(M.CPLATE)
    put(cp & ~top & (nw < 0.3) & (z < 4.0), ORANGE * g1)      # TS's orange chin, low on the bonnet's sides
    nose = is_(M.NOSE)
    if nose.any():
        # TS's orange bands across the nose's front, above and below the grille
        front = nose & sidex & (nu > 0)
        band = front & (((z > 3.15) & (z < 4.0)) | ((z > 6.0) & (z < 6.75)))
        put(band, ORANGE * g1)
    roof = is_(M.ROOF) & top
    if roof.any():
        e = roof & ((np.abs(x - 34.25) < 0.06))
        put(e, ORANGE * 0.62 * g1)
    st = is_(M.STEP)
    put(st & top, OLIVE * 1.6 * g1)

    # ------------------------------------------------------------------ the pedestal and the spine
    ped = is_(M.PED)
    if ped.any():
        s = ped & vert & (phase(x, 2.5, 6.0) < 0.06)
        put(s, OCHRE * 0.62 * g1); bz -= 0.3 * s
    sad = is_(M.SADDLE)
    if sad.any():
        # TS's dark olive band along the saddle's right side
        put(sad & sidey & (nv > 0), OLIVE * 1.1 * g1)
    hou = is_(M.HOUSING)
    if hou.any():
        # the dark hatch on the housing's top (TS's dark patch at x 6-9), its frame lighter
        h = hou & top & (x > 6.0) & (x < 10.0) & (y > 15.1) & (y < 17.9)
        put(h, STEEL_D * 0.75 * g1)
        hf = hou & top & (x > 5.75) & (x < 10.25) & (y > 14.85) & (y < 18.15) & ~h
        put(hf, GREY * 1.12 * g1)
        # a seam round the housing just under its top edge
        s = hou & vert & (np.abs(z - 14.0) < 0.06)
        put(s, GREY * 0.7 * g1)
    bw = is_(M.BOOM_W)
    if bw.any():
        # the long section: white on top (TS), light grey on its sides, segments every 2.6 voxels (the renders' spine)
        put(bw & (nw > 0.55), WHITE * g1)
        seg = bw & (phase(x, 2.6, 19.5) < 0.07) & (x > 19.8) & (x < 27.7)
        put(seg, LIGHT * 0.7 * g1); bz -= 0.3 * seg
    bg = is_(M.BOOM_G)
    put(bg & (nw > 0.55), GREY * 1.12 * g1)
    jt = is_(M.JOINT)
    if jt.any():
        # the collar's slot through its top (TS's gap at y 16)
        slot = jt & top & (x > 28.2) & (x < 29.8) & (y > 15.9) & (y < 17.1)
        put(slot, CORE_C * 1.5)
    tip = is_(M.TIP)
    put(tip & sidex, STEEL_D * 1.2 * g1)
    ramp = is_(M.RAMP)
    if ramp.any():
        # louvres across the slope; the flat top and front plain
        slope = ramp & (nw > 0.3) & (nw < 0.95) & (np.abs(nu) > 0.2)
        lv = slope & (phase(x, 0.55, 26.0) < 0.16)
        put(lv, DARK * 1.6 * g1); bz += 0.25 * lv
        topr = ramp & top & (x > 30.4)
        tl = topr & (phase(x, 0.9, 30.4) < 0.1)
        put(tl, DARK * 1.4 * g1)
    pul = is_(M.PULLEY)
    put(pul & sidey, STEEL_D * g1)

    # ------------------------------------------------------------------ the crate rack
    lid = is_(M.LID) & top
    if lid.any():
        # a lid's inset and its two handles
        crate_edges = np.array([(3.0, 6.0), (7.0, 14.0), (15.0, 21.0), (22.0, 24.0), (26.0, 29.0)])
        inset = np.zeros(sh, bool); handle = np.zeros(sh, bool)
        for a, b in crate_edges:
            m = lid & (x > a) & (x < b)
            ia, ib = a + 0.55, b - 0.55
            g = m & ((np.abs(x - ia) < 0.06) | (np.abs(x - ib) < 0.06) | (np.abs(y - 19.75) < 0.06) |
                     (np.abs(y - 23.25) < 0.06)) & (x > ia - 0.06) & (x < ib + 0.06) & (y > 19.69) & (y < 23.31)
            inset |= g
            if b - a > 2.5:
                xm = (a + b) / 2
                handle |= m & (np.abs(x - xm) < 0.55) & ((np.abs(y - 19.45) < 0.09) | (np.abs(y - 23.55) < 0.09))
        put(inset, ORANGE * 0.62 * g1); bz -= 0.3 * inset
        put(handle, STEEL_D * 1.5 * g1); bz += 0.3 * handle
    cr = is_(M.CRATE)
    if cr.any():
        # the crates' sides: a frame round each face, vertical ribs
        fr = cr & vert & ((phase(x, 1.0, 0.0) < 0.06) & sidey)
        put(fr, OCHRE * 0.7 * g1); bz -= 0.2 * fr
    lmp = is_(M.LAMP_Y, M.LAMP_W)
    if lmp.any():
        emit += (lmp * 0.55)[..., None] * alb
        # a dark rim round the lamp glass
        rim = lmp & ~top
        put(rim, STEEL_D * g1)
    # ------------------------------------------------------------------ the front-left block, the hitch
    flt = is_(M.FLTOP) & top
    if flt.any():
        e = flt & ((np.abs(x - 32.45) < 0.06) | (np.abs(x - 37.55) < 0.06) | (np.abs(y - 19.45) < 0.06) |
                   (np.abs(y - 23.55) < 0.06)) & (x > 32.39) & (x < 37.61) & (y > 19.39) & (y < 23.61)
        put(e, ORANGE * 0.62 * g1); bz -= 0.3 * e
    cpl = is_(M.COUPLING)
    put(cpl & top, STEEL_D * 1.3 * g1)

    # ------------------------------------------------------------------ grime from the ground, the fill light
    low = hm & ~house & ~is_(M.LAMP_Y, M.LAMP_W)
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
    return r.hitmask & g & np.isin(r.comp, M.HOUSE)
