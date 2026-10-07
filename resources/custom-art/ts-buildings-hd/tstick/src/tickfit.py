"""Fit the dug-in Tick Tank's pose to TS's own frames: the hull (no turret) pitched nose-down by th degrees about the
unit's position on the ground, moved f voxels forward and s down, cut at the ground, drawn in TS's camera at TS's own
size (1.10 px a voxel, the cell's centre at TS's (48, 36)); its silhouette against GTTICK's (silhouette overlap, IoU).
    python3 tickfit.py final            the dug-in pose against GTTICK 0
    python3 tickfit.py mk               each GTTICKMK frame (the hull and the turret on it), for the build-up's timing"""
import os, sys, glob, itertools
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(HERE, 'src'), HERE):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import tickm as K, tickrender as TR
import hdv, rc, ttnk3hd as T
import voxrender as VR

TS = os.environ.get('TS_ORIGINAL', '/home/claude/work/ts/ts-nod-buildings-hd-handoff/17-GATICK/ts-original')   # the hand-off's 17-GATICK/ts-original
PPU_TS = K.VOX_PX_BLD / TR.ISO_K
CAM = rc.Cam((-np.sqrt(0.5), -np.sqrt(0.5)), 30.0, PPU_TS, TR.TS_GROUND)
MX = VR.facing_cw(VR.mod_to_cw(K.FACING))
_HULL = None


def hull_items():
    global _HULL
    if _HULL is None:
        c = TR.cfg('iso')
        _HULL = [it for it in T.build_hull(c, K.unit()).items if not it.name.startswith(('claw', 'drum'))]
    return _HULL


def rot(th):
    a = np.radians(th)
    return np.array([[np.cos(a), 0, np.sin(a)], [0, 1.0, 0], [-np.sin(a), 0, np.cos(a)]])


def posed_parts(items, th, s, f):
    R = rot(th)
    out = []
    for it in items:
        jt = hdv.moved_item(it, R, np.array([f, 0.0, -s]))
        K.ground_cut(jt)
        out.append(jt.part.moved(MX))
    return out


def sil(parts, ss=2, W=96, H=48):
    t, who, _, _ = rc.render_ids(parts, CAM, 0, 0, W, H, ss=ss)
    hit = np.isfinite(t).astype(np.float32)
    return hit.reshape(H, ss, W, ss).mean(axis=(1, 3)) > 0.5


def ts_mask(path):
    return np.array(Image.open(path).convert('RGBA'))[..., 3] > 0


def iou(a, b):
    return (a & b).sum() / max(1, (a | b).sum())


def fit_final():
    ref = ts_mask(f'{TS}/GTTICK/frames/gttick-0000.png')
    items = hull_items()
    best = (0, None)
    for th in range(56, 91, 4):
        for s in range(0, 23, 2):
            for f in range(-12, 13, 2):
                m = sil(posed_parts(items, th, s, f), ss=1)
                v = iou(m, ref)
                if v > best[0]:
                    best = (v, (th, s, f))
    print('coarse', best, flush=True)
    th0, s0, f0 = best[1]
    for th in np.arange(th0 - 4, th0 + 4.01, 1.0):
        for s in np.arange(s0 - 2, s0 + 2.01, 0.5):
            for f in np.arange(f0 - 2, f0 + 2.01, 0.5):
                v = iou(sil(posed_parts(items, th, s, f), ss=2), ref)
                if v > best[0]:
                    best = (v, (float(th), float(s), float(f)))
    print('fine', best, flush=True)
    return best


def fit_mk(out=os.path.join(HERE, 'mkfit.txt')):
    """each GTTICKMK frame's hull pose, searched near the previous frame's (the tank only pitches further in)."""
    items = hull_items()
    fs = sorted(glob.glob(f'{TS}/GTTICKMK/frames/*.png'))
    prev = (0.0, 0.0, 0.0)
    rows = []
    for k, fp in enumerate(fs):
        ref = ts_mask(fp)
        th0, s0, f0 = prev
        best = (-1, prev)
        for th in np.arange(max(0.0, th0 - 3), min(90.0, th0 + 15.01), 1.5):
            for s in np.arange(max(-1.0, s0 - 1), s0 + 3.01, 0.5):
                for f in np.arange(f0 - 2, f0 + 2.01, 0.5):
                    v = iou(sil(posed_parts(items, th, s, f), ss=1), ref)
                    if v > best[0]:
                        best = (v, (float(th), float(s), float(f)))
        prev = best[1]
        rows.append((k,) + prev + (best[0],))
        print('%2d  th %5.1f  s %4.1f  f %4.1f  IoU %.3f' % rows[-1], flush=True)
        with open(out, 'w') as fh:
            fh.write('\n'.join('%d %.2f %.2f %.2f %.4f' % r for r in rows) + '\n')
    return rows


if __name__ == '__main__':
    if sys.argv[1] == 'final':
        fit_final()
    elif sys.argv[1] == 'mk':
        fit_mk()
