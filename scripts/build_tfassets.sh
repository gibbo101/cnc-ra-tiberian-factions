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
# tileset, no classic art); the stub declares the classic dimensions the
# launcher sizes the sprite, health bar and selection box from.
# ⚠ 48x48 (tank-sized) is DELIBERATE and matches [TSHVR] ShapeSize=48,48.
# The rack seat table (udata.cpp Hover_Rack_Seat) was eye-dialled by Luke
# against a sprite at THIS size and signed off 2026-08-19. Changing these
# dims rescales the sprite and invalidates every dialled seat -- do not
# "correct" it to 64x64 without redoing the whole seat arc.
# 96 frames: hull 0-31, rack 32-63, shadow 64-95 (the HD art's own shadow block).
python3 scripts/gen_stub_shp.py "$TMPDIR/tshvr_stub.shp" 48 48 96
PACK_ARGS+=("$TMPDIR/tshvr_stub.shp:TSHVR.SHP")

# TS walkers (Titan + Mammoth Mk. II) -- same HD-only stub pattern. Titan gets
# the tank box; the Mk. II's larger 56x56 box makes it render, select and
# health-bar as the hulk it is. RAILFX is the railgun helix spark anim (dims
# only; 6 frames).
python3 scripts/gen_stub_shp.py "$TMPDIR/tstitn_stub.shp" 56 56 128
PACK_ARGS+=("$TMPDIR/tstitn_stub.shp:TSTITN.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tshmec_stub.shp" 72 72 256
PACK_ARGS+=("$TMPDIR/tshmec_stub.shp:TSHMEC.SHP")

# Dropship-bay delivery pod -- the TS Dropship sprite (TSDSHP.ZIP, TS-HD-Graphics-Pack TSHD_VFX.XML).
# Bullet art, single west-facing frame. The launcher sizes HD art off the
# classic dims, so without this stub the pod inherits its donor's
# little-missile dims and the dropship renders TINY (live report, 2026-08-12).
# 123 = HD canvas 656 x 3/16. 656 is the TS-authentic relative scale (6.4
# canvas px per voxel, the shared unit factor) -- anything smaller reads
# tinier than the Mk. II it carries. Re-derive if render scale changes.
# 4 frames: shape 0 = the ship, 1..3 = pre-scaled shadow silhouettes for the
# growing-shadow descent buckets (Draw_It picks by Height).
python3 scripts/gen_stub_shp.py "$TMPDIR/tsdshp_stub.shp" 123 123 4
PACK_ARGS+=("$TMPDIR/tsdshp_stub.shp:TSDSHP.SHP")

# Mech Division token (UNIT_TSMDIV) -- a sidebar-only purchasable that the
# dropship pod expands into 3 Titans + 2 Wolverines; it never renders on the
# map, the stub exists purely so One_Time resolves its Image cleanly.
python3 scripts/gen_stub_shp.py "$TMPDIR/tsmdiv_stub.shp" 16 16 1
PACK_ARGS+=("$TMPDIR/tsmdiv_stub.shp:TSMDIV.SHP")
# TS units wave (Harvester / Wolverine / Disruptor / Amphibious APC) -- same
# HD-only stub pattern; frame counts match the HD zips (rot-only, walk, or
# body+turret) and dims match each unit's rules.ini ShapeSize.
# TSHARV 72x72: its 384 canvas at EA's own density (5.33 canvas px per classic px), so the HD truck's
# pixels draw one for one with EA's TD and RA harvesters'.
python3 scripts/gen_stub_shp.py "$TMPDIR/tsharv_stub.shp" 72 72 64
PACK_ARGS+=("$TMPDIR/tsharv_stub.shp:TSHARV.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tssmec_stub.shp" 48 48 128
PACK_ARGS+=("$TMPDIR/tssmec_stub.shp:TSSMEC.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tssonic_stub.shp" 56 56 64
PACK_ARGS+=("$TMPDIR/tssonic_stub.shp:TSSONIC.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsapc_stub.shp" 48 48 64
PACK_ARGS+=("$TMPDIR/tsapc_stub.shp:TSAPC.SHP")
# Mammoth Mk. I -- HD-only voxel render on a 512 canvas (body+turret 64 frames).
python3 scripts/gen_stub_shp.py "$TMPDIR/ts4tnk_stub.shp" 64 64 64
PACK_ARGS+=("$TMPDIR/ts4tnk_stub.shp:TS4TNK.SHP")
# RA2 easter-egg tanks (Apocalypse / Prism Tank) -- HD-only voxel renders, body+turret 64
# frames; the stub's dims are the box the launcher fits each canvas into (canvas / 8).
python3 scripts/gen_stub_shp.py "$TMPDIR/r2apoc_stub.shp" 56 56 64
PACK_ARGS+=("$TMPDIR/r2apoc_stub.shp:R2APOC.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/r2pris_stub.shp" 48 48 64
PACK_ARGS+=("$TMPDIR/r2pris_stub.shp:R2PRIS.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/c3mk3_stub.shp" 64 64 128
PACK_ARGS+=("$TMPDIR/c3mk3_stub.shp:C3MK3.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/c3pred_stub.shp" 48 48 128
PACK_ARGS+=("$TMPDIR/c3pred_stub.shp:C3PRED.SHP")
# TS aircraft (Orca Fighter / Orca Bomber / Carryall) -- HD-only voxel renders, 32
# facings each; dims match each one's rules.ini ShapeSize.
python3 scripts/gen_stub_shp.py "$TMPDIR/tsorca_stub.shp" 48 48 32
PACK_ARGS+=("$TMPDIR/tsorca_stub.shp:TSORCA.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsorcab_stub.shp" 48 48 32
PACK_ARGS+=("$TMPDIR/tsorcab_stub.shp:TSORCAB.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tscarry_stub.shp" 56 56 32
PACK_ARGS+=("$TMPDIR/tscarry_stub.shp:TSCARRY.SHP")
# TS Juggernaut -- 202 shapes: 120 walk + 32 deployed at rest + 32 deployed aiming + 18 deploy ladder.
python3 scripts/gen_stub_shp.py "$TMPDIR/tsjugg_stub.shp" 56 56 202
PACK_ARGS+=("$TMPDIR/tsjugg_stub.shp:TSJUGG.SHP")
# TS Limpet Drone -- 10 crawl frames then their 10 shadows, no facings (24x24 = ShapeSize). Its mine's stubs sit with the buildings below.
python3 scripts/gen_stub_shp.py "$TMPDIR/tslimp_stub.shp" 24 24 20
PACK_ARGS+=("$TMPDIR/tslimp_stub.shp:TSLIMP.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsmemp_stub.shp" 48 48 32
PACK_ARGS+=("$TMPDIR/tsmemp_stub.shp:TSMEMP.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tslpst_stub.shp" 48 48 32
PACK_ARGS+=("$TMPDIR/tslpst_stub.shp:TSLPST.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsmwar_stub.shp" 48 48 32
PACK_ARGS+=("$TMPDIR/tsmwar_stub.shp:TSMWAR.SHP")
# Subterranean pair (Devil's Tongue / Sub APC) -- 112 shapes each: 32 driving
# + 40 dive + 40 emerge pitch-ladder frames (docs/subterranean-design.md).
python3 scripts/gen_stub_shp.py "$TMPDIR/tssubtank_stub.shp" 48 48 113
PACK_ARGS+=("$TMPDIR/tssubtank_stub.shp:TSSUBTANK.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tssapc_stub.shp" 48 48 113
PACK_ARGS+=("$TMPDIR/tssapc_stub.shp:TSSAPC.SHP")
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

# TSPROC 138x174 = the HD refinery's 736x928 canvas centred on its 4x3 plot: the
# building turned 22.5 degrees inside the plot's columns, the bib on its south edge.
ts_stub TSPROC "$TMPDIR/tsproc_stub.shp" 138 174 2
PACK_ARGS+=("$TMPDIR/tsproc_stub.shp:TSPROC.SHP")
ts_stub TSPROC "$TMPDIR/tsprocmk_stub.shp" 138 174 24
PACK_ARGS+=("$TMPDIR/tsprocmk_stub.shp:TSPROCMAKE.SHP")
# The refinery's event layers share its canvas: the flare stack's fire (20 lit,
# then 20 empty) and the dock lid (5 + 5).
ts_stub TSPROC "$TMPDIR/tsprocfr_stub.shp" 138 174 40
PACK_ARGS+=("$TMPDIR/tsprocfr_stub.shp:TSPROCFR.SHP")
ts_stub TSPROC "$TMPDIR/tsprocld_stub.shp" 138 174 10
PACK_ARGS+=("$TMPDIR/tsprocld_stub.shp:TSPROCLD.SHP")
# ...and its front, drawn over a docked truck: the idle loop's 32 frames masked to the building in front of
# the dock lane.
ts_stub TSPROC "$TMPDIR/tsprocnf_stub.shp" 138 174 32
PACK_ARGS+=("$TMPDIR/tsprocnf_stub.shp:TSPROCNF.SHP")
# TSWEAP 90x96 = the HD war factory's 480x512 canvas centred on its 3x4 plot (72x96 classic): RA's 3x3
# war factory slot with an empty row behind, which the build-up's raised poles reach into; the shadow and
# debris reach past the sides.
ts_stub TSWEAP "$TMPDIR/tsweap_stub.shp" 90 96 2
PACK_ARGS+=("$TMPDIR/tsweap_stub.shp:TSWEAP.SHP")
ts_stub TSWEAP "$TMPDIR/tsweapmk_stub.shp" 90 96 26
# The door, under-door and near-face layers share the building's canvas.
ts_stub TSWEAP "$TMPDIR/tsweapdr_stub.shp" 90 96 18
PACK_ARGS+=("$TMPDIR/tsweapdr_stub.shp:TSWEAPDR.SHP")
ts_stub TSWEAP "$TMPDIR/tsweapud_stub.shp" 90 96 4
PACK_ARGS+=("$TMPDIR/tsweapud_stub.shp:TSWEAPUD.SHP")
# The near face (the building but for its door bay), the idle cycle x healthy/damaged.
ts_stub TSWEAP "$TMPDIR/tsweapnf_stub.shp" 90 96 64
PACK_ARGS+=("$TMPDIR/tsweapnf_stub.shp:TSWEAPNF.SHP")
ts_stub TSWEAP "$TMPDIR/tsweapnu_stub.shp" 90 96 64
PACK_ARGS+=("$TMPDIR/tsweapnu_stub.shp:TSWEAPNU.SHP")
# The deployed Mobile War Factory, on TSWEAP's stub: no idle cycle, a 12-stage shutter.
ts_stub TSDWEAP "$TMPDIR/tsdweap_stub.shp" 168 126 2
PACK_ARGS+=("$TMPDIR/tsdweap_stub.shp:TSDWEAP.SHP")
ts_stub TSDWEAP "$TMPDIR/tsdweapmk_stub.shp" 168 126 19
PACK_ARGS+=("$TMPDIR/tsdweapmk_stub.shp:TSDWEAPMAKE.SHP")
ts_stub TSDWEAP "$TMPDIR/tsdweapdr_stub.shp" 168 126 24
PACK_ARGS+=("$TMPDIR/tsdweapdr_stub.shp:TSDWEAPDR.SHP")
ts_stub TSDWEAP "$TMPDIR/tsdweapud_stub.shp" 168 126 4
PACK_ARGS+=("$TMPDIR/tsdweapud_stub.shp:TSDWEAPUD.SHP")
ts_stub TSDWEAP "$TMPDIR/tsdweapnf_stub.shp" 168 126 2
PACK_ARGS+=("$TMPDIR/tsdweapnf_stub.shp:TSDWEAPNF.SHP")
ts_stub TSDWEAP "$TMPDIR/tsdweapnu_stub.shp" 168 126 2
PACK_ARGS+=("$TMPDIR/tsdweapnu_stub.shp:TSDWEAPNU.SHP")
# TSPILE 48x72 = the HD barracks' 256x384 canvas centred on its 2x1 plot: the bunkers on the
# plot row, the masts and flag in the row behind, empty canvas over the bib row in front.
ts_stub TSPILE "$TMPDIR/tspile_stub.shp" 48 72 2
PACK_ARGS+=("$TMPDIR/tspile_stub.shp:TSPILE.SHP")
ts_stub TSPILE "$TMPDIR/tspilemk_stub.shp" 48 72 24
PACK_ARGS+=("$TMPDIR/tspilemk_stub.shp:TSPILEMAKE.SHP")
# TS Limpet Mine on a 48x48 stub (the build-up's standing drone overhangs the 1x1 plot).
ts_stub TSDLIMP "$TMPDIR/tsdlimp_stub.shp" 48 48 20
PACK_ARGS+=("$TMPDIR/tsdlimp_stub.shp:TSDLIMP.SHP")
ts_stub TSDLIMP "$TMPDIR/tsdlimpmk_stub.shp" 48 48 19
PACK_ARGS+=("$TMPDIR/tsdlimpmk_stub.shp:TSDLIMPMAKE.SHP")
ts_stub TSDPSA "$TMPDIR/tsdpsa_stub.shp" 48 78 10
PACK_ARGS+=("$TMPDIR/tsdpsa_stub.shp:TSDPSA.SHP")
ts_stub TSDPSA "$TMPDIR/tsdpsamk_stub.shp" 48 78 36
PACK_ARGS+=("$TMPDIR/tsdpsamk_stub.shp:TSDPSAMAKE.SHP")
PACK_ARGS+=("$TMPDIR/tsweapmk_stub.shp:TSWEAPMAKE.SHP")
# TSRADR 48x111 = the HD radar's 256x592 canvas centred on its 2x2 plot: the tower and its antennas
# rise into the headroom above.
ts_stub TSRADR "$TMPDIR/tsradr_stub.shp" 48 111 2
PACK_ARGS+=("$TMPDIR/tsradr_stub.shp:TSRADR.SHP")
ts_stub TSRADR "$TMPDIR/tsradrmk_stub.shp" 48 111 26
# TSDEPT 72x72 = the HD service depot's 384x384 canvas, its 3x3 plot; its repair flash (TSDEPTRP)
# draws on the same stub.
ts_stub TSDEPT "$TMPDIR/tsdept_stub.shp" 72 72 2
PACK_ARGS+=("$TMPDIR/tsdept_stub.shp:TSDEPT.SHP")
ts_stub TSDEPT "$TMPDIR/tsdeptmk_stub.shp" 72 72 19
PACK_ARGS+=("$TMPDIR/tsdeptmk_stub.shp:TSDEPTMAKE.SHP")
# TSHPAD 48x48 = the HD helipad's 256x256 canvas, its 2x2 plot.
ts_stub TSHPAD "$TMPDIR/tshpad_stub.shp" 48 48 2
PACK_ARGS+=("$TMPDIR/tshpad_stub.shp:TSHPAD.SHP")
ts_stub TSHPAD "$TMPDIR/tshpadmk_stub.shp" 48 48 24
PACK_ARGS+=("$TMPDIR/tshpadmk_stub.shp:TSHPADMAKE.SHP")
# TSDROP 72x48 = the HD dropship bay's 384x256 canvas, its 3x2 plot.
ts_stub TSDROP "$TMPDIR/tsdrop_stub.shp" 72 48 2
PACK_ARGS+=("$TMPDIR/tsdrop_stub.shp:TSDROP.SHP")
ts_stub TSDROP "$TMPDIR/tsdropmk_stub.shp" 72 48 19
PACK_ARGS+=("$TMPDIR/tsdropmk_stub.shp:TSDROPMAKE.SHP")
# TSPOWR 48x51 = the HD rebuild's 256x272 canvas: the 2x2 plot centred, the cooling
# tower rising into the headroom above it.
ts_stub TSPOWR "$TMPDIR/tspowr_stub.shp" 48 51 2
PACK_ARGS+=("$TMPDIR/tspowr_stub.shp:TSPOWR.SHP")
# TS EMP cannon: static base (healthy + damaged) on the 2x2 48x48 box; the PULSCAN
# turret is the TSPULST layer (32 facings).
ts_stub TSPULS "$TMPDIR/tspuls_stub.shp" 48 48 2
ts_stub TSPULS "$TMPDIR/tspulst_stub.shp" 48 48 32
PACK_ARGS+=("$TMPDIR/tspulst_stub.shp:TSPULST.SHP")
PACK_ARGS+=("$TMPDIR/tspuls_stub.shp:TSPULS.SHP")
ts_stub TSPULS "$TMPDIR/tspulsmk_stub.shp" 48 48 13
PACK_ARGS+=("$TMPDIR/tspulsmk_stub.shp:TSPULSMAKE.SHP")
ts_stub TSPOWR "$TMPDIR/tspowrmk_stub.shp" 48 51 24
PACK_ARGS+=("$TMPDIR/tspowrmk_stub.shp:TSPOWRMAKE.SHP")
# TSTURB 24x24 on a 1x1: the power-turbine addon's placement GHOST (it never
# stands on the map — placement installs it into a TSPOWR). No MAKE stub: the
# buildup state is unreachable.
ts_stub TSTURB "$TMPDIR/tsturb_stub.shp" 24 24 2
PACK_ARGS+=("$TMPDIR/tsturb_stub.shp:TSTURB.SHP")
# TSWALL 33x60 (canvas 176x320: joined arms overshoot the cell edge): the TS concrete wall OVERLAY's classic stub
# (the engine loads walls as non-theatre "<INI>.SHP" by IniName). 48 frames =
# 16 join icons x 3 damage stages, RA's wall layout. Taller than the cell so a
# north-south run's crest can rise above the cell's north edge. No MAKE stub:
# walls never enumerate in the buildup state (dllinterface IsWall guard).
ts_stub TSWALL "$TMPDIR/tswall_stub.shp" 36 60 48
PACK_ARGS+=("$TMPDIR/tswall_stub.shp:TSWALL.SHP")
# TSNWALL: the TS Nod wall overlay's classic stub, TSWALL's twin.
ts_stub TSNWALL "$TMPDIR/tsnwall_stub.shp" 36 60 48
PACK_ARGS+=("$TMPDIR/tsnwall_stub.shp:TSNWALL.SHP")
# TS GDI gates (HD canvas = the footprint): east-west 72x24, north-south 24x72; 20 door frames
# (10 stages, healthy + damaged) and the 10-frame rise out of the slot.
ts_stub TSGATEH "$TMPDIR/tsgateh_stub.shp" 72 24 20
PACK_ARGS+=("$TMPDIR/tsgateh_stub.shp:TSGATEH.SHP")
ts_stub TSGATEH "$TMPDIR/tsgatehmk_stub.shp" 72 24 10
PACK_ARGS+=("$TMPDIR/tsgatehmk_stub.shp:TSGATEHMAKE.SHP")
ts_stub TSGATEV "$TMPDIR/tsgatev_stub.shp" 24 72 20
PACK_ARGS+=("$TMPDIR/tsgatev_stub.shp:TSGATEV.SHP")
ts_stub TSGATEV "$TMPDIR/tsgatevmk_stub.shp" 24 72 10
PACK_ARGS+=("$TMPDIR/tsgatevmk_stub.shp:TSGATEVMAKE.SHP")
# The other gates: the same canvases, each with its own door frame count (the Tesla gate's
# 20 door frames are followed by its 6 shut-loop frames).
ts_stub TSNGATEH "$TMPDIR/tsngateh_stub.shp" 72 24 14
PACK_ARGS+=("$TMPDIR/tsngateh_stub.shp:TSNGATEH.SHP")
ts_stub TSNGATEH "$TMPDIR/tsngatehmk_stub.shp" 72 24 7
PACK_ARGS+=("$TMPDIR/tsngatehmk_stub.shp:TSNGATEHMAKE.SHP")
ts_stub TSNGATEV "$TMPDIR/tsngatev_stub.shp" 24 72 14
PACK_ARGS+=("$TMPDIR/tsngatev_stub.shp:TSNGATEV.SHP")
ts_stub TSNGATEV "$TMPDIR/tsngatevmk_stub.shp" 24 72 7
PACK_ARGS+=("$TMPDIR/tsngatevmk_stub.shp:TSNGATEVMAKE.SHP")
ts_stub ALGATEH "$TMPDIR/algateh_stub.shp" 72 24 20
PACK_ARGS+=("$TMPDIR/algateh_stub.shp:ALGATEH.SHP")
ts_stub ALGATEH "$TMPDIR/algatehmk_stub.shp" 72 24 10
PACK_ARGS+=("$TMPDIR/algatehmk_stub.shp:ALGATEHMAKE.SHP")
ts_stub ALGATEV "$TMPDIR/algatev_stub.shp" 24 72 20
PACK_ARGS+=("$TMPDIR/algatev_stub.shp:ALGATEV.SHP")
ts_stub ALGATEV "$TMPDIR/algatevmk_stub.shp" 24 72 10
PACK_ARGS+=("$TMPDIR/algatevmk_stub.shp:ALGATEVMAKE.SHP")
ts_stub SVGATEH "$TMPDIR/svgateh_stub.shp" 72 24 26
PACK_ARGS+=("$TMPDIR/svgateh_stub.shp:SVGATEH.SHP")
ts_stub SVGATEH "$TMPDIR/svgatehmk_stub.shp" 72 24 10
PACK_ARGS+=("$TMPDIR/svgatehmk_stub.shp:SVGATEHMAKE.SHP")
ts_stub SVGATEV "$TMPDIR/svgatev_stub.shp" 24 72 26
PACK_ARGS+=("$TMPDIR/svgatev_stub.shp:SVGATEV.SHP")
ts_stub SVGATEV "$TMPDIR/svgatevmk_stub.shp" 24 72 10
PACK_ARGS+=("$TMPDIR/svgatevmk_stub.shp:SVGATEVMAKE.SHP")
ts_stub TDGGATEH "$TMPDIR/tdggateh_stub.shp" 72 24 20
PACK_ARGS+=("$TMPDIR/tdggateh_stub.shp:TDGGATEH.SHP")
ts_stub TDGGATEH "$TMPDIR/tdggatehmk_stub.shp" 72 24 10
PACK_ARGS+=("$TMPDIR/tdggatehmk_stub.shp:TDGGATEHMAKE.SHP")
ts_stub TDGGATEV "$TMPDIR/tdggatev_stub.shp" 24 72 20
PACK_ARGS+=("$TMPDIR/tdggatev_stub.shp:TDGGATEV.SHP")
ts_stub TDGGATEV "$TMPDIR/tdggatevmk_stub.shp" 24 72 10
PACK_ARGS+=("$TMPDIR/tdggatevmk_stub.shp:TDGGATEVMAKE.SHP")
ts_stub TDNGATEH "$TMPDIR/tdngateh_stub.shp" 72 24 20
PACK_ARGS+=("$TMPDIR/tdngateh_stub.shp:TDNGATEH.SHP")
ts_stub TDNGATEH "$TMPDIR/tdngatehmk_stub.shp" 72 24 10
PACK_ARGS+=("$TMPDIR/tdngatehmk_stub.shp:TDNGATEHMAKE.SHP")
ts_stub TDNGATEV "$TMPDIR/tdngatev_stub.shp" 24 72 20
PACK_ARGS+=("$TMPDIR/tdngatev_stub.shp:TDNGATEV.SHP")
ts_stub TDNGATEV "$TMPDIR/tdngatevmk_stub.shp" 24 72 10
PACK_ARGS+=("$TMPDIR/tdngatevmk_stub.shp:TDNGATEVMAKE.SHP")
# TS component tower family, same 33x60 canvas family as the wall (176x320 HD):
# TSCTWR bare tower 2 frames (healthy/damaged) + rising buildup; TSVULC armed
# tower = 32 facings x {idle, recoil, damaged idle, damaged recoil} like TDGUN.
ts_stub TSCTWR "$TMPDIR/tsctwr_stub.shp" 36 60 2
PACK_ARGS+=("$TMPDIR/tsctwr_stub.shp:TSCTWR.SHP")
ts_stub TSCTWR "$TMPDIR/tsctwrmk_stub.shp" 36 60 17
PACK_ARGS+=("$TMPDIR/tsctwrmk_stub.shp:TSCTWRMAKE.SHP")
ts_stub TSVULC "$TMPDIR/tsvulc_stub.shp" 36 60 128
PACK_ARGS+=("$TMPDIR/tsvulc_stub.shp:TSVULC.SHP")
ts_stub TSVULC "$TMPDIR/tsvulcmk_stub.shp" 36 60 17
PACK_ARGS+=("$TMPDIR/tsvulcmk_stub.shp:TSVULCMAKE.SHP")
ts_stub TSROCK "$TMPDIR/tsrock_stub.shp" 36 60 128
PACK_ARGS+=("$TMPDIR/tsrock_stub.shp:TSROCK.SHP")
ts_stub TSROCK "$TMPDIR/tsrockmk_stub.shp" 36 60 17
PACK_ARGS+=("$TMPDIR/tsrockmk_stub.shp:TSROCKMAKE.SHP")
ts_stub TSCSAM "$TMPDIR/tscsam_stub.shp" 36 60 128
PACK_ARGS+=("$TMPDIR/tscsam_stub.shp:TSCSAM.SHP")
ts_stub TSCSAM "$TMPDIR/tscsammk_stub.shp" 36 60 17
PACK_ARGS+=("$TMPDIR/tscsammk_stub.shp:TSCSAMMAKE.SHP")
# TSPLUG 72x84 = the HD upgrade center's 384x448 canvas centred on its 3x2 plot (TS Upgrade
# Centre, addon host): the antennas rise into the headroom above the box.
ts_stub TSPLUG "$TMPDIR/tsplug_stub.shp" 72 84 2
PACK_ARGS+=("$TMPDIR/tsplug_stub.shp:TSPLUG.SHP")
ts_stub TSPLUG "$TMPDIR/tsplugmk_stub.shp" 72 84 24
PACK_ARGS+=("$TMPDIR/tsplugmk_stub.shp:TSPLUGMAKE.SHP")
# TSPION 24x24: the Ion Cannon Uplink plug's placement ghost (never on map).
ts_stub TSPION "$TMPDIR/tspion_stub.shp" 24 24 2
PACK_ARGS+=("$TMPDIR/tspion_stub.shp:TSPION.SHP")
# TSPODS / TSSEEK 24x24: the Drop Pod Node and Seeker Control plug ghosts (never on map).
ts_stub TSPODS "$TMPDIR/tspods_stub.shp" 24 24 2
PACK_ARGS+=("$TMPDIR/tspods_stub.shp:TSPODS.SHP")
ts_stub TSSEEK "$TMPDIR/tsseek_stub.shp" 24 24 2
PACK_ARGS+=("$TMPDIR/tsseek_stub.shp:TSSEEK.SHP")
# TSHUNT 24x24 x 8: the hunter seeker droid (aircraft; 192 canvas / 8, one facing x 8 spin frames).
ts_stub TSHUNT "$TMPDIR/tshunt_stub.shp" 48 48 8
PACK_ARGS+=("$TMPDIR/tshunt_stub.shp:TSHUNT.SHP")
PACK_ARGS+=("$TMPDIR/tsradrmk_stub.shp:TSRADRMAKE.SHP")
# TSFACT 75x54 = the HD rebuild's 400x288 canvas: the yard turned 25 degrees like EA's yards and
# fitted inside the 3x2 plot's three columns, the plot centred, the vault rising into the margin.
ts_stub TSFACT "$TMPDIR/tsfact_stub.shp" 75 54 2
PACK_ARGS+=("$TMPDIR/tsfact_stub.shp:TSFACT.SHP")
ts_stub TSFACT "$TMPDIR/tsfactmk_stub.shp" 75 54 32
PACK_ARGS+=("$TMPDIR/tsfactmk_stub.shp:TSFACTMAKE.SHP")
# TSTECH 78x93 = the HD tech centre's 416x496 canvas centred on its 3x2 plot: the wedge on the south
# row, the fins and dome in the north row (walk-behind headroom), the bib row in front.
ts_stub TSTECH "$TMPDIR/tstech_stub.shp" 78 93 2
PACK_ARGS+=("$TMPDIR/tstech_stub.shp:TSTECH.SHP")
ts_stub TSTECH "$TMPDIR/tstechmk_stub.shp" 78 93 24
PACK_ARGS+=("$TMPDIR/tstechmk_stub.shp:TSTECHMAKE.SHP")
# TSFGEN 72x72: the Firestorm Generator on the Tech Center's 3x2 plot and square canvas.
ts_stub TSFGEN "$TMPDIR/tsfgen_stub.shp" 72 72 2
PACK_ARGS+=("$TMPDIR/tsfgen_stub.shp:TSFGEN.SHP")
ts_stub TSFGEN "$TMPDIR/tsfgenmk_stub.shp" 72 72 19
PACK_ARGS+=("$TMPDIR/tsfgenmk_stub.shp:TSFGENMAKE.SHP")
# TSFSDF 33x60, 64 frames: the Firestorm Wall Section on the wall packers' 176x320 canvas.
ts_stub TSFSDF "$TMPDIR/tsfsdf_stub.shp" 33 60 64
PACK_ARGS+=("$TMPDIR/tsfsdf_stub.shp:TSFSDF.SHP")
# TSSILO 48x72 = the HD silo's 256x384 canvas centred on its 2x1 plot: the silo on the plot row,
# empty canvas over the bib row in front.
ts_stub TSSILO "$TMPDIR/tssilo_stub.shp" 48 72 2
PACK_ARGS+=("$TMPDIR/tssilo_stub.shp:TSSILO.SHP")
ts_stub TSSILO "$TMPDIR/tssilomk_stub.shp" 48 72 24
PACK_ARGS+=("$TMPDIR/tssilomk_stub.shp:TSSILOMAKE.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/railfx_stub.shp" 24 24 12
PACK_ARGS+=("$TMPDIR/railfx_stub.shp:RAILFX.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsrailfxs_stub.shp" 24 24 12
PACK_ARGS+=("$TMPDIR/tsrailfxs_stub.shp:TSRAILFXS.SHP")
# TS Jumpjet Infantry: its own stub at E1's 50x39 carrying all 451 poses, since classic drawing
# drops any frame past the shape's count and E1 has 438. TSBANG34 is its shot-down burst.
python3 scripts/gen_stub_shp.py "$TMPDIR/tsjumpjet_stub.shp" 50 39 451
PACK_ARGS+=("$TMPDIR/tsjumpjet_stub.shp:TSJUMPJET.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsbang34_stub.shp" 17 17 13
PACK_ARGS+=("$TMPDIR/tsbang34_stub.shp:TSBANG34.SHP")
# TS GUNFIRE muzzle flash (ANIM_TS_GUNFIRE) -- 3 frames, HD-only stub.
python3 scripts/gen_stub_shp.py "$TMPDIR/tsgunfire_stub.shp" 24 24 3
PACK_ARGS+=("$TMPDIR/tsgunfire_stub.shp:TSGUNFIRE.SHP")
# TS Disruptor sonic wave (ANIM_TS_SONICWAVE) -- HD-only like the other TS art;
# frame count matches TSSONICW.ZIP, dims match the anim type's max dimension.
python3 scripts/gen_stub_shp.py "$TMPDIR/tssonicw_stub.shp" 24 24 25
PACK_ARGS+=("$TMPDIR/tssonicw_stub.shp:TSSONICW.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tssonicp_stub.shp" 24 24 25
PACK_ARGS+=("$TMPDIR/tssonicp_stub.shp:TSSONICP.SHP")
# TS subterranean DIG mound (ANIM_TS_DIG) -- 37 frames on a 64x64 classic box
# (TSDIG.ZIP is a 512 canvas, scripts/ts_pack_dig.py).
python3 scripts/gen_stub_shp.py "$TMPDIR/tsdig_stub.shp" 64 64 37
PACK_ARGS+=("$TMPDIR/tsdig_stub.shp:TSDIG.SHP")
# TS ion strike pair (scripts/ts_pack_ion.py): beam canvas 120x3840 (matches the TD beam's ~4076 virtual px: TD draws at VirtualScale 0x200, ours at 0x100), ring
# 832x408, both / 8 for the classic dims the launcher sizes the HD art off.
python3 scripts/gen_stub_shp.py "$TMPDIR/tsionbm_stub.shp" 15 480 15
PACK_ARGS+=("$TMPDIR/tsionbm_stub.shp:TSIONBM.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsionrng_stub.shp" 104 51 15
PACK_ARGS+=("$TMPDIR/tsionrng_stub.shp:TSIONRNG.SHP")
# E.M. Pulse set (scripts/ts_pack_emp.py): pulse ball 64x64, the two impacts 1216x704, the stun
# sparks 160x144, / 8.
python3 scripts/gen_stub_shp.py "$TMPDIR/tspulsbl_stub.shp" 8 8 23
PACK_ARGS+=("$TMPDIR/tspulsbl_stub.shp:TSPULSBL.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tspulsf1_stub.shp" 152 88 21
PACK_ARGS+=("$TMPDIR/tspulsf1_stub.shp:TSPULSF1.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tspulsf2_stub.shp" 152 88 15
PACK_ARGS+=("$TMPDIR/tspulsf2_stub.shp:TSPULSF2.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsempfx_stub.shp" 20 18 27
PACK_ARGS+=("$TMPDIR/tsempfx_stub.shp:TSEMPFX.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsmempfx_stub.shp" 144 72 12
PACK_ARGS+=("$TMPDIR/tsmempfx_stub.shp:TSMEMPFX.SHP")
# Firestorm field effects (scripts/ts_pack_firestorm_fx.py), canvas / 8.
python3 scripts/gen_stub_shp.py "$TMPDIR/tsfsidle_stub.shp" 12 136 19
PACK_ARGS+=("$TMPDIR/tsfsidle_stub.shp:TSFSIDLE.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsfsgrnd_stub.shp" 12 66 19
PACK_ARGS+=("$TMPDIR/tsfsgrnd_stub.shp:TSFSGRND.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsfsair_stub.shp" 12 28 19
PACK_ARGS+=("$TMPDIR/tsfsair_stub.shp:TSFSAIR.SHP")
# TS drop-pod strike set (scripts/ts_pack_pods.py): husks 192x192, DROPEXP puff
# 400x272, PODRING entry flash 400x208, SMOKEY trail 128x120, pod bullet body
# 192x192 — all / 8 for the classic dims the launcher sizes the HD art off.
python3 scripts/gen_stub_shp.py "$TMPDIR/tsdpod1_stub.shp" 24 24 8
PACK_ARGS+=("$TMPDIR/tsdpod1_stub.shp:TSDPOD1.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsdpod2_stub.shp" 24 24 8
PACK_ARGS+=("$TMPDIR/tsdpod2_stub.shp:TSDPOD2.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsdrpexp_stub.shp" 50 34 12
PACK_ARGS+=("$TMPDIR/tsdrpexp_stub.shp:TSDRPEXP.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tspodrng_stub.shp" 50 26 20
PACK_ARGS+=("$TMPDIR/tspodrng_stub.shp:TSPODRNG.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tssmokey_stub.shp" 16 15 11
PACK_ARGS+=("$TMPDIR/tssmokey_stub.shp:TSSMOKEY.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tspodblt_stub.shp" 24 24 1
PACK_ARGS+=("$TMPDIR/tspodblt_stub.shp:TSPODBLT.SHP")
# TS fire-stream particle (BULLET_TSFIRE) -- 76 shapes (4 axes x 19 states), 20x20 box
# (TSFIRE.ZIP is a 160 canvas, scripts/ts_pack_flame.py).
python3 scripts/gen_stub_shp.py "$TMPDIR/tsfire_stub.shp" 20 20 76
PACK_ARGS+=("$TMPDIR/tsfire_stub.shp:TSFIRE.SHP")

# TS component tower weapon art (scripts/ts_pack_towerfx.py): the Vulcan's muzzle flashes, the
# warheads' impacts, the SAM trail, the RPG canister and the SAM missile. Canvas = TS canvas x 4
# rounded up to whole 8 px cells; stub = canvas / 8; frame counts match the zips.
python3 scripts/gen_stub_shp.py "$TMPDIR/tsmgunn_stub.shp" 9 9 3
PACK_ARGS+=("$TMPDIR/tsmgunn_stub.shp:TSMGUNN.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsmgunne_stub.shp" 9 9 3
PACK_ARGS+=("$TMPDIR/tsmgunne_stub.shp:TSMGUNNE.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsmgune_stub.shp" 9 9 3
PACK_ARGS+=("$TMPDIR/tsmgune_stub.shp:TSMGUNE.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsmgunse_stub.shp" 9 9 3
PACK_ARGS+=("$TMPDIR/tsmgunse_stub.shp:TSMGUNSE.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsmguns_stub.shp" 9 9 3
PACK_ARGS+=("$TMPDIR/tsmguns_stub.shp:TSMGUNS.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsmgunsw_stub.shp" 9 9 3
PACK_ARGS+=("$TMPDIR/tsmgunsw_stub.shp:TSMGUNSW.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsmgunw_stub.shp" 9 9 3
PACK_ARGS+=("$TMPDIR/tsmgunw_stub.shp:TSMGUNW.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsmgunnw_stub.shp" 9 9 3
PACK_ARGS+=("$TMPDIR/tsmgunnw_stub.shp:TSMGUNNW.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tspiff_stub.shp" 30 18 12
PACK_ARGS+=("$TMPDIR/tspiff_stub.shp:TSPIFF.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsclsn16_stub.shp" 16 8 13
PACK_ARGS+=("$TMPDIR/tsclsn16_stub.shp:TSCLSN16.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsclsn22_stub.shp" 22 11 13
PACK_ARGS+=("$TMPDIR/tsclsn22_stub.shp:TSCLSN22.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsclsn30_stub.shp" 31 15 18
PACK_ARGS+=("$TMPDIR/tsclsn30_stub.shp:TSCLSN30.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsclsn42_stub.shp" 44 21 18
PACK_ARGS+=("$TMPDIR/tsclsn42_stub.shp:TSCLSN42.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsclsn58_stub.shp" 62 29 18
PACK_ARGS+=("$TMPDIR/tsclsn58_stub.shp:TSCLSN58.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsxgry1_stub.shp" 10 10 15
PACK_ARGS+=("$TMPDIR/tsxgry1_stub.shp:TSXGRY1.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsxgry2_stub.shp" 18 14 13
PACK_ARGS+=("$TMPDIR/tsxgry2_stub.shp:TSXGRY2.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsexpsml_stub.shp" 14 12 14
PACK_ARGS+=("$TMPDIR/tsexpsml_stub.shp:TSEXPSML.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tssmoky2_stub.shp" 8 7 11
PACK_ARGS+=("$TMPDIR/tssmoky2_stub.shp:TSSMOKY2.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tscanist_stub.shp" 4 3 32
PACK_ARGS+=("$TMPDIR/tscanist_stub.shp:TSCANIST.SHP")
python3 scripts/gen_stub_shp.py "$TMPDIR/tsdiscus_stub.shp" 4 2 32
PACK_ARGS+=("$TMPDIR/tsdiscus_stub.shp:TSDISCUS.SHP")

# Repack into TFASSETS.MIX with TD-prefix renames.
python3 scripts/mix_tools.py pack "$OUTMIX" "${PACK_ARGS[@]}"
echo "TFASSETS.MIX rebuilt with ${#ENTRIES[@]} entries -> $OUTMIX"
