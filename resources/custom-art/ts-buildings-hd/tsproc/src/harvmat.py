"""Materials for the TS Harvester (harv.py): albedo, bump and glow per pixel of an hd.Render.  House green 0,214,0
x (1 + 1.1 grain) on the cab and the tank's back posts, as on every building.  Textured in the truck's own voxel frame
(scene.extra lx, ly), so the detail turns with it.  Colours read from HARV.VXL / HORV.VXL with UNITTEM.PAL (base
colours, before TS's voxel lighting): light grey frames (TS 150-186), a dark top and let-in side panels on the tank
(TS 44-100), mid-grey hoops (129), dark olive tyres, engine block and underside (80, 72, 56), grey hubs, a black
windscreen, a pale roof panel."""
import numpy as np
import walls2 as W
from walls2 import sample, smoothstep, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME
import harv as HV

GREEN = np.array([0, 214, 0.])
STEEL = np.array([172, 174, 178.])          # frames, the wall, the neck, hoops (a touch darker)
STEEL_L = np.array([204, 206, 210.])        # the light frame band, the door, claws
STEEL_D = np.array([84, 85, 90.])           # the tank's top and let-in panels
OLIVE = np.array([88, 79, 61.])             # tyres, the engine block
UNDER = np.array([108, 108, 113.])          # the hull's underside behind the wheels: lighter than the tyres
HUBC = np.array([152, 152, 154.])
GLASSC = np.array([16, 18, 21.])
ROOFC = np.array([200, 200, 204.])
GRIME = np.array([112, 104, 78.])
FILL = 0.32
TANK_FAMILY = (HV.TANK, HV.TFRAME, HV.HOOP, HV.DOOR, HV.REAR)


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


def materials(r, p=HV.P, occ=None, **kw):
    lx = r.field('lx'); ly = r.field('ly')
    s = r.mk.get('s', HV.S)
    z = r.z / s                                       # voxel units
    comp = r.comp
    lid = comp >= HV.LID_BASE                         # the tank sliding off HORV: textured where it has got to
    if lid.any():
        lx = np.where(lid, r.field('tlx'), lx)
    nz = r.nz
    top = nz > 0.75
    u, v = lx * 9.0, np.where(top, ly * 9.0, z * 9.0)
    fine = sample(NOISE_FINE, u, v)
    mott = sample(NOISE_MOTTLE, u * 0.7 + 31, v * 0.7 + 17)
    grain = fine * 0.035 + mott * 0.05
    g1 = (1 + grain)[..., None]
    shape = lx.shape
    alb = np.zeros(shape + (3,), np.float32)
    bx = np.zeros(shape, np.float32); by = np.zeros(shape, np.float32); bz = np.zeros(shape, np.float32)
    emit = np.zeros(shape + (3,), np.float32)

    def put(mask, col):
        nonlocal alb
        alb = np.where(mask[..., None], col, alb)

    house = GREEN * (1 + 1.1 * grain)[..., None]
    dirt = smoothstep(4.5, 0.5, z) * 0.45                 # dust up the lower sides
    under = (~top) & (z < 7.0)                            # the underside between the wheels
    # tyres: dark olive, tread across their rolling face; grey hubs on their flat faces with a dark centre
    tyre = comp == HV.TYRE
    wxs = np.array(p['wheels'])
    wx = wxs[np.argmin(np.abs(lx[..., None] - wxs), axis=-1)]
    wr = p['wheel_r']
    wd = np.hypot(lx - wx, z - wr)
    face = tyre & (r.surface == 3)
    tread = phase(np.arctan2(z - wr, lx - wx) * 6.0, 1.0, 0.0) < 0.35
    put(tyre, OLIVE * 0.95 * g1 * (1 - 0.25 * (tread & ~face))[..., None])
    hubf = face & (wd < 0.58 * wr)
    put(hubf, HUBC * g1 * (1 - 0.45 * (wd < 0.2 * wr) - 0.18 * (np.abs(wd - 0.42 * wr) < 0.1))[..., None])
    put(comp == HV.FRAME, UNDER * 0.9 * g1)
    # the front: the scoop plate (grey, ribbed across), the claws
    sc = comp == HV.SCOOP
    put(sc, mix(STEEL * g1 * (1 - 0.15 * (phase(ly, 2.5, 0.0) < 0.4))[..., None], GRIME, dirt * 0.6))
    put(comp == HV.CLAW, STEEL_L * g1)
    # the tank (HARV's own, and the tank sliding off HORV)
    alb, bz = tank_colours(alb, bz, comp, lx, ly, z, top, g1, dirt, p)
    if lid.any():
        alb, bz = tank_colours(alb, bz, comp, lx, ly, z, top, g1, dirt, p, base=HV.LID_BASE, house=house)
    alb = np.where((comp == HV.REAR)[..., None], house, alb)
    put(comp == HV.WALL, mix(STEEL * g1, UNDER, under.astype(np.float32)))
    put(comp == HV.NECK, mix(STEEL * 1.04 * g1, UNDER, under.astype(np.float32)))
    put(comp == HV.ENGINE, OLIVE * 1.08 * g1 * (1 - 0.16 * (phase(lx, 1.6, 0.0) < 0.5) * top)[..., None])
    # the cab: house colour, panel seams; the windscreen across its sloping front and round the front corners,
    # small side windows; a pale panel on the roof; below it at the front the scoop's grey, the underside olive
    cab = comp == HV.CAB
    c = p['cab']; g = p['glass']
    seam = cab & ((phase(lx, 5.2, 1.0) < 0.22) | (np.abs(z - 9.4) < 0.18) & ~top)
    put(cab, house * (1 - 0.12 * seam)[..., None])
    screen = cab & (lx >= g['x']) & (z >= g['z'][0]) & (z < g['z'][1])
    corner = cab & ~top & (lx >= c['x'][1] - 3.0) & (z >= g['z'][0]) & (z < g['z'][1] - 0.6) & \
        ((ly < c['y'][0] + 0.6) | (ly > c['y'][1] - 0.6) | (lx >= c['nose'][0]))
    side_win = cab & ~top & (lx >= g['side_x'][0]) & (lx < g['side_x'][1]) & (z >= g['side_z'][0]) & (z < g['side_z'][1])
    glass = screen | corner | side_win
    put(glass, GLASSC * g1)
    emit = np.where(glass[..., None], np.array([34, 44, 52.]) * smoothstep(9.0, 12.5, z)[..., None], emit)
    rf = p['roof']
    roof = cab & top & (lx >= rf['x'][0]) & (lx < rf['x'][1]) & (ly >= rf['y'][0]) & (ly < rf['strip'][1])
    put(roof, np.where((ly >= rf['strip'][0])[..., None], STEEL_D * g1, ROOFC * g1))
    put(cab & ~top & (lx >= c['x'][1] - 0.6) & (z < 5.0), STEEL * g1)
    put(cab & under & (z >= 5.0) | cab & ~top & (z < 5.0) & (lx < c['x'][1] - 0.6), UNDER * g1)
    # HORV's bed: a tread plate, a dark seam across it, the tailgate darker; its sides the tank's frame band
    bed = comp == HV.BED
    b = p['bed']
    tp = (phase(lx + ly, 1.4, 0.0) < 0.25) | (phase(lx - ly, 1.4, 0.0) < 0.25)
    bseam = (lx >= b['seam'][0]) & (lx < b['seam'][1])
    tail = lx < b['tail'][1]
    put(bed & top, STEEL_L * 0.94 * g1 * (1 - 0.08 * tp - 0.42 * bseam - 0.2 * tail)[..., None])
    bside = bed & ~top
    if bside.any():
        a2, b2 = tank_colours(alb, bz, np.where(bside, HV.TFRAME, 0), lx, ly, z, top, g1, dirt, p)
        alb = np.where(bside[..., None], a2, alb); bz = np.where(bside, b2, bz)
    # a fill light from the camera on the sides that face it, as EA's HD units have (the key light alone, from the
    # north-west, leaves a unit's camera-facing side in shade); the docked truck in the refinery's scene gets it too
    vw = r.view
    tc = np.array([vw.T[0] * vw.cE, vw.T[1] * vw.cE, vw.sE])
    nf = np.clip(r.nx * tc[0] + r.ny * tc[1] + r.nz * tc[2], 0, 1) * (1 - np.clip(r.nz, 0, 1))
    if occ is not None:
        nf = nf * (1 - 0.85 * np.clip(occ, 0, 1))                       # less where the sky is hidden (in the dock)
    emit = emit + alb * (FILL * nf)[..., None]
    r.glass = glass
    return alb, (bx, by, bz), emit


def tank_colours(alb, bz, comp, lx, ly, z, top, g1, dirt, p=HV.P, base=0, house=None):
    """the tank's colours (HARV's; the refinery's lid; HORV's bed sides as its frame band): comp ids offset by
    `base`.  Its top dark between the hoops, the side panels let in dark (two lighter rows across them, as TS's),
    the frames light, the hoops mid grey, the door pale; the underside the hull's grey."""
    t = p['tank']
    under = (~top) & (z < 7.0)
    core = comp == base + HV.TANK
    frame = comp == base + HV.TFRAME
    # the core: its top dark (mottled), its let-in side panels dark with two lighter rows, its back face the door
    rows = ((z >= 12.0) & (z < 13.0)) | ((z >= 14.0) & (z < 15.0))
    door = core & ~top & (lx < t['x'][0] + t['door_x'] + 0.45)
    panel = core & ~top & ~door
    hi = core & ~top & (z >= t['side_top'])                          # above the frames: the bevel's sides
    tc = np.where(top[..., None], STEEL_D * g1,
                  np.where(rows[..., None], STEEL_D * 1.32 * g1, STEEL_D * 0.92 * g1))
    tc = np.where(hi[..., None], STEEL * 0.85 * g1, tc)
    tc = np.where(door[..., None], STEEL_L * g1 * (1 - 0.14 * (phase(ly, 3.0, 0.0) < 0.35))[..., None], tc)
    alb = np.where(core[..., None], tc, alb)
    bz = bz - 0.35 * (panel & rows)
    # the frames: light, the underside behind the wheels the hull's lighter grey (the tyres stand out against it),
    # dust at the bottom
    fc = mix(STEEL_L * g1, GRIME, dirt)
    alb = np.where(frame[..., None], np.where(under[..., None], UNDER * 0.9 * g1, fc), alb)
    alb = np.where((comp == base + HV.HOOP)[..., None], STEEL * g1, alb)
    alb = np.where((comp == base + HV.DOOR)[..., None], STEEL * g1, alb)          # the sill
    if house is not None:
        alb = np.where((comp == base + HV.REAR)[..., None], house, alb)
    return alb, bz


def trim_mask(r, alb):
    gmask = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    house = np.isin(r.comp, list(HV.HOUSE)) | np.isin(r.comp - HV.LID_BASE, list(HV.HOUSE))
    return r.hitmask & gmask & house
