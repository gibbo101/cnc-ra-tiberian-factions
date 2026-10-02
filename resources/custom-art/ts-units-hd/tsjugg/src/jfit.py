"""
jfit.py - fitting the Juggernaut walker (jugg.py) to TS's JUGGER frames: silhouettes plus colour classes, in TS's own
camera (orthographic, 30 degrees, facings clockwise from screen-up).

    Views(frames)                 TS's masks and classes for frames of the walk (frame = facing x 15 + step)
    loss(parts_of_k, ax, y0)      the mismatch: coverage L1 / TS's area + w_cls x class disagreement
"""
import numpy as np
import rc
import jugg as JG
from jclass import classes, HOUSE, LGREY, DGREY, KHAKI, TAN, BRIGHT, OLIVE, BLUE

WIN = (18, 8, 78, 60)          # x0, y0, x1, y1 in TS's 95 x 95 frame: round the unit


def ts_cls(f, kind='walk'):
    """TS's fitting classes: 1 house, 2 light grey, 3 khaki, 4 tan (tan, bright), 5 dark (olive, dark grey, blue)."""
    c, im = classes(kind, f)
    out = np.zeros(c.shape, int)
    out[c == HOUSE] = 1
    out[c == LGREY] = 2
    out[c == KHAKI] = 3
    out[(c == TAN) | (c == BRIGHT)] = 4
    out[(c == OLIVE) | (c == DGREY) | (c == BLUE)] = 5
    return out, c > 0


# agreement of a model class (rows) with TS's (columns: 0 none, 1 house, 2 light grey, 3 khaki, 4 tan, 5 dark)
AGREE = np.array([[0, 0, 0, 0, 0, 0],
                  [0, 1.0, 0.0, 0.0, 0.0, 0.1],
                  [0, 0.0, 1.0, 0.3, 0.1, 0.4],
                  [0, 0.0, 0.3, 1.0, 0.5, 0.2],
                  [0, 0.0, 0.1, 0.5, 1.0, 0.5],
                  [0, 0.1, 0.3, 0.1, 0.4, 1.0]])


class Views:
    def __init__(self, frames, kind='walk', win=WIN):
        self.frames = list(frames)
        self.facings = [f // 15 for f in self.frames]
        self.win = win
        x0, y0, x1, y1 = win
        self.cls, self.masks = [], []
        for f in self.frames:
            c, m = ts_cls(f, kind)
            self.cls.append(c[y0:y1, x0:x1]); self.masks.append(m[y0:y1, x0:x1])

    def model_cls(self, parts, k, ax, y0, ss=2):
        x0, yw, x1, y1 = self.win; h, w = y1 - yw, x1 - x0
        cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
        M = JG.facing_matrix(self.facings[k])
        pk = [p.moved(M) for p in parts]
        t, who, nrm, O = rc.render_ids(pk, cam, x0, yw, w, h, ss=ss, zstart=200.0)
        cls_of = np.array([0] + [JG.CLASS[p.comp] for p in parts])
        cl = cls_of[who + 1]
        return cl.reshape(h, ss, w, ss).transpose(0, 2, 1, 3).reshape(h, w, ss * ss)

    def loss(self, parts_of, ax, y0, ks=None, ss=2, w_cls=0.5, per_view=False):
        """parts_of: a list of parts (one pose for every view) or a function k -> parts."""
        out = []
        for k in (range(len(self.frames)) if ks is None else ks):
            parts = parts_of(k) if callable(parts_of) else parts_of
            cl = self.model_cls(parts, k, ax, y0, ss)
            cov = (cl > 0).mean(-1); m = self.masks[k]
            l = np.abs(cov - m).sum() / m.sum()
            tc = self.cls[k]; both = m & (cov >= 0.5) & (tc > 0)
            agree = AGREE[cl, tc[..., None]].mean(-1) / np.maximum(cov, 1e-6)
            l += w_cls * (1 - agree[both]).sum() / m.sum()
            out.append(l)
        return out if per_view else float(np.mean(out))

    def iou(self, parts_of, ax, y0, ss=2):
        out = []
        for k in range(len(self.frames)):
            parts = parts_of(k) if callable(parts_of) else parts_of
            cov = (self.model_cls(parts, k, ax, y0, ss) > 0).mean(-1) >= 0.5
            m = self.masks[k]
            out.append((cov & m).sum() / max((cov | m).sum(), 1))
        return np.array(out)


CLS_RGB = {0: (96, 108, 72), 1: (0, 200, 0), 2: (200, 200, 205), 3: (230, 205, 140), 4: (190, 130, 50), 5: (45, 45, 40)}


def cls_img(c):
    out = np.zeros(c.shape + (3,), np.uint8)
    for k, col in CLS_RGB.items():
        out[c == k] = col
    return out


def compare(views, parts_of, ax, y0, name, z=7, ss=2, label=''):
    """TS's classes beside the model's, per view."""
    from PIL import Image, ImageDraw
    tiles = []
    for k in range(len(views.frames)):
        parts = parts_of(k) if callable(parts_of) else parts_of
        cl = views.model_cls(parts, k, ax, y0, ss)
        cov = (cl > 0).mean(-1)
        maj = np.zeros(cov.shape, int); best = np.zeros(cov.shape, int)
        for c in (1, 2, 3, 4, 5):
            cnt = (cl == c).sum(-1)
            better = (cnt > best) & (cov >= 0.5)
            maj = np.where(better, c, maj); best = np.maximum(best, np.where(cov >= 0.5, cnt, 0))
        ts = cls_img(views.cls[k]); ts[~views.masks[k]] = CLS_RGB[0]
        md = cls_img(maj)
        both = np.concatenate([ts, np.zeros((ts.shape[0], 1, 3), np.uint8), md], 1)
        im = Image.fromarray(both).resize((both.shape[1] * z, both.shape[0] * z), Image.NEAREST)
        d = ImageDraw.Draw(im)
        # TS's outline over the model half
        m = views.masks[k]
        edge = m & ~np.pad(m, 1)[2:, 1:-1] | m & ~np.pad(m, 1)[:-2, 1:-1] | m & ~np.pad(m, 1)[1:-1, 2:] | m & ~np.pad(m, 1)[1:-1, :-2]
        ys, xs = np.nonzero(edge)
        off = (m.shape[1] + 1) * z
        for y, x in zip(ys, xs):
            d.rectangle([off + x * z + z // 2 - 1, y * z + z // 2 - 1, off + x * z + z // 2 + 1, y * z + z // 2 + 1],
                        fill=(255, 60, 200))
        d.text((3, 3), '%s %d' % (label, views.frames[k]), fill=(255, 255, 0))
        tiles.append(im)
    W, H = tiles[0].size; cols = 4
    out = Image.new('RGB', (cols * (W + 6), ((len(tiles) + cols - 1) // cols) * (H + 6)), (10, 10, 10))
    for i, t in enumerate(tiles):
        out.paste(t, ((i % cols) * (W + 6), (i // cols) * (H + 6)))
    out.save(name)
    return name
