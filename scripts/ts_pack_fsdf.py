#!/usr/bin/env python3
"""The Firestorm Wall Section's cameo, BuildIcon_TS_Fsdf.tga, from TS's FSPICON, for the TS-Graphics-Pack
(asset_packs.py routes it). The section's art is the HD rebuild's, packed by scripts/ts_pack_hd_buildings.py.

Inputs: $TS_ART_DIR/shp_fspicon (scripts/ts_rebuild_art.sh).
Usage: TS_ART_DIR=~/Desktop/ts-art scripts/ts_pack_fsdf.py
License: GPL v3.
"""
import os, sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR")


def main():
    icon = os.path.join(ART, "shp_fspicon", "frame-0000.png")
    if os.path.exists(icon):
        im = Image.open(icon)
        big = im.resize((im.width * 8, im.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
        big.save(asset_packs.cameo_tga("BuildIcon_TS_Fsdf"))
        print("wrote BuildIcon_TS_Fsdf.tga")


if __name__ == "__main__":
    main()
