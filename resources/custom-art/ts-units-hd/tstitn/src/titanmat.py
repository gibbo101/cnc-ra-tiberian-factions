"""
titanmat.py - materials for the Titan (titan.py), per pixel of an rcrender.RCRender.

Colours read from TS's MMCH frames and MMCHBARL.VXL (UNITTEM.PAL): the Titan's own yellow-brown paint (TS's
ochre ramp, not house colour) on the shell, the boss, the thighs, shins, feet and the waist; steel on the joints,
the knee spurs, the bearing ring, the cannon's bracket and tube (its muzzle brake dark); a black antenna.  House
colour is pure green 0,214,0 x (1 + 1.1 grain) on the band, the pods (the front pair with white lamps), the box
and the cannon's breech, housing and taper, with detail only as thin seams and ribs (the band's plate grooves
and bolts, the box's louvres).  Textured in each part's own frame (r.lu, r.lv, r.lw), so detail turns with it.
"""
import numpy as np
import walls2 as W
from walls2 import smoothstep
import wnoise
import legfit as LF
import torso2 as T2
import barrel as BR

GREEN = np.array([0, 214, 0.])
GOLD = np.array([208, 162, 70.])              # the Titan's own yellow-brown paint (TS's ochre ramp)
GOLD_D = np.array([168, 128, 56.])
OLIVE = np.array([84, 76, 52.])
GUN = np.array([74, 77, 90.])                # the hip dome: dark blue-grey gunmetal
THIGH_C = np.array([78, 72, 50.])            # the thighs: dark olive
BAND_GREY = np.array([128, 128, 134.])
BAND = np.array([118, 118, 124.])
STEEL = np.array([150, 152, 160.])
STEEL_L = np.array([222, 224, 228.])
STEEL_D = np.array([78, 79, 84.])
TAN = np.array([218, 168, 74.])
GOLD_SH = np.array([216, 170, 76.])          # the upper shell: the same yellow-brown, a touch lighter
BLACK = np.array([28, 28, 30.])
GRIME = np.array([112, 104, 78.])
FILL = 0.32


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


def smooth_normals(r, part_index, sigma=0.45):
    """blend the facet normals of a many-faced part (its planes' signed distances, softmax) so the convex
    hull shell shades as a rounded surface."""
    m = (r.who == part_index) & r.hitmask
    if not m.any():
        return
    p = r.parts[part_index]
    N = np.array([c.n for c in p.cons if c.kind == 'plane']); d = np.array([c.d for c in p.cons if c.kind == 'plane'])
    P = np.stack([r.x[m], r.y[m], r.z[m]], 1)
    s = P @ N.T - d[None, :]
    w = np.exp((s - s.max(1, keepdims=True)) / sigma)
    n = w @ N
    n = n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)
    r.nx[m], r.ny[m], r.nz[m] = n[:, 0], n[:, 1], n[:, 2]


def grain_of(r, scale=1.0):
    """walls2's grain, sampled triplanar in the part's own frame (no streaks down vertical faces)."""
    X, Y, Z = r.lu * 6.4 * scale, r.lv * 6.4 * scale, r.lw * 6.4 * scale
    ax, ay, az = np.abs(r.nx) + 1e-3, np.abs(r.ny) + 1e-3, np.abs(r.nz) + 1e-3
    s_ = ax + ay + az
    def tri(noise, o):
        return (W.sample(noise, Y + o, Z + 2 * o) * ax + W.sample(noise, X + 3 * o, Z + o) * ay +
                W.sample(noise, X + o, Y + 5 * o) * az) / s_
    return tri(W.NOISE_FINE, 0) * 0.035 + tri(W.NOISE_MOTTLE, 17) * 0.05


def phase(v, per, off=0.0):
    return np.abs(np.mod(v - off + per / 2, per) - per / 2)


def materials(r, P=None, S=None, occ=None):
    """albedo, bump (bx, by, bz) and glow for every hit pixel; r.parts' comps say which part is which."""
    comp = r.comp
    sh = comp.shape
    alb = np.zeros(sh + (3,), np.float32)
    emit = np.zeros(sh + (3,), np.float32)
    bz = np.zeros(sh, np.float32)
    grain = grain_of(r, scale=1 / 1.5)               # features as big in the game as on the buildings
    g1 = (1 + 0.45 * grain)[..., None]              # painted metal: a fine, quiet grain
    house = GREEN * (1 + 1.1 * grain)[..., None]
    lu, lv, lw = r.lu, r.lv, r.lw
    z = r.z
    nzl = r.nz
    top = nzl > 0.7
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])

    # ---------------------------------------------------------------- legs
    # TS: a dark blue-grey hip dome with a lighter ring band; dark olive thighs; gold shins and feet; grey
    # joints; the knee spur steel with a dark tip
    dust = smoothstep(4.0, 0.0, z) * 0.45
    hip = comp == LF.HIP
    if hip.any():
        hc = S['hip_c'][2] if S else 19.0
        put(hip, GUN * g1)
        band = hip & (np.abs(lw - (hc - 0.4)) < 0.5)
        put(band, BAND_GREY * g1)
        bz -= 0.3 * (hip & (np.abs(np.abs(lw - (hc - 0.4)) - 0.5) < 0.12))
    thigh = comp == LF.THIGH
    if thigh.any():
        put(thigh, GOLD * 0.92 * g1)
        # an armour plate down the thigh's outer face, its edges picked out
        put(thigh & (phase(lw, 2.4) < 0.12), GOLD * 0.6 * g1)
    # the waist: the pelvis and the dome in the body paint, the bearing ring and the hip joints steel
    pel = comp == LF.PELVIS
    if pel.any():
        put(pel, GOLD * 0.95 * g1)
        put(pel & (np.abs(lv) < 0.18) & ~top, GOLD * 0.6 * g1)           # the seam down its front and back
    put(comp == LF.HIPDOME, GOLD * 0.95 * g1)
    ring = comp == LF.HIPRING
    if ring.any():
        put(ring, STEEL * 0.8 * g1)
        put(ring & (np.abs(nzl) < 0.3) & (phase(np.arctan2(lv, lu) * 3.0, 1.6) < 0.09), STEEL_D * g1)   # a few bolts
    put(comp == LF.HIPJOINT, STEEL * 0.8 * g1)
    shin = comp == LF.SHIN
    if shin.any():
        put(shin, mix(GOLD * g1, GRIME, dust))
    foot = comp == LF.FOOT
    if foot.any():
        put(foot, mix(GOLD * 0.96 * g1, GRIME, dust))
        # a dark sole edge
        put(foot & (z < 0.5), mix(OLIVE * 0.8 * g1, GRIME, 0.4))
    put(comp == LF.JOINT, STEEL * 0.8 * g1)
    spur = comp == LF.KNEE
    if spur.any():
        put(spur, STEEL * g1)
        if S is not None:
            put(spur & (r.spur_t > 0.72), STEEL_D * 0.6 * g1)
    # ---------------------------------------------------------------- upper body
    body = comp == T2.BODY
    if body.any():
        put(body, GOLD_SH * g1)
        # the recess on the right flank where the cannon's mount sits: darker, set in
        # TS's dark crease down the right flank above the cannon's mount: a narrow recessed panel, darkest low
        rec = body & ~top & (lv > 4.8) & (lu > -2.6) & (lu < 1.6) & (lw < (P['band'] + 4.6 if P else 37.5))
        depth = smoothstep((P['band'] + 4.6 if P else 37.5), (P['band'] if P else 33.0), lw)
        put(rec, GOLD_SH * (1 - 0.38 * depth)[..., None] * g1)
        edge = body & ~top & (lv > 4.8) & ((np.abs(lu + 2.6) < 0.16) | (np.abs(lu - 1.6) < 0.16)) & \
            (lw < (P['band'] + 4.6 if P else 37.5))
        put(edge, GOLD_SH * 0.55 * g1); bz -= 0.4 * edge
        # the lip's underside, where the shell overhangs the band
        put(body & (nzl < -0.3), OLIVE * g1)
    band = comp == T2.BAND
    if band.any():
        put(band, house)
        arc = np.arctan2(lv, lu) * 9.0
        groove = band & ~top & (phase(arc, 2.6) < 0.16)
        put(groove, GREEN * 0.6 * g1); bz -= 0.5 * groove
        bl = P['band'] if P else 32.0
        bolts = band & ~top & (np.abs(lw - (bl - 1.0)) < 0.2) & (phase(arc + 1.3, 2.6) < 0.2)
        put(bolts, GREEN * 0.8 * g1)
    hatch = comp == T2.HATCH
    if hatch.any():
        hu, hv, hr = (P.get('hu', 2.4), P.get('hv', 0.8), P.get('hr', 2.7)) if P else (2.4, 0.8, 2.7)
        # the rounded boss: smooth, its rim's upright side a shade darker
        put(hatch, GOLD_SH * 1.02 * g1)
        put(hatch & (np.abs(nzl) < 0.25), GOLD_SH * 0.82 * g1)
    pod = comp == T2.POD
    put(pod, house)
    if pod.any() and P is not None:
        # the front pods' lamps: white discs on their front faces
        fu = P['pfu'][1]
        pc = (P['pv'][0] + P['pv'][1]) / 2
        wc = (P['pbot'] + P['ptop']) / 2
        for s in (-1, 1):
            d = np.hypot(lv - s * pc, lw - wc)
            lamp = pod & (lu > fu - 0.35) & (d < 0.95)
            put(lamp, np.array([236, 240, 246.]))
            emit += (lamp * 60.0)[..., None]
            rim = pod & (lu > fu - 0.35) & (np.abs(d - 1.15) < 0.2)
            put(rim, STEEL_D * g1)
    box = comp == T2.BOX
    put(box, house)
    if box.any() and P is not None:
        # louvres on the box's outer (left) side
        louv = box & (lv < P['bv'][0] + 0.3) & (phase(lw, 1.3) < 0.25) & (lw > P['bbot'] + 1.5) & (lw < P['btop'] - 1.0)
        put(louv, GREEN * 0.55 * g1); bz -= 0.3 * louv
        # a grey vent on its front face (TS's grey strip beside the box)
        vent = box & (lu > P['bu'][1] - 0.3) & (lv > P['bv'][1] - 2.0) & (lw > P['bbot'] + 2.0) & (lw < P['btop'] - 1.2)
        put(vent, STEEL * 0.85 * g1 * (1 - 0.35 * (phase(lw, 1.0) < 0.2))[..., None])
    put(comp == T2.ANT, BLACK * g1)
    put(comp == T2.MOUNT, STEEL_D * g1)
    # ---------------------------------------------------------------- cannon
    for c in (BR.BREECH, BR.HOUSING, BR.TAPER):
        put(comp == c, house)
    put(comp == BR.BRACKET, STEEL * g1)
    tube = comp == BR.TUBE
    put(tube, STEEL_L * g1)
    put(comp == BR.MUZZLE, STEEL_D * g1)
    # the fill light from the camera on the sides that face it (EA's HD units are front-lit)
    cam = r.cam
    tc = np.array([cam.T[0] * cam.cE, cam.T[1] * cam.cE, cam.sE]); tc = tc / np.linalg.norm(tc)
    nf = np.clip(r.nx * tc[0] + r.ny * tc[1] + r.nz * tc[2], 0, 1) * (1 - np.clip(r.nz, 0, 1))
    if occ is not None:
        nf = nf * (1 - 0.85 * np.clip(occ, 0, 1))
    if getattr(r, 'fill_mask', None) is not None:
        nf = nf * r.fill_mask
    emit = emit + alb * (FILL * nf)[..., None]
    return alb, (np.zeros(sh, np.float32), np.zeros(sh, np.float32), bz), emit


HOUSE_COMPS = (T2.BAND, T2.POD, T2.BOX, BR.BREECH, BR.HOUSING, BR.TAPER)


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, HOUSE_COMPS)
