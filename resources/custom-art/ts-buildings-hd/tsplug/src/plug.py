"""
TS Upgrade Center (GAPLUG / GTPLUG; TSPLUG in the mod) as a model for hd.py.

Built in its own frame (X east, Y south as TS draws it, units 1 cell = 128, Z up, origin at the centre of TS's 2x3
foundation, X -128..128, Y -192..192), read from GTPLUG / GTPLUGMK / GTPLUG_A.._C in TS's own camera (TS's ground centre
at frame px (60, 90)).  Depth along TS's view ray is fixed by the feet (on the ground) and the slope's foot (on the deck):
  deck      a grey platform raised on square feet (TS draws three of them: the south-west and south-east corners and the
            middle of the east side), its north-west part narrower (GTPLUGMK 03); an ochre step along its south edge
  block     a long tan block along the deck's north part: a flat roof with a raised panel, a bright bevel along its south
            edge, under it a vertical face with the purple band at the top (the band turns the south-east corner and runs
            north along the east face until the ramp covers it)
  slope     TS's 'greenhouse': a house-green slope from the face's foot down to the deck, framed panes with a sill; v2:
            the panes separate panels with dark joints between them (v1: raised green ribs)
  ramp      a steep brown hip at the east end, from the block's north-east corner down to the deck's north-east corner
            and the deck's east edge; a dark slot down it (GTPLUG_C runs a light in it); three grey pipes run up it from
            the deck's east edge and into the building (v2, Luke: TS's pipes go up the side wall then into the building;
            v1 had them standing free in front of it on a plinth)
  sockets   two round plug sockets on the deck's south part, one cell apart: low, round-topped house-green collars round
            grey plates with four holes for the plugs to slot into (v2; v1 had four bolts and taller flat collars)
  roof      antennas (the tallest at the west end carries GTPLUG_B's lights; a fork in the middle), a dish on a box at
            the north edge (GTPLUG_A turns it)
"""
import numpy as np
import hd
from radr import Acc, rod_interval, inbox, in_poly, dblob
from scipy import ndimage


class CropAcc:
    """radr.Acc's layered intervals for one small part, kept only over the box the part covers (a full-grid Acc is
    three layers of full-grid arrays: thirty plug parts at x4 on the RA grid ran out of memory)."""
    def __init__(self, shape, n=3):
        self.shape, self.n, self.adds = shape, n, []

    def add(self, bot, top, comp, mask, name=''):
        bot = np.broadcast_to(np.asarray(bot, np.float32), mask.shape)
        top = np.broadcast_to(np.asarray(top, np.float32), mask.shape)
        m = mask & (top > bot)
        if not m.any():
            return
        rows = np.nonzero(m.any(axis=1))[0]; cols = np.nonzero(m.any(axis=0))[0]
        r0, r1, c0, c1 = rows[0], rows[-1] + 1, cols[0], cols[-1] + 1
        cp = comp if np.ndim(comp) == 0 else np.broadcast_to(comp, mask.shape)[r0:r1, c0:c1].copy()
        self.adds.append((r0, c0, bot[r0:r1, c0:c1].copy(), top[r0:r1, c0:c1].copy(), cp, m[r0:r1, c0:c1].copy(), name))

    def layers(self):
        """the used layers over the parts' box: [(r0, c0, top, bot, comp, name)]."""
        if not self.adds:
            return []
        r0 = min(a[0] for a in self.adds); c0 = min(a[1] for a in self.adds)
        r1 = max(a[0] + a[5].shape[0] for a in self.adds); c1 = max(a[1] + a[5].shape[1] for a in self.adds)
        shp = (r1 - r0, c1 - c0)
        acc = Acc(shp, n=self.n)
        for ar, ac, b, t, cp, m, name in self.adds:
            sl = (slice(ar - r0, ar - r0 + m.shape[0]), slice(ac - c0, ac - c0 + m.shape[1]))
            mm = np.zeros(shp, bool); mm[sl] = m
            bb = np.zeros(shp, np.float32); bb[sl] = b
            tt = np.zeros(shp, np.float32); tt[sl] = t
            if np.ndim(cp):
                cc = np.zeros(shp, np.int16); cc[sl] = cp
            else:
                cc = cp
            acc.add(bb, tt, cc, mm, name)
        return [(r0, c0, t, b, c, '+'.join(nm) or 'part') for t, b, c, nm in zip(acc.top, acc.bot, acc.comp, acc.names)
                if (t >= 0).any()]


def pack_slabs(accs, shape, gap=10):
    """the parts' layers packed into as few full-grid slabs as possible: parts whose footprints, grown by `gap` grid
    px, don't overlap share a slab (so smoothing a slab's top never mixes two parts: the render is the same as one
    slab each); lathed parts ('L:', classed top / bottom by hd) only with lathed ones."""
    packed = []
    st = np.ones((3, 3), bool)
    for a in accs:
        for r0, c0, t, b, c, name in a.layers():
            valid = t >= 0
            lathe_ = name.startswith('L:')
            R0, C0 = max(r0 - gap, 0), max(c0 - gap, 0)
            R1, C1 = min(r0 + t.shape[0] + gap, shape[0]), min(c0 + t.shape[1] + gap, shape[1])
            grown = np.zeros((R1 - R0, C1 - C0), bool)
            grown[r0 - R0:r0 - R0 + t.shape[0], c0 - C0:c0 - C0 + t.shape[1]] = valid
            grown = ndimage.binary_dilation(grown, structure=st, iterations=gap)
            # after every slab holding a part it touches, so where two parts meet the earlier one still wins (as
            # when each part was a slab of its own, in order)
            conf = [i for i, q in enumerate(packed) if (q['m'][R0:R1, C0:C1] & grown).any()]
            for q in packed[(max(conf) + 1 if conf else 0):]:
                if q['L'] == lathe_:
                    break
            else:
                q = dict(top=np.full(shape, -1.0, np.float32), bot=np.zeros(shape, np.float32),
                         comp=np.zeros(shape, np.int16), m=np.zeros(shape, bool), names=[], L=lathe_)
                packed.append(q)
            sl = (slice(r0, r0 + t.shape[0]), slice(c0, c0 + t.shape[1]))
            q['top'][sl] = np.where(valid, t, q['top'][sl])
            q['bot'][sl] = np.where(valid, np.maximum(b, 0.0), q['bot'][sl])
            q['comp'][sl] = np.where(valid, c, q['comp'][sl])
            q['m'][sl] |= valid
            q['names'].append(name)
    return [hd.Slab(q['top'], q['bot'], q['comp'], '+'.join(q['names'])) for q in packed]
import plugs as PG, wnoise as WN

(PLAT, FOOT, BLOCK, LIP, FACE, ROOF, PANEL, PFRAME, SOCK, PLATE, BOLT, RAMP, PIPE, PCAP, ANT, DISH, DMOUNT, LAMP,
 SLAB, STEP, SLOT, RIDGE, LEDGE, FRONT, CORE, BEAM, JOINT, HOLE) = range(1, 29)
DEBRIS, DEB_IN, DEB_BURNT = 40, 41, 42
HOUSE = {PANEL, PFRAME, SOCK} | PG.PG_HOUSE

P = dict(
    deck=dict(x0=-120.0, x0n=-98.0, yw=-12.0, x1=122.5, x1s=110.0, ye=50.0, y0=-124.0, y1=172.0, zb=16.0, zt=33.5,
              cham=2.0, core=26.0),
    # square feet (centre x, y), half size, from the ground to the deck's underside
    feet=dict(pts=((-110.0, 166.0), (86.0, 166.0), (93.0, 29.0), (-109.0, 29.0), (93.0, -112.0), (-88.0, -112.0)),
              a=10.5),
    # the ochre step along the deck's south edge
    step=dict(x=(-57.0, 49.0), y=(164.0, 172.0), h=3.2, n=14),
    # the block's profile across y (north to south): the roof (flat, a raised panel on it), a 45-degree bevel, the
    # vertical band face, a narrow ledge, a short brown face, then the slope.  The upper part (roof to the ledge's
    # front) runs west past the lower body and the deck: TS's notch under the west end.
    block=dict(yn=-86.2, z=89.5, lip=(-0.9, 8.6), face=(80.0, 67.0), ledge=(19.3, 67.0), front=60.5,
               x_roof=(-127.0, 78.0), x_ledge=(-131.0, 78.0), x_low=-98.0,
               band=(71.3, 80.0), strip=(67.0, 71.3),
               ridge=dict(y=(-60.0, -16.0), x=(-118.0, 66.0), h=0.0, cham=3.0),
               # v2: ribs along the roof (TS's roof is ridged along its length): period across y, height
               ribs=dict(per=7.0, h=0.7)),
    # the slope: panes from the front face's foot to (y, z), then the sill down to the deck at y_foot
    # east of the block (x > 78) the slope runs on over the ramp to x 112, its top edge rising to y 8 there
    # v2 (Luke 5 Oct: 'our green bit overhangs'): the slope stops at the block's east end (x 78; v1 ran it on to x 108
    # with its top edge rising, a green wedge standing out over the ramp); east of it the green lies ON the ramp: TS's
    # green there is on the ramp's surface (its tip at TS px (82, 83) = ramp (88, -29, 54)), a skin from the block's
    # east face out to the line TS's green ends on (ramp (88, -29) to (101, 38))
    slope=dict(x=(-98.0, 78.0), pane=(39.3, 39.5), foot=49.3, ribs=50.5, rib0=-87.0, rib_w=4.0, rib_h=2.4,
               east=(78.0, 108.0, 9.0),
               onramp=dict(poly=((77.0, -11.3), (87.9, -29.3), (100.6, 38.4), (96.0, 49.3), (77.0, 49.3)), lift=0.9,
                           rim=3.0,
                           # its west part leans on the block's east face (TS's green wraps the corner a little) and the
                           # slope's end is bevelled down onto the ramp: z = top(y) - bevel * (x - 78)
                           lean=dict(z=(53.0, 60.0), y=(-11.3, 19.3), bevel=0.6)),
               # v2: the ribs between the panes are dark joints sunk into the slope (TS: separate panels)
               joint=dict(w=3.6, d=2.6)),
    # the ramp: a bilinear patch over the quad A (block's north-east top corner), B (deck's north-east corner),
    # C (deck's east edge, south), D (block's east face, south); (x, y, z) each
    ramp=dict(A=(78.0, -86.2, 89.5), B=(121.0, -124.0, 33.5), C=(121.0, 46.0, 33.5), D=(78.0, 30.0, 33.0),
              skirt=(117.0, 123.5), skirt_y=(-124.0, 50.0)),
    # the slot down the ramp (two points on it, found from TS's px (85, 81) and (85, 89)), its half width
    slot=dict(w=2.2),
    # v2: the pipes lie on the ramp: each runs from the deck's east edge up the ramp along the line TS draws straight
    # up (TS screen x 89.5, 92.5, 95.5) to TS screen y `top`, then turns into the ramp (into the building)
    pipes=dict(screen=((89.5, 74.5), (92.5, 74.5), (95.5, 75.5)), r=4.6, foot=1.6,
               pts=((121.0, -34.0, 99.0), (121.0, -53.0, 92.0), (121.0, -71.0, 79.0)), cap=3.0,       # v1 (free-standing)
               plinth=None),
    sockets=dict(c=((-68.0, 111.0), (59.0, 112.0)), r_out=48.5, r_in=37.5, z=47.5, plate=43.5, bolts=21.0,
                 bolt_r=2.6, bolt_h=1.8,
                 # v2: holes for the plugs (where v1's bolts were) and a lower, round-topped collar
                 holes=dict(r=3.6, d=5.0), round=dict(base=39.0, top=45.0)),
    # antennas on the roof: (x, y, top z, radius); the tallest one carries GTPLUG_B's lights
    ants=((-112.0, -21.0, 259.0, 2.3), (-110.0, -46.0, 163.0, 1.5), (-110.0, -62.0, 200.0, 1.6),
          (45.0, -35.0, 178.0, 1.5), (77.0, -56.0, 217.0, 1.6), (74.0, -80.0, 198.0, 1.6)),
    tall=dict(thin_from=200.0, thin_r=1.3, lamps=(202.0, 257.0)),
    # the fork: mast (x, y) to z, a crossbar at zc across +-half along x, prongs up to (left, right)
    fork=dict(c=(-28.0, -77.0), z=195.0, zc=138.0, half=8.0, tops=(212.0, 168.0), r=1.5),
    tbar=dict(z=(184.0, 196.0), half=5.0, r=1.0),            # the cross pieces near the top of antenna 3
    mount=dict(c=(-66.0, -70.0), a=11.0, h=9.0),
    dish=dict(R=12.0, depth=3.5, t=1.8, post=(2.2, 9.0), az=200.0, el=55.0, off=3.0),
)

# the damaged state (GTPLUG 1): where TS breaks it
DMG = dict(
    hole=(40.0, -42.0, 56.0, 40.0, 0.3),       # the roof caved in over its east half: centre, half sizes, roughness
    lipcut=(-8.0, 64.0),                        # the bevel and band broken along x (where the hole reaches the face)
    floor=70.0,                                 # the burnt-out inside (v1 everywhere; v2 only in the `pits`)
    # v2 (TS burns the east half fairly flat): the roof burnt and sunk a little over the hole, deeper only in pits
    burnt=83.0, pits=((28.0, -40.0, 14.0, 11.0), (58.0, -58.0, 10.0, 9.0), (6.0, -62.0, 8.0, 7.0)),
    beams=(((-14.0, -72.0, 86.0), (74.0, -50.0, 80.0)), ((2.0, -12.0, 84.0), (44.0, -80.0, 66.0)),
           ((46.0, -6.0, 76.0), (76.0, -44.0, 88.0)), ((20.0, -30.0, 70.0), (60.0, -20.0, 86.0))),
    beam_r=1.8,
    ants_gone=(3, 4),                           # antennas knocked off the roof (TS's x 75 and 85)
    lean=(-5.0, 3.0),                           # the tallest antenna bent: its top moved by (x, y)
    pipes=((121.0, -34.0, 63.0), (121.0, -53.0, 74.0), (121.0, -71.0, 79.0)),   # v1: snapped short; the third bent over
    bent=((121.0, -71.0, 40.0), (138.0, -64.0, 70.0)),
    fallen=((112.0, -44.0, 44.0), (132.0, -18.0, 30.0)),                      # v1: a broken pipe length on the ramp
    # v2 (pipes on the ramp, TS frame 1): the west two snapped near their feet, the east one whole; a length bent out
    # from the middle one's stump (TS draws it leaning up and east, screen (90, 90) to (97, 80))
    pipe_frac=(0.26, 0.2, 1.0), bent2=((119.0, -50.0, 40.0), (129.0, -72.0, 68.0)),
    pane=(30.0, 27.0, 21.0, 13.0),              # a hole knocked in the slope: x, y, half sizes (v2: TS's whole pane)
    sock=(-20.0, 55.0),                         # socket 1's collar broken off over these angles (deg, from east)
)

# the Dropship Bay (gdrop.py) reuses this model as its east half with v3's shapes: a frozen copy of them for it
import copy as _copy
P_BAY = _copy.deepcopy(P)
# v4 (Luke, 6 Oct 2026, the RA grid facing south: "pipes and lights on the right in ts angle all straight, in ra angle
# walls suddenly not flush with the building and whats the gap on the left?" / "like a rectangle morphed into a
# parallelogram"): one model for both views -
#  - the east end: the block's whole cross-section (roof, bevel, band, ledge, the green slope) runs on east of x 78 under
#    a hip falling east to a vertical end wall at xw: flush with the block from front to back, rectangular in plan
#    (v1-v3: TS's twisted ramp patch, which only read right from TS's camera);
#  - the three pipes stand straight up from the deck in front of the end wall and turn into the hip at its foot;
#    GTPLUG_C's light runs down a vertical lamp column beside them;
#  - the west end flush: the deck's north part, the lower body and the green slope run out to the roof's west end
#    (v1-v3: TS's notch under the roof's west end, where TS joins it to the Dropship Bay).
P['endwall'] = dict(x0=78.0, xw=108.0, zw=82.0,
                    # v5: the pipes where TS draws them (screen x 89, 92, 95: south to north, 16 apart), their bends
                    # stepping down northwards (84, 80.5, 77) so their tops read level from TS's camera as TS's do;
                    # damaged: the south two lose their lower parts (TS frame 1: their tops hang from the bends)
                    pipes=dict(ys=(-40.9, -56.9, -72.9), x=113.8, zb=(84.0, 80.5, 77.0), into=100.0,
                               stub=(68.0, 65.0),
                               # damaged: the broken-off length lying from the deck up against the whole pipe (TS
                               # frame 1: screen (90, 90) to (97, 80))
                               bent=((118.0, -42.0, 35.0), (120.0, -77.3, 61.0))),
                    # GTPLUG_C's lamp column where TS's slot is (screen x 85, y 81-89)
                    light=dict(c=(113.8, -19.5), r=2.8, z=(40.0, 79.0)),
                    # v5: TS's brown end face runs on north past the block's back to the deck's north edge, its top
                    # falling to the deck there: a wedge behind the block, x0 .. xw, from the deck's north edge y0 to the
                    # block's back (hidden from the RA camera; from TS's only its east face shows, TS's brown triangle
                    # right of the pipes)
                    back=dict(x0=78.0, y0=-124.0))
P['deck']['x0n'] = -120.0
P['block']['hipw'] = dict(x0=-90.0, x1=-120.0, zw=82.0)        # v6: the west end hips down as the east end does
P['block']['x_roof'] = (-120.0, P['block']['x_roof'][1])
P['block']['x_ledge'] = (-120.0, P['block']['x_ledge'][1])
P['block']['x_low'] = -120.0
P['slope']['x'] = (-120.0, P['slope']['x'][1])
P['feet']['pts'] = ((-110.0, 166.0), (86.0, 166.0), (93.0, 29.0), (-109.0, 29.0), (93.0, -112.0), (-109.0, -112.0))

# v3 (Luke, 6 Oct 2026: 'upgrade center id like the plugs facing south'): the RA grid TS's way round ('ra0': not turned,
# the sockets and plugs to the south, on a 2x3 plot); 'ra' (turned a quarter, TS east to the south) was v1-v2's
LAYOUTS = {'ts': dict(turn=False), 'ra': dict(turn=True), 'ra1': dict(turn=True, flip=True), 'ra0': dict(turn=False)}


def to_local(X, Y, layout='ts'):
    """'ra': turned a quarter (TS east -> RA south: the ramp and pipes to the camera, the block at the east end, the
    sockets at the west end); 'ra1': the other way (TS west -> RA south)."""
    L = LAYOUTS[layout]
    if not L['turn']:
        return X, Y
    return (-Y, X) if L.get('flip') else (Y, -X)


def to_world(x, y, layout='ts'):
    L = LAYOUTS[layout]
    if not L['turn']:
        return x, y
    return (y, -x) if L.get('flip') else (-y, x)


# build-up controls (GTPLUGMK's order): deck 0..1 the slab grows out from its middle; marks 0..1 the deck's painted
# outlines (gone when done); block 0..1 the block rises out of the deck with its slope and ramp; collar 0..1 the sockets'
# collars grow round from their fronts; plates 0 / 0.5 plain / 1 with bolts; dish 0 / 0.5 its post / 1; ants 0..1 the
# antennas grow up; pipes 0/1; paint 0 bare frames / 0.5 grey panes / 1 house green
BUILD_KEYS = ('deck', 'marks', 'block', 'collar', 'plates', 'dish', 'ants', 'pipes', 'paint')
DONE = {k: 1.0 for k in BUILD_KEYS}
DONE['marks'] = 0.0


# --------------------------------------------------------------------------------------------- shapes
def ramp_uv(x, y, r):
    """the ramp's patch coordinates: v across (0 at the block's east face, 1 at the deck's east edge), u along (0 at
    the rim A-B, 1 at the south edge D-C); and z."""
    A, B, C, D = (np.array(r[k]) for k in 'ABCD')
    v = (x - A[0]) / (B[0] - A[0])
    ya = A[1] + v * (B[1] - A[1]); yd = D[1] + v * (C[1] - D[1])
    u = (y - ya) / np.maximum(yd - ya, 1e-6)
    z = (1 - v) * ((1 - u) * A[2] + u * D[2]) + v * ((1 - u) * B[2] + u * C[2])
    return u, v, z


def ramp_point(r, u, v):
    A, B, C, D = (np.array(r[k]) for k in 'ABCD')
    return (1 - v) * ((1 - u) * A + u * D) + v * ((1 - u) * B + u * C)


def slot_ends(p=None):
    """the slot's two ends on the ramp: the points whose TS-screen position is (85, 81) and (85, 89).  v4: the lamp
    column's axis, top then bottom."""
    p = P if p is None else p
    ew = p.get('endwall')
    if ew:
        lt = ew['light']
        return [np.array([lt['c'][0], lt['c'][1], lt['z'][1]]), np.array([lt['c'][0], lt['c'][1], lt['z'][0]])]
    r = p['ramp']
    A, B, C, D = (np.array(r[k]) for k in 'ABCD')
    u, v = np.meshgrid(np.linspace(0, 1, 401), np.linspace(0, 1, 401))
    u = u[..., None]; v = v[..., None]
    q = (1 - v) * ((1 - u) * A + u * D) + v * ((1 - u) * B + u * C)
    sx = 60 + 0.1875 * (q[..., 0] - q[..., 1]); sy = 90 + 0.09375 * (q[..., 0] + q[..., 1]) - 0.2297 * q[..., 2]
    out = []
    for ys in (80.5, 89.5):
        d = (sx - 85.0) ** 2 + (sy - ys) ** 2
        i = np.unravel_index(np.argmin(d), d.shape)
        out.append(q[i])
    return out


_PIPE_CACHE = {}


def pipe_axes(p=None):
    """v2: the pipes' axes on the ramp, one polyline each: up from inside the deck, along the ramp (offset by the radius
    from its surface) on the line TS draws straight up at screen x `xs`, to TS screen y `top`, then turning into the
    ramp."""
    p = P if p is None else p
    pp = p['pipes']; r_ = pp['r']
    key = (tuple(tuple(p['ramp'][k]) for k in 'ABCD'), tuple(pp['screen']), r_, pp.get('foot', 1.6))
    if key in _PIPE_CACHE:
        return _PIPE_CACHE[key]
    A, B, C, D = (np.array(p['ramp'][k]) for k in 'ABCD')
    u, v = np.meshgrid(np.linspace(0, 1, 801), np.linspace(0, 1, 801))
    U = u[..., None]; V = v[..., None]
    q = (1 - V) * ((1 - U) * A + U * D) + V * ((1 - U) * B + U * C)
    sx = 60 + 0.1875 * (q[..., 0] - q[..., 1]); sy = 90 + 0.09375 * (q[..., 0] + q[..., 1]) - 0.2297 * q[..., 2]
    du = (1 - V) * (D - A) + V * (C - B); dv = (1 - U) * (B - A) + U * (C - D)
    n = np.cross(du, dv); n = n / np.linalg.norm(n, axis=-1, keepdims=True); n = np.where(n[..., 2:3] < 0, -n, n)
    out = []
    for xs, ytop in pp['screen']:
        sel = np.abs(sx - xs) < 0.03
        ys = sy[sel]; Q = q[sel]; N = n[sel]
        tg = np.linspace(ys.max() - pp.get('foot', 1.6), ytop, 6)
        pts = []
        for t_ in tg:
            i = int(np.argmin(np.abs(ys - t_)))
            pts.append(Q[i] + N[i] * (r_ + 0.4))
        a1 = pts[0]
        foot = np.array([a1[0], a1[1], p['deck']['zt'] - 1.0])
        i = int(np.argmin(np.abs(ys - ytop)))
        qt, nt = Q[i], N[i]
        up = pts[-1] - pts[-2]; up = up / np.linalg.norm(up)
        elbow = pts[-1] + up * r_ * 0.9 - nt * r_ * 0.5
        into = qt + up * r_ * 1.4 - nt * (r_ + 2.5)
        out.append([foot] + pts + [elbow, into])
    _PIPE_CACHE[key] = out
    return out


def add_pipe(acc, x, y, pts, r, comp, name='pipe'):
    """a pipe along a polyline: rods between the points, balls at the bends."""
    for a_, b_ in zip(pts[:-1], pts[1:]):
        lo, hi, mm = rod_interval(x, y, a_, b_, r)
        acc.add(lo, hi, comp, mm, name)
    for c_ in pts[1:-1]:
        d2 = (x - c_[0]) ** 2 + (y - c_[1]) ** 2
        mm = d2 <= r * r
        h_ = np.sqrt(np.clip(r * r - d2, 0, None))
        acc.add(c_[2] - h_, c_[2] + h_, comp, mm, name)


def cut_polyline(pts, frac):
    """the polyline from its start to `frac` of its length."""
    seg = [np.linalg.norm(np.asarray(b_) - np.asarray(a_)) for a_, b_ in zip(pts[:-1], pts[1:])]
    L = sum(seg) * frac
    out = [np.asarray(pts[0])]
    for (a_, b_), sl_ in zip(zip(pts[:-1], pts[1:]), seg):
        if L <= sl_:
            out.append(np.asarray(a_) + (np.asarray(b_) - np.asarray(a_)) * (L / max(sl_, 1e-9)))
            break
        out.append(np.asarray(b_)); L -= sl_
    return out


def hip_west(x, b):
    """v6: the roof's west hip - the height cap west of hipw['x0'], falling to hipw['zw'] at hipw['x1'] (inf where
    there is none)."""
    hw = b.get('hipw')
    if not hw:
        return np.full(np.shape(x), np.inf, np.float32)
    k = (b['z'] - hw['zw']) / (hw['x0'] - hw['x1'])
    return np.where(x < hw['x0'], b['z'] - k * (hw['x0'] - x), np.inf).astype(np.float32)


def block_z(y, b):
    """the block's top across y: the roof, the bevel, the ledge (the band face and the front face are the steps)."""
    l0, l1 = b['lip']
    z = np.where(y <= l0, b['z'], b['z'] - (y - l0))
    z = np.where(y > l1, b['ledge'][1], z)
    return np.where(y <= b['ledge'][0], z, 0.0)


def slope_z(y, s, b):
    """the slope from the front face's foot down to the deck."""
    y0, z0 = b['ledge'][0], b['front']
    y1, z1 = s['pane']
    y2, z2 = s['foot'], P['deck']['zt']
    za = z0 + (z1 - z0) * np.clip((y - y0) / (y1 - y0), -1, 1)
    zb = z1 + (z2 - z1) * np.clip((y - y1) / (y2 - y1), 0, 1)
    return np.where(y <= y1, za, zb)


def scene(X, Y, p=None, layout='ts', prog=None, parts=None, level=0, merge=True, dish_t=0.0, dish_az=None,
          shadow=False, plugs=(None, None), plug_t=0.0):
    """shadow=True: the light's pass (the antennas cast no shadows: on the roof they read as cracks)."""
    p = P if p is None else p
    g = dict(DONE); g.update(prog or {})
    x, y = to_local(X, Y, layout)
    H = np.zeros_like(X); C = np.zeros(X.shape, np.int16)
    acc = Acc(X.shape, n=6)          # the raised deck's edges, the overhang, the sockets, the pipes
    acc_a = Acc(X.shape, n=4)        # thin parts in the air: antennas, the dish
    acc_l = Acc(X.shape, n=2)        # the antenna's lamps (kept apart: merged with the mast they'd take it over)
    extra = {}

    def put(h, comp, where=None):
        nonlocal H, C
        if where is not None:
            h = np.where(where, h, 0.0)
        win = h > H + 1e-6
        H = np.where(win, h, H); C = np.where(win, comp, C)

    d = p['deck']
    zt = d['zt']
    if g['deck'] <= 0:
        return hd.Scene(H, C, [], extra)
    # the build-up: the deck grows out from its middle (its shape at the inverse-scaled point)
    dk = float(g['deck'])
    xc_, yc_ = 0.5 * (d['x0'] + d['x1']), 0.5 * (d['y0'] + d['y1'])
    xg, yg = (x, y) if dk >= 1 else (xc_ + (x - xc_) / dk, yc_ + (y - yc_) / dk)
    # ---- the deck: a slab on square feet, solid underneath only well inside its edges (hidden from both cameras)
    x0 = np.where(yg < d['yw'], d['x0n'], d['x0']); x1 = np.where(yg > d['ye'], d['x1s'], d['x1'])
    deck = (xg >= x0) & (xg <= x1) & (yg >= d['y0']) & (yg <= d['y1'])
    e = np.minimum(np.minimum(xg - x0, x1 - xg), np.minimum(yg - d['y0'], d['y1'] - yg)) * min(dk, 1.0)
    dtop = zt - np.clip(d['cham'] - e, 0, None)
    core = deck & (e >= d['core'])
    # the block's lower body and the slope stay solid to the ground (no seam where they would cross the core's edge;
    # their feet sit back far enough under the deck that the gap under its edge still shows)
    bk = p['block']; slp = p['slope']
    core |= inbox(x, y, (bk['x_low'], bk['x_roof'][1]), (bk['yn'], bk['ledge'][0]))
    core |= inbox(x, y, slp['x'], (bk['ledge'][0] - 15.0, slp['foot']))
    ew = p.get('endwall')
    if ew:
        core |= inbox(x, y, (ew['x0'], ew['xw']), (bk['yn'], slp['foot']))
        if ew.get('back'):
            core |= inbox(x, y, (ew['back']['x0'], ew['xw']), (ew['back']['y0'], bk['yn']))
    put(np.where(deck, dtop, 0.0), PLAT, deck)
    ft = p['feet']
    feet = np.zeros(X.shape, bool)
    for (cx, cy) in ft['pts']:
        feet |= inbox(xg, yg, (cx - ft['a'], cx + ft['a']), (cy - ft['a'], cy + ft['a']))
    # the ochre step along the south edge
    st = p['step']
    m = inbox(x, y, st['x'], st['y']) & (dk >= 1)
    put(np.where(m, zt + st['h'] * np.clip((st['y'][1] - y) / 4.0, 0.35, 1.0), 0.0), STEP, m)
    if dk < 1:                      # the slab alone while it grows
        core = deck & (e >= d['core'] * dk)
        acc.add(d['zb'], np.where(deck, dtop, 0.0), PLAT, deck & ~core, 'deck')
        H = np.where(core, zt, 0.0); C = np.where(core, PLAT, 0).astype(np.int16)
        H = np.where(feet, np.maximum(H, d['zb'] + 0.5), H); C = np.where(feet & (H <= d['zb'] + 0.6), FOOT, C)
        return hd.Scene(H, C, acc.slabs(), extra)
    bl = float(g['block'])
    sink = (1.0 - bl) * (p['block']['z'] - zt)       # the block rises: everything above the deck sunk by this

    # ---- the block: the lower body (x >= x_low) solid from the deck; the upper part (roof .. ledge) runs on west
    b = p['block']
    zb_ = block_z(y, b)
    l0, l1 = b['lip']; ly, lz = b['ledge']
    if b.get('ribs'):                                   # v2: ribs along the roof
        rb = b['ribs']
        onroof = y <= l0 - 1.5
        zb_ = zb_ + np.where(onroof, rb['h'] * (0.5 + 0.5 * np.cos(2 * np.pi * (y - b['yn']) / rb['per'])), 0.0)
    comp = np.where(y <= l0, BLOCK, np.where(y <= l1, LIP, LEDGE))
    # v6 (Luke, 7 Oct 2026: 'the roof on the left is a hard cutoff. Can we mirror the slope on the right?'): the roof's
    # west end hips down like the east end's: west of hipw['x0'] the top falls to hipw['zw'] at the roof's west end
    zcapw = hip_west(x, b)
    capw = zb_ > zcapw + 0.05
    zb_ = np.minimum(zb_, zcapw)
    comp = np.where(capw, RAMP, comp)
    xr = np.where(y <= l1, b['x_roof'][0], b['x_ledge'][0])
    xe = np.where(y <= l1, b['x_roof'][1], b['x_ledge'][1])
    inb = (x >= xr) & (x <= xe) & (y >= b['yn']) & (y <= ly)
    low = inb & (x >= b['x_low'])
    up = (zb_ - sink) > zt + 0.3                  # what has risen out of the deck so far
    for k in (BLOCK, LIP, LEDGE, RAMP):
        put(np.where(low, zb_ - sink, 0.0), k, low & (comp == k) & up)
    # the band face: a thin strip just north of the face line (its south side is the face); the front face likewise
    for (yy, ztop, k) in ((l1, b['face'][0], FACE), (ly, lz, FRONT)):
        m = (x >= xr) & (x <= xe) & (y > yy - 2.0) & (y <= yy) & (x >= b['x_low']) & (ztop - sink > zt + 0.3)
        H = np.where(m, ztop - sink, H); C = np.where(m, k, C)
    # the overhang west of the lower body: a slab from the front face's foot up
    ov = inb & (x < b['x_low'] + 4.0)        # overlapping the lower body a little: no seam where they meet
    zov = np.where((y > l1 - 2.0) & (y <= l1), b['face'][0], zb_)
    zov = np.where((y > ly - 2.0) & (y <= ly), np.maximum(zov, lz), zov)
    cov = np.where((y > l1 - 2.0) & (y <= l1), FACE, np.where((y > ly - 2.0) & (y <= ly), FRONT, comp))
    zov = zov - sink
    for k in (BLOCK, LIP, LEDGE, FACE, FRONT, RAMP):
        acc.add(max(b['front'] - sink, zt), zov, k, ov & (cov == k) & (zov > zt + 0.3), 'overhang')
    # v6 (the Dropship Bay, Luke: 'maybe a support pillar under the overhang in the left corner'): a square pillar
    # from the ground to the overhang's underside
    pil = b.get('pillar')
    if pil:
        (pcx, pcy), pa = pil['c'], pil['a']
        mp = inbox(x, y, (pcx - pa, pcx + pa), (pcy - pa, pcy + pa))
        acc.add(pil.get('z0', 0.0), max(b['front'] - sink, zt) + 0.5, LEDGE, mp & (b['front'] - sink > zt + 0.3), 'pillar')
    # the raised panel on the roof
    rg = b['ridge']
    m2 = inbox(x, y, rg['x'], rg['y']) & ~capw
    e2 = np.minimum(np.minimum(x - rg['x'][0], rg['x'][1] - x), np.minimum(y - rg['y'][0], rg['y'][1] - y))
    zrg = b['z'] + np.clip(e2 / rg['cham'], 0, 1) * rg['h'] - sink
    put(np.where(m2 & (x >= b['x_low']) & (zrg > zt + 0.3), zrg, 0.0), RIDGE)
    acc.add(max(b['front'] - sink, zt), zrg, RIDGE, m2 & (x < b['x_low'] + 4.0) & (zrg > zt + 0.3), 'overhang')

    # ---- the slope (house green) from the front face's foot to the deck: ribs down it, the sill at its foot
    sl = p['slope']
    ex0, ex1, ey1 = sl['east']
    ytop = ly - (ly - ey1) * np.clip((x - ex0) / (ex1 - ex0), 0, 1)
    m = (x >= sl['x'][0]) & (x <= sl['x'][1]) & (y > ytop) & (y <= sl['foot'])
    zs = slope_z(y, sl, b)
    ph = (x - sl['rib0']) % sl['ribs']
    jt = sl.get('joint')
    inner = np.minimum(ph, sl['ribs'] - ph) < (jt['w'] if jt else sl['rib_w']) / 2
    outer = (x - sl['x'][0] < sl['rib_w']) | (sl['x'][1] - x < sl['rib_w']) | ((x > ex0) & (y - ytop < sl['rib_w']))
    sill = y > sl['pane'][0]
    if jt:                                  # v2: dark joints sunk between the panes; the outer frame stays raised
        joint = inner & ~outer & ~sill
        rib = outer
    else:
        joint = np.zeros(X.shape, bool)
        rib = inner | outer
    zr = zs + np.where(rib & ~sill, sl['rib_h'], 0.0) - np.where(joint, jt['d'] if jt else 0.0, 0.0) - sink
    m &= zr > zt + 0.3
    put(np.where(m, zr, 0.0), PANEL, m & ~rib & ~sill & ~joint)
    put(np.where(m, zr, 0.0), PFRAME, m & (rib | sill))
    if jt:
        H = np.where(m & joint, zr, H); C = np.where(m & joint, JOINT, C)

    # ---- v4: the east end - the block's cross-section running on east under a hip down to a vertical end wall
    if ew and bl > 0:
        k_h = (b['z'] - ew['zw']) / (ew['xw'] - ew['x0'])
        reg = (x > ew['x0'] - 0.5) & (x <= ew['xw']) & (y >= b['yn']) & (y <= sl['foot'])
        prof = np.where(y <= ly, block_z(y, b), slope_z(y, sl, b))
        pcomp = np.where(y <= l0, BLOCK, np.where(y <= l1, LIP, np.where(y <= ly, LEDGE, PANEL)))
        # the band face and the front face carry on as the steps of the profile (their thin strips)
        pcomp = np.where((y > l1 - 2.0) & (y <= l1), FACE, np.where((y > ly - 2.0) & (y <= ly), FRONT, pcomp))
        prof = np.where((y > l1 - 2.0) & (y <= l1), b['face'][0], np.where((y > ly - 2.0) & (y <= ly), np.maximum(prof, lz), prof))
        zh = b['z'] - k_h * (x - ew['x0'])
        zend = np.minimum(prof, zh) - sink
        cend = np.where(zh < prof - 0.05, RAMP, pcomp)
        m = reg & (zend > zt + 0.3)
        put(np.where(m, zend, 0.0), RAMP, m & (cend == RAMP))
        for k in (BLOCK, LIP, LEDGE, FACE, FRONT, PANEL):
            put(np.where(m, zend, 0.0), k, m & (cend == k))
        bw = ew.get('back')
        if bw:                                  # v5: the wedge behind the block, its top falling north to the deck
            regb = (x >= bw['x0']) & (x <= ew['xw']) & (y >= bw['y0']) & (y < b['yn'] + 0.5)
            zbk = zt + (zh - zt) * np.clip((y - bw['y0']) / (b['yn'] - bw['y0']), 0, 1) - sink
            mb = regb & (zbk > zt + 0.3)
            put(np.where(mb, zbk, 0.0), RAMP, mb)
        extra['slot'] = tuple(tuple(v_) for v_ in slot_ends(p))
    # ---- the ramp: the patch over its quad, down to the deck; brown over the deck's east face under it
    if bl > 0 and not ew:
        r = p['ramp']
        A, B, Cc, D = r['A'], r['B'], r['C'], r['D']
        quad = [(A[0], A[1]), (B[0], B[1]), (Cc[0], Cc[1]), (D[0], D[1])]
        m = in_poly(x, y, quad)
        u, v, zr = ramp_uv(x, y, r)
        zr = zr - sink
        acc.add(d['zb'], zr, RAMP, m & (zr > d['zt'] - 0.5), 'ramp')
        orr = p['slope'].get('onramp')
        if orr:                             # v2: the green skin on the ramp, east of the slope
            # the lean: against the block's east face north of the corner, the slope's own surface south of it,
            # bevelled down eastwards; the skin is whichever is higher, the ramp or the lean
            ln = orr['lean']
            zt_lean = np.where(y >= ln['y'][1], slope_z(y, p['slope'], p['block']),
                               ln['z'][0] + (ln['z'][1] - ln['z'][0]) * np.clip((y - ln['y'][0]) / (ln['y'][1] - ln['y'][0]), 0, 1))
            z_lean = zt_lean - ln['bevel'] * np.maximum(x - 78.3, 0.0) - sink
            inpoly = in_poly(x, y, list(orr['poly']))
            zr_on = np.where(m, zr, d['zt'])            # the ramp where it is, else the deck
            zr = np.where(inpoly, np.maximum(zr_on, z_lean), zr)
            mo = inpoly & (zr > d['zt'] - 0.5) & (x >= 78.3)       # clear of the slope's own surface (no z-fight)
            # its rim: along the edges away from the block (the top edge and the east edge)
            pts_ = np.array(orr['poly'])
            rim = np.zeros(X.shape, bool)
            for (ax_, ay_), (bx_, by_) in ((pts_[0], pts_[1]), (pts_[1], pts_[2])):
                dx_, dy_ = bx_ - ax_, by_ - ay_; L_ = np.hypot(dx_, dy_)
                t_ = np.clip(((x - ax_) * dx_ + (y - ay_) * dy_) / (L_ * L_), 0, 1)
                rim |= np.hypot(x - ax_ - t_ * dx_, y - ay_ - t_ * dy_) < orr['rim']
            acc.add(np.where(m, zr, d['zt']) - 0.5, zr + orr['lift'] + np.where(rim, 1.2, 0.0),
                    np.where(rim, PFRAME, PANEL).astype(np.int16), mo, 'skin')
        sk = r['skirt']
        m = (x >= sk[0]) & (x <= sk[1]) & (y >= r['skirt_y'][0]) & (y <= r['skirt_y'][1]) & deck
        C = np.where(m & (C == PLAT), RAMP, C)
        e0, e1 = slot_ends(p)
        extra['slot'] = (tuple(e0), tuple(e1))

    # ---- the dish's box on the roof
    mt = p['mount']
    m = inbox(x, y, (mt['c'][0] - mt['a'], mt['c'][0] + mt['a']), (mt['c'][1] - mt['a'], mt['c'][1] + mt['a']))
    zm = b['z'] + mt['h'] - sink
    put(np.where(m & (zm > zt + 0.3), zm, 0.0), DMOUNT, m)

    # ---- damaged: the roof caved in over its east half, the bevel and band broken along it, a pane knocked in
    if level >= 1:
        dm = DMG
        hx, hy, rx, ry, rough = dm['hole']
        eh = dblob(x, y, hx, hy, rx, ry, rough, 2101, feat=10.0)
        onblk = np.isin(C, (BLOCK, LIP, RIDGE, DMOUNT)) & (x >= b['x_low'])
        hole = (eh < 0) & onblk
        floor = dm['floor'] + 3.0 * WN.noise(x, y, 9.0, 2102)
        if dm.get('burnt'):                 # v2: burnt and sunk a little all over, deep only in the pits
            pit = np.zeros(X.shape, bool)
            for i_, (qx, qy, qrx, qry) in enumerate(dm['pits']):
                pit |= dblob(x, y, qx, qy, qrx, qry, 0.35, 2160 + i_, feat=6.0) < 0
            floor = np.where(pit, floor, dm['burnt'] + 1.6 * WN.noise(x, y, 7.0, 2163))
        H = np.where(hole, np.minimum(H, floor), H); C = np.where(hole, DEB_BURNT, C)
        lc = (x > dm['lipcut'][0] + 4 * WN.noise(x, y, 6.0, 2103)) & (x < dm['lipcut'][1] + 4 * WN.noise(x, y, 6.0, 2104))
        lipm = lc & np.isin(C, (LIP, FACE)) & (y > l0 - 3.0)
        H = np.where(lipm, H - (6.0 + 4.0 * np.clip(WN.noise(x, y, 5.0, 2105), 0, 1)), H)
        C = np.where(lipm & (C == LIP), DEB_BURNT, C)
        px_, py_, prx, pry = dm['pane']
        ep = dblob(x, y, px_, py_, prx, pry, 0.4, 2106, feat=5.0)
        pane = (ep < 0) & np.isin(C, (PANEL, PFRAME, JOINT))
        H = np.where(pane, H - 7.0, H); C = np.where(pane, DEB_IN, C)

    # ---- everything ground-attached so far stands on the deck: outside the deck's solid core it becomes a slab from
    # the deck's underside (open below, the feet carry it); outside the deck it is dropped (the overhang is a slab)
    edge = (H > 0) & ~core
    acc.add(d['zb'], H, C, edge & deck, 'deck')
    H = np.where(edge, 0.0, H); C = np.where(edge, 0, C).astype(np.int16)
    H = np.where(core, np.maximum(H, zt), H)
    # the feet
    H = np.where(feet, np.maximum(H, d['zb'] + 0.5), H); C = np.where(feet & (H <= d['zb'] + 0.6), FOOT, C)

    # ---- the sockets: green collars round grey plates, four bolts on each plate (on the deck)
    sk = p['sockets']
    for i_s, (cx, cy) in enumerate(sk['c']):
        rr = np.hypot(x - cx, y - cy)
        ring = (rr <= sk['r_out']) & (rr > sk['r_in'])
        ztop = np.full(X.shape, sk['z'], np.float32)
        if sk.get('round'):                 # v2: a lower collar with a rounded top
            rc_ = 0.5 * (sk['r_in'] + sk['r_out']); hw_ = 0.5 * (sk['r_out'] - sk['r_in'])
            prof = np.sqrt(np.clip(1 - ((rr - rc_) / hw_) ** 2, 0, None))
            ztop = (sk['round']['base'] + (sk['round']['top'] - sk['round']['base']) * prof).astype(np.float32)
        if level >= 1 and i_s == 0:
            a0, a1 = DMG['sock']
            ang = np.rad2deg(np.arctan2(y - cy, x - cx))
            brk = (ang > a0 + 6 * WN.noise(x, y, 8.0, 2107)) & (ang < a1 + 6 * WN.noise(x, y, 8.0, 2108))
            ztop = np.where(brk, zt + 1.5 + 3.0 * np.clip(WN.noise(x, y, 4.0, 2109), 0, 1), ztop)
        cl = float(g['collar'])
        if cl < 1:                           # the build-up: the collar grows round both ways from its front (south-east)
            ang = np.rad2deg(np.arctan2(y - cy, x - cx)) - 45.0
            ang = (ang + 180.0) % 360.0 - 180.0
            ring &= np.abs(ang) <= cl * 180.0
        acc.add(zt - 1.0, ztop, SOCK, ring, 'sock')
        if g['plates'] > 0:
            pl = rr <= sk['r_in']
            bolt = np.zeros(X.shape, bool)
            hl = sk.get('holes')
            if g['plates'] >= 1:
                for (bx_, by_) in ((sk['bolts'], 0), (-sk['bolts'], 0), (0, sk['bolts']), (0, -sk['bolts'])):
                    bolt |= np.hypot(x - cx - bx_, y - cy - by_) <= (hl['r'] if hl else sk['bolt_r'])
            acc.add(zt - 1.0, sk['plate'], PLATE, pl & ~bolt, 'plate')
            if hl:                          # v2: holes for the plugs to slot into
                acc.add(zt - 1.0, sk['plate'] - hl['d'], HOLE, pl & bolt, 'plate')
            else:
                acc.add(zt - 1.0, sk['plate'] + sk['bolt_h'], BOLT, pl & bolt, 'plate')
    # ---- the plugs standing in the sockets (west, east)
    pacc = {}

    def A(name):
        if name not in pacc:
            pacc[name] = CropAcc(X.shape, n=3)
        return pacc[name]
    pturn = PG.view_turn(layout, to_local)
    for (cx, cy), kind in zip(sk['c'], plugs):
        if kind:
            pu_, pv_ = PG.plug_frame(x - cx, y - cy, pturn)
            PG.add(kind, pu_, pv_, put, A, t=plug_t, base_w=sk['plate'])

    # ---- the pipes at the deck's east edge on a brown plinth from the ground; bright caps
    pp = p['pipes']
    pl_ = pp['plinth']
    if pl_:
        acc.add(0.0, pl_['z'], RAMP, inbox(x, y, pl_['x'], pl_['y']), 'plinth')
    if ew and g['pipes'] >= 1:                    # v4: straight up in front of the end wall, then into the hip
        ep = ew['pipes']
        for k_p, py_ in enumerate(ep['ys']):
            zb_p = ep['zb'][k_p]
            path = [np.array([ep['x'], py_, zt - 1.0]), np.array([ep['x'], py_, zb_p - 10.0]),
                    np.array([ep['x'] - 3.0, py_, zb_p - 2.0]), np.array([ep['into'], py_, zb_p])]
            if level >= 1 and k_p < len(ep['stub']):
                # v5 (TS frame 1): snapped low down, the top left hanging from its bend; a jagged end
                path[0] = np.array([ep['x'], py_, ep['stub'][k_p]])
                rr_ = np.hypot(x - ep['x'], y - py_)
                jag = ep['stub'][k_p] - 3.5 * np.clip(WN.noise(x, y, 2.5, 2170 + k_p), 0, 1)
                acc.add(jag, ep['stub'][k_p] + 0.5, PIPE, rr_ <= pp['r'], 'pipe')
            add_pipe(acc, x, y, path, pp['r'], PIPE)
        if level >= 1:                            # the broken-off length leaning on the whole pipe
            lo, hi, mb = rod_interval(x, y, ep['bent'][0], ep['bent'][1], pp['r'])
            acc.add(lo, hi, PIPE, mb, 'pipe')
    if ew and g['pipes'] >= 1:                    # the lamp column (GTPLUG_C runs its light down it)
        lt = ew['light']
        rr = np.hypot(x - lt['c'][0], y - lt['c'][1])
        acc.add(zt - 1.0, lt['z'][1], RAMP, rr <= lt['r'], 'lamp')
        acc.add(lt['z'][1], lt['z'][1] + 2.0, PIPE, rr <= lt['r'] + 0.6, 'lamp')
    elif pp.get('screen') and g['pipes'] >= 1:       # v2: the pipes up the ramp and into the building
        for k_p, path in enumerate(pipe_axes(p)):
            if level >= 1:
                fr = DMG['pipe_frac'][k_p]
                if fr < 1:
                    path = cut_polyline(path, fr)
            add_pipe(acc, x, y, path, pp['r'], PIPE)
        if level >= 1:
            lo, hi, mb = rod_interval(x, y, DMG['bent2'][0], DMG['bent2'][1], pp['r'])
            acc.add(lo, hi, PIPE, mb, 'pipe')
    pts = (DMG['pipes'] if level >= 1 else pp['pts']) if (g['pipes'] >= 1 and not pp.get('screen')) else ()
    for k_p, (px_, py_, pz) in enumerate(pts):
        rr = np.hypot(x - px_, y - py_)
        mm = rr <= pp['r']
        if level >= 1:
            if k_p == 2:                     # the third bent over at its middle
                acc.add(0.0, DMG['bent'][0][2], PIPE, mm, 'pipe')
                lo, hi, mb = rod_interval(x, y, DMG['bent'][0], DMG['bent'][1], pp['r'])
                acc.add(lo, hi, PIPE, mb, 'pipe')
            else:                            # snapped: a jagged top, no cap
                acc.add(0.0, pz - 4.0 * np.clip(WN.noise(x, y, 3.0, 2110 + k_p), 0, 1), PIPE, mm, 'pipe')
        else:
            acc.add(0.0, pz - pp['cap'], PIPE, mm, 'pipe')
            acc.add(pz - pp['cap'], pz, PCAP, mm & (rr <= pp['r'] - 0.6), 'pcap')
    if level >= 1 and not pp.get('screen'):
        lo, hi, mb = rod_interval(x, y, DMG['fallen'][0], DMG['fallen'][1], pp['r'] * 0.95)
        acc.add(lo, hi, PIPE, mb, 'pipe')

    # ---- antennas (the build-up: they grow up out of the roof)
    zroof = b['z']
    ga = float(g['ants'])
    if ga <= 0:
        shadow = True                        # (no antennas yet)
    if not shadow:
        hz = lambda zz: zroof + (zz - zroof) * ga
        ants = [(ax, ay, hz(az_), ar) for (ax, ay, az_, ar) in p['ants']]
        for i, (ax, ay, az_, ar) in enumerate(ants):
            if level >= 1 and i in DMG['ants_gone']:
                continue
            if i == 0:
                tl = dict(p['tall'], thin_from=hz(p['tall']['thin_from']))
                lx, ly_ = DMG['lean'] if level >= 1 else (0.0, 0.0)
                fz = (tl['thin_from'] - zroof) / (az_ - zroof)
                mid = (ax + lx * fz, ay + ly_ * fz, tl['thin_from'])
                lo, hi, mm = rod_interval(x, y, (ax, ay, min(zroof, float(hip_west(ax, b))) - 1), mid, ar)
                acc_a.add(lo, hi, ANT, mm, 'ant')
                lo, hi, mm = rod_interval(x, y, mid, (ax + lx, ay + ly_, az_), tl['thin_r'])
                acc_a.add(lo, hi, ANT, mm, 'ant')
                # GTPLUG_B's two lamps on it (lit in the materials)
                if ga >= 1:
                    for lz_ in tl['lamps']:
                        f_ = (lz_ - zroof) / (az_ - zroof)
                        lc_ = (ax + lx * f_, ay + ly_ * f_, lz_)
                        lo, hi, mm = rod_interval(x, y, (lc_[0], lc_[1], lz_ - 2.6), (lc_[0], lc_[1], lz_ + 2.6), 2.6)
                        acc_l.add(lo, hi, LAMP, mm, 'lamp')
            else:
                lo, hi, mm = rod_interval(x, y, (ax, ay, min(zroof, float(hip_west(ax, b))) - 1), (ax, ay, az_), ar)
                acc_a.add(lo, hi, ANT, mm, 'ant')
        tb = dict(p['tbar'], z=tuple(hz(zz) for zz in p['tbar']['z']))
        ax, ay = p['ants'][2][:2]
        for zc in tb['z']:
            lo, hi, mm = rod_interval(x, y, (ax - tb['half'], ay + tb['half'], zc), (ax + tb['half'], ay - tb['half'], zc),
                                      tb['r'])
            acc_a.add(lo, hi, ANT, mm, 'tbar')
        fk = dict(p['fork'], z=hz(p['fork']['z']), zc=hz(p['fork']['zc']), tops=tuple(hz(zz) for zz in p['fork']['tops']))
        fx, fy = fk['c']
        lo, hi, mm = rod_interval(x, y, (fx, fy, zroof - 1), (fx, fy, fk['z']), fk['r'])
        acc_a.add(lo, hi, ANT, mm, 'fork')
        lo, hi, mm = rod_interval(x, y, (fx - fk['half'], fy + fk['half'] * 0.3, fk['zc']),
                                  (fx + fk['half'], fy - fk['half'] * 0.3, fk['zc']), fk['r'])
        acc_a.add(lo, hi, ANT, mm, 'fork')
        for sgn, ztop in ((-1, fk['tops'][0]), (1, fk['tops'][1])):
            px_, py_ = fx + sgn * fk['half'], fy - sgn * fk['half'] * 0.3
            lo, hi, mm = rod_interval(x, y, (px_, py_, fk['zc']), (px_, py_, ztop), fk['r'] * 0.85)
            acc_a.add(lo, hi, ANT, mm, 'fork')

    # ---- damaged: bare roof beams across the hole
    if level >= 1:
        for (b0, b1) in DMG['beams']:
            if DMG.get('burnt'):            # v2: on the burnt roof, not down in a crater
                b0 = (b0[0], b0[1], max(b0[2], DMG['burnt'] + 2.0)); b1 = (b1[0], b1[1], max(b1[2], DMG['burnt'] + 2.0))
            lo, hi, mm = rod_interval(x, y, b0, b1, DMG['beam_r'])
            acc_a.add(lo, hi, BEAM, mm, 'beam')

    # ---- the dish on its post (turned by GTPLUG_A): a shallow disc
    if g['dish'] > 0:
        dd = p['dish']
        az = np.deg2rad(dd['az'] if dish_az is None else dish_az)
        cx, cy = mt['c']
        z0 = b['z'] + mt['h']
        lo, hi, mm = rod_interval(x, y, (cx, cy, z0 - 1), (cx, cy, z0 + dd['post'][1]), dd['post'][0])
        acc_a.add(lo, hi, DMOUNT, mm, 'post')
    if g['dish'] >= 1:
        el = np.deg2rad(dd['el'])
        n = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
        ctr = np.array([cx, cy, z0 + dd['post'][1] + dd['R'] * 0.55]) + n * dd['off']
        lo, hi, mm = rod_interval(x, y, ctr - n * dd['t'] / 2, ctr + n * (dd['t'] / 2 + dd['depth'] * 0.3), dd['R'])
        acc_a.add(lo, hi, DISH, mm, 'dish')
    return hd.Scene(H, C, acc.slabs() + acc_a.slabs() + acc_l.slabs() + pack_slabs(pacc.values(), X.shape),
                    extra)


FLAT = {PLAT: (150, 150, 150), FOOT: (110, 100, 80), BLOCK: (190, 160, 100), LIP: (235, 205, 140),
        FACE: (110, 110, 170), ROOF: (200, 170, 110), RIDGE: (205, 175, 115), PANEL: (0, 150, 0), PFRAME: (0, 215, 0),
        SOCK: (0, 210, 0), PLATE: (140, 140, 140), BOLT: (230, 230, 230), RAMP: (130, 100, 60), PIPE: (190, 190, 190),
        PCAP: (240, 240, 230), ANT: (90, 90, 130), DISH: (60, 60, 70), DMOUNT: (110, 110, 140), LAMP: (255, 255, 255),
        SLAB: (150, 150, 150), STEP: (200, 150, 70), SLOT: (20, 20, 20), LEDGE: (175, 150, 95), FRONT: (100, 80, 45),
        CORE: (60, 60, 60), BEAM: (150, 150, 156), DEB_BURNT: (60, 40, 30), DEB_IN: (30, 30, 30), DEBRIS: (120, 110, 90),
        JOINT: (20, 40, 20), HOLE: (20, 20, 22)}
FLAT.update(PG.FLAT)
