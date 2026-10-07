"""The upper body facing south without the antenna (bay/tstitn-bay-0000.png, as frame 112): the Titan draws it
while deep in a TS war factory's bay, where the antenna would show over the roof.
    python3 bayrender.py OUT_DIR"""
import os, sys
import torso2 as T2
from frameio import save

_parts = T2.parts
T2.parts = lambda *a, **k: [p for p in _parts(*a, **k) if p.name != 'antenna']
import titanrender as TR

UPPER_BODY_SOUTH = 112

if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    img, trim = TR.frame(UPPER_BODY_SOUTH)
    save(img, trim, f'{out}/tstitn-bay-0000.png')
