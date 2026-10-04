"""
infstatic.py - a sequence TS holds still (fire, fire prone): TS's soldier keeps one pose through its 6 frames, only the
muzzle flash comes and goes (frames 0, 2, 4; 0, 2, 3, 5 facing east), so each facing gets one pose for all 6 frames -
nothing moves between them, nothing jumps at the loop.  The pose is fitted to the 8 facings' frames without a flash
together (near the start pose), then each facing's arms, rifle and head to its own frame, held close to it (TS's
facings differ a little).

    python3 infstatic.py UNIT shape.json SEQ start.json iters [refine_iters]
        writes UNIT_SEQ_pose.json (the shared pose) and UNIT_SEQ_frames.json {frame: {Q, facing, step, iou}}
"""
import json, os, sys, time
import numpy as np
import inf as I
import inffit as F
import infseq as SQ
import infrefine as RF

# the widest any pose may go (standing or lying), and how far the shared fit may move each from its start
ABS = dict(pitch=(-100, 100), roll=(-30, 30), yaw=(-40, 40), dx=(-8, 8), dy=(-8, 10), sp=(-40, 30), sy=(-45, 45),
           sr=(-15, 15), hp=(-85, 30), hy=(-50, 50), lhf=(-60, 100), lha=(-15, 40), lht=(-40, 40), lkf=(0, 150),
           laf=(-40, 70), rhf=(-60, 100), rha=(-15, 40), rht=(-40, 40), rkf=(0, 150), raf=(-40, 70), gp=(-100, 140),
           gy=(-150, 90), gr=(-90, 90), rgx=(0.0, 5.5), rgy=(-2.5, 3.5), rgz=(-6.5, 4.0), lfx=(1.0, 5.5),
           lsw=(-60, 60), rsw=(-60, 60), lsf=(-60, 200), lsa=(-30, 90), lst=(-60, 60), lef=(0, 150),
           rsf=(-60, 200), rsa=(-30, 90), rst=(-60, 60), ref=(0, 150))
WIN = dict(dx=2.5, dy=2.5, rgx=1.5, rgy=1.5, rgz=1.5, lfx=1.5, yaw=15.0)


def plain_frames(unit, seq):
    """per facing, a frame of the sequence without TS's muzzle flash (and all its frames)."""
    out = []
    first, n, fc = SQ.SEQ[unit][seq]
    for f in range(8):
        ks = [first + f * n + s for s in range(n)]
        fx = [int((F.ts_classes(F.ts_frame(unit, k)) == F.FX).sum()) for k in ks]
        out.append((ks[int(np.argmin(fx))], ks))
    return out


def fit_shared(unit, S, ax, y0, frames, Q0, iters, out):
    tg = [F.Target(unit, k, f) for f, k in enumerate(frames)]
    keys = [k for k, a, b in F.qspec(Q0)]
    lo = np.array([max(ABS[k][0], Q0[k] - WIN.get(k, 35.0)) for k in keys])
    hi = np.array([min(ABS[k][1], Q0[k] + WIN.get(k, 35.0)) for k in keys])
    x0 = np.clip(np.array([Q0[k] for k in keys]), lo, hi)

    def unpack(x):
        Q = dict(Q0)
        Q.update({k: float(v) for k, v in zip(keys, x)})
        return Q

    def f(x):
        return float(np.mean([F.frame_loss(S, unpack(x), t, ax, y0) for t in tg]))

    def cb(x, fb, it, dt):
        Q = unpack(x)
        json.dump(dict(Q=Q, frames=list(frames), f=float(fb), iou=[F.iou(S, Q, t, ax, y0) for t in tg]), open(out, 'w'),
                  default=float)
        print('it', it, 'best %.4f' % fb, '%.0fs' % dt, flush=True)
    F.cma_fit(f, lo, hi, x0, iters, cb, sigma=0.12, pop=16, seed=1)


def main():
    unit, shape, seq, start = sys.argv[1:5]
    import infunit; infunit.use(unit)
    iters = int(sys.argv[5])
    riters = int(sys.argv[6]) if len(sys.argv) > 6 else 150
    js = json.load(open(shape))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    ax, y0 = js['ax'], js['y0']
    pf = plain_frames(unit, seq)
    pose = '%s_%s_pose.json' % (unit, seq)
    if not os.path.exists(pose) or json.load(open(pose)).get('done') is None:
        Q0 = dict(js['Q']); Q0.update(json.load(open(start))['Q'])
        fit_shared(unit, S, ax, y0, [k for k, ks in pf], Q0, iters, pose)
        js2 = json.load(open(pose)); js2['done'] = 1; json.dump(js2, open(pose, 'w'), default=float)
    Qs = dict(js['Q']); Qs.update(json.load(open(pose))['Q'])
    out = '%s_%s_frames.json' % (unit, seq)
    res = json.load(open(out)) if os.path.exists(out) else {}
    for f, (k, ks) in enumerate(pf):
        if str(ks[0]) in res:
            continue
        t0 = time.time()
        Q, fb, iu = RF.refine(unit, S, ax, y0, k, f, Qs, None, riters)
        res = json.load(open(out)) if os.path.exists(out) else {}
        for s, kk in enumerate(ks):
            res[str(kk)] = dict(Q=Q, f=fb, iou=iu, facing=f, step=s)
        json.dump(res, open(out, 'w'), default=float)
        print(seq, 'facing', f, 'frame', k, 'f %.3f iou %.3f' % (fb, iu), '%.0fs' % (time.time() - t0), flush=True)
    print('done', flush=True)


if __name__ == '__main__':
    main()
