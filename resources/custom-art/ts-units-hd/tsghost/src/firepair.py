"""
firepair.py - fire (and fire prone) the way TS draws it: in each facing TS alternates two poses - between shots the
Ghost holds his railgun at his hip angled across to his left, on each shot he swings it round to point along his facing
with the flash at its muzzle (Luke: "og moving his gun as firing and pointing in right direction").  infstatic.py had one
pose for all 6 frames (and the facings' bodies shared), so the gun settled pointing down between the two.  Here each
facing's frames are split by TS's body (the frames with the same body, flash aside, are one pose) and each pose fitted
to its frame on its own: silhouette and colours, the gun along TS's gun (gunline.py) and its muzzle where TS's flash
starts, the body held near the facing's old pose; prone, on the ground (ground.py) with TS's shadow.

    python3 firepair.py UNIT SEQ iters [FACINGS]      (rewrites UNIT_SEQ_frames.json; the old one kept as _pre_pair)
"""
import json, os, sys, time
import numpy as np
import inf as I
import inffit as F
import infseq as SQ

W_BODY = 0.002
GUN = ('gy', 'gp', 'gr', 'rgx', 'rgy', 'rgz', 'lfx', 'lsw', 'rsw', 'rsf', 'rsa', 'rst', 'ref', 'lsf', 'lsa', 'lst', 'lef')


def groups(unit, ks):
    """TS's frames of one facing grouped by the body they show (the flash's pixels aside): one group if TS holds one
    pose throughout, else its two alternating poses (the shot and between shots: steps 0, 2, 4 and 1, 3, 5) if each
    holds within a few pixels (the flash's dark edge changes a few), else frame by frame."""
    cl = [F.ts_classes(F.ts_frame(unit, k)) for k in ks]

    def diff(i, j):
        va = (cl[i] != F.FX) & (cl[j] != F.FX)
        return int(((cl[i] > 0) != (cl[j] > 0))[va].sum())
    if all(diff(0, i) <= 3 for i in range(1, len(ks))):
        return [list(ks)]
    par = [[ks[i] for i in range(0, len(ks), 2)], [ks[i] for i in range(1, len(ks), 2)]]
    if all(diff(ks.index(g[0]), ks.index(k)) <= 16 for g in par for k in g):
        return par
    return [[k] for k in ks]


def main():
    unit, seq, iters = sys.argv[1], sys.argv[2], int(sys.argv[3])
    facings = [int(v) for v in sys.argv[4].split(',')] if len(sys.argv) > 4 else list(range(8))
    import infunit; infunit.use(unit)
    import infsmooth as SM
    import gunline as G
    import ground
    from infstatic import ABS
    prone = seq == 'prone_fire'
    if prone and F.W_SHADOW <= 0:
        F.W_SHADOW = 0.5
    if unit == 'e2' and F.W_THIN <= 1.0:
        # (the Disc Thrower's arms, stretched out as he winds up and throws, are TS lines 2 px wide: counted three
        # times, or the fit keeps them tucked in)
        F.W_THIN = 3.0
    js = json.load(open('%s_shape.json' % unit))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    ax, y0 = js['ax'], js['y0']
    path = '%s_%s_frames.json' % (unit, seq)
    old = json.load(open(path))
    bak = '%s_%s_frames_pre_pair.json' % (unit, seq)
    if not os.path.exists(bak):
        json.dump(old, open(bak, 'w'), default=float)
    old = json.load(open(bak))
    state = '%s_%s_frames_pair.json' % (unit, seq)
    res = json.load(open(state)) if os.path.exists(state) else {}
    first, n, fc = SQ.SEQ[unit][seq]
    for f in facings:
        ks = [first + f * n + s for s in range(n)]
        for g in groups(unit, ks):
            if all(str(k) in res for k in g):
                continue
            t0 = time.time()
            # the group's frame with the least flash over the body; the flash's start from a frame that has one
            fx = [int((F.ts_classes(F.ts_frame(unit, k)) == F.FX).sum()) for k in g]
            k0 = g[int(np.argmin(fx))]
            tgt = F.Target(unit, k0, f)
            gt = G.GunTarget(unit, k0)
            if max(fx) > 0:
                kf = g[int(np.argmax(fx))]
                gt.root = G.flash_root(unit, kf, gt.line if gt.line is not None else G.ts_line(unit, kf))
                if gt.line is None:
                    gt.line = G.ts_line(unit, kf)
            Q0 = dict(js['Q'], **old[str(k0)]['Q'])
            keys = [q for q, a, b in F.qspec(Q0)]
            sc = SM.scale(keys)
            # (the Disc Thrower's throw is a real movement, fitted smooth before: each frame held near it, arms too, so
            # only what TS's ground and shadow say moves - his legs down, his body on the ground)
            body = np.array([q not in GUN or (unit == 'e2' and prone) for q in keys])
            x_old = np.array([Q0[q] for q in keys])

            def loss(Q):
                parts, dz = I.grounded(S, Q, I.facing_angle(f))
                l = F.parts_loss(parts, tgt, ax, y0)
                if tgt.shadow is not None:
                    import rc
                    l += F.W_SHADOW * tgt.shadow.loss(parts, rc.Cam((0, -1), 30.0, 1.0, (ax, y0)))
                l += gt.pen(S, Q, f, ax, y0, dz)
                if prone:
                    # (the Disc Thrower throws from prone: his chest and throwing arm come up off the ground)
                    l += ground.lying(S, Q, f, dz, head=False, elbows=unit != 'e2', chest=False)
                x = np.array([Q[q] for q in keys])
                return l + W_BODY * float((((x - x_old) / sc)[body] ** 2).sum())
            starts = [Q0] + SM.line_starts(unit, S, ax, y0, k0, f, Q0, n=4) if gt.line is not None else [Q0]
            if gt.line is None:
                starts += [dict(Q0, gy=gy, gp=gp) for gy, gp in SM.RIFLE_STARTS]
            starts.sort(key=loss)
            best = None
            for st in starts[:3]:
                lo = np.array([max(ABS[q][0], st[q] - SM.WIN.get(q, 35.0)) for q in keys])
                hi = np.array([min(ABS[q][1], st[q] + SM.WIN.get(q, 35.0)) for q in keys])
                x0 = np.clip(np.array([st[q] for q in keys]), lo, hi)
                bx = {}

                def cb(x, fb, it, dt):
                    bx['x'] = x; bx['f'] = fb

                def unpack(x):
                    Q = dict(st); Q.update({q: float(v) for q, v in zip(keys, x)})
                    return Q
                F.cma_fit(lambda x: loss(unpack(x)), lo, hi, x0, iters, cb, sigma=0.1, pop=16, seed=1)
                Q = unpack(bx['x'])
                if best is None or bx['f'] < best[1]:
                    best = (Q, bx['f'])
            Q, fb = best
            iu = F.iou(S, Q, tgt, ax, y0)
            dz = I.grounded(S, Q, I.facing_angle(f))[1]
            for k in g:
                res[str(k)] = dict(Q=Q, f=fb, iou=iu, facing=f, step=k - ks[0], group=g, gun=gt.pen(S, Q, f, ax, y0, dz))
            json.dump(res, open(state, 'w'), default=float)
            print(seq, 'facing', f, 'frames', g, 'old %.3f new %.3f iou %.3f (old %.3f) gun %.2f -> %.2f' % (
                loss(Q0), fb, iu, old[str(k0)].get('iou', 0), gt.pen(S, Q0, f, ax, y0, I.grounded(S, Q0, I.facing_angle(f))[1]),
                gt.pen(S, Q, f, ax, y0, dz)), '%.0fs' % (time.time() - t0), flush=True)
    if all(str(first + i) in res for i in range(8 * n)):
        json.dump(res, open(path, 'w'), default=float)
        print('written', path, flush=True)
    print('done', flush=True)


if __name__ == '__main__':
    main()
