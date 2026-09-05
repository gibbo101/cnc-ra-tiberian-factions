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

# TF_MEG_TARGET repoints every edit at another copy of CONFIG.MEG -- package-for-workshop
# uses it to build the release-shaped front-end into the STAGED mod without disturbing the
# repo's own (which always carries the dev shape).
MEG="${TF_MEG_TARGET:-resources/remaster_mods/Vanilla_RA/Data/CONFIG.MEG}"

# The fifth faction's release switch (see TF_TS_GDI_FACTION in redalert/defines.h). With it
# off, the picker row that reads "TS GDI" goes back to reading "Allies", matching a DLL built
# with the faction compiled out.
TS_GDI_FACTION="${TF_TS_GDI_FACTION:-1}"
LOC_OVERRIDES=()
if [[ "$TS_GDI_FACTION" == "0" ]]; then
    LOC_OVERRIDES=(TEXT_FACTION_NAME_FACTION_8=Allies
                   TEXT_FACTION_BONUS_GERMANY=Allies
                   TEXT_FACTION_REDALERT_GERMANY=Allies)
    echo "==> Fifth faction OFF: Germany's picker row stays an Allied duplicate"
fi
BASE_BUI="scripts/bui_work/RA_MAIN_MENU.base.BUI"
EDIT_BUI="scripts/bui_work/RA_MAIN_MENU.edited.BUI"
BASE_HUD="scripts/bui_work/RA_TACTICAL_UI.base.BUI"
EDIT_HUD="scripts/bui_work/RA_TACTICAL_UI.edited.BUI"
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
BASE_FAC="scripts/factions_work/FACTIONS.base.XML"
EDIT_FAC="scripts/factions_work/FACTIONS.edited.XML"

echo "==> Rebuilding edited RA_MAIN_MENU.BUI from base"
python3 scripts/bui_mainmenu_build.py "$BASE_BUI" "$EDIT_BUI"

echo "==> Rebuilding edited RA_TACTICAL_UI.BUI from base (side label under the crest hidden)"
python3 scripts/bui_work/hud_label_hide_build.py "$BASE_HUD" "$EDIT_HUD"

echo "==> Rebuilding edited MUSICEVENTS.XML from base (skirmish playlist)"
python3 scripts/musicevents_build.py "$BASE_MUS" "$MUS_LIST" "$EDIT_MUS"

echo "==> Rebuilding edited MASTERTEXTFILE_EN-US.LOC from base (Unholy Alliance checkbox)"
python3 scripts/loc_relabel.py "$BASE_LOC" "$EDIT_LOC" @scripts/loc_work/mastertext.edits.txt "${LOC_OVERRIDES[@]}"

echo "==> Repacking $MEG with the edited BUI + MUSICEVENTS + MASTERTEXT (in place)"
echo "==> Rebuilding FACTIONS.XML from base (picker order + full-size GDI/Nod plates)"
python3 scripts/factions_build.py "$BASE_FAC" "$EDIT_FAC"
python3 scripts/meg_pack.py repack "$MEG" "$MEG.tmp" \
    "RA_MAIN_MENU.BUI=$EDIT_BUI" \
    "DATA\\ART\\GUI\\RA_TACTICAL_UI.BUI=$EDIT_HUD" \
    "MUSICEVENTS.XML=$EDIT_MUS" "MASTERTEXTFILE_EN-US.LOC=$EDIT_LOC" \
    "DATA\\XML\\OBJECTS\\MISC\\FACTIONS.XML=$EDIT_FAC"
mv "$MEG.tmp" "$MEG"


echo "==> Verifying the edited files inside the MEG"
python3 scripts/meg_extract.py extract "$MEG" "RA_MAIN_MENU.BUI" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/RA_MAIN_MENU.BUI" "$EDIT_BUI" && echo "OK: BUI in CONFIG.MEG matches edited BUI"
python3 scripts/meg_extract.py extract "$MEG" "RA_TACTICAL_UI.BUI" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/RA_TACTICAL_UI.BUI" "$EDIT_HUD" && echo "OK: HUD BUI in CONFIG.MEG matches edited copy"
python3 scripts/meg_extract.py extract "$MEG" "MUSICEVENTS.XML" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/MUSICEVENTS.XML" "$EDIT_MUS" && echo "OK: MUSICEVENTS in CONFIG.MEG matches edited copy"
python3 scripts/meg_extract.py extract "$MEG" "MASTERTEXTFILE_EN-US.LOC" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/MASTERTEXTFILE_EN-US.LOC" "$EDIT_LOC" && echo "OK: MASTERTEXT in CONFIG.MEG matches edited copy"
python3 scripts/meg_extract.py extract "$MEG" "MISC\\FACTIONS.XML" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/FACTIONS.XML" "$EDIT_FAC" && echo "OK: FACTIONS in CONFIG.MEG matches edited copy"
echo "==> Validating shipped XML"
python3 scripts/validate_shipped_xml.py resources/remaster_mods/

echo "==> Done. Rebuild the mod (cmake workflow) to stage it into build output."
