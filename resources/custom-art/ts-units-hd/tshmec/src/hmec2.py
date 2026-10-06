"""
hmec2.py - the Mammoth Mk. II (TS [HMEC]) rebuilt the way the Titan and the Wolverine are: TS's own HMEC.VXL (13
sections) as the blueprint for where every part is and how big, each part modelled clean (flat plates, true slopes,
round pins and tubes, bevelled edges), posed by TS's own walk (HMEC.HVA), with the details of Westwood's own art of
the Mk. II (the render, the FMV stills and the sidebar icon Luke sent): plated panels, the pods' tube mouths, the
pistons on the feet.  The voxel is what the game shows, so its layout and its colours rule; the art fills in the
detail the voxel loses.

Every section has its own frame: q, continuous voxel coordinates (voxel i spans i..i+1), x forward, y from the
unit's right (0) to its left, z up; the section's local frame is min + q * scale (per axis, TS's), and TS's HVA
poses that frame in the unit's (x forward, y left, z up; the unit's position at the origin, on the ground).

The body (section 12, 53 x 31 x 20) is built symmetric about q y = 15 (TS's left half - pods, rear boxes, bays,
hull edge - sits a voxel higher than its right; v2 builds both halves at the mean, half a voxel over the right's).  The four legs are each built from their own sections: TS's
legs differ (the right front and the left rear thigh slant forward, the other two back) and the HVA's joints are
fixed in each, so every thigh, shin and foot spans its own hip, knee and ankle.
"""
import os, sys
from paths import HANDOFF
sys.path.insert(0, os.path.join(HANDOFF, 'renderer'))
import numpy as np
from scipy.spatial import ConvexHull
import vxl
import rc

D = os.path.join(HANDOFF, '03-TSHMEC', 'ts-original') + os.sep
SECS = vxl.read_vxl(D + 'HMEC.VXL')
NAMES, MATS = vxl.read_hva(D + 'HMEC.HVA')
STEPS = (0, 2, 4, 6, 8, 11, 13, 15)               # the mod's 8 walk steps: HVA frames

(FOOT_RR, SHIN_RR, THIGH_RR, FOOT_RF, SHIN_RF, THIGH_RF, FOOT_LR, SHIN_LR, THIGH_LR, FOOT_LF, SHIN_LF, THIGH_LF,
 BODY) = range(13)
LEGS = {'RF': (THIGH_RF, SHIN_RF, FOOT_RF, False), 'RR': (THIGH_RR, SHIN_RR, FOOT_RR, False),
        'LF': (THIGH_LF, SHIN_LF, FOOT_LF, True), 'LR': (THIGH_LR, SHIN_LR, FOOT_LR, True)}

(HULL, KEEL, RBOX, RPOD, RPOD_IN, BAY, BAYPOST, HATCH, SPOD, SPOD_IN, MOUNT, HIPCOV, HIPBRG, HIPCAP, RHIP, RAILBED,
 RAIL, GROOVE, BREECH, HOUSING, FLANGE, SIDEREC, MUZZLE, CHIN, CHINTIP, HULLFRONT,
 THIGH, KNEEPIN, SHIN, GUARD_G, GUARD_A, SHIN_K, BOLT, TOE, HUB, PISTON, SLEEVE, ANKLE, HIPPIN, VISOR,
 TURRET, LAMPHOUSE, LAMP) = range(81, 124)
HOUSE = (RPOD, SPOD, MOUNT, HIPCOV, GUARD_G)

BODY_YC = 15.0                                    # the body's centre line (q y)
BODY_ROLL_SCALE = 0.4                             # the body's roll in TS's walk (up to 5 degrees) is kept at this share
ZS = 0.5                                          # the side attachments' lift over TS's right half (q z)


def mirror_y(y):
    return 2 * BODY_YC - y


# ------------------------------------------------------------------------------------------------ section frames
class Frame:
    """a section's q space -> its local frame (min + q * sc) and its HVA pose."""

    def __init__(self, i):
        s = SECS[i]
        self.i = i
        self.mn = np.asarray(s['min'], float)
        self.sc = (np.asarray(s['max'], float) - self.mn) / np.asarray(s['size'], float)
        self.det = s['det']
        self.size = np.asarray(s['size'])

    def p(self, q):
        return self.mn + np.asarray(q, float) * self.sc

    def q(self, local):
        return (np.asarray(local, float) - self.mn) / self.sc

    def pose(self, hf):
        M = MATS[hf, self.i]
        R = M[:, :3]
        if self.i == BODY and BODY_ROLL_SCALE != 1.0:
            roll = np.arctan2(R[2, 1], R[2, 2]) * (BODY_ROLL_SCALE - 1.0)
            c, s = np.cos(roll), np.sin(roll)
            R = R @ np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]])
        return R, M[:, 3] * self.det

    def r(self, r, axis=None):
        """a length in q units -> local units (the mean of the two axes across `axis`)."""
        if axis is None:
            return r * float(np.mean(self.sc))
        k = [a for a in range(3) if a != axis]
        return r * float(np.mean(self.sc[k]))


FR = [Frame(i) for i in range(13)]


# ------------------------------------------------------------------------------------------------ builders (q space)
def B(F, x0, x1, y0, y1, z0, z1, comp, ch=0.0, name=''):
    """a box over q coordinates; ch: chamfer (local units), a scalar or (edges along x, along y, vertical)."""
    a = F.p((x0, y0, z0)); b = F.p((x1, y1, z1))
    c = (a + b) / 2; h = np.abs(b - a) / 2
    return rc.box(c, np.eye(3), h, comp, ch, name)


def _convex(P):
    n = len(P)
    s = 0.0
    for k in range(n):
        a, b, c = P[k], P[(k + 1) % n], P[(k + 2) % n]
        cr = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if abs(cr) < 1e-12:
            continue
        if s == 0.0:
            s = np.sign(cr)
        elif np.sign(cr) != s:
            raise ValueError('not convex: %s' % (np.asarray(P).tolist(),))


def prism(F, axis, pts, a0, a1, comp, ch=0.0, name='', edges=None, ends=(True, True)):
    """a convex polygon in the two axes other than `axis` (in their order: x-axis -> (y, z), y -> (x, z),
    z -> (x, y)), q coordinates, extruded along `axis` from a0 to a1.  ch chamfers the polygon's edges against the
    two end faces (edges: per polygon edge, whether it is chamfered; ends: which end faces get the chamfers)."""
    ax = [k for k in range(3) if k != axis]
    P = np.array([[F.mn[ax[0]] + u * F.sc[ax[0]], F.mn[ax[1]] + v * F.sc[ax[1]]] for u, v in pts], float)
    _convex(P)
    e0, e1 = F.mn[axis] + a0 * F.sc[axis], F.mn[axis] + a1 * F.sc[axis]
    lo, hi = min(e0, e1), max(e0, e1)
    cen = P.mean(0)

    def vec(n2, na):
        v = np.zeros(3); v[ax[0]], v[ax[1]] = n2[0], n2[1]; v[axis] = na
        return v
    cons = [rc.Plane(vec((0, 0), 1.0), hi), rc.Plane(vec((0, 0), -1.0), -lo)]
    for k in range(len(P)):
        a, b = P[k], P[(k + 1) % len(P)]
        d = b - a
        n = np.array([d[1], -d[0]]); n = n / np.linalg.norm(n)
        if n @ (cen - a) > 0:
            n = -n
        cons.append(rc.Plane(vec(n, 0.0), n @ a))
        if ch > 0 and (edges is None or edges[k]):
            for s, on in ((1.0, ends[1]), (-1.0, ends[0])):
                if not on:
                    continue
                m = vec(n, s); m = m / np.linalg.norm(m)
                ee = hi if s > 0 else -lo
                cons.append(rc.Plane(m, (n @ a + ee - ch) / np.sqrt(2.0)))
    c = vec(cen, (lo + hi) / 2)
    r = float(np.max(np.linalg.norm(P - cen, axis=1)))
    return rc.Part(cons, comp, name, sphere=(c, float(np.hypot(r, (hi - lo) / 2)) + 1e-3))


def hull(F, pts, comp, name=''):
    """the convex hull of q points as a part."""
    P = np.array([F.p(q) for q in pts], float)
    h = ConvexHull(P)
    cons = []
    seen = []
    for eq in h.equations:
        n, d = eq[:3], -eq[3]
        if any(np.allclose(n, n2, atol=1e-6) and abs(d - d2) < 1e-6 for n2, d2 in seen):
            continue
        seen.append((n, d))
        cons.append(rc.Plane(n, d))
    c = P.mean(0)
    return rc.Part(cons, comp, name, sphere=(c, float(np.max(np.linalg.norm(P - c, axis=1))) + 1e-3))


def cyl(F, q0, q1, r, comp, name='', extra=()):
    """a cylinder between two q points; r in q units."""
    p0, p1 = F.p(q0), F.p(q1)
    a = p1 - p0
    ax = int(np.argmax(np.abs(a)))
    return rc.cylinder(p0, p1, F.r(r, ax), comp, name, extra)


def ball(F, c, r, ztop, comp, name=''):
    """an ellipsoid (centre c, radii r, q units) cut flat at q z = ztop."""
    cl = F.p(c)
    rl = np.asarray(r, float) * F.sc
    top = F.p((c[0], c[1], ztop))[2]
    cons = [rc.Ellip(cl, np.eye(3), rl), rc.Plane((0, 0, 1.0), top)]
    return rc.Part(cons, comp, name, sphere=(cl, float(rl.max()) + 1e-3))


def ybox(left):
    """a y-range helper for the body's symmetric halves: (a, b) on the right -> mirrored on the left."""
    def yr(a, b):
        return (a, b) if not left else (mirror_y(b), mirror_y(a))
    return yr


# ------------------------------------------------------------------------------------------------ the joints
def joints():
    """per leg (HVA frame 0; the HVA's links are rigid): hip in the body's and the thigh's q, knee in the thigh's and
    the shin's q, ankle in the shin's and the foot's q."""
    out = {}
    for name, (u, l, f, left) in LEGS.items():
        Ru, tu = FR[u].pose(0); Rl, tl = FR[l].pose(0); Rf, tf = FR[f].pose(0); Rb, tb = FR[BODY].pose(0)
        out[name] = dict(hip_b=FR[BODY].q(Rb.T @ (tu - tb)), hip_t=FR[u].q(np.zeros(3)),
                         knee_t=FR[u].q(Ru.T @ (tl - tu)), knee_s=FR[l].q(np.zeros(3)),
                         ank_s=FR[l].q(Rl.T @ (tf - tl)), ank_f=FR[f].q(np.zeros(3)), left=left)
    return out


J = joints()


# ------------------------------------------------------------------------------------------------ the body
FRONT_BAYS = ((6.3, 9.55), (10.15, 13.4))         # the front's two bays (q z): TS's grey band and light band over it
HYC = 15.5                                        # the front housing's centre line: TS's, half a voxel left of the body's
HY0, HY1 = HYC - 3.5, HYC + 3.5                   # its sides (TS: 7 voxels wide, y 12..18)


def body_parts():
    F = FR[BODY]
    out = []
    # ---------------------------------------------------------------- the hull: crowned top, bevelled bottom edges
    out.append(prism(F, 0, [(5.0, 9.5), (5.5, 9.0), (24.5, 9.0), (25.0, 9.5), (25.0, 15.0 + ZS), (23.0, 16.3),
                            (20.0, 17.0), (10.0, 17.0), (7.0, 16.3), (5.0, 15.0 + ZS)], 4.0, 27.0, HULL, ch=0.4,
                     name='hull'))
    # the keel under it, with TS's belly, running on under the front hips; at the back it rises into the spine's
    # tail (TS: the middle column runs back past the hull to x 0, under the breech)
    out.append(prism(F, 1, [(4.2, 9.0), (4.2, 3.6), (14.0, 2.2), (25.0, 2.2), (33.0, 3.0), (34.0, 4.0), (34.0, 9.0)],
                     HY0, HY1, KEEL, ch=0.45, name='keel', edges=(False, True, True, True, True,
                                                                                    True, True)))
    out.append(prism(F, 1, [(0.3, 13.6), (0.3, 7.0), (2.4, 4.4), (4.4, 3.6), (4.4, 13.6)], BODY_YC - 3.0,
                     BODY_YC + 3.0, KEEL, ch=0.45, name='tail', edges=(True, True, True, False, True)))
    # ---------------------------------------------------------------- the railgun's rails along the top, its breech
    out.append(B(F, 0.8, 26.6, 12.0, 18.0, 16.5, 17.18, RAILBED, ch=0.12, name='railbed'))
    for y0, y1 in ((12.9, 14.4), (15.6, 17.1)):
        out.append(B(F, 0.0, 26.3, y0, y1, 16.9, 17.55, RAIL, ch=(0.16, 0.16, 0.16), name='rail'))
    out.append(B(F, 0.4, 26.3, 14.4, 15.6, 16.6, 17.08, GROOVE, name='groove'))
    out.append(B(F, 0.2, 4.4, 12.2, 17.8, 13.4, 17.0, BREECH, ch=0.45, name='breech'))
    # ---------------------------------------------------------------- the front housing (the railgun's barrel)
    # upper block: the top slopes down to the muzzle frame; the lower blocks leave TS's recess low on each side
    out.append(prism(F, 1, [(27.0, 9.0), (50.6, 9.0), (50.6, 15.44), (48.0, 17.0), (27.0, 17.0)], HY0, HY1, HOUSING,
                     ch=0.45, name='housing', edges=(False, True, True, True, True)))
    out.append(prism(F, 1, [(27.0, 5.0), (35.0, 5.0), (35.0, 9.0), (27.0, 9.0)], HY0, HY1, HOUSING, ch=0.45,
                     name='housing_lb', edges=(True, True, False, True)))
    out.append(prism(F, 1, [(39.0, 5.0), (50.6, 5.0), (50.6, 9.0), (39.0, 9.0)], HY0, HY1, HOUSING, ch=0.45,
                     name='housing_lf', edges=(True, True, False, True)))
    out.append(B(F, 34.9, 39.1, HY0 + 0.75, HY1 - 0.75, 5.25, 9.05, SIDEREC, name='siderec'))
    # the front (Westwood's render and FMVs; TS's ochre frame round two bands, light over grey): the frame's hood
    # round two stacked bays, each with a visor plate sloping down to the front, a lit window band along its top
    out.append(prism(F, 1, [(50.5, 13.4), (53.0, 13.4), (53.0, 14.0), (50.5, 15.5)], HY0, HY1, HOUSING, ch=0.35,
                     name='front_top'))
    out.append(B(F, 50.5, 53.0, HY0, HY1, 5.0, 6.3, HOUSING, ch=0.35, name='front_bot'))
    out.append(B(F, 50.5, 53.0, HY0, HY0 + 1.05, 6.2, 13.5, HOUSING, ch=0.3, name='front_side'))
    out.append(B(F, 50.5, 53.0, HY1 - 1.05, HY1, 6.2, 13.5, HOUSING, ch=0.3, name='front_side'))
    out.append(B(F, 50.5, 53.0, HY0 + 0.9, HY1 - 0.9, 9.55, 10.15, HOUSING, ch=0.16, name='front_divider'))
    out.append(B(F, 50.2, 51.0, HY0 + 0.9, HY1 - 0.9, 6.1, 13.6, MUZZLE, name='front_back'))
    for zb, zt in FRONT_BAYS:
        out.append(prism(F, 1, [(50.9, zb), (52.8, zb), (52.8, zb + 0.42), (50.9, zt - 0.75)], HY0 + 1.0, HY1 - 1.0,
                         VISOR, ch=0.12, name='visor'))
    # a lamp at each top corner of the front (the FMV's searchlight): a housing and a round lens
    for yc in (HY0 + 0.55, HY1 - 0.55):
        out.append(B(F, 51.6, 53.05, yc - 0.6, yc + 0.6, 13.45, 14.75, LAMPHOUSE, ch=0.2, name='lamp_housing'))
        out.append(cyl(F, (52.95, yc, 14.1), (53.3, yc, 14.1), 0.42, LAMP, 'lamp'))
    # the collars round its middle (TS's flange)
    for y0, y1 in ((HY0 - 0.45, HY0 + 0.2), (HY1 - 0.2, HY1 + 0.45)):
        out.append(B(F, 39.0, 44.0, y0, y1, 11.4, 16.4, FLANGE, ch=0.18, name='collar'))
    # the chin gun under the front: a ball turret (the render's and the FMVs'; TS's grey there), its barrel pointing
    # down and forward as TS's
    out.append(ball(F, (48.0, HYC, 3.9), (2.45, 2.35, 1.95), 5.08, TURRET, 'chin_ball'))
    out.append(B(F, 45.4, 50.4, HYC - 1.7, HYC + 1.7, 4.7, 5.12, CHIN, ch=0.12, name='chin_ring'))
    a, b = np.array([49.6, HYC, 3.1]), np.array([52.6, HYC, 0.8])
    out.append(cyl(F, a, b, 0.62, CHIN, 'chin_barrel'))
    d0 = (b - a) / np.linalg.norm(b - a)
    out.append(cyl(F, a + d0 * 0.35, a + d0 * 1.3, 0.85, CHIN, 'chin_sleeve'))
    d = (b - a) / np.linalg.norm(b - a)
    out.append(cyl(F, b - d * 0.05, b + d * 0.55, 0.62, CHINTIP, 'chin_tip'))
    for left in (False, True):
        yr = ybox(left)
        # ------------------------------------------------------------ the rear corner box and its pod on top
        # (TS's left side sits a voxel higher than its right: both halves at the mean, ZS up from the right's)
        z0 = ZS
        out.append(B(F, 2.0, 10.0, *yr(0.0, 5.0), 9.0 + z0, 15.05 + z0, RBOX, ch=0.4, name='rbox'))
        out.append(B(F, 2.0, 9.35, *yr(0.0, 6.0), 15.0 + z0, 19.0 + z0, RPOD, ch=0.35, name='rpod'))
        # its front frame round the tubes' opening (TS: dark, y 1..5, z 16..18)
        out.append(B(F, 9.3, 10.0, *yr(0.0, 6.0), 18.0 + z0, 19.0 + z0, RPOD, ch=0.18, name='rpod_frame'))
        out.append(B(F, 9.3, 10.0, *yr(0.0, 6.0), 15.0 + z0, 16.0 + z0, RPOD, ch=0.18, name='rpod_frame'))
        out.append(B(F, 9.3, 10.0, *yr(0.0, 1.0), 15.9 + z0, 18.1 + z0, RPOD, ch=0.14, name='rpod_frame'))
        out.append(B(F, 9.3, 10.0, *yr(5.0, 6.0), 15.9 + z0, 18.1 + z0, RPOD, ch=0.14, name='rpod_frame'))
        out.append(B(F, 9.0, 9.42, *yr(0.95, 5.05), 15.95 + z0, 18.05 + z0, RPOD_IN, name='rpod_tubes'))
        # ------------------------------------------------------------ the side bay (grey) and the post at its back
        out.append(B(F, 10.0, 12.1, *yr(0.0, 4.7), 9.0 + z0, 15.6 + z0, BAYPOST, ch=0.32, name='baypost'))
        out.append(B(F, 12.0, 20.1, *yr(0.2, 4.7), 9.2 + z0, 15.0 + z0, BAY, ch=0.25, name='bay'))
        out.append(B(F, 13.7, 18.9, *yr(-0.05, 0.45), 10.0 + z0, 14.4 + z0, HATCH, ch=0.12, name='hatch'))
        # ------------------------------------------------------------ the side pod: a tube block, open at both ends
        out.append(B(F, 20.6, 33.4, *yr(0.0, 4.0), 9.0 + z0, 16.0 + z0, SPOD, ch=0.38, name='spod'))
        for xa, xb in ((33.35, 34.0), (20.0, 20.65)):
            out.append(B(F, xa, xb, *yr(0.0, 4.0), 15.0 + z0, 16.0 + z0, SPOD, ch=0.2, name='spod_frame'))
            out.append(B(F, xa, xb, *yr(0.0, 4.0), 9.0 + z0, 10.0 + z0, SPOD, ch=0.2, name='spod_frame'))
            out.append(B(F, xa, xb, *yr(0.0, 1.0), 9.9 + z0, 15.1 + z0, SPOD, ch=0.16, name='spod_frame'))
            out.append(B(F, xa, xb, *yr(3.0, 4.0), 9.9 + z0, 15.1 + z0, SPOD, ch=0.16, name='spod_frame'))
        out.append(B(F, 20.3, 33.7, *yr(0.95, 3.05), 9.95 + z0, 15.05 + z0, SPOD_IN, name='spod_tubes'))
        out.append(B(F, 22.0, 33.6, *yr(3.9, 5.15), 9.0 + z0, 12.0 + z0, MOUNT, ch=0.22, name='mount'))
    # ---------------------------------------------------------------- the hips: per leg, round its own pivot
    for name in ('RF', 'LF'):
        px, py, pz = J[name]['hip_b']
        left = J[name]['left']
        s = 1.0 if left else -1.0                      # outward along y
        yo, yi = py + s * 2.1, py - s * 2.9
        out.append(B(F, px - 2.9, px + 1.3, min(yo, yi), max(yo, yi), pz - 2.4, pz + 1.7, HIPCOV, ch=0.45,
                     name='hipcover'))
        yb0, yb1 = py + s * 2.05, py + s * 4.0
        out.append(B(F, px - 3.8, px + 2.2, min(yb0, yb1), max(yb0, yb1), pz - 4.4, pz + 2.6, HIPBRG, ch=0.35,
                     name='hipbearing'))
        out.append(cyl(F, (px, py + s * 3.9, pz), (px, py + s * 4.45, pz), 2.35, HIPCAP, 'hipcap'))
    for name in ('RR', 'LR'):
        px, py, pz = J[name]['hip_b']
        left = J[name]['left']
        s = 1.0 if left else -1.0
        yo, yi = py + s * 4.1, py - s * 4.6
        out.append(B(F, px - 3.4, px + 2.6, min(yo, yi), max(yo, yi), pz - 2.3, 9.2, RHIP, ch=0.45, name='rearhip'))
        out.append(cyl(F, (px, py + s * 4.0, pz), (px, py + s * 4.55, pz), 1.9, HIPCAP, 'hipcap'))
    return out


# ------------------------------------------------------------------------------------------------ the legs
def thigh_parts(sec, profile, knee, comp_pin=KNEEPIN):
    """a thigh: TS's side profile (q x, z) as a plate across the section's width, a pin through its knee."""
    F = FR[sec]
    Y = F.size[1]
    out = [prism(F, 1, profile, 0.0, float(Y), THIGH, ch=0.5, name='thigh')]
    kx, ky, kz = knee
    out.append(cyl(F, (kx, -0.6, kz), (kx, Y + 0.6, kz), 1.55, comp_pin, 'kneepin'))
    return out


def shin_parts(sec, profile, y0, y1, plate=None, plate_y=None, plate_comp=GUARD_G, ankle=None, outer_low=True):
    """a shin: the grey hydraulic block (TS's side profile, over y0..y1), a plate on its outer side, bolts at its
    ankle."""
    F = FR[sec]
    out = [prism(F, 1, profile, y0, y1, SHIN, ch=0.45, name='shin')]
    if plate is not None:
        out.append(prism(F, 1, plate, plate_y[0], plate_y[1], plate_comp, ch=0.3, name='plate'))
    if ankle is not None:
        ax, ay, az = ankle
        out.append(cyl(F, (ax, y0 - 0.9, az + 0.9), (ax, y1 + 0.9, az + 0.9), 1.05, ANKLE, 'anklepin'))
    return out


def foot_parts(sec, xbar_y, piston_y, ankle):
    """a foot: TS's plus-shaped toe plate (a bar along the unit, a bar across), its hub, and the two pistons from
    the front and back toes up to the ankle."""
    F = FR[sec]
    out = []
    ya, yb = xbar_y
    out.append(prism(F, 1, [(0.0, 0.0), (14.0, 0.0), (14.0, 1.1), (13.2, 1.9), (0.8, 1.9), (0.0, 1.1)], ya, yb, TOE,
                     ch=0.35, name='toe_x'))
    out.append(prism(F, 0, [(0.0, 0.0), (13.0, 0.0), (13.0, 1.0), (12.3, 1.75), (0.7, 1.75), (0.0, 1.0)], 5.0, 9.0,
                     TOE, ch=0.35, name='toe_y'))
    out.append(B(F, 4.7, 9.3, ya - 0.35, yb + 0.35, 0.0, 2.4, HUB, ch=0.4, name='hub'))
    ax, ay, az = ankle
    py0, py1 = piston_y
    pc = (py0 + py1) / 2
    for xt, xs in ((2.4, 4.9), (11.4, 8.4)):
        a = np.array([xt, pc, 1.7]); b = np.array([xs, pc, 4.9])
        out.append(cyl(F, a, b, 0.62, PISTON, 'piston'))
        d = (b - a) / np.linalg.norm(b - a)
        out.append(cyl(F, a + d * 0.1, a + d * 1.9, 0.85, SLEEVE, 'sleeve'))
    out.append(B(F, 4.4, 8.9, py0 - 0.2, py1 + 0.2, 4.2, 5.7, ANKLE, ch=0.35, name='anklehead'))
    return out


def leg_parts():
    """{section: [parts]} for the eight leg sections' thighs and shins and the four feet, from TS's voxels."""
    out = {}
    # thighs: TS's side profiles (the convex outline of each section's voxels)
    out[THIGH_RF] = thigh_parts(THIGH_RF, [(0, 13), (0, 5), (1, 2), (3, 0), (7, 0), (8, 1), (8, 4), (7, 10), (6, 12),
                                           (4, 13)], J['RF']['knee_t'])
    out[THIGH_RR] = thigh_parts(THIGH_RR, [(5, 12), (1, 11), (0, 8), (0, 0), (4, 0), (10, 6), (10, 10), (9, 12)],
                                J['RR']['knee_t'])
    out[THIGH_LF] = thigh_parts(THIGH_LF, [(8, 12), (4, 12), (3, 11), (0, 7), (0, 0), (4, 0), (7, 3), (10, 7), (10, 9),
                                           (9, 11)], J['LF']['knee_t'])
    out[THIGH_LR] = thigh_parts(THIGH_LR, [(7, 12), (1, 12), (0, 10), (0, 4), (2, 2), (5, 0), (9, 0), (10, 2), (10, 4)],
                                J['LR']['knee_t'])
    # shins: the grey block, the house-colour guard on the front legs' outer side, TS's ochre plate on the rear legs'
    out[SHIN_RF] = shin_parts(SHIN_RF, [(8, 0), (8, 7), (6, 11), (4, 12), (3, 12), (1, 11), (1, 5), (3, 2), (5, 0)],
                              3.0, 7.0, plate=[(0, 11), (0, 8), (2, 5.4), (6.5, 5.4), (7, 6.5), (7, 10.5), (6, 12), (1, 12)],
                              plate_y=(2.0, 3.05), plate_comp=GUARD_G, ankle=J['RF']['ank_s'])
    out[SHIN_RR] = shin_parts(SHIN_RR, [(0, 12), (0, 9), (1, 5), (4, 1), (5, 0), (7, 0), (9, 1), (9, 4), (8, 7), (5, 13),
                                        (1, 13)], 3.0, 7.0,
                              plate=[(0, 11), (0, 9), (1, 7), (2, 6), (5, 6), (7, 7), (7, 9), (6, 11), (4, 13), (2, 13)],
                              plate_y=(2.0, 3.05), plate_comp=GUARD_A, ankle=J['RR']['ank_s'])
    out[SHIN_LF] = shin_parts(SHIN_LF, [(0, 10), (0, 4), (1, 1), (2, 0), (4, 0), (6, 2), (6, 10)], 1.0, 6.0,
                              plate=[(0, 12), (0, 7.5), (1.2, 6), (6, 6), (6, 12)], plate_y=(5.95, 7.0),
                              plate_comp=GUARD_G, ankle=J['LF']['ank_s'])
    out[SHIN_LR] = shin_parts(SHIN_LR, [(0, 11), (0, 8), (1, 5), (5, 1), (7, 0), (8, 0), (10, 1), (10, 4), (8, 8),
                                        (6, 11), (5, 12), (2, 12)], 1.0, 7.0, ankle=J['LR']['ank_s'])   # TS: no plate
    # feet: the bar along the unit sits over the pistons (TS: y 6..9 on the right feet, 3..6 on the left)
    out[FOOT_RF] = foot_parts(FOOT_RF, (6.0, 9.0), (7.0, 8.0), J['RF']['ank_f'])
    out[FOOT_RR] = foot_parts(FOOT_RR, (6.0, 9.0), (7.0, 8.0), J['RR']['ank_f'])
    out[FOOT_LF] = foot_parts(FOOT_LF, (3.0, 6.0), (4.0, 5.0), J['LF']['ank_f'])
    out[FOOT_LR] = foot_parts(FOOT_LR, (3.0, 6.0), (4.0, 5.0), J['LR']['ank_f'])
    return out


def model():
    """{section: [parts in the section's local frame]}."""
    m = leg_parts()
    m[BODY] = body_parts()
    return m


def posed(m, hf, Mx=np.eye(3)):
    """every part posed at HVA frame hf and turned by Mx (unit frame -> world): (parts, frames, owner) where frames
    give each part's q coordinates for texturing (rcrender's frames: L = (P - t) @ M)."""
    parts, frames, owner = [], [], []
    for i in range(13):
        F = FR[i]
        R, t = F.pose(hf)
        Rw, tw = Mx @ R, Mx @ t
        Mq = Rw @ np.diag(1.0 / F.sc)
        tq = tw + Rw @ F.mn
        for p in m.get(i, []):
            parts.append(p.moved(Rw, tw)); frames.append((Mq, tq)); owner.append(i)
    return parts, frames, np.array(owner)
