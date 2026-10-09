"""
infseq.py - an infantry unit's sequences (TS's own Sequence layout, which the mod keeps frame for frame) and the fits of
their poses to TS's frames:

  steps in 8 facings (walk, fire, crawl, fire prone, lie down, get up): one pose a step, fitted to that step's frame in
      all 8 facings together (inffit.fit_pose)
  single-facing sequences (the idles, the deaths): one pose a frame, fitted to its frame alone, starting from the frame
      before and held close to it (smooth motion)

    python3 infseq.py UNIT shape.json SEQ [iters]      writes UNIT_SEQ.json: {frame: pose}
"""
import json, os, sys, time
import numpy as np
import inf as I
import inffit as F

# E1Sequence (the hand-off README): name -> (first frame, frames a facing, facings) or (first, count, facing)
SEQ = {'e1': dict(stand=(0, 1, 8), walk=(8, 6, 8), idle1=(56, 15, 'W'), idle2=(71, 14, 'E'), crawl=(86, 6, 8),
                  death1=(134, 15, None), death2=(149, 15, None), fire=(164, 6, 8), prone_fire=(212, 6, 8),
                  lie_down=(260, 2, 8), get_up=(276, 2, 8))}
# the Jumpjet's own: idle 2 runs to 85; his deaths are empty in TS (he dies by the tumble); flight after 291: fly,
# hover and fire in the air (6 a facing each), the tumble (15, one facing)
SEQ['jj'] = dict(SEQ['e1'], idle2=(71, 15, 'E'), fly=(292, 6, 8), hover=(340, 6, 8), fire_fly=(388, 6, 8),
                 tumble=(436, 15, None))
# the Medic's: his fire frames are empty (unarmed); idle 2 runs to 85 (TS's frame 85: he picks his case up again); the
# heal, one 15-frame strip whatever the facing
SEQ['medic'] = dict(SEQ['e1'], idle2=(71, 15, 'E'), heal=(292, 15, None))
# the Cyborg Commando's CyborgSequence (its hand-off README): 9 steps a facing walking and crawling, no lying down or
# getting up (it never goes prone: its crawl is a crippled cyborg's)
SEQ['cyc2'] = dict(stand=(0, 1, 8), walk=(8, 9, 8), idle1=(80, 15, 'W'), idle2=(95, 15, 'E'), crawl=(110, 9, 8),
                   death1=(182, 15, None), death2=(197, 15, None), fire=(212, 6, 8), prone_fire=(260, 6, 8))
FACING = {'N': 0, 'NW': 1, 'W': 2, 'SW': 3, 'S': 4, 'SE': 5, 'E': 6, 'NE': 7}


def frames_of(unit, name):
    """[(step, [frame per facing])] for 8-facing sequences, [(frame, facing)] for the others."""
    first, n, fc = SEQ[unit][name]
    if fc == 8:
        return [(s, [first + f * n + s for f in range(8)]) for s in range(n)]
    return [(first + i, FACING.get(fc)) for i in range(n)]


def fit_frame(unit, S, ax, y0, k, facing, Q0, iters, w_smooth=0.004, yaw_free=40.0, sigma=0.08):
    """one pose on one frame, near Q0."""
    tgt = F.Target(unit, k, facing if facing is not None else 0)
    lo, hi, x0 = [], [], []
    for key, a, b in F.qspec(Q0):
        w = {'yaw': yaw_free, 'dx': 3.0, 'dy': 3.0, 'rgx': 2.0, 'rgy': 2.0, 'rgz': 2.0, 'lfx': 2.0}.get(key, 60.0)
        lo.append(max(a, Q0[key] - w)); hi.append(min(b, Q0[key] + w)); x0.append(Q0[key])
    lo, hi, x0 = np.array(lo, float), np.array(hi, float), np.array(x0, float)
    keys = [k_ for k_, a, b in F.qspec(Q0)]
    sc = np.array([{'dx': 1.0, 'dy': 1.0, 'rgx': 1.0, 'rgy': 1.0, 'rgz': 1.0, 'lfx': 1.0}.get(k_, 10.0) for k_ in keys])

    def f(x):
        Q, i = F.unpack_pose(x, Q0)
        return F.frame_loss(S, Q, tgt, ax, y0) + w_smooth * float((((x - x0) / sc) ** 2).sum())
    best = {}

    def cb(x, fb, it, dt):
        best['x'] = x; best['f'] = fb
    F.cma_fit(f, lo, hi, x0, iters, cb, sigma=sigma, pop=16)
    Q, i = F.unpack_pose(best['x'], Q0)
    return Q, best['f'], F.iou(S, Q, tgt, ax, y0)


if __name__ == '__main__':
    unit, shape, name = sys.argv[1], sys.argv[2], sys.argv[3]
    iters = int(sys.argv[4]) if len(sys.argv) > 4 else 300
    js = json.load(open(shape))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    ax, y0 = js['ax'], js['y0']
    out = '%s_%s.json' % (unit, name)
    res = json.load(open(out)) if os.path.exists(out) else {}
    Q = dict(js['Q'])
    for k, facing in frames_of(unit, name):
        if str(k) in res:
            Q = dict(res[str(k)]['Q']); continue
        t0 = time.time()
        Q, fb, iu = fit_frame(unit, S, ax, y0, k, facing, Q, iters)
        res[str(k)] = dict(Q=Q, f=fb, iou=iu)
        json.dump(res, open(out, 'w'), default=float)
        print('frame', k, 'f %.3f iou %.3f' % (fb, iu), '%.0fs' % (time.time() - t0), flush=True)
    print('done', flush=True)
