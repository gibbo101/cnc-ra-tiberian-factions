"""Find where the mod puts TS's Upgrade Center on its 384x384 canvas: canvas = TS px * K + O, by alpha IoU of TS's
finished build-up frame (GTPLUGMK 16) against the mod's TSPLUGMAKE 0018.
    python3 plugplace.py"""
import numpy as np
from weapplace import search

H = '/home/claude/work/ts/ts-buildings-hd-handoff/12-TSPLUG/'

if __name__ == '__main__':
    ts = H + 'ts-original/GTPLUGMK/frames/16.png'
    mod = H + 'in-mod/tsplugmake-0018.png'
    b = search(ts, mod, np.arange(3.0, 4.2, 0.05), show=False)
    print('coarse best', b)
    b = search(ts, mod, np.arange(b[1] - 0.05, b[1] + 0.051, 0.005), show=False)
    print('fine best', b)
