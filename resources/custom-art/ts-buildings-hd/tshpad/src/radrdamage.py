"""
Damage for the Radar (TS GTRADR 01 + GTRADR_A 15-29; RA has healthy and damaged only), as TS breaks it (the shapes are
built in radr.scene(dmg=1)):
  dish     a big piece of its right side broken away, ragged; a bite out of its left rim; the struts there snapped;
           the feed rod gone (it still turns, as TS's)
  masts    the two west masts snapped and leaning far over to the west, the tall one leaning a little, two stubs
  deck     its top broken up into tilted plates, cracks, a corner knocked off its south-west, scorch
  blocks   the south-west block's green top smashed (a hole torn in it), the south box's front torn open, two of the
           ramp's panels blown out, a hole in the dome's crown
Here: soot round the damage, scorch on the deck, cracks, fresh broken edges, dark insides, a little rubble.
Greys and browns only; placed in the building's own frame so both views match.
"""
import numpy as np
import radr as M, wnoise as WN
from walls2 import smoothstep
from weapdamage import Chunks, ROCK

SOOT = np.array([30, 29, 28.])
FRESH = np.array([186, 182, 168.])
DUST = np.array([112, 104, 84.])
INSIDE_D = np.array([40, 38, 36.])


def model(level, p=None):
    def f(X, Yy, **kw):
        lay = kw.get('layout', 'ts')
        q = M.P if p is None else p
        sc = M.scene(X, Yy, p=q, dmg=level, **kw)
        if level < 1:
            return sc
        x, y = M.to_local(X, Yy, lay)
        parts = kw.get('parts')
        if parts is None or 'plinth' in parts:
            H, C = sc.H.copy(), sc.C.copy()
            rock = np.zeros(H.shape + (3,), np.float32)
            ch = Chunks(760)
            ch.scatter(5, (-12.0, 112.0), (0, 14), (2.2, 4.6), ['tan', 'green', 'steel'], [0.4, 0.3, 0.3], [])
            ch.scatter(4, (-30.0, 118.0), (0, 10), (2.0, 4.0), ['tan', 'steel'], [0.6, 0.4], [])
            ch.scatter(4, (112.0, 34.0), (0, 14), (2.0, 4.2), ['steel', 'green'], [0.6, 0.4], [])
            H, C, rock = ch.apply(x, y, H, C, rock, base=np.where(H > 0, H, 0.0))
            sc.H, sc.C = H.astype(np.float32), C.astype(np.int16)
            sc.extra['rock'] = rock
        # scorch on the deck, round the dish's turret and on the blocks' tops
        scorch = np.zeros(X.shape, np.float32)
        for (sx, sy, rr) in ((-40.0, -10.0, 20.0), (-10.0, -50.0, 16.0), (-62.0, 24.0, 14.0), (2.0, 18.0, 14.0),
                             (-84.0, 66.0, 12.0)):
            scorch = np.maximum(scorch, np.exp(-((x - sx) ** 2 + (y - sy) ** 2) / rr ** 2))
        sc.extra['scorch'] = scorch
        for k in ('soot', 'broken'):
            sc.extra.setdefault(k, np.zeros(X.shape, np.float32))
            sc.extra[k] = np.asarray(sc.extra[k], np.float32)
        return sc
    return f


def mix_(a, b, t):
    return a * (1 - t) + b * t


def mats(r, alb, level, p=None):
    if level < 1:
        return alb
    lay = r.mk.get('layout', 'ts')
    x, y = M.to_local(r.x, r.y, lay)
    z, comp = r.z, r.comp
    top = r.nz > 0.75
    out = alb.copy()
    grain = WN.noise(x, y + z, 1.2, 951) * 0.05
    g1 = (1 + grain)[..., None]
    house = np.isin(comp, list(M.HOUSE))
    # dust all over (not on the house colour), soot round the damage, scorch blobs on the deck
    dust = smoothstep(0.3, 1.3, WN.noise(x, y, 14, 952)) * np.where(top, 0.3, 0.15) * ~house
    out = out * (1 - dust[..., None]) + DUST * g1 * dust[..., None]
    s = r.field('soot')
    soot = smoothstep(0.15, 0.7, np.clip(s * (0.65 + 0.35 * WN.noise(x, y + z, 6, 953)), 0, 1)) * 0.85
    soot = soot * np.where(house, 0.22, 1.0)
    out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
    sc_ = r.field('scorch')
    scb = smoothstep(0.3, 0.6, sc_ * (0.85 + 0.3 * WN.noise(x, y + z, 5, 962))) * 0.85 * np.where(house, 0.25, 1.0)
    scb = scb * np.isin(comp, [M.DECK, M.MACH, M.TURRET, M.DECKS])
    out = out * (1 - scb[..., None]) + SOOT * scb[..., None]
    # cracks across the deck, the plinth and the tan blocks; the deck's plates edged dark
    cz = np.isin(comp, [M.DECK, M.PLINTH, M.TAN, M.ROT, M.DOME])
    cn = WN.ridge(x + 0.4 * z, y - 0.6 * z, 7, 955) + 0.12 * np.abs(WN.noise(x, y + z, 1.5, 956))
    cmask = smoothstep(0.3, 1.0, WN.noise(x, y, 26, 957)) + 0.8 * (comp == M.DECK)
    crack = (1 - smoothstep(0.015, 0.06, cn)) * np.clip(cmask, 0, 1) * cz
    out *= (1 - 0.6 * crack)[..., None]
    plate = (comp == M.DECK) & top & ((np.abs(((x + 300.0) % 34.0) - 17.0) > 16.0) | (np.abs(((y + 300.0) % 30.0) - 15.0) > 14.0))
    out = np.where(plate[..., None], out * 0.45, out)
    # fresh broken edges (light), torn green edges stay green a little darker
    brk = np.clip(r.field('broken') * 1.4, 0, 1)
    out = np.where((house & (brk > 0.3))[..., None], np.array([0, 214, 0.]) * 0.8 * g1, out)
    brk = brk * ~house
    out = out * (1 - brk[..., None]) + FRESH * 0.75 * brk[..., None]
    # the dark insides of holes, burnt panels, rubble
    out = np.where((comp == M.DEB_IN)[..., None], INSIDE_D * (1 + 2.0 * grain)[..., None], out)
    out = np.where((comp == M.DEB_BURNT)[..., None], np.array([44, 38, 34.]) * g1, out)
    rock = r.field('rock')
    if rock.ndim == 3:
        out = np.where((comp == M.DEBRIS)[..., None], rock * (1 + 1.5 * grain)[..., None], out)
    # the broken dish's edge: a light ragged rim where it broke, darker rust over what is left
    ds = comp == M.DISH
    out = np.where(ds[..., None], out * 0.85, out)
    return out
