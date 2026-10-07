"""Previews, README, src and zips for the TS Nod buildings (new to the mod: no in-mod frames to compare with), from a
spec module (as bdeliver.py; see handspec.py).  Differences from bdeliver:
  - no in-mod comparison; the TS-angle view is optional (the mod uses the RA grid): its build-up may be missing, and
    then the build-up previews show TS | RA grid;
  - the RA scene puts the building next to the GDI Construction Yard and Power Plant (cut from the pulse cannon's
    delivered scene preview, at 1x on the same grid), the Component Tower and a Nod wall run;
  - the house colour is compared with the yard's on the RA grid;
  - the 3D models go in a sibling folder <package>-3d, zipped on its own.
    python3 nodeliver.py <spec module> previews | readme | src | zip | all"""
import os, sys, shutil, importlib
import numpy as np
from PIL import Image, ImageDraw
import bdeliver as BD
import ypreview as P

DARK = (30, 30, 30, 255)
HAND = '/home/claude/work/ts/ts-nod-buildings-hd-handoff'
GDI_SCENE = f'{HAND}/examples/pulse-cannon/previews/pulse-cannon-with-yard-plant-tower-and-walls.png'
WALLS = '/home/claude/work/walls'
YARD_BOX = (128, 204, 512, 564)          # the yard's canvas in that scene (384 x 360 at x 128, y 256 - 52)
PLANT_BOX = (640, 248, 896, 520)         # the plant's (256 x 272 at x 640, y 256 - 8)


def nod_wall(n):
    return Image.open(f'{WALLS}/ts-nod-wall-hd/frames/nod-wall-{n:02d}.png').convert('RGBA')


def tower(state=0):
    return Image.open(f'{WALLS}/ts-gdi-component-tower-hd/tower/component-tower-{state:02d}.png').convert('RGBA')


class NodPack(BD.Pack):
    def has(self, view, sub, name):
        return os.path.exists(f"{self.s['pkg']}/{BD.V[view]}/{sub}/{name}.png")

    def ra_scene(self, level=0, t=0):
        """RA grid: the GDI Construction Yard and Power Plant (from the GDI delivery's scene, 1x), this building, the
        Component Tower, a Nod wall run in front."""
        cw, ch = self.s['cells']
        cols, rows = 13 + max(0, cw - 2), 6
        c = P.canvas(cols, rows)
        gdi = Image.open(GDI_SCENE).convert('RGBA')
        for box in (YARD_BOX, PLANT_BOX):
            c.paste(gdi.crop(box), box[:2])
        for x in range(cols):
            m = (2 if x < cols - 1 else 0) + (8 if x > 0 else 0)
            P.paste(c, nod_wall(m), x * 128, 5 * 128)
        bx, by = 8, 4 - ch
        items = [(3, tower(level), (bx + cw + 1) * 128 - 24, 2 * 128 - 96),
                 (4, self.scene('ra', level, t), bx * 128 - self.s.get('ra_left', 0), by * 128 - self.s['ra_head'])]
        for _, im, x, y in sorted(items, key=lambda it: it[0]):
            P.paste(c, im, x, y)
        d = ImageDraw.Draw(c)
        d.rectangle([bx * 128, by * 128, bx * 128 + cw * 128 - 1, by * 128 + ch * 128 - 1], outline=(255, 255, 0, 110))
        return c

    def previews(self):
        s = self.s
        out = f"{s['pkg']}/previews"
        os.makedirs(out, exist_ok=True)
        nm = s['name']
        Zp = self.Z
        iso_c = lambda im: self.crop('iso', im)
        ra_c = lambda im: self.crop('ra', im)
        # on its own (spec own_scene: with its idle overlays at frame 00, e.g. the radar's dish)
        own = (lambda v: self.scene(v, 0, 0)) if s.get('own_scene') else (lambda v: self.base(v))
        a, b = self.zoom(iso_c(own('iso')), Zp), self.zoom(ra_c(own('ra')), Zp)
        W = Image.new('RGBA', (a.width + b.width + 16, max(a.height, b.height) + 30), DARK)
        W.paste(a, (0, 30)); W.paste(b, (a.width + 16, 30))
        P.label(W, f'TS angle, {Zp:g}x', (6, 8))
        P.label(W, f"RA grid, {Zp:g}x (the {s['cells'][0]}x{s['cells'][1]} plot is x {s.get('ra_left', 0)}-"
                   f"{s.get('ra_left', 0) + s['cells'][0] * 128}, y {s['ra_head']}-{s['ra_head'] + s['cells'][1] * 128})",
                (a.width + 22, 8))
        W.save(f'{out}/{nm}-on-its-own.png')
        # states vs TS (the idle overlays at frame 0 on both)
        rows = [self.three_up([iso_c(self.ts_building(lv, 0)), iso_c(self.scene('iso', lv, 0)), ra_c(self.scene('ra', lv, 0))],
                              self.T3(), f'{("healthy", "damaged")[lv]} (frame {lv:02d}) with its idle overlays at frame 00')
                for lv in (0, 1)]
        self.stack(rows).save(f'{out}/{nm}-states-vs-original.png')
        # RA scene
        self.ra_scene(0).save(f'{out}/{nm}-with-yard-plant-tower-and-nod-wall.png')
        self.ra_scene(1).save(f'{out}/{nm}-damaged-with-yard-plant-tower-and-nod-wall.png')
        # house colour next to the yard's (RA grid)
        gdi = Image.open(GDI_SCENE).convert('RGBA')
        zg = s.get('green_zoom', 2)
        t2 = [self.zoom(gdi.crop(YARD_BOX), zg), self.zoom(ra_c(self.scene('ra', 0, 0)), zg)]
        g = Image.new('RGBA', (t2[0].width + t2[1].width + 12, max(t.height for t in t2) + 30), DARK)
        g.paste(t2[0], (0, 30)); g.paste(t2[1], (t2[0].width + 12, 30))
        P.label(g, f"House colour: the GDI Construction Yard (left) and the {s['title']} (right), RA grid, {zg:g}x", (6, 8))
        g.save(f'{out}/house-green-vs-yard.png')
        # build-up
        n = s['build_n']
        T = f"{s['hand']}/ts-original"
        ts_of = s.get('ts_of') or [int(round(i * (s['ts_mk_n'] - 1) / (n - 1))) for i in range(n)]
        mk = s.get('ts_mk', s['ts'] + 'MK')
        tsmk = lambda j: self.ts_canvas([self.ts_path(mk, j)])
        bld = lambda v, i: self.fr(v, 'build-up', f'{nm}-build-{i:02d}')
        iso_ok = all(self.has('iso', 'build-up', f'{nm}-build-{i:02d}') for i in range(n))
        pick = s.get('build_pick') or tuple(int(round(k * (n - 1) / 11)) for k in range(12))
        w = s.get('strip_w', 192)
        half = (len(pick) + 1) // 2
        nrow = 3 if iso_ok else 2
        S = Image.new('RGB', (half * (w + 4), 2 * nrow * (w + 18)), (30, 30, 30))
        d = ImageDraw.Draw(S)
        for m_, i in enumerate(pick):
            col, blk = m_ % half, m_ // half
            j = ts_of[i]
            ims = [iso_c(tsmk(j))] + ([iso_c(bld('iso', i))] if iso_ok else []) + [ra_c(bld('ra', i))]
            labs = [f'TS {j:02d}'] + ([f'HD {i:02d} TS angle'] if iso_ok else []) + [f'HD {i:02d} RA grid']
            for k, im in enumerate(ims):
                h = int(round(w * im.height / im.width))
                tile = P.on_bg(im).resize((w, h), Image.NEAREST if (k == 0 and w >= im.width) else Image.LANCZOS).convert('RGB')
                if h > w:
                    tile = tile.crop((0, (h - w) // 2, w, (h - w) // 2 + w))
                y = (blk * nrow + k) * (w + 18)
                S.paste(tile, (col * (w + 4), y + 16 + (w - tile.height) // 2))
                d.text((col * (w + 4) + 4, y + 2), labs[k], fill=(255, 255, 0))
        S.save(f'{out}/build-up-strip-vs-original.png')
        zgif = s.get('gif_zoom', Zp)
        frs = []
        for i in list(range(n)) + [n - 1] * 8:
            j = ts_of[i]
            ims = [iso_c(tsmk(j))] + ([iso_c(bld('iso', i))] if iso_ok else []) + [ra_c(bld('ra', i))]
            ttl = (f"TS {mk} {j:02d}/{s['ts_mk_n'] - 1}",) + (('HD, TS angle',) if iso_ok else ()) + ('HD, RA grid',)
            frs.append(self.n_up(ims, ttl, f'build-up {i:02d}/{n - 1}', z=zgif))
        self.gif(frs, f'{out}/build-up-vs-original.gif', 120)
        # idle loops vs TS
        ln = s['idle_n']
        for lv in (0, 1):
            frs = [self.three_up([iso_c(self.ts_building(lv, t)), iso_c(self.scene('iso', lv, t)), ra_c(self.scene('ra', lv, t))],
                                 self.T3(), f"{('healthy', 'damaged')[lv]} idle {t:02d}: {s['idle_label']}", z=zgif)
                   for t in range(ln)]
            self.gif(frs, f"{out}/idle-{('healthy', 'damaged')[lv]}-vs-original.gif", s.get('idle_ms', 110))
        for extra in s.get('extra_previews', []):
            extra(self, out)
        print('previews done')

    def ts_path(self, shp, j):
        import glob
        fs = sorted(glob.glob(f"{self.s['hand']}/ts-original/{shp}/frames/*.png"))
        return fs[j]

    def ts_building(self, level=0, t=None):
        paths = [self.ts_path(u['ts_shp'], level) for u in self.s.get('under', [])]
        paths += [self.ts_path(self.s['ts'], level)]
        if t is not None:
            for o in self.s['overlays']:
                if not o.get('idle', True):
                    continue
                j = o['ts_frame'](t, level)
                if j is not None:
                    paths.append(self.ts_path(o['ts_shp'], j))
        return self.ts_canvas(paths)

    def n_up(self, ims, titles, sub=None, z=None):
        z = self.Z if z is None else z
        W = int(round(max(i.width for i in ims) * z))
        H = int(round(max(i.height for i in ims) * z))
        S = Image.new('RGBA', (len(ims) * W + 12 * (len(ims) - 1), H + 34), DARK)
        d = ImageDraw.Draw(S)
        for k, im in enumerate(ims):
            t = self.zoom(im, z, nearest=(k == 0))
            S.paste(t, (k * (W + 12), 34 + (H - t.height) // 2))
            d.text((k * (W + 12) + 6, 4), titles[k], fill=(255, 255, 0, 255))
        if sub:
            d.text((6, 18), sub, fill=(255, 255, 255, 255))
        return S

    def T3(self):
        iw, ih = self.s['iso_size']; rw, rh = self.s['ra_size']
        return (f"TS original (x{self.s['K']:.2f})", f'HD, TS angle ({iw}x{ih})', f'HD, RA grid ({rw}x{rh})')

    def readme(self):
        open(f"{self.s['pkg']}/README.txt", 'w').write(self.s['readme']())
        if self.s.get('readme_3d'):
            os.makedirs(self.s['pkg'] + '-3d', exist_ok=True)
            open(f"{self.s['pkg']}-3d/README.txt", 'w').write(self.s['readme_3d'])

    def src(self):
        d = f"{self.s['pkg']}/src"
        os.makedirs(d, exist_ok=True)
        for f in self.s['src']:
            shutil.copy(f if os.path.isabs(f) else f'/home/claude/work/r/{f}', d)

    def zipit(self, limit=29.5 * 2 ** 20):
        import zipfile
        pkg = self.s['pkg']
        base, name = os.path.dirname(pkg), os.path.basename(pkg)
        outs = []
        for folder, zname in ((pkg, f'{name}.zip'), (pkg + '-3d', f'{name}-3d.zip')):
            if not os.path.isdir(folder):
                continue
            files = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(folder) for f in fs)
            zp = os.path.join(base, zname)
            if os.path.exists(zp):
                os.remove(zp)
            with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
                for f in files:
                    z.write(f, os.path.relpath(f, base))
            print(zname, '%.1f MiB' % (os.path.getsize(zp) / 2 ** 20))
            outs.append(zp)
        return outs


if __name__ == '__main__':
    spec = importlib.import_module(sys.argv[1]).SPEC
    what = sys.argv[2]
    pk = NodPack(spec)
    if what in ('previews', 'all'):
        pk.previews()
    if what in ('readme', 'all'):
        pk.readme()
    if what in ('src', 'all'):
        pk.src()
    if what in ('zip', 'all'):
        pk.zipit()
