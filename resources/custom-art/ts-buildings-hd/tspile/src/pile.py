"""
TS GDI Barracks (GAPILE, TSPILE in the mod) as a model for hd.py.

World: X east, Y south, units (1 cell = 128), origin at the centre of the 2x2 foundation, Z up.
Read from GTPILE / GTPILEMK in TS's own camera (roof slabs fitted to TS's pixels, see tsfit.py):
  pad        light concrete over the foundation, an H: a notch in the middle of the north edge and one in the
             south edge (the entrance's forecourt)
  bunkers    two long earth-sheltered bunkers running east-west, north and south of a narrow yard; battered
             sides of sand-coloured blocks over a red-brown panelled plinth, green house-colour hatches set into
             the slopes (the east ends mostly green); each roofed by two flat sandstone slabs, a gap between
  spine      a lower block joining the two bunkers in the middle of the yard, green hatches on it
  machinery  grey plant at both ends of the spine: a boxy air handler with a fan in the west, a vent stack
             and housing in the east
  entrance   a doorway in the south bunker's face under the roof's edge; steps down from it to the ground
             between two walls that stick out past the slope's foot (the east wall's coping green), GTPILE_A's
             lamps on the walls' upper ends
  masts      two lamp masts on the north bunker (the left one carries GTPILE_B's beacon); a flagpole on the
             east side with the GDI flag (GTPILE_C)
"""
import numpy as np
import hd

(SLAB, BERM, BAND, HATCH, ROOF, FASCIA, VENT, VENTTOP, GRILLE, STEP, CUTWALL, DOORWAY, MAST, LAMP, POLE, FLAG,
 SPINE, SOIL, FAN, DUCT, PORCH, ELAMP) = range(1, 23)
HOUSE = {HATCH, CUTWALL, FLAG}

BUILD_KEYS = ('pad', 'south', 'north', 'spine', 'roofs', 'machines', 'entrance', 'masts', 'mast2', 'pole', 'paint',
              'hatches')
DONE = {k: 1.0 for k in BUILD_KEYS}

P = dict(
    slab_h=3.0,
    pad=(-116.0, 122.0, -120.0, 104.0),              # x0, x1, y0, y1
    notch_n=(0.0, 42.0, -86.0),                      # the north notch: x0, x1, from the north edge to y
    notch_s=(14.0, 69.0, 88.0),                      # the south notch (the entrance's forecourt): x0, x1, from y
    # the bunkers' roof lines (the top of the battered body); the roofs sit on these
    bunkers=dict(n=dict(x0=-95.0, x1=83.0, y0=-67.0, y1=-31.0), s=dict(x0=-95.0, x1=83.0, y0=34.0, y1=75.0)),
    zr=44.0, bat=30.0,
    gap=(-32.0, -23.0),                              # between each bunker's two roof slabs
    roof_t=3.5, roof_over=2.5,
    band=(3.0, 13.0),                                # the red-brown plinth on the slopes: z0, z1
    spine=dict(x0=-38.0, x1=38.0, y0=-31.0, y1=34.0, z=30.0),
    # grey plant: west air handler (box + fan), east vent housing (box + stack)
    ahu=dict(x0=-72.0, x1=-38.0, y0=-26.0, y1=12.0, z=42.0, fan=(-55.0, -7.0, 10.0),
             tank=(-80.0, 0.0, 9.0, 34.0)),
    vent=dict(x0=40.0, x1=66.0, y0=-24.0, y1=6.0, z=34.0, stack=(53.0, -9.0, 7.0, 50.0)),
    # the entrance (TS's GTPILE): a doorway in the south bunker's face under the roof's edge, a flight of steps
    # down from its sill to the ground, between two walls that stick out past the slope's foot, their tops falling
    # with the steps: the west wall sand, the east wall's coping house green (TS's green bar)
    door=dict(x0=22.0, x1=61.0, wall_t=4.0, y_door=74.0, y_end=123.0, top0=24.5, top1=6.0, y_top0=86.0,
              sill=15.0, y_sill=80.0, rise=2.5, run=6.6, dx0=28.0, dx1=55.0, dz=35.0, coping=4.5),
    lamps=((20.0, 82.0, 28.0), (63.0, 82.0, 28.0)),  # the entrance's lamps (GTPILE_A) on the walls' upper ends, x, y, z
    masts=((-50.0, 4.0, 40.0, 124.0), (24.0, -32.0, 47.5, 116.0)),   # x, y, foot z, top z (on the air handler; on the NE roof)
    beacon=0,                                        # the mast with GTPILE_B's beacon
    pole=(70.0, -12.0, 3.0, 176.0),                  # the flagpole in the yard's east end: x, y, foot z, top z
    flag=dict(len=62.0, h=44.0, az=np.deg2rad(-45.0)),   # flies to the north-east (TS); the RA grid flies it east
    flag_az=dict(iso=np.deg2rad(-45.0), ra=0.0),       # per view: to the right, facing the camera, like RA's and TD's
    # green hatches on the slopes: (bunker, side, a0, a1, z0, z1): a along the side (x for n/s sides, y for e/w)
    hatches=(('s', 's', -80.0, -44.0, 3.0, 14.0), ('s', 's', 50.0, 72.0, 3.0, 26.0), ('s', 's', 80.0, 97.0, 8.0, 28.0),
             ('s', 's', -95.0, -81.0, 24.0, 40.0),
             ('s', 'e', 26.0, 49.0, 5.0, 31.0), ('s', 'e', 53.0, 78.0, 5.0, 31.0),
             ('n', 'e', -80.0, -55.0, 5.0, 33.0), ('n', 'e', -51.0, -26.0, 5.0, 33.0),
             ('n', 's', -60.0, -46.0, 26.0, 40.0), ('n', 's', -6.0, 10.0, 26.0, 40.0), ('n', 's', 64.0, 82.0, 24.0, 40.0),
             ('s', 'w', 44.0, 64.0, 10.0, 30.0), ('n', 'w', -58.0, -44.0, 16.0, 30.0)),
    # red-brown panels on the long faces: a band part-way up (z0, z1), broken where hatches are
    panels=(14.0, 22.0),)


def box(X, Y, x0, x1, y0, y1):
    return (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1)


def rect_out(X, Y, x0, x1, y0, y1):
    """per axis: how far outside the rectangle (0 inside), and which side is nearest."""
    dx = np.maximum(np.maximum(x0 - X, X - x1), 0)
    dy = np.maximum(np.maximum(y0 - Y, Y - y1), 0)
    return dx, dy


def body_height(X, Y, b, zr, bat):
    dx, dy = rect_out(X, Y, b['x0'], b['x1'], b['y0'], b['y1'])
    d = np.maximum(dx, dy)
    return zr - d * (zr / bat)


def face_of(X, Y, b):
    """which side of a bunker a point on its slope faces: 'n', 's', 'e', 'w'."""
    dx, dy = rect_out(X, Y, b['x0'], b['x1'], b['y0'], b['y1'])
    ew = np.where(X > b['x1'], 'e', 'w')
    ns = np.where(Y > b['y1'], 's', 'n')
    return np.where(dx >= dy, ew, ns)


def flag_curve(u, t, p=P, damaged=False):
    """the flag's centreline offset (across the flag) at u (0 at the pole .. 1 at the fly), frame t of 7."""
    ph = 2 * np.pi * t / 7.0
    amp = 5.0 * u ** 1.2
    return amp * np.sin(2 * np.pi * (1.1 * u) - ph)


def scene(X, Y, p=P, prog=None, flag=None, damaged=False, hoist=1.0, flag_az=None):
    """prog: build-up controls (BUILD_KEYS, 0..1; None = finished).  flag: frame 0..6 of the flag waving
    (None = no flag: GTPILE_C draws it)."""
    g = dict(DONE); g.update(prog or {})
    H = np.zeros_like(X); C = np.zeros(X.shape, np.int16)
    slabs = []

    def put(h, comp, where=None):
        nonlocal H, C
        if where is not None:
            h = np.where(where, h, 0.0)
        win = h > H + 1e-6
        H = np.where(win, h, H); C = np.where(win, comp, C)

    def slab(top, bot, comp, where, name=''):
        slabs.append(hd.Slab(np.where(where, top, -1.0), np.where(where, np.maximum(bot, 0.0), 0.0),
                             np.where(where, comp, 0).astype(np.int16), name))

    # ---- pad: an H of light concrete
    x0, x1, y0, y1 = p['pad']
    if g['pad'] > 0:
        s = g['pad']
        padm = box(X, Y, x0 * s, x1 * s, y0 * s, y1 * s)
        nx0, nx1, ny = p['notch_n']
        padm &= ~((X >= nx0) & (X <= nx1) & (Y < ny))
        sx0, sx1, sy = p['notch_s']
        padm &= ~((X >= sx0) & (X <= sx1) & (Y > sy))
        put(np.full_like(X, p['slab_h']), SLAB, padm)

    zr, bat = p['zr'], p['bat']
    B = p['bunkers']
    # ---- the spine between the bunkers (lower)
    if g['spine'] > 0:
        sp = p['spine']
        zs = p['slab_h'] + (sp['z'] - p['slab_h']) * g['spine']
        m = box(X, Y, sp['x0'], sp['x1'], sp['y0'] - 6, sp['y1'] + 6)
        put(np.full_like(X, zs), SPINE, m)

    # ---- the bunkers: battered bodies up to the roof line
    for key in ('n', 's'):
        gk = g['north' if key == 'n' else 'south']
        if gk <= 0:
            continue
        b = B[key]
        h = body_height(X, Y, b, zr * gk, bat)
        put(np.where(h > 0, h, 0.0), BERM)
    # the entrance: steps down from a doorway in the south bunker's face, between two walls that stick out
    if g['south'] > 0 and g['entrance'] > 0:
        d = p['door']
        ge = g['entrance']
        wt = d['wall_t']
        # the porch: the slope cut away between the walls' outer faces, down to the steps
        porch = (X >= d['x0'] - wt) & (X <= d['x1'] + wt) & (Y > d['y_door'])
        k = np.clip(np.ceil((Y - d['y_sill']) / d['run']), 0, None)
        floor = np.maximum(d['sill'] - d['rise'] * k, 0.0) * ge
        stairs = porch & (Y <= d['y_end'])
        H = np.where(stairs, floor, H)
        C = np.where(stairs, np.where(floor > 0.05, STEP, 0), C)
        # the walls: their tops level by the door, then falling with the steps to the ground past the slope's foot
        t = np.clip((Y - d['y_top0']) / (d['y_end'] - d['y_top0']), 0, 1)
        wtop = (d['top0'] + (d['top1'] - d['top0']) * t) * ge
        walls = ((X >= d['x0'] - wt) & (X <= d['x0'])) | ((X >= d['x1']) & (X <= d['x1'] + wt))
        put(np.where(walls & (Y > d['y_door'] - 2.0) & (Y <= d['y_end']), wtop, 0.0), PORCH)
        # GTPILE_A's lamps: small housings on the walls' upper ends
        for (lx, ly, lz) in p['lamps']:
            put(np.where(box(X, Y, lx - 2.6, lx + 2.6, ly - 2.6, ly + 2.6), (lz + 2.8) * ge, 0.0), ELAMP)
    # the doorway: dark, in the face at the back of the porch (drawn by materials)

    # ---- roofs: two flat slabs per bunker
    if g['roofs'] > 0:
        o = p['roof_over']
        for key in ('n', 's'):
            b = B[key]
            for (ax, bx_) in ((b['x0'] - o, p['gap'][0]), (p['gap'][1], b['x1'] + o)):
                m = box(X, Y, ax, bx_, b['y0'] - o, b['y1'] + o)
                top = zr + p['roof_t'] * g['roofs']
                slab(np.full_like(X, top), np.full_like(X, zr - 1.0), ROOF, m, 'roof')

    # ---- machinery
    if g['machines'] > 0:
        a = p['ahu']
        za = p['slab_h'] + (a['z'] - p['slab_h']) * g['machines']
        put(np.full_like(X, za), VENT, box(X, Y, a['x0'], a['x1'], a['y0'], a['y1']))
        fx, fy, fr = a['fan']
        dfan = np.hypot(X - fx, Y - fy)
        put(np.where(dfan <= fr, za + 3.0, 0.0), FAN)
        tx_, ty_, tr, tz = a['tank']
        dtk = np.hypot(X - tx_, Y - ty_)
        tzz = p['slab_h'] + (tz - p['slab_h']) * g['machines']
        put(np.where(dtk <= tr, tzz + 3.0 * np.sqrt(np.clip(1 - (dtk / tr) ** 2, 0, 1)), 0.0), DUCT)
        v = p['vent']
        zv = p['slab_h'] + (v['z'] - p['slab_h']) * g['machines']
        put(np.full_like(X, zv), VENT, box(X, Y, v['x0'], v['x1'], v['y0'], v['y1']))
        sx, sy, sr, sz = v['stack']
        ds = np.hypot(X - sx, Y - sy)
        put(np.where(ds <= sr, p['slab_h'] + (sz - p['slab_h']) * g['machines'], 0.0), DUCT)
        put(np.where(ds <= sr - 2.0, p['slab_h'] + (sz - 3.0 - p['slab_h']) * g['machines'], 0.0), GRILLE)

    # ---- masts and the flagpole
    for mi, (mx, my, mz0, mz1) in enumerate(p['masts']):
        gm = g['masts'] if mi == 0 else g['mast2']
        if gm > 0:
            dm = np.hypot(X - mx, Y - my)
            top = mz0 + (mz1 - mz0) * gm
            slab(np.full_like(X, top), np.full_like(X, mz0 - 2), MAST, dm <= 1.5, 'mast')
            # a lamp housing on top, a cross-arm with two small lamps, a short aerial
            slab(np.full_like(X, top + 4.0), np.full_like(X, top - 2.0), LAMP, box(X, Y, mx - 3.2, mx + 3.2, my - 3.2, my + 3.2), 'lamp')
            slab(np.full_like(X, top + 13.0), np.full_like(X, top + 4.0), MAST, dm <= 0.7, 'aerial')
            arm = (np.abs(Y - my) <= 0.9) & (np.abs(X - mx) <= 8.0)
            slab(np.full_like(X, top - 8.0), np.full_like(X, top - 9.8), MAST, arm, 'arm')
            for sx_ in (-7.5, 7.5):
                slab(np.full_like(X, top - 5.5), np.full_like(X, top - 9.0), LAMP, np.hypot(X - mx - sx_, Y - my) <= 1.8, 'armlamp')
    if g['pole'] > 0:
        px_, py_, pz0, pz1 = p['pole']
        dp = np.hypot(X - px_, Y - py_)
        top = pz0 + (pz1 - pz0) * g['pole']
        slab(np.full_like(X, top), np.full_like(X, pz0), POLE, dp <= 1.4, 'pole')
        put(np.where(dp <= 4.0, p['slab_h'] + 3.0, 0.0), POLE)          # its footing

    # ---- the flag (GTPILE_C): a cloth hanging from the pole's top, waving
    extra = {}
    if flag is not None:
        f = p['flag']
        px_, py_, pz0, pz1 = p['pole']
        az = f['az'] if flag_az is None else flag_az          # each view flies it to the right, facing the camera
        ux, uy = np.cos(az), np.sin(az)
        al = (X - px_) * ux + (Y - py_) * uy                      # along the flag
        ac = -(X - px_) * uy + (Y - py_) * ux                     # across
        u = al / f['len']
        on = (u >= 0) & (u <= 1)
        off = flag_curve(np.clip(u, 0, 1), flag, p, damaged)
        cloth = on & (np.abs(ac - off) <= 0.9)
        top = pz1 - 2.0 - 3.0 * np.clip(u, 0, 1) ** 1.5                           # the fly droops a little
        top = top - (1.0 - hoist) * 70.0                           # build-up: hoisted up the pole
        bot = top - f['h'] * (1 - 0.08 * u)
        if damaged:
            # torn: the fly end ragged and shorter, bitten from the top and the bottom edge
            uu = np.clip(u, 0, 1)
            cloth &= u <= 0.82 + 0.06 * np.sin(flag * 1.7)
            bite = np.clip((uu - 0.45) / 0.37, 0, 1)
            jag_b = np.abs(np.sin(uu * 37.0 + flag * 0.9)) * 0.6 + np.abs(np.sin(uu * 13.0 + 1.3)) * 0.4
            jag_t = np.abs(np.sin(uu * 29.0 + 2.1 + flag * 0.7)) * 0.5 + np.abs(np.sin(uu * 11.0)) * 0.5
            bot = bot + f['h'] * 0.42 * bite * jag_b
            top = top - f['h'] * 0.3 * bite ** 1.5 * jag_t
            cloth &= top > bot + 2.0
        slab(top, bot, FLAG, cloth, 'flag')
        extra['flag_u'] = u.astype(np.float32)
    extra['paint'] = np.full_like(X, g['paint'], dtype=np.float32)
    extra['hatches'] = np.full_like(X, g['hatches'], dtype=np.float32)
    return hd.Scene(H, C, slabs, extra)


FLAT = {SLAB: (150, 150, 146), BERM: (140, 118, 76), BAND: (100, 46, 30), HATCH: (0, 190, 0), ROOF: (190, 165, 110),
        FASCIA: (80, 70, 50), VENT: (140, 140, 140), VENTTOP: (90, 90, 90), GRILLE: (40, 40, 40), STEP: (150, 140, 110),
        CUTWALL: (0, 170, 0), DOORWAY: (20, 20, 20), MAST: (70, 70, 70), LAMP: (220, 220, 220), POLE: (50, 50, 40),
        FLAG: (0, 170, 0), SPINE: (120, 104, 70), SOIL: (120, 100, 70), FAN: (60, 60, 60), DUCT: (120, 120, 120),
        PORCH: (170, 150, 100), ELAMP: (200, 200, 200)}
