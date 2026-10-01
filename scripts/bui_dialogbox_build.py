#!/usr/bin/env python3
"""
Rebuild RA_DIALOGBOX_SOVIET.BUI, the confirmation box the main menu opens (Exit Game? and the
like), in the menu's look: Tiberian Dawn's green dialog frame, green text and divider, and the
menu's own steel buttons with green labels.

usage: bui_dialogbox_build.py <base.BUI> <out.BUI>

The file is edited as a chunk tree and keeps its byte size (bui_tree.py). The longer button
names don't fit that budget on their own, so the caption's placeholder sentence, which the launcher replaces with the
dialog's question whenever the box opens, is cut to its first clause.
"""
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bui_tree import (HEADER, leaves, parse_all, replace_texture_set, serialise, string_body,  # noqa: E402
                      string_value, write_same_size)

# Widget tints, edited in place before parsing: (offset of the 03 10 tag, stock RGBA, new RGBA).
# The green is Tiberian Dawn's own dialog's.
TINTS = ((2012, (0.804, 0.157, 0.157, 1.0), (0.0, 1.0, 0.0, 1.0)),       # caption text
         (2524, (0.804, 0.157, 0.157, 0.604), (0.0, 1.0, 0.0, 0.604)))   # divider line

FRAME_TEXTURES = [(b'RA_UI_Frame_Tooltip_Sidebar_' + q, b'UI_Frame_Tooltip_Sidebar_' + q)
                  for q in (b'M', b'TL', b'TM', b'TR', b'ML', b'BL', b'MR', b'BM', b'BR')]
PLACEHOLDER = (b'Dialog Box Statement or Choices Text - Needs to support text choices of remapping '
               b'the unit, structure and research build command hotkeys. These can be lengthy '
               b'sentences!')
STRING_LEAVES = FRAME_TEXTURES + [(b'20 Point Outline', b'20 Point Outline Green'),
                                  (PLACEHOLDER, b'Dialog Box Statement or Choices Text')]
TEXTURE_SETS = [(b'RA_Frame_Tooltip_Sidebar', b'Frame_Tooltip_Sidebar'),
                (b'RA_Search_BTN_Red', b'TF_MainMenuSteelButton_Textures')]
# How many times each name appears in the base; a different count means the base changed.
EXPECTED = {b'20 Point Outline': 3, b'RA_Search_BTN_Red': 3}


def main(base, out):
    d = open(base, 'rb').read()
    raw = bytearray(zlib.decompress(d[HEADER:]))
    for off, stock, new in TINTS:
        assert raw[off:off + 2] == b'\x03\x10', f'no tint tag at {off}'
        got = tuple(round(v, 3) for v in struct.unpack_from('<4f', raw, off + 2))
        assert got == stock, f'tint at {off} is {got}, expected {stock}'
        struct.pack_into('<4f', raw, off + 2, *new)

    roots = parse_all(raw)
    assert b''.join(serialise(r) for r in roots) == raw, 'tree does not round-trip'

    seen = {}
    for leaf in (lf for r in roots for lf in leaves(r)):
        body = leaf[1]
        value = string_value(body)
        for old, new in STRING_LEAVES:
            if value == old:
                leaf[1] = string_body(new)
                seen[old] = seen.get(old, 0) + 1
        for old, new in TEXTURE_SETS:
            n = replace_texture_set(body, old, new)
            if n:
                seen[old] = seen.get(old, 0) + n
    for old, _ in STRING_LEAVES + TEXTURE_SETS:
        want = EXPECTED.get(old, 1)
        assert seen.get(old, 0) == want, f'{old!r} found {seen.get(old, 0)} times, expected {want}'

    pad = write_same_size(d, roots, out)
    print(f'wrote {out}: {len(d)} bytes (payload {len(raw)}, pad {pad})')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
