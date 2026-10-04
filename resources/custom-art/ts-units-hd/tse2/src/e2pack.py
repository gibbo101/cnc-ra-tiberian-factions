"""
e2pack.py - the Disc Thrower's rucksack fitted to TS's frames (the 8 standing frames and the run's), his poses held: its
size, how far it stands off his back, how high, its lean and how round (Luke: TS's "has a rounded curve" and is far
thicker than the box it was).

    python3 e2pack.py iters        writes e2_shape.json's rucksack sizes (the old kept as e2_shape_pre_pack.json)
"""
import json, os, sys, time
import numpy as np
import infunit; infunit.use('e2')
import inf as I
import inffit as F

SPEC = [('rkd', 1.2, 4.2, 2.6), ('rkw', 3.0, 5.6, 4.3), ('rkh', 3.5, 6.8, 5.0), ('rkz', -2.5, 3.5, 0.9),
        ('rko', -1.5, 0.6, 0.3), ('rkt', -5.0, 30.0, 6.0), ('rkr', 1.0, 1.7, 1.25), ('rkf', 0.0, 1.0, 0.6),
        ('rkh2', 0.8, 1.6, 1.1)]
# (ROUND=1: a soft round bag - TS's crawl frames show it as a big dome on his back (Luke: "a rounded curve", "nowhere
# near as thick"): the box only cuts it flat against his back, its corners all rounded off; and it may not sink into his
# back to stand less proud)
import os as _os
if _os.environ.get('ROUND'):
    SPEC = [(k, a, (1.06 if k == 'rkr' else b), (1.02 if k == 'rkr' else c)) for k, a, b, c in SPEC]


def main():
    iters = int(sys.argv[1])
    js = json.load(open('e2_shape.json'))
    if not os.path.exists('e2_shape_pre_pack.json'):
        json.dump(js, open('e2_shape_pre_pack.json', 'w'), indent=1, default=float)
    S0 = dict(I.S0_E2); S0.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    ax, y0 = js['ax'], js['y0']
    st = json.load(open('e2_stand_frames.json'))
    wk = json.load(open('e2_walk_frames.json'))
    items = [(dict(js['Q'], **st[str(f)]['Q']), F.Target('e2', f, f)) for f in range(8)]
    for k in sorted(wk, key=int):
        if (int(k) - 8) % 6 in (0, 3):
            items.append((dict(js['Q'], **wk[k]['Q']), F.Target('e2', int(k), wk[k]['facing'])))
    if os.environ.get('ROUND'):
        # (and his crawl, where TS shows the pack from above: the facings TS drew)
        cr = json.load(open('e2_crawl_frames.json'))
        for k in sorted(cr, key=int):
            v = cr[k]
            if v['step'] in (0, 3) and v['facing'] in (0, 4, 5, 6, 7):
                items.append((dict(js['Q'], **v['Q']), F.Target('e2', int(k), v['facing'])))
    keys = [k for k, a, b, c in SPEC]
    lo = np.array([a for k, a, b, c in SPEC]); hi = np.array([b for k, a, b, c in SPEC])
    x0 = np.clip(np.array([S0.get(k, c) for k, a, b, c in SPEC]), lo, hi)
    x0[keys.index('rkr')] = max(x0[keys.index('rkr')], 1.25) if not os.environ.get('ROUND') else 1.02

    def shape(x):
        S = dict(S0); S.update({k: float(v) for k, v in zip(keys, x)}); S['ruck'] = 1
        return S

    def loss(x):
        S = shape(x)
        return float(np.mean([F.frame_loss(S, Q, t, ax, y0) for Q, t in items]))
    print('frames', len(items), 'start %.4f' % loss(x0), 'old box %.4f' % float(np.mean(
        [F.frame_loss(dict(S0, rkr=0.0), Q, t, ax, y0) for Q, t in items])), flush=True)
    best = {}

    def cb(x, fb, it, dt):
        best['x'] = x; best['f'] = fb
        print('it', it, 'f %.4f' % fb, ' '.join('%s %.2f' % (k, v) for k, v in zip(keys, x)), '%.0fs' % dt, flush=True)
    F.cma_fit(loss, lo, hi, x0, iters, cb, sigma=0.15, pop=12, seed=1)
    S = shape(best['x'])
    js['S'].update({k: float(S[k]) for k in keys})
    json.dump(js, open(os.environ.get('PACK_OUT', 'e2_shape_pack.json'), 'w'), indent=1, default=float)
    print('ious', ' '.join('%.3f' % F.iou(S, Q, t, ax, y0) for Q, t in items), flush=True)
    print('done', flush=True)


if __name__ == '__main__':
    main()
