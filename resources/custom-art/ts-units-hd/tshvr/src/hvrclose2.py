"""hvrclose2.py - close-ups of the assembled Hover MLRS (hull f, the rack 32 + f at the game's seat) at Z times the scale.
    python3 hvrclose2.py out.png f[,f..] [zoom] [crop]"""
import sys
import numpy as np
from PIL import Image, ImageDraw
import hvrclose as C, hvrseat as HS


def assembled(f, Z=6, crop=(30, 14, 166, 150)):
    win = tuple(int(c * Z) for c in crop)
    hull = C.close(f, Z, 2, win=win)
    k, dx, dy = HS.seat(f)
    # the rack drawn over a window moved back by the seat (to the zoomed pixel), so it lands where the game puts it
    sx, sy = int(round(dx * Z)), int(round(dy * Z))
    rack = C.close(k, Z, 2, win=(win[0] - sx, win[1] - sy, win[2] - sx, win[3] - sy))
    # the rack's own background is BG: take the rack's pixels where they differ from it
    a = np.array(rack).astype(int)
    bg = np.array(C.BG)
    mask = (np.abs(a - bg).sum(-1) > 6) & (a.sum(-1) > 0)        # (a window past the canvas's edge crops black)
    h = np.array(hull)
    h[mask] = a[mask]
    return Image.fromarray(h.astype(np.uint8))


if __name__ == '__main__':
    out = sys.argv[1]
    fs = [int(a) for a in sys.argv[2].split(',')]
    Z = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    tiles = [assembled(f, Z) for f in fs]
    w, h = tiles[0].size
    S = Image.new('RGB', (2 * (w + 6) - 6, ((len(tiles) + 1) // 2) * (h + 6) - 6), (30, 30, 30))
    d = ImageDraw.Draw(S)
    for i, t in enumerate(tiles):
        S.paste(t, ((i % 2) * (w + 6), (i // 2) * (h + 6)))
        d.text(((i % 2) * (w + 6) + 6, (i // 2) * (h + 6) + 4), 'facing %d' % fs[i], font=C.FONT, fill=(240, 230, 180))
    S.save(out); print(S.size)
