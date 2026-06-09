#!/bin/bash
# Tiberian Factions — rebuild TFASSETS.MIX from TD's CONQUER.MIX.
#
# mix_tools.py pack does NOT merge with the existing archive; it rebuilds
# from scratch. This script captures the canonical TD-prefixed SHP list
# so adding a new separated building means appending one line below and
# re-running.
#
# Each TD SHP is palette-remapped for RA classic-graphics mode before
# packing: TD's house-colour range (176-191) is moved onto RA's (80-95) so
# the engine recolours it per player, and every other index is matched to
# RA's nearest palette colour. Without this, TD sprites render with wrong
# colours in classic mode (the bug Reilsss/EMC never solved).
#
# Run: bash scripts/build_tfassets.sh
set -euo pipefail

CNCDATA="${HOME}/.steam/steam/steamapps/common/CnCRemastered/Data/CNCDATA"
CONQUER="${CNCDATA}/TIBERIAN_DAWN/CD1/CONQUER.MIX"
TD_PAL="${CNCDATA}/TIBERIAN_DAWN/CD1/TEMPERAT.PAL"
REDALERT="${CNCDATA}/RED_ALERT/CD1/REDALERT.MIX"
# Theatre mix that holds the Tiberium overlay tiles (ti1.tem is a 12-frame
# 24x24 SHP = the 12 density stages) for the classic-mode TIB01 overlay.
TEMPERAT_MIX="${CNCDATA}/TIBERIAN_DAWN/CD1/TEMPERAT.MIX"
OUTMIX="resources/remaster_mods/Vanilla_RA/CCDATA/TFASSETS.MIX"
TMPDIR="$(mktemp -d -t tfassets-XXXXXX)"
trap "rm -rf '$TMPDIR'" EXIT

for f in "$CONQUER" "$TD_PAL" "$REDALERT"; do
    if [[ ! -f "$f" ]]; then
        echo "error: required game file not found: $f" >&2
        echo "       (need a local Steam install of C&C Remastered Collection)" >&2
        exit 1
    fi
done

# RA's temperate palette is the closest-colour remap target. It lives inside
# the encrypted, nested REDALERT.MIX container, so use the dedicated reader.
RA_PAL="${TMPDIR}/RA_TEMPERAT.PAL"
python3 -W ignore scripts/ra_mix_extract.py extract "$REDALERT" TEMPERAT.PAL "$TMPDIR" >/dev/null
mv "${TMPDIR}/TEMPERAT.PAL" "$RA_PAL"

# Canonical list of TD SHPs we ship in TFASSETS.MIX. Format:
#   TD-source-name:TD-prefixed-mod-name
# Add a line per separated building (idle SHP + buildup SHP).
ENTRIES=(
    # M3 Tier 5 — Obelisk of Light (the recipe's vertical slice).
    "OBLI.SHP:TDOBLI.SHP"
    "OBLIMAKE.SHP:TDOBLIMAKE.SHP"
    # M2 Tier 1 — pure-data buildings.
    "NUKE.SHP:TDNUKE.SHP"
    "NUKEMAKE.SHP:TDNUKEMAKE.SHP"
    "NUK2.SHP:TDNUK2.SHP"
    "NUK2MAKE.SHP:TDNUK2MAKE.SHP"
    "PYLE.SHP:TDPYLE.SHP"
    "PYLEMAKE.SHP:TDPYLEMAKE.SHP"
    "SILO.SHP:TDSILO.SHP"
    "SILOMAKE.SHP:TDSILOMAKE.SHP"
    # M3 Tier 2 — defensive turrets.
    "ATWR.SHP:TDATWR.SHP"
    "ATWRMAKE.SHP:TDATWRMAKE.SHP"
    "GTWR.SHP:TDGTWR.SHP"
    "GTWRMAKE.SHP:TDGTWRMAKE.SHP"
    "GUN.SHP:TDGUN.SHP"
    "GUNMAKE.SHP:TDGUNMAKE.SHP"
    "SAM.SHP:TDSAM.SHP"
    "SAMMAKE.SHP:TDSAMMAKE.SHP"
    # M4 Tier 3 — production buildings.
    "HAND.SHP:TDHAND.SHP"
    "HANDMAKE.SHP:TDHANDMAKE.SHP"
    "HPAD.SHP:TDHPAD.SHP"
    "HPADMAKE.SHP:TDHPADMAKE.SHP"
    "FIX.SHP:TDFIX.SHP"
    "FIXMAKE.SHP:TDFIXMAKE.SHP"
    "HQ.SHP:TDHQ.SHP"
    "HQMAKE.SHP:TDHQMAKE.SHP"
    "WEAP.SHP:TDWEAP.SHP"
    "WEAPMAKE.SHP:TDWEAPMAKE.SHP"
    "WEAP2.SHP:TDWEAP2.SHP"
    "AFLD.SHP:TDAFLD.SHP"
    "AFLDMAKE.SHP:TDAFLDMAKE.SHP"
    "FACT.SHP:TDFACT.SHP"
    "FACTMAKE.SHP:TDFACTMAKE.SHP"
    "MCV.SHP:TDMCV.SHP"
    "HARV.SHP:TDHARV.SHP"
    # Combat vehicle arc (2026-05-30): GDI Medium Tank (classic SHP for One_Time
    # ImageData + classic-mode render; HD art is the bundled TDMTNK tileset).
    "MTNK.SHP:TDMTNK.SHP"
    "LTNK.SHP:TDLTNK.SHP"
    "HTNK.SHP:TDHTNK.SHP"
    "FTNK.SHP:TDFTNK.SHP"
    "BIKE.SHP:TDBIKE.SHP"
    "JEEP.SHP:TDJEEP.SHP"
    "BGGY.SHP:TDBGGY.SHP"
    "APC.SHP:TDAPC.SHP"
    "STNK.SHP:TDSTNK.SHP"
    "MSAM.SHP:TDMLRS.SHP"
    "MLRS.SHP:TDMSAM.SHP"
    "ARTY.SHP:TDARTY.SHP"
    "HELI.SHP:TDHELI.SHP"
    "ORCA.SHP:TDORCA.SHP"
    # Tiberium ecosystem -- Visceroid creature (UNIT_TDVICE), spawned when infantry
    # die in Tiberium. Constant-animation blob; vice.shp carries its anim frames.
    "VICE.SHP:TDVICE.SHP"
    "PROC.SHP:TDPROC.SHP"
    "PROCMAKE.SHP:TDPROCMAKE.SHP"
    # M5 Tier 4 — superweapon hosts.
    "EYE.SHP:TDEYE.SHP"
    "EYEMAKE.SHP:TDEYEMAKE.SHP"
    # M5 Phase E2 — Ion Cannon beam-strike anim (ANIM_TD_ION_CANNON).
    "IONSFX.SHP:TDIONSFX.SHP"
    # Combat vehicle arc — vehicle death frag explosion (ANIM_TDFRAG2; TD ANIM_FRAG2
    # uses the SHP named FRAG3). Used by the GDI Medium Tank's death.
    "FRAG3.SHP:TDFRAG3.SHP"
    # M5 Tier 4 — Temple of Nod (Nuclear Strike host).
    "TMPL.SHP:TDTMPL.SHP"
    "TMPLMAKE.SHP:TDTMPLMAKE.SHP"
    # TD infantry muzzle jets — directional spray anims (E4 Flamethrower / E5 Chem Warrior).
    # Classic SHPs so the jet renders in classic mode too (HD uses the RA_VFX TD<X>-<dir> tiles).
    # 8 dirs each in Dir_Facing order; 13 frames, matching the ANIM_FLAME_*/ANIM_CHEM_* ctor stages.
    # Loading these makes the FBALL1 donor-ImageData in adata.cpp One_Time a no-op.
    "FLAME-N.SHP:TDFLAME-N.SHP"
    "FLAME-NE.SHP:TDFLAME-NE.SHP"
    "FLAME-E.SHP:TDFLAME-E.SHP"
    "FLAME-SE.SHP:TDFLAME-SE.SHP"
    "FLAME-S.SHP:TDFLAME-S.SHP"
    "FLAME-SW.SHP:TDFLAME-SW.SHP"
    "FLAME-W.SHP:TDFLAME-W.SHP"
    "FLAME-NW.SHP:TDFLAME-NW.SHP"
    "CHEM-N.SHP:TDCHEM-N.SHP"
    "CHEM-NE.SHP:TDCHEM-NE.SHP"
    "CHEM-E.SHP:TDCHEM-E.SHP"
    "CHEM-SE.SHP:TDCHEM-SE.SHP"
    "CHEM-S.SHP:TDCHEM-S.SHP"
    "CHEM-SW.SHP:TDCHEM-SW.SHP"
    "CHEM-W.SHP:TDCHEM-W.SHP"
    "CHEM-NW.SHP:TDCHEM-NW.SHP"
)

# Extract each SHP from CONQUER.MIX, palette-remap it for RA classic mode,
# then pack the remapped copy under its TD-prefixed name.
PACK_ARGS=()
for entry in "${ENTRIES[@]}"; do
    src="${entry%%:*}"
    dst="${entry##*:}"
    python3 scripts/mix_tools.py extract "$CONQUER" "$src" "$TMPDIR" >/dev/null
    python3 scripts/shptools.py remap "$TMPDIR/$src" "$TMPDIR/remap_$src" "$TD_PAL" "$RA_PAL"
    PACK_ARGS+=("$TMPDIR/remap_$src:$dst")
done

# Tiberian Factions -- classic-mode Tiberium overlay (OVERLAY_TIB01). The engine
# loads it as a non-theatre "TIB01.SHP"; TD's ti1.tem IS already a 12-frame 24x24
# SHP (frame = density 0-11), so we just remap it and pack it under TIB01.SHP.
# Sourced from TEMPERAT.MIX (theatre mix), not CONQUER.MIX. HD mode uses the
# separate tileset art built by scripts/build_tiberium_hd.py.
if [[ -f "$TEMPERAT_MIX" ]]; then
    python3 scripts/mix_tools.py extract "$TEMPERAT_MIX" "ti1.tem" "$TMPDIR" >/dev/null
    python3 scripts/shptools.py remap "$TMPDIR/ti1.tem" "$TMPDIR/remap_TIB01.SHP" "$TD_PAL" "$RA_PAL"
    PACK_ARGS+=("$TMPDIR/remap_TIB01.SHP:TIB01.SHP")

    # Blossom tree rendered as a BUILDING (STRUCT_TDBLOSSOM, IniName "TDBLOSSOM").
    # Classic building art is a non-theatre "TDBLOSSOM.SHP"; TD's 55-frame
    # split2.tem IS the blossom sprite, so remap it and pack it under TDBLOSSOM.SHP.
    python3 scripts/mix_tools.py extract "$TEMPERAT_MIX" "split2.tem" "$TMPDIR" >/dev/null
    python3 scripts/shptools.py remap "$TMPDIR/split2.tem" "$TMPDIR/remap_TDBLOSSOM.SHP" "$TD_PAL" "$RA_PAL"
    PACK_ARGS+=("$TMPDIR/remap_TDBLOSSOM.SHP:TDBLOSSOM.SHP")
else
    echo "warning: $TEMPERAT_MIX not found; classic TIB01/SPLIT2 art skipped" >&2
fi

# Repack into TFASSETS.MIX with TD-prefix renames.
python3 scripts/mix_tools.py pack "$OUTMIX" "${PACK_ARGS[@]}"
echo "TFASSETS.MIX rebuilt with ${#ENTRIES[@]} entries -> $OUTMIX"
