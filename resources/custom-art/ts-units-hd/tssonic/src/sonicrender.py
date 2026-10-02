"""the Disruptor's HD frames (TSSONIC: 448 x 448; 0-31 the hull with its shadow, 32-63 the turret (two sections) without
one, its pivot where in-mod/ has it; 32 facings counter-clockwise from north), built straight from TS's SONIC.VXL and
SONICTUR.VXL posed by their HVAs (vxlunit / voxrender); the RA-grid camera (32 degrees).  Placement found by matching
the voxels to in-mod/: the hull at 6.27 canvas px per voxel with the unit's position at (222.5, 222.7); the turret at
6.15 px per voxel (in-mod/ draws it 2% smaller) with its pivot at (224, 221).

    python3 sonicrender.py frames 0,24,56 [ss] [outdir] [sky]
"""
import os, sys, time
from paths import HANDOFF
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import vxl, vxlunit as VU, voxrender as VR, rcrender as RR
from frameio import save

D = HANDOFF + '/08-TSSONIC/ts-original/'
CANVAS = (448, 448)
PPU, ORIGIN = 6.27, (222.5, 222.7)
PPU_T, ORIGIN_T = 6.15, (224.0, 221.0)
ELEV = 32.0
BOUNDS = ((-35, 35), (-35, 35), (-1, 30))
SHADOW_LEN = 1.0
TSN = float(os.environ.get('TSN', '0.6'))
GZ = -0.24                 # TS's hull reaches a quarter voxel below its HVA origin: raised onto the ground


def load_file(name, pal, gz=0.0):
    secs = vxl.read_vxl(D + name + '.VXL'); names, mats = vxl.read_hva(D + name + '.HVA')
    down = (np.eye(3), np.array([0.0, 0.0, -gz]))
    return VR.Unit([VU.Section(s, pal, sigma=0.3, denoise=0.3) for s in secs], [(mats, i) for i in range(len(secs))],
                   extra_pose=[down] * len(secs))


def load():
    pal = vxl.read_pal(D + 'UNITTEM.PAL')
    return load_file('SONIC', pal, GZ), load_file('SONICTUR', pal)


def camera():
    return RR.Cam((0, -1), ELEV, PPU, (ORIGIN[0], ORIGIN[1] - GZ * PPU * np.cos(np.deg2rad(ELEV))))


def camera_t():
    return RR.Cam((0, -1), ELEV, PPU_T, ORIGIN_T)


def frame(units, k, ss=4, sky=True):
    H, T = units
    common = dict(ss=ss, sky=sky, shadow_len=SHADOW_LEN, px_scale=1.5, speckle=(0.75, 1.2), ts_normals=TSN)
    if k < 32:
        return VR.frame(H, k, 0, camera(), CANVAS, BOUNDS, grime_z=3.0,
                        sharp={i: 2.0 for i in range(len(H.sections))}, **common)
    return VR.frame(T, k - 32, 0, camera_t(), CANVAS, BOUNDS, grime_z=0.0, with_shadow=False,
                    sharp={i: 2.0 for i in range(len(T.sections))}, **common)


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
        save(img, trim, f'{out}/tssonic-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
