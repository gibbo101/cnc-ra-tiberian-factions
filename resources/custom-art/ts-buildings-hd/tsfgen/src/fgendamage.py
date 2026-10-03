"""
Damage for the Firestorm Generator (TS GTFIRE frame 1; frame 2, destroyed, is not used: RA has healthy and damaged
only), as TS breaks it:
  base     its west end, in front of the fins, battered: bites knocked out of its edge, a shallow crater, soot and
           rubble (earth and steel)
  hatch    punched in: a hole through it, its edges bent, dark inside
  drum     its east flank chipped and cracked low down
  clamps   the front fin's clamp sooted and chipped
  fins, ring, pit, arm, dome  untouched, as TS's
Greys and browns only; placed in the building's own frame so both views match.
"""
import numpy as np
import fgen as M, wnoise as WN
from walls2 import smoothstep
from pdamage import blob
from weapdamage import Chunks, ROCK

DEBRIS = 40
SOOT = np.array([30, 29, 28.])
FRESH = np.array([150, 140, 120.])        # bare earth / stone where the base's crust is knocked off
DUST = np.array([120, 110, 92.])
INSIDE_D = np.array([40, 38, 36.])
ROCK.setdefault('earth', np.array([118, 104, 80.]))      # (weapdamage's own table: Chunks colours from it)

WBITES = ((-158.0, 96.0, 18.0, 14.0), (-140.0, 122.0, 16.0, 10.0), (-168.0, 62.0, 10.0, 14.0), (-112.0, 128.0, 12.0, 8.0))
CRATER = (-110.0, 88.0, 26.0, 20.0)
HOLE = (58.0, 92.0, 11.0, 8.0)             # in the hatch
FLANK = (150.0, 4.0, 20.0, 26.0)           # the drum's east flank, low


def model(level, p=None):
    def f(X, Yy, **kw):
        lay = kw.get('layout', 'ts')
        q = M.P if p is None else p
        sc = M.scene(X, Yy, p=p, **kw)
        return damage_scene(sc, X, Yy, level, q, lay)
    return f


def damage_scene(sc, X, Yy, level, p=M.P, layout='ts'):
    if level < 1:
        return sc
    x, y = M.to_local(X, Yy, layout)
    H = sc.H.copy(); C = sc.C.copy()
    soot = np.zeros_like(H); broken = np.zeros_like(H); crack = np.zeros_like(H)
    rock = np.zeros(H.shape + (3,), np.float32)
    base = C == M.BASE
    # ---- the base's west end: bites out of its edge, a shallow crater
    for i, (bx, by, brx, bry) in enumerate(WBITES):
        eb = blob(x, y, bx, by, brx, bry, 0.45, 911 + i, feat=5.0)
        bite = base & (eb < 0)
        H = np.where(bite, 0.0, H); C = np.where(bite, 0, C)
        broken = np.maximum(broken, (base & (eb >= 0) & (eb < 0.35)) * 0.8)
        soot = np.maximum(soot, 0.35 * np.exp(-((x - bx) ** 2 + (y - by) ** 2) / (brx * 2.2) ** 2))
    cx, cy, rx, ry = CRATER
    e = blob(x, y, cx, cy, rx, ry, 0.35, 921, feat=6.0)
    inner = (C == M.BASE) & (e < 0)
    H = np.where(inner, np.maximum(H - 4.0 * np.clip(-e * 2.5, 0, 1), 0.6), H)
    broken = np.maximum(broken, ((C == M.BASE) & (e >= -0.2) & (e < 0.2)) * 0.7)
    soot = np.maximum(soot, 0.9 * np.exp(-((x - cx) ** 2 / (rx * 2.2) ** 2 + (y - cy) ** 2 / (ry * 2.2) ** 2)))
    d = np.hypot((x - cx) / (rx * 3.0), (y - cy) / (ry * 3.0))
    crack = np.maximum(crack, np.clip(1.2 - d, 0, 1))
    # ---- the hatch: a hole punched through, its rim bent up
    hx, hy, hrx, hry = HOLE
    eh = blob(x, y, hx, hy, hrx, hry, 0.35, 931, feat=4.0)
    hatch = C == M.HATCH
    hole = hatch & (eh < 0)
    H = np.where(hole, H - 6.0, H); C = np.where(hole, DEBRIS + 1, C)
    rim = hatch & (eh >= 0) & (eh < 0.3)
    H = np.where(rim, H + 1.5, H)
    broken = np.maximum(broken, rim * 0.5)
    soot = np.maximum(soot, 0.6 * np.exp(-((x - hx) ** 2 + (y - hy) ** 2) / (hrx * 2.4) ** 2))
    # ---- the drum's east flank: chips and cracks low down
    fx, fy, frx, fry = FLANK
    ef = blob(x, y, fx, fy, frx, fry, 0.4, 941, feat=5.0)
    drum = C == M.DRUM
    chip = drum & (ef < 0)
    H = np.where(chip, np.maximum(H - 3.0 * np.clip(-ef * 3, 0, 1), 0.0), H)
    broken = np.maximum(broken, (drum & (ef < 0.25)) * 0.6)
    crack = np.maximum(crack, drum * np.clip(1.0 - np.hypot((x - fx) / (frx * 2.5), (y - fy) / (fry * 2.0)), 0, 1))
    soot = np.maximum(soot, 0.45 * np.exp(-((x - fx) ** 2 + (y - fy) ** 2) / (frx * 1.8) ** 2) * drum)
    # ---- the front fin's clamp: soot (applied in mats)
    q = p['fins'][0]
    soot = np.maximum(soot, 0.55 * np.exp(-((x - q['foot'][0]) ** 2 + (y - q['foot'][1] - 10.0) ** 2) / 30.0 ** 2))
    # ---- rubble: earth and steel bits round the west end and below the drum's flank; green bits off the hatch
    chunks = Chunks(950)
    chunks.scatter(7, (-130.0, 104.0), (4, 40), (2.4, 5.2), ['earth', 'steel'], [0.7, 0.3], [])
    chunks.scatter(3, (64.0, 112.0), (2, 14), (2.0, 3.6), ['green', 'steel'], [0.6, 0.4], [])
    chunks.scatter(3, (166.0, 10.0), (4, 18), (2.0, 4.0), ['earth', 'steel'], [0.5, 0.5], [])
    H, C, rock = chunks.apply(x, y, H, C, rock, base=np.where(H > 0, H, 0.0))
    sc.H, sc.C = H.astype(np.float32), C.astype(np.int16)
    sc.extra.update(soot=soot.astype(np.float32), broken=broken.astype(np.float32), rock=rock,
                    crack=crack.astype(np.float32))
    return sc


def mix_(a, b, t):
    return a * (1 - t) + b * t


def mats(r, alb, level, p=None):
    if level < 1:
        return alb
    p = M.P if p is None else p
    lay = r.mk.get('layout', 'ts')
    x, y = M.to_local(r.x, r.y, lay)
    z, comp = r.z, r.comp
    top = r.nz > 0.75
    out = alb.copy()
    grain = WN.noise(x, y + z, 1.2, 951) * 0.05
    g1 = (1 + grain)[..., None]
    house = np.isin(comp, list(M.HOUSE))
    dust = smoothstep(0.3, 1.3, WN.noise(x, y, 14, 952)) * np.where(top, 0.3, 0.15) * ~house
    out = out * (1 - dust[..., None]) + DUST * g1 * dust[..., None]
    s = r.field('soot')
    soot = smoothstep(0.15, 0.7, np.clip(s * (0.65 + 0.35 * WN.noise(x, y + z, 6, 953)), 0, 1)) * 0.85
    soot = soot * np.where(house, 0.25, 1.0)
    out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
    # cracks over the base and the drum, thin and dark
    cz = np.isin(comp, [M.BASE, M.DRUM])
    cn = WN.ridge(x + 0.4 * z, y - 0.6 * z, 7, 955) + 0.12 * np.abs(WN.noise(x, y + z, 1.5, 956))
    crk = (1 - smoothstep(0.015, 0.06, cn)) * np.clip(r.field('crack') * 1.6, 0, 1) * cz
    out *= (1 - 0.6 * crk)[..., None]
    brk = np.clip(r.field('broken') * 1.2, 0, 1) * ~house
    out = out * (1 - brk[..., None]) + FRESH * 0.85 * g1 * brk[..., None]
    ins = comp == DEBRIS + 1
    out = np.where(ins[..., None], INSIDE_D * (1 + 0.6 * (WN.noise(x, y + z, 3.0, 963) > 0.3))[..., None] * g1, out)
    rock = r.field('rock')
    out = np.where((comp == DEBRIS)[..., None], rock * (1 + 1.5 * grain)[..., None], out)
    return out
