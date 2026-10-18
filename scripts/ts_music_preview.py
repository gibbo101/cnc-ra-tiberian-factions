#!/usr/bin/env python3
"""Draws the TS-Music Workshop item's preview, resources/workshop-previews/TS-Music.jpg: the Tiberian Sun logo, MUSIC in
the pack panel's gold (scripts/pack_panel_art.py) and the track count, on dark green scanlines.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

from pack_panel_art import FONT, gold_text

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(SCRIPTS)
LOGO = os.path.join(SCRIPTS, "title_work", "key-art", "tiberiansun-logo_2x.png")
TRACKS = os.path.join(REPO, "asset-packs", "TS-Music", "tracks.json")
OUT = os.path.join(REPO, "resources", "workshop-previews", "TS-Music.jpg")
SIZE = 1024
GREEN = (46, 192, 0)


def main():
    out = Image.new("RGB", (SIZE, SIZE))
    draw = ImageDraw.Draw(out)
    for y in range(SIZE):
        shade = 1 - abs(y - SIZE / 2) / SIZE
        base = (10, 26, 8) if y % 2 else (12, 36, 6)
        draw.line((0, y, SIZE, y), fill=tuple(int(c * (0.6 + 0.6 * shade)) for c in base))
    art = Image.open(LOGO).convert("RGBA")
    art = art.crop(art.getbbox())
    art.thumbnail((SIZE - 160, 420), Image.LANCZOS)
    out.paste(art, ((SIZE - art.width) // 2, 230), art)
    label = gold_text("MUSIC", 130)
    out.paste(label, ((SIZE - label.width) // 2, 680), label)
    tracks = json.load(open(TRACKS))
    games = {t["game"] for t in tracks}
    line = f"{len(tracks)} tracks from Tiberian Sun" + (" and Firestorm" if "FS" in games else "")
    font = ImageFont.truetype(str(FONT), 40)
    width = draw.textlength(line, font=font)
    draw.text(((SIZE - width) / 2, 850), line, font=font, fill=GREEN)
    out.save(OUT, quality=90)
    print("wrote", OUT, os.path.getsize(OUT) // 1024, "KB")


if __name__ == "__main__":
    main()
