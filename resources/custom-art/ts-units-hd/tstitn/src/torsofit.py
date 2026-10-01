"""
torsofit.py - the Titan's upper body (TS's "turret": frames 120-151) as convex parts, fitted to TS's 32 facings.

Body frame: u forward, v right, w up, in TS sprite px (the legs' units); the turret turns about the unit's axis.
"""
import numpy as np
import rc
from tspal import load, index_map

SHELL, HULL, POD, BOX, ANT, RING, MOUNT, LAMP, KEEL = 11, 12, 13, 14, 15, 16, 17, 18, 19
CLASS = {SHELL: 1, HULL: 6, POD: 6, BOX: 6, ANT: 2, RING: 1, MOUNT: 2, LAMP: 7, KEEL: 2}

P0 = dict(
    # shell: an ellipsoid (centre su, sw; radii sa, sb, sc) trimmed to a box (front sf, rear sr, side ss, bottom sbot)
    su=-2.0, sw=27.0, sa=15.0, sb=10.5, sc=13.0, sf=11.6, sr=-11.4, ss=7.8, sbot=28.5,
    # the green lower hull: a chamfered box
    hf=11.8, hr=-11.6, hs=8.2, hbot=26.0, htop=30.0, hch=1.5,
    # pods under the corners (front and rear), green
    pfu=(5.0, 11.8), pru=(-11.6, -5.5), pv=(2.6, 8.2), pbot=23.4,
    # the green box on top at the rear left
    bu=(-9.4, -2.8), bv=(-3.9, 2.3), btop=44.0, bch=0.8,
    # the antenna
    au=-2.66, av=3.43, atop=50.0, ar=0.45,
    # the hatch ring on top
    ru=3.5, rv=0.5, rr=3.1, rh=0.6,
    # the cannon mount on the right flank
    mu=(-3.0, 3.0), mv=(6.5, 9.0), mw=(26.0, 32.5),
)


def parts(P=P0):
    out = []
    E = rc.Ellip((P['su'], 0.0, P['sw']), np.eye(3), (P['sa'], P['sb'], P['sc']))
    out.append(rc.Part([E, rc.Plane((1, 0, 0), P['sf']), rc.Plane((-1, 0, 0), -P['sr']),
                        rc.Plane((0, 1, 0), P['ss']), rc.Plane((0, -1, 0), P['ss']),
                        rc.Plane((0, 0, -1), -P['sbot'])], SHELL, 'shell'))
    hc = ((P['hf'] + P['hr']) / 2, 0.0, (P['hbot'] + P['htop']) / 2)
    hh = ((P['hf'] - P['hr']) / 2, P['hs'], (P['htop'] - P['hbot']) / 2)
    out.append(rc.box(hc, np.eye(3), hh, HULL, chamfer=(P['hch'], P['hch'], P['hch']), name='hull'))
    for (u0, u1) in (P['pfu'], P['pru']):
        for s in (-1, 1):
            v0, v1 = (P['pv'][0], P['pv'][1]) if s > 0 else (-P['pv'][1], -P['pv'][0])
            c = ((u0 + u1) / 2, (v0 + v1) / 2, (P['pbot'] + P['hbot'] + 1.0) / 2)
            h = ((u1 - u0) / 2, (v1 - v0) / 2, (P['hbot'] + 1.0 - P['pbot']) / 2)
            out.append(rc.box(c, np.eye(3), h, POD, chamfer=(0.7, 0.7, 0.7), name='pod'))
    bc = ((P['bu'][0] + P['bu'][1]) / 2, (P['bv'][0] + P['bv'][1]) / 2, (P['btop'] + P['sbot']) / 2)
    bh = ((P['bu'][1] - P['bu'][0]) / 2, (P['bv'][1] - P['bv'][0]) / 2, (P['btop'] - P['sbot']) / 2)
    out.append(rc.box(bc, np.eye(3), bh, BOX, chamfer=(P['bch'], P['bch'], P['bch']), name='box'))
    out.append(rc.cylinder((P['au'], P['av'], P['sbot']), (P['au'], P['av'], P['atop']), P['ar'], ANT, 'antenna'))
    mc = ((P['mu'][0] + P['mu'][1]) / 2, (P['mv'][0] + P['mv'][1]) / 2, (P['mw'][0] + P['mw'][1]) / 2)
    mh = ((P['mu'][1] - P['mu'][0]) / 2, (P['mv'][1] - P['mv'][0]) / 2, (P['mw'][1] - P['mw'][0]) / 2)
    out.append(rc.box(mc, np.eye(3), mh, MOUNT, chamfer=(0.6, 0.6, 0.6), name='mount'))
    return out


def facing_matrix32(k):
    th = 2 * np.pi * k / 32
    f = np.array([np.sin(th), -np.cos(th), 0.0]); r = np.array([np.cos(th), np.sin(th), 0.0])
    return np.stack([f, r, np.array([0, 0, 1.0])], axis=1)


def ts_classes(f):
    """per pixel: 0 none, 1 tan/gold, 6 house green, 2 dark, 7 bright (lamps)."""
    a = load(f); im, _ = index_map(a)
    c = np.zeros(im.shape, int)
    c[im >= 0] = 2
    c[((im >= 128) & (im <= 167)) | ((im >= 176) & (im <= 185)) | ((im >= 112) & (im <= 125))] = 1
    c[im >= 1000] = 6
    rgb = a[..., :3]
    c[(im >= 0) & (rgb.min(-1) > 150)] = 7
    return c


class TorsoViews:
    def __init__(self, win=(30, 0, 68, 42), ax=47.4, y0=51.5):
        self.win = win
        x0, yw, x1, y1 = win
        self.cls = [ts_classes(120 + k)[yw:y1, x0:x1] for k in range(32)]
        self.masks = [c > 0 for c in self.cls]
        self.cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))

    def render(self, P, ks=range(32), ss=3):
        x0, yw, x1, y1 = self.win
        base = parts(P)
        out = {}
        for k in ks:
            M = facing_matrix32(k)
            pk = [p.moved(M) for p in base]
            t, who, nrm, O = rc.render_ids(pk, self.cam, x0, yw, x1 - x0, y1 - yw, ss=ss, zstart=200.0)
            out[k] = (who, [p.comp for p in base])
        return out
