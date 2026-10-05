"""
mcv2.py - the TS MCV rebuilt the way the Titan and the Wolverine are: TS's own MCV.VXL (45 x 31 x 15 voxels) as the
blueprint for where every part is and how big, each part modelled clean (flat plates, true slopes, round wheels,
bevelled edges), with the shapes and details of Westwood's own renders of the MCV (the GDI pair Luke sent, the Nod
concept): track pods as boxes over a proper track (belt loop, sprocket, idler, road wheels), a segmented spine down the
middle (TS's light grey "boom"), a cab with a sloped visor and a louvred grille, a louvred ramp under the spine's front,
a rack of crates.  The voxel is what the game shows, so its layout and its colours rule; the renders fill in the detail
the voxel loses.

Voxel frame (continuous): x forward from the back (0) to the hitch (45), y across from the unit's right side (0) to its
left (31), z up from the ground; voxel i spans i..i+1.  (The cab and the house-colour deck panels are on the unit's
right, the crate rack and the tow hitch on its left, as in the game.)
Body frame for rendering: u forward, v right, w up, in voxels, the unit's position (the HVA origin, voxel
(21.16, 15.5)) at the origin:  u = x - CX,  v = CY - y,  w = z.
"""
import numpy as np
import rc

CX, CY = 21.16, 15.5
YW = 31.0                                          # the voxel's width (y 0..31): the left side mirrors the right

(COVER, BELT, CORE, WHEEL, HUB, HULL, UNDER, BUMPER, DECK, RAIL, WALL, BLOCK, OPENING, HPANEL, HATCH, CAB, VISOR,
 NOSE, ROOF, PED, SADDLE, CAP, HOUSING, BOOM_G, BOOM_W, JOINT, TIP, PULLEY, RAMP, LDECK, LRAIL, CRATE, LID, DIVIDER,
 FLBLOCK, FLTOP, HITCH, COUPLING, LAMP_Y, LAMP_W, VENT, STEP, SKIRT_IN, FENDER_LIP, GLASS, FRAME, GRILLE, CABIN,
 CPLATE) = range(81, 130)
HOUSE = (COVER, HPANEL, SKIRT_IN, FENDER_LIP)


# ------------------------------------------------------------------------------------------------ helpers
def U(x):
    return x - CX


def V(y):
    return CY - y


def B(x0, x1, y0, y1, z0, z1, comp, ch=0.0, name=''):
    """a box over continuous voxel coordinates; ch: chamfer, a scalar or (edges along x, along y, vertical)."""
    c = np.array([(x0 + x1) / 2 - CX, CY - (y0 + y1) / 2, (z0 + z1) / 2])
    h = np.array([(x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2])
    return rc.box(c, np.eye(3), h, comp, ch, name)


def _convex(P):
    P = np.asarray(P, float)
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
            raise ValueError('not convex: %s' % (P.tolist(),))


def PXZ(pts, y0, y1, comp, ch=0.0, name='', sides=(True, True)):
    """a convex polygon in (x, z) extruded over y0..y1; ch chamfers its edges against the y faces (sides: whether
    the y0 face's and the y1 face's edges are chamfered)."""
    _convex(pts)
    P = np.array([(x - CX, z) for x, z in pts], float)
    cen = P.mean(0)
    v0, v1 = CY - y1, CY - y0
    cons = [rc.Plane((0, 1, 0), v1), rc.Plane((0, -1, 0), -v0)]
    for k in range(len(P)):
        a, b = P[k], P[(k + 1) % len(P)]
        d = b - a
        n = np.array([d[1], -d[0]]); n = n / np.linalg.norm(n)
        if n @ (cen - a) > 0:
            n = -n
        cons.append(rc.Plane((n[0], 0, n[1]), n @ a))
        if ch > 0:
            for s, on in ((1.0, sides[0]), (-1.0, sides[1])):
                if not on:
                    continue
                m = np.array([n[0], s, n[1]]); m = m / np.linalg.norm(m)
                vv = v1 if s > 0 else -v0
                cons.append(rc.Plane(m, (n @ a + vv - ch) / np.sqrt(2.0)))
    c = np.array([cen[0], (v0 + v1) / 2, cen[1]])
    r = float(np.max(np.linalg.norm(P - cen, axis=1)))
    return rc.Part(cons, comp, name, sphere=(c, float(np.hypot(r, (v1 - v0) / 2)) + 1e-3))


def PYZ(pts, x0, x1, comp, ch=0.0, name=''):
    """a convex polygon in (y, z) extruded over x0..x1 (a cross-section run along the unit); ch chamfers its edges
    against the two x faces."""
    _convex(pts)
    P = np.array([(CY - y, z) for y, z in pts], float)
    cen = P.mean(0)
    u0, u1 = x0 - CX, x1 - CX
    cons = [rc.Plane((1, 0, 0), u1), rc.Plane((-1, 0, 0), -u0)]
    for k in range(len(P)):
        a, b = P[k], P[(k + 1) % len(P)]
        d = b - a
        n = np.array([d[1], -d[0]]); n = n / np.linalg.norm(n)
        if n @ (cen - a) > 0:
            n = -n
        cons.append(rc.Plane((0, n[0], n[1]), n @ a))
        if ch > 0:
            for s in (1.0, -1.0):
                m = np.array([s, n[0], n[1]]); m = m / np.linalg.norm(m)
                uu = u1 if s > 0 else -u0
                cons.append(rc.Plane(m, (n @ a + uu - ch) / np.sqrt(2.0)))
    c = np.array([(u0 + u1) / 2, cen[0], cen[1]])
    r = float(np.max(np.linalg.norm(P - cen, axis=1)))
    return rc.Part(cons, comp, name, sphere=(c, float(np.hypot(r, (u1 - u0) / 2)) + 1e-3))


def wheel(x, z, r, y0, y1, comp, name='wheel', bevel=0.0):
    """a wheel (a cylinder across the unit, axis along y) centred at (x, z), from y0 to y1; bevel cuts a 45-degree
    edge round both faces."""
    p0 = np.array([U(x), V(y0), z]); p1 = np.array([U(x), V(y1), z])
    extra = []
    if bevel > 0:
        # a cone-like bevel can't be a plane; approximate it by trimming the rim with 16 planes per face
        a = (p1 - p0) / np.linalg.norm(p1 - p0)
        for k in range(16):
            th = 2 * np.pi * (k + 0.5) / 16
            rad = np.array([np.cos(th), 0.0, np.sin(th)])
            for end, s in ((p0, -1.0), (p1, 1.0)):
                n = rad + s * a; n = n / np.linalg.norm(n)
                q = end + rad * (r - bevel)
                extra.append(rc.Plane(n, n @ q))
    return rc.cylinder(p0, p1, r, comp, name, extra)


def cyl_x(x0, x1, y, z, r, comp, name=''):
    """a cylinder along the unit (axis along x)."""
    return rc.cylinder(np.array([U(x0), V(y), z]), np.array([U(x1), V(y), z]), r, comp, name)


def cyl_z(x, y, z0, z1, r, comp, name=''):
    """an upright cylinder."""
    return rc.cylinder(np.array([U(x), V(y), z0]), np.array([U(x), V(y), z1]), r, comp, name)


def mirror_y(y):
    return YW - y


def side(fn, left):
    """y-range helper: on the left side the range mirrors."""
    def yr(a, b):
        if not left:
            return a, b
        return mirror_y(b), mirror_y(a)
    return yr


# ------------------------------------------------------------------------------------------------ the pods
# per pod: the cover's x span, the belt (end wheel centres, ground run), road wheels, the skirt's segments (TS's)
PODS = (dict(x0=1.0, x1=19.0, ends=(3.7, 17.3), ground=(5.2, 15.8), road=(6.65, 9.35, 12.05, 14.75),
             skirt=((1.0, 4.0), (5.0, 9.0), (11.0, 19.2)), skirt_l=((1.0, 4.0), (5.0, 9.0), (11.0, 19.2)),
             apron=(0.85, 2.0, 2.9)),
        dict(x0=22.0, x1=37.0, ends=(23.7, 35.3), ground=(25.2, 33.8), road=(26.75, 29.5, 32.25),
             skirt=((22.0, 31.0), (35.0, 37.2)), skirt_l=((22.0, 23.0), (24.0, 31.0), (35.0, 37.2)),
             apron=(21.85, 22.6, 23.2)))
R_END = 1.7                 # the sprocket and the idler, wrapped in the belt
Z_END = 2.3
R_ROAD = 1.1                # road wheels
Z_ROAD = 1.55
BELT_TOP = 4.0


def pod(P, left):
    yr = side(None, left)
    out = []
    x0, x1 = P['x0'], P['x1']
    # ---------------------------------------------------------------- the cover (house colour)
    out.append(B(x0, x1, *yr(0.0, 6.0), 5.0, 6.0, COVER, ch=(0.28, 0.28, 0.28), name='cover'))
    # the front mudguard: from the plate's front edge down and forward to the ground's side of the idler
    out.append(PXZ([(x1 - 0.3, 6.0), (x1 + 0.25, 6.0), (x1 + 1.1, 3.6), (x1 + 1.1, 3.0), (x1 + 0.5, 3.0),
                    (x1 - 0.3, 5.2)], *yr(0.0, 6.0), FENDER_LIP, ch=0.2, name='lip'))
    # the rear apron
    a0, a1, a2 = P['apron']
    out.append(PXZ([(a0, 6.0), (a1, 6.0), (a2, 4.2), (a2, 4.0), (a0 + 0.35, 4.0), (a0, 5.0)], *yr(1.0, 6.0), FENDER_LIP,
                   ch=0.18, name='apron'))
    # the outer skirt: a plate a voxel in from the outer face, with TS's gaps
    for sa, sb in (P['skirt_l'] if left else P['skirt']):
        out.append(B(sa, sb, *yr(1.0, 1.55), 4.0, 5.05, COVER, ch=(0.15, 0.12, 0.15), name='skirt'))
    # the inner skirt along the hull
    out.append(B(x0, x1 + 0.2, *yr(5.0, 6.0), 4.0, 5.05, SKIRT_IN, ch=(0.15, 0.15, 0.15), name='skirt_in'))
    # the space under the cover behind the skirt: dark (the track's top run in the cover's shadow)
    out.append(B(x0 + 0.4, x1 - 0.2, *yr(1.55, 5.0), 4.0, 5.0, CORE, name='undercover'))
    # ---------------------------------------------------------------- the track
    ea, eb = P['ends']
    ga, gb = P['ground']
    yo, yi = yr(0.15, 5.0)
    # the belt wrapped round the sprocket (back) and the idler (front)
    for xe in (ea, eb):
        out.append(wheel(xe, Z_END, R_END, *yr(0.15, 5.0), BELT, name='belt_end'))
    # the top run and the bottom run
    out.append(B(ea, eb, *yr(0.15, 5.0), BELT_TOP - 0.72, BELT_TOP, BELT, ch=(0.12, 0.0, 0.0), name='belt_top'))
    rl = Z_END - R_END * np.sin(np.deg2rad(70))          # where the bottom run meets the end wheels
    out.append(PXZ([(ea + R_END * np.cos(np.deg2rad(70)), rl + 0.02), (ga, 0.0), (gb, 0.0),
                    (eb - R_END * np.cos(np.deg2rad(70)), rl + 0.02), (eb - R_END * np.cos(np.deg2rad(70)), 0.8),
                    (ea + R_END * np.cos(np.deg2rad(70)), 0.8)],
                   *yr(0.15, 5.0), BELT, ch=0.1, name='belt_bottom'))
    # the inside of the loop, deep in shadow
    out.append(B(ea, eb, *yr(0.95, 5.0), 0.7, BELT_TOP - 0.7, CORE, name='core'))
    # the sprocket's and the idler's hubs, the road wheels and their hubs
    for xe in (ea, eb):
        out.append(wheel(xe, Z_END, 0.95, *yr(0.0, 0.15), HUB, name='hub'))
    for xr in P['road']:
        out.append(wheel(xr, Z_ROAD, R_ROAD, *yr(0.42, 4.6), WHEEL, name='road', bevel=0.16))
        out.append(wheel(xr, Z_ROAD, 0.5, *yr(0.3, 0.42), HUB, name='road_hub'))
    return out


# ------------------------------------------------------------------------------------------------ the model
def parts():
    P = []
    for p in PODS:
        P += pod(p, False)
        P += pod(p, True)
    # ---------------------------------------------------------------- hull
    P.append(B(1.0, 40.0, 5.0, 26.0, 2.0, 4.0, HULL, ch=(0.3, 0.3, 0.3), name='hull'))
    P.append(B(3.0, 36.0, 6.0, 25.0, 1.0, 2.05, UNDER, ch=0.2, name='under'))
    for ya, yb in ((5.0, 6.0), (25.0, 26.0)):
        P.append(B(19.0, 22.0, ya, yb, 3.9, 6.0, HULL, ch=(0.15, 0.15, 0.15), name='hull_side'))
    P.append(B(37.2, 40.0, 5.0, 6.0, 3.9, 6.0, HULL, ch=(0.15, 0.15, 0.15), name='hull_side'))
    P.append(B(37.2, 40.0, 25.0, 26.0, 3.9, 5.0, HULL, ch=(0.15, 0.15, 0.15), name='hull_side'))
    # bumpers: back (two, either side of the middle), front (under the cab)
    for ya, yb in ((6.0, 15.0), (16.0, 25.0)):
        P.append(PXZ([(0.0, 1.1), (1.9, 1.0), (1.9, 2.0), (1.2, 3.0), (0.0, 3.0)], ya, yb, BUMPER, ch=0.22, name='bumper'))
    P.append(PXZ([(38.6, 1.0), (42.0, 1.0), (42.0, 2.6), (41.6, 3.0), (39.6, 3.0), (38.6, 2.2)], 6.0, 15.0, BUMPER,
                 ch=0.22, name='bumper'))
    # ---------------------------------------------------------------- right deck
    P.append(B(1.0, 40.0, 6.0, 14.0, 3.9, 6.0, DECK, ch=(0.2, 0.2, 0.2), name='deck'))
    # the outer rail: a low parapet, notched where the vents and steps are
    P.append(B(1.0, 40.0, 5.0, 6.0, 5.9, 7.0, RAIL, ch=(0.22, 0.22, 0.22), name='rail'))
    for a, b in ((2.0, 6.0), (8.0, 34.0), (35.0, 39.0)):
        P.append(B(a, b, 5.0, 6.0, 6.9, 8.0, RAIL, ch=(0.24, 0.24, 0.24), name='rail'))
    # the inner wall along the spine's channel
    P.append(B(1.0, 40.0, 14.0, 15.0, 5.9, 7.0, WALL, ch=(0.2, 0.2, 0.2), name='wall'))
    P.append(B(2.0, 39.0, 14.0, 15.0, 6.9, 8.0, WALL, ch=(0.24, 0.24, 0.24), name='wall'))
    # the rear block: a housing over the back of the deck, its top at 10, its back and outer side down to the deck,
    # open under its front (TS); the house-colour panel on top, a hatch at its outer back corner
    P.append(B(2.0, 14.0, 6.0, 15.0, 7.9, 10.0, BLOCK, ch=(0.42, 0.42, 0.3), name='block'))
    P.append(B(2.0, 4.1, 6.0, 15.0, 5.9, 8.2, BLOCK, ch=(0.25, 0.25, 0.25), name='block_back'))
    P.append(B(2.0, 19.0, 6.0, 7.0, 5.9, 8.2, BLOCK, ch=(0.22, 0.22, 0.22), name='block_side'))
    P.append(B(4.1, 12.6, 7.0, 14.0, 5.9, 7.95, OPENING, name='opening'))
    P.append(B(5.0, 13.0, 8.0, 14.0, 9.9, 10.8, HPANEL, ch=(0.26, 0.26, 0.26), name='hpanel'))
    P.append(B(5.75, 8.25, 6.3, 7.95, 9.9, 10.22, HATCH, ch=(0.12, 0.12, 0.12), name='hatch'))
    # the house-colour panel block and strip, held between the rail and the wall a voxel above the deck
    P.append(B(20.0, 28.0, 6.0, 14.0, 7.0, 9.0, HPANEL, ch=(0.3, 0.3, 0.3), name='hpanel'))
    P.append(B(29.0, 31.0, 6.0, 14.0, 7.0, 9.0, HPANEL, ch=(0.26, 0.26, 0.26), name='hpanel'))
    # under them, the deck's floor seen through the gap (in shadow)
    # ---------------------------------------------------------------- the cab
    # the front block (TS's stepped block at the right front; the cockpit is at the left front): its top at 10 to x 38,
    # TS's step (to 9 over x 38-39) and the nose (to 7 over x 39-40), each edge bevelled
    P.append(B(31.0, 38.05, 6.0, 15.0, 5.9, 10.0, CAB, ch=(0.38, 0.38, 0.38), name='cab'))
    P.append(B(37.8, 39.1, 6.0, 15.0, 5.9, 9.0, CAB, ch=(0.3, 0.3, 0.3), name='cabstep'))
    P.append(PXZ([(38.7, 3.0), (40.2, 3.0), (40.2, 6.5), (39.5, 7.2), (38.7, 7.2)], 5.0, 15.0, NOSE, ch=0.25,
                 name='nose'))
    # across the step's front, where TS alternates orange and ochre: a louvred vent in an orange frame
    P.append(B(39.02, 39.16, 6.6, 14.4, 7.75, 8.72, VISOR, name='vent'))
    for za, zb in ((7.48, 7.78), (8.68, 8.98)):
        P.append(B(38.98, 39.28, 6.3, 14.7, za, zb, FRAME, ch=(0.08, 0.08, 0.08), name='frame'))
    for ya, yb in ((6.3, 6.62), (14.38, 14.7)):
        P.append(B(38.98, 39.28, ya, yb, 7.48, 8.98, FRAME, ch=(0.08, 0.08, 0.08), name='frame'))
    # the nose's grille between TS's two orange bands, in its own orange frame
    P.append(B(40.12, 40.26, 6.3, 13.7, 4.4, 5.6, GRILLE, name='grille'))
    for za, zb in ((4.08, 4.42), (5.58, 5.92)):
        P.append(B(40.06, 40.36, 5.98, 14.02, za, zb, FRAME, ch=(0.08, 0.08, 0.08), name='frame'))
    for ya, yb in ((5.98, 6.32), (13.68, 14.02)):
        P.append(B(40.06, 40.36, ya, yb, 4.08, 5.92, FRAME, ch=(0.08, 0.08, 0.08), name='frame'))
    # the roof: an orange panel (TS) and the hatch at its outer edge (TS's black pair at x 34, y 6-7)
    P.append(B(31.9, 36.6, 8.4, 14.2, 9.95, 10.28, ROOF, ch=(0.12, 0.12, 0.12), name='roof'))
    P.append(B(33.65, 35.35, 6.35, 8.0, 9.95, 10.34, HATCH, ch=(0.1, 0.1, 0.1), name='cabhatch'))
    # foot steps on its outer side (TS's olive bits at x 33 and 35, low on that side)
    for xs in (33.0, 35.0):
        P.append(B(xs, xs + 0.9, 5.55, 6.02, 6.45, 6.75, STEP, ch=0.08, name='step'))
    # ---------------------------------------------------------------- the channel, the pedestal, the spine
    P.append(B(1.0, 40.0, 15.0, 18.0, 3.9, 5.0, DECK, ch=0.0, name='channel'))
    P.append(PXZ([(8.0, 4.95), (14.0, 4.95), (15.2, 6.0), (16.0, 7.2), (16.0, 11.05), (6.0, 11.05), (6.0, 7.2),
                  (6.8, 6.0)], 15.0, 18.0, PED, ch=0.25, name='pedestal'))
    P.append(B(5.6, 16.4, 14.5, 18.5, 11.0, 12.02, SADDLE, ch=(0.25, 0.25, 0.25), name='saddle'))
    # the spine (TS's boom): a cap, the grey housing with its dark hatch and white ribs, the long light section,
    # a collar with a slot, the narrower front section with a grey band and a dark tip, the pulley block under it
    P.append(B(4.0, 5.1, 15.0, 18.0, 12.0, 14.0, CAP, ch=(0.3, 0.3, 0.3), name='cap'))
    P.append(PYZ([(14.0, 12.0), (19.0, 12.0), (19.0, 14.4), (18.4, 15.0), (14.6, 15.0), (14.0, 14.4)], 5.0, 15.0,
                 HOUSING, ch=0.3, name='housing'))
    for xr in (13.0, 16.0):
        P.append(PYZ([(13.85, 11.9), (19.15, 11.9), (19.15, 14.5), (18.5, 15.15), (14.5, 15.15), (13.85, 14.5)],
                     xr, xr + 0.9, JOINT, ch=0.12, name='rib'))
    P.append(PYZ([(14.0, 12.0), (18.0, 12.0), (18.0, 14.35), (17.35, 15.0), (14.65, 15.0), (14.0, 14.35)], 15.0, 19.5,
                 BOOM_G, ch=0.2, name='boom_g'))
    P.append(PYZ([(14.0, 12.0), (18.0, 12.0), (18.0, 14.35), (17.35, 15.0), (14.65, 15.0), (14.0, 14.35)], 19.5, 28.0,
                 BOOM_W, ch=0.25, name='boom_w'))
    P.append(PYZ([(13.9, 11.9), (18.1, 11.9), (18.1, 13.6), (17.6, 14.2), (14.4, 14.2), (13.9, 13.6)], 28.0, 30.0,
                 JOINT, ch=0.2, name='collar'))
    P.append(PYZ([(15.0, 12.0), (18.0, 12.0), (18.0, 13.55), (17.45, 14.1), (15.55, 14.1), (15.0, 13.55)], 30.0, 37.0,
                 BOOM_W, ch=0.25, name='front'))
    P.append(PYZ([(14.9, 11.92), (18.1, 11.92), (18.1, 13.6), (17.5, 14.2), (15.5, 14.2), (14.9, 13.6)], 34.0, 35.9,
                 BOOM_G, ch=0.12, name='band'))
    P.append(PYZ([(15.0, 12.0), (18.0, 12.0), (18.0, 13.55), (17.45, 14.1), (15.55, 14.1), (15.0, 13.55)], 37.0, 38.0,
                 TIP, ch=0.3, name='tip'))
    P.append(B(33.0, 37.0, 15.1, 17.9, 10.95, 12.05, PULLEY, ch=(0.35, 0.2, 0.2), name='pulley'))
    P.append(wheel(35.0, 11.3, 0.62, 14.85, 18.15, PULLEY, name='sheave'))
    # the ramp under the spine's front (TS's dark cradle rising in steps): one slope, louvred
    P.append(PXZ([(26.0, 4.95), (41.0, 4.95), (41.0, 8.0), (30.2, 8.0)], 15.0, 18.0, RAMP, ch=0.18, name='ramp'))
    # ---------------------------------------------------------------- left deck: the crate rack
    P.append(B(1.0, 30.0, 18.0, 25.0, 3.9, 6.0, LDECK, ch=(0.2, 0.2, 0.2), name='ldeck'))
    # the rack's frame: an inner rail along y 18, the outer edge along y 24, cross members under the dividers
    P.append(B(2.0, 29.0, 18.0, 19.0, 5.9, 8.0, LDECK, ch=(0.22, 0.22, 0.22), name='rack_in'))
    P.append(B(1.0, 30.0, 24.0, 25.0, 5.9, 7.0, LDECK, ch=(0.2, 0.2, 0.2), name='rack_out'))
    CR = ((3.0, 6.0), (7.0, 14.0), (15.0, 21.0), (22.0, 24.0), (26.0, 29.0))
    for k, (a, b) in enumerate(CR):
        P.append(B(a + 0.06, b - 0.06, 19.0, 24.0, 5.9, 7.7, CRATE, ch=(0.2, 0.2, 0.2), name='crate'))
        P.append(B(a + 0.22, b - 0.22, 19.2, 23.8, 7.6, 8.0, LID, ch=(0.16, 0.16, 0.16), name='lid'))
    for a, b in ((2.0, 3.0), (6.0, 7.0), (14.0, 15.0), (21.0, 22.0), (24.0, 26.0), (29.0, 30.0)):
        P.append(B(a, b, 19.0, 24.0, 5.9, 7.35, DIVIDER, ch=(0.12, 0.12, 0.12), name='divider'))
    # lamps where TS puts its bright voxels: yellow and white on the crate lids
    for (lx, ly, col) in ((3.5, 21.5, LAMP_Y), (4.5, 21.5, LAMP_Y), (3.5, 22.5, LAMP_W), (12.5, 22.5, LAMP_Y),
                          (19.6, 22.5, LAMP_Y), (27.5, 21.5, LAMP_Y), (27.5, 22.5, LAMP_W)):
        P.append(cyl_z(lx, ly, 7.95, 8.22, 0.34, col, name='lamp'))
    # the rail along the deck's outer edge: short pieces (TS's)
    for a, b in ((1.0, 2.0), (4.0, 7.0), (8.0, 10.0), (12.0, 18.0), (19.0, 27.0), (29.0, 30.0)):
        P.append(B(a, b, 25.0, 25.9, 5.9, 6.75, LRAIL, ch=(0.16, 0.16, 0.16), name='lrail'))
    # ---------------------------------------------------------------- the cockpit (the left front: Luke)
    # TS's block at the left front is the cockpit: its body to 6, the cabin on it with its roof at 8 (TS's orange top,
    # with TS's two yellow lamps) and a big sloping windscreen down to the orange chin that sticks out ahead of the hull
    # (TS's dark voxels there are the glass); the chin carries a framed grille (TS's orange and ochre alternating).
    P.append(B(30.0, 40.2, 18.0, 25.0, 3.9, 6.1, FLBLOCK, ch=(0.3, 0.3, 0.3), name='flblock'))
    # the cabin: its windscreen set into it - the cabin's own bodywork frames the glass (the pillars at the sides, the
    # header under the roof's edge, the sill above the bonnet), the glass one pane a little below that surface
    P.append(PXZ([(31.0, 4.85), (42.895, 4.85), (38.0899, 8.0), (31.0, 8.0)], 19.55, 23.45, CABIN, ch=0.0, name='cabin'))
    for ya, yb, sd in ((18.9, 19.55, (True, False)), (23.45, 24.1, (False, True))):
        P.append(PXZ([(31.0, 4.85), (42.9, 4.85), (42.9, 5.05), (38.4, 8.0), (31.0, 8.0)], ya, yb, CABIN, ch=0.3,
                     name='cabin', sides=sd))
    P.append(PXZ([(38.714, 7.567), (38.8182, 7.7259), (38.3916, 8.0055), (38.2875, 7.8466)], 19.5, 23.5, CABIN, name='cabin'))
    P.append(PXZ([(42.8042, 4.8856), (42.9084, 5.0445), (42.4818, 5.3241), (42.3777, 5.1652)], 19.5, 23.5, CABIN, name='cabin'))
    P.append(PXZ([(42.425, 5.1462), (38.6777, 7.6028), (38.6996, 7.6362), (42.4469, 5.1796)], 19.5, 23.5, GLASS, name='glass'))
    P.append(B(31.4, 37.9, 19.3, 23.7, 7.9, 8.22, FLTOP, ch=(0.12, 0.12, 0.12), name='fltop'))
    for (lx, ly, col) in ((33.5, 19.75, LAMP_Y), (34.5, 23.25, LAMP_Y)):
        P.append(cyl_z(lx, ly, 8.15, 8.42, 0.32, col, name='lamp'))
    # the bonnet and nose: one shape flowing on from the windscreen's sill - the bonnet sloping gently down to a
    # bevelled front edge, the front face (TS's orange chin) sticking out ahead of the hull, its grille set into it
    P.append(PXZ([(38.4, 2.0), (44.95, 2.0), (44.95, 4.4), (44.75, 4.6), (42.9, 5.06), (38.4, 5.06)], 18.9, 24.1,
                 CPLATE, ch=0.3, name='bonnet'))
    P.append(PXZ([(44.9, 3.75), (45.2, 3.75), (45.2, 4.15), (44.95, 4.4), (44.9, 4.4)], 18.9, 24.1, HITCH, ch=0.2,
                 name='nose_front'))
    P.append(B(44.9, 45.2, 18.9, 24.1, 2.0, 2.35, HITCH, ch=(0.12, 0.2, 0.12), name='nose_front'))
    for ya, yb in ((18.9, 19.55), (23.45, 24.1)):
        P.append(B(44.9, 45.2, ya, yb, 2.0, 4.15, HITCH, ch=(0.12, 0.2, 0.12), name='nose_front'))
    P.append(B(44.93, 45.0, 19.5, 23.5, 2.3, 3.8, GRILLE, name='grille'))
    return P


if __name__ == '__main__':
    ps = parts()
    print(len(ps), 'parts')
