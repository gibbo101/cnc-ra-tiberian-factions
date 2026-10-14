#!/usr/bin/env python3
"""Write the loose main menu: the CONFIG.MEG menu from bui_mainmenu_build.py plus the TS-HD pack notice.

usage: bui_mainmenu_pack_notice.py <edited RA_MAIN_MENU.BUI> <out loose RA_MAIN_MENU.BUI>

In the menu box, above BUILD and VERSION, it adds two centred lines of text, one for a missing pack
and one for a pack that is installed but switched off; under the box, a button that opens the
pack's Workshop page. All three start
hidden; the launcher layer (redalert/tf_launcher.cpp) shows the ones that fit at the menu.
A loose file overrides the CONFIG.MEG member at any size (docs/bui-front-end-modding.md).
License: GPL v3.
"""
import copy
import struct
import sys

from bui_tree import chain_to, last_id, load, micro, string_body, string_value, write_loose

TEXT_SOURCE = b'Version'
BUTTON_SOURCE = b'Button_Exit'
SCREEN_GROUP = b'ScreenFitter_Group'
MENU_BOX = (0.307, 0.302, 0.416, 0.566)

TEXT_RECT = (MENU_BOX[0], 0.796, MENU_BOX[2], 0.018)
MENU_BUTTONS = (0.3507, 0.3287)
BUTTON_RECT = (MENU_BUTTONS[0], 0.888, MENU_BUTTONS[1], 0.040)
ALIGN_CENTRE = 1
NOTICES = [
    (b'TF_Pack_Missing', b'TIBERIAN SUN GDI NEEDS THE TIBERIAN SUN HD ASSETS MOD'),
    (b'TF_Pack_Off', b'TIBERIAN SUN HD ASSETS IS INSTALLED BUT OFF: ENABLE IT IN MODS AND RESTART'),
]
BUTTON = (b'TF_Pack_Get', b'GET IT ON THE STEAM WORKSHOP')


def element_of(roots, name):
    """The widget's element node (id 1) and the group node holding it."""
    chain = next(c for c in (chain_to(r, name) for r in roots) if c)
    for i in range(len(chain) - 1, 0, -1):
        if chain[i][0] == 1 and chain[i - 1][0] == 0:
            return chain[i], chain[i - 1]
    raise ValueError(name)


def group_node(roots, name):
    """The container node a group widget's members sit in (the node holding its header)."""
    chain = next(c for c in (chain_to(r, name) for r in roots) if c)
    assert chain[-2][0] == 0 and isinstance(chain[-2][1], list)
    return chain[-2]


def clone(roots, source, name, label, rect, fresh):
    """A hidden copy of widget `source` named `name`, showing `label`, at `rect`."""
    element, _ = element_of(roots, source)
    copy_ = copy.deepcopy(element)
    header = chain_to(copy_, source)[-1]
    for c in header[1]:
        if c[0] == 5 and not isinstance(c[1], list):
            c[1][:] = string_body(name)
    w = header[1][0][1]
    at, size = micro(w, 0x01)
    struct.pack_into('<I', w, at, fresh)
    at, size = micro(w, 0x02)
    assert size == 16
    struct.pack_into('<4f', w, at, *rect)
    at, size = micro(w, 0x09)
    w[at] = 1
    labels = []

    def collect(node):
        nid, body = node
        if isinstance(body, list):
            for c in body:
                if c[0] == 1 and not isinstance(c[1], list) and len(c[1]) >= 2 and string_value(c[1]):
                    labels.append(c)
                collect(c)

    collect(copy_)
    assert labels, name
    labels[0][1][:] = string_body(label)
    return copy_


def centre_text(node):
    """Centre a text widget's lines: its properties leaf starts with alignment micro-chunk 0x04."""
    nid, body = node
    if isinstance(body, list):
        return sum(centre_text(c) for c in body)
    if len(body) >= 6 and body[0] == 0x04 and body[1] == 4 and nid == 3:
        struct.pack_into('<I', body, 2, ALIGN_CENTRE)
        return 1
    return 0


def main(src, out):
    base, roots = load(src)
    screen_group = group_node(roots, SCREEN_GROUP)
    fresh = last_id(roots)
    for name, label in NOTICES:
        fresh += 0x10000
        text = clone(roots, TEXT_SOURCE, name, label, TEXT_RECT, fresh)
        assert centre_text(text) == 1, name
        screen_group[1].append(text)
    fresh += 0x10000
    screen_group[1].append(clone(roots, BUTTON_SOURCE, BUTTON[0], BUTTON[1], BUTTON_RECT, fresh))
    write_loose(base, roots, out)
    print('wrote', out)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
