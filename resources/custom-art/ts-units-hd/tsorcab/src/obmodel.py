"""
obmodel.py - the Orca Bomber (TS's [ORCAB], TSORCAB in the mod) rebuilt the way the Titan, the Wolverine, the Dropship
and the Orca Fighter are: TS's own voxel (ORCAB.VXL, one section, posed by its HVA) is the blueprint for where every
part is and how big, each part modelled clean (flat plates, true slopes, round fans and booms, bevelled edges) in TS's
colours - GDI's ochre, TS's brown fan rims, house colour where TS paints it (the fins, the panels on the body's top) -
with the renders Luke sent as the guide to how TS's parts read in HD: the faceted glass over TS's blue glazed nose,
the fans' blades, the segmented booms, bombs in TS's black bays.

q: TS's voxel coordinates, continuous (voxel i spans i..i+1): x back to front 0..44, y from the aircraft's right (0) to
its left 0..40, z up 0..16; the section's local frame is min + q * scale (TS's), and its HVA (frame 0, identity) places
it in the unit's frame.  Symmetric about q y 20 (the HVA origin's; TS's fans and booms are centred on it, its nose,
spine and tail fan half a voxel to the right); w below is the distance out from it.

Parts (TS's voxels in brackets, q units):
  fans       two big lift fans at the wingtips [x 20..32, y 0..11 and 29..40]: TS's brown rims [z 6..10, r 5.75],
             light grey blades and a dark hub inside, the duct's black throat under the rim [z 4..6]
  body       between them [x 18..35, y 10..30, z 3..10]: its back sloping down to x 18, its front blocks either side of
             the nose sloping down to z 8 at the front [x 28..35]; TS's two rows of black bays in their front faces
             [z 3..5 and 6..8]; the spine [y 18..22, z 10..11, x 25..35] up to the canopy; TS's house-colour panels on
             the top either side of the spine [y 15..18 and 22..25, x 23..33] and strips along its outer edges
             [y 11..13 and 27..29]; two small blocks on the top by the booms [x 26..28, z 10..11]
  nose       the keel under the canopy [x 21..44, y 17..22]: its bottom from z 3 at x 21 down to z 0 at x 33..40 and up
             to z 3.5 at the tip; the canopy - TS's blue glazed nose [x 35..44, z 4..10] - and TS's red lamp behind it
             [x 34..36, y 18..21, z 9..11]: a beacon, a red glass dome on the spine's front end (v3)
  booms      two [y 12..15 and 25..28, z 7.6..10, x 0..20], a voxel wider at their roots [x 12..20], TS's dark band at
             x 15..18
  tail       the tail fan's housing between the booms [centre x 6, r 3.6, its rim at z 10..11] with the fan in it, the
             plate joining it to the booms [x 3..9, z 8..10], a keel through it [x 1..12]; the two fins on the booms'
             ends [x 1..6, z 6..16], canted out at the top, house colour
"""
import os, sys
from paths import HANDOFF
sys.path.insert(0, os.path.join(HANDOFF, 'renderer'))
import numpy as np
import vxl
import rc
from qparts import Frame, B, prism, hull, cyl

D = os.path.join(HANDOFF, '24-TSORCAB', 'ts-original') + os.sep

(RIM, THROAT, BLADE, HUB, BODY, SPINE, PANEL, BLOCK, BAY, BOMB, KEEL, CANOPY, LAMP, BOOM, COLLAR, STAB, HOUSING,
 FIN, FLOOR, RACK) = range(81, 101)
HOUSE = (PANEL, FIN)                                # the parts that carry TS's house colour
RINGS = (RIM, THROAT, HOUSING)                      # made of sectors: shaded with their true radial normals


def _load(name, i):
    s = vxl.read_vxl(D + name + '.VXL')[i]
    names, mats = vxl.read_hva(D + name + '.HVA')
    return Frame(s, mats[0, i])


FH = _load('ORCAB', 0)
HYC = 20.0


def Y(w):
    return HYC + w


def hullq(pts, comp, name):
    return hull(FH, pts, comp, name)


def mirror_pts(pts):
    return [(x, 2 * HYC - y, z) for (x, y, z) in pts]


def both(pts, comp, name):
    """a hull on the right (pts) and its mirror on the left."""
    return [hullq(pts, comp, name), hullq(mirror_pts(pts), comp, name)]


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


def rotor(c, r_hub, r_tip, zc, n, comp_hub, comp_blade, name, a_off=0.0, pitch=0.3, chord=0.5, thick=0.08,
          hub_h=(0.7, 0.5), sweep=0.0):
    """a fan: a hub with a spinner and n pitched blades (sweep: the tips' lag, radians)."""
    out = [cyl(FH, (c[0], c[1], zc - hub_h[0]), (c[0], c[1], zc + hub_h[1]), r_hub, comp_hub, name + '_hub')]
    out.append(rc.Part([rc.Ellip(FH.p((c[0], c[1], zc + hub_h[1])), np.eye(3), np.array([r_hub, r_hub, 0.5]) * FH.sc),
                        rc.Plane((0, 0, -1.0), -FH.p((0, 0, zc + hub_h[1]))[2])], comp_hub, name + '_spinner',
                       sphere=(FH.p((c[0], c[1], zc + hub_h[1])), r_hub + 0.6)))
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


# ---------------------------------------------------------------- the lift fans
FAN_C = ((26.0, 5.5), (26.0, 2 * HYC - 5.5))       # TS: rims x 20..32, y 0..11 (and 29..40)
FAN_RO, FAN_RI = 5.75, 4.85
RIM_PROF = [(FAN_RI, 6.0), (FAN_RO, 6.0), (FAN_RO, 9.6), (FAN_RO - 0.35, 10.0), (FAN_RI + 0.25, 10.0),
            (FAN_RI, 9.7)]
THROAT_PROF = [(3.9, 4.05), (4.45, 4.05), (5.05, 6.05), (3.9, 6.05)]


def throat_sectors(c, out_sign, n):
    """the fan's black throat under its rim, its foot lower on the side towards the body (TS: z 4 at the inner half,
    z 5 further out, none below the rim's outer edge)."""
    out = []
    for i in range(n):
        a0, a1 = 2 * np.pi * i / n, 2 * np.pi * (i + 1) / n
        pts = []
        for a in (a0, a1):
            outward = max(0.0, np.sin(a) * out_sign)          # 1 pointing straight away from the body
            zb = 4.05 + 1.0 * outward
            for (r, z) in THROAT_PROF:
                pts.append(_circle(c, r, max(z, zb) if z < 5.0 else z, a))
        out.append(hull(FH, pts, THROAT, 'fan_throat'))
    return out


def fan_parts():
    out = []
    for k, c in enumerate(FAN_C):
        out += ring_sectors(c, RIM_PROF, 36, RIM, 'fan_rim')
        out += throat_sectors(c, -1.0 if k == 0 else 1.0, 30)
        out += rotor(c, 0.95, FAN_RI + 0.04, 8.3, 12, HUB, BLADE, 'fan', a_off=0.25 + 0.4 * k, pitch=0.5, chord=0.85,
                     sweep=0.28 if k == 0 else -0.28)
        out.append(cyl(FH, (c[0], c[1], 5.6), (c[0], c[1], 6.2), 3.95, FLOOR, 'fan_stator'))
    return out


# ---------------------------------------------------------------- the body
BODY_PROFILE = [(18.0, 5.0), (20.6, 3.0), (35.0, 3.0), (35.0, 8.0), (32.0, 9.0), (28.0, 10.0), (22.0, 10.0),
                (18.0, 6.1)]                         # x, z (TS: q 10 top x 21..28, 9 at x 28..32, 8 at x 32..35; its
#                                                      back a wedge, z 5..6 at x 18)
BAY_Z = ((3.25, 4.95), (6.05, 7.75))                 # TS's black rows in the front faces (z 3..5 and 6..8)
BAY_W = ((3.0, 7.1), (-7.1, -3.0))                   # TS: y 13..17 and 22..27 (w out from the centre line)
PANEL_W = (1.5, 5.3)                                 # TS's house-colour panels either side of the spine (y 15..19,
#                                                      20..25), running under its edges
STRIP_W = (6.3, 8.7)                                 # TS's strips along the outer edges (y 12, 26..29)


def body_parts():
    out = []
    out.append(prism(FH, 1, BODY_PROFILE, 10.0, 30.0, BODY, ch=0.35, name='body'))
    # the spine to the canopy (TS: y 18..21 at z 10..11, x 26..35), its back sloping into the top
    out.append(hullq([(22.5, Y(-1.7), 10.0), (22.5, Y(1.7), 10.0), (25.6, Y(-1.6), 11.0), (25.6, Y(1.6), 11.0),
                      (35.4, Y(-1.6), 11.0), (35.4, Y(1.6), 11.0), (35.4, Y(-1.7), 9.0), (35.4, Y(1.7), 9.0),
                      (22.5, Y(-1.7), 9.6), (22.5, Y(1.7), 9.6)], SPINE, 'spine'))
    # TS's house-colour panels on the top either side of the spine, and the strips along its outer edges
    for s in (1, -1):
        for (w0, w1), x0, x1, nm in ((PANEL_W, 22.6, 32.6, 'top_panel'), (STRIP_W, 22.0, 33.4, 'top_strip')):
            ya, yb = sorted((Y(s * w0), Y(s * w1)))
            zt = lambda x: 10.0 if x <= 28.0 else 10.0 - (x - 28.0) / 4.0
            pts = []
            for x in (x0, min(x1, 28.0), x1):
                for yy in (ya, yb):
                    pts += [(x, yy, zt(x) - 0.3), (x, yy, zt(x) + 0.14)]
            out.append(hullq(pts, PANEL, nm))
        # the small blocks on the top by the booms (TS: x 26..28, z 10..11)
        ya, yb = sorted((Y(s * 6.2), Y(s * 7.8)))
        out.append(B(FH, 25.9, 28.1, ya, yb, 9.7, 10.8, BLOCK, ch=0.25, name='top_block'))
    # TS's black bays in the front faces of the front blocks, two rows a side, set in; a bomb's nose in each
    for (w0, w1) in BAY_W:
        ya, yb = sorted((Y(w0), Y(w1)))
        for z0, z1 in BAY_Z:
            out.append(B(FH, 34.3, 35.02, ya, yb, z0, z1, BAY, name='bay'))
            n = 2
            for i in range(n):
                yc = ya + (yb - ya) * (i + 0.5) / n
                zc = (z0 + z1) / 2
                out.append(cyl(FH, (34.6, yc, zc), (35.25, yc, zc), 0.72, BOMB, 'bomb'))
                out.append(rc.Part([rc.Ellip(FH.p((35.25, yc, zc)), np.eye(3), np.array([0.5, 0.72, 0.72]) * FH.sc),
                                    rc.Plane((-1.0, 0, 0), -FH.p((35.25, 0, 0))[0])], BOMB, 'bomb_nose',
                                   sphere=(FH.p((35.25, yc, zc)), 0.8)))
    # TS's black blocks at the fans' front inner corners (x 32..34, y 7..9 and 30..32, z 4..8): bomb racks
    for s in (1, -1):
        ya, yb = sorted((Y(s * 10.3), Y(s * 12.8)))
        out.append(B(FH, 32.0, 34.2, ya, yb, 4.0, 8.0, RACK, ch=0.25, name='rack'))
    return out


# ---------------------------------------------------------------- the nose
def nose_parts():
    out = []
    # the keel (TS: y 17..21; its bottom z 3 at x 21..27, 2 at x 27..31, 1 at x 31..33, 0 at x 33..40, then up to the
    # tip at x 44): its chin one slope from z 3 at x 26.5 to z 0 at x 33
    w = 2.5
    prof = [(26.5, 3.0), (33.2, 0.0), (39.6, 0.0), (41.6, 1.1), (43.3, 2.4), (44.0, 3.6), (44.0, 4.5), (35.0, 7.0),
            (26.5, 7.0)]
    out.append(prism(FH, 1, prof, Y(-w), Y(w), KEEL, ch=0.45, name='keel'))
    return out


# the canopy over TS's blue glazed nose: its top at z 10 from behind the red lamp to x 39.6, its front sloping 45 degrees
# down to the tip (TS: z 9 at x 34..39, then a voxel down a voxel forward to z 4 at x 44), faceted, its sill on the keel
BEACON = (34.7,)                                     # the beacon on the spine's front end (TS's red lamp: x 34..36)
BEACON_R = 0.82
CANOPY_PTS = [(35.6, Y(-2.0), 6.6), (35.6, Y(2.0), 6.6), (35.6, Y(-1.15), 10.1), (35.6, Y(1.15), 10.1),
              (39.6, Y(-2.05), 6.5), (39.6, Y(2.05), 6.5), (39.6, Y(-1.15), 10.0), (39.6, Y(1.15), 10.0),
              (44.05, Y(-1.35), 4.3), (44.05, Y(1.35), 4.3), (44.15, Y(-0.8), 5.1), (44.15, Y(0.8), 5.1),
              (35.6, Y(-2.0), 5.6), (35.6, Y(2.0), 5.6), (43.4, Y(-1.35), 3.9), (43.4, Y(1.35), 3.9)]


def canopy_parts():
    out = [hullq(CANOPY_PTS, CANOPY, 'canopy')]
    # TS's red lamp behind it (x 34..36, y 18..21, z 9..11): a beacon - a red glass dome on a dark ring, on the spine's
    # front end (v3; v2's block read as a blob)
    c = (BEACON[0], HYC, 11.0)
    out.append(cyl(FH, (c[0], c[1], 10.85), (c[0], c[1], 11.22), BEACON_R + 0.22, BLOCK, 'beacon_base'))
    cl = FH.p(c[:2] + (11.18,))
    out.append(rc.Part([rc.Ellip(cl, np.eye(3), np.array([BEACON_R, BEACON_R, 0.78]) * FH.sc),
                        rc.Plane((0, 0, -1.0), -cl[2])], LAMP, 'beacon', sphere=(cl, BEACON_R + 0.2)))
    return out


# ---------------------------------------------------------------- the booms and the tail
BOOM_W = 6.5                                         # TS: y 12..15 and 25..28 (3 voxels; centres 13.5 and 26.5)
BOOM_R = (1.5, 1.42)                                 # half width, half height (TS: z 7..10)
BOOM_Z = 8.6
ROOT_R = (2.0, 1.5)                                  # the booms' roots, a voxel wider (TS: y 11..15 at x 12..20)
TAIL_C = (6.0, HYC)                                  # TS: the housing's rim at z 10, x 2..10, y 17..22; its fan's grey
TAIL_RO, TAIL_RI = 3.6, 1.85                         # at x 4..7, y 18..20


def _oct(yc, zc, hw, hh, e=0.0):
    hw, hh = hw + e, hh + e
    return [(yc - hw, zc - hh * 0.55), (yc - hw * 0.6, zc - hh), (yc + hw * 0.6, zc - hh), (yc + hw, zc - hh * 0.55),
            (yc + hw, zc + hh * 0.55), (yc + hw * 0.6, zc + hh), (yc - hw * 0.6, zc + hh), (yc - hw, zc + hh * 0.55)]


def tail_parts():
    out = []
    for s in (1, -1):
        yc = Y(s * BOOM_W)
        out.append(prism(FH, 0, _oct(yc, BOOM_Z, *BOOM_R), 0.2, 20.5, BOOM, name='boom'))
        # its root, widening into the body (TS: a voxel wider from x 12)
        hw0, hh0 = BOOM_R
        hw1, hh1 = ROOT_R
        pts = []
        for x, hw, hh in ((11.6, hw0, hh0), (14.2, hw1, hh1), (20.5, hw1, hh1)):
            pts += [(x, yy, zz) for (yy, zz) in _oct(yc, BOOM_Z, hw, hh)]
        out.append(hullq(pts, BOOM, 'boom_root'))
        # TS's dark band (x 15..18)
        out.append(prism(FH, 0, _oct(yc, BOOM_Z, *ROOT_R, e=0.1), 15.4, 17.6, COLLAR, name='boom_collar'))
        # the fin on the boom's end, canted out at the top (TS: x 1..7, z 6..16; its front edge furthest forward at z
        # 10.5; y 10..12 at its foot, 12..13 at z 10..12, 10..11 at its top)
        w = lambda v: Y(s * v)
        pts = []
        for z, x0, x1, wa, wb in ((6.0, 1.0, 4.0, 7.6, 9.2), (10.5, 1.4, 7.0, 6.6, 8.2), (16.0, 1.0, 3.0, 8.6, 10.0)):
            for x in (x0, x1):
                for ww in (wa, wb):
                    pts.append((x, w(ww), z))
        out.append(hullq(pts, FIN, 'fin'))
    # the plate joining the tail fan's housing to the booms (TS: x 3..8, z 8..10) and the keel through the housing
    # (TS: x 1..12 at y 18..21, z 8..10)
    out.append(B(FH, 2.7, 8.7, Y(-BOOM_W), Y(BOOM_W), 8.15, 9.85, STAB, ch=0.35, name='tailplane'))
    out.append(B(FH, 0.9, 11.9, Y(-1.6), Y(1.6), 7.95, 9.95, STAB, ch=0.4, name='tail_keel'))
    # the housing round the tail fan, and the fan in it
    prof = [(TAIL_RI, 8.6), (TAIL_RO, 8.6), (TAIL_RO, 10.6), (TAIL_RO - 0.35, 11.0), (TAIL_RI + 0.3, 11.0),
            (TAIL_RI, 10.7)]
    out += ring_sectors(TAIL_C, prof, 28, HOUSING, 'tail_housing')
    out += rotor(TAIL_C, 0.5, TAIL_RI + 0.03, 9.9, 7, HUB, BLADE, 'tail_fan', a_off=0.2, pitch=0.25, chord=0.3,
                 hub_h=(0.6, 0.4))
    out.append(cyl(FH, (TAIL_C[0], TAIL_C[1], 8.7), (TAIL_C[0], TAIL_C[1], 9.0), TAIL_RI + 0.05, FLOOR, 'tail_floor'))
    return out


def model():
    return {'hull': fan_parts() + body_parts() + nose_parts() + canopy_parts() + tail_parts()}


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
