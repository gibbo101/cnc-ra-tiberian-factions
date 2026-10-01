#!/usr/bin/env python3
"""Paint the lobby's player slots, map rows and green menu buttons in steel, on the green fill.

The RA front end uses Tiberian Dawn's lobby screens (factions_build.py). Their slot pieces, map
rows and menu buttons (the Custom map list, the Workshop browser) are green outlines over a
translucent green fill, so the green background shows through them and white text reads poorly.
Each is repainted, in the mod's UI atlas, as a steel plate in the stock piece's own shape: at rest
a light steel edge, and in the hover and pressed states (and the selected map) TD's green outline
is kept, so those states still stand out. The slots and rows are drawn only by the lobby and the
multiplayer menus; the menu button also by TD's own score, options and sync screens, which the RA
front end does not open. The flat green buttons are shared with the in-game chat, so
bui_lobby_build.py points the lobby's at the menu's steel set instead of repainting them.

usage: lobby_art.py <SRGB dir>
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import menu_art  # noqa: E402
import title_logo_build  # noqa: E402

# (rest state, [(state, fill)]) per piece: 'lit' for hover and pressed, 'dark' for a selected
# list row, which must keep green text readable. Every state keeps its green outline; all states
# of a piece share the rest state's shape and region size.
PIECES = {
    'name': ((1, 2837, 444, 87), [((3176, 2832, 444, 87), 'lit'), ((5249, 2790, 444, 87), 'lit')]),
    'faction': ((3027, 3712, 141, 87), [((3027, 3801, 141, 87), 'lit'), ((3027, 3623, 141, 87), 'lit')]),
    'team': ((3568, 510, 208, 87), [((3568, 688, 208, 87), 'lit'), ((3568, 599, 208, 87), 'lit')]),
    'ready': ((292, 6388, 77, 87), []),
    'map row': ((5727, 34, 937, 58), [((2684, 56, 937, 58), 'dark'), ((4788, 34, 937, 58), 'lit')]),
    'menu button left': ((532, 6319, 12, 54), [((270, 6482, 12, 54), 'lit'), ((149, 6290, 12, 54), 'dark')]),
    'menu button mid': ((3458, 6265, 30, 54), [((3490, 6265, 30, 54), 'lit'), ((3426, 6265, 30, 54), 'dark')]),
    'menu button right': ((6, 6316, 12, 54), [((100, 6400, 12, 54), 'lit'), ((202, 6287, 12, 54), 'dark')]),
}
FILL = np.array([80, 83, 88])           # steel plate, at rest (shows as the menu buttons' 118-125)
FILL_LIT = np.array([90, 93, 99])       # hover and pressed
FILL_DARK = np.array([24, 26, 29])      # a selected list row
FILLS = {'rest': FILL, 'lit': FILL_LIT, 'dark': FILL_DARK}
EDGE = np.array([150, 155, 162])        # light steel edge, at rest
FILL_ALPHA = 235


def plate(stock, shape_rect, rect, state):
    """A steel plate in the shape of the rest state, with this state's outline on top; outside
    that shape the state's own glow is left as it is. The rest state's opaque outline and
    translucent fill tell edge from plate."""
    shape = np.asarray(menu_art.atlas_region(stock, shape_rect)).astype(float)
    art = np.asarray(menu_art.atlas_region(stock, rect)).astype(float)
    sa = shape[..., 3]
    inside = sa > 0
    fill_a = np.median(sa[inside & (sa < 200)]) if (inside & (sa < 200)).any() else 0
    edge = np.clip((sa - fill_a) / max(1.0, 255 - fill_a), 0, 1)[..., None]
    a = art[..., 3]
    fill = FILLS[state]
    rgb = fill * (1 - edge) + (EDGE if state == 'rest' else art[..., :3]) * edge
    alpha = FILL_ALPHA * (1 - edge[..., 0]) + 255 * edge[..., 0]
    out = art.copy()
    out[inside, :3] = rgb[inside]
    out[inside, 3] = np.maximum(alpha, a)[inside]
    return Image.fromarray(out.round().astype('uint8'), 'RGBA')


def main(srgb_dir):
    atlas = Path(srgb_dir) / title_logo_build.ATLAS
    stock = menu_art.stock_bytes(title_logo_build.ATLAS)
    for rest, states in PIECES.values():
        title_logo_build.paint_atlas(atlas, plate(stock, rest, rest, 'rest'), rest)
        for rect, state in states:
            title_logo_build.paint_atlas(atlas, plate(stock, rest, rect, state), rect)
    print(title_logo_build.md5(atlas), title_logo_build.ATLAS)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1])
