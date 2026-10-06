"""Materials for the Barracks: albedo, bump and glow per pixel of an hd.Render.  Colours follow the tower, the
yard and the power plant (house green 0,214,0 x (1 + 1.1 grain) on every house part; concrete 218,212,194;
sandstone like the plant's mounds; the red-brown of the plant's turbine frames)."""
import numpy as np
import walls2 as W
from walls2 import sample, smoothstep, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME
import pile as PL

GREEN = np.array([0, 214, 0.])
CONC = np.array([218, 212, 194.])
SAND = np.array([196, 170, 118.])
ROOF_C = np.array([210, 186, 134.])
BAND_C = np.array([128, 58, 40.])
STEEL = np.array([150, 152, 160.])
STEEL_D = np.array([82, 82, 88.])
DARK = np.array([30, 30, 34.])
LENS_OFF = np.array([176, 176, 168.])


EAGLE_R = 0.37   # the emblem's outer radius, in flag heights


def _eagle(eu, ev):
    """The emblem's coverage (0..1) at flag coordinates (eu, ev), sampled bilinearly from gdi_eagle.png."""
    from PIL import Image
    import os
    if not hasattr(_eagle, 'img'):
        here = os.path.dirname(os.path.abspath(__file__))
        _eagle.img = np.asarray(Image.open(os.path.join(here, 'gdi_eagle.png')).convert('L'), np.float32) / 255
    img = _eagle.img
    n = img.shape[0]
    sx = (eu / EAGLE_R * 0.5 + 0.5) * (n - 1)
    sy = (ev / EAGLE_R * 0.5 + 0.5) * (n - 1)
    inside = (sx >= 0) & (sx <= n - 1) & (sy >= 0) & (sy <= n - 1)
    x0 = np.clip(np.floor(sx).astype(int), 0, n - 2)
    y0 = np.clip(np.floor(sy).astype(int), 0, n - 2)
    fx, fy = np.clip(sx - x0, 0, 1), np.clip(sy - y0, 0, 1)
    v = (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x0 + 1] * fx * (1 - fy)
         + img[y0 + 1, x0] * (1 - fx) * fy + img[y0 + 1, x0 + 1] * fx * fy)
    return np.where(inside, v, 0.0)


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


def bunker_of(y, p=PL.P):
    """'n' or 's': the bunker a point belongs to (split in the middle of the yard)."""
    b = p['bunkers']
    mid = (b['n']['y1'] + b['s']['y0']) / 2
    return np.where(y < mid, 'n', 's')


def face_coords(x, y, z, p=PL.P):
    """for points on a bunker's slopes: the side it faces ('n','s','e','w') and the coordinate along it."""
    key = bunker_of(y, p)
    side = np.full(x.shape, 'n', '<U1')
    for k in ('n', 's'):
        m = key == k
        side = np.where(m, PL.face_of(x, y, p['bunkers'][k]), side)
    along = np.where((side == 'n') | (side == 's'), x, y)
    return key, side, along


def hatch_mask(key, side, along, z, p=PL.P):
    m = np.zeros(z.shape, bool)
    frame = np.zeros(z.shape, bool)
    for (bk, sd, a0, a1, z0, z1) in p['hatches']:
        on = (key == bk) & (side == sd) & (along >= a0) & (along <= a1) & (z >= z0) & (z <= z1)
        m |= on
        frame |= on & ((along - a0 < 1.3) | (a1 - along < 1.3) | (z - z0 < 1.3) | (z1 - z < 1.3))
    return m, frame


def materials(r, p=PL.P, occ=None, lights=None, beacon=None, flag_t=None):
    """lights: (a, b) levels 0..1 of the entrance's two lamps (GTPILE_A); beacon: RGB of the mast's beacon
    (GTPILE_B) or None.  Returns albedo, (dnx, dny, dnz) bump, emissive colour."""
    x, y, z, comp = r.x, r.y, r.z, r.comp
    nx, ny, nz = r.nx, r.ny, r.nz
    top = nz > 0.75
    fine = sample(NOISE_FINE, np.where(top, x, x + y), np.where(top, y, z))
    mott = sample(NOISE_MOTTLE, np.where(top, x, x + y) * 0.7 + 31, np.where(top, y, z) * 0.7 + 17)
    grain = fine * 0.035 + mott * 0.05
    g1 = (1 + grain)[..., None]
    shape = x.shape
    alb = np.zeros(shape + (3,), np.float32)
    bx = np.zeros(shape, np.float32); by = np.zeros(shape, np.float32); bz = np.zeros(shape, np.float32)
    emit = np.zeros(shape + (3,), np.float32)

    def put(mask, col):
        nonlocal alb
        alb = np.where(mask[..., None], col, alb)

    house = GREEN * (1 + 1.1 * grain)[..., None]

    # ---------------------------------------------------------------- pad: light concrete, joints, sandy stains
    slab = comp == PL.SLAB
    joint = (phase(x, 32.0, 0.0) < 0.45) | (phase(y, 32.0, 0.0) < 0.45)
    stain = smoothstep(0.5, 1.5, sample(NOISE_GRIME, x * 0.45 + 40, y * 0.45)) * 0.35
    sc = CONC * 0.93 * g1 * (1 - 0.1 * joint)[..., None]
    sc = mix(sc, np.array([176, 156, 112.]), stain)
    put(slab, sc)

    # ---------------------------------------------------------------- the bunkers' slopes
    berm = comp == PL.BERM
    key, side, along = face_coords(x, y, z, p)
    z0b, z1b = p['band']
    band = berm & (z <= z0b + 1.5)                                   # a dark foot
    pz0, pz1 = p['panels']
    dd = p['door']
    in_porch = (x > dd['x0'] - dd['wall_t'] - 0.5) & (x < dd['x1'] + dd['wall_t'] + 0.5) & (y > dd['y_door'] - 1.6)
    panel = berm & (z >= pz0) & (z <= pz1) & ((side == 'n') | (side == 's')) & (phase(along, 44.0, 5.0) < 30.0) & ~in_porch
    panel |= berm & (side == 'e') & (np.abs(along - np.round(along / 26.0) * 26.0) < 2.0) & (z > z0b + 1.5)
    # sandstone blocks in courses above the plinth
    course = np.floor((z - z0b) / 5.5)
    bj = phase(along + 7.0 * (course % 2), 15.0, 0.0) < 0.6
    cj = phase(z - z0b, 5.5, 0.0) < 0.55
    blk = sample(NOISE_MOTTLE, along * 0.3 + course * 7.1, z * 0.3) * 0.09
    bc = SAND * g1 * (1 + blk)[..., None] * (1 - 0.22 * (bj | cj))[..., None]
    grime = smoothstep(0.4, 1.3, sample(NOISE_GRIME, along * 0.35 + 9, z * 0.5)) * 0.3
    bc = mix(bc, np.array([128, 108, 72.]), grime)
    put(berm & ~band, bc)
    bb = (berm & ~band).astype(np.float32)
    bz += 0.3 * ((bj | cj).astype(np.float32) - 0.2) * bb
    # red-brown corrugated panels part-way up the long faces, strips between the east ends' hatches; a dark foot
    rib = np.sin(along * 2 * np.pi / 3.0)
    # v2 (Luke): the panels in house green (they were red-brown), seams between them and along their edges; red-brown
    # only while they go in (the build-up: they turn green with the hatches, as TS's hatches do)
    pseam = (phase(along, 24.0, 0.0) < 0.7) | (np.abs(z - pz0) < 0.7) | (np.abs(z - pz1) < 0.7)
    pc_red = BAND_C * g1 * (1 + 0.08 * rib)[..., None] * (1 - 0.3 * pseam)[..., None]
    pc = mix(pc_red, house * (1 - 0.28 * pseam)[..., None], r.field('hatches', 1.0))
    put(panel, pc)
    put(band, np.array([104, 90, 64.]) * g1)
    bands = panel.astype(np.float32)
    ta = np.where((side == 'n') | (side == 's'), 1.0, 0.0)
    bx += 0.25 * rib * ta * bands; by += 0.25 * rib * (1 - ta) * bands
    # green hatches in the slopes (house colour; louvred on the east ends)
    hm, hf = hatch_mask(key, side, along, z, p)
    hm &= berm & ~in_porch
    louvre = (side == 'e') & (phase(z, 3.0, 0.0) < 0.9)
    hc = house * (1 - 0.28 * (hf | louvre))[..., None]
    # build-up: the hatches go in red-brown and turn green last (TS's GTPILEMK)
    hz = r.field('hatches', 1.0)
    hc = mix(BAND_C * g1 * (1 - 0.28 * (hf | louvre))[..., None], hc, hz)
    put(hm, hc)

    # ---------------------------------------------------------------- the entrance
    d = p['door']
    wt = d['wall_t']
    # the doorway: dark, in the face at the back of the porch, under the roof's edge, a steel frame round it
    back = berm & (np.abs(y - d['y_door']) < 1.6) & (x > d['x0'] - 0.5) & (x < d['x1'] + 0.5)
    door = back & (x >= d['dx0']) & (x <= d['dx1']) & (z >= d['sill'] - 0.5) & (z <= d['dz'])
    dframe = back & (x >= d['dx0'] - 2.2) & (x <= d['dx1'] + 2.2) & (z <= d['dz'] + 2.2) & ~door
    put(back, np.array([150, 132, 92.]) * g1 * (1 - 0.18 * (phase(z, 5.5, 0.0) < 0.55))[..., None])
    put(dframe, STEEL_D * g1)
    put(door, DARK * g1)
    # the steps: pale concrete treads, darker risers
    st = comp == PL.STEP
    put(st, np.where(top[..., None], np.array([204, 198, 182.]) * g1, np.array([140, 134, 120.]) * g1))
    # the walls: sand blocks, a capping course; the east wall's coping house green (TS's green bar)
    pw = comp == PL.PORCH
    tw = np.clip((y - d['y_top0']) / (d['y_end'] - d['y_top0']), 0, 1)
    wtop = d['top0'] + (d['top1'] - d['top0']) * tw
    east = x >= d['x1'] - 0.5
    cap = pw & (top | (z >= wtop - d['coping']))
    wcourse = np.floor(z / 5.0)
    wj = (phase(y + 6.0 * (wcourse % 2), 12.0, 0.0) < 0.6) | (phase(z, 5.0, 0.0) < 0.55)
    put(pw, SAND * g1 * (1 - 0.2 * wj)[..., None])
    put(cap & ~east, np.array([176, 152, 104.]) * g1)
    hz_ = r.field('hatches', 1.0)
    put(cap & east, mix(BAND_C * g1, house * np.where(top, 1.0, 0.82)[..., None], hz_))
    # GTPILE_A's lamps: small steel housings on the walls' upper ends, the lens on the south face
    lamp_px = np.zeros(shape, int) - 1
    el = comp == PL.ELAMP
    put(el, STEEL_D * g1)
    for i, (lx, ly, lz) in enumerate(p['lamps']):
        lens = el & (ny > 0.6) & (np.hypot(x - lx, z - lz) <= 1.9)
        put(lens, LENS_OFF)
        lamp_px = np.where(lens, i, lamp_px)
        if lights is not None and lights[i] > 0:
            emit = np.where(lens[..., None], np.array([255, 255, 255.]) * lights[i], emit)
    r.lamp_px = lamp_px

    # ---------------------------------------------------------------- roofs: sandstone slabs, seams, dark fascia
    roof = comp == PL.ROOF
    rseam = (phase(x, 30.0, 0.0) < 0.6) | (phase(y, 30.0, 11.0) < 0.5)
    rspot = smoothstep(0.55, 1.4, sample(NOISE_GRIME, x * 0.5 + 70, y * 0.5 + 3)) * 0.25
    rc = ROOF_C * g1 * (1 - 0.14 * rseam)[..., None]
    rc = mix(rc, np.array([150, 130, 90.]), rspot)
    put(roof & top, rc)
    put(roof & ~top, np.array([132, 112, 78.]) * g1)
    bz += 0.3 * (rseam.astype(np.float32) - 0.2) * (roof & top)

    # ---------------------------------------------------------------- the spine: dark deck, two green hatches
    sp = comp == PL.SPINE
    if sp.any() and p.get('spine'):                          # v1 only: v2's yard is empty
        spt = sp & top
        s = p['spine']
        sh = spt & (((x >= s['x0'] + 6) & (x <= -6)) | ((x >= 6) & (x <= s['x1'] - 6))) & (np.abs(y - (s['y0'] + s['y1']) / 2) <= 14)
        shf = sh & ((phase(x, 8.0, 0.0) < 0.9) | (np.abs(np.abs(y - (s['y0'] + s['y1']) / 2) - 14) < 1.2))
        put(spt, np.array([122, 116, 102.]) * g1 * (1 - 0.15 * (phase(x + y, 12.0, 0.0) < 0.7))[..., None])
        put(sh, mix(BAND_C * g1, house * (1 - 0.28 * shf)[..., None], r.field('hatches', 1.0)))
        put(sp & ~top, BAND_C * g1 * (1 + 0.08 * np.sin(np.where(np.abs(nx) > np.abs(ny), y, x) * 2 * np.pi / 3.0))[..., None])

    # ---------------------------------------------------------------- v2: the corridors (TS's grey tubes)
    co = comp == PL.CORR
    if co.any():
        cd = p['corridors']
        xm_ = np.zeros(shape, np.float32); hw_ = np.ones(shape, np.float32); zc_ = np.zeros(shape, np.float32)
        for (cx0, cx1, zc, crown) in cd['tubes']:
            on = (x >= cx0 - 2) & (x <= cx1 + 2)
            xm_ = np.where(on, (cx0 + cx1) / 2.0, xm_); hw_ = np.where(on, (cx1 - cx0) / 2.0, hw_)
            zc_ = np.where(on, zc, zc_)
        roofm = co & (z >= zc_ - 0.4)
        wall = co & ~roofm
        # the roof: steel, ribbed round the tube every 6 units (a Quonset's), a seam along the eaves
        rib = (phase(y, 6.0, 0.0) < 0.55)
        eave = z < zc_ + 0.6
        put(roofm, np.array([134, 136, 144.]) * g1 * (1 - 0.07 * rib - 0.18 * eave)[..., None])
        by += 0.18 * (rib.astype(np.float32) - 0.3) * roofm
        # the walls: darker panels with a row of dark windows; a plinth
        wp = phase(y, 12.0, 0.0) < 0.6
        put(wall, np.array([118, 120, 128.]) * g1 * (1 - 0.18 * wp)[..., None])
        win = wall & (z >= zc_ - 13.0) & (z <= zc_ - 5.0) & (phase(y, 12.0, 4.0) < 6.5)
        put(win, DARK * g1)
        put(wall & (z < p['slab_h'] + 3.0), STEEL_D * g1)

    # ---------------------------------------------------------------- machinery
    vent = comp == PL.VENT
    louv = ~top & (phase(z, 2.5, 0.0) < 0.8)
    vseam = top & ((phase(x, 10.0, 0.0) < 0.5) | (phase(y, 10.0, 0.0) < 0.5))
    put(vent, STEEL * g1 * (1 - 0.3 * louv - 0.15 * vseam)[..., None])
    fan = comp == PL.FAN
    fx, fy, fr = p['ahu']['fan']
    fa = np.arctan2(y - fy, x - fx)
    blades = phase(fa * 6 / (2 * np.pi), 1.0, 0.0) < 0.45
    fd = np.hypot(x - fx, y - fy)
    fc = np.where(blades[..., None], np.array([96, 96, 100.]), np.array([34, 34, 38.])) * g1
    fc = np.where((fd > fr - 1.4)[..., None], STEEL_D * g1, fc)
    fc = np.where((fd < 2.0)[..., None], STEEL_D * g1, fc)
    put(fan, fc)
    duct = comp == PL.DUCT
    dband = phase(z, 9.0, 0.0) < 0.9
    put(duct, np.array([140, 142, 150.]) * g1 * (1 - 0.2 * dband)[..., None])
    put(comp == PL.GRILLE, DARK * g1)

    # ---------------------------------------------------------------- masts, lamps, pole
    put(comp == PL.MAST, np.array([74, 74, 80.]) * g1)
    lampc = comp == PL.LAMP
    put(lampc, np.array([188, 188, 194.]) * g1)
    bm = p['masts'][p['beacon']]
    beac = lampc & (np.hypot(x - bm[0], y - bm[1]) <= 3.4) & top            # the lens on top of the mast's lamp
    put(beac, np.array([150, 150, 150.]))
    r.beacon_px = beac
    if beacon is not None:
        alb = np.where(beac[..., None], np.array([30, 30, 30.]), alb)
        emit = np.where(beac[..., None], np.array(beacon, np.float32), emit)
    pole = comp == PL.POLE
    put(pole, np.where((z < p['slab_h'] + 3.5)[..., None], np.array([150, 148, 140.]) * g1, np.array([70, 70, 66.]) * g1))

    # ---------------------------------------------------------------- the flag (GTPILE_C): green, a dark emblem
    fl = comp == PL.FLAG
    if fl.any():
        f = p['flag']
        u = r.field('flag_u')
        top_z = p['pole'][3] - 2.0 - 3.0 * np.clip(u, 0, 1) ** 1.5
        v = (top_z - z) / f['h']
        eu = (u - 0.47) * f['len'] / f['h']
        ev = v - 0.5
        # TS GDI's eagle in its ring, stencilled from the faction emblem (gdi_eagle.png: white = emblem)
        emb = _eagle(eu, ev)
        fc = house * (1 - 0.55 * emb)[..., None]
        fc = mix(fc, np.array([10, 60, 10.]), np.asarray(emb, np.float32) * 0.6)
        hem = (v < 0.03) | (v > 0.97)
        fc = fc * (1 - 0.2 * hem)[..., None]
        put(fl, fc)

    # build-up: the bunkers go up in bare grey block before they are faced (TS's GTPILEMK)
    paint = r.field('paint', 1.0)
    bare = np.isin(comp, [PL.BERM, PL.ROOF, PL.SPINE, PL.STEP, PL.PORCH, PL.CORR]) & (paint < 1.0)
    if bare.any():
        lum = (alb * np.array([0.3, 0.59, 0.11])).sum(axis=2, keepdims=True)
        grey = lum * 0.8 + np.array([46, 46, 48.]) * 0.4
        # house-coloured parts switch at once (grey until the facing is done, then house green): no half-grey green
        hpx = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
        t = np.where(hpx, (paint >= 1.0).astype(np.float32), paint)
        alb = np.where(bare[..., None], mix(grey, alb, t), alb)
    # the house-painted pixels (hatches, panels, the coping, the corridors' roofs, the flag): the damage keeps soot,
    # dust and cracks off them
    r.house_px = r.hitmask & (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return alb, (bx, by, bz), emit


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g
