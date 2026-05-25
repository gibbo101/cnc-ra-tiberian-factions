#!/bin/bash
# Tiberian Factions — rebuild TFASSETS.MIX from TD's CONQUER.MIX.
#
# mix_tools.py pack does NOT merge with the existing archive; it rebuilds
# from scratch. This script captures the canonical TD-prefixed SHP list
# so adding a new separated building means appending one line below and
# re-running.
#
# Run: bash scripts/build_tfassets.sh
set -euo pipefail

CONQUER="${HOME}/.steam/steam/steamapps/common/CnCRemastered/Data/CNCDATA/TIBERIAN_DAWN/CD1/CONQUER.MIX"
OUTMIX="resources/remaster_mods/Vanilla_RA/CCDATA/TFASSETS.MIX"
TMPDIR="$(mktemp -d -t tfassets-XXXXXX)"
trap "rm -rf '$TMPDIR'" EXIT

if [[ ! -f "$CONQUER" ]]; then
    echo "error: CONQUER.MIX not found at $CONQUER" >&2
    echo "       (need a local Steam install of C&C Remastered Collection)" >&2
    exit 1
fi

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
)

# Extract each SHP from CONQUER.MIX into the temp dir.
PACK_ARGS=()
for entry in "${ENTRIES[@]}"; do
    src="${entry%%:*}"
    dst="${entry##*:}"
    python3 scripts/mix_tools.py extract "$CONQUER" "$src" "$TMPDIR" >/dev/null
    PACK_ARGS+=("$TMPDIR/$src:$dst")
done

# Repack into TFASSETS.MIX with TD-prefix renames.
python3 scripts/mix_tools.py pack "$OUTMIX" "${PACK_ARGS[@]}"
echo "TFASSETS.MIX rebuilt with ${#ENTRIES[@]} entries -> $OUTMIX"
