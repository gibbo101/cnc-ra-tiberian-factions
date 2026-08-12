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
    "A10.SHP:TDA10.SHP"
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

# Tiberian Factions -- ported TD terrain TEMPLATES (build_td_tiles.py). The engine
# reads each template's dimensions + land-type from its classic iconset via
# MFCD::Retrieve("TD<NAME>.<theatre suffix>") -- .TEM temperate, .SNO snow (TD
# winter art); HD render is the loose tileset art. The staged iconsets
# (already RA-format-converted by build_td_tiles.py) are packed AS-IS -- no
# palette remap (it would corrupt the header's dimensions/land-type;
# classic-mode colour fidelity is a later refinement).
TEM_STAGE="scripts/_td_tems"
if [[ -d "$TEM_STAGE" ]]; then
    for tem in "$TEM_STAGE"/*.TEM "$TEM_STAGE"/*.SNO "$TEM_STAGE"/*.INT; do
        [[ -e "$tem" ]] || continue
        PACK_ARGS+=("$tem:$(basename "$tem")")
    done
fi

# Tiberian Factions -- snowy trees for converted TD WINTER maps. Winter maps
# run in RA's TEMPERATE theatre, so trees would draw with the green temperate
# shapes in classic mode. TerrainClass::Get_Image_Data (terrain.cpp) swaps to
# "TDW<NAME>.TEM" from this mix when TF_TDWinterMap is set; HD gets the snow
# look via the exported AssetName + the loose tileset entries
# (scripts/build_winter_trees.py). Source = TD's own winter tree art
# (WINTER.MIX *.win), remapped from TD's winter palette to RA's temperate
# palette (the palette classic mode renders these maps with).
WINTER_MIX="${CNCDATA}/TIBERIAN_DAWN/CD1/WINTER.MIX"
if [[ -f "$WINTER_MIX" ]]; then
    python3 scripts/mix_tools.py extract "$WINTER_MIX" "winter.pal" "$TMPDIR" >/dev/null
    TDW_PAL="$TMPDIR/winter.pal"
    for t in t01 t02 t03 t05 t06 t07 t08 t10 t11 t12 t13 t14 t15 t16 t17 \
             tc01 tc02 tc03 tc04 tc05; do
        python3 scripts/mix_tools.py extract "$WINTER_MIX" "$t.win" "$TMPDIR" >/dev/null
        python3 scripts/shptools.py remap "$TMPDIR/$t.win" "$TMPDIR/remap_tdw_$t" "$TDW_PAL" "$RA_PAL"
        PACK_ARGS+=("$TMPDIR/remap_tdw_$t:TDW$(echo $t | tr a-z A-Z).TEM")
    done
else
    echo "warning: $WINTER_MIX not found; classic snowy winter trees skipped" >&2
fi

# Tiberian Factions -- desert building bibs (interior slot). The base game
# ships NO interior bib art, so the engine skips bib smudges on desert maps
# (NULL classic data). Stage TD desert bibs under the native names as .INT:
# the engine then emits the smudge entries, and the launcher resolves their
# HD art from the interior tileset XML (build_tiberium_hd.py BIB* tiles).
# Packed RAW -- classic-mode desert colour fidelity is globally deferred.
DESERT_MIX="$HOME/.steam/steam/steamapps/common/CnCRemastered/Data/CNCDATA/TIBERIAN_DAWN/CD1/DESERT.MIX"
if [[ -f "$DESERT_MIX" ]]; then
    for b in bib1 bib2 bib3; do
        python3 scripts/mix_tools.py extract "$DESERT_MIX" "$b.des" "$TMPDIR" >/dev/null
        PACK_ARGS+=("$TMPDIR/$b.des:$(echo $b | tr a-z A-Z).INT")
    done
fi

# TS-spike -- TSHVR (Hover MLRS) classic stub. HD-only unit (voxel-rendered
# tileset, no classic art); this 64x64 transparent stub declares its classic
# dimensions so the launcher sizes the sprite, health bar and selection box
# for a large platform (vs the 48x48 tank default a donor ImageData gives).
python3 scripts/gen_stub_shp.py "$TMPDIR/tshvr_stub.shp" 48 48 64
PACK_ARGS+=("$TMPDIR/tshvr_stub.shp:TSHVR.SHP")

# TS walkers (Titan + Mammoth Mk. II) -- same HD-only stub pattern. Titan gets
# the tank box; the Mk. II's larger 56x56 box makes it render, select and
# health-bar as the hulk it is. RAILFX is the railgun helix spark anim (dims
# only; 6 frames).
python3 scripts/gen_stub_shp.py "$TMPDIR/tstitn_stub.shp" 56 56 128
PACK_ARGS+=("$TMPDIR/tstitn_stub.shp:TSTITN.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tshmec_stub.shp" 60 60 256
PACK_ARGS+=("$TMPDIR/tshmec_stub.shp:TSHMEC.SHP")

# Dropship-bay delivery pod -- the TS Dropship sprite (TSDSHP.ZIP, RA_VFX.XML).
# Bullet art, single west-facing frame. The launcher sizes HD art off the
# classic dims, so without this stub the pod inherits its donor's
# little-missile dims and the dropship renders TINY (live report, 2026-08-12).
# 123 = HD canvas 656 x 3/16. 656 is the TS-authentic relative scale (6.4
# canvas px per voxel, the shared unit factor) -- anything smaller reads
# tinier than the Mk. II it carries. Re-derive if render scale changes.
python3 scripts/gen_stub_shp.py "$TMPDIR/tsdshp_stub.shp" 123 123 1
PACK_ARGS+=("$TMPDIR/tsdshp_stub.shp:TSDSHP.SHP")
# TS units wave (Harvester / Wolverine / Disruptor / Amphibious APC) -- same
# HD-only stub pattern; frame counts match the HD zips (rot-only, walk, or
# body+turret) and dims match each unit's rules.ini ShapeSize.
python3 scripts/gen_stub_shp.py "$TMPDIR/tsharv_stub.shp" 64 64 32
PACK_ARGS+=("$TMPDIR/tsharv_stub.shp:TSHARV.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tssmec_stub.shp" 48 48 96
PACK_ARGS+=("$TMPDIR/tssmec_stub.shp:TSSMEC.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tssonic_stub.shp" 56 56 64
PACK_ARGS+=("$TMPDIR/tssonic_stub.shp:TSSONIC.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsapc_stub.shp" 48 48 32
PACK_ARGS+=("$TMPDIR/tsapc_stub.shp:TSAPC.SHP")
# TS-tree buildings with TS-authentic footprints (docs/ts-gdi-tree-plan.md):
# classic stubs declare each one's canvas dims (dims x5.33 = HD canvas); the
# MAKE stubs carry the construction frame count the HD buildup zips ship.
# Size pass 2026-08-03: the launcher maps the canvas onto the stub box
# CENTERED on the BSIZE box, so stub height beyond the box splits into equal
# art halos above and below it. (Selection boxes come from the FOUNDATION,
# not the stub — bdata Dimensions(), foundation−20%; the old stub-hug rule
# was a misread.)
# ts_stub emits a TS building's stub after checking its dimensions against the
# canvas ts_pack_tree.py actually packed. The launcher scales a building's
# canvas onto its stub box, so a canvas that grows without the stub growing to
# match renders the building at the wrong size and nothing else looks wrong --
# the failure is silent and only shows up as "that building looks small".
ts_stub() { # <INI> <out.shp> <w> <h> <frames>
    python3 - "$1" "$3" "$4" <<'PY'
import json, os, sys
ini, w, h = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
manifest = "scripts/ts_stub_dims.json"
if os.path.exists(manifest):
    want = json.load(open(manifest)).get(ini)
    if want and list(want) != [w, h]:
        sys.exit(f"{ini}: stub is {w}x{h} but the packed canvas needs {want[0]}x{want[1]}. "
                 f"Re-run scripts/ts_pack_tree.py, or correct the stub here.")
PY
    python3 scripts/gen_stub_shp.py "$2" "$3" "$4" "$5"
}

# TSPROC 72x126: art width-fit to the FULL 3x3 PLOT (72 classic; the 96-wide
# 4-cell fit read oversized next to the 2x2 tier — Luke, 2026-08-04). The
# building content is only 94 src px wide (the TS concrete apron is not
# drawn), so the plot-width fit runs at 4.09x — disc + chimney + smoke is
# ~90 classic px tall at that scale. The stub is sized so the DISC BOTTOM
# lands exactly on the plot's south edge. 138x150 = the BSIZE_44
# foundation: one extra cell (24 classic) of canvas at the BOTTOM offsets
# the half-cell-south anchor move so the art stays pixel-static on the plot.
ts_stub TSPROC "$TMPDIR/tsproc_stub.shp" 138 174 2
PACK_ARGS+=("$TMPDIR/tsproc_stub.shp:TSPROC.SHP")
ts_stub TSPROC "$TMPDIR/tsprocmk_stub.shp" 138 174 19
PACK_ARGS+=("$TMPDIR/tsprocmk_stub.shp:TSPROCMAKE.SHP")
# TSWEAP 144x126: the 5x4 plot is 120x96 classic, and the extra 12 classic a
# side carries the concrete pad's overhang east and south. The hangar fits to
# 4 cells (96 classic) via the packer's fit_w -- the width a Mammoth Mk. II
# needs to clear the bay door.
ts_stub TSWEAP "$TMPDIR/tsweap_stub.shp" 168 126 2
PACK_ARGS+=("$TMPDIR/tsweap_stub.shp:TSWEAP.SHP")
ts_stub TSWEAP "$TMPDIR/tsweapmk_stub.shp" 168 126 19
# The bay-door overlay shares the building's canvas, so it needs the same stub
# box or the launcher scales the door to whatever shape file it was handed.
ts_stub TSWEAP "$TMPDIR/tsweap2_stub.shp" 168 126 18
PACK_ARGS+=("$TMPDIR/tsweap2_stub.shp:TSWEAP2.SHP")
# TSPILE 48x48: back to the grid-matched 2x2 plot width (the 60-overhang
# compromise predates the tier-wide size drop, Luke 2026-08-04).
ts_stub TSPILE "$TMPDIR/tspile_stub.shp" 48 48 2
PACK_ARGS+=("$TMPDIR/tspile_stub.shp:TSPILE.SHP")
ts_stub TSPILE "$TMPDIR/tspilemk_stub.shp" 48 48 19
PACK_ARGS+=("$TMPDIR/tspilemk_stub.shp:TSPILEMAKE.SHP")
PACK_ARGS+=("$TMPDIR/tsweapmk_stub.shp:TSWEAPMAKE.SHP")
# TSRADR 48x96 on the 2x2 plot (TS-authentic Foundation=2x2): Obelisk
# treatment, the dish tower rises a full row above the box. The 3x2/72x150
# size-up read oversized next to the 2x2 power plant (Luke, 2026-08-04).
ts_stub TSRADR "$TMPDIR/tsradr_stub.shp" 48 96 2
PACK_ARGS+=("$TMPDIR/tsradr_stub.shp:TSRADR.SHP")
ts_stub TSRADR "$TMPDIR/tsradrmk_stub.shp" 48 96 20
# TSPOWR 48x48 on the TS-authentic 2x2 grid, same plot as RA POWR (66-on-3x2
# still read oversized -- Luke, 2026-08-04).
ts_stub TSPOWR "$TMPDIR/tspowr_stub.shp" 48 48 2
PACK_ARGS+=("$TMPDIR/tspowr_stub.shp:TSPOWR.SHP")
ts_stub TSPOWR "$TMPDIR/tspowrmk_stub.shp" 48 48 13
PACK_ARGS+=("$TMPDIR/tspowrmk_stub.shp:TSPOWRMAKE.SHP")
PACK_ARGS+=("$TMPDIR/tsradrmk_stub.shp:TSRADRMAKE.SHP")
# TSFACT 72x72 = the RA-conyard 3x3 box (BSIZE_33) + bib, content inside it
# (the 4x3 tier read oversized next to the shrunk tier, Luke 2026-08-04).
ts_stub TSFACT "$TMPDIR/tsfact_stub.shp" 72 72 2
PACK_ARGS+=("$TMPDIR/tsfact_stub.shp:TSFACT.SHP")
ts_stub TSFACT "$TMPDIR/tsfactmk_stub.shp" 72 72 32
PACK_ARGS+=("$TMPDIR/tsfactmk_stub.shp:TSFACTMAKE.SHP")
ts_stub TSTECH "$TMPDIR/tstech_stub.shp" 72 48 2
PACK_ARGS+=("$TMPDIR/tstech_stub.shp:TSTECH.SHP")
ts_stub TSTECH "$TMPDIR/tstechmk_stub.shp" 72 48 19
PACK_ARGS+=("$TMPDIR/tstechmk_stub.shp:TSTECHMAKE.SHP")
ts_stub TSSILO "$TMPDIR/tssilo_stub.shp" 48 48 2
PACK_ARGS+=("$TMPDIR/tssilo_stub.shp:TSSILO.SHP")
ts_stub TSSILO "$TMPDIR/tssilomk_stub.shp" 48 48 19
PACK_ARGS+=("$TMPDIR/tssilomk_stub.shp:TSSILOMAKE.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/railfx_stub.shp" 24 24 12
PACK_ARGS+=("$TMPDIR/railfx_stub.shp:RAILFX.SHP")

# Repack into TFASSETS.MIX with TD-prefix renames.
python3 scripts/mix_tools.py pack "$OUTMIX" "${PACK_ARGS[@]}"
echo "TFASSETS.MIX rebuilt with ${#ENTRIES[@]} entries -> $OUTMIX"
