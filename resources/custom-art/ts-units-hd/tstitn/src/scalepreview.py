"""the Titan next to the HD harvester and EA's HD Mammoth, all facing east, standing on one ground line, at the
size the game draws them: the Titan's canvas (8 canvas px per classic px) at 2/3, the others (EA's 5.33) as they
are."""
import sys
import numpy as np
from PIL import Image, ImageDraw

BG = (96, 108, 72, 255)
REF = __import__('paths').HANDOFF + '/01-TSTITN/reference-hd/TD_HTNK/frames/htnk-%04d.png'
HARV = __import__('paths').HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'


def lineup(frames_fmt, name, legs=72, torso=120):
    titan = Image.open(frames_fmt % legs).convert('RGBA')
    titan.alpha_composite(Image.open(frames_fmt % torso).convert('RGBA'))
    titan = titan.resize((round(titan.size[0] * 2 / 3), round(titan.size[1] * 2 / 3)), Image.LANCZOS)
    harv = Image.open(HARV % 24).convert('RGBA')
    mam = Image.open(REF % 24).convert('RGBA'); mam.alpha_composite(Image.open(REF % 56).convert('RGBA'))
    items = [('EA Mammoth (TD HTNK)', mam), ('TS Harvester (HD)', harv), ('Titan (HD)', titan)]
    gap = 10
    W = sum(im.size[0] for _, im in items) + gap * (len(items) + 1) - 60
    H = 360
    out = Image.new('RGBA', (W, H), BG)
    ground = 330
    x = gap
    d = ImageDraw.Draw(out)
    for label, im in items:
        w, h = im.size
        a = np.array(im)
        solid = (a[..., 3] > 250) & (a[..., :3].max(-1) > 40)
        low = np.nonzero(solid.any(1))[0].max()
        out.alpha_composite(im, (x, ground - low))
        d.text((x + w // 2 - 50, H - 20), label, fill=(240, 232, 190))
        x += w + gap - 40
    out.convert('RGB').save(name)


if __name__ == '__main__':
    lineup(sys.argv[1], sys.argv[2])
