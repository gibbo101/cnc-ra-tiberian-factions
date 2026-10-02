"""Find where the mod puts TS's radar on its 256x512 canvas: canvas = TS px * K + O, by alpha IoU of TS's finished
build-up frame (GTRADRMK 19 = building + dish) against the mod's TSRADRMAKE 0019.
    python3 radrplace.py"""
import numpy as np
from weapplace import search

H = '/home/claude/work/ts/ts-buildings-hd-handoff/07-TSRADR/'

if __name__ == '__main__':
    ts = H + 'ts-original/GTRADRMK/frames/19.png'
    mod = H + 'in-mod/tsradrmake-0019.png'
    b = search(ts, mod, np.arange(2.7, 3.4, 0.05), show=True)
    print('coarse best', b)
    b = search(ts, mod, np.arange(b[1] - 0.05, b[1] + 0.051, 0.005), show=False)
    print('fine best', b)
