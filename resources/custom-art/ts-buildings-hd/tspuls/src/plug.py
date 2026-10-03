"""
TS Upgrade Center (GAPLUG / GTPLUG; TSPLUG in the mod) as a model for hd.py.

Built in its own frame (X east, Y south as TS draws it, units 1 cell = 128, Z up, origin at the centre of TS's 2x3
foundation, X -128..128, Y -192..192), read from GTPLUG / GTPLUGMK / GTPLUG_A.._C in TS's own camera (TS's ground centre
at frame px (60, 90)).  Depth along TS's view ray is fixed by the feet (on the ground) and the slope's foot (on the deck):
  deck      a grey platform raised on square feet (TS draws three of them: the south-west and south-east corners and the
            middle of the east side), its north-west part narrower (GTPLUGMK 03); an ochre step along its south edge
  block     a long tan block along the deck's north part: a flat roof with a raised panel, a bright bevel along its south
            edge, under it a vertical face with the purple band at the top (the band turns the south-east corner and runs
            north along the east face until the ramp covers it)
  slope     TS's 'greenhouse': a house-green slope from the face's foot down to the deck, framed panes with a sill
  ramp      a steep brown hip at the east end, from the block's north-east corner down to the deck's north-east corner
            and the deck's east edge; a dark slot down it (GTPLUG_C runs a light in it); three tall grey pipes stand in
            front of it at the deck's east edge
  sockets   two round plug sockets on the deck's south part, one cell apart: house-green collars round grey plates with
            four bolts (the plugs GTPLUG_D/E/F stand in them)
  roof      antennas (the tallest at the west end carries GTPLUG_B's lights; a fork in the middle), a dish on a box at
            the north edge (GTPLUG_A turns it)
"""
import numpy as np
import hd
from radr import Acc, rod_interval, inbox, in_poly, dblob
from scipy import ndimage


class CropAcc:
    """radr.Acc's layered intervals for one small part, kept only over the box the part covers (a full-grid Acc is
    three layers of full-grid arrays: thirty plug parts at x4 on the RA grid ran out of memory)."""
    def __init__(self, shape, n=3):
        self.shape, self.n, self.adds = shape, n, []

    def add(self, bot, top, comp, mask, name=''):
        bot = np.broadcast_to(np.asarray(bot, np.float32), mask.shape)
        top = np.broadcast_to(np.asarray(top, np.float32), mask.shape)
        m = mask & (top > bot)
        if not m.any():
            return
        rows = np.nonzero(m.any(axis=1))[0]; cols = np.nonzero(m.any(axis=0))[0]
        r0, r1, c0, c1 = rows[0], rows[-1] + 1, cols[0], cols[-1] + 1
        cp = comp if np.ndim(comp) == 0 else np.broadcast_to(comp, mask.shape)[r0:r1, c0:c1].copy()
        self.adds.append((r0, c0, bot[r0:r1, c0:c1].copy(), top[r0:r1, c0:c1].copy(), cp, m[r0:r1, c0:c1].copy(), name))

    def layers(self):
        """the used layers over the parts' box: [(r0, c0, top, bot, comp, name)]."""
        if not self.adds:
            return []
        r0 = min(a[0] for a in self.adds); c0 = min(a[1] for a in self.adds)
        r1 = max(a[0] + a[5].shape[0] for a in self.adds); c1 = max(a[1] + a[5].shape[1] for a in self.adds)
        shp = (r1 - r0, c1 - c0)
        acc = Acc(shp, n=self.n)
        for ar, ac, b, t, cp, m, name in self.adds:
            sl = (slice(ar - r0, ar - r0 + m.shape[0]), slice(ac - c0, ac - c0 + m.shape[1]))
            mm = np.zeros(shp, bool); mm[sl] = m
            bb = np.zeros(shp, np.float32); bb[sl] = b
            tt = np.zeros(shp, np.float32); tt[sl] = t
            if np.ndim(cp):
                cc = np.zeros(shp, np.int16); cc[sl] = cp
            else:
                cc = cp
            acc.add(bb, tt, cc, mm, name)
        return [(r0, c0, t, b, c, '+'.join(nm) or 'part') for t, b, c, nm in zip(acc.top, acc.bot, acc.comp, acc.names)
                if (t >= 0).any()]


def pack_slabs(accs, shape, gap=10):
    """the parts' layers packed into as few full-grid slabs as possible: parts whose footprints, grown by `gap` grid
    px, don't overlap share a slab (so smoothing a slab's top never mixes two parts: the render is the same as one
    slab each); lathed parts ('L:', classed top / bottom by hd) only with lathed ones."""
    packed = []
    st = np.ones((3, 3), bool)
    for a in accs:
        for r0, c0, t, b, c, name in a.layers():
            valid = t >= 0
            lathe_ = name.startswith('L:')
            R0, C0 = max(r0 - gap, 0), max(c0 - gap, 0)
            R1, C1 = min(r0 + t.shape[0] + gap, shape[0]), min(c0 + t.shape[1] + gap, shape[1])
            grown = np.zeros((R1 - R0, C1 - C0), bool)
            grown[r0 - R0:r0 - R0 + t.shape[0], c0 - C0:c0 - C0 + t.shape[1]] = valid
            grown = ndimage.binary_dilation(grown, structure=st, iterations=gap)
            # after every slab holding a part it touches, so where two parts meet the earlier one still wins (as
            # when each part was a slab of its own, in order)
            conf = [i for i, q in enumerate(packed) if (q['m'][R0:R1, C0:C1] & grown).any()]
            for q in packed[(max(conf) + 1 if conf else 0):]:
                if q['L'] == lathe_:
                    break
            else:
                q = dict(top=np.full(shape, -1.0, np.float32), bot=np.zeros(shape, np.float32),
                         comp=np.zeros(shape, np.int16), m=np.zeros(shape, bool), names=[], L=lathe_)
                packed.append(q)
            sl = (slice(r0, r0 + t.shape[0]), slice(c0, c0 + t.shape[1]))
            q['top'][sl] = np.where(valid, t, q['top'][sl])
            q['bot'][sl] = np.where(valid, np.maximum(b, 0.0), q['bot'][sl])
            q['comp'][sl] = np.where(valid, c, q['comp'][sl])
            q['m'][sl] |= valid
            q['names'].append(name)
    return [hd.Slab(q['top'], q['bot'], q['comp'], '+'.join(q['names'])) for q in packed]
import plugs as PG, wnoise as WN

(PLAT, FOOT, BLOCK, LIP, FACE, ROOF, PANEL, PFRAME, SOCK, PLATE, BOLT, RAMP, PIPE, PCAP, ANT, DISH, DMOUNT, LAMP,
 SLAB, STEP, SLOT, RIDGE, LEDGE, FRONT, CORE, BEAM) = range(1, 27)
DEBRIS, DEB_IN, DEB_BURNT = 40, 41, 42
HOUSE = {PANEL, PFRAME, SOCK} | PG.PG_HOUSE

P = dict(
    deck=dict(x0=-120.0, x0n=-98.0, yw=-12.0, x1=122.5, x1s=110.0, ye=50.0, y0=-124.0, y1=172.0, zb=16.0, zt=33.5,
              cham=2.0, core=26.0),
    # square feet (centre x, y), half size, from the ground to the deck's underside
    feet=dict(pts=((-110.0, 166.0), (86.0, 166.0), (93.0, 29.0), (-109.0, 29.0), (93.0, -112.0), (-88.0, -112.0)),
              a=10.5),
    # the ochre step along the deck's south edge
    step=dict(x=(-57.0, 49.0), y=(164.0, 172.0), h=3.2, n=14),
    # the block's profile across y (north to south): the roof (flat, a raised panel on it), a 45-degree bevel, the
    # vertical band face, a narrow ledge, a short brown face, then the slope.  The upper part (roof to the ledge's
    # front) runs west past the lower body and the deck: TS's notch under the west end.
    block=dict(yn=-86.2, z=89.5, lip=(-0.9, 8.6), face=(80.0, 67.0), ledge=(19.3, 67.0), front=60.5,
               x_roof=(-127.0, 78.0), x_ledge=(-131.0, 78.0), x_low=-98.0,
               band=(71.3, 80.0), strip=(67.0, 71.3),
               ridge=dict(y=(-60.0, -16.0), x=(-118.0, 66.0), h=0.0, cham=3.0)),
    # the slope: panes from the front face's foot to (y, z), then the sill down to the deck at y_foot
    # east of the block (x > 78) the slope runs on over the ramp to x 112, its top edge rising to y 8 there
    slope=dict(x=(-98.0, 108.0), pane=(39.3, 39.5), foot=49.3, ribs=50.5, rib0=-87.0, rib_w=4.0, rib_h=2.4,
               east=(78.0, 108.0, 9.0)),
    # the ramp: a bilinear patch over the quad A (block's north-east top corner), B (deck's north-east corner),
    # C (deck's east edge, south), D (block's east face, south); (x, y, z) each
    ramp=dict(A=(78.0, -86.2, 89.5), B=(121.0, -124.0, 33.5), C=(121.0, 46.0, 33.5), D=(78.0, 30.0, 33.0),
              skirt=(117.0, 123.5), skirt_y=(-124.0, 50.0)),
    # the slot down the ramp (two points on it, found from TS's px (85, 81) and (85, 89)), its half width
    slot=dict(w=2.2),
    pipes=dict(pts=((121.0, -34.0, 99.0), (121.0, -53.0, 92.0), (121.0, -71.0, 79.0)), r=5.8, cap=3.0,
               plinth=dict(x=(114.0, 127.0), y=(-86.0, -24.0), z=33.5)),
    sockets=dict(c=((-68.0, 111.0), (59.0, 112.0)), r_out=48.5, r_in=37.5, z=47.5, plate=43.5, bolts=21.0,
                 bolt_r=2.6, bolt_h=1.8),
    # antennas on the roof: (x, y, top z, radius); the tallest one carries GTPLUG_B's lights
    ants=((-112.0, -21.0, 259.0, 2.3), (-110.0, -46.0, 163.0, 1.5), (-110.0, -62.0, 200.0, 1.6),
          (45.0, -35.0, 178.0, 1.5), (77.0, -56.0, 217.0, 1.6), (74.0, -80.0, 198.0, 1.6)),
    tall=dict(thin_from=200.0, thin_r=1.3, lamps=(202.0, 257.0)),
    # the fork: mast (x, y) to z, a crossbar at zc across +-half along x, prongs up to (left, right)
    fork=dict(c=(-28.0, -77.0), z=195.0, zc=138.0, half=8.0, tops=(212.0, 168.0), r=1.5),
    tbar=dict(z=(184.0, 196.0), half=5.0, r=1.0),            # the cross pieces near the top of antenna 3
    mount=dict(c=(-66.0, -70.0), a=11.0, h=9.0),
    dish=dict(R=12.0, depth=3.5, t=1.8, post=(2.2, 9.0), az=200.0, el=55.0, off=3.0),
)

# the damaged state (GTPLUG 1): where TS breaks it
DMG = dict(
    hole=(40.0, -42.0, 54.0, 38.0, 0.3),       # the roof caved in over its east half: centre, half sizes, roughness
    lipcut=(-8.0, 64.0),                        # the bevel and band broken along x (where the hole reaches the face)
    floor=70.0,                                 # the burnt-out inside
    beams=(((-14.0, -72.0, 86.0), (74.0, -50.0, 80.0)), ((2.0, -12.0, 84.0), (44.0, -80.0, 66.0)),
           ((46.0, -6.0, 76.0), (76.0, -44.0, 88.0)), ((20.0, -30.0, 70.0), (60.0, -20.0, 86.0))),
    beam_r=1.8,
    ants_gone=(3, 4),                           # antennas knocked off the roof (TS's x 75 and 85)
    lean=(-5.0, 3.0),                           # the tallest antenna bent: its top moved by (x, y)
    pipes=((121.0, -34.0, 63.0), (121.0, -53.0, 74.0), (121.0, -71.0, 79.0)),   # snapped short; the third bent over
    bent=((121.0, -71.0, 40.0), (138.0, -64.0, 70.0)),
    fallen=((112.0, -44.0, 44.0), (132.0, -18.0, 30.0)),                      # a broken pipe length leaning on the ramp
    pane=(27.0, 27.0, 11.0, 7.0),               # a hole knocked in the slope: x, y, half sizes
    sock=(-20.0, 55.0),                         # socket 1's collar broken off over these angles (deg, from east)
)

LAYOUTS = {'ts': dict(turn=False), 'ra': dict(turn=True), 'ra1': dict(turn=True, flip=True)}


def to_local(X, Y, layout='ts'):
    """'ra': turned a quarter (TS east -> RA south: the ramp and pipes to the camera, the block at the east end, the
    sockets at the west end); 'ra1': the other way (TS west -> RA south)."""
    L = LAYOUTS[layout]
    if not L['turn']:
        return X, Y
    return (-Y, X) if L.get('flip') else (Y, -X)


def to_world(x, y, layout='ts'):
    L = LAYOUTS[layout]
    if not L['turn']:
        return x, y
    return (y, -x) if L.get('flip') else (-y, x)


# build-up controls (GTPLUGMK's order): deck 0..1 the slab grows out from its middle; marks 0..1 the deck's painted
# outlines (gone when done); block 0..1 the block rises out of the deck with its slope and ramp; collar 0..1 the sockets'
# collars grow round from their fronts; plates 0 / 0.5 plain / 1 with bolts; dish 0 / 0.5 its post / 1; ants 0..1 the
# antennas grow up; pipes 0/1; paint 0 bare frames / 0.5 grey panes / 1 house green
BUILD_KEYS = ('deck', 'marks', 'block', 'collar', 'plates', 'dish', 'ants', 'pipes', 'paint')
DONE = {k: 1.0 for k in BUILD_KEYS}
DONE['marks'] = 0.0


# --------------------------------------------------------------------------------------------- shapes
def ramp_uv(x, y, r):
    """the ramp's patch coordinates: v across (0 at the block's east face, 1 at the deck's east edge), u along (0 at
    the rim A-B, 1 at the south edge D-C); and z."""
    A, B, C, D = (np.array(r[k]) for k in 'ABCD')
    v = (x - A[0]) / (B[0] - A[0])
    ya = A[1] + v * (B[1] - A[1]); yd = D[1] + v * (C[1] - D[1])
    u = (y - ya) / np.maximum(yd - ya, 1e-6)
    z = (1 - v) * ((1 - u) * A[2] + u * D[2]) + v * ((1 - u) * B[2] + u * C[2])
    return u, v, z


def ramp_point(r, u, v):
    A, B, C, D = (np.array(r[k]) for k in 'ABCD')
    return (1 - v) * ((1 - u) * A + u * D) + v * ((1 - u) * B + u * C)


def slot_ends(p=None):
    """the slot's two ends on the ramp: the points whose TS-screen position is (85, 81) and (85, 89)."""
    p = P if p is None else p
    r = p['ramp']
    A, B, C, D = (np.array(r[k]) for k in 'ABCD')
    u, v = np.meshgrid(np.linspace(0, 1, 401), np.linspace(0, 1, 401))
    u = u[..., None]; v = v[..., None]
    q = (1 - v) * ((1 - u) * A + u * D) + v * ((1 - u) * B + u * C)
    sx = 60 + 0.1875 * (q[..., 0] - q[..., 1]); sy = 90 + 0.09375 * (q[..., 0] + q[..., 1]) - 0.2297 * q[..., 2]
    out = []
    for ys in (80.5, 89.5):
        d = (sx - 85.0) ** 2 + (sy - ys) ** 2
        i = np.unravel_index(np.argmin(d), d.shape)
        out.append(q[i])
    return out


def block_z(y, b):
    """the block's top across y: the roof, the bevel, the ledge (the band face and the front face are the steps)."""
    l0, l1 = b['lip']
    z = np.where(y <= l0, b['z'], b['z'] - (y - l0))
    z = np.where(y > l1, b['ledge'][1], z)
    return np.where(y <= b['ledge'][0], z, 0.0)


def slope_z(y, s, b):
    """the slope from the front face's foot down to the deck."""
    y0, z0 = b['ledge'][0], b['front']
    y1, z1 = s['pane']
    y2, z2 = s['foot'], P['deck']['zt']
    za = z0 + (z1 - z0) * np.clip((y - y0) / (y1 - y0), -1, 1)
    zb = z1 + (z2 - z1) * np.clip((y - y1) / (y2 - y1), 0, 1)
    return np.where(y <= y1, za, zb)


def scene(X, Y, p=None, layout='ts', prog=None, parts=None, level=0, merge=True, dish_t=0.0, dish_az=None,
          shadow=False, plugs=(None, None), plug_t=0.0):
    """shadow=True: the light's pass (the antennas cast no shadows: on the roof they read as cracks)."""
    p = P if p is None else p
    g = dict(DONE); g.update(prog or {})
    x, y = to_local(X, Y, layout)
    H = np.zeros_like(X); C = np.zeros(X.shape, np.int16)
    acc = Acc(X.shape, n=6)          # the raised deck's edges, the overhang, the sockets, the pipes
    acc_a = Acc(X.shape, n=4)        # thin parts in the air: antennas, the dish
    acc_l = Acc(X.shape, n=2)        # the antenna's lamps (kept apart: merged with the mast they'd take it over)
    extra = {}

    def put(h, comp, where=None):
        nonlocal H, C
        if where is not None:
            h = np.where(where, h, 0.0)
        win = h > H + 1e-6
        H = np.where(win, h, H); C = np.where(win, comp, C)

    d = p['deck']
    zt = d['zt']
    if g['deck'] <= 0:
        return hd.Scene(H, C, [], extra)
    # the build-up: the deck grows out from its middle (its shape at the inverse-scaled point)
    dk = float(g['deck'])
    xc_, yc_ = 0.5 * (d['x0'] + d['x1']), 0.5 * (d['y0'] + d['y1'])
    xg, yg = (x, y) if dk >= 1 else (xc_ + (x - xc_) / dk, yc_ + (y - yc_) / dk)
    # ---- the deck: a slab on square feet, solid underneath only well inside its edges (hidden from both cameras)
    x0 = np.where(yg < d['yw'], d['x0n'], d['x0']); x1 = np.where(yg > d['ye'], d['x1s'], d['x1'])
    deck = (xg >= x0) & (xg <= x1) & (yg >= d['y0']) & (yg <= d['y1'])
    e = np.minimum(np.minimum(xg - x0, x1 - xg), np.minimum(yg - d['y0'], d['y1'] - yg)) * min(dk, 1.0)
    dtop = zt - np.clip(d['cham'] - e, 0, None)
    core = deck & (e >= d['core'])
    # the block's lower body and the slope stay solid to the ground (no seam where they would cross the core's edge;
    # their feet sit back far enough under the deck that the gap under its edge still shows)
    bk = p['block']; slp = p['slope']
    core |= inbox(x, y, (bk['x_low'], bk['x_roof'][1]), (bk['yn'], bk['ledge'][0]))
    core |= inbox(x, y, slp['x'], (bk['ledge'][0] - 15.0, slp['foot']))
    put(np.where(deck, dtop, 0.0), PLAT, deck)
    ft = p['feet']
    feet = np.zeros(X.shape, bool)
    for (cx, cy) in ft['pts']:
        feet |= inbox(xg, yg, (cx - ft['a'], cx + ft['a']), (cy - ft['a'], cy + ft['a']))
    # the ochre step along the south edge
    st = p['step']
    m = inbox(x, y, st['x'], st['y']) & (dk >= 1)
    put(np.where(m, zt + st['h'] * np.clip((st['y'][1] - y) / 4.0, 0.35, 1.0), 0.0), STEP, m)
    if dk < 1:                      # the slab alone while it grows
        core = deck & (e >= d['core'] * dk)
        acc.add(d['zb'], np.where(deck, dtop, 0.0), PLAT, deck & ~core, 'deck')
        H = np.where(core, zt, 0.0); C = np.where(core, PLAT, 0).astype(np.int16)
        H = np.where(feet, np.maximum(H, d['zb'] + 0.5), H); C = np.where(feet & (H <= d['zb'] + 0.6), FOOT, C)
        return hd.Scene(H, C, acc.slabs(), extra)
    bl = float(g['block'])
    sink = (1.0 - bl) * (p['block']['z'] - zt)       # the block rises: everything above the deck sunk by this

    # ---- the block: the lower body (x >= x_low) solid from the deck; the upper part (roof .. ledge) runs on west
    b = p['block']
    zb_ = block_z(y, b)
    l0, l1 = b['lip']; ly, lz = b['ledge']
    comp = np.where(y <= l0, BLOCK, np.where(y <= l1, LIP, LEDGE))
    xr = np.where(y <= l1, b['x_roof'][0], b['x_ledge'][0])
    xe = np.where(y <= l1, b['x_roof'][1], b['x_ledge'][1])
    inb = (x >= xr) & (x <= xe) & (y >= b['yn']) & (y <= ly)
    low = inb & (x >= b['x_low'])
    up = (zb_ - sink) > zt + 0.3                  # what has risen out of the deck so far
    for k in (BLOCK, LIP, LEDGE):
        put(np.where(low, zb_ - sink, 0.0), k, low & (comp == k) & up)
    # the band face: a thin strip just north of the face line (its south side is the face); the front face likewise
    for (yy, ztop, k) in ((l1, b['face'][0], FACE), (ly, lz, FRONT)):
        m = (x >= xr) & (x <= xe) & (y > yy - 2.0) & (y <= yy) & (x >= b['x_low']) & (ztop - sink > zt + 0.3)
        H = np.where(m, ztop - sink, H); C = np.where(m, k, C)
    # the overhang west of the lower body: a slab from the front face's foot up
    ov = inb & (x < b['x_low'] + 4.0)        # overlapping the lower body a little: no seam where they meet
    zov = np.where((y > l1 - 2.0) & (y <= l1), b['face'][0], zb_)
    zov = np.where((y > ly - 2.0) & (y <= ly), np.maximum(zov, lz), zov)
    cov = np.where((y > l1 - 2.0) & (y <= l1), FACE, np.where((y > ly - 2.0) & (y <= ly), FRONT, comp))
    zov = zov - sink
    for k in (BLOCK, LIP, LEDGE, FACE, FRONT):
        acc.add(max(b['front'] - sink, zt), zov, k, ov & (cov == k) & (zov > zt + 0.3), 'overhang')
    # the raised panel on the roof
    rg = b['ridge']
    m2 = inbox(x, y, rg['x'], rg['y'])
    e2 = np.minimum(np.minimum(x - rg['x'][0], rg['x'][1] - x), np.minimum(y - rg['y'][0], rg['y'][1] - y))
    zrg = b['z'] + np.clip(e2 / rg['cham'], 0, 1) * rg['h'] - sink
    put(np.where(m2 & (x >= b['x_low']) & (zrg > zt + 0.3), zrg, 0.0), RIDGE)
    acc.add(max(b['front'] - sink, zt), zrg, RIDGE, m2 & (x < b['x_low'] + 4.0) & (zrg > zt + 0.3), 'overhang')

    # ---- the slope (house green) from the front face's foot to the deck: ribs down it, the sill at its foot
    sl = p['slope']
    ex0, ex1, ey1 = sl['east']
    ytop = ly - (ly - ey1) * np.clip((x - ex0) / (ex1 - ex0), 0, 1)
    m = (x >= sl['x'][0]) & (x <= sl['x'][1]) & (y > ytop) & (y <= sl['foot'])
    zs = slope_z(y, sl, b)
    ph = (x - sl['rib0']) % sl['ribs']
    rib = (np.minimum(ph, sl['ribs'] - ph) < sl['rib_w'] / 2) | (x - sl['x'][0] < sl['rib_w']) | \
          (sl['x'][1] - x < sl['rib_w']) | ((x > ex0) & (y - ytop < sl['rib_w']))
    sill = y > sl['pane'][0]
    zr = zs + np.where(rib & ~sill, sl['rib_h'], 0.0) - sink
    m &= zr > zt + 0.3
    put(np.where(m, zr, 0.0), PANEL, m & ~rib & ~sill)
    put(np.where(m, zr, 0.0), PFRAME, m & (rib | sill))

    # ---- the ramp: the patch over its quad, down to the deck; brown over the deck's east face under it
    if bl > 0:
        r = p['ramp']
        A, B, Cc, D = r['A'], r['B'], r['C'], r['D']
        quad = [(A[0], A[1]), (B[0], B[1]), (Cc[0], Cc[1]), (D[0], D[1])]
        m = in_poly(x, y, quad)
        u, v, zr = ramp_uv(x, y, r)
        zr = zr - sink
        acc.add(d['zb'], zr, RAMP, m & (zr > d['zt'] - 0.5), 'ramp')
        sk = r['skirt']
        m = (x >= sk[0]) & (x <= sk[1]) & (y >= r['skirt_y'][0]) & (y <= r['skirt_y'][1]) & deck
        C = np.where(m & (C == PLAT), RAMP, C)
        e0, e1 = slot_ends(p)
        extra['slot'] = (tuple(e0), tuple(e1))

    # ---- the dish's box on the roof
    mt = p['mount']
    m = inbox(x, y, (mt['c'][0] - mt['a'], mt['c'][0] + mt['a']), (mt['c'][1] - mt['a'], mt['c'][1] + mt['a']))
    zm = b['z'] + mt['h'] - sink
    put(np.where(m & (zm > zt + 0.3), zm, 0.0), DMOUNT, m)

    # ---- damaged: the roof caved in over its east half, the bevel and band broken along it, a pane knocked in
    if level >= 1:
        dm = DMG
        hx, hy, rx, ry, rough = dm['hole']
        eh = dblob(x, y, hx, hy, rx, ry, rough, 2101, feat=10.0)
        onblk = np.isin(C, (BLOCK, LIP, RIDGE, DMOUNT)) & (x >= b['x_low'])
        hole = (eh < 0) & onblk
        floor = dm['floor'] + 3.0 * WN.noise(x, y, 9.0, 2102)
        H = np.where(hole, np.minimum(H, floor), H); C = np.where(hole, DEB_BURNT, C)
        lc = (x > dm['lipcut'][0] + 4 * WN.noise(x, y, 6.0, 2103)) & (x < dm['lipcut'][1] + 4 * WN.noise(x, y, 6.0, 2104))
        lipm = lc & np.isin(C, (LIP, FACE)) & (y > l0 - 3.0)
        H = np.where(lipm, H - (6.0 + 4.0 * np.clip(WN.noise(x, y, 5.0, 2105), 0, 1)), H)
        C = np.where(lipm & (C == LIP), DEB_BURNT, C)
        px_, py_, prx, pry = dm['pane']
        ep = dblob(x, y, px_, py_, prx, pry, 0.4, 2106, feat=5.0)
        pane = (ep < 0) & np.isin(C, (PANEL, PFRAME))
        H = np.where(pane, H - 7.0, H); C = np.where(pane, DEB_IN, C)

    # ---- everything ground-attached so far stands on the deck: outside the deck's solid core it becomes a slab from
    # the deck's underside (open below, the feet carry it); outside the deck it is dropped (the overhang is a slab)
    edge = (H > 0) & ~core
    acc.add(d['zb'], H, C, edge & deck, 'deck')
    H = np.where(edge, 0.0, H); C = np.where(edge, 0, C).astype(np.int16)
    H = np.where(core, np.maximum(H, zt), H)
    # the feet
    H = np.where(feet, np.maximum(H, d['zb'] + 0.5), H); C = np.where(feet & (H <= d['zb'] + 0.6), FOOT, C)

    # ---- the sockets: green collars round grey plates, four bolts on each plate (on the deck)
    sk = p['sockets']
    for i_s, (cx, cy) in enumerate(sk['c']):
        rr = np.hypot(x - cx, y - cy)
        ring = (rr <= sk['r_out']) & (rr > sk['r_in'])
        ztop = np.full(X.shape, sk['z'], np.float32)
        if level >= 1 and i_s == 0:
            a0, a1 = DMG['sock']
            ang = np.rad2deg(np.arctan2(y - cy, x - cx))
            brk = (ang > a0 + 6 * WN.noise(x, y, 8.0, 2107)) & (ang < a1 + 6 * WN.noise(x, y, 8.0, 2108))
            ztop = np.where(brk, zt + 1.5 + 3.0 * np.clip(WN.noise(x, y, 4.0, 2109), 0, 1), ztop)
        cl = float(g['collar'])
        if cl < 1:                           # the build-up: the collar grows round both ways from its front (south-east)
            ang = np.rad2deg(np.arctan2(y - cy, x - cx)) - 45.0
            ang = (ang + 180.0) % 360.0 - 180.0
            ring &= np.abs(ang) <= cl * 180.0
        acc.add(zt - 1.0, ztop, SOCK, ring, 'sock')
        if g['plates'] > 0:
            pl = rr <= sk['r_in']
            bolt = np.zeros(X.shape, bool)
            if g['plates'] >= 1:
                for (bx_, by_) in ((sk['bolts'], 0), (-sk['bolts'], 0), (0, sk['bolts']), (0, -sk['bolts'])):
                    bolt |= np.hypot(x - cx - bx_, y - cy - by_) <= sk['bolt_r']
            acc.add(zt - 1.0, sk['plate'], PLATE, pl & ~bolt, 'plate')
            acc.add(zt - 1.0, sk['plate'] + sk['bolt_h'], BOLT, pl & bolt, 'plate')
    # ---- the plugs standing in the sockets (west, east)
    pacc = {}

    def A(name):
        if name not in pacc:
            pacc[name] = CropAcc(X.shape, n=3)
        return pacc[name]
    pturn = PG.view_turn(layout, to_local)
    for (cx, cy), kind in zip(sk['c'], plugs):
        if kind:
            pu_, pv_ = PG.plug_frame(x - cx, y - cy, pturn)
            PG.add(kind, pu_, pv_, put, A, t=plug_t, base_w=sk['plate'])

    # ---- the pipes at the deck's east edge on a brown plinth from the ground; bright caps
    pp = p['pipes']
    pl_ = pp['plinth']
    acc.add(0.0, pl_['z'], RAMP, inbox(x, y, pl_['x'], pl_['y']), 'plinth')
    pts = (DMG['pipes'] if level >= 1 else pp['pts']) if g['pipes'] >= 1 else ()
    for k_p, (px_, py_, pz) in enumerate(pts):
        rr = np.hypot(x - px_, y - py_)
        mm = rr <= pp['r']
        if level >= 1:
            if k_p == 2:                     # the third bent over at its middle
                acc.add(0.0, DMG['bent'][0][2], PIPE, mm, 'pipe')
                lo, hi, mb = rod_interval(x, y, DMG['bent'][0], DMG['bent'][1], pp['r'])
                acc.add(lo, hi, PIPE, mb, 'pipe')
            else:                            # snapped: a jagged top, no cap
                acc.add(0.0, pz - 4.0 * np.clip(WN.noise(x, y, 3.0, 2110 + k_p), 0, 1), PIPE, mm, 'pipe')
        else:
            acc.add(0.0, pz - pp['cap'], PIPE, mm, 'pipe')
            acc.add(pz - pp['cap'], pz, PCAP, mm & (rr <= pp['r'] - 0.6), 'pcap')
    if level >= 1:
        lo, hi, mb = rod_interval(x, y, DMG['fallen'][0], DMG['fallen'][1], pp['r'] * 0.95)
        acc.add(lo, hi, PIPE, mb, 'pipe')

    # ---- antennas (the build-up: they grow up out of the roof)
    zroof = b['z']
    ga = float(g['ants'])
    if ga <= 0:
        shadow = True                        # (no antennas yet)
    if not shadow:
        hz = lambda zz: zroof + (zz - zroof) * ga
        ants = [(ax, ay, hz(az_), ar) for (ax, ay, az_, ar) in p['ants']]
        for i, (ax, ay, az_, ar) in enumerate(ants):
            if level >= 1 and i in DMG['ants_gone']:
                continue
            if i == 0:
                tl = dict(p['tall'], thin_from=hz(p['tall']['thin_from']))
                lx, ly_ = DMG['lean'] if level >= 1 else (0.0, 0.0)
                fz = (tl['thin_from'] - zroof) / (az_ - zroof)
                mid = (ax + lx * fz, ay + ly_ * fz, tl['thin_from'])
                lo, hi, mm = rod_interval(x, y, (ax, ay, zroof - 1), mid, ar)
                acc_a.add(lo, hi, ANT, mm, 'ant')
                lo, hi, mm = rod_interval(x, y, mid, (ax + lx, ay + ly_, az_), tl['thin_r'])
                acc_a.add(lo, hi, ANT, mm, 'ant')
                # GTPLUG_B's two lamps on it (lit in the materials)
                if ga >= 1:
                    for lz_ in tl['lamps']:
                        f_ = (lz_ - zroof) / (az_ - zroof)
                        lc_ = (ax + lx * f_, ay + ly_ * f_, lz_)
                        lo, hi, mm = rod_interval(x, y, (lc_[0], lc_[1], lz_ - 2.6), (lc_[0], lc_[1], lz_ + 2.6), 2.6)
                        acc_l.add(lo, hi, LAMP, mm, 'lamp')
            else:
                lo, hi, mm = rod_interval(x, y, (ax, ay, zroof - 1), (ax, ay, az_), ar)
                acc_a.add(lo, hi, ANT, mm, 'ant')
        tb = dict(p['tbar'], z=tuple(hz(zz) for zz in p['tbar']['z']))
        ax, ay = p['ants'][2][:2]
        for zc in tb['z']:
            lo, hi, mm = rod_interval(x, y, (ax - tb['half'], ay + tb['half'], zc), (ax + tb['half'], ay - tb['half'], zc),
                                      tb['r'])
            acc_a.add(lo, hi, ANT, mm, 'tbar')
        fk = dict(p['fork'], z=hz(p['fork']['z']), zc=hz(p['fork']['zc']), tops=tuple(hz(zz) for zz in p['fork']['tops']))
        fx, fy = fk['c']
        lo, hi, mm = rod_interval(x, y, (fx, fy, zroof - 1), (fx, fy, fk['z']), fk['r'])
        acc_a.add(lo, hi, ANT, mm, 'fork')
        lo, hi, mm = rod_interval(x, y, (fx - fk['half'], fy + fk['half'] * 0.3, fk['zc']),
                                  (fx + fk['half'], fy - fk['half'] * 0.3, fk['zc']), fk['r'])
        acc_a.add(lo, hi, ANT, mm, 'fork')
        for sgn, ztop in ((-1, fk['tops'][0]), (1, fk['tops'][1])):
            px_, py_ = fx + sgn * fk['half'], fy - sgn * fk['half'] * 0.3
            lo, hi, mm = rod_interval(x, y, (px_, py_, fk['zc']), (px_, py_, ztop), fk['r'] * 0.85)
            acc_a.add(lo, hi, ANT, mm, 'fork')

    # ---- damaged: bare roof beams across the hole
    if level >= 1:
        for (b0, b1) in DMG['beams']:
            lo, hi, mm = rod_interval(x, y, b0, b1, DMG['beam_r'])
            acc_a.add(lo, hi, BEAM, mm, 'beam')

    # ---- the dish on its post (turned by GTPLUG_A): a shallow disc
    if g['dish'] > 0:
        dd = p['dish']
        az = np.deg2rad(dd['az'] if dish_az is None else dish_az)
        cx, cy = mt['c']
        z0 = b['z'] + mt['h']
        lo, hi, mm = rod_interval(x, y, (cx, cy, z0 - 1), (cx, cy, z0 + dd['post'][1]), dd['post'][0])
        acc_a.add(lo, hi, DMOUNT, mm, 'post')
    if g['dish'] >= 1:
        el = np.deg2rad(dd['el'])
        n = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
        ctr = np.array([cx, cy, z0 + dd['post'][1] + dd['R'] * 0.55]) + n * dd['off']
        lo, hi, mm = rod_interval(x, y, ctr - n * dd['t'] / 2, ctr + n * (dd['t'] / 2 + dd['depth'] * 0.3), dd['R'])
        acc_a.add(lo, hi, DISH, mm, 'dish')
    return hd.Scene(H, C, acc.slabs() + acc_a.slabs() + acc_l.slabs() + pack_slabs(pacc.values(), X.shape),
                    extra)


FLAT = {PLAT: (150, 150, 150), FOOT: (110, 100, 80), BLOCK: (190, 160, 100), LIP: (235, 205, 140),
        FACE: (110, 110, 170), ROOF: (200, 170, 110), RIDGE: (205, 175, 115), PANEL: (0, 150, 0), PFRAME: (0, 215, 0),
        SOCK: (0, 210, 0), PLATE: (140, 140, 140), BOLT: (230, 230, 230), RAMP: (130, 100, 60), PIPE: (190, 190, 190),
        PCAP: (240, 240, 230), ANT: (90, 90, 130), DISH: (60, 60, 70), DMOUNT: (110, 110, 140), LAMP: (255, 255, 255),
        SLAB: (150, 150, 150), STEP: (200, 150, 70), SLOT: (20, 20, 20), LEDGE: (175, 150, 95), FRONT: (100, 80, 45),
        CORE: (60, 60, 60), BEAM: (150, 150, 156), DEB_BURNT: (60, 40, 30), DEB_IN: (30, 30, 30), DEBRIS: (120, 110, 90)}
FLAT.update(PG.FLAT)
