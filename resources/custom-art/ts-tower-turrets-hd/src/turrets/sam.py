"""TS GDI Component Tower SAM (GTCTWR_D), v2: a low khaki missile box on trunnions. Its front is a short
upright strip and then the launch face, a shallow slope (the missiles point steeply up) with two rows of
four cells in pairs; behind it the top falls gently to a short back with a row of vents. On the top, set
back and to the turret's left, a green (house colour) collar carrying a flat grey radar plate.
Local frame: f forward, r right, z up from the turret's foot."""
import numpy as np
import tsdf as T

KH, STEEL, GREEN, DARK, KH_LT, STEEL_DK, RED, NOSE_M, BASE, PLATE = 1, 2, 3, 4, 5, 6, 7, 8, 10, 11
CLS = {KH: 1, KH_LT: 1, STEEL: 2, STEEL_DK: 4, GREEN: 3, DARK: 4, RED: 4, NOSE_M: 4, BASE: 1, PLATE: 2}

P0 = dict(bf=-3.0, L=76.0, W=48.5, bz0=8.0, hv=6.0, tb=1.05, Lf=36.0, hb=16.0, bt=1.5,
          tf=1.0, tz=13.0, tr=11.5, tw=9.0,
          sf=-22.0, sr=-8.0, cl=16.0, cw=18.0, gh=5.0, pw=26.0, phh=15.0, pt=0.3, ms=2.0,
          bR=24.0, bh=10.0, px=24.6, py=12.9, zref=15.0)

RING_TOP = 83.2 - (160.0 - 83.7) / np.cos(np.deg2rad(32.0))   # the ring's top, relative to the pivot height


def geom(p):
    """the box's side profile: front f1, back f0, the face's foot (f1, zf), its top edge E, the back top B."""
    f1, f0 = p['bf'] + p['L'] / 2, p['bf'] - p['L'] / 2
    zf = p['bz0'] + p['hv']
    E = (f1 - p['Lf'] * np.sin(p['tb']), zf + p['Lf'] * np.cos(p['tb']))
    B = (f0, p['bz0'] + p['hb'])
    return f1, f0, zf, E, B


def ztop(p, f):
    """the top's height at f (behind the face)."""
    f1, f0, zf, E, B = geom(p)
    return E[1] + (f - E[0]) * (B[1] - E[1]) / (B[0] - E[0])


def face(p):
    """the launch face: its normal n and at(s, t, out) -> local point (s 0..1 up the face, t -1..1 across,
    out along the normal)."""
    f1, f0, zf, E, B = geom(p)
    n = (np.cos(p['tb']), 0.0, np.sin(p['tb']))

    def at(s, t, out=0.0):
        return (f1 + (E[0] - f1) * s + n[0] * out, t * p['W'] / 2, zf + (E[1] - zf) * s + n[2] * out)
    return n, at


def box_planes(p):
    f1, f0, zf, E, B = geom(p)
    hw = p['W'] / 2
    n, _ = face(p)
    vf, vz = B[0] - E[0], B[1] - E[1]                  # along the top, front to back
    nt = np.array([vz, 0.0, -vf]); nt = nt / np.linalg.norm(nt)
    dt = nt[0] * E[0] + nt[2] * E[1]
    pl = [(n, n[0] * f1 + n[2] * zf), ((1, 0, 0), f1), ((-1, 0, 0), -f0), ((0, 1, 0), hw), ((0, -1, 0), hw),
          (tuple(nt), dt), ((0, 0, -1), -p['bz0'])]
    if p['bt'] > 0:
        for s in (1, -1):
            pl.append(((nt[0], s * 1.0, nt[2]), dt + hw - p['bt']))           # chamfered top side edges
            pl.append(((n[0], s * 1.0, n[2]), n[0] * f1 + n[2] * zf + hw - p['bt']))
    return pl


def cells(p):
    """the 2 x 4 missile cells, in pairs: (centre on the face, half width across, half height up the face)."""
    _, at = face(p)
    out = []
    for s in (0.3, 0.7):
        for t in (-0.66, -0.24, 0.24, 0.66):
            out.append((at(s, t), p['W'] * 0.058, p['Lf'] * 0.105))
    return out


def sensor(p):
    """the collar's centre (f, r, z of its foot) on the top."""
    f = p['bf'] + p['sf']
    return f, p['sr'], ztop(p, f)


def parts(p=P0, big_base=False):
    if big_base:
        top = p['zref'] + RING_TOP + 1.4
        out = [T.cyl('z', (0.0, 0.0, 0.0), -3.0, top, 31.6, comp=BASE)]
    else:
        out = [T.cyl('z', (0.0, 0.0, 0.0), -2.0, p['bh'], p['bR'], comp=KH)]                      # turntable
    out.append(T.poly(box_planes(p), comp=KH))
    # the trunnions
    out.append(T.cyl('r', (p['tf'], 0.0, p['tz']), -(p['W'] / 2 + p['tw']), p['W'] / 2 + p['tw'], p['tr'], comp=STEEL_DK))
    # the sensor: green collar, a short mast, the grey plate tilted back
    sf, sr, sz = sensor(p)
    out.append(T.box((sf, sr, sz + p['gh'] / 2 - 1.0), (p['cl'] / 2, p['cw'] / 2, p['gh'] / 2 + 1.0), rd=1.0, comp=GREEN))
    pz = sz + p['gh'] + p['ms']
    out.append(T.box((sf, sr, pz + p['phh'] / 2), (1.4, p['pw'] / 2, p['phh'] / 2), rd=0.8, comp=PLATE,
                     pitch=(p['pt'], sf, pz)))
    out.append(T.cyl('z', (sf, sr, 0.0), sz + p['gh'] - 1.0, pz + 2.0, 2.2, comp=STEEL_DK))
    # the cells, as thin dark plates on the face (for the fit; the HD model bores them)
    for c, hw_, hh in cells(p):
        out.append(T.box(c, (1.2, hw_, hh), comp=DARK, pitch=(p['tb'], c[0], c[2])))
    return out


def bounds(p=P0):
    ext = p['L'] / 2 + abs(p['bf']) + 8
    return (-ext, -(p['W'] / 2 + p['tw'] + 6), -3), (ext, p['W'] / 2 + p['tw'] + 6,
                                                     max(geom(p)[3][1], p['bz0'] + p['hb']) + p['gh'] + p['ms'] + p['phh'] + 8)


# ----------------------------------------------------------------------------- HD detail and materials
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import ct_ra as _R
from walls2 import sample as _sample, phase as _phase, smoothstep as _ss, NOISE_MOTTLE as _NM

NOSE = np.array([214, 212, 204.])


def parts_hd(p=P0, damaged=False):
    """the fitted shape with its detail: the eight cells bored into the launch face with a missile nose in
    each, trunnion hubs, the radar plate with a rim and a bracket behind, vents along the back's foot, and
    a turntable filling the tower's ring."""
    out = [q for q in parts(p, big_base=True) if q['comp'] != DARK]
    n, at = face(p)
    for c, hw_, hh in cells(p):
        lip = T.box(c, (1.0, hw_ + 1.3, hh + 1.3), rd=0.7, comp=STEEL_DK, pitch=(p['tb'], c[0], c[2]))
        out.append(lip)
        cell = T.box(c, (7.0, hw_, hh), rd=0.6, pitch=(p['tb'], c[0], c[2]))
        out.append(dict(cell, sub=True, comp_in=DARK))
        nose_c = (c[0] - n[0] * 3.0, c[1], c[2] - n[2] * 3.0)
        out.append(T.sph(nose_c, min(hw_, hh) * 0.78, comp=NOSE_M))
    # a seam where the upright strip meets the face
    f1, f0, zf, E, B = geom(p)
    out.append(T.box((f1 - 0.2, 0.0, zf - 0.2), (0.9, p['W'] / 2 - 2.0, 0.6), rd=0.4, comp=STEEL_DK))
    # trunnion hubs
    for s in (1, -1):
        e = s * (p['W'] / 2 + p['tw'])
        out.append(T.cyl('r', (p['tf'], 0.0, p['tz']), min(e - s * 1.2, e + s * 1.2), max(e - s * 1.2, e + s * 1.2),
                         p['tr'] * 0.45, comp=STEEL))
    # the radar plate: a bracket behind it
    sf, sr, sz = sensor(p)
    pz = sz + p['gh'] + p['ms']
    out.append(T.box((sf - 2.4, sr, pz + p['phh'] * 0.35), (1.2, 2.0, p['phh'] * 0.3), rd=0.6, comp=STEEL_DK,
                     pitch=(p['pt'], sf, pz)))
    # vents along the foot of the back
    for k in range(4):
        r = (-0.54 + 0.36 * k) * p['W'] / 2
        out.append(T.box((f0 - 0.4, r, p['bz0'] + 4.0), (0.9, 3.6, 2.2), rd=0.4, comp=STEEL))
        out.append(dict(T.box((f0 - 0.4, r, p['bz0'] + 4.0), (1.5, 2.6, 1.3)), sub=True, comp_in=DARK))
    # a bearing band round the turntable's rim
    top = p['zref'] + RING_TOP + 1.4
    out.append(T.cyl('z', (0.0, 0.0, 0.0), top - 1.6, top - 0.4, 32.0, comp=STEEL_DK))
    return out


def albedo(comp, Lp, nl, grain, u, v, p=P0):
    f, r, z = Lp[:, 0], Lp[:, 1], Lp[:, 2]
    g = (1 + grain)[:, None]
    top = nl[:, 2] > 0.75
    kh = _R.KHAKI * (1 + 1.2 * grain)[:, None]
    seam = (_phase(f - p['bf'], 15.0, 7.5) < 0.5) & (np.abs(nl[:, 1]) > 0.7)
    kh = np.where(seam[:, None], kh * 0.84, kh)
    kh = np.where(top[:, None], _R.KHAKI_LT * (1 + 1.2 * grain)[:, None], kh)
    streak = _ss(0.3, 1.3, _sample(_NM, u * 3.0, 5.0 + 0 * v)) * ~top * 0.12
    kh = kh * (1 - streak)[:, None]
    # the radar plate: light grey, slotted across its face, darker behind
    sf, sr, sz = sensor(p)
    pz = sz + p['gh'] + p['ms']
    ca, sa = np.cos(p['pt']), np.sin(p['pt'])
    qf, qz = f - sf, z - pz
    pf_ = qf * ca + qz * sa; pv = -qf * sa + qz * ca                       # in the plate's own frame
    slot = (_phase(pv - 1.5, 3.0) < 0.9) & (pf_ > 1.0) & (np.abs(r - sr) < p['pw'] / 2 - 1.8) & (pv > 1.5) & (pv < p['phh'] - 1.5)
    plate = np.where(slot[:, None], np.array([88, 90, 98.]), np.array([176, 178, 186.])) * g
    plate = np.where((pf_ < -1.0)[:, None], np.array([96, 98, 106.]) * g, plate)
    alb = np.zeros((len(comp), 3))
    for k, c in ((KH, kh), (PLATE, plate), (BASE, _R.KHAKI * 0.84 * (1 + 1.2 * grain)[:, None]), (KH_LT, _R.KHAKI_LT * g),
                 (STEEL, _R.STEEL * g), (STEEL_DK, np.array([70, 72, 78.]) * g), (NOSE_M, NOSE * g),
                 (GREEN, _R.GREEN * (1 + 0.5 * grain)[:, None]), (DARK, np.array([22, 22, 24.]) * g),
                 (RED, np.array([120, 50, 40.]) * g)):
        alb = np.where((comp == k)[:, None], c, alb)
    return alb, comp == GREEN


def chip_points(p=P0):
    f1, f0, zf, E, B = geom(p)
    hw = p['W'] / 2
    return [(f0 + 2.0, hw - 1.0, B[1] - 1.0), (f0 + 1.0, -hw + 2.0, p['bz0'] + 6.0), (E[0] - 2.0, -hw, E[1] - 1.5),
            (p['bf'] - 10.0, hw, p['bz0'] + 8.0)]


def scorch(p=P0):
    _, at = face(p)
    c = at(0.5, 0.0, 2.0)
    f1, f0, zf, E, B = geom(p)
    return ((c[0], c[1], c[2], 18.0), (f0, 0.0, p['bz0'] + p['hb'] * 0.6, 12.0))


def aim_points(p=P0, recoil=0.0):
    """the middle of the launch face, and its eight cells (lower row left to right, then the upper)."""
    _, at = face(p)
    return [at(0.5, 0.0, 0.5)] + [c for c, hw_, hh in cells(p)]
