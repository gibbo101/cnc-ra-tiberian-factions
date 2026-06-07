#!/usr/bin/env bash
# Regenerate the mod's front-end CONFIG.MEG edits, idempotently, in place.
#
# Currently bakes our custom main-menu layout (RA_MAIN_MENU.BUI: START NEW GAME
# removed, MISSION SELECT promoted) into resources/.../Data/CONFIG.MEG. The
# faction-select edits (FACTIONS.XML / master-text) already live in that MEG;
# this only swaps in the rebuilt BUI, so re-running is safe (idempotent).
#
# The BUI edit itself is reproduced from the pristine base BUI by
# scripts/bui_mainmenu_build.py (see memory: project-main-menu-bui-spike).
#
# License: GPL v3.
set -euo pipefail
cd "$(dirname "$0")/.."

MEG="resources/remaster_mods/Vanilla_RA/Data/CONFIG.MEG"
BASE_BUI="scripts/bui_work/RA_MAIN_MENU.base.BUI"
EDIT_BUI="scripts/bui_work/RA_MAIN_MENU.edited.BUI"

echo "==> Rebuilding edited RA_MAIN_MENU.BUI from base"
python3 scripts/bui_mainmenu_build.py "$BASE_BUI" "$EDIT_BUI"

echo "==> Repacking $MEG with the edited BUI (in place)"
python3 scripts/meg_pack.py repack "$MEG" "$MEG.tmp" "RA_MAIN_MENU.BUI=$EDIT_BUI"
mv "$MEG.tmp" "$MEG"

echo "==> Verifying the BUI inside the MEG matches the edited BUI"
python3 - <<PY
import sys
sys.argv=['x','list']
PY
python3 scripts/meg_extract.py extract "$MEG" "RA_MAIN_MENU.BUI" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/RA_MAIN_MENU.BUI" "$EDIT_BUI" && echo "OK: BUI in CONFIG.MEG matches edited BUI"
echo "==> Done. Rebuild the mod (cmake workflow) to stage it into build output."
