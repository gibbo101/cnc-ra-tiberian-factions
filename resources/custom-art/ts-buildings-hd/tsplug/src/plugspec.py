"""Package spec for the Upgrade Center (bdeliver.py)."""
import os
import numpy as np
from PIL import Image, ImageDraw
import ypreview as P

HAND = '/home/claude/work/ts/ts-buildings-hd-handoff/12-TSPLUG'
PKG = os.environ.get('PKG', '/home/claude/work/out/ts-upgrade-center-hd')
PLUGS = (('D', 'drop-pod-node', 'tspods-0000.png', 'Drop Pod Node'), ('E', 'seeker-control', 'tsseek-0000.png', 'Seeker Control'),
         ('F', 'ion-cannon-uplink', 'tspion-0000.png', 'Ion Cannon Uplink'))
MOD_WIN = {'D': (101, 147), 'E': (104, 142), 'F': (104, 118)}


def shape_check(pk, out):
    import plugshape
    plugshape.build(f'{out}/shape-check.png')


def plugs_preview(pk, out):
    """the three plugs: TS's (GTPLUG_D/E/F over GTPLUG) next to ours over the building, both views; the 128x128 pieces
    next to the mod's; and a GIF of E's and F's turning."""
    T = f'{HAND}/ts-original'
    rows = []
    iso = pk.has('iso')                      # v5 (Luke): RA grid only - the TS angle's plug pieces aren't packaged
    for kind, name, mod, title in PLUGS:
        ts = pk.ts_canvas([f'{T}/GTPLUG/frames/00.png', f'{T}/GTPLUG_{kind}/frames/00.png'])
        base_r = pk.scene('ra', 0, 0)
        rp = Image.open(f'{PKG}/ra-grid/plugs/{name}/{name}-00.png').convert('RGBA')
        org = open(f'{PKG}/ra-grid/plugs/{name}/window.txt').read().split()
        base_r.alpha_composite(rp, (int(org[0]), int(org[1])))
        if iso:
            base_i = pk.scene('iso', 0, 0)
            piece = Image.open(f'{PKG}/ts-angle/plugs/{name}/{name}-00.png').convert('RGBA')
            wx, wy = MOD_WIN[kind]
            base_i.alpha_composite(piece, (wx, wy))
        rows.append(pk.three_up(pk.cols(pk.crop('iso', ts), lambda: pk.crop('iso', base_i), lambda: pk.crop('ra', base_r)),
                                pk.T3(), f'{title} (GTPLUG_{kind}) in the east socket'))
        modp = Image.open(f'{HAND}/in-mod/{mod}').convert('RGBA')
        tl = [(pk.zoom(modp, 3, nearest=True), f'In the mod now: {mod} (3x)')]
        if iso:
            tl.append((pk.zoom(piece, 3), f'HD: plugs/{name}/{name}-00 (TS angle, 3x)'))
        tl.append((pk.zoom(rp, 3), f'HD: plugs/{name}/{name}-00 (RA grid, 3x)'))
        r = Image.new('RGBA', (sum(t.width for t, _ in tl) + 12 * (len(tl) - 1), max(t.height for t, _ in tl) + 28),
                      (30, 30, 30, 255))
        xx = 0
        for t, lab in tl:
            r.paste(t, (xx, 28)); P.label(r, lab, (xx + 6, 8)); xx += t.width + 12
        rows.append(r)
    pk.stack(rows).save(f'{out}/plugs-vs-original.png')
    frs = []
    for t in range(15):
        tiles = []
        for kind, name, mod, title in PLUGS[1:]:
            ts = pk.ts_canvas([f'{T}/GTPLUG/frames/00.png', f'{T}/GTPLUG_{kind}/frames/{t:02d}.png']).crop((80, 120, 240, 280))
            hd = Image.open(f'{PKG}/{"ts-angle" if iso else "ra-grid"}/plugs/{name}/{name}-{t:02d}.png').convert('RGBA')
            tiles += [P.on_bg(ts).resize((256, 256), Image.NEAREST), P.on_bg(hd).resize((256, 256), Image.LANCZOS)]
        W = Image.new('RGB', (256 * 4 + 24, 256 + 24), (30, 30, 30))
        for i, tl in enumerate(tiles):
            W.paste(tl.convert('RGB'), (i * 264, 24))
        d = ImageDraw.Draw(W)
        d.text((6, 6), f'GTPLUG_E {t:02d} | HD Seeker Control | GTPLUG_F {t:02d} | HD Ion Cannon Uplink'
                       + ('' if iso else ' (RA grid)'), fill=(255, 255, 0))
        frs.append(W)
    frs[0].save(f'{out}/plugs-turning-vs-original.gif', save_all=True, append_images=frs[1:], duration=110, loop=0)


def loop_preview(pk, out):
    """the plug combinations of loop/ (healthy, the overlays at frame 0), both views; and the mod's tsplug-0000 / -0400
    next to the same combinations."""
    import plugloop as LP
    bg = (90, 100, 80, 255)

    def combo(view, name, level=0, t=0):
        b = Image.open(f'{PKG}/loop/{view}/base/{name}/upgrade-center-{name}-{level:02d}.png').convert('RGBA')
        for sub, pre, n in (('A-dish', 'dish', 20), ('B-lamps', 'lamps', 10), ('C-slot', 'slot', 8)):
            b.alpha_composite(Image.open(f'{PKG}/{view}/{sub}/upgrade-center-{pre}-{t % n + n * level:02d}.png').convert('RGBA'))
        return b
    views = [v for k, v in (('iso', 'ts-angle'), ('ra', 'ra-grid')) if pk.has(k)]
    tiles = []
    for name, right, left in LP.COMBOS:
        for view in views:
            im = combo(view, name)
            c = Image.new('RGBA', im.size, bg); c.alpha_composite(im)
            c = c.convert('RGB').resize((im.width * 2 // 3, im.height * 2 // 3), Image.LANCZOS)
            P.label(c, f'{name} ({view})', (4, 4))
            tiles.append(c)
    W = max(t.width for t in tiles); H = max(t.height for t in tiles)
    cols = 4
    sheet = Image.new('RGB', (cols * (W + 6), ((len(tiles) + cols - 1) // cols) * (H + 6)), (30, 30, 30))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * (W + 6), (i // cols) * (H + 6)))
    sheet.save(f'{out}/loop-plug-combinations.png')
    # a GIF through the combinations in loop/'s order (healthy, the dish / lamps / slot loop playing), both views
    full = {k: title for k, _, _, title in PLUGS}
    frs = []
    for i, (name, right, left) in enumerate(LP.COMBOS):
        lab = 'no plugs' if right is None else ('right: ' + full[right] + ('' if left is None else ',  left: ' + full[left]))
        for t in range(12):
            row = []
            for view in views:
                im = combo(view, name, 0, t)
                c = Image.new('RGBA', im.size, bg); c.alpha_composite(im)
                row.append(c.convert('RGB').resize((im.width * 3 // 4, im.height * 3 // 4), Image.LANCZOS))
            W = Image.new('RGB', (sum(r.width for r in row) + 8 * (len(row) - 1), max(r.height for r in row) + 22), (30, 30, 30))
            xx = 0
            for r_ in row:
                W.paste(r_, (xx, 22)); xx += r_.width + 8
            P.label(W, f'loop {i * 80:04d}-{i * 80 + 79:04d}   {lab}', (6, 4))
            frs.append(W)
    frs[0].save(f'{out}/loop-plug-combinations.gif', save_all=True, append_images=frs[1:], duration=110, loop=0)
    rows = []
    for mod, name in ((('tsplug-0000.png', 'none'), ('tsplug-0400.png', 'right-ion_left-seeker')) if pk.has('iso') else ()):
        m = Image.open(f'{HAND}/in-mod/{mod}').convert('RGBA')
        a = Image.new('RGBA', m.size, bg); a.alpha_composite(m)
        b = Image.new('RGBA', m.size, bg); b.alpha_composite(combo('ts-angle', name))
        r = Image.new('RGB', (m.width * 2 + 10, m.height + 20), (30, 30, 30))
        r.paste(a.convert('RGB'), (0, 20)); r.paste(b.convert('RGB'), (m.width + 10, 20))
        P.label(r, f'In the mod now: {mod}', (4, 4)); P.label(r, f'HD: loop {name} (healthy, overlays at frame 0)', (m.width + 14, 4))
        rows.append(r)
    if rows:
        pk.stack(rows).save(f'{out}/in-mod-loop-vs-hd.png')


def readme():
    return open('/home/claude/work/r/plugreadme.txt').read()


SPEC = dict(
    name='upgrade-center', title='Upgrade Center', pkg=PKG, hand=HAND,
    ts='GTPLUG', K=3.695, O=(-15.0, -112.0), iso_size=(384, 384), ra_size=(384, 448), ra_head=32, ra_left=64,
    cells=(2, 3), state_dir='building', views=('ra',),          # v5 (Luke, 6 Oct 2026): the RA grid only
    overlays=[dict(folder='A-dish', prefix='dish', n=20, ts_shp='GTPLUG_A', ts_frame=lambda t, lv: t % 20),
              dict(folder='B-lamps', prefix='lamps', n=10, ts_shp='GTPLUG_B', ts_frame=lambda t, lv: t % 10 + 10 * lv),
              dict(folder='C-slot', prefix='slot', n=8, ts_shp='GTPLUG_C', ts_frame=lambda t, lv: (t % 8) if lv == 0 else None)],
    loop=None,
    inmod=[('tsplugmake-0018.png', 0, 0, ('build-up', 'upgrade-center-build-23'))],
    build_n=24, ts_mk_n=17, ts_mk='GTPLUGMK', idle_n=40, idle_label='building + A (dish) + B (lamps) + C (slot light)',
    idle_ms=110,
    crop={'iso': (0, 0, 384, 384), 'ra': (0, 0, 384, 448)},
    zoom=1.5, green_zoom=1.5, gif_zoom=1.0, strip_w=150,
    extra_previews=[plugs_preview, loop_preview],          # (v3: the v1 shape check's RA options are history)
    src=['hd.py', 'walls2.py', 'wnoise.py', 'brender.py', 'pfinal.py', 'pdamage.py', 'bdeliver.py', 'ypreview.py',
         'weapdamage.py', 'weap.py', 'weapplace.py', 'tsgeo.py', 'cleanalpha.py', 'radr.py', 'dept.py', 'deptfit.py',
         'plug.py', 'plugs.py', 'plugmat.py', 'plugdamage.py', 'plugbuild.py', 'plugrender.py', 'plugfinal.py',
         'plugspec.py', 'plugeo.py', 'plugfit.py', 'plugsfit.py', 'plugplace.py', 'plugshape.py', 'export3d.py',
         'plugexport.py', 'plugloop.py'],
    readme=readme,
)
