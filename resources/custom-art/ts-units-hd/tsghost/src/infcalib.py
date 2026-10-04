"""
infcalib.py - an infantry unit's HD colours read off its TS frames: for each part, the mean colour TS draws where the
fitted soldier (in TS's own camera) shows that part, against the mean colour the HD frame draws for it, over the 8
standing frames; each part's colour is scaled until the two agree (a few rounds).  TS's sprites are lit, so this keeps
each part as light or dark as TS draws it, under the HD light.

    python3 infcalib.py UNIT shape.json [rounds]      prints MAT for infunit.py
"""
import json, sys
import numpy as np
import rc
import inf as I
import inffit as F
import infrender as R


# a part's colour class and the TS classes that count as its colour (a blue-grey part's lit side reads light blue)
OK_CLASSES = {I.NAVY: (I.NAVY, I.LBLUE), I.DARK: (I.DARK,), I.GREY: (I.GREY,), I.GREEN: (I.GREEN,),
              I.ORANGE: (I.ORANGE,), I.LBLUE: (I.LBLUE,), I.YELLOW: (I.YELLOW,)}
# the helmet: its own navy only (its light blue is the visor and the glint, drawn on their own)
OK_PART = {I.HELMET: (I.NAVY,)}
NEUTRAL_ALL = bool(__import__('os').environ.get('NEUTRAL_ALL'))


def ts_means(unit, S, Q0, poses, ax, y0):
    acc = {}
    for f in range(8):
        Q = dict(Q0, **poses.get(str(f), {}))
        a = F.ts_frame(unit, f)
        parts, dz = I.grounded(S, Q, I.facing_angle(f))
        cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
        H, W = a.shape[:2]
        t, who, nrm, O = rc.render_ids(parts, cam, 0, 0, W, H, ss=3, zstart=80.0)
        comps = np.array([0] + [p.comp for p in parts])[who + 1].reshape(H, 3, W, 3).transpose(0, 2, 1, 3)
        comps = comps.reshape(H, W, 9)
        cls = F.ts_classes(a)
        ok = (a[..., 3] > 0) & (cls != F.FX)
        # TS's outline pixels are dark whatever the part: only pixels well inside the sprite count
        inner = ok.copy()
        inner[1:, :] &= ok[:-1, :]; inner[:-1, :] &= ok[1:, :]; inner[:, 1:] &= ok[:, :-1]; inner[:, :-1] &= ok[:, 1:]
        for c in set(int(v) for v in np.unique(comps)) - {0}:
            # only TS's pixels of the part's own colour class (a part a pixel off would mix in its neighbour's colour)
            k = I.CLASS.get(c, 0)
            # (the helmet's own navy only where it is navy: the Medic's cap is grey)
            ok_cls = OK_PART[c] if (c in OK_PART and k == I.NAVY) else OK_CLASSES.get(k, (k,))
            if NEUTRAL_ALL and k in (I.GREY, I.DARK):
                # (NEUTRAL_ALL: a grey or dark part against all TS's neutral pixels on it, its shaded ones too - the
                # Medic's armour runs across TS's grey and dark classes, and either alone leaves it too light or dark)
                ok_cls = (I.GREY, I.DARK)
            same = np.isin(cls, list(ok_cls))
            m = inner & ((comps == c).sum(-1) >= 7) & same
            if m.any():
                s, n = acc.get(c, (np.zeros(3), 0))
                acc[c] = (s + a[m][:, :3].sum(0), n + int(m.sum()))
    return {c: s / n for c, (s, n) in acc.items() if n >= 3}


def hd_means(S, Q0, poses, ground):
    acc = {}
    for f in range(8):
        Q = dict(Q0, **poses.get(str(f), {}))
        parts, dz = I.grounded(S, Q, I.facing_angle(f))
        img, trim = R.render(parts, ss=2, ground=ground)
        a = np.asarray(img).astype(float)
        cam = R.camera(ground)
        W, H = R.CANVAS
        xs = np.arange(W) + 0.5; ys = np.arange(H) + 0.5
        SX, SY = np.meshgrid(xs, ys)
        O = cam.rays(SX.ravel(), SY.ravel(), zstart=80.0)
        t, who, _ = rc.cast(parts, O, cam.D, want_normals=False)
        comps = np.array([0] + [p.comp for p in parts])[who + 1].reshape(H, W)
        for c in set(int(v) for v in np.unique(comps)) - {0}:
            m = (comps == c) & (a[..., 3] > 250)
            if m.sum() > 4:
                s, n = acc.get(c, (np.zeros(3), 0))
                acc[c] = (s + a[m][:, :3].sum(0), n + int(m.sum()))
    return {c: s / n for c, (s, n) in acc.items()}


NAMES = {v: k for k, v in vars(I).items() if isinstance(v, int) and 700 <= v < 800}


def main():
    unit, shape = sys.argv[1:3]
    rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    import infunit; infunit.use(unit)
    js = json.load(open(shape))
    S = dict(F.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    try:
        poses = {k: v['Q'] for k, v in json.load(open('%s_stand_frames.json' % unit)).items()}
    except FileNotFoundError:
        poses = {}
    ts = ts_means(unit, S, js['Q'], poses, js['ax'], js['y0'])
    for r in range(rounds):
        hd = hd_means(S, js['Q'], poses, (js['ax'], js['y0']))
        for c, v in ts.items():
            if c in hd and c in R.MAT and c not in R.HOUSE:
                # TS's hue, at the brightness that makes the HD part as light as TS's on average
                lum = lambda x: float(np.dot(x, (0.299, 0.587, 0.114)))
                target = lum(R.MAT[c]) * np.clip(lum(v) / max(lum(hd[c]), 1.0), 0.4, 2.5)
                col = np.asarray(v, float) / max(lum(v), 1.0) * target
                if col.max() > 255:
                    col = col * 255.0 / col.max()
                R.MAT[c] = tuple(int(round(x)) for x in np.clip(col, 0, 255))
        print('round', r, {NAMES.get(c, c): (tuple(int(x) for x in ts[c]), tuple(int(x) for x in hd.get(c, (0, 0, 0))))
                            for c in ts}, flush=True)
    print('MAT = {%s}' % ', '.join('I.%s: %s' % (NAMES.get(c, c), R.MAT[c]) for c in sorted(R.MAT)))


if __name__ == '__main__':
    main()


# ---------------------------------------------------------------------------------------------- the ramps' light
def ramp_samples(unit, S, js, table, frames):
    """per ramp part: the HD shading ratio of its samples over the given frames ({frame: (Q, facing)}), and TS's
    mean luminance of the part over the same frames."""
    rec = {c: [] for c in R.RAMP}

    def capture(r, col, mat):
        for c in rec:
            m = (r.comp == c) & r.hitmask
            if m.any() and c in mat:
                rec[c].append(R.lum(col[m]) / float(R.lum(mat[c])))
        return col
    keep = R.apply_ramps
    R.apply_ramps = capture
    ts = {}
    try:
        for k in frames:
            Q, f = table[k]
            parts, dz = I.grounded(S, Q, I.facing_angle(f))
            R.render(parts, ss=2, ground=(js['ax'], js['y0']))
            a = F.ts_frame(unit, k)
            cam = rc.Cam((0, -1), 30.0, 1.0, (js['ax'], js['y0']))
            H, W = a.shape[:2]
            t, who, nrm, O = rc.render_ids(parts, cam, 0, 0, W, H, ss=3, zstart=80.0)
            comps = np.array([0] + [p.comp for p in parts])[who + 1].reshape(H, 3, W, 3).transpose(0, 2, 1, 3)
            comps = comps.reshape(H, W, 9)
            cls = F.ts_classes(a)
            for c in rec:
                m = ((comps == c).sum(-1) >= 5) & (cls == I.CLASS.get(c, 0))
                if m.any():
                    s, n = ts.get(c, (0.0, 0))
                    ts[c] = (s + float(R.lum(a[m][:, :3]).sum()), n + int(m.sum()))
    finally:
        R.apply_ramps = keep
    return ({c: np.concatenate(v) for c, v in rec.items() if v},
            {c: s / n for c, (s, n) in ts.items() if n})


def ramp_fit(unit, shape, sets):
    """G and gamma for each ramp part so that its mean luminance matches TS's in every set of frames (e.g. standing,
    lying): sets = [(name, table, frames)].  Prints and returns {comp: (G, gamma)}."""
    js = json.load(open(shape))
    S = dict(F.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    data = [(name,) + ramp_samples(unit, S, js, table, frames) for name, table, frames in sets]
    out = {}
    for c, (ramp, G0) in [(c, v[:2]) for c, v in R.RAMP.items()]:
        best = None
        for gamma in np.linspace(0.3, 1.0, 15):
            for G in np.linspace(80, 420, 69):
                err = 0.0
                for name, hd, ts in data:
                    if c in hd and c in ts:
                        v = float(np.mean(R.lum(R.ramp_colour(ramp, G * np.clip(hd[c], 0, None) ** gamma))))
                        err += (v - ts[c]) ** 2
                if best is None or err < best[0]:
                    best = (err, G, gamma)
        out[c] = (best[1], best[2])
        print(NAMES.get(c, c), 'G %.0f gamma %.2f' % (best[1], best[2]), 'rms %.1f' % np.sqrt(best[0] / len(data)),
              {name: (round(float(np.mean(R.lum(R.ramp_colour(ramp, best[1] * np.clip(hd[c], 0, None) ** best[2])))), 1),
                      round(ts.get(c, -1), 1)) for name, hd, ts in data if c in hd})
    return out
