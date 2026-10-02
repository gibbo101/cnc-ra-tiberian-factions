"""
Damage for the Helipad (TS GTHPAD 01 + GTHPADBB 01; RA has healthy and damaged only), as TS breaks it:
  pad      cracks over it, a patch of its west part broken up (between the block and the landing circle), scorch
  box      the control box's top smashed in, sooted
  tanks    dented, sooted; the block sooted
  lights   five of the approach lights broken (dark), as TS's damaged GTHPAD_A
Greys and browns only.
"""
import numpy as np
import hpad as M, wnoise as WN
from walls2 import smoothstep
from radr import dblob
from weapdamage import Chunks

SOOT = np.array([30, 29, 28.])
FRESH = np.array([186, 182, 168.])
DUST = np.array([112, 104, 84.])
INSIDE_D = np.array([40, 38, 36.])


def model(level, p=None):
    def f(X, Yy, **kw):
        q = M.P if p is None else p
        sc = M.scene(X, Yy, p=q, **kw)
        if level < 1:
            return sc
        x, y = X, Yy
        H, C = sc.H.copy(), sc.C.copy()
        soot = np.zeros(X.shape, np.float32); broken = np.zeros(X.shape, np.float32)
        # the pad's west part broken up: sunk ragged patch, rubble on it
        e = dblob(x, y, -40.0, 14.0, 26.0, 20.0, 0.4, 801, feat=6.0)
        patch = (C == M.PAD) & (e < 0)
        H = np.where(patch, H - 4.0 - 2.0 * np.clip(-e * 3, 0, 1), H); C = np.where(patch, M.DEB_BURNT, C)
        broken = np.maximum(broken, ((C == M.PAD) & (e >= 0) & (e < 0.25)) * 0.8)
        soot = np.maximum(soot, 0.6 * np.exp(-((x + 40) ** 2 + (y - 14) ** 2) / 40.0 ** 2))
        # the control box: its top smashed in
        b = q['box']
        cx, cy = (b['x'][0] + b['x'][1]) / 2, (b['y'][0] + b['y'][1]) / 2
        for s in sc.slabs:
            if 'box' in s.name:
                ok = (s.top >= 0) & (s.comp == M.BOX)
                dent = 9.0 * np.clip(1.2 - np.hypot(x - cx - 6, y - cy) / 16.0, 0, 1) + 3.0 * WN.noise(x, y, 7.0, 802)
                s.top = np.where(ok, np.maximum(s.top - np.maximum(dent, 0), s.bot + 6.0), s.top)
        soot = np.maximum(soot, 0.7 * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / 26.0 ** 2))
        # the tanks dented, sooted; the block sooted
        tk = C == M.TANK
        H = np.where(tk, H - 2.5 * (0.5 + 0.5 * WN.noise(x, y, 6.0, 803)), H)
        for (tx, ty, tz, tr) in q['tanks']['pts']:
            soot = np.maximum(soot, 0.45 * np.exp(-((x - tx) ** 2 + (y - ty) ** 2) / (tr * 1.6) ** 2))
        soot = np.maximum(soot, 0.5 * np.exp(-((x + 106) ** 2 + (y - 92) ** 2) / 30.0 ** 2))
        rock = np.zeros(H.shape + (3,), np.float32)
        ch = Chunks(810)
        ch.scatter(6, (-40.0, 14.0), (0, 22), (2.2, 4.8), ['conc', 'steel'], [0.7, 0.3], [])
        ch.scatter(4, (cx + 20, cy + 20), (0, 16), (2.0, 4.2), ['tan', 'steel'], [0.6, 0.4], [])
        H, C, rock = ch.apply(x, y, H, C, rock, base=np.where(H > 0, H, 0.0))
        sc.H, sc.C = H.astype(np.float32), C.astype(np.int16)
        sc.extra.update(soot=soot, broken=broken, rock=rock)
        return sc
    return f


def mats(r, alb, level, p=None):
    if level < 1:
        return alb
    x, y, z, comp = r.x, r.y, r.z, r.comp
    top = r.nz > 0.75
    out = alb.copy()
    grain = WN.noise(x, y + z, 1.2, 951) * 0.05
    g1 = (1 + grain)[..., None]
    house = np.isin(comp, list(M.HOUSE)) | ((comp == M.PAD) & (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])))
    dust = smoothstep(0.3, 1.3, WN.noise(x, y, 14, 952)) * np.where(top, 0.3, 0.15) * ~house
    out = out * (1 - dust[..., None]) + DUST * g1 * dust[..., None]
    s = r.field('soot')
    soot = smoothstep(0.15, 0.7, np.clip(s * (0.65 + 0.35 * WN.noise(x, y + z, 6, 953)), 0, 1)) * 0.85
    soot = soot * np.where(house, 0.22, 1.0)
    out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
    cz = np.isin(comp, [M.PAD, M.STEPS, M.BLOCK, M.BOX])
    cn = WN.ridge(x + 0.4 * z, y - 0.6 * z, 7, 955) + 0.12 * np.abs(WN.noise(x, y + z, 1.5, 956))
    cmask = smoothstep(0.2, 0.9, WN.noise(x, y, 26, 957)) + 0.5 * (comp == M.PAD)
    crack = (1 - smoothstep(0.015, 0.06, cn)) * np.clip(cmask, 0, 1) * cz * ~house
    out *= (1 - 0.6 * crack)[..., None]
    brk = np.clip(r.field('broken') * 1.4, 0, 1) * ~house
    out = out * (1 - brk[..., None]) + FRESH * 0.75 * brk[..., None]
    out = np.where((comp == M.DEB_BURNT)[..., None], np.array([70, 62, 50.]) * (1 + 2 * grain)[..., None], out)
    rock = r.field('rock')
    if rock.ndim == 3:
        from weapdamage import ROCK
        out = np.where((comp == M.DEBRIS)[..., None], rock * (1 + 1.5 * grain)[..., None], out)
    return out
