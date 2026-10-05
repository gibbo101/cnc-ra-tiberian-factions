"""
vdeliver.py - render, preview, check and package a voxel unit from a small spec module (see t4spec.py, apcspec.py).

A spec module defines:
  NAME          the mod's frame prefix ('ts4tnk'), FRAMES (count), CANVAS (W, H), INMOD (pattern with %04d)
  load()        -> whatever frame() needs (voxrender.Units)
  frame(u, k, ss, sky) -> (RGBA image, trim image)
  NO_SHADOW     frame ranges drawn without a shadow, e.g. [(32, 63)]
  SHEETS        [(file name, [(label, [frame numbers to lay over each other])...])]: in-mod beside HD
  TURN          optional (file name, [frame numbers to lay over each other] for each of the 32 facings as a function)
  LINEUP        (file name, [(label, path pattern or None for HD, frame list, scale)]) for the scale preview
  CROP          the crop round the unit for the sheets
  GLB           optional function(path) writing the .glb
  SRC           the unit's own source files to package (besides the shared ones)

    python3 vdeliver.py SPEC render PART N [ss] [sky]
    python3 vdeliver.py SPEC previews PKG
    python3 vdeliver.py SPEC check PKG
"""
import os, sys, time, importlib, shutil, re
import numpy as np
from PIL import Image, ImageDraw

BG = (96, 108, 72, 255)
SHARED = ['vxlunit.py', 'voxrender.py', 'vexport.py', 'vdeliver.py', 'vcheck.py', 'tsnormals.py', 'vplace.py', 'rc.py', 'rcrender.py',
          'rcexport.py', 'frameio.py', 'glbcheck.py']
RENDERER = ['hd.py', 'walls2.py', 'wnoise.py', 'export3d.py', 'vxl.py']


def on_bg(im):
    b = Image.new('RGBA', im.size, BG); b.alpha_composite(im)
    return b


def label(im, text, xy=(4, 2), col=(230, 220, 160)):
    ImageDraw.Draw(im).text(xy, text, fill=col)
    return im


def layered(fmt, frames):
    """frames laid over each other: each an index, or (index, dx, dy) to draw it shifted (a turret's seat)."""
    out = None
    for item in frames:
        if isinstance(item, str):                       # a file of its own (e.g. a reference's turret frame)
            k, dx, dy, path = None, 0, 0, item
        else:
            k, dx, dy = (item, 0, 0) if isinstance(item, (int, np.integer)) else item
            path = fmt % k
        im = Image.open(path).convert('RGBA')
        if out is None:
            out = Image.new('RGBA', im.size, (0, 0, 0, 0))
        if dx or dy:
            sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); sh.paste(im, (int(round(dx)), int(round(dy)))); im = sh
        out.alpha_composite(im)
    return out


def render(spec, part, n, ss=4, sky=True, pkg=None):
    pkg = pkg or os.environ.get('PKG')
    os.makedirs(pkg + '/frames', exist_ok=True)
    u = spec.load()
    for k in list(range(spec.FRAMES))[part::n]:
        out = '%s/frames/%s-%04d.png' % (pkg, spec.NAME, k)
        if os.path.exists(out) and os.path.exists(out[:-4] + '-trim.png'):
            continue
        t0 = time.time()
        img, trim = spec.frame(u, k, ss, sky)
        from frameio import save
        save(img, trim, out)
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
    print('done', flush=True)


def pair_tile(spec, hd_fmt, frames, text):
    crop = spec.CROP
    W, H = crop[2] - crop[0], crop[3] - crop[1]
    t = Image.new('RGB', (2 * W + 6, H + 16), (28, 30, 34))
    for j, (lab, fmt) in enumerate((('in-mod', spec.INMOD), ('HD', hd_fmt))):
        t.paste(on_bg(layered(fmt, frames)).crop(crop).convert('RGB'), (j * (W + 6), 16))
        label(t, '%s  %s' % (lab, text), (j * (W + 6) + 4, 2))
    return t


def sheet(spec, hd_fmt, items, name, scale=0.8, cols=2):
    tiles = [pair_tile(spec, hd_fmt, frames, lab) for lab, frames in items]
    tiles = [t.resize((int(t.size[0] * scale), int(t.size[1] * scale)), Image.LANCZOS) for t in tiles]
    Wt, Ht = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    out = Image.new('RGB', (cols * (Wt + 8) + 8, rows * (Ht + 8) + 8), (20, 22, 26))
    for i, t in enumerate(tiles):
        out.paste(t, (8 + (i % cols) * (Wt + 8), 8 + (i // cols) * (Ht + 8)))
    out.save(name)


def gif(spec, hd_fmt, seq, name, scale=0.7, ms=120):
    """seq: [(label, [frames to lay over each other])] played in turn, in-mod beside HD."""
    out = []
    for lab, frames in seq:
        t = pair_tile(spec, hd_fmt, frames, lab)
        t = t.resize((int(t.size[0] * scale), int(t.size[1] * scale)), Image.LANCZOS)
        out.append(t.convert('P', palette=Image.ADAPTIVE, colors=255))
    out[0].save(name, save_all=True, append_images=out[1:], duration=int(ms), loop=0, disposal=1)


def lineup(spec, hd_fmt, items, name, H=260, ground=220):
    """items: [(label, pattern or None for this unit's HD frames, [frames], scale)]: on one ground line, at the size the
    game draws them."""
    crops = []
    for lab, pat, frames, sc in items:
        im = layered(pat or hd_fmt, frames)
        if sc != 1.0:
            im = im.resize((round(im.size[0] * sc), round(im.size[1] * sc)), Image.LANCZOS)
        a = np.array(im)
        ys, xs = np.nonzero(a[..., 3] > 0)
        crops.append((lab, im.crop((max(xs.min() - 6, 0), 0, min(xs.max() + 7, im.size[0]), im.size[1]))))
    gap = 24
    W = sum(im.size[0] for _, im in crops) + gap * (len(crops) + 1)
    out = Image.new('RGBA', (W, H), BG)
    x = gap
    d = ImageDraw.Draw(out)
    for lab, im in crops:
        w, h = im.size
        a = np.array(im)
        solid = (a[..., 3] > 250) & (a[..., :3].max(-1) > 30)
        low = np.nonzero(solid.any(1))[0].max()
        out.alpha_composite(im, (x, ground - low))
        d.text((x + w // 2 - 45, H - 20), lab, fill=(240, 232, 190))
        x += w + gap
    out.convert('RGB').save(name)


def previews(spec, pkg):
    fmt = '%s/frames/%s-%%04d.png' % (pkg, spec.NAME)
    pv = pkg + '/previews'
    os.makedirs(pv, exist_ok=True)
    for name, items in spec.SHEETS:
        sheet(spec, fmt, items, pv + '/' + name)
    for name, seq, ms in getattr(spec, 'GIFS', []):
        gif(spec, fmt, seq, pv + '/' + name, ms=ms)
    name, items = spec.LINEUP
    lineup(spec, fmt, items, pv + '/' + name)
    print('previews done')


def check(spec, pkg):
    import vcheck
    ns = set()
    for a, b in getattr(spec, 'NO_SHADOW', []):
        ns |= set(range(a, b + 1))
    return vcheck.check('%s/frames/%s-%%04d.png' % (pkg, spec.NAME), spec.INMOD, spec.FRAMES, spec.CANVAS, ns,
                        getattr(spec, 'CHECK_SHIFT', (0, 0)))


def package_src(spec, pkg, unit_dir):
    """copy the source into PKG/src with the paths made relative (paths.py says where the hand-off is)."""
    vox = os.path.dirname(os.path.abspath(__file__))
    ren = '/home/claude/units/ts-units-hd-handoff/renderer'
    S = pkg + '/src'
    os.makedirs(S, exist_ok=True)
    for f in SHARED + getattr(spec, 'SHARED_EXTRA', []):
        shutil.copy(os.path.join(vox, f), S)
    for f in RENDERER:
        shutil.copy(os.path.join(ren, f), S)
    for f in spec.SRC + ['paths.py']:
        shutil.copy(os.path.join(unit_dir, f), S)
    for f in os.listdir(S):
        if not f.endswith('.py'):
            continue
        p = os.path.join(S, f)
        s = open(p).read()
        s = re.sub(r"sys\.path\.insert\(0, ['\"]/home/claude/units/work/vox['\"]\)(;[ \t]*|\n)", "", s)
        s = re.sub(r"sys\.path\.insert\(0, ['\"]/home/claude/units/ts-units-hd-handoff/renderer['\"]\)",
                   "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))", s)
        s = s.replace("'/home/claude/units/ts-units-hd-handoff/", "HANDOFF + '/")
        if "HANDOFF + '/" in s and 'from paths import HANDOFF' not in s:
            s = re.sub(r'^(import [^\n]+\n)', r'\1from paths import HANDOFF\n', s, count=1, flags=re.M)
        if 'os.path.dirname' in s and not re.search(r'^[ \t]*import[ \t]+([\w.]+[ \t]*,[ \t]*)*os\b', s, re.M):
            m = re.search(r'^import sys[^\n]*\n', s, re.M)
            s = s[:m.end()] + 'import os\n' + s[m.end():] if m else 'import os\n' + s
        open(p, 'w').write(s)
    left = [f for f in os.listdir(S) if f != 'vdeliver.py' and '/home/claude' in open(os.path.join(S, f)).read()]
    return left


if __name__ == '__main__':
    sys.path.insert(0, os.getcwd())
    spec = importlib.import_module(sys.argv[1])
    cmd = sys.argv[2]
    if cmd == 'render':
        render(spec, int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]) if len(sys.argv) > 5 else 4,
               bool(int(sys.argv[6])) if len(sys.argv) > 6 else True)
    elif cmd == 'previews':
        previews(spec, sys.argv[3])
    elif cmd == 'check':
        check(spec, sys.argv[3])
