"""
TS War Factory (GAWEAP / GTWEAP; TSWEAP in the mod) as a model for hd.py.

Built in its own frame ("local": X east, Y south as TS draws it, units 1 cell = 128, Z up, origin at the centre of TS's
4x3 foundation, X -256..256, Y -192..192), read from GTWEAP / GTWEAPMK / GTWEAPBB / _1 / _2 / _D in TS's own camera:
  hall     the main block on the west half (X -250..-54), a flat roof with machinery, its long axis east-west.
  bay      the vehicle bay through the hall's east end, floor at ground level (rails), behind the door.
  door     a roll-up door at the east end: vertical up to z 40, then a quarter circle (r 49) back into the roof
           (GTWEAP_D rolls it up along that track: the vertical part first, then the curve), between two quarter-round
           fenders that stand proud of it (its housings); a diagonal brace across its lower part.
  panel    the big green sloped panel leaning on the hall's south side, framed by two dark poles (the west one runs on
           over the roof as a beam, the east one is the lamp beam over the door), a green fascia above it.
  west     a green block on the west end (its top rounded down to the south); brown machinery, a pipe loop below it.
  roof     five lamps on the beam over the door (GTWEAP_A), three small lamps (GTWEAP_B), two fans (GTWEAP_C) in
           raised rings at the north-west, tan ridges and rust housings, a green band along the north edge, a green
           cap on the north fender, a green unit on the south fender's face.
  pad      the bib (GTWEAPBB), a separate layer: a concrete apron over the foundation's east half, seams fanning out
           from the end of the exit lane, house-coloured hazard stripes in the lane, a grey patch at its north-west.

Layouts (scene(..., layout=)): 'ts' TS's own placement (the TS-angle view); 'ra' turned a quarter clockwise so the
door faces south (RA's camera): world (X, Y) = (-y, x) of the local frame, a 3 x 4 plot.
"""
import numpy as np
import hd

(HALL, ROOF, GREEN, PANEL, FRAME, DOOR, JAMB, BAYIN, FLOOR, LAMPA, LAMPB, FAN, PIPE, MACH, PAD, CHEV, BEAM, GBLOCK,
 STRIPE, BAYCEIL, GREY, WESTG, FASCIA, NCAP, NSTRIP, PLINTH, FANBOX, SILL, SLAB) = range(1, 30)
HOUSE = {GREEN, PANEL, GBLOCK, CHEV, WESTG, FASCIA, NCAP, NSTRIP}

P = dict(
    hall=dict(x=(-250.0, -54.0), y=(-108.0, 107.0), z=104.0),
    bay=dict(x=(-200.0, -6.0), y=(-73.0, 76.0), ceil=90.0),
    # the door: vertical at x0 up to zc, then a quarter circle (centre (x0 - r, zc)) back to the hinge (x0 - r, zc + r)
    door=dict(x0=-6.0, zc=40.0, r=49.0, t=3.5, strip=7.0, rib=7.0),
    # the fenders: quarter ellipses centred at (xb, 0), semi-axes A (east) and B (up): the foot at xb + A, the top at xb
    jamb=dict(ys=((76.0, 103.0), (-108.0, -73.0)), xb=-52.0, A=62.0, B=98.0, back=-70.0,
              vent=dict(y=(-104.0, -86.0), z=(40.0, 56.0))),                    # a dark vent in the north fender
    ncap=dict(x=(-81.0, 2.0), y=(-108.0, -82.0), z=118.0, bevel=12.0, bot=70.0),   # the green cap on the north fender
    nstrip=dict(x=(-236.0, -81.0), y=(-108.0, -84.0), z=113.0),                # green band along the north edge
    west=dict(x=(-250.0, -160.0), y=(45.0, 108.0), zn=115.0, zs=84.0, seam=-205.0),   # the green block on the west end
    wmach=dict(boxes=(((-250.0, -168.0), (108.0, 126.0), 72.0), ((-236.0, -196.0), (126.0, 140.0), 44.0))),
    pipes=dict(pts=((-242.0, 140.0), (-224.0, 140.0)), r=4.5, z=86.0),      # the pipe loop on the south-west
    fascia=dict(x=(-150.0, -54.0), y=(100.0, 107.0), z=108.0),
    # the sloped panel: the plane z = s (y0 - y) from the ground at y0 up to the hall; green between the poles
    panel=dict(y0=196.0, s=1.256, x=(-140.0, -62.0), z=(14.0, 99.0), poles=(-146.0, -56.0), pw=10.0, ph=5.0,
               sill=(186.0, 196.0, 6.0)),
    # a green unit on the south fender's face: a box turned 45 degrees (one face square to TS's camera), a red band
    # round it, on a dark bracket, a small box on top
    gblock=dict(c=(-24.0, 133.0), w=60.0, d=30.0, z=(24.0, 60.0), bracket=((-38.0, -10.0), (100.0, 128.0), (12.0, 24.0)),
                stripe=(34.0, 38.0), top=dict(off=-10.0, w=18.0, d=14.0, z=72.0)),
    rbeam=dict(x=(-152.0, -142.0), y=(-60.0, 112.0), z=116.0),                 # the west pole's beam over the roof
    beam=dict(x=(-72.0, -56.0), y=(-108.0, 76.0), z=112.0),                   # the lamp beam over the door
    lampsA=dict(x=-60.3, z=123.0, y0=-108.7, dy=42.67, r=6.0),
    # the roof's machinery (TS's roof read at about z 108)
    roofframe=dict(x=(-190.0, -74.0), y=(-84.0, 30.0), z=110.0),
    slats=dict(x=(-166.0, -98.0), y=(-78.0, -6.0), z=(110.0, 121.0), period=24.0),         # three tan ridges along x
    rust=(((-110.0, -76.0), (-104.0, -60.0), 120.0), ((-112.0, -80.0), (-52.0, -14.0), 116.0)),
    darkm=(((-186.0, -140.0), (40.0, 70.0), 106.0), ((-132.0, -96.0), (40.0, 64.0), 108.0),
           ((-176.0, -150.0), (70.0, 98.0), 108.0)),
    lampsB=dict(pts=((-146.0, 40.7), (-114.3, 35.0), (-79.7, 32.3)), zs=(116.0, 110.0, 110.0), r=3.5),   # the west one on the beam
    fanbox=dict(x=(-250.0, -190.0), y=(-104.0, 34.0), z=106.0),
    fans=dict(pts=((-222.0, -67.5), (-219.5, 4.5)), z=106.0, r=15.0, ring=(21.0, 112.0), hub=3.5),
    nwbox=dict(x=(-246.0, -204.0), y=(-48.0, -22.0), z=114.0),               # a rust housing between the fans
    rgreen=dict(x=(-140.0, -100.0), y=(-4.0, 8.0), z=114.0),                  # a green strip on the roof's middle
    # small machinery scattered over the deck (seeded: every view gets the same), two pipes along the roof
    clutter=dict(n=26, seed=7, area=((-246.0, -78.0), (-100.0, 100.0)), size=(8.0, 22.0), h=(3.0, 11.0)),
    rpipes=(((-236.0, -82.0), -96.0, 109.0, 3.2), ((-188.0, -90.0), 84.0, 108.0, 3.2), ((-176.0, -104.0), 50.0, 113.0, 2.6)),
    # the bib: TS's outline (GTWEAPBB unprojected at ground level), the hazard lane in front of the door, the point the
    # seams fan out from, the grey patch at its north-west
    pad=dict(poly=((-64.0, -192.0), (132.0, -192.0), (256.0, -72.0), (256.0, 84.0), (150.0, 192.0), (-44.0, 192.0),
                   (-50.0, 150.0), (-32.0, 112.0), (0.0, 100.0), (0.0, -118.0)), h=1.5,
             # the hazard lane: the door's width, centred on it (Luke: TS's ran off to the north fender's side); the
             # bib's seams fan out from its far end, on the door's centre line too
             lane=dict(x=(-6.0, 72.0), y=(-73.0, 76.0), period=18.0), fan=(80.0, 1.5),
             grey=((-64.0, -192.0), (6.0, -192.0), (6.0, -110.0))),
    # the construction slab of the build-up (GTWEAPMK 0-17): the bib's outline plus the building's footprint
    slab=dict(poly=((-250.0, -150.0), (-196.0, -192.0), (132.0, -192.0), (256.0, -72.0), (256.0, 84.0), (150.0, 192.0),
                    (-176.0, 192.0), (-250.0, 150.0)), h=2.0),
)

LAYOUTS = {'ts': dict(turn=False), 'ra': dict(turn=True)}


def to_local(X, Y, layout='ts'):
    """world ground position -> the building's own frame"""
    if LAYOUTS[layout]['turn']:
        return Y, -X            # local east = world south
    return X, Y


def to_world(x, y, layout='ts'):
    if LAYOUTS[layout]['turn']:
        return -y, x
    return x, y


def in_poly(x, y, poly):
    inside = np.zeros(np.shape(x), bool)
    pts = list(poly)
    for i in range(len(pts)):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
        c = ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1)
        inside ^= c
    return inside


def inbox(x, y, bx, by):
    return (x >= bx[0]) & (x <= bx[1]) & (y >= by[0]) & (y <= by[1])


# ------------------------------------------------------------------------------------------------- the door's track
def door_len(d):
    return d['zc'] + np.pi / 2 * d['r']


def door_roll(t, d):
    """GTWEAP_D: t 0 (shut) .. 1 (rolled up, a strip left at the hinge) -> how far up its track the door's bottom edge
    has gone (track length, units).  TS: the straight part goes in frames 1-4, the curve in 4-8."""
    return np.clip(t, 0, 1) * (door_len(d) - d['strip'])


def track_s(X, Z, d):
    """track coordinate (units from the floor) of a point on the door: up the straight part, then round the curve."""
    cx = d['x0'] - d['r']
    phi = np.arctan2(np.maximum(Z - d['zc'], 0.0), np.maximum(X - cx, 1e-6))
    return np.where(Z <= d['zc'], Z, d['zc'] + d['r'] * phi)


def door_slab(x, d, s0):
    """the door sheet from track position s0 to the hinge, as (top, bot, mask) over local ground x."""
    cx = d['x0'] - d['r']
    r, t, zc = d['r'], d['t'], d['zc']
    u = np.clip(x - cx, 0, r)
    zo = zc + np.sqrt(np.clip(r * r - u * u, 0, None))                      # the curve's outer surface
    ui = np.clip(x - cx, 0, r - t)
    zi = np.where(x - cx < r - t, zc + np.sqrt(np.clip((r - t) ** 2 - ui * ui, 0, None)), zc)
    front = x > d['x0'] - t                                                 # the straight part's thickness
    zi = np.where(front, np.maximum(s0, 0.0) if s0 < zc else zc, zi)
    m = (x >= cx) & (x <= d['x0'])
    if s0 >= zc:
        # only the curve above angle phi0 is left: x <= cx + r cos(phi0)
        phi0 = (s0 - zc) / r
        m &= x <= cx + r * np.cos(phi0) + 0.01
        zi = np.where(front, zc, zi)
    return zo, zi, m


BUILD_KEYS = ('slab', 'hall', 'door', 'jambs', 'chev', 'poles', 'beam', 'roof', 'lampsB', 'lampsA', 'ncap', 'pframe',
              'panel', 'west', 'fans', 'pad', 'padtex', 'paint')
DONE = {k: 1.0 for k in BUILD_KEYS}


def scene(X, Y, p=None, layout='ts', prog=None, pad=False, door=0.0, merge=True):
    """door: 0 shut .. 1 rolled right up (GTWEAP_D 0..8).  pad: the bib alone (in the build-up: the construction slab
    and the bib).  prog: build-up progress per BUILD_KEYS (1 = done)."""
    p = P if p is None else p
    g = dict(DONE); g.update(prog or {})
    x, y = to_local(X, Y, layout)
    H = np.zeros_like(X); C = np.zeros(X.shape, np.int16)
    slabs = []
    extra = {}

    def put(h, comp, where=None):
        nonlocal H, C
        if where is not None:
            h = np.where(where, h, 0.0)
        win = h > H + 1e-6
        H = np.where(win, h, H); C = np.where(win, comp, C)

    def slab(top, bot, comp, where, name=''):
        top = np.broadcast_to(top, X.shape); bot = np.broadcast_to(bot, X.shape)
        slabs.append(hd.Slab(np.where(where, top, -1.0), np.where(where, np.maximum(bot, 0.0), 0.0),
                             np.where(where, comp, 0).astype(np.int16), name))

    def cyl(cx, cy, r, z, comp):
        rr = np.hypot(x - cx, y - cy)
        put(np.where(rr <= r, z, 0.0), comp)

    if pad:
        q = p['pad']
        m = in_poly(x, y, q['poly'])
        if g['padtex'] < 1.0:
            # the build-up's grey construction slab (GTWEAPMK 0-17): grows out from the middle of the foundation and
            # stays under everything until the apron gets its colour (18)
            sl = p['slab']
            grow = np.clip(g['slab'], 0, 1)
            ms = in_poly(x / max(grow, 1e-3), y / max(grow, 1e-3), sl['poly']) if grow > 0 else np.zeros_like(m)
            put(np.where(ms & (g['slab'] > 0), sl['h'], 0.0), SLAB)
        m = m & (g['pad'] > 0)
        put(np.where(m, q['h'], 0.0), PAD)
        ln = q['lane']
        cv = inbox(x, y, ln['x'], ln['y']) & m & (g['chev'] > 0)
        C = np.where(cv & (H > 0), CHEV, C)
        extra['padtex'] = np.full(X.shape, g['padtex'], np.float32)
        return hd.Scene(H, C, slabs, extra)

    h = p['hall']; b = p['bay']; w = p['west']
    hz = h['z'] * g['hall']
    # ---- the hall: a block with a flat roof (the west block takes its south-west corner); the bay runs through its
    #      east end: floor at the ground, a ceiling slab over it, a dark back wall
    hall = inbox(x, y, h['x'], h['y']) & ~inbox(x, y, w['x'], w['y'])
    bay = inbox(x, y, b['x'], b['y'])
    if g['hall'] > 0:
        put(np.where(hall & ~bay, hz, 0.0), HALL)
        if hz > b['ceil'] + 1:
            # 3 units into the hall round its sides and back, over the heightfield's edge (no seam on the roof)
            bayw = inbox(x, y, (b['x'][0] - 3.0, b['x'][1]), (b['y'][0] - 3.0, b['y'][1] + 3.0))
            slab(hz, b['ceil'], BAYCEIL, hall & bayw, 'bayroof')
        else:
            put(np.where(hall & bay, hz, 0.0), BAYCEIL)
        put(np.where(bay & (x < b['x'][0] + 8), min(b['ceil'], hz), 0.0), BAYIN)
        put(np.where(bay & (x >= b['x'][0] + 8), 1.0, 0.0), FLOOR)
    # ---- the west block: green, its top rounded down to the south
    if g['west'] > 0:
        tw = np.clip((y - w['y'][0]) / (w['y'][1] - w['y'][0]), 0, 1)
        zw = w['zs'] + (w['zn'] - w['zs']) * np.sqrt(np.clip(1 - tw * tw, 0, None))
        put(np.where(inbox(x, y, w['x'], w['y']), zw * g['west'], 0.0), WESTG)
    if g['hall'] > 0.5:
        for (bx, by, bz) in p['wmach']['boxes']:
            put(np.where(inbox(x, y, bx, by), bz * min(1.0, g['hall']), 0.0), MACH)
    if g['roof'] > 0:
        pp = p['pipes']
        zp_ = pp['z'] * g['roof']
        for (px_, py_) in pp['pts']:
            cyl(px_, py_, pp['r'], zp_, PIPE)
        (ax, ay), (bx_, by_) = pp['pts']
        bend = (x >= min(ax, bx_)) & (x <= max(ax, bx_)) & (np.abs(y - ay) <= pp['r'])
        if g['roof'] >= 1.0:
            slab(np.full_like(X, pp['z']), np.full_like(X, pp['z'] - 2 * pp['r']), PIPE, bend, 'bend')
    # ---- the green fascia along the top of the hall's south side (above the panel)
    if g['panel'] > 0:
        f = p['fascia']
        put(np.where(inbox(x, y, f['x'], f['y']), f['z'] * min(1.0, g['hall']), 0.0), FASCIA)
    # ---- the door: straight, then a quarter circle back into the roof; rolled up `door` of the way (GTWEAP_D)
    d = p['door']
    if g['door'] > 0:
        s0 = door_roll(door if door is not None else 1.0, d)
        dmask_y = inbox(x, y, (-1e9, 1e9), b['y'])
        if door is not None and door >= 0:              # door=None: no door at all (the bay open, GTWEAP_1)
            zo, zi, m = door_slab(x, d, s0)
            m &= dmask_y
            zo = np.minimum(zo, max(hz, 1.0))
            slab(zo, zi, DOOR, m & (zo > zi + 0.5), 'door')
        extra['door_s0'] = np.full(X.shape, s0, np.float32)
    # ---- the fenders: quarter-round plates either side of the door, standing proud of it
    j = p['jamb']
    if g['jambs'] > 0:
        for (ya, yb) in j['ys']:
            m = inbox(x, y, (j['back'], j['xb'] + j['A']), (ya, yb))
            uu = np.clip((x - j['xb']) / j['A'], 0.0, 1.0)
            zj = np.where(x <= j['xb'], j['B'], j['B'] * np.sqrt(np.clip(1 - uu * uu, 0, None)))
            put(np.where(m, zj * g['jambs'], 0.0), JAMB)
    nc = p['ncap']
    if g['ncap'] > 0:
        ncm = inbox(x, y, nc['x'], nc['y'])
        zcap = nc['z'] - np.clip(x - (nc['x'][1] - nc['bevel']), 0, None)      # a bevel along its east top edge
        zb = nc['bot'] + (1 - g['ncap']) * 40.0
        slab(np.maximum(zcap - (1 - g['ncap']) * 40.0, zb + 1), np.full_like(X, zb), NCAP, ncm, 'ncap')
    # ---- the north band (green) and the lamp beam with its five lamps
    if g['roof'] > 0:
        ns = p['nstrip']
        put(np.where(inbox(x, y, ns['x'], ns['y']), ns['z'] * min(1.0, g['hall']) * min(1.0, g['roof'] * 2), 0.0), NSTRIP)
    if g['beam'] > 0:
        bm = p['beam']
        put(np.where(inbox(x, y, bm['x'], bm['y']), bm['z'] * g['beam'], 0.0), BEAM)
    la = p['lampsA']
    for k in range(5):
        if g['lampsA'] * 5 > k:
            cy = la['y0'] + k * la['dy']
            rr = np.hypot(x - la['x'], y - cy)
            dome = la['z'] - la['r'] + np.sqrt(np.clip(la['r'] ** 2 - rr ** 2, 0, None)) * 1.6
            slab(dome, np.full_like(X, p['beam']['z'] - 4.0), LAMPA, rr <= la['r'], 'lampA')
    # ---- the roof's middle frame, the ridges, the housings, the green strip, the B lamps; the fan platform and fans
    if g['roof'] > 0:
        rf = p['roofframe']
        zr_ = h['z'] + (rf['z'] - h['z']) * g['roof']
        put(np.where(inbox(x, y, rf['x'], rf['y']), zr_, 0.0), ROOF)
        sl = p['slats']
        sm = inbox(x, y, sl['x'], sl['y'])
        rib = np.abs(((y - sl['y'][0]) % sl['period']) - sl['period'] / 2) / (sl['period'] / 2)      # 1 at the gaps
        put(np.where(sm, h['z'] + (sl['z'][1] - (sl['z'][1] - sl['z'][0]) * 0.5 * rib - h['z']) * g['roof'], 0.0), ROOF)
        for (bx, by, bz) in p['rust']:
            put(np.where(inbox(x, y, bx, by), h['z'] + (bz - h['z']) * g['roof'], 0.0), MACH)
        for (bx, by, bz) in p['darkm']:
            put(np.where(inbox(x, y, bx, by), h['z'] + (bz - h['z']) * g['roof'], 0.0), GREY)
        rg = p['rgreen']
        put(np.where(inbox(x, y, rg['x'], rg['y']), h['z'] + (rg['z'] - h['z']) * g['roof'], 0.0), GREEN)
    if g['roof'] >= 1.0:
        for (cx_, cy_, sx_, sy_, hh_, cc_) in clutter(p):
            put(np.where(inbox(x, y, (cx_ - sx_, cx_ + sx_), (cy_ - sy_, cy_ + sy_)), hh_, 0.0), cc_)
        for ((xa, xb_), yc, zc_, rp) in p['rpipes']:
            pm = (x >= xa) & (x <= xb_) & (np.abs(y - yc) <= rp)
            slab(zc_ + np.sqrt(np.clip(rp * rp - (y - yc) ** 2, 0, None)), zc_ - np.sqrt(np.clip(rp * rp - (y - yc) ** 2, 0, None)),
                 FRAME, pm, 'rpipe')
    if g['lampsB'] > 0:
        lb = p['lampsB']
        for (px_, py_), zb_ in zip(lb['pts'], lb['zs']):
            rr = np.hypot(x - px_, y - py_)
            slab(zb_ + np.sqrt(np.clip(lb['r'] ** 2 - rr ** 2, 0, None)), np.full_like(X, zb_ - 6.0), LAMPB,
                 rr <= lb['r'], 'lampB')
    if g['fans'] > 0:
        fb = p['fanbox']
        put(np.where(inbox(x, y, fb['x'], fb['y']), h['z'] + (fb['z'] - h['z']) * g['fans'], 0.0), FANBOX)
        fa = p['fans']
        rr_out, zr = fa['ring']
        for (px_, py_) in fa['pts']:
            rr = np.hypot(x - px_, y - py_)
            put(np.where(rr <= rr_out, h['z'] + (zr - h['z']) * g['fans'], 0.0), FANBOX)
            if g['fans'] >= 1.0:
                H = np.where(rr <= fa['r'], fa['z'], H); C = np.where(rr <= fa['r'], FAN, C)      # the fan sunk in it
                put(np.where(rr <= fa['hub'], fa['z'] + 4.0, 0.0), GREY)
        nb = p['nwbox']
        put(np.where(inbox(x, y, nb['x'], nb['y']), h['z'] + (nb['z'] - h['z']) * g['fans'], 0.0), MACH)
    # ---- the sloped panel and its poles (build-up: the poles lie on the ground pointing south, stand up, then lean
    #      back onto the hall; the panel goes in after), the sill at its foot
    pn = p['panel']
    zp = pn['s'] * (pn['y0'] - y)
    xl, xr = pn['poles'][0] - pn['pw'] / 2, pn['poles'][1] + pn['pw'] / 2
    if g['panel'] <= 0 and g['pframe'] > 0:
        # the build-up's panel frame (GTWEAPMK 6-14): the slope's skeleton, upright ribs in threes, rising up the slope
        # from its foot; TS fills its skin in at 15
        under = (y >= h['y'][1] - 1) & (y <= pn['y0']) & (x >= xl) & (x <= xr)
        zp_c = np.clip(zp, 0, h['z'])
        ph_ = (x - pn['x'][0]) % 26.0
        rib = ((np.abs(ph_ - 5.0) < 1.3) | (np.abs(ph_ - 10.0) < 1.3) | (np.abs(ph_ - 15.0) < 1.3)) & \
            (x >= pn['x'][0]) & (x <= pn['x'][1])
        zsk = np.where(rib, zp_c + 2.0, np.maximum(zp_c - 1.5, 0.0))
        put(np.where(under & (zp_c <= g['pframe'] * h['z'] + 0.5), zsk, 0.0), FRAME)
    if g['panel'] > 0:
        under = (y >= h['y'][1] - 1) & (y <= pn['y0']) & (x >= xl) & (x <= xr)
        zp_c = np.clip(zp, 0, h['z'])
        put(np.where(under, zp_c, 0.0), FRAME)
        green = under & (x >= pn['x'][0]) & (x <= pn['x'][1]) & (zp >= pn['z'][0]) & (zp <= pn['z'][1])
        C = np.where(green & (np.abs(H - zp_c) < 1e-3), PANEL, C)
    if g['poles'] > 0:
        L = np.hypot(pn['y0'] - (h['y'][1] - 4), h['z'] + 6)                  # the pole's length
        lean = np.arctan2(1.0, pn['s'])                                     # its final lean back from vertical (rad)
        q = g['poles']
        # angle from the ground, measured from pointing south: 0 lying south, pi/2 upright, pi/2 + lean leaning north
        ang = np.pi / 2 * min(q / 0.5, 1.0) + lean * max(0.0, (q - 0.5) / 0.5)
        ca, sa = np.cos(ang), np.sin(ang)
        tall = 0.45 <= q < 1.0
        if tall:
            # GTWEAPMK 9-10: TS stands the poles up tall at the top of the slope (as long as the slope's edge and the
            # roof beam they become), then tips them back over the hall; at 11 they lie as the slope's edges and beams
            Lt, yb = 268.0, h['y'][1] + 5.0
            tilt = np.radians(28.0) * max(0.0, (q - 0.5) / 0.5)
            st_, ct_ = np.sin(tilt), np.cos(tilt)
            for px_ in pn['poles']:
                pm = np.abs(x - px_) <= pn['pw'] / 2
                if st_ < 0.05:
                    put(np.where(pm & (np.abs(y - yb) <= pn['pw'] / 2), Lt, 0.0), FRAME)
                else:
                    tt = (yb - y) / st_
                    ok = pm & (tt >= -1.0) & (tt <= Lt)
                    zc_ = np.clip(tt, 0, Lt) * ct_
                    half = pn['ph'] / st_
                    slab(np.minimum(zc_ + half, Lt * ct_ + pn['ph']), np.maximum(zc_ - half, 0.0), FRAME, ok, 'pole')
        for px_ in (() if tall else pn['poles']):
            # the pole as a slab: points (y, z) along its axis from the foot (y0, 0), thickness ph
            along = (y - pn['y0']) * ca                                     # signed distance along the axis (on plan)
            pm = (np.abs(x - px_) <= pn['pw'] / 2)
            if abs(ca) < 1e-3 or (q < 1.0 and ang > np.pi / 2 and abs(ca) < 0.1):    # (near) upright: a column
                put(np.where(pm & (np.abs(y - pn['y0']) <= pn['pw'] / 2), L, 0.0), FRAME)
            elif q < 1.0 and ang > np.pi / 2:
                # leaning back onto the hall (build-up only): a bar through the air from its foot, not a fin under it
                tt = (y - pn['y0']) / ca
                ok = pm & (tt >= -1.0) & (tt <= L)
                zc_ = np.clip(tt, 0, L) * sa
                half = pn['ph'] / abs(ca)
                slab(np.minimum(zc_ + half, L * sa + pn['ph']), np.maximum(zc_ - half, 0.0), FRAME, ok, 'pole')
            else:
                tt = (y - pn['y0']) / ca                                    # distance along the pole
                ok = pm & (tt >= -2) & (tt <= L)
                zc_ = np.clip(tt, 0, L) * sa
                if ang <= np.pi / 2 + 1e-6 and sa < 0.999:
                    slab(zc_ + pn['ph'] / max(abs(ca), 0.2), np.maximum(zc_ - pn['ph'] / max(abs(ca), 0.2), 0), FRAME, ok, 'pole')
                else:
                    put(np.where(ok, np.clip(zc_ + pn['ph'], 0, h['z'] + 6), 0.0), FRAME)
    if g['slab'] >= 1.0 and g['poles'] > 0:
        s0_, s1_, sh = pn['sill']
        put(np.where((y >= s0_) & (y <= s1_) & (x >= xl - 20) & (x <= -12.0), sh, 0.0), SILL)
    # ---- the green unit on the south fender, on a dark bracket, a red band round it
    gb = p['gblock']
    if g['ncap'] > 0:
        u_ = ((x - gb['c'][0]) + (y - gb['c'][1])) / np.sqrt(2)          # towards TS's camera (south-east)
        v_ = ((x - gb['c'][0]) - (y - gb['c'][1])) / np.sqrt(2)          # across it (north-east)
        gm = (np.abs(u_) <= gb['d'] / 2) & (np.abs(v_) <= gb['w'] / 2)
        bxx, byy, bzz = gb['bracket']
        slab(np.full_like(X, bzz[1]), np.full_like(X, bzz[0]), PLINTH, inbox(x, y, bxx, byy), 'bracket')
        slab(np.full_like(X, gb['z'][1]), np.full_like(X, gb['z'][0]), GBLOCK, gm, 'gblock')
        gt = gb['top']
        gtm = (np.abs(u_ - gt['off']) <= gt['d'] / 2) & (np.abs(v_) <= gt['w'] / 2)
        slab(np.full_like(X, gt['z']), np.full_like(X, gb['z'][1]), GBLOCK, gtm, 'gtop')
    if g['beam'] > 0:
        rb = p['rbeam']
        put(np.where(inbox(x, y, rb['x'], rb['y']), rb['z'] * g['beam'], 0.0), FRAME)
    # ---- carve the bay out: whatever stands on the roof over it is a slab from the bay's ceiling up, the bay's floor
    #      under it (the heightfield can't overhang)
    if g['hall'] > 0:
        cv = bay & (x > b['x'][0] + 8) & (x < d['x0'] - d['t']) & (H > b['ceil'] + 0.5) & (C != DOOR)
        if cv.any():
            slab(H, np.full_like(X, b['ceil']), C, cv, 'overbay')
            H = np.where(cv, 1.0, H); C = np.where(cv, FLOOR, C)
    extra['paint'] = np.full(X.shape, g['paint'], np.float32)
    sc = hd.Scene(H, C, slabs, extra)
    return merge_slabs(sc) if merge else sc


_CLUTTER = {}


def clutter(p):
    """small boxes on the roof (on the deck, the middle frame or the fan platform): (cx, cy, half x, half y, top z,
    component), clear of the roof's bigger parts."""
    key = id(p)
    if key in _CLUTTER:
        return _CLUTTER[key]
    q = p['clutter']
    rng = np.random.default_rng(q['seed'])
    keep_out = [p['slats'], p['nwbox'], p['rgreen'], p['beam'], p['rbeam'], p['west']]
    keep_out += [dict(x=bx, y=by) for (bx, by, bz) in p['rust'] + p['darkm']]
    fr, fb = p['fans']['ring'][0] + 4, p['fans']['pts']
    out = []
    tries = 0
    while len(out) < q['n'] and tries < 4000:
        tries += 1
        cx = rng.uniform(*q['area'][0]); cy = rng.uniform(*q['area'][1])
        sx = rng.uniform(*q['size']) / 2; sy = rng.uniform(*q['size']) / 2
        if any((cx + sx > k['x'][0] - 3) and (cx - sx < k['x'][1] + 3) and (cy + sy > k['y'][0] - 3) and (cy - sy < k['y'][1] + 3)
               for k in keep_out):
            continue
        if any(np.hypot(cx - fx, cy - fy) < fr + max(sx, sy) for (fx, fy) in fb):
            continue
        if cy + sy > p['hall']['y'][1] - 4 or cy - sy < p['hall']['y'][0] + 26:
            continue
        if any(abs(cx - o[0]) < sx + o[2] + 2 and abs(cy - o[1]) < sy + o[3] + 2 for o in out):
            continue
        # what it stands on
        on = p['hall']['z']
        for k in (p['roofframe'], p['fanbox']):
            if (cx >= k['x'][0]) and (cx <= k['x'][1]) and (cy >= k['y'][0]) and (cy <= k['y'][1]):
                on = k['z']
        h = on + rng.uniform(*q['h'])
        comp = (MACH, GREY, ROOF, GREY, MACH)[int(rng.integers(0, 5))]
        out.append((cx, cy, sx, sy, h, comp))
    _CLUTTER[key] = out
    return out


def merge_slabs(sc):
    """pack slabs that don't overlap into as few as possible (memory: each slab is three full-grid arrays)."""
    packed = []
    for s in sc.slabs:
        m = s.top >= 0
        if not m.any():
            continue
        for q in packed:
            if not (q['m'] & m).any():
                q['top'] = np.where(m, s.top, q['top']); q['bot'] = np.where(m, s.bot, q['bot'])
                q['comp'] = np.where(m, s.comp, q['comp']); q['m'] |= m; q['names'].append(s.name)
                break
        else:
            packed.append(dict(top=s.top.copy(), bot=s.bot.copy(), comp=s.comp.copy(), m=m.copy(), names=[s.name]))
    sc.slabs = [hd.Slab(q['top'], q['bot'], q['comp'].astype(np.int16), '+'.join(q['names'])) for q in packed]
    return sc


FLAT = {HALL: (120, 80, 60), ROOF: (190, 160, 110), GREEN: (0, 200, 0), PANEL: (0, 230, 0), FRAME: (60, 60, 60),
        DOOR: (150, 150, 150), JAMB: (200, 170, 120), BAYIN: (40, 30, 25), FLOOR: (60, 60, 60), LAMPA: (30, 30, 30),
        LAMPB: (230, 80, 0), FAN: (40, 40, 40), PIPE: (150, 150, 150), MACH: (130, 70, 50), PAD: (200, 190, 160),
        CHEV: (0, 160, 0), BEAM: (50, 45, 40), GBLOCK: (0, 190, 0), STRIPE: (150, 30, 20), BAYCEIL: (35, 30, 28),
        GREY: (110, 110, 110), WESTG: (0, 210, 0), FASCIA: (0, 200, 0), NCAP: (0, 200, 0), NSTRIP: (0, 170, 0),
        PLINTH: (50, 45, 40), FANBOX: (180, 150, 100), SILL: (150, 140, 120), SLAB: (150, 150, 150)}
