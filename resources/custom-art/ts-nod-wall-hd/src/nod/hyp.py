"""Parametric TS Nod wall hypothesis, built per connection mask in TS world coords (e east, s south, z up)."""
import numpy as np
import tsview as T

P = dict(H=0.48, zc=0.25, ta=0.085, edge=0.54, tl=0.10, zl=0.48, R=0.48, cap=0.30)

DIRS = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}


def rot_pieces(pieces, d):
    """pieces are defined for direction +e (east); rotate half-spaces to direction d=(de, ds)."""
    de, ds = d
    out = []
    for pc in pieces:
        q = []
        for (a, b) in pc:
            ae, as_, az = a
            # local (u along d, w perpendicular) -> world: e = u*de - w*ds, s = u*ds + w*de
            # a_local . (u, w, z): need world coeffs: u = e*de + s*ds, w = -e*ds + s*de
            we = ae * de + as_ * (-ds)
            ws = ae * ds + as_ * de
            q.append(((we, ws, az), b))
        out.append(q)
    return out


def arm(p):
    """wedge from the centre to the +e edge, tall at the edge (optionally flat for the last p['flat'])."""
    flat = p.get('flat', 0.0)
    k = (p['H'] - p['zc']) / max(p['edge'] - flat, 1e-3)
    return [[((-1, 0, 0), 0.0), ((1, 0, 0), p['edge']), ((0, -1, 0), p['ta']), ((0, 1, 0), p['ta']),
             ((0, 0, -1), 0.0), ((-k, 0, 1), p['zc']), ((0, 0, 1), p['H'])]]


def leg(p, reach=None):
    """buttress from the centre toward +e, sloping to the ground."""
    R = reach or p['R']
    k = p['zl'] / R
    return [[((-1, 0, 0), 0.0), ((1, 0, 0), R), ((0, -1, 0), p['tl']), ((0, 1, 0), p['tl']),
             ((0, 0, -1), 0.0), ((k, 0, 1), p['zl'])]]


def model(mask, p=P):
    arms = [a for a, b in (('N', 1), ('E', 2), ('S', 4), ('W', 8)) if mask & b]
    pieces = []
    for a in arms:
        pieces += rot_pieces(arm(p), DIRS[a])
    ns = any(a in 'NS' for a in arms); ew = any(a in 'EW' for a in arms)
    if len(arms) == 2 and ns and ew:
        # corner: diagonal leg along the bisector (outward), longer inward
        (a1, a2) = arms
        d1, d2 = np.array(DIRS[a1]), np.array(DIRS[a2])
        bis = -(d1 + d2) / np.linalg.norm(d1 + d2)
        pieces += rot_pieces(leg(p, p['R'] * 0.85), tuple(bis))
        pieces += rot_pieces(leg(p, p['R'] * 1.4), tuple(-bis))
    else:
        for a in 'NESW':
            if a in arms:
                continue
            opp = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}[a]
            if len(arms) == 0:
                if a in 'NS':
                    pieces += rot_pieces(leg(p), DIRS[a])
                else:
                    pieces += rot_pieces(arm(p), DIRS[a])   # post: E-W arms as caps
            elif len(arms) == 1:
                if a == opp_of(arms[0]):
                    pieces += rot_pieces(arm(p), DIRS[a])   # dead end: the far arm stays as a cap
                else:
                    pieces += rot_pieces(leg(p), DIRS[a])
            else:
                pieces += rot_pieces(leg(p), DIRS[a])
    return pieces


def opp_of(a):
    return {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}[a]
