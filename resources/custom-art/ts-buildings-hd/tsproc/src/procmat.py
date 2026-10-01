"""Materials for the Tiberium Refinery: albedo, bump and glow per pixel of an hd.Render.  House green 0,214,0 x
(1 + 1.1 grain) on the skirt's ribs and the deck's rim, as on every building.  Everything is textured in the
building's own frame (proc.to_local), so it turns with the layout.  Colours read from NTREFN: grey skirt plates,
a black deck, a copper cone and sphere, light steel stacks with dark collars, a gold gear ring, a rust wall in the
dock, black pipes."""
import numpy as np
import walls2 as W
from walls2 import sample, smoothstep, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME
import proc as PR
import harvmat as HMAT, harv as HV

GREEN = np.array([0, 214, 0.])
PLATE = np.array([114, 115, 120.])
PLATE_D = np.array([118, 119, 124.])
DECKC = np.array([44, 44, 46.])
COPPER = np.array([198, 128, 104.])
COPPER_D = np.array([120, 62, 44.])
COPPER_S = np.array([132, 74, 58.])
STEEL = np.array([196, 197, 202.])
STEEL_M = np.array([150, 152, 160.])
COLLAR = np.array([70, 70, 74.])
BLACK = np.array([30, 30, 32.])
GOLD = np.array([186, 156, 92.])
RUST = np.array([138, 64, 44.])
DARK = np.array([38, 36, 34.])
CAPC = np.array([232, 232, 228.])
PADC = np.array([214, 208, 190.])
DIRT = np.array([196, 164, 108.])
ORANGE = np.array([236, 150, 38.])
STRIPE_K = np.array([34, 32, 30.])
GRIME = np.array([112, 104, 78.])


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


def layout_of(r):
    return r.mk.get('layout', 'ts')


# NTREFN_C, the dock lamps (both together, 16-frame loop): how lit (0 dim .. 1), and the white flash at the peak
LAMP_LEVEL = (0.4, 1.0, 0.7, 0.58, 0.48, 0.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.4, 1.0, 0.7, 0.58, 0.48)
LAMP_FLASH = (0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0)


def materials(r, p=None, occ=None, lights=None, **kw):
    lay = layout_of(r)
    p = PR.params(lay, p)
    x, y = PR.to_local(r.x, r.y, lay)
    z, comp = r.z, r.comp
    nz = r.nz
    top = nz > 0.75
    fine = sample(NOISE_FINE, np.where(top, x, x + y), np.where(top, y, z))
    mott = sample(NOISE_MOTTLE, np.where(top, x, x + y) * 0.7 + 31, np.where(top, y, z) * 0.7 + 17)
    grain = fine * 0.035 + mott * 0.05
    g1 = (1 + grain)[..., None]
    shape = x.shape
    alb = np.zeros(shape + (3,), np.float32)
    bx = np.zeros(shape, np.float32); by = np.zeros(shape, np.float32); bz = np.zeros(shape, np.float32)
    emit = np.zeros(shape + (3,), np.float32)

    def put(mask, col):
        nonlocal alb
        alb = np.where(mask[..., None], col, alb)

    house = GREEN * (1 + 1.1 * grain)[..., None]
    cx, cy = p['c']
    dx, dy = x - cx, y - cy
    rr = np.hypot(dx, dy)
    phi = np.degrees(np.arctan2(dy, dx)) % 360.0
    step = 360.0 / p['ribs']
    # ---- the skirt: grey plates down the slope, seams across them every so often, grime rising from the foot
    sk = comp == PR.SKIRT
    seam = np.abs(rr - (p['deck_r'] + 44.0)) < 0.8
    k = np.floor(((phi - p['rib0']) % 360.0) / step)
    pshade = 1 + 0.035 * np.sin(k * 2.7 + 0.4)
    gr = smoothstep(26.0, 2.0, z) * (0.45 + 0.35 * smoothstep(-0.6, 1.2, sample(NOISE_GRIME, x * 0.5, y * 0.5)))
    sc = mix(PLATE * g1 * pshade[..., None] * (1 - 0.10 * seam)[..., None], GRIME, gr)
    put(sk, sc)
    bz -= 0.25 * seam * sk
    # ---- the ribs and the deck's rim: house green, a thin seam down the middle of each rib
    rib = comp == PR.RIB
    dang = ((phi - p['rib0'] + step / 2) % step) - step / 2
    across = np.radians(dang) * rr
    put(rib, house * (1 - 0.12 * (np.abs(across) < 0.5))[..., None])
    put(comp == PR.RIM, house)
    # ---- the deck: black, speckled, a ring of bolts in from the rim
    deck = comp == PR.DECK
    speck = smoothstep(1.2, 2.2, sample(NOISE_FINE, x * 1.7 + 5, y * 1.7))
    dc = DECKC * g1 * (1 + 0.5 * speck)[..., None]
    bolts = (np.abs(rr - (p['deck_r'] - 9.0)) < 1.6) & (phase(phi * np.radians(1) * (p['deck_r'] - 9.0), 9.0, 0.0) < 1.8)
    dc = np.where(bolts[..., None], DECKC * 2.2, dc)
    put(deck, dc)
    # ---- the flare stack: a copper cone (streaked), the light steel stack, dark collars; the housing grey
    st = p['stack']
    sdx, sdy = x - st['c'][0], y - st['c'][1]
    saz = np.arctan2(sdy, sdx)
    cone = comp == PR.CONE
    streak = 0.06 * np.sin(saz * 14.0) + 0.04 * sample(NOISE_MOTTLE, saz * 40.0, z * 0.6)
    put(cone, COPPER * (1 + streak)[..., None] * g1)
    stack = comp == PR.STACK
    band_s = (z > st['top'] - 9.0) & (z < st['top'] - 5.0)
    put(stack, np.where(band_s[..., None], COLLAR * g1, STEEL * g1 * (1 - 0.1 * (phase(z, 18.0, 3.0) < 0.9))[..., None]))
    fl = comp == PR.FLANGE
    # collars: steel bands with a dark lip top and bottom (TS's "#%.oo.=%#")
    edge = np.zeros(shape, bool)
    for (a_, b_) in list(st['collars']) + list(p['mid']['collars']):
        edge |= ((z - a_) < 1.4) & (z >= a_ - 0.5)
    put(fl, np.where(top[..., None], COLLAR * 1.6 * g1, np.where(edge[..., None], COLLAR * 0.7 * g1, COLLAR * g1)))
    put(comp == PR.PIPE, BLACK * g1)
    col_ = comp == PR.COLUMN
    tops = np.where(np.hypot(x - p['tall']['c'][0], y - p['tall']['c'][1]) < 20.0, p['tall']['top'], p['mid']['top'])
    band_c = (z > tops - 9.0) & (z < tops - 5.0)
    put(col_, np.where(band_c[..., None], COLLAR * g1, STEEL * g1 * (1 - 0.08 * (phase(z, 22.0, 5.0) < 0.9))[..., None]))
    put(comp == PR.WPIPE, STEEL * 0.95 * g1)
    # the open tops (TS's black holes): inside a light rim the pipe goes down into the dark; the far inside wall
    # just catches a little light, a crescent on the side away from the camera
    vt = r.view.T
    for (ccx, ccy, rad, ztop) in ((st['c'][0], st['c'][1], st['r'], st['top']), (cx, cy, p['mid']['r'], p['mid']['top']),
                                  (p['tall']['c'][0], p['tall']['c'][1], p['tall']['r'], p['tall']['top'])):
        rq = np.hypot(x - ccx, y - ccy)
        rin = rad - PR.RIM_W
        mouth = np.isin(comp, [PR.STACK, PR.COLUMN]) & top & (rq < rin) & (z > ztop - 200.0)   # open at any height (build-up)
        far = np.clip(-((x - ccx) * vt[0] + (y - ccy) * vt[1]) / rin, -1, 1)          # 1 at the far edge
        shade = 0.10 + 0.22 * smoothstep(0.25, 0.95, far) * (rq > 0.55 * rin)
        put(mouth, STEEL * shade[..., None] * g1)
    put(comp == PR.HOLE, np.array([16, 16, 18.]) * g1)
    # ---- the gold gear ring round the flanged column's foot
    put(comp == PR.GOLD, GOLD * g1)
    # ---- the dock: the rust wall, the dark back
    put(comp == PR.DOCKWALL, RUST * g1 * (1 - 0.15 * (phase(z, 12.0, 0.0) < 1.0))[..., None])
    put(comp == PR.DOCKIN, DARK * g1)
    # ---- the copper sphere (a soft highlight, as TS's) and its white cap
    sph = comp == PR.SPHERE
    put(sph, COPPER_S * g1)
    # TS's sphere has a strong pink-white highlight towards the light
    hl = np.clip(r.nx * r.view.L[0] + r.ny * r.view.L[1] + r.nz * r.view.L[2], 0, 1) ** 14
    emit = np.where(sph[..., None], np.array([170, 120, 104.]) * hl[..., None], emit)
    put(comp == PR.CAP, CAPC * g1)
    # ---- the dock lamps: house-green glass, lit per NTREFN_C's frame (a white-hot core at its flashes); housing dark
    put(comp == PR.LAMPBOX, COLLAR * g1)
    lamp = comp == PR.LAMP
    lv = LAMP_LEVEL[lights % 16] if lights is not None else LAMP_LEVEL[0]
    fl = LAMP_FLASH[lights % 16] if lights is not None else 0
    put(lamp, house * (0.42 + 0.3 * lv))
    emit = np.where(lamp[..., None], np.array([0, 150.0, 0]) * lv, emit)
    r.lamp_core = None
    if fl:
        emit = np.where(lamp[..., None], emit + np.array([170, 120, 170.]), emit)
        r.lamp_core = lamp.astype(np.float32)          # white-hot: not house colour at the flash
    r.lamp_lit = lv
    # ---- the docked harvester (in the scene) and its tank sliding off (the lid, NTREFN_A): exactly the harvester's
    #      own materials, in its own frame
    for (lo, hi, key, fx, fy) in ((PR.TRUCK_BASE, 10 ** 4, 'truck', 'truck_lx', 'truck_ly'),
                                  (PR.LID_BASE, PR.TRUCK_BASE, 'lid', 'lid_lx', 'lid_ly')):
        sub = (comp >= lo) & (comp < hi)
        if sub.any():
            ta, (tbx, tby, tbz), te = HMAT.materials(SubView(r, lo, hi, key, fx, fy), occ=occ)
            alb = np.where(sub[..., None], ta, alb)
            bx = np.where(sub, tbx, bx); by = np.where(sub, tby, by); bz = np.where(sub, tbz, bz)
            emit = np.where(sub[..., None], te, emit)
    # ---- the bib: cream concrete slabs, seams on a grid, tan dirt; the hazard band orange and black, worn
    pad = (comp == PR.PAD) | (comp == PR.STRIPE)
    if pad.any():
        seam = (phase(x, 64.0, 0.0) < 1.2) | (phase(y, 64.0, 0.0) < 1.2)
        crack = np.abs(sample(NOISE_GRIME, x * 0.9 + 3, y * 0.9 + 11)) < 0.035
        dirt = smoothstep(0.0, 1.4, sample(NOISE_MOTTLE, x * 0.8 + 50, y * 0.8 + 7)) * 0.7
        pc = mix(PADC * g1 * (1 - 0.06 * seam - 0.22 * crack)[..., None], DIRT, dirt)
        stp = (comp == PR.STRIPE)
        ph = PR.stripe_phase(x, y, p)
        orange = ph < 0.5
        wear = smoothstep(0.6, 1.5, sample(NOISE_FINE, x * 1.3, y * 1.3 + 9)) * 0.5
        sc = np.where(orange[..., None], ORANGE * g1, STRIPE_K * g1)
        sc = mix(sc, pc, wear)
        tex = r.field('padtex', 1.0)
        plain = np.array([168, 168, 166.]) * g1
        pc = mix(plain, pc, tex)
        sc = mix(np.where(orange[..., None], ORANGE * 0.8 * g1, STRIPE_K * g1), sc, np.clip(tex * 1.5, 0, 1))
        put(pad, np.where(stp[..., None], sc, pc))
        bz -= 0.3 * seam * pad * tex
    return alb, (bx, by, bz), emit


class SubView:
    """the render as the harvester's materials see it: its own component ids (those in lo..hi, less lo), its own
    frame (lx, ly from the fields fx, fy), its scale (r.mk[key]['s'])."""
    def __init__(self, r, lo, hi, key, fx, fy):
        self._r = r
        self.comp = np.where((r.comp >= lo) & (r.comp < hi), r.comp - lo, 0)
        self.mk = {'s': r.mk[key]['s']}
        self._f = {'lx': fx, 'ly': fy}

    def field(self, name, default=0.0):
        return self._r.field(self._f.get(name, name), default)

    def __getattr__(self, name):
        return getattr(self._r, name)


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    # house parts, plus the broken rib's piece and green rubble (procdamage: 40 rubble, 43 the rib's piece), and the
    # docked harvester's cab
    truck = (r.comp >= PR.TRUCK_BASE) & np.isin(r.comp - PR.TRUCK_BASE, list(HV.HOUSE))
    lid = (r.comp >= PR.LID_BASE) & (r.comp < PR.TRUCK_BASE) & np.isin(r.comp - PR.LID_BASE, list(HV.HOUSE))
    return r.hitmask & g & (np.isin(r.comp, list(PR.HOUSE)) | np.isin(r.comp, [40, 43]) | truck | lid)
