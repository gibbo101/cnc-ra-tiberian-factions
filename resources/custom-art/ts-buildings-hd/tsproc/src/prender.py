"""Render the Power Plant in both views.
  iso: TS's own camera at the scale and place the building has in the mod now (tspowr-0000.png: TS's frame
       x3.36, TS px (48, 72) - the ground centre - at canvas (131.3, 188.4)), canvas 256x256
  ra:  the RA grid camera (32 degrees, looking north), the foundation's south edge on the plot's south edge,
       the plot centred in the canvas"""
import sys, time
import numpy as np
from PIL import Image
import hd, powr as PW, pmat as PM, pdamage as PD

BOUNDS = ((-170, 170), (-170, 170), 200)
ZMAX = 190.0
PLOT = (256, 256)
ISO_K = 3.36                                   # the mod's scale of TS's sprite
ISO_O = (48 * ISO_K - 30.0, 72 * ISO_K - 53.5)


def iso_view(ss=hd.SS):
    return hd.ts_view(PLOT, ISO_O, ISO_K * hd.TS_PPU, ss=ss)


def ra_view(head=8, ss=hd.SS):
    """canvas grown by `head` px top and bottom; the plot at y head .. head+256."""
    H = PLOT[1] + 2 * head
    oy = head + PLOT[1] - np.sin(np.deg2rad(32.0)) * 128.0
    return hd.ra_view((PLOT[0], H), (PLOT[0] / 2, oy), ss=ss)


def ra_ts_view(head=28, width=288, ss=hd.SS):
    """the RA camera (32 degrees, 1 px per unit) looking from TS's direction (north-west): the tower at the back,
    the pads left, front and right.  The front pad's foot on the plot's south edge; canvas grown to fit."""
    H = PLOT[1] + 2 * head
    front = 64 * np.sqrt(2) + PW.P['mound_r0']
    oy = head + PLOT[1] - np.sin(np.deg2rad(32.0)) * front
    return hd.View((-1, -1), 32.0, 1.0, (width, H), (width / 2, oy), margin=(64, 64), ss=ss)


def model(level=0):
    if level:
        return PD.model(level)
    return lambda X, Y, **k: PW.scene(X, Y, **k)


class Prep:
    """one geometry pass reused for material-only frames (lights, turbine turning)."""
    def __init__(self, view, level=0, **mk):
        self.view, self.level, self.mk = view, level, mk
        self.r = hd.Render(model(level), view, BOUNDS, ZMAX, **mk)
        self.occ = self.r.sky_occlusion()

    def shade(self, turb_angle=0.0, lamp=1.0, lights=None, lights_ok=None):
        """lit colour and house-colour mask per super-sampled pixel."""
        r = self.r
        alb, (bx, by, bz), emit = PM.materials(r, occ=self.occ, turb_angle=turb_angle, lamp=lamp,
                                               lights=lights, lights_ok=lights_ok)
        if self.level:
            alb = PD.mats(r, alb, self.level)
        nx, ny, nz = r.nx + bx, r.ny + by, r.nz + bz
        nl = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-9
        ao = 0.86 + 0.14 * np.clip(r.z / 40.0, 0, 1)
        col = r.shade(alb, sky_occ=self.occ, ao=ao, normals=(nx / nl, ny / nl, nz / nl)) + emit
        if lights is not None and r.flash.max() > 0:
            # the flash: a small horizontal flare round each flashing lens (only lenses you can see bloom)
            from scipy import ndimage
            ss = self.view.ss
            f = r.flash * r.hitmask
            glow = ndimage.gaussian_filter(f, (0.5 * ss, 1.7 * ss)) * 1.6
            col = col + np.clip(glow, 0, 0.9)[..., None] * np.array([150, 150, 255.])
        return col, PM.trim_mask(r, alb).astype(np.float32)

    def frame(self, turb_angle=0.0, lamp=1.0, lights=None, lights_ok=None, want_trim=False, only=None, ground=True,
              shaded=None):
        """only: keep just these (super-sampled) pixels, e.g. one part lifted onto its own canvas; ground: the
        shadow on the empty ground round the building; shaded: (colour, house mask) from shade(), possibly
        mixed from two renders of the same view."""
        col, tm = shaded if shaded is not None else self.shade(turb_angle, lamp, lights, lights_ok)
        img = self.r.compose(col, ground=ground, only=only)
        if not want_trim:
            return img
        if only is not None:
            tm = tm * only
        ss = self.view.ss
        H_, W_ = tm.shape[0] // ss, tm.shape[1] // ss
        trim = Image.fromarray((tm.reshape(H_, ss, W_, ss).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L')
        return img, trim


if __name__ == '__main__':
    ss = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    turbs = tuple(int(c) for c in sys.argv[2] if c.isdigit()) if len(sys.argv) > 2 else ()
    level = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    for name, v in (('iso', iso_view(ss)), ('ra', ra_view(8, ss))):
        t0 = time.time()
        pr = Prep(v, level=level, turbines=turbs)
        img = pr.frame()
        tag = ('-t' + ''.join(map(str, turbs)) if turbs else '') + (f'-d{level}' if level else '')
        img.save(f'/home/claude/work/scratch/p-{name}{tag}.png')
        a = np.array(img)[..., 3]
        ys, xs = np.nonzero(a > 20)
        print(name, img.size, '%.1fs' % (time.time() - t0), 'bbox x', xs.min(), xs.max(), 'y', ys.min(), ys.max())
