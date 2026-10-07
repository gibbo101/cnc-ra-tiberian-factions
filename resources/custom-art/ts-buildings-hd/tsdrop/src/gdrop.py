"""The Dropship Bay from TS's own cut art (GTDROP; GADROP in TS: Westwood cut it, its art stayed in the game files),
modelled in the building's own frame: x east, y south, z up, units (1 cell = 128), origin = the 3x3 foundation's ground
centre (TS draws the foundation's north corner at its 192x144 frame's centre, so the origin is TS px (96, 108)).

TS recycled the bay's east half into the Upgrade Center (GTPLUG): the long block with the house-green slope, the trim
band, the roof with the radar dish (GTDROP_A = GTPLUG_A's dish), the brown ramp at the east end with three pipes up it
and the raised deck on square feet are the same pixels in both, GTPLUG drawn 59 px left and 18 px up of GTDROP (TS's
pixels match there to within a shade).  So that half IS the signed-off Upgrade Center model (plug.py), moved into this
frame (plug's origin = (61.3, -61.3) here) with its deck stretched to the bay's (west to x -164, south to y 127) and
without its sockets, plugs, fork and tall antenna.  What the bay adds, its shapes from Luke's high-res picture of the bay
(inbox/dropship/screenshot) placed and sized to GTDROP 0 / GTDROPMK:
  guard     the jet blast guard: an L-shaped plate standing in a slot in the deck between the tower and the pad, running
            north-south: its back wall on the west leaning back, its floor sloping down to a lip on the east, ribs across
            both, end plates (TS: the dark ribbed trough)
  pad       the landing pad: a dark metal plate on the deck, a hexagon long along x and pointed at its west and east ends,
            a light rim with B's four light strips on it, tan lines from its corners into a centre square, panel seams
  ramp      down from the deck's south edge to the ground: a dark plate between raised side rails, a hinge beam along its
            top, diagonal hazard stripes in house colour across its middle (TS's green stripes)
  west      the tower on the deck's west strip: its body (tan panels, TS's blue-grey band under the eaves), the tall
            console with its sloped east face (where the picture has GDI's emblem: left off), two raised blocks on its
            ridge with a notch between (a louvred vent on the south one), the south gable face and the lean-to north of
            it house green (TS), a pipe down the gable
  notch     TS's grey slope in the deck's north-west notch, rising to a ledge at the back
  ledge     the tan beam along the deck's south-west edge (TS's bright beam), a thick column under its west end
  antennas  two on the block's east end (plug's two there), two on the tower
"""
import copy
import numpy as np
import hd
import plug as PL
from radr import Acc, rod_interval, inbox, dblob
import wnoise as WN

OFF = (61.3, -61.3)                 # plug's origin in this frame

# the bay's own components (plug's are 1-28, 40-42, 50-78).  (PIT, PITW, PADM: no longer used)
PIT, PITW, RAMP2, RAMPS, WBODY, WTRIM, WROOFG, WCROWN, NWALL, ANT2, PADM, RAIL = range(80, 92)
GUARD, GRIB, GSLOT, PADP, PADR, RAMPR, TOPB, VENT, PIPEW, COLW = range(92, 102)
HOUSE = set(PL.HOUSE) | {WROOFG, RAMPS}


def plug_params():
    # v4 (Luke, 7 Oct 2026: "dropship bay is the upgrade center with attached buildings to the left", "straighten out
    # the right hand wall like we did with the upgrade center"): the Upgrade Center's current model (its square east
    # end, its west hip), keeping the bay's own west end: TS's notch, the roof running on west over the guard
    q = copy.deepcopy(PL.P)
    v3 = PL.P_BAY
    q['deck']['x0n'] = v3['deck']['x0n']
    for k in ('x_roof', 'x_ledge', 'x_low'):
        q['block'][k] = v3['block'][k]
    q['slope']['x'] = v3['slope']['x']
    xw_ = v3['block']['x_roof'][0]
    q['block']['hipw'] = dict(x0=xw_ + 30.0, x1=xw_, zw=82.0)       # the overhang's end hips down, as the east end
    # Luke: "maybe a support pillar under the overhang in the left corner": under its south-west corner
    # (Luke 17:52: "bring it to the front left corner": flush with the overhang's front-left corner, the ledge's end)
    q['block']['pillar'] = dict(c=(v3['block']['x_ledge'][0] + 5.5, v3['block']['ledge'][0] - 5.5), a=5.5, z0=0.0)
    d = q['deck']
    d['x0'] = -225.0                 # the bay's deck runs on west (TS: the west block's strip)
    d['x1s'] = d['x1']               # its east edge straight (the Upgrade Center's narrows south of y 50)
    d['y1'] = 188.0                  # and south to the ramp
    q['feet'] = dict(pts=((-211.0, 173.0), (-125.0, 173.0), (-10.0, 173.0), (104.0, 173.0), (104.0, 29.0),
                          (104.0, -112.0), (-88.0, -112.0), (-211.0, 2.0)), a=10.5)
    q['step'] = dict(x=(0.0, -1.0), y=(0.0, -1.0), h=0.0, n=1)       # (none: the ramp is there)
    q['sockets'] = dict(q['sockets'], c=())
    return q


P = dict(
    plug=plug_params(),
    # the jet blast guard: y run, the floor's lip (east) and foot, the wall's top edge (it leans back to the west), the
    # slot round it (x0, x1, y0, y1, its floor), ribs across every per units (width, height), end plates, the top's cap
    guard=dict(y=(-66.0, 86.0), x_lip=-38.0, x_foot=-80.0, x_top=-94.0, z_lip=34.0, z_foot=39.0, z_top=64.0,
               slot=(-104.0, -33.0, -71.0, 91.0, 22.0), per=25.33, rib=(2.4, 1.5), end=(3.0, 3.0), cap=1.8),
    # the landing pad: centre, half length (to the tips) and width, the tips' depth, its height over the deck, the rim,
    # the centre square's half size, the tan lines' width, B's four light strips on the rim (W and E: the tips' edges;
    # N and S: the middle of the long edges)
    pad=dict(c=(70.0, 47.0), half=(80.0, 46.0), tip=32.0, h=1.6, rim=4.5, sq=14.0, line=1.4,
             bars=dict(band=(0.9, 3.6), ns=0.55)),
    # the ramp: plate x/y, side rails (width, height), the hinge beam (y0, y1, height), plain end sections, hazard
    # stripes (period along x, fill, angle to the x axis in degrees)
    ramp=dict(x=(-19.0, 135.0), y=(126.0, 192.0), rail=(6.0, 3.5), hinge=(123.0, 133.0, 4.5), ends=7.0,
              stripes=dict(per=21.0, fill=0.62, ang=30.0)),
    # the tower: its body to the eaves (TS's blue-grey band above z), the gable roof (ridge along y), the lean-to north of
    # it; two raised blocks on the ridge (x, (y0, y1) each, their tops) with a vent on the south one's east face; a pipe
    west=dict(x=(-187.0, -106.0), y=(-9.0, 81.0), z=60.0, trim=6.0, over=3.0, ridge=142.0, gable=2.0,
              annex=dict(x=(-187.0, -150.0), y=(-80.0, -9.0), z0=120.0, z1=80.0, axis='y'),
              tops=dict(x=(-157.0, -137.0), y=((-12.0, 25.0), (32.0, 84.0)), z=(151.0, 149.0), notch=131.0),
              vent=dict(x=(-139.0, -126.0), y=(41.0, 77.0), z=(104.0, 129.0)),
              pipe=((-179.0, 86.5, 36.0), (-179.0, 86.5, 96.0), (-161.0, 86.5, 128.0)), pipe_r=1.7),
    notchwall=dict(x=(-178.0, -40.0), y=(-150.0, -70.0), z0=33.5, z1=60.0, ytop=-112.0, para=(4.0, 6.0)),
    ants=((-183.0, 80.0, 116.0, 1.6), (-150.0, -40.0, 168.0, 1.6)),
    # the tan ledge along the deck's south-west edge (TS's bright beam): its south and west legs (x, y, width), how far
    # it stands out past the deck's edges, its depth under the deck's top and its top over it; the column
    rail=dict(x=(-170.0, -19.0), y=(-9.0, 127.0), w=9.0, out=5.0, h=11.0, top=1.5, col=(-167.0, 124.0, 7.0)),
)


_PLUG_CACHE = {}

# the build-up's parts (0..1 each; gdropbuild.py orders them).  plug.py's own: deck (grows from its middle), marks
# (its painted outlines), block (the east block rises), dish, ants (unused: the bay draws its own antennas), pipes, paint
# (the slope's panes: bare frames, grey, green).  The bay's: house (the walls rise), hroof (its roof, the raised blocks),
# lean (the lean-to), wall (the slope in the notch), ramp, guard (the jet blast guard rises out of its slot), grille (its
# ribs), padm (the pad plate's markings: materials), bpaint (the bay's house-colour parts: 0 bare, 0.5 grey, 1 house
# green), bants (the antennas grow up), rail (the ledge)
BUILD_KEYS = ('deck', 'marks', 'block', 'collar', 'plates', 'dish', 'ants', 'pipes', 'paint',
              'house', 'hroof', 'lean', 'wall', 'ramp', 'grille', 'padm', 'bpaint', 'bants', 'rail', 'guard')
DONE = {k: 1.0 for k in BUILD_KEYS}
DONE['marks'] = 0.0

# the damaged state (GTDROP 1), as TS breaks it.  The east block's is plug.DMG's (the same art: TS draws the Upgrade
# Center's damage there, all but its knocked-in pane: GTDROP 1's slope is whole)
PLUG_DMG = dict(PL.DMG, pane=(9999.0, 9999.0, 1.0, 1.0))
DMG = dict(
    # the house's east roof slope burnt open over its south and middle part (TS: dark red-brown framework, rafters across;
    # the north end of the ridge left standing, the gable end whole)
    roof=dict(c=(-128.0, 34.0), r=(26.0, 44.0), rough=0.3, floor=8.0),
    rafters=(((-146.0, 4.0, 136.0), (-104.0, 4.0, 70.0)), ((-146.0, 26.0, 136.0), (-104.0, 26.0, 70.0)),
             ((-146.0, 48.0, 136.0), (-104.0, 48.0, 70.0)), ((-146.0, 68.0, 134.0), (-110.0, 68.0, 76.0)),
             ((-140.0, -6.0, 120.0), (-120.0, 74.0, 96.0))),
    rafter_r=1.8,
    # the ramp broken through at its west middle (TS: a hole, its edge bent down, chunks)
    ramp=dict(c=(24.0, 166.0), r=(30.0, 18.0), rough=0.4),
)


def to_local(X, Y, layout='ts'):
    return X, Y


def scene(X, Y, p=None, layout='ts', prog=None, level=0, dish_az=None, shadow=False, **kw):
    p = P if p is None else p
    g = dict(DONE); g.update(prog or {})
    x, y = to_local(X, Y, layout)
    pprog = {k: g[k] for k in ('deck', 'marks', 'block', 'collar', 'plates', 'dish', 'ants', 'pipes', 'paint')}
    key = (x.shape, float(x.flat[0]), float(x.flat[-1]), float(y.flat[0]), float(y.flat[-1]), id(p['plug']), level,
           repr(sorted(pprog.items())), dish_az)
    if key not in _PLUG_CACHE:
        if len(_PLUG_CACHE) > 3:
            _PLUG_CACHE.clear()
        keep = PL.DMG
        PL.DMG = PLUG_DMG
        try:
            _PLUG_CACHE[key] = PL.scene(x - OFF[0], y - OFF[1], p=p['plug'], layout='ts', prog=pprog, level=level,
                                        dish_az=dish_az, shadow=True)
        finally:
            PL.DMG = keep
    sc = _PLUG_CACHE[key]
    H, C = sc.H.copy(), sc.C.copy()
    extra = dict(sc.extra)
    zt = p['plug']['deck']['zt']
    zb = p['plug']['deck']['zb']
    acc = Acc(X.shape, n=3)
    if g['deck'] < 1:                                   # the slab alone while it grows
        return hd.Scene(H, C, list(sc.slabs), extra)

    def put(h, comp, where=None):
        nonlocal H, C
        if where is not None:
            h = np.where(where, h, -1.0)
        win = h > H + 1e-6
        H = np.where(win, h, H); C = np.where(win, comp, C)

    # ---- the jet blast guard in its slot (the build-up: the slot first, then the guard rises out of it, then its ribs)
    gd = p['guard']
    rise = float(np.clip((float(g['guard']) - 0.25) / 0.75, 0, 1))     # (guard 0..0.25: the slot is cut; then it rises)
    if g['guard'] > 0:
        sx0, sx1, sy0, sy1, sz = gd['slot']
        slot = inbox(x, y, (sx0, sx1), (sy0, sy1)) & (H >= zt - 0.5) & (C == PL.PLAT)
        H = np.where(slot, sz, H); C = np.where(slot, GSLOT, C)
    if rise > 0:
        y0, y1 = gd['y']
        iny = (y >= y0) & (y <= y1)
        prof, onfl = guard_profile(x, gd)
        inside = iny & (x >= gd['x_top']) & (x <= gd['x_lip'])
        rib = (np.mod(y - y0, gd['per']) < gd['rib'][0]) & (float(g['grille']) > 0)
        hz = gd['slot'][4] + (prof + rib * gd['rib'][1] * float(g['grille']) - gd['slot'][4]) * rise
        H = np.where(inside, hz, H); C = np.where(inside, np.where(rib, GRIB, GUARD), C).astype(np.int16)
        # the end plates: the profile's outline, a few units proud of it
        e_t, e_h = gd['end']
        for ye in (y0, y1 - e_t):
            em = inbox(x, y, (gd['x_top'] - 0.5, gd['x_lip'] + 0.5), (ye, ye + e_t))
            he = gd['slot'][4] + (prof + e_h - gd['slot'][4]) * rise
            H = np.where(em, he, H); C = np.where(em, GRIB, C).astype(np.int16)
        # a rounded cap along the wall's top edge
        lo, hi, mm = rod_interval(x, y, (gd['x_top'] + 1.0, y0, gd['slot'][4] + (gd['z_top'] - gd['slot'][4]) * rise),
                                  (gd['x_top'] + 1.0, y1, gd['slot'][4] + (gd['z_top'] - gd['slot'][4]) * rise), gd['cap'])
        acc.add(lo, hi, GRIB, mm, 'gcap')
    # ---- the landing pad: a dark metal plate on the deck (the build-up: laid with the deck's markings)
    if g['padm'] > 0:
        hp = pad_height(x, y, zt, p)
        on = (hp > 0) & (C == PL.PLAT) & (H >= zt - 0.5)
        H = np.where(on, hp, H); C = np.where(on, PADP, C).astype(np.int16)
    # ---- the tan ledge along the deck's south-west edge (TS's bright beam): a thick fascia beam a little proud of the
    # deck's edges, its west end out past the deck on a thick column
    if g['rail'] > 0:
        rl = p['rail']
        o_ = rl['out']
        onrail = (inbox(x, y, (rl['x'][0] - o_, rl['x'][1]), (rl['y'][1] - rl['w'], rl['y'][1] + o_)) |
                  inbox(x, y, (rl['x'][0] - o_, rl['x'][0] + rl['w']), rl['y']))
        hl = zt - rl['h'] + (rl['h'] + rl['top']) * float(g['rail'])
        acc.add(zt - rl['h'], hl, RAIL, onrail, 'ledge')
        cx_, cy_, cr_ = rl['col']
        cm = (x - cx_) ** 2 + (y - cy_) ** 2 <= cr_ ** 2
        acc.add(0.0, zt - rl['h'], COLW, cm, 'column')
    # ---- the ramp from the deck's south edge down to the ground (the build-up: it reaches out from the deck): a dark
    # plate between raised side rails, a hinge beam along its top edge, hazard stripes (house colour) across its middle
    r = p['ramp']
    if g['ramp'] > 0:
        y1 = r['y'][0] + (r['y'][1] - r['y'][0]) * float(g['ramp'])
        rm = inbox(x, y, r['x'], (r['y'][0] - 2.0, y1))
        hr = zt * np.clip((r['y'][1] - y) / (r['y'][1] - r['y'][0]), 0, 1)
        rw, rh = r['rail']
        rail_ = (x - r['x'][0] < rw) | (r['x'][1] - x < rw)
        hrr = hr + np.where(rail_, rh, 0.0)
        st = r['stripes']
        a_ = np.deg2rad(st['ang'])
        mid = ~rail_ & (x - r['x'][0] >= rw + r['ends']) & (r['x'][1] - x >= rw + r['ends'])
        ph = np.mod((x * np.sin(a_) - y * np.cos(a_)) / (st['per'] * np.sin(a_)), 1.0)
        stripe = mid & (ph < st['fill'])
        cr_ = np.where(rail_, RAMPR, np.where(stripe, RAMPS, RAMP2)).astype(np.int16)
        if level >= 1:                                  # broken through at its west middle
            dm = DMG['ramp']
            eh = dblob(x, y, dm['c'][0], dm['c'][1], dm['r'][0], dm['r'][1], dm['rough'], 3101, feat=6.0)
            hole = rm & (eh < 0) & ~rail_
            rim = rm & (eh >= 0) & (eh < 0.25) & ~rail_
            hrr = np.where(hole, np.minimum(hrr, 2.0 + 3.0 * np.clip(-eh, 0, 1)), hrr)
            hrr = np.where(rim, hrr - 3.0 * (0.25 - eh) / 0.25, hrr)
            cr_ = np.where(hole, PL.DEB_IN, np.where(rim, PL.BEAM, cr_)).astype(np.int16)   # (its torn edge: bare steel)
        win = rm & (hrr > H + 1e-6)
        H = np.where(win, hrr, H); C = np.where(win, cr_, C)
        # the hinge beam along the top edge (on the deck's edge)
        hy0, hy1, hh = r['hinge']
        hm = inbox(x, y, (r['x'][0], r['x'][1]), (hy0, hy1)) & (y <= y1 + 2.0)
        hb = zt + hh * np.sqrt(np.clip(1.0 - ((y - 0.5 * (hy0 + hy1)) / (0.5 * (hy1 - hy0))) ** 2, 0, 1))
        put(np.where(hm, hb, -1.0), RAMPR)
    # ---- the tower: its body to the eaves (the top band, z > w['z'], is the trim: by height), the gable roof (a slab:
    # its gable ends house green), the raised blocks on the ridge, the lean-to north of it, a pipe down the south gable
    w = p['west']
    wb = inbox(x, y, w['x'], w['y'])
    ze = w['z'] + w['trim']
    hs = float(g['house'])
    if hs > 0:
        put(np.where(wb, zt + (ze - zt) * hs, -1.0), WBODY)
    if g['hroof'] > 0:
        ov = w['over']
        rx = (w['x'][0] - ov, w['x'][1] + ov); ry = (w['y'][0] - ov, w['y'][1] + ov)
        xc = 0.5 * (rx[0] + rx[1]); hw = 0.5 * (rx[1] - rx[0])
        rf = inbox(x, y, rx, ry)
        zr = ze + (w['ridge'] - ze) * float(g['hroof']) * np.clip(1.0 - np.abs(x - xc) / hw, 0, 1)
        gab = rf & ((y - ry[0] < w['gable']) | (ry[1] - y < w['gable']))
        rc = np.where(gab, WROOFG, WCROWN).astype(np.int16)
        burn = np.zeros(x.shape, bool)
        if level >= 1:                                  # the east face burnt open over its south and middle part
            dm = DMG['roof']
            eh = dblob(x, y, dm['c'][0], dm['c'][1], dm['r'][0], dm['r'][1], dm['rough'], 3111, feat=8.0)
            burn = rf & (eh < 0) & (x > xc - 6.0) & ~gab
            zr = np.where(burn, ze + dm['floor'] + 3.0 * WN.noise(x, y, 7.0, 3112), zr)
            rc = np.where(burn, PL.DEB_BURNT, rc).astype(np.int16)
            for (b0, b1) in DMG['rafters']:
                lo, hi, mm = rod_interval(x, y, b0, b1, DMG['rafter_r'])
                acc.add(lo, hi, PL.BEAM, mm, 'rafter')
        # the two raised blocks on the ridge (the picture's), a notch between them cut down into the roof
        tp = w['tops']
        nm_ = rf & (y > tp['y'][0][1]) & (y < tp['y'][1][0])
        zr = np.where(nm_, np.minimum(zr, tp['notch']), zr)
        for k, (ty0, ty1) in enumerate(tp['y']):
            tm = inbox(x, y, tp['x'], (ty0, ty1)) & ~burn
            ztop = w['ridge'] + (tp['z'][k] - w['ridge']) * float(g['hroof'])
            east = np.clip((x - (tp['x'][1] - 5.0)) / 5.0, 0, 1)            # its east edge chamfered
            west = np.clip(((tp['x'][0] + 3.0) - x) / 3.0, 0, 1)
            hz_ = ztop - 4.0 * east - 2.0 * west
            acc.add(ze, hz_, TOPB, tm, 'tops')
        acc.add(ze - 1.0, zr, rc, rf, 'roof')
        # the louvred vent on the console's east face under the south block: dark slats across it
        vt = w['vent']
        vm = inbox(x, y, vt['x'], vt['y']) & ~burn & (zr > vt['z'][0]) & (zr < vt['z'][1])
        put(np.where(vm, zr + 0.8, -1.0), VENT)
    # the lean-to north of it: house green, from under the north gable down to the north
    if g['lean'] > 0:
        an = w['annex']
        am = inbox(x, y, an['x'], an['y'])
        if an.get('axis', 'y') == 'y':
            fa = np.clip((y - an['y'][0]) / (an['y'][1] - an['y'][0]), 0, 1)
        else:
            fa = np.clip((x - an['x'][0]) / (an['x'][1] - an['x'][0]), 0, 1)
        za = an['z1'] + (an['z0'] - an['z1']) * fa
        put(np.where(am, zt + (za - zt) * float(g['lean']), -1.0), WROOFG)
    # the pipe down the south gable (the picture's)
    if g['pipes'] > 0 and hs >= 1:
        pts = w['pipe']
        for a0, a1 in zip(pts[:-1], pts[1:]):
            lo, hi, mm = rod_interval(x, y, a0, a1, w['pipe_r'])
            acc.add(lo, hi, PIPEW, mm, 'wpipe')
    # ---- TS's grey slope in the notch, rising to a ledge at the back
    if g['wall'] > 0:
        nw = p['notchwall']
        nm = inbox(x, y, nw['x'], nw['y'])
        hn = nw['z0'] + (nw['z1'] - nw['z0']) * np.clip((nw['y'][1] - y) / (nw['y'][1] - nw['ytop']), 0, 1)
        put(zt + (hn - zt) * float(g['wall']), NWALL, nm)
        pw, ph_ = nw['para']
        pm_ = inbox(x, y, nw['x'], (nw['y'][0], nw['y'][0] + pw)) | inbox(x, y, (nw['x'][0], nw['x'][0] + pw), (nw['y'][0], nw['ytop']))
        put(np.where(pm_, zt + (nw['z1'] + ph_ - zt) * float(g['wall']), -1.0), RAMPR)
    # ---- antennas (the build-up: they grow up); damaged: the east block's nearer one knocked off (as plug's)
    ga = float(g['bants'])
    if not shadow and ga > 0:
        for (ax, ay, az, ar) in p['ants']:
            if not hs:
                continue
            z0_ = w['z'] - 1.0
            lo, hi, mm = rod_interval(x, y, (ax, ay, z0_), (ax, ay, z0_ + (az - z0_) * ga), ar)
            acc.add(lo, hi, ANT2, mm, 'ant')
        for i_a in (4, 5):
            if level >= 1 and i_a in PLUG_DMG['ants_gone']:
                continue
            ax, ay, az, ar = PL.P['ants'][i_a]
            ax, ay = ax + OFF[0], ay + OFF[1]
            zr0 = PL.P['block']['z'] - 1.0
            lo, hi, mm = rod_interval(x, y, (ax, ay, zr0), (ax, ay, zr0 + (az - zr0) * ga), ar)
            acc.add(lo, hi, ANT2, mm, 'ant')
    return hd.Scene(H, C, list(sc.slabs) + acc.slabs(), extra)


def frustum(x, y, b, t, z0, z1):
    """a hip-roofed mass: z0 at the base rectangle b's edge rising linearly to z1 over the top rectangle t (inside b);
    -1 outside b.  Returns the height and the side (0 west, 1 east, 2 north, 3 south, 4 top)."""
    bx0, bx1, by0, by1 = b
    tx0, tx1, ty0, ty1 = t
    fw = np.clip((x - bx0) / max(tx0 - bx0, 1e-6), 0, 1)
    fe = np.clip((bx1 - x) / max(bx1 - tx1, 1e-6), 0, 1)
    fn = np.clip((y - by0) / max(ty0 - by0, 1e-6), 0, 1)
    fs = np.clip((by1 - y) / max(by1 - ty1, 1e-6), 0, 1)
    f = np.minimum(np.minimum(fw, fe), np.minimum(fn, fs))
    side = np.argmin(np.stack([fw, fe, fn, fs]), 0)
    side = np.where(f >= 1.0, 4, side)
    inside = (x >= bx0) & (x <= bx1) & (y >= by0) & (y <= by1)
    return np.where(inside, z0 + (z1 - z0) * f, -1.0), side


def guard_profile(x, gd):
    """the jet blast guard's height across it (x): the floor from its lip up to the foot, the wall from the foot up to its
    top edge (leaning back to the west); and whether x is on the floor."""
    onfl = x >= gd['x_foot']
    zf = gd['z_lip'] + (gd['z_foot'] - gd['z_lip']) * np.clip((gd['x_lip'] - x) / (gd['x_lip'] - gd['x_foot']), 0, 1)
    zw = gd['z_foot'] + (gd['z_top'] - gd['z_foot']) * np.clip((gd['x_foot'] - x) / (gd['x_foot'] - gd['x_top']), 0, 1)
    return np.where(onfl, zf, zw), onfl


def pad_shape(x, y, p=None):
    """the landing pad plate, a hexagon long along x and pointed at its west and east ends: (inside, d = units to the
    nearest edge (>= 0 inside), u, v from its centre)."""
    p = P if p is None else p
    pd = p['pad']
    hx, hy = pd['half']
    u = x - pd['c'][0]; v = y - pd['c'][1]
    k = pd['tip'] / hy
    d_long = hy - np.abs(v)
    d_tip = (hx - np.abs(u) - k * np.abs(v)) / np.sqrt(1.0 + k * k)
    d = np.minimum(d_long, d_tip)
    return d >= 0, d, u, v


def pad_marks(x, y, p=None):
    """the pad plate's markings: 0 plate, 1 rim, 2 tan line, 3 the centre square's outline, 4 a panel seam, 5 inside the
    square; 10-13 B's light strips on the rim (W, N, E, S); -1 off the plate.  And along each strip, 0..1."""
    p = P if p is None else p
    pd = p['pad']
    inside, d, u, v = pad_shape(x, y, p)
    hx, hy = pd['half']
    L = hx - pd['tip']                                   # the long edges run u -L..L
    out = np.where(inside, 0, -1).astype(np.int8)
    au, av = np.abs(u), np.abs(v)
    sq = pd['sq']
    lw = pd['line']
    # panel seams: across at the long edges' ends, along the middle of each half
    seam = inside & ((np.abs(au - L) < 0.6) | ((np.abs(av - hy * 0.5) < 0.6) & (au < L)))
    out[seam] = 4
    # tan lines: from the square's corners out to the long edges' ends, from its west/east sides out to the tips
    def seg(ax, ay, bx, by):
        dx, dy = bx - ax, by - ay
        t = np.clip(((u - ax) * dx + (v - ay) * dy) / (dx * dx + dy * dy), 0, 1)
        return np.hypot(u - ax - t * dx, v - ay - t * dy) < lw
    lines = np.zeros(np.shape(x), bool)
    for sx_ in (-1, 1):
        for sy_ in (-1, 1):
            lines |= seg(sx_ * sq, sy_ * sq, sx_ * L, sy_ * hy)
        lines |= seg(sx_ * sq, 0.0, sx_ * hx, 0.0)
    out[inside & lines & (np.maximum(au, av) > sq)] = 2
    insq = (au <= sq) & (av <= sq)
    out[insq] = 5
    out[insq & (np.maximum(au, av) > sq - 2.2)] = 3
    out[inside & (d < pd['rim'])] = 1
    # B's strips on the rim: W / E the tips' two edges, N / S the middle of the long edges
    b = pd['bars']
    band = inside & (d >= b['band'][0]) & (d <= b['band'][1])
    tipz = au > L
    along = np.zeros(np.shape(x), np.float32)
    out[band & tipz & (u < 0)] = 10
    out[band & tipz & (u > 0)] = 12
    mid = ~tipz & (au <= L * b['ns'])
    out[band & mid & (v < 0)] = 11
    out[band & mid & (v > 0)] = 13
    along = np.where(tipz, (v + hy) / (2 * hy), (u + L * b['ns']) / (2 * L * b['ns']))
    return out, np.clip(along, 0, 1)


def pad_height(x, y, zt, p=None):
    """the pad plate's top (the rim bevelled down to the deck), -1 off it."""
    p = P if p is None else p
    pd = p['pad']
    inside, d, u, v = pad_shape(x, y, p)
    return np.where(inside, zt + pd['h'] * np.clip(0.4 + d / 1.5, 0, 1), -1.0)


def flat_extra(r, alb):
    """the flat fit's colours by height and place: the tower's trim band under its eaves, the pad plate's markings."""
    w = P['west']
    band = (r.comp == WBODY) & (r.z > w['z']) & (r.z <= w['z'] + w['trim'] + 0.5)
    alb[band] = FLAT[WTRIM]
    pm, _ = pad_marks(r.x, r.y)
    pad = r.comp == PADP
    alb[pad & (pm == 1)] = (150, 150, 156)
    alb[pad & (pm == 2)] = (170, 140, 80)
    alb[pad & (pm >= 10)] = (150, 150, 200)
    return alb


FLAT = dict(PL.FLAT)
FLAT.update({PIT: (70, 70, 72), PITW: (90, 90, 92), RAMP2: (140, 140, 165), RAMPS: (0, 200, 0), WBODY: (180, 130, 60),
             WTRIM: (140, 140, 200), WROOFG: (0, 200, 0), WCROWN: (215, 175, 100), NWALL: (165, 165, 165),
             ANT2: (90, 90, 130), PADM: (110, 110, 110), RAIL: (200, 150, 70),
             GUARD: (88, 88, 92), GRIB: (110, 110, 116), GSLOT: (40, 40, 44), PADP: (84, 84, 90), PADR: (150, 150, 156),
             RAMPR: (96, 96, 112), TOPB: (215, 175, 100), VENT: (50, 50, 56), PIPEW: (170, 170, 176), COLW: (180, 140, 70)})
