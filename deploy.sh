#!/usr/bin/env bash
# Build the mod (mingw cross-compile) and mirror-deploy to the Steam Deck.
#
# Prereqs (one-time):
#   - apt: cmake g++-mingw-w64 mingw-w64-tools ninja-build rsync openssh-client
#   - ssh: passwordless key auth to deck@steamdeck (Tailscale hostname)
#   - C&C Remastered launched at least once on the Deck (creates the Mods folder)
#
# Behavior:
#   1. cmake --workflow --preset remaster — produces build/remaster/Vanilla_RA/
#      which already contains the DLL + resources/ content packaged together.
#   2. rsync -av --delete build/remaster/Vanilla_RA/ → deck:.../Mods/Red_Alert/Vanilla_RA/
#      — the --delete is what keeps the Deck from accumulating drift: anything
#      on the Deck not present in build output gets removed.
#
# Flags:
#   --no-build       Skip cmake and rsync the existing build output as-is.
#   --dry-run        rsync --dry-run for a preview of what would change.
#   --no-delete      Drop the --delete flag (rare; mirrors-only mode).
#   --yes            Skip the orphan-deletion confirmation prompt.
#
# License: GPL v3 (inherited from Vanilla Conquer base).

set -euo pipefail
cd "$(dirname "$0")"

NO_BUILD=0
DRY_RUN=0
DELETE_FLAG="--delete"
AUTO_YES=0
for arg in "$@"; do
    case "$arg" in
        --no-build) NO_BUILD=1 ;;
        --dry-run)  DRY_RUN=1 ;;
        --no-delete) DELETE_FLAG="" ;;
        --yes|-y)   AUTO_YES=1 ;;
        *) echo "Unknown flag: $arg" >&2; exit 2 ;;
    esac
done

DECK_HOST="${DECK_HOST:-deck@steamdeck}"
DECK_MODS_DIR="/home/deck/.steam/steam/steamapps/compatdata/1213210/pfx/drive_c/users/steamuser/Documents/CnCRemastered/Mods/Red_Alert"
DECK_TARGET="$DECK_HOST:$DECK_MODS_DIR/Vanilla_RA/"
LOCAL_OUTPUT="build/remaster/Vanilla_RA/"

if [[ "$NO_BUILD" -eq 0 ]]; then
    echo "==> Building Vanilla_RA target (mingw cross-compile, remaster preset)"
    # Force a clean re-pack so resources/ changes always land in the output
    # folder. cmake's file(COPY) inside the workflow doesn't always reflect
    # resources/ deletions; nuking the output is the cheap correct thing.
    rm -rf "$LOCAL_OUTPUT"
    CMAKE_TOOLCHAIN_FILE=cmake/i686-mingw-w64-toolchain.cmake \
      VC_CXX_FLAGS="-w;-fpermissive" \
      cmake --workflow --preset remaster
fi

if [[ ! -f "${LOCAL_OUTPUT}Data/RedAlert.dll" ]]; then
    echo "ERROR: ${LOCAL_OUTPUT}Data/RedAlert.dll not found." >&2
    echo "       Run without --no-build, or re-run cmake manually first." >&2
    exit 1
fi

if [[ -n "$DELETE_FLAG" && "$DRY_RUN" -eq 0 && "$AUTO_YES" -eq 0 ]]; then
    cat <<EOF
==> About to mirror-sync (with --delete) to:
    $DECK_TARGET

    Any files on the Deck under Vanilla_RA/ that are NOT present in
    $LOCAL_OUTPUT will be DELETED. This is intentional — it's how we keep
    Deck and local in sync. Run with --dry-run first to preview.

Continue? [y/N]
EOF
    read -r answer
    if [[ ! "$answer" =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

DRY_FLAG=""
if [[ "$DRY_RUN" -eq 1 ]]; then
    DRY_FLAG="--dry-run"
    echo "==> DRY RUN — no files will be transferred"
fi

# A malformed XML override does not get skipped by the launcher -- it asserts and the
# game dies at startup, so it must never reach a device. Plain resources are copied
# rather than built, which is how a `--` inside an XML comment shipped once already.
echo "==> Validating shipped XML"
python3 scripts/validate_shipped_xml.py "$LOCAL_OUTPUT"

echo "==> rsync -av $DELETE_FLAG $DRY_FLAG $LOCAL_OUTPUT → $DECK_TARGET"
rsync -av $DELETE_FLAG $DRY_FLAG "$LOCAL_OUTPUT" "$DECK_TARGET"

echo "==> Done."
