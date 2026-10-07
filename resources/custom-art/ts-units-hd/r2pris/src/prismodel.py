"""
prismodel.py - the Prism Tank (RA2's [SREF]; R2PRIS in the mod) rebuilt the way the Titan, the Wolverine, the Disruptor
and the Apocalypse are: RA2's own voxels (SREF.VXL the hull, SREFTUR.VXL the prism turret) as the blueprint for where
every part is and how big, each part modelled clean (flat plates, true slopes, round wheels, drums and rings, bevelled
edges) in RA2's colours: a blue-grey hull on two tracks of big road wheels; a raised armoured sponson each side at the
back, banded in house colour, sweeping in at its front to the turret ring; finned coolers and a round fan on the rear
deck; the turret ring a house-colour drum under stepped dark rings and an olive bearing; a periscope block and a cupola
on the front deck; the prism on its post: a quarter-round house-colour fan with a ribbed dark back, round hubs at its
sides, and the glowing emitter in a house-colour frame at its front (Westwood's art: the FMV and the renders Luke sent,
for how those parts read).

Each section has its own frame: q, continuous voxel coordinates (voxel i spans i..i+1), x back to front, y from the
unit's right (0) to its left, z up; the section's local frame is min + q * scale, and its HVA (frame 0, identity for
both) places it in the unit's frame.  The unit is raised 0.18 onto the ground (priscam.py).
"""
import os, sys
from paths import HANDOFF
sys.path.insert(0, os.path.join(HANDOFF, 'renderer'))
import numpy as np
import vxl
import rc
from qparts import Frame, B, prism, hull, cyl
from priscam import GZ, TUR_LIFT

D = os.path.join(HANDOFF, '28-R2PRIS', 'ra2-original') + os.sep

(BELT, WHEEL, HUB, GUARD, FENDER, SPONSON, ARMOUR, BODY, DECK, COOLER, FIN, FAN, RING_G, BUTTRESS, RING, BEARING,
 PERISCOPE, CUPOLA, POST, CRADLE, SIDEHUB, PRISM_G, RIB, FRAME_G, HOUSING, EMITTER) = range(81, 107)
HOUSE = (SPONSON, RING_G, BUTTRESS, PRISM_G, FRAME_G)


def _load(name, i):
    s = vxl.read_vxl(D + name + '.VXL')[i]
    names, mats = vxl.read_hva(D + name + '.HVA')
    return Frame(s, mats[0, i])


FH = _load('SREF', 0)
FT = _load('SREFTUR', 0)
HYC = 16.5                                           # the hull's centre line (q y): tracks 0..7 / 26..33


def mirror_y(y0, y1, c=HYC):
    return (y0, y1), (2 * c - y1, 2 * c - y0)


def fy(y, side):
    return y if side == 0 else 2 * HYC - y


# ---------------------------------------------------------------------------------------------------- the hull
# two tracks (SREF: y 0..7 and 26..33, x 5..44, z 0..7): black belts, their bottom and top runs, five big road wheels
# (SREF's wheels z 0..6) between, the sprocket and the idler at the ends; mudguards at both ends (z 7..9)
BELT_P = [(10.0, 0.0), (38.5, 0.0), (41.0, 1.6), (43.0, 3.8), (44.0, 6.0), (44.0, 7.2), (5.0, 7.2), (5.0, 4.5),
          (6.5, 2.4), (8.5, 0.8)]
RUN_LO = [(10.0, 0.0), (38.5, 0.0), (40.4, 1.0), (40.6, 1.4), (7.6, 1.4), (8.5, 0.8)]
WHEELS = (13.0, 18.4, 23.8, 29.2, 34.6)
WZ, WR = 3.4, 2.55
IDLERS = ((8.4, 3.9, 1.9), (40.0, 3.9, 1.9))


def tracks():
    out = []
    for side in (0, 1):
        y0, y1 = (0.0, 7.0) if side == 0 else (26.0, 33.0)
        sgn = -1.0 if side == 0 else 1.0
        outer = y0 if side == 0 else y1
        core = (y0 + 1.0, y1) if side == 0 else (y0, y1 - 1.0)
        out.append(prism(FH, 1, BELT_P, core[0], core[1], BELT, ch=0.25, name='belt'))
        out.append(prism(FH, 1, RUN_LO, y0, y1, BELT, ch=0.2, name='belt_run'))
        out.append(B(FH, 7.0, 42.4, y0, y1, 6.1, 7.2, BELT, ch=0.2, name='belt_top'))
        for xc in WHEELS:
            a, b = outer - sgn * 0.35, outer - sgn * 5.8
            out.append(cyl(FH, (xc, a, WZ), (xc, b, WZ), WR, WHEEL, 'wheel'))
            out.append(cyl(FH, (xc, a + sgn * 0.15, WZ), (xc, b, WZ), 0.9, HUB, 'wheel_hub'))
        for xc, zc, r in IDLERS:
            a, b = outer - sgn * 0.45, outer - sgn * 5.6
            out.append(cyl(FH, (xc, a, zc), (xc, b, zc), r, WHEEL, 'idler'))
            out.append(cyl(FH, (xc, a + sgn * 0.15, zc), (xc, b, zc), 0.75, HUB, 'wheel_hub'))
        # mudguards at the track's ends (SREF's black, z 7..9)
        out.append(hull(FH, [(4.6, y0, 7.2), (4.6, y1, 7.2), (10.2, y0, 7.2), (10.2, y1, 7.2), (5.4, y0, 9.6),
                             (5.4, y1, 9.6), (9.6, y0, 9.9), (9.6, y1, 9.9)], GUARD, 'mudguard'))
        out.append(hull(FH, [(36.0, y0, 7.2), (36.0, y1, 7.2), (44.2, y0, 7.2), (44.2, y1, 7.2), (37.0, y0, 9.9),
                             (37.0, y1, 9.9), (43.4, y0, 9.9), (43.4, y1, 9.9)], GUARD, 'mudguard'))
    return out


def sponsons():
    """the fender plate over each track (SREF: z 10..11, x 5..45), and at the back the raised sponson on it (x 1..32,
    y 0..8, z 11..14, banded in house colour all round, its front cut on the slant from x 28 at its outer edge to 32),
    the dark armour plate on top (x 6..26, y 2..8, z 14..16) whose nose sweeps down in house colour to the turret ring."""
    out = []
    for side in (0, 1):
        f = lambda y: fy(y, side)
        ys = lambda a, b: (min(f(a), f(b)), max(f(a), f(b)))
        out.append(B(FH, 4.6, 45.6, *ys(0.0, 8.0), 9.9, 11.0, FENDER, ch=0.2, name='fender'))
        pts = []
        for x, y in ((3.0, 0.0), (28.0, 0.0), (32.0, 3.6), (32.0, 8.0), (3.0, 8.0)):
            pts.append((x, f(y), 11.0))
        for x, y in ((1.0, 0.0), (28.0, 0.0), (32.0, 3.6), (32.0, 8.0), (1.0, 8.0)):
            pts.append((x, f(y), 14.0))
        pts += [(1.0, f(0.0), 11.9), (1.0, f(8.0), 11.9)]
        out.append(hull(FH, pts, SPONSON, 'sponson'))
        out.append(B(FH, 6.0, 26.2, *ys(2.0, 8.0), 13.9, 16.0, ARMOUR, ch=0.3, name='armour'))
        out.append(hull(FH, [(26.0, f(2.0), 13.9), (26.0, f(8.0), 13.9), (26.0, f(2.0), 16.0), (26.0, f(8.0), 16.0),
                             (29.0, f(2.0), 13.9), (29.0, f(2.0), 15.3), (32.0, f(8.0), 16.0), (34.0, f(8.0), 13.9),
                             (33.0, f(8.0), 15.2)], SPONSON, 'armour_nose'))
    return out


RING_C = (28.6, HYC)                                   # the turret ring's middle (q x, y)
FAN_C, FAN_R = (9.5, HYC), 4.3                         # the fan on the rear deck (SREF's round pit, x 4..15)
COOLERS = [(x0, x1, yc) for (x0, x1) in ((4.0, 10.2), (15.0, 21.2)) for yc in (8.7, 2 * HYC - 8.7)]
COOLER_Z, COOLER_R = 16.9, 1.95


def deck():
    out = []
    # the hull between the tracks (SREF: y 8..25, its floor at z 8, its deck at z 14, the glacis down to the nose at x 50,
    # z 9..10; the rear face sloping in below z 11)
    body = [(7.0, 8.0), (48.0, 8.0), (49.6, 9.0), (49.6, 10.6), (45.5, 13.4), (44.0, 14.0), (0.4, 14.0), (0.0, 13.6),
            (0.0, 11.0), (3.0, 9.5)]
    out.append(prism(FH, 1, body, 8.0, 25.0, BODY, ch=0.3, name='body'))
    # the rear deck plate (SREF's light deck, x 0..21, z 14..15) with the round fan let into it
    out.append(B(FH, 0.0, 21.2, 8.0, 25.0, 13.8, 15.0, DECK, ch=0.25, name='rear_deck'))
    out.append(cyl(FH, (FAN_C[0], FAN_C[1], 14.7), (FAN_C[0], FAN_C[1], 15.1), FAN_R, FAN, 'fan'))
    out.append(cyl(FH, (FAN_C[0], FAN_C[1], 15.0), (FAN_C[0], FAN_C[1], 15.45), 0.85, FAN, 'fan_hub'))
    # four finned coolers lying along the rear deck (SREF's dark blocks x 4..10 and 15..21, y 7..10 and 23..26,
    # z 15..19; Westwood's engine coolers)
    for x0, x1, yc in COOLERS:
        out.append(cyl(FH, (x0, yc, COOLER_Z), (x1, yc, COOLER_Z), COOLER_R - 0.45, COOLER, 'cooler'))
        for xf in np.arange(x0 + 0.45, x1 - 0.3, 0.62):
            out.append(cyl(FH, (xf, yc, COOLER_Z), (xf + 0.26, yc, COOLER_Z), COOLER_R, FIN, 'cooler_fin'))
        for xe in (x0, x1 - 0.5):
            out.append(cyl(FH, (xe, yc, COOLER_Z), (xe + 0.5, yc, COOLER_Z), COOLER_R + 0.12, COOLER, 'cooler_end'))
        out.append(B(FH, x0 + 0.6, x1 - 0.6, yc - 1.2, yc + 1.2, 14.6, COOLER_Z - 1.2, COOLER, ch=0.15,
                     name='cooler_cradle'))
    # the turret ring: a house-colour drum rising through the deck (SREF: radius 8.6, z 7..16), six buttresses round
    # it (Westwood's arches), stepped dark rings above (z 16..19) and the olive bearing on top (z 19..20)
    cx, cy = RING_C
    out.append(cyl(FH, (cx, cy, 7.5), (cx, cy, 15.8), 8.6, RING_G, 'ring_drum'))
    for k in range(6):
        a = np.deg2rad(30 + 60 * k)
        u = np.array([np.cos(a), np.sin(a)]); v = np.array([-u[1], u[0]])
        pts = []
        for r, z in ((8.2, 15.9), (8.2, 13.9), (10.0, 13.9), (9.4, 14.9)):
            for s in (-0.55, 0.55):
                p = np.array([cx, cy]) + r * u + s * v
                pts.append((p[0], p[1], z))
        out.append(hull(FH, pts, BUTTRESS, 'buttress'))
    out.append(cyl(FH, (cx, cy, 15.7), (cx, cy, 16.85), 7.3, RING, 'ring_step'))
    out.append(cyl(FH, (cx, cy, 16.8), (cx, cy, 17.95), 6.25, RING, 'ring_step'))
    out.append(cyl(FH, (cx, cy, 17.9), (cx, cy, 18.95), 5.1, RING, 'ring_step'))
    out.append(cyl(FH, (cx, cy, 18.9), (cx, cy, 19.95), 4.95, BEARING, 'bearing'))
    # the front deck: a periscope block on the right (SREF: x 38..44, y 10..15, z 14..15) and the commander's cupola on
    # the left (x 38..46, y 18..23, its top z 16)
    out.append(B(FH, 37.8, 43.6, 10.0, 15.0, 13.8, 15.1, PERISCOPE, ch=0.25, name='periscope'))
    out.append(B(FH, 42.6, 43.75, 10.6, 14.4, 14.0, 14.85, PERISCOPE, ch=0.1, name='periscope_glass'))
    out.append(B(FH, 38.0, 45.6, 18.0, 23.0, 13.8, 15.0, CUPOLA, ch=0.3, name='cupola_base'))
    out.append(cyl(FH, (41.6, 20.5, 14.8), (41.6, 20.5, 16.1), 2.35, CUPOLA, 'cupola'))
    out.append(cyl(FH, (41.6, 20.5, 16.0), (41.6, 20.5, 16.4), 1.6, CUPOLA, 'cupola_lid'))
    return out


def hull_parts():
    return tracks() + sponsons() + deck()


# ---------------------------------------------------------------------------------------------------- the prism
TYC = 4.0                                             # the turret's centre line (q y): post 1..7, fan 1..7, hubs 0..8
FAN_CT, FAN_RT = (14.6, 10.8), 10.6                    # the fan: a quarter disc (q x, z), its back and top edges
HUB_C = (8.6, 12.6)                                   # the round hubs at its sides (SREFTUR's discs at y 0 and 8)
EMIT = (16.25, 16.9, 2.05, 5.95, 12.9, 20.0)          # the emitter's face (SREFTUR's white, x 16, y 2..6, z 13..20)


RIB_R = (FAN_RT + 0.15, 15.0)                         # the ribbed back: SREFTUR's dark band round the fan, 4 voxels deep,
RIB_TOP = 21.3                                        # its top cut level with the fan's top (z 21)


def turret_parts():
    out = []
    # the post (SREFTUR's dark column, x 6..12, y 1..7, z 0..9) and its collar
    out.append(cyl(FT, (9.0, TYC, 0.0), (9.0, TYC, 9.2), 2.9, POST, 'post'))
    out.append(cyl(FT, (9.0, TYC, 8.5), (9.0, TYC, 9.4), 3.3, POST, 'post_collar'))
    # the cradle on it (z 9..11) and the arm forward under the emitter (x 13..18)
    out.append(B(FT, 5.6, 13.0, 0.9, 7.1, 9.0, 11.2, CRADLE, ch=0.3, name='cradle'))
    out.append(B(FT, 12.4, 17.4, 1.2, 6.8, 9.2, 11.1, CRADLE, ch=0.25, name='cradle_arm'))
    # the fan: a quarter disc of house colour standing across the turret (SREFTUR's green sides, y 1..7, from its foot at
    # x 4, z 11 round to its top at x 11..15, z 21)
    cx, cz = FAN_CT
    pts = [(cx, cz)] + [(cx + FAN_RT * np.cos(np.deg2rad(a)), cz + FAN_RT * np.sin(np.deg2rad(a)))
                        for a in np.linspace(180, 90, 10)]
    out.append(prism(FT, 1, pts, 1.0, 7.0, PRISM_G, ch=0.3, name='prism_fan'))
    # its ribbed back (SREFTUR's dark back, x 0..6, z 12..21): seven ribs round the arc from its foot (176 degrees, straight
    # back is 180) to where its top meets the fan's (118), gaps between them
    for a0 in np.arange(176.0, 118.0, -8.4):
        a1 = a0 - 6.6
        P = []
        for a in (a0, a1):
            for r in RIB_R:
                for y in (0.7, 7.3):
                    P.append((cx + r * np.cos(np.deg2rad(a)), y, min(cz + r * np.sin(np.deg2rad(a)), RIB_TOP)))
        out.append(hull(FT, P, RIB, 'rib'))
    # the round hubs at its sides, a boss on each
    for y0, y1, b0, b1 in ((0.0, 1.05, -0.3, 0.05), (6.95, 8.0, 7.95, 8.3)):
        out.append(cyl(FT, (HUB_C[0], y0, HUB_C[1]), (HUB_C[0], y1, HUB_C[1]), 3.3, SIDEHUB, 'side_hub'))
        out.append(cyl(FT, (HUB_C[0], b0, HUB_C[1]), (HUB_C[0], b1, HUB_C[1]), 1.5, SIDEHUB, 'side_hub_boss'))
    # the emitter: its dark housing in a house-colour frame (SREFTUR's green at y 1, 6 and on top), the glowing face
    out.append(B(FT, 13.8, 16.35, 1.85, 6.15, 10.9, 20.6, HOUSING, ch=0.15, name='emitter_housing'))
    for (ya, yb) in ((1.0, 1.9), (6.1, 7.0)):
        out.append(B(FT, 13.6, 16.8, ya, yb, 10.9, 21.8, FRAME_G, ch=0.18, name='emitter_frame'))
    out.append(B(FT, 13.6, 16.8, 1.0, 7.0, 20.5, 21.8, FRAME_G, ch=0.2, name='emitter_frame'))
    out.append(B(FT, 16.2, 16.8, 1.85, 6.15, 12.3, 12.95, HOUSING, ch=0.08, name='emitter_sill'))
    x0, x1, y0, y1, z0, z1 = EMIT
    out.append(B(FT, x0, x1, y0, y1, z0, z1, EMITTER, ch=0.05, name='emitter'))
    return out


def model():
    return {'hull': hull_parts(), 'tur': turret_parts()}


SECTIONS = {'hull': FH, 'tur': FT}
# each section centred side to side on the unit's position (as the Disruptor's and the Apocalypse's): RA2's hull sits
# 0.05 voxel right of it, the prism 0.16 left of its pivot; the turret turns about its own middle.  The turret is lifted
# TUR_LIFT as the mod's frames draw it (priscam.py)
_MID = {'hull': (0.0, HYC, 0.0), 'tur': (0.0, TYC, 0.0)}
SHIFT = {k: np.array([0.0, -float(F.p(_MID[k])[1]), -GZ + (TUR_LIFT if k == 'tur' else 0.0)]) for k, F in SECTIONS.items()}


def pose(k):
    R, t = SECTIONS[k].pose()
    return R, t + SHIFT[k]


def posed(m, which, Mx=np.eye(3)):
    parts, frames, owner = [], [], []
    for k in which:
        F = SECTIONS[k]
        R, t = pose(k)
        Rw, tw = Mx @ R, Mx @ t
        Mq = Rw @ np.diag(1.0 / F.sc)
        tq = tw + Rw @ F.mn
        for p in m[k]:
            parts.append(p.moved(Rw, tw)); frames.append((Mq, tq)); owner.append(k)
    return parts, frames, np.array(owner)
