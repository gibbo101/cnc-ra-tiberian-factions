"""recompress a package's PNGs losslessly (oxipng), keeping each file's colour type and bit depth and every pixel
(checked), so the zips stay small: about 9% off the frames.

    python3 pngopt.py FOLDER [level]
"""
import io, os, sys
import numpy as np
from PIL import Image
import oxipng

KEEP = dict(bit_depth_reduction=False, color_type_reduction=False, palette_reduction=False, grayscale_reduction=False,
            optimize_alpha=False)


def optimize_folder(folder, level=2):
    before = after = 0
    for root, _, files in os.walk(folder):
        for f in sorted(files):
            if not f.endswith('.png'):
                continue
            p = os.path.join(root, f)
            d = open(p, 'rb').read()
            o = oxipng.optimize_from_memory(d, level=level, **KEEP)
            before += len(d)
            if len(o) < len(d):
                a = Image.open(io.BytesIO(d)); b = Image.open(io.BytesIO(o))
                if a.mode != b.mode or not np.array_equal(np.asarray(a), np.asarray(b)):
                    raise RuntimeError('pixels changed in ' + p)
                open(p, 'wb').write(o)
                after += len(o)
            else:
                after += len(d)
    return before, after


if __name__ == '__main__':
    b, a = optimize_folder(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 2)
    print('PNGs %.1f MB -> %.1f MB' % (b / 1e6, a / 1e6))
