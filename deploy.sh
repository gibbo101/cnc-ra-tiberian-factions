#!/usr/bin/env bash
# Build the mod (mingw cross-compile) and deploy to the Steam Deck via Tailscale.
#
# Prereqs (one-time):
#   - apt: cmake g++-mingw-w64 mingw-w64-tools ninja-build
#   - ssh: passwordless key auth to deck@steamdeck (Tailscale hostname)
#   - C&C Remastered launched at least once on the Deck (creates the Mods folder)
#
# Usage:
#   ./deploy.sh
#
# After this completes, launch C&C on the Deck, pick Red Alert, enable
# "Tiberian Factions for Red Alert" in the mod list, start a skirmish.

set -euo pipefail

cd "$(dirname "$0")"

DECK_HOST="${DECK_HOST:-deck@steamdeck}"
DECK_MODS_DIR="/home/deck/.steam/steam/steamapps/compatdata/1213210/pfx/drive_c/users/steamuser/Documents/CnCRemastered/Mods/Red_Alert"

echo "==> Building Vanilla_RA target (mingw cross-compile, remaster preset)"
CMAKE_TOOLCHAIN_FILE=cmake/i686-mingw-w64-toolchain.cmake \
  VC_CXX_FLAGS="-w;-fpermissive" \
  cmake --workflow --preset remaster

OUTPUT="build/remaster/Vanilla_RA"
if [[ ! -f "$OUTPUT/Data/RedAlert.dll" ]]; then
  echo "ERROR: expected $OUTPUT/Data/RedAlert.dll not found after build" >&2
  exit 1
fi

echo "==> Deploying $OUTPUT to $DECK_HOST:$DECK_MODS_DIR/"
scp -r "$OUTPUT" "$DECK_HOST:$DECK_MODS_DIR/"

echo "==> Done. Launch C&C Remastered on the Deck and check the mod list."
