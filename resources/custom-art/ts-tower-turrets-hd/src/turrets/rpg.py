"""TS GDI Component Tower RPG (GTCTWR_C), v2: three blocks side by side on a turntable -
  the launcher (the outer block, on the turret's left): two stacked tubes whose mouths are at the front,
      pitched up a little on a trunnion (the round hub on its outer side);
  the targeting sensor (the middle block): level, a lens in its front;
  the green (house colour) ammo box on the right, on two short struts.
Local frame: f forward, r right, z up from the turret's foot."""
import numpy as np
import tsdf as T

KH, STEEL, GREEN, DARK, KH_LT, STEEL_DK, RED, GLASS, BORE, BASE = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
CLS = {KH: 1, KH_LT: 1, STEEL: 2, STEEL_DK: 2, GREEN: 3, DARK: 4, RED: 4, GLASS: 4, BORE: 4, BASE: 1}

P0 = dict(lf=0.5, ll=55.0, lz0=9.0, lh=22.0, lb=4.0, rl=-8.25, wl=30.5, pa=0.0, pvf=-8.0, pvz=16.0,
          sf=0.5, sl=55.0, sz0=9.0, sh=22.0, sb=4.0, rr=23.0, wr=24.75,
          gf=1.0, gl=59.0, gr=54.0, gw=28.25, gz0=8.75, gh=16.5,
          bR=23.0, bh=11.0, px=24.5, py=12.1, zref=16.0)

RING_TOP = 83.2 - (160.0 - 83.7) / np.cos(np.deg2rad(32.0))   # the ring's top, relative to the pivot height


def pitch(p):
    """the launcher's pitch: (angle, pivot f, pivot z) for tsdf's 'pitch'."""
    return (p['pa'], p['pvf'], p['pvz'])


def launcher_box(p):
    return T.slab_box((p['lf'], p['rl'], p['lz0'] + p['lh'] / 2), (p['ll'] / 2, p['wl'] / 2, p['lh'] / 2),
                      bevel_top=p['lb'], bevel_side=2.0, top_axes='r', comp=KH, pitch=pitch(p))


def sensor_box(p):
    return T.slab_box((p['sf'], p['rr'], p['sz0'] + p['sh'] / 2), (p['sl'] / 2, p['wr'] / 2, p['sh'] / 2),
                      bevel_top=p['sb'], bevel_side=2.0, top_axes='r', comp=KH)


def parts(p=P0, recoil=0.0, big_base=False):
    if big_base:
        # a turntable filling the tower's ring (so the grey plug never shows): just over the ring's inner
        # edge, its top a little above the ring
        top = p['zref'] + RING_TOP + 1.4
        out = [T.cyl('z', (0.0, 0.0, 0.0), -3.0, top, 31.6, comp=BASE)]
    else:
        out = [T.cyl('z', (0.0, 0.0, 0.0), -2.0, p['bh'], p['bR'], comp=KH)]
    out.append(launcher_box(p))
    out.append(sensor_box(p))
    out.append(T.box((p['gf'], p['gr'], p['gz0'] + p['gh'] / 2), (p['gl'] / 2, p['gw'] / 2, p['gh'] / 2),
                     rd=3.0, comp=GREEN))                                                            # ammo box
    for fs in (-0.32, 0.32):                                                                          # struts
        out.append(T.box((p['gf'] + fs * p['gl'], p['gr'], p['gz0'] / 2 - 1.0), (3.0, 4.0, p['gz0'] / 2 + 1.0),
                         rd=0.8, comp=STEEL_DK))
    return out


def bounds(p=P0):
    ext = max(abs(p['lf']) + p['ll'] / 2, abs(p['sf']) + p['sl'] / 2, abs(p['gf']) + p['gl'] / 2) + 8
    lo = (-ext, min(p['rl'] - p['wl'] / 2, -p['bR']) - 6, -3)
    hi = (ext, max(p['gr'] + p['gw'] / 2, p['rr'] + p['wr'] / 2) + 4,
          max(p['lz0'] + p['lh'], p['sz0'] + p['sh'], p['gz0'] + p['gh']) + 14)
    return lo, hi


# ----------------------------------------------------------------------------- HD detail and materials
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import ct_ra as _R
from walls2 import sample as _sample, phase as _phase, smoothstep as _ss, NOISE_MOTTLE as _NM

TUBE_R = 0.15            # tube radius as a fraction of the launcher's height (x 0.9)
LIP = 1.0                # the steel lip round each mouth


def tubes(p):
    """(r, z, R) of the launcher's two tube mouths (unpitched), stacked with a clear gap between them."""
    R = TUBE_R * min(p['wl'], p['lh'] * 0.9)
    return [(p['rl'], p['lz0'] + zf * p['lh'], R) for zf in (0.26, 0.74)]


def hub(p):
    """the trunnion hub on the launcher's outer side: (f, z, R, r of the side face)."""
    return p['pvf'], p['pvz'], 0.27 * p['lh'], p['rl'] - p['wl'] / 2


def lens(p):
    """the sensor's lens: (f of the front face, r, z, R)."""
    R = 0.30 * min(p['wr'], p['sh'])
    return p['sf'] + p['sl'] / 2, p['rr'], p['sz0'] + 0.58 * p['sh'], R


def parts_hd(p=P0, damaged=False):
    out = parts(p, big_base=True)
    pt = pitch(p)
    f1, f0 = p['lf'] + p['ll'] / 2, p['lf'] - p['ll'] / 2
    for rc, zc, R in tubes(p):
        # the tube mouths bored into the launcher's front, a steel lip round each; scorched rear ends
        out.append(T.cyl('f', (0.0, rc, zc), f1 - 1.2, f1 + 1.0, R + LIP, comp=STEEL, pitch=pt))
        out.append(dict(T.cyl('f', (0.0, rc, zc), f1 - 10.0, f1 + 3.0, R, pitch=pt), sub=True, comp_in=BORE))
        out.append(T.cyl('f', (0.0, rc, zc), f0 - 1.5, f0 + 1.0, R + 0.8, comp=STEEL_DK, pitch=pt))
        out.append(dict(T.cyl('f', (0.0, rc, zc), f0 - 3.0, f0 + 2.0, R * 0.7, pitch=pt), sub=True, comp_in=RED))
    # the trunnion hub the launcher tilts on (round, so the pitch doesn't change it)
    hf, hz, hR, hr = hub(p)
    out.append(T.cyl('r', (hf, 0.0, hz), hr - 2.2, hr + 1.0, hR, comp=RED))
    out.append(T.cyl('r', (hf, 0.0, hz), hr - 3.0, hr + 1.0, hR * 0.55, comp=BORE))
    # the sensor: a lens in a steel bezel in its front, a seam round its nose
    sf1, lr, lz, lR = lens(p)
    out.append(T.cyl('f', (0.0, lr, lz), sf1 - 1.0, sf1 + 1.6, lR + 2.2, comp=STEEL))
    out.append(dict(T.cyl('f', (0.0, lr, lz), sf1 - 4.0, sf1 + 3.0, lR), sub=True, comp_in=DARK))
    out.append(T.cyl('f', (0.0, lr, lz), sf1 - 4.5, sf1 - 0.8, lR - 0.05, comp=GLASS))
    # the ammo box: a lid seam and two handles on its outer side
    gtop = p['gz0'] + p['gh']
    out.append(T.box((p['gf'], p['gr'], gtop - 3.5), (p['gl'] / 2 + 0.6, p['gw'] / 2 + 0.6, 0.7), rd=0.5, comp=STEEL_DK))
    for fs in (-0.25, 0.25):
        out.append(T.box((p['gf'] + fs * p['gl'], p['gr'] + p['gw'] / 2 + 1.0, gtop - 9.0), (3.5, 1.2, 1.0), rd=0.6,
                         comp=STEEL_DK))
    # a bearing band round the turntable's rim
    top = p['zref'] + RING_TOP + 1.4
    out.append(T.cyl('z', (0.0, 0.0, 0.0), top - 1.6, top - 0.4, 32.0, comp=STEEL_DK))
    return out


GLASS_C = np.array([34, 44, 58.])
RUST = np.array([120, 66, 50.])


def albedo(comp, Lp, nl, grain, u, v, p=P0):
    f, r, z = Lp[:, 0], Lp[:, 1], Lp[:, 2]
    g = (1 + grain)[:, None]
    top = nl[:, 2] > 0.75
    kh = _R.KHAKI * (1 + 1.2 * grain)[:, None]
    seam = (_phase(f - p['lf'], 14.0, 7.0) < 0.5) & ~top & (np.abs(nl[:, 1]) > 0.7)       # panel seams on the sides
    kh = np.where(seam[:, None], kh * 0.84, kh)
    kh = np.where(top[:, None], _R.KHAKI_LT * (1 + 1.2 * grain)[:, None], kh)
    streak = _ss(0.3, 1.3, _sample(_NM, u * 3.0, 5.0 + 0 * v)) * ~top * 0.12
    kh = kh * (1 - streak)[:, None]
    # the lens: dark glass, a glint at its upper left
    sf1, lr, lz, lR = lens(p)
    glint = np.clip(1 - np.hypot(r - (lr - 0.36 * lR), z - (lz + 0.36 * lR)) / (0.26 * lR), 0, 1) ** 1.2
    tz = np.clip((z - (lz - lR)) / (2 * lR), 0, 1) ** 1.4                  # the glass mirrors the sky at the top
    glass = np.array([26, 36, 50.]) + (np.array([92, 118, 146.]) - np.array([26, 36, 50.])) * tz[:, None]
    glass = glass + (np.array([226, 234, 240.]) - glass) * glint[:, None]
    gr = _R.GREEN * (1 + 0.5 * grain)[:, None]
    alb = np.zeros((len(comp), 3))
    for k, c in ((KH, kh), (BASE, _R.KHAKI * 0.84 * (1 + 1.2 * grain)[:, None]), (KH_LT, _R.KHAKI_LT * g), (STEEL, _R.STEEL * g), (STEEL_DK, np.array([84, 86, 92.]) * g),
                 (GREEN, gr), (DARK, np.array([24, 22, 22.]) * g), (RED, RUST * g), (GLASS, glass),
                 (BORE, np.array([30, 12, 10.]) * g)):
        alb = np.where((comp == k)[:, None], c, alb)
    return alb, comp == GREEN


def chip_points(p=P0):
    f0, f1 = p['lf'] - p['ll'] / 2, p['lf'] + p['ll'] / 2
    ltop, stop = p['lz0'] + p['lh'], p['sz0'] + p['sh']
    return [(p['sf'] + p['sl'] / 2 - 1.0, p['rr'] + p['wr'] / 2 - 1.0, stop - 1.0),
            (p['sf'] - p['sl'] / 2 + 2.0, p['rr'] + p['wr'] / 2 - 1.0, stop - 2.0),
            (p['gf'] + p['gl'] / 2 - 1.0, p['gr'] + p['gw'] / 2 - 1.0, p['gz0'] + p['gh'] - 1.0),
            (f0 + 6.0, p['rl'] - p['wl'] / 2, ltop - 3.0)]


def scorch(p=P0):
    f0, f1 = p['lf'] - p['ll'] / 2, p['lf'] + p['ll'] / 2
    zc = p['lz0'] + p['lh'] / 2
    return ((f0 - 2.0, p['rl'], zc - 3.0, 14.0), (f1 + 2.0, p['rl'], zc + 4.0, 12.0), (p['sf'] - 10.0, p['rr'], p['sz0'] + p['sh'], 10.0))


def unpitch(p, pts):
    """points given in the launcher's own (unpitched) frame -> the turret's frame."""
    a, f0, z0 = pitch(p)
    ca, sa = np.cos(a), np.sin(a)
    out = []
    for f, r, z in pts:
        qf, qz = f - f0, z - z0
        out.append((f0 + qf * ca - qz * sa, r, z0 + qf * sa + qz * ca))
    return out


def aim_points(p=P0, recoil=0.0):
    """the launcher's two tube mouths: lower, then upper."""
    f1 = p['lf'] + p['ll'] / 2
    return unpitch(p, [(f1 + 0.5, rc, zc) for rc, zc, R in tubes(p)])
