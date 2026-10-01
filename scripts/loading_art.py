#!/usr/bin/env python3
"""Draw the loading screen's faction emblem row and its glint, as loose texture overrides.

The loading screen's spinner (LoadingTwiddle_Quad) is played by the launcher as a fixed 4x4 grid
of frames at 24 fps from ANIM_LOADTWIDDLE_RA.DDS. Every cell here holds the same row of the six
faction emblems, as they end the startup intro, so the spinner stands still as the row;
bui_loadingscreen_build.py widens its quad to the row's shape (CELL's aspect) and gives it the
Logo_Sheen effect. That effect scrolls UI_LOGOEFFECT_00.DDS across the screen (no stock screen uses
either): the quad shows only as far as the texture's alpha allows and the texture's colour is added
on top. The texture is drawn opaque, black but for one soft white band along u - v, so the row stays
whole and a diagonal glint keeps sweeping across it, left to right, every 3.3 s.

usage: loading_art.py <SRGB dir>
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import logo_art  # noqa: E402
import title_logo_build  # noqa: E402

EMBLEMS = ('allied.png', 'soviet.png', 'gdi.png', 'nod.png', 'tsgdi.png', 'tsnod.png')
GRID = 4
CELL = (968, 176)                 # 5.5:1, the widened quad's shape
EMBLEM_H, STEP = 115, 153         # emblem size and spacing within a cell
GLINT_SIZE, GLINT_WIDTH = 256, 0.016
GLINT_PEAK = 150


def emblem(name):
    e = logo_art.load(name, EMBLEM_H)
    if name == 'tsgdi.png':
        e = logo_art.tame(e, 0.80, 0.90)
    if name == 'tsnod.png':
        e = logo_art.blackout(e)
    return e


def emblem_row():
    row = Image.new('RGBA', CELL, (0, 0, 0, 0))
    for i, name in enumerate(EMBLEMS):
        e = emblem(name)
        cx = CELL[0] / 2 + (i - (len(EMBLEMS) - 1) / 2) * STEP
        row.alpha_composite(e, (round(cx - e.width / 2), round(CELL[1] / 2 - e.height / 2)))
    return row


def spinner_sheet():
    row = emblem_row()
    sheet = Image.new('RGBA', (CELL[0] * GRID, CELL[1] * GRID), (0, 0, 0, 0))
    for i in range(GRID * GRID):
        sheet.alpha_composite(row, ((i % GRID) * CELL[0], (i // GRID) * CELL[1]))
    return title_logo_build.bleed(sheet)


def glint():
    yy, xx = np.mgrid[0:GLINT_SIZE, 0:GLINT_SIZE]
    phase = ((xx - yy) / GLINT_SIZE) % 1.0
    band = np.exp(-((phase - 0.5) / GLINT_WIDTH) ** 2)
    px = np.zeros((GLINT_SIZE, GLINT_SIZE, 4))
    px[..., :3] = GLINT_PEAK * band[..., None]
    px[..., 3] = 255
    return Image.fromarray(px.round().astype('uint8'), 'RGBA')


def main(srgb_dir):
    srgb = Path(srgb_dir)
    for name, img in (('ANIM_LOADTWIDDLE_RA.DDS', spinner_sheet()), ('UI_LOGOEFFECT_00.DDS', glint())):
        (srgb / name).write_bytes(title_logo_build.dds_bytes(img))
        print(title_logo_build.md5(srgb / name), name)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1])
