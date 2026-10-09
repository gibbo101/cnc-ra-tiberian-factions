#!/usr/bin/env bash
# Build the mod (mingw cross-compile) and mirror-deploy it to the Steam Deck or the Linux desktop.
#
# Prereqs (one-time):
#   - apt: cmake g++-mingw-w64 mingw-w64-tools ninja-build rsync openssh-client
#   - ssh: passwordless key auth to deck@steamdeck (Tailscale hostname)
#   - C&C Remastered launched at least once on the target (creates the Mods folder)
#
# Behavior:
#   1. cmake --workflow --preset remaster, then a full restage of resources/ and the asset packs
#      into build/remaster/Vanilla_RA/ (a fresh folder, so nothing stale rides along).
#   2. Refuses to deploy when the game is running on the target, when the target path is not a
#      Mods/Red_Alert/Vanilla_RA folder, or when a gitignored locked file (the UI atlas, the
#      intro) is missing or differs from its committed md5.
#   3. Lists what the mirror would delete and asks before going on.
#   4. Desktop only: backs up every file it will replace or delete to
#      ~/Desktop/Tiberian Factions/deploy-backups/desktop-<branch>-<timestamp>/.
#   5. rsync -ac --delete build/remaster/Vanilla_RA/ -> target, then checks by checksum that the
#      target matches the build. -c matters: the RA*_SFX_EVA_* seed WAVs can match the build in
#      size and mtime but not content, and -a alone skips them. The mirror never deletes CustomMaps/,
#      where the launcher keeps the maps it receives in LAN games.
#
# Flags:
#   --desktop        Deploy to this machine's Proton prefix instead of the Deck.
#   --no-build       Skip cmake and the restage; deploy the existing build output as-is.
#   --dry-run        Show what would change and stop.
#   --no-delete      Drop the --delete flag (rare; mirrors-only mode).
#   --yes            Skip the deletion confirmation prompt.
#
# License: GPL v3 (inherited from Vanilla Conquer base).

set -euo pipefail
cd "$(dirname "$0")"

NO_BUILD=0
DRY_RUN=0
DELETE_FLAG="--delete --filter=P_/CustomMaps/"
AUTO_YES=0
DESKTOP=0
for arg in "$@"; do
    case "$arg" in
        --desktop)  DESKTOP=1 ;;
        --no-build) NO_BUILD=1 ;;
        --dry-run)  DRY_RUN=1 ;;
        --no-delete) DELETE_FLAG="" ;;
        --yes|-y)   AUTO_YES=1 ;;
        *) echo "Unknown flag: $arg" >&2; exit 2 ;;
    esac
done

MODS_SUFFIX="steamapps/compatdata/1213210/pfx/drive_c/users/steamuser/Documents/CnCRemastered/Mods/Red_Alert/Vanilla_RA/"
LOCAL_OUTPUT="build/remaster/Vanilla_RA/"
if [[ "$DESKTOP" -eq 1 ]]; then
    TARGET_DIR="$HOME/.steam/steam/$MODS_SUFFIX"
    TARGET="$TARGET_DIR"
    SURFACE="desktop"
else
    DECK_HOST="${DECK_HOST:-deck@steamdeck}"
    TARGET_DIR="/home/deck/.steam/steam/$MODS_SUFFIX"
    TARGET="$DECK_HOST:$TARGET_DIR"
    SURFACE="$DECK_HOST"
fi

# An empty or wrong target turns the --delete mirror into a wipe of whatever it points at.
case "${TARGET_DIR:?}" in
    /*/Mods/Red_Alert/Vanilla_RA/) ;;
    *) echo "ERROR: refusing to deploy to '$TARGET_DIR': not a Mods/Red_Alert/Vanilla_RA folder." >&2; exit 1 ;;
esac

on_target() {
    if [[ "$DESKTOP" -eq 1 ]]; then "$@"; else ssh -n "$DECK_HOST" "$@"; fi
}

if [[ "$NO_BUILD" -eq 0 ]]; then
    echo "==> Building Vanilla_RA target (mingw cross-compile, remaster preset)"
    CMAKE_TOOLCHAIN_FILE=cmake/i686-mingw-w64-toolchain.cmake \
      VC_CXX_FLAGS="-w;-fpermissive" \
      cmake --workflow --preset remaster
    # The CMake copy only runs when the DLL relinks and never deletes, so restage from scratch.
    echo "==> Restaging $LOCAL_OUTPUT"
    rm -rf "${LOCAL_OUTPUT:?}"
    python3 scripts/stage_asset_packs.py "$LOCAL_OUTPUT" --full
    cp build/remaster/RelWithDebInfo/RedAlert.dll "${LOCAL_OUTPUT}Data/"
fi

if [[ ! -f "${LOCAL_OUTPUT}Data/RedAlert.dll" ]]; then
    echo "ERROR: ${LOCAL_OUTPUT}Data/RedAlert.dll not found." >&2
    echo "       Run without --no-build, or re-run cmake manually first." >&2
    exit 1
fi

# Gitignored files that differ per checkout; a worktree without main's copies would strip them.
check_locked() {
    local file="$1" want="$2" have
    if [[ ! -f "$file" ]]; then
        echo "ERROR: $file is missing (gitignored: copy main's into this checkout)." >&2
        exit 1
    fi
    have=$(md5sum "$file" | cut -d' ' -f1)
    if [[ "$have" != "$want" ]]; then
        echo "ERROR: $file is $have, the committed lock says $want (copy main's or rebuild it)." >&2
        exit 1
    fi
}
echo "==> Checking locked gitignored files"
check_locked "${LOCAL_OUTPUT}Data/ART/TEXTURES/SRGB/MT_COMMANDBAR_COMMON.TGA" \
    "$(awk '$2 == "MT_COMMANDBAR_COMMON.TGA" {print $1}' scripts/campaigns_work/textures.md5)"
check_locked "${LOCAL_OUTPUT}Data/ART/MOVIES/RA/REDINTRO.BK2" "$(cat scripts/intro_work/REDINTRO.md5)"

# A malformed XML override does not get skipped by the launcher -- it asserts and the
# game dies at startup, so it must never reach a device. Plain resources are copied
# rather than built, which is how a `--` inside an XML comment shipped once already.
echo "==> Validating shipped XML"
python3 scripts/validate_shipped_xml.py "$LOCAL_OUTPUT"

if on_target pgrep -x ClientG.exe >/dev/null; then
    echo "ERROR: the game is running on $SURFACE; close it before deploying." >&2
    exit 1
fi

echo "==> Comparing $LOCAL_OUTPUT with $TARGET"
CHANGES=$(rsync -acn $DELETE_FLAG --itemize-changes "$LOCAL_OUTPUT" "$TARGET" | grep -v '^\.d' || true)
DELETIONS=$(grep '^\*deleting' <<<"$CHANGES" | cut -c13- || true)
REPLACED=$(grep -E '^[<>]f[^+]' <<<"$CHANGES" | cut -c13- || true)
echo "    $(grep -cE '^[<>]f\+' <<<"$CHANGES" || true) new, $(grep -cE '^[<>]f[^+]' <<<"$CHANGES" || true) replaced, $(grep -c '^\*deleting' <<<"$CHANGES" || true) deleted"
if [[ -n "$DELETIONS" ]]; then
    echo "==> These files on $SURFACE are not in the build and will be DELETED:"
    sed 's/^/    /' <<<"$DELETIONS"
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "==> DRY RUN: nothing transferred"
    grep -v '^\.f\.\.t' <<<"$CHANGES" | sed 's/^/    /' || true
    exit 0
fi

if [[ -n "$DELETIONS" && "$AUTO_YES" -eq 0 ]]; then
    echo "Continue? [y/N]"
    read -r answer
    if [[ ! "$answer" =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

if [[ "$DESKTOP" -eq 1 && -n "$DELETIONS$REPLACED" ]]; then
    BACKUP="$HOME/Desktop/Tiberian Factions/deploy-backups/desktop-$(git rev-parse --abbrev-ref HEAD | tr / -)-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP"
    printf '%s\n%s\n' "$DELETIONS" "$REPLACED" | grep -v '/$' | grep . | while read -r f; do
        (cd "$TARGET_DIR" && cp -p --parents "$f" "$BACKUP/")
    done
    echo "==> Backed up replaced and deleted files to $BACKUP"
fi

echo "==> rsync -ac $DELETE_FLAG $LOCAL_OUTPUT -> $TARGET"
rsync -ac $DELETE_FLAG "$LOCAL_OUTPUT" "$TARGET"

LEFT=$(rsync -acn $DELETE_FLAG --itemize-changes "$LOCAL_OUTPUT" "$TARGET" | grep -vc '^\.d' || true)
if [[ "$LEFT" -ne 0 ]]; then
    echo "ERROR: $LEFT files still differ from the build on $SURFACE." >&2
    exit 1
fi
echo "==> Done: $SURFACE matches the build by checksum (DLL $(md5sum "${LOCAL_OUTPUT}Data/RedAlert.dll" | cut -c1-8))."
