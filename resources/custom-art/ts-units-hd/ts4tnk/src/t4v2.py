"""
t4v2.py - the Mammoth Mk. I (TS's unused [4TNK]) rebuilt the way the Titan, the Wolverine, the MCV and the Mk. II are:
TS's own voxels (4TNK.VXL hull, 4TNKTUR.VXL turret, 4TNKBARL.VXL barrels) as the blueprint for where every part is
and how big, each part modelled clean (flat plates, true slopes, round wheels and barrels, bevelled edges) in TS's
colours - house colour over nearly all of it, as TS left it (and as EA's HD Mammoths are) - with the detail of EA's
HD Mammoths where TS's voxels mark the place.

Each voxel file has one section with its own frame: q, continuous voxel coordinates (voxel i spans i..i+1), x forward,
y from the unit's right (0) to its left, z up; the section's local frame is min + q * scale (TS's), and its HVA
(frame 0) places it in the unit's frame (x forward, y left, z up; the unit's position at the origin).  TS's hull
sits 1.24 voxels above its HVA origin (its tracks' lowest voxels): as v1, the model is lowered onto the ground and
the camera raised to match, so every pixel stays where the mod's frames have it.

The hull (37 x 24 x 10 voxels: q x 0..37 back to front, y 0..24, z 0..10) is built symmetric about q y = 12, the
turret (24 x 24 x 15) about q y = 12, the barrels (22 x 10 x 4) as TS has them.
"""
import os, sys
from paths import HANDOFF
sys.path.insert(0, os.path.join(HANDOFF, 'renderer'))
import numpy as np
import vxl
import rc
from qparts import Frame, B, prism, hull, cyl, ball

D = os.path.join(HANDOFF, '05-TS4TNK', 'ts-original') + os.sep
GZ = 1.24                                           # TS's hull floats this far over its HVA origin (v1's find)

(HULL_C, COVER, SKIRT, DECKPLATE, BELT, WHEEL, HUB, CORE, RING, GRILLE, TAIL, HEAD, VENT, TURRET, CUPOLA, POD,
 POD_FRONT, TIP, ANTENNA, ANTBASE, SLEEVE, BARREL, COLLAR, MUZZLE, HATCH, LAMPHOUSE, MANTLET, DHATCH, PORT,
 ARM) = range(81, 111)
HOUSE = (HULL_C, COVER, SKIRT, DECKPLATE, TURRET, SLEEVE, COLLAR, MANTLET, DHATCH, PORT)


def _load(name):
    s = vxl.read_vxl(D + name + '.VXL')[0]
    names, mats = vxl.read_hva(D + name + '.HVA')
    return Frame(s, mats[0, 0])


FH, FT, FB = _load('4TNK'), _load('4TNKTUR'), _load('4TNKBARL')
HYC = 12.0                                          # the hull's centre line (q y)
TYC = 12.0                                          # the turret's


def mirror(y, c):
    return 2 * c - y


def yr_of(left, c):
    def yr(a, b):
        return (a, b) if not left else (mirror(b, c), mirror(a, c))
    return yr


def plane_q(F, n_q, q_point):
    """the half-space n . q <= n . q_point in q space, as a plane in the section's local frame."""
    n = np.asarray(n_q, float) / F.sc
    n = n / np.linalg.norm(n)
    return rc.Plane(n, n @ F.p(q_point))


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


# ------------------------------------------------------------------------------------------------ the hull
# per track unit: the belt's ends (wheel centres), its run on the ground, the road wheels (TS: two units a side,
# the belts on the ground at x 3..14 and 21..32)
UNITS = (dict(x0=2.0, x1=16.0, ends=(3.65, 14.35), ground=(4.6, 13.4), road=(6.4, 9.0, 11.6)),
         dict(x0=20.0, x1=34.0, ends=(21.65, 32.35), ground=(22.6, 31.4), road=(24.4, 27.0, 29.6)))
R_END, Z_END = 1.55, 1.75
R_ROAD, Z_ROAD = 1.05, 1.3
BELT_TOP = 3.8


def track_unit(U, left):
    F = FH
    yr = yr_of(left, HYC)
    out = []
    ea, eb = U['ends']
    ga, gb = U['ground']
    for xe in (ea, eb):
        out.append(wheel(F, xe, Z_END, R_END, *yr(0.2, 4.7), BELT, name='belt_end'))
        out.append(wheel(F, xe, Z_END, 0.85, *yr(0.05, 0.2), HUB, name='hub'))
    out.append(B(F, ea, eb, *yr(0.2, 4.7), BELT_TOP - 0.62, BELT_TOP, BELT, ch=(0.1, 0.0, 0.0), name='belt_top'))
    c70, s70 = np.cos(np.deg2rad(70)), np.sin(np.deg2rad(70))
    rl = Z_END - R_END * s70
    out.append(prism(F, 1, [(ea + R_END * c70, rl + 0.02), (ga, 0.0), (gb, 0.0), (eb - R_END * c70, rl + 0.02),
                            (eb - R_END * c70, 0.75), (ea + R_END * c70, 0.75)], *yr(0.2, 4.7), BELT, ch=0.1,
                     name='belt_bottom'))
    out.append(B(F, ea, eb, *yr(0.9, 4.7), 0.65, BELT_TOP - 0.6, CORE, name='core'))
    for xr in U['road']:
        out.append(wheel(F, xr, Z_ROAD, R_ROAD, *yr(0.45, 4.4), WHEEL, name='road', bevel=0.14))
    return out


def hull_parts():
    F = FH
    out = []
    for left in (False, True):
        yr = yr_of(left, HYC)
        for U in UNITS:
            out += track_unit(U, left)
            # the skirt over each unit (TS's green down to z 1 between the end wheels, the wheels' tops open)
            out.append(prism(F, 1, [(U['x0'] + 1.2, 1.25), (U['x1'] - 1.2, 1.25), (U['x1'] + 0.1, 2.6),
                                    (U['x1'] + 0.1, 3.4), (U['x0'] - 0.1, 3.4), (U['x0'] - 0.1, 2.6)],
                             *yr(-0.05, 0.6), SKIRT, ch=0.16, name='skirt'))
        # the long cover over both units (one green side, back to front as TS's): its ends slope, its top at 8
        out.append(prism(F, 1, [(0.2, 3.0), (36.2, 3.0), (36.2, 5.0), (34.6, 8.0), (0.7, 8.0), (0.2, 7.4)],
                         *yr(0.0, 4.95), COVER, ch=0.32, name='cover'))
        # the cover's underside between the units (dark)
        out.append(B(F, 15.6, 20.4, *yr(0.6, 4.6), 1.4, 3.05, CORE, name='gap'))
        # the tail lamps (TS's orange at the back of each cover) and the headlamps on the front of the hull
        out.append(B(F, -0.15, 0.4, *yr(1.9, 4.1), 4.8, 6.6, LAMPHOUSE, ch=0.12, name='tail_house'))
        out.append(B(F, -0.3, 0.0, *yr(2.15, 3.85), 5.05, 6.35, TAIL, name='tail'))
    # the hull between the covers: its front a glacis down to the nose, its back plate
    out.append(prism(F, 1, [(0.5, 2.6), (35.0, 2.6), (36.0, 3.8), (36.0, 5.0), (31.2, 8.0), (0.5, 8.0)], 4.85, 19.15,
                     HULL_C, ch=0.3, name='hull', edges=(True, True, True, True, True, True)))
    # the raised plate over the rear deck (TS's step at x 2..13) and the two caps on it (TS's white voxels)
    out.append(B(F, 1.8, 13.2, 5.6, 18.4, 7.9, 8.95, DECKPLATE, ch=0.3, name='deckplate'))
    for yc in (9.0, 15.0):
        out.append(cyl(F, (3.9, yc, 8.9), (3.9, yc, 9.35), 0.85, VENT, 'vent'))
    # the turret ring
    out.append(cyl(F, (19.0, HYC, 7.9), (19.0, HYC, 9.45), 6.2, RING, 'ring'))
    # the rear grille (TS's black panel between the tail lamps)
    out.append(B(F, -0.25, 0.55, 7.0, 17.0, 4.0, 7.8, GRILLE, ch=0.1, name='grille'))
    # the headlamps on the glacis (TS's grey pair) and their hoods
    for yc in (9.0, 15.0):
        out.append(B(F, 33.2, 35.2, yc - 1.15, yc + 1.15, 5.2, 6.9, LAMPHOUSE, ch=0.2, name='head_house'))
        out.append(cyl(F, (34.9, yc, 6.0), (35.45, yc, 6.0), 0.68, HEAD, 'headlamp'))
    # the front deck in front of the turret (Luke's models, the RA Mammoth's): a raised hex hatch on the left, a
    # round port on the right (TS's deck is plain house colour there)
    hexp = [(29.8 + 1.05 * np.cos(a), 15.6 + 1.05 * np.sin(a)) for a in np.deg2rad(np.arange(0.0, 360.0, 60.0))]
    out.append(prism(F, 2, hexp, 7.9, 8.24, DHATCH, ch=0.08, name='deck_hatch'))
    out.append(cyl(F, (30.0, 8.4, 7.9), (30.0, 8.4, 8.2), 0.85, PORT, 'deck_port'))
    return out


# ------------------------------------------------------------------------------------------------ the turret
def turret_parts():
    F = FT
    out = []
    # the body: a wide wedge, its front and back sloping, its top's edges chamfered (TS's steps); its back notched in
    # the middle (TS: the floor's back at x 3 between y 9 and 14, x 1 either side, where the antennas stand)
    sec = [(4.0, 0.0), (20.0, 0.0), (21.0, 1.0), (21.0, 3.9), (18.6, 6.0), (5.4, 6.0), (3.0, 3.9), (3.0, 1.0)]

    def body_part(back_x, name, extra=()):
        p = prism(F, 0, sec, 0.0, 23.2, TURRET, ch=0.0, name=name)
        p.cons.append(plane_q(F, (4.2, 0.0, 3.8), (23.2, 0.0, 1.4)))                 # the front glacis
        p.cons.append(plane_q(F, (-5.0, 0.0, 3.4), (back_x, 0.0, 1.0)))              # the sloping back
        p.cons.append(plane_q(F, (-1.0, 0.0, -1.0), (back_x + 1.0, 0.0, 0.0)))       # the floor's back edge
        p.cons.append(plane_q(F, (1.0, 0.0, -1.0), (23.0, 0.0, 0.0)))                # and its front edge
        # its sides taper towards the back (TS: y 3..21 at the front half, 4..20 at the back)
        p.cons.append(plane_q(F, (-1.0, -16.0, 0.0), (4.0, 4.0, 0.0)))
        p.cons.append(plane_q(F, (-1.0, 16.0, 0.0), (4.0, 20.0, 0.0)))
        # the front's corners cut back in plan (TS's front is a blunt chevron: its sides 2 voxels behind its middle)
        p.cons.append(plane_q(F, (5.5, -4.5, 0.0), (24.0, TYC - 2.5, 0.0)))
        p.cons.append(plane_q(F, (5.5, 4.5, 0.0), (24.0, TYC + 2.5, 0.0)))
        for n, q in extra:
            p.cons.append(plane_q(F, n, q))
        return p
    out.append(body_part(2.2, 'turret'))
    # the two rear lobes reaching back past the notch
    out.append(body_part(-0.4, 'turret_lobe', [((0, 1.0, 0), (0, TYC - 3.2, 0)), ((1.0, 0, 0), (7.0, 0, 0))]))
    out.append(body_part(-0.4, 'turret_lobe', [((0, -1.0, 0), (0, TYC + 3.2, 0)), ((1.0, 0, 0), (7.0, 0, 0))]))
    # the mantlet the barrels come out of (TS's block at the front middle)
    out.append(B(F, 19.6, 24.0, TYC - 2.4, TYC + 2.4, 0.2, 3.6, MANTLET, ch=0.35, name='mantlet'))
    # the commander's hatch on top: a raised block, TS's dark front on it
    out.append(B(F, 9.8, 18.6, TYC - 2.2, TYC + 2.2, 5.6, 7.0, TURRET, ch=0.35, name='hatchblock'))
    out.append(B(F, 15.4, 18.8, TYC - 1.9, TYC + 1.9, 6.0, 7.15, CUPOLA, ch=0.25, name='cupola'))
    # its round hatch (Luke's models: right of the dark plate's middle)
    out.append(cyl(F, (17.2, 11.55, 7.0), (17.2, 11.55, 7.32), 0.95, HATCH, 'hatch'))
    # the two antennas at the back
    for yc in (7.5, 16.5):
        out.append(cyl(F, (3.9, yc, 5.5), (3.9, yc, 7.2), 0.55, ANTBASE, 'antbase'))
        out.append(cyl(F, (3.9, yc, 7.0), (3.9, yc, 15.0), 0.34, ANTENNA, 'antenna'))
    # the tusk pods either side (TS's black boxes, grey tubes and orange missile tips at their fronts)
    for left in (False, True):
        yr = yr_of(left, TYC)
        pts = [(1.2, 1.7), (4.2, 1.7), (4.2, 7.0), (1.6, 7.0), (0.5, 5.9), (0.5, 2.4)]
        if left:
            pts = [(mirror(y, TYC), z) for y, z in pts][::-1]
        out.append(prism(F, 0, pts, 4.0, 12.3, POD, ch=0.3, name='pod'))
        out.append(B(F, 12.2, 12.9, *yr(0.8, 3.95), 2.0, 6.75, POD_FRONT, ch=0.12, name='pod_front'))
        # the arm joining it to the turret (TS's white block between them, x 8..10)
        out.append(B(F, 7.8, 10.2, *yr(3.4, 5.4), 2.0, 4.8, ARM, ch=0.15, name='pod_arm'))
        for yc in (1.6, 3.15):
            for zc in (3.2, 5.5):
                y0, y1 = yr(yc - 0.5, yc + 0.5)
                out.append(cyl(F, (12.7, (y0 + y1) / 2, zc), (13.2, (y0 + y1) / 2, zc), 0.5, TIP, 'tip'))
    return out


# ------------------------------------------------------------------------------------------------ the barrels
def barrel_parts():
    F = FB
    out = []
    for y0, y1 in ((0.0, 3.0), (7.0, 10.0)):
        yc = (y0 + y1) / 2
        out.append(B(F, 0.0, 9.0, y0 + 0.05, y1 - 0.05, 0.0, 4.0, SLEEVE, ch=0.3, name='sleeve'))
        out.append(cyl(F, (8.8, yc, 2.0), (22.0, yc, 2.0), 1.18, BARREL, 'barrel'))
        # the collar: a square block (TS's: 3 wide, 4 tall, as the sleeve; square on Luke's models too)
        out.append(B(F, 12.0, 15.0, y0 - 0.12, y1 + 0.12, -0.1, 4.1, COLLAR, ch=0.3, name='collar'))
        # a ring at the muzzle (Luke's models; TS's barrel runs straight to its end)
        out.append(cyl(F, (21.2, yc, 2.0), (22.0, yc, 2.0), 1.32, MUZZLE, 'muzzle'))
    return out


def model():
    return {'hull': hull_parts(), 'tur': turret_parts(), 'barl': barrel_parts()}


SECTIONS = {'hull': FH, 'tur': FT, 'barl': FB}


def posed(m, which, Mx=np.eye(3)):
    """the parts of the named sections posed (HVA frame 0, lowered by GZ) and turned by Mx (unit frame -> world):
    (parts, frames, owner) as hmec2.posed."""
    parts, frames, owner = [], [], []
    for k in which:
        F = SECTIONS[k]
        R, t = F.pose()
        t = t + np.array([0.0, 0.0, -GZ])
        Rw, tw = Mx @ R, Mx @ t
        Mq = Rw @ np.diag(1.0 / F.sc)
        tq = tw + Rw @ F.mn
        for p in m[k]:
            parts.append(p.moved(Rw, tw)); frames.append((Mq, tq)); owner.append(k)
    return parts, frames, np.array(owner)
