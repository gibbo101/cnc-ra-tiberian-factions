"""the Prism Tank's HD frames (R2PRIS: 384 x 384; 0-31 the hull with its shadow, 32-63 the turret without one;
32 facings counter-clockwise from north), built straight from Red Alert 2's SREF, SREFTUR voxels posed
by their HVAs (vxlunit / voxrender, RA2's palette and its 244 voxel normals); the RA-grid camera (32 degrees).  Placement
found by matching the voxels to in-mod/: the hull at 5.03 canvas px per voxel with the unit's position at
(191.5, 191.02); the turret at 4.9 px per voxel (in-mod/ draws it that much smaller) with its pivot at
(191.5, 185.96).

    python3 prisrender.py frames 0,24,56 [ss] [outdir] [sky]
"""
import os, sys, time
from paths import HANDOFF
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import vxl, vxlunit as VU, voxrender as VR, rcrender as RR
from frameio import save

D = HANDOFF + '/28-R2PRIS/ra2-original/'
CANVAS = (384, 384)
PPU, ORIGIN = 5.03, (191.5, 191.02)
PPU_T, ORIGIN_T = 4.9, (191.5, 185.96)
ELEV = 32.0
BOUNDS = ((-40, 40), (-40, 40), (-1, 40))
SHADOW_LEN = 1.0
TSN = float(os.environ.get('TSN', '0.6'))
GZ = -0.18                 # the hull's lowest voxels against its HVA origin: the model is moved onto the ground


def load_file(name, pal, gz=0.0):
    secs = vxl.read_vxl(D + name + '.VXL'); names, mats = vxl.read_hva(D + name + '.HVA')
    down = (np.eye(3), np.array([0.0, 0.0, -gz]))
    return [VU.Section(s, pal, sigma=0.3, denoise=0.3) for s in secs], [(mats, i) for i in range(len(secs))], [down] * len(secs)


def unit(*files):
    secs, mats, extra = [], [], []
    for s, m, e in files:
        secs += s; mats += m; extra += e
    return VR.Unit(secs, mats, extra_pose=extra)


def load():
    pal = vxl.read_pal(D + 'UNITTEM.PAL')
    H = unit(*[load_file(n, pal, GZ) for n in ['SREF']])
    T = unit(*[load_file(n, pal) for n in ['SREFTUR']])
    return H, T


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
        save(img, trim, f'{out}/r2pris-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
