"""Per-component tone check at TS's resolution: our TS-angle render brought back to TS's 144x144 frame vs GTRADR 00 +
GTRADR_A 00, mean colour per model component (where both have a solid pixel) and our/TS luminance ratio.
    python3 radrtone.py [ss 2] [render png (else renders)]"""
import sys
import numpy as np
from PIL import Image
import hd, radr as M, radrfit as F, radrrender as RR


def to_ts(img):
    """our 256x512 canvas -> TS's 144x144 frame (inverse of canvas = TS px x K + O), box filtered."""
    K, (ox, oy) = RR.ISO_K, RR.ISO_O
    W = int(round(144 * K))
    big = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    big.paste(img, (int(round(-ox)), int(round(-oy))))
    return np.array(big.resize((144, 144), Image.BOX)).astype(float)


def comp_map(dish_t=0.0, parts=None):
    S = 4
    v = F.view(S, 1)
    kw = dict(dish_t=dish_t)
    if parts:
        kw['parts'] = parts
    r = hd.Render(lambda X, Y, **k: M.scene(X, Y, **k), v, bounds=((-200, 200), (-200, 200), 370), zmax=370,
                  smooth_px=0.0, **kw)
    return np.where(r.hitmask, r.comp, 0)[S // 2::S, S // 2::S][:144, :144]


if __name__ == '__main__':
    ss = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    if len(sys.argv) > 2:
        img = Image.open(sys.argv[2]).convert('RGBA')
    else:
        pr, v = RR.prep('iso', ss)
        img = RR.on_canvas(pr.frame(), 'iso')
        img.save('/home/claude/work/scratch/radr/render/tone.png')
    o = to_ts(img)
    c = comp_map()
    ts = np.array(F.ts_frame(0, 0)).astype(float)
    names = {vv: k for k, vv in vars(M).items() if isinstance(vv, int) and k.isupper() and 0 < vv < 40}
    print(f'{"comp":8s} {"n":>5s}  {"TS mean":16s} {"ours":16s} lum ratio')
    for k in sorted(set(c.reshape(-1)) - {0}):
        m = (c == k) & (ts[..., 3] > 0) & (o[..., 3] > 200)
        if m.sum() < 5:
            continue
        a = ts[m][:, :3].mean(0); b = o[m][:, :3].mean(0)
        la = (a * [0.3, 0.59, 0.11]).sum(); lb = (b * [0.3, 0.59, 0.11]).sum()
        print(f'{names.get(k, k):8s} {m.sum():5d}  {str(np.round(a).astype(int)):16s} {str(np.round(b).astype(int)):16s} {lb / la:.2f}')
