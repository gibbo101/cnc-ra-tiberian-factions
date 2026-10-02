"""
wolfhd.py - the Wolverine as rendered in HD: the fitted model (wolf.py) with its detail (the gun barrels and
muzzle rings, the head's lamp, rounded shoulder pads), placed for the mod's frames.

The mod's frames (TSSMEC, 384 x 384, 128 frames):
   0-95    the walk: frame = facing x 12 + step (facings counter-clockwise from north: 0 N, 1 NW, 2 W, 3 SW, 4 S,
           5 SE, 6 E, 7 NE), 2 ticks a step
   96-127  firing: 96 + facing x 4 + step, standing as TS stands to fire, the flash on steps 0 and 2
"""
import json
import numpy as np
import rc
import wolf as WF
import gait as G

from paths import HERE
WORK = HERE + '/'
PPU = 6.4
CANVAS = (384, 384)
TS_ANCHOR = (47.5, 53.0)          # TS's sprite point that sits at canvas (192, 307) in the mod
CANVAS_ANCHOR = (192.0, 307.0)

BARREL, MRING, LAMPC, WINDOW, DRUM, BELT, HANDLE, TOE = 71, 72, 73, 74, 75, 76, 77, 78


def load(path=WORK + 'wolf_final.json'):
    js = json.load(open(path))
    P = dict(WF.P0); P.update(js['P'])
    model = dict(P=P, ax=js['ax'], y0=js['y0'], stand=js['pose'])
    if 'gait' in js:
        model['gait'] = G.Gait.from_json(js['gait'])
    model['walk'] = {int(k): v for k, v in js.get('walk', {}).items()}
    return model


def walk_pose(model, step):
    """the pose for walk step 0-11 (TS's own 12 walk frames, the mod's steps)."""
    g = model.get('gait')
    if g is not None:
        return g.pose(2 * np.pi * step / 12.0)
    return model['walk'][step]


def gatling(P, side, dw):
    """the gun's front end as Westwood's render has it: a short drum on the housing, six barrels round a spindle
    with a clamp ring two thirds along, their tips at the fitted muzzle (TS's light grey end)."""
    out = []
    ax = np.array([1.0, 0, 0])
    r0 = min(P['gh'], P['gk'])
    c = np.array([0.0, side * P['gv'], P['gw'] + dw])
    u_tip = P['gu1']; u_back = P['gu1'] - P['gm']
    drum0, drum1 = u_back - 0.25, u_back + 0.42
    out.append(rc.cylinder(c + ax * drum0, c + ax * drum1, r0 * 0.88, DRUM, 'drum'))
    rr = r0 * 0.46
    rb = max(0.13, r0 * 0.15)
    for i in range(6):
        a = np.pi / 6 + i * np.pi / 3
        off = np.array([0.0, np.cos(a), np.sin(a)]) * rr
        out.append(rc.cylinder(c + off + ax * drum1, c + off + ax * u_tip, rb, BARREL, 'barrel'))
    out.append(rc.cylinder(c + ax * drum1, c + ax * (u_tip - 0.05), rr - rb * 0.6, BARREL, 'spindle'))
    uc = drum1 + 0.62 * (u_tip - drum1)
    out.append(rc.cylinder(c + ax * (uc - 0.11), c + ax * (uc + 0.11), rr + rb + 0.12, MRING, 'clamp'))
    return out


def ammo_belt(P, side, dw, links=9):
    """the ammo belt hanging from the gun's underside in a loop back to the arm, as in the render: a chain of
    small brass links (each a box across the belt), kept short so the silhouette stays TS's."""
    out = []
    A = np.array([P['gu0'] + 3.8, side * (P['gv'] + 0.25), P['gw'] - P['gk'] + 0.15 + dw])
    B = np.array([P['gu0'] + 0.5, side * (P['gv'] + 0.15), P['gw'] - P['gk'] + 0.15 + dw])
    sag = 2.0
    pts = []
    for t in np.linspace(0, 1, links + 1):
        p = A + (B - A) * t
        p = p - np.array([0, 0, sag * 4 * t * (1 - t)])
        pts.append(p)
    for i in range(links):
        p0, p1 = pts[i], pts[i + 1]
        out.append(rc.seg_box(p0, p1, 0.95, 0.34, BELT, up=(0, 0, 1.0), ext=-0.05, name='belt'))
    return out


def clawed_foot(p):
    """Westwood's foot: a heel block and three toes, the outer two splayed, each toe's top sloping down to a
    blunt claw; inside the fitted foot's box so the silhouette stays TS's."""
    R, c, h = box_frame(p)
    f, s, u = R[:, 0], R[:, 1], R[:, 2]
    hl, hw, hh = h
    out = []
    # heel and instep: the rear 55%, full width and height
    x0, x1 = -hl, -hl + 1.1 * hl
    out.append(rc.box(c + f * (x0 + x1) / 2, R, ((x1 - x0) / 2, hw, hh), WF.FOOT, chamfer=(0.4, 0.45, 0.35),
                      name='foot'))
    tw = hw * 0.31                                     # each toe's half width: three toes and two slits within
                                                       # the fitted foot's width, so the feet stand where TS's do
    for k, (dv, ang, ext) in enumerate(((-0.66, -0.07, 0.0), (0.0, 0.0, 0.15), (0.66, 0.07, 0.0))):
        Rt = np.stack([np.cos(ang) * f + np.sin(ang) * s, -np.sin(ang) * f + np.cos(ang) * s, u], 1)
        t0, t1 = -0.15 * hl, hl * 0.98 + ext
        cc = c + s * dv * hw + Rt[:, 0] * (t0 + t1) / 2 - u * hh * 0.12
        toe = rc.box(cc, Rt, ((t1 - t0) / 2, tw, hh * 0.86), TOE, chamfer=(0.3, 0.25, 0.25), name='toe')
        # the toe's top slopes down to its tip
        tip = cc + Rt[:, 0] * (t1 - t0) / 2 + u * (hh * 0.86 - hh * 0.95)
        back = cc + Rt[:, 0] * (-(t1 - t0) / 2 + 0.5) + u * hh * 0.86
        d = tip - back
        n = np.cross(Rt[:, 1], d); n = n / np.linalg.norm(n)
        if n @ u < 0:
            n = -n
        toe.cons.append(rc.Plane(n, n @ tip))
        out.append(toe)
    return out


def roof_handles(P, dw):
    """the two grab handles standing on the roof's back, each a bar on two posts."""
    out = []
    w = P['hw1'] + dw
    for side in (-1, 1):
        v = side * max(1.6, P['hv'] - 1.5)
        ua, ub = P['hu0'] + 0.7, P['hu0'] + 2.3
        for uu in (ua, ub):
            out.append(rc.box((uu, v, w + 0.3), np.eye(3), (0.13, 0.13, 0.32), HANDLE, name='handle'))
        out.append(rc.box(((ua + ub) / 2, v, w + 0.62), np.eye(3), ((ub - ua) / 2 + 0.13, 0.13, 0.12), HANDLE,
                          chamfer=(0.0, 0.08, 0.08), name='handle'))
    return out


def detail(parts, P, dw=0.0):
    """the fitted model with Westwood's details (from the render the TS sprite was made from): gatling barrel
    clusters and ammo belts on the guns, clawed feet, grab handles on the roof, the pilot's window, rounded
    shoulder pads and the lamp."""
    out = []
    for p in parts:
        if p.comp == WF.MUZZLE:
            R, c, h = box_frame(p)
            side = np.sign(c[1])
            out += gatling(P, side, dw)
            out += ammo_belt(P, side, dw)
            continue
        if p.comp == WF.SHOULDER:
            R, c, h = box_frame(p)
            q = rc.box(c, np.eye(3), h, WF.SHOULDER, chamfer=(min(h[1], h[2]) * 0.55, min(h[0], h[2]) * 0.45,
                                                              min(h[0], h[1]) * 0.45), name='shoulder')
            q.cons += [c_ for c_ in p.cons[6:] if c_.kind == 'plane' and abs(c_.n[2]) > 0.3 and abs(c_.n[1]) > 0.3]
            out.append(q)
            continue
        if p.comp == WF.FOOT:
            out += clawed_foot(p)
            continue
        out.append(p)
    # the pilot's window: TS's black slit across the front, just under the cab's sloping face (read from TS's
    # frames: a dark band one pixel high across the front facing south, an upright black line at the front edge
    # side-on; Westwood's render has it as the slit in the roof's front)
    wc = P.get('win_w', P['hw0'] - 0.85) + dw          # right under the cab's front edge, as TS has it
    hh = P.get('win_h', 0.5)
    hv = min(P.get('win_v', 3.2), P['tv'] - 0.2)
    out.append(rc.box((P['tu1'] - 0.12, 0.0, wc), np.eye(3), (0.2, hv, hh), WINDOW, chamfer=(0.0, 0.12, 0.12),
                      name='window'))
    out += roof_handles(P, dw)
    # the orange lamp on the head's sloping front, at its right edge (read from TS's frames 99-101)
    lu, lv = 1.9, min(3.85, P['hv'] + P['hcv'] - 0.45)
    du = P['hu1'] - P['hsu']
    n = np.array([P['hs'], 0, du]); n = n / np.linalg.norm(n)
    w_s = P['hw1'] - P['hs'] * (lu - P['hsu']) / du + dw
    base = np.array([lu, lv, w_s])
    out.append(rc.cylinder(base - n * 0.3, base + n * 0.32, 0.55, LAMPC, 'lamp'))
    return out


def box_frame(part):
    cons = part.cons
    R = np.stack([cons[1].n, cons[3].n, cons[5].n], 1)
    a = np.array([(cons[2 * i + 1].d - cons[2 * i].d) / 2 for i in range(3)])
    h = np.array([(cons[2 * i + 1].d + cons[2 * i].d) / 2 for i in range(3)])
    return R, R @ a, h


def body(model, pose):
    """every part in the body frame (ground at w = 0), with the HD detail."""
    P = model['P']
    return detail(WF.body_parts(P, pose), P, pose[6])


def muzzles(model, pose):
    """the two muzzle tips in the body frame."""
    P = model['P']
    return [np.array([P['gu1'], s * P['gv'], P['gw'] + pose[6]]) for s in (-1, 1)]


def facing_cw(k, n=8):
    return WF.facing_matrix(k, n)


def mod_to_cw(f, n=8):
    """the mod's facing f (counter-clockwise from north) -> TS's clockwise index."""
    return (n - f) % n


def placed(model, pose, k8):
    M = facing_cw(k8)
    return [p.moved(M) for p in body(model, pose)], M
