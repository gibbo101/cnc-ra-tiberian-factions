"""
deathfit2.py - a death refitted to TS's frames AND TS's shadow (the mod's frames carry it): from TS's camera alone a
leg raised in the air and a leg lying further back look the same, and the first fits left the soldier half sitting with a
leg up (Luke: "leg in the air way above the shadow"; "both deaths the shadow is super weird").  TS's shadow shows where
the body really is: once TS's soldier is down, his shadow hugs him.

  1. the last frame (lying) fitted from the old pose and from lying poses (on his back or front, turned every way)
  2. backwards to the first frame: each frame from the one after it (and from its old pose), the better kept
  3. forwards: each frame from the one before it, kept if better
  4. relaxed: each frame towards the middle of its neighbours (a smooth fall)
The fall may turn him further than a step does (yaw +-110, roll +-80).

    SHADOW=1 python3 deathfit2.py UNIT SEQ iters [sweeps]
"""
import json, os, sys, time
import numpy as np
import inf as I
import inffit as F
import infseq as SQ


def lying_pen(S, Q, facing, dz, w=0.03):
    """how far a soldier TS shows lying is off the ground: his hips, chest, head, knees and ankles above where lying
    puts them (their own radii, a little over), squared, w a unit squared."""
    P = I.Pose(S, Q, I.facing_angle(facing))
    pr, cr, hr = max(S['pr']) + 0.5, max(S['cr']) + 0.6, max(S['hr']) + 0.6
    z = [(P.pelvis[0][2] + dz, pr), (P.chest[0][2] + dz, cr), (P.head[0][2] + dz, hr)]
    for s in 'lr':
        z.append((P.legs[s][2][2] + dz, 2.0)); z.append((P.legs[s][4][2] + dz, 2.0))
    return w * sum(max(0.0, a - b) ** 2 for a, b in z)


def centred(S, Q, tgt, ax, y0):
    """Q moved along the ground so the soldier's outline in TS's camera is centred where TS's is (screen x = X,
    screen y = Y / 2 on the ground)."""
    import rc
    parts, dz = I.grounded(S, Q, I.facing_angle(tgt.facing))
    cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
    cl = F.model_cls(parts, cam, tgt.win, ss=1)[..., 0]
    ys, xs = np.nonzero(cl > 0)
    ty, tx = np.nonzero(tgt.mask)
    if len(xs) == 0:
        return Q
    sx, sy = tx.mean() - xs.mean(), ty.mean() - ys.mean()
    from infstatic import ABS
    return dict(Q, dx=float(np.clip(Q['dx'] + sx, *ABS['dx'])), dy=float(np.clip(Q['dy'] + 2.0 * sy, *ABS['dy'])))


def lying_starts(Q0):
    """lying poses: on his back or front, turned every way, rolled, legs straight or apart, arms down or out."""
    out = []
    legs = [dict(lhf=0.0, rhf=0.0, lkf=5.0, rkf=5.0, lha=5.0, rha=5.0, lht=0.0, rht=0.0, laf=0.0, raf=0.0),
            dict(lhf=25.0, rhf=-5.0, lkf=30.0, rkf=10.0, lha=25.0, rha=25.0, lht=0.0, rht=0.0, laf=0.0, raf=0.0)]
    arms = [{}, dict(lsf=60.0, lsa=70.0, lef=20.0, rsf=60.0, rsa=70.0, ref=20.0)] if Q0.get('ik', 1.0) < 0.5 else [{}]
    for pitch in (-90.0, -65.0, 65.0, 90.0):
        for yaw in np.arange(-170.0, 171.0, 20.0):
            for roll in (-60.0, -30.0, 0.0, 30.0, 60.0):
                for lg in legs:
                    for am in arms:
                        q = dict(Q0, pitch=pitch, yaw=float(yaw), roll=roll, sp=0.0, sy=0.0, sr=0.0, hp=0.0, hy=0.0)
                        q.update(lg); q.update(am)
                        out.append(q)
    return out


def main():
    unit, seq, iters = sys.argv[1], sys.argv[2], int(sys.argv[3])
    sweeps = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    import infunit; infunit.use(unit)
    import infsmooth as SM
    from infstatic import ABS
    ABS['yaw'] = (-180.0, 180.0); ABS['roll'] = (-80.0, 80.0); ABS['dx'] = (-16.0, 16.0); ABS['dy'] = (-16.0, 16.0)
    SM.WIN['dx'] = SM.WIN['dy'] = 5.0           # (a fall carries him further than a step)
    # (TS's shadow shrinks to nothing as he goes down - Luke: "on the og's the shadow disappears as the unit falls, on
    # ours they still look like they're floating in midair": in a death it counts as much as the outline)
    F.W_SHADOW = max(F.W_SHADOW, float(os.environ.get('DEATH_SHADOW', 1.0)))
    F.SS = int(os.environ.get('FIT_SS', F.SS))          # (2: a coarser, faster render while fitting)
    import tsshadow as _T
    if sum(int(_T.ts_shadow(unit, k).sum()) for k, f in SQ.frames_of(unit, seq)) < 20:
        # (frames the mod draws without TS's shadow - the Jumpjet's tumble, in the air: the game draws his shadow)
        F.W_SHADOW = 0.0
        print(seq, 'no TS shadow in these frames: fitted to the outline alone', flush=True)
    js = json.load(open('%s_shape.json' % unit))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    ax, y0 = js['ax'], js['y0']
    stand = dict(js['Q'])
    frames = [k for k, f in SQ.frames_of(unit, seq)]
    out = '%s_%s_frames.json' % (unit, seq)
    old = json.load(open(out))
    bak = '%s_%s_frames_pre_shadow.json' % (unit, seq)
    if not os.path.exists(bak):
        json.dump(old, open(bak, 'w'), default=float)
    state = '%s_%s_frames_shadow.json' % (unit, seq)
    res = json.load(open(state)) if os.path.exists(state) else {}
    facing = old[str(frames[0])]['facing']
    if str(facing) in (json.load(open('%s_stand_frames.json' % unit)) if os.path.exists('%s_stand_frames.json' % unit) else {}):
        stand = dict(stand, **json.load(open('%s_stand_frames.json' % unit))[str(facing)]['Q'])
    cpath = '%s_%s_case.json' % (unit, seq)
    case = json.load(open(cpath)) if os.path.exists(cpath) else None

    def with_case(Q, k):
        if case is None:
            return Q
        return dict(Q, cfx=case['cfx'], cfy=case['cfy'], cfa=case['cfa'], cft=case.get('cft', 0.0),
                    cfix=float(case['cfix'].get(str(k), 0.0)))
    tg = {}
    # the frames TS draws lying as the last one does (the same body, blood aside) lie on the ground too
    import tsshadow as T
    last = F.ts_classes(F.ts_frame(unit, frames[-1]))
    lying = set()
    for k in frames[::-1]:
        c = F.ts_classes(F.ts_frame(unit, k))
        va = (c != F.FX) & (last != F.FX)
        if ((c > 0) != (last > 0))[va].sum() <= 3:
            lying.add(k)
        else:
            break
    print(seq, 'lying frames', sorted(lying), flush=True)
    import ground
    w_legs = float(os.environ.get('LEGS', 0.003))
    # (GUN_LINE: the gun laid along TS's gun in every frame too - the Ghost's railgun, flung up and then lying out
    # beside him, which a fit to the body alone hid under him)
    guns = {}

    def gun_pen(S_, Q_, k, dz_):
        if not os.environ.get('GUN_LINE') or (Q_.get('ik', 1.0) < 0.5 and Q_.get('gone', 0.0) < 0.5):
            return 0.0
        import gunline
        if k not in guns:
            guns[k] = gunline.GunTarget(unit, k)
        return guns[k].pen(S_, Q_, facing, ax, y0, dz_)
    F.EXTRA = lambda S_, Q_, t_, dz_: ((lying_pen(S_, Q_, facing, dz_) if t_.k in lying else 0.0) +
                                       ground.legs_down(S_, Q_, facing, dz_, w=w_legs) + gun_pen(S_, Q_, t_.k, dz_))

    def tgt(k):
        if k not in tg:
            tg[k] = F.Target(unit, k, facing)
        return tg[k]

    def loss(Q, k):
        return F.frame_loss(S, with_case(Q, k), tgt(k), ax, y0)

    def put(k, Q, f, tag):
        res[str(k)] = dict(Q=Q, f=f, iou=F.iou(S, with_case(Q, k), tgt(k), ax, y0), facing=facing, sweep=0, how=tag)
        json.dump(res, open(state, 'w'), default=float)

    def oldQ(k):
        return dict(stand, **old[str(k)]['Q'])

    # 1: the last frame
    kl = frames[-1]
    if str(kl) not in res:
        t0 = time.time()
        Q0 = oldQ(kl)
        starts, seen = [Q0], set()
        for q in lying_starts(Q0):
            # (pitch 90 turns yaw into roll: one start per way the body lies)
            B = I.Rz(I.facing_angle(facing) + q['yaw']) @ I.Ry(q['pitch']) @ I.Rx(q['roll'])
            key = tuple(np.round(B.ravel(), 1)) + (q['lhf'], q.get('lsf', 0.0))
            if key in seen:
                continue
            seen.add(key)
            q = centred(S, with_case(q, kl), tgt(kl), ax, y0)
            starts.append(centred(S, q, tgt(kl), ax, y0))
        sc = [(loss(q, kl), i) for i, q in enumerate(starts)]
        sc.sort()
        print(seq, len(starts), 'starts, best', ['%.3f' % v for v, i in sc[:8]], flush=True)
        best = None
        for v, i in sc[:8]:
            q = starts[i]
            Q, fb, iu = SM.fit_one(unit, S, ax, y0, kl, facing, with_case(q, kl), [], iters, win=50.0, sigma=0.12)
            l = loss(Q, kl)
            print(seq, 'last', kl, 'start %.3f -> %.3f iou %.3f' % (loss(q, kl), l, iu), flush=True)
            if best is None or l < best[1]:
                best = (Q, l)
        put(kl, best[0], best[1], 'last')
        print(seq, 'last frame', kl, 'old %.3f new %.3f' % (loss(Q0, kl), best[1]), '%.0fs' % (time.time() - t0), flush=True)
    # 2: backwards
    for i in range(len(frames) - 2, 0, -1):
        k = frames[i]
        if str(k) in res:
            continue
        t0 = time.time()
        nxt = dict(stand, **res[str(frames[i + 1])]['Q'])
        cands = []
        Q, fb, iu = SM.fit_best(unit, S, ax, y0, k, facing, with_case(nxt, k), [(SM.W_PREV, with_case(nxt, k))],
                                iters, falls=True)
        cands.append((loss(Q, k), Q, 'from next'))
        Qo = oldQ(k)
        Q2, fb2, iu2 = SM.fit_one(unit, S, ax, y0, k, facing, with_case(Qo, k), [], max(iters // 2, 60), win=30.0,
                                  sigma=0.08)
        cands.append((loss(Q2, k), Q2, 'from old'))
        cands.append((loss(Qo, k), Qo, 'old'))           # (a short fit can end a touch worse than where it began)
        cands.sort(key=lambda t: t[0])
        put(k, cands[0][1], cands[0][0], cands[0][2])
        print(seq, 'back', k, ' '.join('%s %.3f' % (c[2], c[0]) for c in cands), 'old %.3f' % loss(Qo, k),
              '%.0fs' % (time.time() - t0), flush=True)
    if str(frames[0]) not in res:
        Q0 = oldQ(frames[0])
        put(frames[0], Q0, loss(Q0, frames[0]), 'old')
    # 3: forwards
    fw = '%s_%s_fwd.done' % (unit, seq)
    if not os.path.exists(fw):
        for i in range(1, len(frames)):
            k = frames[i]
            t0 = time.time()
            prev = dict(stand, **res[str(frames[i - 1])]['Q'])
            Q, fb, iu = SM.fit_best(unit, S, ax, y0, k, facing, with_case(prev, k), [(SM.W_PREV, with_case(prev, k))],
                                    max(iters * 2 // 3, 60), falls=True, keep=1)
            a, b = res[str(k)]['f'], loss(Q, k)
            if b < a - 0.003:
                put(k, Q, b, 'from prev')
            print(seq, 'fwd', k, 'had %.3f from prev %.3f' % (a, b), '%.0fs' % (time.time() - t0), flush=True)
        open(fw, 'w').write('done')
    # 4: relax
    for sw in range(1, sweeps + 1):
        for i, k in enumerate(frames):
            if i == 0 or res[str(k)].get('sweep', 0) >= sw:
                continue
            t0 = time.time()
            Qs = [dict(stand, **res[str(kk)]['Q']) for kk in frames]
            before = with_case(Qs[i - 1], k)
            if i + 1 < len(frames):
                after = with_case(Qs[i + 1], k)
                pulls = [(SM.W_MID, {q: 0.5 * (before[q] + after[q]) for q in before})]
            else:
                pulls = [(SM.W_PREV, before)]
            Q, fb, iu = SM.fit_one(unit, S, ax, y0, k, facing, with_case(Qs[i], k), pulls, max(iters // 2, 40), win=20.0,
                                   sigma=0.06)
            l = loss(Q, k)
            res[str(k)] = dict(Q=Q, f=l, iou=iu, facing=facing, sweep=sw, how=res[str(k)].get('how', ''))
            json.dump(res, open(state, 'w'), default=float)
            print(seq, 'sweep', sw, 'frame', k, 'f %.3f iou %.3f' % (l, iu), '%.0fs' % (time.time() - t0), flush=True)
    # the result in the frames file the renderer reads (the old one kept as _pre_shadow)
    json.dump({k: dict(v, sweep=99) for k, v in res.items()}, open(out, 'w'), default=float)
    print('done', flush=True)


if __name__ == '__main__':
    main()
