"""
motion.py - how far the soldier's landmarks (the muzzle, the rifle's back end, the hands, the head, the feet) move from
each step of a looping sequence to the next, the last step back to the first included (TS px, in the soldier's own
frame, so the run's forward travel is left out): a jump shows as one step much bigger than the rest.

    python3 motion.py UNIT shape.json poses.json SEQ [facing]
"""
import json, sys
import numpy as np
import inf as I
import infcheck as C
import infseq as SQ


def landmarks(S, Q):
    P = I.Pose(S, Q, 0.0)
    out = dict(lhand=P.arms['l'][4], rhand=P.arms['r'][4], head=P.head[0], lfoot=P.legs['l'][4],
               rfoot=P.legs['r'][4])
    if S.get('rifle', 1) > 0.5:                      # a unit with a rifle (E1): its muzzle and back end too
        G0, RG = P.rifle
        out.update(muzzle=G0 + RG[:, 0] * (S['gl'] - S['gg']), butt=G0 - RG[:, 0] * S['gg'])
    dz = -min(p.low for p in I.parts(S, Q, 0.0))
    return {k: v + np.array([0, 0, dz]) - np.array([Q['dx'], Q['dy'], 0]) for k, v in out.items()}


def report(unit, S, Qbase, poses, seq, facing):
    steps = SQ.frames_of(unit, seq)
    L = []
    for s, ks in steps:
        Q, f = C.pose_for(ks[facing], poses, Qbase)
        L.append(landmarks(S, Q))
    n = len(L)
    rows = {}
    for key in L[0]:
        rows[key] = [float(np.linalg.norm(L[(i + 1) % n][key] - L[i][key])) for i in range(n)]
    return rows


def main():
    unit, shape, poses, seq = sys.argv[1:5]
    import infunit; infunit.use(unit)
    facings = [int(sys.argv[5])] if len(sys.argv) > 5 else range(8)
    js = json.load(open(shape))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    P = json.load(open(poses))
    worst = []
    for f in facings:
        rows = report(unit, S, js['Q'], P, seq, f)
        print('facing', f)
        for k, v in rows.items():
            print('  %-7s' % k, ' '.join('%5.1f' % x for x in v), '  max/mean %.2f' % (max(v) / max(np.mean(v), 1e-6)))
        worst.append(max(max(v) for v in rows.values()))
    print('largest step of any landmark: %.1f px' % max(worst))


if __name__ == '__main__':
    main()
