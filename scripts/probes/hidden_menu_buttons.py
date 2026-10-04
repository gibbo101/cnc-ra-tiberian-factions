#!/usr/bin/env python3
"""Probe: unhide the main menu's hidden stock buttons so each can be clicked.

usage: hidden_menu_buttons.py <in.BUI> <out.BUI>
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from bui_tree import load, headers, replace_texture_set, write_same_size  # noqa: E402

STEEL = b'TF_MainMenuSteelButton_Textures'
STRIP = [b'Button_Buy_Demo', b'Button_CoopCampaign', b'Button_Metagame', b'Button_Campaign',
         b'Button_Multiplayer', b'Button_Unranked', b'Button_LAN', b'Button_MetaDesigner',
         b'Button_Manual', b'Button_Editor', b'Button_Load']


def micro(widget, tag):
    """Offset of micro-chunk `tag`'s data in a header leaf, walking [id][size][data]."""
    p = 0
    while p + 2 <= len(widget):
        i, s = widget[p], widget[p + 1]
        if i == tag:
            return p + 2, s
        p += 2 + s
    raise KeyError(f'no micro-chunk {tag:#x}')


def one(roots, name):
    found = headers(roots, name)
    assert len(found) == 1, (name, len(found))
    return found[0][1][0][1]


def set_hidden(widget, value):
    at, size = micro(widget, 0x09)
    assert size == 1
    widget[at] = value


def set_rect(widget, x, y, w, h):
    at, size = micro(widget, 0x02)
    assert size == 16
    struct.pack_into('<4f', widget, at, x, y, w, h)


def main(src, out):
    d, roots = load(src)
    group = one(roots, b'Group')
    set_hidden(group, 0)
    set_rect(group, 0.645, 0.30, 0.15, 0.033)
    for k, name in enumerate(STRIP):
        w = one(roots, name)
        set_hidden(w, 0)
        set_rect(w, 0.0, k * 1.2, 1.0, 1.0)
        assert replace_texture_set(w, b'default', STEEL) == 1, name
    sk = one(roots, b'Button_Skirmish')
    set_hidden(sk, 0)
    set_rect(sk, 0.0052, 0.8951, 0.9896, 0.1049)
    set_hidden(one(roots, b'Credits_Button'), 0)
    for name in (b'Button_Host', b'Button_Join'):
        assert replace_texture_set(one(roots, name), b'default', STEEL) == 1, name
    pad = write_same_size(d, roots, out)
    print(f'wrote {out}: {len(d)} bytes, pad {pad}')


if __name__ == '__main__':
    main(*sys.argv[1:])
