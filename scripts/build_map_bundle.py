#!/usr/bin/env python3
"""
Bundled custom-map builder (Tiberian Factions mod).

Delivery model (decided 2026-06-09 after the official-list bisect):
converted TD maps ship INSIDE the mod at <mod>/CustomMaps/ as
Local_Custom_Maps triplets (mpr + tga + json) under synthetic UGC
filenames. The DLL self-installs them into the user's
Documents/CnCRemastered/Local_Custom_Maps/Red_Alert/ when the launcher
registers the mod path (TF_Install_Bundled_Maps, dllinterface.cpp) -- they
appear in the lobby's CUSTOM maps list with our own preview art. Official-
list delivery was rejected: a mod cannot add instances (server resolves
from base data) and slot-hijacking shows the wrong lobby thumbnail.

The maps are VANILLA-SAFE: the transcoder keeps [MapPack] free of TD-ported
template ids (those cells ship in the [TFTDTiles] side-channel only our DLL
reads), so an installed map still loads under vanilla RA -- just with plain
clear shorelines -- if the mod is later disabled.

Synthetic UGC ids use a recognizable F1BE ("TIBE") prefix that no real
Steam UGC handle or other tool will collide with.

Usage: python3 scripts/build_map_bundle.py
Then:  rebuild (cmake workflow) + deploy. Adding a map = add a MAPS row.
"""
import os, shutil, sys, tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import td_map_to_ra

REPO = Path(__file__).resolve().parent.parent
TD_COMMUNITY = (Path.home()
                / ".steam/steam/steamapps/common/CnCRemastered/Data/CNCDATA/TIBERIAN_DAWN/COMMUNITY")
BUNDLE = REPO / "resources/remaster_mods/Vanilla_RA/CustomMaps"

# (TD source ini, bundle index, display name)
# Display name shows in the lobby's custom list; keep the player count and
# the TF tag visible (the maps persist in Documents even without the mod).
MAPS = [
    ("SCMC2EA", 1, "TD Elevation (2) [TF]"),
    ("SCMC3EA", 2, "TD Heavy Metal (4) [TF]"),
]


def ugc_stem(index):
    return f"UGC_F1BE000000000{index:03X}_000000000000{index:04X}_MAPDATA"


def main():
    BUNDLE.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp())
    for src, index, name in MAPS:
        out = work / f"map{index}.mpr"
        td_map_to_ra.convert(str(TD_COMMUNITY / f"{src}.INI"), str(out), name)
        stem = ugc_stem(index)
        for ext_src, ext_dst in ((".mpr", ".MPR"), (".json", ".JSON"), (".tga", ".TGA")):
            shutil.copy(out.with_suffix(ext_src), BUNDLE / (stem + ext_dst))
        print(f"bundled {name} -> {stem}")
    print(f"\n{len(MAPS)} maps in {BUNDLE}")
    print("NEXT: rebuild (cmake workflow) + deploy; DLL installs them on first mod load")


if __name__ == "__main__":
    main()
