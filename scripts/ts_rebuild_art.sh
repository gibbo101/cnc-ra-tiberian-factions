#!/usr/bin/env bash
# Rebuilds $TS_ART_DIR from the Steam Tiberian Sun install: extracts every
# SHP the TS packers consume and decodes it to the shp_<name>/frame-NNNN.png
# layout ts_pack_tree.py expects.
#
# Building bases, their animation SHPs, the *BB apron plates and the war
# factory's door pair (GTWEAP_D shutter stages + GTWEAP_1 under-door bay,
# ART.INI DoorAnim/UnderDoorAnim) live in the temperate theater archive;
# buildups (*MK) in the isometric temperate
# archive; sidebar cameos in CONQUER. Everything decodes against UNITTEM.PAL
# except cameos, which use CAMEO.PAL — the terrain palettes decode to noise.
#
# Usage: TS_ART_DIR=~/Desktop/ts-art scripts/ts_rebuild_art.sh
set -euo pipefail

: "${TS_ART_DIR:?set TS_ART_DIR to the directory to (re)build}"
TIBSUN="${TIBSUN_MIX:-$HOME/.local/share/Steam/steamapps/common/Command & Conquer Tiberian Sun/TIBSUN.MIX}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(dirname "$HERE")"
EXTRACT="$(dirname "$(dirname "$REPO")")/cnc-remastered-mods/tools/ts_extract.py"
[ -f "$EXTRACT" ] || EXTRACT="$(dirname "$REPO")/tools/ts_extract.py"
[ -f "$TIBSUN" ] || { echo "TIBSUN.MIX not found at: $TIBSUN" >&2; exit 1; }
[ -f "$EXTRACT" ] || { echo "ts_extract.py not found at: $EXTRACT" >&2; exit 1; }

RAW="$TS_ART_DIR/.raw"
mkdir -p "$RAW" "$TS_ART_DIR"

TEMPERAT="GTCNST.SHP GTCNST_A.SHP GTCNST_B.SHP GTCNST_C.SHP
          GTDEPT.SHP GTDEPT_A.SHP GTDEPT_B.SHP GTDEPTBB.SHP
          GTHPAD.SHP GTHPAD_A.SHP GTHPADBB.SHP
          GTPILE.SHP GTPILE_A.SHP GTPILE_B.SHP GTPILE_C.SHP
          GTPOWR.SHP GTPOWR_A.SHP GTPOWR_B.SHP
          GTRADR.SHP GTRADR_A.SHP
          GTSILO.SHP
          GTTECH.SHP GTTECH_A.SHP
          GTWEAP.SHP GTWEAP_A.SHP GTWEAP_B.SHP GTWEAP_C.SHP GTWEAPBB.SHP
          GTWEAP_D.SHP GTWEAP_1.SHP
          NTREFN.SHP NTREFN_A.SHP NTREFN_B.SHP NTREFN_C.SHP NTREFNBB.SHP
          GTPLUG.SHP GTPLUG_A.SHP GTPLUG_B.SHP GTPLUG_C.SHP GTPLUG_E.SHP GTPLUG_F.SHP"

ISOTEMP="GTCNSTMK.SHP GTDEPTMK.SHP GTHPADMK.SHP GTPILEMK.SHP GTPOWRMK.SHP
         GTRADRMK.SHP GTSILOMK.SHP GTTECHMK.SHP GTWEAPMK.SHP NTREFNMK.SHP
         GTPLUGMK.SHP"

CONQUER="BRRKICON.SHP HELIICON.SHP RADRICON.SHP TECHICON.SHP WEAPICON.SHP TURBICON.SHP
         PLUGICON.SHP SEEKICON.SHP IONCICON.SHP"

# The remaining cameos live in the per-side sidebar archives rather than
# CONQUER. SIDEC01 is GDI, SIDEC02 Nod; all three take the GDI variant, the
# refinery included — its cameo differs between sides even though the tree
# builds the structure itself from Nod's NTREFN art.
SIDEC01="FIXICON.SHP REFICON.SHP SILOICON.SHP MCVICON.SHP"

echo "== extracting =="
python3 "$EXTRACT" "$TIBSUN" CACHE.MIX    extract "$RAW" UNITTEM.PAL CAMEO.PAL >/dev/null
python3 "$EXTRACT" "$TIBSUN" TEMPERAT.MIX extract "$RAW" $TEMPERAT >/dev/null
python3 "$EXTRACT" "$TIBSUN" ISOTEMP.MIX  extract "$RAW" $ISOTEMP  >/dev/null
python3 "$EXTRACT" "$TIBSUN" CONQUER.MIX  extract "$RAW" $CONQUER  >/dev/null
python3 "$EXTRACT" "$TIBSUN" SIDEC01.MIX  extract "$RAW" $SIDEC01  >/dev/null


echo "== decoding =="
decode() { # <shp-name> <palette>
    local stem="${1%.SHP}"
    python3 "$HERE/ts_shp.py" "$RAW/$1" "$RAW/$2" \
        "$TS_ART_DIR/shp_$(echo "$stem" | tr '[:upper:]' '[:lower:]')" >/dev/null
}
for f in $TEMPERAT $ISOTEMP; do decode "$f" UNITTEM.PAL; done
for f in $CONQUER $SIDEC01; do decode "$f" CAMEO.PAL; done

echo "== $(find "$TS_ART_DIR" -maxdepth 1 -type d -name 'shp_*' | wc -l) shp_* dirs in $TS_ART_DIR =="
