"""the Titan's upper body, v2: the main body is the convex hull of TS's carved upper body (32 views), painted
green below the band line and tan above; the pods, box, antenna, mount and lamps are parts of their own."""
import numpy as np
import rc

BODY, POD, BOX, ANT, MOUNT, LAMP, BAND, HATCH = 21, 22, 23, 24, 25, 26, 27, 28
CLASS = {BODY: 1, POD: 6, BOX: 6, ANT: 2, MOUNT: 2, LAMP: 7, BAND: 6, HATCH: 1}

P0 = dict(band=32.0, pfu=(4.0, 11.5), pru=(-11.5, -6.0), pv=(2.4, 7.4), pbot=23.4, ptop=27.5,
          bu=(-9.4, -2.8), bv=(-3.9, 2.3), btop=44.0, bbot=36.0, bch=0.6,
          au=-2.66, av=3.43, atop=50.0, ar=0.45, abot=38.0,
          mu=(-3.0, 2.5), mv=(6.8, 8.8), mw=(27.0, 32.0))


def merge_planes(eq, ang=2.5):
    """merge hull facets whose normals are within ang degrees, keeping the outermost offset."""
    n = eq[:, :3] / np.linalg.norm(eq[:, :3], axis=1, keepdims=True)
    d = -eq[:, 3] / np.linalg.norm(eq[:, :3], axis=1)
    used = np.zeros(len(n), bool); out = []
    cosmin = np.cos(np.deg2rad(ang))
    order = np.argsort(-d)
    for i in order:
        if used[i]:
            continue
        grp = (~used) & (n @ n[i] > cosmin)
        used |= grp
        nn = n[grp].mean(0); nn /= np.linalg.norm(nn)
        # outermost along the merged normal: the max of each member plane's support... use member offsets
        out.append(rc.Plane(nn, d[grp].max()))
    return out


_PL = None


def body_planes():
    global _PL
    if _PL is None:
        eq = np.load(__import__('paths').HERE + '/shell_planes28.npy')
        _PL = merge_planes(eq)
    return _PL


def top_height(u, v, planes=None):
    """the body's top surface height at (u, v) (the lowest of its upward-facing planes)."""
    pl = planes or body_planes()
    w = np.inf
    for p in pl:
        if p.n[2] > 0.05:
            w = min(w, (p.d - p.n[0] * u - p.n[1] * v) / p.n[2])
    return w


def top_normal(u, v, eps=0.25):
    dwu = (top_height(u + eps, v) - top_height(u - eps, v)) / (2 * eps)
    dwv = (top_height(u, v + eps) - top_height(u, v - eps)) / (2 * eps)
    n = np.array([-dwu, -dwv, 1.0]); return n / np.linalg.norm(n)


def parts(P=P0, inflate=0.125, detail=True):
    pl = [rc.Plane(p.n, p.d + inflate) for p in body_planes()]
    sph = (np.array([0.0, -0.5, 33.5]), 17.5)
    if not detail:
        out = [rc.Part(pl, BODY, 'body', sphere=sph)]
    else:
        # the gold shell, its lower edge a lip over the green band; the band set in under it
        lip = P.get('lip', 0.4)
        out = [rc.Part(pl + [rc.Plane((0, 0, -1.0), -(P['band'] - 0.15))], BODY, 'body', sphere=sph),
               rc.Part([rc.Plane(p.n, p.d - lip) for p in pl if p.n[2] < 0.9] + [rc.Plane((0, 0, 1.0), P['band'] + 0.2)],
                       BAND, 'band', sphere=sph)]
        # the round boss on the shell's front top (TS's rounded bump): an upright rim and a low dome inside it
        hu, hv, hr = P.get('hu', 2.4), P.get('hv', 0.8), P.get('hr', 2.7)
        wt = top_height(hu, hv)
        out.append(rc.cylinder((hu, hv, wt - 1.6), (hu, hv, wt + 0.45), hr + 0.3, HATCH, 'bossrim'))
        out.append(rc.Part([rc.Ellip((hu, hv, wt + 0.1), np.eye(3), (hr, hr, 1.55)),
                            rc.Plane((0, 0, -1.0), -(wt - 0.6))], HATCH, 'boss',
                           sphere=(np.array([hu, hv, wt + 0.1]), hr + 0.1)))
    for (u0, u1) in (P['pfu'], P['pru']):
        for s in (-1, 1):
            v0, v1 = (P['pv'][0], P['pv'][1]) if s > 0 else (-P['pv'][1], -P['pv'][0])
            c = ((u0 + u1) / 2, (v0 + v1) / 2, (P['pbot'] + P['ptop']) / 2)
            h = ((u1 - u0) / 2, (v1 - v0) / 2, (P['ptop'] - P['pbot']) / 2)
            out.append(rc.box(c, np.eye(3), h, POD, chamfer=(0.7, 0.7, 0.7), name='pod'))
    bc = ((P['bu'][0] + P['bu'][1]) / 2, (P['bv'][0] + P['bv'][1]) / 2, (P['btop'] + P['bbot']) / 2)
    bh = ((P['bu'][1] - P['bu'][0]) / 2, (P['bv'][1] - P['bv'][0]) / 2, (P['btop'] - P['bbot']) / 2)
    out.append(rc.box(bc, np.eye(3), bh, BOX, chamfer=(P['bch'], P['bch'], P['bch']), name='box'))
    out.append(rc.cylinder((P['au'], P['av'], P['abot']), (P['au'], P['av'], P['atop']), P['ar'], ANT, 'antenna'))
    mc = ((P['mu'][0] + P['mu'][1]) / 2, (P['mv'][0] + P['mv'][1]) / 2, (P['mw'][0] + P['mw'][1]) / 2)
    mh = ((P['mu'][1] - P['mu'][0]) / 2, (P['mv'][1] - P['mv'][0]) / 2, (P['mw'][1] - P['mw'][0]) / 2)
    out.append(rc.box(mc, np.eye(3), mh, MOUNT, chamfer=(0.5, 0.5, 0.5), name='mount'))
    return out
