#!/usr/bin/env python3
"""Paint the encyclopedia's detail box, TF_UI_ENC_STATS.DDS (docs/encyclopedia.md): one green list box like the
CAMPAIGNS page's, TD's list-box rim nine-sliced over its scanlines, covering the page's briefing box and the slot
under it so the picture, description and stats share one box (scripts/bui_encyclopedia_build.py places it).

usage: encyclopedia_art.py <dir with the stock UI_MISSIONSELECT_BG and UI_LOADGAME_BG_SCANLINES .DDS> <SRGB out dir>
License: GPL v3.
"""
import os
import sys

from PIL import Image

from campaigns_backgrounds import (LIST_BOX, LIST_HOLE, UNDERLAY_FILL, nine_slice, read_dds, tile)
from title_logo_build import dds_bytes

SIZE = (949, 708)   # the box's 417x311 screen px in the frame's texture px (2123 / 933 per px)


def plate(frame, scanlines):
    w, h = SIZE
    out = Image.new('RGBA', SIZE, UNDERLAY_FILL)
    out.alpha_composite(tile(scanlines.crop(LIST_HOLE), (w - 8, h - 8)), (4, 4))
    spans = (LIST_BOX[0] + 44, LIST_BOX[2] - 44, LIST_BOX[1] + 44, LIST_BOX[3] - 44)
    out.alpha_composite(nine_slice(frame, LIST_BOX, SIZE, (44, 44, 44), (44, 44, 44, 44), spans))
    return out


def main(src_dir, out_dir):
    _, frame = read_dds(os.path.join(src_dir, 'UI_MISSIONSELECT_BG.DDS'))
    _, scanlines = read_dds(os.path.join(src_dir, 'UI_LOADGAME_BG_SCANLINES.DDS'))
    path = os.path.join(out_dir, 'TF_UI_ENC_STATS.DDS')
    with open(path, 'wb') as f:
        f.write(dds_bytes(plate(frame, scanlines)))
    print('wrote', path)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
