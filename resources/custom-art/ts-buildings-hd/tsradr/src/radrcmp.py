"""Side by side: TS (GTRADR + GTRADR_A, scaled into the mod's canvas, lanczos) | our TS-angle render | our RA render.
    python3 radrcmp.py <iso png> <ra png> <out> [dish frame 0] [base 0] [zoom 1]"""
import sys
import numpy as np
from PIL import Image, ImageDraw
import radrrender as RR

TS = '/home/claude/work/ts/ts-buildings-hd-handoff/07-TSRADR/ts-original/'
BG = (96, 108, 72, 255)


def ts_canvas(dish=0, base=0, extra=()):
    im = Image.new('RGBA', (144, 144), (0, 0, 0, 0))
    im.alpha_composite(Image.open(f'{TS}GTRADR/frames/{base:02d}.png').convert('RGBA'))
    if dish is not None:
        im.alpha_composite(Image.open(f'{TS}GTRADR_A/frames/{dish:02d}.png').convert('RGBA'))
    for e in extra:
        im.alpha_composite(Image.open(e).convert('RGBA'))
    K, (ox, oy) = RR.ISO_K, RR.ISO_O
    big = im.resize((int(round(144 * K)), int(round(144 * K))), Image.LANCZOS)
    can = Image.new('RGBA', RR.CANVAS['iso'], (0, 0, 0, 0))
    can.alpha_composite(big, (int(round(ox)), int(round(oy))) if ox >= 0 and oy >= 0 else (0, 0)) if False else None
    can.paste(big, (int(round(ox)), int(round(oy))), big)
    return can


def on_bg(im):
    b = Image.new('RGBA', im.size, BG); b.alpha_composite(im); return b


def sheet(ims, labels, out, zoom=1.0):
    ims = [on_bg(i) for i in ims]
    if zoom != 1.0:
        ims = [i.resize((int(i.width * zoom), int(i.height * zoom)), Image.LANCZOS) for i in ims]
    H = max(i.height for i in ims)
    S = Image.new('RGBA', (sum(i.width + 8 for i in ims), H + 20), (30, 30, 30, 255))
    d = ImageDraw.Draw(S); x = 0
    for i, l in zip(ims, labels):
        S.paste(i, (x, 20)); d.text((x + 4, 4), l, fill=(255, 255, 0, 255)); x += i.width + 8
    S.save(out)


if __name__ == '__main__':
    iso, ra, out = sys.argv[1:4]
    dk = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    base = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    zoom = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0
    sheet([ts_canvas(dk, base), Image.open(iso).convert('RGBA'), Image.open(ra).convert('RGBA')],
          ['TS (x3.015)', 'HD, TS angle', 'HD, RA grid'], out, zoom)
