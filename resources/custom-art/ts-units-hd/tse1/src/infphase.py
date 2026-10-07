"""
infphase.py - which step of a looping sequence each of TS's facings starts on: the shared cycle's poses are laid over
each facing's TS frames at every cyclic offset, and a facing takes the offset its frames fit clearly best (TS draws
some facings' loops starting a step on: E2's run facing west).  Offsets 3 apart swap the legs, so the one nearest 0
is kept unless the other is clearly better.

    python3 infphase.py UNIT shape.json SEQ cycle.json [margin]
        writes UNIT_SEQ_phase.json [8 offsets] (merged with the offsets the cycle was fitted with)
"""
import json, os, sys
import numpy as np


def main():
    unit, shape, seq, cycle = sys.argv[1:5]
    margin = float(sys.argv[5]) if len(sys.argv) > 5 else 0.03
    import infunit; infunit.use(unit)
    import infcycle as C, inffit as F, infseq as SQ
    js, S = C.load_shape(shape)
    lay = C.layout(C.spec_of(unit, seq))
    x = C.load_coef(cycle, lay)
    N = C.N
    Qs = [C.step_pose(dict(js['Q']), lay, x, s, None, seq) for s in range(N)]
    old = C.phase_of(unit, seq)
    ts = SQ.frames_of(unit, seq)
    new = []
    for f in range(8):
        # TS step t shown by cycle step t + offset
        sc = [np.mean([F.iou(S, Qs[(t + r) % N], F.Target(unit, ks[f], f), js['ax'], js['y0']) for t, ks in ts])
              for r in range(N)]
        best = int(np.argmax(sc))
        keep = old[f]
        r = best if sc[best] > sc[keep] + margin else keep
        new.append(r)
        print('facing', f, ' '.join('%.3f' % v for v in sc), ' was', keep, 'now', r, flush=True)
    json.dump(new, open('%s_%s_phase.json' % (unit, seq), 'w'))
    print('changed' if new != old else 'unchanged', new)


if __name__ == '__main__':
    main()
