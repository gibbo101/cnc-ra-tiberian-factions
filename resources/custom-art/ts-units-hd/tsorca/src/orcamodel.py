"""
orcamodel.py - the Orca Fighter (TS's [ORCA], TSORCA in the mod) rebuilt the way the Titan, the Wolverine, the Dropship
and the Mobile EMP Cannon are: TS's own voxel (ORCA.VXL, one section, posed by its HVA) is the blueprint for where every
part is and how big, each part modelled clean (flat plates, true slopes, round fans and tubes, bevelled edges) in TS's
colours - GDI's ochre, house colour where TS paints it (the fins, the fan rings, the pods' top panels; v3, Luke: not the
nose's sides) - with Westwood's art Luke sent (the TS intro's FMV, TS's cameo, a mod's render) as the guide to how
TS's parts read in HD: the faceted canopy over TS's cockpit, the fans' blades, the rocket tubes.

q: TS's voxel coordinates, continuous (voxel i spans i..i+1): x back to front 0..41, y from the aircraft's right (0) to
its left 0..25, z up 0..15; the section's local frame is min + q * scale (TS's), and its HVA (frame 0, identity) places
it in the unit's frame.  It is symmetric about q y 12.5 (TS's centre line); w below is the distance out from it.

Parts (TS's voxels in brackets, q units):
  pods       two rocket pods either side of the body [x 23..33, y 0..10 and 15..25, z 2..8], corners cut as TS's
             steps; on top a house-colour panel [x 24..33, y 3..9, z 8..9, its front lip down to z 7]; six rocket tubes
             in each front face [TS's 2 x 2 black squares: y 1..3, 4..6, 7..9; z 5..7 and 2..4]
  body       between the pods [y 10..15]: its belly sloping from the chin [z 0 at x 31] up to z 2.5 at x 23, its top
             z 9..10 with a spine [the top narrows to y 11..14 behind x 27], a rounded hump behind the cockpit [x 27..31,
             z 10..11], a grey hatch on the spine [x 25..27]; behind the pods the rear body [x 16..23, z 6..9] over a
             keel [down to z 3 at x 19..23]
  nose       the lower nose [x 32..38, y 9..16, z 1..5], its sides ochre (v3, Luke; TS paints them house colour), its
             black cheeks where it narrows to the tip [x 36..38], the tip [x 37..41, y 11..14, z 2..6], the chin
             [z 0..1.6]
  canopy     TS's cockpit is a dark pit in the nose's top [x 32..36, y 11..14] and a slit to the tip [x 36..39]: here a
             faceted glass canopy over it (the FMV's), its sill on TS's walls, its rear bulkhead TS's dark step up to the
             body's top [x 31..33]
  fans       two lift fans beside the body behind the pods [x 16..23, y 4..10 and 15..21, z 6..9]: house-colour rings,
             a hub and blades inside (TS: a dark hub and cross)
  boom       to the tail [x 6..17, y 11..14, z 7..9], a fairing under its front [x 13..17, z 6]
  tail       the tailplane [x 2..7, y 5..20, z 7..9], the tail fan's housing round its duct [centre x 4.5, r 1.5, its
             rim z 9..10], the fan inside, a cone behind [x 0..2]; the two fins at the tailplane's tips [y 4..5 and
             20..21, x 0..5, z 5..15], house colour
"""
import os, sys
from paths import HANDOFF
sys.path.insert(0, os.path.join(HANDOFF, 'renderer'))
import numpy as np
import vxl
import rc
from qparts import Frame, B, prism, hull, cyl

D = os.path.join(HANDOFF, '23-TSORCA', 'ts-original') + os.sep

(POD, COVER, TUBE, BODY, DECK, HUMP, HATCH, KEEL, NOSE, TIP, CHIN, CANOPY, BULKHEAD, FAN, HUB, BLADE, FLOOR, BOOM,
 STAB, HOUSING, FIN, CONE, ROCKET) = range(81, 104)
HOUSE = (COVER, FAN, FIN)                           # the parts that carry TS's house colour (v3, Luke: not the nose's
#                                                     sides, which TS paints house colour: ochre there)
RINGS = (FAN, HOUSING)                              # made of sectors: shaded with their true radial normals


def _load(name, i):
    s = vxl.read_vxl(D + name + '.VXL')[i]
    names, mats = vxl.read_hva(D + name + '.HVA')
    return Frame(s, mats[0, i])


FH = _load('ORCA', 0)
HYC = 12.5


def Y(w):
    return HYC + w


def mir(y0, y1):
    """the right-hand span (y0..y1, q) and its mirror on the left."""
    return (y0, y1), (2 * HYC - y1, 2 * HYC - y0)


def hullq(pts, comp, name):
    return hull(FH, pts, comp, name)


def mirror_pts(pts):
    return [(x, 2 * HYC - y, z) for (x, y, z) in pts]


def _circle(c_q, r, z, a):
    cl = FH.p((c_q[0], c_q[1], z))
    return tuple(FH.q(cl + r * np.array([np.cos(a), np.sin(a), 0.0])))


def ring_sectors(c_q, prof, n, comp, name, a_off=0.0):
    """a ring round c_q (q x, y) as n convex sectors; prof: its section as (radius (local units), q z) points."""
    out = []
    for i in range(n):
        a0, a1 = a_off + 2 * np.pi * i / n, a_off + 2 * np.pi * (i + 1) / n
        pts = [_circle(c_q, r, z, a) for (r, z) in prof for a in (a0, a1)]
        out.append(hull(FH, pts, comp, name))
    return out


# ---------------------------------------------------------------- the rocket pods
# TS (y 0 side): z 2 x 24..31, z 3 x 24..32, z 4..5 x 23..32, z 6 x 24..32, z 7 x 25..31: a box with its corners cut
POD_PROFILE = [(24.0, 2.0), (32.55, 2.0), (33.0, 2.45), (33.0, 7.45), (32.45, 8.0), (25.3, 8.0), (23.0, 5.8),
               (23.0, 4.15)]
TUBE_Y = (2.0, 5.0, 8.0)                            # the right pod's tubes (the left's mirrored): TS's 2-voxel squares
TUBE_Z = (6.05, 3.35)                               # TS's rows (z 5..7 and 2..4), the lower a little up to sit on the face
TUBE_R = 0.92                                       # the tube's rim; its bore BORE_R
BORE_R = 0.72
COVER_PTS = [(24.3, 4.1), (25.7, 3.0), (33.0, 3.0), (33.0, 8.7), (24.3, 8.7)]   # x, y (right pod)


def pod_parts():
    out = []
    (r0, r1), (l0, l1) = mir(0.0, 10.0)
    out.append(prism(FH, 1, POD_PROFILE, r0, r1, POD, ch=0.4, name='pod', ends=(True, False)))
    out.append(prism(FH, 1, POD_PROFILE, l0, l1, POD, ch=0.4, name='pod', ends=(False, True)))
    for s in (1, -1):
        pts = [(x, y if s > 0 else 2 * HYC - y) for (x, y) in COVER_PTS]
        if s < 0:
            pts = pts[::-1]
        out.append(prism(FH, 2, pts, 7.95, 9.0, COVER, ch=0.22, name='pod_cover', ends=(False, True)))
        ya, yb = (3.0, 8.7) if s > 0 else (2 * HYC - 8.7, 2 * HYC - 3.0)
        out.append(B(FH, 32.1, 33.05, ya, yb, 7.05, 9.0, COVER, ch=(0.2, 0.0, 0.2), name='pod_cover_lip'))
        for yt in TUBE_Y:
            yy = yt if s > 0 else 2 * HYC - yt
            for zt in TUBE_Z:
                out.append(cyl(FH, (32.85, yy, zt), (33.16, yy, zt), TUBE_R, TUBE, 'rocket_tube'))
    return out


# ---------------------------------------------------------------- the body
def body_parts():
    out = []
    # the forward body between the pods: its belly from the chin (z 0 at x 31.5) up to z 2.55 at x 22.5 (TS: z 2 at
    # x 24..27, z 1 at x 28..30, z 0 at x 31..36)
    out.append(prism(FH, 1, [(22.4, 2.6), (31.6, 0.0), (32.6, 0.0), (32.6, 9.0), (22.4, 9.0)], 10.0, 15.0, BODY,
                     ch=0.3, name='body'))
    # its top: TS's spine (y 11..14 at z 10 from x 23) widening to the full top at x 27, flat to the cockpit; its
    # front sloping down behind the canopy (TS's step: z 10 at x 31, 9 at x 32, 7 at x 33) - the canopy's bulkhead
    out.append(hullq([(22.5, 10.0, 8.8), (22.5, 15.0, 8.8), (22.5, 10.0, 9.0), (22.5, 15.0, 9.0), (22.5, 11.1, 10.0),
                      (22.5, 13.9, 10.0), (27.0, 10.0, 10.0), (27.0, 15.0, 10.0), (31.2, 10.0, 10.0),
                      (31.2, 15.0, 10.0), (31.2, 10.0, 8.8), (31.2, 15.0, 8.8)], DECK, 'deck'))
    out.append(hullq([(31.0, 10.0, 8.8), (31.0, 15.0, 8.8), (31.0, 10.0, 10.0), (31.0, 15.0, 10.0),
                      (33.2, 10.0, 7.0), (33.2, 15.0, 7.0), (33.2, 10.0, 6.4), (33.2, 15.0, 6.4)], BULKHEAD,
                     'bulkhead'))
    # the hump behind the cockpit (TS: x 27..31, y 11..13, z 10..11), rounded
    out.append(hullq([(27.0, 11.4, 10.0), (27.0, 13.6, 10.0), (27.4, 11.2, 10.7), (27.4, 13.8, 10.7),
                      (27.9, 11.6, 11.05), (27.9, 13.4, 11.05), (30.6, 11.6, 11.05), (30.6, 13.4, 11.05),
                      (31.1, 11.2, 10.6), (31.1, 13.8, 10.6), (31.4, 11.3, 10.0), (31.4, 13.7, 10.0)], HUMP, 'hump'))
    # TS's grey hatch on the spine (x 25..27, y 12..13 at the top): a small raised plate
    out.append(B(FH, 25.0, 27.0, 11.75, 13.25, 9.8, 10.22, HATCH, ch=0.12, name='spine_hatch'))
    # the rear body behind the pods, between the fans (TS: x 17..22, z 6..8 at y 10..14)
    out.append(B(FH, 16.0, 22.8, 10.0, 15.0, 6.3, 9.0, BODY, ch=0.3, name='rear_body'))
    # its keel (TS: z 3 at x 19..23, z 5 at x 18, z 6 at x 17; 3 voxels wide at x 19..20, 5 at x 21..22)
    out.append(hullq([(16.3, 11.1, 6.5), (16.3, 13.9, 6.5), (16.5, 11.1, 6.2), (16.5, 13.9, 6.2), (18.6, 11.0, 3.3),
                      (18.6, 14.0, 3.3), (22.6, 10.2, 2.6), (22.6, 14.8, 2.6), (22.6, 10.2, 6.5), (22.6, 14.8, 6.5),
                      (18.6, 11.0, 6.5), (18.6, 14.0, 6.5)], KEEL, 'keel'))
    return out


# ---------------------------------------------------------------- the nose
def nose_parts():
    out = []
    # the lower nose (TS: y 9..15, z 1..4 at x 33..37), its sides house colour, narrowing at its front to the tip:
    # TS's black cheeks (x 36..37, y 10 and 14, z 1..4)
    top, bot = 5.0, 1.35
    pts = []
    for z, dx in ((top, 0.0), (bot, -0.9)):
        pts += [(32.4, 9.0, z), (36.2 + dx, 9.0, z), (38.3 + dx, 11.0, z), (38.3 + dx, 14.0, z), (36.2 + dx, 16.0, z),
                (32.4, 16.0, z)]
    out.append(hullq(pts, NOSE, 'nose_lower'))
    # the chin under it (TS: z 0 at x 31..36, y 10..14)
    out.append(B(FH, 30.8, 36.9, 10.0, 15.0, 0.0, 1.7, CHIN, ch=0.45, name='chin'))
    # the tip (TS: x 37..40, y 11..13, z 2..5): a blunt snout
    out.append(hullq([(37.4, 11.0, 1.7), (37.4, 14.0, 1.7), (37.4, 11.0, 5.6), (37.4, 14.0, 5.6),
                      (40.3, 11.0, 2.0), (40.3, 14.0, 2.0), (40.3, 11.0, 5.2), (40.3, 14.0, 5.2),
                      (41.0, 11.4, 2.4), (41.0, 13.6, 2.4), (41.0, 11.4, 4.8), (41.0, 13.6, 4.8)], TIP, 'nose_tip'))
    # the upper nose round the canopy (TS: the cockpit's walls, y 10 and 14 at z 5..7, x 33..36)
    out.append(hullq([(32.4, 10.0, 4.8), (32.4, 15.0, 4.8), (32.4, 10.0, 6.5), (32.4, 15.0, 6.5),
                      (38.4, 10.6, 4.8), (38.4, 14.4, 4.8), (38.4, 10.6, 5.6), (38.4, 14.4, 5.6)], NOSE, 'nose_upper'))
    return out


# the canopy: faceted glass (the FMV's), its sill on TS's walls (z 6.5 at x 33 to 5.6 at x 38), its ridge half a voxel
# over TS's nose (TS: the pit open to z 7), down to the tip's top
CANOPY_PTS = [(32.9, 10.35, 6.4), (32.9, 14.65, 6.4), (32.9, 11.5, 7.55), (32.9, 13.5, 7.55),
              (35.6, 10.45, 6.1), (35.6, 14.55, 6.1), (35.6, 11.65, 7.25), (35.6, 13.35, 7.25),
              (39.4, 11.45, 5.45), (39.4, 13.55, 5.45), (39.6, 11.9, 5.75), (39.6, 13.1, 5.75),
              (32.9, 10.35, 5.6), (32.9, 14.65, 5.6), (39.4, 11.45, 4.9), (39.4, 13.55, 4.9)]


def canopy_parts():
    return [hullq(CANOPY_PTS, CANOPY, 'canopy')]


# ---------------------------------------------------------------- the lift fans
FAN_C = ((19.6, 7.15), (19.6, 2 * HYC - 7.15))      # TS: rings x 16..23, y 4..10 (and 15..21)
FAN_RO, FAN_RI = 3.2, 2.3
FAN_Z = (6.0, 9.0)
FAN_PROF = [(FAN_RI, 6.0), (FAN_RO, 6.0), (FAN_RO, 8.6), (FAN_RO - 0.28, 9.0), (FAN_RI + 0.2, 9.0), (FAN_RI, 8.75)]
N_BLADES = 9


def fan_rotor(c, r_hub, r_tip, zc, n, comp_hub, comp_blade, name, a_off=0.0, pitch=0.28, chord=0.34, thick=0.07):
    out = []
    out.append(cyl(FH, (c[0], c[1], zc - 0.75), (c[0], c[1], zc + 0.55), r_hub, comp_hub, name + '_hub'))
    out.append(rc.Part([rc.Ellip(FH.p((c[0], c[1], zc + 0.55)), np.eye(3), np.array([r_hub, r_hub, 0.42]) * FH.sc),
                        rc.Plane((0, 0, -1.0), -FH.p((0, 0, zc + 0.55))[2])], comp_hub, name + '_spinner',
                       sphere=(FH.p((c[0], c[1], zc + 0.55)), r_hub + 0.5)))
    for i in range(n):
        a = a_off + 2 * np.pi * i / n
        pts = []
        for rr, ch in ((r_hub * 0.85, chord * 1.15), (r_tip, chord)):
            da = ch / rr
            for sgn in (-1, 1):
                p = _circle(c, rr, zc + sgn * pitch * 0.5, a + sgn * da)
                for t in (-thick, thick):
                    pts.append((p[0], p[1], p[2] + t))
        out.append(hull(FH, pts, comp_blade, name + '_blade'))
    return out


def fan_parts():
    out = []
    for k, c in enumerate(FAN_C):
        out += ring_sectors(c, FAN_PROF, 28, FAN, 'fan_ring')
        out += fan_rotor(c, 0.62, FAN_RI + 0.04, 7.55, N_BLADES, HUB, BLADE, 'fan', a_off=0.3 + 0.5 * k)
        # the duct's floor under the blades: dark (TS fills its rings' floor round a dark hub)
        out.append(cyl(FH, (c[0], c[1], 6.05), (c[0], c[1], 6.4), FAN_RI + 0.05, FLOOR, 'fan_floor'))
    return out


# ---------------------------------------------------------------- the boom and the tail
TAIL_C = (4.5, 12.5)                                 # the tail fan's duct (TS: x 3..5, y 11..13 open top to bottom)
TAIL_RI, TAIL_RO = 1.55, 3.05
FIN_PROFILE = [(0.25, 5.0), (3.0, 5.0), (5.0, 8.0), (5.0, 9.0), (2.4, 15.0), (0.25, 15.0)]   # x, z (TS: x 0..5)
FIN_Y = (3.75, 5.2)                                 # TS: 2 voxels thick, y 3..5 at its ends, 4..6 between


def tail_parts():
    out = []
    # the boom (TS: y 11..13, z 7..8, x 6..16), octagonal, and the fairing under its front (TS: z 6 at x 13..15)
    oct_ = [(11.0, 7.4), (11.4, 7.0), (13.6, 7.0), (14.0, 7.4), (14.0, 8.6), (13.6, 9.0), (11.4, 9.0), (11.0, 8.6)]
    out.append(prism(FH, 0, oct_, 6.6, 17.0, BOOM, name='boom'))
    out.append(B(FH, 12.8, 16.8, 11.2, 13.8, 5.95, 7.6, BOOM, ch=0.45, name='boom_fairing'))
    # the tailplane (TS: x 2..6, y 5..19, z 7..8), its leading corners cut (TS's steps at y 5..6 and 18..19)
    out.append(prism(FH, 2, [(1.6, 4.85), (5.3, 4.85), (7.0, 6.6), (7.0, 18.4), (5.3, 20.15), (1.6, 20.15)],
                     6.98, 9.02, STAB, ch=0.3, name='tailplane'))
    # the tail fan's housing round its duct (TS: the rim at z 9, x 2..6, y 9..15), and the fan in it
    prof = [(TAIL_RI, 7.0), (TAIL_RO, 7.0), (TAIL_RO, 9.55), (TAIL_RO - 0.35, 10.0), (TAIL_RI + 0.25, 10.0),
            (TAIL_RI, 9.7)]
    out += ring_sectors(TAIL_C, prof, 22, HOUSING, 'tail_housing')
    out += fan_rotor(TAIL_C, 0.45, TAIL_RI + 0.03, 8.5, 6, HUB, BLADE, 'tail_fan', a_off=0.2, pitch=0.22, chord=0.24)
    out.append(cyl(FH, (TAIL_C[0], TAIL_C[1], 7.05), (TAIL_C[0], TAIL_C[1], 7.35), TAIL_RI + 0.05, FLOOR, 'tail_floor'))
    # the cone behind it (TS: x 0..1, y 11..13, z 7..9)
    out.append(hullq([(1.8, 10.2, 7.0), (1.8, 14.8, 7.0), (1.8, 10.4, 9.7), (1.8, 14.6, 9.7),
                      (0.1, 11.1, 7.2), (0.1, 13.9, 7.2), (0.1, 11.3, 9.5), (0.1, 13.7, 9.5)], CONE, 'tail_cone'))
    # the fins at the tailplane's tips (TS: x 0..4, z 5..14, house colour), raked back above and below it
    for (y0, y1), ends in zip(mir(*FIN_Y), ((True, True), (True, True))):
        out.append(prism(FH, 1, FIN_PROFILE, y0, y1, FIN, ch=0.28, name='fin', ends=ends))
    return out


def model():
    return {'hull': pod_parts() + body_parts() + nose_parts() + canopy_parts() + fan_parts() + tail_parts()}


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
