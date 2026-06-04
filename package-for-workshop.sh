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
# Confirmed 2026-05-20: the symlink-based first attempt broke the published
# item until re-uploaded with a real-dir copy.
#
# License: GPL v3 (inherited from Vanilla Conquer base).

set -euo pipefail
cd "$(dirname "$0")"

BUILD_DIR="build/remaster/Vanilla_RA"
STAGE_DIR="dist/workshop-content"
SUBFOLDER_NAME="Vanilla_RA"

if [[ ! -d "$BUILD_DIR" ]]; then
    echo "ERROR: $BUILD_DIR not found. Run a build first:" >&2
    echo "  CMAKE_TOOLCHAIN_FILE=cmake/i686-mingw-w64-toolchain.cmake \\" >&2
    echo "    VC_CXX_FLAGS=\"-w;-fpermissive\" \\" >&2
    echo "    cmake --workflow --preset remaster" >&2
    exit 1
fi

mkdir -p "$STAGE_DIR/$SUBFOLDER_NAME"
# Remove any existing symlink at the destination (legacy from earlier script versions)
[[ -L "$STAGE_DIR/$SUBFOLDER_NAME" ]] && rm "$STAGE_DIR/$SUBFOLDER_NAME" && mkdir -p "$STAGE_DIR/$SUBFOLDER_NAME"
rsync -a --delete "$BUILD_DIR/" "$STAGE_DIR/$SUBFOLDER_NAME/"

# --- Strip debug symbols from the shipped DLL --------------------------------
# The remaster preset builds RelWithDebInfo, embedding ~25MB of DWARF debug
# sections (.debug_info/.debug_line/...) that bloat RedAlert.dll from ~2MB to
# ~27MB. They do nothing in the shipped mod: no debugger is attached to the
# Proton DLL, and our runtime diagnostics are fprintf-based — compiled into
# .text, so they survive stripping. Strip ONLY this staged Workshop copy;
# build/ and the Deck deploy keep full symbols for local debugging.
# (DontCryJustDie Workshop report 2026-06-04: "27mb when the original is 1.17mb".)
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
