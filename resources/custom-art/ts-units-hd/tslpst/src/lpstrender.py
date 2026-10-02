"""the Mobile Sensor Array's HD frames (TSLPST: 384 x 384, 32 facings counter-clockwise from north, with its shadow), built
straight from TS's LPST.VXL posed by its HVA (vxlunit / voxrender); the RA-grid camera (32 degrees), 6.24 canvas px per
voxel, the unit's position at canvas (191.5, 191.08) as in-mod/ has it (found by matching the voxel to in-mod/).

    python3 lpstrender.py frames 0,12,24 [ss] [outdir] [sky]
"""
import os, sys, time
from paths import HANDOFF
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import vxl, vxlunit as VU, voxrender as VR, rcrender as RR
from frameio import save

D = HANDOFF + '/12-TSLPST/ts-original/'
CANVAS = (384, 384)
PPU = 6.24
ORIGIN = (191.5, 191.08)
ELEV = 32.0
BOUNDS = ((-35, 35), (-35, 35), (-1, 30))
SHADOW_LEN = 1.0
TSN = float(os.environ.get('TSN', '0.6'))
# TS's voxel sits GZ voxels above its HVA origin: the model is lowered onto the ground and the camera's origin raised to
# match, so every pixel stays where in-mod/ has it and the shadow meets the wheels
GZ = 0.0


def load():
    pal = vxl.read_pal(D + 'UNITTEM.PAL')
    secs = vxl.read_vxl(D + 'LPST.VXL'); names, mats = vxl.read_hva(D + 'LPST.HVA')
    down = (np.eye(3), np.array([0.0, 0.0, -GZ]))
    return VR.Unit([VU.Section(s, pal, sigma=0.3, denoise=0.3) for s in secs], [(mats, i) for i in range(len(secs))],
                   extra_pose=[down] * len(secs))


def camera():
    return RR.Cam((0, -1), ELEV, PPU, (ORIGIN[0], ORIGIN[1] - GZ * PPU * np.cos(np.deg2rad(ELEV))))


def frame(unit, k, ss=4, sky=True):
    return VR.frame(unit, k, 0, camera(), CANVAS, BOUNDS, ss=ss, sky=sky, shadow_len=SHADOW_LEN, px_scale=1.5,
                    sharp={i: 2.0 for i in range(len(unit.sections))}, speckle=(0.75, 1.2), grime_z=3.0,
                    ts_normals=TSN)


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
        save(img, trim, f'{out}/tslpst-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
