#!/usr/bin/env python3
"""
Add the mod's green text styles to FONTLIBRARY.BFD, the launcher's named text styles.

usage: fontlib_build.py <base.BFD> <out.BFD>

Each style is a top-level node [name, font face, properties], its colour the properties'
`0b 10` RGBA. The lobby's steel slots and rows want the main menu's green text, but the launcher
recolours some of their text widgets as it fills them, which overrides a widget tint; a style
that is green itself stays green. The library has green styles only at 18, 20, 24 and 30 points,
so each style below copies a white stock one and takes the green of the menu's labels
("24 Point Regular Outline Green", (0, 1, 0)). The names are short because the screens that use
them have only a few bytes to spare. The file keeps its byte size (bui_tree.py).
"""
import copy
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bui_tree import load, string_body, string_value, write_same_size  # noqa: E402

GREEN = (0.0, 1.0, 0.0, 1.0)
STYLES = [(b'G16', b'16 Point Outline'), (b'G18', b'18 Point Outline'),
          (b'G18R', b'18 Point Regular'), (b'G15R', b'15 Point Regular')]


def main(base, out):
    d, roots = load(base)
    by_name = {string_value(r[1][0][1]): r for r in roots}
    for name, source in STYLES:
        assert name not in by_name, f'{name!r} already in the library'
        style = copy.deepcopy(by_name[source])
        style[1][0][1] = string_body(name)
        props = style[1][2][1]
        at = props.find(b'\x0b\x10')
        assert at >= 0 and struct.unpack_from('<4f', props, at + 2) == (1.0, 1.0, 1.0, 1.0), source
        struct.pack_into('<4f', props, at + 2, *GREEN)
        roots.append(style)
    pad = write_same_size(d, roots, out)
    print(f'wrote {out}: {len(d)} bytes (pad {pad}), {len(roots)} styles')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
