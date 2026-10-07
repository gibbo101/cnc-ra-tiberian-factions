"""Materials for the Upgrade Center: albedo, normal tweaks and glow per pixel of an hd.Render.  House green 0,214,0 x
(1 + 1.1 grain) on the slope (panes, ribs, sill) and the sockets' collars.  Colours read from GTPLUG (TS lit them):
a mid-grey concrete deck on brown feet, an ochre step; a tan block with a striped roof, a bright bevel, the purple band
between grey lines, tan and brown below it; a brown ramp with a rust-red rim, a dark slot down it; light steel pipes
with white caps; grey socket plates with white bolts; blue-grey antennas, the dish's box and the dish.
Overlays (material only):
  slot_t=k   GTPLUG_C: a running light down the slot (white, yellow, orange, red, dark red), frame k
  ant_t=k    GTPLUG_B: the tallest antenna's two lamps blink, frame k"""
import numpy as np
from walls2 import sample, smoothstep, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME
import plug as M, plugs as PG

GREEN = np.array([0, 214, 0.])
CONC = np.array([172, 172, 174.])           # TS's deck 113-137 grey
CONC_D = np.array([150, 150, 152.])
FOOTC = np.array([140, 122, 88.])           # TS 89,80,60 / 97,89,64
STEPC = np.array([196, 162, 100.])          # TS 153,121,56 / 141,121,80 (v2: a plain tan bar; v1 214,170,92 ribbed)
TAN = np.array([196, 156, 90.])             # the roof: TS 133-153, 109-121, 56 (v2 browner; v1 210,174,104)
TAN_D = np.array([158, 120, 70.])           # (v1 176,142,82)
ROOFRED = np.array([150, 104, 68.])         # v2: TS's red-brown streaks along the roof (TS 129,80,64 / 113,76,40)
JOINTC = np.array([34, 38, 34.])            # v2: the dark joints between the slope's panes
HOLEC = np.array([22, 22, 26.])             # v2: the sockets' holes
LIPC = np.array([240, 212, 146.])           # TS 190,165,105 / 206,182,113
BANDC = np.array([106, 106, 198.])          # TS 85,85,157
GREYL = np.array([150, 150, 150.])          # TS 113 grey lines either side of the band
LEDGEC = np.array([196, 166, 106.])         # TS 141,121,80
BROWN = np.array([132, 104, 58.])           # TS 97,76,40 / 85,68,40
RAMPC = np.array([128, 100, 60.])           # TS 85-105, 68-85, 40-44
RIMC = np.array([150, 78, 56.])             # TS's rust-red top edge 105,56,40 / 129,80,64
STEEL = np.array([206, 208, 212.])          # TS's pipes 145-190 grey
CAPC = np.array([246, 246, 236.])
SLOTC = np.array([26, 24, 22.])
PLATEC = np.array([166, 166, 168.])         # TS 113-137
BOLTC = np.array([236, 236, 250.])          # TS 198,198,222
ANTC = np.array([138, 138, 174.])           # TS 76,76,101 / 101,101,125 / 125,125,149 (v2 lighter; v1 112,112,146)
# the plugs
FLANGEC = np.array([156, 156, 158.])        # TS 97-113 grey
PODC = np.array([150, 124, 74.])            # D's casing: TS 113,93,48 / 97,76,40 / 133,109,56
CAPD = np.array([170, 148, 100.])
LAMPBC = np.array([86, 86, 94.])
ANTDC = np.array([218, 172, 84.])           # D's uplink antenna: TS's ochre 141-145, 106-121, 56-64
PIPEC = np.array([150, 152, 172.])
EBODYC = np.array([166, 160, 120.])         # E's shoulder: TS 107,103,78 / 137,137,113 olive-khaki
EBODYD = np.array([130, 122, 88.])
ELOWC = np.array([104, 96, 66.])            # E's dark lower half: TS 61,56,39
ELOWD = np.array([74, 68, 46.])
ESKIRTC = np.array([92, 80, 58.])           # TS 44-60 dark foot
EBANDC = np.array([178, 148, 88.])          # E's band: TS 87,75,46 / 121,105,64 ochre-brown
ESHOULC = np.array([188, 176, 132.])
EWINC = np.array([54, 62, 70.])
SCOPERC = np.array([120, 118, 112.])
GRILLC = np.array([96, 90, 72.])
GRILLD = np.array([36, 34, 30.])
FCOLC = np.array([70, 62, 48.])
EYEOFF = np.array([96, 100, 108.])
FFOOTC = np.array([88, 80, 60.])            # F: TS 44-60 dark foot
FBANDC = np.array([178, 160, 108.])          # F's band: TS 91,82,55 / 113,105,72
FDRUMC = np.array([82, 72, 48.])            # F's drum: TS 47,42,27
FDRUMD = np.array([62, 56, 38.])
FBODYC2 = np.array([102, 90, 58.])          # F's body: TS 59,52,33 / 76,64,40
FBODYD2 = np.array([76, 66, 44.])
FRIBD = np.array([128, 118, 82.])
FRINGC = np.array([40, 36, 28.])
FPLATC = np.array([180, 170, 130.])         # F's platform: TS 107,102,82 / 137,129,89
FPLATD = np.array([142, 132, 100.])
FBODYC = np.array([158, 150, 116.])          # TS 80-105 olive-khaki ribbed body
FBODYD = np.array([126, 118, 90.])
FRIBC = np.array([170, 158, 108.])          # F's ribs: TS 76,69,48 / 113,105,72
FUPPERC = np.array([94, 84, 64.])          # TS 44-60
HEADD = np.array([116, 108, 82.])
DISHG = np.array([196, 198, 200.])
DISHBC = np.array([80, 80, 86.])
FEEDC = np.array([66, 66, 72.])
FLEGC = np.array([120, 112, 80.])           # F's rails: TS 66,63,42 / 105,97,72
FYOKEC = np.array([128, 122, 98.])
FHEADC = np.array([140, 130, 100.])
PODC_D = np.array([118, 100, 66.])
HATCHC = np.array([212, 182, 120.])         # TS 141-145, 121, 80 lit
MACHC = np.array([128, 128, 154.])          # TS 85,85,113 / 97,97,97
DOMEC = np.array([178, 172, 134.])          # E's dome: TS 98,95,71 / 149,149,125
PANTC = np.array([40, 36, 30.])             # E's antennas: TS 32,28,20
EYEHC = np.array([84, 78, 62.])
EYEC = np.array([246, 246, 238.])
TOWERC = np.array([136, 108, 70.])          # F: TS 85-105, 68-85, 40-56
LEGC = np.array([104, 84, 58.])
NECKC = np.array([88, 78, 52.])             # F's neck: TS 55,49,31
HEADC = np.array([150, 126, 86.])
DISHW = np.array([236, 236, 232.])          # TS 190-255
MOUNTC = np.array([146, 146, 176.])         # TS 113,113,137 / 89,89,113
DISHC = np.array([92, 92, 100.])
DIRT = np.array([120, 104, 74.])

# GTPLUG_C: the slot's light, top to bottom per frame (read off TS's frames; see plugovl.py)
SLOT_COLS = {'w': np.array([255, 255, 255.]), 'r': np.array([255, 0, 0.]), 'd': np.array([190, 0, 0.]),
             'o': np.array([255, 125, 0.]), 'yo': np.array([255, 190, 0.]), 'y': np.array([255, 255, 0.])}
# TS's 8 cells down the slot at frame 0; the pattern moves down one cell a frame
SLOT_PATTERN = ('w', 'r', 'd', 'd', 'r', 'o', 'yo', 'y')
# GTPLUG_B: the lamps' level per frame (TS: white with a blue-white glow, flickering, fading through the blues, off)
B_LEVELS = (1.0, 0.8, 1.0, 0.8, 0.55, 0.45, 0.25, 0.0, 0.0, 0.0)
LAMP_ON = np.array([226, 230, 255.])
LAMP_BLUE = np.array([120, 120, 255.])


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


def materials(r, p=None, occ=None, slot_t=None, ant_t=None, level=0, **kw):
    p = M.P if p is None else p
    lay = r.mk.get('layout', 'ts')
    x, y = M.to_local(r.x, r.y, lay)
    z, comp = r.z, r.comp
    nx, ny, nz = r.nx, r.ny, r.nz
    lnx, lny = M.to_local(nx, ny, lay)
    top = nz > 0.75
    fine = sample(NOISE_FINE, np.where(top, x, x + y), np.where(top, y, z))
    mott = sample(NOISE_MOTTLE, np.where(top, x, x + y) * 0.7 + 31, np.where(top, y, z) * 0.7 + 17)
    grain = fine * 0.035 + mott * 0.05
    g1 = (1 + grain)[..., None]
    shape = x.shape
    alb = np.zeros(shape + (3,), np.float32) + 128
    bx = np.zeros(shape, np.float32); by = np.zeros(shape, np.float32); bz = np.zeros(shape, np.float32)
    emit = np.zeros(shape + (3,), np.float32)
    house = GREEN * (1 + 1.1 * grain)[..., None]
    grime = smoothstep(0.15, 1.3, sample(NOISE_GRIME, x * 0.7 + 7, (y + z) * 0.7 + 3))
    low = smoothstep(30.0, 2.0, z)
    d = p['deck']; b = p['block']
    g = dict(M.DONE); g.update(r.mk.get('prog') or {})

    def put(mask, col):
        nonlocal alb
        alb = np.where(mask[..., None], col, alb)

    # ---- the deck: concrete, slab joints on its top, its sides a little darker; feet; the ochre step
    pl = comp == M.PLAT
    joint = (phase(x + 3.0, 64.0, 0.0) < 1.1) | (phase(y - 20.0, 64.0, 0.0) < 1.1)
    dcol = mix(CONC * g1, CONC_D * g1, 0.35 * grime)
    put(pl, np.where((joint & top)[..., None], CONC_D * 0.86 * g1, dcol))
    bz -= 0.2 * (joint & top & pl)
    # the build-up: painted outlines on the deck where the block and the sockets go (GTPLUGMK 04-11)
    if g['marks'] > 0:
        sl_ = p['slope']
        bx0, bx1, by0, by1 = b['x_low'], b['x_roof'][1], b['yn'], sl_['foot']
        dr = np.minimum(np.minimum(np.abs(x - bx0), np.abs(x - bx1)), np.minimum(np.abs(y - by0), np.abs(y - by1)))
        inrect = (x > bx0 - 2) & (x < bx1 + 2) & (y > by0 - 2) & (y < by1 + 2)
        line = inrect & (dr < 1.8)
        for (cx, cy) in p['sockets']['c']:
            line |= np.abs(np.hypot(x - cx, y - cy) - (p['sockets']['r_out'] + 4.0)) < 1.6
        mk = line & pl & top
        put(mk, CONC_D * 0.62 * g1)
    put(comp == M.FOOT, mix(FOOTC * g1, DIRT * g1, 0.4 * low))
    stp = comp == M.STEP
    groove = phase(x - p['step']['x'][0], (p['step']['x'][1] - p['step']['x'][0]) / p['step']['n'], 0.0) < 1.6
    put(stp, mix(STEPC * g1, DIRT * g1, 0.3 * grime))          # v2: plain (v1 had grooves across it)
    # ---- the block: the roof (stripes along it), the bevel, the band face (band between grey lines, tan, brown)
    roof = (comp == M.BLOCK) | (comp == M.RIDGE)
    yy = (y - b['yn']) / (b['lip'][0] - b['yn'])             # 0 at the north edge, 1 at the bevel
    stripe = smoothstep(0.30, 0.40, yy) * (1 - smoothstep(0.78, 0.86, yy))
    rcol = mix(TAN_D * g1, TAN * g1, 0.45 + 0.55 * stripe)
    # v2: red-brown streaks running along the roof (TS's roof is streaky)
    rstreak = smoothstep(0.35, 0.85, sample(NOISE_MOTTLE, x * 0.05 + 3.0, y * 0.85 + 11.0))
    rcol = mix(rcol, ROOFRED * g1, 0.42 * rstreak)
    # the rust-red rim along the north edge
    rcol = np.where((y < b['yn'] + 2.5)[..., None], RIMC * g1, rcol)
    put(roof, mix(rcol, DIRT * g1, 0.25 * grime))
    put(comp == M.LIP, LIPC * g1)
    fc = comp == M.FACE
    bnd = (z >= b['band'][0]) & (z <= b['band'][1] - 0.6)
    gl = ((z > b['band'][1] - 0.6) | ((z < b['band'][0]) & (z >= b['band'][0] - 2.6)))
    fcol = np.where(bnd[..., None], BANDC * g1, np.where(gl[..., None], GREYL * g1, LEDGEC * g1))
    put(fc, fcol)
    put(comp == M.LEDGE, LEDGEC * g1)
    put(comp == M.FRONT, BROWN * g1)
    # v2: TS's band turns the block's south-east corner and runs north along its east face (until the ramp covers it);
    # the east face brown above and below it, as TS's (v1 left the east face plain tan)
    xe_ = b['x_roof'][1]
    east = (np.abs(x - xe_) < 1.4) & (lnx > 0.6) & (y < b['lip'][1] + 0.6) & (y > b['yn']) & (z < b['z'] - 0.8) & \
        np.isin(comp, [M.BLOCK, M.LIP, M.LEDGE, M.FACE, M.FRONT, M.RIDGE])
    gl_e = ((z > b['band'][1] - 0.6) & (z <= b['band'][1] + 1.8)) | ((z < b['band'][0]) & (z >= b['band'][0] - 2.6))
    ecol = np.where(bnd[..., None], BANDC * g1, np.where(gl_e[..., None], GREYL * g1,
                    np.where((z > b['band'][1])[..., None], RAMPC * 1.12 * g1, BROWN * g1)))
    put(east, ecol)
    # ---- the slope: house green, nothing else on it (the build-up: bare light frames, then grey panes, then green)
    put(comp == M.SOCK, house)
    sp = (comp == M.PANEL) | (comp == M.PFRAME)
    if g['paint'] >= 1:
        put(sp, house)
    elif g['paint'] >= 0.5:
        put(comp == M.PANEL, np.array([110, 110, 108.]) * g1)
        put(comp == M.PFRAME, np.array([168, 166, 136.]) * g1)
    else:
        put(comp == M.PANEL, np.array([196, 194, 168.]) * g1)
        put(comp == M.PFRAME, np.array([222, 220, 196.]) * g1)
    # ---- the ramp: brown with darker streaks down it, the rim rust-red, the slot dark
    rp = comp == M.RAMP
    streak = sample(NOISE_MOTTLE, (x + y) * 0.9 + 5, z * 0.25 + 9)
    rcol = mix(RAMPC * g1, RAMPC * 0.72 * g1, smoothstep(0.1, 0.9, streak) * 0.6)
    u, v, zr = M.ramp_uv(x, y, p['ramp'])
    if p.get('endwall'):
        # v4: the hip's top edge (where it meets the roof) and the end wall's top edge rust-red
        ew_ = p['endwall']
        rim = rp & (((np.abs(x - ew_['x0']) < 2.0) & (z > p['block']['z'] - 4.0)) |
                    ((np.abs(x - ew_['xw']) < 1.6) & (np.abs(z - ew_['zw']) < 1.8)))
        bw_ = ew_.get('back')
        if bw_:                             # v5: and the wedge's falling top edge (TS's rust-red rim down to the deck)
            zbk_ = d['zt'] + (ew_['zw'] - d['zt']) * np.clip((y - bw_['y0']) / (b['yn'] - bw_['y0']), 0, 1)
            rim |= rp & (np.abs(x - ew_['xw']) < 1.6) & (y < b['yn'] + 0.5) & (np.abs(z - zbk_) < 2.2)
        hw_ = b.get('hipw')
        if hw_:                             # v6: the west hip's edges rust-red as the east one's
            rim |= rp & (((np.abs(x - hw_['x0']) < 2.0) & (z > b['z'] - 4.0)) |
                         ((np.abs(x - hw_['x1']) < 1.6) & (np.abs(z - hw_['zw']) < 1.8)))
        # v5: TS's purple band turns the south-east corner onto the end wall and runs north to the lamp column
        ewall = (np.abs(x - ew_['xw']) < 1.4) & (lnx > 0.6) & (y < b['lip'][1] + 0.6) & \
            (y > ew_['light']['c'][1] + ew_['light']['r'] + 3.0) & (z > b['band'][0] - 2.6) & (z <= b['band'][1] + 1.8) & \
            ~np.isin(comp, [M.PIPE, M.PCAP])
        bnd_e = (z >= b['band'][0]) & (z <= b['band'][1] - 0.6)
        put(ewall, np.where(bnd_e[..., None], BANDC * g1, GREYL * g1))
        rp = rp & ~ewall
        rim &= ~ewall
    else:
        rim = rp & (u < 0.035) & (z > d['zt'] + 2)
    put(rp, mix(rcol, DIRT * g1, 0.3 * low))
    put(rim, RIMC * g1)
    slot = np.zeros(shape, bool)
    sl = r.field('slot', None) if False else None
    e0, e1 = M.slot_ends(p)
    e0 = np.array(e0); e1 = np.array(e1)
    dvec = e1 - e0; L = np.linalg.norm(dvec); dvec = dvec / L
    rel = np.stack([x - e0[0], y - e0[1], z - e0[2]], -1)
    t = rel @ dvec
    dist = np.linalg.norm(rel - t[..., None] * dvec, axis=-1)
    slot = rp & (t >= 0) & (t <= L) & (dist < p['slot']['w'] * 1.8)
    put(slot, SLOTC * g1)
    bz -= 0.0
    # ---- pipes, caps
    put(comp == M.PIPE, mix(STEEL * g1, DIRT * g1, 0.35 * low))
    put(comp == M.PCAP, CAPC * g1)
    # ---- sockets: grey plates, white bolts
    put(comp == M.PLATE, PLATEC * g1)
    put(comp == M.BOLT, BOLTC * g1)
    put(comp == M.HOLE, HOLEC * g1)
    put(comp == M.JOINT, JOINTC * g1)
    # ---- the roof's kit; the tallest antenna's lamps (GTPLUG_B frame ant_t lights them)
    put(comp == M.ANT, ANTC * g1)
    lamp = comp == M.LAMP
    put(lamp, ANTC * 1.15 * g1)
    if ant_t is not None:
        lv = B_LEVELS[int(ant_t) % 10]
        if lv > 0:
            col = LAMP_BLUE * (1 - lv) + LAMP_ON * lv
            alb = np.where(lamp[..., None], col * 0.7, alb)
            emit = np.where(lamp[..., None], col * (0.25 + 0.75 * lv), emit)
    put(comp == M.DMOUNT, MOUNTC * g1)
    put(comp == M.DISH, DISHC * g1)
    if p.get('endwall'):
        # v5: the solid core's faces under the deck (where the gap under its edge shows them) are the deck's concrete
        # in its shade, never the colour of the part on top (v4 showed green under the slope's east end)
        und = (z < d['zb'] - 0.5) & ~np.isin(comp, [M.FOOT, M.DEBRIS, M.DEB_IN, M.DEB_BURNT])
        put(und, CONC_D * 0.8 * g1)

    # ---- the plugs (TS's GTPLUG_D/E/F colours, redrawn)
    put(comp == PG.PG_FLANGE, FLANGEC * g1)
    plug_t = r.mk.get('plug_t', 0.0)
    pturn = PG.view_turn(lay, M.to_local)
    pnx, pny = PG.plug_frame(lnx, lny, pturn)
    for (cx, cy), kind in zip(p['sockets']['c'], r.mk.get('plugs', (None, None))):
        if not kind:
            continue
        u_, v_ = PG.plug_frame(x - cx, y - cy, pturn)
        w_ = z - p['sockets']['plate']
        rr_ = np.hypot(u_, v_)
        near = rr_ < 70.0
        a_, b_ = PG.ab(u_, v_)
        mott = smoothstep(0.2, 1.0, sample(NOISE_MOTTLE, (u_ + v_) * 1.6 + 11, w_ * 1.6 + 3))
        if kind == 'D':
            q = PG.Q['D']
            pb = near & (comp == PG.PG_BODY)
            hu, hv = q['half']
            # the casing: olive-brown armour, panel seams (a band round it, the chamfers' edges), a darker skirt
            seam = (np.abs(w_ - 36.0) < 0.9) | (~top & (np.abs(np.abs(u_) + np.abs(v_) - (hu + hv - q['cham'])) < 1.2)) | \
                (~top & (w_ > 56.0) & (np.abs(w_ - 58.0) < 0.9))
            cas = mix(PODC * g1, PODC_D * g1, 0.45 * mott)
            cas = np.where((w_ < 8.0)[..., None], PODC_D * 0.8 * g1, cas)
            cas = np.where(seam[..., None], PODC_D * 0.62 * g1, cas)
            # a hatch on the east face (towards the camera's right): its frame, a handle
            eface = ~top & (pnx > 0.7)
            hat = eface & (np.abs(v_ - 4.0) <= 11.0) & (w_ >= 10.0) & (w_ <= 52.0)
            hat_in = eface & (np.abs(v_ - 4.0) <= 9.0) & (w_ >= 12.0) & (w_ <= 50.0)
            cas = np.where((hat & ~hat_in)[..., None], PODC_D * 0.55 * g1, cas)
            handle = eface & (np.abs(v_ + 1.0) <= 1.0) & (np.abs(w_ - 31.0) <= 5.0)
            cas = np.where(handle[..., None], CAPD * 1.1 * g1, cas)
            # rivets along the band seam
            riv = ~top & (np.abs(w_ - 39.0) < 1.0) & (phase(u_ + v_, 6.0, 0.0) < 1.2)
            cas = np.where(riv[..., None], CAPD * 1.05 * g1, cas)
            put(pb, cas)
            put(near & (comp == PG.PG_CAP), CAPD * g1)
            put(near & (comp == PG.PG_LAMPB), LAMPBC * g1)
            lm = near & (comp == PG.PG_LAMP)
            put(lm, CAPC * g1)
            emit = np.where(lm[..., None], np.array([150, 150, 140.]), emit)
            put(near & (comp == PG.PG_HATCH), ANTDC * g1 * np.where((nz > 0.2)[..., None], 1.0, 0.75))
            mch = near & (comp == PG.PG_MACH)
            put(mch, MACHC * g1 * (1 - 0.3 * (~top & (phase(u_, 5.0, 0.0) < 1.2)))[..., None])
            put(near & (comp == PG.PG_PIPE), PIPEC * g1 * (1 - 0.2 * (phase(u_, 9.0, 0.0) < 1.2))[..., None])
            put(near & (comp == PG.PG_GREEN), house)
        elif kind == 'E':
            q = PG.Q['E']
            turn, blink = PG.e_turn(plug_t)
            pb = near & (comp == PG.PG_EBODY)
            gs = (1 + 0.45 * grain)[..., None]                  # a smoother metal finish than the concrete's grain
            ang = np.arctan2(v_, u_) - np.radians(turn)
            lower = w_ < q['lower']
            band = (w_ >= q['band'][0]) & (w_ <= q['band'][1])
            col = mix(EBODYC * gs, EBODYD * gs, 0.18 * mott)                 # the khaki shoulder
            col = np.where(lower[..., None], mix(ELOWC * gs, ELOWD * gs, 0.25 * mott), col)
            col = np.where(band[..., None], mix(EBANDC * gs, EBANDC * 0.8 * gs, 0.25 * mott), col)
            # seams: the band's edges and a line round the shoulder; panel seams every 30 degrees on the lower half and
            # every 45 on the shoulder
            ring = (np.abs(w_ - q['band'][0]) < 0.7) | (np.abs(w_ - q['band'][1]) < 0.7) | (np.abs(w_ - 52.0) < 0.6)
            col = np.where(ring[..., None], ELOWD * 0.8 * gs, col)
            seam = (lower & (phase(ang * rr_, np.pi / 6.0 * rr_ + 1e-6, 0.0) < 0.9)) | \
                ((w_ > q['band'][1] + 1.0) & (w_ < 60.0) & (phase(ang * rr_, np.pi / 4.0 * rr_ + 1e-6, 0.0) < 0.7))
            col = np.where(seam[..., None], col * 0.72, col)
            put(pb, col)
            put(near & (comp == PG.PG_DOME), mix(DOMEC * gs, EBODYD * gs, 0.15 * mott))
            put(near & (comp == PG.PG_ANT), PANTC * gs)
            put(near & (comp == PG.PG_EYEH), EYEHC * gs)
            put(near & (comp == PG.PG_MACH), SCOPERC * gs)
            em = near & (comp == PG.PG_EYE)
            # the lit glass mostly glows (so the light's angle on the small disc doesn't streak it)
            put(em, mix(EYEOFF * 0.4, EYEC * 0.2, blink) * gs)
            emit = np.where(em[..., None], mix(EYEOFF * 0.35, EYEC * 0.8, blink), emit)
            put(near & (comp == PG.PG_EPLATE), mix(EBANDC * gs, EBODYD * gs, 0.3 * mott))
            gm = near & (comp == PG.PG_DARK)
            # the grille: slots across the muff's face
            a2 = np.radians(q['scope']['base'] + turn)
            fwd = np.cos(a2) * u_ + np.sin(a2) * v_
            put(gm, np.where((phase(fwd + 0.0 * w_, 2.4, 0.0) < 1.1)[..., None], GRILLD * gs, GRILLC * gs))
        elif kind == 'F':
            q = PG.Q['F']
            # the plinth (dark), the platform (a tan rim, its floor a little darker), the railings (khaki posts, olive
            # rails), the slim pole (dark brown, faint courses), black rings
            put(near & (comp == PG.PG_TOWER), mix(FDRUMC * g1, FDRUMD * g1, 0.3 * mott))
            dkm = near & (comp == PG.PG_FBAND)
            put(dkm, np.where(top[..., None], mix(FBODYC2 * g1, FBODYD2 * g1, 0.35 * mott), FBANDC * g1))
            put(near & (comp == PG.PG_RIB), mix(FRIBC * g1, FRIBD * g1, 0.35 * mott))
            put(near & (comp == PG.PG_LEG), FLEGC * g1)
            course = (phase(w_, 9.0, 3.0) < 0.5) & ~top
            put(near & (comp == PG.PG_NECK), np.where(course[..., None], NECKC * 0.8 * g1, mix(NECKC * g1, FBODYC2 * g1, 0.3 * mott)))
            put(near & (comp == PG.PG_DARK), FRINGC * g1)
            pfm = near & (comp == PG.PG_FPLAT)
            put(pfm, mix(FPLATC * g1, FPLATD * g1, 0.3 * mott) * (1 - 0.25 * (np.abs(rr_ - q['yoke']['r'] + 3.0) < 0.6))[..., None])
            hdm = near & (comp == PG.PG_HEAD)
            hs = (phase(w_, 9.0, 2.0) < 0.8) & ~top
            put(hdm, mix(FHEADC * g1, HEADD * g1, 0.4 * mott) * (1 - 0.25 * hs)[..., None])
            # the dish's face: white panels in a grid
            C, n, acr, up = PG.f_dish(plug_t)
            rel = np.stack([u_ - C[0], v_ - C[1], w_ - C[2]], -1)
            s1 = rel @ acr; s2 = rel @ up
            grid = (phase(s1 + 24.5, 12.25, 0.0) < 0.45) | (phase(s2 + 17.5, 11.67, 0.0) < 0.45)
            dm = near & (comp == PG.PG_DISH)
            put(dm, np.where(grid[..., None], DISHG * g1, DISHW * g1))
            put(near & (comp == PG.PG_DISHB), DISHBC * g1)
            put(near & (comp == PG.PG_FEED), FEEDC * g1)

    # ---- GTPLUG_C: the slot's running light (frame slot_t)
    if slot_t is not None and level == 0:
        cols = slot_colours(slot_t)
        if cols is not None:
            k = np.clip((t / L * len(cols)).astype(int), 0, len(cols) - 1)
            for i, c in enumerate(cols):
                if c is None:
                    continue
                m = slot & (k == i)
                alb = np.where(m[..., None], SLOT_COLS[c] * 0.5, alb)
                emit = np.where(m[..., None], SLOT_COLS[c] * 0.75, emit)
    return alb, (bx, by, bz), emit


def slot_colours(t):
    """GTPLUG_C frame t (0-7): the slot's eight cells, top to bottom."""
    t = int(t) % 8
    return [SLOT_PATTERN[(k - t) % 8] for k in range(8)]


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, list(M.HOUSE) + [43])
