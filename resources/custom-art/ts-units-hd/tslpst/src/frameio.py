"""saving a frame with its -trim.png (from the buildings' pfinal.py)."""
import os
import numpy as np
from PIL import Image


def save(img, trim, path, alpha_from=None):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    img.save(path)
    t = np.array(trim).astype(np.float32) / 255.0
    if alpha_from is not None:
        t = t * (np.array(alpha_from)[..., 3] > 0)
    Image.fromarray((np.clip(t, 0, 1) * 255).round().astype(np.uint8), 'L').save(path[:-4] + '-trim.png')
