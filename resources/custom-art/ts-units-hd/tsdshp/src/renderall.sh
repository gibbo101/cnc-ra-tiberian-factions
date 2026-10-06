#!/bin/sh
# renders the package's frames: frames/ 0-3 and facings/ 0-31 (facing 8 is frame 0), at full supersampling, the
# facings in two halves side by side (two processes)
#     sh renderall.sh [PKG]        (default pkg_v3/ts-dshp-hd)
cd "$(dirname "$0")"
P=${1:-pkg_v3/ts-dshp-hd}
mkdir -p $P/frames $P/facings
A=""; B=""
for k in $(seq 0 15); do [ $k -ne 8 ] && A="$A,$k"; done
for k in $(seq 16 31); do B="$B,$k"; done
( timeout 1200 python3 dshprender.py frames 0,1,2,3 4 $P/frames 1 && \
  timeout 5400 python3 dshprender.py facings ${A#,} 4 $P/facings 1 ) &
PA=$!
timeout 5400 python3 dshprender.py facings ${B#,} 4 $P/facings 1 &
PB=$!
wait $PA; wait $PB
cp $P/frames/tsdshp-0000.png $P/facings/tsdshp-0008.png
cp $P/frames/tsdshp-0000-trim.png $P/facings/tsdshp-0008-trim.png
echo ALL DONE
