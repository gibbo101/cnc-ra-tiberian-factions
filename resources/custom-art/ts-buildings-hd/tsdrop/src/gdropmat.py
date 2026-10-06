"""Materials for the Dropship Bay (gdrop.py): albedo, normal tweaks and glow per pixel of an hd.Render.
The east half is the Upgrade Center's block, so plugmat colours it (it sees the render moved into plug's own frame);
the bay's own parts are coloured here, after Luke's high-res picture of the bay, in GTDROP's colours:
  deck      plugmat's concrete with its slab joints, tan dirt and grime round the guard and the pad
  pad       a dark metal plate: a light rim (B's four light strips on it: dim blue-grey; lightsB lights them), tan lines
            from its corners into a centre square outlined dull red, darker panel seams
  guard     the jet blast guard: dark streaky metal, its ribs, end plates and top cap a shade lighter; the slot round it
            near black
  ramp      a dark blue-grey plate between lighter rails, house-green hazard stripes across its middle, the hinge beam
  tower     tan plaster panels with grime (TS's tan; the picture's), TS's blue-grey band under the eaves; the console's
            sloped east face in larger tan panels (GDI's emblem there in the picture: left off, no logos), the raised
            blocks on its ridge, a louvred vent; the south gable face and the lean-to house green; a steel pipe
  notch     TS's grey slope: concrete with tan dirt
  ledge     the tan beam along the deck's south-west edge and its column
House green exactly 0,214,0 x (1 + 1.1 grain)."""
import os
import numpy as np
from walls2 import sample, smoothstep, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME
import gdrop as M, plug as PL, plugmat as PM

GREEN = PM.GREEN
WALLC = np.array([178, 146, 88.])           # the tower's tan plaster: TS 148,132,80 / 164,132,56; the picture's tan
WALLD = np.array([128, 102, 60.])
WALLSEAM = np.array([96, 76, 44.])
STEELC = np.array([168, 168, 176.])
VENTC = np.array([46, 46, 52.])
TRIMC = np.array([150, 150, 196.])          # TS's light blue-grey band (136,136,160 x 1.2)
TRIMD = np.array([70, 70, 96.])
ROOFC = np.array([220, 184, 108.])           # TS 152,120,56 / 164,132,56 / 148,132,80
ROOFL = np.array([222, 204, 150.])          # TS's lighter panels 160,160,136
RAMPF = np.array([104, 104, 128.])          # the ramp's plate: TS's blue-grey 88,88,112 / 112,112,136, the picture's dark
RAMPR_C = np.array([136, 136, 160.])        # its rails and hinge beam
GUARDC = np.array([82, 82, 88.])            # the guard: TS 68-96 grey; the picture's charcoal metal
GRIBC = np.array([112, 112, 120.])
GSLOTC = np.array([34, 34, 38.])
PADC = np.array([78, 78, 86.])              # the pad plate: TS's darker grey 68-84; the picture's
PADSEAM = np.array([52, 52, 58.])
PADRIM = np.array([168, 168, 174.])         # its light rim: TS 128-140
PADLINE = np.array([186, 150, 80.])         # the tan lines: TS 140,120,80 (brightened)
PADSQ = np.array([152, 62, 48.])            # the centre square's outline (the picture's dull red)
BARC = np.array([122, 124, 150.])           # B's strips, dark
BAR_ON = np.array([236, 240, 255.])
NWALLC = np.array([166, 166, 168.])         # TS 112 grey
DIRTC = np.array([184, 162, 112.])          # TS's tan dirt on it 128,120,84 / 140,120,80
# GTDROP_B, read off TS's frames per bar (W, N, E, S): (white level 0..1, the share of the bar flashing house colour).
# 00-19 over the healthy building (a bright flash: white, house colour, fading; then a softer one), 20-39 the damaged:
# the west bar as before, the north bar half smashed (its rest flashes harder, first flash only), the south bar a stub
# (second flash only), the east bar dimmer
B_LEVELS = [
    ((0.0, 0.0), (0.03, 0.0), (0.03, 0.0), (0.03, 0.0)), ((0.0, 0.0), (0.03, 0.0), (0.03, 0.0), (0.03, 0.0)),
    ((0.03, 0.0), (0.03, 0.0), (0.09, 0.0), (0.0, 0.0)), ((0.26, 0.0), (0.26, 0.0), (0.35, 0.0), (0.24, 0.0)),
    ((0.97, 0.0), (0.84, 0.0), (1.0, 0.0), (0.87, 0.0)), ((0.0, 0.63), (0.0, 0.55), (0.01, 0.67), (0.0, 0.67)),
    ((0.59, 0.0), (0.52, 0.0), (0.65, 0.0), (0.53, 0.0)), ((0.26, 0.0), (0.26, 0.0), (0.35, 0.0), (0.24, 0.0)),
    ((0.03, 0.0), (0.03, 0.0), (0.09, 0.0), (0.0, 0.0)), ((0.0, 0.0), (0.03, 0.0), (0.03, 0.0), (0.03, 0.0)),
    ((0.0, 0.0), (0.03, 0.0), (0.03, 0.0), (0.03, 0.0)), ((0.0, 0.0), (0.03, 0.0), (0.03, 0.0), (0.03, 0.0)),
    ((0.03, 0.0), (0.06, 0.0), (0.06, 0.0), (0.05, 0.0)), ((0.16, 0.0), (0.25, 0.0), (0.2, 0.0), (0.19, 0.0)),
    ((0.52, 0.0), (0.71, 0.0), (0.54, 0.0), (0.52, 0.0)), ((0.0, 0.37), (0.05, 0.45), (0.05, 0.33), (0.05, 0.33)),
    ((0.32, 0.0), (0.45, 0.0), (0.35, 0.0), (0.33, 0.0)), ((0.16, 0.0), (0.25, 0.0), (0.2, 0.0), (0.19, 0.0)),
    ((0.03, 0.0), (0.06, 0.0), (0.06, 0.0), (0.05, 0.0)), ((0.0, 0.0), (0.03, 0.0), (0.03, 0.0), (0.03, 0.0)),
    ((0.0, 0.0), (0.05, 0.0), (0.03, 0.0), (0.0, 0.0)), ((0.0, 0.0), (0.05, 0.0), (0.03, 0.0), (0.0, 0.0)),
    ((0.03, 0.0), (0.05, 0.0), (0.09, 0.0), (0.0, 0.0)), ((0.26, 0.0), (0.47, 0.0), (0.35, 0.0), (0.0, 0.0)),
    ((0.97, 0.0), (1.0, 0.0), (0.35, 0.0), (0.0, 0.0)), ((0.0, 0.63), (0.0, 1.0), (0.09, 0.0), (0.0, 0.0)),
    ((0.59, 0.0), (0.94, 0.0), (0.65, 0.0), (0.0, 0.0)), ((0.26, 0.0), (0.47, 0.0), (0.35, 0.0), (0.0, 0.0)),
    ((0.03, 0.0), (0.05, 0.0), (0.09, 0.0), (0.0, 0.0)), ((0.0, 0.0), (0.05, 0.0), (0.03, 0.0), (0.0, 0.0)),
    ((0.0, 0.0), (0.05, 0.0), (0.03, 0.0), (0.0, 0.0)), ((0.0, 0.0), (0.05, 0.0), (0.03, 0.0), (0.0, 0.0)),
    ((0.03, 0.0), (0.05, 0.0), (0.06, 0.0), (0.0, 0.0)), ((0.16, 0.0), (0.05, 0.0), (0.2, 0.0), (0.06, 0.0)),
    ((0.52, 0.0), (0.05, 0.0), (0.35, 0.0), (0.47, 0.0)), ((0.0, 0.37), (0.05, 0.0), (0.2, 0.0), (0.47, 0.0)),
    ((0.32, 0.0), (0.05, 0.0), (0.06, 0.0), (0.06, 0.0)), ((0.16, 0.0), (0.05, 0.0), (0.03, 0.0), (0.0, 0.0)),
    ((0.03, 0.0), (0.05, 0.0), (0.03, 0.0), (0.0, 0.0)), ((0.0, 0.0), (0.05, 0.0), (0.03, 0.0), (0.0, 0.0)),
]
NB = 20
SMASHED = np.array([46, 46, 52.])


class Shifted:
    """the render as plugmat sees it: moved into plug's own frame, TS's way round, no plugs."""
    def __init__(self, r):
        self._r = r
        self.x = r.x - M.OFF[0]
        self.y = r.y - M.OFF[1]
        mk = dict(r.mk)
        mk['layout'] = 'ts'
        mk['plugs'] = (None, None)
        self.mk = mk

    def __getattr__(self, k):
        return getattr(self._r, k)


EAGLE_EAST = (14.0, 95.0, 24.0)     # the emblem's centre (y, z) and radius on the console's east face, model units
EAGLE_SOUTH = (-146.5, 32.0, 27.0)  # its centre (x, z) and radius on the tower's south wall
EAGLEC = np.array([92.0, 70.0, 44.0])


def _eagle(u, v):
    """The emblem's coverage (0..1) at (u, v) in -1..1 across its circle, sampled bilinearly from gdi_eagle.png."""
    from PIL import Image
    if not hasattr(_eagle, 'img'):
        here = os.path.dirname(os.path.abspath(__file__))
        _eagle.img = np.asarray(Image.open(os.path.join(here, 'gdi_eagle.png')).convert('L'), np.float32) / 255
    img = _eagle.img
    n = img.shape[0]
    sx, sy = (u * 0.5 + 0.5) * (n - 1), (v * 0.5 + 0.5) * (n - 1)
    inside = (sx >= 0) & (sx <= n - 1) & (sy >= 0) & (sy <= n - 1)
    x0 = np.clip(np.floor(sx).astype(int), 0, n - 2)
    y0 = np.clip(np.floor(sy).astype(int), 0, n - 2)
    fx, fy = np.clip(sx - x0, 0, 1), np.clip(sy - y0, 0, 1)
    val = (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x0 + 1] * fx * (1 - fy)
           + img[y0 + 1, x0] * (1 - fx) * fy + img[y0 + 1, x0 + 1] * fx * fy)
    return np.where(inside, val, 0.0)


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


def materials(r, p=None, occ=None, level=0, lightsB=None, **kw):
    p = M.P if p is None else p
    level = max(int(level), int(r.mk.get('dmg_level', 0) or 0))
    alb, (bx, by, bz), emit = PM.materials(Shifted(r), p=p['plug'], occ=occ, level=level)
    x, y = M.to_local(r.x, r.y, r.mk.get('layout', 'ts'))
    z, comp = r.z, r.comp
    nx, ny, nz = r.nx, r.ny, r.nz
    top = nz > 0.75
    fine = sample(NOISE_FINE, np.where(top, x, x + y), np.where(top, y, z))
    mott = sample(NOISE_MOTTLE, np.where(top, x, x + y) * 0.7 + 31, np.where(top, y, z) * 0.7 + 17)
    grain = fine * 0.035 + mott * 0.05
    g1 = (1 + grain)[..., None]
    house = GREEN * (1 + 1.1 * grain)[..., None]
    grime = smoothstep(0.15, 1.3, sample(NOISE_GRIME, x * 0.7 + 7, (y + z) * 0.7 + 3))
    low = smoothstep(30.0, 2.0, z)

    def put(mask, col):
        nonlocal alb
        alb = np.where(mask[..., None], col, alb)

    g = dict(M.DONE); g.update(r.mk.get('prog') or {})
    deck = (comp == PL.PLAT) & top
    # ---- the landing pad plate: rim, tan lines, the centre square, seams; B's strips on the rim
    pdm = comp == M.PADP
    pm, along = M.pad_marks(x, y, p)
    pc = PADC * (1 + grain * 1.6)[..., None] * (1 - 0.18 * smoothstep(0.4, 1.0, grime))[..., None]
    put(pdm, pc)
    put(pdm & (pm == 4), PADSEAM * g1)
    put(pdm & (pm == 5), PADC * 0.86 * g1)
    put(pdm & (pm == 2), PADLINE * g1)
    put(pdm & (pm == 3), PADSQ * g1)
    put(pdm & (pm == 1), mix(PADRIM * g1, PADC * g1, 0.25 * grime))
    bars = pdm & (pm >= 10)
    put(bars, BARC * g1)
    smashed = np.zeros(x.shape, bool)
    if level >= 1:                                      # GTDROP_B's damaged half: the north strip's west half gone,
        smashed = bars & (((pm == 11) & (along < 0.45)) | ((pm == 13) & (along > 0.33)))   # the south a stub
        put(smashed, SMASHED * g1)
    if lightsB is not None:
        lv = B_LEVELS[int(lightsB) % NB + NB * (1 if level >= 1 else 0)]
        for k in range(4):
            m = bars & (pm == 10 + k) & ~smashed
            white, hfrac = lv[k]
            if white > 0:
                put(m, mix(BARC * g1, BAR_ON, white))
                emit = np.where(m[..., None], emit + BAR_ON * 0.55 * white, emit)
            if hfrac > 0:
                hm = m & (along <= hfrac)
                put(hm, house)
                emit = np.where(hm[..., None], emit + np.array([0, 90, 0.]), emit)
    # ---- tan dirt on the deck (TS: tan along the slope's foot, round the pad and the deck's edges), grime round the
    # guard's slot
    sl_ = p['plug']['slope']
    yfoot = sl_['foot'] + M.OFF[1]
    near_slope = smoothstep(26.0, 6.0, np.abs(y - yfoot - 8.0)) * (x > -40)
    dmask = smoothstep(0.25, 0.85, sample(NOISE_MOTTLE, x * 0.6 + 13, y * 0.6 + 41))
    _, dpad, _, _ = M.pad_shape(x, y, p)
    near_pad = smoothstep(-16.0, -2.0, dpad) * smoothstep(1.0, -1.0, dpad)
    gd = p['guard']
    sx0, sx1, sy0, sy1, _ = gd['slot']
    dslot = np.maximum(np.maximum(sx0 - x, x - sx1), np.maximum(sy0 - y, y - sy1))
    near_slot = smoothstep(14.0, 0.0, dslot) * (dslot > 0)
    dd = np.clip(0.7 * near_slope * (0.5 + 0.5 * dmask) + 0.35 * dmask * (x > 140) + 0.45 * near_pad * dmask, 0, 0.85)
    put(deck, mix(alb, DIRTC * g1, dd))
    put(deck, mix(alb, PM.DIRT * g1, 0.45 * near_slot * (0.4 + 0.6 * grime)))
    # ---- the jet blast guard: dark streaky metal, ribs / end plates / cap lighter; the slot near black
    streak = 0.5 + 0.5 * sample(NOISE_MOTTLE, y * 0.08 + 5.0, z * 0.9 + x * 0.9 + 3.0)
    gm = comp == M.GUARD
    put(gm, GUARDC * (0.86 + 0.24 * streak)[..., None] * g1)
    put(comp == M.GRIB, GRIBC * (0.9 + 0.15 * streak)[..., None] * g1)
    put(comp == M.GSLOT, GSLOTC * g1)
    # ---- the ramp: dark blue-grey plate, lighter rails and hinge beam, house-green hazard stripes
    put(comp == M.RAMP2, mix(RAMPF * g1, PM.DIRT * g1, 0.22 * low * grime))
    put(comp == M.RAMPR, mix(RAMPR_C * g1, PM.DIRT * g1, 0.18 * grime))
    bp = float(g['bpaint'])
    bare = np.array([196, 194, 168.]) * g1 if bp < 0.5 else np.array([110, 110, 108.]) * g1
    put(comp == M.RAMPS, house if bp >= 1 else bare)
    # ---- the tower: tan plaster panels with grime; TS's blue-grey band under the eaves; the console face in larger
    # panels; the raised blocks; the vent; the house-green gable face and lean-to; the pipe
    w = p['west']
    wall = comp == M.WBODY
    seam = (phase(x + y, 44.0, 0.0) < 0.9) | (np.abs(z - 47.0) < 0.6)
    blot = smoothstep(0.55, 0.95, sample(NOISE_MOTTLE, x * 1.6 + y * 0.4 + 3.0, z * 1.6 + y * 0.9 + 9.0))
    wc = mix(WALLC * g1, WALLD * g1, 0.4 * grime + 0.3 * low + 0.35 * blot)
    wc = np.where(seam[..., None], WALLSEAM * g1, wc)
    put(wall, wc)
    band = wall & (z > w['z']) & (z <= w['z'] + w['trim'] + 0.5)
    dash = phase(x + y, 10.0, 0.0) < 2.5
    put(band, np.where(dash[..., None], TRIMD * g1, TRIMC * g1))
    roof = comp == M.WCROWN
    rstreak = smoothstep(0.35, 0.85, sample(NOISE_MOTTLE, y * 0.06 + 3.0, x * 0.85 + 11.0))
    rc = mix(ROOFC * g1, PM.ROOFRED * g1, 0.06 * rstreak)
    rblot = smoothstep(0.5, 0.95, sample(NOISE_MOTTLE, x * 1.3 + 17.0, y * 1.3 + z * 0.6 + 5.0))
    rc = mix(rc, WALLD * g1, 0.35 * smoothstep(0.45, 1.1, grime) + 0.3 * rblot)
    # big panels: seams across every 32 units of y, one along the face part-way up
    rseam = (phase(y - w['y'][0] - 5.0, 32.0, 0.0) < 0.9) | (np.abs(z - 104.0) < 0.6)
    rc = np.where(rseam[..., None], PM.TAN_D * g1, rc)
    put(roof, rc)
    tb = comp == M.TOPB
    put(tb, mix(ROOFC * 1.04 * g1, WALLD * g1, 0.3 * smoothstep(0.5, 1.1, grime)))
    vm = comp == M.VENT
    slat = phase(z, 3.4, 0.0) < 1.5
    put(vm, np.where(slat[..., None], VENTC * 1.9 * g1, VENTC * g1))
    put(comp == M.WROOFG, house if bp >= 1 else bare)
    put(comp == M.PIPEW, STEELC * g1)
    # ---- TS GDI's eagle (gdi_eagle.png) painted on the tower, as the concept art has GDI's emblem there:
    # GDROP_EAGLE=east on the console's sloped east face, south on the tower's south wall, none for none
    face = os.environ.get('GDROP_EAGLE', 'east')
    if face != 'none':
        if face == 'east':
            xc = 0.5 * (w['x'][0] + w['x'][1])
            em = (comp == M.WCROWN) & (x > xc + 2.0)
            u, v = -(y - EAGLE_EAST[0]) / EAGLE_EAST[2], -(z - EAGLE_EAST[1]) / EAGLE_EAST[2]
        else:
            em = (comp == M.WBODY) & (y > w['y'][1] - 1.5) & (z < w['z'] - 1.0)
            u, v = (x - EAGLE_SOUTH[0]) / EAGLE_SOUTH[2], -(z - EAGLE_SOUTH[1]) / EAGLE_SOUTH[2]
        cov = np.where(em, _eagle(u, v), 0.0)
        alb = mix(alb, EAGLEC * g1, cov * 0.85)
    # ---- TS's grey slope in the notch: concrete with tan dirt
    nwm = comp == M.NWALL
    dirt = smoothstep(0.3, 0.9, sample(NOISE_MOTTLE, x * 0.9 + 21, (y + z) * 0.9 + 5))
    nseam = (phase(x + 2.0, 23.0, 0.0) < 0.8) | (phase(y, 40.0, 0.0) < 0.8)
    put(nwm, np.where(nseam[..., None], NWALLC * 0.72 * g1, mix(NWALLC * g1, DIRTC * g1, 0.55 * dirt)))
    # ---- the ledge and its column, the bay's antennas
    put(comp == M.RAIL, mix(PM.STEPC * g1, PM.DIRT * g1, 0.3 * grime))
    put(comp == M.COLW, mix(PM.STEPC * 0.92 * g1, PM.DIRT * g1, 0.35 * grime + 0.3 * low))
    put(comp == M.ANT2, PM.ANTC * g1)
    return alb, (bx, by, bz), emit


def trim_mask(r, alb):
    """the house parts where they are green, and B's light strips where they flash house colour (on the pad plate:
    nothing else on it is green)."""
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & (np.isin(r.comp, list(M.HOUSE)) | (r.comp == M.PADP))
