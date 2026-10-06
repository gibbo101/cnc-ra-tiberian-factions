"""
otmodel.py - the Orca Transport (TS's [ORCATRAN], TSORCATRAN in the mod) rebuilt the way the Titan, the Orcas and the
Carryall are: TS's own voxel (ORCATRAN.VXL, one section, posed by its HVA) is the blueprint for where every part is and
how big, each part modelled clean (flat plates, true slopes, round fans, bevelled edges) in TS's colours - GDI's ochre,
TS's house colour where TS paints it (the wing's slopes and the belly band, the front section's flanks, the nose, the
belly strips), khaki fan drums, grey hatch and rails, a dark grey cockpit with black windows.

q: TS's voxel coordinates, continuous (voxel i spans i..i+1): x back to front 0..70, y from the aircraft's right (0) to
its left 0..39, z up 0..14; the section's local frame is min + q * scale (TS's), and its HVA (frame 0) places it in the
unit's frame.  Symmetric about q y 19.0 (TS's mirror line); w below is the distance out from it (negative: the right).
Each section's outline is fitted to TS's voxel staircase: the line through the middle of each step (where the voxels'
centres change from filled to empty), averaged over TS's two sides where they differ by a voxel.

Parts (TS's voxels in brackets, q units):
  rear block   [x 0..10]: 30 wide [w +/-15, z 3..8.5], its shoulders sloping in to the roof [w +/-10, z 11]; its back a
               slope [x 0.8 at z 5 to 4.6 at z 11] over a bumper [x 0..1.3, z 3..5], TS's two dark vents in the slope;
               between the rear fans [x 10..19.6] 22 wide [w +/-11]
  roof panel   raised on the roof [x 4.5..19, z 11..13]: 16 wide behind x 10, 14 wide ahead of it (TS: z 11 at y 11..26
               and 12..25, z 12 at y 12..25 and 13..24), its back sloping as the back does
  wing         through the hull just ahead of the rear block [x 18..23.6]: its flat bottom at z 3 across the whole width
               [w +/-19], its tips [w 19, z 3..4.9], its tops curving up to the deck [w 10.6, z 10.7]
  hull         the middle [x 19.6..43]: 24 wide [w +/-12, z 3..8.3], 20 at the deck [w +/-10, z 11]; a strake along
               each side [x 23.6..28.6 out to w 14 at z 5..7, then to x 36 out to w 13]; TS's grey hatch on the deck
               [x 19..29, w +/-5.5, z 11..12]; the hump [x 29..44, w +/-7.2 at z 11 to +/-3.6 at its top, z 14], its
               front sloping [x 40 at z 14 to 44 at z 12] down to the cockpit
  front        [x 42.8..54]: 26 wide [w +/-13 at z 4.6..7.5], 13 at the deck [z 11]; the cockpit on its deck [x 41..53,
               w +/-6, z 11..12], notched at the front [x 50..53, w +/-3]; TS's two black windows run down the hump's
               front and along the cockpit [x 40.5..48.5]; its dark grey face plate [x 54..55, w +/-11, z 5..11]
  nose         [x 55..70]: an octagon [w +/-2.5 at z 3, 5.5 at z 5.3..6.8, 2.6 at z 11], its front a slope from z 11 at
               x 65.4 to 7.6 at x 70 (TS's blue-grey panes in it), its chin rising to z 5.2 at x 69.4
  fans         four drums: at the back [x 14, w +/-14.65], in the rear block's notches; at the front [x 60.5,
               w +/-9.65] beside the nose on grey struts [x 55..59.8]; each a cup [r 3.4..3.6 at its bottom, z 5, to
               4.7..4.8 at z 9..10.7], a lip on top [r 2.8 to the drum's edge, z 9.6..11] round a recessed fan: nine
               blades, a grey hub with a dark centre (TS's light khaki disc a voxel below the lip)
  legs         six (TS's): under the rear block [x 5..11, w 12.25], under the wing's tips [x 18..24, w 16], under the
               front section [x 49..55, w 9.75]: a foot pad on the ground, a strut and a drag rod, a knuckle under the
               body; dark olive mounts in the wing's tips
  belly        TS's house-coloured strips under the hull [x 28..44, w 8..12, z 2..3]; TS's ochre door box under the
               right side between the rear fans [x 9..20, y 8..12, z 2..3] with its amber panel
  rails        TS's dark grey rails along the deck's edges [x 22..40.6, w 8.1..9.95]
"""
import os, sys
from paths import HANDOFF, OT_D
sys.path.insert(0, os.path.join(HANDOFF, 'renderer'))
import numpy as np
import vxl
import rc
from qparts import Frame, B, prism, hull, cyl

D = OT_D

(REAR, PANEL, BUMPER, CORE, WING, HULL, STRAKE, HATCH, HUMP, FRONT, CANOPY, FACE, NOSE, DRUM, LIP, BLADE, HUB, FLOOR,
 STRUT, LEGM, LEG, FOOT, RAIL, BELLY, DOOR) = range(81, 106)
HOUSE = (WING, FRONT, NOSE, BELLY, HULL)             # the parts that carry TS's house colour (where TS paints it:
#                                                     the hull only its sides' lowest row ahead of x 28)
RINGS = (DRUM, LIP)                                  # made of sectors: shaded with their true radial normals


def _load(name, i):
    s = vxl.read_vxl(D + name + '.VXL')[i]
    names, mats = vxl.read_hva(D + name + '.HVA')
    return Frame(s, mats[0, i])


FH = _load('ORCATRAN', 0)
HYC = 19.0


def Y(w):
    return HYC + w


def hullq(pts, comp, name):
    return hull(FH, pts, comp, name)


def section(half):
    """a convex section from its right half's outline listed bottom to top (w >= 0): the mirror closes it."""
    pts = [(w, z) for (w, z) in half] + [(-w, z) for (w, z) in reversed(half)]
    return [(Y(w), z) for (w, z) in pts]


def plane_q(a, b, c, inside):
    """the plane through three q points (in the section's local frame), facing away from a q point inside."""
    A, Bp, C = FH.p(a), FH.p(b), FH.p(c)
    n = np.cross(Bp - A, C - A); n /= np.linalg.norm(n)
    if n @ (FH.p(inside) - A) > 0:
        n = -n
    return rc.Plane(n, float(n @ A))


def cut_xz(part, a, b, inside):
    """cut a part by the plane through the (x, z) line a -> b, across y."""
    part.cons.append(plane_q((a[0], 0.0, a[1]), (b[0], 0.0, b[1]), (a[0], 1.0, a[1]), inside))
    return part


def _circle(c_q, r, z, a):
    cl = FH.p((c_q[0], c_q[1], z))
    return tuple(FH.q(cl + r * np.array([np.cos(a), np.sin(a), 0.0])))


def ring_sectors(c_q, prof, n, comp, name, a_off=0.0):
    """a solid of revolution round the vertical through c_q, from its (r [local units], z [q]) profile (convex), as n
    sectors; points at r 0 make them wedges (a closed body)."""
    out = []
    for i in range(n):
        a0, a1 = a_off + 2 * np.pi * i / n, a_off + 2 * np.pi * (i + 1) / n
        pts = []
        for (r, z) in prof:
            if r <= 1e-6:
                pts.append(tuple(c_q[:2]) + (z,))
            else:
                pts += [_circle(c_q, r, z, a) for a in (a0, a1)]
        out.append(hull(FH, pts, comp, name))
    return out


def rotor(c, r_hub, r_tip, zc, n, comp_hub, comp_blade, name, a_off=0.0, pitch=0.3, chord=0.5, thick=0.08,
          hub_h=(0.7, 0.5), dome=0.5, sweep=0.0):
    out = [cyl(FH, (c[0], c[1], zc - hub_h[0]), (c[0], c[1], zc + hub_h[1]), r_hub, comp_hub, name + '_hub')]
    out.append(rc.Part([rc.Ellip(FH.p((c[0], c[1], zc + hub_h[1])), np.eye(3), np.array([r_hub, r_hub, dome]) * FH.sc),
                        rc.Plane((0, 0, -1.0), -FH.p((0, 0, zc + hub_h[1]))[2])], comp_hub, name + '_spinner',
                       sphere=(FH.p((c[0], c[1], zc + hub_h[1])), r_hub + dome + 0.2)))
    for i in range(n):
        a = a_off + 2 * np.pi * i / n
        pts = []
        for rr, ch, sw in ((r_hub * 0.85, chord * 1.1, 0.0), (r_tip, chord, sweep)):
            da = ch / rr
            for sgn in (-1, 1):
                p = _circle(c, rr, zc + sgn * pitch * 0.5, a + sw + sgn * da)
                for t in (-thick, thick):
                    pts.append((p[0], p[1], p[2] + t))
        out.append(hull(FH, pts, comp_blade, name + '_blade'))
    return out


# ---------------------------------------------------------------- the rear block
REAR_X = (0.0, 10.0, 19.6)                           # behind the fans | between them (TS: w 15 to x 10 at z 3..5)
REAR_HALF = [(15.0, 3.0), (15.0, 8.5), (10.0, 11.0)]  # TS: w 15 to z 8.5, 13 at z 9.5, 11 at 10.5
CORE_HALF = [(11.0, 3.0), (11.0, 9.5), (10.0, 11.0)]  # TS: w 12..10 between the fans, 11 at z 9, 10 at z 10
BACK = ((0.78, 5.0), (4.56, 11.0))                   # the back slope (x, z) (TS: x 1 at z 5, 2 at 6..7, 3 at 8, 4 at
#                                                     9..10, 5 at 11, 6 at 12: the least-squares line through the steps)
BUMPER_BOX = ((0.0, 1.3), 14.9, (3.0, 5.0))
PANEL_BACK = ((4.5, 11.0), (6.5, 13.0))              # the roof panel's back, as the back slope (TS: x 5 at z 11, 6 at 12)
PANEL_A = (10.0, [(8.2, 11.0), (8.2, 11.4), (7.0, 13.0)])    # behind x 10 (TS: w 8 at z 11, 7 at 12)
PANEL_B = (19.0, [(7.2, 11.0), (7.2, 11.4), (5.5, 13.0)])    # ahead, to x 19 (TS: w 7 at z 11, 6 and 5 at 12)
# TS's three black vents in the back slope (w, z), as TS draws them (its rows z 5..8, y 10..28): a triangle either side,
# its upright edge outboard (TS: y 11 / 27), its top along the khaki band (z 9), its slant from the band at w 2.5 down
# and out to w 7.2 at its foot (TS: the vents' inner ends w 3 at z 8, 4 at 7, 5 at 6, 7 at 5, alike both sides), and
# one pointing up between them (TS: w 4 either side at z 5, 3 at 6, 2 at 7, its tip at 8); TS's ochre struts between
# them make an inverted V
VENT_POLYS = [[(-8.5, 9.0), (-8.5, 5.1), (-7.2, 5.1), (-2.5, 9.0)],
              [(8.5, 9.0), (2.5, 9.0), (7.2, 5.1), (8.5, 5.1)],
              [(-4.4, 5.1), (4.4, 5.1), (0.0, 8.95)]]


def rear_parts():
    out = []
    blk = prism(FH, 0, section(REAR_HALF), REAR_X[0], REAR_X[1] + 0.3, REAR, ch=0.45, name='rear_block',
                edges=None, ends=(False, False))
    cut_xz(blk, BACK[0], BACK[1], (8.0, HYC, 7.0))
    out.append(blk)
    out.append(prism(FH, 0, section(CORE_HALF), REAR_X[1], REAR_X[2], CORE, ch=0.4, name='rear_core',
                     ends=(False, False)))
    (x0, x1), hw, (z0, z1) = BUMPER_BOX
    out.append(B(FH, x0, x1, Y(-hw), Y(hw), z0, z1, BUMPER, ch=0.3, name='bumper'))
    x0 = PANEL_BACK[0][0]
    for k, (x1, half) in enumerate((PANEL_A, PANEL_B)):
        p = prism(FH, 0, section(half), x0, x1 + (0.05 if k == 0 else 0.0), PANEL, ch=0.3, name='roof_panel',
                  ends=(k == 1, True))
        if k == 0:
            cut_xz(p, PANEL_BACK[0], PANEL_BACK[1], (12.0, HYC, 12.0))
        out.append(p)
        x0 = x1
    return out


# ---------------------------------------------------------------- the wing through the hull
WING_X = (18.0, 23.6)                                # TS: x 18..23 (left) / 18..24 (right)
WING_HALF = [(19.0, 3.0), (19.0, 4.75), (15.25, 8.5), (11.0, 10.6), (9.0, 11.0)]   # TS (its left side, the
#                                                     right's a voxel bumpier): w 19 to z 5, 18 at 5.5, 17 at 6.5,
#                                                     16 at 7.5, 15 at 8.5, 13 at 9.5, 11 at 10.5


def wing_parts():
    return [prism(FH, 0, section(WING_HALF), WING_X[0], WING_X[1], WING, ch=0.35, name='wing')]


# ---------------------------------------------------------------- the hull, its strakes, hatch and hump
HULL_X = (19.6, 43.0)
HULL_HALF = [(12.0, 3.0), (12.0, 8.3), (10.0, 9.3)]   # TS: w 12 to z 8.5, 10 at z 9.5 and 10.5 (the deck's sides:
HULL_DECK = (10.0, (9.2, 11.0))                      # a block of its own above the shoulders, w 10 to z 11)
STRAKES = [((23.4, 28.6), [(12.0, 3.2), (14.0, 5.0), (14.0, 7.0), (12.0, 9.0)]),   # TS: w 13 at z 4, 14 at 5..6,
           ((28.4, 36.4), [(12.0, 4.4), (13.0, 5.0), (13.0, 7.0), (12.0, 7.6)])]   # 13 at 7 / 13 at z 5..6 to x 35
HATCH_BOX = ((19.0, 29.0), 5.5, (10.8, 12.0))       # TS's grey panel on the deck (z 11 at x 19..28, y 13..24 / 14..23)
HUMP_X = (28.9, 45.0)
HUMP_HALF = [(7.2, 11.0), (3.6, 14.0)]               # TS: w 7 at z 11, 5 at 12, 4 at 13
HUMP_FRONT = ((40.0, 14.0), (44.0, 12.0))            # TS: x 41 at z 13, 43 at 12, 44 at 11
RAIL_X = (22.0, 42.8)
RAIL_W = (8.1, 9.95)                                 # TS: y 9..10 and 27..28 at z 10, x 22..40, and on the core
CORE_RAIL_X = (10.3, 18.0)                           # between the rear fans (TS: y 9 and 28 at z 10, x 10..18)
FRONT_RAIL = ((42.6, 54.3), (8.9, 10.1), (9.4, 11.05))   # along the front section's shoulders (TS's left side: y 28,
#                                                     z 9..10, x 22..55, green either side; its right has a dark strip
#                                                     by the cockpit instead)


def hull_parts():
    out = [prism(FH, 0, section(HULL_HALF), HULL_X[0], HULL_X[1], HULL, ch=0.4, name='hull', ends=(False, False))]
    hw, (z0, z1) = HULL_DECK
    out.append(B(FH, HULL_X[0], HULL_X[1], Y(-hw), Y(hw), z0, z1, HULL, ch=(0.0, 0.4, 0.0), name='hull_deck'))
    for (x0, x1), half in STRAKES:
        for s in (-1, 1):
            pts = []
            for x in (x0, x1):
                for (w, z) in half:
                    # the strake's front end tapers in by its last half voxel
                    ww = w if (x == x0 or w <= 12.0) else w - (0.5 if x1 > 30 else 0.0)
                    pts.append((x, Y(s * ww), z))
            out.append(hullq(pts, STRAKE, 'strake'))
    (x0, x1), hw, (z0, z1) = HATCH_BOX
    out.append(B(FH, x0, x1, Y(-hw), Y(hw), z0, z1, HATCH, ch=0.25, name='hatch'))
    h = prism(FH, 0, section(HUMP_HALF), HUMP_X[0], HUMP_X[1], HUMP, ch=0.4, name='hump', ends=(True, False))
    cut_xz(h, HUMP_FRONT[0], HUMP_FRONT[1], (35.0, HYC, 12.0))
    out.append(h)
    for s in (-1, 1):
        ya, yb = sorted((Y(s * RAIL_W[0]), Y(s * RAIL_W[1])))
        for (x0, x1) in (RAIL_X, CORE_RAIL_X):
            out.append(B(FH, x0, x1, ya, yb, 10.65, 11.25, RAIL, ch=0.18, name='rail'))
        (x0, x1), (wa, wb), (z0, z1) = FRONT_RAIL
        ya, yb = sorted((Y(s * wa), Y(s * wb)))
        out.append(B(FH, x0, x1, ya, yb, z0, z1, RAIL, ch=0.18, name='rail'))
    return out


# ---------------------------------------------------------------- the front section, its cockpit, its face plate
FRONT_X = (42.8, 54.0)
FRONT_HALF = [(12.0, 3.0), (13.0, 4.6), (13.0, 7.5), (11.0, 9.5), (6.5, 11.0)]   # TS: w 12 at z 3, 13 at 5..7, 12 at
#                                                     8.5, 11 at 9.5, 8 at 10.5
COCKPIT_X = (41.0, 50.0, 53.0)                       # TS: z 11 at x 43..49 (y 16..21) and 43..52 (y 13..15, 22..24)
COCKPIT_W = (3.0, 6.0)
COCKPIT_Z = (10.8, 12.0)
WINDOWS = ((40.5, 48.5), (1.0, 3.6))                 # TS's two black slots: x 41..48 (down the hump's front from x
#                                                     40), y 15..17 / 20..21 (intakes: the FMV's crew sit in the
#                                                     glazed nose)
FACE_X = (53.8, 55.0)
FACE_HALF = [(11.0, 5.0), (11.0, 10.0), (9.0, 11.0)]  # TS: x 54, y 8..29 at z 5..9, 10..27 at z 10


def front_parts():
    out = [prism(FH, 0, section(FRONT_HALF), FRONT_X[0], FRONT_X[1], FRONT, ch=0.4, name='front',
                 ends=(False, True))]
    x0, xm, x1 = COCKPIT_X
    wi, wo = COCKPIT_W
    z0, z1 = COCKPIT_Z
    out.append(B(FH, x0, xm, Y(-wi - 0.05), Y(wi + 0.05), z0, z1, CANOPY, ch=0.2, name='cockpit'))
    for s in (-1, 1):
        ya, yb = sorted((Y(s * wi), Y(s * wo)))
        out.append(B(FH, x0, x1, ya, yb, z0, z1, CANOPY, ch=0.22, name='cockpit'))
    out.append(prism(FH, 0, section(FACE_HALF), FACE_X[0], FACE_X[1], FACE, ch=0.3, name='face_plate',
                     ends=(False, True)))
    return out


# ---------------------------------------------------------------- the nose
NOSE_X = (53.9, 70.0)                               # TS: its bottom from x 54
NOSE_HALF = [(2.5, 3.0), (5.5, 5.3), (5.5, 6.8), (3.0, 10.6), (2.6, 11.0)]   # TS: w 3 at z 3.5, 4 at 4.5, 5..6 at
#                                                     5.5..6.5, 5 at 7.5, 4.5 at 8.5, 4 at 9.5, 3 at 10.5
NOSE_FRONT = ((65.4, 11.0), (70.0, 7.6))             # the top's slope at the front (TS: x 66 at z 10.5, 68 at 9.5,
#                                                     69 at 8.5, 70 at 7.5)
NOSE_CHIN = ((65.0, 3.0), (69.4, 5.2))               # the bottom rising to the front (TS: x 66 at z 3.5, 68 at 4.5)
PANES = ((65.0, 68.6), 3.4)                          # TS's blue-grey panes on the front slope (x 65..68, y 16..22)


def nose_parts():
    n = prism(FH, 0, section(NOSE_HALF), NOSE_X[0], NOSE_X[1], NOSE, ch=0.35, name='nose', ends=(False, True))
    cut_xz(n, NOSE_FRONT[0], NOSE_FRONT[1], (60.0, HYC, 6.0))
    cut_xz(n, NOSE_CHIN[0], NOSE_CHIN[1], (60.0, HYC, 6.0))
    return [n]


# ---------------------------------------------------------------- the fans
FAN_REAR = (14.0, 14.65)                             # x, w out (TS's lips' footprint: x 14.0, y 4.35 and 33.63)
FAN_FRONT = (60.5, 9.65)                             # TS: x 60.5, y 9.5 and 28.8
FANS = [('RR', (FAN_REAR[0], Y(-FAN_REAR[1]))), ('RL', (FAN_REAR[0], Y(FAN_REAR[1]))),
        ('FR', (FAN_FRONT[0], Y(-FAN_FRONT[1]))), ('FL', (FAN_FRONT[0], Y(FAN_FRONT[1])))]
LIP_RI = 3.3                                         # the lip's inner radius (local units, as all radii here):
#                                                     TS's lip ring is r 2.8..4.8, opened a little so the fan reads
LIP_Z = (9.6, 11.0)
FLOOR_Z = 9.45
# the cups' outer profiles (r, z): TS's rear drums r 3.25..3.5 at z 5, 4.25 at 6, 4.8..5 at 9..10; the front drums
# 3.35..4.35 at z 5..6, 4.35 at 7..8, 4.35..5.35 at 9..10 (their two sides differ by a voxel)
CUP = {'R': [(3.45, 5.0), (3.95, 5.5), (4.45, 6.6), (4.8, 8.6), (4.8, LIP_Z[0])],
       'F': [(3.55, 5.0), (3.95, 5.6), (4.35, 7.0), (4.7, 9.0), (4.7, LIP_Z[0])]}
HUB_R = 1.3                                          # TS: a grey hub with a dark centre amid the light khaki-grey disc


def cup_profile(kind):
    prof = [(0.0, 5.0)] + CUP[kind] + [(0.0, LIP_Z[0])]
    return prof


def lip_profile(kind):
    ro = CUP[kind][-1][0]
    return [(LIP_RI, LIP_Z[0]), (ro, LIP_Z[0]), (ro, 10.7), (ro - 0.28, 11.0), (LIP_RI + 0.24, 11.0),
            (LIP_RI, 10.76)]


def fan_parts():
    out = []
    for k, (nm, c) in enumerate(FANS):
        kind = nm[0]
        out += ring_sectors(c, cup_profile(kind), 32, DRUM, 'fan_drum', a_off=0.04 * k)
        out += ring_sectors(c, lip_profile(kind), 40, LIP, 'fan_lip', a_off=0.04 * k)
        out.append(cyl(FH, (c[0], c[1], LIP_Z[0] - 0.2), (c[0], c[1], FLOOR_Z + 0.1), LIP_RI + 0.05, FLOOR,
                       'fan_floor'))
        out += rotor(c, HUB_R, LIP_RI + 0.02, 10.1, 9, HUB, BLADE, 'fan', a_off=0.2 + 0.31 * k, pitch=0.42,
                     chord=0.62, hub_h=(0.55, 0.32), dome=0.24, sweep=0.2 if c[1] < HYC else -0.2)
    # the front fans' struts to the nose (TS's grey frames: x 55..59, y 13..15 and 22..25, z 5..9), and the frame on
    # the face plate's edges they spring from (TS: x 55, posts at y 8..10 and 26..29, bars at z 5 and 9)
    for s in (-1, 1):
        ya, yb = sorted((Y(s * 3.6), Y(s * 6.4)))
        out.append(B(FH, 55.0, 59.8, ya, yb, 5.0, 10.0, STRUT, ch=0.25, name='fan_strut'))
        ya, yb = sorted((Y(s * 8.0), Y(s * 10.8)))
        out.append(B(FH, 54.9, 56.0, ya, yb, 5.0, 10.0, STRUT, ch=0.2, name='face_post'))
        ya, yb = sorted((Y(s * 6.2), Y(s * 8.2)))
        for z0, z1 in ((5.0, 6.0), (9.0, 10.0)):
            out.append(B(FH, 54.9, 56.0, ya, yb, z0, z1, STRUT, ch=0.15, name='face_bar'))
    return out


# ---------------------------------------------------------------- the legs, the belly
LEGS = [(5.0, 12.25, 1.75), (18.0, 16.0, 2.0), (49.0, 9.75, 1.75)]   # foot's back x, w, half width (TS's feet: x 5..11
#                                                     / 18..24 / 49..55; y 5..8 + 29..33 / 1..5 + 33..37 / 8..11 + 27..31)


def leg_parts():
    out = []
    for i, (x0, w, hw) in enumerate(LEGS):
        for s in (-1, 1):
            wc = s * w
            ya, yb = sorted((Y(wc - hw), Y(wc + hw)))
            out.append(B(FH, x0, x0 + 6.0, ya, yb, 0.0, 1.0, FOOT, ch=0.3, name='leg_foot'))
            ya, yb = sorted((Y(wc - hw + 0.35), Y(wc + hw - 0.35)))
            out.append(B(FH, x0 + 1.4, x0 + 4.0, ya, yb, 0.9, 2.15, LEG, ch=0.2, name='leg_strut'))
            ya, yb = sorted((Y(wc - hw + 0.6), Y(wc + hw - 0.6)))
            out.append(B(FH, x0 + 4.9, x0 + 5.9, ya, yb, 0.9, 2.15, LEG, ch=0.15, name='leg_rod'))
            ya, yb = sorted((Y(wc - hw), Y(wc + hw)))
            out.append(B(FH, x0 + 1.0, x0 + 5.0, ya, yb, 2.0, 3.15, LEG, ch=0.25, name='leg_knuckle'))
            if i == 1:
                # the mount in the wing's tip (TS: dark olive, z 4 at x 18..22, y 0..5)
                ya, yb = sorted((Y(s * 14.2), Y(s * 19.06)))
                out.append(B(FH, 18.6, 23.0, ya, yb, 3.95, 4.95, LEGM, ch=0.12, name='leg_mount'))
    return out


BELLY_X = (28.0, 44.0)
BELLY_W = (8.0, 12.0)
DOOR_BOX = ((9.0, 20.0), (8.0, 12.0), (2.0, 3.05))   # TS: z 2 at x 9..19, y 8..11 (the right side only)


def belly_parts():
    out = []
    for s in (-1, 1):
        ya, yb = sorted((Y(s * BELLY_W[0]), Y(s * BELLY_W[1])))
        out.append(B(FH, BELLY_X[0], BELLY_X[1], ya, yb, 2.0, 3.05, BELLY, ch=0.22, name='belly_strip'))
    (x0, x1), (y0, y1), (z0, z1) = DOOR_BOX
    out.append(B(FH, x0, x1, y0, y1, z0, z1, DOOR, ch=0.22, name='door'))
    return out


def model():
    return {'hull': rear_parts() + wing_parts() + hull_parts() + front_parts() + nose_parts() + fan_parts() +
            leg_parts() + belly_parts()}


SECTIONS = {'hull': FH}


def posed(m, which=('hull',), Mx=np.eye(3)):
    """the parts posed (TS's HVA, frame 0) and turned by Mx (unit frame -> world): (parts, frames, owner)."""
    parts, frames, owner = [], [], []
    for k in which:
        F = SECTIONS[k]
        R, t = F.pose()
        Rw, tw = Mx @ R, Mx @ t
        Mq = Rw @ np.diag(1.0 / F.sc)
        tq = tw + Rw @ F.mn
        for p in m[k]:
            parts.append(p.moved(Rw, tw)); frames.append((Mq, tq)); owner.append(k)
    return parts, frames, np.array(owner)
