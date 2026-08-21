#!/usr/bin/env python3
"""Split TSHVR's baked drop shadow into its own shape block.

PARKED 2026-08-21, NOT PART OF THE BUILD. Once the ground units came down to
EA's 6px throw, the Hover MLRS's longer 17px shadow read as its own thing and
Luke's verdict on the bob as it stands was "looks ok", so the still-shadow
experiment was never needed. Running this changes TSHVR from 64 to 96 frames
and REQUIRES the matching draw-order change in UnitClass::Draw_It plus a 96
frame classic stub in build_tfassets.sh -- the art alone would render the hull
with no shadow at all. Left here complete because the analysis is done.

WHY
---
The Hover MLRS bobs: UnitClass::Draw_It nudges y by a few pixels per rendered
frame so the hull rides up and down. With the shadow baked into the hull frames
the shadow rode with it, so the whole unit translated and nothing read as hover.
A shadow that stays put while the hull rises off it is the effect.

The launcher makes the FIRST Techno_Draw_Object of an object the base draw and
sorts every later draw above it (dllinterface.cpp, SortOrder = base + n). So the
shadow is drawn first, at the un-bobbed y, and the hull and rack follow at the
bobbed y. That ordering is the whole mechanism -- a shadow drawn after the hull
would sort on top of it.

FRAME LAYOUT (96 shapes, was 64)
    0-31   hull, shadow stripped out
    32-63  rack, untouched
    64-95  shadow silhouettes, one per hull facing

Sub-object draws silently drop shape indexes >= 128 (launcher-render-contracts
#2), which the hull and rack now are -- both sit well under at 0-63. The shadow
block is the BASE draw, and base draws are not capped.

The classic stub SHP must carry 96 frames to match (build_tfassets.sh).

Usage:  ts_hover_split_shadow.py [--dry-run]
"""
import io, json, os, sys, zipfile
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ts_reshadow import (UNITS_DIR, EA_ALPHA, OFFSET_OVERRIDE, uncrop,
                         find_shadow_alpha, strip_shadow, write_zip, tga_bytes)

UNIT = "TSHVR"
HULL_FRAMES = 32


def silhouette(frame, dx, dy, alpha):
    """The shadow alone, on the frame's own canvas, at the resting offset."""
    out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    mask = frame.split()[3].point(lambda a: alpha if a > 0 else 0)
    black = Image.new("RGBA", frame.size, (0, 0, 0, 255))
    out.paste(black, (dx, dy), mask)
    return out


def main():
    dry = "--dry-run" in sys.argv
    path = f"{UNITS_DIR}/{UNIT}.ZIP"
    src = zipfile.ZipFile(path)
    names = sorted(n[:-4] for n in src.namelist() if n.endswith(".tga"))
    stem = names[0].rsplit("-", 1)[0]
    full = []
    for n in names:
        meta = json.loads(src.read(n + ".meta"))
        full.append(uncrop(Image.open(io.BytesIO(src.read(n + ".tga"))).convert("RGBA"), meta))
    src.close()

    if len(full) != 64:
        print(f"{UNIT}: expected 64 frames, found {len(full)} -- already split? aborting")
        return 1

    sa = find_shadow_alpha(full)
    if sa is None:
        print(f"{UNIT}: no baked shadow found, nothing to split")
        return 1
    dx, dy = OFFSET_OVERRIDE[UNIT]

    hulls, stripped_px = [], 0
    for im in full[:HULL_FRAMES]:
        h, n = strip_shadow(im, sa)
        hulls.append(h)
        stripped_px += n
    racks = full[HULL_FRAMES:]
    shadows = [silhouette(h, dx, dy, EA_ALPHA) for h in hulls]

    out = hulls + racks + shadows
    print(f"{UNIT}: {len(full)} -> {len(out)} frames  "
          f"[hull 0-{HULL_FRAMES-1} shadow stripped ({stripped_px} px), "
          f"rack {HULL_FRAMES}-{len(full)-1} untouched, "
          f"shadow {len(full)}-{len(out)-1} at offset ({dx},{dy}) alpha {EA_ALPHA}]")
    canvas = full[0].width
    over = [i for i, im in enumerate(shadows) if (im.getbbox() or (0,0,0,0))[3] > canvas]
    if over:
        print(f"  ⚠ {len(over)} shadow frames exceed the {canvas}px canvas: {over[:5]}")

    if not dry:
        write_zip(path, stem, out)
        print(f"  wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
