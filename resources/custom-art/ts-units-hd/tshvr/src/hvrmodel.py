"""
hvrmodel.py - the Hover MLRS (TS's [HVR], TSHVR in the mod) rebuilt the way the Titan, the Wolverine, the War Factory
and the Disruptor are: TS's own voxels (HVR.VXL the hull, HVRTUR.VXL the missile rack) as the blueprint for where every
part is and how big, each part modelled clean (flat plates, true slopes, round tubes, bevelled edges) in TS's colours -
GDI's ochre pontoons, the grey deck between them, the house-colour cockpit frame and missile pods - with Westwood's art
of the Hover MLRS (and the mods' renders Luke sent) where TS's voxels have the part: the pods' missile tubes, the ducts
in the pontoons' fronts, the canopy's glass, the hover fans.

Each section has its own frame: q, continuous voxel coordinates (voxel i spans i..i+1), x back to front, y from the
unit's right (0) to its left, z up; the section's local frame is min + q * scale (TS's), and its HVA (frame 0) places
it in the unit's frame.  The hull is 38 x 20 x 8, the rack 12 x 19 x 19 (its lowest five layers, the base ring that
sits down in the hull, is left off: Luke seats the rack low on the hull's back, its pods on the back deck).
"""
import os, sys
from paths import HANDOFF
sys.path.insert(0, os.path.join(HANDOFF, 'renderer'))
import numpy as np
import vxl
import rc
from qparts import Frame, B, prism, hull, cyl

D = os.path.join(HANDOFF, '07-TSHVR', 'ts-original') + os.sep

(OCHRE, KHAKI, SKIRT, FAN, DUCT, COWL, LAMP, BUMPER, DECK_D, DECK, DECK_L, SLOT, HOUSE_C, GLASS, POD, COLLAR,
 FACE, TUBE, TIP, MAST, MOUNT, TURNTABLE) = range(81, 103)
HOUSE = (HOUSE_C, POD)


def _load(name, i):
    s = vxl.read_vxl(D + name + '.VXL')[i]
    names, mats = vxl.read_hva(D + name + '.HVA')
    return Frame(s, mats[0, i])


FH = _load('HVR', 0)
FR = _load('HVRTUR', 0)
HYC = 10.0                                          # the hull's centre line (q y)

# where the rack sits (Luke: on the hull's back, centred across it, almost touching its back end, on a circular pad with
# a support holding the pods up, as the Disruptor's turret): at HVRTUR.HVA's height (TS's ring then stands on the back
# deck, z 7), moved RACK_SHIFT across onto the hull's centre line (TS's hull runs 0.2 voxels left of its HVA origin),
# RACK_AFT voxels aft (TS's own TurretOffset=-64 is 8.14)
RACK_SHIFT = np.array([0.0, 0.20, 0.0])             # the pivot onto the hull's centre line (q y 10)
RACK_AFT = 12.66
PIVOT = (5.88, 9.25)                                # the rack's pivot (q x, y): the support's middle, the pods' middle


def rack_unit(qr, shift=None):
    """a rack q point in the unit's frame, the rack at its HVA place moved by shift (RACK_SHIFT)."""
    Rr, tr = FR.pose()
    return Rr @ FR.p(qr) + tr + (RACK_SHIFT if shift is None else shift)


def rack_to_hull(qr):
    """a rack q point -> hull q, the rack seated as the game draws it (RACK_SHIFT, RACK_AFT aft)."""
    Rh, th = FH.pose()
    u = rack_unit(qr) - np.array([RACK_AFT, 0.0, 0.0])
    return FH.q(np.linalg.inv(Rh) @ (u - th))


# the rack's frames turn it about its pivot, standing on the unit's position (FRAME_SHIFT from its HVA place); the game
# draws rack frame 32 + g with that point on the pad's centre, SEAT_U in the unit's frame (x forward, y left) of the
# hull's facing: 12.54 voxels aft of the unit's position and 0.20 to its left
PIVOT_U = rack_unit((PIVOT[0], PIVOT[1], 0.0))[:2]
FRAME_SHIFT = RACK_SHIFT - np.array([PIVOT_U[0], PIVOT_U[1], 0.0])
SEAT_U = np.array([PIVOT_U[0] - RACK_AFT, PIVOT_U[1]])


# the pad the rack turns on (Luke: a circular pad between the pontoons, the rack on it as the Disruptor's turret on its
# base; only the pods move when it fires): part of the hull, so it stays put and is drawn in depth with the deck; under
# the rack's pivot, on the back deck (z 7), its rim 4.45 out (TS's ring, 6 out, would lie over the pontoons), a step on
# top (3.8 out) the support stands on
PAD_C = rack_to_hull((PIVOT[0], PIVOT[1], 0.0))[:2]                 # (q x, y): about (6.43, 10.0)
PAD_Z = (6.9, rack_to_hull((0, 0, 1.25))[2], rack_to_hull((0, 0, 1.7))[2])    # its foot (in the deck), rim top, step top
PAD_R = (4.45, 4.0)                                 # the rim's and the step's radii (local units: true circles)


def mirror(y0, y1, c=HYC):
    return (y0, y1), (2 * c - y1, 2 * c - y0)


# ---------------------------------------------------------------- the hull
# two pontoons (TS: y 0..5 and 15..20, x 0..38): ochre, their tops at z 7 over the back (x 0..25) with a raised hump
# (TS: x 13..25, z 8), stepping down to z 6 over the front; their bottoms at z 2, the back end rising (TS: z 3..4 at
# x 0..4); a rubber skirt under the front (TS's red-brown, x 30..36, z 1..2).  TS has a ledge at z 7 in front of the hump
# (x 25..27): it comes down to the front's z 6 so the hump's front face is two voxels tall, for its vent (Luke: the
# vents further back near the pods, Westwood's and the mods')
PONT_BACK = [(0.0, 4.0), (1.0, 3.0), (5.0, 2.0), (25.2, 2.0), (25.2, 7.0), (0.0, 7.0)]
PONT_FRONT = [(25.2, 2.0), (35.3, 2.0), (35.3, 6.0), (25.2, 6.0)]
# each pontoon's front end (TS: x 35..38), as Westwood's art and the mods' have it (Luke: the vent angles): its face
# undercut, leaning back from the top's front edge (TS's front, x 38) to the bottom (TS: x 36 at z 2), a big intake in it
# (TS's dark front and its opening under the lip) between two walls, framed above and below, louvres across it (the
# middle one at TS's khaki lip, z 4..5)
FACE_X0, FACE_K = 36.3, 0.425                        # the face: x = FACE_X0 + FACE_K (z - 2), so x 38.0 at the top (z 6)
INTAKE_Y = (0.75, 3.75)                             # the intake's sides, across the pontoon from its outer side
INTAKE_Z = (2.55, 5.35)                             # its foot and head on the face
INTAKE_D = 0.5                                      # how far its back is set in from the face
LOUVRES_Z = (3.2, 3.95, 4.7)


def face_x(z):
    return FACE_X0 + FACE_K * (z - 2.0)


HUMP_VENT = (0.7, 6.22, 7.8)                        # the hump vent's inset from the hump's sides, its foot and top (q)


def across(y0, y1, a, b):
    """a span across a pontoon measured from its outer side (y0 < HYC: the right pontoon) -> absolute q y."""
    return (y0 + a, y0 + b) if y0 < HYC else (y1 - b, y1 - a)


def pontoons():
    out = []
    for (y0, y1) in mirror(0.0, 5.0):
        out.append(prism(FH, 1, PONT_BACK, y0, y1, OCHRE, ch=0.25, name='pontoon'))
        out.append(prism(FH, 1, PONT_FRONT, y0, y1, OCHRE, ch=0.25, name='pontoon'))
        out.append(B(FH, 13.0, 25.2, y0 + 0.15, y1 - 0.15, 6.8, 8.0, OCHRE, ch=0.3, name='pontoon_hump'))
        # the front end: the intake's two walls, the frames above and below it, its dark back, the louvres across it
        ia, ib = across(y0, y1, *INTAKE_Y)
        z0, z1 = INTAKE_Z
        out.append(prism(FH, 1, [(35.2, z1), (face_x(z1), z1), (face_x(6.0), 6.0), (35.2, 6.0)], y0, y1, OCHRE,
                         ch=0.2, name='front_top'))
        for (wa, wb) in ((y0, ia), (ib, y1)):
            out.append(prism(FH, 1, [(35.2, 2.0), (face_x(2.0), 2.0), (face_x(z1), z1), (35.2, z1)], wa, wb, OCHRE,
                             ch=0.12, name='front_wall'))
        out.append(prism(FH, 1, [(35.2, 2.0), (face_x(2.0), 2.0), (face_x(z0), z0), (35.2, z0)], ia, ib, OCHRE,
                         ch=0.1, name='intake_frame'))
        out.append(prism(FH, 1, [(35.0, z0), (face_x(z0) - INTAKE_D, z0), (face_x(z1) - INTAKE_D, z1), (35.0, z1)],
                         ia, ib, DUCT, name='intake'))
        for zc in LOUVRES_Z:
            xb, xf = face_x(zc) - INTAKE_D - 0.05, face_x(zc) - 0.04
            out.append(prism(FH, 1, [(xb, zc + 0.09), (xf, zc - 0.11), (xf, zc - 0.01), (xb, zc + 0.19)], ia + 0.02,
                             ib - 0.02, KHAKI, name='louvre'))
        # the vent in the hump's front face (Westwood's raised blocks by the pods and the mods' have one: Luke): a dark
        # slot in a raised frame, louvres across it
        va, vb = y0 + HUMP_VENT[0], y1 - HUMP_VENT[0]
        z0, z1 = HUMP_VENT[1], HUMP_VENT[2]
        out.append(B(FH, 25.0, 25.27, va + 0.2, vb - 0.2, z0 + 0.18, z1 - 0.18, DUCT, name='hump_vent'))
        for (za, zb) in ((z0, z0 + 0.18), (z1 - 0.18, z1)):
            out.append(B(FH, 25.0, 25.5, va, vb, za, zb, OCHRE, ch=0.06, name='vent_frame'))
        for (ya, yb) in ((va, va + 0.2), (vb - 0.2, vb)):
            out.append(B(FH, 25.0, 25.5, ya, yb, z0 + 0.18, z1 - 0.18, OCHRE, ch=0.06, name='vent_frame'))
        # the skirt under the front (TS's red-brown) and the hover fans hanging under the outer half (TS: two black
        # blocks, x 17..19 and 21..23)
        out.append(prism(FH, 1, [(29.4, 2.05), (35.4, 2.05), (35.0, 1.1), (30.2, 1.1)], y0 + 0.2, y1 - 0.2, SKIRT,
                         ch=0.1, name='skirt'))
        yo = (y0 + 0.1, y0 + 2.1) if y0 < HYC else (y1 - 2.1, y1 - 0.1)
        for xa in (17.0, 21.0):
            out.append(B(FH, xa, xa + 2.0, yo[0], yo[1], 0.0, 2.2, FAN, ch=0.15, name='hover_fan'))
        # TS's light-pink voxels: a lamp bar across each pontoon's back top edge, a lamp at its front outer corner
        out.append(B(FH, -0.06, 0.35, y0 + 0.4, y1 - 0.4, 6.15, 6.85, LAMP, ch=0.05, name='tail_lamp'))
        yl = (y0 + 0.35, y0 + 1.25) if y0 < HYC else (y1 - 1.25, y1 - 0.35)
        out.append(B(FH, 35.0, 35.8, yl[0], yl[1], 5.95, 6.25, LAMP, ch=0.04, name='head_lamp'))
    return out


# the body between the pontoons (TS: y 5..15): a blue-grey bar across its back (TS: x 1, z 5), the dark engine deck
# (TS: x 2..9, up to z 7), a slot across (TS: x 9, down to z 4) under a base plate for the rack's pad, flush with the
# engine deck (x 8.4..12.9: the rack sits on the back, Luke), the grey mid deck (TS: x 10..30, z 6),
# the cockpit on its front right (TS: x 22..31, y 5..10: a house-colour frame round a dark glass top, a bar across it
# at x 25..27, z 8), TS's light grey plate beside it (TS: x 22..30, y 10..15), the front stepping down to z 5 (TS: x 30
# ..34) and a blue-grey bar across the front (TS: x 34, z 4..5)
CP_X, CP_Y = (22.0, 31.2), (5.0, 10.0)               # the cockpit (q x, y)


def body():
    out = [B(FH, 0.9, 2.1, 5.0, 15.0, 4.9, 6.1, BUMPER, ch=0.15, name='rear_bar'),
           B(FH, 1.9, 9.0, 5.0, 15.0, 3.4, 7.0, DECK_D, ch=0.2, name='engine_deck'),
           B(FH, 8.6, 10.4, 5.0, 15.0, 2.4, 4.0, SLOT, name='slot'),
           B(FH, 8.4, 12.9, 5.0, 15.0, 4.0, 7.0, DECK, ch=0.15, name='turret_base'),
           B(FH, 10.0, 30.6, 5.0, 15.0, 2.8, 6.0, DECK, ch=0.15, name='mid_deck'),
           B(FH, 30.0, 34.2, 5.0, 15.0, 1.6, 5.0, DECK, ch=0.2, name='front_deck'),
           B(FH, 33.8, 35.0, 5.0, 15.0, 3.0, 5.2, BUMPER, ch=0.15, name='front_bar'),
           B(FH, 21.6, 30.2, 10.4, 14.6, 5.8, 6.25, DECK_L, ch=0.08, name='front_plate')]
    # the cockpit: its frame in house colour, the canopy on it facing forward (TS: dark over the top, x 23..30, and down
    # over its front edge; house colour at its back, x 22): its glass from the bar forward with a steep windscreen, a
    # house-colour fairing behind the bar (Luke: no window behind it; TS's dark top runs back to x 23); the bar across it
    # (TS: x 25..27, z 8)
    (x0, x1), (y0, y1) = CP_X, CP_Y
    out.append(B(FH, x0, x1, y0, y1, 5.6, 6.6, HOUSE_C, ch=0.15, name='cockpit'))
    pts = []
    for (xa, xb, ya, yb, zz) in ((26.55, x1 - 0.6, y0 + 0.35, y1 - 0.35, 6.5), (26.65, x1 - 1.35, y0 + 0.95, y1 - 0.95, 7.35)):
        pts += [(xa, ya, zz), (xb, ya, zz), (xa, yb, zz), (xb, yb, zz)]
    out.append(hull(FH, pts, GLASS, 'canopy'))
    pts = []
    for (xa, xb, ya, yb, zz) in ((x0 + 0.45, 26.7, y0 + 0.35, y1 - 0.35, 6.5), (23.55, 26.7, y0 + 0.95, y1 - 0.95, 7.35)):
        pts += [(xa, ya, zz), (xb, ya, zz), (xa, yb, zz), (xb, yb, zz)]
    out.append(hull(FH, pts, HOUSE_C, 'canopy_fairing'))
    out.append(B(FH, 25.2, 26.8, y0 + 0.1, y1 - 0.1, 6.5, 7.75, HOUSE_C, ch=0.15, name='canopy_bar'))
    out += pad()
    return out


def pad():
    (cx, cy), (z0, z1, z2) = PAD_C, PAD_Z
    rq = lambda r: r / FH.r(1.0, 2)
    return [cyl(FH, (cx, cy, z0), (cx, cy, z1), rq(PAD_R[0]), TURNTABLE, name='pad'),
            cyl(FH, (cx, cy, z1 - 0.05), (cx, cy, z2), rq(PAD_R[1]), TURNTABLE, name='pad_top')]


def hull_parts():
    return pontoons() + body()


# ---------------------------------------------------------------- the rack
# two missile pods (TS: y 0..7 and 11..19, x 0..12, z 5..9) in house colour, an ochre band across their backs (TS: x 0,
# z 7..9), an ochre collar round their fronts (TS: x 10..11) and the dark faces in front of it (TS: x 11..12, z 6..9)
# with Westwood's two rows of four missile tubes; an antenna at each pod's back outer corner (TS: x 2..4, z 9..19); a
# dark block between the pods at their feet (TS: x 3..7, y 7..12, z 5..6)
POD_Y = ((-0.15, 6.95), (11.55, 18.65))            # centred on the pivot (TS: 0..7 and 11..19)
POD_X, POD_Z = (0.0, 10.1), (5.0, 9.0)
TUBE_Z = (6.85, 8.2)
TUBE_R = 0.52


def tube_ys(y0, y1):
    return list(np.linspace(y0 + 0.95, y1 - 0.95, 4))


def rack_parts():
    out = []
    for (y0, y1) in POD_Y:
        out.append(B(FR, POD_X[0], POD_X[1], y0, y1, POD_Z[0], POD_Z[1], POD, ch=0.22, name='pod'))
        out.append(B(FR, 9.9, 11.05, y0 - 0.12, y1 + 0.12, 4.88, 9.12, COLLAR, ch=0.15, name='collar'))
        out.append(B(FR, 10.9, 11.75, y0 + 0.12, y1 - 0.12, 5.75, 9.0, FACE, ch=0.1, name='face'))
        for zc in TUBE_Z:
            for yc in tube_ys(y0, y1):
                out.append(cyl(FR, (11.6, yc, zc), (11.95, yc, zc), TUBE_R, TUBE, name='tube'))
                out.append(cyl(FR, (11.7, yc, zc), (12.05, yc, zc), TUBE_R * 0.62, TIP, name='missile'))
        # the antenna: a mount on the pod's back outer corner, the mast
        ym = y0 + 0.75 if y0 < 9.25 else y1 - 0.75
        out.append(B(FR, 2.2, 3.8, ym - 0.55, ym + 0.55, 8.8, 9.6, MAST, ch=0.1, name='antenna_mount'))
        out.append(cyl(FR, (3.0, ym, 9.5), (3.0, ym, 19.0), 0.32, MAST, name='antenna'))
    out.append(B(FR, 3.0, 7.2, 6.75, 11.75, 4.7, 6.1, MOUNT, ch=0.15, name='mount'))
    out += pedestal()
    return out


# the support (TS: HVRTUR's five lowest layers - a ring round the pivot, 6 voxels out, two voxels high, and two legs from
# it up under the pods' inner sides): a column under the mount and a leg under each pod's inner half, standing on the
# hull's pad (pad(): the pad itself is the hull's, so it doesn't move when the pods do), all inside its top step's rim
# at every turn
def pedestal():
    cx, cy = PIVOT
    out = [B(FR, cx - 2.28, cx + 2.32, cy - 1.85, cy + 1.85, 1.7, 5.2, MOUNT, ch=0.15, name='column')]
    for (y0, y1) in ((cy - 3.65, cy - 2.35), (cy + 2.35, cy + 3.65)):
        out.append(B(FR, cx - 1.7, cx + 1.7, y0, y1, 1.7, 5.1, MOUNT, ch=0.12, name='leg'))
    return out


def model():
    return {'hull': hull_parts(), 'rack': rack_parts()}


SECTIONS = {'hull': FH, 'rack': FR}


def posed(m, which, Mx=np.eye(3), shift=None):
    """the parts of the named sections posed (HVA frame 0, plus shift[section] in the unit's frame if given) and turned by
    Mx (unit frame -> world): (parts, frames, owner)."""
    parts, frames, owner = [], [], []
    shift = shift or {}
    for k in which:
        F = SECTIONS[k]
        R, t = F.pose()
        t = t + np.asarray(shift.get(k, np.zeros(3)), float)
        Rw, tw = Mx @ R, Mx @ t
        Mq = Rw @ np.diag(1.0 / F.sc)
        tq = tw + Rw @ F.mn
        for p in m[k]:
            parts.append(p.moved(Rw, tw)); frames.append((Mq, tq)); owner.append(k)
    return parts, frames, np.array(owner)
