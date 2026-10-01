#!/bin/bash
# Run a RAD Video Tools command-line tool (binkc, binkmix, binkconv, ...) from
# the private Wine prefix ~/.local/opt/wine-fmv, unattended.
#
#   radvideo.sh binkc  <input> <output.bik> [switches...]
#   radvideo.sh binkmix <input.bik> <sound.wav> <output.bik> [switches...]
#   radvideo.sh binkconv <input> <output> [switches...]
#
# Paths may be Linux paths; they are converted to Wine (Z:) paths. An image
# sequence uses RAD's pattern syntax, e.g.  /path/frame_?????.png*0-899
# (the *first-last suffix is kept as is).
#
# The RAD tools are GUI programs: they need an X display and finish with a
# "Done!" dialog that waits for a click. This script starts its own Xvfb on
# display :77 (override with RADVIDEO_DISPLAY), waits for a window whose
# title contains "Done", presses Enter on it, and returns the tool's exit
# status. Other window titles are echoed to stderr; if the tool is still
# running after RADVIDEO_TIMEOUT seconds (default 7200) the display is
# screenshotted to /tmp/radvideo_timeout.png and the tool is killed.
set -u
PREFIX="$HOME/.local/opt/wine-fmv"
RADEXE='C:\RADVideo\radvideo64.exe'
DISP="${RADVIDEO_DISPLAY:-:77}"
XVFB="$HOME/.local/opt/xvfb/usr/bin/Xvfb"
TIMEOUT="${RADVIDEO_TIMEOUT:-7200}"

case "$DISP" in :1|:2) echo "refusing to use display $DISP" >&2; exit 2;; esac

if ! [ -e "/tmp/.X11-unix/X${DISP#:}" ]; then
    nohup "$XVFB" "$DISP" -screen 0 1920x1080x24 -nolisten tcp -noreset >/dev/null 2>&1 &
    for _ in $(seq 50); do [ -e "/tmp/.X11-unix/X${DISP#:}" ] && break; sleep 0.1; done
fi

export WINEPREFIX="$PREFIX" WINEDEBUG=-all DISPLAY="$DISP"
unset WAYLAND_DISPLAY

tool="$1"; shift
args=()
for a in "$@"; do
    # An absolute Linux path (its parent directory exists and is not /) is
    # converted; RAD switches such as /O or /V100 are passed through.
    if [[ "$a" == /* ]]; then
        pat=""; p="$a"
        if [[ "$p" == *'*'* ]]; then pat="*${p#*\*}"; p="${p%%\**}"; fi
        parent="$(dirname -- "$p")"
        if [[ "$parent" != "/" && -d "$parent" ]]; then
            a="Z:${p//\//\\}$pat"
        fi
    fi
    args+=("$a")
done

wine "$RADEXE" "$tool" "${args[@]}" &
wpid=$!
start=$(date +%s)
status=0
lastnames=""
while kill -0 "$wpid" 2>/dev/null; do
    names=""
    for w in $(xdotool search --name "." 2>/dev/null); do
        name="$(xdotool getwindowname "$w" 2>/dev/null)"
        [[ -z "$name" || "$name" == "Default IME" ]] && continue
        names+="$name|"
        if [[ "$name" == *Done* ]]; then
            xdotool key --window "$w" Return 2>/dev/null
        fi
    done
    # Report any window that is not a progress title (NN% - ...) so error
    # dialogs show up on stderr; a hung dialog ends in the timeout below.
    if [[ "$names" != "$lastnames" ]]; then
        IFS='|' read -ra arr <<< "$names"
        for n in "${arr[@]}"; do
            [[ "$n" == *%* || "$n" == *Done* ]] || echo "radvideo: window '$n'" >&2
        done
        lastnames="$names"
    fi
    if (( $(date +%s) - start > TIMEOUT )); then
        DISPLAY="$DISP" scrot -o /tmp/radvideo_timeout.png 2>/dev/null
        echo "radvideo: timed out after ${TIMEOUT}s (screenshot /tmp/radvideo_timeout.png)" >&2
        kill "$wpid"; status=1; break
    fi
    sleep 1
done
wait "$wpid" 2>/dev/null
rc=$?
(( status == 0 )) && status=$rc
exit $status
