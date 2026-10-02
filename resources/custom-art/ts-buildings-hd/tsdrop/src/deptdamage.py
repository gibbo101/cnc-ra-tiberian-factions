"""
Damage for the Service Depot (TS GTDEPT 01 + GTDEPTBB 01; RA has healthy and damaged only), as TS breaks it:
  pad     cracked all over; a big blast in its north-east quarter inside the band (the slabs broken, sunk and tilted,
          scorched, rubble on them), a smaller scorch on the gratings; its west and north-east corners knocked off
  wall    its north end broken off at the top (a jagged break through the rail and its lamps), sooted
  hoods   the north hood dented in, a hole torn in its front
Greys and browns only, in the building's own frame so both views match.
"""
import numpy as np
import dept as M, wnoise as WN
from walls2 import smoothstep
from radr import dblob
from weapdamage import Chunks

SOOT = np.array([30, 29, 28.])
FRESH = np.array([190, 188, 180.])
DUST = np.array([112, 104, 84.])
INSIDE_D = np.array([40, 38, 40.])

BLAST = (58.0, -58.0, 40.0, 38.0)            # the pad's blast (relative to its centre): x, y, rx, ry
SCORCH2 = (-36.0, -38.0, 18.0, 12.0)         # the smaller scorch on the gratings
BITES = ((-128.0, 38.0, 14.0, 22.0), (92.0, -100.0, 18.0, 12.0))      # the pad's corners knocked off (relative)
WALL_BREAK = -58.0                           # the wall's north end breaks off north of this y


def model(level, p=None):
    def f(X, Yy, **kw):
        q = M.P if p is None else p
        sc = M.scene(X, Yy, p=q, **kw)
        if level < 1:
            return sc
        lay = kw.get('layout', 'ts')
        x, y = M.to_local(X, Yy, lay)
        H, C = sc.H.copy(), sc.C.copy()
        soot = np.zeros(X.shape, np.float32); broken = np.zeros(X.shape, np.float32)
        pq = q['pad']
        cx, cy = pq['c']
        rx_, ry_ = x - cx, y - cy
        rock = np.zeros(H.shape + (3,), np.float32)
        ch = Chunks(1010)
        padc = np.isin(C, [M.PAD, M.GRATE, M.GAP, M.RIM, M.BAND, M.SKIRT])
        if padc.any():
            # the blast: the slabs inside it broken up (sunk, tilted plates), scorched; rubble on them
            bx_, by_, brx, bry = BLAST
            e = dblob(rx_, ry_, bx_, by_, brx, bry, 0.35, 1011, feat=10.0)
            inb = padc & (e < 0) & (C != M.BAND)
            cell = WN.noise(np.floor(rx_ / 14.0) * 14.0, np.floor(ry_ / 14.0) * 14.0, 3.0, 1012)
            tilt = (rx_ % 14.0 - 7.0) * 0.12 * cell + (ry_ % 14.0 - 7.0) * 0.1 * WN.noise(np.floor(rx_ / 14.0), np.floor(ry_ / 14.0), 1.0, 1013)
            sink = (2.5 + 2.0 * np.clip(-e * 2, 0, 1)) + tilt
            H = np.where(inb, np.maximum(H - np.clip(sink, 0.5, 6.0), 1.0), H)
            C = np.where(inb & (np.clip(-e * 3, 0, 1) > 0.7) & (WN.noise(rx_, ry_, 8.0, 1014) > 0.35), M.DEB_BURNT, C)
            soot = np.maximum(soot, 0.68 * np.clip(0.85 - e, 0, 1) * padc)
            broken = np.maximum(broken, (padc & (e >= 0) & (e < 0.18)) * 0.7)
            # the smaller scorch on the gratings
            sx_, sy_, srx, sry = SCORCH2
            e2 = dblob(rx_, ry_, sx_, sy_, srx, sry, 0.4, 1015, feat=6.0)
            soot = np.maximum(soot, 0.85 * np.clip(0.8 - e2, 0, 1) * padc)
            in2 = padc & (e2 < -0.3) & (C != M.BAND)
            H = np.where(in2, H - 1.5, H)
            # the corners knocked off
            for i, (kx, ky, krx, kry) in enumerate(BITES):
                eb = dblob(rx_, ry_, kx, ky, krx, kry, 0.45, 1016 + i, feat=5.0)
                gone = padc & (eb < 0)
                H = np.where(gone, 0.0, H); C = np.where(gone, 0, C)
                broken = np.maximum(broken, (padc & (eb >= 0) & (eb < 0.4)) * 0.8)
            ch.scatter(9, (cx + bx_, cy + by_), (0, 34), (2.2, 5.6), ['conc', 'steel'], [0.8, 0.2], [])
            ch.scatter(4, (cx - 128.0, cy + 40.0), (10, 30), (2.0, 4.6), ['conc'], [1.0], [])
            ch.scatter(3, (cx + 96.0, cy - 104.0), (6, 22), (2.0, 4.2), ['conc'], [1.0], [])
        gant = np.isin(C, [M.WALL, M.BASE, M.MACH, M.HOOD, M.HOODIN, M.BOX, M.BROWN, M.GTRIM])
        if gant.any() or any(np.isin(s.comp, [M.RAIL, M.STUD, M.PANEL, M.FRAME, M.HOOD]).any() for s in sc.slabs):
            wl = q['wall']
            # the wall's north end broken off: a jagged line falling from z 70 at the break to z 34 at the end
            jag = WN.noise(x, y, 4.0, 1021) * 5.0 + WN.noise(x, y, 11.0, 1022) * 4.0
            north = y < WALL_BREAK
            zcut = np.where(north, 66.0 - (WALL_BREAK - y) * 1.6 + jag, 1e9)
            wm = (C == M.WALL) & north
            H = np.where(wm, np.minimum(H, np.maximum(zcut, 26.0)), H)
            broken = np.maximum(broken, (wm & (H >= zcut - 3.0)) * 0.9)
            for s in sc.slabs:
                ok = (s.top >= 0) & north & np.isin(s.comp, [M.RAIL, M.STUD, M.PANEL, M.FRAME])
                s.top = np.where(ok, np.where(np.minimum(s.top, zcut) > s.bot + 1.0, np.minimum(s.top, zcut), -1.0), s.top)
            soot = np.maximum(soot, 0.7 * np.exp(-((x - wl['x'][1]) ** 2 / 30.0 ** 2 + (y - WALL_BREAK + 8.0) ** 2 / 26.0 ** 2)))
            # the north hood dented, a hole in its front
            hd_ = q['mach']['hoods']
            yc = hd_['ys'][1]
            hx = hd_['x'][1]
            for s in sc.slabs:
                ok = (s.top >= 0) & (s.comp == M.HOOD) & (np.abs(y - yc) <= hd_['w'] / 2 + 1)
                dent = 5.0 * np.clip(1.0 - np.hypot(x - hx + 4.0, y - yc - 3.0) / 12.0, 0, 1) + 1.5 * WN.noise(x, y, 4.0, 1023)
                s.top = np.where(ok, np.maximum(s.top - np.maximum(dent, 0), s.bot + 1.0), s.top)
            eh = dblob(x, y, hx - 1.0, yc + 4.0, 5.0, 4.0, 0.3, 1024, feat=3.0)
            for s in sc.slabs:
                hole = (s.top >= 0) & (s.comp == M.HOOD) & (eh < 0)
                s.comp = np.where(hole, M.DEB_IN, s.comp).astype(np.int16)
            soot = np.maximum(soot, 0.6 * np.exp(-((x - hx) ** 2 + (y - yc) ** 2) / 22.0 ** 2))
            soot = np.maximum(soot, 0.45 * np.exp(-((x + 150.0) ** 2 + (y - 10.0) ** 2) / 40.0 ** 2))
            ch.scatter(5, (-150.0, -66.0), (4, 24), (2.0, 4.6), ['steel', 'tan'], [0.6, 0.4], [])
            ch.scatter(3, (-118.0, 8.0), (4, 14), (1.8, 3.6), ['steel'], [1.0], [])
        H, C, rock = ch.apply(x, y, H, C, rock, base=np.where(H > 0, H, 0.0))
        sc.H, sc.C = H.astype(np.float32), C.astype(np.int16)
        sc.extra.update(soot=soot, broken=broken, rock=rock)
        return sc
    return f


def mats(r, alb, level, p=None):
    if level < 1:
        return alb
    p = M.P if p is None else p
    lay = r.mk.get('layout', 'ts')
    x, y = M.to_local(r.x, r.y, lay)
    z, comp = r.z, r.comp
    top = r.nz > 0.75
    out = alb.copy()
    grain = WN.noise(x, y + z, 1.2, 1051) * 0.05
    g1 = (1 + grain)[..., None]
    house = np.isin(comp, list(M.HOUSE))
    dust = smoothstep(0.3, 1.3, WN.noise(x, y, 14, 1052)) * np.where(top, 0.3, 0.15) * ~house
    out = out * (1 - dust[..., None]) + DUST * g1 * dust[..., None]
    s = r.field('soot')
    soot = smoothstep(0.15, 0.7, np.clip(s * (0.65 + 0.35 * WN.noise(x, y + z, 6, 1053)), 0, 1)) * 0.88
    soot = soot * np.where(house, 0.22, 1.0)
    out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
    # cracks all over the pad (TS's damaged pad is cracked from edge to edge), the wall, the hoods
    cz = np.isin(comp, [M.PAD, M.RIM, M.SKIRT, M.GRATE, M.WALL, M.HOOD])
    cn = WN.ridge(x + 0.4 * z, y - 0.6 * z, 8, 1055) + 0.12 * np.abs(WN.noise(x, y + z, 1.5, 1056))
    cmask = smoothstep(0.2, 0.9, WN.noise(x, y, 30, 1057)) + 1.0 * np.isin(comp, [M.PAD, M.RIM, M.GRATE])
    crack = (1 - smoothstep(0.015, 0.065, cn)) * np.clip(cmask, 0, 1) * cz * ~house
    out *= (1 - 0.6 * crack)[..., None]
    brk = np.clip(r.field('broken') * 1.4, 0, 1) * ~house
    out = out * (1 - brk[..., None]) + FRESH * 0.75 * brk[..., None]
    out = np.where((comp == M.DEB_BURNT)[..., None], np.array([80, 76, 78.]) * (1 + 2 * grain)[..., None], out)
    out = np.where((comp == M.DEB_IN)[..., None], INSIDE_D * g1, out)
    rock = r.field('rock')
    if rock.ndim == 3:
        out = np.where((comp == M.DEBRIS)[..., None], rock * (1 + 1.5 * grain)[..., None], out)
    return out
