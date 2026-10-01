import numpy as np
from PIL import Image, ImageDraw
import torsofit as TF

CC = {0: (25, 25, 35), 1: (215, 170, 80), 2: (70, 70, 70), 6: (0, 190, 0), 7: (255, 255, 255)}

def class_img(c):
    img = np.zeros(c.shape + (3,), np.uint8)
    for k, col in CC.items():
        img[c == k] = col
    return img

def model_classes(who, comps, ss):
    H, W = who.shape
    cls = np.zeros(who.shape, int)
    for i, cp in enumerate(comps):
        cls[who == i] = TF.CLASS[cp]
    # majority per pixel
    h, w = H // ss, W // ss
    c4 = cls.reshape(h, ss, w, ss).transpose(0, 2, 1, 3).reshape(h, w, ss * ss)
    cov = (c4 > 0).mean(-1)
    out = np.zeros((h, w), int)
    for k in CC:
        if k == 0:
            continue
        cnt = (c4 == k).sum(-1)
        out = np.where((cov >= 0.5) & (cnt > np.take_along_axis(np.stack([(c4 == q).sum(-1) for q in CC], -1), np.zeros((h, w, 1), int), -1)[..., 0] * 0 - 1) & (cnt == np.max(np.stack([(c4 == q).sum(-1) for q in CC if q], -1), -1)), k, out)
    return out

def compare(views, P, ks, name, z=6, ss=3):
    r = views.render(P, ks, ss)
    tiles = []
    for k in ks:
        who, comps = r[k]
        mc = model_classes(who, comps, ss)
        tc = views.cls[k]
        both = np.concatenate([class_img(tc), np.zeros((tc.shape[0], 2, 3), np.uint8), class_img(mc)], axis=1)
        im = Image.fromarray(both); im = im.resize((im.size[0] * z, im.size[1] * z), Image.NEAREST)
        ImageDraw.Draw(im).text((3, 3), '%d' % (120 + k), fill=(255, 255, 0))
        tiles.append(im)
    W, H = tiles[0].size
    cols = 4
    out = Image.new('RGB', (cols * (W + 6), ((len(tiles) + cols - 1) // cols) * (H + 6)), (0, 0, 0))
    for i, t in enumerate(tiles):
        out.paste(t, ((i % cols) * (W + 6), (i // cols) * (H + 6)))
    out.save(name)
