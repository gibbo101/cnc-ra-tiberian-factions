"""
TS GDI Component Tower rebuilt for Red Alert Remastered (HD).
Canvas 176x320; the cell is the centred 128x128 square (x 24-152, y 96-224); cell ground centre (88, 160).

Shape from ctwr/ctower.py (fitted to the TS sprites in TS's own view, ~91% silhouette overlap):
square khaki body with cut corners (dark recesses; a door with a lamp on the south-east one), eight braces
from the top of the corners down onto the wall connectors, a round blue-grey top plate with four bolt holes
(N/E/S/W) and the green house-colour ring, and a concrete pad.

Camera: a real orthographic camera 32 degrees above the ground, looking north (TS: 30 degrees, looking
north-west). The model is built at TS's proportions in physical units; depth reaches the screen x sin 32 and
heights x cos 32 (the ray-cast works on those screen-scaled heights). Lighting, ~75% shadow, materials and
outline as the GDI wall (walls2.py).

The tower stands on its own. render_coupling(side) makes the generic wall coupling for one side as an
overlay (drawn after the tower wherever any kind of wall is next to it): a sill, a steel beam and a khaki
sleeve straddling the cell edge that the wall runs into.
"""
import numpy as np
from PIL import Image
from scipy import ndimage
import walls2 as W
from walls2 import smoothstep, sample, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME, SS
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ctwr'))
import ctower as CT
from ctower import PAD, CORE, RIB, SKIRT, TOP, RING, CONN, COLLAR, STRUT
NECK, FLANGE = 10, 11

ELEV = np.deg2rad(32.0)                 # camera 32 degrees above the ground, looking north (TS: 30)
SYF, SZF = float(np.sin(ELEV)), float(np.cos(ELEV))   # ground depth and heights as they reach the screen
FZ = 1.0                                # the ray-cast works on screen-scaled ("model") heights
SH_DIR = (W.SHADOW_DIR[0] / W.FZ, W.SHADOW_DIR[1] / W.FZ)   # same shadow on screen as the walls throw
CONN_ZS = 1.0
CW, CH = 176, 320                       # canvas
OX, OY = 24, 96                         # cell origin inside the canvas
MG = 24                                 # ground margin round the canvas (neighbour stubs, shadows)
ZMAX = 100.0
RA_ZS = 105.0 / 128.0                   # TS-proportion heights -> RA (walls 40, pillars 60, tower top ~67)
PH_LEN = 34.0                           # how far the phantom neighbour arms reach past the cell edge

KHAKI = np.array([196, 176, 112.])
KHAKI_LT = np.array([218, 198, 134.])
STEEL = np.array([146, 148, 158.])
RECESS = np.array([74, 74, 78.])
PLATE = np.array([150, 150, 178.])
HOLE = np.array([26, 26, 32.])
GREEN = np.array([0, 214, 0.])
PADC = np.array([204, 204, 200.])
SOCKET = np.array([60, 60, 62.])
LAMP_OFF = np.array([150, 150, 142.])
LAMP_ON = np.array([255, 250, 225.])
BEAM_C = np.array([140, 142, 152.])        # coupling neck: a steel beam
SILL = 12
# generic coupling. Widths across the side's axis (v, *_w, sl_base, sl_top) are screen px, so a coupling is
# the same size on every side, as the walls it meets are (they are drawn on the flat ground grid); lengths
# along the axis (u) and heights are physical.
# The sleeve hugs the tower the same way on every side: centred sl_c out from the middle (physical), from
# sl_in inside that to sl_out past it, where the braces come down onto it (TS's connectors are not extended
# either). On the east and west that is the cell edge, so the sleeve reaches over the end of the wall there
# (walls are overlays in RA, drawn under buildings). On the south the wall comes into the tower's cell up to
# the sleeve: that bit of wall is drawn by an end piece for the kind of wall (end-<wall>-S-*.png). On the
# north the tower hides it all.
CPL = dict(sill_from=40.0, sill_w=21.0, sill_h=3.5,
           neck_from=36.0, neck_w=9.0, neck_h=13.0, neck_cham=3.0,
           sl_c=64.0, sl_in=9.0, sl_out=9.0,
           sl_base=31.0, sl_top=15.0, sl_h=32.0, sl_batter=0.2, sl_cham=2.5)

T = dict(CT.T)                                # the fitted TS proportions (1 cell = 128 units every way)
T['pad_h'] = 3.5
LAMP_P = (30.5, 30.5, 7.0)                    # foot of the door on the south-east recess (TS: same place)


def phys(X, Y):
    """screen-space ground position -> physical (dx, dy) from the cell centre."""
    return X - 64.0, (Y - 64.0) / SYF


def ground_grid():
    xs = (np.arange(-(OX + MG) * SS, (CW - OX + MG) * SS) + 0.5) / SS
    ys = (np.arange(-(OY + MG) * SS, (CH - OY + FZ * ZMAX + MG) * SS) + 0.5) / SS
    return np.meshgrid(xs, ys)


GX, GY = ground_grid()


def side_uv(side, X=None, Y=None):
    X = GX if X is None else X; Y = GY if Y is None else Y
    dx, dy = phys(X, Y)
    if side in 'EW':
        return (dx if side == 'E' else -dx), dy
    return (dy if side == 'S' else -dy), dx


def cpl_uv(side, X=None, Y=None):
    """coupling coordinates: u physical distance out from the centre along the side's axis, v screen px
    across it."""
    X = GX if X is None else X; Y = GY if Y is None else Y
    dx, dy = phys(X, Y)
    if side in 'EW':
        return (dx if side == 'E' else -dx), dy * SYF
    return (dy if side == 'S' else -dy), dx


def edge_u(side):
    """physical distance from the centre to the cell edge on that side (the screen cell is square)."""
    return 64.0 if side in 'EW' else 64.0 / SYF


def sleeve_outer_u(c=CPL):
    """physical distance out from the tower's middle to the sleeve's outer end (its mouth, at the foot)."""
    return c['sl_c'] + c['sl_out']


def coupling(side, c=CPL):
    """generic wall coupling on one side: a khaki sleeve hugging the foot of the tower where the braces
    come down, a little bigger all round than the end of any of the walls (GDI, Nod, RA concrete) so
    whichever wall arrives runs into it, on a low sill, with a short steel beam back into the tower. The
    sleeve's cross-section is a trapezoid like the GDI wall's; its mouth leans back like the walls' faces."""
    u, v = cpl_uv(side)
    av = np.abs(v)
    uc, s_in, s_out = c['sl_c'], c['sl_in'], c['sl_out']
    sill = (u >= c['sill_from']) & (u <= uc + s_out) & (av <= c['sill_w'])
    hs = np.where(sill, c['sill_h'] - np.clip(av - (c['sill_w'] - 1.5), 0, None), 0.0)
    neck = (u >= c['neck_from']) & (u <= uc - s_in + 0.5) & (av <= c['neck_w'])
    hn = np.where(neck, c['neck_h'] - np.clip(av - (c['neck_w'] - c['neck_cham']), 0, None), 0.0)
    b, h, ch = c['sl_batter'], c['sl_h'], c['sl_cham']
    wo = uc + s_out - u                          # in from the sleeve's outer end
    wi = u - (uc - s_in)                         # out from its inner end
    on = (wo >= 0) & (wi >= 0) & (av <= c['sl_base'])
    hv = h * np.clip((c['sl_base'] - av) / (c['sl_base'] - c['sl_top']), 0, 1)
    hv = np.minimum(hv, (h - ch) + (c['sl_top'] + ch - av))             # chamfer on the top's side edges
    ho = np.minimum(wo / b, (h - ch) + (wo - b * (h - ch)))              # leaning outer end, chamfered top edge
    hi = h - np.clip(1.5 - wi, 0, None)
    hf = np.where(on, np.clip(np.minimum.reduce([hv, ho, hi, np.full_like(hv, h)]), 0, None), 0.0)
    H = np.maximum.reduce([hs, hn, hf])
    C = np.where(hf >= np.maximum(hn, hs), FLANGE, np.where(hn >= hs, NECK, SILL)).astype(np.int8)
    C = np.where(H > 0, C, 0).astype(np.int8)
    return H, C


# ----------------------------------------------------------------------------- geometry
def build(prog=None, t=T, conns=''):
    """prog: build-up controls (pad, frame, clad, paint, ring, plate in 0..1); None = finished tower.
    Returns H, C, slab (the overhanging top plate), p."""
    p = dict(pad=1.0, frame=1.0, clad=1.0, paint=1.0, ring=1.0, plate=1.0)
    if prog:
        p.update(prog)
    dx, dy = phys(GX, GY)
    r = np.hypot(dx, dy)
    H = np.zeros_like(GX); C = np.zeros(GX.shape, np.int8)

    def put(h, comp):
        nonlocal H, C
        win = h > H + 1e-6
        H = np.where(win, h, H); C = np.where(win, comp, C)

    oct_ = CT.octagon_r(dx, dy)
    if p['pad'] > 0:
        pr = t['pad_r'] * np.cos(np.pi / 8) * p['pad']
        put(np.where(oct_ <= pr, t['pad_h'], 0.0), PAD)
    a, ch = t['body_a'], t['chamfer']
    ax, ay = np.abs(dx), np.abs(dy)
    starts = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            starts.append((sx * (a - 0.8 * ch), sy * a, sx * t['rib_foot'][0], sy * t['rib_foot'][1]))
            starts.append((sx * a, sy * (a - 0.8 * ch), sx * t['rib_foot'][1], sy * t['rib_foot'][0]))

    def beam(cx, cy, px, py, width, ztop, expo):
        L = np.hypot(px - cx, py - cy)
        ux, uy = (px - cx) / L, (py - cy) / L
        al = (dx - cx) * ux + (dy - cy) * uy
        ac = -(dx - cx) * uy + (dy - cy) * ux
        f = np.clip(al / L, 0, 1)
        return np.where((np.abs(ac) <= width) & (al >= -2) & (al <= L), ztop * (1 - f ** expo), 0.0)

    # steel frame (build-up only): a core column, eight posts and raking struts rising
    if 0 < p['frame'] and p['clad'] < 1:
        fz = p['frame']
        put(np.where(oct_ <= 22.0, (t['body_z'] + 2) * fz, 0.0), STRUT)
        for (cx, cy, px, py) in starts:
            d = np.maximum(np.abs(dx - cx), np.abs(dy - cy))
            tip = (t['body_z'] + 12) * fz
            put(np.where(d <= 3.2, tip - 3.0 * np.clip(d, 0, 3.2), 0.0), STRUT)
            put(beam(cx, cy, px, py, 1.8, t['body_z'] * 0.85 * fz, 1.0), STRUT)
    k = p['clad']
    if k > 0:
        body = (ax <= a) & (ay <= a) & (ax + ay <= 2 * a - ch)
        put(np.where(body, t['body_z'] * k, 0.0), SKIRT)
        recess = (ax + ay > 2 * a - ch - 4.0) & (ax + ay <= 2 * a - ch) & (np.abs(ax - ay) < 0.62 * ch)
        H = np.where(recess & (C == SKIRT), 0.0, H); C = np.where(recess & (C == SKIRT), 0, C)
        put(np.where(recess, (t['body_z'] - 4) * k, 0.0), CORE)
        for (cx, cy, px, py) in starts:
            put(beam(cx, cy, px, py, t['rib_w'], t['rib_top_z'] * k, 1.35), RIB)
    plate = np.full_like(GX, -1.0); Cs = np.zeros(GX.shape, np.int8); lo = 0.0
    if p['plate'] > 0 and k > 0:
        tz = t['top_z'] * k
        inr = r <= t['top_r'] * min(1.0, 0.6 + 0.4 * p['plate'])
        plate = np.where(inr, tz, -1.0)
        holes = np.zeros_like(r, bool)
        for hx, hy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            holes |= np.hypot(dx - hx * t['hole_at'], dy - hy * t['hole_at']) <= t['hole_r']
        plate = np.where(holes & inr, tz - t['hole_d'], plate)
        Cs = np.where(inr, TOP, 0).astype(np.int8)
        ring = inr & (r > t['top_r'] - t['ring_w'])
        plate = np.where(ring, tz + 1.2, plate)
        Cs = np.where(ring, RING, Cs).astype(np.int8)
        lo = tz - t['top_t']
    for side in conns:                            # generic couplings (only in the overlay renders)
        h, c = coupling(side)
        win = h > H
        H = np.where(win, h, H); C = np.where(win, c, C)
    return H, C, dict(top=plate, lo=lo, comp=Cs), p


def to_screen(H, slab, C=None):
    """physical heights -> screen-scaled heights for the ray-cast, softened a touch like the walls.
    With C, also returns the component map with the softening's skirts (each face spills ~1 px past its
    footprint) given to the taller part they came from, so a face keeps its own colour down to its foot."""
    Hu = H * SZF
    Hm = ndimage.gaussian_filter(Hu, 0.5 * SS, mode='nearest')
    top = np.where(slab['top'] > 0, slab['top'] * SZF, -1.0)
    sl = dict(top=top, lo=slab['lo'] * SZF, comp=slab['comp'])
    if C is None:
        return Hm, sl
    return Hm, sl, skirt_comp(Hu, Hm, C)


def skirt_comp(Hu, Hm, C, rad=None):
    rad = int(round(1.5 * SS)) if rad is None else rad
    raised = Hm > Hu + 0.3
    n0, n1 = Hu.shape
    Hp = np.pad(Hu, rad, mode='edge'); Cp = np.pad(C, rad, mode='edge')
    best = Hu.copy(); bc = C.copy()
    for oy in range(-rad, rad + 1):
        for ox in range(-rad, rad + 1):
            if oy * oy + ox * ox > rad * rad:
                continue
            h = Hp[rad + oy:rad + oy + n0, rad + ox:rad + ox + n1]
            m = h > best
            best = np.where(m, h, best)
            bc = np.where(m, Cp[rad + oy:rad + oy + n0, rad + ox:rad + ox + n1], bc)
    return np.where(raised, bc, C).astype(np.int8)


# ----------------------------------------------------------------------------- ray-cast + shading
def raycast(H, slab, PH):
    HS, WS = CH * SS, CW * SS
    rows = np.arange(HS)[:, None]; cols = np.arange(WS)[None, :] + MG * SS
    n0 = MG * SS
    Hs, Ps = H * SS, PH * SS
    top = slab['top'] * SS; lo = slab['lo'] * SS
    zmax = int(np.ceil(max(Hs.max(), top.max(), Ps.max()))) + 2
    hit_z = np.full((HS, WS), -1.0)
    kind = np.zeros((HS, WS), np.int8)          # 1 ground-attached, 2 slab, 3 phantom
    for z in range(zmax, -1, -1):
        jj = rows + int(round(FZ * z)) + n0
        free = hit_z < 0
        g = free & (Hs[jj, cols] >= z) & (Hs[jj, cols] > 0.5)
        s = free & ~g & (top[jj, cols] >= z) & (z >= lo) & (top[jj, cols] > 0)
        q = free & ~g & ~s & (Ps[jj, cols] >= z) & (Ps[jj, cols] > 0.5)
        for m, kd in ((g, 1), (s, 2), (q, 3)):
            hit_z[m] = z; kind[m] = kd
    hit = hit_z >= 0
    gj = np.clip((rows + np.round(FZ * np.maximum(hit_z, 0)) + n0).astype(int), 0, H.shape[0] - 1)
    gi = np.broadcast_to(cols, (HS, WS))
    return hit, np.maximum(hit_z, 0) / SS, gj, gi, kind


def normals(H, slab, gj, gi, kind):
    gy, gx = np.gradient(H, 1.0 / SS)
    nx, ny = -gx[gj, gi], -gy[gj, gi]
    tt = np.where(slab['top'] > 0, slab['top'], slab['lo'] - 8)
    gyt, gxt = np.gradient(tt, 1.0 / SS)
    on = kind == 2
    nx = np.where(on, -gxt[gj, gi], nx); ny = np.where(on, -gyt[gj, gi], ny)
    nx, ny = nx / SZF, ny * SYF / SZF             # screen-scaled slopes -> physical slopes
    nz = np.ones_like(nx)
    nl = np.sqrt(nx * nx + ny * ny + nz * nz)
    return nx / nl, ny / nl, nz / nl


def in_shadow(env, x, y, z):
    kx, ky = SH_DIR
    sh = np.zeros(x.shape, bool)
    i0 = (x + OX + MG) * SS; j0 = (y + OY + MG) * SS
    for t in np.arange(0.75, ZMAX, 0.75):
        i = np.clip(np.round(i0 - kx * t * SS).astype(int), 0, env.shape[1] - 1)
        j = np.clip(np.round(j0 - ky * t * SS).astype(int), 0, env.shape[0] - 1)
        sh |= env[j, i] > z + t + 0.6
    return sh


def downsample(rgba):
    pre = rgba.copy(); pre[..., :3] *= rgba[..., 3:4]
    pre = pre.reshape(CH, SS, CW, SS, 4).mean(axis=(1, 3))
    a = pre[..., 3:4]
    out = np.where(a > 1e-6, pre[..., :3] / np.maximum(a, 1e-6), 0)
    return Image.fromarray(np.dstack([np.clip(out, 0, 255), np.clip(a * 255, 0, 255)]).round().astype(np.uint8), 'RGBA')


def fade_right(im, band=14.0):
    """the tower's shadow runs past the canvas's east edge; fade it out over the last few px instead of a
    hard cut (shadow pixels only)."""
    a = np.array(im).astype(float)
    f = np.clip((CW - 0.5 - np.arange(CW)[None, :]) / band, 0, 1)
    f = f * f * (3 - 2 * f)
    shadow = a[..., :3].max(axis=2) < 8
    a[..., 3] = np.where(shadow, a[..., 3] * f, a[..., 3])
    return Image.fromarray(a.round().astype(np.uint8), 'RGBA')


def wall_albedo(x, y, z, comp, grain):
    """exactly the GDI wall's concrete and collar (walls2.render)."""
    ew = np.abs(x - 64.0) >= np.abs(y - 64.0)
    along = np.where(ew, x - 64.0, y - 64.0)
    half = np.mod(along, 128.0) < 64.0
    conc = W.CONCRETE * (1 + grain)[..., None] * np.where(half, 1.0, 0.96)[..., None]
    rib = 1 - smoothstep(0.0, 0.9, phase(along, W.P['rib_every']))
    och = W.OCHRE * (1 + 0.8 * grain)[..., None] * (1 - 0.18 * rib)[..., None]
    return np.where((comp == COLLAR)[..., None], och, conc)


def shade_scene(H, C, slab, p, dmg=None):
    """ray-cast and light a scene; returns everything the compositing steps need."""
    hit, z, gj, gi, kind = raycast(H, slab, np.zeros_like(H))
    nx, ny, nz = normals(H, slab, gj, gi, kind)
    x, y = GX[gj, gi], GY[gj, gi]
    comp = np.where(kind == 2, slab['comp'][gj, gi], C[gj, gi])
    env = np.maximum(H, np.where(slab['top'] > 0, slab['top'], 0))
    ssh = in_shadow(env, x, y, z)
    ndl = np.clip(nx * W.LIGHT[0] + ny * W.LIGHT[1] + nz * W.LIGHT[2], 0, None)
    shade = W.AMBIENT + W.SKY * (0.5 + 0.5 * nz) + W.DIFFUSE * ndl * (1 - 0.8 * ssh)
    top_like = nz > 0.75
    ew_face = np.abs(ny) >= np.abs(nx)
    u = np.where(top_like | ew_face, x, y)
    v = np.where(top_like, y, z)
    grain = sample(NOISE_FINE, u, v) * 0.035 + sample(NOISE_MOTTLE, u, v) * 0.05
    alb = albedo(x, y, z, comp, grain, top_like, u, v, p, nx, ny)
    if dmg is not None:
        alb = dmg['mats'](alb, x, y, z, comp, top_like, grain, u, v)
    grime = np.clip(1 - z / 15.0, 0, 1) ** 1.5 * np.clip(0.55 + 0.35 * sample(NOISE_GRIME, u, v), 0, 1)
    grime = grime * ~np.isin(comp, [TOP, RING]) * np.where(comp == PAD, 0.3, 1.0)
    alb = alb * (1 - grime[..., None]) + W.GRIME * grime[..., None]
    ao = 0.8 + 0.2 * np.clip(z / W.P['h'], 0, 1)
    col = alb * (shade * ao)[..., None]
    return dict(hit=hit, z=z, x=x, y=y, comp=comp, col=col, alb=alb, env=env, kind=kind)


def ground_alpha(env):
    HS, WS = CH * SS, CW * SS
    rows = np.arange(HS)[:, None]; cols_ = np.arange(WS)[None, :]
    gxg = (cols_ + 0.5) / SS - OX + 0.0 * rows
    gyg = (rows + 0.5) / SS - OY + 0.0 * cols_
    gsh = in_shadow(env, gxg, gyg, np.zeros_like(gxg))
    shadow_a = ndimage.gaussian_filter(gsh.astype(float), 1.5 * SS) * W.SHADOW_ALPHA
    dist = ndimage.distance_transform_edt(~(env > 0.5)) / SS
    ii = np.clip(((gxg + OX + MG) * SS).astype(int), 0, env.shape[1] - 1)
    jj = np.clip(((gyg + OY + MG) * SS).astype(int), 0, env.shape[0] - 1)
    contact = np.clip(1 - dist[jj, ii] / 7.0, 0, 1) ** 1.5 * 0.5
    return np.maximum(shadow_a, contact)


def tower_scene(prog=None, damage=None, physical=False):
    H, C, slab, p = build(prog)
    dmg = None
    if damage is not None:
        H, C, slab, dmg = damage(H, C, slab)
    if physical:
        return H, C, slab, p, dmg
    Hm, slm, Cm = to_screen(H, slab, C)
    return Hm, Cm, slm, p, dmg


def render(prog=None, damage=None, lamp=None, want_trim=False):
    """the tower on its own (no couplings)."""
    H, C, slab, p, dmg = tower_scene(prog, damage)
    sc = shade_scene(H, C, slab, p, dmg)
    hit = sc['hit']
    rgba = np.zeros(hit.shape + (4,))
    rgba[..., :3] = np.where(hit[..., None], sc['col'], 0.0)
    rgba[..., 3] = np.where(hit, 1.0, ground_alpha(sc['env']))
    ring = ndimage.binary_dilation(hit, iterations=int(0.9 * SS)) & ~hit
    rgba[..., :3] = np.where(ring[..., None], 28.0, rgba[..., :3])
    rgba[..., 3] = np.where(ring, np.maximum(rgba[..., 3], 0.55), rgba[..., 3])
    out = [fade_right(downsample(rgba))]
    if want_trim:
        alb = sc['alb']
        greenish = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
        tm = (hit & greenish).astype(float).reshape(CH, SS, CW, SS).mean(axis=(1, 3))
        out.append(Image.fromarray((tm * 255).round().astype(np.uint8), 'L'))
    if lamp is not None:
        out.append(lamp_frames(lamp, hit, sc['z'], sc['x'], sc['y'], sc['comp']))
    return out if len(out) > 1 else out[0]


def render_coupling(side, prog=None, damage=None, cdamage=None):
    """overlay for one side: the coupling where it is not hidden by the tower, its outline, and the
    shadow it throws on the tower and the ground. Draw it on top of the tower frame."""
    Ht, Ct, slab, p, dmg = tower_scene(prog, damage, physical=True)
    hc, cc = coupling(side)
    if cdamage is not None:
        hc, cmats = cdamage(side, hc, cc)
    else:
        cmats = None
    win = hc > Ht
    Hp = np.where(win, hc, Ht); C = np.where(win, cc, Ct).astype(np.int8)
    H, slab, C = to_screen(Hp, slab, C)

    def mats(alb, x, y, z, comp, top_like, grain, u, v):
        if dmg is not None:
            alb = dmg['mats'](alb, x, y, z, comp, top_like, grain, u, v)
        if cmats is not None:
            alb = cmats(alb, x, y, z, comp, top_like, grain, u, v)
        return alb
    sc = shade_scene(H, C, slab, p, dict(mats=mats))
    hit, comp = sc['hit'], sc['comp']
    mine = hit & np.isin(comp, [NECK, FLANGE, SILL])
    # the coupling's shadow on what is round it
    env_c = np.where(np.isin(C, [NECK, FLANGE, SILL]), H, 0.0)
    sh_obj = in_shadow(env_c, sc['x'], sc['y'], sc['z']) & hit & ~mine
    ga = ground_alpha(env_c)
    rgba = np.zeros(hit.shape + (4,))
    rgba[..., :3] = np.where(mine[..., None], sc['col'], 0.0)
    a = np.where(mine, 1.0, np.where(hit, 0.45 * ndimage.gaussian_filter(sh_obj.astype(float), 0.8 * SS), ga))
    rgba[..., 3] = a
    ring = ndimage.binary_dilation(mine, iterations=int(0.9 * SS)) & ~hit
    rgba[..., :3] = np.where(ring[..., None], 28.0, rgba[..., :3])
    rgba[..., 3] = np.where(ring, np.maximum(rgba[..., 3], 0.55), rgba[..., 3])
    return fade_right(downsample(rgba))


def albedo(x, y, z, comp, grain, top_like, u, v, p, nx=None, ny=None):
    dx, dy = phys(x, y)
    z = z / SZF                                  # physical height for the tests below
    r = np.hypot(dx, dy)
    paint = p['paint']
    kh = KHAKI * (1 + 1.2 * grain)[..., None]
    seam = (phase(u, 13.0, 6.5) < 0.6) & ~top_like
    kh = np.where(seam[..., None], kh * 0.84, kh)
    roof_edge = top_like & (np.maximum(np.abs(dx), np.abs(dy)) > T['body_a'] - 2.5)
    kh = np.where(roof_edge[..., None], kh * 1.08, kh)
    streak = smoothstep(0.3, 1.3, sample(NOISE_MOTTLE, u * 3.0, 5.0 + 0 * v)) * ~top_like * 0.14
    kh = kh * (1 - streak)[..., None]
    body_c = STEEL * (1 + grain)[..., None] * (1 - paint) + kh * paint
    rib_c = (STEEL * 1.12 * (1 - paint) + KHAKI_LT * paint) * (1 + grain)[..., None]
    rec_c = RECESS * (1 + grain)[..., None]
    se = (dx > 0) & (dy > 0) & (comp == CORE)
    door = se & (np.abs(dx - dy) < 5.5) & (z < 24)
    frame_ = se & (np.abs(np.abs(dx - dy) - 6.2) < 0.9) & (z < 26)
    rec_c = np.where(door[..., None], RECESS * 0.5, rec_c)
    rec_c = np.where(frame_[..., None], KHAKI * 0.7, rec_c)
    plate_c = PLATE * (1 + 0.8 * grain)[..., None]
    rim = (r > T['top_r'] - T['ring_w'] - 2.0) & (r <= T['top_r'] - T['ring_w'])
    plate_c = np.where(rim[..., None], plate_c * 0.82, plate_c)
    groove = np.abs(r - 11.5) < 0.9
    plate_c = np.where(groove[..., None], plate_c * 0.78, plate_c)
    bevel = (r > 11.5 + 0.9) & (r < 13.2)
    plate_c = np.where(bevel[..., None], plate_c * 1.08, plate_c)
    stain = smoothstep(0.4, 1.4, sample(NOISE_GRIME, u * 1.3, v * 1.3)) * 0.12
    plate_c = plate_c * (1 - stain)[..., None]
    hole = np.zeros_like(r, bool); hole_lit = np.zeros_like(r, bool)
    for hx, hy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
        ex, ey = dx - hx * T['hole_at'], dy - hy * T['hole_at']
        dh = np.hypot(ex, ey)
        hole |= dh <= T['hole_r']
        hole_lit |= (dh > T['hole_r']) & (dh <= T['hole_r'] + 1.4) & (ex + ey > 0.5)
    plate_c = np.where(hole[..., None], HOLE, plate_c)
    plate_c = np.where(hole_lit[..., None], plate_c * 1.22, plate_c)
    ring_c = (GREEN * p['ring'] + KHAKI_LT * (1 - p['ring']))[None, None, :] * (1 + 0.5 * grain)[..., None]
    pad_c = PADC * (1 + grain)[..., None]
    ang = np.arctan2(dy, dx)
    sock = (np.abs(np.mod(ang + np.pi / 8, np.pi / 4) - np.pi / 8) < 0.09) & (r > 44) & (r < 54)
    centre = (CT.octagon_r(dx, dy) < 15) & (p['pad'] >= 0.85)
    sock = sock & (p['pad'] >= 0.85)
    pad_c = np.where((sock | centre)[..., None], SOCKET * (1 + grain)[..., None], pad_c)
    strut_c = np.array([96, 98, 106.]) * (1 + 1.2 * grain)[..., None]
    wall_c = wall_albedo(x, y, z, comp, grain)
    # generic coupling: khaki sleeve (the tower's paint) with a steel lip round its mouth and bolts on top;
    # steel beam with joints; the pad's concrete for the sill
    c = CPL
    ew = np.abs(dx) >= 0.75 * np.abs(dy)         # which side's coupling a point belongs to
    cu = np.where(ew, np.abs(dx), np.abs(dy)); cv = np.where(ew, dy * SYF, dx)
    s_out, s_in = c['sl_out'], c['sl_in']
    wo = c['sl_c'] + s_out - cu
    fl_c = KHAKI * (1 + 1.2 * grain)[..., None]
    lip = (wo > c['sl_batter'] * z + 0.6) & (wo < c['sl_batter'] * z + 3.2)
    fl_c = np.where(lip[..., None], STEEL * (1 + grain)[..., None], fl_c)
    mid = (s_out + s_in) * 0.5
    band = np.abs(wo - mid) < 0.6
    fl_c = np.where(band[..., None], fl_c * 0.8, fl_c)
    bolt = top_like & (np.hypot(np.abs(cv) - 9.0, (wo - mid - 2.6) * np.where(ew, 1.0, SYF)) < 1.3)
    fl_c = np.where(bolt[..., None], fl_c * 0.5, fl_c)
    joint = phase(cu, 16.0, 8.0) < 0.6
    neck_c = BEAM_C * (1 + grain)[..., None] * np.where(joint, 0.62, 1.0)[..., None]
    sill_c = PADC * (1 + grain)[..., None]
    alb = np.zeros(x.shape + (3,))
    for k_, c_ in ((PAD, pad_c), (CORE, rec_c), (RIB, rib_c), (SKIRT, body_c), (TOP, plate_c),
                   (RING, ring_c), (CONN, wall_c), (COLLAR, wall_c), (STRUT, strut_c),
                   (NECK, neck_c), (FLANGE, fl_c), (SILL, sill_c)):
        alb = np.where((comp == k_)[..., None], c_, alb)
    lx, ly, lz = LAMP_P
    lamp_m = (np.hypot(dx - lx, dy - ly) < 5.5) & (np.abs(z - lz) < 3.5) & np.isin(comp, [CORE, PAD])
    alb = np.where(lamp_m[..., None], LAMP_OFF, alb)
    return alb


def lamp_frames(levels, real, z, x, y, comp):
    """the blinking lamp as overlay frames (lit lamp + a small glow), one per level."""
    lx, ly, lz = LAMP_P
    pdx, pdy = phys(x, y)
    lamp_m = real & (np.hypot(pdx - lx, pdy - ly) < 5.5) & (np.abs(z / SZF - lz) < 3.5) & np.isin(comp, [CORE, PAD])
    core = lamp_m.astype(float)
    glow = np.clip(ndimage.gaussian_filter(core, 3.0 * SS) * 4.0, 0, 1)
    frames = []
    for level in levels:
        rgba = np.zeros(core.shape + (4,))
        rgba[..., :3] = LAMP_ON
        rgba[..., 3] = np.clip(np.maximum(core * level, glow * 0.5 * level), 0, 1)
        frames.append(downsample(rgba))
    return frames


