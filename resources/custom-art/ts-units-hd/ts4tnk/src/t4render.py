"""the Mammoth Mk. I's HD frames (TS4TNK: 512 x 512; 0-31 the hull with its shadow, 32-63 the turret with the barrels,
no shadow, drawn at the hull's canvas centre; 32 facings counter-clockwise from north), built straight from TS's
4TNK.VXL, 4TNKTUR.VXL and 4TNKBARL.VXL posed by their HVAs (vxlunit / voxrender); the RA-grid camera (32 degrees),
6.23 canvas px per voxel, the unit's position at canvas (255.5, 254.7) as in-mod/ has it.

    python3 t4render.py frames 0,24,56 [ss] [outdir] [sky]
"""
import os, sys, time
from paths import HANDOFF
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import vxl, vxlunit as VU, voxrender as VR, rcrender as RR
from frameio import save

D = HANDOFF + '/05-TS4TNK/ts-original/'
CANVAS = (512, 512)
PPU = 6.23
ORIGIN = (255.5, 254.7)
ELEV = 32.0
BOUNDS = ((-40, 40), (-40, 40), (-1, 30))
SHADOW_LEN = 1.0
TSN = float(os.environ.get('TSN', '0.6'))


def load_file(name, pal, sigma=0.3, denoise=0.3):
    secs = vxl.read_vxl(D + name + '.VXL'); names, mats = vxl.read_hva(D + name + '.HVA')
    return [VU.Section(s, pal, sigma=sigma, denoise=denoise) for s in secs], mats


# TS's hull sits 1.24 voxels above its HVA origin (its tracks' lowest voxels): the model is lowered onto the ground
# and the camera's origin raised to match, so every pixel stays where in-mod/ has it and the shadow meets the tracks
GZ = 1.24


def load():
    pal = vxl.read_pal(D + 'UNITTEM.PAL')
    hull, mh = load_file('4TNK', pal)
    tur, mt = load_file('4TNKTUR', pal)
    bar, mb = load_file('4TNKBARL', pal)
    down = (np.eye(3), np.array([0.0, 0.0, -GZ]))
    H = VR.Unit(hull, [(mh, i) for i in range(len(hull))], extra_pose=[down] * len(hull))
    T = VR.Unit(tur + bar, [(mt, i) for i in range(len(tur))] + [(mb, i) for i in range(len(bar))],
                extra_pose=[down] * (len(tur) + len(bar)))
    return H, T


def camera():
    return RR.Cam((0, -1), ELEV, PPU, (ORIGIN[0], ORIGIN[1] - GZ * PPU * np.cos(np.deg2rad(ELEV))))


def frame(units, k, ss=4, sky=True):
    H, T = units
    if k < 32:
        return VR.frame(H, k, 0, camera(), CANVAS, BOUNDS, ss=ss, sky=sky, shadow_len=SHADOW_LEN, px_scale=1.5,
                        sharp={i: 2.0 for i in range(len(H.sections))}, speckle=(0.75, 1.2), grime_z=3.0,
                        ts_normals=TSN)
    return VR.frame(T, k - 32, 0, camera(), CANVAS, BOUNDS, ss=ss, sky=sky, shadow_len=SHADOW_LEN, px_scale=1.5,
                    sharp={i: 2.0 for i in range(len(T.sections))}, speckle=(0.75, 1.2), grime_z=0.0,
                    with_shadow=False, ts_normals=TSN)


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
        save(img, trim, f'{out}/ts4tnk-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
