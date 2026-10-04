"""
hdgrid.py - a sequence in all 8 facings at once, HD (and TS's sprite as the mod draws it, above it), as a looping GIF:
one GIF frame a step.

    python3 hdgrid.py UNIT shape.json poses.json SEQ OUT.gif [ms] [ts]
        poses.json: the steps' poses {step: {Q, frames}} or every frame's {frame: {Q, facing}}
"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
import inf as I
import infrender as R
import infcheck as C
import infseq as SQ

DIRS = ['N', 'NW', 'W', 'SW', 'S', 'SE', 'E', 'NE']
CROP = (78, 30, 190, 130)
ORDER = [0, 7, 6, 5, 4, 3, 2, 1]        # N, NE, E, SE, S, SW, W, NW: round the compass


def tile(im, label, z):
    b = Image.new('RGBA', im.size, C.BG); b.alpha_composite(im.convert('RGBA'))
    b = b.crop(CROP).convert('RGB')
    b = b.resize((round(b.width * z), round(b.height * z)), Image.LANCZOS)
    ImageDraw.Draw(b).text((3, 2), label, fill=(230, 220, 160))
    return b


def main():
    unit, shape, steps, seq, out = sys.argv[1:6]
    import infunit; infunit.use(unit)
    ms = int(sys.argv[6]) if len(sys.argv) > 6 else 133
    ts = len(sys.argv) > 7
    js = json.load(open(shape))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    st = json.load(open(steps))
    z = 1.5
    frames = []
    for s, ks in SQ.frames_of(unit, seq):
        tiles = []
        for f in ORDER:
            Q, ff = C.pose_for(ks[f], st, js['Q'])
            parts, dz = I.grounded(S, Q, I.facing_angle(f))
            hd, trim = R.render(parts, ss=4, ground=(js['ax'], js['y0']))
            col = [tile(hd, 'HD %s  %d' % (DIRS[f], ks[f]), z)]
            if ts:
                col.insert(0, tile(C.ts_on_canvas(unit, ks[f]), 'TS %s' % DIRS[f], z))
            tiles.append(col)
        cw, ch = tiles[0][0].width, tiles[0][0].height
        nrow = len(tiles[0])
        im = Image.new('RGB', (4 * (cw + 3), 2 * nrow * (ch + 3)), (18, 20, 24))
        for i, col in enumerate(tiles):
            for j, t in enumerate(col):
                im.paste(t, ((i % 4) * (cw + 3), ((i // 4) * nrow + j) * (ch + 3)))
        frames.append(im)
        print('step', s, flush=True)
    pal = [f.convert('P', palette=Image.ADAPTIVE, colors=255) for f in frames]
    pal[0].save(out, save_all=True, append_images=pal[1:], duration=ms, loop=0, disposal=1)


if __name__ == '__main__':
    main()
