"""Final frames for the dug-in Tick Tank (17-GATICK), both views, into PKG/<view>/...
    python3 tickfinal.py states|turret|build ra|iso [ss] [first last]

  building/tick-tank-dug-in-00, -01   the base dug in (no turret): healthy, damaged
  turret/tick-tank-dug-in-turret-00..31
                                      the turret at the mod's 32 facings (00 north, anticlockwise: 08 west, 16 south,
                                      24 east), each cut against the healthy base: the turret's pixels solid, the
                                      shadow it casts (and the sky it hides) as black at the darkening's alpha, so it
                                      darkens whichever state it is laid over.  One set over both states.
  build-up/tick-tank-dug-in-build-00..24
                                      00 the tank as the units hand-off draws it (hull + turret at facing 24, the
                                      turret casting no shadow, EA's way); 01-04 the turret's shadow fading in; 24 is
                                      exactly building-00 with turret-24."""
import os, sys, time
import numpy as np
from PIL import Image
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(HERE, 'src'), HERE):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import tickm as K, tickrender as TR, tickdamage as D

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-nod-tick-tank-dug-in-hd')
NAME = 'tick-tank-dug-in'
VIEWS = {'ra': 'ra-grid', 'iso': 'ts-angle'}
BUILD_N = 25
FADE_N = 5                      # frames 01..04 blend the turret's shadow in


def path(v, sub, name):
    return f'{PKG}/{VIEWS[v]}/{sub}/{name}.png'


def save(img, trim, p):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    img.save(p)
    trim.save(p[:-4] + '-trim.png')


def build_t(i):
    return i / (BUILD_N - 1.0)


def render(v, t, angle=None, level=0, fly=False, ss=4, base=True, shadow=True, return_r=False):
    c = TR.cfg(v)
    M = K.model(c, t=t, turret=angle, damage=level, base=base, fly=fly)
    out = TR.frame(M, c, ss=ss, decal=D.decal_fn(level) if base else None, shadow=shadow, return_r=return_r)
    return (out + (M,)) if return_r else out


# ------------------------------------------------------------------------------------------------ the turret layer
def overlay_turret(base, full, cov, thr=3):
    """the turret's layer from the full frame against the base: solid where the turret covers a pixel; elsewhere what
    it changes on the base (its shadow, the sky it hides) as black at the darkening's alpha (least squares over the
    channels), so it darkens either state; on the ground (see-through) the alpha and colour are solved (ovl.py)."""
    a = np.array(base).astype(np.float64) / 255.0
    b = np.array(full).astype(np.float64) / 255.0
    diff = np.abs(a - b).max(axis=2) * 255.0 > thr
    diff = ndimage.binary_dilation(diff, iterations=1)
    tur = cov > 1e-3
    out = np.zeros_like(b)
    out[tur] = b[tur]
    ab, af = a[..., 3], b[..., 3]
    opaque = ~tur & diff & (ab >= 0.999) & (af >= 0.999)
    A, B = a[..., :3], b[..., :3]
    k = (A * B).sum(-1) / np.maximum((A * A).sum(-1), 1e-9)          # B ~ k A
    dark = opaque & (k <= 1.0)
    out[dark, 3] = np.clip(1 - k[dark], 0, 1)
    out[dark, :3] = 0.0
    light = opaque & (k > 1.0)                                       # brighter (rare): copied
    out[light] = b[light]
    seen = ~tur & diff & ~opaque
    grow = seen & (af > ab + 1e-3)
    ao = np.where(af >= 0.999, 1.0, (af - ab) / np.maximum(1.0 - ab, 1e-6))
    num = B * af[..., None] - A * (ab * (1.0 - ao))[..., None]
    co = num / np.maximum(ao, 1e-6)[..., None]
    out[grow, :3] = np.clip(co[grow], 0, 1)
    out[grow, 3] = np.clip(ao[grow], 0, 1)
    return Image.fromarray((np.clip(out, 0, 1) * 255.0).round().astype(np.uint8), 'RGBA')


def composite(base, ov):
    im = base.copy()
    im.alpha_composite(ov)
    return im


# ------------------------------------------------------------------------------------------------ passes
def states(v, ss=4, levels=(0, 1)):
    for level in levels:
        t0 = time.time()
        p = path(v, 'building', f'{NAME}-{level:02d}')
        if os.path.exists(p) and os.environ.get('RESUME'):
            continue
        img, trim = render(v, 1.0, None, level, ss=ss)
        save(img, trim, p)
        print(v, 'state', level, '%.0fs' % (time.time() - t0), flush=True)


def turret(v, ss=4, frames=None):
    base = Image.open(path(v, 'building', f'{NAME}-00')).convert('RGBA')
    for f in (frames if frames is not None else range(32)):
        p = path(v, 'turret', f'{NAME}-turret-{f:02d}')
        if os.path.exists(p) and os.environ.get('RESUME'):
            continue
        t0 = time.time()
        img, trim, r, M = render(v, 1.0, K.turret_angle(f), 0, ss=ss, return_r=True)
        cov = TR.coverage(r, M.items, ('turret_ring', 'turret_plate', 'turret_dome', 'turret_skirt', 'turret_slot', 'turret_trunnion', 'turret_gun',
                                       'turret_hatch', 'turret_light'))
        ov = overlay_turret(base, img, cov)
        tr = np.array(trim).astype(np.float32) * (cov > 1e-3)
        save(ov, Image.fromarray(tr.round().astype(np.uint8), 'L'), p)
        if f == K.FACING:
            trim.save(f'{PKG}/.full24-{v}-trim.png')
        print(v, 'turret', f, '%.0fs' % (time.time() - t0), flush=True)


def blend(a, b, w):
    A = np.array(a).astype(np.float64) / 255.0; B = np.array(b).astype(np.float64) / 255.0
    pa = A[..., :3] * A[..., 3:4]; pb = B[..., :3] * B[..., 3:4]
    al = A[..., 3:4] * (1 - w) + B[..., 3:4] * w
    pc = pa * (1 - w) + pb * w
    rgb = np.where(al > 1e-6, pc / np.maximum(al, 1e-6), 0)
    out = np.concatenate([rgb, al], -1)
    return Image.fromarray((np.clip(out, 0, 1) * 255).round().astype(np.uint8), 'RGBA')


def unit_style(v, t, ss):
    """the hull (posed at t, its own shadow) with the turret laid over it casting no shadow: the units' way."""
    a, at = render(v, t, None, 0, ss=ss)
    b, bt = render(v, t, K.turret_angle(K.FACING), 0, ss=ss, base=False, shadow=False)
    img = composite(a, b)
    ab = np.array(b)[..., 3].astype(np.float32) / 255.0
    trim = np.array(bt).astype(np.float32) + np.array(at).astype(np.float32) * (1 - ab)
    return img, Image.fromarray(np.clip(trim, 0, 255).round().astype(np.uint8), 'L')


def build(v, ss=4, frames=None):
    for i in (frames if frames is not None else range(BUILD_N)):
        p = path(v, 'build-up', f'{NAME}-build-{i:02d}')
        if os.path.exists(p) and os.environ.get('RESUME'):
            continue
        t0 = time.time()
        t = build_t(i)
        if i == 0:
            img, trim = TR.unit_frame(TR.cfg(v), ss=ss)
        elif i < FADE_N:
            a, at = unit_style(v, t, ss)
            b, bt = render(v, t, K.turret_angle(K.FACING), 0, fly=True, ss=ss)
            w = i / float(FADE_N)
            img = blend(a, b, w)
            trim = Image.fromarray((np.array(at).astype(np.float32) * (1 - w) + np.array(bt).astype(np.float32) * w)
                                   .round().astype(np.uint8), 'L')
        elif i == BUILD_N - 1:
            base = Image.open(path(v, 'building', f'{NAME}-00')).convert('RGBA')
            ov = Image.open(path(v, 'turret', f'{NAME}-turret-{K.FACING:02d}')).convert('RGBA')
            img = composite(base, ov)
            tp = f'{PKG}/.full24-{v}-trim.png'
            if os.path.exists(tp):
                trim = Image.open(tp).convert('L')
            else:
                trim = render(v, 1.0, K.turret_angle(K.FACING), 0, ss=ss)[1]
        else:
            img, trim = render(v, t, K.turret_angle(K.FACING), 0, fly=True, ss=ss)
        save(img, trim, p)
        print(v, 'build', i, '%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    what, v = sys.argv[1], sys.argv[2]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    rng = None
    if len(sys.argv) > 5:
        rng = list(range(int(sys.argv[4]), int(sys.argv[5]) + 1))
    if what == 'states':
        states(v, ss)
    elif what == 'turret':
        turret(v, ss, rng)
    elif what == 'build':
        build(v, ss, rng)
    print('all done', what, v, flush=True)
