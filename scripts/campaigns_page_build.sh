#!/usr/bin/env bash
# Build the CAMPAIGNS page's loose files into the mod's Data (docs/campaigns-page.md), from the
# stock bases in scripts/campaigns_work/ and the game's TEXTURES_SRGB.MEG. Idempotent. The built
# textures and atlas must match scripts/campaigns_work/textures.md5; --lock records new ones.
set -euo pipefail
cd "$(dirname "$0")/.."

DATA=resources/remaster_mods/Vanilla_RA/Data
WORK=scripts/campaigns_work
SRGB="$DATA/ART/TEXTURES/SRGB"
ATLAS="$SRGB/MT_COMMANDBAR_COMMON.TGA"
TEXTURES_MEG="$HOME/.steam/steam/steamapps/common/CnCRemastered/Data/TEXTURES_SRGB.MEG"
TEXTURES="RA_UI_MISSIONSELECT_BG.DDS RA_UI_MISSIONSELECT_BG_BLUE.DDS RA_UI_MISSIONSELECT_BG_RED.DDS
          RA_UI_MISSIONSELECT_SCANLINES_BLUE.DDS RA_UI_MISSIONSELECT_SCANLINES_RED.DDS
          TF_UI_MISSIONSELECT_ITEMLIST_TSGDI_OFF.DDS TF_UI_MISSIONSELECT_ITEMLIST_TSGDI_SELECTED.DDS
          MT_COMMANDBAR_COMMON.TGA"

if [[ ! -f "$ATLAS" ]]; then
    echo "ERROR: no UI atlas at $ATLAS. Copy main's (it is gitignored) before building the page." >&2
    exit 1
fi
STOCK="$(mktemp -d)"
trap 'rm -rf "$STOCK"' EXIT
for t in UI_MISSIONSELECT_BG.DDS UI_LOADGAME_BG_SCANLINES.DDS RA_UI_MISSIONSELECT_BG.DDS MT_COMMANDBAR_COMMON.MTD; do
    python3 scripts/meg_extract.py extract "$TEXTURES_MEG" "DATA\\ART\\TEXTURES\\SRGB\\$t" "$STOCK" >/dev/null
done
MTD="$STOCK/MT_COMMANDBAR_COMMON.MTD"
mkdir -p "$DATA/ART/GUI/RA" "$SRGB" "$DATA/XML"

echo "==> Backgrounds"
python3 scripts/campaigns_backgrounds.py "$STOCK" "$SRGB"
echo "==> Screen and mission row"
python3 scripts/campaigns_screen.py "$WORK/RA_MISSIONSELECT.base.BUI" "$WORK/UI_MISSIONSELECT.base.BUI" \
    "$DATA/ART/GUI/RA/RA_MISSIONSELECT.BUI"
python3 scripts/campaigns_rows.py "$WORK/RA_MISSIONSELECT_LISTENTRY.base.BUI" \
    "$WORK/UI_MISSIONSELECT_LISTENTRY.base.BUI" "$DATA/ART/GUI/RA/RA_MISSIONSELECT_LISTENTRY.BUI"
echo "==> Tab icons and row crests in the UI atlas"
python3 scripts/campaigns_atlas.py "$ATLAS" "$MTD"
python3 scripts/campaigns_row_art.py "$ATLAS" "$MTD" "$STOCK/RA_UI_MISSIONSELECT_BG.DDS" "$SRGB"
echo "==> Stock missions hidden, mod missions added"
python3 scripts/campaigns_instances.py "$WORK/INSTANCES.base.XML" "$WORK/missions.xml" "$DATA/XML/INSTANCES.XML"

if [[ "${1:-}" == "--lock" ]]; then
    (cd "$SRGB" && md5sum $TEXTURES) > "$WORK/textures.md5"
    echo "==> Locked the textures and atlas in $WORK/textures.md5"
elif ! (cd "$SRGB" && md5sum --quiet -c -) < "$WORK/textures.md5"; then
    echo "ERROR: the built textures or atlas differ from $WORK/textures.md5. If the art changed on" >&2
    echo "purpose, rerun with --lock; if only the atlas differs, rebuild it from main's first." >&2
    exit 1
fi
