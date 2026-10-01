"""
TS Harvester (HARV, and HORV: the same truck with its tank off, as TS draws it while it unloads) as a model for
hd.py, read voxel by voxel from TS's own HARV.VXL / HORV.VXL (49 x 20 x 19; the dumps are in the comments).

Built in voxel units in the truck's own frame (x forward from its back end at 0 to its claws at 49, y across from
its left side at 0 to 20, z up from the ground; a voxel's top face is its index + 1), then placed in the world at its
position, turned to its facing and scaled by S (world units per voxel):
  wheels   five a side at x 6.5, 12, 18, 27, 33, radius 3.5: dark olive tyres, grey hubs
  tank     (HARV) x 0-21: a box with its top edges bevelled, 17 up; four hoops arched over the middle of its top to
           19; along each side a dark panel let in a voxel between a light frame (the ends, a band along the
           bottom); its back end two house-colour posts either side of a pale door
  wall     the tank's front frame, x 21-22 (HARV and HORV)
  neck     x 22-27, 16 up, a dark olive engine block along its middle (x 22-29) to 19
  cab      x 27-42, house colour, 17 up with bevelled edges, its front sloping down from x 35.5 to 13; a black
           windscreen across the slope and round the front corners, small side windows, a pale panel on the roof
  front    a grey scoop plate across the front (x 36-42, to 4 up), four claws past it (the outer two to x 48, 4 up;
           the inner two to x 49, 3 up)
  bed      (HORV) where the tank was: a flat tread plate 9 up over x 0-21 (a lower tailgate at the back)
HARV = HORV + the tank above the bed: the refinery's lid (NTREFN_A) is that tank.

Facings follow the mod (and RA): frame 0 faces north, then counter-clockwise a 32nd of a turn per frame (8 west,
16 south, 24 east).
"""
import numpy as np
import hd

(TYRE, HUB, FRAME, SCOOP, CLAW, TANK, HOOP, DOOR, NECK, ENGINE, CAB, GLASS, ROOF, BED, REAR, WALL, TFRAME) = range(1, 18)
HOUSE = {CAB, REAR}

S = 4.35            # side-on as long as EA's TD harvester (TS's own size, fitted to Luke's docking video, is 3.46)
# the voxel model's point that sits on the unit's position: 3 voxels behind the hull's middle, so the truck stands
# forward of its position as EA's harvesters do
CEN = (24.5 - 3.07, 10.0)

P = dict(
    wheels=(6.5, 12.0, 18.0, 27.0, 33.0), wheel_r=3.5, wheel_y=((1.0, 4.0), (16.0, 19.0)),
    frame=dict(x=(1.0, 41.0), y=(3.0, 17.0), z=7.0),
    # the tank: footprint, its core (inside the side frames), top, the bevel's steps, the side frames' top where the
    # panel is let in (x range) and elsewhere; the hoops; the back posts (house colour) and the door between them
    tank=dict(x=(0.0, 21.0), y=(2.0, 18.0), core=(3.0, 17.0), top=17.0, side_top=15.0,
              panel=dict(x=(5.0, 20.0), band=9.0),
              hoops=((5.0, 7.0), (9.0, 12.0), (13.5, 16.0), (18.0, 20.0)), hoop_y=(5.0, 15.0), hoop_z=(18.0, 19.0),
              posts=dict(x=(0.0, 1.0), ys=((4.0, 7.0), (13.0, 16.0)), top=16.0, sill=8.0), door_x=1.0),
    wall=dict(x=(21.0, 22.0), top=17.0),
    neck=dict(x=(22.0, 27.0), top=16.0),
    engine=dict(x=(22.0, 29.0), y=(7.0, 12.0), top=19.0, ends=18.0),
    cab=dict(x=(27.0, 42.0), y=(2.0, 18.0), top=17.0, bevel=3.0, slope=(35.5, 0.667), nose=(40.6, 4.0)),
    glass=dict(x=40.4, z=(7.0, 13.7), side_x=(36.0, 39.0), side_z=(10.0, 12.0)),
    roof=dict(x=(30.0, 36.5), y=(6.0, 12.0), strip=(12.0, 13.0)),
    scoop=dict(x=(36.0, 42.0), y=(0.0, 20.0), top=4.0),
    claws=(((0.4, 2.4), 48.0, 4.0), ((17.6, 19.6), 48.0, 4.0), ((6.2, 8.0), 49.0, 3.0), ((12.0, 13.8), 49.0, 3.0)),
    claw_x0=42.0,
    bed=dict(x=(1.0, 21.0), top=9.0, tail=(1.0, 2.0, 7.5), seam=(12.0, 14.0)),
)


def heading(frame):
    a = 2 * np.pi * frame / 32.0
    return -np.sin(a), -np.cos(a)


def to_local(X, Y, frame, pos=(0.0, 0.0), s=S):
    """world (units) -> the truck's voxel frame."""
    hx, hy = heading(frame)
    dx, dy = X - pos[0], Y - pos[1]
    fwd = dx * hx + dy * hy
    left = dx * hy - dy * hx
    return fwd / s + CEN[0], CEN[1] - left / s


def to_world(x, y, frame, pos=(0.0, 0.0), s=S):
    hx, hy = heading(frame)
    fwd, left = (x - CEN[0]) * s, (CEN[1] - y) * s
    return pos[0] + fwd * hx + left * hy, pos[1] + fwd * hy - left * hx


def box(x, y, bx, by):
    return (x >= bx[0]) & (x < bx[1]) & (y >= by[0]) & (y < by[1])


def bevel(y, y0, y1, top, steps):
    """a top with its long edges bevelled down a voxel per voxel for `steps` voxels (TS's 14/15/16/17)."""
    d = np.minimum(y - y0, y1 - y)                           # voxels in from the nearer side
    return top - np.clip(steps - np.floor(np.maximum(d, 0.0)), 0, steps)


def tank_field(x, y, p=P):
    """the tank (HARV's, and the lid): heights (voxels, 0 where none) and components, over the truck's frame."""
    t = p['tank']
    H = np.zeros(np.shape(x), np.float32); C = np.zeros(np.shape(x), np.int16)

    def put(h, comp, where):
        nonlocal H, C
        h = np.where(where, h, 0.0)
        win = h > H + 1e-6
        H = np.where(win, h, H); C = np.where(win, comp, C).astype(np.int16)

    x1 = t['x'][0] + t['door_x']                            # behind the posts
    foot = box(x, y, (x1, t['x'][1]), t['y'])
    core = box(x, y, (x1, t['x'][1]), t['core'])
    # the core: its top's long edges and its back end (the first two voxels) a voxel lower
    low = (bevel(y, t['core'][0], t['core'][1], 0.0, 1.0) < 0) | (x < x1 + 2.0)
    put(np.where(low, t['top'] - 1.0, t['top']), TANK, core)
    # the side frames: full height at the ends, a band along the bottom where the panel is let in
    side = foot & ~box(x, y, (-1e9, 1e9), t['core'])
    pan = (x >= t['panel']['x'][0]) & (x < t['panel']['x'][1])
    put(np.where(pan, t['panel']['band'], t['side_top']), TFRAME, side)
    # hoops arched over the middle of the top
    hy0, hy1 = t['hoop_y']
    for (h0, h1) in t['hoops']:
        hm = box(x, y, (h0, h1), (hy0, hy1))
        edge = (y < hy0 + 1.0) | (y >= hy1 - 1.0)
        put(np.where(edge, t['hoop_z'][0], t['hoop_z'][1]), HOOP, hm)
    # the back end: two house-colour posts, a low sill between them in front of the door (the core's back face)
    po = t['posts']
    for ys in po['ys']:
        put(np.full(np.shape(x), po['top']), REAR, box(x, y, po['x'], ys))
    put(np.full(np.shape(x), po['sill']), DOOR, box(x, y, po['x'], (po['ys'][0][1], po['ys'][1][0])))
    return H, C


def scene(X, Y, frame=8, pos=(0.0, 0.0), s=S, p=P, unloading=False, tank_off=None, only=None, lid_off=None):
    """only: 'tank' to model the tank alone (the refinery's lid), shifted back by tank_off voxels.
    lid_off (with unloading): HORV with its tank on it slid back lid_off voxels, nothing of the tank past the truck's
    back end (the refinery's lid as a layer over the HORV unit)."""
    x, y = to_local(X, Y, frame, pos, s)
    H = np.zeros_like(X); C = np.zeros(X.shape, np.int16)
    slabs = []
    sz = s

    def put(h, comp, where):
        nonlocal H, C
        h = np.where(where, h * sz, 0.0)
        win = h > H + 1e-6
        H = np.where(win, h, H); C = np.where(win, comp, C).astype(np.int16)

    def slab(top, bot, comp, where, name=''):
        slabs.append(hd.Slab(np.where(where, top * sz, -1.0).astype(np.float32),
                             np.where(where, np.maximum(bot * sz, 0.0), 0.0).astype(np.float32),
                             np.where(where, comp, 0).astype(np.int16), name))

    if only == 'tank':
        # the refinery's lid: the tank (HARV = HORV + this), slid back by tank_off voxels
        xs = x + (tank_off or 0.0)
        Ht, Ct = tank_field(xs, y, p)
        bed = p['bed']['top']
        m = Ht > 0
        slabs.append(hd.Slab(np.where(m, Ht * sz, -1.0).astype(np.float32), np.where(m, bed * sz, 0.0).astype(np.float32),
                             np.where(m, Ct, 0).astype(np.int16), 'lid'))
        return hd.Scene(np.zeros_like(H), np.zeros_like(C), slabs, {'lx': xs.astype(np.float32), 'ly': y.astype(np.float32)})
    # wheels: cylinders across the truck (slabs: their round tops and bottoms, flat faces at the sides)
    wr = p['wheel_r']
    for wx in p['wheels']:
        dxw = x - wx
        hh = np.sqrt(np.clip(wr * wr - dxw * dxw, 0, None))
        for (y0, y1) in p['wheel_y']:
            m = (np.abs(dxw) < wr) & (y >= y0) & (y < y1)
            slab(wr + hh, wr - hh, TYRE, m, 'tyre')
    f = p['frame']
    put(np.full_like(X, f['z']), FRAME, box(x, y, f['x'], f['y']))
    sc = p['scoop']
    put(np.full_like(X, sc['top']), SCOOP, box(x, y, sc['x'], sc['y']))
    for (ys, x1, top) in p['claws']:
        cm = box(x, y, (p['claw_x0'], x1), ys)
        tip = np.clip((x1 - x) / 2.0, 0.45, 1.0)                     # the claws taper down to their tips
        put(top * tip, CLAW, cm)
    t = p['tank']
    if unloading:
        b = p['bed']
        put(np.where(x < b['tail'][1], b['tail'][2], b['top']), BED, box(x, y, b['x'], t['y']))
    else:
        Ht, Ct = tank_field(x, y, p)
        put(Ht, Ct, Ht > 0)
    w = p['wall']
    put(bevel(y, t['y'][0], t['y'][1], w['top'], 2.0), WALL, box(x, y, w['x'], t['y']))
    n = p['neck']
    put(bevel(y, t['y'][0], t['y'][1], n['top'], 2.0), NECK, box(x, y, n['x'], t['y']))
    e = p['engine']
    ends = (x < e['x'][0] + 1.0) | (x >= e['x'][1] - 2.0)
    put(np.where(ends, e['ends'], e['top']), ENGINE, box(x, y, e['x'], e['y']))
    c = p['cab']
    cab = box(x, y, c['x'], c['y']) & ~((x >= c['nose'][0]) & ((y < c['y'][0] + 2.0) | (y >= c['y'][1] - 2.0)))
    top = bevel(y, c['y'][0], c['y'][1], c['top'], c['bevel']) - np.clip(x - c['slope'][0], 0, None) * c['slope'][1]
    put(np.maximum(top, 5.0), CAB, cab)
    extra = {'lx': x.astype(np.float32), 'ly': y.astype(np.float32)}
    if unloading and lid_off is not None:
        # the tank stays over the bed (nothing of it past the back end), so it goes into the heightfield like HARV's
        xs = x + lid_off
        Ht, Ct = tank_field(xs, y, p)
        keep = (Ht > 0) & (x >= 0.0)
        h = np.where(keep, Ht * sz, 0.0)
        win = h > H + 1e-6
        H = np.where(win, h, H); C = np.where(win, LID_BASE + Ct, C).astype(np.int16)
        extra['tlx'] = xs.astype(np.float32)
    return hd.Scene(H, C, slabs, extra)


LID_BASE = 100          # the tank sliding off HORV (scene(..., unloading=True, lid_off=)): component ids + 100


def merge_slabs(sc):
    """pack slabs that don't overlap into as few as possible (memory: each slab is three full-grid arrays)."""
    packed = []
    for s_ in sc.slabs:
        m = s_.top >= 0
        if not m.any():
            continue
        for q in packed:
            if not (q['m'] & m).any():
                q['top'] = np.where(m, s_.top, q['top']); q['bot'] = np.where(m, s_.bot, q['bot'])
                q['comp'] = np.where(m, s_.comp, q['comp']); q['m'] |= m; q['names'].append(s_.name)
                break
        else:
            packed.append(dict(top=s_.top.copy(), bot=s_.bot.copy(), comp=s_.comp.copy(), m=m.copy(), names=[s_.name]))
    sc.slabs = [hd.Slab(q['top'], q['bot'], q['comp'].astype(np.int16), '+'.join(q['names'])) for q in packed]
    return sc


FLAT = {TYRE: (70, 64, 50), HUB: (130, 130, 130), FRAME: (70, 70, 72), SCOOP: (150, 150, 154), CLAW: (170, 170, 174),
        TANK: (80, 80, 80), HOOP: (140, 140, 140), DOOR: (180, 180, 180), NECK: (150, 150, 154),
        ENGINE: (96, 86, 64), CAB: (0, 200, 0), GLASS: (10, 10, 12), ROOF: (190, 190, 194), BED: (150, 150, 154),
        REAR: (0, 200, 0), WALL: (160, 160, 164), TFRAME: (170, 170, 172)}
