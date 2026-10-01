"""
Damage for the Tiberium Silo (TS GTSILO frame 1; RA has healthy and damaged only), as TS breaks it:
  blades the west blade's buttress broken away below the bend (bits of it on the ground), the east one's foot
         snapped off and lying by it; two lamps dead (TS's damaged GTSILO_B lights 3 of 5)
  lid    a hole blown in it (the dark inside showing), cracks across the glass, soot round the hole
  pump   the loader's top torn, soot
  ground soot on the body and the earth, rubble (glass, blade, steel) round the foot
"""
import numpy as np
import hd, silo as SL, wnoise as WN
from walls2 import smoothstep
from pdamage import Chunks, blob

DEBRIS = 40
SOOT = np.array([30, 29, 28.])
FRESH = np.array([206, 198, 180.])
DUST = np.array([120, 110, 92.])
INSIDE = np.array([28, 30, 36.])
ROCK = {'glass': np.array([152, 158, 188.]) * 0.85, 'green': np.array([0, 214, 0.]) * 0.8,
        'steel': np.array([110, 112, 120.]), 'earth': np.array([96, 82, 62.])}
HOLE = (-34.0, 2.0, 16.0, 12.0, 701)        # offset from the silo's middle, radii, seed
BROKEN = 4                   # the west blade: its buttress gone below the bend
SNAPPED = 2                  # the east blade: its foot snapped off
DEAD = (0, 2)                # lamps that no longer light (TS's damaged set lights 3 of 5)


class SiloChunks(Chunks):
    def apply(self, X, Y, H, C, rock, base_h=0.0):
        for (cx, cy, rr, kind, ang, dk, topz, tilt, steep, shade) in self.items:
            win = (np.abs(X - cx) < 2 * rr + 2) & (np.abs(Y - cy) < 2 * rr + 2)
            if not win.any():
                continue
            ddx, ddy = X[win] - cx, Y[win] - cy
            g = np.max([np.cos(a) * ddx + np.sin(a) * ddy - d for a, d in zip(ang, dk)], axis=0)
            h = np.clip(-g * steep, 0, None)
            h = np.minimum(h, np.clip(topz + tilt[0] * ddx + tilt[1] * ddy, 0.4, None)) * (g < 0)
            base = np.minimum(H[win], base_h + 1.0)
            hh = np.where(h > 0, h + base, 0)
            full = np.zeros_like(H); full[win] = hh
            m = full > H
            H[m] = full[m]; C[m] = DEBRIS
            rock[m] = ROCK[kind] * shade
        return H, C, rock


def model(level, p=SL.P):
    def f(X, Yy, **kw):
        sc = SL.scene(X, Yy, p=p, **kw)
        return damage_scene(sc, X, Yy, level, SL.geo(kw.get('layout', 'ts'), p))
    return f


def damage_scene(sc, X, Yy, level, p=SL.P):
    if level < 1:
        return sc
    H = sc.H.copy(); C = sc.C.copy()
    soot = np.zeros_like(H); broken = np.zeros_like(H)
    rock = np.zeros(H.shape + (3,), np.float32)
    cx, cy = p['centre']
    jag = WN.noise(X, Yy, 2.2, 711)
    # ---- the hole in the lid
    hx, hy, rx, ry, seed = HOLE
    e = blob(X, Yy, cx + hx, cy + hy, rx, ry, 0.5, seed, feat=4.0)
    hole = e < 0
    for s in sc.slabs:
        if s.name == 'lid':
            s.top = np.where(hole & (s.top >= 0), -1.0, s.top)
    broken = np.maximum(broken, ((e >= 0) & (e < 0.4)) * 0.8)
    inside = hole & (np.hypot(X - cx, Yy - cy) < p['skirt'][1])
    H = np.where(inside, np.maximum(H, p['skirt'][2] - 6.0), H)
    C = np.where(inside, DEBRIS + 1, C)
    soot = np.maximum(soot, 0.95 * np.exp(-(((X - cx - hx) / (rx * 2.2)) ** 2 + ((Yy - cy - hy) / (ry * 2.4)) ** 2)))

    def blade_frame(k):
        a = p['fins_az'][k]
        ux, uy = np.cos(a), np.sin(a)
        return (X - cx) * ux + (Yy - cy) * uy, -(X - cx) * uy + (Yy - cy) * ux, ux, uy
    # ---- the west blade: its buttress gone below the bend, a ragged stub left
    al, ac, ux, uy = blade_frame(BROKEN)
    claw = (C == SL.FIN) & (np.abs(ac) < 26.0) & (al > p['root_r'])
    gone = claw & (al > p['lamp_r'] - 4.0 + 6.0 * jag)
    stub = claw & (al > p['lamp_r'] - 12.0) & ~gone
    H = np.where(gone, 0.0, np.where(stub, np.minimum(H, SL.lamp_z(p) - 10.0 + 6.0 * jag), H))
    C = np.where(gone, 0, C)
    soot = np.maximum(soot, 0.6 * np.exp(-((al - p['lamp_r']) ** 2 + ac ** 2) / 16.0 ** 2))
    fx, fy = cx + (p['foot_r'] - 10) * ux, cy + (p['foot_r'] - 10) * uy
    # ---- the east blade: its foot snapped off below the stepped edge's middle
    al2, ac2, ux2, uy2 = blade_frame(SNAPPED)
    snap_r = p['lamp_r'] + 0.55 * (p['foot_r'] - p['lamp_r'])
    claw2 = (C == SL.FIN) & (np.abs(ac2) < 26.0) & (al2 > p['root_r'])
    gone2 = claw2 & (al2 > snap_r + 4.0 * jag)
    H = np.where(gone2, 0.0, H)
    C = np.where(gone2, 0, C)
    # the snapped piece lying flat beside its foot: a green wedge on the ground
    ox, oy = cx + (p['foot_r'] - 6) * ux2 - 16 * uy2, cy + (p['foot_r'] - 6) * uy2 + 16 * ux2
    pa = (X - ox) * ux2 + (Yy - oy) * uy2
    pc = -(X - ox) * uy2 + (Yy - oy) * ux2
    piece = (pa > -18) & (pa < 10) & (np.abs(pc) < 6.0 * np.clip((10 - pa) / 28.0, 0.15, 1)) & (np.hypot(X, Yy) < 136)
    H = np.where(piece, np.maximum(H, 3.5 + 1.0 * jag), H)
    C = np.where(piece, DEBRIS + 2, C)
    # ---- the loader: its top torn
    pm = p['pump']
    pcx, pcy = cx + pm['off'][0], cy + pm['off'][1]
    for s in sc.slabs:
        if s.name == 'pump':
            torn = (s.top >= 0) & ((X - pcx) + 0.6 * (Yy - pcy) > -6.0 + 8.0 * jag)
            s.top = np.where(torn, np.minimum(s.top, pm['z'] - 14.0 + 6.0 * jag), s.top)
    soot = np.maximum(soot, 0.7 * np.exp(-((X - pcx) ** 2 + (Yy - pcy) ** 2) / 22.0 ** 2))
    # ---- soot on the body and round the foot
    for (sx, sy, rr) in ((cx + 40, cy + 50, 26.0), (cx - 60, cy + 30, 24.0), (cx + 60, cy - 40, 22.0)):
        soot = np.maximum(soot, 0.6 * np.exp(-((X - sx) ** 2 + (Yy - sy) ** 2) / rr ** 2))
    # ---- rubble: bits of the west buttress, glass, steel
    chunks = SiloChunks(720)
    chunks.scatter(9, (fx, fy), (2, 24), (2.4, 5.6), ['green', 'glass', 'steel'], [0.6, 0.2, 0.2], [])
    chunks.scatter(6, (cx + 20, cy + 96), (2, 18), (2.2, 4.6), ['glass', 'earth', 'steel'], [0.4, 0.35, 0.25], [(pcx, pcy, 22.0)])
    chunks.scatter(5, (pcx - 6, pcy + 4), (14, 24), (2.2, 4.4), ['steel', 'earth'], [0.6, 0.4], [])
    H, C, rock = chunks.apply(X, Yy, H, C, rock, 0.0)
    sc.H, sc.C = H.astype(np.float32), C.astype(np.int16)
    sc.extra.update(soot=soot.astype(np.float32), broken=broken.astype(np.float32), rock=rock)
    return sc


def mats(r, alb, level, p=SL.P):
    if level < 1:
        return alb
    p = SL.geo(r.mk.get('layout', 'ts'), p)
    x, y, z, comp = r.x, r.y, r.z, r.comp
    top = r.nz > 0.75
    out = alb.copy()
    grain = WN.noise(x, y + z, 1.2, 741) * 0.05
    g1 = (1 + grain)[..., None]
    house = comp == SL.FIN
    dust = smoothstep(0.3, 1.3, WN.noise(x, y, 14, 742)) * np.where(top, 0.4, 0.2) * ~house
    out = out * (1 - dust[..., None]) + DUST * g1 * dust[..., None]
    s = r.field('soot')
    soot = smoothstep(0.15, 0.7, np.clip(s * (0.65 + 0.35 * WN.noise(x, y + z, 6, 743)), 0, 1)) * 0.85
    soot = soot * np.where(house, 0.45, 1.0)
    out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
    # cracks across the glass and the body
    cz = np.isin(comp, [SL.LID, SL.SKIRT, SL.SLAB])
    cn = WN.ridge(x + 0.4 * z, y - 0.6 * z, 7, 744) + 0.12 * np.abs(WN.noise(x, y + z, 1.5, 745))
    cmask = np.maximum(smoothstep(0.5, 1.2, WN.noise(x, y, 26, 746)), (comp == SL.LID) * 0.8)
    crack = (1 - smoothstep(0.015, 0.06, cn)) * cmask * cz
    out *= (1 - 0.6 * crack)[..., None]
    brk = np.clip(r.field('broken') * 1.4, 0, 1) * (comp == SL.LID)
    out = out * (1 - brk[..., None]) + FRESH * 0.8 * brk[..., None]
    ins = comp == DEBRIS + 1
    out = np.where(ins[..., None], INSIDE * (0.8 + 0.3 * WN.noise(x, y, 2.0, 747))[..., None] * g1, out)
    piece = comp == DEBRIS + 2
    out = np.where(piece[..., None], np.array([0, 214, 0.]) * 0.85 * g1, out)
    rock = r.field('rock')
    out = np.where((comp == DEBRIS)[..., None], rock * (1 + 1.5 * grain)[..., None], out)
    return out
