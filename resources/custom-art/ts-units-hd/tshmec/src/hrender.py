"""the Mammoth Mk. II's HD frames (TSHMEC: 576 x 576, frame = facing x 8 + step, 32 facings counter-clockwise from
north, 8 walk steps = HVA frames 0,2,4,6,8,11,13,15), built straight from HMEC.VXL's 13 sections posed by HMEC.HVA
(vxlunit / voxrender), the camera 35 degrees above the ground (Luke's choice for this unit), 6.8 canvas px per voxel,
the unit's position at canvas (287.5, 374) as in-mod/ has it.

    python3 hrender.py frames 0,64,128 [ss] [outdir] [sky]
"""
import os, sys, time
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import vxl, vxlunit as VU, voxrender as VR, rcrender as RR
from frameio import save

from paths import HANDOFF
D = HANDOFF + '/03-TSHMEC/ts-original/'
CANVAS = (576, 576)
PPU = 6.8
ORIGIN = (287.5, 374.0)
ELEV = 35.0
STEPS = (0, 2, 4, 6, 8, 11, 13, 15)
BOUNDS = ((-45, 45), (-45, 45), (-1, 40))
TSN = float(os.environ.get('TSN', '0.6'))         # TS's voxel normals as shading detail
SHADOW_LEN = 0.62                      # the walkers' (Titan, Wolverine): a tall unit's shadow stays on its canvas


def load(sigma=0.3, denoise=0.3):
    secs = vxl.read_vxl(D + 'HMEC.VXL'); names, mats = vxl.read_hva(D + 'HMEC.HVA')
    pal = vxl.read_pal(D + 'UNITTEM.PAL')
    S = [VU.Section(s, pal, sigma=sigma, denoise=denoise) for s in secs]
    return VR.Unit(S, mats)


def camera():
    return RR.Cam((0, -1), ELEV, PPU, ORIGIN)


def frame(unit, k, ss=4, sky=True):
    f, step = divmod(k, 8)
    return VR.frame(unit, f, STEPS[step], camera(), CANVAS, BOUNDS, ss=ss, sky=sky, shadow_len=SHADOW_LEN,
                    px_scale=1.5, sharp={i: 2.0 for i in range(13)}, speckle=(0.75, 1.2), grime_z=4.0,
                    ts_normals=TSN)


if __name__ == '__main__':
    ks = [int(a) for a in sys.argv[2].split(',')]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    out = sys.argv[4] if len(sys.argv) > 4 else 'out'
    sky = bool(int(sys.argv[5])) if len(sys.argv) > 5 else True
    os.makedirs(out, exist_ok=True)
    unit = load()
    print('boxes', sum(len(s.boxes) for s in unit.sections), flush=True)
    for k in ks:
        t0 = time.time()
        img, trim = frame(unit, k, ss, sky)
        save(img, trim, f'{out}/tshmec-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
