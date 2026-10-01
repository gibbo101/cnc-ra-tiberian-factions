import numpy as np
from PIL import Image, ImageDraw
import legfit as LF

def compare(views, parts, name, z=6):
    r = views.render(parts, ss=2)
    tiles = []
    for k, ((m, who), t) in enumerate(zip(r, views.masks)):
        h, w = t.shape
        img = np.zeros((h, w, 3), np.uint8); img[...] = (25, 25, 35)
        img[t & ~m] = (220, 60, 60)        # TS only (missing in model): red
        img[m & ~t] = (60, 120, 230)       # model only (extra): blue
        img[m & t] = (200, 200, 200)
        im = Image.fromarray(img).resize((w * z, h * z), Image.NEAREST)
        ImageDraw.Draw(im).text((3, 3), 'CW%d' % k, fill=(255, 255, 0))
        tiles.append(im)
    W, H = tiles[0].size
    out = Image.new('RGB', (4 * (W + 4), 2 * (H + 4)), (0, 0, 0))
    for i, t in enumerate(tiles):
        out.paste(t, ((i % 4) * (W + 4), (i // 4) * (H + 4)))
    out.save(name)
    return out
