"""
mwarmodel.py - the Mobile War Factory (Firestorm's [MOBWARG], TSMWAR in the mod) rebuilt the way the Titan, the
Wolverine, the MCV, the Mammoths, the APC and the sensor array are: TS's own voxel (MWAR_NOD.VXL, one section) as the
blueprint for where every part is and how big, each part modelled clean (flat plates, true slopes, round wheels,
bevelled edges) in TS's colours - grey plate with TS's house-colour blocks, a dark grey chassis and crane, black
tyres, rails and openings, olive equipment boxes.

q: continuous voxel coordinates (voxel i spans i..i+1): x 0..44 back to front, y 0..25 from the unit's right to its
left, z 0..24 up; the local frame is min + q * scale (TS's), placed in the unit's frame by the HVA (frame 0) and
lowered GZ onto the ground (mwarcam.py).

TS's layout, back to front: the rear frame (two grey corner blocks, two black rails across); a house-colour block
the full width and height; the middle section (grey sides with two black rails, a house-colour top with grey and
black panels); a second house-colour block; the front tower (grey side walls cut away diagonally at the front over a
house-colour core, a house-colour roof running forward as a canopy); the rounded, stepped grey nose.  Six wheels a
side: two pairs under grey fenders at the back half, outboard, and a pair under the nose, inboard; olive boxes on the
sides before the front wheels and on the nose's left; the folded crane lying on top.
"""
import os, sys
from paths import HANDOFF
sys.path.insert(0, os.path.join(HANDOFF, 'renderer'))
import numpy as np
import vxl
import rc
from qparts import Frame, B, prism, hull, cyl
from mwarcam import GZ

D = os.path.join(HANDOFF, '14-TSMWAR', 'ts-original') + os.sep

(CHASSIS, TYRE, HUB, FENDER, OLIVE, BODY, DARK, BLACK, GREEN, NOSE, CRANE, LIGHT, TUBE, CHROME, GLASS) = range(81, 96)
HOUSE = (GREEN,)


def _load(name):
    s = vxl.read_vxl(D + name + '.VXL')[0]
    names, mats = vxl.read_hva(D + name + '.HVA')
    return Frame(s, mats[0, 0])


F = _load('MWAR_NOD')
YC = 12.5                                           # the wheels' centre line (q y)
YB = 12.0                                           # the body's (TS: its blocks y 3..21, the wheels' 0..25)
TUBE_R = 2.7                                        # the tube on top: its radius and its axis's ends (q); its top
TUBE_A = (13.9, YB, 24.3 - TUBE_R)                  # at the back as high as TS's boom (z 24), falling as TS's does
TUBE_B = (27.0, YB, 24.3 - TUBE_R - 0.36 * (27.0 - 13.9))


def plane_q(n_q, q_point):
    n = np.asarray(n_q, float) / F.sc
    n = n / np.linalg.norm(n)
    return rc.Plane(n, n @ F.p(q_point))


def mirror(y0, y1, c=YC):
    """a y range and its mirror about a centre line (the wheels' by default)."""
    return (y0, y1), (2 * c - y1, 2 * c - y0)


# ---------------------------------------------------------------- the running gear
WHEELS_OUT = (5.0, 10.0, 20.0, 25.0)                 # TS: outboard, y 0..3 and 22..25, under the fenders
WHEELS_FRONT = (35.0, 40.0)                          # TS: inboard under the nose, y 7..10 and 15..18
R_WHEEL, Z_WHEEL = 2.5, 2.5


def fender_profile(xa, xb, z0=4.2, z1=6.05, n=9):
    """a fender's side: a flattened arch from xa to xb, its ends down at z0, its top z1."""
    xm, hw = (xa + xb) / 2, (xb - xa) / 2
    pts = [(xa, z0), (xb, z0)]
    for k in range(n + 1):
        u = 1.0 - 2.0 * k / n                       # 1 .. -1 across the top, front to back
        pts.append((xm + hw * u, z0 + (z1 - z0) * (1 - abs(u) ** 4) ** 0.5))
    return pts[:2] + pts[3:-1]                       # the arch's own end points repeat the corners


def wheel(x, y0, y1, outer_y):
    out = [cyl(F, (x, y0, Z_WHEEL), (x, y1, Z_WHEEL), R_WHEEL, TYRE, 'tyre')]
    s = -1.0 if outer_y < YC else 1.0
    out.append(cyl(F, (x, outer_y - 0.25 * s, Z_WHEEL), (x, outer_y + 0.06 * s, Z_WHEEL), 1.25, HUB, 'hub'))
    return out


def running_gear():
    out = []
    for (y0, y1) in mirror(0.05, 3.0):
        right = y0 < YC
        outer = y0 if right else y1
        for x in WHEELS_OUT:
            out += wheel(x, y0, y1, outer)
        # the fenders over each pair (TS: z 5..6, their ends stepping down to z 4), curved and chrome as Westwood's
        # cameo has them, a little wider than the tyres
        fy0, fy1 = (y0 - 0.05, y1 + 0.15) if right else (y0 - 0.15, y1 + 0.05)
        for xa, xb in ((2.0, 14.0), (17.0, 28.0)):
            out.append(prism(F, 1, fender_profile(xa, xb), fy0, fy1, FENDER, ch=0.12, name='fender'))
        # the olive box before the front wheels (TS: x 28..33, z 2..6), set in a little from the tyres' outside
        oy0, oy1 = (y0 + 0.35, y1 + 0.2) if right else (y0 - 0.2, y1 - 0.35)
        out.append(B(F, 28.0, 33.0, oy0, oy1, 2.0, 6.0, OLIVE, ch=0.2, name='olive_box'))
    for (y0, y1) in mirror(7.0, 10.0):
        outer = y0 if y0 < YC else y1
        for x in WHEELS_FRONT:
            out += wheel(x, y0, y1, outer)
    # the chassis (TS's dark grey: y 3..22, z 2..4) and the rear bumper across (TS: x 0, z 3)
    out.append(B(F, 0.6, 32.5, 3.0, 22.0, 2.0, 4.2, CHASSIS, ch=0.2, name='chassis'))
    out.append(B(F, 0.0, 1.4, 0.3, 24.7, 2.8, 4.2, BLACK, ch=0.25, name='rear_bumper'))
    return out


# ---------------------------------------------------------------- the body
def body():
    out = []
    # the rear frame (TS: x 0..4): grey corner blocks at y 5..9 and 15..19, the black rail across (z 9..11) and the
    # dark grey hatch above it (z 14..19)
    for (y0, y1) in mirror(5.0, 9.0, YB):
        out.append(B(F, 1.0, 4.3, y0, y1, 4.0, 9.0, BODY, ch=0.22, name='rear_block'))
        out.append(B(F, 2.0, 4.3, y0, y1, 11.0, 14.0, BODY, ch=0.18, name='rear_frame'))
    out.append(B(F, 0.0, 3.0, 4.0, 20.0, 9.0, 11.0, BLACK, ch=0.45, name='rear_rail'))
    # the rear hatch (TS: dark grey, 52, its back's top edge stepped down to x 0 at z 16)
    out.append(prism(F, 1, [(0.0, 14.0), (4.2, 14.0), (4.2, 19.0), (2.0, 19.0), (0.0, 16.4)], 5.0, 19.0, DARK,
                     ch=0.3, name='rear_hatch'))
    # the two house-colour blocks the full width and height (TS: x 4..10 and 19..25, y 3..21, z 4..19)
    out.append(B(F, 4.0, 10.0, 3.0, 21.0, 4.0, 19.0, GREEN, ch=0.25, name='green_block'))
    out.append(B(F, 19.0, 25.0, 3.0, 21.0, 4.0, 19.0, GREEN, ch=0.25, name='green_block'))
    # the middle section between them: grey sides (TS: y 4..21 up to z 13), two black rails along each side (TS: z
    # 6..8 and 9..11, a voxel proud), its top a house-colour box (TS: y 5..19, up to 18) with grey panels on its
    # sides, and behind it a black bar across, as high as the blocks (TS: x 10..14, black 63, up to z 19)
    out.append(B(F, 9.8, 19.2, 4.0, 20.0, 4.0, 13.0, BODY, ch=0.2, name='middle'))
    for (y0, y1) in mirror(3.0, 4.3, YB):
        for z0, z1 in ((6.0, 8.0), (9.0, 11.0)):
            out.append(B(F, 10.0, 19.0, y0, y1, z0, z1, BLACK, ch=0.2, name='side_rail'))
    out.append(B(F, 13.8, 19.4, 5.0, 19.0, 12.9, 18.0, GREEN, ch=0.2, name='middle_top'))
    out.append(B(F, 10.0, 14.0, 5.0, 19.0, 12.9, 19.0, BLACK, ch=0.2, name='middle_bar'))
    # the front tower (TS: x 24..33): grey side walls (TS: y 6..7 and 18..19) cut away diagonally at the front
    # over a house-colour core, its sides cut away again two voxels further on (TS: the green band left between the
    # cuts, from x 28..30 at z 6 to x 31..33 at z 10), on a grey floor (TS: z 5); a grey face high on its front
    # (TS: x 31..32, z 10..14); the house-colour roof running forward over the nose's back as a canopy (TS: x
    # 24..36, y 7..17, z 14..18), its sides hanging down to the nose's hood, their lower edges carrying on the
    # core's cut (TS: x 32..33 at z 11 to x 32..35 at z 13)
    out.append(prism(F, 1, [(24.6, 4.0), (27.9, 4.0), (32.6, 9.5), (32.6, 14.6), (24.6, 14.6)], 7.0, 18.0, GREEN,
                     ch=0.2, name='tower_core'))
    out.append(B(F, 24.6, 32.0, 5.0, 19.0, 4.0, 6.0, BODY, ch=0.15, name='tower_floor'))
    for (y0, y1) in ((6.0, 7.1), (17.9, 19.0)):
        out.append(B(F, 24.6, 28.2, y0, y1, 4.0, 14.8, BODY, ch=0.15, name='tower_wall'))
        out.append(prism(F, 1, [(28.0, 8.0), (32.6, 11.0), (32.6, 14.8), (28.0, 14.8)], y0, y1, BODY, ch=0.15,
                         name='tower_wall'))
    out.append(B(F, 30.8, 32.8, 6.0, 19.0, 10.0, 14.8, BODY, ch=0.2, name='tower_front'))
    out.append(B(F, 24.0, 36.0, 7.0, 17.0, 14.4, 18.0, GREEN, ch=0.25, name='roof'))
    for (y0, y1) in ((6.9, 7.9), (16.0, 17.0)):
        out.append(prism(F, 1, [(32.4, 9.3), (36.0, 13.5), (36.0, 14.6), (32.4, 14.6)], y0, y1, GREEN, ch=0.12,
                         name='canopy_side'))
    # a side window high in each of the cab's walls, ahead of the door (the windscreen is the nose's: nose())
    for (y0, y1) in ((5.93, 6.0), (19.0, 19.07)):
        out.append(B(F, 29.2, 32.0, y0, y1, 11.5, 14.1, GLASS, ch=0.02, name='side_window'))
    # a hatch in the roof ahead of the crane's support, a step proud
    out.append(B(F, 31.4, 34.6, 10.4, 13.6, 17.95, 18.2, GREEN, ch=0.08, name='roof_hatch'))
    return out


# ---------------------------------------------------------------- the nose: the cab's front
# TS's stepped grey nose, sloping down from under the canopy's front edge (TS: its top 13 at x 36 to 9 at x 43), is
# the cab's front (Luke: its window as the MCV's): the windscreen raked down the upper slope from under the canopy's
# edge, the cab's bodywork framing the glass (a pillar each side and one in the middle, the sill), the glass a little
# below that frame; the bonnet below it sloping gently down to a bevelled front edge, the grille in its front face
# over the bumper.
WS_TOP = (35.6, 14.45)                               # the windscreen's slope, from under the canopy's front edge
WS_BOT = (40.6, 10.85)                               # down to the sill (q x, z)
WS_D = np.subtract(WS_BOT, WS_TOP) / np.hypot(*np.subtract(WS_BOT, WS_TOP))
WS_N = np.array([-WS_D[1], WS_D[0]])                 # out of the slope (up and forward)
WS_L = float(np.hypot(*np.subtract(WS_BOT, WS_TOP)))


def on_slope(s, off=0.0):
    """a point s along the windscreen's slope from its top, off out of it (q x, z)."""
    p = np.array(WS_TOP) + WS_D * s + WS_N * off
    return (float(p[0]), float(p[1]))


def nose():
    out = [prism(F, 1, [(35.0, 4.5), (40.6, 4.5), WS_BOT, WS_TOP, (35.0, 14.45)], 7.0, 16.0, NOSE, ch=0.2,
                 name='cab')]
    out.append(B(F, 32.6, 35.2, 8.05, 15.95, 9.8, 14.45, NOSE, ch=0.1, name='cab_back'))
    out.append(prism(F, 1, [(40.5, 4.5), (44.0, 4.5), (44.0, 9.35), (43.55, 9.85), (40.5, 10.85)], 7.0, 16.0, NOSE,
                     ch=0.25, name='bonnet'))
    # the windscreen: the glass a little proud of the slope, set below its frame
    g0, g1 = 0.4, WS_L - 0.5
    out.append(prism(F, 1, [on_slope(g0, 0.03), on_slope(g0, 0.07), on_slope(g1, 0.07), on_slope(g1, 0.03)],
                     7.75, 15.25, GLASS, name='windscreen'))
    for (ya, yb), off in (((7.0, 7.75), 0.14), ((15.25, 16.0), 0.14), ((11.38, 11.62), 0.11)):
        out.append(prism(F, 1, [on_slope(-0.2), on_slope(-0.2, off), on_slope(WS_L, off), on_slope(WS_L)], ya, yb,
                         NOSE, ch=0.04, name='ws_pillar'))
    out.append(prism(F, 1, [on_slope(WS_L - 0.55), on_slope(WS_L - 0.55, 0.14), on_slope(WS_L + 0.05, 0.14),
                            on_slope(WS_L + 0.05)], 7.0, 16.0, NOSE, ch=0.05, name='ws_sill'))
    out.append(B(F, 33.0, 43.2, 10.0, 15.0, 2.0, 4.7, NOSE, ch=0.2, name='nose_keel'))
    # its back, narrower, reaching in under the tower's front (TS: x 31..33, y 9..15, z 6..10)
    out.append(B(F, 30.6, 33.4, 9.0, 16.0, 4.5, 10.0, NOSE, ch=0.15, name='nose_back'))
    # the silver bumper across its front at the bottom (Westwood's cameo)
    out.append(B(F, 43.5, 44.5, 7.3, 15.7, 4.5, 5.7, CHROME, ch=0.25, name='bumper'))
    # the olive box stepped down the nose's left side (TS: y 16..18, x 36..42, z 4..10)
    out.append(prism(F, 1, [(36.0, 4.4), (42.6, 4.4), (42.6, 8.0), (38.4, 10.0), (36.0, 10.0)], 15.9, 17.5, OLIVE,
                     ch=0.15, name='nose_box'))
    return out


# ---------------------------------------------------------------- the folded crane on top
def crane():
    out = []
    # its pedestal at the back (TS: x 13..17, y 10..14, z 16..19), the wedge of the folded boom on top (TS: flat on
    # z 19, its top stepping down from z 24 at x 14..16 to z 20 at x 25), its arms along its sides at the back
    # (TS: y 7..9 and 15..17, blue-grey joints), its front support (TS: x 25..30, z 18..20)
    out.append(B(F, 13.0, 17.0, 10.0, 14.0, 16.0, 20.2, CRANE, ch=0.15, name='crane_pedestal'))
    # the boom: a tube lying tilted on top (Westwood's cameo: a white tube; TS: its top stepping down from z 24 at
    # x 14..16 to z 20 at x 25, its front end down in the roof)
    a, b = F.p(TUBE_A), F.p(TUBE_B)
    out.append(rc.cylinder(a, b, F.r(TUBE_R), TUBE, 'tube'))
    out.append(rc.cylinder(a - (b - a) / np.linalg.norm(b - a) * F.r(0.35), a, F.r(TUBE_R - 0.35), CRANE, 'tube_cap'))
    # the cradle's side plates along the tube's back half, as high as its top at the back, their blue-grey clamps
    # at the top (TS: y 7..9 and 15..17, from z 24 at x 15..16 down to z 19 at x 19)
    for (y0, y1) in mirror(7.0, 9.3, YB):
        out.append(prism(F, 1, [(13.2, 18.6), (19.8, 18.6), (19.8, 20.2), (16.6, 24.0), (14.8, 24.0), (13.2, 23.0)],
                         y0, y1, CRANE, ch=0.12, name='crane_bracket'))
    out.append(B(F, 24.8, 30.0, 9.0, 15.0, 17.6, 19.6, CRANE, ch=0.15, name='crane_support'))
    # the pivots the boom folds on: a round boss on each side plate's outside, in TS's blue-grey clamp
    for yo, yi in ((6.78, 7.05), (17.22, 16.95)):
        out.append(cyl(F, (16.3, yo, 22.2), (16.3, yi, 22.2), 0.72, LIGHT, 'pivot'))
    return out


def model():
    return running_gear() + body() + nose() + crane()


def posed(m, Mx=np.eye(3)):
    """the parts posed (HVA frame 0), lowered GZ onto the ground and turned by Mx (unit frame -> world):
    (parts, frames)."""
    R, t = F.pose()
    Rw, tw = Mx @ R, Mx @ t + np.array([0.0, 0.0, -GZ])
    Mq = Rw @ np.diag(1.0 / F.sc)
    tq = tw + Rw @ F.mn
    return [p.moved(Rw, tw) for p in m], [(Mq, tq)] * len(m)
