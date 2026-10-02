"""the Mobile EMP Cannon's HD frames (TSMEMP: 384 x 384, 32 facings counter-clockwise from north, with its shadow), built
straight from TS's M_EMP.VXL posed by its HVA (vxlunit / voxrender); the RA-grid camera (32 degrees), 6.26 canvas px per
voxel, the unit's position at canvas (191.0, 190.82) as in-mod/ has it (found by matching the voxel to in-mod/),
the model on the ground there.

    python3 memprender.py frames 0,12,24 [ss] [outdir] [sky]
"""
import os, sys, time
from paths import HANDOFF
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import vxl, vxlunit as VU, voxrender as VR, rcrender as RR
from frameio import save

D = HANDOFF + '/13-TSMEMP/ts-original/'
CANVAS = (384, 384)
PPU = 6.26
ORIGIN = (191.0, 190.82)
ELEV = 32.0
BOUNDS = ((-35, 35), (-35, 35), (-1, 30))
SHADOW_LEN = 1.0
TSN = float(os.environ.get('TSN', '0.6'))
# TS's voxel floats: its lowest voxel sits GZ = 4.29 voxels above its HVA origin (about 3 classic px; the hand-off's
# README allows it to sit on the ground like the other vehicles).  The model is lowered onto the ground at the unit's
# position, so the HD frames draw it LOW_PX canvas px lower than in-mod/ (its size and its x are in-mod/'s), with its
# shadow under its tracks.  To keep in-mod/'s float instead, raise the camera's origin by LOW_PX (see camera()).
GZ = 4.29
LOW_PX = GZ * PPU * np.cos(np.deg2rad(ELEV))


def load():
    pal = vxl.read_pal(D + 'UNITTEM.PAL')
    secs = vxl.read_vxl(D + 'M_EMP.VXL'); names, mats = vxl.read_hva(D + 'M_EMP.HVA')
    down = (np.eye(3), np.array([0.0, 0.0, -GZ]))
    return VR.Unit([VU.Section(s, pal, sigma=0.3, denoise=0.3) for s in secs], [(mats, i) for i in range(len(secs))],
                   extra_pose=[down] * len(secs))


def camera(keep_float=False):
    return RR.Cam((0, -1), ELEV, PPU, (ORIGIN[0], ORIGIN[1] - (LOW_PX if keep_float else 0.0)))


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
        save(img, trim, f'{out}/tsmemp-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
