"""
mempmodel.py - the Mobile EMP Cannon (TS's [MOBILEMP], Firestorm; TSMEMP in the mod) rebuilt the way the Titan, the
Wolverine, the Disruptor and the Dropship are: TS's own voxel (M_EMP.VXL, one section, posed by its HVA) is the
blueprint for where every part is and how big, each part modelled clean (flat plates, true slopes, round wheels and
pipes, bevelled edges) in TS's colours - the dark ochre hull, the grey emitter tower and conduits, the house-colour
track covers - with Westwood's Firestorm icon and the HD render Luke sent as the guide to how TS's parts read in HD
(the emitter's glowing orb on its plinth, the ribbed conduits, the hatch box).

q: TS's voxel coordinates, continuous (voxel i spans i..i+1): x back to front 0..36, y from the unit's right (0) to
its left 0..29, z up 0..18; the section's local frame is min + q * scale (TS's), its HVA (frame 0) places it in the
unit's frame, and the model is lowered GZ onto the ground (mempcam.py).  TS's layout: a U - two track pods (y 0..5,
24..29) the whole length, joined by the hull (the deck, x 12..34) at the front; the U opens backwards between them.
"""
import os, sys
from paths import HANDOFF
sys.path.insert(0, os.path.join(HANDOFF, 'renderer'))
import numpy as np
import vxl
import rc
from qparts import Frame, B, prism, hull, cyl, ball
from mempcam import GZ

D = os.path.join(HANDOFF, '13-TSMEMP', 'ts-original') + os.sep

(BELT, WHEEL, HUB, HOUSING, FENDER, DECK, LEDGE, LIP, TOWER, COLLAR, ORB, CROWN, PLINTH, BOX, PIPE, MOUNT, EMITTER,
 SLOT, GLASS) = range(81, 100)
HOUSE = (FENDER,)


def _load(name, i):
    s = vxl.read_vxl(D + name + '.VXL')[i]
    names, mats = vxl.read_hva(D + name + '.HVA')
    return Frame(s, mats[0, i])


FH = _load('M_EMP', 0)
HYC = 14.5                                          # the hull's centre line (q y): the pods are 0..5 and 24..29
PODS = ((0.0, 5.0), (24.0, 29.0))
EMITTERS = os.environ.get('MEMP_EMITTERS', '0') == '1'   # the glowing capsules along the covers (Westwood's icon)


def mirror(y0, y1, c=HYC):
    return (y0, y1), (2 * c - y1, 2 * c - y0)


# ---------------------------------------------------------------- the track pods
# TS's tracks (y 0..5 and 24..29): a belt round an idler at the back and a sprocket at the front (TS: their light grey
# faces at x 1..5 and 30..35, z 2..5), its bottom run z 0..1 from x 6 to 30, its top run at z 5..6; six road wheels
# between the runs (TS: light grey pairs at x 6..30, z 2..4, seen through the open side); grey housings at both ends
# above the belt (TS: x 0..10 and 25..36, z 6..8) under the cover
IDLER, SPROCKET, END_R, END_Z = 3.3, 32.7, 2.15, 3.25
WHEELS_X = [7.6, 11.9, 16.2, 20.5, 24.8, 29.1]
WHEEL_R, WHEEL_Z = 1.42, 2.15


def pod_parts():
    out = []
    for (y0, y1) in PODS:
        ym = (y0 + y1) / 2
        # the belt: its runs and its two ends wrapped round the idler and the sprocket, a dark core inside
        out.append(B(FH, IDLER, SPROCKET, y0 + 0.25, y1 - 0.25, 5.15, 6.35, BELT, ch=0.15, name='belt_top'))
        out.append(B(FH, 6.0, 30.0, y0 + 0.25, y1 - 0.25, 0.0, 1.05, BELT, ch=0.15, name='belt_bottom'))
        out.append(prism(FH, 1, [(IDLER, 0.6), (6.6, 0.0), (29.4, 0.0), (SPROCKET, 0.6), (SPROCKET, 5.6),
                                 (IDLER, 5.6)], y0 + 1.25, y1 - 1.25, BELT, name='belt_core'))
        for xc in (IDLER, SPROCKET):
            out.append(cyl(FH, (xc, y0 + 0.25, END_Z), (xc, y1 - 0.25, END_Z), END_R + 0.95, BELT, 'belt_end'))
            out.append(cyl(FH, (xc, y0 - 0.06, END_Z), (xc, y1 + 0.06, END_Z), END_R, WHEEL, 'sprocket'))
            for ya, yb in ((y0 - 0.16, y0 + 0.2), (y1 - 0.2, y1 + 0.16)):
                out.append(cyl(FH, (xc, ya, END_Z), (xc, yb, END_Z), 0.85, HUB, 'hub'))
        for xw in WHEELS_X:
            out.append(cyl(FH, (xw, y0 + 0.45, WHEEL_Z), (xw, y1 - 0.45, WHEEL_Z), WHEEL_R, WHEEL, 'road_wheel'))
            for ya, yb in ((y0 + 0.3, y0 + 0.6), (y1 - 0.6, y1 - 0.3)):
                out.append(cyl(FH, (xw, ya, WHEEL_Z), (xw, yb, WHEEL_Z), 0.55, HUB, 'hub'))
        # the housings at the ends above the belt, under the cover (TS's grey and dark voxels)
        out.append(B(FH, 0.55, 10.6, y0 + 0.1, y1 - 0.1, 5.7, 8.05, HOUSING, ch=0.25, name='housing'))
        out.append(B(FH, 24.4, 35.45, y0 + 0.1, y1 - 0.1, 5.7, 8.05, HOUSING, ch=0.25, name='housing'))
        # the cover, house colour (TS: z 8 the whole length x 2..34, its skirt down to z 7 over the middle,
        # x 7..29 underneath and x 11..24 on the outer side)
        out.append(B(FH, 2.0, 34.0, y0, y1, 8.0, 9.0, FENDER, ch=0.28, name='cover'))
        out.append(B(FH, 10.6, 24.4, y0, y1, 6.95, 8.05, FENDER, ch=0.18, name='cover_skirt'))
        if EMITTERS:
            for xe in (7.0, 12.4, 17.8, 23.2, 28.6):
                out.append(cyl(FH, (xe - 0.85, ym, 9.45), (xe + 0.85, ym, 9.45), 0.52, EMITTER, 'emitter'))
                out.append(B(FH, xe - 1.2, xe + 1.2, ym - 0.75, ym + 0.75, 8.95, 9.25, HOUSING, ch=0.08,
                             name='emitter_base'))
    return out


# ---------------------------------------------------------------- the hull
def hull_parts():
    out = []
    # the deck between the pods (TS: x 12..34, y 5..24, z 3..9, dark ochre), flush with the covers
    out.append(B(FH, 12.0, 34.4, 4.9, 24.1, 3.0, 9.0, DECK, ch=0.3, name='deck'))
    # its back - the U's inner end - with a grey lip on top (TS: x 9..12, y 9..19, z 7..9)
    out.append(B(FH, 9.0, 12.4, 8.8, 20.2, 7.0, 8.75, LIP, ch=0.22, name='lip'))
    # the prongs' inner walls aft of the deck, TS's machinery (khaki, olive and brown at x 1..12, z 3..7)
    for (y0, y1) in ((4.9, 7.2), (21.8, 24.1)):
        out.append(B(FH, 1.0, 12.2, y0, y1, 3.0, 7.2, LEDGE, ch=0.2, name='ledge'))
    return out


# ---------------------------------------------------------------- the emitter
# TS's tower on the deck's right front (TS: an octagon x 20..27, y 6..13, z 9..16, a little wider at z 13..16; its top a
# light grey crown and cap, z 16..18), on TS's olive ring round its foot (the render's plinth); the cap is the emitter's
# orb (Westwood's icon: it glows)
TOWER_C = (23.5, 9.5)
TOWER_R = 3.35


def octagon(c, r, phase=np.pi / 8):
    return [(c[0] + r * np.cos(phase + k * np.pi / 4), c[1] + r * np.sin(phase + k * np.pi / 4)) for k in range(8)]


def tower_parts():
    out = []
    cx, cy = TOWER_C
    out.append(prism(FH, 2, octagon(TOWER_C, 4.35), 8.9, 9.35, PLINTH, ch=0.12, name='plinth'))
    out.append(prism(FH, 2, octagon(TOWER_C, TOWER_R), 9.3, 13.2, TOWER, ch=0.15, name='tower'))
    out.append(prism(FH, 2, octagon(TOWER_C, TOWER_R + 0.5), 13.1, 15.75, COLLAR, ch=0.22, name='collar'))
    out.append(prism(FH, 2, octagon(TOWER_C, 3.15), 15.7, 16.3, CROWN, ch=0.12, name='crown'))
    out.append(ball(FH, (cx, cy, 15.85), (2.75, 2.75, 2.25), 18.2, ORB, 'orb'))
    return out


# ---------------------------------------------------------------- the hatch box and the conduits
SLOT_Y = (17.5, 22.1)                               # the cockpit slot's glass (q y, z) on the box's front face (q x 29)
SLOT_Z = (9.7, 10.5)


def deck_parts():
    out = []
    # TS's grey box on the deck's left front (TS: x 21..29, y 16..24, z 9..11), with a cockpit slot across its front
    # (Luke: "similar to the disruptor"; TS's box front is plain grey): the dark glass in a frame proud of the face, the
    # Disruptor's viewport made as long and low as the box's front allows
    out.append(B(FH, 21.0, 29.0, 16.0, 23.6, 8.9, 11.0, BOX, ch=0.25, name='hatch_box'))
    (y0, y1), (z0, z1) = SLOT_Y, SLOT_Z
    out.append(B(FH, 28.9, 29.06, y0, y1, z0, z1, GLASS, name='cockpit_slot'))
    f = 0.16
    for (ya, yb, za, zb) in ((y0 - f, y1 + f, z1, z1 + f), (y0 - f, y1 + f, z0 - f, z0),
                             (y0 - f, y0, z0, z1), (y1, y1 + f, z0, z1)):
        out.append(B(FH, 28.9, 29.16, ya, yb, za, zb, BOX, ch=0.04, name='cockpit_slot_frame'))
    # TS's conduits across the deck by the U's inner end (TS: x 14 to z 12, x 15..17 to z 11, y 9..20), on their mounts
    # (TS: x 12..16, y 8..10 and 18..21); ribbed (the render's hose)
    out.append(cyl(FH, (14.45, 9.4, 10.55), (14.45, 19.6, 10.55), 1.42, PIPE, 'conduit'))
    out.append(cyl(FH, (16.75, 9.4, 10.05), (16.75, 19.6, 10.05), 0.95, PIPE, 'conduit'))
    for (y0, y1) in ((7.9, 9.6), (19.4, 21.1)):
        out.append(B(FH, 12.3, 18.0, y0, y1, 8.9, 11.4, MOUNT, ch=0.2, name='mount'))
    return out


def model():
    return {'hull': pod_parts() + hull_parts() + tower_parts() + deck_parts()}


SECTIONS = {'hull': FH}


def pose(k='hull'):
    """the section's pose in the unit's frame: TS's HVA (frame 0), lowered onto the ground (GZ)."""
    R, t = FH.pose()
    return R, t + np.array([0.0, 0.0, -GZ])


def posed(m, which=('hull',), Mx=np.eye(3)):
    """the parts posed (pose()) and turned by Mx (unit frame -> world): (parts, frames, owner)."""
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
