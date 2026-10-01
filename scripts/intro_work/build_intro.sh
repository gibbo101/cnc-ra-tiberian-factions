#!/usr/bin/env bash
# Build the startup intro (REDINTRO.BK2) from shots.tsv and install it in the mod's resources.
#
# The launcher plays Data/ART/MOVIES/RA/REDINTRO.BK2 as Red Alert's startup movie; a mod copy
# replaces the stock one. It must be Bink 1 or Bink 2 (the player reads the header). The file
# is ~136 MB, over GitHub's 100 MB limit, so it is gitignored: build it here, and
# package-for-workshop.sh refuses to package unless it matches REDINTRO.md5.
#
# Needs the FMV library at $TF_FMV_LIB (default ~/Desktop/Tiberian Factions/tf-intro-lib) with its decoder and
# RAD Video Tools set up (README.md).
#
# usage: scripts/intro_work/build_intro.sh [shots.tsv]
set -euo pipefail
cd "$(dirname "$0")/../.."
LIB="${TF_FMV_LIB:-$HOME/Desktop/Tiberian Factions/tf-intro-lib}"
SHOTS="${1:-scripts/intro_work/shots.tsv}"
OUT="resources/remaster_mods/Vanilla_RA/Data/ART/MOVIES/RA/REDINTRO.BK2"
WORK="$(mktemp -d "$LIB/edit/build.XXXX")"
trap 'rm -rf "$WORK"' EXIT

python3 scripts/intro_work/intro_cut.py "$SHOTS" frames "$WORK/frames"
last=$(( $(ls "$WORK/frames"/frame_*.jpg | wc -l) - 1 ))
"$LIB/tools/radvideo.sh" binkc "$WORK/frames/frame_?????.jpg*0-$last" "$WORK/video.bik" \
    /V100 /F30 /D1500000 /L-1 /O
"$LIB/tools/radvideo.sh" binkmix "$WORK/video.bik" "$WORK/frames/music.wav" "$WORK/intro.bik" /L4 /O
mkdir -p "$(dirname "$OUT")"
cp "$WORK/intro.bik" "$OUT"
md5sum "$OUT"
echo "Expected for the locked cut: $(cat scripts/intro_work/REDINTRO.md5)"
