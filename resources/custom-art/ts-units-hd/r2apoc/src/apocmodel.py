"""
apocmodel.py - the Apocalypse Tank (RA2's [APOC], art MTNK; R2APOC in the mod) rebuilt the way the Titan, the Wolverine
and the Disruptor are: RA2's own voxels (MTNK.VXL the hull, MTNKTUR.VXL the turret, MTNKBARL.VXL the twin barrels) as
the blueprint for where every part is and how big, each part modelled clean (flat plates, true slopes, round wheels,
drums and tubes, bevelled edges) in RA2's colours: an olive hull on four track pods, house-colour fuel drums on the
rear fenders, dark engine grilles, a toothed plough on two rams at the nose; a light olive turret on a house-colour
skirt, a round hatch on top, two whip antennas at its back, a 4-tube rocket pod each side angled up and forward, the
twin barrels with muzzle brakes (Westwood's art: the FMV, the cameo, the in-game model, for how those parts read).

Each section has its own frame: q, continuous voxel coordinates (voxel i spans i..i+1), x back to front, y from the
unit's right (0) to its left, z up; the section's local frame is min + q * scale, and its HVA (frame 0, identity for
all three) places it in the unit's frame.  The unit is lowered GZ onto the ground (apoccam.py).
"""
import os, sys
from paths import HANDOFF
sys.path.insert(0, os.path.join(HANDOFF, 'renderer'))
import numpy as np
import vxl
import rc
from qparts import Frame, B, prism, hull, cyl
from apoccam import GZ

D = os.path.join(HANDOFF, '27-R2APOC', 'ra2-original') + os.sep

(OLIVE, BELT, WHEEL, HUB, GREEN, DRUM, GRILLE, BLACK, LAMP, PLOUGH, RAM, TUR, SKIRT, HATCH, AERIAL, POD, TUBE,
 STRAP, MOUNT, BARREL, SLEEVE, MUZZLE, MANTLET, HOOK) = range(81, 105)
HOUSE = (GREEN, DRUM, SKIRT)


def _load(name, i):
    s = vxl.read_vxl(D + name + '.VXL')[i]
    names, mats = vxl.read_hva(D + name + '.HVA')
    return Frame(s, mats[0, i])


FH = _load('MTNK', 0)
FT = _load('MTNKTUR', 0)
FB = _load('MTNKBARL', 0)
HYC = 16.0                                           # the hull's centre line (q y): tracks 1..8 / 24..31, body 7..25


def my(y0, y1, c=HYC):
    return (y0, y1), (2 * c - y1, 2 * c - y0)


def ellipse(cx, cz, rx, rz, n=24):
    return [(cx + rx * np.cos(2 * np.pi * k / n), cz + rz * np.sin(2 * np.pi * k / n)) for k in range(n)]


# ---------------------------------------------------------------------------------------------------- the hull
# four track pods (MTNK: the rear pair x 5..28, the front pair x 30..49, y 1..8 and 24..31): black belts, their bottom
# run (z 0..2) under the grey road wheels (z 2..4; 4 at the back, 3 at the front), the idlers rising to the fenders
BELT_REAR = [(7.0, 0.0), (25.0, 0.0), (26.3, 1.2), (27.7, 4.0), (27.7, 7.0), (5.1, 7.0), (5.1, 4.0), (5.9, 1.2)]
BELT_FRONT = [(32.0, 0.0), (46.0, 0.0), (47.2, 1.2), (48.4, 4.0), (48.4, 6.6), (30.0, 6.6), (30.0, 4.0), (31.0, 1.2)]
RUN_REAR = [(7.0, 0.0), (25.0, 0.0), (26.0, 1.0), (26.2, 1.6), (5.8, 1.6), (6.0, 1.0)]
RUN_FRONT = [(32.0, 0.0), (46.0, 0.0), (46.9, 1.0), (47.1, 1.6), (30.9, 1.6), (31.1, 1.0)]
WHEELS_REAR = (10.0, 14.0, 18.0, 22.4)
WHEELS_FRONT = (34.2, 39.0, 43.8)
IDLERS = ((6.7, 4.9), (26.2, 4.9), (31.6, 4.7), (46.8, 4.7))
WZ, WR = 3.0, 1.55


def track_pods():
    out = []
    # the rear pods y 1..8 (and 24..31), the front pods narrower: y 3..8 (24..29), MTNK's
    for belt, run, wheels, idlers, (ya, yb) in ((BELT_REAR, RUN_REAR, WHEELS_REAR, IDLERS[:2], (1.0, 8.0)),
                                                 (BELT_FRONT, RUN_FRONT, WHEELS_FRONT, IDLERS[2:], (3.0, 8.0))):
        for (y0, y1) in my(ya, yb):
            sgn = -1.0 if y0 < HYC else 1.0
            out_face = y0 if sgn < 0 else y1                  # the pod's outer face
            core = (y0 + 0.8, y1) if sgn < 0 else (y0, y1 - 0.8)
            out.append(prism(FH, 1, belt, core[0], core[1], BELT, ch=0.25, name='belt'))
            out.append(prism(FH, 1, run, y0, y1, BELT, ch=0.2, name='belt_run'))
            for xc in wheels:
                a, b = out_face - sgn * 0.15, out_face - sgn * 1.0
                out.append(cyl(FH, (xc, a, WZ), (xc, b, WZ), WR, WHEEL, 'wheel'))
                out.append(cyl(FH, (xc, a + sgn * 0.12, WZ), (xc, b, WZ), 0.55, HUB, 'wheel_hub'))
            for xc, zc in idlers:
                a, b = out_face - sgn * 0.25, out_face - sgn * 1.0
                out.append(cyl(FH, (xc, a, zc), (xc, b, zc), 1.45, WHEEL, 'idler'))
                out.append(cyl(FH, (xc, a + sgn * 0.12, zc), (xc, b, zc), 0.5, HUB, 'wheel_hub'))
    return out


def fenders():
    """the fenders over the tracks: at the back full width (y 0..8, x 3..30) - a low outer plate (z 8..9) with a lip
    down to z 7 at its edge, the inner plate a step higher (z 9..10) - and over the front pods narrower (y 2..8, x 30..46),
    sloping down at the front to a mudguard (z 5 at x 49)."""
    out = []
    for side in (0, 1):
        f = (lambda y: y) if side == 0 else (lambda y: 2 * HYC - y)
        def ys(a, b):
            return (min(f(a), f(b)), max(f(a), f(b)))
        # the rear fender's outer plate and lip (a prism along x), its back end sloping down to z 6 (MTNK's x 3)
        pts = [(f(0.0), 7.0), (f(0.9), 7.0), (f(3.6), 8.0), (f(3.6), 9.0), (f(0.0), 9.0)]
        if side == 1:
            pts = pts[::-1]
        out.append(prism(FH, 0, pts, 3.0, 30.0, OLIVE, ch=0.15, name='fender_outer'))
        out.append(B(FH, 3.0, 30.0, *ys(3.4, 8.2), 8.6, 10.0, OLIVE, ch=0.2, name='fender'))
        out.append(B(FH, 30.0, 46.0, *ys(2.0, 8.2), 8.0, 10.0, OLIVE, ch=0.2, name='fender'))
        out.append(B(FH, 30.0, 46.0, *ys(2.0, 2.9), 7.0, 8.2, OLIVE, ch=0.1, name='fender_lip'))
        nose = [(45.5, 8.0), (48.8, 5.2), (49.6, 5.2), (49.6, 6.0), (46.0, 10.0)]
        out.append(prism(FH, 1, nose, *ys(2.0, 8.2), OLIVE, ch=0.15, name='fender_nose'))
        # small dark fittings on the fenders against the hull (MTNK's dark voxels at x 23-24, 32-34, 43-44)
        for xa, xb in ((23.0, 24.8), (32.4, 34.4), (43.0, 44.8)):
            out.append(B(FH, xa, xb, *ys(4.0, 7.0), 9.8, 11.0, LAMP, ch=0.2, name='fitting'))
    return out


def drums():
    """the four fuel drums on the rear fenders (MTNK's house colour, x 4..10 and 11..17, y 0..8, z 9..14), lying across
    the hull, two hoops round each (MTNK's ridges at y 2..4, 5..7; Westwood's red drums)."""
    out = []
    for (y0, y1) in my(0.1, 7.9):
        for xc in (7.0, 14.0):
            out.append(prism(FH, 1, ellipse(xc, 11.25, 2.85, 2.25), y0, y1, DRUM, ch=0.45, name='drum'))
            for ya, yb in ((2.25, 3.75), (5.25, 6.75)):
                ya, yb = (ya, yb) if y0 < HYC else (2 * HYC - yb, 2 * HYC - ya)
                out.append(prism(FH, 1, ellipse(xc, 11.25, 3.05, 2.55), ya, yb, DRUM, ch=0.15, name='drum_hoop'))
    return out


GLACIS = ((45.0, 12.0), (52.8, 8.0))                  # the glacis' top and bottom edges (q x, z)


def glacis_z(x):
    (x0, z0), (x1, z1) = GLACIS
    return z0 + (x - x0) * (z1 - z0) / (x1 - x0)


def plough():
    """the toothed plough across the nose (MTNK: a zig-zag blade at z 4..6, x 52..59, y 5..27; Westwood's: a black
    blade of jagged teeth) on two rams running forward under the hull (y 11 and 21, from brackets at x 42..46).
    v2.1 (Luke: sharp and menacing, not a flat bumper bar): the blade is chiselled - tall at its back (z 4.2..6.6), its
    top sloping down to a knife edge at its front (z 4.4..4.8) - and seven spikes come off its front edge, tapering to
    points angled forward and down: the longest at the middle, one at each end swept outward, two on each flank."""
    out = []
    path = [(55.2, 5.4), (53.3, 8.3), (54.5, 11.0), (56.4, 13.6), (57.2, 16.0)]
    full = path + [(x, 2 * HYC - y) for x, y in path[::-1][1:]]
    w = 1.9
    for (xa, ya), (xb, yb) in zip(full[:-1], full[1:]):
        d = np.array([xb - xa, yb - ya]); L = np.linalg.norm(d); d = d / L
        n = np.array([-d[1], d[0]])
        if n[0] < 0:
            n = -n                                        # n: the blade's front, forward
        e = d * 0.45
        pts = []
        for (px, py) in ((xa - e[0], ya - e[1]), (xb + e[0], yb + e[1])):
            bx, by = px - n[0] * w / 2, py - n[1] * w / 2     # the back edge: tall
            fx, fy = px + n[0] * w / 2, py + n[1] * w / 2     # the front edge: a knife edge
            pts += [(bx, by, 4.2), (bx, by, 6.6), (fx, fy, 4.4), (fx, fy, 4.8)]
        out.append(hull(FH, pts, PLOUGH, 'plough'))
    # the spikes: (base on the blade's front edge, direction in plan, length)
    spikes = [((57.9, 16.0), (1.0, 0.0), 3.3),
              ((55.7, 11.9), (0.86, -0.51), 2.4), ((55.7, 2 * HYC - 11.9), (0.86, 0.51), 2.4),
              ((55.6, 4.9), (0.62, -0.78), 2.6), ((55.6, 2 * HYC - 4.9), (0.62, 0.78), 2.6),
              ((54.2, 8.4), (0.93, -0.36), 1.7), ((54.2, 2 * HYC - 8.4), (0.93, 0.36), 1.7)]
    for (bx, by), (dx, dy), L in spikes:
        dd = np.array([dx, dy]) / np.hypot(dx, dy); nn = np.array([-dd[1], dd[0]])
        hw, z0, z1 = 0.95, 4.15, 6.0
        base = [(bx - 0.6 * dd[0] + s * hw * nn[0], by - 0.6 * dd[1] + s * hw * nn[1], z) for s in (-1, 1)
                for z in (z0, 5.0)]
        base += [(bx - 0.9 * dd[0], by - 0.9 * dd[1], z1)]          # a ridge along its top, back to the blade's spine
        tip = (bx + L * dd[0], by + L * dd[1], 3.75)
        out.append(hull(FH, base + [tip], PLOUGH, 'spike'))
    for yc in (11.0, 2 * HYC - 11.0):
        out.append(B(FH, 41.6, 46.2, yc - 1.0, yc + 1.0, 3.9, 5.4, BLACK, ch=0.2, name='ram_bracket'))
        out.append(cyl(FH, (42.0, yc, 4.75), (53.8, yc, 4.95), 0.62, RAM, 'ram'))
        out.append(cyl(FH, (45.8, yc, 4.75), (49.0, yc, 4.8), 0.85, BLACK, 'ram_barrel'))
    return out


def hull_parts():
    out = track_pods() + fenders() + drums() + plough()
    # the hull between the pods (MTNK: y 7..25, its belly at z 5, its deck at z 12 from x 6 to 45, the glacis down to the
    # nose at x 53, z 7..8, the rear face at x 5)
    body = [(7.0, 5.0), (51.0, 5.0), (52.8, 7.2), (52.8, 8.0), GLACIS[0], (6.0, 12.0), (5.0, 11.0), (5.0, 6.8)]
    out.append(prism(FH, 1, body, 7.0, 25.0, OLIVE, ch=0.3, name='body'))
    # the engine grilles on the rear deck (MTNK's dark panels x 9..17, y 9..15 and 17..23) and the radiator grille across
    # the rear face (x 5, y 9..23, z 7..11): dark, louvred (materials)
    for (y0, y1) in ((9.0, 15.0), (17.0, 23.0)):
        out.append(B(FH, 9.0, 17.0, y0, y1, 11.6, 12.12, GRILLE, ch=0.08, name='deck_grille'))
    out.append(B(FH, 4.8, 5.4, 9.0, 23.0, 7.0, 10.8, GRILLE, ch=0.06, name='rear_grille'))
    # two round hatches on the glacis (MTNK's dark blocks x 46..51, y 10..14 and 17..21; Westwood's round covers)
    (x0, z0), (x1, z1) = GLACIS
    t = np.array([x1 - x0, 0.0, z1 - z0]); t /= np.linalg.norm(t)
    nrm = np.array([-t[2], 0.0, t[0]])
    for yc in (12.0, 20.0):
        c = np.array([48.6, yc, glacis_z(48.6)])
        out.append(cyl(FH, tuple(c - 0.3 * nrm), tuple(c + 0.75 * nrm), 2.0, HATCH, 'glacis_hatch'))
        out.append(cyl(FH, tuple(c + 0.7 * nrm), tuple(c + 0.95 * nrm), 1.25, HATCH, 'glacis_hatch_top'))
    return out


# ---------------------------------------------------------------------------------------------------- the turret
TYC = float(FT.q((0.0, 0.0, 0.0))[1])                 # the turret's centre line (q y 12.41: its pivot): RA2's shell (skirt
                                                      # 3..21, top 5..19) sits 0.4 voxel right of it, the pods on it

L0 = [(5.4, 5.2), (11.0, 4.0), (22.0, 4.0), (25.0, 8.5), (25.0, 15.5), (22.0, 20.0), (11.0, 20.0), (5.4, 18.8)]
L1 = [(4.2, 4.6), (9.0, 3.0), (22.0, 3.0), (25.0, 8.0), (25.0, 16.0), (22.0, 21.0), (9.0, 21.0), (4.2, 19.4)]
L2 = [(3.0, 5.0), (8.0, 4.2), (21.0, 4.2), (23.6, 8.5), (23.6, 15.5), (21.0, 19.8), (8.0, 19.8), (3.0, 19.0)]
L3 = [(2.0, 5.2), (20.2, 5.2), (22.2, 8.4), (22.2, 15.6), (20.2, 18.8), (2.0, 18.8)]
ZL = (0.0, 2.4, 4.6, 7.0)

POD_C = (10.5, 6.0)                                   # the rocket pods' middle (q x, z), their axis 43 degrees up
POD_A = np.deg2rad(43.0)
POD_S = (-4.4, 4.1)                                   # along the axis from the middle
POD_Y = (2.6, 2 * TYC - 2.6)                          # their middles across (q y; MTNKTUR's 0..5 and 19..25)
TUBE_R, TUBE_D = 1.12, 1.18                           # each tube's radius, and its offset from the pod's axis
AERIALS = (8.0, 2 * TYC - 8.0)                                 # the whip antennas (q y; MTNK's x 0..3, z 6..17, leaning back)


def pod_axis():
    return np.array([np.cos(POD_A), 0.0, np.sin(POD_A)]), np.array([-np.sin(POD_A), 0.0, np.cos(POD_A)])


def pod_parts(yc):
    u, v = pod_axis()
    c = np.array([POD_C[0], yc, POD_C[1]])
    out = []
    for a in (-1, 1):
        for b in (-1, 1):
            o = c + a * TUBE_D * v + np.array([0.0, b * TUBE_D, 0.0])
            out.append(cyl(FT, tuple(o + POD_S[0] * u), tuple(o + POD_S[1] * u), TUBE_R, TUBE, 'tube'))
    # two straps round the bundle and a back plate; the mount it turns on, into the turret's side
    for s0, s1 in ((-3.2, -2.4), (1.9, 2.7)):
        pts = []
        for s in (s0, s1):
            for a in (-1, 1):
                for b in (-1, 1):
                    pts.append(tuple(c + s * u + a * (TUBE_D + TUBE_R + 0.12) * v + np.array([0.0, b * (TUBE_D + TUBE_R + 0.12), 0.0])))
        out.append(hull(FT, pts, STRAP, 'pod_strap'))
    pts = []
    for s in (POD_S[0] - 0.3, POD_S[0] + 0.25):
        for a in (-1, 1):
            for b in (-1, 1):
                pts.append(tuple(c + s * u + a * (TUBE_D + TUBE_R) * v + np.array([0.0, b * (TUBE_D + TUBE_R), 0.0])))
    out.append(hull(FT, pts, STRAP, 'pod_back'))
    yin = TYC - 7.2 if yc < TYC else TYC + 7.2
    out.append(cyl(FT, (9.6, yc, 5.6), (9.6, yin, 5.6), 1.5, MOUNT, 'pod_mount'))
    out.append(cyl(FT, (9.6, yc + (1.0 if yc < TYC else -1.0) * 0.3, 5.6),
                   (9.6, yin + (0.4 if yc < TYC else -0.4), 5.6), 2.0, MOUNT, 'pod_mount_ring'))
    return out


def turret_parts():
    out = []
    dy = TYC - 12.0                                   # the shell centred on the pivot
    lv = lambda L, z: [(x, y + dy, z) for x, y in L]
    # the house-colour skirt (MTNKTUR's green, z 0..4.6: widest at z 1..3, its front sloping forward to x 25, its back
    # undercut) and the light olive top (z 4.6..7: its front at x 22, its back at x 2.6)
    out.append(hull(FT, lv(L0, ZL[0]) + lv(L1, ZL[1]) + lv(L2, ZL[2]), SKIRT, 'skirt'))
    out.append(hull(FT, lv(L2, ZL[2]) + lv(L3, ZL[3]), TUR, 'turret'))
    # the round hatch on top (MTNKTUR's dark x 10..16, y 9..15; Westwood's: a ring with notches round a lid)
    out.append(cyl(FT, (13.0, TYC, 6.8), (13.0, TYC, 7.75), 3.0, HATCH, 'cupola'))
    out.append(cyl(FT, (13.0, TYC, 7.7), (13.0, TYC, 8.15), 2.05, HATCH, 'cupola_lid'))
    out.append(cyl(FT, (13.0, TYC, 8.1), (13.0, TYC, 8.4), 0.75, HATCH, 'cupola_boss'))
    # the whip antennas at the back corners (MTNKTUR's x 0..3, z 6..17), on mounts
    for yc in AERIALS:
        out.append(B(FT, 2.0, 4.4, yc - 0.95, yc + 0.95, 6.4, 7.6, HATCH, ch=0.2, name='aerial_mount'))
        out.append(cyl(FT, (3.1, yc, 7.4), (2.6, yc, 8.6), 0.55, AERIAL, 'aerial_base'))
        out.append(cyl(FT, (2.7, yc, 8.4), (0.6, yc, 17.0), 0.26, AERIAL, 'aerial'))
    # two hooks at the back (MTNKTUR's grey voxels)
    for yc in AERIALS:
        out.append(B(FT, 1.5, 2.5, yc - 0.6, yc + 0.6, 4.4, 5.4, HOOK, ch=0.15, name='hook'))
    for yc in POD_Y:
        out += pod_parts(yc)
    return out


# ---------------------------------------------------------------------------------------------------- the barrels
BAR_Y = (1.5, 10.5)                                   # MTNKBARL's two barrels (q y; z 0..3, x 0..27)
BAR_Z = 1.5


def barrel_parts():
    out = []
    for yc in BAR_Y:
        c = lambda x: (x, yc, BAR_Z)
        out.append(B(FB, 1.6, 5.4, yc - 2.05, yc + 2.05, BAR_Z - 2.0, BAR_Z + 2.0, MANTLET, ch=0.45, name='mantlet'))
        out.append(cyl(FB, c(4.0), c(9.2), 1.55, SLEEVE, 'barrel_root'))
        out.append(cyl(FB, c(9.0), c(9.7), 1.68, SLEEVE, 'barrel_collar'))
        out.append(cyl(FB, c(9.6), c(24.4), 1.32, BARREL, 'barrel'))
        out.append(cyl(FB, c(24.2), c(26.9), 1.66, MUZZLE, 'muzzle'))
        out.append(cyl(FB, c(26.85), c(27.15), 1.5, MUZZLE, 'muzzle_lip'))
    return out


def model():
    return {'hull': hull_parts(), 'tur': turret_parts(), 'barl': barrel_parts()}


SECTIONS = {'hull': FH, 'tur': FT, 'barl': FB}
# each section centred side to side on the unit's position (as the Disruptor's v5): RA2's hull sits 0.1 voxel left of it,
# the barrels 0.1 left; the turret is centred on its pivot in the model (its shell, TYC)
_MID = {'hull': (0.0, HYC, 0.0), 'tur': (0.0, TYC, 0.0), 'barl': (0.0, sum(BAR_Y) / 2, 0.0)}
SHIFT = {k: np.array([0.0, -float(F.p(_MID[k])[1]), -GZ]) for k, F in SECTIONS.items()}


def pose(k):
    """a section's pose in the unit's frame: RA2's HVA (frame 0), the unit lowered onto the ground."""
    R, t = SECTIONS[k].pose()
    return R, t + SHIFT[k]


def posed(m, which, Mx=np.eye(3)):
    """the parts of the named sections posed (pose()) and turned by Mx (unit frame -> world): (parts, frames, owner)."""
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
