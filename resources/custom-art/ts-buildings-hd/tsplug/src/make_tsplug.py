"""Compose TSPLUG.ZIP's 800 frames from this package (Python 3 + Pillow):
    python3 make_tsplug.py ts-angle|ra-grid OUTDIR
ORDER below lists the plug combinations block by block (80 frames each: 40 healthy then 40 damaged, the dish / lamps /
slot loop playing over each); change it to match TSPLUG.ZIP. Writes OUTDIR/tsplug-0000.png .. and the -trim.png masks."""
import os, sys
from PIL import Image, ImageChops

ORDER = ['none', 'right-seeker', 'right-seeker_left-ion', 'right-seeker_left-pods', 'right-ion', 'right-ion_left-seeker', 'right-ion_left-pods', 'right-pods', 'right-pods_left-seeker', 'right-pods_left-ion']
NA, NB, NC = 20, 10, 8
here = os.path.dirname(os.path.abspath(__file__))
view, out = sys.argv[1], sys.argv[2]
pkg = os.path.dirname(here)
os.makedirs(out, exist_ok=True)


def load(p):
    return Image.open(p).convert('RGBA')


def ov(sub, prefix, i):
    p = f'{pkg}/{view}/{sub}/upgrade-center-{prefix}-{i:02d}'
    return load(p + '.png'), Image.open(p + '-trim.png').convert('L')


def stack(im, trim, o, otrim):
    """an overlay over a frame and its house-colour mask: what the overlay covers solidly is no longer house colour
    (its see-through shadow and outline pixels, near black, leave the mask alone); its own house colour adds."""
    im.alpha_composite(o)
    r, g, b, a = o.split()
    bright = ImageChops.lighter(ImageChops.lighter(r, g), b).point(lambda v: 255 if v > 40 else 0)
    cover = ImageChops.multiply(a, bright)
    return ImageChops.lighter(ImageChops.multiply(trim, ImageChops.invert(cover)), otrim)


k = 0
for combo in ORDER:
    for level in (0, 1):
        base = load(f'{here}/{view}/base/{combo}/upgrade-center-{combo}-{level:02d}.png')
        btrim = Image.open(f'{here}/{view}/base/{combo}/upgrade-center-{combo}-{level:02d}-trim.png').convert('L')
        for t in range(40):
            im, trim = base.copy(), btrim
            for sub, prefix, i in (('A-dish', 'dish', t % NA + NA * level), ('B-lamps', 'lamps', t % NB + NB * level),
                                   ('C-slot', 'slot', t % NC + NC * level)):
                o, otrim = ov(sub, prefix, i)
                trim = stack(im, trim, o, otrim)
            im.save(f'{out}/tsplug-{k:04d}.png')
            trim.save(f'{out}/tsplug-{k:04d}-trim.png')
            k += 1
print(k, 'frames')
