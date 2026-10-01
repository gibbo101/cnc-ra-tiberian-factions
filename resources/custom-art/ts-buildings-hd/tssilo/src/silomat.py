"""Materials for the Tiberium Silo: albedo, bump and glow per pixel of an hd.Render.  House green 0,214,0 x
(1 + 1.1 grain) as on every building; the lid TS's blue-grey glass panels; the stored Tiberium is natural
Tiberium green (not house colour: kept out of the trim)."""
import numpy as np
import walls2 as W
from walls2 import sample, smoothstep, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME
import silo as SL

GREEN = np.array([0, 214, 0.])
LID_C = np.array([140, 146, 178.])
STEEL = np.array([150, 152, 160.])
STEEL_D = np.array([70, 70, 76.])
EARTH_D = np.array([96, 82, 62.])
TIB = np.array([92, 196, 64.])
TIB_D = np.array([36, 104, 34.])
TIB_GLINT = np.array([196, 255, 170.])


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


def materials(r, p=SL.P, occ=None, fill=0.0, lights=None):
    """fill: 0..1, the stored Tiberium (GTSILO_A); lights: 0..1 per fin-tip lamp, or (r, g, b) per lamp (GTSILO_B)."""
    p = SL.geo(r.mk.get('layout', 'ts'), p)
    x, y, z, comp = r.x, r.y, r.z, r.comp
    nx, ny, nz = r.nx, r.ny, r.nz
    top = nz > 0.75
    cx, cy = p['centre']
    d = np.hypot(x - cx, y - cy)
    az = np.arctan2(y - cy, x - cx)
    u = np.where(top, x, az * 50.0)
    v = np.where(top, y, z)
    fine = sample(NOISE_FINE, u, v)
    mott = sample(NOISE_MOTTLE, u * 0.7 + 31, v * 0.7 + 17)
    grain = fine * 0.035 + mott * 0.05
    g1 = (1 + grain)[..., None]
    shape = x.shape
    alb = np.zeros(shape + (3,), np.float32)
    bx = np.zeros(shape, np.float32); by = np.zeros(shape, np.float32); bz = np.zeros(shape, np.float32)
    emit = np.zeros(shape + (3,), np.float32)
    tib = np.zeros(shape, bool)

    def put(mask, col):
        nonlocal alb
        alb = np.where(mask[..., None], col, alb)

    house = GREEN * (1 + 1.1 * grain)[..., None]
    # dark earth ring round the foot
    soil = comp == SL.SLAB
    sn = sample(NOISE_GRIME, x * 0.6 + 5, y * 0.6)
    put(soil, EARTH_D * g1 * (1 + 0.12 * sn)[..., None])
    # the skirt: dark ribbed metal
    sk = comp == SL.SKIRT
    rib = phase(az * 45.0, 6.0, 0.0) < 1.0
    put(sk, STEEL_D * g1 * (1 - 0.22 * rib)[..., None])
    # the lid: glass panels in a dark frame (radial and ring seams), white glints; the rim band dark
    lid = comp == SL.LID
    R = p['lid_r']
    seam = (phase(az * R / (2 * np.pi) * 2 * np.pi / 12.0 * 12.0 / R * R, 2 * np.pi * R / 12.0, 0.0) < 1.2)
    ring = (np.abs(d - R * 0.42) < 0.9) | (np.abs(d - R * 0.74) < 0.9) | (d < 9.0) & (np.abs(d - 8.0) < 0.8)
    pan = np.floor(az / (2 * np.pi / 12.0)) + 13 * np.floor(d / (R * 0.37))
    shade_p = 1 + 0.07 * np.sin(pan * 2.7)
    lc = LID_C * g1 * shade_p[..., None]
    glint = top & (np.abs(np.sin(pan * 1.9)) > 0.86) & (d > R * 0.3) & (d < R * 0.9) & \
        (phase(az * R, 2 * np.pi * R / 12.0, 4.0) < 7.0) & (np.abs(d - R * (0.5 + 0.2 * np.sin(pan))) < 3.0)
    lc = np.where(glint[..., None], np.array([236, 238, 248.]), lc)
    lc = lc * (1 - 0.3 * (seam | ring))[..., None]
    # the stored Tiberium, seen through the glass: fills from the front (south) edge back
    if fill > 0:
        reach = (y - cy) / R                               # -1 at the back .. 1 at the front
        tib = lid & top & (reach > 1 - 2 * fill + 0.06 * np.sin(az * 7.0 + d * 0.3))
        tn = sample(NOISE_FINE, x * 1.6 + 3, y * 1.6)
        tc = mix(TIB_D, TIB, np.clip(0.55 + 0.6 * tn, 0, 1))
        glt = (sample(NOISE_FINE, x * 3.1 + 11, y * 3.1) > 0.62)
        tc = np.where(glt[..., None], TIB_GLINT, tc)
        tc = mix(tc, lc, 0.25) * (1 - 0.3 * (seam | ring))[..., None]
        lc = np.where(tib[..., None], tc, lc)
        emit = np.where(tib[..., None], np.array([10, 40, 6.]), emit)
    rimband = lid & ~top & (nz < 0.4)
    lc = np.where(rimband[..., None], STEEL_D * g1, lc)
    put(lid, lc)
    put(comp == SL.CAP, np.array([132, 132, 140.]) * g1)
    # the fins: house colour, a thin seam along the ridge
    fin = comp == SL.FIN
    put(fin, house)
    # the fin-tip lamps
    lamp = comp == SL.TIPLAMP
    put(lamp, np.array([186, 186, 192.]) * g1)
    lens = lamp & top
    r.lamp_px = lens
    if lights is not None:
        k = np.full(shape, -1)
        for i, a in enumerate(p['fins_az']):
            tip = SL.fin_tip(a, p)
            tx, ty = cx + tip * np.cos(a), cy + tip * np.sin(a)
            k = np.where(lens & (np.hypot(x - tx, y - ty) < 3.0), i, k)
        for i, col in enumerate(lights):
            if col is None:
                continue
            m = k == i
            alb = np.where(m[..., None], np.array([40, 40, 46.]), alb)
            emit = np.where(m[..., None], np.array(col, np.float32), emit)
    # the pump housing: grey slats; its pipe
    pump = comp == SL.PUMP
    slat = ~top & (phase(np.where(np.abs(nx) > np.abs(ny), y, x), 2.5, 0.0) < 0.8)
    put(pump, STEEL * g1 * (1 - 0.3 * slat)[..., None])
    put(comp == SL.PIPE, np.array([128, 128, 134.]) * g1 * (1 - 0.15 * (phase(z, 4.0, 0.0) < 0.6))[..., None])
    # the vent box: grey with diagonal stripes on its sides, a dark grate on top
    vent = comp == SL.VENT
    stripe = ~top & (phase(np.where(np.abs(nx) > np.abs(ny), y, x) + z, 5.0, 0.0) < 2.2)
    put(vent, STEEL * g1 * (1 - 0.45 * stripe)[..., None])
    put(comp == SL.GRATE, np.array([46, 46, 50.]) * g1 * (1 + 0.4 * (phase(x - y, 3.0, 0.0) < 1.0))[..., None])
    # grime at the foot
    gr = smoothstep(0.35, 1.2, sample(NOISE_GRIME, u, v)) * np.clip(1 - z / 14.0, 0, 1) * 0.3
    gr = gr * ~np.isin(comp, [SL.FIN, SL.LID])
    alb = mix(alb, np.array([92, 82, 64.]), gr)
    r.tib_px = tib
    return alb, (bx, by, bz), emit


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    tib = getattr(r, 'tib_px', None)
    if tib is not None:
        g &= ~tib
    # the blades, and their broken bits on the ground (damaged)
    return r.hitmask & g & np.isin(r.comp, list(SL.HOUSE) + [40, 42])
