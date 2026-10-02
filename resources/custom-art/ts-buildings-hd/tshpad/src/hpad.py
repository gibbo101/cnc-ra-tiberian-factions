"""
TS Helipad (GAHPAD / GTHPAD; TSHPAD in the mod) as a model for hd.py.

Built in its own frame (X east, Y south as TS draws it, units 1 cell = 128, Z up, origin at the centre of TS's 2x2
foundation), read from GTHPAD / GTHPADBB / GTHPADMK / GTHPAD_A in TS's own camera:
  pad      GTHPADBB, the bib: a low octagonal platform over the east of the foundation, a landing circle on it (black,
           a house-green ring, white markings: a cross and a dashed ring, bars), a flight of pink-tan steps down its
           south-east side, a railing of dark posts along its south-west edge
  block    a tan machinery block at the south-west, white-lit, dark at its foot
  tanks    green fuel tanks along the west side, pipes between them
  box      the control box at the north-west, raised on a stand
  lights   GTHPAD_A: lights set in the cross's arms, a light running in from the four ends to the middle
"""
import numpy as np
import hd
import wnoise as WN
from radr import Acc, rod_interval, in_poly, inbox

(PAD, LAND, RING, MARK, STEPS, RAIL, BLOCK, BLOCKD, TANK, PIPE, BOX, BOXD, STAND, LIGHT, SLAB, GREEN) = range(1, 17)
DEBRIS, DEB_IN, DEB_BURNT = 40, 41, 42
HOUSE = {RING, TANK, GREEN}

P = dict(
    pad=dict(poly=((-79.0, -113.0), (-65.0, -129.0), (44.0, -129.0), (122.0, -51.0), (122.0, 30.0), (30.0, 122.0),
                   (-79.0, 122.0)), h=16.0,
             land=dict(c=(0.5, -26.5), r=66.0, ring=78.0),
             steps=dict(top=145.0, foot=176.0, span=(-96.0, 48.0), n=4),
             # GTHPAD_A: approach lights in a cross in front of the landing circle, 4 on each arm and one in the middle
             lights=dict(c=(57.0, 33.0), arm=46.7, r=3.2),
             rail=dict(y=118.0, x=(-79.0, 6.0), every=16.0, h=12.0, r=1.6)),
    block=dict(x=(-111.0, -78.0), y=(54.0, 110.0), z=38.0, foot=8.0,
               tower=dict(x=(-116.0, -94.0), y=(62.0, 98.0), z=60.0), arm=((-106.0, 80.0, 60.0), (-96.0, 64.0, 74.0))),
    tanks=dict(pts=((-94.0, -17.0, 38.0, 15.0), (-100.0, -58.0, 34.0, 15.0), (-106.0, 16.0, 30.0, 11.0), (-108.0, -36.0, 48.0, 11.0)), spheres=(),
                rack=dict(x=(-110.0, -94.0), y=(-44.0, 16.0), z=24.0)),
    box=dict(x=(-92.0, -58.0), y=(-126.0, -80.0), z=(30.0, 70.0)),
    stand=dict(x=(-86.0, -64.0), y=(-120.0, -86.0)),
    pipes=(((-100.0, 56.0, 10.0), (-96.0, 20.0, 10.0)), ((-92.0, 20.0, 12.0), (-90.0, -24.0, 12.0)),
           ((-90.0, -64.0, 14.0), (-78.0, -84.0, 26.0)), ((-96.0, 4.0, 26.0), (-94.0, -30.0, 30.0))),
)

LAYOUTS = {'ts': dict(turn=False), 'ra': dict(turn=False)}


def to_local(X, Y, layout='ts'):
    return X, Y


def light_points(p=None):
    """the approach lights: 4 on each arm of the cross (outer first) and the middle one last: list of (x, y); the
    ring index of each (4 outermost .. 1, 0 the middle) is light_rings()."""
    p = P if p is None else p
    li = p['pad']['lights']
    cx, cy = li['c']
    pts = []
    for k in (4, 3, 2, 1):
        d = li['arm'] * k / 4.0
        pts += [(cx - d, cy), (cx, cy - d), (cx, cy + d), (cx + d, cy)]
    pts.append((cx, cy))
    return pts


def light_rings():
    return [4] * 4 + [3] * 4 + [2] * 4 + [1] * 4 + [0]


PARTS = ('pad', 'block', 'tanks', 'box', 'pipes')
BUILD_KEYS = ('rim', 'steps', 'pyramid', 'deck', 'dome', 'hatch', 'land', 'tanks', 'pipes', 'block', 'box', 'paint')
DONE = {k: 1.0 for k in BUILD_KEYS}


def scene(X, Y, p=None, layout='ts', prog=None, parts=None, level=0, merge=True, pad=None):
    """pad True: the bib alone (GTHPADBB); False: the building alone (GTHPAD); None: both."""
    p = P if p is None else p
    g = dict(DONE); g.update(prog or {})
    x, y = to_local(X, Y, layout)
    H = np.zeros_like(X); C = np.zeros(X.shape, np.int16)
    acc = Acc(X.shape)
    extra = {}
    if parts is None:
        parts = PARTS if pad is None else (('pad',) if pad else tuple(k for k in PARTS if k != 'pad'))
    want = lambda k: k in parts

    def put(h, comp, where=None):
        nonlocal H, C
        if where is not None:
            h = np.where(where, h, 0.0)
        win = h > H + 1e-6
        H = np.where(win, h, H); C = np.where(win, comp, C)

    q = p['pad']
    building = prog is not None
    if want('pad'):
        m = in_poly(x, y, q['poly'])
        lc = q['land']
        if building:
            # GTHPADMK: the pad's rim frame goes round first, a pyramid of panels stands in the middle and opens, the
            # deck is laid from the rim in round a square hole, a white dome rises in the hole and sinks back, the hole
            # is closed, then the landing circle is painted
            cxp, cyp = lc['c']
            inset = 6.0
            sh = 1.0 - np.clip(g['rim'], 0, 1)
            core = in_poly((x - 14.0) / max(1 - inset / 110.0, 1e-3) + 14.0, (y + 3.0) / max(1 - inset / 125.0, 1e-3) - 3.0, q['poly'])
            rimm = m & ~core & (g['rim'] > 0)
            put(np.where(rimm, q['h'] * np.clip(g['rim'] * 1.5, 0.2, 1.0), 0.0), RAIL)
            d = np.clip(g['deck'], 0, 1)
            if d > 0:
                # laid inward from the rim: a growing ring of deck
                rr = np.maximum(np.abs(x - cxp) / 1.0, np.abs(y - cyp))
                reach = 170.0 * (1.0 - d)
                deck = m & (rr >= reach) & core
                hole = (np.abs(x - cxp) < 44.0) & (np.abs(y - cyp) < 44.0) & (g['hatch'] < 1.0)
                hole &= ~((y - cyp) < -44.0 + 88.0 * np.clip(g['hatch'], 0, 1))          # the hatch slides shut
                put(np.where(deck & ~hole, q['h'], 0.0), PAD)
                put(np.where(deck & hole, 2.0, 0.0), RAIL)
            pyr = g['pyramid']
            if 0 < pyr < 2.0:
                grow = min(pyr, 1.0); sink = max(pyr - 1.0, 0.0)
                hw = 56.0 * grow
                ap = 74.0 * grow * (1.0 - sink)
                cheb = np.maximum(np.abs(x - cxp), np.abs(y - cyp))
                zp = np.clip(ap * (1 - cheb / max(hw, 1e-3)), 0, None) + 2.0
                open_ = (sink > 0.3) & ((x - cxp) > (y - cyp) * 0.2)
                put(np.where((cheb <= hw) & (zp > 2.1) & ~open_, zp, 0.0), SLAB)
            dm = g['dome']
            if 0 < dm < 2.0:
                up_ = 1.0 - abs(dm - 1.0)
                rr2 = np.hypot(x - cxp, y - cyp)
                zd = (q['h'] - 40.0 + 70.0 * up_) + 0.0
                zz = zd + np.sqrt(np.clip(46.0 ** 2 - rr2 ** 2, 0, None)) * 0.9
                put(np.where((rr2 <= 46.0) & (zz > 2.0), np.maximum(zz, 2.0), 0.0), SLAB)
            extra['land'] = np.full(X.shape, float(g['land'] >= 1.0), np.float32)
        else:
            put(np.where(m, q['h'], 0.0), PAD)
            extra['land'] = np.full(X.shape, 1.0, np.float32)
    if want('pad') and (not building or g['steps'] > 0):
        st = q['steps']
        s_ = x + y
        u = x - y
        sm = (s_ >= st['top'] - 1) & (s_ <= st['foot']) & (u >= st['span'][0]) & (u <= st['span'][1])
        k = np.floor((s_ - st['top']) / ((st['foot'] - st['top']) / st['n']))
        put(np.where(sm, q['h'] * (1 - (k + 1) / (st['n'] + 1)), 0.0), STEPS)
        if not building or g['deck'] >= 1.0:
            ra = q['rail']
            for px in np.arange(ra['x'][0] + 4, ra['x'][1], ra['every']):
                put(np.where(np.hypot(x - px, y - ra['y']) <= ra['r'] + 0.8, q['h'] + ra['h'], 0.0), RAIL)
            lo, hi, mm = rod_interval(x, y, (ra['x'][0], ra['y'], q['h'] + ra['h']), (ra['x'][1], ra['y'], q['h'] + ra['h']), ra['r'])
            acc.add(lo, hi, RAIL, mm, 'rail')
        if not building or g['land'] >= 1.0:
            li = q['lights']
            for (lx, ly) in light_points(p):
                rr = np.hypot(x - lx, y - ly)
                put(np.where(rr <= li['r'], q['h'] + 1.2 * np.sqrt(np.clip(1 - (rr / li['r']) ** 2, 0, None)), 0.0), LIGHT)
    if want('block') and (not building or g['block'] > 0):
        b = p['block']
        f_ = float(np.clip(g['block'], 0, 1)) if building else 1.0
        put(np.where(inbox(x, y, b['x'], b['y']), b['z'] * max(f_, 0.15), 0.0), BLOCK)
        tw = b['tower']
        if f_ >= 0.6:
            put(np.where(inbox(x, y, tw['x'], tw['y']), b['z'] + (tw['z'] - b['z']) * (f_ - 0.6) / 0.4, 0.0), BLOCK)
        if f_ >= 1.0:
            lo, hi, mm = rod_interval(x, y, b['arm'][0], b['arm'][1], 3.0)
            acc.add(lo, hi, PIPE, mm, 'arm')
    if want('tanks') and (not building or g['tanks'] > 0):
        t = p['tanks']
        rk = t['rack']
        put(np.where(inbox(x, y, rk['x'], rk['y']), rk['z'], 0.0), STAND)
        ft = float(np.clip(g['tanks'], 0, 1)) if building else 1.0
        for (tx, ty, tz, tr) in t['pts']:
            rr = np.hypot(x - tx, y - ty)
            dome = tz * max(ft, 0.1) + 0.45 * tr * np.sqrt(np.clip(1 - (rr / tr) ** 2, 0, None))
            put(np.where(rr <= tr, dome, 0.0), TANK)
        for (sx, sy, sz, sr) in t['spheres']:
            rr = np.hypot(x - sx, y - sy)
            hh = np.sqrt(np.clip(sr * sr - rr * rr, 0, None))
            acc.add(sz - hh, sz + hh, TANK, rr <= sr, 'sphere')
            lo, hi, mm = rod_interval(x, y, (sx, sy, 0.0), (sx, sy, sz), 2.5)
            acc.add(lo, hi, STAND, mm, 'leg')
    if want('box') and (not building or g['box'] > 0):
        b = p['box']; s = p['stand']
        fb = float(np.clip(g['box'], 0, 1)) if building else 1.0
        put(np.where(inbox(x, y, s['x'], s['y']), b['z'][0] * min(1.0, fb * 2), 0.0), STAND)
        if fb > 0.5:
            acc.add(np.full(X.shape, b['z'][0]), np.full(X.shape, b['z'][0] + (b['z'][1] - b['z'][0]) * (fb - 0.5) / 0.5),
                    BOX, inbox(x, y, b['x'], b['y']), 'box')
    if want('pipes') and (not building or g['pipes'] > 0):
        for (a0, a1) in p['pipes']:
            lo, hi, mm = rod_interval(x, y, a0, a1, 4.0)
            acc.add(lo, hi, PIPE, mm, 'pipe')
    extra['paint'] = np.full(X.shape, g['paint'], np.float32)
    return hd.Scene(H, C, acc.slabs(), extra)


FLAT = {PAD: (190, 170, 120), LAND: (20, 20, 20), RING: (0, 200, 0), MARK: (230, 230, 230), STEPS: (230, 180, 170),
        RAIL: (40, 40, 40), BLOCK: (200, 180, 140), BLOCKD: (40, 40, 40), TANK: (0, 200, 0), PIPE: (120, 120, 120),
        BOX: (200, 180, 140), BOXD: (60, 50, 40), STAND: (80, 80, 80), LIGHT: (255, 255, 255), SLAB: (150, 150, 150),
        GREEN: (0, 200, 0)}
