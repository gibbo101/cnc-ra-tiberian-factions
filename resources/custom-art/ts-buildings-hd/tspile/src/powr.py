"""
TS GDI Power Plant (GAPOWR, TSPOWR in the mod) and its Power Turbine add-on (GAPOWRUP / GTPOWR_B, TSTURB),
rebuilt as one model for hd.py.

World: X east, Y south, units (1 cell = 128), origin at the centre of the 2x2 foundation.  Measured from
TS's GTPOWR frame 0 (TS camera: 30 degrees, looking north-west; ground centre at TS px (48, 72)):

  slab      light concrete, a clover of round pads over the four cells, 4 high
  sockets   on the SW, SE and NE cells: a sloped earthen mound (r 56 at the ground, 40 at the top, 25 high)
            with a dark steel rim, the green house-colour ring (outer r 38) and a blue-grey plate with four
            bolt holes (N/E/S/W) - the same socket as the Component Tower's top
  tower     on the NW cell: a dark steel drum (r 48, 43.5 high) with a door facing south-east; the green
            collar (r 51, 43.5-67.5) with vertical ribs and hanging green pipes at its west and east sides;
            the cooling tower cone (r 40 at 67.5 to r 22.6 at 171) in seven courses, rust-stained at the top,
            open at the top, a small dark window on its south face at ~117
  decks     raised dark steel walkways (top 25) from the drum to the NE and SW mounds, with light concrete
            fairings sweeping down to the slab on the side facing the middle (TS's pale "tusks" either side
            of the door)
  lamp      a small green dome on the slab in front of the door
  turbine   (the add-on) a grey bell-shaped housing on a socket's plate, a band of green windows turning under
            a small cap
"""
import numpy as np
import hd

(SLAB, MOUND, MRIM, RING, PLATE, DRUM, DOOR, DECK, FAIR, COLLAR, PIPE, CONE, CONEIN, LAMP, WINDOW,
 THOUSE, TBAND, TCAP) = range(1, 19)
HOUSE = {RING, COLLAR, PIPE, LAMP}

BUILD_KEYS = ('slab', 'pads', 'mound_ne', 'mound_sw', 'mound_se', 'drum', 'decks', 'pipes', 'cone', 'collar',
              'rings', 'plates', 'lamp', 'pod')
POD_UP = 0.8           # build-up: the east pod rises out of its mound over pod 0..0.8, then its ring comes
DONE = {k: 1.0 for k in BUILD_KEYS}

P = dict(
    slab_h=4.0, slab_r=50.0,
    sockets=((-64.0, 64.0), (64.0, 64.0), (64.0, -64.0)),     # SW, SE, NE (TS: W, S, E on screen)
    slots=((64.0, -64.0), (64.0, 64.0), (-64.0, 64.0)),        # turbine slots 1 (east), 2 (south), 3 (west)
    sock_z=25.0, mound_r0=52.5, mound_r1=43.5,                 # mound radius at the ground / at the top
    rim_r=44.0, ring_r=38.5, ring_w=7.0, ring_up=1.2,
    hole_at=19.5, hole_r=2.6, hole_d=3.0,
    tower=(-64.0, -64.0),
    drum_r=48.0, drum_h=43.5,
    collar_r=53.0, collar_z=(44.0, 70.0),
    cone_z=(67.5, 171.0), cone_r=(40.85, 21.75), courses=7, step=1.7, wall=3.2, cone_in=34.0,
    door_w=15.0, door_h=34.0, door_d=6.0, door_az=np.deg2rad(45.0),     # facing south-east
    window=(np.deg2rad(80.0), 133.0, 12.0, 13.0),                         # azimuth (from east, to south), z, w, h
    deck_z=25.0, deck_w=34.0, fair=22.0, deck_past=34.0,
    # the tower's lights (TS GTPOWR_A): four rings, measured from TS's pixels on the visible side
    lights_z=(76.0, 95.0, 127.0, 157.0), lights_az=tuple(np.deg2rad(a) for a in (-15, 25, 97, 165, 235, 305)),
    light_r=2.4,
    lamp=(-11.0, -11.0, 11.0, 7.0),
    pipes=tuple(np.deg2rad(a) for a in (124.0, 136.0, 148.0, -36.0, -50.0)),   # azimuths (x east, y south)
    pipe_r=56.5, pipe_w=1.5, pipe_z=(20.0, 72.0),
    turb=dict(r0=31.5, h=26.0, band_up=7.0, band_r=19.5, cap_r=14.0, cap_h=8.0, hatch=(np.deg2rad(8.0), 9.0, 8.0)),
)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def cone_radius(z, p=P):
    """the cone's outer radius at height z: seven courses, each a little narrower than the one below."""
    z0, z1 = p['cone_z']; r0, r1 = p['cone_r']
    t = np.clip((z - z0) / (z1 - z0), 0, 1)
    n = p['courses']
    k = np.minimum(np.floor(t * n), n - 1)
    # within a course the radius falls a little less than the taper; at each joint it steps in
    lin = r0 + (r1 - r0) * t
    within = t * n - k
    return lin + p['step'] * (within - 0.5)


def cone_height(d, p=P):
    """invert cone_radius: the height of the cone's outer surface over a ground point at distance d."""
    zs = np.linspace(p['cone_z'][0], p['cone_z'][1], 2048)
    rs = cone_radius(zs, p)
    # rs falls with z (monotonic); np.interp wants increasing x
    return np.interp(d, rs[::-1], zs[::-1], left=p['cone_z'][1], right=-1.0)


def box(X, Y, x0, x1, y0, y1):
    return (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1)


def scene(X, Y, p=P, prog=None, turbines=(), turb_angle=0.0):
    """prog: build-up controls (BUILD_KEYS, 0..1; None = finished).  turbines: slots with a pod (0 east, 1 south
    = the middle, 2 west); the plant always has the east one, the upgrades fill the middle, then the west."""
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

    tx, ty = p['tower']
    # ---- slab: the middle square first, then the round pads over the cells (TS: frames 1-6)
    if g['slab'] > 0:
        sm = (np.abs(X) <= 72 * g['slab']) & (np.abs(Y) <= 72 * g['slab'])
        if g['pads'] > 0:
            for (cx, cy) in list(p['sockets']) + [p['tower']]:
                sm |= np.hypot(X - cx, Y - cy) <= p['slab_r'] * min(1.0, 0.4 + 0.6 * g['pads'])
        put(np.full_like(X, p['slab_h']), SLAB, sm)

    # ---- socket mounds: sloped earthen sides, a dark steel rim, the ring and the plate
    z1 = p['sock_z']
    for (cx, cy), key in zip(p['sockets'], ('mound_sw', 'mound_se', 'mound_ne')):
        d = np.hypot(X - cx, Y - cy)
        m = g[key]
        if m <= 0:
            continue
        zt = p['slab_h'] + (z1 - p['slab_h']) * m
        ma = np.arctan2(Y - cy, X - cx)
        # a rough stone plinth: steep sides with a rounded top edge, the foot a little irregular
        wob = 1.2 * np.abs(np.sin(4 * ma + cx * 0.05)) + 0.9 * np.abs(np.sin(7 * ma + cy * 0.07)) - 1.0
        uu = np.clip((d - p['mound_r1']) / (p['mound_r0'] + wob - p['mound_r1']), 0, 1)
        side = zt - (zt - 0.0) * uu ** 2.4
        put(np.where(d <= p['mound_r0'] + wob, side, 0.0), MOUND)
        top = d <= p['rim_r']
        put(np.where(top, zt, 0.0), MRIM)
        rings, plates = g['rings'], g['plates']
        if prog is not None and key == 'mound_ne':
            # the east pod comes with the plant: its ring and plate come with it (TS's GTPOWRMK). Until it is up
            # the mound is hollow, a dark pit the pod rises out of
            rings = max(rings, float(np.clip((g['pod'] - POD_UP) / (1 - POD_UP), 0, 1)))
            plates = max(plates, 1.0 if g['pod'] >= POD_UP else 0.0)
            if g['pod'] < POD_UP:
                pit = d <= p['ring_r'] - p['ring_w']
                H = np.where(pit, zt - 6.0, H); C = np.where(pit, MRIM, C)
        if rings > 0:
            ring = (d <= p['ring_r']) & (d > p['ring_r'] - p['ring_w'])
            put(np.where(ring, zt + p['ring_up'] * rings, 0.0), RING)
        if plates > 0:
            inner = d <= p['ring_r'] - p['ring_w']
            holes = np.zeros_like(d, bool)
            for hx, hy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                holes |= np.hypot(X - cx - hx * p['hole_at'], Y - cy - hy * p['hole_at']) <= p['hole_r']
            hz = np.where(holes, zt - p['hole_d'], zt + 0.4)
            H = np.where(inner, hz, H); C = np.where(inner, PLATE, C)

    # ---- decks: raised walkways from the drum to the NE and SW mounds, fairings towards the middle
    if g['decks'] > 0:
        for (sx, sy), mkey in ((p['sockets'][2], 'mound_ne'), (p['sockets'][0], 'mound_sw')):
            ux, uy = sx - tx, sy - ty
            L = np.hypot(ux, uy); ux, uy = ux / L, uy / L
            al = (X - tx) * ux + (Y - ty) * uy                 # along the deck
            ac = -(X - tx) * uy + (Y - ty) * ux                # across (+: towards the middle of the plant)
            # the side facing the middle is the one on the side of the plant's centre
            cs = np.sign(-(0 - tx) * uy + (0 - ty) * ux)
            ac = ac * cs
            zt = p['slab_h'] + (p['deck_z'] - p['slab_h']) * g['decks']
            on = (al >= 0) & (al <= (L + p['deck_past'] * g[mkey]) * min(1.0, g['decks'] * 1.5))
            if prog is not None and mkey == 'mound_ne' and g['pod'] < POD_UP:
                on &= np.hypot(X - sx, Y - sy) > p['ring_r'] - p['ring_w']      # not across the east pod's pit
            top = on & (np.abs(ac) <= p['deck_w'] / 2)
            put(np.where(top, zt, 0.0), DECK)
            fr = on & (ac > p['deck_w'] / 2) & (ac <= p['deck_w'] / 2 + p['fair'])
            u = (ac - p['deck_w'] / 2) / p['fair']
            fz = p['slab_h'] + (zt - p['slab_h']) * np.cos(np.clip(u, 0, 1) * np.pi / 2) ** 0.8
            put(np.where(fr, fz, 0.0), FAIR)
            back = on & (ac < -p['deck_w'] / 2) & (ac >= -p['deck_w'] / 2 - 4)
            put(np.where(back, zt - 6.0, 0.0), DECK)

    # ---- the tower: drum (with the door), collar, cone
    dx, dy = X - tx, Y - ty
    d = np.hypot(dx, dy)
    az = np.arctan2(dy, dx)
    if g['drum'] > 0:
        dh = p['slab_h'] + (p['drum_h'] - p['slab_h']) * g['drum']
        # the door: a recess in the south-east face, under a lintel (the drum's outer ring is a slab)
        da = np.angle(np.exp(1j * (az - p['door_az'])))
        tang = np.abs(da) * d
        door = (tang <= p['door_w'] / 2) & (d > p['drum_r'] - p['door_d']) & (d <= p['drum_r']) & (np.abs(da) < np.pi / 2)
        core = d <= p['drum_r'] - p['door_d']
        put(np.where(core, dh, 0.0), DRUM)
        ring = (d <= p['drum_r']) & ~core
        dz = min(p['door_h'], dh)
        slab(np.full_like(X, dh), np.where(door, dz, 0.0), DRUM, ring & ~door | (ring & door & (dh > dz + 0.5)), 'drum')
        C = np.where(core & (tang <= p['door_w'] / 2) & (np.abs(da) < np.pi / 2) &
                     (d > p['drum_r'] - p['door_d'] - 2.5), DOOR, C)
        H = np.where(door & ~core, p['slab_h'], H); C = np.where(door & ~core, DOOR, C)
    if g['collar'] > 0:
        c0, c1 = p['collar_z']
        slab(np.full_like(X, c0 + (c1 - c0) * g['collar']), np.full_like(X, c0), COLLAR,
             d <= p['collar_r'], 'collar')
    if g['cone'] > 0:
        z0, z1_ = p['cone_z']
        ztop = z0 + (z1_ - z0) * g['cone']
        hc = np.minimum(cone_height(d, p), ztop)
        inside_r = cone_radius(ztop, p) - p['wall']
        hc = np.where(d <= inside_r, ztop - p['cone_in'], hc)
        put(np.where((d <= p['cone_r'][0] + 1.0) & (hc > 0), hc, 0.0), CONE)
        C = np.where((d <= inside_r) & (C == CONE), CONEIN, C)
    # the green pipes hanging at the collar's west and east sides
    if g['pipes'] > 0:
        pz0, pz1 = p['pipe_z']
        for a in p['pipes']:
            px_, py_ = tx + p['pipe_r'] * np.cos(a), ty + p['pipe_r'] * np.sin(a)
            dp = np.hypot(X - px_, Y - py_)
            slab(np.full_like(X, pz0 + (pz1 - pz0) * g['pipes']), np.full_like(X, pz0), PIPE, dp <= p['pipe_w'], 'pipe')
    # the lamp on the slab in front of the door
    if g['lamp'] > 0:
        lx, ly, lr, lh = p['lamp']
        dl = np.hypot(X - lx, Y - ly)
        put(np.where(dl <= lr, p['slab_h'] + lh * np.sqrt(np.clip(1 - (dl / lr) ** 2, 0, 1)), 0.0), LAMP)

    # ---- the pods (power turbines) on their sockets.  The east pod (slot 1) comes with the plant; in the
    # build-up it rises out of its mound, cap first (TS's GTPOWRMK), under the `pod` control
    rise = {s: 1.0 for s in turbines}
    if prog is not None and g['pod'] > 0:
        rise[0] = min(1.0, g['pod'] / POD_UP)
    drop_f = np.zeros_like(X)
    for s, u in rise.items():
        cx, cy = p['slots'][s]
        t = p['turb']
        dt = np.hypot(X - cx, Y - cy)
        z0 = p['sock_z'] + 0.4
        # still below the socket's top: whatever hasn't risen yet stays hidden inside the mound
        drop = (1.0 - u) * (t['h'] + t['band_up'] + t['cap_h'] + 1.0)
        z0 = z0 - drop
        drop_f = np.where(dt <= t['r0'] + 2.0, drop, drop_f)
        # a rounded dome housing, a band of windows standing up round its crown, a small cap on top
        hh = z0 + t['h'] * np.sqrt(np.clip(1 - (dt / t['r0']) ** 2, 0, 1))
        put(np.where(dt <= t['r0'], hh, 0.0), THOUSE)
        band = dt <= t['band_r']
        put(np.where(band, z0 + t['h'] + t['band_up'], 0.0), TBAND)
        capu = np.clip(1 - (dt / t['cap_r']) ** 2, 0, 1)
        put(np.where(dt <= t['cap_r'], z0 + t['h'] + t['band_up'] + t['cap_h'] * np.sqrt(capu), 0.0), TCAP)

    extra = dict(turb_angle=np.full_like(X, turb_angle), pod_drop=drop_f)
    return hd.Scene(H, C, slabs, extra)
