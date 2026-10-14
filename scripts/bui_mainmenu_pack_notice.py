#!/usr/bin/env python3
"""Write the loose main menu: the CONFIG.MEG menu from bui_mainmenu_build.py plus the asset-pack panel.

usage: bui_mainmenu_pack_notice.py <edited RA_MAIN_MENU.BUI> <out loose RA_MAIN_MENU.BUI>

Adds the pack panel top right (the Westwood plate's mirror), every piece hidden and placed straight in
ScreenFitter_Group: the frame (TF_Pack_Frame) and one logo per required pack (TF_Logo_<id>), images cloned from
the menu box's Button_BG; a centred status line (TF_Pack_Status); and two buttons, GET IT ON THE STEAM WORKSHOP
and ENABLE AND RESTART. The launcher layer (redalert/tf_launcher.cpp) shows the pieces for a pack that is missing
or switched off, and sets the status line. Sizes and textures come
from scripts/pack_panel_art.py. The credits hot spot that covered the top right moves onto the Westwood plate.
A loose file overrides the CONFIG.MEG member at any size (docs/bui-front-end-modding.md).
License: GPL v3.
"""
import copy
import struct
import sys

from bui_tree import chain_to, last_id, load, micro, rename_widget, renumber, string_body, string_value, write_loose
from pack_panel_art import LAYOUT, PACK_LOGOS, PANEL

SCREEN_GROUP = b'ScreenFitter_Group'
QUAD_SOURCE = b'Button_BG'
TEXT_SOURCE = b'Version'
BUTTON_SOURCE = b'Button_Exit'
CREDITS = b'Jurassic_Button_1'
CORE = (1920, 1080)
FIT_ORIGIN = (0.03281, -0.02315)   # ScreenFitter_Group on screen: screen = origin + span * child
FIT_SPAN = (0.90417, 1.04167)
PLATE = (53, 24, 453, 118)         # the Westwood plate, core pixels
ALIGN_CENTRE = 1
STATUS = b'NEEDED FOR THE TIBERIAN SUN GDI FACTION'
BUTTONS = ((b'TF_Pack_Get', b'GET IT ON THE STEAM WORKSHOP'), (b'TF_Pack_Enable', b'ENABLE AND RESTART'))


def element_of(node, name):
    """The widget's element node (id 1) under `node`."""
    chain = chain_to(node, name)
    for i in range(len(chain) - 1, 0, -1):
        if chain[i][0] == 1 and chain[i - 1][0] == 0:
            return chain[i]
    raise ValueError(name)


def element_in(roots, name):
    return element_of(next(r for r in roots if chain_to(r, name)), name)


def fitted(x, y, w, h):
    """A core-pixel rect in ScreenFitter_Group's units."""
    return ((x / CORE[0] - FIT_ORIGIN[0]) / FIT_SPAN[0], (y / CORE[1] - FIT_ORIGIN[1]) / FIT_SPAN[1],
            w / CORE[0] / FIT_SPAN[0], h / CORE[1] / FIT_SPAN[1])


def in_panel(x, y, w, h):
    """A rect in panel pixels, in ScreenFitter_Group's units."""
    return fitted(PANEL[0] + x, PANEL[1] + y, w, h)


def set_header(element, old, new, rect, hidden):
    """Rename a widget and set its rect and hidden flag."""
    header = chain_to(element, old)[-1]
    if new != old:
        assert rename_widget(element, old, new) >= 1, old
    w = header[1][0][1]
    at, size = micro(w, 0x02)
    assert size == 16
    struct.pack_into('<4f', w, at, *rect)
    at, _ = micro(w, 0x09)
    w[at] = 1 if hidden else 0


def set_label(element, label):
    """Replace a text or button widget's label: its first string leaf with id 1."""
    labels = []

    def collect(node):
        nid, body = node
        if isinstance(body, list):
            for c in body:
                if c[0] == 1 and not isinstance(c[1], list) and len(c[1]) >= 2 and string_value(c[1]):
                    labels.append(c)
                collect(c)

    collect(element)
    assert labels
    labels[0][1][:] = string_body(label)


def set_texture(quad, texture):
    """Point an image widget at a texture: the string leaf with id 2 in its texture node."""
    for c in quad[1]:
        if c[0] == 4:
            for t in c[1]:
                if t[0] == 1 and isinstance(t[1], list):
                    leaf = next(x for x in t[1] if x[0] == 2)
                    leaf[1][:] = string_body(texture)
                    return
    raise ValueError('no texture node')


def centre_text(node):
    """Centre a text widget's lines: its properties leaf starts with alignment micro-chunk 0x04."""
    nid, body = node
    if isinstance(body, list):
        return sum(centre_text(c) for c in body)
    if len(body) >= 6 and body[0] == 0x04 and body[1] == 4 and nid == 3:
        struct.pack_into('<I', body, 2, ALIGN_CENTRE)
        return 1
    return 0


def panel(roots):
    """The pack panel's widgets, frame first so the rest draws over it; ids not yet renumbered."""
    quad = element_in(roots, QUAD_SOURCE)
    frame = copy.deepcopy(quad)
    set_header(frame, QUAD_SOURCE, b'TF_Pack_Frame', fitted(*PANEL), hidden=True)
    set_texture(frame, b'tf_ui_pack_panel')
    widgets = [frame]
    for pack in PACK_LOGOS:
        logo = copy.deepcopy(quad)
        set_header(logo, QUAD_SOURCE, b'TF_Logo_' + pack.encode(), in_panel(*LAYOUT['logo']), hidden=True)
        set_texture(logo, b'tf_ui_pack_logo_' + pack.lower().encode())
        widgets.append(logo)
    status = copy.deepcopy(element_in(roots, TEXT_SOURCE))
    set_header(status, TEXT_SOURCE, b'TF_Pack_Status', in_panel(*LAYOUT['status']), hidden=True)
    set_label(status, STATUS)
    assert centre_text(status) == 1
    widgets.append(status)
    for name, label in BUTTONS:
        button = copy.deepcopy(element_in(roots, BUTTON_SOURCE))
        set_header(button, BUTTON_SOURCE, name, in_panel(*LAYOUT['button']), hidden=True)
        set_label(button, label)
        widgets.append(button)
    return widgets


def main(src, out):
    base, roots = load(src)
    screen_group = chain_to(next(r for r in roots if chain_to(r, SCREEN_GROUP)), SCREEN_GROUP)[-2]
    fresh = last_id(roots)
    for widget in panel(roots):
        fresh = renumber(widget, fresh)
        screen_group[1].append(widget)
    credits = element_in(roots, CREDITS)
    set_header(credits, CREDITS, CREDITS, fitted(*PLATE), hidden=False)
    write_loose(base, roots, out)
    print('wrote', out)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
