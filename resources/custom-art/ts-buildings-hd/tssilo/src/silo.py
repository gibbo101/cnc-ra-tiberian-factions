"""
TS GDI Tiberium Silo (GASILO, TSSILO in the mod) as a model for hd.py, at TS's own size on its 2x2 foundation.

World: X east, Y south, units (1 cell = 128), origin at the centre of the 2x2 foundation, Z up.
Read from GTSILO / GTSILOMK in TS's own camera (GTSILO_B's lamps and the blades' feet fix the centre and the
heights):
  earth  a dark earth ring round the silo (TS: no pad)
  body   a dark ribbed drum, as tall as a 2-storey block, carrying the lid
  lid    a wide, shallow blue-grey dome of glass panels in a dark rim (radius 80) overhanging the body, a small cap
         on top; it shows the stored Tiberium (GTSILO_A: four fill levels)
  blades five green house-colour blades: each lies on the lid from the cap out past the rim, where its lamp sits
         (GTSILO_B), then drops as a buttress to the ground, its sloping edge stepped
  pump   a grey slatted loader tower on legs at the foundation's south corner, a pipe across to the body
  vent   a striped vent box against the body on the east
Layouts: 'ts' where TS draws it (its middle a little west of the foundation's: the TS-angle view); 'ra' centred
on the 2x2 (RA's grid).
"""
import numpy as np
import hd

(SLAB, SKIRT, LID, RIM, CAP, FIN, TIPLAMP, PUMP, PIPE, VENT, GRATE) = range(1, 12)
HOUSE = {FIN}

BUILD_KEYS = ('pad', 'lid', 'skirt', 'fins', 'pump', 'vent')
DONE = {k: 1.0 for k in BUILD_KEYS}

LAYOUTS = {'ts': (-9.0, 5.0), 'ra': (0.0, 0.0)}
FOOT_R = {'ts': 134.0, 'ra': 126.0}  # the claws' reach (TS's; on RA's grid kept inside the 2x2's canvas)
FIN_ORDER = (1, 0, 4, 3, 2)          # the order TS's GTSILOMK puts the blades on: north-east (with the lid), north,
                                     # west, south, east

P = dict(
    slab_h=0.0,
    soil_r=96.0,                                     # a dark earth ring round the foot (TS: no pad)
    centre=LAYOUTS['ts'],                            # (set per layout by geo())
    skirt=(72.0, 68.0, 40.0),                        # the body: radius at the ground, at the top, top z
    lid_r=80.0, rim=(38.0, 44.0), crown=8.0,         # rim band z0..z1, the dome rises crown above the rim
    cap=(10.0, 6.0),                                 # radius, height above the crown
    # five blades (TS's five lamps, 72 degrees apart)
    fins_az=tuple(np.deg2rad(a) for a in (-147.0, -75.0, -3.0, 69.0, 141.0)),
    lamp_r=95.0, foot_r=127.0, root_r=60.0,          # the lamp (the bend), the buttress's foot, its inner edge
    fin_w=(3.0, 20.0), fin_t=3.4, plate_t=3.0,       # the strip's width at the cap, at the bend; thicknesses
    claw_slope=5.0,                                  # the buttress's sides: height lost per unit out from the ridge
    pump=dict(off=(94.0, 98.0), w=30.0, d=28.0, z=46.0, legs=12.0),
    vent=dict(off=(83.0, 24.0), w=24.0, d=24.0, z=34.0),
)


def geo(layout='ts', p=P):
    """the parameters with the layout's centre."""
    q = dict(p)
    q['centre'] = LAYOUTS[layout]
    q['foot_r'] = FOOT_R[layout]
    return q


def box(X, Y, x0, x1, y0, y1):
    return (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1)


def fin_tip(az, p=P):
    """how far out the blade's lamp sits (the bend)."""
    return p['lamp_r']


def lid_height(d, p=P):
    z0, z1 = p['rim']
    return z1 + p['crown'] * np.clip(1 - (d / p['lid_r']) ** 2, 0, 1)


def lamp_z(p=P):
    return lid_height(p['lid_r'], p) + p['fin_t'] + 0.2


def strip_top(r, p=P):
    """the strip's top along the blade: on the lid, then level out to the bend."""
    R = p['lid_r']
    return np.where(r <= R, lid_height(np.minimum(r, R), p) + p['fin_t'], lid_height(R, p) + p['fin_t'])


def strip_width(r, p=P):
    w0, w1 = p['fin_w']
    return w0 + (w1 - w0) * np.clip(r / p['lamp_r'], 0, 1) ** 1.3


def plate_top(r, p=P):
    """the buttress's top edge: level with the strip to the bend, then down to its foot, stepped."""
    zb = lamp_z(p) - 1.0
    t = np.clip((r - p['lamp_r']) / (p['foot_r'] - p['lamp_r']), 0, 1)
    top = zb * (1 - t ** 1.7)                          # it stays high, then drops to a point (TS's claws)
    steps = np.floor(t * 4.0)
    notch = (t * 4.0 - steps) < 0.35
    return np.where(r <= p['lamp_r'], zb, top - 5.0 * notch * (t < 0.95) * (t > 0.05))


def scene(X, Y, p=P, prog=None, layout='ts'):
    g = dict(DONE); g.update(prog or {})
    p = geo(layout, p)
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

    cx, cy = p['centre']
    pm, v = p['pump'], p['vent']
    pcx, pcy = cx + pm['off'][0], cy + pm['off'][1]
    vcx, vcy = cx + v['off'][0], cy + v['off'][1]
    d = np.hypot(X - cx, Y - cy)
    az = np.arctan2(Y - cy, X - cx)
    if g['pad'] > 0:
        soil = d <= p['soil_r'] * g['pad']
        # and under the loader
        soil |= (g['pad'] >= 1) & box(X, Y, pcx - pm['w'] / 2 - 8, pcx + pm['w'] / 2 + 8, pcy - pm['d'] / 2 - 8, pcy + pm['d'] / 2 + 6)
        put(np.where(soil, 1.0 + 0.6 * np.clip(1 - d / p['soil_r'], 0, 1), 0.0), SLAB)
    # ---- the body: a ribbed drum under the lid (rises after the lid appears: TS's GTSILOMK)
    if g['skirt'] > 0:
        r0, r1, zt = p['skirt']
        zt_ = zt * g['skirt']
        rr = r0 + (r1 - r0) * 0.5
        put(np.where(d <= rr, zt_, 0.0), SKIRT)
        put(np.where((d > rr) & (d <= r0), np.minimum(zt_, 6.0), 0.0), SKIRT)          # a plinth
    # ---- the lid: a slab (it overhangs the body), its dark rim band and the glass dome; it sits on the body,
    #      so it rides up with it in the build-up
    lift = p['skirt'][2] * (1.0 - g['skirt']) if g['skirt'] < 1 else 0.0
    if g['lid'] > 0:
        R = p['lid_r'] * min(1.0, 0.25 + 0.75 * g['lid'])
        z0, z1 = p['rim']
        on = d <= R
        top = lid_height(d * p['lid_r'] / max(R, 1e-3), p) - lift
        slab(top, np.full_like(X, z0 - lift), LID, on, 'lid')
        cr, ch = p['cap']
        capm = d <= cr
        slab(np.where(capm, lid_height(0.0, p) + ch * np.sqrt(np.clip(1 - (d / cr) ** 2, 0, 1)) + 0.5 - lift, -1.0),
             np.full_like(X, z1 - lift), CAP, capm, 'cap')
    # ---- the blades: a strip on the lid from the cap out to the bend (the lamp), then a buttress to the ground
    if g['fins'] > 0:
        n = len(p['fins_az'])
        shown = int(np.ceil(g['fins'] * n - 1e-6))
        for k in FIN_ORDER[:shown]:
            a = p['fins_az'][k]
            ux, uy = np.cos(a), np.sin(a)
            sl = min(1.0, 0.25 + 0.75 * g['lid'])                      # it unfolds with the lid
            al = ((X - cx) * ux + (Y - cy) * uy) / sl
            ac = (-(X - cx) * uy + (Y - cy) * ux) / sl
            w = strip_width(al, p)
            strip = (al >= 3.0) & (al <= p['lamp_r'] + 3.0) & (np.abs(ac) <= w / 2)
            zt = strip_top(al, p) - lift
            zt = zt + 1.0 * np.clip(1 - np.abs(ac) / np.maximum(w / 2, 1e-3), 0, 1)       # a ridge along it
            slab(zt, zt - p['fin_t'] - 1.0, FIN, strip, 'fin')
            # the buttress (only once the body is up): a ridge falling from the bend to its foot, its sides sloping
            # out to the ground (TS's claws catch the light on them)
            if g['skirt'] >= 1:
                pt = plate_top(al, p) - p['claw_slope'] * np.maximum(np.abs(ac) - p['plate_t'] / 2, 0.0)
                claw = (al >= p['root_r']) & (al <= p['foot_r']) & (pt > 0.5)
                put(np.where(claw, pt, 0.0), FIN)
            # its lamp at the bend
            tx, ty = cx + p['lamp_r'] * sl * ux, cy + p['lamp_r'] * sl * uy
            dl = np.hypot(X - tx, Y - ty)
            lz = lamp_z(p) - lift
            slab(np.full_like(X, lz + 2.4) + 0.8 * np.sqrt(np.clip(1 - (dl / 2.6) ** 2, 0, 1)), np.full_like(X, lz - 1.5),
                 TIPLAMP, dl <= 2.6, 'tiplamp')
    # ---- the loader tower at the south corner (on legs, slatted), a pipe across to the body; the vent box
    if g['pump'] > 0:
        zp = pm['z'] * g['pump']
        lg = pm['legs']
        x0, x1, y0, y1 = pcx - pm['w'] / 2, pcx + pm['w'] / 2, pcy - pm['d'] / 2, pcy + pm['d'] / 2
        body = box(X, Y, x0, x1, y0, y1)
        slab(np.full_like(X, zp), np.full_like(X, min(lg, zp)), PUMP, body, 'pump')
        for (lx, ly) in ((x0 + 3, y0 + 3), (x1 - 3, y0 + 3), (x0 + 3, y1 - 3), (x1 - 3, y1 - 3)):
            put(np.where(box(X, Y, lx - 2.5, lx + 2.5, ly - 2.5, ly + 2.5), lg + 0.5, 0.0), PIPE)
        put(np.where(box(X, Y, x0 + 4, x1 - 4, y0 + 4, y1 - 4), zp + 4.0 * g['pump'], 0.0), GRATE)
        ux, uy = cx - pcx, cy - pcy
        L = np.hypot(ux, uy); ux, uy = ux / L, uy / L
        al = (X - pcx) * ux + (Y - pcy) * uy
        ac = -(X - pcx) * uy + (Y - pcy) * ux
        pipe = (al >= 0) & (al <= L - p['skirt'][1] + 4) & (np.abs(ac) <= 3.4)
        zc = zp - 9.0 + 0.0 * al
        slab(zc + 3.4, zc - 3.4, PIPE, pipe & (g['pump'] >= 1), 'chute')
    if g['vent'] > 0:
        zv = v['z'] * g['vent']
        vb = box(X, Y, vcx - v['w'] / 2, vcx + v['w'] / 2, vcy - v['d'] / 2, vcy + v['d'] / 2)
        put(np.where(vb, zv, 0.0), VENT)
        put(np.where(box(X, Y, vcx - v['w'] / 2 + 3, vcx + v['w'] / 2 - 3, vcy - v['d'] / 2 + 3, vcy + v['d'] / 2 - 3), zv + 1.2, 0.0), GRATE)
    return hd.Scene(H, C, slabs, {})


FLAT = {SLAB: (150, 150, 146), SKIRT: (70, 66, 62), LID: (150, 156, 184), RIM: (60, 60, 66), CAP: (120, 120, 130),
        FIN: (0, 200, 0), TIPLAMP: (200, 200, 200), PUMP: (130, 130, 136), PIPE: (110, 110, 116),
        VENT: (140, 140, 146), GRATE: (60, 60, 64)}
