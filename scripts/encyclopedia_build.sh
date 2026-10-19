#!/usr/bin/env bash
# Build the encyclopedia's files into the mod's Data (docs/encyclopedia.md): the stats plate from the game's
# TEXTURES_SRGB.MEG (encyclopedia_art.py), the screen and list row from the CAMPAIGNS page's files
# (bui_encyclopedia_build.py; run campaigns_page_build.sh first), the faction logos and the live picture's canvas
# (encyclopedia_logos.py) and the descriptions in ModText.csv (encyclopedia_text.py). Idempotent.
set -euo pipefail
cd "$(dirname "$0")/.."

DATA=resources/remaster_mods/Vanilla_RA/Data
SRGB="$DATA/ART/TEXTURES/SRGB"
TEXTURES_MEG="$(python3 scripts/steam_library.py path common/CnCRemastered/Data/TEXTURES_SRGB.MEG)"

STOCK="$(mktemp -d)"
trap 'scripts/clear_dir.sh "$STOCK"' EXIT
for t in UI_MISSIONSELECT_BG.DDS UI_LOADGAME_BG_SCANLINES.DDS; do
    python3 scripts/meg_extract.py extract "$TEXTURES_MEG" "DATA\\ART\\TEXTURES\\SRGB\\$t" "$STOCK" >/dev/null
done
echo "==> Stats plate"
(cd scripts && python3 encyclopedia_art.py "$STOCK" "../$SRGB")
echo "==> Screen and list row"
(cd scripts && python3 bui_encyclopedia_build.py "../$DATA/ART/GUI/RA/RA_MISSIONSELECT.BUI" \
    "../$DATA/ART/GUI/RA/RA_MISSIONSELECT_LISTENTRY.BUI" bui_work/RA_MAIN_MENU.edited.BUI "../$DATA/ART/GUI/RA")
echo "==> Logos and canvas"
(cd scripts && python3 encyclopedia_logos.py "../$SRGB")
echo "==> Descriptions"
python3 scripts/encyclopedia_text.py
