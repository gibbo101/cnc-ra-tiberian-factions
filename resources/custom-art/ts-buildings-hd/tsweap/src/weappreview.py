"""Extra previews for the War Factory package (bdeliver extra_previews), built from the package's own frames:
  layers-<view>.png             every layer on its own, then how they stack (idle, and with the door up)
  door-vs-original.gif          the door rolling up and down over the bay (bib, _1, _2, _D), next to TS's
  exit-and-jambs.png            where the exit and the door's jambs are, on both views (and on the mod's frame now)"""
import numpy as np
from PIL import Image, ImageDraw
import ypreview as P
import weap as M, weaprender as WR

DARK = (30, 30, 30, 255)
NM = 'war-factory'
ND = 9
V = {'iso': 'ts-angle', 'ra': 'ra-grid'}


def lay(pk, view, sub, name):
    return pk.fr(view, sub, f'{NM}-{name}')


def with_idle(pk, view, im, lv, t):
    for o in pk.s['overlays']:
        im.alpha_composite(pk.ov(view, o, t, lv))
    return im


def door_scene(pk, view, lv, k, t=None):
    """bib, building-bay, 1-under-door, 2-over-units, D-door k (a unit would go between _1 and _2), the idle overlays
    at t."""
    im = lay(pk, view, 'bib', f'bib-{lv:02d}')
    for sub, nm in (('building-bay', f'bay-{lv:02d}'), ('1-under-door', f'under-{lv:02d}'), ('2-over-units', f'over-{lv:02d}'),
                    ('D-door', f'door-{k:02d}')):                # one door for both states, as TS's
        im.alpha_composite(lay(pk, view, sub, nm))
    return with_idle(pk, view, im, lv, t) if t is not None else im


def ts_door(pk, lv, k, t=None):
    T = f"{pk.s['hand']}/ts-original"
    paths = [f'{T}/GTWEAPBB/frames/{lv:02d}.png', f'{T}/GTWEAP_1/frames/{lv:02d}.png', f'{T}/GTWEAP_2/frames/{lv:02d}.png',
             f'{T}/GTWEAP_D/frames/{k:02d}.png']
    if t is not None:
        for o in pk.s['overlays']:
            j = o['ts_frame'](t, lv)
            if j is not None:
                paths.append(f"{T}/{o['ts_shp']}/frames/{j:02d}.png")
    return pk.ts_canvas(paths)


def tile(im, w, h, z, title, sub=None):
    t = P.on_bg(im).resize((max(1, int(round(im.width * z))), max(1, int(round(im.height * z)))), Image.LANCZOS)
    c = Image.new('RGBA', (w, h), DARK)
    c.paste(t, ((w - t.width) // 2, 34 + (h - 34 - t.height) // 2))
    d = ImageDraw.Draw(c)
    d.text((6, 4), title, fill=(255, 255, 0, 255))
    if sub:
        d.text((6, 18), sub, fill=(220, 220, 220, 255))
    return c


def layers(pk, out):
    """per view: each layer alone (on the ground colour), then the stacks."""
    for view in ('iso', 'ra'):
        cr = lambda im: pk.crop(view, im)
        z = 0.5 if view == 'iso' else 0.62
        ims = [
            (lay(pk, view, 'bib', 'bib-00'), 'bib/ 00', 'GTWEAPBB: under everything'),
            (lay(pk, view, 'building', '00'), 'building/ 00', 'GTWEAP: the whole building, door shut'),
            (lay(pk, view, 'building-bay', 'bay-00'), 'building-bay/ 00', "the door bay (TSWEAP.ZIP's frames now)"),
            (lay(pk, view, '2-over-units', 'over-00'), '2-over-units/ 00', 'GTWEAP_2: the rest, over units'),
            (lay(pk, view, '1-under-door', 'under-00'), '1-under-door/ 00', 'GTWEAP_1: the bay with the door up'),
            (lay(pk, view, 'D-door', 'door-00'), 'D-door/ 00', 'GTWEAP_D: shut'),
            (lay(pk, view, 'D-door', 'door-04'), 'D-door/ 04', 'half way up'),
            (lay(pk, view, 'D-door', 'door-08'), 'D-door/ 08', 'rolled up into the roof'),
            (lay(pk, view, 'A-lamps', 'lamps-08'), 'A-lamps/ 08', 'GTWEAP_A: the five lamps'),
            (lay(pk, view, 'B-lamps', 'lamps-b-00'), 'B-lamps/ 00', 'GTWEAP_B: three roof lamps'),
            (lay(pk, view, 'C-fans', 'fans-00'), 'C-fans/ 00', 'GTWEAP_C: the two fans'),
        ]
        idle = pk.base(view, 0); idle = with_idle(pk, view, idle, 0, 8)
        up = door_scene(pk, view, 0, 8, t=8)
        shut = door_scene(pk, view, 0, 0)
        ref = pk.base(view, 0)
        diff = np.abs(np.array(shut).astype(int) - np.array(ref).astype(int)).max(axis=2)
        ims += [(idle, 'idle', 'bib + building + A + B + C'),
                (up, 'door up', 'bib + bay + 1 + [unit] + 2 + D 08 + A + B + C'),
                (shut, 'check', f'bib + bay + 1 + 2 + D 00 = bib + building ({(diff > 8).sum()} px differ)')]
        cw = int(round(cr(ims[0][0]).width * z))
        ch = int(round(cr(ims[0][0]).height * z)) + 36
        cols = 4
        rows = (len(ims) + cols - 1) // cols
        S = Image.new('RGBA', (cols * (cw + 8), rows * (ch + 8) + 30), DARK)
        P.label(S, f"War Factory, {V[view]}: the layers (each on its own), and how they stack", (6, 8))
        for n, (im, title, sub) in enumerate(ims):
            S.paste(tile(cr(im), cw, ch, z, title, sub), ((n % cols) * (cw + 8), 30 + (n // cols) * (ch + 8)))
        S.save(f'{out}/layers-{V[view]}.png')


def door_gif(pk, out):
    zg = pk.s.get('gif_zoom', 0.6)
    iso_c = lambda im: pk.crop('iso', im)
    ra_c = lambda im: pk.crop('ra', im)
    frs = []
    t = 0
    for lv in (0, 1):
        st = ('healthy', 'damaged')[lv]
        seq = [('idle', 0)] * 3 + [('door', k) for k in range(ND)] + [('door', ND - 1)] * 6 \
            + [('door', k) for k in range(ND - 1, -1, -1)] + [('idle', 0)] * 3
        for what, k in seq:
            if what == 'idle':
                ims = [pk.ts_building(lv, t), pk.scene('iso', lv, t), pk.scene('ra', lv, t)]
                sub = f'{st}: idle (bib + building + A + B + C)'
            else:
                ims = [ts_door(pk, lv, k, t), door_scene(pk, 'iso', lv, k, t), door_scene(pk, 'ra', lv, k, t)]
                sub = f'{st}: door {k:02d} (bib + bay + 1 + 2 + D, A + B + C)'
            frs.append(pk.three_up([iso_c(ims[0]), iso_c(ims[1]), ra_c(ims[2])],
                                   ('TS: GTWEAPBB + _1 + _2 + _D', 'HD, TS angle', 'HD, RA grid'), sub, z=zg))
            t += 1
    pk.gif(frs, f'{out}/door-vs-original.gif', 110)


def marks(view):
    """exit and jambs: (name, local x, y) at the floor -> canvas px."""
    d, b = M.P['door'], M.P['bay']
    pts = [('exit', d['x0'], (b['y'][0] + b['y'][1]) / 2.0), ('left jamb', d['x0'], b['y'][1]), ('right jamb', d['x0'], b['y'][0])]
    W, H = WR.canvas_of(view)
    v = WR.view(view, 1, win=(0, 0, W, H))
    out = []
    for name, x, y in pts:
        X, Y = M.to_world(np.array(x), np.array(y), WR.LAYOUT[view])
        px, py = v.project(float(X), float(Y), 0.0)
        out.append((name, px, py))
    return out


def draw_marks(im, pts, z, x0=0, y0=0):
    d = ImageDraw.Draw(im)
    for name, px, py in pts:
        sx, sy = (px - x0) * z, (py - y0) * z
        col = (255, 60, 255, 255) if name == 'exit' else (0, 255, 255, 255)
        d.line([(sx - 7, sy), (sx + 7, sy)], fill=col, width=2); d.line([(sx, sy - 7), (sx, sy + 7)], fill=col, width=2)
        d.text((sx + 6, sy + 4), f'{name} ({px:.1f}, {py:.1f})', fill=col)


def exit_marks(pk, out):
    rows = []
    # TS angle: the mod's frame now, our bay, our whole building
    box = (330, 210, 650, 420)
    z = 2
    pts = marks('iso')
    ims = [(Image.open(f"{pk.s['hand']}/in-mod/tsweap-0000.png").convert('RGBA'), 'in the mod now: tsweap-0000 (the door bay)'),
           (lay(pk, 'iso', 'building-bay', 'bay-00'), 'HD: building-bay/ 00'),
           (pk.base('iso', 0), 'HD: bib + building')]
    w, h = (box[2] - box[0]) * z, (box[3] - box[1]) * z
    R = Image.new('RGBA', (3 * (w + 8), h + 30), DARK)
    for n, (im, t) in enumerate(ims):
        c = P.on_bg(im.crop(box)).resize((w, h), Image.LANCZOS)
        draw_marks(c, pts, z, box[0], box[1])
        R.paste(c, (n * (w + 8), 30))
        P.label(R, t + f' ({z}x)', (n * (w + 8) + 6, 8))
    rows.append(R)
    # RA grid: the 3 x 4 plot as delivered, and the same frame cropped to a 3 x 3 plot (RA's own WEAP)
    z = 1.5
    pts0 = marks('ra')
    x0, y0, x1, y1 = WR.PLOT['ra']
    panels = []
    for rows_, top in ((4, 0), (3, 128)):
        im = P.on_bg(pk.base('ra', 0)).crop((0, top, 416, 512))
        d = ImageDraw.Draw(im)
        for i in range(4):
            d.line([(x0 + i * 128, 0), (x0 + i * 128, im.height - 1)], fill=(255, 255, 0, 160))
        for j in range(rows_ + 1):
            yy = min(j * 128, im.height - 1)
            d.line([(x0, yy), (x1 - 1, yy)], fill=(255, 255, 0, 160))
        im = im.resize((int(im.width * z), int(im.height * z)), Image.LANCZOS)
        pts = [(n, px, py - top) for n, px, py in pts0]
        draw_marks(im, pts, z)
        cx, cy = 208.0, im.height / z / 2.0
        txt = [f'3 x {rows_} plot: canvas 416 x {512 - top}' + ('' if not top else f' (y {top}-512 of the frames)'),
               f'plot x 16-400, y 0-{512 - top}, centre ({cx:.0f}, {cy:.0f})', 'from the plot centre, in leptons (2 per px):']
        txt += [f'  {n}: {2 * (px - cx):+.0f}, {2 * (py - cy):+.0f}' for n, px, py in pts]
        T = Image.new('RGBA', (im.width, im.height + 30 + 16 * len(txt) + 8), DARK)
        T.paste(im, (0, 30))
        P.label(T, f'RA grid ({z:g}x), as a 3 x {rows_} plot', (6, 8))
        for n, s in enumerate(txt):
            P.label(T, s, (6, im.height + 36 + 16 * n), fill=(255, 255, 255, 255))
        panels.append(T)
    R = Image.new('RGBA', (sum(p.width for p in panels) + 16, max(p.height for p in panels)), DARK)
    R.paste(panels[0], (0, 0)); R.paste(panels[1], (panels[0].width + 16, 0))
    rows.append(R)
    pk.stack(rows, 12).save(f'{out}/exit-and-jambs.png')


EXTRAS = [layers, door_gif, exit_marks]
