"""
TS Service Depot (GADEPT / GTDEPT; TSDEPT in the mod) as a model for hd.py, and the Dropship Bay (TSDROP: the
depot's pad alone, Westwood's cut GADROP).

Built in its own frame (X east, Y south as TS draws it, units 1 cell = 128, Z up, origin at the centre of TS's 3x3
foundation, X -192..192, Y -192..192), read from GTDEPT / GTDEPTBB / GTDEPTMK / GTDEPT_A.._D in TS's own camera:
  pad      GTDEPTBB, the bib: a big low platform, an octagon with its corners cut a little, sloped sides; a house-green
           octagonal band inset on its top; lavender-grey concrete inside it with two steel gratings along its west
           side and painted guide lines with small lamps in them (GTDEPT_A runs a light along them); a tan rim outside
           the band.  TS's pad is centred a little south-east of the foundation's centre (its top at z 10, so its centre
           is (12.25, 12.25): TS's ring is centred on the frame's ground point)
  gantry   GTDEPT, along the foundation's west edge: a green base plate on the ground; a wall standing on its west
           edge (a house-green panel in a frame, grey ends, a dark top rail with lamps on it; its top slopes down at
           the south end, a green edge there)
  machine  in front of the wall: a dark block with two white guide rails standing out of it towards the pad (v3;
           each a slim upright post with a flat top, its top running back over the block, the corner rounded), the
           repair arm riding in the slot between them; a lamp on the block's face south of the rails (GTDEPT_B lights
           it); the arm folds down into the block
  arm      GTDEPT_C: a green lattice boom rises out of the machine, swings over towards the pad and lowers a grey tool
           onto the vehicle (a spark), then swings back up and sinks into the machine
  odds     a small box with a red light north of the machine; a brown reel at the wall's south end
"""
import numpy as np
import hd
from radr import Acc, rod_interval, in_poly, inbox

(PAD, SKIRT, RIM, BAND, GRATE, GAP, LINE, LAMP, BASE, WALL, PANEL, FRAME, POST, RAIL, STUD, MACH, HOOD, HOODIN, BOX,
 REDL, BROWN, ARM, TOOL, SPARK, SLAB, GTRIM, MKFRAME, GUIDE, LITE) = range(1, 30)
DEBRIS, DEB_IN, DEB_BURNT = 40, 41, 42
HOUSE = {BAND, BASE, PANEL, GTRIM, ARM, FRAME, MKFRAME}

P = dict(
    pad=dict(c=(12.25, 12.25), d=126.0, k2=1.02, w=8.0, h=10.0, band=(101.0, 114.0),
             # the two steel gratings along the west side (x relative to the pad's centre) and the dark gap between
             # v2 (Luke 4 Oct: they read as tyre marks): gone. v1 had grates ((-97, -79), (-59, -39)), gap (-74, -64)
             grates=(), gap=None,
             # painted guide lines (relative to the pad's centre): (x0, y0, x1, y1); lamps every `every` along them
             lines=((-3.0, -100.0, -3.0, -35.0), (-28.0, -12.0, 60.0, -12.0), (28.0, -55.0, 90.0, -55.0),
                    (28.0, -35.0, 92.0, -35.0), (38.0, 7.0, 72.0, 7.0), (29.0, 7.0, 29.0, 95.0)),
             ticks=((-22.0, 25.0, 2.0, 25.0), (-22.0, 58.0, -8.0, 58.0), (55.0, 28.0, 92.0, 28.0)),
             every=9.0, lamp_r=1.8, line_w=2.4),
    base=dict(x=(-187.0, -110.0), y=(-63.0, 80.0), h=5.0, bevel=3.0),
    wall=dict(x=(-192.0, -187.0), y=(-80.0, 80.0), z=70.0, slope_y=42.0, z_south=56.0,
              panel=dict(y=(-42.0, 40.0), z=(8.0, 54.0), frame=4.0),
              rail=dict(z=(57.0, 70.0), out=2.5),
              studs=dict(y0=-76.0, every=11.0, r=2.0, h=3.5),
              north=(-80.0, -42.0), south=(42.0, 80.0), edge=4.0),
    # v2 (Luke 4 Oct: in TS the arm sits wedged between two rails; v1's two chunky hoods side by side didn't read):
    # two slim white rails (inverted-U frames) with an 18-unit gap between them, the arm's pivot in the gap.
    # v1: hoods ys (28, 2), w 23, t 4, x (-138, -126)
    # v3 (Luke 5 Oct: v2's rails still read as two arches; TS's are rails): read from TS's pixels, two straight guide
    # rails standing out of the block towards the pad, 27 apart, 5 thick: an upright post at the front (flat top, the
    # corner rounded), its top running back over the block (TS's white top edges and white front edges, the slot
    # dark between them). The arm rides in the slot. `hoods` is v2's (used only when `rails` is None).
    mach=dict(x=(-156.0, -138.0), y=(-12.0, 40.0), z=36.0,
              hoods=dict(ys=(31.0, -1.0), w=14.0, t=3.0, x=(-136.0, -128.0), z=(5.0, 52.0)), inner=-142.0,
              rails=dict(ys=(27.0, 0.0), t=5.0, post=(-131.5, -125.5), back=-156.0, z=(5.0, 47.0), beam=11.0,
                         bend=6.0, fillet=4.0),
              # GTDEPT_B's lamp: on the block's east face, south of the rails (TS's B lights x 37-39, y 91-96)
              lite=dict(y=(32.0, 39.0), z=(12.0, 33.0), out=1.2)),
    box=dict(x=(-150.0, -130.0), y=(-58.0, -40.0), z=18.0, lamp=(-140.0, -49.0, 21.0, 3.0)),
    # the brown reel at the wall's south foot (TS's red-brown blob); v2: show False = taken off (Luke: it read as a barrel)
    brown=dict(c=(-154.0, 92.0), r=11.0, z=(2.0, 22.0), axis='y', len=(80.0, 104.0), show=False),
    # the repair arm: pivot, boom length and section, the tool hung from its end, the spark at the tool's tip
    arm=dict(p0=(-132.0, 13.5, 39.0), L=100.0, w=14.0, tool=46.0, tw=9.0, spark=4.5),     # v1 p0 (-135.5, 12.5, 39), v2 y 15
)

# 'ra': turned a quarter (TS east -> RA south), so the gantry stands along the plot's north edge facing the camera
# (on RA's camera TS's wall would be seen edge-on) and the arm swings out over the pad towards the viewer.
# 'drop-ra': the Dropship Bay's pad alone, turned the same way and centred on its plot.  off = the local point at the
# world origin.
LAYOUTS = {'ts': dict(turn=False, off=(0.0, 0.0)), 'ra': dict(turn=True, off=(0.0, 0.0)),
           'drop-ts': dict(turn=False, off=(0.0, 0.0)), 'drop-ra': dict(turn=True, off=(12.25, 12.25))}


def to_local(X, Y, layout='ts'):
    L = LAYOUTS[layout]
    x, y = (Y, -X) if L['turn'] else (X, Y)
    return x + L['off'][0], y + L['off'][1]


def to_world(x, y, layout='ts'):
    L = LAYOUTS[layout]
    x, y = x - L['off'][0], y - L['off'][1]
    return (-y, x) if L['turn'] else (x, y)


# ------------------------------------------------------------------------------------------------------ geometry
def cut_oct(cx, cy, d, k2=1.02):
    """the pad's outline: an octagon (edge distance d, normals at k*45 deg) with its corners cut by the octagon turned
    22.5 deg at distance d*k2.  Returns the 16 corners (counter-clockwise in screen terms)."""
    pts = []
    for k in range(16):
        a1, a2 = np.radians(k * 22.5), np.radians((k + 1) * 22.5)
        d1 = d if k % 2 == 0 else d * k2
        d2 = d if (k + 1) % 2 == 0 else d * k2
        # solve n1.p = d1, n2.p = d2
        A = np.array([[np.cos(a1), np.sin(a1)], [np.cos(a2), np.sin(a2)]])
        p = np.linalg.solve(A, [d1, d2])
        pts.append((cx + p[0], cy + p[1]))
    return pts


def oct_dist(x, y, cx, cy, k2=1.02):
    """the 'distance' that cut_oct uses: the largest of the 16 edge functions (so dist <= d is inside)."""
    dx, dy = x - cx, y - cy
    out = None
    for k in range(16):
        a = np.radians(k * 22.5)
        v = dx * np.cos(a) + dy * np.sin(a)
        if k % 2:
            v = v / k2
        out = v if out is None else np.maximum(out, v)
    return out


def quad_interval(x, corners):
    """vertical intervals of a convex polygon in the (x, z) plane over each x: (lo, hi, mask)."""
    lo = np.full(x.shape, np.inf); hi = np.full(x.shape, -np.inf)
    n = len(corners)
    for i in range(n):
        (x1, z1), (x2, z2) = corners[i], corners[(i + 1) % n]
        if abs(x2 - x1) < 1e-9:
            m = np.abs(x - x1) < 0.5
            lo = np.where(m, np.minimum(lo, min(z1, z2)), lo); hi = np.where(m, np.maximum(hi, max(z1, z2)), hi)
            continue
        t = (x - x1) / (x2 - x1)
        m = (t >= 0) & (t <= 1)
        z = z1 + t * (z2 - z1)
        lo = np.where(m, np.minimum(lo, z), lo); hi = np.where(m, np.maximum(hi, z), hi)
    ok = hi > lo
    return np.where(ok, lo, 0.0), np.where(ok, hi, 0.0), ok


def beam_xz(x, y, p0, ang, L, w, yw, s0=0.0):
    """a square beam in the x-z plane: from p0 (3D), at `ang` from vertical towards +x, from s0 to L along its axis,
    w thick (in x-z), across y +-yw/2 of p0's y.  (lo, hi, mask) of z over the ground."""
    u = np.array([np.sin(ang), np.cos(ang)]); nrm = np.array([np.cos(ang), -np.sin(ang)])
    b = np.array([p0[0], p0[2]])
    cs = [b + s0 * u - w / 2 * nrm, b + L * u - w / 2 * nrm, b + L * u + w / 2 * nrm, b + s0 * u + w / 2 * nrm]
    lo, hi, ok = quad_interval(x, [tuple(c) for c in cs])
    ok &= np.abs(y - p0[1]) <= yw / 2
    return lo, hi, ok


def arm_pose(t):
    """GTDEPT_C frame t (0-15) -> (extension 0..1 out of the machine, boom angle from vertical (rad), tool angle from
    vertical (rad), spark).  TS: 0-2 the boom rises, 3-4 it swings over towards the pad, 5-10 it holds there with the
    tool down on the vehicle (a spark at 6), 11-12 back up, 13 upright, 14-15 it sinks back."""
    ext = {0: 0.34, 1: 0.67, 14: 0.67, 15: 0.34}.get(t, 1.0)
    ang = {3: 20.0, 4: 38.0, 11: 38.0, 12: 20.0}.get(t, 53.0 if 5 <= t <= 10 else 0.0)
    tool = {3: 4.0, 4: 12.0, 11: 12.0, 12: 4.0}.get(t, 48.0 if 5 <= t <= 10 else 0.0)
    return ext, np.radians(ang), np.radians(tool), t == 6


PARTS = ('pad', 'base', 'wall', 'mach', 'box', 'brown')
BUILD_KEYS = ('padgrow', 'padrim', 'padtex', 'band', 'wall', 'wallup', 'frame', 'panel', 'mach', 'box', 'brown', 'base',
              'paint')
DONE = {k: 1.0 for k in BUILD_KEYS}


def scene(X, Y, p=None, layout='ts', prog=None, parts=None, level=0, merge=True, pad=None, arm=None):
    """pad True: the bib alone (GTDEPTBB); False: the building alone (GTDEPT); None: both.  arm: GTDEPT_C frame
    (None: folded away, as GTDEPT draws it)."""
    p = P if p is None else p
    g = dict(DONE); g.update(prog or {})
    x, y = to_local(X, Y, layout)
    H = np.zeros_like(X); C = np.zeros(X.shape, np.int16)
    acc = Acc(X.shape)
    extra = {}
    if parts is None:
        parts = PARTS if pad is None else (('pad',) if pad else tuple(k for k in PARTS if k != 'pad'))
    want = lambda k: k in parts
    building = prog is not None

    def put(h, comp, where=None):
        nonlocal H, C
        if where is not None:
            h = np.where(where, h, 0.0)
        win = h > H + 1e-6
        H = np.where(win, h, H); C = np.where(win, comp, C)

    # ------------------------------------------------------------------------------------------------- the pad
    q = p['pad']
    if want('pad'):
        cx, cy = q['c']
        dist = oct_dist(x, y, cx, cy, q['k2'])
        h, w = q['h'], q['w']
        grow = float(np.clip(g['padgrow'], 0, 1)) if building else 1.0
        if grow > 0:
            # the sides slope down from the top's edge (d) to the ground (d + w)
            ztop = np.clip((q['d'] + w - dist) / w, 0, 1) * h
            inside = dist <= q['d'] + w
            if building and grow < 1.0:
                # GTDEPTMK 0-5: the pad is laid from the gantry's side (its west / south-west) across to the
                # north-east, a ragged front
                sweep = (x - cx) * 0.85 - (y - cy) * 0.53
                front = -(q['d'] + w) * 1.05 + 2.1 * (q['d'] + w) * grow
                inside &= sweep <= front + 6.0 * np.sin((x + 2.0 * y) / 23.0)
            put(np.where(inside, ztop, 0.0), PAD)
            C = np.where(inside & (dist > q['d']) & (C == PAD), SKIRT, C)
            topm = (C == PAD)
            # the house-green band, the rim outside it; the gratings and the gap between them (a little sunk)
            b0, b1 = q['band']
            if not building or g['band'] >= 1.0:
                C = np.where(topm & (dist >= b0) & (dist <= b1), BAND, C)
            C = np.where(topm & (dist > b1), RIM, C)
            inner = topm & (dist < b0 - 1.0)
            for (ga, gb_) in q['grates']:
                gm = inner & (x - cx >= ga) & (x - cx <= gb_)
                C = np.where(gm, GRATE, C); H = np.where(gm, H - 1.2, H)
            if q.get('gap'):
                gm = inner & (x - cx >= q['gap'][0]) & (x - cx <= q['gap'][1])
                C = np.where(gm, GAP, C); H = np.where(gm, H - 2.0, H)
            extra['dist'] = dist.astype(np.float32)
            extra['padtex'] = np.full(X.shape, float(g['padtex']) if building else 1.0, np.float32)
    # ------------------------------------------------------------------------------------------------ the gantry
    if want('base') and (not building or g['base'] > 0):
        b = p['base']
        m = inbox(x, y, b['x'], b['y'])
        e = np.minimum(np.minimum(x - b['x'][0], b['x'][1] - x), np.minimum(y - b['y'][0], b['y'][1] - y))
        put(np.where(m, b['h'] * np.clip(0.4 + e / b['bevel'], 0, 1), 0.0), BASE)
    if want('wall'):
        wl = p['wall']
        up = float(np.clip(g['wallup'], 0, 1)) if building else 1.0
        if not building or g['wall'] > 0:
            if up >= 0.999:
                ztop = np.where(y <= wl['slope_y'], wl['z'],
                                wl['z'] - (wl['z'] - wl['z_south']) * np.clip((y - wl['slope_y']) / (wl['y'][1] - wl['slope_y']), 0, 1))
                m = inbox(x, y, wl['x'], wl['y'])
                put(np.where(m, ztop, 0.0), WALL)
                rz = wl['rail']['z']
                # the dark top rail: proud of the wall on its east face
                rm = inbox(x, y, (wl['x'][0], wl['x'][1] + wl['rail']['out']), (wl['y'][0], wl['slope_y']))
                acc.add(np.full(X.shape, rz[0]), np.full(X.shape, rz[1]), RAIL, rm, 'rail')
                # lamps along the rail's top
                st = wl['studs']
                for yy in np.arange(st['y0'], wl['slope_y'] - 2, st['every']):
                    rr = np.hypot(x - (wl['x'][0] + wl['x'][1] + wl['rail']['out']) / 2, y - yy)
                    acc.add(np.full(X.shape, rz[1] - 1.0),
                            rz[1] + st['h'] * np.sqrt(np.clip(1 - (rr / st['r']) ** 2, 0, None)), STUD, rr <= st['r'], 'stud')
                # the green edge at its south end, standing a little proud
                se = inbox(x, y, (wl['x'][0] - 1.0, wl['x'][1] + 1.5), (wl['y'][1] - wl['edge'], wl['y'][1]))
                put(np.where(se, ztop + 1.0, 0.0), GTRIM)
                # green bands across its grey end sections (TS: a green line across each, about a third of the way up)
                for (ya, yb_), zb in ((wl['north'], 25.0), ((wl['south'][0], wl['y'][1] - wl['edge']), 29.0)):
                    bm = inbox(x, y, (wl['x'][1], wl['x'][1] + 1.5), (ya, yb_))
                    acc.add(np.full(X.shape, zb - 2.0), np.full(X.shape, zb + 2.0), GTRIM, bm, 'gband')
                # the panel: a house-green sheet in a frame on the wall's east face (a thin raised plate)
                pn = wl['panel']
                pm = inbox(x, y, (wl['x'][1], wl['x'][1] + 2.0), pn['y'])
                acc.add(np.full(X.shape, pn['z'][0]), np.full(X.shape, pn['z'][1]), PANEL, pm, 'panel')
                fm = inbox(x, y, (wl['x'][1], wl['x'][1] + 3.0), (pn['y'][0] - wl['panel']['frame'], pn['y'][1] + wl['panel']['frame']))
                acc.add(np.full(X.shape, pn['z'][0] - wl['panel']['frame']), np.full(X.shape, pn['z'][1] + wl['panel']['frame']),
                        FRAME, fm & ~pm, 'pframe')
            else:
                # build-up (GTDEPTMK 0-5): the wall lies flat towards the pad, its face up, and is raised about its
                # foot; one green plate (TS draws it green, then as a braced frame) until it stands
                ang = (np.pi / 2) * (1 - up)                     # from vertical, towards the east
                t_ = wl['x'][1] - wl['x'][0]
                u = np.array([np.sin(ang), np.cos(ang)]); nrm = np.array([np.cos(ang), -np.sin(ang)])
                base0 = np.array([wl['x'][0], 0.0])
                cs = [base0, base0 + t_ * nrm, base0 + t_ * nrm + wl['z'] * u, base0 + wl['z'] * u]
                cs = [(c_[0], max(c_[1], 0.0)) for c_ in cs]
                lo, hi, m = quad_interval(x, cs)
                m &= (y >= wl['y'][0]) & (y <= wl['y'][1]) & (hi > 0.2)
                acc.add(np.maximum(lo, 0.0), np.maximum(hi, 1.5), MKFRAME, m, 'wallmk')
                extra['brace'] = np.full(X.shape, float(g['frame']), np.float32)
    if want('mach') and (not building or g['mach'] > 0):
        mc = p['mach']
        fm = float(np.clip(g['mach'], 0, 1)) if building else 1.0
        put(np.where(inbox(x, y, mc['x'], mc['y']), mc['z'] * fm, 0.0), MACH)
        rl = mc.get('rails')
        if rl:
            z0, z1 = rl['z']
            zt = z0 + (z1 - z0) * fm                       # the rails' top (they grow with the block in the build-up)
            px0, px1 = rl['post']; b = rl['bend']
            rr = rl['t'] / 2; ri = rl.get('fillet', 4.0)
            for yc in rl['ys']:
                dy = np.abs(y - yc)
                drop = rr - np.sqrt(np.clip(rr * rr - dy * dy, 0, None))        # a round bar: its section rounded
                # in plan: the post's front rounded
                m = inbox(x, y, (rl['back'], px1), (yc - rr, yc + rr)) & (x <= px1 - rr + np.sqrt(np.clip(rr * rr - dy * dy, 0, None)))
                # the post up the front, bent over at the top (the corner rounded), running back over the block
                top = np.where(x > px1 - b, zt - b + np.sqrt(np.clip(b * b - (x - (px1 - b)) ** 2, 0, None)), zt) - drop
                bot = np.where(x >= px0, z0, np.maximum(zt - rl['beam'], z0))
                # a fillet in the inside corner, under the bend
                cx, cz = px0 - ri, zt - rl['beam'] - ri
                fil = (x >= cx) & (x < px0)
                bot = np.where(fil, np.minimum(bot, cz + np.sqrt(np.clip(ri * ri - (x - cx) ** 2, 0, None))), bot)
                acc.add(bot, top, GUIDE, m & (top > bot), 'guide')
            lt = mc['lite']
            ml = inbox(x, y, (mc['x'][1] - 0.5, mc['x'][1] + lt['out']), lt['y'])
            acc.add(np.full(X.shape, lt['z'][0] * fm), np.full(X.shape, lt['z'][1] * fm), LITE, ml, 'lite')
        hd_ = mc['hoods']
        for yc in (hd_['ys'] if not rl else ()):
            # an arched hood: an inverted U (a half-pipe on two legs) facing east, its inside dark
            r_out = hd_['w'] / 2; r_in = r_out - hd_['t']
            z0, z1 = hd_['z']
            zs = z0 + (z1 - z0 - r_out) * fm                                    # the arch's springing height
            m = inbox(x, y, hd_['x'], (yc - r_out, yc + r_out))
            dy = np.abs(y - yc)
            arch_top = zs + np.sqrt(np.clip(r_out ** 2 - dy ** 2, 0, None))
            inner_top = zs + np.sqrt(np.clip(r_in ** 2 - dy ** 2, 0, None))
            leg = dy >= r_in
            # the hood's shell: legs full height to the springing, the arch over the opening
            acc.add(np.where(leg, z0, inner_top), arch_top, HOOD, m, 'hood')
            # its dark inside (the back of the opening), set a little back
            mi = inbox(x, y, (hd_['x'][0] - 4.0, hd_['x'][0] + 2.0), (yc - r_in, yc + r_in))
            acc.add(np.full(X.shape, z0), inner_top, HOODIN, mi, 'hoodin')
    if want('box') and (not building or g['box'] > 0):
        bx = p['box']
        put(np.where(inbox(x, y, bx['x'], bx['y']), bx['z'], 0.0), BOX)
        lx, ly, lz, lr = bx['lamp']
        rr = np.hypot(x - lx, y - ly)
        put(np.where(rr <= lr, lz + 1.2 * np.sqrt(np.clip(1 - (rr / lr) ** 2, 0, None)), 0.0), REDL)
    if want('brown') and (not building or g['brown'] > 0) and p['brown'].get('show', True):
        br = p['brown']
        cx_, zc_ = br['c'][0], (br['z'][0] + br['z'][1]) / 2
        r = br['r']
        m = (np.abs(x - cx_) <= r) & (y >= br['len'][0]) & (y <= br['len'][1])
        hh = np.sqrt(np.clip(r * r - (x - cx_) ** 2, 0, None))
        acc.add(zc_ - hh, zc_ + hh, BROWN, m, 'reel')
    # ------------------------------------------------------------------------------------------- the repair arm
    if arm is not None and (want('mach') or want('arm')):
        a = p['arm']
        ext, ang, tang, spark = arm_pose(int(arm) % 16)
        p0 = np.array(a['p0'])
        # the boom: sunk into the machine by (1 - ext) of its length
        s0 = -a['L'] * (1 - ext)
        lo, hi, m = beam_xz(x, y, p0, ang, a['L'] * ext + 0.0, a['w'], a['w'], s0=max(s0, -a['L']))
        lo = np.maximum(lo, p['mach']['z'] - 2.0)
        acc.add(lo, hi, ARM, m & (hi > lo), 'arm')
        tip = p0 + a['L'] * ext * np.array([np.sin(ang), 0.0, np.cos(ang)])
        if ang > 0.05 or tang > 0.05:
            # the tool hangs from the boom's end, angled out towards the pad
            lo, hi, m = beam_xz(x, y, tip, np.pi - tang, a['tool'], a['tw'], a['tw'])
            acc.add(np.maximum(lo, 0.0), hi, TOOL, m, 'tool')
            if spark:
                tt = tip + a['tool'] * np.array([np.sin(tang), 0.0, -np.cos(tang)])
                rr2 = (x - tt[0]) ** 2 + (y - tt[1]) ** 2
                sh = np.sqrt(np.clip(a['spark'] ** 2 - rr2, 0, None))
                acc.add(tt[2] - sh, tt[2] + sh, SPARK, rr2 <= a['spark'] ** 2, 'spark')
    extra['paint'] = np.full(X.shape, g['paint'], np.float32)
    return hd.Scene(H, C, acc.slabs(), extra)


FLAT = {PAD: (150, 150, 176), SKIRT: (200, 200, 200), RIM: (170, 150, 110), BAND: (0, 200, 0), GRATE: (70, 70, 80),
        GAP: (20, 20, 20), LINE: (220, 220, 220), LAMP: (255, 255, 255), BASE: (0, 190, 0), WALL: (150, 150, 150),
        PANEL: (0, 160, 0), FRAME: (0, 220, 0), POST: (190, 190, 190), RAIL: (30, 30, 30), STUD: (200, 160, 100),
        MACH: (60, 60, 64), HOOD: (230, 230, 230), HOODIN: (30, 30, 40), BOX: (110, 110, 110), REDL: (220, 30, 20),
        GUIDE: (232, 232, 232), LITE: (90, 90, 100),
        BROWN: (120, 60, 40), ARM: (0, 210, 0), TOOL: (120, 120, 140), SPARK: (255, 255, 255), SLAB: (150, 150, 150),
        GTRIM: (0, 230, 0), MKFRAME: (0, 200, 0)}
