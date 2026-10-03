"""Previews, README, src and zip for the Firestorm Wall Section package (walls don't fit bdeliver's building layout).

    python3 fsdfpack.py previews | readme | src | zip | all"""
import os, sys, shutil, zipfile
import numpy as np
from PIL import Image, ImageDraw
import ypreview as P

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-firestorm-wall-hd')
HAND = '/home/claude/work/ts/ts-buildings-hd-handoff/17-TSFSDF'
NAME = 'firestorm-wall'
V = {'iso': 'ts-angle', 'ra': 'ra-grid'}
DARK = (30, 30, 30, 255)
TSK, TSO = 3.5, (4, 34)


def fr(view, k):
    return Image.open(f'{PKG}/{V[view]}/wall/{NAME}-{k:02d}.png').convert('RGBA')


def pulse(view, k):
    return Image.open(f'{PKG}/{V[view]}/A-pulse/{NAME}-pulse-{k:02d}.png').convert('RGBA')


def ts(k, shp='GTFSDF'):
    im = Image.open(f'{HAND}/ts-original/{shp}/frames/{k:02d}.png').convert('RGBA')
    big = im.resize((round(48 * TSK), round(48 * TSK)), Image.NEAREST)
    c = Image.new('RGBA', (176, 320), (0, 0, 0, 0)); c.alpha_composite(big, TSO)
    return c


def mask_of(cells, c):
    x, y = c
    return (1 if (x, y - 1) in cells else 0) | (2 if (x + 1, y) in cells else 0) | (4 if (x, y + 1) in cells else 0) | \
        (8 if (x - 1, y) in cells else 0)


def ra_run(cv, cells, at, add=0):
    """sections on the RA grid canvas cv, cells relative to `at` (grid cells); add: 16 damaged, 32 the field on."""
    for c in sorted(cells, key=lambda c: (c[1], c[0])):
        im = fr('ra', mask_of(cells, c) + add)
        P.paste(cv, im, (at[0] + c[0]) * 128 - 24, (at[1] + c[1]) * 128 - 96)


def iso_run(cells, getter, W=900, H=520, o=(80, 120)):
    """sections on TS's diamond grid (a cell east = (+84, +42) px, south = (-84, +42) at x3.5), back to front."""
    cv = Image.new('RGBA', (W, H), P.BG)
    for c in sorted(cells, key=lambda c: (c[0] + c[1], c[0])):
        x, y = c
        im = getter(mask_of(cells, c))
        cx, cy = o[0] + (x - y) * 84 + 300, o[1] + (x + y) * 42
        P.paste(cv, im, int(cx - 88), int(cy - 160))
    return cv


RING = {(x, y) for x in range(4) for y in range(3) if x in (0, 3) or y in (0, 2)}
TEE = {(0, 1), (1, 1), (2, 1), (3, 1), (1, 0), (1, 2), (2, 2)}
CROSS = {(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)}
LINE = {(x, 0) for x in range(5)}


def tile(im, title, sub=None, z=1.0, w=None, h=None):
    t = P.on_bg(im)
    if z != 1.0:
        t = t.resize((int(t.width * z), int(t.height * z)), Image.LANCZOS)
    w = w or t.width; h = h or t.height + 30
    c = Image.new('RGBA', (w, h), DARK)
    c.paste(t, ((w - t.width) // 2, 30))
    d = ImageDraw.Draw(c)
    d.text((4, 2), title, fill=(255, 255, 0, 255))
    if sub:
        d.text((4, 15), sub, fill=(220, 220, 220, 255))
    return c


def grid_of(ims, cols, gap=6):
    w = max(i.width for i in ims); h = max(i.height for i in ims)
    rows = (len(ims) + cols - 1) // cols
    S = Image.new('RGBA', (cols * (w + gap), rows * (h + gap)), DARK)
    for k, im in enumerate(ims):
        S.paste(im, ((k % cols) * (w + gap), (k // cols) * (h + gap)))
    return S


def previews():
    out = f'{PKG}/previews'
    os.makedirs(out, exist_ok=True)
    # every frame of both views (cropped to the cell's band)
    for view in ('iso', 'ra'):
        band = (0, 70, 176, 250)
        rows = []
        for add, lab in ((0, 'healthy (00-15)'), (16, 'damaged (16-31)'), (32, 'the field on (32-47)'), (48, 'damaged, the field on (48-63)')):
            ims = [tile(fr(view, m + add).crop(band), f'{m + add:02d}', z=0.75) for m in range(16)]
            g = grid_of(ims, 16, 4)
            lab_im = Image.new('RGBA', (g.width, 20), DARK); ImageDraw.Draw(lab_im).text((4, 4), lab, fill=(255, 255, 255, 255))
            rows += [lab_im, g]
        S = Image.new('RGBA', (rows[1].width, sum(r.height for r in rows)), DARK)
        y = 0
        for r in rows:
            S.paste(r, (0, y)); y += r.height
        S.save(f'{out}/{NAME}-all-frames-{V[view]}.png')
    # TS vs HD (TS's angle): healthy 0-15 and the field on 32-47
    band = (0, 80, 176, 240)
    ims = []
    for m in range(16):
        ims.append(tile(ts(m).crop(band), f'TS {m:02d}'))
        ims.append(tile(fr('iso', m).crop(band), f'HD {m:02d}'))
    for m in (0, 5, 7, 15):
        ims.append(tile(ts(m + 32).crop(band), f'TS {m + 32:02d}'))
        ims.append(tile(fr('iso', m + 32).crop(band), f'HD {m + 32:02d}'))
    grid_of(ims, 8).save(f'{out}/{NAME}-vs-original.png')
    # runs on the RA grid, next to a GDI wall run and the Component Tower
    cv = P.canvas(16, 9)
    ra_run(cv, RING, (1, 1)); ra_run(cv, TEE, (6, 1), 32); ra_run(cv, CROSS, (12, 1), 16)
    ra_run(cv, LINE, (1, 6))
    for x in range(7, 12):                                        # a GDI wall run alongside
        m = (2 if x < 11 else 0) + (8 if x > 7 else 0)
        P.paste(cv, P.gdi_wall(m), x * 128, 6 * 128)
    P.paste(cv, P.tower(0), 13 * 128 - 24, 6 * 128 - 96)
    d = ImageDraw.Draw(cv)
    for t, xy in (('a ring', (1, 1)), ('a T, the field on', (6, 1)), ('a cross, damaged', (12, 1)), ('a line', (1, 6)),
                  ('a GDI wall run', (7, 6)), ('the Component Tower', (13, 6))):
        d.text((xy[0] * 128 + 4, xy[1] * 128 - 18), t, fill=(255, 255, 0, 255))
    cv.save(f'{out}/{NAME}-runs-ra-grid.png')
    # a run in TS's angle, next to TS's own sprites run the same way
    a = iso_run(RING, lambda m: ts(m)); b = iso_run(RING, lambda m: fr('iso', m))
    S = Image.new('RGBA', (a.width, a.height * 2 + 10), DARK)
    S.paste(a, (0, 0)); S.paste(b, (0, a.height + 10))
    d = ImageDraw.Draw(S); d.text((6, 6), "TS's own frames (x3.5) on TS's grid", fill=(255, 255, 0, 255))
    d.text((6, a.height + 16), 'HD, TS angle', fill=(255, 255, 0, 255))
    S.save(f'{out}/{NAME}-run-ts-angle-vs-original.png')
    # GTFSDF_A: the emitter pulsing, on a lone section
    frs = []
    for k in list(range(4)) * 4:
        t_ = ts(0); t_.alpha_composite(ts(k, 'GTFSDF_A'))
        i_ = fr('iso', 0); i_.alpha_composite(pulse('iso', k))
        r_ = fr('ra', 0); r_.alpha_composite(pulse('ra', k))
        band = (0, 90, 176, 230)
        row = grid_of([tile(t_.crop(band), 'TS GTFSDF_A', z=2), tile(i_.crop(band), 'HD, TS angle', z=2),
                       tile(r_.crop(band), 'HD, RA grid', z=2)], 3)
        frs.append(row)
    q = [f.convert('RGB').quantize(colors=255, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG) for f in frs]
    q[0].save(f'{out}/pulse-vs-original.gif', save_all=True, append_images=q[1:], duration=150, loop=0, optimize=True)
    print('previews done')


def readme():
    txt = f"""Tiberian Sun Firestorm Wall Section (Firestorm GAFSDF; TSFSDF in the mod) rebuilt for Red Alert Remastered (HD).

v2 (2026-10-03): checked frame by frame against TS's own GTFSDF / GTFSDF_A (previews/run-vs-original.gif,
sections-vs-original.gif) and brought closer to them: the live field now glows TS's strong blue and light blue (with
white glints and pure blue studs) over the pad's whole outer band and the whole grating, not a pale lilac; the dish
stays dark when it is on, as TS's; the gratings' rungs are TS's six chunky rungs to a cell, grey on top with
blue-lit faces, over dark gaps, with brackets on the rails; the emitter is TS's trident standing up in the dish
(three prongs, the middle tallest) instead of a flat mark, and GTFSDF_A's frame 02 lights its prongs, as TS's.

One 3D model fitted to TS's own sprites (GTFSDF, GTFSDF_A), one cell, joining its neighbours like a wall, rendered with
the same renderer as the Construction Yard and the rest (materials, light, shadow ~75% black, outline).

CANVAS     176x320 in both views, as the mod's (the Component Tower's): the cell at x 24-152, y 96-224, its ground
           centre at (88, 160).
ra-grid/   RA's wall view, as the GDI wall and the gates: looking north, the ground not foreshortened (a cell is
           128x128 px), heights up 0.6 px per unit; so sections join edge to edge on RA's square grid (see
           previews/{NAME}-runs-ra-grid.png).
ts-angle/  TS's own camera, lit from TS's side. TS's frame x3.5 (the cell's diamond 168 px wide, inside the canvas;
           the mod's frame is a placeholder, so there was no scale to keep), TS px (0, 0) at canvas (4, 34). These
           tile on TS's diamond grid (a cell east = +84, +42 px), not on RA's square one.
COLOUR     no house colour (TS's section has none); every frame still has its -trim.png (all black).

What it is (read from TS's frames):
  pad        a low lilac-grey steel pad in the middle of the cell, its rim raised, a light band round a dark dish in
             its middle; the emitter a trident standing in the dish (a short bar with three prongs, the middle
             tallest), facing the camera in each view as TS draws it face-on
  gratings   a grating bridge from the pad to the cell's edge on every side with a neighbour: steel rails with
             brackets on their outer sides, six chunky rungs to a cell (grey on top, their faces lit blue) over dark
             gaps; a section with neighbours on two opposite sides only is all grating, no pad (TS's 05, 10)
  field on   the pad's outer band and rim, the rails, the brackets and the whole grating glow blue and light blue with
             white glints, pure blue studs round the rim; the dish, the band round it and the trident stay as they are
             (TS's 32-47)

wall/{NAME}-00..63     TSFSDF.ZIP's layout: frame = the neighbour mask (N1 E2 S4 W8) + 16 damaged + 32 the field on.
                        Damaged (my own: TS's GTFSDF has healthy and rubble only): the pad's south-west corner chipped,
                        a crack across it, scorch round the dish, a dent in each grating (bars knocked down), soot,
                        steel bits. Greys and browns only.
A-pulse/{NAME}-pulse-00..07
                        GTFSDF_A: the emitter pulsing (00 as it is, 01 the ring round the dish glowing white with blue
                        studs on its inner edge, 02 the trident's prongs white, 03 the whole dish light blue with the
                        trident white), 04-07 empty, as TS's. Cut against wall-00: draw it over any section with a pad
                        (every mask but 05 and 10, the all-grating ones); it matches the field-on frames too (the dish
                        is the same in both).
No build-up: TS has none for its wall sections.

previews/  every frame of both views; TS's frames next to the HD TS-angle ones; runs on the RA grid (a ring, a T with
           the field on, a damaged cross, a line) next to a GDI wall run and the Component Tower; a ring in TS's angle
           next to TS's own sprites run the same way; pulse-vs-original.gif; run-vs-original.gif (a run three ways:
           TS's own frames on TS's grid, HD TS angle, HD RA grid; the field off, switching on with the pulse, off, then
           damaged); sections-vs-original.gif (every mask, off then on, TS | HD TS angle | HD RA grid at 2x).
3d/        firestorm-wall.glb: one mesh per kind of section (alone, end, straight, corner, T, cross: masks 0, 1, 5, 3,
           7, 15; the rest are these turned), 1.5 cells apart along x, the trident facing south. 3d/stl/: the same as print-ready STL (mm at 1
           cell = 32 mm, Z up, flat on Z = 0, watertight, thin parts thickened to 1 mm; README-stl.txt).
src/       Python 3 (numpy, scipy, Pillow). fsdf.py the model, fsdfmat.py its materials (the field, the pulse),
           fsdfdamage.py the damage, fsdfrender.py the views (the RA wall view: a camera at 59.04 degrees, cos/sin =
           0.6, stretched upright), fsdffinal.py the frames (walls|pulse iso|ra), fsdfexport.py the .glb, stlprint.py
           the STL, fsdfpack.py the previews and this package.

My calls (each easy to change):
  - RA grid in RA's wall view (like the GDI wall), so runs join; the TS-angle set tiles on TS's grid only.
  - The damaged frames are my own (TS has none for it).
  - TS angle at x3.5, so the cell fits the 176 px canvas.
  - The trident turns to face the camera in each view (TS draws it face-on); in the .glb it faces south (the RA grid's
    way).
"""
    open(f'{PKG}/README.txt', 'w').write(txt)


SRC = ['hd.py', 'walls2.py', 'wnoise.py', 'brender.py', 'pfinal.py', 'pdamage.py', 'radr.py', 'plug.py', 'plugs.py',
       'export3d.py', 'stlprint.py', 'stlpack.py', 'ypreview.py', 'weapdamage.py', 'fsdf.py', 'fsdfmat.py',
       'fsdfdamage.py', 'fsdfrender.py', 'fsdffinal.py', 'fsdfexport.py', 'fsdfpack.py', 'fsdfreview.py']


def src():
    d = f'{PKG}/src'
    os.makedirs(d, exist_ok=True)
    for f in SRC:
        shutil.copy(f'/home/claude/work/r/{f}', d)


def zipit():
    base, name = os.path.dirname(PKG), os.path.basename(PKG)
    files = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(PKG) for f in fs)
    rest = [f for f in files if '/3d/' not in f]
    for zn, fl in ((f'{name}.zip', rest),):
        with zipfile.ZipFile(os.path.join(base, zn), 'w', zipfile.ZIP_DEFLATED) as z:
            for f in fl:
                z.write(f, os.path.relpath(f, base))
        print(zn, '%.1f MiB' % (os.path.getsize(os.path.join(base, zn)) / 2 ** 20))


if __name__ == '__main__':
    w = sys.argv[1]
    if w in ('previews', 'all'):
        previews()
    if w in ('readme', 'all'):
        readme()
    if w in ('src', 'all'):
        src()
    if w in ('zip', 'all'):
        zipit()
