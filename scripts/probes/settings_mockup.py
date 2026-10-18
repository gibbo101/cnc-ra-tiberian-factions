#!/usr/bin/env python3
"""Mockups of the TIBERIAN FACTIONS SETTINGS page's AUDIO tab, painted over an in-game ADD-ONS screenshot.

Usage: settings_mockup.py <ADD-ONS screenshot 1920x1080> <encyclopedia screenshot> <out dir>
       settings_mockup.py s4 <out dir>   (S4, painted over the S2 mockups)
Writes S1 (soundtrack list + a row per faction) and S2 (encyclopedia-style faction tabs), each with TS-Music
loaded and missing.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRGB = os.path.join(REPO, "resources", "remaster_mods", "Vanilla_RA", "Data", "ART", "TEXTURES", "SRGB")
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
COND = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
HEAD = (151, 255, 109)
TEXT = (46, 192, 0)
DIM = (40, 150, 6)
AMBER = (255, 176, 40)
GREY = (120, 128, 132)
FACTIONS = [("ALLIES", "ALLIES", "RED ALERT"), ("SOVIETS", "SOVIETS", "RED ALERT"), ("GDI", "GDI", "TIBERIAN DAWN"),
            ("NOD", "NOD", "TIBERIAN DAWN"), ("TS GDI", "TSGDI", "TIBERIAN SUN")]
SOUNDTRACKS = [("MIX", "Every track, shuffled (the default)"), ("FACTION", "Each faction plays its own music"),
               ("RED ALERT", "Red Alert's tracks only"), ("TIBERIAN DAWN", "Tiberian Dawn's tracks only"),
               ("TIBERIAN SUN", "Tiberian Sun and Firestorm's tracks only")]


def font(size, path=BOLD):
    return ImageFont.truetype(path, size)


def crest(name, size):
    """A faction's gold crest from the encyclopedia's About rows."""
    im = Image.open(os.path.join(SRGB, f"TF_ENC_ABOUT_{name}.TGA")).convert("RGBA")
    return im.resize((size, size), Image.LANCZOS)


def fill(base, box, tile_box):
    """Covers `box` with copies of the blank panel area `tile_box` of `base`."""
    tile = base.crop(tile_box)
    x0, y0, x1, y1 = box
    for y in range(y0, y1, tile.height):
        for x in range(x0, x1, tile.width):
            base.paste(tile.crop((0, 0, min(tile.width, x1 - x), min(tile.height, y1 - y))), (x, y))


def centred(draw, cx, y, text, size, colour, path=BOLD):
    f = font(size, path)
    w = draw.textlength(text, font=f)
    draw.text((cx - w / 2, y), text, font=f, fill=colour)


def row(draw, box, selected):
    draw.rounded_rectangle(box, radius=6, fill=(21, 58, 10) if selected else (14, 40, 9),
                           outline=HEAD if selected else (6, 22, 4), width=3 if selected else 2)


def radio(draw, cx, cy, on, colour=HEAD):
    draw.ellipse((cx - 11, cy - 11, cx + 11, cy + 11), outline=colour, width=3)
    if on:
        draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=colour)


def button(draw, box, label, size=24, colour=HEAD, fill_colour=(14, 32, 36), outline=(70, 96, 104)):
    draw.rectangle(box, fill=fill_colour, outline=outline, width=3)
    centred(draw, (box[0] + box[2]) / 2, (box[1] + box[3]) / 2 - size * 0.62, label, size, colour)


def frame(addons):
    """The ADD-ONS screen with its title, tabs and instructions cleared, and both panels holding an empty list."""
    im = addons.copy()
    d = ImageDraw.Draw(im)
    fill(im, (520, 112, 1400, 175), (395, 112, 455, 175))
    centred(d, 960, 116, "TIBERIAN FACTIONS SETTINGS", 46, (215, 220, 222))
    fill(im, (330, 210, 1300, 274), (1310, 210, 1360, 274))
    button(d, (344, 222, 644, 266), "AUDIO", 24, HEAD, (24, 52, 40), HEAD)
    button(d, (672, 222, 972, 266), "GAME RULES", 24, GREY, (24, 34, 38), (52, 64, 70))
    fill(im, (330, 300, 1600, 370), (1500, 300, 1560, 370))
    d.text((344, 306), "Music for skirmish and LAN games. A change plays from the next track.", font=font(19),
           fill=TEXT)
    fill(im, (330, 420, 930, 470), (870, 420, 920, 470))
    fill(im, (331, 488, 929, 928), (340, 640, 920, 920))
    fill(im, (990, 420, 1605, 470), (1540, 420, 1590, 470))
    im.paste(im.crop((326, 478, 934, 936)), (988, 478))
    return im, d


def s1(addons, ts_loaded):
    im, d = frame(addons)
    centred(d, 627, 428, "SOUNDTRACK", 28, HEAD)
    for i, (name, about) in enumerate(SOUNDTRACKS):
        y = 500 + i * 84
        row(d, (340, y, 915, y + 74), i == 0)
        radio(d, 372, y + 37, i == 0)
        d.text((400, y + 9), name, font=font(24), fill=HEAD if i == 0 else TEXT)
        needs = name == "TIBERIAN SUN" and not ts_loaded
        d.text((400, y + 42), "Needs the Tiberian Sun Music add-on" if needs else about, font=font(17, COND),
               fill=AMBER if needs else DIM if i else TEXT)
    centred(d, 1297, 428, "FACTION MUSIC", 28, HEAD)
    d.text((1004, 494), "When the soundtrack is FACTION:", font=font(17, COND), fill=TEXT)
    for i, (label, key, music) in enumerate(FACTIONS):
        y = 522 + i * 76
        row(d, (1000, y, 1595, y + 68), False)
        im.paste(crest(key, 54), (1010, y + 7), crest(key, 54))
        d.text((1078, y + 19), label, font=font(24), fill=HEAD)
        if music == "TIBERIAN SUN" and not ts_loaded:
            button(d, (1300, y + 12, 1582, y + 58), "GET ADD-ON", 22, AMBER, (40, 30, 10), AMBER)
            continue
        d.text((1290, y + 21), "◀", font=font(22), fill=HEAD)
        centred(d, 1435, y + 21, music, 21, TEXT)
        d.text((1562, y + 21), "▶", font=font(22), fill=HEAD)
    d.text((1004, 904), "Two spare rows wait for future factions.", font=font(15, COND), fill=DIM)
    button(d, (1185, 960, 1600, 1010), "DEFAULTS", 24)
    return im


def s2(addons, enc, ts_loaded):
    im, d = frame(addons)
    fill(im, (330, 272, 1600, 384), (1500, 300, 1560, 370))
    tabs = enc.crop((360, 255, 1310, 372))
    tabs = tabs.resize((int(tabs.width * 0.9), int(tabs.height * 0.9)), Image.LANCZOS)
    im.paste(tabs, (344, 274))
    for x in (1240, 1370):
        d.rectangle((x, 336, x + 110, 374), outline=(52, 64, 70), width=2)
    centred(d, 1360, 290, "MORE TO COME", 21, GREY)
    centred(d, 627, 428, "SOUNDTRACK", 28, HEAD)
    for i, (name, about) in enumerate(SOUNDTRACKS):
        y = 500 + i * 84
        row(d, (340, y, 915, y + 74), i == 1)
        radio(d, 372, y + 37, i == 1)
        d.text((400, y + 9), name, font=font(24), fill=HEAD if i == 1 else TEXT)
        needs = name == "TIBERIAN SUN" and not ts_loaded
        d.text((400, y + 42), "Needs the Tiberian Sun Music add-on" if needs else about, font=font(17, COND),
               fill=AMBER if needs else DIM if i != 1 else TEXT)
    centred(d, 1297, 428, "GDI PLAYS", 28, HEAD)
    im.paste(crest("GDI", 96), (1249, 498), crest("GDI", 96))
    for i, (name, current) in enumerate([("RED ALERT", False), ("TIBERIAN DAWN", True), ("TIBERIAN SUN", False),
                                         ("MIX", False)]):
        y = 612 + i * 76
        row(d, (1000, y, 1595, y + 66), current)
        radio(d, 1032, y + 33, current)
        d.text((1060, y + 19), name, font=font(23), fill=HEAD if current else TEXT)
        if name == "TIBERIAN SUN" and not ts_loaded:
            button(d, (1370, y + 11, 1585, y + 55), "GET ADD-ON", 19, AMBER, (40, 30, 10), AMBER)
    button(d, (1185, 960, 1600, 1010), "DEFAULTS", 24)
    return im


def wide_box(im):
    """The two panels joined into one: the left list box stretched by its middle across both, under one plate."""
    box = im.crop((326, 478, 934, 936))
    left, mid, right = box.crop((0, 0, 40, box.height)), box.crop((200, 0, 240, box.height)), box.crop(
        (box.width - 40, 0, box.width, box.height))
    fill(im, (318, 404, 1612, 950), (1500, 300, 1560, 370))
    x = 326
    im.paste(left, (x, 478))
    for x in range(366, 1556, 40):
        im.paste(mid, (x, 478))
    im.paste(right, (1556, 478))


def s3(addons, ts_loaded):
    im, d = frame(addons)
    fill(im, (330, 300, 1600, 370), (1500, 300, 1560, 370))
    d.text((344, 306), "Choose the music each faction plays in skirmish and LAN games. MIX plays every soundtrack.",
           font=font(19), fill=TEXT)
    wide_box(im)
    centred(d, 960, 428, "FACTION MUSIC", 28, HEAD)
    choices = ["MIX", "RED ALERT", "TIBERIAN DAWN", "TIBERIAN SUN"]
    for i, (label, key, _) in enumerate(FACTIONS):
        y = 500 + i * 84
        row(d, (340, y, 1580, y + 74), False)
        im.paste(crest(key, 58), (352, y + 8), crest(key, 58))
        d.text((424, y + 22), label, font=font(25), fill=HEAD)
        for j, name in enumerate(choices):
            x = 640 + j * 232
            on = j == 0
            if name == "TIBERIAN SUN" and not ts_loaded:
                button(d, (x, y + 14, x + 218, y + 60), "GET ADD-ON", 19, AMBER, (40, 30, 10), AMBER)
                continue
            button(d, (x, y + 14, x + 218, y + 60), name, 19, HEAD if on else TEXT,
                   (30, 70, 20) if on else (12, 30, 8), HEAD if on else (20, 60, 12))
    d.text((352, 916), "More factions join this list as they arrive.", font=font(16, COND), fill=DIM)
    button(d, (1185, 960, 1600, 1010), "DEFAULTS", 24)
    return im


def scanlines(draw, box):
    """A list box's empty interior: the game's alternating green scanlines."""
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        draw.line((x0, y, x1, y), fill=(18, 46, 12) if y % 2 else (21, 65, 8))


def s4(s2_image, faction, label, ts_loaded):
    """S2's faction tabs over the picked faction's crest (left) and its four music choices (right)."""
    im = s2_image.copy()
    d = ImageDraw.Draw(im)
    fill(im, (330, 420, 930, 470), (870, 420, 920, 470))
    fill(im, (990, 420, 1605, 470), (1540, 420, 1590, 470))
    scanlines(d, (336, 488, 924, 926))
    scanlines(d, (994, 486, 1594, 928))
    centred(d, 627, 428, label, 28, HEAD)
    big = crest(faction, 300)
    im.paste(big, (477, 560), big)
    centred(d, 1290, 428, "MUSIC", 28, HEAD)
    rows = [("MIX", "Every soundtrack, shuffled (the default)"), ("RED ALERT", "Red Alert's tracks only"),
            ("TIBERIAN DAWN", "Tiberian Dawn's tracks only"),
            ("TIBERIAN SUN", "Tiberian Sun and Firestorm's tracks only")]
    for i, (name, about) in enumerate(rows):
        y = 500 + i * 96
        row(d, (1000, y, 1580, y + 84), i == 0)
        radio(d, 1032, y + 42, i == 0)
        d.text((1060, y + 14), name, font=font(25), fill=HEAD if i == 0 else TEXT)
        needs = name == "TIBERIAN SUN" and not ts_loaded
        d.text((1060, y + 50), "Needs its add-on" if needs else about, font=font(17, COND),
               fill=AMBER if needs else TEXT if i == 0 else DIM)
        if needs:
            button(d, (1370, y + 20, 1566, y + 64), "GET ADD-ON", 20, AMBER, (40, 30, 10), AMBER)
    return im


def main(addons_path, enc_path, out):
    os.makedirs(out, exist_ok=True)
    addons = Image.open(addons_path).convert("RGB")
    enc = Image.open(enc_path).convert("RGB")
    for ts, tag in ((True, "ts-loaded"), (False, "ts-missing")):
        s1(addons, ts).save(os.path.join(out, f"mockup-S1-faction-rows-{tag}.jpg"), quality=92)
        s2(addons, enc, ts).save(os.path.join(out, f"mockup-S2-faction-tabs-{tag}.jpg"), quality=92)
        s3(addons, ts).save(os.path.join(out, f"mockup-S3-one-list-{tag}.jpg"), quality=92)
    print("wrote 6 mockups to", out)


if __name__ == "__main__":
    if sys.argv[1] == "s4":
        out = sys.argv[2]
        for ts, tag in ((True, "ts-loaded"), (False, "ts-missing")):
            base = Image.open(os.path.join(out, f"mockup-S2-faction-tabs-{tag}.jpg")).convert("RGB")
            s4(base, "GDI", "GDI", ts).save(os.path.join(out, f"mockup-S4-crest-and-choices-{tag}.jpg"), quality=92)
        print("wrote S4 to", out)
    else:
        main(*sys.argv[1:4])
