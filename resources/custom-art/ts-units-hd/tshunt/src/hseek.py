"""
hseek.py - the Hunter-Seeker (TS [GHUNTER]) as convex parts, read off TS's GGHUNT sprite.  TS draws it from one side
only: its 8 frames differ just in the star's light and the fins' flash.  Read from frame 4 (columns and rows of TS's
73 x 73 frame; the axis on column 36; a unit up is 0.866 rows, a unit towards the camera 0.5 rows down):

  - the mast: 1 px, blue-grey (rows 8-9), with a bronze band (row 7) and a grey tip (row 6)
  - the star (rows 10-12): a blue core 3 px across, a spike either side (columns 34 and 38), its light on the centre
    pixel (36, 11) and a dark grey stub just under the light (36, 12)
  - the neck (columns 35-37, rows 14-20): bronze, with a dark collar (row 16) under its top
  - the strut (row 19): a grey bar from column 32 to 40 behind the neck, between the wings' inner edges
  - the wings (rows 16-20): thin blades, wider at the bottom and leaning in at the top (columns 27-32 and 40-45), each
    with a dark slot one pixel in from its outer edge ((30, 17)-(29, 18) and (42, 17)-(43, 18)); a red-brown mark on
    the left one's inner top corner (32, 16)
  - the shoulder (rows 21-24): 13 px across (columns 30-42) but only 3-4 rows tall, so a bar across the body, not a
    disc (a disc that wide would stand 7 rows tall); its ends rise into two rounded lobes (their tops on row 21 at
    columns 31 and 41, the row empty between them and the body)
  - the chest: TS's highlight (white (35, 23)-(36, 23), yellow (35, 22), pink round them) sits on the shoulder's
    middle where a surface faces the camera, so the body's top there is a round mass standing out in front of the bar
    (its lower edge dark: (36, 24)-(37, 24))
  - the body: 7 px across (columns 33-39) from row 25 down, a lug either side at rows 27-28 (columns 32 and 40), a blue
    strip down its front (column 36, rows 27-29), its bottom on row 34
  - fins round the bottom: one towards the camera (columns 35-37, rows 32-35: 1 px at its top and 3 below, a ridged
    wedge) and two to the sides (columns 31-33 and 39-41, rows 31-34), red-brown marks at their roots ((33, 31), its
    twin (39, 31) in shadow)

Frame: x east, y south (towards the camera), z up; units TS px; origin on the axis at the body's bottom (z 0).
"""
import numpy as np
import rc

(BODY, SHOULDER, LOBE, LUG, NECK, COLLAR, MAST, BAND, TIP, STAR, SPIKE, STUB, WING, SLOT, STRUT, FIN, STRIP,
 MARK, CHEST) = range(601, 620)
# fitting classes: 2 steel (TS's remap; painted steel in the mod), 4 bronze, 5 dark or blue, 6 red-brown
CLASS = {BODY: 4, CHEST: 4, SHOULDER: 4, LOBE: 4, LUG: 4, NECK: 4, BAND: 4, COLLAR: 5, MAST: 5, TIP: 5, STAR: 5, SPIKE: 5,
         STUB: 5, WING: 2, SLOT: 2, STRUT: 2, FIN: 2, STRIP: 5, MARK: 6}

P0 = dict(
    # the body: two half ellipsoids (top and bottom) meeting at its widest, zb; its top dbt over the shoulder bar's
    # middle (TS's row 21 is the bar's top: the body does not rise past it)
    rb=3.6, zb=6.0, dbt=0.0, hbl=6.0,
    # the chest: a ball on the body's top at the shoulder bar's height (over the bar's middle by dch), standing out in
    # front of it
    dch=0.3, rch=2.8,
    # the shoulder bar (round in section, long across) and its two lobes
    zs=13.4, sx=5.0, sb=1.6,
    lx=5.0, ldz=1.1, lr=1.5,
    # the lugs
    gx=3.6, zg=7.6, gr=1.0,
    # the neck, its top and its collar
    rn=1.5, znt=22.6, zc=21.8,
    # the mast: radius, the band's bottom and top, the tip's top
    rm=0.45, bz0=30.7, bz1=31.9, zmt=32.8,
    # the star: core radius and height, the side spikes' reach past the core and thickness, the stub's
    rst=1.5, zst=26.7, ls=1.0, ts=0.6, lsb=0.6, tsb=0.7,
    # the strut: height, half-length, radius
    stz=17.4, stl=4.5, str_=0.45,
    # the wings: anchor (inner bottom corner) out from the axis, its depth and height; the blade's lean back from
    # upright (degrees); its outline on the blade (bottom width, inner overhang, top width, lower and full height,
    # in TS px as the camera sees them); thickness; the slot's inset and span along the outer edge
    wxa=5.5, wya=0.0, wza=15.7, wa=85.0, wb=4.0, wi=2.0, wtop=3.0, wh1=2.0, wh2=5.0, wt=0.6,
    so=1.0, s0=0.12, s1=0.7,
    # the fins, three alike: root (out from the axis, height), reach out and drop, half-width and ridge height; the
    # side ones' angle from the front one
    fr=2.5, fz=4.4, fl=3.0, fd=2.6, fw=1.5, fh=1.4, fa=120.0,
    # the blue strip on the body's front: centre height, half-height
    tz=9.1, th=1.7,
    # the red-brown marks' radius
    mr=0.45)


def ellip(c, r, comp, name, clip=None):
    c = np.asarray(c, float); r = np.asarray(r, float)
    cons = [rc.Ellip(c, np.eye(3), r)] + list(clip or [])
    return rc.Part(cons, comp, name, sphere=(c, float(r.max()) + 1e-3))


def prism(poly, n, t, comp, name):
    """a flat plate: the convex polygon poly (3D points in one plane, normal n) t thick."""
    V = [np.asarray(v, float) for v in poly]
    n = np.asarray(n, float); n = n / np.linalg.norm(n)
    C = np.mean(V, 0)
    cons = [rc.Plane(n, n @ C + t / 2), rc.Plane(-n, -n @ C + t / 2)]
    for a, b in zip(V, V[1:] + V[:1]):
        m = np.cross(b - a, n); m = m / np.linalg.norm(m)
        if m @ (C - a) > 0:
            m = -m
        cons.append(rc.Plane(m, m @ a))
    R = max(np.linalg.norm(v - C) for v in V) + t
    return rc.Part(cons, comp, name, sphere=(C, R + 1e-3))


def wedge(p0, p1, w, h, comp, name, ext=0.6):
    """a ridged fin: its ridge from p0 to p1 (the top edge), a base w either side and h under the ridge (a triangle in
    section); ext runs it back past p0 (into the body)."""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    R = rc.frame_from(p1 - p0, (0, 0, 1.0))
    ex, ey, ez = R[:, 0], R[:, 1], R[:, 2]
    L = np.linalg.norm(p1 - p0)
    cons = [rc.Plane(ex, ex @ p1), rc.Plane(-ex, -ex @ p0 + ext), rc.Plane(-ez, -ez @ p0 + h)]
    for s in (-1.0, 1.0):
        m = s * h * ey + w * ez
        m = m / np.linalg.norm(m)
        cons.append(rc.Plane(m, m @ p0))
    c = (p0 + p1) / 2 - ez * h / 2
    return rc.Part(cons, comp, name, sphere=(c, float(np.hypot(L / 2 + ext, max(w, h))) + 1e-3))


def wing_frame(P, s):
    """the left (s -1) or right (s +1) wing's anchor, in-blade axes (out, up) and normal."""
    a = np.deg2rad(P['wa'])
    A = np.array([s * P['wxa'], P['wya'], P['wza']])
    ep = np.array([s, 0.0, 0.0])
    eu = np.array([0.0, -np.sin(a), np.cos(a)])
    n = np.array([0.0, np.cos(a), np.sin(a)])
    # outline heights are given as TS's camera sees them (30 degrees): up the blade they are 1 / cos(lean - 30) longer
    k = 1.0 / np.cos(np.deg2rad(P['wa'] - 30.0))
    return A, ep, eu, n, k


def wing_outline(P, s):
    A, ep, eu, n, k = wing_frame(P, s)
    pq = [(0.0, 0.0), (P['wb'], 0.0), (P['wb'], P['wh1'] * k), (P['wtop'] - P['wi'], P['wh2'] * k),
          (-P['wi'], P['wh2'] * k), (-P['wi'], P['wh1'] * k)]
    return [A + p * ep + q * eu for p, q in pq], n


def slot_points(P, s):
    """the slot's two ends: along the outer edge (from its lower corner to the top), set in by so."""
    A, ep, eu, n, k = wing_frame(P, s)
    F = np.array([P['wb'], P['wh1'] * k]); T = np.array([P['wtop'] - P['wi'], P['wh2'] * k])
    out = []
    for f in (P['s0'], P['s1']):
        p, q = F + f * (T - F)
        out.append(A + (p - P['so']) * ep + q * eu + n * (P['wt'] / 2))
    return out


def mark_points(P):
    """the red-brown marks: the left wing's inner top corner, the side fins' roots."""
    A, ep, eu, n, k = wing_frame(P, -1.0)
    w = A + (-P['wi'] + 0.5) * ep + (P['wh2'] * k - 0.5) * eu + n * (P['wt'] / 2)
    out = [w]
    for s in (-1.0, 1.0):
        e = side_dir(P, s)
        out.append(e * (body_radius(P, P['fz']) + 0.1) + np.array([0, 0, P['fz'] + 0.3]))
    return out


def side_dir(P, s):
    a = np.deg2rad(s * P['fa'])
    return np.array([np.sin(a), np.cos(a), 0.0])


def body_radius(P, z):
    """the body's radius at height z."""
    zb = P['zb']
    h = hbu(P) if z >= zb else P['hbl']
    return P['rb'] * np.sqrt(max(1 - ((z - zb) / h) ** 2, 0.0))


def hbu(P):
    return max(P['zs'] + P['dbt'] - P['zb'], 0.5)


def parts(P):
    out = []
    zb = P['zb']
    up = rc.Plane(np.array([0, 0, -1.0]), -zb)            # keeps z >= zb
    dn = rc.Plane(np.array([0, 0, 1.0]), zb)              # keeps z <= zb
    out.append(ellip((0, 0, zb), (P['rb'], P['rb'], hbu(P)), BODY, 'body', [up]))
    out.append(ellip((0, 0, zb), (P['rb'], P['rb'], P['hbl']), BODY, 'body', [dn]))
    out.append(ellip((0, 0, P['zs'] + P['dch']), (P['rch'],) * 3, CHEST, 'chest'))
    # the shoulder bar and its lobes
    out.append(ellip((0, 0, P['zs']), (P['sx'], P['sb'], P['sb']), SHOULDER, 'shoulder'))
    for s in (-1.0, 1.0):
        out.append(ellip((s * P['lx'], 0, P['zs'] + P['ldz']), (P['lr'],) * 3, LOBE, 'lobe'))
        out.append(ellip((s * P['gx'], 0, P['zg']), (P['gr'], P['gr'], P['gr']), LUG, 'lug'))
    # the neck and its collar
    out.append(rc.cylinder((0, 0, P['zs']), (0, 0, P['znt']), P['rn'], NECK, 'neck'))
    out.append(rc.cylinder((0, 0, P['zc'] - 0.5), (0, 0, P['zc'] + 0.5), P['rn'] + 0.2, COLLAR, 'collar'))
    # the mast, its band and its tip
    out.append(rc.cylinder((0, 0, P['znt'] - 0.3), (0, 0, P['bz0']), P['rm'], MAST, 'mast'))
    out.append(rc.cylinder((0, 0, P['bz0']), (0, 0, P['bz1']), P['rm'] + 0.05, BAND, 'band'))
    out.append(rc.cylinder((0, 0, P['bz1']), (0, 0, P['zmt'] - P['rm']), P['rm'], TIP, 'tip'))
    out.append(ellip((0, 0, P['zmt'] - P['rm']), (P['rm'],) * 3, TIP, 'tip'))
    # the star: core, side spikes, the stub under the light
    c = np.array([0, 0, P['zst']])
    out.append(ellip(c, (P['rst'],) * 3, STAR, 'star'))
    for s in (-1.0, 1.0):
        out.append(rc.seg_box(c, c + np.array([s, 0, 0]) * (P['rst'] + P['ls']), P['ts'], P['ts'], SPIKE,
                              up=(0, 0, 1.0), name='spike'))
    out.append(rc.seg_box(c, c + np.array([0, 1.0, 0]) * (P['rst'] + P['lsb']), P['tsb'], P['tsb'], STUB,
                          up=(0, 0, 1.0), name='stub'))
    # the strut between the wings' inner edges, through the neck
    out.append(rc.cylinder((-P['stl'], 0, P['stz']), (P['stl'], 0, P['stz']), P['str_'], STRUT, 'strut'))
    # the wings and their slots
    for s in (-1.0, 1.0):
        poly, n = wing_outline(P, s)
        out.append(prism(poly, n, P['wt'], WING, 'wing'))
        a, b = slot_points(P, s)
        R = rc.frame_from(b - a, n)
        L = np.linalg.norm(b - a)
        out.append(rc.box((a + b) / 2, R, (L / 2, 0.38, 0.06), SLOT, name='slot'))
    # the fins: the front one, then the two to the sides
    for s in (0.0, -1.0, 1.0):
        e = side_dir(P, s)
        out.append(wedge(e * P['fr'] + np.array([0, 0, P['fz']]),
                         e * (P['fr'] + P['fl']) + np.array([0, 0, P['fz'] - P['fd']]), P['fw'], P['fh'], FIN, 'fin'))
    # the blue strip down the body's front
    y = body_radius(P, P['tz']) - 0.15
    out.append(rc.box(np.array([0, y, P['tz']]), np.eye(3), (0.55, 0.3, P['th']), STRIP, name='strip'))
    # the red-brown marks
    for q in mark_points(P):
        out.append(ellip(q, (P['mr'],) * 3, MARK, 'mark'))
    return out


def star_light(P, elev=30.0):
    """the star's light: the point of the core that faces the camera (TS: the centre pixel)."""
    e = np.deg2rad(elev)
    return np.array([0, P['rst'] * np.cos(e), P['zst'] + P['rst'] * np.sin(e)])
