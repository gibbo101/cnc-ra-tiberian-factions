"""
sonmodel.py - the Disruptor (TS's [SONIC], TSSONIC in the mod) rebuilt the way the Titan, the Wolverine, the MCV, the
Mammoths, the APC, the sensor array and the War Factory are: TS's own voxels (SONIC.VXL the hull, SONICTUR.VXL the
turret's two sections - the turntable ring and the turret with its dish) as the blueprint for where every part is and
how big, each part modelled clean (flat plates, true slopes, round wheels, bevelled edges) in TS's colours - GDI's
ochre track pods, house-colour decks, a dark hull, the grey and white dish on its dark base - with Westwood's art of
the Disruptor where TS's voxels have the part (the dish's white panels, the hazard stripes round the ring, the
emitter's yellow barrel and red tip).

Each section has its own frame: q, continuous voxel coordinates (voxel i spans i..i+1), x back to front, y from the
unit's right (0) to its left, z up; the section's local frame is min + q * scale (TS's), and its HVA (frame 0) places
it in the unit's frame.  The hull (47 x 25 x 11) is raised GZ onto the ground (soncam.py).
"""
import os, sys
from paths import HANDOFF
sys.path.insert(0, os.path.join(HANDOFF, 'renderer'))
import numpy as np
import vxl
import rc
from qparts import Frame, B, prism, hull, cyl
from soncam import GZ

D = os.path.join(HANDOFF, '08-TSSONIC', 'ts-original') + os.sep

(OCHRE, BELT, BODY, GREEN, BLACK, OLIVE, TRENCH, RING, HAZARD, RIM, BASE, DISH, DISH_W, STRUT, BRACE, EMIT, EMIT_TIP,
 HOUSING, KHAKI, ARM_CAP, ARM, ARM_BAND, COIL, ARM_TIP, AXLE, BRACKET, PISTON, ROD, SPRING, CROSS, GLASS) = range(81, 112)
HOUSE = (GREEN,)


def _load(name, i):
    s = vxl.read_vxl(D + name + '.VXL')[i]
    names, mats = vxl.read_hva(D + name + '.HVA')
    return Frame(s, mats[0, i])


FH = _load('SONIC', 0)
FR, FT = _load('SONICTUR', 0), _load('SONICTUR', 1)
HYC = 12.5                                          # the hull's centre line (q y)


def mirror(y0, y1, c=HYC):
    return (y0, y1), (2 * c - y1, 2 * c - y0)


# ---------------------------------------------------------------- the hull
# four track pods (TS's: the rear pair x 2..22, the front pair x 23..45, y 0..6 and 19..25): black belts with rounded
# ends (TS: z 0..5) under ochre covers whose skirts come down to z 3, their ends sloping (TS's)
BELT_REAR = [(6.0, 0.0), (18.0, 0.0), (20.0, 1.0), (22.0, 3.0), (22.0, 4.6), (3.0, 4.6), (3.0, 3.0), (5.0, 1.0)]
BELT_FRONT = [(28.0, 0.0), (40.0, 0.0), (42.5, 1.2), (44.4, 2.6), (45.0, 3.6), (45.0, 4.6), (24.0, 4.6), (24.0, 2.6),
              (25.2, 1.2)]
COVER_REAR = [(5.0, 3.0), (20.0, 3.0), (22.0, 5.0), (22.0, 7.0), (4.0, 7.0), (2.0, 6.0), (2.0, 4.0)]
COVER_FRONT = [(26.0, 3.0), (42.0, 3.0), (44.0, 4.0), (44.0, 5.0), (42.0, 7.0), (23.0, 7.0), (23.0, 5.0), (24.2, 3.8)]


def track_pods():
    out = []
    for (y0, y1) in mirror(0.0, 6.0):
        for belt, cover in ((BELT_REAR, COVER_REAR), (BELT_FRONT, COVER_FRONT)):
            out.append(prism(FH, 1, belt, y0 + 0.6, y1 - 0.6, BELT, ch=0.2, name='belt'))
            out.append(prism(FH, 1, cover, y0, y1, OCHRE, ch=0.3, name='track_cover'))
    return out


# the ochre box on the front left (TS: x 34..41, y 14..20, z 4..10, its front higher, z 11), with a viewport across its
# front (Luke) where TS has dark voxels (x 41..42, y 15..19, z 8..10): the glass in a frame proud of the face
VP_Y = (15.3, 18.7)                                 # the viewport's glass (q y, z) on the box's front face (q x 41.2)
VP_Z = (8.6, 10.0)


def ochre_box():
    out = [B(FH, 33.6, 41.2, 14.0, 20.0, 4.0, 10.0, OCHRE, ch=0.2, name='ochre_box'),
           B(FH, 36.6, 41.2, 14.6, 19.4, 9.5, 11.0, OCHRE, ch=0.2, name='ochre_box')]
    (y0, y1), (z0, z1) = VP_Y, VP_Z
    out.append(B(FH, 41.1, 41.26, y0, y1, z0, z1, GLASS, name='viewport'))
    f = 0.2
    for (ya, yb, za, zb) in ((y0 - f, y1 + f, z1, z1 + f), (y0 - f, y1 + f, z0 - f, z0),
                             (y0 - f, y0, z0, z1), (y1, y1 + f, z0, z1)):
        out.append(B(FH, 41.1, 41.36, ya, yb, za, zb, OCHRE, ch=0.04, name='viewport_frame'))
    return out


def hull_parts():
    out = track_pods()
    # the hull between the pods: dark, its floor at z 3, its deck at z 8 over the front half (TS's)
    out.append(B(FH, 1.0, 44.6, 5.0, 20.0, 3.0, 8.0, BODY, ch=0.2, name='body'))
    # the rear deck, house colour (TS: x 3..21, y 6..19, up to z 10; v1-v3 had it a voxel to the left, at y 7..20), its
    # back a grille stepping down to the rear plate (TS: z 7 at x 3 down to z 5 at x 0, its house colour y 6..18; v4
    # plain, Luke: no grilles or black lines on the house colour)
    out.append(B(FH, 3.0, 21.3, 6.0, 19.0, 7.0, 10.0, GREEN, ch=0.3, name='rear_deck'))
    out.append(prism(FH, 1, [(0.0, 3.0), (3.2, 3.0), (3.2, 7.2), (0.0, 5.0)], 6.0, 18.0, GREEN, ch=0.15,
                     name='rear_grille'))
    # louvred blocks on the rear pods' inner edges, black posts between them (TS: x 6..14, y 3..6 and 19..21)
    for (y0, y1) in ((2.9, 5.9), (19.1, 21.1)):
        out.append(B(FH, 5.8, 14.6, y0, y1, 6.8, 8.0, GREEN, ch=0.12, name='side_louvre'))
        for xa in (7.9, 11.9):
            out.append(B(FH, xa, xa + 1.1, y0 + 0.1, y1, 6.8, 9.0, BLACK, ch=0.12, name='post'))
    # the front: the long house-colour box on the right on its black base (TS: x 26..46, the box y 6..12 up to z 11, its
    # back end a step lower, the base y 5..13; v1-v3 had them a voxel to the left), its front coming down to z 5 (TS's)
    out.append(B(FH, 25.0, 46.8, 5.0, 13.0, 7.8, 9.0, BLACK, ch=0.15, name='box_base'))
    out.append(B(FH, 25.8, 29.2, 6.0, 12.0, 8.8, 10.0, GREEN, ch=0.2, name='front_box'))
    out.append(B(FH, 28.8, 45.6, 6.0, 12.0, 8.8, 11.0, GREEN, ch=0.25, name='front_box'))
    out.append(B(FH, 27.5, 46.6, 6.0, 12.0, 5.0, 7.9, GREEN, ch=0.2, name='front_low'))
    out += ochre_box()
    # the olive plate across the front's left (TS: x 44..46, y 13..20, z 6..7)
    out.append(B(FH, 43.0, 46.4, 12.8, 20.4, 5.0, 8.2, OLIVE, ch=0.2, name='front_plate'))
    return out


# ---------------------------------------------------------------- the turret
TC = (8.5, 9.0)                                     # the rim's centre (turret q x, y; TS's ring sits half a voxel off it)
DISH_Z = (5.0, 12.0)                                # the dish (turret q z)
DISH_T = (2.6, 1.6)                                 # its thickness at its foot and its top (TS's back slopes)


def dish_x(y):
    """the dish's front face (turret q x) across it: concave forward, its middle at x 9.6, its edges at 13 (TS's)."""
    return 9.6 + 0.031 * (np.asarray(y, float) - 9.4) ** 2


def _circle(F, c_q, r, z, a):
    cl = F.p((c_q[0], c_q[1], z))
    return tuple(F.q(cl + r * np.array([np.cos(a), np.sin(a), 0.0])))


def ring_sectors(F, c_q, prof, n, comp, name):
    """a ring round c_q (q x, y) as n convex sectors; prof: its section as (radius (local units), q z) points."""
    out = []
    for i in range(n):
        a0, a1 = 2 * np.pi * i / n, 2 * np.pi * (i + 1) / n
        pts = [_circle(F, c_q, r, z, a) for (r, z) in prof for a in (a0, a1)]
        out.append(hull(F, pts, comp, name))
    return out


# v5: the circular pad (the turntable and its rim) at PAD_K of TS's radius, its height TS's, so on screen it is v4's pad
# and stays on the green deck at every facing; the rest of the turret is TS's size (Luke: the dish back to its size,
# only the pad smaller)
from soncam import K_TUR, K_TUR_V4
PAD_K = K_TUR_V4 / K_TUR                            # 0.70


def ring_parts():
    # TS's turntable: a disc of ochre and black (Westwood's hazard stripes round the turret), sunk a voxel inside the
    # rim
    return [cyl(FR, (8.0, 8.0, 0.0), (8.0, 8.0, 2.0), 7.75 * PAD_K, HAZARD, 'hazard_ring')]


# the emitter arm (TS: a rod two voxels thick, y 8..10, from x 15 to the tip at x 21, rising toward the dish - its tip
# at z 2..4, its back end at z 4..5: about 12 degrees - light grey at the back with a raised band on top at x 16, dark
# forward of x 17, a grey tip), on the FMV's arm: end caps, a band, a coil of rings behind the tip, a trunnion through
# it carried by a zig-zag bracket each side down to the turntable, a piston each side back to a beam across the turret
# in front of the dish (TS: x 11..12, y 5..13).  Under the arm's back half TS is open to the turntable (x 13..15).
ARM_P0 = np.array([15.0, 9.0, 4.68])
ARM_P1 = np.array([21.8, 9.0, 3.18])
ARM_L = float(np.linalg.norm(ARM_P1 - ARM_P0))
ARM_U = (ARM_P1 - ARM_P0) / ARM_L
ARM_R = 0.93
COIL_S = [4.31 + 0.42 * k for k in range(4)]          # the fins behind the tip (their middles, along the arm from its back)
AXLE_S = 4.94                                         # the trunnion: through the fins (the FMV's), at TS's x 19.8
BRACKET_Y = ((7.4, 7.85), (10.15, 10.6))
PISTON_Y = (6.0, 12.0)


def arm_at(s):
    return ARM_P0 + s * ARM_U


def arm_z(x):
    return float(ARM_P0[2] + (x - ARM_P0[0]) * ARM_U[2] / ARM_U[0])


def _arm_cyl(s0, s1, r, comp, name):
    return cyl(FT, tuple(arm_at(s0)), tuple(arm_at(s1)), r, comp, name)


def _bar(F, p, q, y0, y1, w, comp, name):
    """a flat bar in the x-z plane from p to q (q x, z), w wide, y0..y1 thick, its ends run on by w/2."""
    p = np.asarray(p, float); q = np.asarray(q, float)
    d = (q - p) / np.linalg.norm(q - p); n = np.array([-d[1], d[0]])
    p2, q2 = p - d * w / 2, q + d * w / 2
    pts = []
    for c in (p2, q2):
        for s in (-1, 1):
            a = c + s * n * w / 2
            pts += [(a[0], y0, a[1]), (a[0], y1, a[1])]
    return hull(F, pts, comp, name)


def arm_parts():
    out = []
    # the arm, back to front: a boss and a white cap, a lip, the light grey body (TS's x 15..17) with a raised band
    # (TS's x 16) and a strap, the dark sleeve (TS's dark front, x 18..20) with a strap, four fins behind the tip (the
    # FMV's coil), a collar, the grey tip in two steps
    out.append(_arm_cyl(-0.10, 0.02, 0.42, ARM_CAP, 'arm_boss'))
    out.append(_arm_cyl(0.0, 0.32, 0.80, ARM_CAP, 'arm_cap'))
    out.append(_arm_cyl(0.30, 0.48, 1.0, ARM_BAND, 'arm_lip'))
    out.append(_arm_cyl(0.46, 3.3, ARM_R, ARM, 'arm_body'))
    out.append(_arm_cyl(0.98, 1.62, 1.1, ARM_BAND, 'arm_band'))
    out.append(_arm_cyl(2.45, 2.72, 1.0, ARM_BAND, 'arm_strap'))
    out.append(_arm_cyl(3.26, 5.66, 0.9, COIL, 'arm_sleeve'))
    out.append(_arm_cyl(3.55, 3.82, 0.97, COIL, 'arm_strap'))
    for s in COIL_S:
        out.append(_arm_cyl(s - 0.11, s + 0.11, 1.05, COIL, 'arm_fin'))
    out.append(_arm_cyl(5.62, 5.88, 1.04, COIL, 'arm_collar'))
    out.append(_arm_cyl(5.86, 6.72, 0.84, ARM_TIP, 'arm_tip'))
    out.append(_arm_cyl(6.70, ARM_L, 0.60, ARM_TIP, 'arm_tip_end'))
    # the trunnion through it, a nut each end outside the brackets
    a = arm_at(AXLE_S)
    out.append(cyl(FT, (a[0], 7.2, a[2]), (a[0], 10.8, a[2]), 0.28, AXLE, 'trunnion'))
    for y0, y1 in ((7.05, 7.4), (10.6, 10.95)):
        out.append(cyl(FT, (a[0], y0, a[2]), (a[0], y1, a[2]), 0.42, AXLE, 'trunnion_nut'))
    # a zig-zag bracket each side (TS: y 7 and 10, x 15..20, down to z 1): the trunnion on its front peak, pins into
    # the arm on the others, a foot bar along the turntable; a plate between them under the arm's front (TS's)
    t0 = (15.5, arm_z(15.5)); t1 = (17.7, arm_z(17.7)); t2 = (a[0], a[2])
    b0 = (16.6, 1.05); b1 = (18.75, 1.05)
    for y0, y1 in BRACKET_Y:
        for p, q in ((t0, b0), (b0, t1), (t1, b1), (b1, t2)):
            out.append(_bar(FT, p, q, y0, y1, 0.42, BRACKET, 'bracket'))
        out.append(B(FT, 16.0, 19.35, y0, y1, 1.0, 1.4, BRACKET, ch=0.06, name='bracket_foot'))
        yi = 8.3 if y0 < 9 else 9.7
        for t in (t0, t1):
            out.append(cyl(FT, (t[0], min(y0, yi), t[1]), (t[0], max(y1, yi), t[1]), 0.2, AXLE, 'bracket_pin'))
    out.append(B(FT, 16.3, 19.3, 7.85, 10.15, 1.0, 1.35, BRACKET, ch=0.05, name='bracket_plate'))
    # a piston each side (TS: y 5..7 and 11..13, x 11..19, z 1..4): the barrel from the beam, a collar, the rod in a
    # coil spring (the FMV's), its eye linked to the bracket
    for yc in PISTON_Y:
        out.append(cyl(FT, (13.0, yc, 2.75), (13.25, yc, 2.75), 0.98, PISTON, 'piston_flange'))
        out.append(cyl(FT, (13.0, yc, 2.75), (15.8, yc, 2.75), 0.82, PISTON, 'piston'))
        out.append(cyl(FT, (15.8, yc, 2.75), (16.15, yc, 2.75), 0.92, PISTON, 'piston_collar'))
        out.append(cyl(FT, (16.15, yc, 2.75), (17.95, yc, 2.75), 0.28, ROD, 'piston_rod'))
        for xs in (16.42, 16.8, 17.18, 17.56):
            out.append(cyl(FT, (xs - 0.08, yc, 2.75), (xs + 0.08, yc, 2.75), 0.55, SPRING, 'spring'))
        out.append(B(FT, 17.85, 18.35, yc - 0.36, yc + 0.36, 2.4, 3.1, BRACKET, ch=0.06, name='piston_eye'))
        ly = (yc + 0.36, BRACKET_Y[0][0] + 0.1) if yc < 9 else (BRACKET_Y[1][1] - 0.1, yc - 0.36)
        out.append(B(FT, 17.95, 18.25, ly[0], ly[1], 2.5, 2.95, BRACKET, name='piston_link'))
    # the beam across in front of the dish (TS: x 11..12, y 5..13, z 1..3, black at its right end)
    out.append(B(FT, 10.8, 13.0, 5.0, 13.0, 1.0, 4.0, CROSS, ch=0.2, name='beam'))
    return out


def turret_parts():
    out = []
    # the rim round the turntable, grey (TS: z 0..2, its outside 8.4 from the middle; v5 at PAD_K of TS's radius, its
    # height and top bevel TS's)
    ri, ro = 7.25 * PAD_K, 8.6 * PAD_K
    out += ring_sectors(FT, TC, [(ri, 0.0), (ro, 0.0), (ro, 1.75), (ro - 0.25, 2.0), (ri, 2.0)], 48, RIM, 'rim')
    # the dark base: a block each side under the dish's ends, grey rails on them (TS: y 3..5 and 13..15, x 3..13,
    # z 2..4, the rails z 4), a post under the dish's middle (TS: x 7..10, y 7..11) stepping down in front of it (TS: x 9
    # to z 4, x 10 to z 3)
    for (y0, y1) in ((3.0, 5.0), (13.0, 15.0)):
        out.append(B(FT, 3.0, 13.2, y0, y1, 1.6, 4.0, BASE, ch=0.2, name='base_side'))
        out.append(B(FT, 6.0, 14.0, y0 + 0.15, y1 - 0.15, 3.9, 4.9, STRUT, ch=0.12, name='rail'))
    out.append(B(FT, 7.0, 9.4, 7.0, 11.4, 1.6, 5.2, BASE, ch=0.2, name='base_post'))
    out.append(B(FT, 9.2, 10.1, 7.0, 11.2, 1.0, 4.0, BASE, ch=0.15, name='base_step'))
    out.append(B(FT, 9.9, 11.0, 7.0, 11.2, 1.0, 3.1, BASE, ch=0.15, name='base_step'))
    out += arm_parts()
    # the dish: TS's curved shell standing across the turret, concave forward (TS: its middle at x 9..10, its edges
    # at x 12..13, y 0..19, z 5..12), in panels (Westwood's)
    ys = np.linspace(0.2, 18.6, 13)
    for ya, yb in zip(ys[:-1], ys[1:]):
        pts = []
        for y in (ya, yb):
            for z, th in zip(DISH_Z, DISH_T):
                pts += [(float(dish_x(y)), y, z), (float(dish_x(y)) - th, y, z)]
        out.append(hull(FT, pts, DISH, 'dish'))
    # behind it: the post holding it (TS: x 5..8, y 7..11, z 4..11) and a blue-grey brace each side (TS: y 4, 13)
    out.append(B(FT, 5.6, 8.2, 7.6, 11.2, 4.0, 11.2, STRUT, ch=0.15, name='dish_post'))
    for (y0, y1) in ((4.0, 5.0), (13.0, 14.0)):
        out.append(hull(FT, [(4.6, y0, 4.0), (4.6, y1, 4.0), (8.6, y0, 4.0), (8.6, y1, 4.0),
                             (7.4, y0, 7.4), (7.4, y1, 7.4), (9.0, y0, 7.4), (9.0, y1, 7.4)], BRACE, 'brace'))
    # olive fittings at the dish's four corners (TS's)
    for y0, y1 in ((0.0, 1.5), (17.4, 18.9)):
        for z0, z1 in ((5.8, 7.4), (10.2, 11.8)):
            xm = float(dish_x((y0 + y1) / 2))
            out.append(B(FT, xm - 2.2, xm + 0.2, y0, y1, z0, z1, KHAKI, ch=0.12, name='fitting'))
    return out


def model():
    return {'hull': hull_parts(), 'ring': ring_parts(), 'tur': turret_parts()}


SECTIONS = {'hull': FH, 'ring': FR, 'tur': FT}


def _middle(F, q):
    R, t = F.pose()
    c = R @ F.p(q) + t
    return np.array([c[0], c[1], 0.0])


def _posed_z(F, q, dz=0.0):
    R, t = F.pose()
    return float((R @ F.p(q) + t)[2] + dz)


# v4: the turret's two sections each centred on the pivot (TS's turntable sits half a voxel off the turret's rim and the
# turret a third of a voxel right of the pivot), so the ring turns on the spot and stays on the deck at every facing.
# v5: the hull centred side to side on the unit's position too (TS's hull sits 0.11 voxel left of it: its middle, q y
# 12.5, where the pods, the deck and the body are centred), so the pad turning about the pivot is centred on the deck;
# and the turret lowered so its pad stands on the deck's top (TS's turntable foot floats 0.58 voxel above it)
HULL_Y = float(_middle(FH, (0.0, 12.5, 0.0))[1])
DECK_TOP = _posed_z(FH, (10.0, 12.5, 10.0), -GZ)    # the rear deck's top (its box's top, hull q z 10), raised as the hull
DROP = _posed_z(FR, (8.0, 8.0, 0.0)) - DECK_TOP     # the turntable's foot onto the deck: 0.58
SHIFT = {'hull': np.array([0.0, -HULL_Y, -GZ]),
         'ring': -_middle(FR, (8.0, 8.0, 0.0)) - np.array([0.0, 0.0, DROP]),
         'tur': -_middle(FT, (TC[0], TC[1], 0.0)) - np.array([0.0, 0.0, DROP])}
from soncam import Z_BASE as _ZB
assert abs(DECK_TOP - _ZB) < 0.01, (DECK_TOP, _ZB)  # soncam's turret base is the deck's top


def pose(k):
    """a section's pose in the unit's frame: TS's HVA (frame 0), the hull raised onto the ground and centred side to
    side on the unit's position, the turret's sections centred on the pivot and lowered onto the deck."""
    R, t = SECTIONS[k].pose()
    return R, t + SHIFT[k]


def posed(m, which, Mx=np.eye(3)):
    """the parts of the named sections posed (pose()) and turned by Mx (unit frame -> world): (parts, frames, owner)."""
    parts, frames, owner = [], [], []
    for k in which:
        F = SECTIONS[k]
        R, t = pose(k)
        Rw, tw = Mx @ R, Mx @ t
        Mq = Rw @ np.diag(1.0 / F.sc)
        tq = tw + Rw @ F.mn
        for p in m[k]:
            parts.append(p.moved(Rw, tw)); frames.append((Mq, tq)); owner.append(k)
    return parts, frames, np.array(owner)
