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
import os, shutil, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import td_map_to_ra

REPO = Path(__file__).resolve().parent.parent
GAME = Path.home() / ".steam/steam/steamapps/common/CnCRemastered"
TD_COMMUNITY = GAME / "Data/CNCDATA/TIBERIAN_DAWN/COMMUNITY"
TD_GENERAL = GAME / "Data/CNCDATA/TIBERIAN_DAWN/CD1/GENERAL.MIX"
TD_COVERTOPS = GAME / "Data/CNCDATA/TIBERIAN_DAWN/CD1/SC-001.MIX"
BUNDLE = REPO / "resources/remaster_mods/Vanilla_RA/CustomMaps"

# (source, bundle index, display name). Source = loose COMMUNITY ini stem,
# or "mix:<stem>" for the classic MP maps inside GENERAL.MIX (ini+bin).
# Display name shows in the lobby's custom list; keep the player count and
# the TF tag visible (the maps persist in Documents even without the mod).
# All TEMPERATE sources; winter/desert wait on their theatre work.
MAPS = [
    ("SCMC2EA", 1, "TD Elevation (2) [TF]"),
    ("SCMC3EA", 2, "TD Heavy Metal (4) [TF]"),
    ("mix:scm01ea", 3, "TD Green Acres (8) [TF]"),
    ("mix:scm03ea", 4, "TD Lost Arena (8) [TF]"),
    ("mix:scm04ea", 5, "TD River Raid (6) [TF]"),
    ("mix:scm08ea", 6, "TD Pitfall (8) [TF]"),
    ("mix:scm71ea", 7, "TD One Pass Fits All (6) [TF]"),
    ("mix:scm73ea", 8, "TD King Takes Pawn (6) [TF]"),
    ("mix:scm96ea", 9, "TD Tiberium Garden (6) [TF]"),
    # Covert Operations additions (SC-001.MIX)
    ("mix:scm50ea", 10, "TD Emerald Highlands (8) [TF]"),
    ("mix:scm61ea", 11, "TD King of the Mountain (8) [TF]"),
    ("mix:scm62ea", 12, "TD Surgical Incision (7) [TF]"),
    ("mix:scm75ea", 13, "TD Village of the Unfortunate (6) [TF]"),
    ("mix:scm90ea", 14, "TD A Long Way from Home (6) [TF]"),
]


def ugc_stem(index):
    return f"UGC_F1BE000000000{index:03X}_000000000000{index:04X}_MAPDATA"


def main():
    BUNDLE.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp())
    for src, index, name in MAPS:
        out = work / f"map{index}.mpr"
        if src.startswith("mix:"):
            stem = src[4:]
            for ext in (".ini", ".bin"):
                got = False
                for mix in (TD_GENERAL, TD_COVERTOPS):
                    r = subprocess.run([sys.executable, str(REPO / "scripts/mix_tools.py"),
                                        "extract", str(mix), stem + ext, str(work)],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    if r.returncode == 0 and (work / (stem + ext)).exists():
                        got = True
                        break
                assert got, f"{stem}{ext} not found in GENERAL.MIX or SC-001.MIX"
            src_ini = work / (stem + ".ini")
        else:
            src_ini = TD_COMMUNITY / f"{src}.INI"
        td_map_to_ra.convert(str(src_ini), str(out), name)
        stem = ugc_stem(index)
        for ext_src, ext_dst in ((".mpr", ".MPR"), (".json", ".JSON"), (".tga", ".TGA")):
            shutil.copy(out.with_suffix(ext_src), BUNDLE / (stem + ext_dst))
        print(f"bundled {name} -> {stem}")
    print(f"\n{len(MAPS)} maps in {BUNDLE}")
    print("NEXT: rebuild (cmake workflow) + deploy; DLL installs them on first mod load")


if __name__ == "__main__":
    main()
