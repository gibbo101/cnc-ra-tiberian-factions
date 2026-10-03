"""
TS Firestorm Wall Section (Firestorm GAFSDF; TSFSDF in the mod) as a model for hd.py: one cell, joining its
neighbours (mask N1 E2 S4 W8, as RA's walls), read from GTFSDF / GTFSDF_A in TS's own camera.

Built in the cell's own frame ("local": x east, y south, z up, origin at the cell's ground centre, x, y -64..64):
  pad       a low steel pad in the middle of the cell, its rim raised, the emitter in a round dark dish in its middle:
            a trident standing up in it (a short bar and three prongs, facing the camera: TS draws it face-on)
  arms      a grating bridge from the pad to the cell's edge on every side with a neighbour (steel rails with
            brackets on their outer sides, chunky rungs over dark gaps, six to a cell), so a run joins edge to edge
  straight  a section with neighbours on two opposite sides only (N-S or E-W) is all grating, no pad (as TS's 5, 10)
live=True: the field is on (TS 32-47): the rims, the grating's bars and the dish glow blue.
"""
import numpy as np
import hd
from radr import rod_interval
from plug import CropAcc, pack_slabs

(PAD, RIM, DISH, HUB, PRONG, GRATE, RAIL, BASE) = range(1, 9)
HOUSE = set()

P = dict(
    pad=dict(a=39.0, h=5.0, bevel=2.0, rim=dict(w=5.0, up=1.6)),
    dish=dict(r=21.0, sink=2.0, ring=dict(r=(17.0, 20.5), up=1.0), band=26.0),
    hub=dict(len=26.0, d=4.0, h=3.0),                    # the trident's bar, lying across the dish
    prongs=dict(n=3, gap=9.5, w=2.8, h=(12.5, 16.5, 12.5), tip=3.0),  # three prongs standing on it, the middle tallest
    arm=dict(w=73.0, h=4.0, rail=dict(w=3.5, up=2.2), bars=dict(every=128.0 / 6, w=10.5), base_h=0.8,
             bracket=dict(every=32.0, at=16.0, len=4.5, out=3.0)),
)

DIRS = {1: (0.0, -1.0), 2: (1.0, 0.0), 4: (0.0, 1.0), 8: (-1.0, 0.0)}      # N, E, S, W in local (x east, y south)
EDGE = 64.0
# the trident faces the camera: across the TS camera's line in TS's view (its bar north-east to south-west), across
# RA's (its bar east-west) on the RA grid
LAYOUTS = {'ts': dict(turn=False, face=45.0), 'ra': dict(turn=False, face=90.0)}
BUILD_KEYS = ('base', 'pad', 'dish', 'arms', 'paint')
DONE = {k: 1.0 for k in BUILD_KEYS}


def to_local(X, Y, layout='ts'):
    return X, Y


def straight(mask):
    return mask in (5, 10)


def arm_box(x, y, d, a, w):
    """the arm's footprint towards d from the pad's edge a to the cell's edge, w wide: (along, across, mask)."""
    dx, dy = d
    along = x * dx + y * dy
    across = -x * dy + y * dx
    return along, across, (along >= a - 1.0) & (along <= EDGE) & (np.abs(across) <= w / 2.0)


def rung_mask(run, bw):
    """the rungs across a grating: run = the coordinate along the run; the same phase everywhere, so the rungs of
    neighbouring sections line up."""
    ph = np.mod(run + bw['every'] / 2.0, bw['every'])
    return np.abs(ph - bw['every'] / 2.0) <= bw['w'] / 2.0


def trident_axes(x, y, layout='ts'):
    """(u along the trident's bar, v across it, + toward the camera) for the layout."""
    f = np.radians(LAYOUTS.get(layout, {}).get('face', 45.0))
    nx, ny = np.cos(f), np.sin(f)                 # toward the camera (local x east, y south)
    return x * (-ny) + y * nx, x * nx + y * ny


def scene(X, Y, p=None, layout='ts', prog=None, mask=0, live=False, **kw):
    p = P if p is None else p
    g = dict(DONE); g.update(prog or {})
    x, y = to_local(X, Y, layout)
    H = np.zeros_like(X); C = np.zeros(X.shape, np.int16)
    extra = {'paint': np.full(X.shape, g['paint'], np.float32), 'live': np.full(X.shape, 1.0 if live else 0.0, np.float32),
             'mask': np.full(X.shape, float(mask), np.float32)}
    cacc = {}

    def put(h, comp, where=None):
        nonlocal H, C
        if where is not None:
            h = np.where(where, h, 0.0)
        win = h > H + 1e-6
        H = np.where(win, h, H); C = np.where(win, comp, C)

    def slab(top, bot, comp, where, name=''):
        key = name.rstrip('0123456789') or 'part'
        if key not in cacc:
            cacc[key] = CropAcc(X.shape, n=3)
        top = np.broadcast_to(np.asarray(top, np.float32), X.shape); bot = np.broadcast_to(np.asarray(bot, np.float32), X.shape)
        cacc[key].add(np.maximum(bot, 0.0), top, comp, where & (top > bot), name)

    q, am = p['pad'], p['arm']
    gp = float(np.clip(g['pad'], 0, 1)); ga = float(np.clip(g['arms'], 0, 1))
    r = np.hypot(x, y)
    # ---- the arms (grating bridges) to every neighbour; a straight section is grating end to end
    dirs = [d for bit, d in DIRS.items() if mask & bit]
    if straight(mask):
        dirs = [DIRS[1], DIRS[4]] if mask == 5 else [DIRS[2], DIRS[8]]
    a0 = 0.0 if straight(mask) else q['a'] - 2.0
    bw = am['bars']
    for d in dirs:
        along, across, m = arm_box(x, y, d, a0, am['w'])
        if ga <= 0:
            continue
        hb = am['base_h']
        # chunky rungs across the run (six to a cell, the same phase in every section so runs line up), the gaps
        # between them open down to a low floor
        run = y if abs(d[1]) > 0 else x
        rung = rung_mask(run, bw)
        put(np.where(m, np.where(rung, hb + (am['h'] - hb) * ga, hb * ga + 0.2), 0.0), GRATE)
        # the rails along its sides
        rail = m & (np.abs(across) >= am['w'] / 2.0 - am['rail']['w'])
        put(np.where(rail, (am['h'] + am['rail']['up']) * ga, 0.0), RAIL)
        # brackets on the rails' outer sides
        bk = am['bracket']
        ph = np.mod(run - bk['at'], bk['every'])
        on = (np.minimum(ph, bk['every'] - ph) <= bk['len'] / 2.0)
        bm = (along >= a0 + 2.0) & (along <= EDGE - 2.0) & (np.abs(across) > am['w'] / 2.0) & \
             (np.abs(across) <= am['w'] / 2.0 + bk['out']) & on
        put(np.where(bm, (am['h'] + am['rail']['up'] - 0.8) * ga, 0.0), RAIL)
    # ---- the pad: a low square slab, bevelled, its rim raised; the dish sunk in its middle
    if not straight(mask) and gp > 0:
        ax_ = np.maximum(np.abs(x), np.abs(y))
        inside = ax_ <= q['a']
        top = q['h'] * gp - np.clip(ax_ - (q['a'] - q['bevel']), 0, None) * 0.9
        put(np.where(inside, np.maximum(top, 0.5), 0.0), PAD)
        rim = inside & (ax_ >= q['a'] - q['rim']['w'] - q['bevel'])
        put(np.where(rim, (q['h'] + q['rim']['up']) * gp - np.clip(ax_ - (q['a'] - q['bevel']), 0, None) * 0.9, 0.0), RIM)
        dq = p['dish']
        if g['dish'] > 0:
            disc = r <= dq['r']
            H = np.where(disc & (C == PAD), np.maximum(q['h'] * gp - dq['sink'], 0.5), H)
            C = np.where(disc & np.isin(C, [PAD]), DISH, C)
            ring = (r >= dq['ring']['r'][0]) & (r <= dq['ring']['r'][1])
            put(np.where(ring, q['h'] * gp - dq['sink'] + dq['ring']['up'], 0.0), RIM)
            gd = float(np.clip(g['dish'], 0, 1))
            z0 = q['h'] * gp - dq['sink']
            u, v = trident_axes(x, y, layout)
            hb, pr = p['hub'], p['prongs']
            bar = (np.abs(u) <= hb['len'] / 2.0) & (np.abs(v) <= hb['d'] / 2.0)
            if gd > 0:
                slab(np.where(bar, z0 + hb['h'] * gd, -1.0), z0 - 0.5, HUB, bar, 'trident-bar')
            for k in range(pr['n']):
                c = (k - (pr['n'] - 1) / 2.0) * pr['gap']
                du = np.abs(u - c); dv = np.abs(v)
                rr_ = np.maximum(du, dv)
                tine = rr_ <= pr['w'] / 2.0
                # a square prong, its top drawn to a point over the last `tip` units
                top = z0 + hb['h'] + (pr['h'][k] - pr['tip'] * (rr_ / (pr['w'] / 2.0)) ** 1.5)
                if gd > 0:
                    slab(np.where(tine, z0 + (top - z0) * gd, -1.0), z0 - 0.5, PRONG, tine, f'prong{k}')
    return hd.Scene(H.astype(np.float32), C, pack_slabs(cacc.values(), X.shape), extra)


COLORS = {PAD: (150, 150, 170), RIM: (170, 170, 196), DISH: (60, 60, 64), HUB: (120, 120, 130), PRONG: (180, 180, 200),
          GRATE: (60, 60, 50), RAIL: (150, 150, 200), BASE: (120, 120, 120)}
