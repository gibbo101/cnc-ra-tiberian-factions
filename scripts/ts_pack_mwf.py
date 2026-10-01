#!/usr/bin/env python3
"""Package the TS Mobile War Factory (Firestorm [MOBWARG]) as TSMWAR.

  TSMWAR.ZIP (units)   32 frames: the MWAR_NOD.VXL hull, one per facing, on a 384 canvas
                       (ShapeSize 48) at the TS voxel density 6.4/12 (ts_pack_memp.py).
  BuildIcon_TS_MobileWarFactory.tga, the base RA_TSMWAR sidebar entry and the ModText rows.
Art, cameo, tiles and sidebar entry go to the tree asset_packs.py routes each name to (the
TS-Graphics-Pack); the ModText rows to the mod's own ModText.csv.

Render (the voxel ledger in docs/launcher-render-contracts.md):
  vxl_render.py MWAR_NOD.VXL renders_mwar --frames 32 --yaw0 90 --px-per-voxel 12
      --team-green 0,560,0 --elev 32 --hva MWAR_NOD.HVA --canvas 900
TS painted this hull in its darkest remap shades, so the fleet's 0,200,0 left it a third as bright as
the APC's team colour; 0,560,0 lifts every shade to full and the team pixels plateau at about 160
(APC 185), the closest this model gets.
Follow with scripts/ts_reshadow.py TSMWAR, then the cameo badge and variant scripts.

Inputs (set TS_ART_DIR): renders_mwar, .raw/MWARICON.SHP and CAMEO.PAL. MWAR_NOD.VXL/HVA sit at
the top of the TS install's expand01.mix, MWARICON in its E01SC01.MIX (scripts/ts_rebuild_art.sh).

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
from ts_pack_memp import vox_frames

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
    unit = vox_frames("renders_mwar")
    inf.write_zip(asset_packs.art_zip("TSMWAR", "UNITS"), "tsmwar", unit)
    inf.patch_tileset("TSMWAR", len(unit))
    cameo()
    inf.sidebar("TSMWAR", "BuildIcon_TS_MobileWarFactory")
    inf.text_rows("TSMWAR", "Mobile War Factory",
                  "Slow, heavily armoured vehicle. Deploys into a war factory wherever you need one. "
                  "One at a time.")


if __name__ == "__main__":
    main()
