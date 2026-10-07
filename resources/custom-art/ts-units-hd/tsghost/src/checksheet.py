"""
checksheet.py - a frame-by-frame sheet: each frame of a sequence as the mod draws it now (TS's sprite and TS's shadow)
beside the HD frame, on the same scale, for checking against TS.

    python3 checksheet.py UNIT PKG FRAMES out.png [cols] [title]       FRAMES: 134-148,149-163
"""
import sys
from paths import HANDOFF
import numpy as np
from PIL import Image, ImageDraw
import infunit

ROOT = HANDOFF + '/'
BG = np.array([96, 100, 72], float)


def on_bg(img):
    a = np.asarray(img.convert('RGBA')).astype(float); al = a[..., 3:4] / 255.0
    return Image.fromarray(np.clip(a[..., :3] * al + BG * (1 - al), 0, 255).astype(np.uint8))


def frames_arg(s):
    out = []
    for part in s.split(','):
        if '-' in part:
            a, b = part.split('-'); out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def main():
    unit, pkg, fr, out = sys.argv[1:5]
    cols = int(sys.argv[5]) if len(sys.argv) > 5 else 5
    title = sys.argv[6] if len(sys.argv) > 6 else ''
    u = infunit.UNITS[unit]
    stem = 'ts' + u['name'].lower()
    ks = frames_arg(fr)
    box = (48, 22, 222, 152)                     # (the soldier and his shadow on the 267 x 208 canvas)
    Z = 1.5
    tw, th = int((box[2] - box[0]) * Z), int((box[3] - box[1]) * Z)
    cells = []
    for k in ks:
        a = on_bg(Image.open(ROOT + '%s/in-mod/%s/frames/%s-%04d.png' % (u['dir'], stem, stem, k))).crop(box)
        b = on_bg(Image.open('%s/frames/%s-%04d.png' % (pkg, stem, k))).crop(box)
        c = Image.new('RGB', (2 * tw + 6, th + 16), (24, 24, 24))
        c.paste(a.resize((tw, th), Image.LANCZOS), (0, 16)); c.paste(b.resize((tw, th), Image.LANCZOS), (tw + 6, 16))
        d = ImageDraw.Draw(c)
        d.text((4, 2), 'TS (as the mod has it)  %d' % k, fill=(230, 230, 120))
        d.text((tw + 10, 2), 'HD  %d' % k, fill=(230, 230, 120))
        cells.append(c)
    cw, ch = cells[0].size
    rows = (len(cells) + cols - 1) // cols
    head = 24 if title else 0
    sheet = Image.new('RGB', (cols * (cw + 8), rows * (ch + 8) + head), (40, 40, 40))
    if title:
        ImageDraw.Draw(sheet).text((8, 6), title, fill=(255, 255, 255))
    for i, c in enumerate(cells):
        sheet.paste(c, ((i % cols) * (cw + 8), head + (i // cols) * (ch + 8)))
    sheet.save(out)
    print(out, sheet.size)


if __name__ == '__main__':
    main()
