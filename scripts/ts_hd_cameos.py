#!/usr/bin/env python3
"""Install the HD sidebar cameos (resources/custom-art/ts-hd-cameos/BuildIcon_*.png, 341x256, from the HD
art chat) into the TS-HD-Graphics-Pack, then rebake every badged, locked and countdown variant from them.

Each PNG becomes BuildIcon_<name>.tga in the TS-HD pack, beside the classic cameo in TS-Graphics-Pack;
staging copies the HD one (scripts/stage_asset_packs.py) and the bakers read it (asset_packs.cameo_source).
The units the Dropship Bay delivers get its HD cameo as an inset, bottom right, above the sidebar's name band.

Usage: ts_hd_cameos.py
License: GPL v3.
"""
import glob
import json
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs  # noqa: E402
import cameo_badge_build  # noqa: E402
import ts_mk2_cooldown_cameos  # noqa: E402

SRC = os.path.join(asset_packs.REPO, "resources", "custom-art", "ts-hd-cameos")
SRGB = os.path.join(asset_packs.pack_data("TS-HD-Graphics-Pack"), "ART", "TEXTURES", "SRGB")
BAY_DELIVERED = {"BuildIcon_TS_MammothMk2", "BuildIcon_TS_MechDivision"}
BAY_ICON = "BuildIcon_TS_Drop"
NAME_BAND_TOP = 195  # the launcher's name band covers the cameo below this row (UI_SIDEBAR_CONSTRUCTIONENTRY.BUI)
INSET = (100, 75)


def users(icons):
    """The IniNames whose sidebar entry shows one of these cameos."""
    plain = json.loads(cameo_badge_build.ICON_MAP.read_text(encoding="utf-8"))
    return sorted(e[3:] for e, icon in cameo_badge_build.pristine_sources(plain).items() if icon in icons)


def bay_badge(img):
    """The Dropship Bay's cameo in a gold frame, laid in the bottom-right corner above the name band."""
    w, h = INSET
    badge = Image.new("RGBA", (w + 6, h + 6))
    draw = ImageDraw.Draw(badge)
    draw.rectangle([0, 0, w + 5, h + 5], fill=(20, 18, 10, 255))
    draw.rectangle([1, 1, w + 4, h + 4], fill=(212, 170, 60, 255))
    bay = Image.open(os.path.join(SRC, f"{BAY_ICON}.png")).convert("RGBA").resize((w, h), Image.LANCZOS)
    badge.paste(bay, (3, 3))
    img.alpha_composite(badge, (img.width - badge.width - 6, NAME_BAND_TOP - badge.height - 4))
    return img


def main():
    os.makedirs(SRGB, exist_ok=True)
    icons = set()
    for png in sorted(glob.glob(os.path.join(SRC, "BuildIcon_*.png"))):
        stem = os.path.splitext(os.path.basename(png))[0]
        img = Image.open(png).convert("RGBA")
        if img.size != (341, 256):
            sys.exit(f"{stem}: {img.size[0]}x{img.size[1]}, a cameo is 341x256")
        if stem in BAY_DELIVERED:
            img = bay_badge(img)
        img.save(os.path.join(SRGB, f"{stem}.tga"))
        icons.add(stem)
    print(f"installed {len(icons)} HD cameos into {SRGB}")
    inis = users(icons)
    cameo_badge_build.main(inis)
    if any(icon in icons for icon, _ in ts_mk2_cooldown_cameos.LOCKED.values()):
        ts_mk2_cooldown_cameos.bake_locked()
    if any(icon in icons for icon in ts_mk2_cooldown_cameos.UNITS.values()):
        ts_mk2_cooldown_cameos.bake_art()


if __name__ == "__main__":
    main()
