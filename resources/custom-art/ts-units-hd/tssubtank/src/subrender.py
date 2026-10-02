"""the Devil's Tongue's HD frames (TSSUBTANK: 384 x 384, 113 frames): 0-31 driving with its shadow, 32 facings counter-clockwise
from north; 32-71 diving, 8 facings x 5 steps (frame = 32 + facing x 5 + step, facing 0 N, 1 NW ... 7 NE; nose pitched
down 8, 16, 24, 32, 40 degrees); 72-111 emerging (nose up 40, 32, 24, 16, 8 degrees); no shadow while diving or
emerging; 112 the disturbed-earth marker.  Built straight from TS's SUBTANK.VXL posed by its HVA (vxlunit /
voxrender); the RA-grid camera (32 degrees), 6.256 canvas px per voxel, the unit's position at canvas (192.0, 190.8) as
in-mod/ has it; the pitch turns about the unit's position on the ground, as in-mod/ does (found by matching TS's
voxels to in-mod/'s dive frames).

    python3 subrender.py frames 0,24,62,112 [ss] [outdir] [sky]
"""
import os, sys, time
from paths import HANDOFF
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import vxl, vxlunit as VU, voxrender as VR, rcrender as RR
from frameio import save

D = HANDOFF + '/09-TSSUBTANK/ts-original/'
MARKER = HANDOFF + '/09-TSSUBTANK/in-mod/tssubtank/frames/tssubtank-0112.png'
CANVAS = (384, 384)
PPU = 6.256
ORIGIN = (192.0, 190.8)
ELEV = 32.0
BOUNDS = ((-40, 40), (-40, 40), (-25, 30))
SHADOW_LEN = 1.0
TSN = float(os.environ.get('TSN', '0.6'))


def load():
    pal = vxl.read_pal(D + 'UNITTEM.PAL')
    secs = vxl.read_vxl(D + 'SUBTANK.VXL'); names, mats = vxl.read_hva(D + 'SUBTANK.HVA')
    return VR.Unit([VU.Section(s, pal, sigma=0.3, denoise=0.3) for s in secs], [(mats, i) for i in range(len(secs))])


def camera():
    return RR.Cam((0, -1), ELEV, PPU, ORIGIN)


def pitch(deg):
    """nose down by deg about the unit's position (the left axis)."""
    a = np.deg2rad(deg)
    return np.array([[np.cos(a), 0.0, np.sin(a)], [0.0, 1.0, 0.0], [-np.sin(a), 0.0, np.cos(a)]])


def layout(k):
    """frame k -> (facing of 32, nose-down degrees, with shadow)."""
    if k < 32:
        return k, 0.0, True
    if k < 72:
        f8, s = divmod(k - 32, 5)
        return f8 * 4, 8.0 * (s + 1), False
    f8, s = divmod(k - 72, 5)
    return f8 * 4, -(40.0 - 8.0 * s), False


def frame(unit, k, ss=4, sky=True):
    if k == 112:
        # the disturbed-earth marker: the mod's own drawing (already smooth), as it is
        return Image.open(MARKER).convert('RGBA'), Image.new('L', CANVAS, 0)
    f, deg, shadow = layout(k)
    unit.extra_pose = [(pitch(deg), np.zeros(3))] * len(unit.sections) if deg else None
    return VR.frame(unit, f, 0, camera(), CANVAS, BOUNDS, ss=ss, sky=sky, shadow_len=SHADOW_LEN, px_scale=1.5,
                    sharp={i: 2.0 for i in range(len(unit.sections))}, speckle=(0.75, 1.2),
                    grime_z=3.0 if not deg else 0.0, ts_normals=TSN, with_shadow=shadow)


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
        save(img, trim, f'{out}/tssubtank-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
