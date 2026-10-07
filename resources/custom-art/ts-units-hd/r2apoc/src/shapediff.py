"""shapediff.py - the model drawn flat (apocshape) with the mod's silhouette edge drawn over it in magenta, and where
the mod has pixels the model lacks in red, where the model has extra in blue.
    python3 shapediff.py out.png frames [zoom] [crop x0,y0,x1,y1]"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
import apocshape as S
import apocmodel as T
from apoccam import flat_cam, unit_to_world, frame_of

out = sys.argv[1]
ks = [int(a) for a in sys.argv[2].split(',')]
z = int(sys.argv[3]) if len(sys.argv) > 3 else 2
crop = tuple(int(v) for v in sys.argv[4].split(',')) if len(sys.argv) > 4 else (40, 60, 408, 330)
m = T.model()
tiles = []
for k in ks:
    which, facing, tur = frame_of(k)
    parts, _, _ = T.posed(m, which, unit_to_world(facing))
    fl, cov = S.flat(parts, flat_cam(tur))
    a = np.array(S.inmod(k))[..., 3] > 250
    b = Image.new('RGBA', fl.size, S.BG + (255,)); b.alpha_composite(fl)
    im = np.array(b.convert('RGB')).astype(float)
    miss = a & ~cov; extra = cov & ~a
    im[miss] = im[miss] * 0.3 + np.array([255, 40, 40]) * 0.7
    im[extra] = im[extra] * 0.4 + np.array([60, 120, 255]) * 0.6
    edge = a & ~ndimage.binary_erosion(a)
    im[edge] = (255, 0, 255)
    t = Image.fromarray(im.astype(np.uint8)).crop(crop)
    tiles.append(t.resize((t.width * z, t.height * z), Image.NEAREST))
W = sum(t.width for t in tiles); H = max(t.height for t in tiles)
S_ = Image.new('RGB', (W, H)); x = 0
for t in tiles:
    S_.paste(t, (x, 0)); x += t.width
S_.save(out)
