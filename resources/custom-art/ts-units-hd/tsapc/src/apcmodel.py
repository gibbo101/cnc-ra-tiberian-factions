"""
apcmodel.py - the Amphibious APC (TS's [APC]) rebuilt the way the Titan, the Wolverine, the MCV and the Mammoths
are: TS's own voxels (APC.VXL on land, APCW.VXL on water) as the blueprint for where every part is and how big, each
part modelled clean (flat plates, true slopes, round wheels, bevelled edges) in TS's colours - house colour over
nearly all of it, as TS has it - with TS's panel lines (its darker remap shades) as seams.

The land hull's section is one: q, continuous voxel coordinates (voxel i spans i..i+1): x 0..39 back to front, y 0..22
from the unit's right to its left, z 0..14 up; its local frame is min + q * scale (TS's), and its HVA (frame 0)
places it in the unit's frame.  The water hull (APCW.VXL, TS's hull on water: the upper hull alone, sunk to its
waterline) is the land hull's upper part: its voxels match the land hull's above z 7 once moved (0.4, 0, 0.2) in the
local frame, so the water model is the land model's upper parts placed by that and by APCW's HVA.
"""
import os, sys
from paths import HANDOFF
sys.path.insert(0, os.path.join(HANDOFF, 'renderer'))
import numpy as np
import vxl
import rc
from qparts import Frame, B, prism, hull, cyl

D = os.path.join(HANDOFF, '06-TSAPC', 'ts-original') + os.sep

(HULL, LOWER, SKIRT, BOW, REAR, VENT, CUPOLA, PERI, HATCH, BLOCK, BUMPER, TYRE, HUB, CAP, LAMP, CAB, LIGHTHOUSE,
 LENS) = range(81, 99)
HOUSE = (HULL, LOWER, SKIRT, BOW, REAR, VENT, CUPOLA, HATCH, CAB)


def _load(name):
    s = vxl.read_vxl(D + name + '.VXL')[0]
    names, mats = vxl.read_hva(D + name + '.HVA')
    return Frame(s, mats[0, 0])


FL, FW = _load('APC'), _load('APCW')
YC = 11.0                                          # the hull's centre line (q y)
WATER_SHIFT = np.array([0.9, 0.0, 0.2])            # land local -> water local (fitted to the mod's water frames)
WATERLINE = 7.0                                     # q z: the water hull is the land hull above this


def plane_q(F, n_q, q_point):
    """the half-space n . q <= n . q_point in q space, as a plane in the section's local frame."""
    n = np.asarray(n_q, float) / F.sc
    n = n / np.linalg.norm(n)
    return rc.Plane(n, n @ F.p(q_point))


def mirror(y):
    return 2 * YC - y


def wheel(F, x, z, r, y0, y1, comp, name='wheel', bevel=0.0):
    """a wheel (axis across the unit) centred at q (x, z), from y0 to y1; bevel trims a 45-degree edge round both
    faces (16 planes a face)."""
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


def bow_planes(F, p):
    """the bow: its upper face sloping down to the stem, its bottom sloping up to it, its corners cut back in plan
    (TS: x 39 at y 4..17, x 37 at y 2 and 19, x 36 at y 1 and 20)."""
    p.cons.append(plane_q(F, (1.0, 0.0, 2.0), (39.0, 0.0, 11.0)))
    p.cons.append(plane_q(F, (1.0, 0.0, -1.0), (39.0, 0.0, 8.0)))
    p.cons.append(plane_q(F, (1.0, -1.2, 0.0), (34.4, 0.0, 0.0)))
    p.cons.append(plane_q(F, (1.0, 1.2, 0.0), (60.8, 0.0, 0.0)))
    return p


WHEELS = (8.0, 15.0, 27.5)                          # TS: a pair at the back, one at the front
R_WHEEL, Z_WHEEL = 3.5, 3.5


def rot_block(F, xc, yc, ang, rad, along, across, z0, z1, comp, name):
    """a block on a circle round (xc, yc): its middle `rad` out at angle `ang` (0 = forward, towards +x), `along`
    deep radially and `across` wide, from z0 to z1 (q units)."""
    u = np.array([np.cos(ang), np.sin(ang)]); v = np.array([-u[1], u[0]])
    c = np.array([xc, yc]) + rad * u
    pts = []
    for a in (-along / 2, along / 2):
        for b in (-across / 2, across / 2):
            xy = c + a * u + b * v
            for z in (z0, z1):
                pts.append((xy[0], xy[1], z))
    return hull(F, pts, comp, name)


def upper_parts(F):
    """the parts above the waterline: the upper hull and the bow over it, the roof's cupola, periscopes and hatch,
    the dark block at the front of the roof, the vents on the rear shoulders."""
    out = []
    # the upper hull: its sides upright, its shoulders stepping in to the roof (TS: y 1..21 at z 8..11, 2..20 at
    # 11..12, 5..17 on top at 13), its bottom edges chamfered; its back's top edge chamfered, its front the bow
    sec = [(1.0, 7.6), (1.0, 11.0), (2.0, 12.0), (5.0, 13.0), (17.0, 13.0), (20.0, 12.0), (21.0, 11.0), (21.0, 7.6),
           (20.4, 7.0), (1.6, 7.0)]
    p = prism(F, 0, sec, 1.0, 39.0, HULL, ch=0.0, name='hull')
    p.cons.append(plane_q(F, (-1.0, 0.0, 1.0), (1.0, 0.0, 11.0)))
    out.append(bow_planes(F, p))
    # the cupola on the roof (TS: a ring of dark blocks round a raised hatch, open at the back)
    cx, cy = 15.2, 10.8
    out.append(cyl(F, (cx, cy, 12.9), (cx, cy, 13.65), 3.3, CUPOLA, 'cupola'))
    for ang in (0.0, 55.0, -55.0, 125.0, -125.0):
        out.append(rot_block(F, cx, cy, np.deg2rad(ang), 2.75, 1.1, 1.8 if ang == 0 else 1.5, 13.0, 14.3, PERI,
                             'periscope'))
    out.append(cyl(F, (cx, cy, 13.4), (cx, cy, 14.0), 1.85, HATCH, 'hatch'))
    # TS's two dark lamps at the top of the back, at the rear door's corners
    for yc in (5.0, 17.0):
        out.append(B(F, 0.7, 1.4, yc - 0.55, yc + 0.55, 10.2, 11.0, LAMP, ch=0.08, name='rear_lamp'))
    # the driver's cab at the front of the roof (the reference art's; TS's dark block and slot there): its top with
    # TS's dark hatch, its front sloping down to the roof's front edge, the windscreen in it
    cab = [(29.0, 12.95), (35.1, 12.95), (33.1, 13.9), (29.0, 13.9)]
    out.append(prism(F, 1, cab, 8.6, 14.2, CAB, ch=0.1, name='cab'))
    out.append(B(F, 29.25, 31.0, 9.15, 13.0, 13.8, 14.05, BLOCK, ch=0.06, name='cab_hatch'))
    # the searchlight on the cab's right front corner (Westwood's FMV), pointing forwards
    out.append(cyl(F, (31.9, 9.3, 14.35), (32.9, 9.3, 14.35), 0.48, LIGHTHOUSE, 'searchlight'))
    out.append(cyl(F, (32.85, 9.3, 14.35), (33.0, 9.3, 14.35), 0.36, LENS, 'searchlight_lens'))
    # two lamps in square housings on the bow's front, on its left half (Westwood's FMV)
    for yc in (13.1, 15.5):
        out.append(B(F, 38.75, 39.2, yc - 0.75, yc + 0.75, 8.85, 10.35, LIGHTHOUSE, ch=0.08, name='lamp_housing'))
        out.append(cyl(F, (39.1, yc, 9.6), (39.32, yc, 9.6), 0.5, LENS, 'lamp'))
    # the vents on the rear shoulders, over the rear wheels (TS's darkest remap there, raised to the roof's edge)
    for x0, x1 in ((6.0, 11.0), (13.0, 18.0)):
        for left in (False, True):
            s = [(2.0, 11.4), (2.0, 12.25), (5.0, 13.2), (5.0, 12.4)]
            if left:
                s = [(mirror(y), z) for y, z in s][::-1]
            out.append(prism(F, 0, s, x0, x1, VENT, ch=0.1, name='vent'))
    return out


def lower_parts(F):
    """the parts below the waterline: the lower hull between the wheels, the panels between the wheel pairs, the
    bow's lower block, the block behind the rear wheels and its dark bumper, the six wheels."""
    out = []
    out.append(B(F, 4.0, 34.0, 5.0, 17.0, 3.0, 7.3, LOWER, ch=0.2, name='lower'))
    # the side panels between the rear pair and the front wheel (TS's side door there)
    out.append(B(F, 18.9, 24.0, 1.0, 21.0, 4.0, 7.4, SKIRT, ch=0.15, name='door_panel'))
    # the bow's lower block in front of the front wheel, its bottom sloping up to the stem
    p = B(F, 31.2, 39.0, 2.0, 20.0, 2.0, 7.4, BOW, ch=0.15, name='bow_lower')
    out.append(bow_planes(F, p))
    # the block behind the rear wheels down to the bumper, the bumper across the back (TS's dark band)
    out.append(B(F, 1.0, 4.6, 2.0, 20.0, 5.0, 7.6, REAR, ch=0.15, name='rear_block'))
    out.append(B(F, 0.0, 1.3, 2.0, 20.0, 4.0, 6.0, BUMPER, ch=0.12, name='bumper'))
    for xw in WHEELS:
        for y0, y1, yo in ((0.0, 5.0, 0.0), (17.0, 22.0, 22.0)):
            out.append(wheel(F, xw, Z_WHEEL, R_WHEEL, y0, y1, TYRE, 'tyre', bevel=0.45))
            # the hub on its outer face, a cap in its middle (s: outwards along y)
            s = -1.0 if yo == 0.0 else 1.0
            out.append(cyl(F, (xw, yo - 0.5 * s, Z_WHEEL), (xw, yo + 0.05 * s, Z_WHEEL), 2.45, HUB, 'hub'))
            out.append(cyl(F, (xw, yo - 0.3 * s, Z_WHEEL), (xw, yo + 0.2 * s, Z_WHEEL), 0.8, CAP, 'hub_cap'))
    return out


def model():
    up = upper_parts(FL)
    return {'land': up + lower_parts(FL), 'water': [p for p in up]}


def posed(m, which, Mx=np.eye(3)):
    """the named hull's parts posed and turned by Mx (unit frame -> world): (parts, frames, owner).  Both hulls are
    built in the land section's frame; the water hull is placed by APCW's HVA, moved by WATER_SHIFT."""
    R, t = FL.pose()
    if which == 'water':
        Rw_, tw_ = FW.pose()
        R, t = Rw_, tw_ + Rw_ @ WATER_SHIFT
    Rw, tw = Mx @ R, Mx @ t
    Mq = Rw @ np.diag(1.0 / FL.sc)
    tq = tw + Rw @ FL.mn
    parts, frames, owner = [], [], []
    for p in m[which]:
        parts.append(p.moved(Rw, tw)); frames.append((Mq, tq)); owner.append(which)
    return parts, frames, np.array(owner)
