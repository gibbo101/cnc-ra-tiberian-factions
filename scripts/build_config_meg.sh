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
LOOSE_INP="resources/remaster_mods/Vanilla_RA/Data/XML/INPUTTRANSLATORCONFIGURATIONS.XML"
BASE_MUS="scripts/music_work/MUSICEVENTS.base.XML"
EDIT_MUS="scripts/music_work/MUSICEVENTS.edited.XML"
MUS_LIST="scripts/music_work/MUSIC.listing.txt"
BASE_INP="scripts/input_work/INPUTTRANSLATORCONFIGURATIONS.base.XML"
EDIT_INP="scripts/input_work/INPUTTRANSLATORCONFIGURATIONS.edited.XML"
BASE_LOC="scripts/loc_work/MASTERTEXTFILE_EN-US.base.LOC"
EDIT_LOC="scripts/loc_work/MASTERTEXTFILE_EN-US.edited.LOC"

echo "==> Rebuilding edited RA_MAIN_MENU.BUI from base"
python3 scripts/bui_mainmenu_build.py "$BASE_BUI" "$EDIT_BUI"

echo "==> Rebuilding edited MUSICEVENTS.XML from base (skirmish playlist)"
python3 scripts/musicevents_build.py "$BASE_MUS" "$MUS_LIST" "$EDIT_MUS"

echo "==> Rebuilding edited MASTERTEXTFILE_EN-US.LOC from base (Unholy Alliance checkbox)"
python3 scripts/loc_relabel.py "$BASE_LOC" "$EDIT_LOC" @scripts/loc_work/mastertext.edits.txt

echo "==> Repacking $MEG with the edited BUI + MUSICEVENTS + MASTERTEXT (in place)"
python3 scripts/meg_pack.py repack "$MEG" "$MEG.tmp" \
    "RA_MAIN_MENU.BUI=$EDIT_BUI" \
    "MUSICEVENTS.XML=$EDIT_MUS" "MASTERTEXTFILE_EN-US.LOC=$EDIT_LOC"
mv "$MEG.tmp" "$MEG"


echo "==> Verifying the edited files inside the MEG"
python3 scripts/meg_extract.py extract "$MEG" "RA_MAIN_MENU.BUI" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/RA_MAIN_MENU.BUI" "$EDIT_BUI" && echo "OK: BUI in CONFIG.MEG matches edited BUI"
python3 scripts/meg_extract.py extract "$MEG" "MUSICEVENTS.XML" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/MUSICEVENTS.XML" "$EDIT_MUS" && echo "OK: MUSICEVENTS in CONFIG.MEG matches edited copy"
python3 scripts/meg_extract.py extract "$MEG" "MASTERTEXTFILE_EN-US.LOC" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/MASTERTEXTFILE_EN-US.LOC" "$EDIT_LOC" && echo "OK: MASTERTEXT in CONFIG.MEG matches edited copy"
echo "==> Validating shipped XML"
python3 scripts/validate_shipped_xml.py resources/remaster_mods/

echo "==> Done. Rebuild the mod (cmake workflow) to stage it into build output."
