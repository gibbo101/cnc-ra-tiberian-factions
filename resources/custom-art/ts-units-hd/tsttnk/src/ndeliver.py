"""
ndeliver.py - render, preview, check and package a voxel unit that is NEW to the mod (no in-mod frames yet), from a
small spec module (see bggyspec.py).  vdeliver.py's job for units already in the mod; here TS's own voxels, drawn as
they are (tsvox.py: every voxel a splat in its palette colour, lit by its TS normal, through the same camera), stand
beside the HD frames in the previews, and the scale preview adds the unit to the Devil's Tongue's (the HD harvester and
the Devil's Tongue, as the game draws them).

A spec module defines:
  NAME, FRAMES, CANVAS          the frame prefix ('tsbggy'), the frame count, the canvas (W, H)
  load() / frame(u, k, ss, sky) the unit and one HD frame (RGBA image, trim image)
  ref_frame(u, k)               TS's voxels drawn as they are for frame k (RGBA image)
  NO_SHADOW                     frame ranges drawn without a shadow, e.g. [(32, 63)]
  CROP                          the crop round the unit for the sheets and GIFs
  SHEETS                        [(file name, [(label, [frames to lay over each other])...])]: TS's voxels beside HD
  GIFS                          [(file name, [(label, [frames])...], ms per frame)]
  LINEUP                        (file name, [(label, frame list)]) the unit's frames added to the Devil's Tongue's scale preview
  muzzle_text()                 optional: muzzle.txt
  GLB(path), GLB_NAME           the .glb
  SRC                           the unit's own source files to package (besides the shared ones)

    python3 ndeliver.py SPEC render PART N [ss] [sky]     (PKG=folder; frames already there are kept)
    python3 ndeliver.py SPEC ref PKGREF                   TS's voxels for every frame (PKGREF/<name>-NNNN.png)
    python3 ndeliver.py SPEC previews PKG PKGREF
    python3 ndeliver.py SPEC check PKG PKGREF
"""
import os, sys, time, importlib
import numpy as np
from PIL import Image, ImageDraw

BG = (96, 108, 72, 255)
HERE = os.path.dirname(os.path.abspath(__file__))
SCALE_BASE = 'examples/devils-tongue/previews/scale.png'      # in the hand-off: the HD harvester and the Devil's Tongue


def on_bg(im):
    b = Image.new('RGBA', im.size, BG); b.alpha_composite(im)
    return b


def label(im, text, xy=(4, 2), col=(230, 220, 160)):
    ImageDraw.Draw(im).text(xy, text, fill=col)
    return im


def layered(fmt, frames):
    out = None
    for k in frames:
        im = Image.open(fmt % k).convert('RGBA')
        if out is None:
            out = Image.new('RGBA', im.size, (0, 0, 0, 0))
        out.alpha_composite(im)
    return out


def render(spec, part, n, ss=4, sky=True, pkg=None):
    from frameio import save
    pkg = pkg or os.environ.get('PKG')
    os.makedirs(pkg + '/frames', exist_ok=True)
    u = spec.load()
    for k in list(range(spec.FRAMES))[part::n]:
        out = '%s/frames/%s-%04d.png' % (pkg, spec.NAME, k)
        if os.path.exists(out) and os.path.exists(out[:-4] + '-trim.png'):
            continue
        t0 = time.time()
        img, trim = spec.frame(u, k, ss, sky)
        save(img, trim, out)
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
    print('done', flush=True)


def ref(spec, out):
    os.makedirs(out, exist_ok=True)
    u = spec.load()
    for k in range(spec.FRAMES):
        spec.ref_frame(u, k).save('%s/%s-%04d.png' % (out, spec.NAME, k))
    print('ref done')


def pair_tile(spec, hd_fmt, ref_fmt, frames, text):
    crop = spec.CROP
    W, H = crop[2] - crop[0], crop[3] - crop[1]
    t = Image.new('RGB', (2 * W + 6, H + 16), (28, 30, 34))
    for j, (lab, fmt) in enumerate((("TS's voxels", ref_fmt), ('HD', hd_fmt))):
        t.paste(on_bg(layered(fmt, frames)).crop(crop).convert('RGB'), (j * (W + 6), 16))
        label(t, '%s  %s' % (lab, text), (j * (W + 6) + 4, 2))
    return t


def sheet(spec, hd_fmt, ref_fmt, items, name, scale=1.0, cols=2):
    tiles = [pair_tile(spec, hd_fmt, ref_fmt, frames, lab) for lab, frames in items]
    if scale != 1.0:
        tiles = [t.resize((int(t.size[0] * scale), int(t.size[1] * scale)), Image.LANCZOS) for t in tiles]
    Wt, Ht = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    out = Image.new('RGB', (cols * (Wt + 8) + 8, rows * (Ht + 8) + 8), (20, 22, 26))
    for i, t in enumerate(tiles):
        out.paste(t, (8 + (i % cols) * (Wt + 8), 8 + (i // cols) * (Ht + 8)))
    out.save(name)


def gif(spec, hd_fmt, ref_fmt, seq, name, scale=1.0, ms=120):
    out = []
    for lab, frames in seq:
        t = pair_tile(spec, hd_fmt, ref_fmt, frames, lab)
        if scale != 1.0:
            t = t.resize((int(t.size[0] * scale), int(t.size[1] * scale)), Image.LANCZOS)
        out.append(t)
    # one palette for the whole GIF, so the colours don't flicker from frame to frame
    W, H = out[0].size
    strip = Image.new('RGB', (W, H * len(out)))
    for i, t in enumerate(out):
        strip.paste(t, (0, i * H))
    pal_img = strip.quantize(colors=255, method=Image.MEDIANCUT)
    fr = [t.quantize(palette=pal_img, dither=Image.NONE) for t in out]
    fr[0].save(name, save_all=True, append_images=fr[1:], duration=int(ms), loop=0, disposal=1)


def lineup_onto(base_path, items, name, ground=220, gap=24):
    """add units to a scale preview (the Devil's Tongue's: units on one ground line at y 220, labels at the bottom), each
    item (label, RGBA image at the size the game draws it)."""
    base = Image.open(base_path).convert('RGBA')
    H = base.size[1]
    crops = []
    for lab, im in items:
        a = np.array(im)
        ys, xs = np.nonzero(a[..., 3] > 0)
        crops.append((lab, im.crop((max(xs.min() - 6, 0), 0, min(xs.max() + 7, im.size[0]), im.size[1]))))
    W = base.size[0] + sum(im.size[0] for _, im in crops) + gap * len(crops)
    out = Image.new('RGBA', (W, H), BG)
    out.paste(base, (0, 0))
    d = ImageDraw.Draw(out)
    x = base.size[0]
    for lab, im in crops:
        w, h = im.size
        a = np.array(im)
        solid = (a[..., 3] > 250) & (a[..., :3].max(-1) > 30)
        low = np.nonzero(solid.any(1))[0].max()
        out.alpha_composite(im, (x, ground - low))
        tw = d.textlength(lab)
        d.text((x + w // 2 - tw / 2, H - 20), lab, fill=(240, 232, 190))
        x += w + gap
    out.convert('RGB').save(name)


def previews(spec, pkg, ref_dir):
    from paths import HANDOFF
    fmt = '%s/frames/%s-%%04d.png' % (pkg, spec.NAME)
    rfmt = '%s/%s-%%04d.png' % (ref_dir, spec.NAME)
    pv = pkg + '/previews'
    os.makedirs(pv, exist_ok=True)
    for name, items in spec.SHEETS:
        sheet(spec, fmt, rfmt, items, pv + '/' + name)
    for name, seq, ms in getattr(spec, 'GIFS', []):
        gif(spec, fmt, rfmt, seq, pv + '/' + name, ms=ms)
    name, items = spec.LINEUP
    ims = []
    for lab, frames in items:
        im = layered(fmt, frames)
        ims.append((lab, im.resize((round(im.size[0] * 2 / 3), round(im.size[1] * 2 / 3)), Image.LANCZOS)))
    lineup_onto(os.path.join(HANDOFF, getattr(spec, 'SCALE_BASE', SCALE_BASE)), ims, pv + '/' + name)
    print('previews done')


def check(spec, pkg, ref_dir):
    """every frame and trim on the canvas, trims only on house green, the house colour pure green, the shadow at alpha
    >= 128 where the frame carries one; and the HD silhouette against TS's voxels drawn as they are."""
    ns = set()
    for a, b in getattr(spec, 'NO_SHADOW', []):
        ns |= set(range(a, b + 1))
    W, H = spec.CANVAS
    bad = []; ious = []; dlow = []; dtop = []; edge = []
    for k in range(spec.FRAMES):
        p = '%s/frames/%s-%04d.png' % (pkg, spec.NAME, k); t = p[:-4] + '-trim.png'
        if not (os.path.exists(p) and os.path.exists(t)):
            bad.append((k, 'missing')); continue
        a = np.array(Image.open(p).convert('RGBA')).astype(int); tr = np.array(Image.open(t))
        if a.shape != (H, W, 4) or tr.shape != (H, W):
            bad.append((k, 'size'))
        full = (tr == 255) & (a[..., 3] == 255)
        if full.any() and (a[full][:, 0].max() > 0 or a[full][:, 2].max() > 0):
            bad.append((k, 'house not pure green'))
        if ((tr > 0) & (a[..., 3] < 128)).any():
            bad.append((k, 'trim outside the unit'))
        dark = (a[..., :3].max(-1) < 8) & (a[..., 3] > 0) & (a[..., 3] < 250)
        # a shadow lies off the unit: dark see-through pixels more than 2 px from its opaque body (the antialiased
        # edges of its own black parts don't count)
        from scipy import ndimage
        off = ndimage.distance_transform_edt(a[..., 3] < 250) > 2.0
        if k not in ns:
            if not (dark & off).any() or a[..., 3][dark & off].max() < 128:
                bad.append((k, 'shadow alpha'))
        elif (dark & off & (a[..., 3] > 160)).sum() > 50:
            bad.append((k, 'shadow on a no-shadow frame'))
        al = a[..., 3]
        edge.append(max(al[:3].max(), al[-3:].max(), al[:, :3].max(), al[:, -3:].max()))
        if edge[-1] >= 250:
            bad.append((k, 'the unit reaches the canvas edge'))
        r = np.array(Image.open('%s/%s-%04d.png' % (ref_dir, spec.NAME, k)).convert('RGBA'))[..., 3] > 0
        sa = al > 250
        if sa.any() and r.any():
            ious.append((sa & r).sum() / max((sa | r).sum(), 1))
            ya = np.nonzero(sa.any(1))[0]; yb = np.nonzero(r.any(1))[0]
            dlow.append(ya.max() - yb.max()); dtop.append(ya.min() - yb.min())
    print('frames checked: %d;  problems:' % spec.FRAMES, bad[:20] if bad else 'none', '(%d)' % len(bad))
    print('highest alpha within 3 px of the canvas edge: %d' % max(edge))
    if ious:
        print("silhouette overlap with TS's voxels: mean %.3f (min %.3f, max %.3f)" % (np.mean(ious), min(ious), max(ious)))
        print("lowest solid pixel, HD minus TS's voxels: mean %.1f (min %d, max %d)" % (np.mean(dlow), min(dlow), max(dlow)))
        print("highest solid pixel, HD minus TS's voxels: mean %.1f (min %d, max %d)" % (np.mean(dtop), min(dtop), max(dtop)))
    return bad, ious


if __name__ == '__main__':
    sys.path.insert(0, os.getcwd())
    spec = importlib.import_module(sys.argv[1])
    cmd = sys.argv[2]
    if cmd == 'render':
        render(spec, int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]) if len(sys.argv) > 5 else 4,
               bool(int(sys.argv[6])) if len(sys.argv) > 6 else True)
    elif cmd == 'ref':
        ref(spec, sys.argv[3])
    elif cmd == 'previews':
        previews(spec, sys.argv[3], sys.argv[4])
    elif cmd == 'check':
        check(spec, sys.argv[3], sys.argv[4])


def muzzle_sheet(spec, pkg, cols, out, zoom=3, half=(65, 55)):
    """the muzzle points (cols: [(label, unit-frame point, (r, g, b))]) marked on every 4th facing, zoomed round them."""
    import nvox
    tiles = []
    for k in range(0, 32, 4):
        im = on_bg(Image.open('%s/frames/%s-%04d.png' % (pkg, spec.NAME, k)).convert('RGBA'))
        pts = [(nvox.project(spec.CFG, p, k), c) for _, p, c in cols]
        cx = np.mean([p[0][0] for p in pts]); cy = np.mean([p[0][1] for p in pts])
        box = (int(cx - half[0]), int(cy - half[1]), int(cx + half[0]), int(cy + half[1]))
        pad = max(half) + 4
        big = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), im.getpixel((0, 0)))
        big.paste(im, (pad, pad))
        c = big.crop(tuple(v + pad for v in box)).resize(((box[2] - box[0]) * zoom, (box[3] - box[1]) * zoom), Image.NEAREST)
        d = ImageDraw.Draw(c)
        for (x, y), colr in pts:
            X, Y = (x - box[0]) * zoom, (y - box[1]) * zoom
            d.ellipse((X - 4, Y - 4, X + 4, Y + 4), outline=colr, width=2)
        d.text((4, 4), 'facing %d' % k, fill=(255, 255, 255))
        tiles.append(c.convert('RGB'))
    W, H = tiles[0].size
    sheet_ = Image.new('RGB', (W * 4, H * 2))
    for i, t in enumerate(tiles):
        sheet_.paste(t, ((i % 4) * W, (i // 4) * H))
    d = ImageDraw.Draw(sheet_)
    x = 8
    for lab, _, colr in cols:
        d.text((x, H * 2 - 14), lab, fill=colr); x += 8 * len(lab) + 24
    sheet_.save(out)
    return sheet_.size
