"""
deathshadow.py - a dying soldier's shadow as TS's frames have it: it shrinks as he falls and is all but gone once he
lies on the ground (Luke: "on the og's the shadow disappears as the unit falls. On ours they still look like they're
floating in midair because of their shadows").

How much shadow TS shows round each death frame (tsshadow.ts_shadow: on the ground TS's soldier leaves showing) sets how
much the HD frame shows round ours, in proportion to the standing frames (TS's standing shadow against ours, the median
over the 8 facings).  The HD frame gets there by raising the shadow's light (a shorter shadow, drawn in under him, as a
body's shadow is once it lies on the ground); it fades the shadow only where even a light straight overhead leaves more
of it showing than TS does.

    python3 deathshadow.py UNIT [SEQ,SEQ]   writes UNIT_shadow_w.json {frame: [shadow length, strength]} (default seqs:
                                            death1,death2; infall.py draws those frames with them)
"""
import json, os, sys
import numpy as np
from scipy import ndimage
import rcrender as RR
import inf as I
import infall as A
import infrender as R
import infseq as SQ
import tsshadow as T

LENS = [1.0, 0.85, 0.7, 0.55, 0.4, 0.25, 0.1, 0.0]       # (x infrender.SHADOW_LEN)


# (TS's frames' dark rim round the soldier is their outline (the sprite scaled up), not shadow: TS's shadow counts from
# a pixel clear of him; every pixel of ours counts - a band of it along a lying soldier is what reads as a gap under
# him)
RING_TS = 1          # TS px
RING_HD = 0          # HD canvas px


def ts_area(unit, k):
    import inffit as F
    body = F.ts_frame(unit, k)[..., 3] > 0
    ring = ndimage.binary_dilation(body, structure=np.ones((3, 3), bool), iterations=RING_TS)
    return float((T.ts_shadow(unit, k) & ~ring).sum())


def hd_area(unit, S, js, Q, f, lens=LENS):
    """the HD frame's cast shadow showing round him (canvas px), for each shadow length (x SHADOW_LEN)."""
    parts, dz = I.grounded(S, Q, I.facing_angle(f))
    cam = R.camera((js['ax'], js['y0']))
    win = R.find_window(parts, cam)
    r = RR.RCRender(parts, cam, R.CANVAS, win, R.BOUNDS, ss=1, shadow_len=R.SHADOW_LEN, px_scale=R.PX_SCALE)
    Wc, Hc = R.CANVAS
    cover = np.zeros((Hc, Wc), bool)
    x0, y0, x1, y1 = r.win
    cover[y0:y1, x0:x1] = r.hitmask
    if RING_HD:
        cover = ndimage.binary_dilation(cover, structure=np.ones((3, 3), bool), iterations=RING_HD)
    SX, SY = np.meshgrid(np.arange(Wc) + 0.5, np.arange(Hc) + 0.5)
    gx, gy = cam.ground(SX, SY)
    P = np.stack([gx, gy, np.zeros_like(gx)], -1)
    base = cam.cam_to_world(RR.LS_CAM)
    out = []
    for L in lens:
        sl = R.SHADOW_LEN * L
        Ls = np.array([base[0] * sl, base[1] * sl, base[2]], float)
        sm = RR.LightMap(parts, Ls / np.linalg.norm(Ls), r.bounds, r.sm.step)
        out.append(float((sm.test(P, bias=0.05, pcf=1) * ~cover).sum()))
    return out


def choose(h, target):
    """the longest shadow (x SHADOW_LEN) that shows no more than target, and the strength left to fade it to target
    when even straight down shows more."""
    if h[0] <= target:
        return 1.0, 1.0
    for i in range(1, len(LENS)):
        if h[i] <= target:
            t = (h[i - 1] - target) / max(h[i - 1] - h[i], 1e-6)
            return LENS[i - 1] + t * (LENS[i] - LENS[i - 1]), 1.0
    return 0.0, float(np.clip(target / max(h[-1], 1e-6), 0.0, 1.0))


def falling(v):
    """the closest sequence that never rises (pool adjacent violators): once the shadow starts drawing in under him it
    doesn't come back out."""
    blocks = []
    for x in v:
        blocks.append([float(x), 1])
        while len(blocks) > 1 and blocks[-2][0] / blocks[-2][1] < blocks[-1][0] / blocks[-1][1]:
            s, c = blocks.pop(); blocks[-1][0] += s; blocks[-1][1] += c
    out = []
    for s, c in blocks:
        out += [s / c] * c
    return out


def schedule(unit, S, js, tab, seqs=('death1', 'death2'), log=print):
    """{frame: [shadow length, strength]} for the frames of seqs."""
    # standing: TS's shadow against ours, per facing
    rs = []
    for k in range(8):
        a, h = ts_area(unit, k), hd_area(unit, S, js, *tab[k], lens=[1.0])[0]
        rs.append(a / max(h, 1.0))
    r0 = float(np.median(rs))
    log('standing TS/HD ' + ' '.join('%.3f' % v for v in rs) + ' median %.3f' % r0)
    out = {}
    for seq in seqs:
        ks = [k for k, fc in SQ.frames_of(unit, seq) if k in tab]
        if not ks:
            continue
        ta = np.array([ts_area(unit, k) for k in ks])
        # (TS's frames jitter by a few pixels: a 3-frame median)
        tm = np.array([np.median(ta[max(i - 1, 0):i + 2]) for i in range(len(ta))])
        rows = []
        for k, a, am in zip(ks, ta, tm):
            h = hd_area(unit, S, js, *tab[k])
            L, s = choose(h, am / r0)
            rows.append((k, L, s))
            log('%s %d TS %.0f (%.0f) target %.0f HD %s -> length %.2f strength %.2f' % (
                seq, k, a, am, am / r0, ' '.join('%.0f' % v for v in h), L, s))
        # (smooth: never longer again once it shortens, and starting to shorten a frame ahead of a sudden drop)
        Ls = falling([L for k, L, s in rows])
        Ls = [min(Ls[i], float(np.mean(Ls[max(i - 1, 0):i + 2]))) for i in range(len(Ls))]
        ss_ = falling([s for k, L, s in rows])
        for (k, L0, s0), L, s in zip(rows, Ls, ss_):
            out[str(k)] = [round(L * R.SHADOW_LEN, 4), round(s, 3)]
        log(seq + ' lengths ' + ' '.join('%.2f' % v for v in Ls))
        log(seq + ' strengths ' + ' '.join('%.2f' % v for v in ss_))
    return out


def main():
    unit = sys.argv[1]
    seqs = sys.argv[2].split(',') if len(sys.argv) > 2 else ['death1', 'death2']
    import infunit; infunit.use(unit)
    js = json.load(open('%s_shape.json' % unit))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    tab = A.pose_table(unit, dict(js['Q']))
    path = '%s_shadow_w.json' % unit
    out = json.load(open(path)) if os.path.exists(path) else {}
    out.update(schedule(unit, S, js, tab, seqs, log=lambda m: print(m, flush=True)))
    json.dump(out, open(path, 'w'), indent=1)
    print('done', flush=True)


if __name__ == '__main__':
    main()
