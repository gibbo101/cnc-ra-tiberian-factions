"""
TS GDI Component Tower (GACTWR) rebuilt as a heightfield, shared by the TS-view check and the RA render.

Ground grid in HD px of the tower's own cell (0..128, centre 64,64) plus margins. Heights in HD units at
TS proportions (1 cell of height = 128); the RA render scales them with RA_SCALE.

Parts (from the TS frames and the build-up):
  pad        octagonal concrete pad filling the cell, anchor sockets round the rim, a socket in the middle
  core       octagonal column in the middle (with a door and a light on the south-east face)
  ribs       eight curved buttress ribs flaring from under the top down to the pad (the khaki "legs")
  skirt      a low khaki shell between the ribs
  top        a round blue-grey plate with four bolt holes (N/E/S/W) and the green house-colour ring
  connectors a GDI wall stub on each side (N/E/S/W) finishing with the other half of the ochre collar
"""
import numpy as np
from scipy import ndimage
import walls2 as W

PAD, CORE, RIB, SKIRT, TOP, RING, CONN, COLLAR, STRUT = 1, 2, 3, 4, 5, 6, 7, 8, 9

T = dict(
    pad_r=58.0, pad_h=4.0,               # pad circumradius (octagon), thickness
    body_a=40.0, body_z=74.0,            # square body, half-size and roof height (TS: 0.31 / 0.58 cells)
    chamfer=18.0,                        # corners cut back: a dark recess (a door on the south-east one)
    top_z=82.0,                          # top plate surface (TS: ~0.64 cells)
    top_r=37.0, ring_w=6.0, top_t=7.0,   # plate radius incl. ring, ring width, plate thickness
    hole_r=2.4, hole_at=18.7, hole_d=3.0,
    rib_w=4.6, rib_top_z=78.0, rib_foot=(13.0, 61.0),   # corner-to-connector braces
    conn_from=30.0,                      # connector stubs start inside the body and run to the cell edge
)


def grid(x0, x1, y0, y1, ss):
    xs = x0 + (np.arange(int((x1 - x0) * ss)) + 0.5) / ss
    ys = y0 + (np.arange(int((y1 - y0) * ss)) + 0.5) / ss
    return np.meshgrid(xs, ys)


def octagon_r(dx, dy):
    """'radius' of an octagon with flat faces on the axes and diagonals (inradius metric)."""
    a = np.maximum(np.abs(dx), np.abs(dy))
    b = (np.abs(dx) + np.abs(dy)) / np.sqrt(2)
    return np.maximum(a, b)


def scaled(t, zs):
    """TS-proportion heights -> RA heights (zs = RA units per TS unit of height)."""
    q = dict(t)
    for k in ('body_z', 'top_z', 'top_t', 'rib_top_z'):
        q[k] = t[k] * zs
    return q


def build(X, Y, t=T, stage='full', wall=W.P, conns='NESW'):
    """stage: 'full' | 'no_ring' | 'pad' | 'frame' (for the build-up); returns H, C, slab."""
    dx, dy = X - 64.0, Y - 64.0
    r = np.hypot(dx, dy)
    ang = np.arctan2(dy, dx)
    H = np.zeros_like(X); C = np.zeros(X.shape, np.int8)

    def put(h, comp):
        nonlocal H, C
        win = h > H + 1e-6
        H = np.where(win, h, H); C = np.where(win, comp, C)

    oct_ = octagon_r(dx, dy)
    pad_in = t['pad_r'] * np.cos(np.pi / 8)
    put(np.where(oct_ <= pad_in, t['pad_h'], 0.0), PAD)
    none = dict(top=np.full_like(X, -1.0), lo=0.0, comp=np.zeros(X.shape, np.int8))
    if stage == 'pad':
        return H, C, none
    # connectors: GDI wall stubs on the axes, profile from walls2, collar half at the cell edge
    P = wall
    for d in conns:
        if d in 'EW':
            u = dx if d == 'E' else -dx; v = dy
        else:
            u = dy if d == 'S' else -dy; v = dx
        a = np.abs(v)
        inside = (u >= t['conn_from']) & (u <= 64.0 + 0.001)
        arm = W.trap(a, P['top'], P['base'], P['h'])
        put(np.where(inside, arm, 0.0), CONN)
        o = P['collar_out']
        band = inside & (u >= 64.0 - P['collar_half'])
        col = W.trap(a, P['top'] + o, P['base'] + o, P['h'] + o)
        put(np.where(band, col, 0.0), COLLAR)
    if stage == 'frame':
        return H, C, none
    # square body with cut corners
    a, ch = t['body_a'], t['chamfer']
    ax, ay = np.abs(dx), np.abs(dy)
    body = (ax <= a) & (ay <= a) & (ax + ay <= 2 * a - ch)
    put(np.where(body, t['body_z'], 0.0), SKIRT)
    # the cut corners are a dark recess set back into the body
    recess = (ax + ay > 2 * a - ch - 4.0) & (ax + ay <= 2 * a - ch) & (np.abs(ax - ay) < 0.62 * ch)
    H = np.where(recess & (C == SKIRT), 0.0, H); C = np.where(recess & (C == SKIRT), 0, C)
    put(np.where(recess, t['body_z'] - 4, 0.0), CORE)
    # braces: from the top of each corner, splaying down onto the two neighbouring connectors
    fx, fy = t['rib_foot']
    for sx in (-1, 1):
        for sy in (-1, 1):
            for (cx, cy, px, py) in ((sx * (a - ch / 2), sy * a, sx * fx, sy * fy),
                                     (sx * a, sy * (a - ch / 2), sx * fy, sy * fx)):
                L = np.hypot(px - cx, py - cy)
                ux, uy = (px - cx) / L, (py - cy) / L
                along = (dx - cx) * ux + (dy - cy) * uy
                across = -(dx - cx) * uy + (dy - cy) * ux
                f = np.clip(along / L, 0, 1)
                z = t['rib_top_z'] * (1 - f ** 1.35)
                on = (np.abs(across) <= t['rib_w']) & (along >= -2) & (along <= L)
                put(np.where(on, z, 0.0), RIB)
    # top plate + ring: a separate slab (it overhangs the ribs), returned apart from the heightfield
    plate = np.where(r <= t['top_r'], t['top_z'], -1.0)
    ring = r > t['top_r'] - t['ring_w']
    holes = np.zeros_like(r, bool)
    for hx, hy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
        holes |= np.hypot(dx - hx * t['hole_at'], dy - hy * t['hole_at']) <= t['hole_r']
    plate = np.where(holes & (r <= t['top_r']), t['top_z'] - t['hole_d'], plate)
    Cs = np.where(r <= t['top_r'], TOP, 0).astype(np.int8)
    if stage == 'full':
        plate = np.where(ring & (r <= t['top_r']), t['top_z'] + 1.2, plate)
        Cs = np.where(ring & (r <= t['top_r']), RING, Cs).astype(np.int8)
    slab = dict(top=plate, lo=t['top_z'] - t['top_t'], comp=Cs)
    return H, C, slab
