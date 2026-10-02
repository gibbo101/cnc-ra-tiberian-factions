"""silhouette disagreement per view: TS only (red), model only (blue), both (grey); with TS's colours dimmed."""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
import wolf as WF, wfit as WFT
from wpal import load


def diff_sheet(V, parts, ax, y0, name, z=10):
    tiles = []
    x0, yw, x1, y1 = V.win
    for k in range(len(V.frames)):
        cl = V.model_cls(parts, k, ax, y0, 2)
        cov = (cl > 0).mean(-1) >= 0.5
        m = V.masks[k]
        a = load(V.frames[k])[yw:y1, x0:x1, :3].astype(float)
        img = np.zeros(m.shape + (3,))
        img[:] = (40, 44, 36)
        both = m & cov
        img[both] = a[both] * 0.6 + 60
        img[m & ~cov] = (230, 40, 40)
        img[~m & cov] = (60, 110, 255)
        im = Image.fromarray(img.clip(0, 255).astype(np.uint8)).resize((m.shape[1] * z, m.shape[0] * z), Image.NEAREST)
        d = ImageDraw.Draw(im)
        for gx in range(0, im.size[0], z * 5):
            d.line([(gx, 0), (gx, im.size[1])], fill=(70, 70, 70))
        for gy in range(0, im.size[1], z * 5):
            d.line([(0, gy), (im.size[0], gy)], fill=(70, 70, 70))
        d.text((3, 3), str(V.frames[k]), fill=(255, 255, 0))
        tiles.append(im)
    W, H = tiles[0].size; cols = 4
    out = Image.new('RGB', (cols * (W + 6), ((len(tiles) + cols - 1) // cols) * (H + 6)), (0, 0, 0))
    for i, t in enumerate(tiles):
        out.paste(t, ((i % cols) * (W + 6), (i // cols) * (H + 6)))
    out.save(name)


if __name__ == '__main__':
    js = json.load(open(sys.argv[1]))
    P = dict(WF.P0); P.update(js['P'])
    frames = [int(a) for a in sys.argv[3].split(',')] if len(sys.argv) > 3 else list(range(96, 104))
    V = WFT.Views(frames)
    pose = js['pose']
    diff_sheet(V, WF.body_parts(P, pose), js['ax'], js['y0'], sys.argv[2])
