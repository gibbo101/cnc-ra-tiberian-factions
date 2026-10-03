"""Find where the mod puts TS's EMP Pulse Cannon on its 256x256 canvas: canvas = TS px * K + O, by alpha IoU of TS's
finished build-up frame (NAPULSMK 19) against the mod's TSPULSMAKE 0012, and of NAPULS 0 + NAPULS_A 0 against
TSPULS 0000.
    python3 pulsplace.py"""
import numpy as np
from PIL import Image
from weapplace import search

H = '/home/claude/work/ts/ts-buildings-hd-handoff/13-TSPULS/'

if __name__ == '__main__':
    ts = H + 'ts-original/NAPULSMK/frames/19.png'
    mod = H + 'in-mod/tspulsmake-0012.png'
    b = search(ts, mod, np.arange(2.0, 4.6, 0.05), show=False)
    print('coarse best', b)
    b = search(ts, mod, np.arange(b[1] - 0.05, b[1] + 0.051, 0.005), show=False)
    print('fine best (make)', b)
    base = Image.open(H + 'ts-original/NAPULS/frames/00.png').convert('RGBA')
    base.alpha_composite(Image.open(H + 'ts-original/NAPULS_A/frames/00.png').convert('RGBA'))
    base.save('/tmp/puls-ba.png')
    b2 = search('/tmp/puls-ba.png', H + 'in-mod/tspuls-0000.png', np.arange(b[1] - 0.05, b[1] + 0.051, 0.005), show=False)
    print('fine best (building + head)', b2)
