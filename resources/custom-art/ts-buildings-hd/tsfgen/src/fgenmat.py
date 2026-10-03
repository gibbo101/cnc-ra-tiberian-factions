"""Materials for the Firestorm Generator (GAFIRE): albedo, bump and glow per pixel of an hd.Render.  House green
0,214,0 x (1 + 1.1 grain) on the fins' clamps, the hatch, the kerb and the arm's collar, as on every building (detail
only as thin seams).  Textured in the building's own frame (fgen.to_local).  Colours read from GTFIRE / _A: an
earthen grey-brown base, the drum's ribbed brown side, a grey-lilac steel ring, the pit dark, the fins brown stone
with grey-lilac steel edges, the arm dark steel, the dome a tan stone lid with a grey cap.
GTFIRE_B: the ring glows blue (ring=True) or lightning cracks in the pit (bolt=k: drawn by the model as EMIT rods);
GTFIRE_C: the lamps at the fins' tips light blue-white and fade, one after the other (lamps=k)."""
import numpy as np
from walls2 import sample, smoothstep, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME
import fgen as M

GREEN = np.array([0, 214, 0.])
EARTH = np.array([128, 108, 76.])
EARTH_D = np.array([84, 70, 50.])
PEBBLE = np.array([146, 132, 108.])
DRUMC = np.array([132, 102, 62.])
DRUM_D = np.array([84, 64, 40.])
RINGC = np.array([182, 182, 208.])
RING_D = np.array([128, 128, 152.])
PITC = np.array([58, 58, 62.])
PIT_D = np.array([30, 30, 32.])
STEEL = np.array([150, 152, 162.])
STEEL_D = np.array([96, 98, 106.])
FINC = np.array([140, 112, 76.])
FIN_D = np.array([104, 82, 54.])
EDGEC = np.array([176, 176, 204.])
ARMC = np.array([66, 68, 72.])
ARM_D = np.array([46, 48, 52.])
DOMEC = np.array([182, 156, 106.])
DOME_D = np.array([140, 116, 76.])
CAPC = np.array([140, 140, 144.])
CAP_D = np.array([104, 104, 108.])
GLASS = np.array([62, 66, 84.])
MKGREY = np.array([168, 168, 170.])
PRIMER = np.array([150, 84, 62.])           # TS's MK draws the house parts red-brown before they go green
GRIME = np.array([100, 90, 70.])
# GTFIRE_B: the ring's glow (TS 101,101,255 with a deep blue inner edge) and the lightning (153,153,255 .. white)
RING_GLOW = np.array([118, 118, 255.])
RING_EDGE = np.array([30, 30, 255.])
BOLT = np.array([150, 160, 255.])
# GTFIRE_C: the two lamps (front fin, back fin), 6 frames: TS's levels (white, 206, 153, 129, 97, 97 / blue-white)
C_LEV = (1.0, 0.75, 0.5, 0.3, 0.12, 0.12)
C_OFFS = (5, 2)                 # frame of each lamp's flash (front fin's lamp at 5, the back fin's at 2)
C_COL = np.array([214, 222, 255.])


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


def layout_of(r):
    return r.mk.get('layout', 'ts')


def materials(r, p=None, occ=None, level=0, **kw):
    lay = layout_of(r)
    p = M.P if p is None else p
    x, y = M.to_local(r.x, r.y, lay)
    z, comp = r.z, r.comp
    nx, ny, nz = r.nx, r.ny, r.nz
    top = nz > 0.75
    fine = sample(NOISE_FINE, np.where(top, x, x + y), np.where(top, y, z))
    mott = sample(NOISE_MOTTLE, np.where(top, x, x + y) * 0.7 + 31, np.where(top, y, z) * 0.7 + 17)
    grain = fine * 0.035 + mott * 0.05
    g1 = (1 + grain)[..., None]
    shape = x.shape
    alb = np.zeros(shape + (3,), np.float32) + 128
    bx = np.zeros(shape, np.float32); by = np.zeros(shape, np.float32); bz = np.zeros(shape, np.float32)
    emit = np.zeros(shape + (3,), np.float32)

    def put(mask, col):
        nonlocal alb
        alb = np.where(mask[..., None], col, alb)

    house = GREEN * (1 + 1.1 * grain)[..., None]
    grime = smoothstep(0.2, 1.3, sample(NOISE_GRIME, x * 0.6 + 7, (y + z) * 0.6 + 3))
    low = smoothstep(20.0, 2.0, z)
    d = p['drum']
    cx, cy = d['c']
    rr = np.hypot(x - cx, y - cy)
    ang = np.arctan2(y - cy, x - cx)
    # ---- the base: earthen grey-brown, mottled, pebbles, darker where it slopes down at the edge
    base = comp == M.BASE
    clump = sample(NOISE_MOTTLE, x * 1.9 + 5, y * 1.9 + 11)
    peb = smoothstep(0.55, 0.8, sample(NOISE_FINE, x * 2.6 + 3, y * 2.6 + 9))
    ec = mix(EARTH * g1, EARTH_D * g1, np.clip(0.35 * smoothstep(-0.2, 0.6, clump) + 0.4 * smoothstep(0.95, 0.6, nz), 0, 1))
    ec = mix(ec, PEBBLE * g1, 0.55 * peb)
    put(base, ec)
    bz += (0.25 * peb - 0.12 * smoothstep(-0.2, 0.6, clump)) * base
    # ---- the drum's side: brown, ribbed (a rib every 15 degrees), a dark band at its foot
    drum = comp == M.DRUM
    nrib = d.get('ribs', 24)
    rib = np.abs(np.mod(ang / (2 * np.pi) * nrib + 0.5, 1.0) - 0.5)          # 0 on a rib's line
    ribm = rib < 0.07
    dc = mix(DRUMC * g1, DRUM_D * g1, np.clip(0.55 * ribm + 0.3 * grime + 0.3 * low, 0, 1))
    put(drum, dc)
    ta = -np.sin(ang); tb = np.cos(ang)                                    # the ribs stand out a little
    bx += np.where(drum, 0.35 * np.sign(np.mod(ang / (2 * np.pi) * nrib, 1.0) - 0.5) * (rib < 0.12) * ta, 0)
    by += np.where(drum, 0.35 * np.sign(np.mod(ang / (2 * np.pi) * nrib, 1.0) - 0.5) * (rib < 0.12) * tb, 0)
    # ---- the ring: grey-lilac steel, radial seams every 30 degrees, a darker inner lip; GTFIRE_B: glowing blue
    ring = comp == M.RING
    rseam = np.abs(np.mod(ang / (2 * np.pi) * 12 + 0.5, 1.0) - 0.5) < 0.03
    inner = rr < d['rp'] + 4.0
    rc = mix(RINGC * g1, RING_D * g1, np.clip(0.6 * rseam + 0.5 * inner + 0.4 * smoothstep(0.9, 0.5, nz), 0, 1))
    put(ring, rc)
    if kw.get('ring'):
        put(ring, np.where(inner[..., None], RING_EDGE, RING_GLOW * g1))
        emit = np.where(ring[..., None], emit + np.where(inner[..., None], RING_EDGE * 0.7, RING_GLOW * 0.75), emit)
    # ---- the pit: dark, darker deeper; its wall the ring's inner face
    pit = np.isin(comp, [M.PIT, M.PITF]) | (ring & (nz < 0.5) & (rr < d['rp'] + 2.0))
    put(pit, mix(PITC * g1, PIT_D * g1, np.clip(1.0 - (z - d['floor']) / 24.0, 0, 1)))
    if kw.get('ring'):
        put(pit, PIT_D * g1 * 0.8)
    # ---- the emitter: steel, dark joints
    mech = comp == M.MECH
    put(mech, np.where((phase(z, 7.0, 0.0) < 1.2)[..., None], STEEL_D * g1, STEEL * g1))
    # ---- the struts: grey-lilac steel
    put(comp == M.STRUT, mix(EDGEC * g1, RING_D * g1, smoothstep(0.6, 0.0, nz) * 0.4))
    # ---- the fins: brown stone in strata, grey-lilac steel on their narrow edges
    fin = comp == M.FIN
    strata = sample(NOISE_MOTTLE, (x + y) * 0.9 + 3, z * 2.2 + 41)
    fc = mix(FINC * g1, FIN_D * g1, np.clip(0.45 * smoothstep(-0.3, 0.7, strata) + 0.25 * grime, 0, 1))
    put(fin, fc)
    edge = np.zeros(shape, bool)
    for q in p['fins']:
        el, ew, et = M.fin_axes(q)
        # the narrow side faces: the normal along the fin's width axis
        side = np.abs(nx * ew[0] + ny * ew[1] + nz * ew[2]) > 0.75
        foot = np.array([q['foot'][0], q['foot'][1]])
        near = np.hypot(x - foot[0], y - foot[1]) < q['L'] + q['w']
        edge |= fin & side & near
    put(edge, mix(EDGEC * g1, RING_D * g1, 0.25 * grime))
    # ---- house green: the clamps, the hatch, the kerb, the arm's collar; seams
    cl = comp == M.CLAMP
    put(cl, np.where((phase(z, 12.0, 3.0) < 0.8)[..., None], house * 0.62, house))
    ht = comp == M.HATCH
    a_h = np.radians(p['hatch']['az'])
    across = -(x - cx) * np.sin(a_h) + (y - cy) * np.cos(a_h)
    hseam = (np.abs(across) < 0.8) | (np.abs(np.abs(across) - p['hatch']['w'] / 2.0) < 1.6)
    put(ht, np.where(hseam[..., None], house * 0.62, house))
    put(comp == M.STRIP, house)
    ag = comp == M.ARMG
    put(ag, np.where((phase(z + x * 0.3, 10.0, 0.0) < 0.7)[..., None], house * 0.62, house))
    # ---- the arm: dark steel with panel lines; the hinge
    arm = comp == M.ARM
    put(arm, mix(ARMC * g1, ARM_D * g1, np.clip(0.5 * (phase(x - y, 22.0, 0.0) < 1.0) + 0.3 * smoothstep(0.5, 0.0, nz), 0, 1)))
    # ---- the dome: tan stone, mottled; its cap grey with ribs
    dome = comp == M.DOME
    dm = p['dome']
    dmot = sample(NOISE_MOTTLE, x * 1.6 + 13, (y + z) * 1.6 + 7)
    put(dome, mix(DOMEC * g1, DOME_D * g1, np.clip(0.45 * smoothstep(-0.3, 0.7, dmot) + 0.3 * smoothstep(0.4, 0.0, nz), 0, 1)))
    cap = comp == M.DOMEC
    crib = np.abs(np.mod(ang / (2 * np.pi) * 8 + 0.5, 1.0) - 0.5) < 0.04
    put(cap, mix(CAPC * g1, CAP_D * g1, np.clip(0.6 * crib + 0.3 * smoothstep(0.9, 0.5, nz), 0, 1)))
    # ---- the lamps at the fins' tips: dark glass; GTFIRE_C lights them blue-white, one after the other
    lamp = comp == M.LAMP
    put(lamp, GLASS * g1)
    kC = kw.get('lamps')
    if kC is not None and lamp.any():
        for i, q in enumerate(p['fins']):
            tip = M.fin_tip(q, p['base']['h'])
            near = lamp & (np.hypot(x - tip[0], y - tip[1]) < p['lamps']['r'] * 2.5)
            lv = C_LEV[(kC - C_OFFS[i]) % 6]
            put(near, mix(GLASS * g1, C_COL, lv))
            emit = np.where(near[..., None], emit + C_COL * 0.85 * lv, emit)
    # ---- the lightning (GTFIRE_B, even frames): EMIT rods, white-blue, glowing
    em = comp == M.EMIT
    put(em, BOLT)
    emit = np.where(em[..., None], emit + np.array([90, 96, 160.]), emit)
    # ---- the build-up: plain grey until painted, the house parts green last
    put(comp == M.SLAB, MKGREY * g1)
    paint = r.field('paint', 1.0)
    if np.any(paint < 1):
        grey_ = r.hitmask & ~np.isin(comp, [M.LAMP, M.SLAB]) & ~np.isin(comp, list(M.HOUSE))
        alb = np.where(grey_[..., None], mix(MKGREY * g1, alb, np.clip(paint, 0, 1)), alb)
        emit = emit * np.clip(paint, 0, 1)[..., None]
    green = r.field('green', 1.0)
    if np.any(green < 1):
        # the house parts: grey, then red-brown primer as the colours come in (TS's MK), then green
        hm = np.isin(comp, list(M.HOUSE))
        pre = mix(MKGREY * g1, PRIMER * g1, np.clip(paint, 0, 1))
        alb = np.where(hm[..., None], mix(pre, alb, np.clip(green, 0, 1)), alb)
    # grime at the foot (not on house colour)
    gr = smoothstep(0.35, 1.2, sample(NOISE_GRIME, x * 0.8, y * 0.8 + z)) * low * 0.3
    gr = gr * np.isin(comp, [M.DRUM, M.FIN, M.STRUT])
    alb = mix(alb, GRIME, gr)
    return alb, (bx, by, bz), emit


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, list(M.HOUSE) + [40, 42])
