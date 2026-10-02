"""the Carryall's HD frames (TSCARRY: 448 x 448, 32 facings counter-clockwise from north, no baked shadow), built
straight from TS's TRNSPORT.VXL posed by its HVA (vxlunit / voxrender); the RA-grid camera (32 degrees), 6.30 canvas px per
voxel, the voxel's origin at canvas (223.5, 222.9) as in-mod/ has it (found by matching the voxel to in-mod/).  It flies: no
shadow (the game draws it from the frame), no grime from the ground, no occlusion by the ground.

    python3 carryrender.py frames 0,12,24 [ss] [outdir] [sky]
"""
import os, sys, time
from paths import HANDOFF
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import vxl, vxlunit as VU, voxrender as VR, rcrender as RR
from frameio import save

D = HANDOFF + '/25-TSCARRY/ts-original/'
CANVAS = (448, 448)
PPU = 6.30
ORIGIN = (223.5, 222.9)
ELEV = 32.0
BOUNDS = ((-60, 60), (-60, 60), (-5, 40))
TSN = float(os.environ.get('TSN', '0.6'))


def load():
    pal = vxl.read_pal(D + 'UNITTEM.PAL')
    secs = vxl.read_vxl(D + 'TRNSPORT.VXL'); names, mats = vxl.read_hva(D + 'TRNSPORT.HVA')
    return VR.Unit([VU.Section(s, pal, sigma=0.3, denoise=0.3) for s in secs], [(mats, i) for i in range(len(secs))])


def camera():
    return RR.Cam((0, -1), ELEV, PPU, ORIGIN)


def frame(unit, k, ss=4, sky=True):
    return VR.frame(unit, k, 0, camera(), CANVAS, BOUNDS, ss=ss, sky=sky, px_scale=1.5,
                    sharp={i: 2.0 for i in range(len(unit.sections))}, speckle=(0.75, 1.2), grime_z=0,
                    ts_normals=TSN, with_shadow=False, ground_ao=False)


if __name__ == '__main__':
    ks = [int(a) for a in sys.argv[2].split(',')]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    out = sys.argv[4] if len(sys.argv) > 4 else 'out'
    sky = bool(int(sys.argv[5])) if len(sys.argv) > 5 else True
    os.makedirs(out, exist_ok=True)
    unit = load()
    for k in ks:
        t0 = time.time()
        img, trim = frame(unit, k, ss, sky)
        save(img, trim, f'{out}/tscarry-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
