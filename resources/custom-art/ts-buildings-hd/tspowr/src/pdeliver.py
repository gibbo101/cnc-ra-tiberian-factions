"""Previews, README, src and zip for the Power Plant package (run after pfinal.py has made the frames).
    python3 pdeliver.py previews | readme | src | zip | all"""
import os, sys, shutil
import numpy as np
from PIL import Image, ImageDraw
import ypreview as P, pbuild as B, panim as PA, powr as PW, prender as PR
from pfinal import PKG, NAME, VIEWS as V, POD_NAMES, pod_origin

HAND = '/home/claude/work/ts/ts-buildings-hd-handoff/02-TSPOWR'
TS = f'{HAND}/ts-original'
YARD = '/home/claude/work/out/ts-gdi-construction-yard-hd'
BG = P.BG
DARK = (30, 30, 30, 255)
Z = 2
N = PA.A_N
RA_HEAD = 8                       # RA canvas 256x272: the plot at y 8 .. 264


# ------------------------------------------------------------------------------------------------ frames
def fr(view, sub, name):
    return Image.open(f'{PKG}/{V[view]}/{sub}/{name}.png').convert('RGBA')


def plant(view, level=0):
    """the plant with its east pod (at rest)."""
    return fr(view, 'plant', f'{NAME}-{level:02d}')


def lights(view, t, level=0):
    return fr(view, 'A-lights', f'{NAME}-lights-{t + N * level:02d}')


def pod(view, name, t, level=0):
    return fr(view, f'B-pods/{name}', f'{NAME}-pod-{name}-{t + N * level:02d}')


def scene(view, level=0, t=0, npods=1, lit=True):
    """the plant + its pods (1: east; 2: + middle; 3: + west) + the tower lights, drawn the way the game draws them."""
    im = plant(view, level)
    for nm in POD_NAMES[:npods]:
        im.alpha_composite(pod(view, nm, t, level))
    if lit:
        im.alpha_composite(lights(view, t, level))
    return im


def loop(view, npods, level, t):
    return fr(view, 'loop', f'{NAME}-loop-{(2 * (npods - 1) + level) * N + t:02d}')


def ts_canvas(paths):
    """TS frames composited, x3.36 nearest, placed on the mod's 256x256 canvas like tspowr-0000."""
    base = Image.open(paths[0]).convert('RGBA')
    for p in paths[1:]:
        base.alpha_composite(Image.open(p).convert('RGBA'))
    ts = np.array(base)
    yy, xx = np.mgrid[0:256, 0:256]
    tx = np.floor((xx + 0.5 + 30.0) / PR.ISO_K).astype(int)
    ty = np.floor((yy + 0.5 + 53.5) / PR.ISO_K).astype(int)
    ok = (tx >= 0) & (tx < 96) & (ty >= 0) & (ty < 96)
    out = np.zeros((256, 256, 4), np.uint8)
    out[ok] = ts[ty[ok], tx[ok]]
    return Image.fromarray(out)


def ts_plant(level=0, t=None, pod=False):
    paths = [f'{TS}/GTPOWR/frames/{level:02d}.png']
    if pod:
        paths.append(f'{TS}/GTPOWR_B/frames/{(t or 0) % N:02d}.png')
    if t is not None:
        paths.append(f'{TS}/GTPOWR_A/frames/{t % N + N * level:02d}.png')
    return ts_canvas(paths)


# ------------------------------------------------------------------------------------------------ layout
def zoom(im, z=Z, nearest=False):
    return P.on_bg(im).resize((im.width * z, im.height * z), Image.NEAREST if nearest else Image.LANCZOS)


def three_up(ims, titles, sub=None, z=Z):
    """TS (on the mod's canvas) | TS angle | RA grid, at z x."""
    W = 256 * z
    H = 272 * z
    S = Image.new('RGBA', (3 * W + 24, H + 34), DARK)
    d = ImageDraw.Draw(S)
    for k, im in enumerate(ims):
        t = zoom(im, z, nearest=(k == 0))
        S.paste(t, (k * (W + 12), 34 + (H - t.height) // 2))
        d.text((k * (W + 12) + 6, 4), titles[k], fill=(255, 255, 0, 255))
    if sub:
        d.text((6, 18), sub, fill=(255, 255, 255, 255))
    return S


def stack(ims, gap=0, bg=DARK):
    W = max(i.width for i in ims)
    S = Image.new('RGBA', (W, sum(i.height for i in ims) + gap * (len(ims) - 1)), bg)
    y = 0
    for i in ims:
        S.paste(i, (0, y))
        y += i.height + gap
    return S


def gif(frames, path, ms):
    q = [f.convert('RGB').quantize(colors=255, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=ms, loop=0, optimize=True)


T3 = ('TS original (x3.36, the mod\'s canvas)', 'HD, TS angle (256x256)', 'HD, RA grid (256x272)')


# ------------------------------------------------------------------------------------------------ scenes
def ra_scene(level=0, t=0, npods=2, cols=10, rows=6):
    """RA grid: the Construction Yard, the Power Plant and the Component Tower with a GDI wall run in front.
    RA order: walls with the map, then buildings from the back (north) to the front."""
    c = P.canvas(cols, rows)
    for x in range(cols):
        m = (2 if x < cols - 1 else 0) + (8 if x > 0 else 0)
        P.paste(c, P.gdi_wall(m), x * 128, 5 * 128)
    yard = Image.open(f'{YARD}/ra-grid/yard/construction-yard-{level:02d}.png').convert('RGBA')
    items = [(3, P.tower(level), 8 * 128 - 24, 2 * 128 - 96),
             (4, yard, 1 * 128, 2 * 128 - P.YARD_HEAD),
             (4, scene('ra', level, t, npods), 5 * 128, 2 * 128 - RA_HEAD)]
    for _, im, x, y in sorted(items, key=lambda it: it[0]):
        P.paste(c, im, x, y)
    d = ImageDraw.Draw(c)
    d.rectangle([128, 256, 128 + 384 - 1, 256 + 256 - 1], outline=(255, 255, 0, 110))
    d.rectangle([5 * 128, 256, 5 * 128 + 256 - 1, 256 + 256 - 1], outline=(255, 255, 0, 110))
    return c


def slot_offsets():
    """top-left of the 128 pod canvas on the plant's canvas for each socket (east, middle, west), both views."""
    p = PW.P
    offs = {}
    for v in ('iso', 'ra'):
        view = PR.iso_view(1) if v == 'iso' else PR.ra_view(RA_HEAD, 1)
        at = pod_origin(view)[2]
        o = []
        for (cx, cy) in p['slots']:
            sx, sy = view.project(np.array([cx]), np.array([cy]), np.array([p['sock_z']]))
            o.append((int(round(sx[0] - at[0])), int(round(sy[0] - at[1]))))
        offs[v] = o
    return offs


# ------------------------------------------------------------------------------------------------ previews
def previews():
    out = f'{PKG}/previews'
    os.makedirs(out, exist_ok=True)

    # on its own (with its east pod), both views, 2x
    W = Image.new('RGBA', (512 * 2 + 16, 544 + 30), DARK)
    W.paste(zoom(plant('iso')), (0, 30 + 16))
    W.paste(zoom(plant('ra')), (512 + 16, 30))
    P.label(W, 'TS angle, 2x', (6, 8))
    P.label(W, 'RA grid, 2x (the 2x2 plot is y 8-264 of the canvas)', (512 + 22, 8))
    W.save(f'{out}/plant-on-its-own.png')

    # the two states next to TS's (TS: GTPOWR + its turbine, GTPOWR_B frame 00)
    rows = [three_up([ts_plant(lv, pod=True), plant('iso', lv), plant('ra', lv)], T3,
                     f'{("healthy", "damaged")[lv]} (frame {lv:02d}), with the east pod') for lv in (0, 1)]
    stack(rows).save(f'{out}/plant-states-vs-original.png')

    # in the mod now vs HD, frame for frame: the loop has the same layout as TSPOWR.ZIP
    rows = []
    for k, (n, npods, lv) in enumerate(((0, 1, 0), (36, 2, 1))):
        s = Image.new('RGBA', (512 * 2 + 12, 512 + 28), DARK)
        s.paste(zoom(Image.open(f'{HAND}/in-mod/tspowr-{n:04d}.png').convert('RGBA'), nearest=True), (0, 28))
        s.paste(zoom(fr('iso', 'loop', f'{NAME}-loop-{n:02d}')), (512 + 12, 28))
        P.label(s, f'In the mod now: tspowr-{n:04d}.png (2x)', (6, 8))
        P.label(s, f'HD, TS angle: loop/{NAME}-loop-{n:02d} ({("healthy", "damaged")[lv]}, {npods} pod{"s" if npods > 1 else ""}) (2x)', (512 + 18, 8))
        rows.append(s)
    stack(rows).save(f'{out}/in-mod-vs-hd.png')

    # RA grid, next to the Construction Yard, the Component Tower and a GDI wall run
    ra_scene(0).save(f'{out}/plant-with-yard-tower-and-walls.png')
    ra_scene(1).save(f'{out}/plant-damaged-with-yard-tower-and-walls.png')

    # house colour: the yard next to the plant (three pods), both views
    g = Image.new('RGBA', (768 + 512 + 12, 512 + 720 + 12 + 56), DARK)
    y_iso = Image.open(f'{YARD}/ts-angle/yard/construction-yard-00.png').convert('RGBA')
    y_ra = Image.open(f'{YARD}/ra-grid/yard/construction-yard-00.png').convert('RGBA')
    g.paste(zoom(y_iso), (0, 28))
    g.paste(zoom(scene('iso', 0, 0, 3)), (768 + 12, 28))
    g.paste(zoom(y_ra), (0, 512 + 12 + 56))
    g.paste(zoom(scene('ra', 0, 0, 3)), (768 + 12, 512 + 12 + 56 + 88))
    P.label(g, 'House colour: Construction Yard (left) and Power Plant (right), TS angle, 2x', (6, 8))
    P.label(g, 'RA grid, 2x', (6, 512 + 12 + 36))
    g.save(f'{out}/house-green-vs-yard.png')

    # the pod on its own (128x128) vs the mod's TSTURB, and drawn on the middle socket vs the in-place overlay
    tt = Image.open(f'{HAND}/in-mod/tsturb-0000.png').convert('RGBA')
    pieces = [tt, fr('iso', 'pod-128', 'power-pod-00'), fr('iso', 'pod-128', 'power-pod-01'),
              fr('ra', 'pod-128', 'power-pod-00'), fr('ra', 'pod-128', 'power-pod-01')]
    names = ['mod now: tsturb-0000', 'HD TS angle 00', 'HD TS angle 01', 'HD RA grid 00', 'HD RA grid 01']
    s = Image.new('RGBA', (5 * (384 + 8), 384 + 28), DARK)
    for k, im in enumerate(pieces):
        s.paste(zoom(im, 3, nearest=(k == 0)), (k * 392, 28))
        P.label(s, names[k] + ' (3x)', (k * 392 + 6, 8))
    rows = [s]
    offs = slot_offsets()
    for v in ('iso', 'ra'):
        ox, oy = offs[v][1]
        a = plant(v)
        P.paste(a, fr(v, 'pod-128', 'power-pod-00'), ox, oy)
        b = scene(v, 0, 0, 2, lit=False)
        r = Image.new('RGBA', (512 * 2 + 12, 544 + 28), DARK)
        r.paste(zoom(a), (0, 28))
        r.paste(zoom(b), (512 + 12, 28))
        P.label(r, f'{("TS angle", "RA grid")[v == "ra"]}: the plant + the 128 piece drawn on the middle socket at ({ox}, {oy})', (6, 8))
        P.label(r, 'the plant + B-pods/middle (in place, with its shadow)', (512 + 18, 8))
        rows.append(r)
    stack(rows, 8).save(f'{out}/pod-piece-vs-tsturb.png')

    # build-up: strip and GIF against GTPOWRMK
    n = len(B.SEQ)
    tsmk = lambda j: ts_canvas([f'{TS}/GTPOWRMK/frames/{j:02d}.png'])
    bld = lambda v, i: fr(v, 'build-up', f'{NAME}-build-{i:02d}')
    pick = (0, 3, 6, 9, 11, 13, 14, 15, 16, 17, 18, 20, 21, 23)
    w = 192
    half = len(pick) // 2
    S = Image.new('RGB', (half * (w + 4), 6 * (w + 18)), (30, 30, 30))
    d = ImageDraw.Draw(S)
    for m, i in enumerate(pick):
        col, blk = m % half, m // half
        j = B.ts_index(i)
        for k, im in enumerate((tsmk(j), bld('iso', i), bld('ra', i))):
            h = int(round(w * im.height / im.width))
            tile = P.on_bg(im).resize((w, h), Image.NEAREST if k == 0 else Image.LANCZOS).convert('RGB')
            if h > w:
                tile = tile.crop((0, (h - w) // 2, w, (h - w) // 2 + w))
            y = (blk * 3 + k) * (w + 18)
            S.paste(tile, (col * (w + 4), y + 16))
            d.text((col * (w + 4) + 4, y + 2), (f'TS {j:02d}', f'HD {i:02d} TS angle', f'HD {i:02d} RA grid')[k], fill=(255, 255, 0))
    S.save(f'{out}/build-up-strip-vs-original.png')
    frs = []
    for i in list(range(n)) + [n - 1] * 8:
        j = B.ts_index(i)
        frs.append(three_up([tsmk(j), bld('iso', i), bld('ra', i)],
                            (f'TS GTPOWRMK {j:02d}/{B.TS_N - 1}', 'HD, TS angle', 'HD, RA grid'), f'build-up {i:02d}/{n - 1}'))
    gif(frs, f'{out}/build-up-vs-original.gif', 120)

    # idle: A (lights) + B (the east pod turning) over the plant, healthy and damaged, against TS
    for lv in (0, 1):
        frs = [three_up([ts_plant(lv, t, pod=True), scene('iso', lv, t, 1), scene('ra', lv, t, 1)], T3,
                        f'{("healthy", "damaged")[lv]} idle {t:02d}: the plant + A (tower lights) + B (the east pod turning)')
               for t in range(N)]
        gif(frs, f'{out}/idle-{("healthy", "damaged")[lv]}-vs-original.gif', 110)

    # one, two and three pods (the plant fills east to west), both views, healthy and damaged
    for lv in (0, 1):
        frs = []
        for t in range(N):
            S = Image.new('RGBA', (3 * (512 + 12), 34 + 512 + 12 + 544), DARK)
            d = ImageDraw.Draw(S)
            for k, title in enumerate(('1 pod: the plant as built (east)', '2 pods: + upgrade 1 (middle)',
                                       '3 pods: + upgrade 2 (west)')):
                x = k * (512 + 12)
                S.paste(zoom(scene('iso', lv, t, k + 1)), (x, 34))
                S.paste(zoom(scene('ra', lv, t, k + 1)), (x, 34 + 512 + 12))
                d.text((x + 6, 4), title, fill=(255, 255, 0, 255))
            d.text((6, 18), f'{("healthy", "damaged")[lv]} {t:02d}: plant + B + A, drawn from the overlays.  Top: TS angle.  Bottom: RA grid.',
                   fill=(255, 255, 255, 255))
            frs.append(S)
        gif(frs, f'{out}/pods-1-2-3-{("healthy", "damaged")[lv]}.gif', 110)
    print('previews done')


# ------------------------------------------------------------------------------------------------ readme
def readme():
    org = {v: pod_origin(PR.iso_view(1) if v == 'iso' else PR.ra_view(RA_HEAD, 1)) for v in ('iso', 'ra')}
    offs = slot_offsets()
    fo = lambda v: ', '.join(f'{nm} ({x}, {y})' for nm, (x, y) in zip(POD_NAMES, offs[v]))
    txt = f"""Tiberian Sun GDI Power Plant (GAPOWR, TSPOWR in the mod) and its power pods (the Power Turbine, TSTURB in the
mod) rebuilt for Red Alert Remastered (HD).

One 3D model fitted to TS's own sprites (GTPOWR, GTPOWR_A, GTPOWR_B, GTPOWRMK), rendered two ways with the same
renderer as the Construction Yard and the Component Tower: same materials, light, shadow (baked in at ~75% black)
and outline.

ts-angle/  TS's own camera, lit from TS's side so it reads like the sprite.
           CANVAS 256x256, the same canvas, scale and place as the building in the mod now
           (in-mod/tspowr-0000.png: TS's frame x3.36). Drops in over the current frames.
ra-grid/   Turned to sit on RA's square grid: an orthographic camera 32 degrees above the ground, looking north
           (the tower's, the walls' and the yard's camera). The cooling tower stands on the north-west cell, the
           three pod sockets on the other three.
           CANVAS 256x272: the 256 px of the plot plus 8 px top and bottom. The 2x2 plot is x 0-256, y 8-264, so
           its centre is the canvas centre (128, 136) and the game's centre-on-plot anchoring puts it right. The
           foundation's south edge sits on the plot's south edge; everything (shadow too) stays inside the canvas.
COLOUR     Green = house colour, kept green, exactly the yard's green (same colour and grain on every building,
           so the house colours come out the same). Every frame has a -trim.png (white = house colour,
           antialiased), the same as the tower's and the yard's.

PODS       The plant fills east to west: it comes with the east pod, the first Power Turbine upgrade fills the
           middle socket, the second the west one. So there are three looks: 1 pod (east), 2 (east, middle),
           3 (east, middle, west).
             east    TS angle: the right-hand socket   RA grid: the north-east cell (back right)
             middle  TS angle: the front socket        RA grid: the south-east cell (front right)
             west    TS angle: the left-hand socket    RA grid: the south-west cell (front left)

Each view has the same folders:

plant/power-plant-00.png       healthy, with its east pod (the turbine at rest, frame 00 of its turn).
plant/power-plant-01.png       damaged: the top of the cooling tower broken open with a scorched notch, a hole
                               burnt through the tower's side, soot streaks, cracks in the slab and the mounds,
                               chunks knocked off the middle socket's ring and the east and west mounds, one of
                               the west pipes snapped, rubble on the slab; the east pod sooted, its window band
                               dead. Greys and browns only. No destroyed frame: RA has healthy and damaged only.

loop/power-plant-loop-00..71.png
    Full frames with the animations baked in, laid out like TSPOWR.ZIP (its frame 0000 is the healthy plant
    with one pod and 0036 the damaged plant with two, which is this layout):
        00-11 1 pod healthy   12-23 1 pod damaged
        24-35 2 pods healthy  36-47 2 pods damaged
        48-59 3 pods healthy  60-71 3 pods damaged
    Each 12-frame block is one loop of the tower lights and the pods turning. Straight renders, so the pods'
    shadows on each other are exact. Drop-in for TSPOWR.ZIP.

build-up/power-plant-build-00..23.png
    24 frames, in the order TS's GTPOWRMK builds it, without TS's construction arm: the middle of the slab
    spreads, then the round pads (00-04); the dark drum rises on the tower's site (05-08); the east mound (it
    stays hollow), the green pipes and the decks (07-10); the cooling tower goes up course by course while the
    west mound and then the middle one rise (10-19); the east pod rises out of its mound, cap first, and its
    green ring comes round it (13-18), as in TS; the green collar (17-19); the rings and plates on the other two
    sockets (20-22). 23 is the finished plant (exactly power-plant-00). TSPOWRMAKE.ZIP has 13 frames: for 13,
    take 00, 02, 04 ... 22 and 23, or play all 24 faster.

Animation overlays, if you draw them over the plant rather than use loop/. Each holds only the pixels it
changes, on the plant's canvas, in place:
  A-lights/power-plant-lights-00..23.png         GTPOWR_A: the tower's lamps. Four rings of six lamps, lit
                                                 house green; a white-blue flash runs up the tower ring by ring
                                                 (bottom ring at frame 09, then 00, 03, 06), each fading over
                                                 three frames (12-frame loop). 00-11 healthy, 12-23 damaged (the
                                                 bottom ring works, one lamp left on the second ring and one on
                                                 the top ring, the third ring dead).
  B-pods/east/power-plant-pod-east-00..23.png    GTPOWR_B: the east pod turning (the window band and the
                                                 housing's hatches, 10 degrees a frame, 12-frame loop). Only its
                                                 moving parts. 00-11 healthy, 12-23 damaged (still turning; TS
                                                 has no damaged pod, so this one matches the damaged plant).
  B-pods/middle/power-plant-pod-middle-00..23.png  the middle pod (upgrade 1), whole, turning, with its shadow.
  B-pods/west/power-plant-pod-west-00..23.png      the west pod (upgrade 2), whole, turning, with its shadow.
  DRAW ORDER  the plant, B east, B middle (1+ upgrades), B west (2 upgrades), then A; all at the same frame
              number. Each pod is cut against the plant with the pods before it, so drawn in this order they
              give back the straight render (checked against loop/: the same but for a few antialiased edge
              pixels where the tower's lamps sit on its outline). The lights never overlap a pod.

pod-128/power-pod-00.png, power-pod-01.png
    The pod on its own 128x128 canvas, like the mod's TSTURB (2 frames: 00 healthy, 01 damaged): the turbine and
    its socket's green ring and plate, no shadow. The damaged one is sooted with its window band dead, on an
    intact ring. The TS-angle piece is cut from the plant's canvas at ({org['iso'][0]}, {org['iso'][1]}), the window where the
    mod's tsturb-0000 matches the east pod on tspowr-0000, so it sits exactly where TSTURB sits now (socket
    centre at ({org['iso'][2][0]:.1f}, {org['iso'][2][1]:.1f}) on the 128 canvas). The RA-grid piece has its socket centre on the same spot.
    Top-left of the 128 canvas on the plant's canvas, per socket:
      TS angle: {fo('iso')}
      RA grid:  {fo('ra')}
    (for the west socket the window starts left of the plant's canvas; the pod itself stays inside it.)
pod-128/turning/power-pod-turn-00..23.png
    The same piece turning (00-11 healthy, 12-23 damaged), if you'd rather animate TSTURB.

previews/  the plant on its own; both states next to TS's; the mod's frames 0000 and 0036 next to the same loop
           frames; next to the Construction Yard, the Component Tower and a GDI wall run (RA grid); the house
           colour next to the yard's; the pod piece vs the mod's TSTURB (and on the middle socket vs the
           overlay); the build-up as a strip and a GIF against GTPOWRMK; the idle loop (healthy and damaged)
           against TS's own animations; one, two and three pods (healthy and damaged). The GIFs are built from
           this package's frames and overlays, drawn the way the game draws them.
src/       Python 3 (numpy, scipy, Pillow). hd.py is the renderer (walls2.py gives the light and materials).
           powr.py is the model, pmat.py the materials, pdamage.py the damage, panim.py the animations,
           pbuild.py the build-up.
           python3 pfinal.py states|piece|build iso|ra [ss]   makes the frames (ss 4 = supersampling used here)
           python3 pdeliver.py previews                        makes the previews
           python3 pcheck.py                                   checks the package
"""
    open(f'{PKG}/README.txt', 'w').write(txt)
    print(txt)


def src():
    d = f'{PKG}/src'
    os.makedirs(d, exist_ok=True)
    for f in ('hd.py', 'walls2.py', 'wnoise.py', 'powr.py', 'pmat.py', 'pdamage.py', 'prender.py', 'panim.py',
              'pbuild.py', 'pfinal.py', 'pdeliver.py', 'pcheck.py', 'ypreview.py'):
        shutil.copy(f'/home/claude/work/r/{f}', d)


def zipit(limit=29.5 * 2 ** 20):
    """one zip if it stays under the upload cap; otherwise the package in part 1 and loop/ in part 2, both
    unzipping into the same folder."""
    import zipfile
    base = os.path.dirname(PKG)
    name = os.path.basename(PKG)
    files = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(PKG) for f in fs)
    total = sum(os.path.getsize(f) for f in files)
    for old in [f for f in os.listdir(base) if f.startswith(name) and f.endswith('.zip')]:
        os.remove(os.path.join(base, old))
    if total < limit:
        parts = [(f'{name}.zip', files)]
    else:
        parts = [(f'{name}-part1.zip', [f for f in files if '/loop/' not in f]),
                 (f'{name}-part2-loop.zip', [f for f in files if '/loop/' in f])]
    for zname, fl in parts:
        with zipfile.ZipFile(os.path.join(base, zname), 'w', zipfile.ZIP_DEFLATED) as z:
            for f in fl:
                z.write(f, os.path.relpath(f, base))
        print(zname, '%.1f MiB' % (os.path.getsize(os.path.join(base, zname)) / 2 ** 20))


if __name__ == '__main__':
    what = sys.argv[1]
    if what in ('previews', 'all'):
        previews()
    if what in ('readme', 'all'):
        readme()
    if what in ('src', 'all'):
        src()
    if what in ('zip', 'all'):
        zipit()
