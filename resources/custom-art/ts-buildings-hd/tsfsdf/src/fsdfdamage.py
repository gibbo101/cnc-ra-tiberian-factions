"""
Damage for the Firestorm Wall Section: the mod's damaged frames (+16; TS's own GTFSDF has only healthy and rubble).
In the cell's own frame, the same for every mask so a damaged run reads as one: the pad's rim chipped at its south-west
corner and a crack across the pad, scorch round the dish, a dent in the grating's bars (a few bars knocked down) on
each arm, soot; steel bits on the ground.  Greys and browns only.
"""
import numpy as np
import fsdf as M, wnoise as WN
from walls2 import smoothstep
from pdamage import blob
from weapdamage import Chunks, ROCK

DEBRIS = 40
SOOT = np.array([30, 29, 28.])
FRESH = np.array([176, 176, 182.])


def model(level, p=None):
    def f(X, Yy, **kw):
        sc = M.scene(X, Yy, p=p, **kw)
        return damage_scene(sc, X, Yy, level, M.P if p is None else p, kw.get('mask', 0))
    return f


def damage_scene(sc, X, Yy, level, p=M.P, mask=0):
    if level < 1:
        return sc
    x, y = X, Yy
    H = sc.H.copy(); C = sc.C.copy()
    soot = np.zeros_like(H); broken = np.zeros_like(H); crack = np.zeros_like(H)
    rock = np.zeros(H.shape + (3,), np.float32)
    q = p['pad']
    # the pad's south-west corner chipped
    e = blob(x, y, -q['a'] + 4.0, q['a'] - 4.0, 13.0, 10.0, 0.45, 1101, feat=4.0)
    chip = np.isin(C, [M.PAD, M.RIM]) & (e < 0)
    H = np.where(chip, np.maximum(H - 3.0, 0.6), H)
    broken = np.maximum(broken, (np.isin(C, [M.PAD, M.RIM]) & (e < 0.3)) * 0.8)
    soot = np.maximum(soot, 0.5 * np.exp(-((x + q['a']) ** 2 + (y - q['a']) ** 2) / 26.0 ** 2))
    # a crack across the pad, scorch round the dish
    crack = np.maximum(crack, np.clip(1.0 - np.abs(x * 0.6 + y * 0.8 - 6.0) / 3.0, 0, 1) * (np.hypot(x, y) < q['a']))
    soot = np.maximum(soot, 0.55 * np.exp(-(np.hypot(x, y) - p['dish']['r']) ** 2 / 9.0 ** 2) * (np.hypot(x, y) < q['a']))
    # the gratings: a dent in each arm (bars knocked down), soot over it
    am = p['arm']
    for bit, (dx, dy) in M.DIRS.items():
        if not (mask & bit) and not (M.straight(mask) and ((mask == 5 and bit in (1, 4)) or (mask == 10 and bit in (2, 8)))):
            continue
        cx, cy = dx * 52.0 + dy * 10.0, dy * 52.0 - dx * 10.0
        e = blob(x, y, cx, cy, 11.0, 11.0, 0.4, 1110 + bit, feat=4.0)
        dent = (C == M.GRATE) & (e < 0)
        H = np.where(dent, np.maximum(H - 2.6, 0.5), H)
        broken = np.maximum(broken, ((C == M.GRATE) | (C == M.RAIL)) * (e < 0.25) * 0.5)
        soot = np.maximum(soot, 0.5 * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / 14.0 ** 2))
    chunks = Chunks(1150 + mask)
    chunks.scatter(3, (-q['a'] - 6.0, q['a'] + 6.0), (2, 10), (1.6, 3.0), ['steel'], [1.0], [])
    H, C, rock = chunks.apply(x, y, H, C, rock, base=np.zeros_like(H))
    sc.H, sc.C = H.astype(np.float32), C.astype(np.int16)
    sc.extra.update(soot=soot.astype(np.float32), broken=broken.astype(np.float32), rock=rock, crack=crack.astype(np.float32))
    return sc


def mats(r, alb, level, p=None):
    if level < 1:
        return alb
    x, y, z, comp = r.x, r.y, r.z, r.comp
    out = alb.copy()
    grain = WN.noise(x, y + z, 1.2, 1151) * 0.05
    g1 = (1 + grain)[..., None]
    s = r.field('soot')
    soot = smoothstep(0.15, 0.7, np.clip(s * (0.65 + 0.35 * WN.noise(x, y + z, 5, 1152)), 0, 1)) * 0.8
    out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
    cn = WN.ridge(x * 1.3, y * 1.3, 5, 1153)
    crk = (1 - smoothstep(0.02, 0.07, cn)) * np.clip(r.field('crack') * 1.5, 0, 1) * np.isin(comp, [M.PAD, M.RIM])
    out *= (1 - 0.6 * crk)[..., None]
    brk = np.clip(r.field('broken'), 0, 1)
    out = out * (1 - brk[..., None]) + FRESH * 0.8 * g1 * brk[..., None]
    rock = r.field('rock')
    out = np.where((comp == DEBRIS)[..., None], rock * (1 + 1.5 * grain)[..., None], out)
    return out
