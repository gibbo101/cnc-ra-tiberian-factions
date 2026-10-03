"""
Damage for the Limpet Mine: the mod's damaged frames (TS's DLIMPET draws its damaged frame the same as the healthy one).
Light, as befits a mine that is barely scratched or gone: the east claw's point snapped off (bare metal at the break),
a bite out of the ring's top on its south-west with soot round it, the claws' edges chipped to bare metal in places,
scorch on the ring.  Greys and browns only; no soot
on the house green (chips only).
"""
import numpy as np
import dlimp as M, wnoise as WN
from walls2 import smoothstep

DEBRIS = 40
SOOT = np.array([30, 29, 28.])
FRESH = np.array([170, 172, 178.])


def model(level, p=None):
    def f(X, Yy, **kw):
        kw = dict(kw); kw['dmg'] = level
        sc = M.scene(X, Yy, p=p, **kw)
        return damage_scene(sc, X, Yy, level, M.P if p is None else p, kw)
    return f


def damage_scene(sc, X, Yy, level, p, kw):
    if level < 1:
        return sc
    x, y = X, Yy
    H = sc.H.copy(); C = sc.C.copy()
    rock = np.zeros(H.shape + (3,), np.float32)
    pz = dict(p['settled']); pz.update(kw.get('pose') or {})
    sc.H, sc.C = H.astype(np.float32), C.astype(np.int16)
    sc.extra.update(rock=rock)
    return sc


def mats(r, alb, level, p=None):
    if level < 1:
        return alb
    p = M.P if p is None else p
    x, y, z, comp = r.x, r.y, r.z, r.comp
    out = alb.copy()
    grain = WN.noise(x, y + z, 1.2, 1851) * 0.05
    g1 = (1 + grain)[..., None]
    pz = dict(p['settled']); pz.update(r.mk.get('pose') or {})
    z0 = float(pz['z'])
    rr = np.hypot(x, y); ang = np.degrees(np.arctan2(y, x))
    # soot: round the bite in the ring (south-west) and in streaks over the ring and the collar
    dang = np.abs(np.mod(ang - 128.0 + 180.0, 360.0) - 180.0)
    s = 0.85 * np.exp(-(dang / 28.0) ** 2) + 0.35 * np.clip(WN.noise(x * 0.8, y * 0.8 + z, 6, 1852), 0, 1)
    soot = smoothstep(0.2, 0.75, s * (0.6 + 0.4 * WN.noise(x, y + z, 3, 1853))) * 0.85
    soot = soot * np.isin(comp, [M.RING, M.COLLAR, M.KNOB])
    out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
    # the bite's broken face: bare metal
    bite = (comp == M.RING) & (dang < 15.0) & (z > z0 + p['ring']['h'] - 4.0)
    out = np.where(bite[..., None], FRESH * 0.75 * g1, out)
    # the claws: chips to bare metal along their edges; the broken claw's end
    leg = comp == M.LEG
    chip = leg & (WN.noise(x * 0.9, y * 0.9 + z, 4, 1854) > 1.35)
    out = np.where(chip[..., None], FRESH * 0.8 * g1, out)
    lg = p['legs']
    d, e, tan, Hh = M.claw_frame(M.leg_az(M.BROKEN_CLAW, r.mk.get('layout', 'ts')), lg['hinge'], float(pz['phi']), z0)
    n_ = d + 0.45 * tan; n_ /= np.linalg.norm(n_)
    Lt = float(pz.get('L', 46.0))
    dist = (x - Hh[0]) * n_[0] + (y - Hh[1]) * n_[1] + (z - Hh[2]) * n_[2] - float(np.dot(d * (Lt - M.DMG_CUT), n_))
    brk = leg & (dist > -2.2) & (np.abs(ang - M.leg_az(M.BROKEN_CLAW, r.mk.get('layout', 'ts'))) < 35.0)
    out = np.where(brk[..., None], FRESH * 0.7 * g1, out)
    rock = r.field('rock')
    out = np.where((comp == DEBRIS)[..., None], rock * (1 + 1.5 * grain)[..., None], out)
    return out
