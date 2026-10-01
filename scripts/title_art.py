#!/usr/bin/env python3
"""Render the TIBERIAN FACTIONS / RED ALERT title from Red Alert's own front-end logo.

Source is the stock UI_RA_MAINLOGO.DDS (1948x552) read from the game's TEXTURES_SRGB.MEG. The steel
wings and the red RED ALERT stay untouched; the gold COMMAND & CONQUER stack is erased (a V-shaped
cut following the plate's top edge, with the Q's tail patched from the steel beside it) and replaced
by TIBERIAN / rule / FACTIONS in Tiberian Sun's molten style:
  * font Archivo Black (SIL OFL, title_work/), per-glyph tracking 0.10, each word stretched to its box;
  * the letter faces are filled with the molten texture of the TIBERIAN on Tiberian Sun's logo
    (title_work/key-art/tiberiansun-logo_2x.png), push-pull-filled and stretched over each line,
    inside a thin gold bevel rim, as on that logo; light grain, a top-left bevel, a thin dark
    outline and a soft drop shadow offset (-9, +9);
  * the rule between the words stays gold: the original's two tips with a crossfaded middle.
Output is deterministic (fixed noise seed).

usage: title_art.py <out.png>
"""
import io
import sys
from pathlib import Path

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import meg_extract  # noqa: E402

TEXTURES_MEG = Path.home() / '.steam/steam/steamapps/common/CnCRemastered/Data/TEXTURES_SRGB.MEG'
STOCK_LOGO = 'DATA\\ART\\TEXTURES\\SRGB\\UI_RA_MAINLOGO.DDS'
FONT = SCRIPT_DIR / 'title_work/ArchivoBlack-Regular.ttf'
LINES = (('TIBERIAN', (488, 22, 1442, 102)), ('FACTIONS', (470, 180, 1460, 286)))
FIRE_LOGO = SCRIPT_DIR / 'title_work/key-art/tiberiansun-logo_2x.png'
FIRE_LETTERS = (70, 270, 1180, 410)    # the TIBERIAN wordmark on that logo


def stock_logo():
    return Image.open(io.BytesIO(meg_extract.read_member(TEXTURES_MEG, STOCK_LOGO))).convert('RGBA')


def blur(arr, r):
    k = int(r * 3) | 1
    x = np.arange(-k, k + 1)
    g = np.exp(-x ** 2 / (2 * r * r))
    g /= g.sum()
    a = arr.astype(float)
    p = np.pad(a, ((0, 0), (k, k)), mode='edge')
    a = (sliding_window_view(p, 2 * k + 1, axis=1) * g).sum(-1)
    p = np.pad(a, ((k, k), (0, 0)), mode='edge')
    return (sliding_window_view(p, 2 * k + 1, axis=0) * g).sum(-1)


def erase_cnc(a):
    """The stock logo with the COMMAND & CONQUER lettering cut away above the plate."""
    H, W = a.shape[:2]
    r, g, b, al = (a[..., i] for i in range(4))
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    sat = (mx - mn) / np.maximum(mx, 1)
    yy, xx = np.mgrid[0:H, 0:W]
    top = 316 - 0.064 * np.abs(xx - 975)
    core = (xx >= 540) & (xx <= 1415) & (yy < top - 5)
    ext = (xx > 1460) & (xx <= 1482) & (yy < 180)
    steel = (sat < 0.22) & (mx > 90) & (al > 200)
    edge = ext | (((xx >= 460) & (xx < 540)) | ((xx > 1415) & (xx <= 1460))) & (
        (yy < 205) | ((yy < top - 5) & ~steel))
    out = a.copy()
    out[core | edge] = 0
    out[(xx >= 505) & (xx <= 545) & (yy >= 190) & (yy <= 225)] = 0
    q_tail = (xx >= 930) & (xx <= 1030) & (yy >= 290) & (yy <= 345) & (sat > 0.45) & (r > 120) & (
        g > 80) & (b < 120)
    for y, x in zip(*np.nonzero(q_tail)):
        dx = -110 if x < 975 else 110
        out[y, x] = a[y - int(round(0.064 * abs(dx))), x + dx]
    return out


def fire_field(size):
    """Tiberian Sun's molten letter faces, push-pull-filled to a solid texture and stretched over
    each title line (with a 20 px margin), black elsewhere."""
    x0, y0, x1, y1 = FIRE_LETTERS
    a = np.asarray(Image.open(FIRE_LOGO).convert('RGBA')).astype(float)[y0:y1, x0:x1]
    face = (a[..., 3] > 250) & (a[..., 0] > 190) & (a[..., 1] > 60) & (a[..., 1] < 215) & (a[..., 2] < 110)
    fm = np.array(Image.fromarray((face * 255).astype('uint8')).filter(ImageFilter.MinFilter(5))) > 0
    rgb = a[..., :3] * fm[..., None]
    w = fm.astype(float)
    acc = np.zeros_like(rgb)
    accw = np.zeros_like(w)
    for r in (2, 4, 8, 16, 32, 64):
        br = np.stack([blur(rgb[..., i], r) for i in range(3)], -1)
        bw = blur(w, r)
        take = (accw < 0.5) & (bw > 1e-3)
        acc[take] = br[take] / bw[take, None]
        accw[take] = 1
    acc[fm] = a[fm, :3]
    texture = Image.fromarray(acc.clip(0, 255).astype('uint8'))
    width, height = size
    field = np.zeros((height, width, 3))
    for _, (bx0, by0, bx1, by1) in LINES:
        stretched = texture.resize((bx1 - bx0 + 40, by1 - by0 + 40), Image.LANCZOS)
        field[by0 - 20:by1 + 20, bx0 - 20:bx1 + 20] = np.asarray(stretched)
    return field


def text_mask(txt, box, size, track=0.10):
    x0, y0, x1, y1 = box
    font = ImageFont.truetype(str(FONT), 200)
    glyphs = []
    for ch in txt:
        t = Image.new('L', (400, 300), 0)
        ImageDraw.Draw(t).text((20, 10), ch, font=font, fill=255)
        glyphs.append(t.crop(t.getbbox()))
    gh = max(g.height for g in glyphs)
    gap = int(gh * track)
    t = Image.new('L', (sum(g.width for g in glyphs) + gap * (len(glyphs) - 1), gh + 40), 0)
    x = 0
    for g in glyphs:
        t.paste(g, (x, gh - g.height))
        x += g.width + gap
    t = t.crop(t.getbbox()).resize((x1 - x0, y1 - y0), Image.LANCZOS)
    m = Image.new('L', size, 0)
    m.paste(t, (x0, y0))
    return m


def gold(mask, y0, y1, foil, rng):
    m = np.array(mask).astype(float) / 255
    H, W = m.shape
    yy = np.mgrid[0:H, 0:W][0]
    t = np.clip((yy - y0) / max(1, (y1 - y0)), 0, 1)[..., None]
    top, mid, bot = np.array([246, 226, 110.]), np.array([220, 180, 50.]), np.array([200, 140, 18.])
    col = np.where(t < 0.5, top + (mid - top) * (t / 0.5), mid + (bot - mid) * ((t - 0.5) / 0.5))
    blotch = blur(rng.normal(0, 1, (H, W)), 6)
    blotch = blotch / np.abs(blotch).max()
    scratch = blur(rng.normal(0, 1, (H, W)), 0.8)
    scratch = scratch / np.abs(scratch).max()
    col = 0.25 * col + 0.75 * foil
    col = col * (1 + 0.03 * blotch[..., None] + 0.05 * scratch[..., None])
    gy, gx = np.gradient(blur(m, 2.2))
    shade = (-gx * 0.6 - gy * 0.8) * 14
    col = np.clip(col + shade[..., None] * np.array([255, 230, 150.]), 0, 255)
    return col, m


def molten(col, m, fire):
    """The molten fill, bevel-lit, inside a thin rim of the plain lettering colour."""
    fill = np.clip(0.9 * fire + 0.1 * col, 0, 255)
    gy, gx = np.gradient(blur(m, 2.2))
    shade = (-gx * 0.6 - gy * 0.8) * 14
    fill = np.clip(fill + shade[..., None] * np.array([255, 200, 120.]), 0, 255)
    inner = np.asarray(Image.fromarray((m * 255).astype('uint8')).filter(ImageFilter.MinFilter(9))).astype(float) / 255
    rim = np.clip(m - blur(inner, 1.0), 0, 1)[..., None]
    return fill * (1 - rim) + col * rim


def comp(base, col, m, shadow_off=(-9, 9)):
    out = np.array(base).astype(float)

    def over(rgb, a):
        A = out[..., 3] / 255
        na = a + A * (1 - a)
        out[..., :3] = np.where(na[..., None] > 0,
                                (rgb * a[..., None] + out[..., :3] * A[..., None] * (1 - a[..., None]))
                                / np.maximum(na[..., None], 1e-6), 0)
        out[..., 3] = na * 255

    grown = np.array(Image.fromarray((m * 255).astype('uint8')).filter(ImageFilter.MaxFilter(3))).astype(float) / 255
    sh = np.roll(np.roll(grown, shadow_off[1], 0), shadow_off[0], 1)
    over(np.zeros_like(col) + [25, 15, 0], blur(sh, 4) * 0.8)
    over(np.zeros_like(col) + [70, 45, 5], grown * 0.8)
    over(col, m)
    return Image.fromarray(np.clip(out, 0, 255).astype('uint8'))


def render():
    stock = stock_logo()
    a = np.array(stock).astype(int)
    img = Image.fromarray(erase_cnc(a).astype('uint8')).convert('RGBA')
    fire = fire_field(img.size)
    rng = np.random.default_rng(7)
    for txt, box in LINES:
        col, m = gold(text_mask(txt, box, img.size), box[1], box[3], fire, rng)
        img = comp(img, molten(col, m, fire), m)
    img.alpha_composite(stock.crop((560, 112, 902, 156)), (560, 112))
    src = a.astype(float)
    cl, cr = src[112:156, 895], src[112:156, 1046]
    mid = np.stack([cl + (cr - cl) * ((x - 895) / 151) for x in range(896, 1046)], 1)
    img.alpha_composite(Image.fromarray(mid.clip(0, 255).astype('uint8')), (896, 112))
    img.alpha_composite(stock.crop((1046, 112, 1370, 156)), (1046, 112))
    return img


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    render().save(sys.argv[1])
