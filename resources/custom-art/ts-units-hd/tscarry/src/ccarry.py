"""ccarry.py - the Carryall carrying the HD harvester as the game draws them: the Carryall's frame at two thirds (the
game's scale for this canvas), then the harvester's frame of the same facing (the hand-off's example, at the game's
scale, its baked ground shadow left out) drawn after it with its centre 6 classic px (32 game px) below the Carryall's
centre, as the mod draws a carried vehicle.
    python3 ccarry.py out.png PKG_FRAMES_PATTERN [facings] [zoom]"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from paths import HANDOFF
from ccam import ORIGIN

HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
HARV_C = (192.0, 192.0)                              # the harvester's position on its canvas
DROP = 32.0                                          # 6 classic px in game px (48 canvas px on the Carryall's canvas)
BG = (96, 108, 72, 255)
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)


def no_shadow(im):
    """the frame without its baked ground shadow (pure black, 75% and the faint fringe)."""
    a = np.array(im.convert('RGBA'))
    a[a[..., :3].max(-1) < 6] = 0
    return Image.fromarray(a, 'RGBA')


def carrying(fmt, f, z=1.5, W=330, H=300):
    s = 2 / 3
    cimg = Image.open(fmt % f).convert('RGBA')
    cimg = cimg.resize((round(cimg.width * s), round(cimg.height * s)), Image.LANCZOS)
    cx, cy = ORIGIN[0] * s, ORIGIN[1] * s
    h = no_shadow(Image.open(HARV % f))
    out = Image.new('RGBA', (W, H), BG)
    ox, oy = W / 2 - cx, H * 0.42 - cy                # the Carryall's centre at (W/2, 0.42 H)
    out.alpha_composite(cimg, (int(round(ox)), int(round(oy))))
    hx, hy = W / 2 - HARV_C[0], H * 0.42 + DROP - HARV_C[1]
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lay.paste(h, (int(round(hx)), int(round(hy))), h)
    out.alpha_composite(lay)
    if z != 1:
        out = out.resize((round(W * z), round(H * z)), Image.LANCZOS)
    ImageDraw.Draw(out).text((6, 4), 'facing %d' % f, font=FONT, fill=(240, 232, 190))
    return out


def sheet(out, fmt, fs=tuple(range(0, 32, 4)), z=1.0, cols=4):
    tiles = [carrying(fmt, f, z) for f in fs]
    w, h = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    S = Image.new('RGB', (cols * (w + 6) - 6, rows * (h + 6) - 6), (24, 24, 24))
    for i, t in enumerate(tiles):
        S.paste(t.convert('RGB'), ((i % cols) * (w + 6), (i // cols) * (h + 6)))
    S.save(out)
    return S.size


if __name__ == '__main__':
    fs = tuple(int(a) for a in sys.argv[3].split(',')) if len(sys.argv) > 3 else tuple(range(0, 32, 4))
    z = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
    print(sheet(sys.argv[1], sys.argv[2], fs, z))
