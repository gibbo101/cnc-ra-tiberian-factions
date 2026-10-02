#!/usr/bin/env python3
"""The sidebar side of the TS Juggernaut (Firestorm, TSJUGG): BuildIcon_TS_Juggernaut.tga, the base
RA_TSJUGG sidebar entry and the ModText rows (cameo and sidebar entry in the tree asset_packs.py
routes each name to; ModText in the mod). Its art is the HD rebuild's, packed by
scripts/ts_pack_hd_buildings.py with its fire points (redalert/tsjugg_muzzle.h), 202 frames:
  0-119    walk: 8 facings (CCW from N) x 15 steps
  120-151  deployed at rest, 32 facings (CCW from N)
  152-183  deployed aiming, the barrels raised 45 degrees
  184-201  the deploy (18 frames), played backwards to pack up
Inputs (set TS_ART_DIR): shp_juggicon (CAMEO.PAL, --no-remap).
License: GPL v3.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ts_pack_infantry as inf


def main():
    inf.cameo("juggicon", "BuildIcon_TS_Juggernaut")
    inf.sidebar("TSJUGG", "BuildIcon_TS_Juggernaut")
    inf.text_rows("TSJUGG", "Juggernaut",
                  "Long-range walking artillery. Sets down to fire three shells and packs up to move.")


if __name__ == "__main__":
    main()
