"""
TS Tiberium Refinery (NAREFN; TSPROC in the mod) as a model for hd.py.

Built in its own frame ("local": X east, Y south as TS draws it, units 1 cell = 128, Z up, origin at the centre of
TS's 4x3 foundation, X -256..256, Y -192..192), read from NTREFN / NTREFNMK / NTREFNBB in TS's own camera:
  umbrella  a round deck (black, a green rim) up on a skirt that slopes to the ground all round: sixteen green
            ribs (house colour) down the slope, flat grey panels between them. Its centre is on the dock's axis.
  dock      TS's harvester parks on the foundation's cell (2, 1) facing east, its back end under the deck's east
            rim: the skirt is cut open there (a slot from the ground up under the deck), the bib's hazard stripes
            run in on its floor, a dark red wall at the back.
  east      the skirt's east panels run on past the dock as a red-brown hood; a copper sphere with a white cap
            sits behind it.
  stacks    the flare stack at the back (a brown cone, a grey stack with two flanges, a black pipe beside it), two
            columns on the deck (one flanged, on a gold ring; one tall with a pipe bent over to a black post),
            a cluster of thin pipes on the west.
  pad       the bib (NTREFNBB), a separate layer: a concrete apron round the dock, hazard stripes on the lane.

Layouts (scene(..., layout=)): 'ts' TS's own placement (the TS-angle view, and the RA grid's start).
"""
import numpy as np
import hd

(SKIRT, RIB, DECK, RIM, HOOD, SPHERE, CAP, CONE, STACK, FLANGE, PIPE, COLUMN, GOLD, WPIPE, DOCKWALL, DOCKIN,
 PAD, STRIPE, BASE, LAMP, LAMPBOX, HOLE) = range(1, 23)
RIM_W, HOLE_D = 2.4, 9.0             # the stacks' open tops (TS's black holes): rim width; depth of a broken column's hollow
HOUSE = {RIB, RIM, LAMP}             # TS draws the dock lamps in house colour (NTREFN_C's remap greens)

P = dict(
    c=(-102.8, -8.7),            # the umbrella's centre (on the dock's axis, Y 0)
    deck_r=86.4, deck_z=74.0,  # the deck: radius to the rim's outside, height
    rim_w=4.0, rim_h=1.5,      # the green ring round the deck's top
    band=6.7,                  # the deck's edge: a green band this tall above the skirt
    foot_r=173.3,              # the skirt's foot on the ground
    ribs=16, rib0=13.1,        # number of ribs, the first one's angle (degrees, 0 = east, 90 = south)
    rib_w=6.4, rib_h=4.0,      # rib width, how far it stands proud of the skirt
    rib_ext=6.8,               # the ribs run this far past the panels' foot
    dock=dict(a=(-31.9, 35.6), r_back=40.0, ceil=58.0),   # the cut: between these rib angles, its back wall, ceiling
    # the flare stack (behind the deck, on the skirt): a brown cone (z0, r0) -> (z1, r1), the grey stack (radius, top),
    # two collars (z0, z1), their radius, a dark lip at the top
    stack=dict(c=(-199.8, -33.1), cone=(50.0, 30.0, 146.7, 17.0), r=11.0, top=249.0,
               collars=((189.0, 194.5), (220.5, 226.0)), cr=17.0, lip=5.0,
               box=(60.0, 103.0, 7.5), box_off=(16.0, 2.0)),             # the grey housing at the cone's front foot: z0, z1, half-size
    spipe=dict(c=(-184.5, -48.5), r=3.6, top=249.0, box=(214.0, 245.0, 7.0)),   # the black pipe beside it
    # on the deck: the flanged column at its centre on a gold ring, the tall column, the black pipe off its top
    mid=dict(r=9.4, top=163.0, collars=((100.0, 105.0), (131.0, 136.0)), cr=17.0, ring=(29.0, 37.0, 2.2), teeth=36),
    tall=dict(c=(-78.7, -33.3), r=10.5, top=198.0),
    tpipe=dict(c=(-62.0, -44.0), r=3.0, top=203.0),
    links=(117.0, 160.0),          # heights of the two black links from the flanged column to the tall one
    # the copper sphere (centre, radius) and its white cap (radius, height)
    sphere=dict(c=(-34.4, -108.5, 57.0), r=40.0, cap=(15.0, 9.0)),
    # thin pipes on the west, behind the skirt: (x, y, radius, top)
    wpipes=((-243.1, 10.2, 3.8, 96.6), (-235.1, 2.2, 3.8, 92.3), (-224.5, -8.5, 3.8, 88.0), (-219.1, -13.8, 3.8, 114.0)),
    # the two dock lamps (NTREFN_C) on the deck's edge band either side of the dock: azimuth, radius of the glass
    lamps=dict(az=(31.8, -14.0), r=4.6, z=70.6, out=3.2),
    # the bib (NTREFNBB): a concrete apron over the foundation's east half, its corners cut, its west edge round the
    # skirt's foot (and in under the deck in the dock); hazard stripes on cell column 2, across the docked harvester
    pad=dict(poly=((-4.0, -170.0), (12.0, -188.0), (140.0, -188.0), (252.0, -100.0), (260.0, -70.0), (260.0, 78.0),
                   (166.0, 196.0), (4.0, 196.0), (-4.0, 182.0)), h=2.0, margin=4.0,
             stripes=dict(x=(17.0, 97.0), y=(-111.0, 116.0), n=(0.46, 0.89), period=41.5)),
)

# 'ts': TS's own (the TS-angle view).  'ra': the RA grid, TS's way round (the dock to the east).  `lift` raises the
# deck and everything on it: it was 18 for the mod's harvester (1.32x TS's); with TS's own harvester size (Luke) it is
# 0, so the RA-grid refinery is TS's exact shape too.
# The mod's harvester is EA's TD harvester's length (1.26x TS's, and 1.07x more on the RA grid, whose building is
# drawn at 0.935): there the deck is lifted 22 so it clears the truck's roof, and under the deck the dock opens
# out from TS's wedge into a straight-sided bay (`bay`: its north and south edges in world y, its back wall's x) as
# wide as the truck with room either side, so the truck backs in under the deck. The skirt keeps TS's opening.
LAYOUTS = {'ts': dict(lift=0.0), 'ra': dict(lift=22.0, bay=dict(y=(-51.5, 52.5), x_back=-76.0, lip=3.0))}
_CACHE = {}


def params(layout='ts', p=None):
    """the parameters for a layout: TS's own, or lifted for the mod's harvester."""
    base = P if p is None else p
    dz = LAYOUTS[layout]['lift']
    bay = LAYOUTS[layout].get('bay')
    if dz == 0 and bay is None:
        return base
    key = (id(base), layout)
    if key in _CACHE:
        return _CACHE[key]
    q = {k: (dict(v) if isinstance(v, dict) else v) for k, v in base.items()}
    q['deck_z'] = base['deck_z'] + dz
    q['dock']['ceil'] = base['dock']['ceil'] + dz
    if bay is not None:
        q['dock']['bay'] = bay
    q['lamps']['z'] = base['lamps']['z'] + dz
    m = q['mid']; m['top'] += dz; m['collars'] = tuple((a + dz, b + dz) for a, b in m['collars'])
    q['tall']['top'] += dz
    q['tpipe']['top'] += dz
    q['links'] = tuple(z + dz for z in base['links'])
    # what stands on the skirt rises with it (the skirt is higher by dz x its height's share there)
    def on_skirt(xy):
        r = np.hypot(xy[0] - base['c'][0], xy[1] - base['c'][1])
        return dz * np.clip((base['foot_r'] - r) / (base['foot_r'] - base['deck_r']), 0, 1)
    sph = q['sphere']; sx, sy, sz = sph['c']; sph['c'] = (sx, sy, sz + on_skirt((sx, sy)))
    st = q['stack']; c0, r0, c1, r1 = st['cone']; st['cone'] = (c0 + on_skirt(st['c']), r0, c1, r1)
    st['box'] = (st['box'][0] + on_skirt(st['c']), st['box'][1] + on_skirt(st['c']), st['box'][2])
    q['wpipes'] = tuple((wx, wy, wr, wt + on_skirt((wx, wy))) for (wx, wy, wr, wt) in base['wpipes'])
    _CACHE[key] = q
    return q


def to_local(X, Y, layout='ts'):
    return X, Y          # both layouts keep TS's way round


def to_world(x, y, layout='ts'):
    return x, y


def skirt_z(r, p=P):
    """height of the skirt's surface at radius r (a straight cone from under the deck's edge band to the foot)."""
    z0 = p['deck_z'] - p['band']
    return np.where(r <= p['deck_r'], z0, z0 * np.clip((p['foot_r'] - r) / (p['foot_r'] - p['deck_r']), 0, 1))


def in_poly(x, y, poly):
    inside = np.zeros(np.shape(x), bool)
    pts = list(poly)
    for i in range(len(pts)):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
        c = ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1)
        inside ^= c
    return inside


def pad_mask(x, y, p=P):
    """the bib: TS's outline, its west edge just outside the skirt's foot except in the dock, where it runs in under
    the deck to the dock's back wall, so no ground shows inside the dock from any angle."""
    cx, cy = p['c']
    r = np.hypot(x - cx, y - cy)
    in_dock, floor = dock_cut(x, y, p)
    floor = floor & (r <= p['foot_r'])
    return (in_poly(x, y, p['pad']['poly']) & ((r >= p['foot_r'] - p['pad']['margin']) | in_dock)) | floor


def dock_cut(x, y, p=P):
    """the dock: (the cut through the skirt, the floor under it to the back wall). TS's wedge between two ribs; with
    the layout's `bay`, a straight-sided bay under the deck as well, out of sight but for the opening."""
    d = p['dock']
    cx, cy = p['c']
    r = np.hypot(x - cx, y - cy)
    phi = np.degrees(np.arctan2(y - cy, x - cx)) % 360.0
    a0, a1 = d['a']
    wedge = ((phi - a0) % 360.0) <= (a1 - a0) % 360.0
    cut, floor = wedge & (r > d['r_back']), wedge & (r >= d['r_back'] - 2.0)
    bay = d.get('bay')
    if bay is not None:
        # a ring under the deck's edge stays solid outside the wedge: the faceted skirt's top dips below the round
        # deck between the ribs, and that slit would show into the bay
        inside = (y >= bay['y'][0]) & (y <= bay['y'][1]) & (r < p['deck_r'] - bay.get('lip', 3.0))
        cut = cut | (inside & (x > bay['x_back']))
        floor = floor | (inside & (x >= bay['x_back'] - 2.0))
    return cut, floor


def stripes(x, y, p=P):
    """the hazard stripes on the bib: True where orange (the rest of the striped band is black)."""
    s = p['pad']['stripes']
    band = (x >= s['x'][0]) & (x <= s['x'][1]) & (y >= s['y'][0]) & (y <= s['y'][1])
    return band


def stripe_phase(x, y, p=P):
    s = p['pad']['stripes']
    return ((x * s['n'][0] + y * s['n'][1]) / s['period']) % 1.0


def rib_angles(p=P):
    return p['rib0'] + 360.0 / p['ribs'] * np.arange(p['ribs'])


def _window(X, Y, pos, R):
    """the rows and columns of the grid that hold everything within R of pos (the grid may be turned to the screen)."""
    m = (np.abs(X - pos[0]) <= R) & (np.abs(Y - pos[1]) <= R)
    if not m.any():
        return None
    rows = np.nonzero(m.any(axis=1))[0]; cols = np.nonzero(m.any(axis=0))[0]
    return slice(rows[0], rows[-1] + 1), slice(cols[0], cols[-1] + 1)


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


BUILD_KEYS = ('ribs', 'ring', 'skirt', 'deck', 'dock', 'cone', 'stack', 'wpipes', 'mid', 'tall', 'pipes', 'gear',
              'sphere', 'cap', 'lamps', 'pad', 'padtex')
DONE = {k: 1.0 for k in BUILD_KEYS}


def order(k, salt=0.0):
    """0..1 per panel/part index: the order they go in (build-up)."""
    return np.abs(np.sin(k * 7.31 + 1.7 + salt) * 9871.13) % 1.0


def scene(X, Y, p=None, layout='ts', prog=None, pad=False, merge=True, lid=None, truck=None):
    """prog: build-up progress per BUILD_KEYS (1 = done).  pad: the bib alone.  lid: the harvester's tank in the
    dock (the refinery's NTREFN_A): dict(model=harv module, frame, pos, s, off, wall) - the tank slid `off` voxels
    back from where it sits on the docked truck, nothing of it past the wall plane x = wall (local units).
    truck: the whole harvester docked (HARV, or HORV with unloading=True): dict(model, frame, pos, s, unloading)."""
    p = params(layout, p)
    g = dict(DONE); g.update(prog or {})
    x, y = to_local(X, Y, layout)
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

    def stand(top, comp, where, name):
        """something standing on the deck: solid from the ground where the skirt hides its foot (TS's wedge), or
        from the deck's underside when the dock is a bay, which would otherwise show it as a pillar inside."""
        if p['dock'].get('bay') is None:
            put(np.where(where, top, 0.0), comp)
        else:
            slab(np.full_like(X, top) if np.ndim(top) == 0 else top, np.full_like(X, p['deck_z'] - p['band']),
                 comp, where, name)

    def hole(rr_, rad, top_, base):
        """an open pipe's top: inside the rim the column drops into a dark hole (where nothing stands above it)."""
        nonlocal H, C
        if top_ - HOLE_D < base + 1.0:
            return
        m = (rr_ <= rad - RIM_W) & (np.abs(H - top_) < 1e-3)
        H = np.where(m, top_ - HOLE_D, H); C = np.where(m, HOLE, C)

    cx, cy = p['c']
    dx, dy = x - cx, y - cy
    r = np.hypot(dx, dy)
    phi = np.degrees(np.arctan2(dy, dx)) % 360.0
    if pad:
        m = pad_mask(x, y, p)
        stp = stripes(x, y, p) & m
        show = (m & (g['pad'] > 0)) | (stp & (g['dock'] > 0))
        put(np.where(show, p['pad']['h'], 0.0), PAD)
        C = np.where(stp & (H > 0), STRIPE, C)
        return hd.Scene(H, C, slabs, {'padtex': np.full_like(X, g['padtex'], dtype=np.float32)})
    d = p['dock']
    a0, a1 = d['a']
    ang = ((phi - a0) % 360.0)
    in_dock = ang <= (a1 - a0) % 360.0
    # ---- the skirt: a cone of flat panels between the ribs (a 16-sided pyramid frustum), from under the deck's
    #      green edge band down to the foot; build-up: the panels go in one by one
    n = p['ribs']
    step = 360.0 / n
    k = np.floor(((phi - p['rib0']) % 360.0) / step)
    mid = np.radians(p['rib0'] + (k + 0.5) * step)
    rr = r * np.cos(np.radians(phi) - mid) / np.cos(np.radians(step / 2))   # flat facets: radius along the facet
    zs = skirt_z(rr, p)
    if g['skirt'] > 0:
        on = (rr <= p['foot_r']) & (r > 0) & (order(k) < g['skirt'])
        put(np.where(on, zs, 0.0), SKIRT)
    # ---- the ribs: proud strips down the slope, a little past the panels' foot; build-up: they lie flat on the
    #      ground first (TS's GTREFNMK 0) and are raised about their feet
    if g['ribs'] > 0:
        dang = ((phi - p['rib0'] + step / 2) % step) - step / 2           # degrees from the nearest rib
        across = np.radians(dang) * r
        rib = (np.abs(across) <= p['rib_w'] / 2) & (r >= p['deck_r'] - 2) & (r <= p['foot_r'] + p['rib_ext'])
        zrib = skirt_z(r - p['rib_ext'] * np.clip((r - p['deck_r']) / (p['foot_r'] - p['deck_r']), 0, 1), p)
        put(np.where(rib, zrib * g['ribs'] + p['rib_h'], 0.0), RIB)
    # ---- the dock: the skirt is cut away between two ribs (TS: from the rib at -31.9 to the one at 35.6
    #      degrees), a cavity under the deck's east side, the north cut face a red-brown wall, the back dark
    notch, _ = dock_cut(x, y, p)
    H = np.where(notch, 0.0, H); C = np.where(notch, 0, C)
    bay = d.get('bay')
    if g['skirt'] > 0.3:
        if bay is not None:
            back = (y >= bay['y'][0]) & (y <= bay['y'][1]) & (x <= bay['x_back']) & (x > bay['x_back'] - 8)
        else:
            back = in_dock & (r <= d['r_back']) & (r > d['r_back'] - 8)
        put(np.where(back, d['ceil'], 0.0), DOCKIN)
    # ---- the deck: one thick disc over the skirt (and over the dock), its edge a green band, a thin green ring
    #      round its top; build-up: the ring first, then a frame of spokes, then the plate from the middle out
    deck = r <= p['deck_r']
    rim = deck & (r >= p['deck_r'] - p['rim_w'])
    dtop = np.where(rim, p['deck_z'] + p['rim_h'], p['deck_z'])
    dcomp = np.where(r >= p['deck_r'] - 1.5, RIM, np.where(rim, RIM, DECK))
    if g['ring'] > 0:
        show = rim.copy()
        if g['deck'] > 0:
            spokes = (np.abs(((phi - p['rib0']) % step) - step / 2) * np.radians(1) * r < 3.0)
            plate = r <= p['deck_r'] * np.clip((g['deck'] - 0.35) / 0.65, 0, 1)
            show |= deck & (spokes | plate | (r < 14.0))
        slabs.append(hd.Slab(np.where(show, dtop, -1.0), np.where(show, p['deck_z'] - p['band'], 0.0),
                             np.where(show, dcomp, 0).astype(np.int16), 'deck'))
    H = np.where(deck & (H > p['deck_z'] - p['band']), p['deck_z'] - p['band'], H)
    # the dock lamps: a small housing on the edge band, the glass facing out
    if g['lamps'] > 0:
        lm = p['lamps']
        for a_ in lm['az']:
            ux, uy = np.cos(np.radians(a_)), np.sin(np.radians(a_))
            lx0, ly0 = cx + p['deck_r'] * ux, cy + p['deck_r'] * uy
            ou = (x - lx0) * ux + (y - ly0) * uy
            ov = -(x - lx0) * uy + (y - ly0) * ux
            hb = (ou >= -2.0) & (ou <= lm['out']) & (np.abs(ov) <= lm['r'] + 1.5)
            slab(np.full_like(X, lm['z'] + lm['r'] + 1.5), np.full_like(X, lm['z'] - lm['r'] - 1.5), LAMPBOX, hb, 'lampbox')
            dome = np.sqrt(np.clip(lm['r'] ** 2 - ov ** 2, 0, None))
            gl = (ou > lm['out']) & (ou <= lm['out'] + 2.6) & (np.abs(ov) <= lm['r'])
            slab(lm['z'] + dome * 0.95, lm['z'] - dome * 0.95, LAMP, gl, 'lamp')
    # the north cut face: a thin wall under the rib at a0, red-brown on its face into the dock
    if g['skirt'] > 0.3:
        dn = ((phi - a0 + 180.0) % 360.0) - 180.0
        wall = (np.radians(np.abs(dn)) * r <= 3.0) & (r > d['r_back']) & (r <= p['foot_r'])
        if bay is not None:
            # under the deck the bay's north side carries it
            wall = (wall & (r >= p['deck_r'])) | ((np.abs(y - bay['y'][0]) <= 3.0) & (x > bay['x_back'])
                                                   & (r < p['deck_r']))
        put(np.where(wall, skirt_z(r, p), 0.0), DOCKWALL)
    # ---- the flare stack: a copper cone on the skirt behind the deck, the grey stack, two collars, a domed top;
    #      build-up: the cone rises, then the stack out of it (its collars go on as it passes them)
    st = p['stack']
    sdx, sdy = x - st['c'][0], y - st['c'][1]
    sr = np.hypot(sdx, sdy)
    z0, r0, z1, r1 = st['cone']
    if g['cone'] > 0:
        z1g = z0 + (z1 - z0) * g['cone']
        cz = z0 + (z1 - z0) * np.clip((r0 - sr) / (r0 - r1), 0, 1)
        put(np.where(sr <= r0, np.minimum(np.where(sr <= r1, z1, cz), z1g), 0.0), CONE)
        if 'box' in st:
            hz0, hz1, hs = st['box']
            bo = st.get('box_off', (10.0, 10.0))
            hb = (np.abs(sdx - bo[0]) <= hs) & (np.abs(sdy - bo[1]) <= hs)
            put(np.where(hb, min(hz1, z1g), 0.0), STACK)
    if g['stack'] > 0:
        topg = z1 + (st['top'] - z1) * g['stack']
        put(np.where(sr <= st['r'], topg, 0.0), STACK)
        for (a_, b_) in st['collars']:
            if b_ <= topg + 0.5:
                slab(np.full_like(X, b_), np.full_like(X, a_), FLANGE, sr <= st['cr'], 'collar')
    if g['pipes'] > 0:
        sp = p['spipe']
        pr_ = np.hypot(x - sp['c'][0], y - sp['c'][1])
        put(np.where(pr_ <= sp['r'], sp['top'], 0.0), PIPE)
        b0, b1, br = sp['box']
        slab(np.full_like(X, b1), np.full_like(X, b0), PIPE, pr_ <= br, 'pipebox')
    # ---- on the deck: the flanged column at the centre on a gold ring, the tall column, the pipe off its top
    m_ = p['mid']
    if g['gear'] > 0:
        rin, rout, rh = m_['ring']
        teeth = (np.cos(np.radians(phi) * m_['teeth']) > 0.0)
        gear = (r <= rout) & (r >= rin) & ((r <= rout - 3) | teeth)
        stand(p['deck_z'] + rh, GOLD, gear, 'gear')
    if g['mid'] > 0:
        topm = p['deck_z'] + (m_['top'] - p['deck_z']) * g['mid']
        put(np.where(r <= m_['r'], topm, 0.0), COLUMN)
        for (a_, b_) in m_['collars']:
            if b_ <= topm + 0.5:
                slab(np.full_like(X, b_), np.full_like(X, a_), FLANGE, r <= m_['cr'], 'mcollar')
    t_ = p['tall']
    tr_ = np.hypot(x - t_['c'][0], y - t_['c'][1])
    if g['tall'] > 0:
        topt = p['deck_z'] + (t_['top'] - p['deck_z']) * g['tall']
        stand(topt, COLUMN, tr_ <= t_['r'], 'tall')
    if g['pipes'] > 0:
        tp = p['tpipe']
        tpr = np.hypot(x - tp['c'][0], y - tp['c'][1])
        stand(tp['top'], PIPE, tpr <= tp['r'], 'tpipe')
        # the pipe's bend from the column's top over to it
        ux, uy = tp['c'][0] - t_['c'][0], tp['c'][1] - t_['c'][1]
        L_ = np.hypot(ux, uy); ux, uy = ux / L_, uy / L_
        s_ = (x - t_['c'][0]) * ux + (y - t_['c'][1]) * uy
        n_ = -(x - t_['c'][0]) * uy + (y - t_['c'][1]) * ux
        arm = (s_ >= 0) & (s_ <= L_) & (np.abs(n_) <= tp['r'])
        slab(np.full_like(X, tp['top']), np.full_like(X, tp['top'] - 2 * tp['r']), PIPE, arm, 'tarm')
        # two black links from the flanged column to the tall one
        vx, vy = t_['c'][0] - cx, t_['c'][1] - cy
        Lv = np.hypot(vx, vy); vx, vy = vx / Lv, vy / Lv
        s2 = dx * vx + dy * vy
        n2 = -dx * vy + dy * vx
        link = (s2 >= 0) & (s2 <= Lv) & (np.abs(n2) <= 2.6)
        for zl in p['links']:
            slab(np.full_like(X, zl + 2.6), np.full_like(X, zl - 2.6), PIPE, link, 'link')
    # ---- the copper sphere (build-up: it rises out of the skirt) and its white cap
    sph = p['sphere']
    qx, qy, qz = sph['c']
    if g['sphere'] > 0:
        qd = np.hypot(x - qx, y - qy)
        qh = np.sqrt(np.clip(sph['r'] ** 2 - qd ** 2, 0, None))
        lift_ = (1.0 - g['sphere']) * 2.0 * sph['r']
        slab(qz + qh - lift_, qz - qh - lift_, SPHERE, (qd < sph['r']) & (qz + qh - lift_ > 0), 'sphere')
        if g['cap'] > 0:
            capr, caph = sph['cap']
            slab(np.full_like(X, qz + np.sqrt(sph['r'] ** 2 - capr ** 2) + caph * g['cap']), np.full_like(X, qz), CAP,
                 qd <= capr, 'cap')
    # ---- thin pipes on the west, standing behind the skirt
    if g['wpipes'] > 0:
        for i_, (wx, wy, wr, wt) in enumerate(p['wpipes']):
            if order(i_, 3.0) < g['wpipes']:
                put(np.where(np.hypot(x - wx, y - wy) <= wr, wt, 0.0), WPIPE)
    extra = {}
    # ---- the docked harvester itself (HARV, or HORV while it unloads), in the scene so the building hides what it
    #      should of it and their shadows fall on each other
    if truck is not None:
        # modelled on the part of the grid round the truck (its wheels etc. are many slabs: packed there first,
        # then placed on the full grid), its own frame (lx, ly) everywhere
        hv = truck['model']
        sub = _window(X, Y, truck['pos'], 31.0 * truck['s'] + 6.0)
        if sub is not None:
            rs, cs = sub
            tsc = merge_slabs(hv.scene(X[rs, cs], Y[rs, cs], frame=truck['frame'], pos=truck['pos'], s=truck['s'],
                                       unloading=truck['unloading']))
            Ht = np.zeros_like(H); Ht[rs, cs] = tsc.H
            Ct = np.zeros(X.shape, np.int16); Ct[rs, cs] = tsc.C
            put(Ht, (TRUCK_BASE + Ct).astype(np.int16), Ht > 0)
            for s_ in tsc.slabs:
                top = np.full(X.shape, -1.0, np.float32); top[rs, cs] = s_.top
                bot = np.zeros(X.shape, np.float32); bot[rs, cs] = s_.bot
                cp = np.zeros(X.shape, np.int16); cp[rs, cs] = np.where(s_.top >= 0, TRUCK_BASE + s_.comp, 0)
                slabs.append(hd.Slab(top, bot, cp, 'truck-' + s_.name))
            del tsc
        lx_, ly_ = hv.to_local(X, Y, truck['frame'], truck['pos'], truck['s'])
        extra['truck_lx'] = np.asarray(lx_, np.float32)
        extra['truck_ly'] = np.asarray(ly_, np.float32)
    # ---- the harvester's tank in the dock (NTREFN_A): on the docked HORV's bed (it never passes the truck's back
    #      end), so in the heightfield like HARV's own tank
    if lid is not None:
        hv = lid['model']
        tsc = hv.scene(X, Y, frame=lid['frame'], pos=lid['pos'], s=lid['s'], only='tank', tank_off=lid['off'])
        ls = tsc.slabs[0]
        keep = (ls.top >= 0) & (x >= lid['wall'])
        put(np.where(keep, ls.top, 0.0), (LID_BASE + ls.comp).astype(np.int16), keep)
        extra['lid_lx'] = tsc.extra['lx'].astype(np.float32)
        extra['lid_ly'] = tsc.extra['ly'].astype(np.float32)
    sc = hd.Scene(H, C, slabs, extra)
    return merge_slabs(sc) if merge else sc


LID_BASE = 100          # the lid's tank: harvester component ids + 100
# where the harvester docks (NTREFN_A's tank lines up with it): TS's (fitted to the docking video: 6 units east of
# the dock cell's centre, TS's harvester at 3.46 units per voxel); on the RA grid the same, nudged under a unit so the
# unit's 384x384 sprite lands on whole pixels (250, 340); both face east (mod frame 24, HORV 56)
DOCK = {'ts': dict(pos=(70.5, 1.5), s=3.46, frame=24), 'ra': dict(pos=(70.0, 0.458), s=3.46, frame=24)}
TANK_LEN = 21.5         # voxels: the tank slides back this far into the building (TS: 5 frames, the last a sliver)


def lid_args(layout, k, hv):
    """NTREFN_A frame k (0..9): the tank sliding back into the building (0-4), gone (5-9)."""
    if k >= 5:
        return None
    dk = DOCK[layout]
    wall = dk['pos'][0] + (0.0 - hv.CEN[0]) * dk['s']
    return dict(model=hv, frame=dk['frame'], pos=dk['pos'], s=dk['s'], off=k * TANK_LEN / 4.6, wall=wall)


TRUCK_BASE = 200        # the docked harvester in the scene: its component ids + 200


def truck_args(layout, unloading, hv):
    """the harvester docked: HARV (loaded, as it arrives) or HORV (unloading: its tank off, the lid slides it in)."""
    dk = DOCK[layout]
    return dict(model=hv, frame=dk['frame'], pos=dk['pos'], s=dk['s'], unloading=bool(unloading))


FLAT = {SKIRT: (120, 120, 120), RIB: (0, 200, 0), DECK: (30, 30, 30), RIM: (0, 230, 0), HOOD: (150, 70, 50),
        SPHERE: (170, 100, 80), CAP: (230, 230, 230), CONE: (170, 100, 80), STACK: (190, 190, 190),
        FLANGE: (20, 20, 20), PIPE: (10, 10, 10), COLUMN: (170, 170, 170), GOLD: (160, 130, 60),
        WPIPE: (170, 170, 170), DOCKWALL: (90, 40, 30), DOCKIN: (30, 30, 30), PAD: (200, 200, 190),
        STRIPE: (230, 150, 40), BASE: (60, 60, 60), LAMP: (0, 255, 0), LAMPBOX: (70, 70, 74), HOLE: (8, 8, 8)}
