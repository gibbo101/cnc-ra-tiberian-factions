"""
infreport.py - an infantry unit's numbers for its README: per sequence, how well the fitted soldier covers TS's frames
in TS's own camera (silhouette overlap, effects left out), how the finished HD frames overlap the mod's current ones,
how far the looping sequences' landmarks move a step (no jumps), and where the standing soldier's feet land.

    python3 infreport.py UNIT shape.json FRAMES_DIR out.json
"""
import json, os, sys
import numpy as np
from PIL import Image
import inf as I
import inffit as F
import infall as AL
import infseq as SQ
import motion as M

SEQS = ['stand', 'walk', 'idle1', 'idle2', 'crawl', 'death1', 'death2', 'fire', 'prone_fire', 'lie_down', 'get_up',
        'fly', 'hover', 'fire_fly', 'tumble', 'heal']


def seq_frames(unit, seq):
    first, n, fc = SQ.SEQ[unit][seq]
    if fc == 8:
        return [first + f * n + s for f in range(8) for s in range(n)]
    if seq == 'stand':
        return list(range(8))
    return [first + i for i in range(n)]


def main():
    unit, shape, fdir, out = sys.argv[1:5]
    import infunit; infunit.use(unit)
    js = json.load(open(shape))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    tab = AL.pose_table(unit, dict(js['Q']))
    d, name = F.UNITS[unit]
    stem = 'ts' + name.lower()
    mod = F.ROOT + '%s/in-mod/ts%s/frames/ts%s-%%04d.png' % (d, name.lower(), name.lower())
    rep = dict(ts={}, mod={}, motion={}, feet=None)
    for seq in SEQS:
        if seq not in SQ.SEQ[unit]:
            continue
        ks = [k for k in seq_frames(unit, seq) if k in tab]
        if not ks:
            continue
        ious, movs = [], []
        for k in ks:
            Q, f = tab[k]
            ious.append(F.iou(S, Q, F.Target(unit, k, f), js['ax'], js['y0']))
            p = os.path.join(fdir, '%s-%04d.png' % (stem, k))
            if os.path.exists(p):
                a = np.asarray(Image.open(p))[..., 3] > 250
                b = np.asarray(Image.open(mod % k).convert('RGBA'))[..., 3] > 250
                movs.append((a & b).sum() / max((a | b).sum(), 1))
        rep['ts'][seq] = float(np.mean(ious))
        if movs:
            rep['mod'][seq] = float(np.mean(movs))
        print(seq, 'TS %.3f' % rep['ts'][seq], 'mod %.3f' % rep['mod'].get(seq, -1), flush=True)
    # the looping sequences (E2's throws are loops too; E1's fire holds still, so its are 0)
    for seq in ('walk', 'crawl', 'fire', 'prone_fire'):
        worst = 0.0
        for f in range(8):
            rows = M.report(unit, S, js['Q'], {str(k): dict(Q=tab[k][0], facing=tab[k][1]) for k in tab}, seq, f)
            worst = max(worst, max(max(v) for v in rows.values()))
        rep['motion'][seq] = worst
    lows, mlows = [], []
    for k in range(8):
        p = os.path.join(fdir, '%s-%04d.png' % (stem, k))
        if os.path.exists(p):
            a = np.asarray(Image.open(p))[..., 3] > 250
            lows.append(int(np.nonzero(a.any(1))[0].max()))
            b = np.asarray(Image.open(mod % k).convert('RGBA'))[..., 3] > 250
            mlows.append(int(np.nonzero(b.any(1))[0].max()))
    rep['feet'] = lows
    rep['feet_mod'] = mlows
    json.dump(rep, open(out, 'w'), indent=1)
    print(json.dumps(rep))


if __name__ == '__main__':
    main()
