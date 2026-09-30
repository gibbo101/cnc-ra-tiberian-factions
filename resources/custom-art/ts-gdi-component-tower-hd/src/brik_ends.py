"""End pieces for RA's own concrete wall (BRIK), cut from BRIK's HD frames so they match exactly.

Each piece is the first stretch of BRIK entering the gate's end cell, finished with BRIK's own end cap:
  W: wall comes in from the west, ends ~34 px in     E: from the east, ends ~34 px in
  N: from the north, ends ~30 px in                  S: from the south, ends ~28 px in
The cap is BRIK's end frame shifted into place; the edge that meets the neighbouring wall cell is
taken from BRIK's straight frame (so it tiles like a normal BRIK join) and blended over 10 px.
States: ok = BRIK 0-15, damaged = BRIK 16-31, destroyed = the broken-stub edge of BRIK's rubble frames.
"""
import numpy as np
from PIL import Image

REF = 'ref'
DMG = 'ref-dmg'


def load(n):
    p = f'{REF}/brik-{n:02d}.png' if n < 16 else f'{DMG}/brik-{n:02d}.png'
    return np.array(Image.open(p).convert('RGBA')).astype(float)


def shift(a, dx=0, dy=0):
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    xs0, xs1 = max(0, -dx), min(W, W - dx)
    ys0, ys1 = max(0, -dy), min(H, H - dy)
    out[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx] = a[ys0:ys1, xs0:xs1]
    return out


def blend(a, b, w):
    """premultiplied mix of RGBA arrays with weight w (1 = a)."""
    pa, pb = a.copy(), b.copy()
    pa[..., :3] *= pa[..., 3:4] / 255; pb[..., :3] *= pb[..., 3:4] / 255
    m = pa * w[..., None] + pb * (1 - w[..., None])
    al = m[..., 3:4]
    m[..., :3] = np.where(al > 0, m[..., :3] * 255 / np.maximum(al, 1e-6), 0)
    return m


def piece(side, off):
    """off: 0 ok, 16 damaged."""
    x = np.arange(128)[None, :] * np.ones((128, 1))
    y = np.arange(128)[:, None] * np.ones((1, 128))
    if side == 'W':
        cap = shift(load(off + 8), dx=-85)                 # BRIK's east end moved to ~34 px in
        edge = load(off + 10)
        w = np.clip((x - 6) / 10, 0, 1)                    # 1 -> use the cap version
        # past the cap there is nothing of the straight wall
        out = blend(cap, np.where((x < 16)[..., None], edge, 0), w)
    elif side == 'E':
        cap = shift(load(off + 2), dx=85)
        edge = load(off + 10)
        w = np.clip((121 - x) / 10, 0, 1)
        out = blend(cap, np.where((x > 111)[..., None], edge, 0), w)
    elif side == 'N':
        cap = shift(load(off + 1), dy=-75)
        edge = load(off + 5)
        w = np.clip((y - 6) / 10, 0, 1)
        out = blend(cap, np.where((y < 16)[..., None], edge, 0), w)
    else:  # S
        cap = shift(load(off + 4), dy=73)
        edge = load(off + 5)
        w = np.clip((121 - y) / 10, 0, 1)
        out = blend(cap, np.where((y > 111)[..., None], edge, 0), w)
    return out


def destroyed(side):
    """The broken stub where BRIK's rubble frames meet the next cell."""
    if side in 'WE':
        a = load_rubble(58)
        x = np.arange(128)[None, :] * np.ones((128, 1))
        keep = (x < 40) if side == 'W' else (x > 87)
    else:
        a = load_rubble(53)
        y = np.arange(128)[:, None] * np.ones((1, 128))
        keep = (y < 40) if side == 'N' else (y > 87)
    out = a.copy()
    out[..., 3] = np.where(keep, out[..., 3], 0)
    return out


def load_rubble(n):
    return np.array(Image.open(f'{DMG}/brik-{n:02d}.png').convert('RGBA')).astype(float)


if __name__ == '__main__':
    import os
    os.makedirs('gates/out2', exist_ok=True)
    for side in 'NESW':
        for st, off in (('ok', 0), ('damaged', 16)):
            Image.fromarray(np.clip(piece(side, off), 0, 255).round().astype(np.uint8), 'RGBA').save(
                f'gates/out2/end-brik-{side}-{st}.png')
        Image.fromarray(np.clip(destroyed(side), 0, 255).round().astype(np.uint8), 'RGBA').save(
            f'gates/out2/end-brik-{side}-destroyed.png')
    print('brik end pieces written')
