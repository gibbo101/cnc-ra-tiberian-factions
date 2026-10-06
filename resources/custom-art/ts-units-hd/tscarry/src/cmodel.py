"""
cmodel.py - the Carryall (TS's [TRNSPORT], TSCARRY in the mod) rebuilt the way the Titan, the Wolverine, the Dropship
and the Orcas are: TS's own voxel (TRNSPORT.VXL, one section, posed by its HVA) is the blueprint for where every part is
and how big, each part modelled clean (flat plates, true slopes, round fans, bevelled edges) in TS's colours - GDI's
ochre, TS's house colour where TS paints it (the pods along the spine, the engine under the cab, the outer quarter of
each fan's rim) - with the references Luke sent as the guide to how TS's parts read in HD: the fans' straps and blades,
the jointed claws under the hoist, the round engine under the cab, the ducted fan in the tail fin.

q: TS's voxel coordinates, continuous (voxel i spans i..i+1): x back to front 0..52, y from the aircraft's right (0) to
its left 0..39, z up 0..19; the section's local frame is min + q * scale (TS's), and its HVA (frame 0) places it in the
unit's frame (the unit's position at q 23.6, 19.5, 0.55).  Symmetric about q y 19.25 (TS's fans, claws, body and cab are
centred between 19.0 and 19.5); w below is the distance out from it (negative: the right).

Parts (TS's voxels in brackets, q units):
  fans     four ducted lift fans [rims z 10..15]: two at the back [centres x 7.4, w -/+13.0, r 6.5] and two at the
           front [x 40.5, w -/+10.2, r 6.5]; thick rims (r 4.3..6.5), TS's house colour on the outer quarter of each
           [from just past the outward point to the fan's end], ten straps round each (the renders'; TS's ochre gaps in
           the house colour); dark blades and a grey hub inside, its top flush with the rim (TS's black inside, grey hub)
  spine    the beam from the tail to the cab [x 5..43, z 10..15]: 6 wide at mid height, its top 3 wide [x 5..31], a
           5 wide box in front of the pods [x 31..43]; a keel strip under its front [x 30..38, z 9..10]
  pods     TS's house-colour pods along the spine's sides over the hoist [x 17..31.5, out to w 6.2 at x 21..25, z 11..15],
           three rust-red domes low on each [x 18.5, 21.5, 24.5: TS 106], a khaki vent on each [x 20..23.5]
  arms     the fans' arms: at the back [x 4..11, z 11..13] to the tail, at the front [x 37..43, z 12..14] to the cab
  cab      [x 39.5..52, w +/-3, z 6.4..14]: its roof a voxel under the spine's top [x 43..48], the windscreen sloping to the
           nose [x 48..51.6, z 14 -> 11.3], the nose's face [x 52, z 7..11]; TS's black windows (the roof's front, the
           windscreen, the sides by them) as dark glass, blue as the cameo's; two rust-red lamps on its sides [x 40..41,
           z 9]; TS's house-colour engine under it [x 41.5..51, r 2.1, its bottom at z 4] with its intake at the front
  hoist    TS's grey bell under the middle [centre x 24.75; r 5 at z 7, 3.4 at z 10]; four claws on the diagonals: an ochre
           bracket under the pod [r 4.9..6.3, z 8..11], a black upper arm out and down to the knee [r 9.5, z 5], a grey
           finger down to z 1 [r 10], hooked in at the tip (the FMV's)
  tail     the fin [x 0..11, w +/-1.85, top z 19] with TS's round duct through it [centre x 3, z 15.75, r 1.7]: a brown lip
           on each face, a small fan inside; the tail block under it [x 0..14, w +/-5, bottom z 6], its back sloping
  gear     TS's landing gear: two skids under the tail block [x 4..14, w -/+3.75, z 0..1] on legs with light grey
           struts, a pad under the engine [x 40..48, z 1..2] on a post
"""
import os, sys
from paths import HANDOFF
sys.path.insert(0, os.path.join(HANDOFF, 'renderer'))
import numpy as np
import vxl
import rc
from qparts import Frame, B, prism, hull, cyl

D = os.path.join(HANDOFF, '25-TSCARRY', 'ts-original') + os.sep

(RIM, STRAP, BLADE, HUB, FLOOR, SPINE, POD, DOME, TAILB, FIN, LIP, ARM, CAB, NACELLE, BELL, BRACKET, PIVOT, CLAW,
 FINGER, TIP, GEAR, SKID, STRUT, KEEL, LAMP, TBLADE) = range(81, 107)
HOUSE = (POD, NACELLE, RIM)                         # the parts that carry TS's house colour (the rims: their outer band)
RINGS = (RIM, STRAP)                                # made of sectors: shaded with their true radial normals


def _load(name, i):
    s = vxl.read_vxl(D + name + '.VXL')[i]
    names, mats = vxl.read_hva(D + name + '.HVA')
    return Frame(s, mats[0, i])


FH = _load('TRNSPORT', 0)
HYC = 19.25


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
          hub_h=(0.7, 0.5), dome=0.5, sweep=0.0):
    """a fan: a hub with a spinner and n pitched blades (sweep: the tips' lag, radians)."""
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


# ---------------------------------------------------------------- the lift fans
FAN_REAR = (7.4, 13.0)                               # x, w out (TS: x 1..14, y 0..13 and 26..39; r 6.4..6.6)
FAN_FRONT = (40.5, 10.2)                             # TS: x 34..47, y 2..16 and 23..36
# (name, centre (q x, y), outward sign in w, the fan's end in x: -1 back, +1 front)
FANS = [('RR', (FAN_REAR[0], Y(-FAN_REAR[1])), -1, -1), ('RL', (FAN_REAR[0], Y(FAN_REAR[1])), 1, -1),
        ('FR', (FAN_FRONT[0], Y(-FAN_FRONT[1])), -1, 1), ('FL', (FAN_FRONT[0], Y(FAN_FRONT[1])), 1, 1)]
FAN_RO, FAN_RI = 6.42, 4.28                         # local units (q 6.5 and 4.3)
FAN_Z = (10.0, 15.0)                                 # TS: rims z 10..14 (voxels)
RIM_PROF = [(FAN_RI, 10.0), (FAN_RO, 10.0), (FAN_RO, 14.62), (FAN_RO - 0.34, 15.0), (FAN_RI + 0.42, 15.0),
            (FAN_RI, 14.6)]
BAND_T = (8.0, 96.0)                                 # TS's house colour: degrees from the outward point to the fan's end
STRAP_T0, STRAP_N = 24.0, 10                         # straps every 36 degrees, two through the band (TS's ochre gaps)
STRAP_HW = 0.36                                      # half width (local units)
HUB_R = 1.42


def fan_angle(name_or_fan, a_rad):
    """the angle t (degrees) round a fan from its outward point towards its end, for a world angle a round its centre
    (a: atan2(q y - cy, q x - cx))."""
    _, c, o, e = name_or_fan
    vx, vy = np.cos(a_rad), np.sin(a_rad)
    return np.degrees(np.arctan2(vx * e, vy * o))      # outward (0, o) -> 0; the end (e, 0) -> 90


def fan_world_angle(fan, t_deg):
    _, c, o, e = fan
    t = np.radians(t_deg)
    return np.arctan2(o * np.cos(t), e * np.sin(t))


def fan_parts():
    out = []
    for k, fan in enumerate(FANS):
        nm, c, o, e = fan
        out += ring_sectors(c, RIM_PROF, 40, RIM, 'fan_rim', a_off=0.05 * k)
        # the straps round the rim's outer face (the renders' barrel straps; TS's ochre gaps in the house colour)
        for j in range(STRAP_N):
            a = fan_world_angle(fan, STRAP_T0 + 360.0 / STRAP_N * j)
            da = STRAP_HW / FAN_RO
            pts = []
            for aa in (a - da, a + da):
                for (r, z) in ((FAN_RO - 0.12, 9.96), (FAN_RO + 0.13, 9.96), (FAN_RO + 0.13, 14.55),
                               (FAN_RO - 0.12, 14.86)):
                    pts.append(_circle(c, r, z, aa))
            out.append(hullq(pts, STRAP, 'fan_strap'))
        out += rotor(c, HUB_R, FAN_RI + 0.04, 12.6, 10, HUB, BLADE, 'fan', a_off=0.21 + 0.37 * k, pitch=0.62,
                     chord=0.72, hub_h=(2.35, 1.95), dome=0.48, sweep=0.22 * o * e)
        out.append(cyl(FH, (c[0], c[1], 10.35), (c[0], c[1], 10.85), FAN_RI + 0.06, FLOOR, 'fan_floor'))
    # the arms: at the back to the tail block (TS: x 4..11, y 12..16 and 22..27, z 11..12), at the front to the cab
    # (TS: x 37..43, y 14..16 and 22..25, z 12..13)
    for s in (-1, 1):
        ya, yb = sorted((Y(s * 2.8), Y(s * 8.4)))
        out.append(B(FH, 4.0, 11.0, ya, yb, 11.0, 13.0, ARM, ch=0.3, name='rear_arm'))
        ya, yb = sorted((Y(s * 2.8), Y(s * 5.6)))
        out.append(B(FH, 37.4, 42.6, ya, yb, 11.9, 14.02, ARM, ch=0.3, name='front_arm'))
    return out


# ---------------------------------------------------------------- the spine and the pods
SPINE_OCT = [(-2.0, 10.0), (2.0, 10.0), (3.0, 11.0), (3.0, 13.0), (1.5, 15.0), (-1.5, 15.0), (-3.0, 13.0),
             (-3.0, 11.0)]                          # w, z (TS at x 15: y 16..21 at z 11..12, 17..20 at 10 and 13,
#                                                     18..20 at 14)
# the pods: (x, w out, z bottom, z top at the outer edge, z top at the spine, w of the top's inner edge)
POD_ST = [(16.8, 4.3, 11.15, 13.5, 13.95, 2.35), (18.3, 5.25, 11.0, 13.4, 14.05, 2.3), (20.6, 5.25, 11.0, 13.4, 14.05, 2.3),
          (20.9, 6.15, 11.0, 13.95, 15.0, 1.45), (24.6, 6.15, 11.0, 13.95, 15.0, 1.45),
          (26.3, 5.25, 12.0, 14.05, 15.0, 1.45), (28.2, 4.3, 12.0, 14.3, 15.0, 1.45), (30.2, 4.3, 12.0, 14.3, 15.0, 1.45),
          (31.5, 3.3, 12.1, 13.6, 14.0, 2.2)]
DOME_X = (18.6, 21.5, 24.4)                          # TS's rust-red spots low on the pods' outer faces (x 18..19, 21, 24)
DOME_Z = 11.75
DOME_R = 0.5
VENT_X = (20.3, 23.7)                                # TS's khaki on the pods' outer tops (x 20..23)


def pod_pts(s):
    pts = []
    for (x, wo, zb, zto, zti, wi) in POD_ST:
        bev = min(1.9, wo - wi - 0.3)
        sec = [(2.9, zb), (wo - 0.45, zb), (wo, zb + 0.45), (wo, zto), (wo - bev, zti), (wi, zti)]
        pts += [(x, Y(s * w), z) for (w, z) in sec]
    return pts


def _cast_point(part, q0, d):
    """where a ray from q0 (inside) along d (q) leaves a part: the surface point, q (cast back from far out)."""
    p1 = FH.p(np.asarray(q0, float) + 30.0 * np.asarray(d, float))
    Dw = FH.p(q0) - p1
    Dw = Dw / np.linalg.norm(Dw)
    t, who, _ = rc.cast([part], p1[None, :], Dw, want_normals=False)
    return FH.q(p1 + Dw * t[0])


def spine_parts():
    out = []
    out.append(prism(FH, 0, [(Y(w), z) for (w, z) in SPINE_OCT], 5.6, 31.8, SPINE, ch=0.5, name='spine',
                     ends=(True, False)))
    out.append(B(FH, 30.8, 43.2, Y(-2.5), Y(2.5), 10.0, 15.0, SPINE, ch=0.35, name='spine_front'))
    out.append(B(FH, 30.2, 38.8, Y(-0.6), Y(0.6), 9.0, 10.2, KEEL, ch=0.2, name='keel'))
    for s in (-1, 1):
        pod = hullq(pod_pts(s), POD, 'pod')
        out.append(pod)
        # TS's rust-red spots low on the pods' outer faces: small domes
        for x in DOME_X:
            q = _cast_point(pod, (x, Y(s * 3.5), DOME_Z), (0, s, 0))
            cl = FH.p(q)
            out.append(rc.Part([rc.Ellip(cl, np.eye(3), np.array([DOME_R, DOME_R, DOME_R]) * FH.sc)], DOME, 'pod_dome',
                               sphere=(cl, DOME_R + 0.1)))
    return out


# ---------------------------------------------------------------- the cab and the engine under it
CAB_W = 3.0
CAB_PROF = [(39.6, 9.0), (40.6, 6.0), (50.4, 6.0), (52.0, 7.05), (52.0, 10.85), (51.65, 11.2), (47.2, 14.0),
            (39.6, 14.0)]                            # x, z (TS: its bottom z 6 at x 41..50, 7 at the nose)
WINDSCREEN = ((47.2, 14.0), (51.65, 11.2))          # TS: the roof z 14 to x 48, then 13 at x 48, 12 at x 49..50, 11
#                                                     at 51: one slope through the steps
ROOF_GLASS = (45.9, 47.6)                            # TS's black roof window (x 46..47), its frame behind it (x 45)
SCREEN_GLASS = (48.45, 51.3)                         # TS's black windscreen (x 49..50), the olive frame bar (x 48)
SIDE_GLASS = (45.9, 48.45, 12.25)                    # the side windows by them (TS: x 46..47, z 12..13)
NAC_C = (6.15, 2.1)                                  # the engine: centre z, radius (TS: y 17..20, z 4..7, x 41..50)
NAC_X = (41.4, 43.6, 50.15)                         # its front leaning back at the bottom (TS: x 50 at z 4..5,
NAC_TILT = 0.31                                      # 51 at z 6..7)
LAMP_Q = (40.7, 9.5)                                 # TS's rust-red marks on the cab's sides (x 40..41, z 9)
LAMP_R = 0.42


def cab_parts():
    out = [prism(FH, 1, CAB_PROF, Y(-CAB_W), Y(CAB_W), CAB, ch=0.42, name='cab')]
    # its chin under the spine's front (TS: x 38..40, y 17..21 at z 9, 18..19 at z 8)
    out.append(hullq([(x, Y(s * w), z) for (x, w, z) in ((37.8, 2.4, 10.0), (37.9, 2.2, 9.0), (38.3, 1.1, 8.1),
                                                          (40.6, 2.7, 6.1), (40.6, 2.7, 10.0)) for s in (-1, 1)],
                     CAB, 'cab_chin'))
    pts = []
    for x, r, zc in ((NAC_X[0], 1.15, 6.75), (NAC_X[1], NAC_C[1], NAC_C[0]), (NAC_X[2], NAC_C[1], NAC_C[0])):
        for i in range(28):
            a = 2 * np.pi * i / 28
            zz = zc + r * np.sin(a)
            xx = x if x != NAC_X[2] else x + NAC_TILT * (zz - (NAC_C[0] - NAC_C[1]))
            pts.append((xx, HYC + r * np.cos(a), zz))
    out.append(hullq(pts, NACELLE, 'engine'))
    for s in (-1, 1):
        q = _cast_point(out[0], (LAMP_Q[0], HYC, LAMP_Q[1]), (0, s, 0))
        cl = FH.p(q)
        out.append(rc.Part([rc.Ellip(cl, np.eye(3), np.array([LAMP_R, LAMP_R, LAMP_R]) * FH.sc)], LAMP, 'cab_lamp',
                           sphere=(cl, LAMP_R + 0.1)))
    # TS's nose gear under the engine: a pad (x 40..48, z 1), a post (x 42..44, z 2..3), a light grey bracket (z 3..4)
    out.append(B(FH, 40.0, 48.0, Y(-1.4), Y(1.4), 1.0, 2.0, SKID, ch=0.32, name='nose_pad'))
    out.append(B(FH, 42.0, 44.0, Y(-0.95), Y(0.95), 1.9, 3.25, GEAR, ch=0.15, name='nose_post'))
    out.append(hullq([(x, Y(s * 1.05), z) for (x, z) in ((41.0, 3.0), (45.0, 3.0), (40.0, 4.9), (44.2, 4.9))
                      for s in (-1, 1)], STRUT, 'nose_strut'))
    return out


# ---------------------------------------------------------------- the hoist and its claws
BELL_C = (24.75, HYC)                                # TS: x 20..30, y 14..24 at z 7; 21..28 at z 9
BELL_R = ((5.0, 7.0), (3.35, 10.05))                 # (radius (local), z): its flat bottom and its top under the spine
CLAW_DIAG = ((-1, -1), (1, -1), (-1, 1), (1, 1))     # (x, w) signs: the four diagonals (TS's fingers at r 10)
KNEE = (10.0, 5.2)                                   # r, z (TS: the knee out to r 11.5 at z 5)


def claw(sx, sw):
    d = np.array([sx, sw], float) / np.sqrt(2.0)
    t = np.array([-sw, sx], float) / np.sqrt(2.0)

    def q(r, s, z):
        u = BELL_C[0] + r * d[0] + s * t[0]
        w = r * d[1] + s * t[1]
        return (u, Y(w), z)
    out = []
    # the bracket under the pod (TS's ochre, x 19..21 / 27..29, z 8..9)
    out.append(hullq([q(r, s, z) for r in (4.5, 6.5) for s in (-1.0, 1.0) for z in (7.95, 11.3)], BRACKET,
                     'claw_bracket'))
    # the pivot, the upper arm out and down to the knee (TS's black, 3 wide), the knee
    p0 = np.array([5.5, 7.6]); p1 = np.array(KNEE)
    dv = (p1 - p0) / np.linalg.norm(p1 - p0); nv = np.array([-dv[1], dv[0]])
    pts = []
    for p, th, hw in ((p0, 0.62, 0.95), (p1, 0.78, 1.15)):
        for k in (-th, th):
            rz = p + k * nv
            pts += [q(rz[0], s, rz[1]) for s in (-hw, hw)]
    out.append(hullq(pts, CLAW, 'claw_arm'))
    for (r, z), rr, hw, comp in (((5.5, 7.6), 0.72, 1.3, PIVOT), (KNEE, 0.92, 1.4, PIVOT)):
        out.append(cyl(FH, q(r, -hw, z), q(r, hw, z), rr, comp, 'claw_pivot'))
    # the finger down to the ground (TS's grey, 2 voxels square, r 8.7..11.5, z 1..5) and its tip, hooked in (the
    # FMV's)
    pts = [q(r, s, 5.5) for r in (9.1, 10.95) for s in (-0.98, 0.98)]
    pts += [q(r, s, 2.0) for r in (9.25, 10.95) for s in (-0.86, 0.86)]
    out.append(hullq(pts, FINGER, 'claw_finger'))
    pts = [q(r, s, 2.05) for r in (9.25, 10.95) for s in (-0.84, 0.84)]
    pts += [q(r, s, 1.35) for r in (9.0, 10.55) for s in (-0.66, 0.66)]
    pts += [q(r, s, 0.9) for r in (8.55, 9.25) for s in (-0.36, 0.36)]
    out.append(hullq(pts, TIP, 'claw_tip'))
    return out


def hoist_parts():
    pts = []
    for (r, z) in BELL_R:
        for i in range(36):
            pts.append(_circle(BELL_C, r, z, 2 * np.pi * (i + 0.5) / 36))
    out = [hullq(pts, BELL, 'hoist_bell')]
    for sx, sw in CLAW_DIAG:
        out += claw(sx, sw)
    return out


# ---------------------------------------------------------------- the tail
TAIL_OCT = [(-4.0, 6.0), (4.0, 6.0), (5.0, 7.4), (5.0, 10.1), (3.0, 12.8), (-3.0, 12.8), (-5.0, 10.1), (-5.0, 7.4)]
FIN_W = 1.85


def plane_q(a, b, c, inside):
    """the plane through three q points (in the section's local frame), facing away from a q point inside."""
    A, Bp, C = FH.p(a), FH.p(b), FH.p(c)
    n = np.cross(Bp - A, C - A); n /= np.linalg.norm(n)
    if n @ (FH.p(inside) - A) > 0:
        n = -n
    return rc.Plane(n, float(n @ A))
FIN_OUT = [(0.0, 12.6), (10.9, 12.6), (10.9, 15.2), (10.6, 15.4), (7.0, 17.8), (4.6, 19.0), (0.8, 19.0), (0.0, 18.2)]   # x, z
#                                                     (counter-clockwise; TS: top z 19 at x 1..5, 18 to x 7, 17 to x 8, 16 to
#                                                     x 10)
DUCT_C = (3.0, 15.75)                                # TS: the hole x 1..4, z 14..16; the painted ring x 0..5, z 13..18
DUCT_R, LIP_R = 1.72, 2.42
FIN_BEV = 0.24


def _inset(poly, d):
    """a convex polygon (counter-clockwise) moved in by d."""
    P = np.asarray(poly, float)
    n = len(P)
    lines = []
    for i in range(n):
        a, b = P[i], P[(i + 1) % n]
        e = (b - a) / np.linalg.norm(b - a)
        nin = np.array([-e[1], e[0]])
        lines.append((a + d * nin, e))
    out = []
    for i in range(n):
        (p1, e1), (p2, e2) = lines[i - 1], lines[i]
        A = np.array([e1, -e2]).T
        s = np.linalg.solve(A, p2 - p1)
        out.append(p1 + s[0] * e1)
    return out


def _ray_hit(poly, c, a):
    """where a ray from c at angle a leaves a convex polygon."""
    P = np.asarray(poly, float)
    d = np.array([np.cos(a), np.sin(a)])
    best = None
    for i in range(len(P)):
        p, q2 = P[i], P[(i + 1) % len(P)]
        e = q2 - p
        A = np.array([d, -e]).T
        if abs(np.linalg.det(A)) < 1e-12:
            continue
        t, u = np.linalg.solve(A, p - np.asarray(c))
        if t > 0 and -1e-9 <= u <= 1 + 1e-9 and (best is None or t < best):
            best = t
    return np.asarray(c) + best * d


def _between(c, a0, a1, p):
    ang = np.arctan2(p[1] - c[1], p[0] - c[0])
    da = (ang - a0) % (2 * np.pi)
    return 0 < da < (a1 - a0) % (2 * np.pi)


def fin_parts():
    """the fin with TS's round duct through it: 16 convex pieces round the hole, the duct's lips, the fan in it."""
    out = []
    n = 16
    c = np.array(DUCT_C)
    outer = FIN_OUT
    inner = _inset(FIN_OUT, FIN_BEV)
    for i in range(n):
        a0, a1 = 2 * np.pi * i / n, 2 * np.pi * (i + 1) / n
        pts = []
        for a in (a0, a1):
            h = c + DUCT_R * np.array([np.cos(a), np.sin(a)])
            pts += [(h[0], Y(w), h[1]) for w in (-FIN_W, FIN_W)]
            o = _ray_hit(outer, c, a); s_ = _ray_hit(inner, c, a)
            pts += [(o[0], Y(w), o[1]) for w in (-FIN_W + FIN_BEV, FIN_W - FIN_BEV)]
            pts += [(s_[0], Y(w), s_[1]) for w in (-FIN_W, FIN_W)]
        for poly, ww in ((outer, FIN_W - FIN_BEV), (inner, FIN_W)):
            for p in poly:
                if _between(c, a0, a1, p):
                    pts += [(p[0], Y(w), p[1]) for w in (-ww, ww)]
        out.append(hullq(pts, FIN, 'fin'))
    # the duct's lips on the fin's faces (TS's brown ring round the hole)
    m = 20
    for s in (-1, 1):
        for i in range(m):
            a0, a1 = 2 * np.pi * i / m, 2 * np.pi * (i + 1) / m
            pts = []
            for a in (a0, a1):
                for r in (DUCT_R, LIP_R):
                    p = c + r * np.array([np.cos(a), np.sin(a)])
                    pts += [(p[0], Y(s * w), p[1]) for w in (FIN_W - 0.1, FIN_W + (0.17 if r == DUCT_R else 0.12))]
            out.append(hullq(pts, LIP, 'duct_lip'))
    # the fan in the duct: a hub across it, seven pitched blades (TS's grey hub, black blades)
    out.append(cyl(FH, (c[0], Y(-1.25), c[1]), (c[0], Y(1.25), c[1]), 0.56, HUB, 'tail_fan_hub'))
    for i in range(7):
        a = 0.3 + 2 * np.pi * i / 7
        pts = []
        for rr, ch in ((0.45, 0.42), (DUCT_R - 0.03, 0.36)):
            da = ch / rr
            for sg in (-1, 1):
                p = c + rr * np.array([np.cos(a + sg * da), np.sin(a + sg * da)])
                for t in (-0.07, 0.07):
                    pts.append((p[0], Y(sg * 0.22 + t), p[1]))
        out.append(hullq(pts, TBLADE, 'tail_fan_blade'))
    return out


def tail_parts():
    out = fin_parts()
    # the tail block under the fin (TS: x 0..15; w +/-2 at the back, 5 at z 7..10, 4 at the bottom z 6; its back
    # sloping from z 12 at x 0 to z 6 at x 4, its front bottom rising to the spine, z 9 at x 15): an octagon along x,
    # cut by its back and front slopes and its sides drawn in at both ends
    blk = prism(FH, 0, [(Y(w), z) for (w, z) in TAIL_OCT], 0.15, 15.2, TAILB, name='tail_block')
    blk.cons += [plane_q((0.15, 0, 12.0), (4.0, 0, 6.0), (0.15, 1, 12.0), (8.0, HYC, 10.0)),
                 plane_q((8.4, 0, 6.0), (12.4, 0, 9.0), (8.4, 1, 6.0), (8.0, HYC, 10.0))]
    for s in (-1, 1):
        blk.cons += [plane_q((0.15, Y(s * 1.9), 0), (4.0, Y(s * 4.98), 0), (0.15, Y(s * 1.9), 1), (8.0, HYC, 10.0)),
                     plane_q((10.8, Y(s * 5.0), 0), (15.2, Y(s * 1.7), 0), (10.8, Y(s * 5.0), 1), (8.0, HYC, 10.0))]
    out.append(blk)
    out.append(B(FH, 11.0, 15.2, Y(-1.0), Y(1.0), 9.0, 10.4, TAILB, ch=0.2, name='tail_keel'))   # TS: x 11..15, z 9
    # TS's landing gear under it: a skid each side (x 4..14, z 0..1, its front turned up), a leg (x 6..9, z 1..3), a
    # light grey strut over it (z 3..5) and two posts into the block
    for s in (-1, 1):
        wc = s * 3.75
        ya, yb = sorted((Y(wc - 1.5), Y(wc + 1.5)))
        out.append(B(FH, 4.0, 14.0, ya, yb, 0.0, 0.95, SKID, ch=0.34, name='skid'))
        out.append(hullq([(x, Y(wc + k), z) for (x, k, z) in
                          ((12.9, -1.4, 0.6), (12.9, 1.4, 0.6), (14.0, -1.4, 0.6), (14.0, 1.4, 0.6),
                           (14.0, -1.2, 2.0), (14.0, 1.2, 2.0), (13.55, -1.2, 2.0), (13.55, 1.2, 2.0))],
                         SKID, 'skid_tip'))
        out.append(hullq([(x, Y(wc + k), z) for (x, z) in ((6.0, 0.85), (10.0, 0.85), (6.0, 2.0), (10.0, 2.0),
                                                           (6.0, 3.4), (9.0, 3.4)) for k in (-1.3, 1.3)],
                         GEAR, 'leg'))
        ya, yb = sorted((Y(wc - 0.7), Y(wc + 0.7)))
        out.append(B(FH, 4.0, 10.4, ya, yb, 3.1, 5.3, STRUT, ch=0.22, name='strut'))
        ya, yb = sorted((Y(wc - 0.45), Y(wc + 0.45)))
        out.append(B(FH, 5.0, 6.0, ya, yb, 5.1, 6.5, GEAR, ch=0.1, name='strut_post'))
        out.append(hullq([(x, Y(wc + k), z) for (x, z) in ((8.8, 5.0), (9.8, 5.0), (10.6, 7.6), (11.7, 7.6))
                          for k in (-0.45, 0.45)], GEAR, 'strut_post'))      # TS: up into the block at x 10..12
    return out


def model():
    return {'hull': fan_parts() + spine_parts() + cab_parts() + hoist_parts() + tail_parts()}


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
