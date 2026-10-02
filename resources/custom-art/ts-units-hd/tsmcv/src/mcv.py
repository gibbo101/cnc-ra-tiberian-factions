"""
mcv.py - the TS MCV (MCV.VXL, 45 x 31 x 15 voxels) as convex parts for the rc ray caster, read voxel by voxel from
the layer dumps (vchars.py, vfaces.py) so every step, gap and detail sits where TS has it.

Voxel frame: x forward from the back (0) to the hitch (44), y across from the unit's right side (0) to its left
(30) (the in-mod frames, rendered from the same voxel, are this way round: the cab and the green deck panels on
the right, the shelf and the hitch on the left), z up from the ground; voxel i spans i..i+1.  Ranges below are
inclusive voxel indices.
Body frame for rendering: u forward, v right, w up, in voxels, the unit's position (the HVA origin, voxel
(21.16, 15.5)) at the origin.

The MCV, from the voxel:
  tracks    four units (x 1-19 and 22-37, right y 0-5, left y 25-30): a house-colour cover (a plate at z 5 over
            y 0-5, a skirt a voxel in from the outer face at z 4 with gaps where the dark track shows through, end
            lips, the front lip down to z 3); the track belt below, its loop z 0-3 with sloped ends (z 0 x 5-16,
            z 1 x 3-17, z 2-3 x 2-18); dark bits of the track proud of the skirt at z 4 where TS has them
  hull      the lower hull (x 1-39, y 5-25, z 2-3) on a dark underside with bumpers front and back (z 1-2)
  right     the right deck (y 6-13, top z 5) with its rail along the outer edge (y 5, z 6-7, a notch at x 6-7) and
            the spine along its inner edge (y 14, z 5-7): the rear block (x 3-13, top z 9, its back stepped
            down to the rim at x 1-2, open underneath at its front) with a house-colour panel on top (x 5-12,
            y 8-13, z 10) and a dark hatch at its outer back corner; a house-colour panel block (x 20-27, z 7-8)
            and strip (x 29-30) bridging rail and spine with a voxel's gap under them; the cab at the front
            (x 31-37, top z 9; its front stepped down: x 38 to z 8, x 39 to z 6) with a hatch on its roof and a
            grille across its front
  channel   between the spine and the left deck (y 15-17) a floor at z 4: the crane's pedestal on it (x 6-15,
            z 5-10, tapering at its foot), its saddle (z 11, a dark band along its right side), the boom on top
            (z 12-14): a cap, the dark-topped housing (x 5-14, y 14-18) with two white bands across, the main tube
            (x 20-27, y 14-17), a joint (x 28-29, a slot in its top), the front section (x 30-37, y 15-17, z 12-13);
            under the boom's front a dark cradle rising in steps from x 26 to the front (z 5-7)
  left      the left deck (y 18-24, x 1-29, to z 6) carrying the shelf (z 7, x 2-28, y 18-23: five crates); a
            rail of short pieces along its outer edge (y 25, z 6); the front-left block (x 31-39, top z 7 over x
            32-37); the tow hitch at the front (x 37-44: an orange frame and plate, a dark coupling, z 2-6)
"""
import numpy as np
import rc

CX, CY = 21.16, 15.5

(COVER, TRACK, TBIT, HULL, UNDER, DECK, BUMPER, BLOCK, PANEL, CAB, PLATE, SADDLE, BOOM_D, BOOM_G, BOOM_W, BOOM_T,
 RAIL, SHELF, RECESS, HITCH, EYE, RIM, SPINE, POST, BAND, CRATE) = range(81, 107)
CRATES = ((3, 5), (7, 13), (15, 20), (22, 23), (26, 28))        # the shelf's crates (x), dividers between them
DIVIDERS = ((6, 6), (14, 14), (21, 21), (24, 25))
HOUSE = (COVER, PANEL)


def _box_cons(lo, hi, ch=0.0, edges='all'):
    """planes of the axis-aligned box lo..hi (body frame) with its edges chamfered by ch (scalar or per edge family:
    edges along u, along v, along w); edges='top' chamfers only the top edges and the vertical ones."""
    lo = np.asarray(lo, float); hi = np.asarray(hi, float)
    cons = [rc.Plane((1, 0, 0), hi[0]), rc.Plane((-1, 0, 0), -lo[0]), rc.Plane((0, 1, 0), hi[1]),
            rc.Plane((0, -1, 0), -lo[1]), rc.Plane((0, 0, 1), hi[2]), rc.Plane((0, 0, -1), -lo[2])]
    ch = np.broadcast_to(np.asarray(ch, float), (3,))
    c = (lo + hi) / 2; h = (hi - lo) / 2
    E = np.eye(3)
    for e, (i, j) in enumerate(((1, 2), (0, 2), (0, 1))):
        if ch[e] <= 0:
            continue
        for si in (-1.0, 1.0):
            for sj in (-1.0, 1.0):
                if edges == 'top' and ((i == 2 and si < 0) or (j == 2 and sj < 0)):
                    continue
                n = si * E[i] + sj * E[j]; n = n / np.linalg.norm(n)
                cons.append(rc.Plane(n, n @ c + (h[i] + h[j] - min(ch[e], h[i] * 1.6, h[j] * 1.6)) / np.sqrt(2.0)))
    return cons, c, h


def vb(x0, x1, y0, y1, z0, z1, comp, ch=0.0, name='', edges='all', inset=0.0):
    """a box over voxels x0..x1, y0..y1, z0..z1 (inclusive indices), in the body frame; inset shrinks it."""
    lo = np.array([x0 - CX + inset, CY - (y1 + 1) + inset, z0 + inset])
    hi = np.array([x1 + 1 - CX - inset, CY - y0 - inset, z1 + 1 - inset])
    cons, c, h = _box_cons(lo, hi, ch, edges)
    return rc.Part(cons, comp, name, sphere=(c, float(np.linalg.norm(h)) + 1e-3))


def vbz(x0, x1, y0, y1, zlo, zhi, comp, ch=0.0, name=''):
    """a box over voxels x0..x1, y0..y1 from height zlo to zhi (floats)."""
    lo = np.array([x0 - CX, CY - (y1 + 1), zlo]); hi = np.array([x1 + 1 - CX, CY - y0, zhi])
    cons, c, h = _box_cons(lo, hi, ch, 'top')
    return rc.Part(cons, comp, name, sphere=(c, float(np.linalg.norm(h)) + 1e-3))


def prism_xz(pts, y0, y1, comp, name='', ch=0.0):
    """a convex polygon in (x, z) voxel coordinates, extruded over voxels y0..y1; ch chamfers its long edges
    against the two y faces."""
    P = np.array([(x - CX, z) for x, z in pts], float)
    cen = P.mean(0)
    v0, v1 = CY - (y1 + 1), CY - y0
    cons = [rc.Plane((0, 1, 0), v1), rc.Plane((0, -1, 0), -v0)]
    for k in range(len(P)):
        a, b = P[k], P[(k + 1) % len(P)]
        d = b - a
        n = np.array([d[1], -d[0]]); n = n / np.linalg.norm(n)
        if n @ (cen - a) > 0:
            n = -n
        cons.append(rc.Plane((n[0], 0, n[1]), n @ a))
        if ch > 0:
            for s in (1.0, -1.0):
                m = np.array([n[0], s, n[1]]); m = m / np.linalg.norm(m)
                vv = v1 if s > 0 else -v0
                cons.append(rc.Plane(m, (n @ a + vv - ch) / np.sqrt(2.0)))
    c = np.array([cen[0], (v0 + v1) / 2, cen[1]])
    r = float(np.max(np.linalg.norm(P - cen, axis=1)))
    return rc.Part(cons, comp, name, sphere=(c, float(np.hypot(r, (v1 - v0) / 2)) + 1e-3))


def mirror_y(y):
    return 30 - y


# ---------------------------------------------------------------------------------------------- tracks
UNITS = (dict(x0=1, x1=18, rear=(1, 2), belt=(2, 19, 3, 5, 17), skirt=((1, 3), (5, 8), (11, 19)),
              bits=((3, 5), (8, 11), (17, 19)), window=(6, 16), wbit=(8, 12)),
         dict(x0=22, x1=36, rear=(22, 22), belt=(22, 37, 23, 25, 35), skirt=((22, 30), (35, 37)),
              bits=((23, 24), (30, 35)), window=(26, 34), wbit=(29, 32)))
LEFT_SKIRT = (((1, 3), (5, 8), (11, 19)), ((22, 22), (24, 30), (35, 37)))
LEFT_BITS = (((3, 5), (8, 11), (17, 19)), ((22, 24), (30, 35)))


def track_unit(U, side, k):
    """one track unit; side 'r' (y 0-5) or 'l' (y 25-30, mirrored)."""
    Y = (lambda y: y) if side == 'r' else mirror_y

    def yr(a, b):
        a, b = Y(a), Y(b)
        return min(a, b), max(a, b)
    out = []
    x0, x1 = U['x0'], U['x1']
    # the cover: a plate at z 5 over y 0-5
    out.append(vb(x0, x1, *yr(0, 5), 5, 5, COVER, ch=(0.3, 0.3, 0.3), name='cover'))
    # the front lip: x1..x1+1 at z 4 (y 1-5), x1+1 at z 3 (y 0-5)
    out.append(vb(x1, x1 + 1, *yr(1 if k == 0 else 0, 5), 4, 4, COVER, ch=(0.2, 0.2, 0.2), name='cover'))
    out.append(vb(x1 + 1, x1 + 1, *yr(0, 5), 3, 3, COVER, ch=(0.2, 0.2, 0.2), name='cover'))
    # the rear lip at z 4
    out.append(vb(U['rear'][0], U['rear'][1], *yr(1, 5), 4, 4, COVER, ch=(0.2, 0.2, 0.2), name='cover'))
    # the skirts at z 4: the outer one a voxel in from the outer face, with gaps; the inner one along y 5
    skirt = U['skirt'] if side == 'r' else LEFT_SKIRT[k]
    for a, b in skirt:
        out.append(vb(a, b, *yr(1, 1), 4, 4, COVER, ch=(0.18, 0.18, 0.18), name='cover'))
    out.append(vb(x0, x1 + 1, *yr(5, 5), 4, 4, COVER, ch=0.15, name='cover'))
    # the belt: a loop z 0-3 with sloped ends, across y 0-4
    xa, xb, xr1, xr0, xf0 = U['belt']
    pts = [(xa, 2.0), (xa, 4.0), (xb, 4.0), (xb, 2.0), (xf0, 0.0), (xr0, 0.0), (xr1, 1.0)]
    if side == 'r':
        out.append(prism_xz(pts, 0, 4, TRACK, 'track', ch=0.3))
    else:
        # the left belt: its loop over y 26-29, and an outer layer at y 30 recessed a voxel between its ends at z 1-2
        # (the ends, the top run, the bottom run and a bit over the middle wheel stand out)
        out.append(prism_xz(pts, 26, 29, TRACK, 'track', ch=0.3))
        wa, wb = U['window']
        out.append(vb(xa, xb - 1, 30, 30, 3, 3, TRACK, ch=(0.25, 0.25, 0.25), name='track'))
        out.append(vb(xr0, xf0 - 1, 30, 30, 0, 0, TRACK, ch=(0.25, 0.25, 0.25), name='track'))
        out.append(prism_xz([(xa, 2.0), (xa, 3.0), (wa, 3.0), (wa, 0.0), (xr0, 0.0), (xr1, 1.0)], 30, 30, TRACK,
                            'track', ch=0.25))
        out.append(prism_xz([(wb, 3.0), (xb, 3.0), (xb, 2.0), (xf0, 0.0), (wb, 0.0)], 30, 30, TRACK, 'track', ch=0.25))
        out.append(vb(U['wbit'][0], U['wbit'][1], 30, 30, 2, 2, TBIT, ch=(0.25, 0.25, 0.3), name='tbit'))
    # dark bits of the track standing proud of the skirt at z 4, on the outer face
    bits = U['bits'] if side == 'r' else LEFT_BITS[k]
    for a, b in bits:
        out.append(vb(a, b, *yr(0, 0), 4, 4, TBIT, ch=(0.25, 0.25, 0.3), name='tbit'))
    return out


def parts():
    P = []
    # ------------------------------------------------------------------------------------------ tracks
    for k, U in enumerate(UNITS):
        P += track_unit(U, 'r', k)
        P += track_unit(U, 'l', k)
    # ------------------------------------------------------------------------------------------ hull
    P.append(vb(3, 35, 6, 24, 1, 1, UNDER, name='under'))
    P.append(vb(1, 39, 5, 25, 2, 3, HULL, ch=(0.25, 0.25, 0.25), name='hull'))
    # the hull between and beyond the track units at y 5 / 25, z 4-5
    for y in (5, 25):
        P.append(vb(19, 21, y, y, 4, 5, HULL, ch=0.15, name='hull'))
    P.append(vb(38, 39, 5, 5, 4, 5, HULL, ch=0.15, name='hull'))
    P.append(vb(37, 37, 5, 5, 5, 5, HULL, ch=0.15, name='hull'))
    P.append(vb(38, 39, 25, 25, 4, 4, HULL, ch=0.15, name='hull'))
    # bumpers: back (x 0 z 1-2, x 1 z 1; y 6-14 and 16-24), front (x 39-41 z 1, x 40-41 z 2; y 6-14)
    for ya, yb in ((6, 14), (16, 24)):
        P.append(vb(0, 0, ya, yb, 1, 2, BUMPER, ch=0.25, name='bumper'))
        P.append(vb(1, 1, ya, yb, 1, 1, BUMPER, ch=0.2, name='bumper'))
    P.append(vb(39, 41, 6, 14, 1, 1, BUMPER, ch=0.25, name='bumper'))
    P.append(vb(40, 41, 6, 14, 2, 2, BUMPER, ch=0.25, name='bumper'))
    # ------------------------------------------------------------------------------------------ right deck
    P.append(vb(1, 39, 6, 13, 4, 5, DECK, ch=(0.25, 0.25, 0.25), name='deck'))
    P.append(vb(1, 2, 6, 13, 6, 6, RIM, ch=(0.25, 0.25, 0.25), name='rim'))
    # the rail along the outer edge: y 5 at z 6 (x 1-39) and z 7 (a notch at x 6-7 and at 34), a voxel wider at
    # z 7 over x 14-19 and at x 28
    P.append(vb(1, 39, 5, 5, 6, 6, RAIL, ch=(0.22, 0.22, 0.22), name='rail_r'))
    for a, b in ((2, 5), (8, 33), (35, 38)):
        P.append(vb(a, b, 5, 5, 7, 7, RAIL, ch=(0.22, 0.22, 0.22), name='rail_r'))
    P.append(vb(14, 19, 6, 6, 7, 7, RAIL, ch=(0.2, 0.2, 0.2), name='rail_r'))
    P.append(vb(28, 28, 6, 6, 7, 7, RAIL, ch=(0.2, 0.2, 0.2), name='rail_r'))
    # the spine along the inner edge (y 14): z 4-6 x 1-39, z 7 x 2-38
    P.append(vb(1, 39, 14, 14, 4, 6, SPINE, ch=(0.22, 0.22, 0.22), name='spine'))
    P.append(vb(2, 38, 14, 14, 7, 7, SPINE, ch=(0.22, 0.22, 0.22), name='spine'))
    # the rear block: top z 9 (x 3-13, y 6-14, its sides from z 8), the outer wall down to z 7 (x 2-19 along y 6,
    # the rail's extra width carrying on), the back stepped (x 2-3 at z 7), open under its front (z 6-7)
    P.append(vb(3, 13, 6, 14, 8, 9, BLOCK, ch=(0.35, 0.35, 0.35), name='block'))
    P.append(vb(2, 13, 6, 6, 7, 7, BLOCK, ch=(0.22, 0.22, 0.22), name='block'))
    P.append(vb(2, 3, 6, 13, 7, 7, BLOCK, ch=(0.25, 0.25, 0.25), name='block'))
    P.append(vb(6, 6, 6, 7, 6, 6, POST, ch=0.15, name='post'))
    P.append(vb(8, 8, 6, 7, 6, 6, POST, ch=0.15, name='post'))
    P.append(vb(5, 12, 8, 13, 10, 10, PANEL, ch=(0.3, 0.3, 0.3), name='panel', edges='top'))
    # the house-colour panel block and strip, bridging rail and spine at z 7-8 with a voxel's gap under them
    P.append(vb(20, 27, 6, 13, 7, 8, PANEL, ch=(0.3, 0.3, 0.3), name='panel'))
    P.append(vb(29, 30, 6, 13, 7, 8, PANEL, ch=(0.25, 0.25, 0.25), name='panel'))
    # the cab: x 31-37 to z 9 (y 6-14), its front stepped: x 38 at z 6-8 (y 6-14), x 39 at z 3-6 (y 5-14)
    P.append(vb(31, 37, 6, 14, 6, 9, CAB, ch=(0.4, 0.4, 0.4), name='cab'))
    P.append(vb(38, 38, 6, 14, 6, 8, CAB, ch=(0.3, 0.3, 0.3), name='cabfront'))
    P.append(vb(39, 39, 5, 14, 3, 6, CAB, ch=(0.3, 0.3, 0.3), name='cabfront'))
    # ------------------------------------------------------------------------------------------ channel and crane
    P.append(vb(1, 39, 15, 17, 4, 4, DECK, ch=0.0, name='channel'))
    # the pedestal: walls x 6-15 z 7-10 (its right side along y 14 from z 8), tapering at its foot
    P.append(vb(6, 15, 15, 17, 7, 10, PLATE, ch=(0.25, 0.25, 0.25), name='plate'))
    P.append(vb(3, 15, 14, 14, 8, 9, PLATE, ch=(0.22, 0.22, 0.22), name='plate'))
    P.append(vb(6, 15, 14, 14, 10, 10, PLATE, ch=(0.22, 0.22, 0.22), name='plate'))
    P.append(vb(7, 14, 15, 17, 6, 6, PLATE, ch=(0.2, 0.2, 0.2), name='plate'))
    P.append(vb(8, 13, 15, 17, 5, 5, PLATE, ch=(0.2, 0.2, 0.2), name='plate'))
    # its saddle (z 11) and the dark band along the saddle's right side (y 14, x 5-17)
    P.append(vb(6, 15, 15, 17, 11, 11, SADDLE, ch=(0.25, 0.25, 0.25), name='saddle'))
    P.append(vb(5, 17, 14, 14, 11, 11, BAND, ch=(0.25, 0.25, 0.25), name='band'))
    for a, b in ((7, 8), (13, 13), (16, 16)):
        P.append(vb(a, b, 18, 18, 11, 11, BAND, ch=(0.22, 0.22, 0.22), name='band'))
    # the boom (z 12-14)
    # (the long edges rounded; where two lengths meet at the same section they meet flush)
    P.append(vb(4, 4, 15, 17, 12, 13, BOOM_G, ch=(0.35, 0.3, 0.3), name='boom'))
    P.append(vb(5, 14, 14, 18, 12, 14, BOOM_D, ch=(0.6, 0.45, 0.45), name='boom'))
    P.append(vb(15, 27, 14, 17, 12, 14, BOOM_W, ch=(0.7, 0.0, 0.0), name='boom'))
    P.append(vb(15, 20, 18, 18, 12, 13, BOOM_G, ch=(0.35, 0.3, 0.3), name='boom'))
    P.append(vb(28, 29, 14, 15, 12, 13, BOOM_W, ch=(0.35, 0.0, 0.0), name='boom'))
    P.append(vb(28, 29, 17, 17, 12, 13, BOOM_W, ch=(0.3, 0.0, 0.0), name='boom'))
    P.append(vb(30, 37, 15, 17, 12, 13, BOOM_W, ch=(0.5, 0.0, 0.4), name='boom'))
    P.append(vb(33, 36, 15, 17, 11, 11, BOOM_T, ch=(0.3, 0.3, 0.3), name='boom'))
    # the cradle under the boom's front: z 5 from x 26, z 6 from x 28, z 7 from x 30, to x 40
    P.append(prism_xz([(26, 5.0), (26, 6.0), (30, 8.0), (41, 8.0), (41, 5.0)], 15, 17, RAIL, 'cradle', ch=0.25))
    # ------------------------------------------------------------------------------------------ left deck
    P.append(vb(1, 29, 18, 24, 4, 5, RECESS, ch=(0.25, 0.25, 0.25), name='leftdeck'))
    P.append(vb(1, 29, 18, 18, 6, 6, RECESS, ch=(0.2, 0.2, 0.2), name='leftdeck'))
    P.append(vb(1, 29, 21, 24, 6, 6, RECESS, ch=(0.2, 0.2, 0.2), name='leftdeck'))
    P.append(vb(2, 29, 19, 20, 6, 6, RECESS, ch=(0.2, 0.2, 0.2), name='leftdeck'))
    # the shelf (z 7): its inner edge (y 18), five crates (y 19-23) with dark dividers between them a little lower
    P.append(vb(2, 28, 18, 18, 7, 7, SHELF, ch=(0.22, 0.22, 0.22), name='shelf', edges='top'))
    for k, (a, b) in enumerate(CRATES):
        P.append(vb(a, b, 19, 20, 7, 7, CRATE, ch=(0.25, 0.25, 0.25), name='crate', edges='top'))
        P.append(vb(a if k else 2, b, 21, 23, 7, 7, CRATE, ch=(0.25, 0.25, 0.25), name='crate', edges='top'))
    for a, b in DIVIDERS:
        P.append(vbz(a, b, 19, 23, 7.0, 7.72, SHELF, ch=(0.15, 0.15, 0.15), name='divider'))
    for a, b in ((1, 1), (4, 6), (8, 9), (12, 17), (19, 26), (29, 29)):
        P.append(vb(a, b, 25, 25, 6, 6, RAIL, ch=(0.2, 0.2, 0.2), name='rail_l'))
    # the front-left block: z 4-6 over x 30-39 (y 18-24), the top at z 7 over x 32-37 (y 19-23)
    P.append(vb(30, 40, 18, 24, 4, 5, RECESS, ch=(0.22, 0.22, 0.22), name='fl_base'))
    P.append(vb(31, 35, 18, 18, 6, 6, BLOCK, ch=(0.22, 0.22, 0.22), name='fl_block'))
    P.append(vb(39, 39, 18, 18, 6, 6, BLOCK, ch=(0.2, 0.2, 0.2), name='fl_block'))
    P.append(vb(31, 39, 19, 19, 6, 6, BLOCK, ch=(0.22, 0.22, 0.22), name='fl_block'))
    P.append(vb(31, 34, 20, 22, 6, 6, BLOCK, ch=(0.22, 0.22, 0.22), name='fl_block'))
    P.append(vb(31, 38, 23, 23, 6, 6, BLOCK, ch=(0.22, 0.22, 0.22), name='fl_block'))
    P.append(vb(31, 31, 24, 24, 6, 6, BLOCK, ch=(0.2, 0.2, 0.2), name='fl_block'))
    P.append(vb(35, 39, 24, 24, 6, 6, BLOCK, ch=(0.22, 0.22, 0.22), name='fl_block'))
    P.append(vb(32, 37, 19, 23, 7, 7, BLOCK, ch=(0.3, 0.3, 0.3), name='fl_top', edges='top'))
    # the hitch: the coupling (dark, x 35-41 at z 6, the ring x 36-43 at z 5), the plate (z 4, x 37-44), the
    # orange frame (z 2-3) out to x 44
    P.append(vb(35, 41, 20, 22, 6, 6, EYE, ch=(0.25, 0.25, 0.25), name='coupling'))
    P.append(vb(36, 43, 20, 22, 5, 5, EYE, ch=(0.3, 0.3, 0.3), name='ring'))
    P.append(vb(37, 44, 20, 23, 4, 4, HITCH, ch=(0.25, 0.25, 0.25), name='hitch'))
    P.append(vb(44, 44, 19, 19, 4, 4, HITCH, ch=0.2, name='hitch'))
    P.append(vb(40, 43, 19, 23, 2, 2, HITCH, ch=(0.25, 0.25, 0.25), name='hitch'))
    P.append(vb(40, 44, 19, 19, 3, 3, HITCH, ch=(0.25, 0.25, 0.25), name='hitch'))
    P.append(vb(40, 44, 23, 23, 3, 3, HITCH, ch=(0.25, 0.25, 0.25), name='hitch'))
    P.append(vb(44, 44, 19, 23, 3, 3, HITCH, ch=(0.25, 0.25, 0.25), name='hitch'))
    return P
