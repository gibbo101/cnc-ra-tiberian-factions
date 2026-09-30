"""TS GDI Component Tower Vulcan (GTCTWR_B): a khaki gun box with a twin Gatling cannon and green (house
colour) ammo drums on its flanks. Local frame: f forward (the guns), r right, z up from the turret's foot."""
import numpy as np
import tsdf as T

# materials
KH, STEEL, GREEN, DARK, KH_LT, STEEL_DK, RED = 1, 2, 3, 4, 5, 6, 7
CLS = {KH: 1, KH_LT: 1, STEEL: 2, STEEL_DK: 2, GREEN: 3, DARK: 4, RED: 4}

P0 = dict(bf=-6.0, L=44.0, Wd=48.0, Hb=30.0, bt=8.0, bs=6.0, bb=4.0,
          gs=22.0, gz=17.0, gr=5.8, gtip=69.0, hr=8.0, hl=10.0,
          pf=-4.0, pl=26.0, prad=8.0, po=6.0, pz=10.0,
          px=23.6, py=13.8, zref=12.0)


def parts(p=P0, recoil=0.0):
    b1 = p['bf'] + p['L'] / 2                                       # the body's front along f
    hw = p['Wd'] / 2
    body = T.slab_box((p['bf'], 0.0, p['Hb'] / 2), (p['L'] / 2, hw, p['Hb'] / 2),
                      bevel_top=p['bt'], bevel_side=p['bs'], comp=KH)
    if p.get('bb', 0) > 0:                                            # chamfered bottom edges too
        extra = []
        for sf, sr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            e = (p['bf'] * sf + p['L'] / 2 * abs(sf)) + (hw * abs(sr))
            extra.append(((sf, sr, -1), e - p['bb']))
        body = T.poly([(tuple(n * 1.0), d) for n, d in zip(body['n'], body['d'])] + extra, comp=KH)
    out = [body]
    # green ammo drums on both flanks (drums lying fore and aft)
    for s in (1, -1):
        out.append(T.cyl('f', (0.0, s * (hw + p['po']), p['pz']), p['pf'] - p['pl'] / 2, p['pf'] + p['pl'] / 2,
                         p['prad'], comp=GREEN))
    # twin Gatling: a housing at the body's face, then the barrel clusters
    for s in (1, -1):
        rc = s * p['gs'] / 2
        out.append(T.cyl('f', (0.0, rc, p['gz']), b1 - 4.0, b1 + p['hl'], p['hr'], comp=STEEL))
        out.append(T.cyl('f', (0.0, rc, p['gz']), b1 + p['hl'] - 1.0 - recoil, p['gtip'] - recoil, p['gr'], comp=STEEL))
    return out


def bounds(p=P0):
    side = p['Wd'] / 2 + p['po'] + p['prad'] + 4
    return (p['bf'] - p['L'] / 2 - 4, -side, -2), (p['gtip'] + 4, side, p['Hb'] + 6)


# ----------------------------------------------------------------------------- HD materials
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import ct_ra as _R
from walls2 import sample as _sample, phase as _phase, smoothstep as _ss, NOISE_MOTTLE as _NM

GUN_DARK = np.array([70, 72, 78.])
BORE = np.array([22, 22, 26.])


def albedo(comp, Lp, nl, grain, u, v, p=P0):
    """colours per material; returns rgb (N, 3) and the house-colour flag."""
    f, r, z = Lp[:, 0], Lp[:, 1], Lp[:, 2]
    g = (1 + grain)[:, None]
    top = nl[:, 2] > 0.75
    kh = _R.KHAKI * (1 + 1.2 * grain)[:, None]
    # panel seams on the body's sides and a lighter, worn top with a seam across it
    seam = (_phase(np.where(np.abs(nl[:, 0]) > np.abs(nl[:, 1]), r, f), 13.0, 6.5) < 0.55) & ~top
    kh = np.where(seam[:, None], kh * 0.84, kh)
    kh = np.where(top[:, None], _R.KHAKI_LT * (1 + 1.2 * grain)[:, None], kh)
    kh = np.where((top & (np.abs(f - p['bf']) < 0.7))[:, None], kh * 0.8, kh)
    streak = _ss(0.3, 1.3, _sample(_NM, u * 3.0, 5.0 + 0 * v)) * ~top * 0.12
    kh = kh * (1 - streak)[:, None]
    # guns: steel housings, barrel clusters with dark bands, dark bores on the muzzle face
    b1 = p['bf'] + p['L'] / 2
    st = _R.STEEL * g
    band = (_phase(f - b1, 7.0, 3.5) < 1.1) & (f > b1 + p['hl'])
    st = np.where(band[:, None], GUN_DARK * g, st)
    face = nl[:, 0] > 0.8                                          # the muzzle faces
    rc = np.where(r > 0, p['gs'] / 2, -p['gs'] / 2)
    rr = np.hypot(r - rc, z - p['gz'])
    ang = np.arctan2(z - p['gz'], r - rc)
    bores = (np.abs(rr - p['gr'] * 0.55) < p['gr'] * 0.3) & (np.cos(6 * ang) > 0.35)
    st = np.where((face & (f > p['gtip'] - 2.0 - 12))[:, None] & (bores | (rr < p['gr'] * 0.2))[:, None], BORE, st)
    gr = _R.GREEN * (1 + 0.5 * grain)[:, None]
    alb = np.zeros((len(comp), 3))
    for k, c in ((KH, kh), (KH_LT, _R.KHAKI_LT * g), (STEEL, st), (STEEL_DK, GUN_DARK * g), (GREEN, gr),
                 (DARK, _R.RECESS * g), (RED, np.array([120, 70, 56.]) * g)):
        alb = np.where((comp == k)[:, None], c, alb)
    return alb, comp == GREEN


def parts_hd(p=P0, recoil=0.0, damaged=False):
    """the fitted shape with its detail: each Gatling is six barrels round a spindle held by clamp bands,
    ending in a muzzle clamp; the drums have end caps and a band; the housings a lip."""
    out = [q for q in parts(p, recoil) if not (q['kind'] == 'cyl' and q['axis'] == 'f' and q['comp'] == STEEL
                                               and q['R'] == p['gr'])]
    b1 = p['bf'] + p['L'] / 2
    f0, f1 = b1 + p['hl'] - 1.0 - recoil, p['gtip'] - recoil
    rb = p['gr'] * 0.36                                          # one barrel
    ring = p['gr'] - rb                                          # barrels' circle
    for s in (1, -1):
        rc = s * p['gs'] / 2
        out.append(T.cyl('f', (0.0, rc, p['gz']), f0, f1 - 1.0, p['gr'] * 0.35, comp=STEEL_DK))     # spindle
        for k in range(6):
            a = k * np.pi / 3 + np.pi / 6
            out.append(T.cyl('f', (0.0, rc + ring * np.cos(a), p['gz'] + ring * np.sin(a)), f0, f1, rb, comp=STEEL))
        for fc, w in ((f0 + 3.0, 2.2), (f0 + (f1 - f0) * 0.55, 2.0), (f1 - 3.0, 3.0)):             # clamp bands
            out.append(T.cyl('f', (0.0, rc, p['gz']), fc - w / 2, fc + w / 2, p['gr'] + 0.6, comp=STEEL_DK))
        out.append(T.cyl('f', (0.0, rc, p['gz']), b1 + p['hl'] - 2.0, b1 + p['hl'] + 0.5, p['hr'] + 0.8,
                         comp=STEEL_DK))                                                          # housing lip
    hw = p['Wd'] / 2
    for s in (1, -1):                                             # drum end caps and a band
        c = (0.0, s * (hw + p['po']), p['pz'])
        for fe in (p['pf'] - p['pl'] / 2, p['pf'] + p['pl'] / 2):
            out.append(T.cyl('f', c, fe - 1.0, fe + 1.0, p['prad'] - 1.5, comp=STEEL_DK))
        out.append(T.cyl('f', c, p['pf'] - 1.2, p['pf'] + 1.2, p['prad'] + 0.5, comp=GREEN))
    return out


def chip_points(p=P0):
    b0, b1, hw, H = p['bf'] - p['L'] / 2, p['bf'] + p['L'] / 2, p['Wd'] / 2, p['Hb']
    return [(b1 - 2.0, hw - 2.0, H - p['bt'] + 1.0), (b0 + 3.0, -hw + 2.0, H - p['bt'] + 2.0),
            (p['bf'] + 4.0, hw, H * 0.35), (b0 + 1.0, hw - 6.0, 4.0)]


def scorch(p=P0):
    b1 = p['bf'] + p['L'] / 2
    return ((b1 + 2.0, 0.0, p['gz'], 15.0), (p['bf'] - 6.0, -p['Wd'] / 2, p['Hb'] * 0.6, 12.0))


def aim_points(p=P0, recoil=0.0):
    """the two muzzles (the barrel tips, on each cluster's axis)."""
    return [(p['gtip'] - recoil, s * p['gs'] / 2, p['gz']) for s in (-1, 1)]
