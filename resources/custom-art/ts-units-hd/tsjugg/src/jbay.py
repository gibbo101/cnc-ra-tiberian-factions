"""The walk facing south without the antenna (bay/tsjugg-bay-NNNN.png, the 15 steps of frames 60-74): the
Juggernaut draws these while deep in a TS war factory's bay, where the antenna would show over the roof.
    python3 jbay.py OUT_DIR"""
import os, sys
import jugg
from frameio import save

jugg.antenna_parts = lambda P, dw=0.0: []
import jtrender as JT

SOUTH_WALK = range(60, 75)

if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    model = JT.load()
    for i, k in enumerate(SOUTH_WALK):
        img, trim = JT.frame(k, model, 4, True)
        save(img, trim, f'{out}/tsjugg-bay-{i:04d}.png')
        print('frame', k, flush=True)
