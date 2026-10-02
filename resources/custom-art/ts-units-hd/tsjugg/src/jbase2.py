"""
jbase2.py - the Juggernaut's deployed base as TS builds it: TS's base frame (DJUGG 0) draws the walker's near leg
unchanged as its front limb (the same pixels as JUGGER CW5 step 0 and DJUGGMK frame 0), so the base here is

    the walker's two legs, standing as at walk step 0 facing south-west (the near one is the front limb, the far one
    stands behind the column), the pivot column the cabin turns on, and two limbs unfolded west and east.

Fitted to DJUGG frame 0 in TS's camera (30 degrees): the column, the two side limbs (their yaw and shared sizes) and
the base's place (bax, by0); the walker's legs are fixed by the walk fit and stand where the walker stands in TS's
deploy (its ground point at JUGGER's + (1, 14)).

Base frame: x east, y south, z up, origin = the column's foot.

    python3 jbase2.py out.json iters [start.json|-] [seed]
"""
import os
import json, sys, time
import numpy as np
import cma
import rc
import jugg as JG
import jbase as JB
import jfit as JF

WALK = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fit_walk_e.json')
DJUGG_TO_JUGGER = (1.0, 14.0)
S30 = np.sin(np.deg2rad(30.0))
S32 = np.sin(np.deg2rad(32.0))


def walker_legs():
    """the walker's two legs at walk step 0, facing south-west (CW5), relative to its ground point; and that point in
    DJUGG's frame."""
    js = json.load(open(WALK))
    P = dict(JG.P0); P.update(js['P'])
    pose = js['poses']['0'] if 'poses' in js else js['pose']
    M = JG.facing_matrix(5)
    legs = []
    for side, ang in ((-1, pose[0:3]), (1, pose[3:6])):
        legs += [p.moved(M) for p in JG.leg_parts(side, *ang, P, pose[6])[0]]
    g = (js['ax'] + DJUGG_TO_JUGGER[0], js['y0'] + DJUGG_TO_JUGGER[1])
    return legs, g


LEGS, G = walker_legs()

P0 = dict(pr=4.9, ph=19.0, rr=4.5, rh=2.2, yw=286.6, ye=81.6,
          hh=10.9, hr=4.8, kh=2.0, kr=5.7, fr=11.3, lw=5.9, ld=5.8, fl=8.0, fw=6.2, fhh=3.7)


def walker_offset(bax, by0, sin_e=S30):
    """where the walker's ground point stands against the column's foot (world, TS px): its screen offset in DJUGG's
    frame read through a camera sin_e above the ground (TS's 30 degrees for the fits; the HD scenes use 32, so the
    walker lands on the same canvas point in the walk frames and in the deploy and deployed frames)."""
    return np.array([G[0] - bax, (G[1] - by0) / sin_e, 0.0])


def base_parts(P, bax, by0, sin_e=S30):
    """the base in its own frame (origin the column's foot); bax, by0: its place in DJUGG's frame (sets where the
    walker's legs stand against the column)."""
    out = [rc.cylinder((0, 0, 0.0), (0, 0, P['ph']), P['pr'], JB.PIVOT, 'pivot'),
           rc.cylinder((0, 0, P['ph'] - P['rh']), (0, 0, P['ph']), P['rr'], JB.RIM, 'rim')]
    for yaw in (P['yw'], P['ye']):
        out += JB.limb(P, yaw)
    d = walker_offset(bax, by0, sin_e)
    out += [p.moved(np.eye(3), d) for p in LEGS]
    return out


SPEC = [('pr', 1.5, 7), ('ph', 8, 24), ('rr', 2, 8), ('rh', 0.5, 4), ('yw', 230, 320), ('ye', 40, 130),
        ('hh', 4, 20), ('hr', 0, 7), ('kh', 1, 18), ('kr', 2, 16), ('fr', 6, 24), ('lw', 1.5, 8), ('ld', 1.5, 8),
        ('fl', 2, 11), ('fw', 2, 9), ('fhh', 1, 5)]
CAM = [('bax', 46, 56), ('by0', 56, 68)]
ALL = SPEC + CAM


def unpack(x):
    P = dict(P0)
    for (k, *_), v in zip(SPEC, x[:len(SPEC)]):
        P[k] = float(v)
    return P, float(x[len(SPEC)]), float(x[len(SPEC) + 1])


if __name__ == '__main__':
    out = sys.argv[1]; iters = int(sys.argv[2])
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    V = JB.BaseView()
    lo = np.array([s[1] for s in ALL], float); hi = np.array([s[2] for s in ALL], float); span = hi - lo
    if len(sys.argv) > 3 and sys.argv[3] != '-':
        js = json.load(open(sys.argv[3])); Ps = dict(P0); Ps.update(js['P'])
        x0 = np.array([Ps[k] for k, *_ in SPEC] + [js['bax'], js['by0']], float)
    else:
        x0 = np.array([P0[k] for k, *_ in SPEC] + [50.93, 62.63], float)
    x0 = np.clip(x0, lo + 1e-3, hi - 1e-3)

    def f(z):
        P, ax, y0 = unpack(lo + np.clip(z, 0, 1) * span)
        return V.loss(base_parts(P, ax, y0), ax, y0, w_cls=0.6)
    es = cma.CMAEvolutionStrategy((x0 - lo) / span, 0.1, {'bounds': [0, 1], 'popsize': 20, 'maxiter': iters,
                                                         'seed': seed, 'verbose': -9})
    t0 = time.time(); it = 0
    print('start %.4f' % f((x0 - lo) / span), flush=True)
    while not es.stop():
        Z = es.ask(); es.tell(Z, [f(z) for z in Z]); it += 1
        if it % 10 == 0 or es.stop():
            P, ax, y0 = unpack(lo + np.clip(es.result.xbest, 0, 1) * span)
            json.dump(dict(P=P, bax=ax, by0=y0, f=es.result.fbest), open(out, 'w'), default=float)
            print('it', it, 'best %.4f' % es.result.fbest, '%.0fs' % (time.time() - t0), flush=True)
    P, ax, y0 = unpack(lo + np.clip(es.result.xbest, 0, 1) * span)
    print('done %.4f iou %.3f' % (es.result.fbest, V.iou(base_parts(P, ax, y0), ax, y0)[0]), flush=True)
