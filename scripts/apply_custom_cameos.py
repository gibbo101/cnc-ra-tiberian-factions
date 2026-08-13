#!/usr/bin/env python3
"""Install the hand-made cameos over the packer-generated ones.

resources/custom-cameos/<IconName>.png is the canonical art for any BuildIcon
a human has drawn (Luke's compositions on the reconstructed TS scene
background). The TS packers also generate some of these names from game
assets; they check this directory first, and this script re-asserts every
override in one pass — run it after any packer that touches SRGB, and before
ts_mk2_cooldown_cameos.py, which bakes its countdown sets from the base TGAs.

License: GPL v3.
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CUSTOM = ROOT / "resources/custom-cameos"
SRGB = ROOT / "resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB"

for png in sorted(CUSTOM.glob("*.png")):
    img = Image.open(png).convert("RGBA").resize((341, 256), Image.LANCZOS)
    out = SRGB / f"{png.stem}.tga"
    img.save(out)
    print(f"installed {png.name} -> {out.name}")
