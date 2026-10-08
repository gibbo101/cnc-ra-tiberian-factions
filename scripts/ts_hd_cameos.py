#!/usr/bin/env python3
"""Install the HD sidebar cameos (resources/custom-art/ts-hd-cameos/BuildIcon_*.png, 341x256, from the HD
art chat) into the TS-HD-Graphics-Pack, then rebake every badged and locked variant from them.

Each PNG becomes BuildIcon_<name>.tga in the TS-HD pack, beside the classic cameo in TS-Graphics-Pack;
staging copies the HD one (scripts/stage_asset_packs.py) and the bakers read it (asset_packs.cameo_source).

Usage: ts_hd_cameos.py
License: GPL v3.
"""
import glob
import json
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs  # noqa: E402
import cameo_badge_build  # noqa: E402
import ts_mk2_cooldown_cameos  # noqa: E402

SRC = os.path.join(asset_packs.REPO, "resources", "custom-art", "ts-hd-cameos")
SRGB = os.path.join(asset_packs.pack_data("TS-HD-Graphics-Pack"), "ART", "TEXTURES", "SRGB")


def users(icons):
    """The IniNames whose sidebar entry shows one of these cameos."""
    plain = json.loads(cameo_badge_build.ICON_MAP.read_text(encoding="utf-8"))
    return sorted(e[3:] for e, icon in cameo_badge_build.pristine_sources(plain).items() if icon in icons)


def main():
    os.makedirs(SRGB, exist_ok=True)
    icons = set()
    for png in sorted(glob.glob(os.path.join(SRC, "BuildIcon_*.png"))):
        stem = os.path.splitext(os.path.basename(png))[0]
        img = Image.open(png).convert("RGBA")
        if img.size != (341, 256):
            sys.exit(f"{stem}: {img.size[0]}x{img.size[1]}, a cameo is 341x256")
        img.save(os.path.join(SRGB, f"{stem}.tga"))
        icons.add(stem)
    print(f"installed {len(icons)} HD cameos into {SRGB}")
    inis = users(icons)
    cameo_badge_build.main(inis)
    if any(icon in icons for icon, _ in ts_mk2_cooldown_cameos.LOCKED.values()):
        ts_mk2_cooldown_cameos.bake_locked()


if __name__ == "__main__":
    main()
