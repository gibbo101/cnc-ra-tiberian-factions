#!/usr/bin/env bash
# Regenerate the mod's front-end CONFIG.MEG edits, idempotently, in place.
#
# Bakes into resources/.../Data/CONFIG.MEG:
#  - our custom main-menu layout (RA_MAIN_MENU.BUI: START NEW GAME removed,
#    MISSION SELECT promoted), rebuilt from the pristine base BUI by
#    scripts/bui_mainmenu_build.py (see memory: project-main-menu-bui-spike)
#  - the menu's confirmation box (RA_DIALOGBOX_SOVIET.BUI) in TD's green frame with the
#    menu's steel buttons, rebuilt from its base by scripts/bui_dialogbox_build.py
#  - the loading screen's spinner as the faction emblem row with a glint
#    (RA_UI_LOADINGSCREEN.BUI, by scripts/bui_loadingscreen_build.py; its textures
#    come from scripts/loading_art.py)
#  - Tiberian Dawn's skirmish lobby, LAN lobby, LAN match list and Workshop map browser on
#    RA's steel backdrop (UI_SKIRMISH_GAMELOBBY.BUI and its LAN/Workshop siblings, by
#    scripts/bui_lobby_build.py, which also sizes its faction picture for RA's emblems
#    in BUTTONFACTIONCOMBOBOX.BUI, gives its nine-row list room in UI_GAMELOBBY_PLAYERSLOT.BUI,
#    and sets the text on its steel slots and rows in green);
#    factions_build.py points the RA front end at them
#  - the mod's green text styles in FONTLIBRARY.BFD (scripts/fontlib_build.py)
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
BASE_DLG="scripts/bui_work/RA_DIALOGBOX_SOVIET.base.BUI"
EDIT_DLG="scripts/bui_work/RA_DIALOGBOX_SOVIET.edited.BUI"
BASE_LOAD="scripts/bui_work/RA_UI_LOADINGSCREEN.base.BUI"
EDIT_LOAD="scripts/bui_work/RA_UI_LOADINGSCREEN.edited.BUI"
BASE_LOBBY="scripts/bui_work/UI_SKIRMISH_GAMELOBBY.base.BUI"
EDIT_LOBBY="scripts/bui_work/UI_SKIRMISH_GAMELOBBY.edited.BUI"
TD_SCREENS="UI_LAN_GAMELOBBY UI_LAN_MULTIPLAYERMENU UI_WORKSHOPMAP_BROWSE BUTTONPLAYERNAMECOMBOBOX BUTTONTEAMCOMBOBOX UI_LISTBOX_MAPSELECT_ENTRY UI_LISTBOX_LAN_ENTRY UI_GAMELOBBY_PLAYERSLOT"
BASE_FCOMBO="scripts/bui_work/BUTTONFACTIONCOMBOBOX.base.BUI"
BASE_FONT="scripts/font_work/FONTLIBRARY.base.BFD"
EDIT_FONT="scripts/font_work/FONTLIBRARY.edited.BFD"
EDIT_CUSTOM="scripts/bui_work/UI_CUSTOM_MAP_FILE_ENTRY.edited.BUI"
EDIT_FCOMBO="scripts/bui_work/BUTTONFACTIONCOMBOBOX.edited.BUI"
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
BASE_GUI="scripts/gui_work/GUITEXTURESETS.base.XML"
EDIT_GUI="scripts/gui_work/GUITEXTURESETS.edited.XML"

echo "==> Rebuilding edited RA_MAIN_MENU.BUI from base"
python3 scripts/bui_mainmenu_build.py "$BASE_BUI" "$EDIT_BUI"

echo "==> Rebuilding edited RA_DIALOGBOX_SOVIET.BUI from base (the menu's confirmation box)"
python3 scripts/bui_dialogbox_build.py "$BASE_DLG" "$EDIT_DLG"

echo "==> Rebuilding edited RA_UI_LOADINGSCREEN.BUI from base (emblem row with a glint)"
python3 scripts/bui_loadingscreen_build.py "$BASE_LOAD" "$EDIT_LOAD"

echo "==> Rebuilding edited UI_SKIRMISH_GAMELOBBY.BUI from base (TD lobby, RA backdrop)"
python3 scripts/bui_lobby_build.py "$BASE_LOBBY" "$EDIT_LOBBY"
python3 scripts/bui_lobby_build.py "$BASE_FCOMBO" "$EDIT_FCOMBO"
for n in $TD_SCREENS UI_CUSTOM_MAP_FILE_ENTRY; do
    python3 scripts/bui_lobby_build.py "scripts/bui_work/$n.base.BUI" "scripts/bui_work/$n.edited.BUI"
done

echo "==> Rebuilding FONTLIBRARY.BFD from base (the mod's green text styles)"
python3 scripts/fontlib_build.py "$BASE_FONT" "$EDIT_FONT"

echo "==> Rebuilding edited RA_TACTICAL_UI.BUI from base (side label under the crest hidden)"
python3 scripts/bui_work/hud_label_hide_build.py "$BASE_HUD" "$EDIT_HUD"

echo "==> Rebuilding edited MUSICEVENTS.XML from base (skirmish playlist)"
python3 scripts/musicevents_build.py "$BASE_MUS" "$MUS_LIST" "$EDIT_MUS"

echo "==> Rebuilding edited MASTERTEXTFILE_EN-US.LOC from base (Unholy Alliance checkbox)"
python3 scripts/loc_relabel.py "$BASE_LOC" "$EDIT_LOC" @scripts/loc_work/mastertext.edits.txt "${LOC_OVERRIDES[@]}"

echo "==> Rebuilding GUITEXTURESETS.XML from base (the main menu's steel buttons, the CAMPAIGNS row sets)"
python3 scripts/gui_texturesets_build.py "$BASE_GUI" "$EDIT_GUI"

echo "==> Repacking $MEG with the edited BUI + MUSICEVENTS + MASTERTEXT (in place)"
echo "==> Rebuilding FACTIONS.XML from base (picker order + full-size GDI/Nod plates)"
python3 scripts/factions_build.py "$BASE_FAC" "$EDIT_FAC"
python3 scripts/meg_pack.py repack "$MEG" "$MEG.tmp" \
    "RA_MAIN_MENU.BUI=$EDIT_BUI" \
    "DATA\\ART\\GUI\\RA_TACTICAL_UI.BUI=$EDIT_HUD" \
    "DATA\\ART\\GUI\\RA\\RA_DIALOGBOX_SOVIET.BUI=$EDIT_DLG" \
    "DATA\\ART\\GUI\\RA\\RA_UI_LOADINGSCREEN.BUI=$EDIT_LOAD" \
    "DATA\\ART\\GUI\\UI_SKIRMISH_GAMELOBBY.BUI=$EDIT_LOBBY" \
    "DATA\\ART\\GUI\\BUTTONFACTIONCOMBOBOX.BUI=$EDIT_FCOMBO" \
    $(for n in $TD_SCREENS; do printf '%s ' "DATA\\ART\\GUI\\$n.BUI=scripts/bui_work/$n.edited.BUI"; done) \
    "DATA\\ART\\GUI\\CNC\\UI_CUSTOM_MAP_FILE_ENTRY.BUI=$EDIT_CUSTOM" \
    "DATA\\ART\\GUI\\FONTLIBRARY.BFD=$EDIT_FONT" \
    "MUSICEVENTS.XML=$EDIT_MUS" "MASTERTEXTFILE_EN-US.LOC=$EDIT_LOC" \
    "DATA\\XML\\OBJECTS\\MISC\\FACTIONS.XML=$EDIT_FAC" \
    "DATA\\ART\\GUI\\GUITEXTURESETS.XML=$EDIT_GUI"
mv "$MEG.tmp" "$MEG"


echo "==> Verifying the edited files inside the MEG"
python3 scripts/meg_extract.py extract "$MEG" "RA_MAIN_MENU.BUI" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/RA_MAIN_MENU.BUI" "$EDIT_BUI" && echo "OK: BUI in CONFIG.MEG matches edited BUI"
python3 scripts/meg_extract.py extract "$MEG" "RA_TACTICAL_UI.BUI" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/RA_TACTICAL_UI.BUI" "$EDIT_HUD" && echo "OK: HUD BUI in CONFIG.MEG matches edited copy"
python3 scripts/meg_extract.py extract "$MEG" "RA_DIALOGBOX_SOVIET.BUI" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/RA_DIALOGBOX_SOVIET.BUI" "$EDIT_DLG" && echo "OK: dialog BUI in CONFIG.MEG matches edited copy"
python3 scripts/meg_extract.py extract "$MEG" "RA_UI_LOADINGSCREEN.BUI" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/RA_UI_LOADINGSCREEN.BUI" "$EDIT_LOAD" && echo "OK: loading screen BUI in CONFIG.MEG matches edited copy"
python3 scripts/meg_extract.py extract "$MEG" "GUI\\UI_SKIRMISH_GAMELOBBY.BUI" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/UI_SKIRMISH_GAMELOBBY.BUI" "$EDIT_LOBBY" && echo "OK: lobby BUI in CONFIG.MEG matches edited copy"
python3 scripts/meg_extract.py extract "$MEG" "GUI\\BUTTONFACTIONCOMBOBOX.BUI" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/BUTTONFACTIONCOMBOBOX.BUI" "$EDIT_FCOMBO" && echo "OK: faction combo BUI in CONFIG.MEG matches edited copy"
python3 scripts/meg_extract.py extract "$MEG" "CNC\\UI_CUSTOM_MAP_FILE_ENTRY.BUI" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/UI_CUSTOM_MAP_FILE_ENTRY.BUI" "$EDIT_CUSTOM" && echo "OK: custom map entry in CONFIG.MEG matches edited copy"
python3 scripts/meg_extract.py extract "$MEG" "GUI\\FONTLIBRARY.BFD" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/FONTLIBRARY.BFD" "$EDIT_FONT" && echo "OK: FONTLIBRARY in CONFIG.MEG matches edited copy"
for n in $TD_SCREENS; do
    python3 scripts/meg_extract.py extract "$MEG" "GUI\\$n.BUI" /tmp/_megverify >/dev/null
    cmp "/tmp/_megverify/$n.BUI" "scripts/bui_work/$n.edited.BUI" && echo "OK: $n in CONFIG.MEG matches edited copy"
done
python3 scripts/meg_extract.py extract "$MEG" "MUSICEVENTS.XML" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/MUSICEVENTS.XML" "$EDIT_MUS" && echo "OK: MUSICEVENTS in CONFIG.MEG matches edited copy"
python3 scripts/meg_extract.py extract "$MEG" "MASTERTEXTFILE_EN-US.LOC" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/MASTERTEXTFILE_EN-US.LOC" "$EDIT_LOC" && echo "OK: MASTERTEXT in CONFIG.MEG matches edited copy"
python3 scripts/meg_extract.py extract "$MEG" "MISC\\FACTIONS.XML" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/FACTIONS.XML" "$EDIT_FAC" && echo "OK: FACTIONS in CONFIG.MEG matches edited copy"
python3 scripts/meg_extract.py extract "$MEG" "GUI\\GUITEXTURESETS.XML" /tmp/_megverify >/dev/null
cmp "/tmp/_megverify/GUITEXTURESETS.XML" "$EDIT_GUI" && echo "OK: GUITEXTURESETS in CONFIG.MEG matches edited copy"
echo "==> Validating shipped XML"
python3 scripts/validate_shipped_xml.py resources/remaster_mods/

echo "==> Done. Rebuild the mod (cmake workflow) to stage it into build output."
