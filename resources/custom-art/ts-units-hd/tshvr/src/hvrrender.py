"""the Hover MLRS's HD frames (TSHVR: 192 x 192, 4 canvas px per classic pixel; 0-31 the hull, no shadow; 32-63 the rack,
no shadow; 64-95 the hull's shadow on its own; 32 facings counter-clockwise from north), built straight from TS's
HVR.VXL and HVRTUR.VXL posed by their HVAs (vxlunit / voxrender); the RA-grid camera (32 degrees), 2.95 canvas px per
voxel, the hull's position at canvas (95.5, 106) as in-mod/ has it.  Each rack frame is placed so its content is
centred where in-mod/'s is (the mod's seat tables cancel today's per-frame drift); each shadow frame is the HD hull's
silhouette, shifted as in-mod/'s shadow is (5 px right, 17 px down: it hovers), black at alpha 191, softened.

    python3 hvrrender.py frames 0,24,56,88 [ss] [outdir] [sky]
"""
import os, sys, time
from paths import HANDOFF
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from scipy import ndimage
import vxl, vxlunit as VU, voxrender as VR, rcrender as RR
from frameio import save

D = HANDOFF + '/07-TSHVR/ts-original/'
INMOD = HANDOFF + '/07-TSHVR/in-mod/tshvr/frames/tshvr-%04d.png'
CANVAS = (192, 192)
PPU = 2.95
ORIGIN = (95.5, 106.0)
ELEV = 32.0
BOUNDS = ((-30, 30), (-30, 30), (-1, 30))
PX_SCALE = 0.75                 # the game draws this canvas at 4/3 (4 canvas px per classic pixel against 5.33)
SHADOW_SHIFT = (5, 17)          # in-mod/'s shadow frames: the hull's silhouette, 5 px right and 17 px down
SHADOW_ALPHA = 191
TSN = float(os.environ.get('TSN', '0.6'))


# the rack's lowest voxel layers are its base ring, which sits down in the hull's turret ring: the mod's rack frames
# leave it off (drawn over the hull it would cover the deck), so they are left off here too
RING_LAYERS = 5


def load_file(name, pal, drop_below=0):
    secs = vxl.read_vxl(D + name + '.VXL'); names, mats = vxl.read_hva(D + name + '.HVA')
    for s in secs:
        if drop_below:
            s['col'][:, :, :drop_below] = -1
    return VR.Unit([VU.Section(s, pal, sigma=0.3, denoise=0.3) for s in secs], [(mats, i) for i in range(len(secs))])


def load():
    pal = vxl.read_pal(D + 'UNITTEM.PAL')
    return load_file('HVR', pal), load_file('HVRTUR', pal, RING_LAYERS)


def camera(origin=ORIGIN):
    return RR.Cam((0, -1), ELEV, PPU, origin)


def bbox_centre(a, thr=128):
    ys, xs = np.nonzero(a > thr)
    return (xs.min() + xs.max() + 1) / 2.0, (ys.min() + ys.max() + 1) / 2.0


def render(unit, f, origin, ss, sky):
    return VR.frame(unit, f, 0, camera(origin), CANVAS, BOUNDS, ss=ss, sky=sky, px_scale=PX_SCALE, speckle=(0.75, 1.2),
                    ts_normals=TSN, grime_z=0.0, with_shadow=False, sharp={i: 2.0 for i in range(len(unit.sections))})


def rack_origin(T, f):
    """where the rack frame f's origin goes so its content is centred where in-mod/'s is."""
    img0, _ = render(T, f, ORIGIN, 1, False)
    cx0, cy0 = bbox_centre(np.array(img0)[..., 3], 250)
    tgt = bbox_centre(np.array(Image.open(INMOD % (32 + f)).convert('RGBA'))[..., 3], 250)
    return (ORIGIN[0] + tgt[0] - cx0, ORIGIN[1] + tgt[1] - cy0)


def frame(units, k, ss=4, sky=True):
    H, T = units
    if k < 32:
        return render(H, k, ORIGIN, ss, sky)
    if k < 64:
        # the rack: centred where in-mod/'s rack frame has its content
        f = k - 32
        img0, _ = render(T, f, ORIGIN, 1, False)
        cx0, cy0 = bbox_centre(np.array(img0)[..., 3], 250)
        tgt = bbox_centre(np.array(Image.open(INMOD % k).convert('RGBA'))[..., 3], 250)
        o = (ORIGIN[0] + tgt[0] - cx0, ORIGIN[1] + tgt[1] - cy0)
        img, trim = render(T, f, o, ss, sky)
        t = np.array(trim); t[np.array(img)[..., 3] < 128] = 0
        return img, Image.fromarray(t, 'L')
    # the hull's shadow on its own: its HD silhouette, shifted as in-mod/'s, black, softened
    img, _ = render(H, k - 64, ORIGIN, ss, False)
    a = np.array(img)[..., 3].astype(np.float32) / 255.0
    sh = np.zeros_like(a)
    dx, dy = SHADOW_SHIFT
    sh[dy:, dx:] = a[:a.shape[0] - dy, :a.shape[1] - dx]
    sh = ndimage.gaussian_filter((sh > 0.5).astype(np.float32), 1.5 * PX_SCALE)
    out = np.zeros(a.shape + (4,), np.uint8)
    out[..., 3] = np.round(np.clip(sh, 0, 1) * SHADOW_ALPHA).astype(np.uint8)
    return Image.fromarray(out, 'RGBA'), Image.new('L', CANVAS, 0)


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
        save(img, trim, f'{out}/tshvr-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
