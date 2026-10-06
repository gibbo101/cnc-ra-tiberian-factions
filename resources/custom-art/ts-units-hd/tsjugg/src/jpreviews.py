"""
jpreviews.py - the Juggernaut package's previews, from its own frames:
    walk-east.gif, walk-south.gif   the walk, the mod's frames beside HD (15 steps, 3 ticks a step)
    deploy.gif                      the deploy, the mod's frames beside HD (2 ticks a frame), held at both ends
    turn.gif                        the deployed cabin turning through its 32 facings at rest, beside the mod's
    walk-8-facings.png              TS's sprite, the mod's frame and HD, walk step 0 in each facing
    titan-legs.png                  TS's sprite, HD and the HD Titan's leg frame, walk step 0 in each facing: the
                                    same legs (the Titan's canvas puts its ground 54 px lower; shifted to match)
    rest-8-facings.png, aim-8-facings.png   the deployed piece, the mod's frames beside HD
    scale.png                       next to the HD Titan and the HD harvester, as the game draws them
    shape-walker.png, shape-cabin.png, shape-base.png   TS's sprites as colour classes beside the model's, in TS's
                                    own camera (jshapecheck)

    python3 jpreviews.py PKG
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
from paths import HANDOFF

PKG = sys.argv[1]
PV = PKG + '/previews'
os.makedirs(PV, exist_ok=True)
HD = PKG + '/frames/tsjugg-%04d.png'
INMOD = HANDOFF + '/04-TSJUGG/in-mod/tsjugg/frames/tsjugg-%04d.png'
TS = HANDOFF + '/04-TSJUGG/ts-original/JUGGER/frames/jugger-%03d.png'
BG = (96, 108, 72, 255)
DIRS = ['N', 'NW', 'W', 'SW', 'S', 'SE', 'E', 'NE']


def on_bg(p, crop):
    im = Image.open(p).convert('RGBA')
    b = Image.new('RGBA', im.size, BG); b.alpha_composite(im)
    return b.crop(crop).convert('RGB')


def pair(k, crop, scale, label):
    tiles = []
    for lab, fmt in (('in-mod', INMOD), ('HD', HD)):
        b = on_bg(fmt % k, crop)
        b = b.resize((round(b.size[0] * scale), round(b.size[1] * scale)), Image.LANCZOS)
        t = Image.new('RGB', (b.size[0], b.size[1] + 16), (28, 30, 34)); t.paste(b, (0, 16))
        ImageDraw.Draw(t).text((4, 2), '%s  %s' % (lab, label), fill=(230, 220, 160))
        tiles.append(t)
    w, h = tiles[0].size
    out = Image.new('RGB', (2 * w + 6, h), (20, 22, 26))
    out.paste(tiles[0], (0, 0)); out.paste(tiles[1], (w + 6, 0))
    return out


def gif(name, ks, crop, scale, ms, hold=None):
    fr = [pair(k, crop, scale, 'frame %d' % k).convert('P', palette=Image.ADAPTIVE, colors=255) for k in ks]
    d = [hold.get(k, ms) if hold else ms for k in ks]
    fr[0].save(PV + '/' + name, save_all=True, append_images=fr[1:], duration=d, loop=0, disposal=1)


def sheet(name, ks, labels, crop, scale=0.75, cols=4):
    tiles = [pair(k, crop, scale, lab) for k, lab in zip(ks, labels)]
    W, H = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    out = Image.new('RGB', (cols * (W + 8) + 8, rows * (H + 8) + 8), (20, 22, 26))
    for i, t in enumerate(tiles):
        out.paste(t, (8 + (i % cols) * (W + 8), 8 + (i // cols) * (H + 8)))
    out.save(PV + '/' + name)


WALK_CROP = (40, 60, 420, 390)
gif('walk-east.gif', range(90, 105), WALK_CROP, 0.7, 200)
gif('walk-south.gif', range(60, 75), WALK_CROP, 0.7, 200)
gif('deploy.gif', range(184, 202), (20, 90, 428, 400), 0.7, 133, hold={184: 700, 201: 700})
gif('turn.gif', range(120, 152), (20, 30, 428, 390), 0.6, 100)
sheet('rest-8-facings.png', [120 + 4 * f for f in range(8)], DIRS, (20, 30, 428, 390))
sheet('aim-8-facings.png', [152 + 4 * f for f in range(8)], DIRS, (20, 0, 428, 390))

# walk step 0 in each facing: TS's sprite (scaled as the mod draws it), the mod's frame, HD
K, DX, DY = 6.33, -76.72, 9.33                  # TS px -> the mod's walk canvas
tiles = []
for f in range(8):
    cw = (8 - f) % 8
    ts = Image.open(TS % (cw * 15)).convert('RGBA')
    big = Image.new('RGBA', (448, 448), (0, 0, 0, 0))
    up = ts.resize((round(ts.size[0] * K), round(ts.size[1] * K)), Image.NEAREST)
    big.paste(up, (round(DX), round(DY)), up)
    row = []
    for lab, im in (("TS's sprite", big), ('in-mod', Image.open(INMOD % (f * 15)).convert('RGBA')),
                    ('HD', Image.open(HD % (f * 15)).convert('RGBA'))):
        b = Image.new('RGBA', im.size, BG); b.alpha_composite(im)
        b = b.crop(WALK_CROP).convert('RGB').resize((228, 198), Image.LANCZOS)
        t = Image.new('RGB', (228, 214), (28, 30, 34)); t.paste(b, (0, 16))
        ImageDraw.Draw(t).text((4, 2), '%s  %s' % (lab, DIRS[f]), fill=(230, 220, 160))
        row.append(t)
    r = Image.new('RGB', (3 * 228 + 8, 214), (20, 22, 26))
    for i, t in enumerate(row):
        r.paste(t, (i * 232, 0))
    tiles.append(r)
W, H = tiles[0].size
out = Image.new('RGB', (2 * (W + 8) + 8, 4 * (H + 8) + 8), (20, 22, 26))
for i, t in enumerate(tiles):
    out.paste(t, (8 + (i % 2) * (W + 8), 8 + (i // 2) * (H + 8)))
out.save(PV + '/walk-8-facings.png')

# scale: as the game draws them (this canvas and the Titan's at two thirds: 8 px a classic pixel against 5.33)
TITAN = os.environ.get('TITAN_FRAMES', os.path.join(HANDOFF, '..', 'ts-titan-hd', 'frames')) + '/tstitn-%04d.png'      # the HD Titan's frames, for scale.png
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'


def layered(paths):
    out = None
    for p in paths:
        im = Image.open(p).convert('RGBA')
        out = im if out is None else Image.alpha_composite(out, im)
    return out


items = [('TS Harvester (HD)', layered([HARV % 24]), 1.0),
         ('Titan (HD)', layered([TITAN % 72, TITAN % 120]), 2 / 3),
         ('Juggernaut walking (HD)', layered([HD % 90]), 2 / 3),
         ('Juggernaut deployed (HD)', layered([HD % 144]), 2 / 3)]
crops = []
for lab, im, sc in items:
    if sc != 1.0:
        im = im.resize((round(im.size[0] * sc), round(im.size[1] * sc)), Image.LANCZOS)
    a = np.array(im); ys, xs = np.nonzero(a[..., 3] > 0)
    crops.append((lab, im.crop((max(xs.min() - 6, 0), 0, min(xs.max() + 7, im.size[0]), im.size[1]))))
gap = 24; Hs = 300; ground = 250
Wt = sum(c.size[0] for _, c in crops) + gap * (len(crops) + 1)
out = Image.new('RGBA', (Wt, Hs), BG)
d = ImageDraw.Draw(out)
x = gap
for lab, im in crops:
    a = np.array(im)
    solid = (a[..., 3] > 250) & (a[..., :3].max(-1) > 30)
    low = np.nonzero(solid.any(1))[0].max()
    out.alpha_composite(im, (x, ground - low))
    d.text((x + im.size[0] // 2 - 55, Hs - 20), lab, fill=(240, 232, 190))
    x += im.size[0] + gap
out.convert('RGB').save(PV + '/scale.png')

# the Titan's legs: TS's sprite, HD, the HD Titan's leg frame (its step 0, the same facing; its canvas has the ground
# point at (224, 364) against this one's (224, 310), so it is drawn 54 px higher)
tiles = []
for f in range(8):
    cw = (8 - f) % 8
    ts = Image.open(TS % (cw * 15)).convert('RGBA')
    big = Image.new('RGBA', (448, 448), (0, 0, 0, 0))
    up = ts.resize((round(ts.size[0] * K), round(ts.size[1] * K)), Image.NEAREST)
    big.paste(up, (round(DX), round(DY)), up)
    ti = Image.open(TITAN % (f * 12)).convert('RGBA')
    tsh = Image.new('RGBA', ti.size, (0, 0, 0, 0)); tsh.paste(ti, (0, -54), ti)
    row = []
    for lab, im in (("TS's sprite", big), ('HD', Image.open(HD % (f * 15)).convert('RGBA')), ("HD Titan's legs", tsh)):
        b = Image.new('RGBA', im.size, BG); b.alpha_composite(im)
        b = b.crop(WALK_CROP).convert('RGB').resize((228, 198), Image.LANCZOS)
        t = Image.new('RGB', (228, 214), (28, 30, 34)); t.paste(b, (0, 16))
        ImageDraw.Draw(t).text((4, 2), '%s  %s' % (lab, DIRS[f]), fill=(230, 220, 160))
        row.append(t)
    r = Image.new('RGB', (3 * 228 + 8, 214), (20, 22, 26))
    for i, t in enumerate(row):
        r.paste(t, (i * 232, 0))
    tiles.append(r)
W, H = tiles[0].size
out = Image.new('RGB', (2 * (W + 8) + 8, 4 * (H + 8) + 8), (20, 22, 26))
for i, t in enumerate(tiles):
    out.paste(t, (8 + (i % 2) * (W + 8), 8 + (i // 2) * (H + 8)))
out.save(PV + '/titan-legs.png')
print('previews done')
