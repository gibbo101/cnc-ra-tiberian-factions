"""TSPLUG.ZIP's loop with the plugs baked in: one folder per plug combination (the first plug goes in the right-hand
socket, east in TS's frame; the second in the left-hand, west), each the building + its plugs (still, at their frame 0)
healthy and damaged, without the A/B/C overlays; make_tsplug.py (also written into the package) composes TSPLUG's 800
frames from these and the A-dish / B-lamps / C-slot frames in any block order.

    python3 plugloop.py iso|ra [ss]          the base frames, into PKG/loop/<view>/base/<combo>/
    python3 plugloop.py script               writes PKG/loop/make_tsplug.py and PKG/loop/README.txt"""
import os, sys, time, resource
import numpy as np
from PIL import Image
import plug as M, plugrender as RR
from pfinal import save

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-upgrade-center-hd')
NAME = 'upgrade-center'
VIEWS = {'iso': 'ts-angle', 'ra': 'ra-grid'}
SHORT = {'D': 'pods', 'E': 'seeker', 'F': 'ion'}
# (folder, right / first plug, left / second plug), in the default block order: 0000 none, 0400 Ion right + Seeker left
COMBOS = [('none', None, None), ('right-seeker', 'E', None), ('right-seeker_left-ion', 'E', 'F'),
          ('right-seeker_left-pods', 'E', 'D'), ('right-ion', 'F', None), ('right-ion_left-seeker', 'F', 'E'),
          ('right-ion_left-pods', 'F', 'D'), ('right-pods', 'D', None), ('right-pods_left-seeker', 'D', 'E'),
          ('right-pods_left-ion', 'D', 'F')]


def render(vname, ss=4, only=None):
    out = f'{PKG}/loop/{VIEWS[vname]}/base'
    for name, right, left in COMBOS:
        if only and name not in only:
            continue
        for level in (0, 1):
            t0 = time.time()
            pr, v = RR.prep(vname, ss, level=level, prog=dict(M.DONE, dish=0.0), plugs=(left, right), plug_t=0)
            f, ft = pr.frame(want_trim=True)
            del pr
            save(RR.on_canvas(f, vname), RR.on_canvas(ft, vname), f'{out}/{name}/{NAME}-{name}-{level:02d}.png')
            print(vname, name, level, '%.0fs' % (time.time() - t0),
                  'peak %.2f GB' % (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6), flush=True)


SCRIPT = r'''"""Compose TSPLUG.ZIP's 800 frames from this package (Python 3 + Pillow):
    python3 make_tsplug.py ts-angle|ra-grid OUTDIR
ORDER below lists the plug combinations block by block (80 frames each: 40 healthy then 40 damaged, the dish / lamps /
slot loop playing over each); change it to match TSPLUG.ZIP. Writes OUTDIR/tsplug-0000.png .. and the -trim.png masks."""
import os, sys
from PIL import Image, ImageChops

ORDER = %(order)r
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
            for sub, prefix, i in (('A-dish', 'dish', t %% NA + NA * level), ('B-lamps', 'lamps', t %% NB + NB * level),
                                   ('C-slot', 'slot', t %% NC + NC * level)):
                o, otrim = ov(sub, prefix, i)
                trim = stack(im, trim, o, otrim)
            im.save(f'{out}/tsplug-{k:04d}.png')
            trim.save(f'{out}/tsplug-{k:04d}-trim.png')
            k += 1
print(k, 'frames')
'''


def script():
    os.makedirs(f'{PKG}/loop', exist_ok=True)
    open(f'{PKG}/loop/make_tsplug.py', 'w').write(SCRIPT % dict(order=[c[0] for c in COMBOS]))
    lines = ['TSPLUG.ZIP\'s loop with the plugs baked in.', '',
             'base/<combo>/upgrade-center-<combo>-00 (healthy) and -01 (damaged), with -trim.png, both views: the',
             'building with its plugs (the first plug in the right-hand socket, the second in the left-hand one; the plugs',
             'still, at their frame 0), without the A / B / C overlays.', '',
             'make_tsplug.py composes the 800 frames: python3 make_tsplug.py ts-angle OUTDIR (or ra-grid). Its ORDER list',
             'gives the combinations block by block (80 frames each: 40 healthy, then 40 damaged); as delivered it is', '']
    for i, (name, right, left) in enumerate(COMBOS):
        lines.append('  %04d-%04d  %s' % (i * 80, i * 80 + 79, name))
    lines += ['', '(0000 = no plugs and 0400 = Ion Cannon Uplink right + Seeker Control left, as in the mod now.)']
    open(f'{PKG}/loop/README.txt', 'w').write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    if sys.argv[1] == 'script':
        script()
    else:
        render(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 4, sys.argv[3:] or None)
