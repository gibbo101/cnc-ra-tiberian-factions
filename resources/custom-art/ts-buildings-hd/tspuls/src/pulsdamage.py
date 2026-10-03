"""
Damage for the EMP Pulse Cannon (TS NAPULS frame 1; RA has healthy and damaged only), as TS breaks it: the arms'
ridges and ends crumbled (chunks bitten out of them, rough broken concrete inside), cracks and soot over the arms and
the cone, rubble chunks of the same concrete round the foot (TS's NAPULS 1 scatters them to the left, front and right).
The drum and the head stay whole (TS's NAPULS_A has no damaged head). Greys and browns only, in the building's own frame
so both views match.
"""
import numpy as np
import puls as M, wnoise as WN
import weapdamage as WD
from walls2 import smoothstep
from weapdamage import Chunks

WD.ROCK.setdefault('khaki', np.array([188, 180, 146.]) * 0.82)
WD.ROCK.setdefault('khakid', np.array([150, 142, 112.]) * 0.82)

SOOT = np.array([34, 32, 28.])
BROKEN = np.array([150, 142, 116.])          # the concrete's broken inside: rougher, a little greyer
CRACK = np.array([52, 48, 40.])
DUST = np.array([120, 110, 86.])

# chunks bitten out of the arms: (arm k, distance along it, depth, radius)
BITES = ((0, 74.0, 10.0, 14.0), (0, 104.0, 7.0, 11.0), (1, 58.0, 9.0, 13.0), (1, 96.0, 8.0, 12.0),
         (3, 84.0, 7.0, 11.0), (2, 70.0, 6.0, 10.0))


def bite_centres(p=None):
    a = (M.P if p is None else p)['arms']
    out = []
    for k, s, d, rad in BITES:
        ang = np.radians(45.0 + 90.0 * k + a['delta'])
        dx, dy = np.cos(ang), np.sin(ang)
        qx, qy = dy, -dx                                  # the arm's right (its ridge sits `off` that way)
        out.append((s * dx + a['off'] * qx, s * dy + a['off'] * qy, d, rad))
    return out


def model(level, p=None):
    def f(X, Yy, **kw):
        q = M.P if p is None else p
        kw = dict(kw); kw['level'] = level
        sc = M.scene(X, Yy, p=q, **kw)
        if level < 1:
            return sc
        lay = kw.get('layout', 'ts')
        x, y = M.to_local(X, Yy, lay)
        H, C = sc.H.copy(), sc.C.copy()
        broken = np.zeros(X.shape, np.float32)
        soot = np.zeros(X.shape, np.float32)
        conc = np.isin(C, [M.BASE, M.ARM])
        for i, (bx, by, depth, rad) in enumerate(bite_centres(q)):
            d = np.hypot(x - bx, y - by)
            jag = WN.noise(x, y, 3.2, 3301 + i)
            rr = rad * (0.75 + 0.5 * jag)
            m = conc & (d < rr)
            cut = depth * np.clip(1 - (d / np.maximum(rr, 1e-3)) ** 2, 0, 1) * (0.7 + 0.6 * WN.noise(x, y, 2.0, 3311 + i))
            H = np.where(m, np.maximum(H - cut, 0.0), H)
            broken = np.maximum(broken, np.where(m, smoothstep(0.5, 2.5, cut), 0.0))
            soot = np.maximum(soot, 0.8 * np.exp(-(d / (rad * 1.9)) ** 2))
        # soot streaks on the cone round the collar and down the front
        r = np.hypot(x, y)
        soot = np.maximum(soot, 0.55 * np.exp(-((x - 10.0) ** 2 + (y - 60.0) ** 2) / 26.0 ** 2))
        soot = np.maximum(soot, 0.45 * np.exp(-((x + 46.0) ** 2 + (y + 20.0) ** 2) / 22.0 ** 2))
        # rubble round the foot: chunks of the same concrete (TS: to the left, the front and the right)
        rock = np.zeros(H.shape + (3,), np.float32)
        ch = Chunks(3320)
        ch.scatter(5, (-70.0, 92.0), (0, 26), (2.8, 6.0), ['khaki', 'khakid'], [0.6, 0.4], [])     # front left
        ch.scatter(4, (-104.0, 30.0), (0, 14), (2.4, 5.0), ['khaki', 'khakid'], [0.6, 0.4], [])    # left
        ch.scatter(3, (40.0, 112.0), (0, 18), (2.4, 4.6), ['khaki', 'khakid'], [0.6, 0.4], [])     # front
        ch.scatter(4, (98.0, -66.0), (0, 22), (2.4, 5.4), ['khaki', 'khakid'], [0.6, 0.4], [])     # right
        Hb = np.where(H > 0, H, 0.0)
        H, C, rock = ch.apply(x, y, H, C, rock, base=Hb)
        sc.H, sc.C = H.astype(np.float32), C.astype(np.int16)
        sc.extra.update(soot=soot.astype(np.float32), broken=broken.astype(np.float32), rock=rock)
        return sc
    return f


def mats(r, alb, level, p=None):
    if level < 1:
        return alb
    lay = r.mk.get('layout', 'ts')
    x, y = M.to_local(r.x, r.y, lay)
    z, comp = r.z, r.comp
    top = r.nz > 0.75
    out = alb.copy()
    grain = WN.noise(x, y + z, 1.2, 3331) * 0.05
    g1 = (1 + grain)[..., None]
    house = np.isin(comp, list(M.HOUSE))
    head = np.isin(comp, list(M.HEAD))
    conc = np.isin(comp, [M.BASE, M.ARM, M.RIM])
    # broken concrete where chunks came out: rougher and greyer
    b = r.field('broken')
    rough = 0.85 + 0.3 * WN.noise(x * 2.0, y * 2.0 + z, 1.4, 3332)
    out = np.where((conc & (b > 0.05))[..., None], out * (1 - b[..., None]) + BROKEN * rough[..., None] * b[..., None], out)
    # cracks across the arms and the cone: thin dark lines where a stretched noise crosses its middle
    n1 = WN.noise(x * 0.9 + z * 0.3, y * 0.9 - z * 0.2, 9.0, 3333)
    n2 = WN.noise(x * 1.1 - z * 0.2, y * 1.1 + z * 0.3, 13.0, 3334)
    crack = conc & ((np.abs(n1 - 0.5) < 0.018) | (np.abs(n2 - 0.5) < 0.014)) & (WN.noise(x, y, 30.0, 3335) > 0.45)
    out = np.where(crack[..., None], CRACK * g1, out)
    # dust on the tops
    dust = smoothstep(0.35, 1.3, WN.noise(x, y, 14, 3336)) * np.where(top, 0.25, 0.12) * conc
    out = out * (1 - dust[..., None]) + DUST * g1 * dust[..., None]
    # soot: heavy on the concrete, light on the house colour, none on the head (it turns: kept clean, as TS's)
    s = r.field('soot')
    soot = smoothstep(0.12, 0.7, np.clip(s * (0.6 + 0.4 * WN.noise(x, y + z, 6, 3337)), 0, 1)) * 0.85
    soot = soot * np.where(house, 0.22, 1.0) * ~head
    out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
    rock = r.field('rock')
    if rock.ndim == 3:
        out = np.where((comp == M.DEBRIS)[..., None], rock * (1 + 1.5 * grain)[..., None], out)
    return out
