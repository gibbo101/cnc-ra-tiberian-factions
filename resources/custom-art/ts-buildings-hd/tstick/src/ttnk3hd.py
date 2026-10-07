"""ttnk3hd.py - the Tick Tank (TS [TTNK]) v3: Westwood's own render of it (the official art Luke sent) followed closely,
at the in-game voxel's size and place (TTNK.VXL's index space: x 0-31 back to front, y 0-21 right to left, z up; the
unit's position, TS's HVA origin, at x 18.56, y 10.5), with a turret that turns (TS's couldn't; RA can):

  side hulls  two long, narrow armour hulls over the tracks (y 0-5.3 and 15.7-21): a house-colour top running down over
              the sloped nose, side skirts in a darker house colour (the render's dark maroon is its Nod red in
              shade) with thin trim lines in the full house colour, the back sloping down; a
              black lamp dome with a white lens on each nose, a small dark box at each back corner
  tracks      khaki, under the hulls, their fronts showing below the noses with an olive sprocket
  centre      the wide camouflaged centre body (y 5.3-15.7): two big rounded humps along its back half, standing
              above the hulls; a flat deck in front of them carrying the turret; the front sloping down to the drum
  drum        the white knurled grinding drum across the whole front of the centre body, a big blade raking forward
              and down from each end
  pipes       the twin white pipes on the left hull, two-thirds of the way back, by its inner edge
  turret      on a ring on the deck, its pivot on the unit's position: the render's two house-colour C-shaped
              brackets either side of the black breech, the short grey gun beside the right bracket, the round
              house-colour hatch with two small lights behind (frames of its own: it turns)
"""
import os
import numpy as np
import hdv
import nvox as N
from wnoise import noise

YC = 10.5                          # the centre line (index space)
PIVOT_X = 18.559                   # the unit's position (TS's HVA origin) along x: the turret turns about it
DECK_Z = 6.9                       # the deck the turret ring stands on (level: the turret turns on it)
HIGH_BACK = bool(int(os.environ.get('HIGH_BACK', '1')))   # v3.4 (Luke 7 Oct): the middle's back raised (the ramps), a bigger flat top dug in
HIGH_SIDES = bool(int(os.environ.get('HIGH_SIDES', '0')))  # v3.5 (Luke 7 Oct): the side hulls stay as v3.3; only the middle is raised
TOP_BACK, TOP_FRONT = (9.8 if HIGH_SIDES else 8.4), 5.95    # the hull tops' height at the back (x 2.2) and the front (x 27.65): low at the front
HUMP = dict(c=(7.7, 8.4), r=(6.8, 3.35, 2.1), tilt=12.0, ys=(8.6, 12.4))   # the humps: rising toward the back


def top(x):
    """the hull tops' height at x (index): a wedge, low at the front, high at the back."""
    return TOP_BACK + (x - 2.2) * (TOP_FRONT - TOP_BACK) / (27.65 - 2.2)


def hump_top(x, dy=0.0):
    """the height of a hump's surface at x, dy across from its crest line (index; the humps are tilted ellipsoids)."""
    (cx, cz), (rx, ry, rz), th = HUMP['c'], HUMP['r'], np.radians(HUMP['tilt'])
    k = np.sqrt(max(0.0, 1 - (dy / ry) ** 2))
    t = np.linspace(0, 2 * np.pi, 2000)
    px = cx + k * (rx * np.cos(t) * np.cos(th) + rz * np.sin(t) * np.sin(th))
    pz = cz + k * (-rx * np.cos(t) * np.sin(th) + rz * np.sin(t) * np.cos(th))
    near = np.abs(px - x) < 0.05
    return float(pz[near].max()) if near.any() else None


RAMP = dict(x_front=15.2, x_top=4.0, z_top=10.4, r_back=3.0, z_floor=2.8)
if HIGH_BACK:
    RAMP.update(x_top=2.6, z_top=11.6, r_back=1.6)


def ramp_top(x):
    """the ramps' top height at x (index)."""
    R = RAMP
    if x >= R['x_front']:
        return DECK_Z
    if x >= R['x_top']:
        return DECK_Z + (R['z_top'] - DECK_Z) * (R['x_front'] - x) / (R['x_front'] - R['x_top'])
    dx = R['x_top'] - x
    return R['z_top'] - R['r_back'] + np.sqrt(max(R['r_back'] ** 2 - dx * dx, 0.0))


def ramp_profile():
    """the ramps' side profile (x, z), convex: the floor, the front at the deck, the rising top, the round at the back,
    the flat back face."""
    R = RAMP
    x_back = R['x_top'] - R['r_back']
    pts = [(x_back, R['z_floor']), (R['x_front'] + 0.4, R['z_floor']), (R['x_front'] + 0.4, DECK_Z - 0.2),
           (R['x_front'], DECK_Z)]
    for a in np.linspace(0, np.pi / 2, 9):
        pts.append((R['x_top'] - R['r_back'] * np.sin(a), R['z_top'] - R['r_back'] + R['r_back'] * np.cos(a)))
    return pts


def M_(y):
    return 2 * YC - y


# ------------------------------------------------------------------------------------------------- patterns
def camo(r, m, it):
    """Westwood's camouflage: near-black with small olive blotches, sparse yellow-olive flecks and grey-white mottling
    (fixed on the part: sampled in its own frame)."""
    u, v, w = r.lu[m], r.lv[m], r.lw[m]
    X = u + 0.55 * w; Y = v - 0.45 * w + 0.3 * u
    n1 = noise(X, Y, 1.5, 11) + 0.5 * noise(X, Y, 0.7, 13)
    n2 = noise(X + 3.1, Y - 1.7, 0.6, 23)
    n3 = noise(X - 2.3, Y + 4.1, 0.9, 37)
    base = np.array([26, 28, 22], np.float32)
    olive = np.array([74, 78, 42], np.float32)
    yel = np.array([170, 156, 70], np.float32)
    grey = np.array([150, 152, 146], np.float32)
    t1 = np.clip((n1 - 0.25) / 0.45, 0, 1)[:, None]
    t2 = np.clip((n2 - 1.2) / 0.4, 0, 1)[:, None]
    t3 = np.clip((n3 - 1.0) / 0.4, 0, 1)[:, None] * 0.85
    c = base[None, :] * (1 - t1) + olive[None, :] * t1
    c = c * (1 - t2) + yel[None, :] * t2
    return c * (1 - t3) + grey[None, :] * t3


def mottle(r, m, it):
    """the house-colour tops' weathering: lighter blotches (a multiplier: the house colour stays pure green)."""
    u, v, w = r.lu[m], r.lv[m], r.lw[m]
    n = noise(u + 0.4 * w, v - 0.3 * w, 1.6, 51)
    return 1.0 + 0.22 * np.clip((n - 0.55) / 0.35, 0, 1)


def knurl(r, m, it):
    """the drum's knurled face: a fine diamond cross-hatch."""
    u, v, w = r.lu[m], r.lv[m], r.lw[m]
    a = np.arctan2(w, v) * 2.4
    f = np.ones(m.sum(), np.float32)
    g1 = hdv.phase(u * 1.6 + a, 1.0) < 0.22
    g2 = hdv.phase(u * 1.6 - a, 1.0) < 0.22
    f[g1 | g2] = 0.8
    return f


def tread(r, m, it):
    f = np.ones(m.sum(), np.float32)
    f[hdv.phase(r.lu[m], 1.1) < 0.28] = 0.62
    return f


def mats():
    return {
        'house': dict(house=True, spec=0.25, power=24, pattern=mottle),
        'house_plain': dict(house=True, spec=0.28, power=26),
        'skirt': dict(house=True, spec=0.18, power=18, pattern=lambda r, m, it: np.full(m.sum(), 0.5, np.float32)),
        'camo': dict(col=(56, 58, 40), spec=0.12, power=16, pattern=camo),
        'body': dict(col=(62, 64, 68), spec=0.3, power=28),
        'rail': dict(col=(150, 152, 158), spec=0.55, power=46),
        'drum': dict(col=(220, 218, 210), spec=0.35, power=30, pattern=knurl),
        'drum_cap': dict(col=(172, 172, 170), spec=0.4, power=34),
        'blade': dict(col=(214, 214, 216), spec=0.6, power=50),
        'track': dict(col=(148, 136, 90), spec=0.12, power=12, pattern=tread),
        'sprocket': dict(col=(122, 118, 72), spec=0.3, power=26),
        'black': dict(col=(24, 24, 26), spec=0.35, power=34),
        'gunmetal': dict(col=(52, 52, 56), spec=0.42, power=36),
        'lens': dict(col=(255, 252, 240), emit=0.75, spec=0.5, power=40),
        'light': dict(col=(255, 250, 230), emit=0.85, spec=0.4, power=30),
        'gun': dict(col=(150, 150, 156), spec=0.5, power=40),
        'pipe': dict(col=(222, 222, 224), spec=0.45, power=38),
        'pipe_band': dict(col=(44, 44, 48), spec=0.3, power=30),
        'dirt': dict(col=(118, 98, 70), spec=0.08, power=8),
    }


CLAW = dict(root=(29.4, 0.0), ctrl=(33.3, -0.25), tip=(34.4, 2.4), w0=2.3, t0=0.3, t1=0.12, z0=1.7, z1=1.15, n=16)


def claw_items(V, y, out, nm):
    """one claw, a mandible (Westwood's renders: the two claws curve in toward each other, flat, low at the front): a
    horizontal blade whose centre line runs in plan from the drum's end forward and round toward the middle (root,
    ctrl, tip as (forward x, inward offset from the drum end)); its width tapering from w0 to the point, fuller on the
    outer (convex) edge; thickness t0 -> t1; its height falling from z0 to z1."""
    C = CLAW
    inward = -out                                       # out = -1 on the right (y small), +1 on the left
    pts2 = [np.array(C[k], float) for k in ('root', 'ctrl', 'tip')]
    p0, p1, p2 = [np.array([q[0], y + inward * q[1]]) for q in pts2]
    ts = np.linspace(0, 1, C['n'] + 1)
    cen = [(1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2 for t in ts]
    items = []
    for i in range(C['n']):
        sl = []
        for j in (i, i + 1):
            t = ts[j]
            d = 2 * (1 - t) * (p1 - p0) + 2 * t * (p2 - p1)
            d = d / np.linalg.norm(d)
            nrm = np.array([-d[1], d[0]])               # across the blade in plan
            if nrm[1] * inward > 0:
                nrm = -nrm                              # point it to the outer side
            w = C['w0'] * (1 - t) ** 0.85
            a = cen[j] + nrm * w * 0.6
            b = cen[j] - nrm * w * 0.4
            th = C['t0'] + (C['t1'] - C['t0']) * t
            zc = C['z0'] + (C['z1'] - C['z0']) * t
            for x_, y_ in (a, b):
                sl += [(x_, y_, zc - th), (x_, y_, zc + th)]
        items.append(V.hull('blade', sl, 'claw%d' % i + nm, rnd=0.0))
    # the claw's root: a block holding it on the drum's end
    items.append(V.hull('blade', [(x_, y + dy, z_) for x_ in (28.7, 30.1) for dy in (-0.3, 0.3) for z_ in (1.0, 3.2)],
                        'claw_root' + nm, rnd=0.2))
    return items


# ------------------------------------------------------------------------------------------------- the hull
def build_hull(cfg, unit):
    V = hdv.VoxelFrame(cfg, unit, 0)
    M = hdv.Model(mats())
    sx = V.sc[0]
    t_b, t_f = top(2.2), top(27.6)
    skirt = [(0.4, 0.9), (25.5, 0.9), (29.3, 3.4), (27.6, t_f - 0.55), (2.2, t_b - 0.55), (0.4, 4.6)]
    if HIGH_SIDES:                                  # the back nearly upright, the full height
        skirt = [(0.4, 0.9), (25.5, 0.9), (29.3, 3.4), (27.6, t_f - 0.55), (1.0, top(1.0) - 0.55), (0.4, top(1.0) - 1.3)]
    bx = 1.0 if HIGH_SIDES else 2.15
    track = [(1.2, 0.0), (28.6, 0.0), (30.2, 1.4), (29.8, 3.0), (28.3, 3.4), (1.8, 3.4), (0.3, 2.0)]
    for side in ('_r', '_l'):
        Y = (lambda a, b: (a, b)) if side == '_r' else (lambda a, b: (M_(b), M_(a)))
        y0, y1 = Y(0.0, 5.3)
        out = y0 if side == '_r' else y1                 # the outer side
        sgn = -1.0 if side == '_r' else 1.0              # outward along y
        M.add(V.prism_span('skirt', skirt, y0, y1, name='skirt' + side, rnd=0.35))
        # the house-colour top, sloping down from the back to the nose, a little proud of the skirt (its edge shows)
        M.add(V.prism_span('house', [(bx, top(bx) - 0.55), (bx, top(bx) + 0.05), (27.65, top(27.65) + 0.05),
                                     (27.3, top(27.3) - 0.55)], y0 - 0.06, y1 + 0.06, name='top' + side, rnd=0.4))
        M.add(V.prism_span('house', [(27.3, top(27.3) - 0.55), (27.65, top(27.65) + 0.05), (29.75, 3.45), (29.25, 3.35)],
                           y0 - 0.06, y1 + 0.06, name='nose' + side, rnd=0.4))
        # thin house-colour trim lines down the outer skirt
        for x in (8.6, 15.0, 21.4):
            M.add(V.slab('house_plain', x - 0.13, x + 0.13, out - 0.05 if sgn > 0 else out - 0.03, out + 0.03 if sgn > 0 else out + 0.05,
                         1.2, top(x) - 0.55, name='trim%d' % int(x) + side))
        ty0, ty1 = Y(0.4, 4.9)
        M.add(V.prism_span('track', track, ty0, ty1, name='track' + side, rnd=0.3))
        M.add(hdv.cyl('sprocket', V.p(28.4, ty0 - 0.1, 1.8), V.p(28.4, ty1 + 0.1, 1.8), 1.25 * sx, 'sprocket' + side))
        M.add(hdv.cyl('black', V.p(28.4, out + sgn * 0.05, 1.8), V.p(28.4, out + sgn * 0.35, 1.8), 0.55 * sx, 'hub' + side))
        # the lamp dome on the nose, its white lens forward; the small dark box at the back corner
        ym = (y0 + y1) / 2
        zl = top(26.1) + 0.05
        dome = hdv.ellip('black', V.p(26.1, ym, zl), np.array([0.95, 0.9, 0.8]) * sx, name='lamp' + side)
        hdv.cut(dome, np.array([0, 0, -1.0]), V.p(26.1, ym, zl - 0.05))
        M.add(dome)
        M.add(hdv.ellip('lens', V.p(26.82, ym, zl + 0.3), np.array([0.28, 0.42, 0.36]) * sx, name='lamp_lens' + side))
        zt = top(3.05) + 0.05
        M.add(V.slab('black', 2.4, 3.7, ym - 0.9, ym + 0.9, zt - 0.1, zt + 0.85, ch=0.2, name='tail_box' + side))
    # ---------------------------------------------------------------- the dark grey centre body
    M.add(V.prism_span('body', [(14.4, 2.8), (28.4, 2.8), (28.4, 4.2), (24.8, DECK_Z), (14.4, DECK_Z)], 5.3, 15.7,
                       name='centre_front', rnd=0.6))
    M.add(V.prism_span('body', [(1.0, 2.8), (14.6, 2.8), (14.6, DECK_Z), (1.6, 8.6), (1.0, 8.0)], 5.3, 15.7,
                       name='centre_back', rnd=0.6))
    # v3.3 (Luke 7 Oct: "the black bit middle back that the turret will travel up as it deploys"): Westwood's two
    # long ramps, side by side with a groove between: flat tops with softened edges rising from the deck behind the
    # turret to the back, rolling over in a big round at the rear onto a flat back face. The turret runs up them.
    for (ya, yb), nm in (((5.55, 10.2), '_r'), ((10.8, 15.45), '_l')):
        M.add(V.prism_span('body', ramp_profile(), ya, yb, name='ramp' + nm, rnd=0.7))
    # the groove between them: dark, a little below the ramps' tops
    M.add(V.prism_span('black', [(x_, z_ - 0.55 if z_ > 3 else z_) for x_, z_ in ramp_profile()], 10.15, 10.85,
                       name='ramp_groove', rnd=0.1))
    # the turret's ring well in the deck (the hull frames show it where the turret stands)
    M.add(hdv.cyl('black', V.p(PIVOT_X, YC, DECK_Z - 0.06), V.p(PIVOT_X, YC, DECK_Z + 0.06), 4.1 * sx, 'ring_well'))
    # ---------------------------------------------------------------- the drum and its claws
    M.add(hdv.cyl('drum', V.p(29.6, 5.75, 2.9), V.p(29.6, 15.25, 2.9), 2.2 * sx, 'drum'))
    for y0, y1, nm in ((5.35, 5.8, '_r'), (15.2, 15.65, '_l')):
        M.add(hdv.cyl('drum_cap', V.p(29.6, y0, 2.9), V.p(29.6, y1, 2.9), 2.3 * sx, 'drum_cap' + nm))
    # a flat curved claw from each end of the drum: a smooth crescent sweeping forward and down to its point (v3.3:
    # short overlapping slices along a curve, so its edges run smooth instead of the v3.1 three-piece sawtooth)
    for y, out, nm in ((5.55, -1, '_r'), (15.45, 1, '_l')):
        M.add(claw_items(V, y, out, nm))
    # ---------------------------------------------------------------- the twin pipes on the left hull
    def pz(x):
        return top(x) + 0.7
    for y, nm in ((16.75, 'a'), (18.15, 'b')):
        M.add(hdv.cyl('pipe', V.p(7.6, y, pz(7.6)), V.p(15.4, y, pz(15.4)), 0.68 * sx, 'pipe_' + nm))
        M.add(hdv.cyl('gun', V.p(15.35, y, pz(15.35)), V.p(15.95, y, pz(15.95)), 0.72 * sx, 'pipe_cap_' + nm))
        M.add(hdv.cyl('house_plain', V.p(7.4, y, pz(7.4)), V.p(7.95, y, pz(7.95)), 0.72 * sx, 'pipe_end_' + nm))
        for x in (10.2, 12.8):
            M.add(hdv.cyl('pipe_band', V.p(x - 0.2, y, pz(x - 0.2)), V.p(x + 0.2, y, pz(x + 0.2)), 0.74 * sx,
                          'pipe_band%d_' % int(x) + nm))
    M.add(V.hull('gunmetal', [(x_, y_, z_) for x_ in (11.1, 11.9) for y_ in (16.0, 18.9)
                              for z_ in (top(x_) - 0.05, top(x_) + 0.6)], 'pipe_clamp', rnd=0.2))
    return M


# ------------------------------------------------------------------------------------------------- the turret
# v3.3 (Luke 6 Oct: "Turret feels like it should be rounded, like the Nod light tank"): a low rounded dome the size of
# v3.2's turret (x1.75, Luke 4 Oct) on v3.2's seat (ring and plate kept at x1.12), with the render's two house-colour
# brackets kept as curved cheek plates hugging its sides, the round hatch on top, and a long gun out of a mantlet in its
# front, as Westwood's second render draws it. TURRET_STYLE: 'dark' (the hull's dark grey, the cheeks house colour, as
# the render) or 'house' (all house colour, the TD Nod light tank's way, dark details).
TURRET_STYLE = os.environ.get('TURRET_STYLE', 'house')   # Luke 7 Oct: house colour
SEAT = 1.46                                  # the plate's top above the deck (v3.2's: 1.3 x 1.12)
DOME = dict(c=(-0.4, 0.0, SEAT - 0.1), r=(4.7, 4.3, 4.2))   # v3.4 (Luke: TS's is a smaller circle, a higher dome)
if os.environ.get('DOME_R'):                 # a test: the dome's half-sizes (forward, across, up)
    DOME['r'] = tuple(float(v) for v in os.environ['DOME_R'].split(','))
GUN_SHIFT = DOME['r'][0] - 6.4               # the gun's parts follow the dome's front
GUN_V, GUN_W = 0.0, SEAT + 1.55 + max(0.0, DOME['r'][2] - 3.1) * 0.45
MUZZLE_LOCAL = (14.8 + GUN_SHIFT, GUN_V, GUN_W)          # the gun's tip in the turret's frame (voxels)
TURRET_SCALE = 1.0                           # (parts below are in voxels already)
TURRET_K = float(os.environ.get('TURRET_K', 1.0))   # a test scale for the whole turret (1.0 = v3.3)


def turret_local():
    """the turret's parts in its own frame (voxels: u forward, v left, w up from the deck; the pivot at 0):
    [(kind, mat, args, name)]."""
    dome_m = 'house' if TURRET_STYLE == 'house' else 'body'
    cheek_m = 'gunmetal' if TURRET_STYLE == 'house' else 'house_plain'
    P = []
    P.append(('cyl', 'gunmetal', ((0, 0, 0.0), (0, 0, 0.84), 3.8), 'turret_ring'))
    P.append(('cyl', 'black', ((0, 0, 0.84), (0, 0, SEAT), 3.36), 'turret_plate'))
    (cu, cv, cw), (ru, rv, rw) = DOME['c'], DOME['r']
    P.append(('dome', dome_m, ((cu, cv, cw), (ru, rv, rw), SEAT), 'turret_dome'))
    # the skirt: a wider lip round the dome's foot (house colour on the dark dome, as the light tank's rim)
    skirt_m = 'house_plain' if TURRET_STYLE != 'house' else 'gunmetal'
    P.append(('dome', skirt_m, ((cu, cv, SEAT + 0.15), (ru + 0.55, rv + 0.55, 0.85), SEAT), 'turret_skirt'))
    # the mantlet and the long gun
    # v3.4 (Luke 7 Oct): a slit in the dome's front above and below the gun, so it can elevate; the gun on a trunnion
    # across the slit
    P.append(('slot', 'black', (0.85, GUN_W - 2.0, GUN_W + 2.4), 'turret_slot'))
    tu = DOME['c'][0] + DOME['r'][0] * 0.78
    P.append(('cyl', 'gunmetal', ((tu, -1.05, GUN_W), (tu, 1.05, GUN_W), 0.8), 'turret_trunnion'))
    P.append(('cyl', 'gun', ((tu - 0.2, GUN_V, GUN_W), (8.6 + GUN_SHIFT, GUN_V, GUN_W), 0.95), 'turret_gun_sleeve'))
    P.append(('cyl', 'gun', ((8.4 + GUN_SHIFT, GUN_V, GUN_W), (13.6 + GUN_SHIFT, GUN_V, GUN_W), 0.6), 'turret_gun'))
    P.append(('cyl', 'black', ((13.4 + GUN_SHIFT, GUN_V, GUN_W), (14.8 + GUN_SHIFT, GUN_V, GUN_W), 0.78), 'turret_gun_muzzle'))
    # the round hatch on top, toward the back, and its two small lights
    hc = np.array([-2.2 * DOME['r'][0] / 6.4, 1.3 * DOME['r'][1] / 5.7, 0.0]); hc[2] = dome_w(hc[0], hc[1])
    n = dome_n(hc[0], hc[1])
    P.append(('cyl', 'house_plain' if TURRET_STYLE != 'house' else 'gunmetal',
              (tuple(hc - n * 0.25), tuple(hc + n * 0.22), 1.5), 'turret_hatch'))
    for v in (-1.6, -0.7):
        q = np.array([-3.6 * DOME['r'][0] / 6.4, v * DOME['r'][1] / 5.7, 0.0]); q[2] = dome_w(q[0], q[1]) - 0.1
        P.append(('ellip', 'light', (tuple(q), 0.28), 'turret_light%s' % ('_r' if v < -1 else '_l')))
    return P


def dome_w(u, v):
    (cu, cv, cw), (ru, rv, rw) = DOME['c'], DOME['r']
    k = 1 - ((u - cu) / ru) ** 2 - ((v - cv) / rv) ** 2
    return cw + rw * np.sqrt(max(k, 0.0))


def dome_n(u, v):
    (cu, cv, cw), (ru, rv, rw) = DOME['c'], DOME['r']
    w = dome_w(u, v)
    g = np.array([(u - cu) / ru ** 2, (v - cv) / rv ** 2, (w - cw) / rw ** 2])
    return g / np.linalg.norm(g)


def turret_items(V, at_x=PIVOT_X, at_z=DECK_Z, angle=0.0, lift=0.0):
    """the turret's parts placed on the hull: its pivot at index (at_x, YC, at_z + lift), turned by angle (radians,
    counter-clockwise seen from above, 0 = forward)."""
    sx = V.sc[0]
    ca, sa = np.cos(angle), np.sin(angle)
    Rz = np.array([[ca, -sa, 0], [sa, ca, 0], [0, 0, 1.0]])

    k = TURRET_K

    def P(q):
        u, v, w = (c_ * k for c_ in q)
        return V.p(at_x + u * ca - v * sa, YC + u * sa + v * ca, at_z + lift + w)
    sx = sx * k
    Rw = V.R @ Rz
    down = Rw @ np.array([0, 0, -1.0])
    out = []
    for kind, mat, args, name in turret_local():
        if kind == 'cyl':
            a, b, r = args
            out.append(hdv.cyl(mat, P(a), P(b), r * sx, name, rnd=0.3))
        elif kind == 'box':
            (u0, u1), (v0, v1), (w0, w1) = args
            pts = [(u, v, w) for u in (u0, u1) for v in (v0, v1) for w in (w0, w1)]
            out.append(hdv.hull(mat, [P(q) for q in pts], name, rnd=0.35))
        elif kind == 'hull':
            out.append(hdv.hull(mat, [P(q) for q in args], name, rnd=0.35))
        elif kind == 'ellip':
            c, r = args
            out.append(hdv.ellip(mat, P(c), np.array([r, r, r]) * sx, name=name))
        elif kind == 'ellip3':
            c, r = args
            out.append(hdv.ellip(mat, P(c), np.array(r) * sx, R=Rw, name=name))
        elif kind == 'dome':
            c, r, floor = args
            it = hdv.ellip(mat, P(c), np.array(r) * sx, R=Rw, name=name, rnd=0.5)
            hdv.cut(it, down, P((0, 0, floor)))
            out.append(it)
        elif kind == 'slot':
            hw, w0, w1 = args
            (cu, cv, cw), (ru, rv, rw) = DOME['c'], DOME['r']
            it = hdv.ellip(mat, P((cu, cv, cw)), np.array([ru + 0.06, rv + 0.06, rw + 0.06]) * sx, R=Rw, name=name, rnd=0.2)
            vside = Rw @ np.array([0, 1.0, 0])
            hdv.cut(it, vside, P((0, hw, 0))); hdv.cut(it, -vside, P((0, -hw, 0)))
            hdv.cut(it, down, P((0, 0, max(w0, SEAT + 0.6)))); hdv.cut(it, -down, P((0, 0, w1)))
            hdv.cut(it, Rw @ np.array([-1.0, 0, 0]), P((cu + 0.3 * ru, 0, 0)))
            out.append(it)
        elif kind == 'cheek':
            (s_,) = args
            # a shell over the dome's flank: the dome grown by 0.3, cut to a band across the side (|v| > 3.0) and
            # between the mantlet and the back third
            (cu, cv, cw), (ru, rv, rw) = DOME['c'], DOME['r']
            it = hdv.ellip(mat, P((cu, cv, cw)), np.array([ru + 0.3, rv + 0.3, rw + 0.3]) * sx, R=Rw, name=name, rnd=0.4)
            side = Rw @ np.array([0, -s_, 0.0])             # pointing inward
            hdv.cut(it, side, P((0, s_ * 3.4, 0)))
            hdv.cut(it, Rw @ np.array([1.0, 0, 0]), P((3.6, 0, 0)))
            hdv.cut(it, Rw @ np.array([-1.0, 0, 0]), P((-4.2, 0, 0)))
            hdv.cut(it, down, P((0, 0, SEAT)))
            hdv.cut(it, Rw @ np.array([0, 0, 1.0]), P((0, 0, SEAT + 2.9)))
            out.append(it)
    return out


def build_turret(cfg, unit):
    """the turret alone (its frames): the pivot on the unit's position, as the hull frames have it."""
    V = hdv.VoxelFrame(cfg, unit, 0)
    M = hdv.Model(mats())
    M.add(turret_items(V))
    return M


def build(cfg, unit, angle=0.0):
    """hull and turret together (the .glb, the composite checks)."""
    V = hdv.VoxelFrame(cfg, unit, 0)
    M = build_hull(cfg, unit)
    M.add(turret_items(V, angle=angle))
    return M


def turret_pivot(cfg, unit):
    """the turret's pivot at the top of its ring's seat (unit frame): the .glb's turret node."""
    return N.to_unit(cfg, unit, 0, [PIVOT_X, YC, DECK_Z])


def muzzle(cfg, unit):
    """the gun's tip with the turret facing forward (unit frame)."""
    u, v, w = (c * TURRET_SCALE for c in MUZZLE_LOCAL)
    return N.to_unit(cfg, unit, 0, [PIVOT_X + u, YC + v, DECK_Z + w])


def rail_lift(x):
    """how far the turret's ring rises above the deck at x as it runs back along the rails (onto the humps)."""
    r = 3.8
    back = x - r * 0.55                                   # where the ring's back rests on the rails
    if back >= RAMP['x_front']:
        return 0.0
    zs = [ramp_top(xx) for xx in np.linspace(back, x + r * 0.55, 8)]
    zr = max(zs)
    return max(0.0, zr - DECK_Z)


def dug_in(cfg, unit, t=1.0):
    """the deploy as Luke describes it, t from 0 (driving) to 1 (dug in): the turret runs back over the deck and up onto
    the humps at the back, then the nose burrows (the tank pitches nose-down about its back end, its front sinking
    under the ground into a mound of dirt)."""
    V = hdv.VoxelFrame(cfg, unit, 0)
    M = build_hull(cfg, unit)
    ts = min(1.0, t / 0.55)
    ts = ts * ts * (3 - 2 * ts)
    tp = max(0.0, (t - 0.35) / 0.65)
    tp = tp * tp * (3 - 2 * tp)
    x = PIVOT_X + (6.6 - PIVOT_X) * ts
    lift = rail_lift(x)
    M.add(turret_items(V, at_x=x, lift=lift))
    th = np.radians(9.0 * tp)
    R = np.array([[np.cos(th), 0, np.sin(th)], [0, 1.0, 0], [-np.sin(th), 0, np.cos(th)]])
    piv = V.p(0.6, YC, 0.0)
    items = []
    for it in M.items:
        jt = hdv.moved_item(it, R, piv - R @ piv)
        hdv.cut(jt, np.array([0, 0, -1.0]), np.zeros(3))
        items.append(jt)
    M.items = items
    if tp > 0:
        mound = hdv.ellip('dirt', V.p(28.6, YC, 0.0), np.array([2.6 * tp + 0.2, 10.6, 1.5 * tp + 0.05]) * V.sc[0],
                          name='dirt_mound')
        hdv.cut(mound, np.array([0, 0, -1.0]), np.zeros(3))
        M.items.append(mound)
    return M


def run_back(cfg, unit, x=6.6):
    """the review view: the turret run back up the ramps (before the nose burrows)."""
    V = hdv.VoxelFrame(cfg, unit, 0)
    M = build_hull(cfg, unit)
    M.add(turret_items(V, at_x=x, lift=rail_lift(x)))
    return M


# ------------------------------------------------------------------------------------------------- the dug-in's needs
RING_SCALE = 1.12                         # v3.2's seat (ring 3.8, plate top 1.46): the v3.3 parts are in voxels already


def turret_point(q, ring=False):
    """a point of the turret's own frame: v3.3's parts are in voxels already (kept for the dug-in scripts)."""
    return tuple(q)
