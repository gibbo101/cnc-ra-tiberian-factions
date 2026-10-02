#!/usr/bin/env python3
"""The sidebar side of the TS Mobile War Factory (Firestorm [MOBWARG], TSMWAR):
BuildIcon_TS_MobileWarFactory.tga, the base RA_TSMWAR sidebar entry and the ModText rows. Its art
is the HD rebuild's, packed by scripts/ts_pack_hd_buildings.py. The cameo and sidebar entry go to
the tree asset_packs.py routes each name to; the ModText rows to the mod's own ModText.csv.
Follow with the cameo badge and variant scripts.

Inputs (set TS_ART_DIR): .raw/MWARICON.SHP and CAMEO.PAL. MWARICON sits in the TS install's
E01SC01.MIX (scripts/ts_rebuild_art.sh).

License: GPL v3.
"""
import os
import sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import asset_packs
import ts_shp
import ts_pack_infantry as inf

RAW = f"{inf.ART}/.raw"


def cameo():
    pal = ts_shp.load_pal(f"{RAW}/CAMEO.PAL")
    (_, _), raw = ts_shp.decode_shp(f"{RAW}/MWARICON.SHP")
    icon = ts_shp.frame_to_rgba(raw[0], pal, remap=None)
    flat = Image.new("RGBA", icon.size, (0, 0, 0, 255))
    flat.alpha_composite(icon)
    big = flat.resize((flat.width * 8, flat.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    path = asset_packs.cameo_tga("BuildIcon_TS_MobileWarFactory")
    big.save(path)
    print(f"wrote {path}")


def main():
    cameo()
    inf.sidebar("TSMWAR", "BuildIcon_TS_MobileWarFactory")
    inf.text_rows("TSMWAR", "Mobile War Factory",
                  "Slow, heavily armoured vehicle. Deploys into a war factory wherever you need one. "
                  "One at a time.")


if __name__ == "__main__":
    main()
