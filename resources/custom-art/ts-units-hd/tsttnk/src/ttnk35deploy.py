"""ttnkdeploy.py PKG - previews/dig-in-concept.gif: the Tick Tank digging in as Luke describes it (the turret runs back
over the deck and up onto the humps, the nose burrows into the ground), 16 steps at facing 20, held at both ends."""
import os, sys
import numpy as np
from PIL import Image
import hdv
import ndeliver as D


def gif(spec, pkg, facing=20, n=16, ss=3):
    u = spec.vunit()
    frames = []
    for i in range(n):
        t = i / (n - 1)
        M = __import__('ttnk35hd').dug_in(spec.CFG, u, t)
        img, _ = hdv.frame(M, spec.CFG, facing, ss=ss)
        frames.append(D.on_bg(img).crop(spec.CROP).convert('RGB'))
    seq = [frames[0]] * 6 + frames + [frames[-1]] * 10 + frames[::-1] + [frames[0]] * 4
    W, H = frames[0].size
    strip = Image.new('RGB', (W, H * len(frames)))
    for i, f in enumerate(frames):
        strip.paste(f, (0, i * H))
    pal = strip.quantize(colors=255, method=Image.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.NONE) for f in seq]
    out = os.path.join(pkg, 'previews', 'dig-in-concept.gif')
    q[0].save(out, save_all=True, append_images=q[1:], duration=90, loop=0, disposal=1)
    return out


if __name__ == '__main__':
    sys.path.insert(0, os.getcwd())
    import importlib
    print(gif(importlib.import_module('ttnk35spec'), sys.argv[1]))
