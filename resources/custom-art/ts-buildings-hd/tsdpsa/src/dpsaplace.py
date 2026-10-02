"""Find where the mod puts TS's Sensor Array on its 256x416 canvas: canvas = TS px * K + O, by alpha IoU of TS's
finished build-up frame (GTDPSAMK 35 = GTDPSA 0) against the mod's TSDPSAMAKE 0018.
    python3 dpsaplace.py"""
import numpy as np
from weapplace import search

H = '/home/claude/work/ts/ts-buildings-hd-handoff/14-TSDPSA/'

if __name__ == '__main__':
    ts = H + 'ts-original/GTDPSAMK/frames/35.png'
    mod = H + 'in-mod/tsdpsamake-0018.png'
    b = search(ts, mod, np.arange(4.0, 5.0, 0.05), show=True)
    print('coarse best', b)
    b = search(ts, mod, np.arange(b[1] - 0.05, b[1] + 0.051, 0.005), show=False)
    print('fine best', b)
