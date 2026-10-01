"""Materials for the Tech Center: albedo, bump and glow per pixel of an hd.Render.  House green 0,214,0 x
(1 + 1.1 grain) on the dome's panels and the fins, as on every building.  Everything is textured in the
building's own frame (tech.to_local), so it turns with the layout."""
import numpy as np
import walls2 as W
from walls2 import sample, smoothstep, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME
import tech as TC

GREEN = np.array([0, 214, 0.])
CONC = np.array([218, 212, 194.])
SAND = np.array([200, 174, 116.])
BROWN = np.array([128, 100, 66.])
STEEL = np.array([150, 152, 160.])
STEEL_D = np.array([82, 82, 88.])
STRUT_C = np.array([120, 78, 46.])
DARK = np.array([26, 28, 30.])
# GTTECH_A, healthy: the whole dome brightens and fades back, all its panels together (TS: +0, 10, 17, 20, 22,
# 20, 17, 10 on the green)
PULSE = (0.0, 0.46, 0.77, 0.92, 1.0, 0.92, 0.77, 0.46)


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


def layout_of(r):
    return r.mk.get('layout', 'ts')


def materials(r, p=TC.P, occ=None, pulse=None, sparks=None):
    """pulse: frame 0..7 of GTTECH_A's healthy pulse (the dome's panels glow up and fade together); sparks: frame
    0..7 of its damaged frames (sparks in the smashed panels, the rest flickering)."""
    lay = layout_of(r)
    L = TC.LAYOUTS[lay]
    x, y = TC.to_local(r.x, r.y, lay)
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
    put(comp == TC.SLAB, CONC * 0.92 * g1)
    # the terraces: louvred bands on the sides (sand over brown, dark slats, grey edges), grey treads on top
    band = comp == TC.BAND
    side = band & ~top
    k = np.floor(z / 10.0)
    bc = np.where((k % 2 == 0)[..., None], SAND * g1, BROWN * g1)
    slat = phase(z, 2.6, 0.0) < 0.9
    bc = bc * (1 - 0.3 * slat)[..., None]
    edge = phase(z, 10.0, 0.0) < 1.2
    bc = np.where(edge[..., None], STEEL * g1, bc)
    put(side, bc)
    put(band & top, STEEL * 0.92 * g1)
    bz += 0.3 * (slat.astype(np.float32) - 0.3) * side
    # the east face's grille: a dark recess behind the struts; its batter plain grey
    e = p['east']
    gy0, gy1 = L['east']['grille']
    xe = max(px for (px, py) in L['poly'])
    recess = side & (x > xe - 22.0) & (y > gy0) & (y < gy1) & (z < e['z'] + 2.0)
    put(recess, DARK * g1)
    bat = comp == TC.LOUVRE
    put(bat, STEEL * 0.88 * g1 * (1 - 0.08 * (phase(z, 11.0, 0.0) < 0.9))[..., None])
    # the roof: sand, panel seams; the parapet grey
    roof = comp == TC.ROOF
    rseam = (phase(x, 32.0, 0.0) < 0.6) | (phase(y, 32.0, 9.0) < 0.6)
    stain = smoothstep(0.5, 1.4, sample(NOISE_GRIME, x * 0.4 + 9, y * 0.4)) * 0.25
    rc = mix(SAND * g1 * (1 - 0.12 * rseam)[..., None], np.array([150, 130, 86.]), stain)
    put(roof, rc)
    put(comp == TC.PARAPET, STEEL * g1)
    # the east framework
    put(comp == TC.FRAME, STEEL * g1 * (1 - 0.15 * (phase(z, 8.0, 0.0) < 0.8))[..., None])
    put(comp == TC.BASE, STEEL_D * g1)
    # the dome: green panels in brown struts
    dome = comp == TC.DOME
    strut, pid, az, el = TC.dome_lattice(x, y, z, L, p)
    pshade = 1 + 0.06 * np.sin(pid * 1.7)
    paint = r.field('panels', 1.0)
    pc = house * pshade[..., None]
    if pulse is not None:
        q = PULSE[pulse % len(PULSE)]
        pc = pc * (1 + 0.32 * q)
        emit = np.where((dome & ~strut)[..., None], np.array([0, 38, 0.]) * q, emit)
    put(dome, np.where(strut[..., None], STRUT_C * g1, pc))
    r.dome_strut = dome & strut
    r.dome_pid = pid
    r.dome_panel = dome & ~strut
    put(comp == TC.STRUT, STRUT_C * g1)
    # the fins: house colour, ribbed: ribs sloping down from the middle to both sides (chevrons, like TS's
    # banding), a rim along the outline, the ribs a shade darker
    fin = comp == TC.FIN
    a = TC.arch_dims(L, p)
    fshade = np.ones(shape, np.float32)
    for (cxy, d, e_) in L['arches']:
        sa_, _ = TC.arch_coords(x, y, cxy, d)
        nn = (x - cxy[0]) * e_[0] + (y - cxy[1]) * e_[1]
        mine = fin & (np.abs(sa_) <= a['span'] / 2 + 2) & (np.abs(nn) <= a['t'])
        if not mine.any():
            continue
        xx = np.abs(sa_)
        rib = phase(z + 0.55 * xx, a['rib'], 0.0) < 2.4
        rim = (TC.fin_top(xx, a) - z) < 5.0
        fshade = np.where(mine, np.where(rim, 0.95, np.where(rib, 0.7, 0.88)), fshade)
        bz += 0.35 * (rib & mine & ~rim).astype(np.float32)
    put(fin, house * fshade[..., None])
    r.sparks = sparks
    r.pulse = pulse
    return alb, (bx, by, bz), emit


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, list(TC.HOUSE))
