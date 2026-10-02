"""the Amphibious APC's HD frames (TSAPC: 384 x 384; 0-31 on land with its shadow, 32-63 the water hull TS swaps in on
water, no shadow; 32 facings counter-clockwise from north), built straight from TS's APC.VXL and APCW.VXL posed by their
HVAs (vxlunit / voxrender); the RA-grid camera (32 degrees), 6.25 canvas px per voxel, the land hull's position at
canvas (191, 190.35) and the water hull's at (191.5, 158), as in-mod/ has them.

    python3 arender.py frames 0,24,56 [ss] [outdir] [sky]
"""
import os, sys, time
from paths import HANDOFF
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import vxl, vxlunit as VU, voxrender as VR, rcrender as RR
from frameio import save

D = HANDOFF + '/06-TSAPC/ts-original/'
CANVAS = (384, 384)
PPU = 6.25
ORIGIN_LAND = (191.0, 190.35)
ORIGIN_WATER = (191.5, 158.0)
ELEV = 32.0
BOUNDS = ((-30, 30), (-30, 30), (-1, 20))
SHADOW_LEN = 1.0
TSN = float(os.environ.get('TSN', '0.6'))


def load_file(name, pal, sigma=0.3, denoise=0.3):
    secs = vxl.read_vxl(D + name + '.VXL'); names, mats = vxl.read_hva(D + name + '.HVA')
    return VR.Unit([VU.Section(s, pal, sigma=sigma, denoise=denoise) for s in secs],
                   [(mats, i) for i in range(len(secs))])


def load():
    pal = vxl.read_pal(D + 'UNITTEM.PAL')
    return load_file('APC', pal), load_file('APCW', pal)


def camera(origin=ORIGIN_LAND):
    return RR.Cam((0, -1), ELEV, PPU, origin)


def frame(units, k, ss=4, sky=True):
    land, water = units
    common = dict(ss=ss, sky=sky, shadow_len=SHADOW_LEN, px_scale=1.5, speckle=(0.75, 1.2), ts_normals=TSN)
    if k < 32:
        return VR.frame(land, k, 0, camera(ORIGIN_LAND), CANVAS, BOUNDS, grime_z=3.0,
                        sharp={i: 2.0 for i in range(len(land.sections))}, **common)
    return VR.frame(water, k - 32, 0, camera(ORIGIN_WATER), CANVAS, BOUNDS, grime_z=0.0, with_shadow=False,
                    sharp={i: 2.0 for i in range(len(water.sections))}, **common)


if __name__ == '__main__':
    ks = [int(a) for a in sys.argv[2].split(',')]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    out = sys.argv[4] if len(sys.argv) > 4 else 'out'
    sky = bool(int(sys.argv[5])) if len(sys.argv) > 5 else True
    os.makedirs(out, exist_ok=True)
    units = load()
    for k in ks:
        t0 = time.time()
        img, trim = frame(units, k, ss, sky)
        save(img, trim, f'{out}/tsapc-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
