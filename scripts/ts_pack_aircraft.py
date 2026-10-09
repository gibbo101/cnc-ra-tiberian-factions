#!/usr/bin/env python3
"""The sidebar side of the TS aircraft (Orca Fighter, Orca Bomber, Carryall, Orca Transport):
  - BuildIcon_TS_<Name>.tga from the TS cameo (CAMEO.PAL, no remap), the base RA_<INI>
    entry in TSBUILDABLES.XML, and the ModText rows.
  Their art is the HD rebuilds', packed by scripts/ts_pack_hd_buildings.py: 32 facings on a square
  canvas (ShapeSize x 8), no baked shadow, as aircraft get the engine's air shadow.
  Cameos and XML go to the tree asset_packs.py routes each name to.
Inputs (set TS_ART_DIR):
  $TS_ART_DIR/shp_orcaicon|shp_obmbicon|shp_otrnicon|shp_crryicon/frame-0000.png (ts_shp.py --no-remap)
Then: faction_masks.txt <INI> 16, cameo_badge_build.py <INI>, cameo_variants_build.py.
License: GPL v3.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ts_pack_infantry as inf   # cameo, sidebar, text_rows

# ini -> (cameo stem, icon name, display name, description)
AIRCRAFT = {
    "TSORCA": ("orcaicon", "BuildIcon_TS_OrcaFighter", "Orca Fighter",
               "VTOL gunship. Fires Hellfire missiles at ground and air, and rearms at the Helipad."),
    "TSORCAB": ("obmbicon", "BuildIcon_TS_OrcaBomber", "Orca Bomber",
                "Heavy VTOL bomber. Drops its bombs from over the target and rearms at the Helipad."),
    "TSCARRY": ("otrnicon", "BuildIcon_TS_Carryall", "Carryall",
                "Unarmed VTOL transport. Lifts one vehicle and sets it down where you send it."),
    "TSORCATRAN": ("crryicon", "BuildIcon_TS_OrcaTransport", "Orca Transport",
                   "Unarmed VTOL transport. Carries five infantry, landing to load and unload them."),
}


def pack(ini):
    cameo_stem, icon, display, desc = AIRCRAFT[ini]
    inf.cameo(cameo_stem, icon)
    inf.sidebar(ini, icon)
    inf.text_rows(ini, display, desc)


if __name__ == "__main__":
    for ini in (sys.argv[1:] or list(AIRCRAFT)):
        pack(ini)
