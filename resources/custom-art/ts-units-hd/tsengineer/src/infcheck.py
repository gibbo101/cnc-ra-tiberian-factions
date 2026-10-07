"""
infcheck.py - the infantry shape check: per facing, TS's sprite (scaled as the mod draws it), the mod's frame, HD and
EA's HD Minigunner; and HD frames rendered from fitted poses.

    python3 infcheck.py UNIT shape.json OUT.png FRAMES [poses.json] [ea]
        FRAMES: TS / mod frame numbers; their poses come from poses.json ({step: {Q, frames}}) when given, else the
        standing pose; ea adds EA's frame of the same number (standing only)
"""
import json, sys
from paths import HANDOFF
import numpy as np
from PIL import Image, ImageDraw
import inf as I
import inffit as F
import infrender as R

ROOT = HANDOFF + '/'
K, DX, DY = 3.068, 38.06, 10.57            # the mod's frames: TS's sprite x 3.068 at (38.06, 10.57) (infmap.py)
BG = (96, 104, 72, 255)
CROP = (68, 16, 200, 148)
DIRS = ['N', 'NW', 'W', 'SW', 'S', 'SE', 'E', 'NE']
EA_NAME = dict(e1='Minigunner', e2='Grenadier', eng='Engineer')


def ts_on_canvas(unit, k):
    d, name = F.UNITS[unit]
    ts = Image.open(ROOT + '%s/ts-original/%s/frames/%s-%03d.png' % (d, name, name.lower(), k)).convert('RGBA')
    big = Image.new('RGBA', R.CANVAS, (0, 0, 0, 0))
    # the unit's own placement in the mod (infunit.use sets it)
    up = ts.resize((round(ts.size[0] * R.K), round(ts.size[1] * R.K)), Image.NEAREST)
    big.paste(up, (round(R.DX), round(R.DY)), up)
    return big


def tile(im, label, z=2):
    b = Image.new('RGBA', im.size, BG); b.alpha_composite(im.convert('RGBA'))
    b = b.crop(CROP).convert('RGB')
    b = b.resize((b.width * z, b.height * z), Image.LANCZOS)
    t = Image.new('RGB', (b.width, b.height + 16), (28, 30, 34)); t.paste(b, (0, 16))
    ImageDraw.Draw(t).text((3, 2), label, fill=(230, 220, 160))
    return t


def pose_for(k, poses, Qs):
    """the pose of frame k: from per-frame poses ({frame: {Q, facing}}) or a sequence's steps ({step: {Q, frames}})."""
    if poses:
        if str(k) in poses and 'facing' in poses[str(k)]:
            return dict(Qs, **poses[str(k)]['Q']), poses[str(k)]['facing']
        for s, v in poses.items():
            if 'frames' in v and k in v['frames']:
                return dict(Qs, **v['Q']), v['frames'].index(k)
    return dict(Qs), k % 8


def main():
    unit, shape, out = sys.argv[1], sys.argv[2], sys.argv[3]
    import infunit; infunit.use(unit)
    frames = [int(v) for v in sys.argv[4].split(',')]
    poses = json.load(open(sys.argv[5])) if len(sys.argv) > 5 and sys.argv[5] != '-' else None
    ea = len(sys.argv) > 6
    js = json.load(open(shape))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    d, name = F.UNITS[unit]
    rows = []
    for k in frames:
        Q, f = pose_for(k, poses, js['Q'])
        parts, dz = I.grounded(S, Q, I.facing_angle(f))
        hd, trim = R.render(parts, ss=4, ground=(js['ax'], js['y0']))
        row = [tile(ts_on_canvas(unit, k), "TS's sprite %d (%s)" % (k, DIRS[f])),
               tile(Image.open(ROOT + '%s/in-mod/ts%s/frames/ts%s-%04d.png' % (d, name.lower(), name.lower(), k)),
                    'in-mod'),
               tile(hd, 'HD')]
        if ea:
            ref = infunit.UNITS[unit]['ref']                  # EA's soldier of the same kind (RA_E6: e6-0000.png)
            row.append(tile(Image.open(ROOT + '%s/reference-hd/%s/frames/%s-%04d.png' % (d, ref, ref.split('_', 1)[1].lower(),
                                                                                         k)),
                            infunit.UNITS[unit].get('ref_name', "EA's " + EA_NAME.get(unit, 'soldier'))))
        rows.append(row)
    W = sum(t.width + 4 for t in rows[0]); Hh = rows[0][0].height
    cols = 2 if len(rows) > 4 else 1
    nr = (len(rows) + cols - 1) // cols
    S2 = Image.new('RGB', (cols * (W + 12), nr * (Hh + 6)), (18, 20, 24))
    for i, row in enumerate(rows):
        x = (i % cols) * (W + 12); y = (i // cols) * (Hh + 6)
        for t in row:
            S2.paste(t, (x, y)); x += t.width + 4
    S2.save(out)


if __name__ == '__main__':
    main()
