"""
infgif.py - a sequence as a GIF: TS's sprite (scaled as the mod draws it), the mod's frame and HD side by side.

    python3 infgif.py UNIT shape.json poses.json OUT.gif FRAMES [ms] [z]
"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
import inf as I
import infrender as R
import infcheck as C


def main():
    unit, shape, poses, out = sys.argv[1:5]
    import infunit; infunit.use(unit)
    frames = [int(v) for v in sys.argv[5].split(',')]
    ms = int(sys.argv[6]) if len(sys.argv) > 6 else 133
    z = float(sys.argv[7]) if len(sys.argv) > 7 else 2.0
    js = json.load(open(shape))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    P = json.load(open(poses)) if poses != '-' else None
    d, name = C.F.UNITS[unit]
    imgs = []
    for k in frames:
        Q, f = C.pose_for(k, P, js['Q'])
        parts, dz = I.grounded(S, Q, I.facing_angle(f))
        hd, trim = R.render(parts, ss=4, ground=(js['ax'], js['y0']))
        row = []
        for lab, im in (("TS's sprite", C.ts_on_canvas(unit, k)),
                        ('in-mod', Image.open(C.ROOT + '%s/in-mod/ts%s/frames/ts%s-%04d.png'
                                              % (d, name.lower(), name.lower(), k))), ('HD', hd)):
            b = Image.new('RGBA', im.size, C.BG); b.alpha_composite(im.convert('RGBA'))
            b = b.crop(C.CROP).convert('RGB')
            b = b.resize((round(b.width * z), round(b.height * z)), Image.LANCZOS if lab == 'HD' else Image.NEAREST)
            t = Image.new('RGB', (b.width, b.height + 16), (28, 30, 34)); t.paste(b, (0, 16))
            ImageDraw.Draw(t).text((3, 2), '%s  %d' % (lab, k), fill=(230, 220, 160))
            row.append(t)
        o = Image.new('RGB', (sum(t.width + 4 for t in row), row[0].height), (18, 20, 24)); x = 0
        for t in row:
            o.paste(t, (x, 0)); x += t.width + 4
        imgs.append(o.convert('P', palette=Image.ADAPTIVE, colors=255))
    imgs[0].save(out, save_all=True, append_images=imgs[1:], duration=ms, loop=0, disposal=1)


if __name__ == '__main__':
    main()
