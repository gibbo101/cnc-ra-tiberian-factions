#!/usr/bin/env python3
"""Build the Tiberian Factions main-menu art: key-art soldiers either side of a steel menu box.

Writes into the mod's Data/ART/TEXTURES/SRGB/ directory:
  * RA_MAINMENUBG_02.DDS (2878x1200), the menu background. The launcher fits its central
    1920x1080 (the CORE, at 479,60) to the screen and lets the margins show on wider or
    taller screens, so the composition is laid out in core coordinates and the smoke
    backdrop runs to every edge. Left: the Remastered goggles soldier; right: the Tiberian
    Sun soldier; both dissolve into the smoke before the menu box. The Westwood plate and
    publisher logos sit at their stock positions, because the logo buttons draw their colour
    hover art at those fixed spots; at rest the logos show as faint steel silhouettes. Outside
    the core there is only smoke, shaded like the startup intro's backdrop, for 16:10 screens.
  * UI_RA_MAINMENU_GRID_RED.DDS and _01.DDS, fully transparent, so the stock radar grid no
    longer draws behind the menu.
  * the box (UI_RA_MAINMENU_BUTTON_BG and _SCANLINES atlas regions, drawn only by the main
    menu) repainted from red to steel, keeping the stock alpha so the box stays see-through.
  * steel menu buttons (normal, hover, pressed) in three TD main-menu button regions, and
    TD's stock green new-content glow (UI_BONUSBUTTONHIGHLIGHT) for the Bonus Gallery pulse.
The stock regions are read from the game's own atlas, so re-running gives the same result.

Key art (EA's) is read from title_work/key-art/:
  remastered-library_hero_2x.jpg (Steam app 1213210 library hero, 3840x1240)
  tiberiansun-full-head.jpg (the Tiberian Sun box soldier, full head, no logo)

usage: menu_art.py <mod Data/ART/TEXTURES/SRGB dir>
"""
import io
import sys
from pathlib import Path

import numpy as np
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import meg_extract  # noqa: E402
import title_logo_build  # noqa: E402

KEY_ART = SCRIPT_DIR / 'title_work/key-art'
TEXTURES_MEG = Path.home() / '.steam/steam/steamapps/common/CnCRemastered/Data/TEXTURES_SRGB.MEG'
BG_SIZE = (2878, 1200)
CORE = (479, 60)
BOX = (602, 322, 1314, 944)            # the menu box on the core, from the live layout
CORE_H = 1080
MARGIN_SHADE = 0.85                    # the startup intro's backdrop brightness
# The launcher draws the (Bink 1) startup movie darker than a texture of the same value: a dark
# tone v shows as about 1.08 v - 9 (measured on the desktop framebuffer, dark range).
VIDEO_LEVELS = (1.08, -9.0)
PLATE = (52, 24, 506, 142)             # Westwood plate, core coordinates
# Publisher logos: the hover art's atlas region and where the stock background engraves it (core).
LOGOS = (((6491, 5420, 86, 64), (78, 1006, 88, 66)),       # Petroglyph
         ((1361, 2476, 101, 74), (208, 1004, 101, 74)),    # Lemon Sky
         ((3577, 427, 189, 66), (354, 1008, 184, 64)))     # Electronic Arts
LOGO_TINT, LOGO_OPACITY = (150, 156, 166), 0.55
BOX_REGIONS = ((727, 1818, 723, 557), (4788, 1798, 723, 557))
BOX_STEEL, BOX_CAP = (0.57, 0.59, 0.62), 120
# Button art: the stock red sell/repair button states (shared with the in-game sidebar, so left
# alone) recoloured into TD main-menu button regions that only TD's own main menu draws.
# gui_texturesets_build.py points the menu's button set at these regions.
BUTTONS = (((1466, 2548, 601, 66), (2684, 231, 891, 91)),     # normal  -> UI_BUTTON_MAIN_06_MID
           ((846, 1569, 601, 66), (5698, 201, 891, 91)),      # hover   -> UI_BUTTON_MAIN_07_MID
           ((2069, 2548, 601, 66), (5698, 387, 891, 91)))     # pressed -> UI_BUTTON_MAIN_PRESSED_06_MID
BUTTON_STEEL, BUTTON_CAP = (0.447, 0.47, 0.49), 255
# TD's green new-content glow, which the RA menu's Bonus Gallery pulse is pointed at; restored
# from stock over idle art an earlier sidebar experiment left there.
BONUS_GLOW = (5698, 94, 905, 105)
GRIDS = {'UI_RA_MAINMENU_GRID_RED.DDS': (1125, 1080), 'UI_RA_MAINMENU_GRID_RED_01.DDS': (1125, 1125)}


def stock_bytes(name):
    return meg_extract.read_member(TEXTURES_MEG, 'DATA\\ART\\TEXTURES\\SRGB\\' + name)


def stock_texture(name):
    return Image.open(io.BytesIO(stock_bytes(name))).convert('RGBA')


def ramp(n, a, b):
    return np.clip((np.arange(n) - a) / max(1, b - a), 0, 1)


def with_mask(img, mask):
    layer = img.convert('RGBA')
    layer.putalpha(Image.fromarray((np.clip(mask, 0, 1) * 255).astype('uint8')))
    return layer


def smoke(hero):
    """The smoky right side of the Remastered hero, mirrored outward to fill the canvas."""
    tile = hero.crop((1900, 0, 3840, 1240))
    tile = tile.resize((round(tile.width * BG_SIZE[1] / tile.height), BG_SIZE[1]), Image.LANCZOS)
    flip = tile.transpose(Image.FLIP_LEFT_RIGHT)
    w = tile.width
    strip = Image.new('RGB', (w * 3, BG_SIZE[1]))
    strip.paste(flip, (0, 0))
    strip.paste(tile, (w, 0))
    strip.paste(flip, (2 * w, 0))
    x0 = (strip.width - BG_SIZE[0]) // 2
    return strip.crop((x0, 0, x0 + BG_SIZE[0], BG_SIZE[1])).convert('RGBA')


def place(canvas, layer, core_xy):
    canvas.alpha_composite(layer, (CORE[0] + core_xy[0], CORE[1] + core_xy[1]))


def below_core_fade(rows, top):
    """Fades a layer out by the core's bottom edge, so only smoke shows in the bottom margin."""
    return 1 - ramp(rows, CORE_H - 30 - top, CORE_H - top)


def shade_margins(canvas):
    """Makes the rows outside the core look like the intro's backdrop as the launcher shows it:
    16:10 screens (the Steam Deck) see these rows above and below the 16:9 startup movie once
    the launcher reveals the menu behind it, so they continue the movie's backdrop."""
    a = np.asarray(canvas).astype(float)
    rows = np.arange(a.shape[0])
    inside = ramp(len(rows), CORE[1], CORE[1] + 20) * (1 - ramp(len(rows), CORE[1] + CORE_H - 20, CORE[1] + CORE_H))
    gain, offset = VIDEO_LEVELS
    as_video = (a[..., :3] * MARGIN_SHADE * gain + offset).clip(0, 255)
    a[..., :3] = a[..., :3] * inside[:, None, None] + as_video * (1 - inside[:, None, None])
    return Image.fromarray(a.clip(0, 255).astype('uint8'), canvas.mode)


def remastered_soldier(hero):
    face = hero.crop((0, 0, 1560, 1240))
    s = 0.76
    face = face.resize((round(face.width * s), round(face.height * s)), Image.LANCZOS)
    x, y = -70, 1140 - face.height
    fw, fh = face.size
    fade_right = 1 - ramp(fw, BOX[0] - 90 - x, BOX[0] - 10 - x)
    mask = ramp(fh, 0, 330)[:, None] * ramp(fw, 0, 140)[None, :] * fade_right[None, :]
    mask *= below_core_fade(fh, y)[:, None]
    return with_mask(face, mask), (x, y)


def ts_soldier():
    ts = Image.open(KEY_ART / 'tiberiansun-full-head.jpg').convert('RGB').crop((160, 0, 1053, 908))
    s = 1.04
    ts = ts.resize((round(ts.width * s), round(ts.height * s)), Image.LANCZOS)
    tw, th = ts.size
    x, y = 1980 - tw, 1140 - th
    yy, xx = np.mgrid[0:th, 0:tw]
    r = np.hypot((xx - tw * 0.50) / (tw * 0.58), (yy - th * 0.56) / (th * 0.66))
    mask = np.clip((1.12 - r) / 0.40, 0, 1)
    mask *= ramp(tw, BOX[2] + 10 - x, BOX[2] + 110 - x)[None, :] * ramp(th, 0, 200)[:, None]
    mask *= (1 - ramp(tw, tw - 170, tw - 20))[None, :]
    mask *= below_core_fade(th, y)[:, None]
    return with_mask(ts, mask), (x, y)


def stock_piece(stock, rect, feather):
    x0, y0, x1, y1 = rect
    piece = stock.crop((CORE[0] + x0, CORE[1] + y0, CORE[0] + x1, CORE[1] + y1))
    w, h = piece.size
    mask = (ramp(w, 0, feather)[None, :] * (1 - ramp(w, w - feather, w))[None, :]
            * ramp(h, 0, feather)[:, None] * (1 - ramp(h, h - feather, h))[:, None])
    return with_mask(piece, mask), (x0, y0)


def logo_silhouettes(stock_atlas):
    for region, (x, y, w, h) in LOGOS:
        alpha = atlas_region(stock_atlas, region).getchannel('A').resize((w, h), Image.LANCZOS)
        shape = Image.new('RGBA', (w, h), LOGO_TINT + (0,))
        shape.putalpha(alpha.point(lambda v: int(v * LOGO_OPACITY)))
        yield shape, (x, y)


def background(stock_atlas):
    hero = Image.open(KEY_ART / 'remastered-library_hero_2x.jpg').convert('RGB')
    stock = stock_texture('RA_MAINMENUBG_02.DDS')
    canvas = smoke(hero)
    for layer, xy in (remastered_soldier(hero), ts_soldier(), stock_piece(stock, PLATE, 6),
                      *logo_silhouettes(stock_atlas)):
        place(canvas, layer, xy)
    return shade_margins(canvas)


def steel(region_img, gains, cap):
    """Red art to steel, same alpha: the red channel carries all the shading."""
    a = np.asarray(region_img).astype(float)
    out = a.copy()
    for ch, gain in enumerate(gains):
        out[..., ch] = np.clip(a[..., 0] * gain, 0, cap)
    return Image.fromarray(out.astype('uint8'), 'RGBA')


def resized(img, size):
    return img.convert('RGBa').resize(size, Image.LANCZOS).convert('RGBA')


def atlas_region(atlas_bytes, rect):
    x, y, w, h = rect
    rows = []
    for yy in range(h):
        o = (title_logo_build.ATLAS_HDR
             + ((title_logo_build.ATLAS_H - 1 - (y + yy)) * title_logo_build.ATLAS_W + x) * 4)
        rows.append(atlas_bytes[o:o + w * 4])
    b, g, r, a = Image.frombytes('RGBA', (w, h), b''.join(rows)).split()
    return Image.merge('RGBA', (r, g, b, a))


def main(srgb_dir):
    srgb = Path(srgb_dir)
    stock_atlas = stock_bytes(title_logo_build.ATLAS)
    (srgb / 'RA_MAINMENUBG_02.DDS').write_bytes(title_logo_build.dds_bytes(background(stock_atlas)))
    for name, size in GRIDS.items():
        (srgb / name).write_bytes(title_logo_build.dds_bytes(Image.new('RGBA', size, (0, 0, 0, 0))))
    atlas = srgb / title_logo_build.ATLAS
    for rect in BOX_REGIONS:
        title_logo_build.paint_atlas(atlas, steel(atlas_region(stock_atlas, rect), BOX_STEEL, BOX_CAP), rect)
    for src, dst in BUTTONS:
        art = steel(atlas_region(stock_atlas, src), BUTTON_STEEL, BUTTON_CAP)
        title_logo_build.paint_atlas(atlas, resized(art, dst[2:]), dst)
    title_logo_build.paint_atlas(atlas, atlas_region(stock_atlas, BONUS_GLOW), BONUS_GLOW)
    for p in ['RA_MAINMENUBG_02.DDS', *GRIDS, title_logo_build.ATLAS]:
        print(title_logo_build.md5(srgb / p), p)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1])
