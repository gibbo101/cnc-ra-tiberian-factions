#!/usr/bin/env python3
"""Paint the main menu's asset-pack panel: its frame and one logo per required pack.

The panel sits top right, mirroring the Westwood plate, and shows a required pack that is missing or switched
off (scripts/bui_mainmenu_pack_notice.py lays it out, redalert/tf_launcher.cpp fills it). Writes, loose in the
mod's Data/ART/TEXTURES/SRGB/:
  * TF_UI_PACK_PANEL.DDS: the main menu box's steel (UI_RA_MAINMENU_BUTTON_BG in the mod's UI atlas), nine-sliced
    to the panel's size so its bevel keeps its width;
  * TF_UI_PACK_LOGO_<ID>.DDS for each pack in PACK_LOGOS: the game's box-art logo with the pack's tag under it in
    the title's font (Archivo Black, title_work/), in gold.
PANEL and the LAYOUT rects are 1080p core pixels; the layout script converts them.

usage: pack_panel_art.py <mod Data/ART/TEXTURES/SRGB dir>
License: GPL v3.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import title_logo_build  # noqa: E402

SCRIPT_DIR = Path(__file__).resolve().parent
FONT = SCRIPT_DIR / 'title_work/ArchivoBlack-Regular.ttf'
BOX_REGION = (727, 1818, 723, 557)     # UI_RA_MAINMENU_BUTTON_BG in the UI atlas (menu_art.BOX_REGIONS)
CORNER = 30                            # the box's bevel, kept unscaled by the nine-slice

PANEL = (1414, 24, 453, 290)           # core x, y, w, h: the Westwood plate's mirror, grown down for the button
LAYOUT = {                             # inside the panel, panel pixels
    'logo': (30, 12, 393, 158),
    'status': (12, 176, 429, 26),
    'button': (12, 220, 429, 50),
}
SCALE = 2                              # texture pixels per core pixel, for a sharp logo at 4K
# Workshop pack id -> (logo source, tag under it)
PACK_LOGOS = {
    'TSHD': (SCRIPT_DIR / 'title_work/key-art/tiberiansun-logo_2x.png', 'HD ASSETS'),
}
GOLD_TOP, GOLD_BOTTOM = (255, 232, 150), (196, 132, 34)


def frame(atlas):
    """The box region nine-sliced to the panel's size, at SCALE."""
    x, y, w, h = BOX_REGION
    src = atlas.crop((x, y, x + w, y + h))
    W, H = PANEL[2] * SCALE, PANEL[3] * SCALE
    c = CORNER
    out = Image.new('RGBA', (W, H))
    cols = ((0, c, 0, c), (c, w - c, c, W - c), (w - c, w, W - c, W))
    rows = ((0, c, 0, c), (c, h - c, c, H - c), (h - c, h, H - c, H))
    for sx0, sx1, dx0, dx1 in cols:
        for sy0, sy1, dy0, dy1 in rows:
            out.paste(src.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0), Image.LANCZOS), (dx0, dy0))
    return out


def gold_text(text, height):
    """Text in the title's font, gold top to bottom, with a dark outline and a soft shadow."""
    font = ImageFont.truetype(str(FONT), height)
    left, top, right, bottom = font.getbbox(text)
    pad = height // 4
    size = (right - left + 2 * pad, bottom - top + 2 * pad)
    mask = Image.new('L', size)
    ImageDraw.Draw(mask).text((pad - left, pad - top), text, font=font, fill=255)
    ramp = np.linspace(0, 1, size[1])[:, None, None]
    rgb = (np.array(GOLD_TOP) * (1 - ramp) + np.array(GOLD_BOTTOM) * ramp).repeat(size[0], axis=1)
    face = Image.fromarray(rgb.astype(np.uint8), 'RGB').convert('RGBA')
    face.putalpha(mask)
    rim = mask.filter(ImageFilter.MaxFilter(2 * (height // 14) + 1))
    shadow = rim.filter(ImageFilter.GaussianBlur(height // 10))
    out = Image.new('RGBA', size)
    out.paste((0, 0, 0, 200), (height // 16, height // 16), shadow)
    out.paste((40, 20, 0, 255), (0, 0), rim)
    out.alpha_composite(face)
    return out


def logo(source, tag):
    """The game's logo above the pack's tag, filling the logo rect at SCALE."""
    W, H = LAYOUT['logo'][2] * SCALE, LAYOUT['logo'][3] * SCALE
    art = Image.open(source).convert('RGBA')
    art = art.crop(art.getbbox())
    label = gold_text(tag, H // 5)
    art.thumbnail((W, H - label.height), Image.LANCZOS)
    out = Image.new('RGBA', (W, H))
    out.alpha_composite(art, ((W - art.width) // 2, 0))
    out.alpha_composite(label, ((W - label.width) // 2, H - label.height))
    return out


def main(srgb_dir):
    srgb = Path(srgb_dir)
    atlas = Image.open(srgb / title_logo_build.ATLAS).convert('RGBA')
    (srgb / 'TF_UI_PACK_PANEL.DDS').write_bytes(title_logo_build.dds_bytes(title_logo_build.bleed(frame(atlas))))
    for pack, (source, tag) in PACK_LOGOS.items():
        art = title_logo_build.bleed(logo(source, tag))
        (srgb / f'TF_UI_PACK_LOGO_{pack}.DDS').write_bytes(title_logo_build.dds_bytes(art))
    print('wrote the pack panel and', len(PACK_LOGOS), 'logo(s) in', srgb)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
