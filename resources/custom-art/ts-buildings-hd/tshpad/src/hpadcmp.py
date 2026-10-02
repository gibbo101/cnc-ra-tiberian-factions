"""TS (GTHPADBB + GTHPAD [+ GTHPAD_A], scaled into the mod's canvas) | our TS angle | our RA grid.
    python3 hpadcmp.py <iso png> <ra png> <out> [lights frame or -1] [level 0] [zoom 1]"""
import sys
from PIL import Image, ImageDraw
import hpadrender as RR

TS = '/home/claude/work/ts/ts-buildings-hd-handoff/08-TSHPAD/ts-original/'
BG = (96, 108, 72, 255)


def ts_canvas(lights=None, level=0, bib=True, bld=True):
    im = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
    if bib:
        im.alpha_composite(Image.open(f'{TS}GTHPADBB/frames/{level:02d}.png').convert('RGBA'))
    if bld:
        im.alpha_composite(Image.open(f'{TS}GTHPAD/frames/{level:02d}.png').convert('RGBA'))
    if lights is not None and lights >= 0:
        im.alpha_composite(Image.open(f'{TS}GTHPAD_A/frames/{lights + 8 * level:02d}.png').convert('RGBA'))
    K, (ox, oy) = RR.ISO_K, RR.ISO_O
    big = im.resize((int(round(96 * K)), int(round(96 * K))), Image.LANCZOS)
    can = Image.new('RGBA', RR.CANVAS['iso'], (0, 0, 0, 0))
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
    lt = int(sys.argv[4]) if len(sys.argv) > 4 else -1
    lv = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    zoom = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0
    sheet([ts_canvas(lt, lv), Image.open(iso).convert('RGBA'), Image.open(ra).convert('RGBA')],
          ['TS (x3.55)', 'HD, TS angle', 'HD, RA grid'], out, zoom)
