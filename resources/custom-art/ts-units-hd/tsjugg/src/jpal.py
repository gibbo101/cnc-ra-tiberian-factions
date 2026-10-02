"""TS palette helpers for the Juggernaut's decoded SHP frames (UNITTEM.PAL 6-bit x4; house remap shown green)."""
import numpy as np
from PIL import Image
from paths import HANDOFF
H = HANDOFF + '/04-TSJUGG/'
PALF = H + 'ts-original/UNITTEM.PAL'
raw = np.frombuffer(open(PALF, 'rb').read()[:768], np.uint8).reshape(256, 3).astype(int)
P4 = raw * 4
SRC = {'walk': H + 'ts-original/JUGGER/frames/jugger-%03d.png', 'base': H + 'ts-original/DJUGG/frames/djugg-%03d.png',
       'cabin': H + 'ts-original/DJUGG_A/frames/djugg_a-%03d.png', 'deploy': H + 'ts-original/DJUGGMK/frames/djuggmk-%03d.png'}
INMOD = H + 'in-mod/tsjugg/frames/tsjugg-%04d.png'


def load(kind, f):
    return np.array(Image.open(SRC[kind] % f).convert('RGBA')).astype(int)


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
