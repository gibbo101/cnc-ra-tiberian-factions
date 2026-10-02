#!/usr/bin/env python3
"""The sidebar side of the TS Mobile Sensor Array ([LPST], TSLPST) and of the sensor it deploys into
([GADPSA], TSDPSA): BuildIcon_TS_SensorArray.tga, the base RA_TSLPST / RA_TSDPSA entries and the
ModText rows. Their art is the HD rebuilds', packed by scripts/ts_pack_hd_buildings.py. The cameo
and sidebar entries go to the tree asset_packs.py routes each name to; the ModText rows to the
mod's own ModText.csv. Follow with the cameo badge and variant scripts.

Inputs (set TS_ART_DIR): .raw/LPSTICON.SHP and CAMEO.PAL (scripts/ts_rebuild_art.sh extracts them).

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
import ts_pack_limpet as limp

ART = inf.ART
RAW = f"{ART}/.raw"


def cameo():
    pal = ts_shp.load_pal(f"{RAW}/CAMEO.PAL")
    (_, _), raw = ts_shp.decode_shp(f"{RAW}/LPSTICON.SHP")
    icon = ts_shp.frame_to_rgba(raw[0], pal, remap=None)
    flat = Image.new("RGBA", icon.size, (0, 0, 0, 255))
    flat.alpha_composite(icon)
    big = flat.resize((flat.width * 8, flat.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
    path = asset_packs.cameo_tga("BuildIcon_TS_SensorArray")
    big.save(path)
    print(f"wrote {path}")


def main():
    cameo()
    inf.sidebar("TSLPST", "BuildIcon_TS_SensorArray")
    inf.text_rows("TSLPST", "Mobile Sensor Array",
                  "Unarmed support vehicle. Deploys into a sensor that shows you cloaked and "
                  "underground enemies nearby. Deploy again to move it.")
    limp.sidebar_building("TSDPSA", "BuildIcon_TS_SensorArray")
    limp.text_rows_building("TSDPSA", "Sensor Array",
                            "A deployed Mobile Sensor Array. Shows you cloaked and underground "
                            "enemies nearby. Deploy again to pack it up.")


if __name__ == "__main__":
    main()
