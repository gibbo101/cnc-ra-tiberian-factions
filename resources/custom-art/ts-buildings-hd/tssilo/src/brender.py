"""Generic renderer wrapper for a building (model module + materials module [+ damage module]), both views:
  iso: TS's own camera at the scale and place the building has in the mod now (TS frame x K, TS px (0, 0) at
       canvas (ox, oy)), on the mod's canvas
  ra:  the RA grid camera (32 degrees, looking north), the foundation's south edge on the plot's south edge,
       the plot centred in the canvas (grown by `head` px top and bottom)"""
import numpy as np
from PIL import Image
import hd


class Building:
    def __init__(self, model, mats, damage=None, iso_k=3.2, iso_o=(-26.0, -96.0), ts_size=96, ts_ground=(48, 72),
                 plot=(256, 256), head=0, bounds=((-200, 200), (-200, 200), 240), zmax=240.0, plot_cells=(2, 2),
                 iso_size=None):
        self.model, self.mats, self.damage = model, mats, damage
        self.iso_k, self.iso_o = iso_k, iso_o
        self.ts_ground = ts_ground
        self.plot, self.head = plot, head
        self.bounds, self.zmax = bounds, zmax
        self.plot_cells = plot_cells
        self.iso_size = iso_size or plot

    def iso_view(self, ss=hd.SS):
        K = self.iso_k
        o = (self.ts_ground[0] * K + self.iso_o[0], self.ts_ground[1] * K + self.iso_o[1])
        return hd.ts_view(self.iso_size, o, K * hd.TS_PPU, ss=ss)

    def ra_view(self, ss=hd.SS):
        W, Hp = self.plot
        H = Hp + 2 * self.head
        depth = self.plot_cells[1] * 128.0
        oy = self.head + Hp - np.sin(np.deg2rad(32.0)) * depth / 2
        return hd.ra_view((W, H), (W / 2, oy), ss=ss)

    def view(self, name, ss=hd.SS):
        return self.iso_view(ss) if name == 'iso' else self.ra_view(ss)

    def scene_fn(self, level):
        if level and self.damage is not None:
            return self.damage.model(level)
        return lambda X, Y, **k: self.model.scene(X, Y, **k)


class Prep:
    """one geometry pass reused for material-only frames."""
    def __init__(self, bld, view, level=0, **mk):
        self.b, self.view, self.level, self.mk = bld, view, level, mk
        self.r = hd.Render(bld.scene_fn(level), view, bld.bounds, bld.zmax, **mk)
        self.occ = self.r.sky_occlusion()

    def shade(self, **mat_kw):
        r = self.r
        alb, (bx, by, bz), emit = self.b.mats.materials(r, occ=self.occ, **mat_kw)
        if self.level and self.b.damage is not None:
            alb = self.b.damage.mats(r, alb, self.level)
        nx, ny, nz = r.nx + bx, r.ny + by, r.nz + bz
        nl = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-9
        ao = 0.86 + 0.14 * np.clip(r.z / 40.0, 0, 1)
        col = r.shade(alb, sky_occ=self.occ, ao=ao, normals=(nx / nl, ny / nl, nz / nl)) + emit
        glow = mat_kw.get('glow_fn')
        return col, self.b.mats.trim_mask(r, alb).astype(np.float32)

    def frame(self, want_trim=False, only=None, ground=True, shaded=None, **mat_kw):
        col, tm = shaded if shaded is not None else self.shade(**mat_kw)
        img = self.r.compose(col, ground=ground, only=only)
        if not want_trim:
            return img
        if only is not None:
            tm = tm * only
        ss = self.view.ss
        H_, W_ = tm.shape[0] // ss, tm.shape[1] // ss
        trim = Image.fromarray((tm.reshape(H_, ss, W_, ss).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L')
        return img, trim
