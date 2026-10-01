#!/usr/bin/env python3
"""
Rebuild RA_UI_LOADINGSCREEN.BUI in the mod's green: the loading spinner shows the faction emblem
row with a glint, the map-name and player-list frames use Tiberian Dawn's green frames, and the
hint line takes TD's green tint.

The screen holds the spinner twice, in its singleplayer and multiplayer layouts (skirmish uses the
multiplayer one); both get the same treatment.

usage: bui_loadingscreen_build.py <base.BUI> <out.BUI>

Each spinner quad (LoadingTwiddle_Quad) keeps its height and centre and grows WIDEN times wider,
the shape of the emblem row loading_art.py draws into every frame of its texture. Its header
container gains the Logo_Sheen effect leaf, the way the menu box carries its sheen: an id 0x16
leaf [0x17][size][u16 len][name] before the closing id 0x27 leaf. The file keeps its byte size
(bui_tree.py).

The frames and the hint tint are the values TD's own UI_LOADINGSCREEN.BUI gives the same widgets.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bui_tree import headers, leaves, load, string_body, string_value, write_same_size  # noqa: E402

QUAD = b'LoadingTwiddle_Quad'
STOCK_RECTS = [(0.4671, 0.6111, 0.0659, 0.1574), (0.4671, 0.7593, 0.0659, 0.1574)]
WIDEN = 5.5
EFFECT = b'Logo_Sheen'
FRAMES = (b'ra_ui_loadscreenframes', b'ui_loadscreenframes')
HINT = b'Hint_Text'
STOCK_TINT, HINT_TINT = (1.0, 1.0, 1.0, 1.0), (0.502, 1.0, 0.0, 1.0)


def effect_leaf(name):
    return [0x16, bytearray(bytes([0x17, len(name) + 2]) + struct.pack('<H', len(name)) + name)]


def tint(header, stock, new):
    widget = header[1][0][1]
    tag = widget.find(b'\x03\x10')
    got = tuple(round(v, 3) for v in struct.unpack_from('<4f', widget, tag + 2))
    assert got == stock, f'tint is {got}, expected {stock}'
    struct.pack_into('<4f', widget, tag + 2, *new)


def restyle(header, stock_rect):
    children = header[1]
    widget = children[0][1]
    tag = widget.find(b'\x02\x10')
    x, y, w, h = struct.unpack_from('<4f', widget, tag + 2)
    assert tuple(round(v, 4) for v in (x, y, w, h)) == stock_rect, f'spinner rect is {(x, y, w, h)}'
    struct.pack_into('<4f', widget, tag + 2, x - w * (WIDEN - 1) / 2, y, w * WIDEN, h)
    assert not any(c[0] == 0x16 for c in children), 'spinner already has an effect'
    close = next(i for i, c in enumerate(children) if c[0] == 0x27)
    children.insert(close, effect_leaf(EFFECT))


def main(base, out):
    d, roots = load(base)
    spinners = headers(roots, QUAD)
    assert len(spinners) == len(STOCK_RECTS), f'found {len(spinners)} spinners'
    for header, rect in zip(spinners, STOCK_RECTS):
        restyle(header, rect)

    frames = [lf for r in roots for lf in leaves(r) if lf[0] == 2 and string_value(lf[1]) == FRAMES[0]]
    assert len(frames) == 1, f'found {len(frames)} frame textures'
    frames[0][1] = string_body(FRAMES[1])

    hints = headers(roots, HINT)
    assert len(hints) == 2, f'found {len(hints)} hint lines'
    for header in hints:
        tint(header, STOCK_TINT, HINT_TINT)

    pad = write_same_size(d, roots, out)
    print(f'wrote {out}: {len(d)} bytes (pad {pad})')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
