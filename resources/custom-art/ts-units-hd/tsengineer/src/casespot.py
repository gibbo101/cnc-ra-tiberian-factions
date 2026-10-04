"""
casespot.py - where the Medic sets his case down (idle 2, the heal) or drops it (the deaths), read off TS's frames: the
case's cross (TS's pure red, a plus in the case's light grey) in the frames where it stays put; the spot (cfx, cfy)
and the way its broad face looks (cfa) fitted so the model's case and cross land on TS's; and each frame's cfix (1
on the ground, 0 in his hand).

    python3 casespot.py UNIT SEQ FACING    -> UNIT_SEQ_case.json {cfx, cfy, cfa, cfix: {frame: v}, cross: {frame: xy}}
"""
import json, os, sys
import numpy as np
import rc
import inf as I
import inffit as F
import infseq as SQ


def case_cross(a):
    """the centre (x, y) of the case's cross in TS frame a: red pixels in a plus, light grey round it; or None."""
    red = (a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 0) & (a[..., 3] > 0)
    lum = a[..., :3].astype(float) @ np.array([0.299, 0.587, 0.114])
    neutral = (np.abs(a[..., 0].astype(int) - a[..., 2].astype(int)) < 30) & (a[..., 3] > 0)
    H, W = red.shape
    best = None
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if not red[y, x]:
                continue
            arms = int(red[y - 1, x]) + int(red[y + 1, x]) + int(red[y, x - 1]) + int(red[y, x + 1])
            if arms < 2:
                continue
            ring = [(y - 1, x - 1), (y - 1, x + 1), (y + 1, x - 1), (y + 1, x + 1)]
            grey = sum(1 for yy, xx in ring if neutral[yy, xx] and lum[yy, xx] >= 120)
            # (a cross on the case: its corners the case's light grey, not blood)
            score = arms + grey
            if grey >= 2 and (best is None or score > best[0]):
                best = (score, (x + 0.5, y + 0.5))
    return None if best is None else best[1]


def case_parts(S, Q, facing):
    ps, dz = I.grounded(S, Q, I.facing_angle(facing))
    return [p for p in ps if p.name == 'medkit' or p.name.startswith('case_cross')], ps


def main():
    unit, seq, facing = sys.argv[1], sys.argv[2], int(sys.argv[3])
    import infunit; infunit.use(unit)
    js = json.load(open('%s_shape.json' % unit))
    S = dict(F.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    Q0 = dict(js['Q'])
    sf = json.load(open('%s_stand_frames.json' % unit))
    if str(facing) in sf:
        Q0.update(sf[str(facing)]['Q'])
    frames = [k for k, f in SQ.frames_of(unit, seq)]
    xy = {k: case_cross(F.ts_frame(unit, k)) for k in frames}
    # on the ground: the frames whose cross stays within a pixel of the most common spot
    pts = np.array([v for v in xy.values() if v is not None])
    if not len(pts):
        print('no cross'); return
    cnt = [(np.linalg.norm(pts - p, axis=1) <= 1.01).sum() for p in pts]
    home = pts[int(np.argmax(cnt))]
    on = {k: (v is not None and np.linalg.norm(np.array(v) - home) <= 1.01) for k, v in xy.items()}
    print('cross', {k: (None if v is None else tuple(round(c, 1) for c in v)) for k, v in xy.items()})
    print('on the ground', [k for k in frames if on[k]], 'home', home)
    cam = rc.Cam((0, -1), 30.0, 1.0, (js['ax'], js['y0']))
    tg = [k for k in frames if on[k]]
    targets = []
    for k in tg:
        a = F.ts_frame(unit, k)
        red = (a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 0) & (a[..., 3] > 0)
        x, y = xy[k]
        win = np.zeros_like(red); win[int(y) - 1:int(y) + 2, int(x) - 1:int(x) + 2] = True
        targets.append(red & win)
    T = np.any(targets, axis=0)
    H, W = T.shape

    def model_red(cfx, cfy, cfa, cft=0.0):
        Q = dict(Q0, cfix=1.0, cfx=cfx, cfy=cfy, cfa=cfa, cft=cft)
        cps, ps = case_parts(S, Q, facing)
        t, who, nrm, O = rc.render_ids(cps, cam, 0, 0, W, H, ss=3, zstart=80.0)
        names = np.array([''] + [p.name for p in cps])[who + 1].reshape(H, 3, W, 3).transpose(0, 2, 1, 3).reshape(H, W, 9)
        return np.char.startswith(names, 'case_cross').sum(-1) >= 4

    def score(v):
        M = model_red(*v)
        return 2.0 * float((M & T).sum()) / max(float(M.sum() + T.sum()), 1.0)
    # start: the cross unprojected at the case's middle height, the face looking at the camera
    mk = np.asarray(S['mk'], float)
    pr = home[0] - cam.ox; q = home[1] - cam.oy
    z = mk[2]
    pt = (q + cam.cE * z) / cam.sE
    P = pr * np.asarray(cam.R, float) + pt * np.asarray(cam.T, float)
    best = None
    tilts = [float(t) for t in os.environ.get('CASE_TILTS', '0').split(',')]
    for cft in tilts:
        for cfa in range(0, 360, 15):
            n = np.array([np.cos(np.deg2rad(cfa)), np.sin(np.deg2rad(cfa))])
            for back in (1.0, -1.0):
                for dz in (-2.0, 0.0, 2.0):
                    c = P[:2] - n * mk[1] * back + np.asarray(cam.T, float) * dz
                    v = (float(c[0]), float(c[1]), float(cfa), cft)
                    sc = score(v)
                    if best is None or sc > best[0]:
                        best = (sc, v)
    print('grid best', best)
    # local refine
    sc, v = best
    step = np.array([0.5, 0.5, 7.5, 10.0 if len(tilts) > 1 else 0.0])
    for it in range(40):
        improved = False
        for i in range(4):
            if step[i] == 0.0:
                continue
            for d in (-1.0, 1.0):
                w = np.array(v, float); w[i] += d * step[i]
                s2 = score(tuple(w))
                if s2 > sc:
                    sc, v, improved = s2, tuple(float(t) for t in w), True
        if not improved:
            step = step * 0.5
            if step[0] < 0.06:
                break
    print('refined', round(sc, 3), [round(t, 2) for t in v])
    out = dict(cfx=v[0], cfy=v[1], cfa=v[2], cft=v[3], f1=sc, cfix={str(k): (1.0 if on[k] else 0.0) for k in frames},
               cross={str(k): xy[k] for k in frames})
    json.dump(out, open('%s_%s_case.json' % (unit, seq), 'w'), default=float)
    print('wrote', '%s_%s_case.json' % (unit, seq))


if __name__ == '__main__':
    main()
