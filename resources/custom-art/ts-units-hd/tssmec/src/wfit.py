"""
wfit.py - fitting the Wolverine (wolf.py) to TS's SMECH frames: silhouettes plus colour classes, in TS's own camera
(orthographic, 30 degrees, facings clockwise from screen-up).

    Views(frames)          TS's masks and classes for 8 facings of one pose
    loss(P, pose, cam)     the mismatch: coverage L1 / TS's area + w_cls x class disagreement
"""
import numpy as np
import rc
import wolf as WF
from wclass import classes, TAN, KHAKI, OLIVE, GREY, DARK, HOUSE, BRIGHT

WIN = (30, 14, 66, 54)          # x0, y0, x1, y1 in TS's 95 x 95 frame: round the unit


def ts_cls(f):
    """TS's classes: 1 tan, 2 olive (dark material, or tan in deep shadow), 3 dark grey, 4 light grey, 5 house."""
    c, im, a = classes(f)
    out = np.zeros(c.shape, int)
    out[(c == TAN) | (c == BRIGHT) | (c == KHAKI)] = 1
    out[c == OLIVE] = 2
    out[c == DARK] = 3
    out[c == GREY] = 4
    out[c == HOUSE] = 5
    mask = a[..., 3] > 0
    return out, mask


# agreement of a model class (rows: 1 tan, 2 dark material, 3 gun dark, 4 light metal, 5 house) with TS's (columns:
# 0 none, 1 tan, 2 olive, 3 dark grey, 4 light grey, 5 house)
AGREE = np.array([[0, 0, 0, 0, 0, 0],
                  [0, 1.0, 0.6, 0.1, 0.2, 0.0],
                  [0, 0.25, 1.0, 0.8, 0.1, 0.0],
                  [0, 0.0, 0.6, 1.0, 0.6, 0.0],
                  [0, 0.15, 0.25, 0.6, 1.0, 0.0],
                  [0, 0.0, 0.1, 0.0, 0.0, 1.0]])


def facing_of(f):
    """TS's clockwise facing (of 8) of SMECH frame f."""
    if f < 96:
        return f // 12
    if f < 104:
        return f - 96
    return (f - 104) // 4


class Views:
    def __init__(self, frames, win=WIN):
        self.frames = list(frames)
        self.facings = [facing_of(f) for f in self.frames]
        self.win = win
        x0, y0, x1, y1 = win
        self.cls, self.masks = [], []
        for f in self.frames:
            c, m = ts_cls(f)
            self.cls.append(c[y0:y1, x0:x1]); self.masks.append(m[y0:y1, x0:x1])

    def model_cls(self, parts, k, ax, y0, ss=2):
        """the model's classes for this view list's k-th frame (its own facing)."""
        x0, yw, x1, y1 = self.win; h, w = y1 - yw, x1 - x0
        cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
        M = WF.facing_matrix(self.facings[k])
        pk = [p.moved(M) for p in parts]
        t, who, nrm, O = rc.render_ids(pk, cam, x0, yw, w, h, ss=ss, zstart=200.0)
        cls_of = np.array([0] + [WF.CLASS[p.comp] for p in parts])
        cl = cls_of[who + 1]
        return cl.reshape(h, ss, w, ss).transpose(0, 2, 1, 3).reshape(h, w, ss * ss)

    def loss(self, parts, ax, y0, ks=None, ss=2, w_cls=0.5, per_view=False):
        out = []
        for k in (range(len(self.frames)) if ks is None else ks):
            cl = self.model_cls(parts, k, ax, y0, ss)
            cov = (cl > 0).mean(-1); m = self.masks[k]
            l = np.abs(cov - m).sum() / m.sum()
            tc = self.cls[k]; both = m & (cov >= 0.5) & (tc > 0)
            agree = AGREE[cl, tc[..., None]].mean(-1) / np.maximum(cov, 1e-6)
            l += w_cls * (1 - agree[both]).sum() / m.sum()
            out.append(l)
        return out if per_view else float(np.mean(out))


CLS_RGB = {0: (96, 108, 72), 1: (214, 166, 70), 2: (70, 66, 30), 3: (40, 40, 44), 4: (190, 190, 196), 5: (0, 200, 0)}


def cls_img(c):
    out = np.zeros(c.shape + (3,), np.uint8)
    for k, col in CLS_RGB.items():
        out[c == k] = col
    return out


def compare(views, parts, ax, y0, name, z=8, ss=2, label=''):
    """TS's classes beside the model's, per facing."""
    from PIL import Image, ImageDraw
    tiles = []
    for k in range(len(views.frames)):
        cl = views.model_cls(parts, k, ax, y0, ss)
        cov = (cl > 0).mean(-1)
        maj = np.zeros(cov.shape, int)
        best = np.zeros(cov.shape, int)
        for c in (1, 2, 3, 4, 5):
            cnt = (cl == c).sum(-1)
            better = (cnt > best) & (cov >= 0.5)
            maj = np.where(better, c, maj); best = np.maximum(best, np.where(cov >= 0.5, cnt, 0))
        ts = cls_img(views.cls[k]); ts[~views.masks[k]] = CLS_RGB[0]
        md = cls_img(maj)
        # outline of TS's mask over the model
        both = np.concatenate([ts, np.zeros((ts.shape[0], 1, 3), np.uint8), md], 1)
        im = Image.fromarray(both).resize((both.shape[1] * z, both.shape[0] * z), Image.NEAREST)
        d = ImageDraw.Draw(im)
        d.text((3, 3), '%s %d' % (label, views.frames[k]), fill=(255, 255, 0))
        tiles.append(im)
    W, H = tiles[0].size; cols = 4
    out = Image.new('RGB', (cols * (W + 6), ((len(tiles) + cols - 1) // cols) * (H + 6)), (10, 10, 10))
    for i, t in enumerate(tiles):
        out.paste(t, ((i % cols) * (W + 6), (i // cols) * (H + 6)))
    out.save(name)
    return name
