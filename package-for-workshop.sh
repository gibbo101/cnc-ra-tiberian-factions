#!/usr/bin/env bash
# Stage the freshly-built mod into the Workshop-required wrapper folder layout.
#
# The Steam Workshop scanner for App 1213210 looks for ccmod.json inside a
# named SUBFOLDER of the uploaded content (i.e. <workshop-item>/<ModName>/ccmod.json),
# not at the root. Our build produces build/remaster/Vanilla_RA/ccmod.json which
# is the right INSIDE-folder shape, but the uploader needs to point at a PARENT
# folder containing Vanilla_RA/. This script makes that parent at dist/workshop-content/.
#
# Idempotent. Uses rsync to mirror the build output into the wrapper subfolder.
#
# IMPORTANT: must NOT use a symlink for the subfolder. SteamUGC preserves
# symlinks AS symlinks in the depot, and the Deck (and other Linux clients)
# fail to install with "Disk write failure" trying to materialise them.
#
# License: GPL v3 (inherited from Vanilla Conquer base).

set -euo pipefail
cd "$(dirname "$0")"

BUILD_DIR="build/remaster/Vanilla_RA"
STAGE_DIR="dist/workshop-content"
SUBFOLDER_NAME="Vanilla_RA"

# --- Release build: dev cheats compiled OUT ----------------------------------
# package-for-workshop ALWAYS rebuilds with -DTF_DEV_BUILD=0, so the shipped DLL
# never contains dev cheat code (instant-build, reveal-all, A* diagnostic log) no
# matter what state the local dev build is in. Adding the flag changes the cmake
# cache, which forces a reconfigure + recompile of the affected files.
# NOTE: this leaves the build/ cache at TF_DEV_BUILD=0. The standard local build
# command (VC_CXX_FLAGS="-w;-fpermissive") resets it back to dev (cheats on)
# because the differing flag string re-triggers a reconfigure. Always pass
# VC_CXX_FLAGS explicitly for local builds; a bare `cmake --workflow` reuses the
# cached release flags and would (harmlessly) build a no-cheats local DLL.
#
# The fifth faction (Tiberian Sun GDI) ships: TF_TS_GDI_FACTION keeps its default of 1, so the
# DLL and the repo's CONFIG.MEG and picker art are already in release shape.

# A re-packed vehicle comes out of its packer with the hull drawn high; unit_centring.py moves
# it onto the unit and records the drop the fire points need. Refuse to ship one it hasn't seen.
if ! python3 scripts/unit_centring.py --check > /dev/null; then
    python3 scripts/unit_centring.py --check >&2
    echo "ERROR: a vehicle's hull is off centre. Run scripts/unit_centring.py and rebuild." >&2
    exit 1
fi

# A release ships with its docs closed out to the rules in docs/README.md.
if ! python3 scripts/docs_check.py >&2; then
    echo "ERROR: the docs break the rules in docs/README.md. Fix them before packaging." >&2
    exit 1
fi

# A release ships with its code comments to the rules in CLAUDE.md (no names, no dates, no missing docs).
if ! python3 scripts/code_check.py >&2; then
    echo "ERROR: code comments break the rules in CLAUDE.md. Fix them before packaging." >&2
    exit 1
fi

echo "==> Release build (TF_DEV_BUILD=0 — dev cheats compiled out)"
CMAKE_TOOLCHAIN_FILE=cmake/i686-mingw-w64-toolchain.cmake \
  VC_CXX_FLAGS="-w;-fpermissive;-DTF_DEV_BUILD=0" \
  cmake --workflow --preset remaster

# The build's copy step never deletes, so build/ can hold files the source no longer has. The
# mod folder is staged again from scratch: the mod's own tree, the asset packs, the DLL.
BUILT_DLL="build/remaster/RelWithDebInfo/RedAlert.dll"
if [[ ! -f "$BUILT_DLL" ]]; then
    echo "ERROR: $BUILT_DLL not found after the release build." >&2
    exit 1
fi
rm -rf "$BUILD_DIR"
python3 scripts/stage_asset_packs.py --full "$BUILD_DIR"
cp "$BUILT_DLL" "$BUILD_DIR/Data/RedAlert.dll"

mkdir -p "$STAGE_DIR/$SUBFOLDER_NAME"
# Remove any existing symlink at the destination (legacy from earlier script versions)
[[ -L "$STAGE_DIR/$SUBFOLDER_NAME" ]] && rm "$STAGE_DIR/$SUBFOLDER_NAME" && mkdir -p "$STAGE_DIR/$SUBFOLDER_NAME"
rsync -a --delete "$BUILD_DIR/" "$STAGE_DIR/$SUBFOLDER_NAME/"

# --- Startup intro: gitignored, so make sure the locked cut is what ships -------
STAGED_INTRO="$STAGE_DIR/$SUBFOLDER_NAME/Data/ART/MOVIES/RA/REDINTRO.BK2"
WANT_INTRO="$(cat scripts/intro_work/REDINTRO.md5)"
if [[ ! -f "$STAGED_INTRO" ]]; then
    echo "ERROR: no startup intro in the staged mod. Build it: scripts/intro_work/build_intro.sh" >&2
    exit 1
fi
if [[ "$(md5sum "$STAGED_INTRO" | cut -d' ' -f1)" != "$WANT_INTRO" ]]; then
    echo "ERROR: staged REDINTRO.BK2 is not the locked cut (want md5 $WANT_INTRO)." >&2
    exit 1
fi
echo "✓ Startup intro is the locked cut ($WANT_INTRO)"

# --- CAMPAIGNS page textures and the UI atlas: gitignored, so make sure the locked set ships ---
if ! (cd "$STAGE_DIR/$SUBFOLDER_NAME/Data/ART/TEXTURES/SRGB" && md5sum --quiet -c -) < scripts/campaigns_work/textures.md5; then
    echo "ERROR: the staged CAMPAIGNS page textures or UI atlas are missing or stale. Build them: scripts/campaigns_page_build.sh" >&2
    exit 1
fi
echo "✓ CAMPAIGNS page textures and UI atlas match scripts/campaigns_work/textures.md5"

# --- Strip debug symbols from the shipped DLL --------------------------------
# The remaster preset builds RelWithDebInfo, embedding ~25MB of DWARF debug
# sections (.debug_info/.debug_line/...) that bloat RedAlert.dll from ~2MB to
# ~27MB. They do nothing in the shipped mod: no debugger is attached to the
# Proton DLL, and our runtime diagnostics are fprintf-based — compiled into
# .text, so they survive stripping. Strip ONLY this staged Workshop copy;
# build/ and the Deck deploy keep full symbols for local debugging.
STRIP_BIN="$(command -v i686-w64-mingw32-strip || true)"
STAGED_DLL="$STAGE_DIR/$SUBFOLDER_NAME/Data/RedAlert.dll"
if [[ -n "$STRIP_BIN" && -f "$STAGED_DLL" ]]; then
    before="$(du -h "$STAGED_DLL" | cut -f1)"
    "$STRIP_BIN" --strip-all "$STAGED_DLL"
    echo "✓ Stripped RedAlert.dll: $before → $(du -h "$STAGED_DLL" | cut -f1)"
elif [[ -z "$STRIP_BIN" ]]; then
    echo "WARNING: i686-w64-mingw32-strip not found — shipping UNSTRIPPED DLL ($(du -h "$STAGED_DLL" | cut -f1))." >&2
fi

echo "✓ Workshop staging ready ($(du -sh "$STAGE_DIR/$SUBFOLDER_NAME" | cut -f1)):"
ls -la "$STAGE_DIR/"
echo
echo "Point tools/workshop-uploader/workshop.json contentfolder at:"
echo "  ../../$STAGE_DIR"
echo
echo "Then publish with:"
echo "  cd tools/workshop-uploader"
echo "  dotnet run --no-build -- workshop.json \"vX.Y.Z — change note\""
