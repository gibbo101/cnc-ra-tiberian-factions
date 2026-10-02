"""MCV.VXL: the colour of the first voxel seen from each side (top, right = y 0, left = y max, front = x max,
back = x 0), unshaded palette colours, 16 px a voxel, labelled every 5 voxels; dimmed with depth."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
import vxl
from vdump import col, colour, X, Y, Z

K = 16


def face(view):
    f = col >= 0
    if view == 'top':      # rows y (0 at top), cols x
        idx = np.where(f.any(2), Z - 1 - np.argmax(f[:, :, ::-1], axis=2), -1)          # (x, y) -> z
        H, W = Y, X
        get = lambda r, c: (c, r, idx[c, r]); dep = lambda r, c: idx[c, r] / (Z - 1)
    elif view in ('right', 'left'):   # rows z (top = high), cols x (right: x left->right as seen from y<0 ... )
        if view == 'right':
            idx = np.where(f.any(1), np.argmax(f, axis=1), -1)                          # (x, z) -> y
            dep = lambda r, c: 1 - idx[c, Z - 1 - r] / Y
        else:
            idx = np.where(f.any(1), Y - 1 - np.argmax(f[:, ::-1], axis=1), -1)
            dep = lambda r, c: idx[c, Z - 1 - r] / Y
        H, W = Z, X
        get = lambda r, c: (c, idx[c, Z - 1 - r], Z - 1 - r)
    elif view in ('front', 'back'):  # rows z, cols y
        if view == 'front':
            idx = np.where(f.any(0), X - 1 - np.argmax(f[::-1], axis=0), -1)             # (y, z) -> x
            dep = lambda r, c: idx[c, Z - 1 - r] / X
        else:
            idx = np.where(f.any(0), np.argmax(f, axis=0), -1)
            dep = lambda r, c: 1 - idx[c, Z - 1 - r] / X
        H, W = Z, Y
        get = lambda r, c: (idx[c, Z - 1 - r], c, Z - 1 - r)
    img = np.zeros((H * K, W * K, 3)); img[:] = (30, 30, 30)
    for r in range(H):
        for c in range(W):
            x, y, z = get(r, c)
            if x < 0 or y < 0 or z < 0:
                continue
            ci = col[x, y, z]
            if ci < 0:
                continue
            img[r * K:(r + 1) * K, c * K:(c + 1) * K] = colour(np.array([ci]))[0] * (0.7 + 0.3 * dep(r, c))
    im = Image.fromarray(img.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    for c in range(0, W + 1, 5):
        d.line([(c * K, 0), (c * K, H * K)], fill=(110, 110, 120))
    for r in range(0, H + 1, 5):
        d.line([(0, r * K), (W * K, r * K)], fill=(110, 110, 120))
    pad = Image.new('RGB', (W * K + 30, H * K + 20), (20, 20, 24))
    pad.paste(im, (30, 20))
    d = ImageDraw.Draw(pad)
    for c in range(0, W, 5):
        d.text((30 + c * K + 2, 4), str(c), fill=(220, 220, 140))
    for r in range(0, H, 5):
        lab = r if view == 'top' else Z - 1 - r
        d.text((2, 20 + r * K + 2), str(lab), fill=(220, 220, 140))
    return pad


if __name__ == '__main__':
    for v in ('top', 'right', 'left', 'front', 'back'):
        face(v).save('face_%s.png' % v)
    print('ok')
