#!/usr/bin/env python3
"""Mockup of the main menu's add-ons notice: the pack panel with the Tiberian Factions title logo, the notice
and the ADD-ONS PAGE button, painted over a 1280x800 Deck screenshot of the menu showing the panel.

Usage: addons_notice_mockup.py <Deck menu screenshot> <UI_RA_MAINLOGO.DDS> <out.jpg>
"""
import sys

from PIL import Image, ImageDraw, ImageFont

PANEL = (945, 59, 1241, 245)           # the panel's frame on the Deck screenshot
INNER = (951, 64, 1235, 200)           # inside the frame, above the button
BLANK = (952, 64, 966, 200)            # a full-height strip of the panel's own backdrop, left of the old content
LABEL = (962, 210, 1226, 228)          # the button's old label, inside its steel face
FACE = (1045, 203, 1060, 205)          # a sliver of the button's face without text
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
GREEN, BRIGHT = (46, 192, 0), (70, 255, 30)
LINES = ("YOU HAVE TIBERIAN FACTIONS ADD-ONS", "AVAILABLE THAT ARE NOT ENABLED")
BUTTON = ">> ADD-ONS PAGE <<"


def tile(im, box, source):
    """Covers `box` with copies of the strip `source`, which keeps the backdrop's horizontal grain."""
    piece = im.crop(source)
    x0, y0, x1, y1 = box
    for y in range(y0, y1, piece.height):
        for x in range(x0, x1, piece.width):
            im.paste(piece.crop((0, 0, min(piece.width, x1 - x), min(piece.height, y1 - y))), (x, y))


def centred(draw, cx, y, text, size, colour):
    font = ImageFont.truetype(BOLD, size)
    draw.text((cx - draw.textlength(text, font=font) / 2, y), text, font=font, fill=colour)


def main(shot, logo_path, out):
    im = Image.open(shot).convert("RGB")
    tile(im, INNER, BLANK)
    tile(im, LABEL, FACE)
    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.crop(logo.getbbox())
    logo.thumbnail((250, 80), Image.LANCZOS)
    cx = (PANEL[0] + PANEL[2]) // 2
    im.paste(logo, (cx - logo.width // 2, 72), logo)
    draw = ImageDraw.Draw(im)
    for i, line in enumerate(LINES):
        centred(draw, cx, 160 + i * 17, line, 13, GREEN)
    centred(draw, cx, 210, BUTTON, 16, BRIGHT)
    im.save(out, quality=94)
    print("wrote", out)


if __name__ == "__main__":
    main(*sys.argv[1:4])
