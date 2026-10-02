"""
Damage for the Sensor Array.  TS draws none: GTDPSA's three frames are the same picture (and GTDPSA_A's damaged half is
empty: the damaged array's light is out).  RA needs a damaged state, so this is a light one in TS's manner (greys and
browns only, the vehicle kept whole):
  dish     a bite out of the radar dish's rim, soot over it
  cab      its north-east top corner stoved in, the window smashed (dark, cracked)
  deck     a scorch over the deck's east half and the housing's slope, the stripe chipped, paint chipped off edges
  mast     sooted up its west side (the house-green panel only lightly)
  ground   a few chunks of ochre plate and steel by the tracks and on the deck
"""
import numpy as np
import dpsa as M, wnoise as WN
from walls2 import smoothstep
from radr import dblob
from weapdamage import Chunks

SOOT = np.array([30, 29, 28.])
BARE = np.array([128, 124, 116.])
DUST = np.array([112, 104, 84.])
SMASH = np.array([34, 36, 44.])


def model(level, p=None):
    def f(X, Yy, **kw):
        q = M.P if p is None else p
        sc = M.scene(X, Yy, p=q, **kw)
        if level < 1:
            return sc
        lay = kw.get('layout', 'ts')
        x, y = M.to_local(X, Yy, lay)
        H, C = sc.H.copy(), sc.C.copy()
        soot = np.zeros(X.shape, np.float32)
        # the cab's north-east top corner stoved in
        cb = q['cab']
        cx_, cy_ = cb['x'][1] - 4.0, cb['y'][0] + 5.0
        e = dblob(x, y, cx_, cy_, 13.0, 11.0, 0.35, 1401, feat=5.0)
        cab = (C == M.CAB) & (e < 0.15)
        H = np.where(cab, H - (5.0 + 5.0 * np.clip(-e * 3, 0, 1)), H)
        soot = np.maximum(soot, 0.75 * np.exp(-((x - cx_) ** 2 + (y - cy_) ** 2) / 16.0 ** 2))
        # a scorch over the deck's east half and the housing's slope
        soot = np.maximum(soot, 0.6 * np.exp(-((x - 20.0) ** 2 / 34.0 ** 2 + (y - 8.0) ** 2 / 26.0 ** 2)))
        soot = np.maximum(soot, 0.5 * np.exp(-((x + 2.0) ** 2 + (y + 10.0) ** 2) / 18.0 ** 2))
        # the mast: sooted up its west side
        pv = q['mast']['pivot']
        soot = np.maximum(soot, 0.45 * np.exp(-((x - pv[0] + 10.0) ** 2 + (y - pv[1] - 6.0) ** 2) / 16.0 ** 2))
        # the radar dish: a bite out of its top rim
        g = dict(M.DONE); g.update(kw.get('prog') or {})
        if float(g['theta']) >= 89.0:
            df = M.head_pose(q, float(g['theta']), float(g['unfold']))
            n = df['n']
            u1 = np.cross(n, [0, 0, 1.0]); u1 /= np.linalg.norm(u1); u2 = np.cross(n, u1)
            Pb = df['C'] - 0.95 * df['R'] * (0.8 * u2 - 0.6 * u1)            # up the face, a little to its south side
            bite = dblob(x, y, Pb[0], Pb[1], 8.0, 7.0, 0.4, 1402, feat=4.0) < 0.0
            for s in sc.slabs:
                if 'head' in s.name:
                    mid = 0.5 * (s.top + s.bot)
                    ok = (s.top >= 0) & (s.comp == M.HEAD) & bite & (np.abs(mid - Pb[2]) < 9.0)
                    s.top = np.where(ok, -1.0, s.top)
            soot = np.maximum(soot, 0.6 * np.exp(-((x - Pb[0]) ** 2 + (y - Pb[1]) ** 2) / 12.0 ** 2))
        # rubble by the tracks and on the deck
        rock = np.zeros(H.shape + (3,), np.float32)
        ch = Chunks(1410)
        ch.scatter(4, (30.0, 56.0), (0, 14), (2.0, 4.2), ['tan', 'steel'], [0.6, 0.4], [])
        ch.scatter(3, (-50.0, 58.0), (0, 10), (1.8, 3.6), ['tan', 'steel'], [0.5, 0.5], [])
        ch.scatter(3, (24.0, 10.0), (0, 10), (1.6, 3.2), ['tan', 'steel'], [0.6, 0.4], [])
        Hb = np.where(H > 0, H, 0.0)
        H, C, rock = ch.apply(x, y, H, C, rock, base=Hb)
        sc.H, sc.C = H.astype(np.float32), C.astype(np.int16)
        sc.extra.update(soot=soot, rock=rock)
        return sc
    return f


def mats(r, alb, level, p=None):
    if level < 1:
        return alb
    q = M.P if p is None else p
    lay = r.mk.get('layout', 'ts')
    x, y = M.to_local(r.x, r.y, lay)
    z, comp = r.z, r.comp
    top = r.nz > 0.75
    out = alb.copy()
    grain = WN.noise(x, y + z, 1.2, 1451) * 0.05
    g1 = (1 + grain)[..., None]
    house = np.isin(comp, list(M.HOUSE)) | ((comp == M.MAST) & (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])))
    dust = smoothstep(0.3, 1.3, WN.noise(x, y, 14, 1452)) * np.where(top, 0.3, 0.15) * ~house
    out = out * (1 - dust[..., None]) + DUST * g1 * dust[..., None]
    # paint chipped off the hull's, cab's and stripe's edges and corners: bare grey metal
    body = np.isin(comp, [M.HULL, M.STRIPE, M.CAB, M.WEDGE, M.MAST, M.LEG]) & ~house
    s_ = r.field('soot')
    chip = smoothstep(0.6, 0.9, WN.noise(x * 1.3, y * 1.3 + z, 2.6, 1453)) * body * 0.8 * smoothstep(0.08, 0.35, s_)
    chip *= np.where(comp == M.STRIPE, 1.6, 1.0)
    chip = np.clip(chip, 0, 1)
    out = out * (1 - chip[..., None]) + BARE * g1 * chip[..., None]
    # soot
    s = r.field('soot')
    soot = smoothstep(0.15, 0.7, np.clip(s * (0.65 + 0.35 * WN.noise(x, y + z, 6, 1454)), 0, 1)) * 0.85
    soot = soot * np.where(house, 0.22, 1.0)
    out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
    # the cab's window smashed: dark, cracks
    gl = comp == M.GLASS
    cn = WN.ridge(x + 0.4 * z, z - 0.6 * x, 4, 1455)
    out = np.where(gl[..., None], SMASH * g1 * (1 + 0.8 * (cn < 0.05))[..., None], out)
    # the plate's broken edge: fresh metal round the bite
    rock = r.field('rock')
    if rock.ndim == 3:
        out = np.where((comp == M.DEBRIS)[..., None], rock * (1 + 1.5 * grain)[..., None], out)
    return out
