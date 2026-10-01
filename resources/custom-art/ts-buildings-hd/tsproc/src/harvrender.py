"""The TS Harvester rendered for the mod: RA's camera (32 degrees above the ground, looking north), on the mod's
384x384 unit canvas with the truck's position at PIVOT (where the mod's TSHARV puts it), at the mod's size (S units
per voxel).  Frames 0-31: HARV's 32 facings; 32-63: HORV's (unloading), in the mod's order (frame 0 faces north,
counter-clockwise, 8 west, 16 south, 24 east)."""
import os, sys, time
import numpy as np
from PIL import Image
import hd, harv as HV, harvmat as HM

CANVAS = (384, 384)
PIVOT = (188.0, 214.5)
BOUNDS = ((-170, 170), (-170, 170), 130)
ZMAX = 130.0


# EA's HD units cast a short, soft shadow from a high light at about 70%: the buildings' shadow light with
# its slant cut to SHADOW_SLANT, and SHADOW_ALPHA in place of the buildings' 75%.
SHADOW_SLANT = 0.3
SHADOW_ALPHA = 0.70
LS_UNIT = np.array([hd.LS_CAM[0] * SHADOW_SLANT, hd.LS_CAM[1] * SHADOW_SLANT, hd.LS_CAM[2]])


def view(ss=hd.SS, pivot=PIVOT, size=CANVAS):
    return hd.View((0, -1), 32.0, 1.0, size, pivot, margin=(24, 24), ss=ss, shadow_light=LS_UNIT / np.linalg.norm(LS_UNIT))


class HarvPrep:
    """one geometry pass (a facing, HARV or HORV) reused for material-only variants."""
    def __init__(self, frame, unloading=False, ss=hd.SS, s=HV.S, pivot=PIVOT, pos=(0.0, 0.0), **kw):
        self.frame, self.unloading = frame, unloading
        self.view = view(ss, pivot)
        mk = dict(frame=frame, unloading=unloading, s=s, pos=pos)
        mk.update(kw)
        self.r = hd.Render(lambda X, Y, **k: HV.merge_slabs(HV.scene(X, Y, **k)), self.view, BOUNDS, ZMAX, **mk)
        self.occ = self.r.sky_occlusion()

    def shade(self):
        r = self.r
        alb, (bx, by, bz), emit = HM.materials(r, occ=self.occ)
        nx, ny, nz = r.nx + bx, r.ny + by, r.nz + bz
        nl = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-9
        ao = 0.86 + 0.14 * np.clip(r.z / 40.0, 0, 1)
        col = r.shade(alb, sky_occ=self.occ, ao=ao, normals=(nx / nl, ny / nl, nz / nl)) + emit
        return col, HM.trim_mask(r, alb).astype(np.float32)

    def frame_img(self, want_trim=True):
        col, tm = self.shade()
        keep, hd.W.SHADOW_ALPHA = hd.W.SHADOW_ALPHA, SHADOW_ALPHA
        try:
            img = self.r.compose(col, ground=True)
        finally:
            hd.W.SHADOW_ALPHA = keep
        if not want_trim:
            return img
        ss = self.view.ss
        H_, W_ = tm.shape[0] // ss, tm.shape[1] // ss
        trim = Image.fromarray((tm.reshape(H_, ss, W_, ss).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L')
        return img, trim


def mod_frame(k):
    """mod frame k (0..63) -> (facing, unloading)."""
    return k % 32, k >= 32


if __name__ == '__main__':
    ss = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    ks = [int(a) for a in sys.argv[2].split(',')] if len(sys.argv) > 2 else [0, 8, 16, 24]
    out = sys.argv[3] if len(sys.argv) > 3 else '/home/claude/work/scratch/harv'
    os.makedirs(out, exist_ok=True)
    for k in ks:
        t0 = time.time()
        f, unl = mod_frame(k)
        pr = HarvPrep(f, unl, ss)
        img, trim = pr.frame_img()
        img.save(f'{out}/h-{k:02d}.png'); trim.save(f'{out}/h-{k:02d}-trim.png')
        print(k, '%.1fs' % (time.time() - t0), flush=True)
