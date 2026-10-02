#!/usr/bin/env python3
"""Package the TS Mobile Sensor Array ([LPST]) and the entries of the sensor it deploys into ([GADPSA]).

  TSLPST.ZIP (units)            32 frames: the LPST.VXL hull, one per facing, on a 384 canvas
                                (ShapeSize 48) at the TS voxel density 6.4/12 (ts_pack_memp.py).
  BuildIcon_TS_SensorArray.tga, the base RA_TSLPST / RA_TSDPSA entries and the ModText rows.
The sensor's own art (TSDPSA, TSDPSAMAKE) is its HD rebuild, packed by scripts/ts_pack_hd_buildings.py.
Art, cameo, tiles and sidebar entries go to the tree asset_packs.py routes each name to (the
TS-Graphics-Pack); the ModText rows to the mod's own ModText.csv.

Render (the voxel ledger in docs/launcher-render-contracts.md):
  vxl_render.py LPST.VXL renders_lpst --frames 32 --yaw0 90 --px-per-voxel 12
      --team-green 0,380,0 --elev 32 --hva LPST.HVA --canvas 720
(0,380,0: TS painted it in dark remap shades; the fleet's 0,200,0 read at half the APC's team colour)
Follow with scripts/ts_reshadow.py TSLPST, then the cameo badge and variant scripts.

Inputs (set TS_ART_DIR): renders_lpst, .raw/LPSTICON.SHP and CAMEO.PAL (scripts/ts_rebuild_art.sh extracts them all).

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
from ts_pack_memp import vox_frames

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
    unit = vox_frames("renders_lpst")
    inf.write_zip(asset_packs.art_zip("TSLPST", "UNITS"), "tslpst", unit)
    inf.patch_tileset("TSLPST", len(unit))


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
