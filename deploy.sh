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
#      into build/remaster/Vanilla_RA/ and the folder of each asset-pack mod it uses beside it
#      (scripts/asset_packs.py USED), fresh folders so nothing stale rides along.
#   2. Refuses to deploy when the game is running on the target, when a target path is not its
#      Mods/Red_Alert/<folder>, or when a gitignored locked file (the UI atlas, the CAMPAIGNS page
#      textures, the intro) is missing or differs from its committed md5.
#   3. Lists what the mirror would delete and asks before going on.
#   4. Desktop only: backs up every file it will replace or delete to
#      ~/Desktop/Tiberian Factions/deploy-backups/desktop-<branch>-<timestamp>/, and after a
#      deploy that checks out keeps only the newest 3 of those folders.
#   5. rsync -ac --delete each folder to Mods/Red_Alert/<folder>/ on the target, then checks by
#      checksum that it matches the build. -c matters: the RA*_SFX_EVA_* seed WAVs can match the build in
#      size and mtime but not content, and -a alone skips them. The mirror never deletes CustomMaps/,
#      where the launcher keeps the maps it receives in LAN games.
#
# Flags:
#   --desktop        Deploy to this machine's Proton prefix instead of the Deck.
#   --no-build       Skip cmake and the restage; deploy the existing build output as-is.
#   --dry-run        Show what would change and stop.
#   --no-delete      Drop the --delete flag (rare; mirrors-only mode).
#   --mod-only       Deploy Tiberian Factions alone and leave the asset-pack folders as they are (testing
#                    a pack subscribed from the Workshop, with no local copy in Mods).
#   --yes            Skip the deletion confirmation prompt.
#
# License: GPL v3 (inherited from Vanilla Conquer base).

set -euo pipefail
cd "$(dirname "$0")"

NO_BUILD=0
DRY_RUN=0
MOD_ONLY=0
DELETE_FLAG="--delete --filter=P_/CustomMaps/"
AUTO_YES=0
DESKTOP=0
KEEP_BACKUPS=3
BACKUP_ROOT="$HOME/Desktop/Tiberian Factions/deploy-backups"
BACKUP_MARKER=".deploy-sh-backup"
for arg in "$@"; do
    case "$arg" in
        --desktop)  DESKTOP=1 ;;
        --no-build) NO_BUILD=1 ;;
        --dry-run)  DRY_RUN=1 ;;
        --no-delete) DELETE_FLAG="" ;;
        --mod-only) MOD_ONLY=1 ;;
        --yes|-y)   AUTO_YES=1 ;;
        *) echo "Unknown flag: $arg" >&2; exit 2 ;;
    esac
done

MODS_SUFFIX="steamapps/compatdata/1213210/pfx/drive_c/users/steamuser/Documents/CnCRemastered/Mods/Red_Alert/"
LOCAL_ROOT="build/remaster/"
LOCAL_OUTPUT="${LOCAL_ROOT}Vanilla_RA/"
USED_LIST="$(python3 scripts/asset_packs.py used)"
mapfile -t USED_MODS <<< "$USED_LIST"
if [[ "$DESKTOP" -eq 1 ]]; then
    TARGET_ROOT="$HOME/.steam/steam/$MODS_SUFFIX"
    TARGET_HOST=""
    SURFACE="desktop"
else
    DECK_HOST="${DECK_HOST:-deck@steamdeck}"
    TARGET_ROOT="/home/deck/.steam/steam/$MODS_SUFFIX"
    TARGET_HOST="$DECK_HOST:"
    SURFACE="$DECK_HOST"
fi

on_target() {
    if [[ "$DESKTOP" -eq 1 ]]; then "$@"; else ssh -n "$DECK_HOST" "$@"; fi
}

if [[ "$NO_BUILD" -eq 0 ]]; then
    echo "==> Building Vanilla_RA target (mingw cross-compile, remaster preset)"
    CMAKE_TOOLCHAIN_FILE=cmake/i686-mingw-w64-toolchain.cmake \
      VC_CXX_FLAGS="-w;-fpermissive" \
      cmake --workflow --preset remaster
    # The CMake copy only runs when the DLL relinks and never deletes, so restage from scratch.
    echo "==> Restaging $LOCAL_OUTPUT and ${USED_MODS[*]}"
    scripts/clear_dir.sh "${LOCAL_OUTPUT:?}"
    for mod in "${USED_MODS[@]}"; do
        scripts/clear_dir.sh "${LOCAL_ROOT:?}${mod:?}/"
    done
    python3 scripts/stage_asset_packs.py "$LOCAL_OUTPUT" --full --strict
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
while read -r want name; do
    check_locked "${LOCAL_OUTPUT}Data/ART/TEXTURES/SRGB/$name" "$want"
done < scripts/campaigns_work/textures.md5
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

# The mod folders this deploy mirrors: Tiberian Factions, then each asset-pack mod it uses.
FOLDERS=(Vanilla_RA "${USED_MODS[@]}")
if [[ "$MOD_ONLY" -eq 1 ]]; then
    FOLDERS=(Vanilla_RA)
fi
for folder in "${FOLDERS[@]}"; do
    if [[ ! -d "$LOCAL_ROOT$folder" ]]; then
        echo "ERROR: $LOCAL_ROOT$folder is missing; build first (drop --no-build)." >&2
        exit 1
    fi
done
BACKUP=""

# Lists one folder's changes into CHANGES, DELETIONS and REPLACED.
compare() {
    local local_dir="$1" target="$2"
    CHANGES=$(rsync -acn $DELETE_FLAG --itemize-changes "$local_dir" "$target" | grep -v '^\.d' || true)
    DELETIONS=$(grep '^\*deleting' <<<"$CHANGES" | cut -c13- || true)
    REPLACED=$(grep -E '^[<>]f[^+]' <<<"$CHANGES" | cut -c13- || true)
}

ALL_DELETIONS=""
for folder in "${FOLDERS[@]}"; do
    target_dir="$TARGET_ROOT$folder/"
    # An empty or wrong target turns the --delete mirror into a wipe of whatever it points at.
    case "${target_dir:?}" in
        /*/Mods/Red_Alert/"$folder"/) ;;
        *) echo "ERROR: refusing to deploy to '$target_dir': not a Mods/Red_Alert/$folder folder." >&2; exit 1 ;;
    esac
    echo "==> Comparing $LOCAL_ROOT$folder/ with $TARGET_HOST$target_dir"
    compare "$LOCAL_ROOT$folder/" "$TARGET_HOST$target_dir"
    echo "    $(grep -cE '^[<>]f\+' <<<"$CHANGES" || true) new, $(grep -cE '^[<>]f[^+]' <<<"$CHANGES" || true) replaced, $(grep -c '^\*deleting' <<<"$CHANGES" || true) deleted"
    if [[ -n "$DELETIONS" ]]; then
        echo "==> These files in $folder on $SURFACE are not in the build and will be DELETED:"
        sed 's/^/    /' <<<"$DELETIONS"
        ALL_DELETIONS+="$DELETIONS"
    fi
    if [[ "$DRY_RUN" -eq 1 ]]; then
        grep -v '^\.f\.\.t' <<<"$CHANGES" | sed 's/^/    /' || true
    fi
done

if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "==> DRY RUN: nothing transferred"
    exit 0
fi

if [[ -n "$ALL_DELETIONS" && "$AUTO_YES" -eq 0 ]]; then
    echo "Continue? [y/N]"
    read -r answer
    if [[ ! "$answer" =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

for folder in "${FOLDERS[@]}"; do
    target_dir="$TARGET_ROOT$folder/"
    compare "$LOCAL_ROOT$folder/" "$TARGET_HOST$target_dir"
    if [[ "$DESKTOP" -eq 1 && -n "$DELETIONS$REPLACED" ]]; then
        if [[ -z "$BACKUP" ]]; then
            BACKUP="$BACKUP_ROOT/desktop-$(git rev-parse --abbrev-ref HEAD | tr / -)-$(date +%Y%m%d-%H%M%S)"
            mkdir -p "$BACKUP"
            touch "$BACKUP/$BACKUP_MARKER"
        fi
        mkdir -p "$BACKUP/$folder"
        printf '%s\n%s\n' "$DELETIONS" "$REPLACED" | grep -v '/$' | grep . | while read -r f; do
            (cd "$target_dir" && cp -p --parents "$f" "$BACKUP/$folder/")
        done
    fi
    echo "==> rsync -ac $DELETE_FLAG $LOCAL_ROOT$folder/ -> $TARGET_HOST$target_dir"
    rsync -ac $DELETE_FLAG "$LOCAL_ROOT$folder/" "$TARGET_HOST$target_dir"
    LEFT=$(rsync -acn $DELETE_FLAG --itemize-changes "$LOCAL_ROOT$folder/" "$TARGET_HOST$target_dir" | grep -vc '^\.d' || true)
    if [[ "$LEFT" -ne 0 ]]; then
        echo "ERROR: $LEFT files in $folder still differ from the build on $SURFACE." >&2
        exit 1
    fi
done
[[ -n "$BACKUP" ]] && echo "==> Backed up replaced and deleted files to $BACKUP"

if [[ "$DESKTOP" -eq 1 && -d "$BACKUP_ROOT" ]]; then
    # Only folders carrying this script's marker; hand-made backups are never touched.
    find "$BACKUP_ROOT" -mindepth 2 -maxdepth 2 -type f -name "$BACKUP_MARKER" -printf '%h\n' \
        | xargs -r -d '\n' -n1 basename \
        | awk '{print substr($0, length($0) - 14) " " $0}' | sort -r | tail -n +$((KEEP_BACKUPS + 1)) \
        | cut -d' ' -f2 | while read -r old; do
            scripts/clear_dir.sh "${BACKUP_ROOT:?}/$old"
            echo "==> Pruned old backup $old"
        done
fi
echo "==> Done: $SURFACE matches the build by checksum (DLL $(md5sum "${LOCAL_OUTPUT}Data/RedAlert.dll" | cut -c1-8); ${FOLDERS[*]})."
