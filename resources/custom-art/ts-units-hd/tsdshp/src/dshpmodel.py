"""
dshpmodel.py - the TS Dropship (TS's [DSHP], TSDSHP in the mod) rebuilt the way the Titan, the Wolverine, the Disruptor
and the Hover MLRS are: TS's own voxels (DSHP.VXL) as the blueprint for where every part is and how big, each part
modelled clean (flat plates, true slopes, bevelled edges) in TS's colours, GDI's gold where TS paints house colour (it
is never house-coloured), with Westwood's art of the dropship (the TS intro's FMV) and the mods' renders Luke sent for
details where TS's voxels have the part.

The section's frame: q, continuous voxel coordinates (voxel i spans i..i+1), x back to front (95 voxels), y from the
ship's right (0) to its left (43), z up (23); the local frame is min + q * scale (TS's), and the HVA (frame 0) places
it in the unit's frame.  The ship is symmetric about q y 21.5 (TS's own centre line, the HVA origin's); w below is the
distance out from it.

Parts (TS's voxels in brackets, q units):
  tail       x 0.5..24.5: lofted through TS's own cross-sections (a tapering arch); its back the cargo door (gold)
  keel       a dark wedge under the tail [x 15..25, z 3..8, w 3]
  lower body a landing block at each end [rear x 21..32, front x 59..75, w 9.5, z 3..12; the front one's chin sloping
             up to the nose], the bay between them [w 7, grey]
  skids      gold, under the blocks [rear x 24..36, front x 52..68, z 0..3, w 2..9.3], gold rails between [w 4.3..6.6]
  sponsons   along the bay [x 30..54]: gold sides [out to w 12.5], red-brown decks, dark undersides
  cabin      above: the back half [x 23.5..46, w 5.5, top z 22], the front half [x 46..63, w 6.5, top z 23] (brown
             roofs), its brow sloping down to the front beam, a neck forward to the nose [x 66..76]: a floor, two
             pipes along its sides [w 4, z 15.5], a gabled roof
  beams      two across the top [rear x 29..36, front x 65.5..73, z 18..21], rounded planks into
  pods       four engine pods [rear x 22..45, w 15..20, z 15..22; front x 60..78, w 15.5..19.5, z 16..22]: gold
             frames round dark intakes at both ends, dark olive thruster boxes under them [rear x 24..39, z 11..18;
             front x 61..74, z 13..18] stepping out past the nacelles, dark collars where the beams join
  nose       x 76..95: lofted through TS's cross-sections, its spine, a dark gear keel under it [x 69..87]
  lamps      TS's: amber on the cabin's sides [x 46, z 19] and round the neck [x 73..74], yellow along the front
             block's sides [x 61..70, z 8..9], the nav lamps either side of the nose's tip [x 92, z 11..12]
"""
import os, sys
from paths import HANDOFF
sys.path.insert(0, os.path.join(HANDOFF, 'renderer'))
import numpy as np
import vxl
import rc
from qparts import Frame, B, prism, hull, cyl

D = os.path.join(HANDOFF, '26-TSDSHP', 'ts-original') + os.sep

(TAIL, NOSE, CABIN, NECK, PIPE, BLOCK, BAY, SKID, SPONSON, KEEL, BEAM, POD, CAP, INTAKE, THRUSTER, COLLAR, LAMP,
 LAMP_Y, NAV, CORE, TAIL_END, NOSE_TIP, DECK, SPINE, NOSE_HI, TIP_HI, HOOD) = range(81, 108)
LOFTS = (TAIL, NOSE)                                # shaded with the smoothed body's own normals (dshprender)
# NOSE_HI / TIP_HI: the nose's and the tip's upper parts at the front, cut by the cockpit's plate (flat shading where cut,
# the smoothed body's normals elsewhere)
HOUSE = ()                                          # never house-coloured: GDI's gold instead (no trim)


def _load(name, i):
    s = vxl.read_vxl(D + name + '.VXL')[i]
    names, mats = vxl.read_hva(D + name + '.HVA')
    return Frame(s, mats[0, i])


FH = _load('DSHP', 0)
HYC = 21.5


def Y(w):
    return HYC + w


def sides(pts_w):
    """(x, w, z) points mirrored to both sides -> q points."""
    return [(x, Y(s * w), z) for s in (1, -1) for (x, w, z) in pts_w]


def hullw(pts_w, comp, name):
    return hull(FH, sides(pts_w), comp, name)


def boxw(x0, x1, w, z0, z1, comp, ch=0.0, name=''):
    """a box across the centre line, w either side."""
    return B(FH, x0, x1, Y(-w), Y(w), z0, z1, comp, ch, name)


def pair(x0, x1, w0, w1, z0, z1, comp, ch=0.0, name=''):
    """a box on each side, w0..w1 out from the centre line."""
    return [B(FH, x0, x1, Y(w0), Y(w1), z0, z1, comp, ch, name + '_l'),
            B(FH, x0, x1, Y(-w1), Y(-w0), z0, z1, comp, ch, name + '_r')]


# ------------------------------------------------------------------------------------------------ TS's sections
# the tail and the nose are lofted through TS's own cross-sections: the filled voxels of each (no keels), smoothed
# (Gaussian, 1 voxel along the ship, 0.7 across: TS's steps become slopes), cut where the smoothed body crosses 0.45
# (dshpvox.py); each pair of neighbouring stations is one convex part.  The tail's back is the cargo door.
TAIL_X = [4.5, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.5]
G_TAIL = (0, 24, 0, 4)                              # dshpvox.region_smoothed's arguments
ISO = 0.38


def iso_station(G, xq, dz=0.5):
    import dshpvox as V
    z0, z1 = V.iso_top_bottom(G, xq, level=ISO)
    zs = list(np.arange(z0 + 0.04, z1 - 0.04, dz)) + [z1 - 0.04]
    pts = []
    for zq in zs:
        sec = V.iso_section(G, xq, zq, zq, dz=1.0, level=ISO)
        if sec:
            hw = sec[0][1]
            pts += [(xq, Y(hw), zq), (xq, Y(-hw), zq)]
    return pts


def iso_loft(G, xs, comp, name):
    st = [iso_station(G, x) for x in xs]
    return [hull(FH, st[k] + st[k + 1], comp, '%s%d' % (name, k)) for k in range(len(st) - 1)]


def tail():
    import dshpvox as V
    G = V.region_smoothed(*G_TAIL)
    P = iso_loft(G, TAIL_X, TAIL, 'tail')
    # its back: the cargo door, flat (TS: the back face upright at x 0 from z 8.4 to 12.3, below it the door's foot
    # sloping forward to x 4.5 at z 3.1)
    P.append(hull(FH, iso_station(G, TAIL_X[0]) + sides([(0.0, 4.2, 8.4), (0.0, 4.35, 10.2), (0.0, 3.6, 11.6),
                                                         (0.0, 2.4, 12.25)]), TAIL_END, 'tail_end'))
    # the spine along its top (TS's light strip; the FMV's raised spine carrying the vents), riding the top line
    pts = []
    for xq in (2.6, 4.5, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 23.6):
        zt = V.iso_top_bottom(G, xq, level=ISO)[1]
        pts += [(xq, 1.05, zt + 0.32), (xq, 1.35, zt + 0.08), (xq, 1.35, zt - 0.6)]
    P.append(hull(FH, sides(pts), SPINE, 'tail_spine'))
    return P


# the nose and the cockpit: one smooth body (dshpnose.py): TS's nose smoothed, the cockpit's housing run into it (Westwood's
# tall front plate, the window high in it), cut flat by the cockpit's plate above TS's lower lip; lofted through its
# sections, finer where the plate crosses them
NOSE_X = [76.0, 77.5, 79.0, 80.5, 82.0, 83.5, 85.0, 86.5, 88.0, 89.0, 90.0, 90.5, 91.0, 91.5, 92.0, 92.5, 93.0, 93.5,
          94.0]


def nose():
    import dshpnose as N
    xs = list(NOSE_X)
    # the tip: the last station just short of where the body ends
    x = xs[-1]
    while N.top_bottom(x + 0.1) is not None and x < 96:
        x += 0.1
    if x > xs[-1] + 0.05:
        xs.append(x - 0.02)
    st = [N.station(xq) for xq in xs]
    return [hull(FH, st[k] + st[k + 1], NOSE, 'nose%d' % k) for k in range(len(st) - 1) if st[k] and st[k + 1]]


# ------------------------------------------------------------------------------------------------ the lower body
def lower_body():
    P = []
    # the rear landing block (TS: full width x 21..31, its back sloping down and forward from z 9 to z 3)
    P.append(hullw([(21.0, 9.0, 7.0), (21.0, 9.0, 9.6), (21.0, 7.8, 11.2), (23.5, 9.4, 3.0), (32.5, 9.4, 3.0),
                    (32.5, 9.4, 10.2), (32.5, 7.8, 12.4), (24.0, 7.8, 12.4)], BLOCK, 'rear_block'))
    # the bay between the blocks (TS: grey walls 7 out under the sponsons)
    P.append(boxw(31.5, 60.0, 7.2, 1.2, 12.4, BAY, 0.3, 'bay'))
    # the front landing block (TS: full width x 59..75, its chin sloping up from z 3 at x 67 to z 8.5 at x 74.5)
    P.append(hullw([(59.0, 9.4, 3.0), (59.0, 9.4, 10.0), (59.0, 7.6, 12.8), (67.5, 9.4, 3.0), (74.5, 8.6, 8.4),
                    (74.8, 7.4, 12.0), (68.0, 9.4, 10.0), (68.0, 7.6, 12.8)], BLOCK, 'front_block'))
    # the gold skids under the blocks (TS: z 0..3, either side of a grey channel 2 out) and the rails between them
    for x0, x1, nm in ((24.0, 36.2, 'skid_rear'), (52.0, 67.8, 'skid_front')):
        for s in (1, -1):
            P.append(hull(FH, [(x, Y(s * w), z) for (x, w, z) in
                               [(x0, 2.1, 1.2), (x0, 9.2, 1.2), (x0, 2.1, 3.2), (x0, 9.2, 3.2),
                                (x0 + 1.2, 2.1, 0.05), (x0 + 1.2, 9.0, 0.05), (x1 - 1.2, 2.1, 0.05),
                                (x1 - 1.2, 9.0, 0.05), (x1, 2.1, 1.2), (x1, 9.2, 1.2), (x1, 2.1, 3.2),
                                (x1, 9.2, 3.2)]], SKID, nm))
    P += pair(35.5, 52.8, 4.3, 6.6, 1.0, 3.0, SKID, 0.3, 'rail')
    P.append(boxw(23.8, 68.0, 2.3, 0.8, 3.4, BAY, 0.2, 'channel'))
    return P


def sponsons():
    P = []
    # TS: x 30..54; the gold side bulging out to 12.5 (z 10..13), its top sloping up and in to 9.6 out at z 15 (TS's
    # gold rows at z 12..14), a dark underside (z 8..10, 11.5 out); on it the red-brown deck, a raised strip from the
    # cabin's wall to 9.6 out, its top at z 16 (TS's red rows at z 15)
    gold = [(11.0, 8.0), (11.8, 8.8), (12.5, 10.0), (12.5, 13.0), (11.6, 14.3), (9.4, 15.0), (5.5, 15.0), (5.5, 8.0)]
    deck = [(9.6, 14.6), (9.6, 15.55), (9.2, 16.0), (5.5, 16.0), (5.5, 14.6)]
    for s in (1, -1):
        for sec, comp, ends in ((gold, SPONSON, ((30.0, 0.8), (31.6, 1.0), (52.4, 1.0), (54.0, 0.8))),
                                (deck, DECK, ((30.6, 0.9), (31.6, 1.0), (52.6, 1.0), (53.8, 0.9)))):
            pts = []
            for x, k in ends:
                for w, z in sec:
                    # the ends drawn in a little (TS's tapered ends)
                    pts.append((x, Y(s * (5.5 + (w - 5.5) * k)), z if k == 1.0 else 8.6 + (z - 8.0) * 0.92))
            P.append(hull(FH, pts, comp, 'sponson' if comp == SPONSON else 'deck'))
    return P


# ------------------------------------------------------------------------------------------------ the cabin
def cabin():
    P = []
    P.append(boxw(23.5, 46.3, 5.5, 11.0, 22.0, CABIN, 0.45, 'cabin_back'))
    P.append(boxw(46.0, 63.0, 6.5, 12.0, 23.0, CABIN, 0.45, 'cabin_front'))
    # the brow: the front half's front face, sloping down from its roof to the front beam (TS: x 63..66)
    # (TS: its top two voxels narrower: chamfered along the slope)
    P.append(prism(FH, 1, [(62.6, 12.5), (62.6, 23.0), (63.4, 23.0), (66.4, 18.6), (66.4, 12.5)], Y(-6.5), Y(6.5),
                   CABIN, 1.4, 'brow', edges=[False, True, True, False, False]))
    return P


def neck():
    P = []
    # TS: x 66..76: a floor (z 13..14, 4.5 out), two pipes along its sides (3 voxels: w 4, z 15.5), a gabled roof
    # (4.5 out at z 17 to the spine, 1.5 out at z 21), dark inside
    P.append(boxw(65.5, 76.3, 4.6, 12.6, 13.9, NECK, 0.25, 'neck_floor'))
    for s in (1, -1):
        P.append(cyl(FH, (65.5, Y(s * 4.0), 15.5), (76.6, Y(s * 4.0), 15.5), 1.45, PIPE, 'pipe'))
    P.append(hullw([(65.5, 4.6, 16.8), (76.3, 4.6, 16.8), (76.3, 4.4, 17.6), (76.3, 1.6, 20.6), (76.3, 1.1, 21.0),
                    (65.5, 4.4, 17.6), (65.5, 1.6, 21.0)], NECK, 'neck_roof'))
    P.append(boxw(65.5, 76.0, 3.0, 13.5, 17.2, CORE, 0.0, 'neck_core'))
    return P


def beams():
    P = []
    for x0, x1, nm in ((29.0, 36.0, 'beam_rear'), (65.6, 73.0, 'beam_front')):
        P.append(prism(FH, 1, [(x0, 19.4), (x0 + 0.9, 18.0), (x1 - 0.9, 18.0), (x1, 19.4), (x1 - 0.7, 21.0),
                               (x0 + 0.7, 21.0)], Y(-15.6), Y(15.6), BEAM, 0.0, nm))
    return P


# ------------------------------------------------------------------------------------------------ the engine pods
# nacelle: x0..x1, w0..w1 out, z0..z1; its gold frames (TS's ends, 2 voxels deep) round a dark intake (TS's hole,
# about half the face each way); the thruster box under it: tx0..tx1, out to tw0..tw1, tz0..tz1, its lower tier one
# voxel further out (TS)
PODS = {'rear': dict(x=(22.0, 45.0), w=(15.0, 20.0), z=(15.0, 22.0), cap=1.7, hole_w=(16.3, 18.7), hole_z=(17.0, 20.2),
                     tx=(24.0, 39.0), tw=(14.4, 20.9), tz=(15.0, 18.0), lw=(14.2, 21.3), lz=(11.0, 15.2)),
        'front': dict(x=(60.0, 78.0), w=(15.5, 19.5), z=(16.0, 22.0), cap=1.6, hole_w=(16.5, 18.5), hole_z=(17.8, 20.3),
                      tx=(61.0, 74.0), tw=(14.6, 20.6), tz=(15.2, 18.0), lw=(14.5, 21.2), lz=(13.0, 15.4))}


def pod(which, s):
    p = PODS[which]
    x0, x1 = p['x']; w0, w1 = p['w']; z0, z1 = p['z']; c = p['cap']
    hw0, hw1 = p['hole_w']; hz0, hz1 = p['hole_z']

    def bw(xa, xb, wa, wb, za, zb, comp, ch, nm):
        ya, yb = sorted((Y(s * wa), Y(s * wb)))
        return B(FH, xa, xb, ya, yb, za, zb, comp, ch, nm)
    P = [bw(x0 + c - 0.3, x1 - c + 0.3, w0, w1, z0, z1, POD, 0.5, 'nacelle_' + which)]
    for xa, xb, xi in ((x0, x0 + c, x0 + 0.65), (x1 - c, x1, x1 - 0.65)):
        # the frame: four bars round the hole, and the intake set into it
        P.append(bw(xa, xb, w0, w1, z0, hz0, CAP, 0.3, 'cap_lo'))
        P.append(bw(xa, xb, w0, w1, hz1, z1, CAP, 0.3, 'cap_hi'))
        P.append(bw(xa, xb, w0, hw0, hz0 - 0.2, hz1 + 0.2, CAP, 0.2, 'cap_in'))
        P.append(bw(xa, xb, hw1, w1, hz0 - 0.2, hz1 + 0.2, CAP, 0.2, 'cap_out'))
        xi0, xi1 = (xi, x0 + c + 0.2) if xa == x0 else (x1 - c - 0.2, xi)
        P.append(bw(xi0, xi1, hw0 - 0.1, hw1 + 0.1, hz0 - 0.1, hz1 + 0.1, INTAKE, 0.0, 'intake'))
    tx0, tx1 = p['tx']
    P.append(bw(tx0, tx1, p['tw'][0], p['tw'][1], p['tz'][0], p['tz'][1], THRUSTER, 0.3, 'thruster_hi'))
    P.append(bw(tx0, tx1, p['lw'][0], p['lw'][1], p['lz'][0], p['lz'][1], THRUSTER, 0.35, 'thruster_lo'))
    return P


def pods():
    P = []
    for which in ('rear', 'front'):
        for s in (1, -1):
            P += pod(which, s)
    # the beams' collars on the pods' inner sides (TS's dark band where the beam joins)
    for x0, x1 in ((28.6, 36.4), (65.2, 73.4)):
        P += pair(x0, x1, 14.6, 15.4, 17.6, 21.4, COLLAR, 0.25, 'collar')
    return P


def keels():
    P = []
    P.append(hullw([(15.5, 2.6, 7.6), (16.5, 2.6, 5.2), (19.0, 3.0, 4.0), (21.0, 3.0, 3.0), (25.0, 3.0, 3.0),
                    (25.0, 3.0, 8.0)], KEEL, 'tail_keel'))
    P.append(hullw([(68.6, 1.6, 9.0), (69.4, 1.6, 4.2), (72.0, 1.6, 5.0), (76.0, 1.7, 7.0), (80.0, 2.3, 8.0),
                    (83.5, 2.3, 9.0), (87.0, 2.0, 10.0), (87.0, 2.0, 12.0), (68.6, 2.0, 12.5)], KEEL, 'nose_keel'))
    return P


def lamps():
    P = []
    L = lambda c, r, comp, nm: rc.Part([rc.Ellip(FH.p(c), np.eye(3), np.asarray(r, float) * FH.sc)], comp, nm,
                                      sphere=(FH.p(c), float(np.max(r)) + 1e-3))
    for s in (1, -1):
        # amber: the cabin's sides at its step (TS: x 46, z 19), the neck (TS: x 73..74, its sides at z 16.5 and
        # either side of its spine at z 19.5)
        P.append(L((46.6, Y(s * 6.55), 19.5), (0.45, 0.22, 0.45), LAMP, 'lamp_cabin'))
        P.append(L((73.6, Y(s * 4.55), 16.6), (0.42, 0.2, 0.42), LAMP, 'lamp_neck'))
        P.append(L((73.6, Y(s * 1.7), 20.3), (0.38, 0.3, 0.3), LAMP, 'lamp_spine'))
        # yellow along the front block's sides (TS: x 61..70, z 8..9)
        for x in (61.6, 64.0, 66.4):
            P.append(L((x, Y(s * 9.45), 8.6), (0.5, 0.2, 0.32), LAMP_Y, 'lamp_block'))
        # the nav lamps either side of the nose's tip (TS: house colour, x 92, z 11..12), set into the lip's side
        import dshpnose as N
        P.append(L((92.3, Y(s * (N.halfwidth(92.3, 12.2) - 0.12)), 12.2), (0.5, 0.4, 0.42), NAV, 'nav'))
    return P


def model():
    parts = (tail() + nose() + lower_body() + sponsons() + cabin() + neck() + beams() + pods() + keels() + lamps())
    return {'hull': parts}


SECTIONS = {'hull': FH}


def posed(m, which=('hull',), Mx=np.eye(3), shift=None):
    """the parts posed (HVA frame 0, plus shift[section] in the unit's frame if given) and turned by Mx (unit frame ->
    world): (parts, frames, owner)."""
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
