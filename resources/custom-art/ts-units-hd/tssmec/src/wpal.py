"""TS palette helpers for the decoded SMECH frames (6-bit palette x4; house remap shown green)."""
import numpy as np
from PIL import Image
from paths import HANDOFF
PALF = HANDOFF + '/02-TSSMEC/ts-original/UNITTEM.PAL'
raw = np.frombuffer(open(PALF, 'rb').read()[:768], np.uint8).reshape(256, 3).astype(int)
P4 = raw * 4
SRC = HANDOFF + '/02-TSSMEC/ts-original/SMECH/frames/smech-%03d.png'


def load(f):
    return np.array(Image.open(SRC % f)).astype(int)


def index_map(a):
    """palette index per pixel (-1 transparent); house-green pixels -> 1000 + green level (remap)."""
    m = a[..., 3] > 0
    out = np.full(a.shape[:2], -1, int)
    rgb = a[..., :3]
    green = m & (rgb[..., 0] == 0) & (rgb[..., 2] == 0) & (rgb[..., 1] > 0)
    d = ((rgb[..., None, :] - P4[None, None, :, :]) ** 2).sum(-1)
    idx = d.argmin(-1)
    out[m] = idx[m]
    out[green] = 1000 + rgb[..., 1][green]
    return out, d.min(-1)
