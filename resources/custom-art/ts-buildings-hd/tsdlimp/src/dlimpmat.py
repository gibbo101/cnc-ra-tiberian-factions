"""Materials for the Limpet Mine (DLIMPET): house green 0,214,0 x (1 + 1.1 grain) on the body and the claws (detail only
as thin seams), a grey collar and a glossy black knob on top, a grey ring with a dark hinge slot and a white light over
each claw.  Colours read from DLIMPET / DLIMPMK / DLIMP_A.
Frame kwargs (the overlays and the build-up's blinking):
  lamp = 0 amber, 1 red, 2 dark red (DLIMPMK: the lamp low on the body's front cycles every frame); None: dark
  eye  = 'w' white, 'b' blue-white (DLIMPMK 3, 13, 23, 33 and 4, 14, ...); None: dark
  glow = 0..9 (DLIMP_A): the dug-in top flashes white (0), bright green (1) and fades back to its dark green (2-6);
         7-9 as it is
The dug-in top (the body's top deep in its ring) is darker, as TS's (house green in its shadow)."""
import numpy as np
from walls2 import sample, smoothstep, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME
import dlimp as M

GREEN = np.array([0, 214, 0.])
COLLARC = np.array([128, 128, 132.])
COLLAR_D = np.array([84, 84, 88.])
KNOBC = np.array([40, 40, 42.])
RINGC = np.array([150, 150, 154.])
RING_S = np.array([118, 118, 122.])
RING_D = np.array([70, 70, 74.])
SLOTC = np.array([22, 22, 24.])
WHITE = np.array([236, 236, 236.])
LAMPS = (np.array([255, 176, 20.]), np.array([255, 24, 0.]), np.array([176, 10, 0.]))
LAMP_OFF = np.array([96, 40, 20.])
EYE_W = np.array([250, 250, 250.])
EYE_B = np.array([206, 206, 255.])
EYE_OFF = np.array([54, 62, 70.])
MKGREY = np.array([168, 168, 170.])
DUG = 0.5                                   # the dug-in top's albedo (in the ring's shadow, as TS's dark green)
GLOW = (1.0, 1.0, 0.85, 0.7, 0.55, 0.4, 0.25)


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


def pose_of(r, p):
    pz = dict(p['settled']); pz.update(r.mk.get('pose') or {})
    return pz


def materials(r, p=None, occ=None, level=0, **kw):
    p = M.P if p is None else p
    x, y = M.to_local(r.x, r.y, r.mk.get('layout', 'ts'))
    z, comp = r.z, r.comp
    nz = r.nz
    top = nz > 0.75
    fine = sample(NOISE_FINE, np.where(top, x, x + y), np.where(top, y, z))
    mott = sample(NOISE_MOTTLE, np.where(top, x, x + y) * 0.7 + 31, np.where(top, y, z) * 0.7 + 17)
    grain = fine * 0.035 + mott * 0.05
    g1 = (1 + grain)[..., None]
    shape = x.shape
    alb = np.zeros(shape + (3,), np.float32) + 128
    bx = np.zeros(shape, np.float32); by = np.zeros(shape, np.float32); bz = np.zeros(shape, np.float32)
    emit = np.zeros(shape + (3,), np.float32)

    def put(m, col):
        nonlocal alb
        alb = np.where(m[..., None], col, alb)

    pz = pose_of(r, p)
    z0 = float(pz['z']); zb = z0 - float(pz['sink'])
    rg = p['ring']
    house = GREEN * (1 + 1.1 * grain)[..., None]
    ang = np.degrees(np.arctan2(y, x))
    rr = np.hypot(x, y)
    # ---- the body: house green, seams round it at the foot and the shoulder of its widest band, and down it between
    # the claws
    body = comp == M.BODY
    dzb = z - zb
    seam = (np.abs(dzb - 11.0) < 0.45) | (np.abs(dzb - 26.0) < 0.45)
    seam |= (np.abs(np.mod(ang - 45.0 + 45.0, 90.0) - 45.0) * np.pi / 180.0 * rr < 0.45) & (dzb > 11.0) & (dzb < 40.0)
    put(body, np.where(seam[..., None], house * 0.62, house))
    # the dug-in top: the body's top inside the ring, below its rim
    dug = body & (rr < rg['r'][0] + 0.6) & (z < z0 + rg['h'] - 0.3)
    put(dug, house * DUG)
    # ---- the claws: house green; the sleeve's end a thin seam
    leg = comp == M.LEG
    put(leg, house)
    # ---- the collar and the knob
    put(comp == M.COLLAR, mix(COLLARC * g1, COLLAR_D * g1, 0.5 * smoothstep(0.9, 0.3, nz)))
    knob = comp == M.KNOB
    put(knob, KNOBC * g1)
    # ---- the lamp and the eye
    lamp = comp == M.LAMP
    lk = kw.get('lamp')
    if lk is None:
        put(lamp, LAMP_OFF * g1)
    else:
        col = LAMPS[int(lk) % 3]
        put(lamp, col); emit = np.where(lamp[..., None], emit + col * 0.55, emit)
    eye = comp == M.EYE
    ek = kw.get('eye')
    if ek is None:
        put(eye, EYE_OFF)
    else:
        col = EYE_W if ek == 'w' else EYE_B
        put(eye, col); emit = np.where(eye[..., None], emit + col * 0.6, emit)
    # ---- the ring: light grey top, mid grey side, dark underneath; over each claw a dark hinge slot in its side and a
    # white light beside it
    ring = comp == M.RING
    put(ring, np.where(top[..., None], RINGC * g1, mix(RING_S * g1, RING_D * g1, smoothstep(0.0, -0.6, nz))))
    side = ring & (np.abs(nz) < 0.6) & (rr > rg['r'][1] - 1.0)
    lay = r.mk.get('layout', 'ts')
    azs = np.array([M.leg_az(k, lay) for k in range(4)])
    dd = np.mod(ang[..., None] - azs + 180.0, 360.0) - 180.0
    rel = np.take_along_axis(dd, np.argmin(np.abs(dd), axis=-1)[..., None], -1)[..., 0]   # degrees from the nearest claw
    slot = side & (rel > -11.0) & (rel < -3.5) & (z > z0 + 3.6) & (z < z0 + rg['h'] - 0.8)
    put(slot, SLOTC)
    lt = side & (rel > -2.5) & (rel < 5.5) & (z > z0 + 3.6) & (z < z0 + rg['h'] - 0.8)
    put(lt, WHITE); emit = np.where(lt[..., None], emit + WHITE * 0.3, emit)
    # the ring's inner wall: dark
    inner = ring & ~top & (rr < rg['r'][0] + 1.0)
    put(inner, RING_D * g1)
    # ---- DLIMP_A: the dug-in top flashing
    gk = kw.get('glow')
    if gk is not None and int(gk) < 7:
        gk = int(gk)
        lens = body & (rr < rg['r'][0] + 0.6) & (z < z0 + rg['h'] + 2.0)
        rim = ring & (rr < rg['r'][0] + 2.5)
        if gk == 0:
            put(lens, np.array([255, 255, 255.]))
            emit = np.where(lens[..., None], emit + np.array([255, 255, 255.]) * 0.9, emit)
            emit = np.where(rim[..., None], emit + np.array([150, 150, 150.]), emit)
        else:
            lev = GLOW[gk]
            put(lens, GREEN)
            emit = np.where(lens[..., None], emit + np.array([0, 214, 0.]) * 0.85 * lev, emit)
            if gk <= 3:
                emit = np.where(rim[..., None], emit + np.array([40, 110, 40.]) * lev, emit)
    # the build-up grey (unused: TS's drone flies in finished)
    paint = r.field('paint', 1.0)
    if np.any(paint < 1):
        hm = r.hitmask & ~np.isin(comp, [M.LAMP, M.EYE])
        alb = np.where(hm[..., None], mix(MKGREY * g1, alb, np.clip(paint, 0, 1)), alb)
    return alb, (bx, by, bz), emit


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 30)
    return r.hitmask & g & np.isin(r.comp, list(M.HOUSE) + [40, 42])
