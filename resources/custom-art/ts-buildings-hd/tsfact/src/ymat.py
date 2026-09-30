"""Materials for the Construction Yard: albedo, bump and glow per pixel of an hd.Render.
Colours and noise follow walls2 / the component tower (concrete 226,226,222; house green 0,214,0;
steel 146,148,158; grime 112,104,78 rising from the base)."""
import numpy as np
import walls2 as W
from walls2 import sample, smoothstep, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME
import yard as Y

GREEN = np.array([0, 214, 0.])
CONC = W.CONCRETE
STEEL = np.array([146, 148, 158.])
DARK = np.array([74, 74, 78.])
PANEL_G = np.array([158, 156, 148.])
RUST = np.array([128, 96, 64.])
OCHRE = W.OCHRE
COPING = np.array([176, 166, 138.])
HAZ_Y = np.array([222, 180, 40.])
LAMP_C = np.array([255, 150, 36.])
GRILLE = np.array([0, 70, 0.])


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


def uv(r):
    top = r.nz > 0.75
    ns = np.abs(r.ny) >= np.abs(r.nx)
    u = np.where(top | ns, r.x, r.y)
    v = np.where(top, r.y, r.z)
    return u.astype(np.float32), v.astype(np.float32), top


def dots(a, b, pa, pb, rad, oa=0.0, ob=0.0):
    """a lattice of round dots (rivets/bolts) with periods pa, pb."""
    da = phase(a, pa, oa); db = phase(b, pb, ob)
    return 1 - smoothstep(rad * 0.6, rad, np.hypot(da, db))


def materials(r, p=Y.P, fan_angle=0.0, lamps=1.0, occ=None, lamp_levels=None, door=1.0, fan_on=(True, True, True)):
    """lamp_levels: brightness of each roof lamp, south to north (the _C chase); door: the door lamp;
    fan_on: which fans turn (a wrecked fan stays still)."""
    """returns albedo, (dnx, dny, dnz) bump, emissive colour."""
    x, y, z, comp = r.x, r.y, r.z, r.comp
    nx, ny, nz = r.nx, r.ny, r.nz
    u, v, top = uv(r)
    fine = sample(NOISE_FINE, u, v)
    mott = sample(NOISE_MOTTLE, u * 0.7 + 31, v * 0.7 + 17)
    grime_n = sample(NOISE_GRIME, u, v)
    grain = fine * 0.035 + mott * 0.05
    shape = x.shape
    alb = np.zeros(shape + (3,), np.float32)
    bx = np.zeros(shape, np.float32); by = np.zeros(shape, np.float32); bz = np.zeros(shape, np.float32)
    emit = np.zeros(shape + (3,), np.float32)
    g1 = (1 + grain)[..., None]

    def put(mask, col):
        nonlocal alb
        alb = np.where(mask[..., None], col, alb)

    yS, yN = p['yS'], p['yN']
    south_face = (ny > 0.6) & ~top
    east_face = (nx > 0.6) & ~top

    # ---------------------------------------------------------------- pad and kerb: concrete slabs
    pad = comp == Y.PAD
    joint = (phase(x, 64.0, 32.0) < 0.55) | (phase(y, 64.0, 32.0) < 0.55)
    stain = smoothstep(0.6, 1.6, sample(NOISE_GRIME, x * 0.5 + 40, y * 0.5)) * 0.18
    pc = CONC * 0.93 * g1 * (1 - 0.14 * joint)[..., None]
    pc = mix(pc, np.array([150, 140, 118.]), stain)
    # tyre marks and a hazard strip on the apron in front of the arch
    apron = (y > yS) & (x < p['x_open'] + 10) & (x > p['xw'])
    tyre = (apron & (phase(x + 3 * np.sin(y * 0.05), 46.0, 10) < 3.0)).astype(np.float32)
    pc = mix(pc, np.array([120, 118, 112.]), tyre * smoothstep(0.2, 1.2, sample(NOISE_MOTTLE, x, y * 0.3)) * 0.5)
    haz = (y > yS + 1) & (y < yS + 11) & (x > p['xw'] + 6) & (x < p['x_open'] - 2)
    stripe = phase(x - y, 20.0, 0.0) < 5.0
    pc = np.where((haz & stripe)[..., None], HAZ_Y * g1, np.where(haz[..., None], np.array([40, 40, 40.]) * g1, pc))
    put(pad, pc)
    kerb = comp == Y.KERB
    kc = np.where(top[..., None], COPING * 0.95 * g1, CONC * 0.8 * g1)
    put(kerb, kc)

    # ---------------------------------------------------------------- interior
    inside = comp == Y.INSIDE
    put(inside, CONC * 0.55 * g1 * (1 - 0.1 * joint)[..., None])
    put(comp == Y.NWALL, np.array([92, 94, 100.]) * g1)
    put(comp == Y.DOOR, np.array([44, 46, 50.]) * g1)

    # ---------------------------------------------------------------- green metal (house colour)
    greenish = np.isin(comp, [Y.RAIL, Y.RIB, Y.ROOF, Y.STACK, Y.BOOM, Y.CBASE, Y.CAB])
    gc = GREEN * (1 + 1.1 * grain)[..., None]
    put(greenish, gc)

    # ribs: rivet rows along both edges of the top
    rib = comp == Y.RIB
    drib, k, yk = Y.rib_index(y, p)
    rv = (1 - smoothstep(0.66, 1.1, phase(x, 10.0))) * (np.abs(np.abs(y - yk) - p['rib_w'] * 0.3) < 1.0) * top
    alb = np.where((rib & (rv > 0.5))[..., None], alb * 0.62, alb)
    # the east cladding: panel seams down the slope and across, rivets on the seams
    roof = (comp == Y.ROOF) & ~south_face
    seam_a = phase(y - yS, (yS - yN) / 6.0, 0.0) < 0.7                # seams at the rib lines, continued
    seam_b = phase(x, 26.0, 13.0) < 0.6
    rv2 = (1 - smoothstep(0.5, 0.9, phase(x, 8.0))) * (np.abs(phase(y - yS, (yS - yN) / 6.0) - 1.8) < 0.7)
    alb = np.where((roof & (seam_a | seam_b))[..., None], alb * 0.72, alb)
    alb = np.where((roof & (rv2 > 0.5))[..., None], alb * 0.66, alb)

    # ---------------------------------------------------------------- grey panels of the west half
    drib_, _, _ = Y.rib_index(y, p)
    panel = (comp == Y.PANEL) | ((comp == Y.ROOF) & (x < p['xc'] - 1.5) & (drib_ > p['rib_w'] / 2) & ~south_face & (nz > 0.2))
    cor = np.sin(y * 2 * np.pi / 4.0)
    pcol = PANEL_G * g1
    rust = smoothstep(0.5, 1.3, sample(NOISE_GRIME, x * 0.35 + 7, y * 1.2)) * 0.55
    band = np.exp(-((phase(y - yk, (yS - yN) / 6.0, (yS - yN) / 12.0)) / 4.0) ** 2) * 0.35
    pcol = mix(pcol, RUST * g1, np.clip(rust + band, 0, 0.8))
    put(panel, pcol)
    bmask = panel.astype(np.float32)
    by += 0.22 * cor * bmask

    # ---------------------------------------------------------------- south wall: grey ribbed cladding
    sw = (comp == Y.ROOF) & south_face & (z < p['crown'] - 6)
    swc = np.array([188, 188, 184.]) * g1
    rb = np.sin(x * 2 * np.pi / 7.0)
    swc = swc * (1 - 0.08 * (rb > 0.6))[..., None]
    swc = mix(swc, W.GRIME, np.clip(1 - (z - p['pad_h']) / 22.0, 0, 1) ** 1.5 * 0.5)
    put(sw, swc)
    bx += 0.28 * rb * sw.astype(np.float32)
    # door frame
    dx0, dx1, dh = p['door']
    frame = sw & ((((np.abs(x - dx0) < 2.2) | (np.abs(x - dx1) < 2.2)) & (z < dh + 2)) | ((np.abs(z - dh) < 2.2) & (x > dx0 - 2) & (x < dx1 + 2)))
    put(frame, np.array([96, 98, 104.]) * g1)
    door_band = sw & (np.abs(z - dh - 6) < 3) & (x > dx0 - 2) & (x < dx1 + 2)
    put(door_band & (phase(x - z, 8.0) < 2.2), HAZ_Y * g1)
    put(door_band & ~(phase(x - z, 8.0) < 2.2), np.array([40, 40, 40.]) * g1)

    # ---------------------------------------------------------------- the window box jutting out of the east slope
    b = p['box']
    bx_ = comp == Y.BOX
    btop = bx_ & (nz > 0.55)
    bface = bx_ & ~btop & (nx > 0.5)
    bend = bx_ & ~btop & ~bface
    ctop = COPING * g1
    ctop = mix(ctop, W.GRIME, smoothstep(0.6, 1.4, grime_n) * 0.3)
    ctop = np.where((phase(y - b['y0'], 32.0, 0.0) < 0.6)[..., None], ctop * 0.8, ctop)      # coping joints
    put(btop, ctop)
    fcol = np.array([158, 160, 164.]) * g1
    g0, g1_ = b['glass']
    in_gl = bface & (z > g0) & (z < g1_)
    t = np.clip((z - g0) / (g1_ - g0), 0, 1)
    refl = 0.55 + 0.45 * np.clip(np.sin(y * 0.045 + t * 1.3) * 0.5 + 0.5, 0, 1)
    glc = np.array([22, 52, 46.]) * (0.65 + 0.7 * t * refl)[..., None]
    mull = phase(y - b['y0'], 22.0, 0.0) < 1.1
    glc = np.where(mull[..., None], np.array([70, 74, 80.]) * g1, glc)
    fcol = np.where(in_gl[..., None], glc, fcol)
    lip = bface & ((np.abs(z - g1_ - 1.2) < 1.2) | (np.abs(z - g0 + 1.2) < 1.2))
    fcol = np.where(lip[..., None], np.array([92, 94, 98.]) * g1, fcol)
    put(bface, fcol)
    put(bend, np.array([150, 152, 156.]) * g1)
    bz = bz + 0
    by = by + 0
    bx = bx + 0.0
    dl = comp == Y.DLAMP
    put(dl, np.array([255, 250, 120.]))
    # seams on the lower east slope (one runs the length of the roof under the window)
    low_seam = (comp == Y.ROOF) & ~south_face & (np.abs(z - 29.0) < 1.1) & (x > p['xc'])
    alb = np.where(low_seam[..., None], alb * 0.45, alb)

    # ---------------------------------------------------------------- fans: housing, blades, hub
    fan = comp == Y.FAN
    put(fan, STEEL * g1)
    hub = comp == Y.FANHUB
    hc = np.array([34, 34, 38.]) * g1
    for fy in p['fans_y']:
        dx_, dy_ = x - p['fan_x'], y - fy
        d = np.hypot(dx_, dy_)
        mine = hub & (d <= p['fan_r'] + 1)
        ang = np.arctan2(dy_, dx_) - (fan_angle if fan_on[p['fans_y'].index(fy)] else 0.0)
        blade = (np.mod(ang * 5 / (2 * np.pi) + 0.15 * d / p['fan_r'], 1.0) < 0.42) & (d > 3.5) & (d < p['fan_r'] - 1.5)
        hc = np.where((mine & blade)[..., None], np.array([128, 130, 138.]) * g1 * (0.8 + 0.25 * d / p['fan_r'])[..., None], hc)
        hc = np.where((mine & (d <= 3.8))[..., None], STEEL * 1.05 * g1, hc)
    put(hub, hc)

    # ---------------------------------------------------------------- stacks: steel cap ring, dark mouth
    st = comp == Y.STACK
    for (sx, sy, sr, sh) in p['stacks']:
        d = np.hypot(x - sx, y - sy)
        zb = float(Y.roof_z(np.array([sx]), p)[0])
        mouth = st & top & (d < sr - 1.6) & (z > zb + sh - 1) & (sr > 5)
        put(mouth, np.array([30, 30, 30.]))
        ring = st & (np.abs(z - (zb + sh)) < 3.5) & (d < sr + 2) & (sr > 5)
        put(ring & ~mouth, STEEL * g1)
        band = st & (np.abs(z - (zb + sh * 0.45)) < 1.6)
        put(band, GREEN * 0.55 * g1)

    # ---------------------------------------------------------------- crane
    boom = comp == Y.BOOM
    cr = p['crane']
    alb = np.where((boom & (nz < 0.35))[..., None], alb * 0.8, alb)
    put(comp == Y.CLAW, STEEL * 0.95 * g1)
    put(comp == Y.CWEIGHT, GREEN * 0.62 * g1)
    base = comp == Y.CBASE
    xm, ym = Y.to_parked(x, y, p)
    vent = base & ~top & (phase(np.where(np.abs(nx) > np.abs(ny), ym, xm), 5.0) < 1.2) & (z > 5) & (z < 15)
    alb = np.where(vent[..., None], alb * 0.45, alb)
    tracks = base & ~top & (z < 6)
    put(tracks, np.array([52, 52, 54.]) * g1)
    trk = comp == Y.TRACK
    tread = phase(xm, 5.0) < 1.6
    put(trk, np.where(tread[..., None], np.array([38, 38, 40.]) * g1, np.array([64, 64, 66.]) * g1))

    # ---------------------------------------------------------------- lamps (glow)
    lamp = comp == Y.LAMP
    put(lamp, LAMP_C)
    if lamp_levels is None:
        lv = np.full(x.shape, lamps, np.float32)
    else:
        drib_l, k_l, _ = Y.rib_index(y, p)
        lv = np.asarray(lamp_levels, np.float32)[k_l.astype(int)]
    lampc = np.where((lv > 0.9)[..., None], np.array([255, 196, 70.]), LAMP_C)      # full = yellow-orange
    emit = np.where(lamp[..., None], lampc * (0.95 * lv)[..., None], emit)
    alb = np.where(lamp[..., None], LAMP_C * (0.35 + 0.65 * lv)[..., None], alb)
    emit = np.where((comp == Y.DLAMP)[..., None], np.array([255, 250, 120.]) * 0.9 * door, emit)
    # the crate being built (wood, with dark straps)
    cr_ = comp == Y.CRATE
    wood = np.array([150, 108, 60.]) * (1 + 1.6 * grain)[..., None]
    strap = (phase(x, 9.0) < 1.2) | (phase(y, 9.0) < 1.2)
    put(cr_, np.where(strap[..., None], np.array([70, 60, 50.]) * g1, wood))

    # ---------------------------------------------------------------- grime rising from the base, dirt
    is_ground = pad | inside | kerb
    gr = np.clip(1 - (z - p['pad_h']) / 16.0, 0, 1) ** 1.5 * np.clip(0.55 + 0.35 * grime_n, 0, 1) * (~is_ground)
    alb = mix(alb, W.GRIME, gr * 0.8)
    if occ is not None:
        # dirt collects where the sky is hidden (wall feet, crevices)
        alb = mix(alb, W.GRIME * 0.8, np.clip(occ - 0.25, 0, 1) * 0.35 * is_ground)
    return alb, (bx, by, bz), emit


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g
