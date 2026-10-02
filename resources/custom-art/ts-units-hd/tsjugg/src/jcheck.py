"""
jcheck.py - checks the Juggernaut's 202 frames against the hand-off's "Keep" list and the mod's frames:
  - 202 frames, 448 x 448, each with its -trim.png (the same size, house colour only where the frame is solid)
  - one ground line: the lowest body pixel (solid and not the shadow's black) per frame, by part
  - deploy frame 184 = walk frame 45, 201 = rest frame 132
  - the shadow: its strongest alpha (at least 128) and that it stays off the canvas edge
  - silhouette overlap with the mod's frames, by part

    python3 jcheck.py PKG  -> prints a summary and writes PKG/../check.json
"""
import json, os, sys
import numpy as np
from scipy import ndimage
from PIL import Image
from paths import HANDOFF

PKG = sys.argv[1]
HD = PKG + '/frames/tsjugg-%04d.png'
INMOD = HANDOFF + '/04-TSJUGG/in-mod/tsjugg/frames/tsjugg-%04d.png'
PARTS = {'walk': range(0, 120), 'rest': range(120, 152), 'aim': range(152, 184), 'deploy': range(184, 202)}


def body_mask(a, fill=False):
    """the unit's own pixels: solid, and not the shadow (which is pure black); fill closes the holes TS's black pixels
    leave inside the mod's frames, for the silhouette overlap."""
    m = (a[..., 3] > 250) & (a[..., :3].max(-1) > 24)
    return ndimage.binary_fill_holes(m) if fill else m


def lowest_body(a):
    rows = np.nonzero(body_mask(a).any(1))[0]
    return int(rows.max()) if rows.size else -1


def main():
    bad = []
    res = {}
    for name, ks in PARTS.items():
        lows, ovs, shad, mlows, edges = [], [], [], [], []
        for k in ks:
            p = HD % k
            if not os.path.exists(p) or not os.path.exists(p[:-4] + '-trim.png'):
                bad.append((k, 'missing'))
                continue
            a = np.asarray(Image.open(p).convert('RGBA'))
            t = np.asarray(Image.open(p[:-4] + '-trim.png').convert('L'))
            if a.shape[:2] != (448, 448) or t.shape != (448, 448):
                bad.append((k, 'size'))
            if (t[a[..., 3] < 8] > 0).any():
                bad.append((k, 'trim outside the frame'))
            e = np.zeros(a.shape[:2], bool); e[0] = e[-1] = True; e[:, 0] = e[:, -1] = True
            mod = np.asarray(Image.open(INMOD % k).convert('RGBA'))
            sh = (a[..., :3].max(-1) == 0) & (a[..., 3] > 0)
            edges.append((int((e & body_mask(a)).sum()), int((e & body_mask(mod)).sum()),
                          int(a[..., 3][e & sh].max()) if (e & sh).any() else 0))
            lows.append(lowest_body(a)); mlows.append(lowest_body(mod))
            shad.append(int(a[..., 3][sh].max()) if sh.any() else 0)
            m, b = body_mask(a, True), body_mask(mod, True)
            ovs.append((m & b).sum() / max((m | b).sum(), 1))
        ed = np.array(edges)
        res[name] = dict(lowest_min=min(lows), lowest_max=max(lows), lowest_median=float(np.median(lows)),
                         mod_lowest_min=min(mlows), mod_lowest_max=max(mlows),
                         overlap=float(np.mean(ovs)), overlap_min=float(np.min(ovs)), shadow_alpha=max(shad),
                         edge_frames=int((ed[:, 0] > 0).sum()), mod_edge_frames=int((ed[:, 1] > 0).sum()),
                         edge_shadow_alpha=int(ed[:, 2].max()))
    for k, src in ((184, 45), (201, 132)):
        if not np.array_equal(np.asarray(Image.open(HD % k)), np.asarray(Image.open(HD % src))):
            bad.append((k, 'not the same as %d' % src))
    res['bad'] = bad
    res['overlap_all'] = float(np.mean([res[n]['overlap'] * len(PARTS[n]) for n in PARTS]) * len(PARTS) / 202)
    json.dump(res, open(os.path.join(os.path.dirname(PKG), 'check.json'), 'w'), indent=1)
    for n in PARTS:
        r = res[n]
        print('%-7s lowest body pixel %d-%d (median %d; mod %d-%d)  overlap %.3f (min %.3f)  shadow alpha %d  '
              'body at the edge in %d frames (mod %d), shadow at the edge up to alpha %d'
              % (n, r['lowest_min'], r['lowest_max'], r['lowest_median'], r['mod_lowest_min'], r['mod_lowest_max'],
                 r['overlap'], r['overlap_min'], r['shadow_alpha'], r['edge_frames'], r['mod_edge_frames'],
                 r['edge_shadow_alpha']))
    print('overlap, all 202: %.3f' % res['overlap_all'], '| problems', bad)


if __name__ == '__main__':
    main()
