"""
infmasks.py - the head close up, facing by facing: TS's sprite (as the mod scales it), the mod's frame and HD, the same
window round the HD head in each (the masks: the faceplate's light blue in TS against HD's).

    python3 infmasks.py UNIT shape.json stand_frames.json FRAMES_DIR out.png [facings]
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
import inf as I
import inffit as F
import infrender as R
import infcheck as C

DIRS = ['N', 'NW', 'W', 'SW', 'S', 'SE', 'E', 'NE']


def head_xy(S, Q, f, js):
    parts, dz = I.grounded(S, Q, I.facing_angle(f))
    P = I.Pose(S, Q, I.facing_angle(f))
    c = np.asarray(P.head[0], float) + np.array([0, 0, dz])
    x, y = R.camera((js['ax'], js['y0'])).project(c)
    return float(x), float(y)


def main():
    unit, shape, poses, fdir, out = sys.argv[1:6]
    import infunit; infunit.use(unit)
    facings = [int(v) for v in sys.argv[6].split(',')] if len(sys.argv) > 6 else [4, 3, 2, 5, 6, 1, 0]
    js = json.load(open(shape))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    P = json.load(open(poses))
    d, name = F.UNITS[unit]
    stem = 'ts' + name.lower()
    half, z = 15, 5
    rows = []
    for f in facings:
        Q = dict(js['Q'], **P[str(f)]['Q']) if str(f) in P else dict(js['Q'])
        hx, hy = head_xy(S, Q, f, js)
        box = (int(round(hx)) - half, int(round(hy)) - half, int(round(hx)) + half, int(round(hy)) + half)
        ims = [(C.ts_on_canvas(unit, f), 'TS %s' % DIRS[f]),
               (Image.open(C.ROOT + '%s/in-mod/ts%s/frames/ts%s-%04d.png' % (d, name.lower(), name.lower(), f))
                .convert('RGBA'), '%s %s' % (__import__('infunit').mod_label(__import__('infunit').CURRENT[0]), DIRS[f])),
               (Image.open(os.path.join(fdir, '%s-%04d.png' % (stem, f))).convert('RGBA'), 'HD %s' % DIRS[f])]
        row = []
        for im, label in ims:
            b = Image.new('RGBA', im.size, C.BG); b.alpha_composite(im)
            t = b.crop(box).convert('RGB').resize((2 * half * z, 2 * half * z),
                                                  Image.NEAREST if label.startswith('TS') else Image.LANCZOS)
            ImageDraw.Draw(t).text((3, 2), label, fill=(255, 255, 0))
            row.append(t)
        rows.append(row)
    w = 2 * half * z
    sheet = Image.new('RGB', (3 * (w + 4), len(rows) * (w + 4)), (18, 20, 24))
    for j, row in enumerate(rows):
        for i, t in enumerate(row):
            sheet.paste(t, (i * (w + 4), j * (w + 4)))
    sheet.save(out)


if __name__ == '__main__':
    main()
