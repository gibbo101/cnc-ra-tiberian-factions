"""
lpstmodel.py - the Mobile Sensor Array (TS's [LPST]) rebuilt the way the Titan, the Wolverine, the MCV, the Mammoths
and the APC are: TS's own voxel (LPST.VXL, one section) as the blueprint for where every part is and how big, each part
modelled clean (flat plates, true slopes, round wheels, bevelled edges) in TS's colours - GDI's ochre with TS's
house-colour panels, dark grey track covers and bumpers, a dark mast, blue-grey windows, yellow lamps.

q: continuous voxel coordinates (voxel i spans i..i+1): x 0..39 back to front, y 0..23 from the unit's right to its
left, z 0..23 up; the local frame is min + q * scale (TS's), placed in the unit's frame by the HVA (frame 0).

TS's layout: two track units a side under dark grey covers; between them a keel; on it the sensor pole folded down the
right half the whole length (Luke: it swings up at its back end when the array deploys; the radar dish, packed in the
grey casing at its front end, only comes out then), resting on its hinge, cradle, struts and mount; on the left half a
tall block at the back (the mast on it), stairs down to a low deck, and the cab at the front with its windows.
"""
import os, sys
from paths import HANDOFF
sys.path.insert(0, os.path.join(HANDOFF, 'renderer'))
import numpy as np
import vxl
import rc
from qparts import Frame, B, prism, hull, cyl

D = os.path.join(HANDOFF, '12-TSLPST', 'ts-original') + os.sep

(HOUSING, BLOCK, STAIR, DECK, CAB, KEEL, COVER, BELT, WHEEL, HUB, CORE, BUMPER, MAST, PANEL, LAMP, REARLAMP,
 DISH, HINGE, MOUNT, CRADLE) = range(81, 101)
HOUSE = (PANEL,)
OCHRE_PARTS = (HOUSING, BLOCK, STAIR, DECK, CAB, KEEL)


def _load(name):
    s = vxl.read_vxl(D + name + '.VXL')[0]
    names, mats = vxl.read_hva(D + name + '.HVA')
    return Frame(s, mats[0, 0])


F = _load('LPST')
YC = 11.0                                           # the hull's centre line (q y)
POLE_Y, SIDE_Y = 10.7, 11.0                         # the groove between the pole and the block and cab (q y)


def plane_q(n_q, q_point):
    n = np.asarray(n_q, float) / F.sc
    n = n / np.linalg.norm(n)
    return rc.Plane(n, n @ F.p(q_point))


def wheel(x, z, r, y0, y1, comp, name='wheel', bevel=0.0):
    p0, p1 = F.p((x, y0, z)), F.p((x, y1, z))
    rl = F.r(r, 1)
    extra = []
    if bevel > 0:
        a = (p1 - p0) / np.linalg.norm(p1 - p0)
        for k in range(16):
            th = 2 * np.pi * (k + 0.5) / 16
            rad = np.array([np.cos(th), 0.0, np.sin(th)])
            for end, s in ((p0, -1.0), (p1, 1.0)):
                n = rad + s * a; n = n / np.linalg.norm(n)
                q = end + rad * (rl - F.r(bevel, 1))
                extra.append(rc.Plane(n, n @ q))
    return rc.cylinder(p0, p1, rl, comp, name, extra)


# the track units (TS: two a side).  Each belt's lower run on the ground at x 4..15 and 23..33, its ends stepping up
# to x 0..18 and 21..35 at z 2 (TS's steps, as slopes); the belt rises at each end to the cover (TS: z 4), and between
# the ends there is a gap under the cover (TS: z 3..4) in which the belt's top shows, its olive-brown tread a voxel in
# from its outer side (TS's).  On its outer side three road wheels with grey hubs (TS: hubs at x 5, 8, 11 and 25, 28,
# 31, z 1).  At each unit's front end a dark grey lip under the cover (TS: z 3..5, x 18..19 and 35..37).  The covers:
# x 0..18 and 20..36, z 4..6.  The belts are TS's y 0..5 and 17..22; the left cover overhangs its belt by a voxel
# (TS: y 17..23).
UNITS = (dict(poly=[(4.0, 0.0), (15.0, 0.0), (17.0, 1.0), (18.0, 2.0), (18.0, 3.0), (0.0, 3.0), (0.0, 2.0)],
              wraps=((0.0, 2.2), (16.6, 18.0)), road=(5.5, 8.5, 11.5),
              cover=(0.0, 18.0), lip=(18.0, 19.0)),
         dict(poly=[(23.0, 0.0), (33.0, 0.0), (35.0, 2.0), (35.0, 3.0), (21.0, 3.0), (21.0, 2.0)],
              wraps=((21.0, 22.2), (33.8, 35.0)), road=(25.5, 28.5, 31.5),
              cover=(20.0, 36.0), lip=(35.0, 37.0)))
R_ROAD, Z_ROAD, R_HUB = 1.2, 1.45, 0.5
BELTS = ((0.0, 5.0), (17.0, 22.0))                  # TS's right and left belts (q y)
COVERS = ((0.0, 5.0), (17.0, 23.0))                 # and their covers


def inset(poly, d):
    """a convex polygon (q x, z) shrunk by d on every edge."""
    P = np.asarray(poly, float)
    n = len(P)
    c = P.mean(0)
    lines = []
    for k in range(n):
        a, b = P[k], P[(k + 1) % n]
        e = b - a
        nn = np.array([e[1], -e[0]]) / np.linalg.norm(e)
        if nn @ (c - a) < 0:
            nn = -nn
        if lines and abs(lines[-1][0] @ nn - 1.0) < 1e-9:
            continue                                   # collinear with the edge before
        lines.append((nn, nn @ a + d))                 # inside: nn . p >= nn . a + d
    out = []
    n = len(lines)
    for k in range(n):
        (n1, d1), (n2, d2) = lines[k - 1], lines[k]
        out.append(np.linalg.solve(np.array([n1, n2]), np.array([d1, d2])))
    return [tuple(p) for p in out]


def track_unit(U, y0, y1):
    yo = y0 if y0 < YC else y1
    s = -1.0 if y0 < YC else 1.0
    out = [prism(F, 1, U['poly'], y0 + 0.12, y1 - 0.12, BELT, ch=0.18, name='belt')]
    # the belt rising round each end to the cover
    for xa, xb in U['wraps']:
        out.append(B(F, xa, xb, y0 + 0.12, y1 - 0.12, 2.4, 4.05, BELT, ch=0.15, name='belt_wrap'))
    # the lower run's outer face recessed between its edges (the wheels' side)
    ya, yb = sorted((yo - 0.3 * s, yo + 0.02 * s))
    out.append(prism(F, 1, inset(U['poly'], 0.42), ya, yb, CORE, name='belt_side'))
    for xr in U['road']:
        out.append(cyl(F, (xr, yo - 0.35 * s, Z_ROAD), (xr, yo + 0.05 * s, Z_ROAD), R_ROAD, WHEEL, 'road_wheel'))
        out.append(cyl(F, (xr, yo - 0.2 * s, Z_ROAD), (xr, yo + 0.13 * s, Z_ROAD), R_HUB, HUB, 'hub'))
    # the dark grey lip at the unit's front end, under the cover's edge
    out.append(B(F, U['lip'][0], U['lip'][1], y0, y1, 3.0, 5.0, COVER, ch=0.18, name='track_lip'))
    return out


def model():
    out = []
    # ---------------------------------------------------------------- running gear
    for (y0, y1), (c0, c1) in zip(BELTS, COVERS):
        for U in UNITS:
            out += track_unit(U, y0, y1)
            # the dark grey cover over each unit (TS: z 4..6)
            out.append(B(F, U['cover'][0], U['cover'][1], c0, c1, 4.0, 6.0, COVER, ch=0.25, name='track_cover'))
    # the keel between the tracks (TS: x 1..35 at z 2, the back's bottom row stepped in to x 1, its front sloping
    # out to x 37 at z 4; its back the unit's back plate at x 0)
    p = B(F, 0.0, 37.0, 5.0, 17.0, 2.0, 6.2, KEEL, ch=0.2, name='keel')
    p.cons.append(plane_q((-1.0, 0.0, -1.0), (0.0, 0.0, 3.0)))
    p.cons.append(plane_q((1.0, 0.0, -1.0), (35.0, 0.0, 2.0)))
    out.append(p)
    # ---------------------------------------------------------------- the body
    # the sensor pole, folded down the right half (TS: a box at y 6..11, z 9..15, x 1..37).  Luke: it swings up at
    # its back end when the array deploys, and the grey at its front end is the radar dish.  A beam of its own: a
    # groove between it and the block and the cab beside it (y POLE_Y..SIDE_Y); its top back edge stepped down (TS:
    # z 14 at x 1..3); its front end set in a voxel below its top (TS's recess there), over the dish's pod.
    p = B(F, 1.0, 36.0, 6.0, POLE_Y, 9.0, 15.0, HOUSING, ch=0.22, name='pole')
    p.cons.append(plane_q((-1.0, 0.0, 1.0), (1.5, 0.0, 14.0)))
    out.append(p)
    out.append(B(F, 35.9, 37.0, 6.0, POLE_Y, 12.0, 15.0, HOUSING, ch=0.22, name='pole_tip'))
    # what it rests on (TS's layer under it, z 7..9): the hinge it swings up on in the open recess at its back end
    # (TS's dark grey there), a dark grey cradle along its back half (TS: x 4..18, louvred), two dark struts (TS:
    # x 20..23 at y 7 and 9, open between), and the mount its front end lies in (TS: x 24..37, its right side up to
    # z 12 from x 29)
    out.append(cyl(F, (3.3, 6.25, 8.0), (3.3, POLE_Y - 0.25, 8.0), 0.62, HINGE, 'hinge_axle'))
    for ya, yb in ((6.35, 7.05), (POLE_Y - 1.05, POLE_Y - 0.35)):
        out.append(B(F, 2.5, 4.1, ya, yb, 6.2, 8.4, HINGE, ch=0.08, name='hinge_bracket'))
    out.append(B(F, 4.0, 18.6, 6.1, POLE_Y - 0.1, 6.2, 9.0, CRADLE, ch=0.12, name='cradle'))
    for ya, yb in ((7.0, 8.0), (9.0, 10.0)):
        out.append(B(F, 20.0, 23.0, ya, yb, 6.2, 9.0, MAST, ch=0.1, name='strut'))
    out.append(B(F, 24.0, 36.0, 5.0, POLE_Y, 6.2, 9.0, MOUNT, ch=0.18, name='mount'))
    out.append(B(F, 29.0, 37.0, 5.0, 5.95, 8.9, 12.0, MOUNT, ch=0.15, name='mount_side'))
    # the radar dish, packed away in its grey casing low on the pole's front end (TS's grey block at x 36..38, z 8..10,
    # y 6..11; Luke: the dish only comes out when the array deploys)
    out.append(B(F, 36.0, 38.0, 6.15, POLE_Y - 0.15, 8.0, 10.0, DISH, ch=0.3, name='dish_casing'))
    # the tall block at the back of the left half (TS: x 3..15, y 11..17, up to 15) and the low rear deck under the
    # pole's back end and behind the block (TS: x 1..4, y 5..17, top 7)
    out.append(B(F, 3.0, 15.0, SIDE_Y, 17.0, 6.0, 15.0, BLOCK, ch=0.22, name='block'))
    out.append(B(F, 0.8, 4.2, 5.0, 17.0, 6.0, 7.0, DECK, ch=0.12, name='rear_deck'))
    # the stairs down from the block to the low deck (TS: tops 13, 12, 11, 10 at x 15..19, then 8)
    for i, (x0, top) in enumerate(((15.0, 13.0), (16.0, 12.0), (17.0, 11.0), (18.0, 10.0), (19.0, 8.0))):
        out.append(B(F, x0 - 0.05, x0 + 1.0, SIDE_Y, 17.0, 6.0, top, STAIR, ch=0.08, name='stair'))
    # the low deck between the stairs and the cab (TS: top 7)
    out.append(B(F, 19.9, 29.2, SIDE_Y, 17.0, 6.0, 7.0, DECK, ch=0.1, name='deck'))
    # the cab at the front of the left half (TS: x 29..36, y 10..17, its roof at 16): its lower front out to the green
    # panel (TS: x 37, up to z 12), the windscreen set back above it (TS: x 36, z 12..15, blue-grey), raked a little;
    # the band of side windows along its left side proud by a voxel (TS: y 17..18, x 29..36, z 12..15, blue-grey)
    out.append(B(F, 29.0, 36.0, SIDE_Y, 17.0, 6.0, 16.0, CAB, ch=0.2, name='cab'))
    out.append(B(F, 35.5, 37.0, SIDE_Y, 17.0, 6.0, 12.0, CAB, ch=0.15, name='cab_front'))
    out.append(prism(F, 1, [(35.0, 11.95), (36.6, 11.95), (36.0, 15.0), (35.0, 15.0)], SIDE_Y, 17.95, CAB, ch=0.06,
                     name='windscreen'))
    out.append(B(F, 29.0, 36.0, 16.9, 18.0, 12.0, 15.0, CAB, ch=0.12, name='side_windows'))
    # TS's house-colour panels, each proud of its face: the strip along the pole's right side, the panel on the
    # block's left side (wider below), the cab's front
    out.append(B(F, 6.0, 20.0, 5.4, 6.15, 10.0, 13.0, PANEL, ch=0.1, name='panel_right'))
    out.append(B(F, 7.0, 15.0, 16.85, 17.6, 7.0, 11.0, PANEL, ch=0.1, name='panel_left'))
    out.append(B(F, 7.0, 10.0, 16.85, 17.6, 10.9, 13.0, PANEL, ch=0.1, name='panel_left_top'))
    out.append(B(F, 36.9, 37.15, 11.0, 17.0, 9.0, 12.0, PANEL, ch=0.06, name='panel_front'))
    # TS's dark bumpers: a bar in front of the dish on two brackets (TS: the bar at x 38..39, z 6..9, y 6..9; the
    # brackets at x 37), and one under the cab's front (TS: out to x 39, z 6..9)
    out.append(B(F, 37.9, 39.0, 6.0, 9.0, 6.0, 9.0, BUMPER, ch=0.22, name='bumper'))
    out.append(B(F, 36.6, 38.0, 6.0, 9.0, 6.0, 7.0, BUMPER, ch=0.1, name='bumper_base'))
    for ya, yb in ((6.1, 6.8), (8.2, 8.9)):
        out.append(B(F, 36.6, 38.0, ya, yb, 6.8, 8.0, BUMPER, ch=0.08, name='bumper_bracket'))
    out.append(B(F, 36.4, 39.0, 13.0, 17.0, 6.0, 9.0, BUMPER, ch=0.25, name='bumper_left'))
    # the mast at the back of the block (TS: x 4, y 13..15, up to 23)
    out.append(B(F, 3.9, 5.0, 13.0, 15.0, 14.9, 23.0, MAST, ch=0.15, name='mast'))
    # TS's yellow: lamps low on the front (TS: x 36, z 5, y 13..17), a lamp block at the back's left corner (TS: x 0..3,
    # y 13..17, z 2..7, its bottom row set in)
    out.append(B(F, 36.85, 37.2, 13.0, 16.9, 5.0, 6.0, LAMP, ch=0.08, name='front_lamps'))
    p = B(F, 0.0, 2.6, 13.0, 17.0, 2.0, 7.05, REARLAMP, ch=0.15, name='rear_lamp_block')
    p.cons.append(plane_q((-1.0, 0.0, -1.0), (0.0, 0.0, 3.0)))
    out.append(p)
    return out


def posed(m, Mx=np.eye(3)):
    """the parts posed (HVA frame 0) and turned by Mx (unit frame -> world): (parts, frames)."""
    R, t = F.pose()
    Rw, tw = Mx @ R, Mx @ t
    Mq = Rw @ np.diag(1.0 / F.sc)
    tq = tw + Rw @ F.mn
    return [p.moved(Rw, tw) for p in m], [(Mq, tq)] * len(m)
