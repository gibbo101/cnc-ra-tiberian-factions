"""
TS GDI Construction Yard (GACNST -> TSFACT) as a model for hd.py.

World: units, 1 cell = 128, origin at the centre of TS's 3x3 foundation, x east, y south, z up.

Measured from GTCNST / GTCNSTMK in TS's own camera (landmarks within ~3 TS px, see yfeat.py):
  * a hangar 2 cells long north-south (y -158 .. 98) on TS's 3x3 pad, a cell of apron to the south
  * cross-section, west to east: a barrel vault from the west foot rail up to its crown (~1 cell high, a
    little east of the middle), curving down past the fans, then a flat diagonal straight down to a kerb
    along the east side; a long window box juts out where the curve meets the diagonal (its top grey-brown
    coping, a dark window in its face), and the diagonal carries on under it
  * west half of the vault: grey panels between seven green ribs a third of a cell apart, a lamp on the
    crown of each; east half: solid green cladding with three fans
  * open to the south in the west part (the arch), closed by a grey ribbed wall with a door in the east part,
    the deep south rib framing both
  * two green stacks on the roof; a crane on the apron with its boom leaning into the arch, a claw below it
"""
import numpy as np
import hd

# components
(PAD, KERB, RAIL, RIB, PANEL, ROOF, EWALL, SWALL, INSIDE, CORNICE, SLOT, FAN, STACK, LAMP,
 BOOM, CBASE, CLAW, NWALL, DOOR, FANHUB, CAB, CWEIGHT, WFRAME, GLASS, BOX, DLAMP, CRATE, TRACK) = range(1, 29)

# build-up controls (0 .. 1 each); the finished building has them all at 1
BUILD_KEYS = ('mcv', 'pad', 'rail', 'ribs', 'clad', 'panels', 'fans', 'box', 'crane', 'stacks', 'lamps', 'door')
DONE = {k: 1.0 for k in BUILD_KEYS}
HOUSE = {RAIL, RIB, ROOF, EWALL, STACK, BOOM, CBASE, CAB}

P = dict(
    pad_h=4.0, chamfer=-309.0,                     # pad; its SW corner cut where x - y < chamfer
    yN=-158.0, yS=98.0,                            # hangar's north and south ends
    xw=-184.0, xc=48.0, crown=123.0,               # west foot, crown position and height
    a_up=87.3,                                     # east of the crown the vault curves down (semi-axis) ...
    diag=(137.0, 45.0, 160.0, 12.0),               # ... to a flat diagonal: from (x, z) to the kerb (x, z)
    # the window box juts out of the east slope: its top from (x0, z0) to (x1, z1), its face at xf down to zf
    box=dict(x0=106.0, z0=92.0, x1=134.0, z1=84.0, xf=135.5, zf=45.0, y0=-152.0, y1=72.0,
             glass=(54.0, 76.0)),
    kerb_w=25.0, kerb_h=9.0,
    shell=7.0,                                     # vault shell thickness (open west part)
    n_ribs=7, rib_w=13.0, rib_up=4.5,
    rib0_depth=24.0,                               # the south rib (the arch) is a deep member
    x_open=28.0,                                   # the arch is open from the west foot to here
    door=(31.0, 49.0, 44.0),                       # door in the south wall: x0, x1, height
    door_lamp=(34.0, 46.5),                        # a lamp over the top-left of the doorway (x, z)
    rail_w=12.0, rail_h=12.0,
    stacks=((-40.0, -70.0, 9.0, 60.0), (-62.0, -60.0, 3.2, 54.0)),   # x, y, radius, height above roof
    fan_x=76.0, fans_y=(46.0, -30.0, -106.0), fan_r=17.0, fan_depth=8.0,
    apron=192.0,                                   # south edge of the pad
    crane=dict(base=(124.0, 150.0), base_wh=(60.0, 44.0), base_h=20.0, pivot=(114.0, 146.0), pivot_h=34.0,
               tip=(-76.0, 110.0, 66.0), boom_w=10.0, boom_t=9.0, tail=26.0, claw_drop=34.0),
)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# The MCV arrives where the unit deployed: MCV_FROM is the world point under the deploying unit's
# centre (set per view), and it faces south-west there, as the unit does when it deploys. While the
# build-up's 'drive' runs 0 -> 1 it drives to its parked pose over the crane's base. POSE holds the
# current pose (centre, turn) for the materials, None when parked.
MCV_FROM = None
MCV_CENTRE = (-23.0, 0.0)          # the unfolded MCV's centre, relative to the crane's base
MCV_TURN = -np.pi / 4              # from the parked heading (cab west) to south-west
POSE = None


def mcv_pose(p, drive):
    """(centre, turn) of the MCV group at drive 0..1, or None once it is parked."""
    if MCV_FROM is None or drive >= 1:
        return None
    bx, by = p['crane']['base']
    px, py = bx + MCV_CENTRE[0], by + MCV_CENTRE[1]
    fx, fy = MCV_FROM
    return (fx + (px - fx) * drive, fy + (py - fy) * drive), MCV_TURN * (1 - drive)


def to_parked(X, Y, p=P, pose=None):
    """world points -> where they sit on the parked MCV group (identity when parked)."""
    pose = POSE if pose is None else pose
    if pose is None:
        return X, Y
    (cx, cy), a = pose
    bx, by = p['crane']['base']
    dx, dy = X - cx, Y - cy
    c, s = np.cos(-a), np.sin(-a)
    return (bx + MCV_CENTRE[0] + c * dx - s * dy, by + MCV_CENTRE[1] + s * dx + c * dy)


def from_parked(x, y, p=P, pose=None):
    """a point on the parked MCV group -> where it is in the world now."""
    pose = POSE if pose is None else pose
    if pose is None:
        return x, y
    (cx, cy), a = pose
    bx, by = p['crane']['base']
    dx, dy = x - (bx + MCV_CENTRE[0]), y - (by + MCV_CENTRE[1])
    c, s = np.cos(a), np.sin(a)
    return cx + c * dx - s * dy, cy + s * dx + c * dy


# ----------------------------------------------------------------------------------------------- profile
def diag_z(x, p=P):
    xa, za, xb, zb = p['diag']
    return za + (zb - za) * (x - xa) / (xb - xa)


def x_join(p=P):
    """where the curved east roof meets the flat diagonal."""
    xs = np.linspace(p['xc'], p['diag'][2], 4001)
    zc, a = p['crown'], p['a_up']
    zv = zc * np.sqrt(np.clip(1 - ((xs - p['xc']) / a) ** 2, 0, None))
    d = zv - diag_z(xs, p)
    cross = np.nonzero((d[:-1] > 0) & (d[1:] <= 0))[0]          # curve drops below the diagonal
    return float(xs[cross[-1] + 1])


def roof_z(x, p=P):
    """outer roof height across the hangar (west foot -> crown -> curve -> diagonal -> kerb); < 0 outside."""
    xw, xc, zc = p['xw'], p['xc'], p['crown']
    zw = zc * np.sqrt(np.clip(1 - ((x - xc) / (xc - xw)) ** 2, 0, None))
    zv = zc * np.sqrt(np.clip(1 - ((x - xc) / p['a_up']) ** 2, 0, None))
    xj = x_join(p)
    z = np.where(x <= xc, zw, np.where(x <= xj, zv, diag_z(x, p)))
    return np.where((x >= xw) & (x <= p['diag'][2]), z, -1.0)


def box_z(x, p=P):
    """the window box's top (coping), then its face straight down; < 0 outside it (in x)."""
    b = p['box']
    top = b['z0'] + (b['z1'] - b['z0']) * (x - b['x0']) / (b['x1'] - b['x0'])
    face = b['z1'] + (b['zf'] - b['z1']) * np.clip((x - b['x1']) / (b['xf'] - b['x1']), 0, 1)
    z = np.where(x <= b['x1'], top, face)
    return np.where((x >= b['x0']) & (x <= b['xf']), z, -1.0)


def roof_inner(x, p=P):
    t = p['shell']
    xw, xc, zc = p['xw'] + t, p['xc'], p['crown'] - t
    return np.where(x >= xw, zc * np.sqrt(np.clip(1 - ((x - xc) / (xc - xw)) ** 2, 0, None)), 0.0)


def rib_y(k, p=P):
    return p['yS'] - k * (p['yS'] - p['yN']) / (p['n_ribs'] - 1)


def rib_index(y, p=P):
    step = (p['yS'] - p['yN']) / (p['n_ribs'] - 1)
    k = np.clip(np.round((p['yS'] - y) / step), 0, p['n_ribs'] - 1)
    yk = p['yS'] - k * step
    return np.abs(y - yk), k, yk


def box(X, Y, x0, x1, y0, y1):
    return (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1)


# ----------------------------------------------------------------------------------------------- scene
def scene(X, Y, p=P, prog=None, crane_pose=None, open_roof=0.0, crate=None):
    """prog: build-up controls (BUILD_KEYS, 0..1; None = finished).  open_roof: kept for experiments
    (the production animation keeps the roof shut).  crate: (x, y, size) of a crate on the hangar floor."""
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

    yS, yN = p['yS'], p['yN']
    # pad (TS's whole foundation, its south-west corner cut); the RA version trims the apron
    padm = box(X, Y, -192, 192, -192, p['apron']) & (X - Y >= p['chamfer'])
    if g['pad'] < 1:
        mx, my = p['crane']['base'] if MCV_FROM is None else MCV_FROM
        padm &= (np.abs(X - mx) <= 30 + 390 * g['pad']) & (np.abs(Y - my) <= 24 + 390 * g['pad'])
        padm &= g['pad'] > 0
    put(np.full_like(X, p['pad_h']), PAD, padm)

    along = (Y >= yN) & (Y <= yS)
    zo = roof_z(X, p)
    drib, k, yk = rib_index(Y, p)
    on_rib = drib <= p['rib_w'] / 2
    rib_zone = X < p['xc'] + 10                      # ribs stand proud on the grey west half only
    rib_add = p['rib_up'] * smoothstep(p['xc'] + 12, p['xc'], X)
    y_sw = yS - 4.0                                  # the south wall, just behind the south rib's face
    in_rib0 = Y > yS - p['rib_w']

    # build-up: each rib grows from the west foot up and over; the east part is clad from the north
    x_rib_end = x_join(p)
    fk = np.clip(g['ribs'] * 1.25 - 0.04 * (p['n_ribs'] - 1 - k), 0, 1)       # the north ribs lead
    rib_grown = X <= p['xw'] + (x_rib_end - p['xw']) * fk
    clad_front = yN + (y_sw - yN + 1) * g['clad']
    # ---- closed east part (behind the south wall): the roof right down to the kerb
    closed = (Y >= yN) & (Y <= np.minimum(y_sw, clad_front)) & (X >= p['x_open'] - 6) & (g['clad'] > 0)
    put(np.where(on_rib, zo + rib_add, zo), ROOF, closed & (zo > 0))
    # the window box jutting out where the curve meets the diagonal
    b = p['box']
    inb = closed & (Y >= b['y0']) & (Y <= b['y1'])
    bz_ = box_z(X, p)
    put(zo + (bz_ - zo) * g['box'], BOX, inb & (bz_ > 0) & (g['box'] > 0))
    # kerb along the east foot (comes with the pad)
    xe = p['diag'][2]
    put(np.full_like(X, p['kerb_h']), KERB, box(X, Y, xe - 2, xe + p['kerb_w'], yN - 6, yS) & padm)
    # the ribs over the part not yet clad (free-standing arches during the build-up)
    if g['clad'] < 1 or g['ribs'] < 1:
        free = on_rib & (X >= p['x_open'] - 6) & (X <= x_rib_end) & rib_grown & ~closed & along & (g['ribs'] > 0)
        slab(zo + p['rib_up'], np.maximum(zo - 9.0, 0.0), RIB, free & (zo > 0) & ~in_rib0, 'ribs_free')

    # ---- the south rib: a deep arch across the whole front (a slab: the wall and the opening are under it)
    rib0 = in_rib0 & (Y <= yS) & (zo > 0)
    zi = roof_inner(X, p)
    r0_bot = np.where(X < p['x_open'], np.maximum(zi - p['rib0_depth'] + 6, 0), zo - p['rib0_depth'])
    # one continuous piece down to the ground (a solid part and a slab meeting would leave a crease)
    if g['clad'] < 1:
        rib0 &= rib_grown | ((X >= p['x_open'] - 6) & (Y <= clad_front + p['rib_w']))
        r0_bot = np.where(X >= p['x_open'] - 6, np.maximum(zo - 9.0, 0.0), r0_bot)
        rib0 &= (X < p['x_open'] - 6) | (X <= x_rib_end) | (Y <= clad_front + p['rib_w'])
    rib0 &= g['ribs'] > 0
    slab(zo + p['rib_up'], np.where(r0_bot <= p['pad_h'] + 1, 0.0, r0_bot), RIB, rib0, 'rib0')
    # front face of the closed part: the south wall (behind the rib) - part of the solid above
    # door
    dx0, dx1, dh = p['door']
    door = box(X, Y, dx0, dx1, y_sw - 6, y_sw + 0.5)
    lx, lz = p['door_lamp']
    dl = (np.hypot(X - lx, Y - (y_sw + 1.5)) <= 2.2) & (g['door'] >= 0.5) & (g['clad'] >= 1)
    slab(np.full_like(X, lz + 2.2), np.full_like(X, lz - 2.2), DLAMP, dl, 'doorlamp')
    H = np.where(door & (H > dh), H, np.where(door, np.minimum(H, p['pad_h']), H))
    C = np.where(door & (H <= p['pad_h'] + 0.1), DOOR, C)

    # ---- open west part: the vault shell over the hangar floor, ribs deeper and proud
    openpart = along & (X < p['x_open']) & (zo > 0) & ~in_rib0
    top = zo + np.where(on_rib & rib_zone, p['rib_up'], 0.0)
    bot = np.where(on_rib, np.maximum(zi - 5.0, 0), zi)
    # near the foot the shell comes down to the floor: the same slab, solid to the ground there
    low = openpart & (bot <= p['pad_h'] + 0.5)
    if open_roof > 0:
        # the front two bays' panels slide up the vault towards the crown
        front = (Y > rib_y(2, p) + p['rib_w'] / 2) & ~on_rib & ~in_rib0
        lim = p['xw'] + 14 + (p['xc'] - 24 - p['xw']) * open_roof
        gone = openpart & front & (X < lim) & ~low
        openpart = openpart & ~gone
    if g['ribs'] < 1 or g['panels'] < 1:
        grown_panel = X <= p['xw'] + (p['xc'] - p['xw']) * g['panels']
        openpart &= np.where(on_rib, rib_grown & (g['ribs'] > 0), grown_panel & (g['panels'] > 0))
    slab(top, np.where(low, 0.0, bot), np.where(on_rib, RIB, PANEL), openpart, 'shell')
    # back (north) wall inside (with the panels) and the hangar floor
    put(np.where(zo > 0, zo, 0.0), NWALL, box(X, Y, p['xw'], p['x_open'], yN, yN + 8) & (zo > 0) & (g['panels'] >= 1))
    floor = along & (X < p['x_open']) & (X > p['xw'] + 6) & (g['panels'] >= 1)
    C = np.where(floor & (C == PAD), INSIDE, C)
    # west foot rail
    rail_s = yS + 2 - (yS - yN + 4) * g['rail']                    # slides out north along the west edge
    put(np.full_like(X, p['rail_h']), RAIL, box(X, Y, p['xw'] - 4, p['xw'] + p['rail_w'], rail_s, yS + 2) & (g['rail'] > 0) & padm)

    # ---- fans: round housings sunk into the east slope (hub and blades are painted)
    for fy in (p['fans_y'] if g['fans'] >= 0.5 else ()):
        d = np.hypot(X - p['fan_x'], Y - fy)
        ring = (d <= p['fan_r'] + 3.0) & (d > p['fan_r']) & closed
        put(zo + 2.0, FAN, ring)
        hole = (d <= p['fan_r']) & closed
        H = np.where(hole, zo - p['fan_depth'], H)
        C = np.where(hole, FANHUB, C)

    # ---- stacks
    for (sx, sy, sr, sh) in (p['stacks'] if (g['stacks'] > 0 and g['clad'] >= 1) else ()):
        d = np.hypot(X - sx, Y - sy)
        sh = sh * g['stacks']
        zb = float(roof_z(np.array([sx]), p)[0])
        put(np.full_like(X, zb + sh), STACK, d <= sr)
        put(np.full_like(X, zb + sh + 2.5), STACK, (d <= sr + 1.5) & (d > sr - 1.5) & (sr > 5))
        put(np.full_like(X, zb + 5.0), STACK, d <= sr + 3.0)

    # ---- lamps on the crown of every rib (small slabs sitting on the rib)
    lamp = np.zeros_like(X, bool)
    for kk in range(p['n_ribs']):
        # the end ribs are the building's edges: their lamps sit in on the rib, not hanging off the end
        yl = np.clip(rib_y(kk, p), yN + p['rib_w'] / 2, yS - p['rib_w'] / 2)
        lamp |= np.hypot(X - p['xc'], (Y - yl) * 1.0) <= 3.0
    slab(zo + p['rib_up'] + 3.0, zo, LAMP, lamp & (zo > 0) & (g['ribs'] >= 1) & (g['clad'] >= 1), 'lamps')

    # ---- crane
    cr = p['crane'] if crane_pose is None else dict(p['crane'], **crane_pose)
    bx, by = cr['base']; bw, bd = cr['base_wh']
    m = g['mcv']
    global POSE
    POSE = mcv_pose(p, g.get('drive', 1.0))
    Xw, Yw = X, Y
    X, Y = to_parked(Xw, Yw, p)
    if m < 1:
        # the MCV: a long tracked body with a cab at its west end, folding down into the crane's base
        L_ = 1 - m
        body = box(X, Y, bx - bw / 2 - 58 * L_, bx + bw / 2 + 14 * L_, by - bd / 2 - 6 * L_, by + bd / 2 + 6 * L_)
        put(np.full_like(X, cr['base_h'] + 4 * L_), CBASE, body)
        for side in (-1, 1):
            tr = box(X, Y, bx - bw / 2 - 64 * L_, bx + bw / 2 + 18 * L_, by + side * (bd / 2 + 6 * L_) - 7 * L_ - 0.01,
                     by + side * (bd / 2 + 6 * L_) + 7 * L_ + 0.01)
            put(np.full_like(X, 13.0 * L_ + 0.01), TRACK, tr & (L_ > 0.05))
        cab = box(X, Y, bx - bw / 2 - 58 * L_, bx - bw / 2 - 30 * L_, by - bd / 2 + 4, by + bd / 2 - 4)
        put(np.full_like(X, cr['base_h'] + 16 * L_), CAB, cab & (L_ > 0.05))
    put(np.full_like(X, cr['base_h']), CBASE, box(X, Y, bx - bw / 2, bx + bw / 2, by - bd / 2, by + bd / 2))
    px_, py_ = cr['pivot']
    put(np.full_like(X, cr['pivot_h']), CAB, np.hypot(X - px_, Y - py_) <= 16.0)
    tx, ty, tz = cr['tip']
    if g['crane'] < 1:
        fold = np.array([px_ - 118.0, py_ + 2.0, cr['pivot_h'] + 2.0])           # lying west along the MCV
        rest = np.array([tx, ty, tz])
        s_ = g['crane']
        # swing up: interpolate the direction, keep the length growing (telescoping out)
        tx, ty, tz = fold + (rest - fold) * (s_ * s_ * (3 - 2 * s_))
        cr = dict(cr, claw_drop=cr['claw_drop'] * max(s_, 0.25))
    L3 = np.array([tx - px_, ty - py_, tz - cr['pivot_h']])
    u = L3 / np.linalg.norm(L3)
    tail = (px_ - u[0] * cr['tail'], py_ - u[1] * cr['tail'], cr['pivot_h'] - u[2] * cr['tail'] + 2)
    X, Y = Xw, Yw
    tail = from_parked(tail[0], tail[1], p) + (tail[2],)
    tx, ty = from_parked(tx, ty, p)
    b_ = beam_slab(X, Y, tail, (tx, ty, tz), cr['boom_w'], cr['boom_t'], BOOM); b_.name = 'boom'
    slabs.append(b_)
    cw = np.hypot(X - tail[0], Y - tail[1]) <= 11.0
    slab(np.full_like(X, tail[2] + 12), np.full_like(X, max(tail[2] - 10, 0)), CWEIGHT, cw, 'cweight')
    # claw under the tip: a cable and a three-fingered grab (or lying on the ground when it has fallen)
    cx_, cy_, cz_ = cr.get('claw_at', (tx, ty, tz - cr['claw_drop']))
    if g['crane'] < 0.5:
        cx_, cy_, cz_ = -500.0, -500.0, 0.0                                        # the claw goes on last
    dc = np.hypot(X - cx_, Y - cy_)
    if 'claw_at' not in cr and g['crane'] >= 0.5:
        slab(np.full_like(X, tz - 3.0), np.full_like(X, cz_ + 8), CLAW, dc <= 1.6, 'cable')
    ang = np.arctan2(Y - cy_, X - cx_)
    finger = (np.abs(np.mod(ang * 3 / (2 * np.pi) + 0.5, 1.0) - 0.5) < 0.11) & (dc <= 15.0)
    zf = cz_ + 8 - 1.1 * dc
    slab(zf + 5.0, zf - 3.0, CLAW, finger, 'fingers')
    slab(np.full_like(X, cz_ + 14), np.full_like(X, cz_ + 5), CLAW, dc <= 7.0, 'grab')
    if crate is not None:
        cx, cy, cs = crate
        if cs > 0.5:
            cbox = (np.abs(X - cx) <= cs) & (np.abs(Y - cy) <= cs * 0.8)
            put(np.full_like(X, p['pad_h'] + cs * 1.1), CRATE, cbox)
            put(np.full_like(X, p['pad_h'] + cs * 1.1 + 1.5), CRATE, cbox & (np.abs(X - cx) <= cs - 2) & (np.abs(Y - cy) <= cs * 0.8 - 2))
    return hd.Scene(H, C, slabs)


def beam_slab(X, Y, a, b, w, t, comp):
    """a straight beam from point a to b (world), rounded section w (half-width across) x t (half-thickness),
    as a slab."""
    ax, ay, az = a; bx, by, bz = b
    L = np.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / L, (by - ay) / L
    s = (X - ax) * ux + (Y - ay) * uy
    c = -(X - ax) * uy + (Y - ay) * ux
    f = s / L
    on = (np.abs(c) <= w) & (f >= 0) & (f <= 1)
    zc = az + (bz - az) * np.clip(f, 0, 1)
    slope = abs(bz - az) / L
    tv = t * np.sqrt(1 + slope * slope)
    prof = np.sqrt(np.clip(1 - (c / w) ** 2, 0, 1)) ** 0.35
    top = np.where(on, zc + tv * prof, -1.0)
    bot = np.where(on, zc - tv * prof, 0.0)
    return hd.Slab(top, np.maximum(bot, 0.0), np.where(on, comp, 0).astype(np.int16))


# ----------------------------------------------------------------------------------------------- colours
FLAT = {PAD: (150, 150, 146), KERB: (160, 150, 120), RAIL: (0, 150, 0), RIB: (0, 200, 0), PANEL: (120, 116, 104),
        ROOF: (0, 170, 0), EWALL: (0, 120, 0), SWALL: (160, 160, 158), INSIDE: (40, 40, 40),
        CORNICE: (150, 138, 108), SLOT: (0, 60, 0), FAN: (110, 110, 110), STACK: (0, 180, 0),
        LAMP: (255, 150, 0), BOOM: (0, 210, 0), CBASE: (0, 150, 0), CLAW: (130, 130, 130),
        NWALL: (40, 40, 40), DOOR: (20, 20, 20), FANHUB: (40, 40, 40), CAB: (0, 170, 0), CWEIGHT: (0, 120, 0),
        WFRAME: (150, 138, 108), GLASS: (0, 70, 20), BOX: (150, 138, 108), DLAMP: (255, 255, 0), CRATE: (150, 110, 60),
        TRACK: (50, 50, 52)}
