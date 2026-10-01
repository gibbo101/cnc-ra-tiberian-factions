"""
TS GDI Tech Center (GATECH, TSTECH in the mod) as a model for hd.py.

Built in its own frame ("local": X east, Y south as TS draws it, units 1 cell = 128, Z up, origin at the centre of
TS's 3x2 foundation, X -192..192, Y -128..128), read from GTTECH / GTTECHMK in TS's own camera:
  wedge   a triangle in plan (GTTECHMK's first frames draw it): TS's is a right triangle, the long south face
          (Y 101), the east face (X 159) and the back face running from the north-east corner to the narrow west
          end (a short west face there). Three terraces of louvred bands step in up its sides (sand, brown, grey
          edges); a flat sandy roof inside a grey parapet.
  east    the east face (the wide end): the terraces' louvres along its southern part, a recessed grille of
          vertical struts in the middle, a plain sloping batter to the north-east corner.
  dome    a big geodesic dome on the roof: green (house colour) triangular panels in brown struts.
  fins    two green (house colour) fins straddling the narrow end: each solid and symmetric, straight sides
          rising from the ground on either side of the building to a flat top (TS's camera sees them nearly
          edge-on, as tall narrow shapes).

Layouts (scene(..., layout=)), the same building placed for each view:
  'ts'   TS's own (the TS-angle view): the right triangle on the 3x2, the dome and the fins where TS has them.
  'rot'  RA's grid, TS's building turned a quarter, long and thin on a 2x3 (world X -128..128, Y -192..192): the
         narrow end to the north, the east face to the south facing the camera; the dome and the
         fins where TS has them on the building.
  'ts3'  RA's grid, TS's way round on the 3x2: as 'ts'.
"""
import numpy as np
import hd

(SLAB, BAND, LOUVRE, ROOF, PARAPET, FRAME, DOME, STRUT, FIN, FINEDGE, DOOR, BASE) = range(1, 13)
HOUSE = {DOME, FIN}

BUILD_KEYS = ('block', 'roof', 'east', 'fin1', 'fin2', 'dome', 'panels')        # fin1/fin2: the arches
DONE = {k: 1.0 for k in BUILD_KEYS}

P = dict(
    terraces=((0.0, 15.0, 0.0), (15.0, 30.0, 9.5), (30.0, 45.0, 19.0)),   # z0, z1, inset
    roof_z=45.0, parapet=(3.0, 3.0),                 # height, width
    east=dict(strut=9.0, z=36.0, depth=(5.0, 12.0)),     # the grille: strut spacing, height, depth in the face
    # the two fins (house colour): each solid - no gap under it - and symmetric, TS's shape: straight sides rising
    # from the ground on either side of the building to a flat top. Span between its feet, the flat top's length,
    # height, thickness, rib spacing
    arch=dict(span=140.0, top=66.0, h=131.0, w=14.0, t=12.0, p=2.2, rib=11.0),
)

TS_POLY = ((-159.0, 101.0), (159.0, 101.0), (159.0, -128.0), (-159.0, 77.0))
LAYOUTS = {
    'ts': dict(rot=False, ox=0.0, oy=0.0, poly=TS_POLY, pivot=47.0,
               east=dict(grille=(-81.0, -6.0), slope_y=-81.0),
               dome=dict(c=(20.5, -51.5), r=70.0, h=10.0),
               # the arches cross the wedge square to its back face, near its narrow end (TS's camera sees them
               # nearly edge-on: the tall narrow shapes); centre, the span's direction, the side each tilts to
               arches=(((-68.2, 54.4), (0.584, 0.811), (0.811, -0.584)),
                       ((-20.2, 59.7), (0.584, 0.811), (0.811, -0.584)))),
    # TS's own building, turned a quarter (its narrow west end to the north, its east face to the south, facing
    # the camera): world X = ox - local Y, world Y = local X + oy; everything where TS has it
    'rot': dict(rot=True, ox=-4.5, oy=0.0, poly=TS_POLY, pivot=47.0,
                east=dict(grille=(-81.0, -6.0), slope_y=-81.0),
                dome=dict(c=(20.5, -51.5), r=70.0, h=10.0),
                arches=(((-68.2, 54.4), (0.584, 0.811), (0.811, -0.584)),
                        ((-20.2, 59.7), (0.584, 0.811), (0.811, -0.584)))),
    'ts3': dict(rot=False, ox=0.0, oy=0.0, poly=TS_POLY, pivot=47.0,
                east=dict(grille=(-81.0, -6.0), slope_y=-81.0),
                dome=dict(c=(20.5, -51.5), r=70.0, h=10.0),
                arches=(((-68.2, 54.4), (0.584, 0.811), (0.811, -0.584)),
                        ((-20.2, 59.7), (0.584, 0.811), (0.811, -0.584)))),
}


def to_local(X, Y, layout='ts'):
    L = LAYOUTS[layout]
    if L['rot']:
        return Y - L['oy'], L['ox'] - X
    return X, Y


def to_world(x, y, layout='ts'):
    L = LAYOUTS[layout]
    if L['rot']:
        return L['ox'] - y, x + L['oy']
    return x, y


def edges(poly):
    """the polygon's edges as inward unit normals and offsets: inside where nx*x + ny*y - c >= 0."""
    pts = np.array(poly)
    cen = pts.mean(axis=0)
    out = []
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        d = b - a
        n = np.array([-d[1], d[0]]) / np.hypot(*d)
        if np.dot(n, cen - a) < 0:
            n = -n
        out.append((n[0], n[1], float(np.dot(n, a))))
    return out


def inset_dist(x, y, poly):
    """how far inside the polygon (negative outside)."""
    return np.min([nx * x + ny * y - c for (nx, ny, c) in edges(poly)], axis=0)


def dome_geo(L, p=P):
    d = L['dome']
    zc = p['roof_z'] + d['h']
    rb = np.sqrt(d['r'] ** 2 - d['h'] ** 2)
    return d['c'], d['r'], zc, rb


def _icosa():
    """an icosahedron (unit circumradius) turned so one vertex points straight up: its vertices and faces."""
    ph = (1 + 5 ** 0.5) / 2
    V = []
    for a in (-1, 1):
        for b in (-ph, ph):
            V += [(0, a, b), (a, b, 0), (b, 0, a)]
    V = np.array(V, float)
    V /= np.linalg.norm(V[0])
    top = V[np.argmax(V[:, 2] + 0.01 * V[:, 1])]
    zc = np.array([0, 0, 1.0])
    ax = np.cross(top, zc); s = np.linalg.norm(ax); c = np.dot(top, zc)
    if s > 1e-9:
        ax /= s
        K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
        Rm = np.eye(3) + np.sin(np.arctan2(s, c)) * K + (1 - c) * K @ K
        V = V @ Rm.T
    e = np.min([np.linalg.norm(V[i] - V[j]) for i in range(12) for j in range(i + 1, 12)])
    F = [(i, j, k) for i in range(12) for j in range(i + 1, 12) for k in range(j + 1, 12)
         if abs(np.linalg.norm(V[i] - V[j]) - e) < 1e-6 and abs(np.linalg.norm(V[j] - V[k]) - e) < 1e-6
         and abs(np.linalg.norm(V[i] - V[k]) - e) < 1e-6]
    return V, np.array(F)


ICO_V, ICO_F = _icosa()
ICO_C = ICO_V[ICO_F].mean(axis=1)
ICO_C /= np.linalg.norm(ICO_C, axis=1)[:, None]


def geodesic_dir(dx, dy, dz, freq=2, w=0.05):
    """a geodesic dome's struts on the unit sphere (an icosahedron, each face cut into freq^2 triangles, a hub at
    the top): returns the strut mask and a panel id for directions (dx, dy, dz) from the sphere's centre."""
    d = np.stack([dx, dy, dz], -1).astype(np.float64)
    d /= np.linalg.norm(d, axis=-1, keepdims=True) + 1e-12
    fi = np.argmax(d @ ICO_C.T, axis=-1)
    v0, v1, v2 = (ICO_V[ICO_F[fi, k]] for k in range(3))
    n = np.cross(v1 - v0, v2 - v0)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    hf = np.sum(n * v0, axis=-1)
    n = n * np.sign(hf)[..., None]                    # outward
    hf = np.abs(hf)
    t = hf / np.sum(n * d, axis=-1)
    p = d * t[..., None]
    e0, e1, e2 = v1 - v0, v2 - v0, p - v0
    d00 = np.sum(e0 * e0, -1); d01 = np.sum(e0 * e1, -1); d11 = np.sum(e1 * e1, -1)
    d20 = np.sum(e2 * e0, -1); d21 = np.sum(e2 * e1, -1)
    den = d00 * d11 - d01 * d01
    lb = (d11 * d20 - d01 * d21) / den
    lc = (d00 * d21 - d01 * d20) / den
    la = 1 - lb - lc
    alt = np.sqrt(d00) * np.sqrt(3) / 2
    s = np.zeros(la.shape, bool)
    for l in (la, lb, lc):
        q = l * freq
        s |= np.abs(q - np.round(q)) * alt / freq < w * hf / 2
    ia, ib = np.floor(lb * freq), np.floor(lc * freq)
    up = (lb * freq - ia) + (lc * freq - ib) > 1
    pid = fi * 1000 + ia * 37 + ib * 3 + up
    return s, pid.astype(np.float64)


def dome_lattice(x, y, z, L, p=P):
    """the dome's struts and panel ids at points (x, y, z) on it (local coordinates), with azimuth and elevation."""
    (cx, cy), R, zc, rb = dome_geo(L, p)
    dx, dy, dz = x - cx, y - cy, z - zc
    s, pid = geodesic_dir(dx, dy, dz)
    az = np.arctan2(dy, dx)
    el = np.arctan2(dz, np.hypot(dx, dy))
    return s, pid, az, el


def panel_order(pid):
    """0..1 per panel: the order the panels go in (build-up)."""
    return np.abs(np.sin(pid * 7.31 + 1.7) * 9871.13) % 1.0


def arch_dims(L, p=P):
    a = dict(p['arch'])
    if 'arch_span' in L:
        a['span'] = L['arch_span']
    return a


def arch_coords(x, y, cxy, d):
    """along the arch's span (0 at its apex) and through it (along its tilt side)."""
    dx, dy = x - cxy[0], y - cxy[1]
    return dx * d[0] + dy * d[1], dx * (-d[1]) + dy * d[0]


def fin_top(xx, a):
    """the fin's outline, TS's: straight sides sloping up from its feet to a flat top; its height xx out from
    the middle."""
    S, T, Hh = a['span'], a['top'], a['h']
    return np.where(xx <= T / 2, Hh, Hh * np.clip((S / 2 - xx) / ((S - T) / 2), 0, 1))


def scene(X, Y, p=P, prog=None, layout='ts'):
    g = dict(DONE); g.update(prog or {})
    L = LAYOUTS[layout]
    x, y = to_local(X, Y, layout)
    H = np.zeros_like(X); C = np.zeros(X.shape, np.int16)
    slabs = []

    def put(h, comp, where=None):
        nonlocal H, C
        if where is not None:
            h = np.where(where, h, 0.0)
        win = h > H + 1e-6
        H = np.where(win, h, H); C = np.where(win, comp, C)

    def slab(top, bot, comp, where, name=''):
        slabs.append(hd.Slab(np.where(where, top, -1.0), np.where(where, np.maximum(bot, 0.0), 0.0),
                             np.where(where, comp, 0).astype(np.int16), name))

    ins = inset_dist(x, y, L['poly'])
    e = dict(p['east']); e.update(L['east'])
    xe = max(px for (px, py) in L['poly'])                # the east face (the wide end)
    d_top = p['terraces'][-1][2]
    # TS's east face: the terraces' louvres along its southern part, a recessed grille in the middle, a plain
    # sloping batter to the north-east corner
    ins_e = xe - x
    ins_o = np.min([nx * x + ny * y - c for (nx, ny, c) in edges(L['poly']) if abs(nx + 1.0) > 1e-6], axis=0)
    east_face = (ins_e <= ins_o + 0.5) & (ins_e < d_top + 1.0) & (ins >= 0)
    gy0, gy1 = e['grille']
    grille = east_face & (y > gy0) & (y < gy1)
    batter = east_face & (y <= e['slope_y'])
    # ---- the wedge: three terraces stepping in, the roof inside a parapet
    if g['block'] > 0:
        ztop = p['roof_z'] * g['block']
        for (z0, z1, d) in p['terraces']:
            if z0 >= ztop:
                break
            put(np.full_like(X, min(z1, ztop)), BAND, ins >= d)
        bh = np.clip(ins_e / d_top, 0, 1) * ztop
        H = np.where(batter, np.minimum(H, bh + 0.01), H)
        C = np.where(batter & (H > 0.01), LOUVRE, C)
        # the grille's recess: the lower terraces cut back to the top one's face (dark, by the materials)
        cut = grille & (ins_e < d_top - 0.5)
        H = np.where(cut, 0.0, H)
        C = np.where(cut, 0, C)
    if g['roof'] > 0:
        ph, pw = p['parapet']
        put(np.where((ins >= d_top) & (ins < d_top + pw), p['roof_z'] + ph * g['roof'], 0.0), PARAPET)
        inner = ins >= d_top + pw
        on = inner & (H >= p['roof_z'] - 0.5)
        H = np.where(on, p['roof_z'] + 0.01, H)
        C = np.where(on & (C == BAND), ROOF, C)
    # ---- the grille: vertical struts in the recess, a rail top and bottom
    if g['east'] > 0:
        ze = e['z'] * g['east']
        dz0, dz1 = e['depth']
        fr = grille & (ins_e >= dz0) & (ins_e <= dz1)
        strut = fr & (np.abs(((y - gy0) % e['strut']) - e['strut'] / 2) > e['strut'] / 2 - 1.6)
        slab(np.full_like(X, ze), np.full_like(X, 0.0), FRAME, strut, 'frame')
        rail = fr & (np.abs(ins_e - (dz0 + dz1) / 2) < 2.0)
        slab(np.full_like(X, ze + 2.5), np.full_like(X, ze - 2.0), FRAME, rail, 'rail')
        slab(np.full_like(X, min(5.0, ze)), np.full_like(X, 0.0), FRAME, rail, 'rail0')
    # ---- the dome: geodesic, on the roof; build-up: struts first (see-through), then the panels go in
    (cx, cy), R, zc, rb = dome_geo(L, p)
    dd = np.hypot(x - cx, y - cy)
    cap = zc + np.sqrt(np.clip(R ** 2 - dd ** 2, 0, None))
    under = dd <= R
    if g['dome'] > 0:
        strut, pid, az, el = dome_lattice(x, y, cap, L, p)
        el0 = -np.arcsin(min(1.0, (zc - p['roof_z']) / R))
        grown = el <= el0 + (np.pi / 2 - el0) * g['dome'] + 1e-6
        filled = under & (panel_order(pid) < g['panels'])
        on_roof = ins >= d_top
        if g['panels'] > 0:
            put(np.where(filled & on_roof, cap, 0.0), DOME)
            # past the roof's back edge it overhangs: a shell, nothing under it
            slab(cap, np.full_like(X, p['roof_z'] - 2.0), DOME, filled & ~on_roof, 'domeover')
        # see-through struts where a panel isn't in yet (where it is, the materials draw them)
        slab(cap + 0.8, cap - 2.5, STRUT, under & strut & grown & ~filled, 'domestrut')
        ring = (dd <= rb + 2.0) & (dd >= rb - 4.0)
        put(np.where(ring & (ins >= d_top), p['roof_z'] + 3.5, 0.0), STRUT)          # its base ring
        slab(np.full_like(X, p['roof_z'] + 3.5), np.full_like(X, p['roof_z'] - 2.0), STRUT, ring & (ins < d_top), 'ringover')
    # ---- the fins: solid arch-shaped fins up one side of the building, over, down the other; build-up: each
    #      raised from lying over the roof, tipping up about the line through its feet (TS's GTTECHMK)
    a = arch_dims(L, p)
    for k, (cxy, d, e_) in enumerate(L['arches']):
        gk = g['fin1' if k == 0 else 'fin2']
        if gk <= 0:
            continue
        sa_, _ = arch_coords(x, y, cxy, d)
        n_ = (x - cxy[0]) * e_[0] + (y - cxy[1]) * e_[1]                      # through it, towards its tilt side
        xx = np.abs(sa_)
        top = fin_top(xx, a)
        if gk >= 1.0:
            m = (np.abs(n_) <= a['t'] / 2) & (xx <= a['span'] / 2) & (top > 0.5)
            slab(top, np.zeros_like(X), FIN, m, 'fin')
        else:
            ang = (1.0 - gk) * np.pi / 2 * 0.92
            sa, ca = max(np.sin(ang), 1e-3), np.cos(ang)
            za = n_ / sa                                      # the height in the fin's own plane for this column
            inside = (za >= 0) & (za <= top) & (xx <= a['span'] / 2)
            th = min(a['t'] / sa, 400.0)
            zm = za * ca
            slab(zm + th / 2, np.maximum(zm - th / 2, 0.0), FIN, inside, 'fin')
    return hd.Scene(H, C, slabs, {'panels': np.full_like(X, g['panels'], dtype=np.float32)})


FLAT = {SLAB: (150, 150, 146), BAND: (150, 128, 90), LOUVRE: (110, 96, 70), ROOF: (196, 170, 110), PARAPET: (140, 140, 146),
        FRAME: (130, 130, 136), DOME: (0, 200, 0), STRUT: (110, 70, 40), FIN: (0, 190, 0), FINEDGE: (0, 120, 0),
        DOOR: (30, 30, 34), BASE: (40, 40, 44)}
