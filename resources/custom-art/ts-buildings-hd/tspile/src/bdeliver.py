"""Previews, README, src and zip for a building package (Barracks, Silo, Tech Center), from a spec:

  spec = dict(name, title, pkg, hand (hand-off folder), ts (TS SHP prefix, e.g. 'GTPILE'), K, O (in-mod placement:
              canvas = TS px x K + O), iso_size, ra_size, ra_head, cells (plot w, h), state_name ('building'),
              overlays=[dict(folder, prefix, n, ts_shp, ts_frame=lambda t, level: index or None, label)],
              loop=dict(n, map=lambda t: {prefix: overlay frame}) or None, inmod=[(file, level, loop frame)],
              build_n, ts_mk_n, src=[files], readme=text)
    python3 bdeliver.py <spec module> previews | readme | src | zip | all"""
import os, sys, shutil, importlib
import numpy as np
from PIL import Image, ImageDraw
import ypreview as P

DARK = (30, 30, 30, 255)
Z = 2
YARD = '/home/claude/work/out/ts-gdi-construction-yard-hd'
PLANT = '/home/claude/work/out/ts-gdi-power-plant-hd'
V = {'iso': 'ts-angle', 'ra': 'ra-grid'}


class Pack:
    def __init__(self, spec):
        self.s = spec

    # ------------------------------------------------------------------ frames
    def fr(self, view, sub, name):
        return Image.open(f"{self.s['pkg']}/{V[view]}/{sub}/{name}.png").convert('RGBA')

    def building(self, view, level=0):
        return self.fr(view, self.s['state_dir'], f"{self.s['name']}-{level:02d}")

    def ov(self, view, o, t, level=0):
        return self.fr(view, o['folder'], f"{self.s['name']}-{o['prefix']}-{t % o['n'] + level * o['n']:02d}")

    def scene(self, view, level=0, t=0, which=None):
        im = self.building(view, level)
        for o in self.s['overlays']:
            if which is not None and o['prefix'] not in which:
                continue
            if o.get('idle', True):
                im.alpha_composite(self.ov(view, o, t, level))
        return im

    def ts_canvas(self, paths):
        base = Image.open(paths[0]).convert('RGBA')
        for p in paths[1:]:
            base.alpha_composite(Image.open(p).convert('RGBA'))
        ts = np.array(base)
        W, H = self.s['iso_size']
        yy, xx = np.mgrid[0:H, 0:W]
        K, (ox, oy) = self.s['K'], self.s['O']
        th, tw = ts.shape[:2]
        tx = np.floor((xx + 0.5 - ox) / K).astype(int); ty = np.floor((yy + 0.5 - oy) / K).astype(int)
        ok = (tx >= 0) & (tx < tw) & (ty >= 0) & (ty < th)
        out = np.zeros((H, W, 4), np.uint8)
        out[ok] = ts[ty[ok], tx[ok]]
        return Image.fromarray(out)

    def ts_building(self, level=0, t=None):
        T = f"{self.s['hand']}/ts-original"
        paths = [f"{T}/{self.s['ts']}/frames/{level:02d}.png"]
        if t is not None:
            for o in self.s['overlays']:
                if not o.get('idle', True):
                    continue
                j = o['ts_frame'](t, level)
                if j is not None:
                    paths.append(f"{T}/{o['ts_shp']}/frames/{j:02d}.png")
        return self.ts_canvas(paths)

    # ------------------------------------------------------------------ layout
    @staticmethod
    def zoom(im, z=Z, nearest=False):
        return P.on_bg(im).resize((im.width * z, im.height * z), Image.NEAREST if nearest else Image.LANCZOS)

    def three_up(self, ims, titles, sub=None, z=Z):
        W = max(i.width for i in ims) * z
        H = max(i.height for i in ims) * z
        S = Image.new('RGBA', (3 * W + 24, H + 34), DARK)
        d = ImageDraw.Draw(S)
        for k, im in enumerate(ims):
            t = self.zoom(im, z, nearest=(k == 0))
            S.paste(t, (k * (W + 12), 34 + (H - t.height) // 2))
            d.text((k * (W + 12) + 6, 4), titles[k], fill=(255, 255, 0, 255))
        if sub:
            d.text((6, 18), sub, fill=(255, 255, 255, 255))
        return S

    @staticmethod
    def stack(ims, gap=0):
        W = max(i.width for i in ims)
        S = Image.new('RGBA', (W, sum(i.height for i in ims) + gap * (len(ims) - 1)), DARK)
        y = 0
        for i in ims:
            S.paste(i, (0, y)); y += i.height + gap
        return S

    @staticmethod
    def gif(frames, path, ms):
        q = [f.convert('RGB').quantize(colors=255, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG) for f in frames]
        q[0].save(path, save_all=True, append_images=q[1:], duration=ms, loop=0, optimize=True)

    def T3(self):
        iw, ih = self.s['iso_size']; rw, rh = self.s['ra_size']
        return (f"TS original (x{self.s['K']:.2f}, the mod's canvas)", f'HD, TS angle ({iw}x{ih})', f'HD, RA grid ({rw}x{rh})')

    # ------------------------------------------------------------------ RA scene
    def ra_scene(self, level=0, t=0):
        """RA grid: the Construction Yard, the Power Plant, this building and the Component Tower, a GDI wall run in
        front.  Walls first, then buildings from the back to the front."""
        cw, ch = self.s['cells']
        cols, rows = 13 + max(0, cw - 2), 6
        c = P.canvas(cols, rows)
        for x in range(cols):
            m = (2 if x < cols - 1 else 0) + (8 if x > 0 else 0)
            P.paste(c, P.gdi_wall(m), x * 128, 5 * 128)
        yard = Image.open(f'{YARD}/ra-grid/yard/construction-yard-{level:02d}.png').convert('RGBA')
        plant = Image.open(f'{PLANT}/ra-grid/loop/power-plant-loop-{(2 + level) * 12:02d}.png').convert('RGBA')
        bx = 8
        by = 4 - ch                                 # the building's plot sits on rows by .. 3
        items = [(3, P.tower(level), (bx + cw + 1) * 128 - 24, 2 * 128 - 96),
                 (4, yard, 1 * 128, 2 * 128 - P.YARD_HEAD),
                 (4, plant, 5 * 128, 2 * 128 - 8),
                 (4, self.scene('ra', level, t), bx * 128, by * 128 - self.s['ra_head'])]
        for _, im, x, y in sorted(items, key=lambda it: it[0]):
            P.paste(c, im, x, y)
        d = ImageDraw.Draw(c)
        d.rectangle([bx * 128, by * 128, bx * 128 + cw * 128 - 1, by * 128 + ch * 128 - 1], outline=(255, 255, 0, 110))
        return c

    # ------------------------------------------------------------------ previews
    def previews(self):
        s = self.s
        out = f"{s['pkg']}/previews"
        os.makedirs(out, exist_ok=True)
        nm = s['name']
        iw, ih = s['iso_size']; rw, rh = s['ra_size']
        # on its own
        W = Image.new('RGBA', (iw * Z + rw * Z + 16, max(ih, rh) * Z + 30), DARK)
        W.paste(self.zoom(self.building('iso')), (0, 30))
        W.paste(self.zoom(self.building('ra')), (iw * Z + 16, 30))
        P.label(W, 'TS angle, 2x', (6, 8))
        P.label(W, f"RA grid, 2x (the {s['cells'][0]}x{s['cells'][1]} plot is y {s['ra_head']}-{s['ra_head'] + s['cells'][1] * 128} of the canvas)", (iw * Z + 22, 8))
        W.save(f'{out}/{nm}-on-its-own.png')
        # states vs TS (the idle overlays at frame 0 on both)
        rows = [self.three_up([self.ts_building(lv, 0), self.scene('iso', lv, 0), self.scene('ra', lv, 0)], self.T3(),
                              f'{("healthy", "damaged")[lv]} (frame {lv:02d}) with its idle overlays at frame 00') for lv in (0, 1)]
        self.stack(rows).save(f'{out}/{nm}-states-vs-original.png')
        # the mod's frames vs ours
        rows = []
        for (fn, lv, t) in s['inmod']:
            im = Image.open(f"{s['hand']}/in-mod/{fn}").convert('RGBA')
            if s.get('loop'):
                ours = self.fr('iso', 'loop', f"{nm}-loop-{t + lv * s['loop']['n']:02d}")
                lab = f"HD, TS angle: loop/{nm}-loop-{t + lv * s['loop']['n']:02d}"
            else:
                ours = self.building('iso', lv)
                lab = f"HD, TS angle: {s['state_dir']}/{nm}-{lv:02d}"
            r = Image.new('RGBA', (iw * Z * 2 + 12, ih * Z + 28), DARK)
            r.paste(self.zoom(im, nearest=True), (0, 28)); r.paste(self.zoom(ours), (iw * Z + 12, 28))
            P.label(r, f'In the mod now: {fn} (2x)', (6, 8)); P.label(r, lab + ' (2x)', (iw * Z + 18, 8))
            rows.append(r)
        self.stack(rows).save(f'{out}/in-mod-vs-hd.png')
        # RA scene
        self.ra_scene(0).save(f'{out}/{nm}-with-yard-plant-tower-and-walls.png')
        self.ra_scene(1).save(f'{out}/{nm}-damaged-with-yard-plant-tower-and-walls.png')
        # house colour next to the yard's
        y_iso = Image.open(f'{YARD}/ts-angle/yard/construction-yard-00.png').convert('RGBA')
        y_ra = Image.open(f'{YARD}/ra-grid/yard/construction-yard-00.png').convert('RGBA')
        g = Image.new('RGBA', (768 + iw * Z + 12, 512 + 720 + 12 + 56), DARK)
        g.paste(self.zoom(y_iso), (0, 28)); g.paste(self.zoom(self.scene('iso', 0, 0)), (768 + 12, 28))
        g.paste(self.zoom(y_ra), (0, 512 + 12 + 56)); g.paste(self.zoom(self.scene('ra', 0, 0)), (768 + 12, 512 + 12 + 56))
        P.label(g, f"House colour: Construction Yard (left) and {s['title']} (right), TS angle, 2x", (6, 8))
        P.label(g, 'RA grid, 2x', (6, 512 + 12 + 36))
        g.save(f'{out}/house-green-vs-yard.png')
        # build-up
        n = s['build_n']
        T = f"{s['hand']}/ts-original"
        ts_i = lambda i: int(round(i * (s['ts_mk_n'] - 1) / (n - 1)))
        tsmk = lambda j: self.ts_canvas([f"{T}/{s['ts']}MK/frames/{j:02d}.png"])
        bld = lambda v, i: self.fr(v, 'build-up', f'{nm}-build-{i:02d}')
        pick = s.get('build_pick') or tuple(int(round(k * (n - 1) / 11)) for k in range(12))
        w = 192
        half = (len(pick) + 1) // 2
        S = Image.new('RGB', (half * (w + 4), 6 * (w + 18)), (30, 30, 30))
        d = ImageDraw.Draw(S)
        for m, i in enumerate(pick):
            col, blk = m % half, m // half
            j = ts_i(i)
            for k, im in enumerate((tsmk(j), bld('iso', i), bld('ra', i))):
                h = int(round(w * im.height / im.width))
                tile = P.on_bg(im).resize((w, h), Image.NEAREST if k == 0 else Image.LANCZOS).convert('RGB')
                if h > w:
                    tile = tile.crop((0, (h - w) // 2, w, (h - w) // 2 + w))
                y = (blk * 3 + k) * (w + 18)
                S.paste(tile, (col * (w + 4), y + 16 + (w - tile.height) // 2))
                d.text((col * (w + 4) + 4, y + 2), (f'TS {j:02d}', f'HD {i:02d} TS angle', f'HD {i:02d} RA grid')[k], fill=(255, 255, 0))
        S.save(f'{out}/build-up-strip-vs-original.png')
        frs = []
        for i in list(range(n)) + [n - 1] * 8:
            j = ts_i(i)
            frs.append(self.three_up([tsmk(j), bld('iso', i), bld('ra', i)],
                                     (f"TS {s['ts']}MK {j:02d}/{s['ts_mk_n'] - 1}", 'HD, TS angle', 'HD, RA grid'), f'build-up {i:02d}/{n - 1}'))
        self.gif(frs, f'{out}/build-up-vs-original.gif', 120)
        # idle loops vs TS
        ln = s['idle_n']
        for lv in (0, 1):
            frs = [self.three_up([self.ts_building(lv, t), self.scene('iso', lv, t), self.scene('ra', lv, t)], self.T3(),
                                 f"{('healthy', 'damaged')[lv]} idle {t:02d}: {s['idle_label']}") for t in range(ln)]
            self.gif(frs, f"{out}/idle-{('healthy', 'damaged')[lv]}-vs-original.gif", s.get('idle_ms', 110))
        for extra in s.get('extra_previews', []):
            extra(self, out)
        print('previews done')

    def readme(self):
        open(f"{self.s['pkg']}/README.txt", 'w').write(self.s['readme']())

    def src(self):
        d = f"{self.s['pkg']}/src"
        os.makedirs(d, exist_ok=True)
        for f in self.s['src']:
            shutil.copy(f'/home/claude/work/r/{f}', d)

    def zipit(self, limit=29.5 * 2 ** 20):
        import zipfile
        pkg = self.s['pkg']
        base, name = os.path.dirname(pkg), os.path.basename(pkg)
        files = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(pkg) for f in fs)
        total = sum(os.path.getsize(f) for f in files)
        for old in [f for f in os.listdir(base) if f.startswith(name) and f.endswith('.zip')]:
            os.remove(os.path.join(base, old))
        if total < limit:
            parts = [(f'{name}.zip', files)]
        else:
            parts = [(f'{name}-part1.zip', [f for f in files if '/loop/' not in f]),
                     (f'{name}-part2-loop.zip', [f for f in files if '/loop/' in f])]
        outs = []
        for zname, fl in parts:
            with zipfile.ZipFile(os.path.join(base, zname), 'w', zipfile.ZIP_DEFLATED) as z:
                for f in fl:
                    z.write(f, os.path.relpath(f, base))
            print(zname, '%.1f MiB' % (os.path.getsize(os.path.join(base, zname)) / 2 ** 20))
            outs.append(os.path.join(base, zname))
        return outs


if __name__ == '__main__':
    spec = importlib.import_module(sys.argv[1]).SPEC
    what = sys.argv[2]
    pk = Pack(spec)
    if what in ('previews', 'all'):
        pk.previews()
    if what in ('readme', 'all'):
        pk.readme()
    if what in ('src', 'all'):
        pk.src()
    if what in ('zip', 'all'):
        pk.zipit()
