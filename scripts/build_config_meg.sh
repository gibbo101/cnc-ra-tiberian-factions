#!/usr/bin/env bash
# Regenerate the mod's front-end CONFIG.MEG edits, idempotently, in place.
#
# Bakes into resources/.../Data/CONFIG.MEG:
#  - our custom main-menu layout (RA_MAIN_MENU.BUI: START NEW GAME removed,
#    MISSION SELECT promoted), rebuilt from the pristine base BUI by
#    scripts/bui_mainmenu_build.py (see memory: project-main-menu-bui-spike)
#  - GAMECONSTANTS.XML with CFE Patch Redux pixel-perfect zoom factors,
#    rebuilt same-size from the pristine base by scripts/gameconstants_build.py
#    (see docs/cfe-port-plan.md). The same artifact is also staged loose at
#    Data/XML/GAMECONSTANTS.XML (CFE's proven delivery path) so the zoom edit
#    applies regardless of loose-vs-mod-MEG precedence.
# The faction-select edits (FACTIONS.XML / master-text) already live in that
# MEG; re-running is safe (idempotent).
#
# License: GPL v3.
set -euo pipefail
cd "$(dirname "$0")/.."

MEG="resources/remaster_mods/Vanilla_RA/Data/CONFIG.MEG"
BASE_BUI="scripts/bui_work/RA_MAIN_MENU.base.BUI"
EDIT_BUI="scripts/bui_work/RA_MAIN_MENU.edited.BUI"
BASE_GC="scripts/gc_work/GAMECONSTANTS.base.XML"
EDIT_GC="scripts/gc_work/GAMECONSTANTS.edited.XML"
LOOSE_GC="resources/remaster_mods/Vanilla_RA/Data/XML/GAMECONSTANTS.XML"

echo "==> Rebuilding edited RA_MAIN_MENU.BUI from base"
python3 scripts/bui_mainmenu_build.py "$BASE_BUI" "$EDIT_BUI"

echo "==> Rebuilding edited GAMECONSTANTS.XML from base (pixel-perfect zoom)"
python3 scripts/gameconstants_build.py "$BASE_GC" "$EDIT_GC"

echo "==> Repacking $MEG with the edited BUI + GAMECONSTANTS (in place)"
python3 scripts/meg_pack.py repack "$MEG" "$MEG.tmp" \
    "RA_MAIN_MENU.BUI=$EDIT_BUI" "GAMECONSTANTS.XML=$EDIT_GC"
mv "$MEG.tmp" "$MEG"

echo "==> Staging loose Data/XML/GAMECONSTANTS.XML"
cp "$EDIT_GC" "$LOOSE_GC"

echo "==> Verifying the edited files inside the MEG"
python3 scripts/meg_extract.py extract "$MEG" "RA_MAIN_MENU.BUI" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/RA_MAIN_MENU.BUI" "$EDIT_BUI" && echo "OK: BUI in CONFIG.MEG matches edited BUI"
python3 scripts/meg_extract.py extract "$MEG" "GAMECONSTANTS.XML" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/GAMECONSTANTS.XML" "$EDIT_GC" && echo "OK: GAMECONSTANTS in CONFIG.MEG matches edited copy"
cmp "$LOOSE_GC" "$EDIT_GC" && echo "OK: loose GAMECONSTANTS matches edited copy"
echo "==> Done. Rebuild the mod (cmake workflow) to stage it into build output."
