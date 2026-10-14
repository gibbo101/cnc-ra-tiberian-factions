#!/usr/bin/env python3
"""The sidebar side of the TS Tick Tank (TSTTNK) and its dug-in form (TSTICK): TS's cameo, their buildables XML
entries and ModText rows. Their art is the HD rebuilds', packed by scripts/ts_pack_hd_buildings.py.

Inputs (set TS_ART_DIR to a folder holding them, from TIBSUN.MIX: CONQUER.MIX and CACHE.MIX):
  $TS_ART_DIR/TICKICON.SHP + CAMEO.PAL

Usage: TS_ART_DIR=... ts_pack_ttnk.py
License: GPL v3.
"""
import os
import sys

import hqx
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs
import ts_shp

if not os.environ.get("TS_ART_DIR"):
    raise SystemExit("set TS_ART_DIR to the folder holding TICKICON.SHP and CAMEO.PAL")
import ts_pack_infantry as inf  # noqa: E402

ART = inf.ART
ICON = "BuildIcon_TS_TickTank"


def cameo():
    """TS's cameo through CAMEO.PAL as shipped (its 16-31 is Nod's red ramp), hq4x as the house policy."""
    pal = ts_shp.load_pal(f"{ART}/CAMEO.PAL")
    _, frames = ts_shp.decode_shp(f"{ART}/TICKICON.SHP")
    icon = ts_shp.frame_to_rgba(frames[0], pal, remap=None)
    big = hqx.hq4x(icon.convert("RGB")).convert("RGBA").resize((341, 256), Image.LANCZOS)
    asset_packs.save_classic_cameo(big, ICON)


if __name__ == "__main__":
    cameo()
    inf.sidebar("TSTTNK", ICON)
    inf.text_rows("TSTTNK", "Tick Tank", "Nod tank that digs in for heavy armour. Deploy to dig in.")
    inf.sidebar("TSTICK", ICON, kind="STRUCTURE")
    inf.text_rows("TSTICK", "Deployed Tick Tank", "A Tick Tank dug in. Deploy again to dig it out.", kind="STRUCTURE")
