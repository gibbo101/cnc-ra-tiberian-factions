#!/usr/bin/env python3
"""Paint the CAMPAIGNS page's own row art as loose textures (docs/campaigns-page.md): TD's plain
row with a mod faction's crest, for the crest groups campaigns_rows.py adds.

usage: campaigns_row_art.py <MT_COMMANDBAR_COMMON.TGA> <MT_COMMANDBAR_COMMON.MTD> <stock RA_UI_MISSIONSELECT_BG.DDS (header)> <out dir>
"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from campaigns_atlas import Atlas, crest_row  # noqa: E402
from campaigns_backgrounds import read_dds, write_dds  # noqa: E402

# (texture base name, crest); GUITEXTURESETS names them as <base>_Off.tga and <base>_Selected.tga.
ROWS = [('TF_UI_MISSIONSELECT_ITEMLIST_TSGDI', 'tsgdi.png')]
SIZE_FROM = 'UI_MISSIONSELECT_ITEMLIST_GDI_OFF'
STATES = (('OFF', 'UI_MISSIONSELECT_ITEMLIST_OFF'), ('SELECTED', 'UI_MISSIONSELECT_ITEMLIST_SELECTED'))


def main(atlas_path, mtd, header_dds, out_dir):
    atlas = Atlas(atlas_path, mtd)
    header, _ = read_dds(header_dds)
    size = tuple(atlas.region(SIZE_FROM)[2:])
    os.makedirs(out_dir, exist_ok=True)
    for name, emblem in ROWS:
        for state, source in STATES:
            row = atlas.crop(atlas.region(source)).resize(size, Image.LANCZOS)
            write_dds(os.path.join(out_dir, '%s_%s.DDS' % (name, state)), header, crest_row(row, emblem))
        print('row art', name, '<-', emblem)


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
