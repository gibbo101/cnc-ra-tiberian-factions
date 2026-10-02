"""the Mobile EMP Cannon's blast in HD (TSMEMPFX: 12 frames on the mod's 1152 x 576 canvas, played once at the unit's
centre on the ground; no house colour).

Each HD frame is TS's own frame (Firestorm's MEMPFX, ANIM.PAL), drawn again at the canvas's resolution:
- the ring's shape is TS's, pixel for pixel in place (TS px x 4 at canvas (16, 10), where in-mod/ has it), its stepped
  outline smoothed into a clean antialiased edge;
- its colours are TS's 12 (four lavenders, four maroons, a cream, two oranges, white), each streak and speck where TS
  has it: TS's pixels of each colour family (maroon, orange, lavender, cream, white) are redrawn as one shape with
  rounded, antialiased edges instead of 4 x 4 blocks (at every point the family whose smoothed share is largest wins),
  and within a family the shade runs smoothly between TS's own shades;
- a fine grain through the colour, long along x as TS's streaks are (as the units' paint carries a grain).
Nothing is added that TS's frame does not have: no glow, no new sparks.

    python3 mempfx.py OUTDIR [k,k,...]          writes OUTDIR/fx/tsmempfx-%04d.png (+ -trim.png, all black)
    python3 mempfx.py OUTDIR previews           the blast's previews from OUTDIR/fx into OUTDIR/previews
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from paths import HANDOFF

TS = HANDOFF + '/13-TSMEMP/ts-original/MEMPFX/frames/mempfx-%03d.png'
INMOD = HANDOFF + '/13-TSMEMP/in-mod/tsmempfx/frames/tsmempfx-%04d.png'
CANVAS = (1152, 576)
SCALE = 4                    # canvas px per TS px, as in-mod/ has it
OFF = (16, 10)               # where TS's frame sits on the canvas (in-mod/'s place: overlap 0.99)
N = 12
SS = 2

# TS's colours (ANIM.PAL as the frames decode), darkest to lightest within each family
MAROON = np.array([(80, 16, 8), (85, 20, 8), (89, 20, 8), (93, 20, 8)], float)
ORANGE = np.array([(202, 105, 32), (202, 109, 36)], float)
LAVENDER = np.array([(137, 97, 255), (157, 109, 255), (174, 121, 255), (190, 137, 255)], float)
CREAM = np.array([222, 194, 145], float)
WHITE = np.array([255, 255, 255], float)
FAMILIES = {'maroon': MAROON, 'orange': ORANGE, 'lavender': LAVENDER, 'cream': CREAM[None], 'white': WHITE[None]}


def classify(a):
    """TS's frame -> a family index per pixel (-1 empty): 0 maroon, 1 orange, 2 lavender, 3 cream, 4 white."""
    rgb = a[..., :3].astype(float)
    out = np.full(a.shape[:2], -1, int)
    for i, name in enumerate(['maroon', 'orange', 'lavender', 'cream', 'white']):
        for c in FAMILIES[name]:
            out[(np.abs(rgb - c).sum(-1) < 6) & (a[..., 3] > 0)] = i
    if ((a[..., 3] > 0) & (out < 0)).any():
        raise ValueError('a colour outside TS\'s 12')
    return out


def to_canvas(m, order=1):
    """a TS-px map onto the supersampled canvas grid (TS px centres at OFF + (i + 0.5) x SCALE)."""
    H, W = CANVAS[1] * SS, CANVAS[0] * SS
    ys = ((np.arange(H) + 0.5) / SS - OFF[1]) / SCALE - 0.5
    xs = ((np.arange(W) + 0.5) / SS - OFF[0]) / SCALE - 0.5
    Y, X = np.meshgrid(ys, xs, indexing='ij')
    return ndimage.map_coordinates(m.astype(float), [Y, X], order=order, mode='constant', cval=0.0)


def frame(k, sig=0.45, sig_a=0.55, grain=0.06):
    """TS's frame drawn again at the canvas's resolution with its own layout: each colour family's TS pixels as a
    shape with rounded, antialiased edges (the family whose smoothed share is largest wins each point), the colour
    within a family TS's own shade there."""
    a = np.array(Image.open(TS % k).convert('RGBA'))
    fam = classify(a)
    solid = (fam >= 0).astype(float)
    alpha = np.clip((to_canvas(ndimage.gaussian_filter(solid, sig_a)) - 0.5) / (0.5 / (SCALE * SS) * 4.0) + 0.5, 0, 1)
    share = np.stack([to_canvas(ndimage.gaussian_filter((fam == i).astype(float), sig)) for i in range(5)])
    win = share.argmax(0)
    # TS's shade within each family, carried from the nearest TS pixel of that family
    rgbts = a[..., :3].astype(float)
    rgb = np.zeros(alpha.shape + (3,))
    for i in range(5):
        m = fam == i
        if not m.any():
            continue
        # fill the family's colour outwards so every point has the nearest TS pixel's shade of it
        idx = ndimage.distance_transform_edt(~m, return_distances=False, return_indices=True)
        filled = rgbts[idx[0], idx[1]]
        ch = np.stack([to_canvas(filled[..., c], order=1) for c in range(3)], -1)
        sel = win == i
        rgb[sel] = ch[sel]
    # a fine grain through the colour, long along x as TS's streaks are (as the units' paint carries a grain)
    rng = np.random.default_rng(700 + k)
    g = ndimage.gaussian_filter(rng.standard_normal(alpha.shape), (0.6 * SS, 2.0 * SS))
    rgb = rgb * (1 + grain * g / g.std())[..., None]
    A = alpha.reshape(CANVAS[1], SS, CANVAS[0], SS).mean((1, 3))
    C = (rgb * alpha[..., None]).reshape(CANVAS[1], SS, CANVAS[0], SS, 3).mean((1, 3))
    C = C / np.maximum(A, 1e-6)[..., None]
    out = np.zeros((CANVAS[1], CANVAS[0], 4), np.uint8)
    out[..., :3] = np.clip(np.round(C), 0, 255)
    out[..., 3] = np.clip(np.round(A * 255), 0, 255)
    out[out[..., 3] == 0, :3] = 0
    return Image.fromarray(out, 'RGBA')



BG = (96, 108, 72, 255)


def on_bg(im):
    b = Image.new('RGBA', im.size, BG); b.alpha_composite(im)
    return b


def previews(out):
    pv = os.path.join(out, 'previews'); os.makedirs(pv, exist_ok=True)
    hd = os.path.join(out, 'fx', 'tsmempfx-%04d.png')
    # the blast played: in-mod beside HD
    tiles = []
    for k in range(N):
        t = Image.new('RGB', (2 * CANVAS[0] + 24, CANVAS[1] + 40), (28, 30, 34))
        for j, (lab, fmt) in enumerate((('in-mod', INMOD), ('HD', hd))):
            t.paste(on_bg(Image.open(fmt % k).convert('RGBA')).convert('RGB'), (j * (CANVAS[0] + 24), 40))
            ImageDraw.Draw(t).text((j * (CANVAS[0] + 24) + 8, 12), '%s  frame %d' % (lab, k), fill=(230, 220, 160))
        tiles.append(t)
    small = [t.resize((t.size[0] * 9 // 20, t.size[1] * 9 // 20), Image.LANCZOS) for t in tiles]
    pal = [s.convert('P', palette=Image.ADAPTIVE, colors=255) for s in small]
    pal[0].save(os.path.join(pv, 'blast.gif'), save_all=True, append_images=pal[1:] + [pal[-1]] * 3, duration=100,
                loop=0, disposal=1)
    # a close look: frame 6's right-hand side at full size, in-mod above HD
    crop = (700, 100, 1152, 400)
    w, h = crop[2] - crop[0], crop[3] - crop[1]
    c = Image.new('RGB', (w, 2 * h + 60), (28, 30, 34))
    for j, (lab, fmt) in enumerate((('in-mod', INMOD), ('HD', hd))):
        c.paste(on_bg(Image.open(fmt % 6).convert('RGBA')).crop(crop).convert('RGB'), (0, 30 + j * (h + 30)))
        ImageDraw.Draw(c).text((8, 10 + j * (h + 30)), '%s  frame 6, full size' % lab, fill=(230, 220, 160))
    c.save(os.path.join(pv, 'blast-close.png'))
    # every frame, in-mod beside HD, at a third
    th = []
    for k in range(N):
        t = Image.new('RGB', (2 * (CANVAS[0] // 3) + 8, CANVAS[1] // 3 + 18), (28, 30, 34))
        for j, (lab, fmt) in enumerate((('in-mod', INMOD), ('HD', hd))):
            im = on_bg(Image.open(fmt % k).convert('RGBA')).convert('RGB')
            t.paste(im.resize((CANVAS[0] // 3, CANVAS[1] // 3), Image.LANCZOS), (j * (CANVAS[0] // 3 + 8), 18))
            ImageDraw.Draw(t).text((j * (CANVAS[0] // 3 + 8) + 4, 3), '%s  frame %d' % (lab, k), fill=(230, 220, 160))
        th.append(t)
    W, H = th[0].size
    sheet = Image.new('RGB', (2 * W + 24, 6 * H + 56), (20, 22, 26))
    for k, t in enumerate(th):
        sheet.paste(t, (8 + (k % 2) * (W + 8), 8 + (k // 2) * (H + 8)))
    sheet.save(os.path.join(pv, 'blast-frames.png'))
    print('previews done')


if __name__ == '__main__':
    out = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == 'previews':
        previews(out)
        sys.exit()
    ks = [int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else range(N)
    os.makedirs(os.path.join(out, 'fx'), exist_ok=True)
    for k in ks:
        im = frame(k)
        p = os.path.join(out, 'fx', 'tsmempfx-%04d.png' % k)
        im.save(p)
        Image.new('L', CANVAS, 0).save(p[:-4] + '-trim.png')
        print('fx frame', k, flush=True)
