#!/usr/bin/env python3
"""Write the loose main menu: the CONFIG.MEG menu from bui_mainmenu_build.py, the ADD-ONS row and the pack panel.

usage: bui_mainmenu_pack_notice.py <edited RA_MAIN_MENU.BUI> <out loose RA_MAIN_MENU.BUI>

Adds TIBERIAN FACTIONS ADD-ONS (TF_AddOns, a clone of EXIT GAME) between LAN MODE and REPLAY / OBSERVER, the rows
under it lower; it opens the ADD-ONS screen (scripts/bui_addons_build.py). FACTION ENCYCLOPEDIA (TF_Encyclopedia)
goes under it, opening the encyclopedia (scripts/bui_encyclopedia_build.py), and REPLAY / OBSERVER takes BONUS
GALLERY's row; the gallery's button and its new-content badge move off screen, as the launcher shows them again
(shrunk, the badge stretched into view). TIBERIAN FACTIONS SETTINGS (TF_Settings) goes under REPLAY / OBSERVER,
opening the Settings page (scripts/bui_settings_build.py), OPTIONS taking HELP's row; HELP moves off screen.
Adds the add-ons notice top right (the Westwood plate's mirror), every piece hidden and placed straight in
ScreenFitter_Group: the frame (TF_Pack_Frame) and the title-over-ADD-ONS logo (TF_Pack_Logo), images cloned from
the menu box's Button_BG; the menu box's moving scanline sheen over the frame (TF_Pack_Sheen); two centred lines
(TF_Pack_Status, TF_Pack_Status2); and ENABLE ADD-ONS (TF_Pack_Open). The launcher layer
(redalert/tf_launcher.cpp) shows them while an add-on is not enabled. TF_Version,
centred between BUILD and VERSION in the menu box, shows the mod's version, which the launcher layer reads from
ccmod.json. Sizes and textures come
from scripts/pack_panel_art.py. The credits hot spot that covered the top right moves onto the Westwood plate.
A loose file overrides the CONFIG.MEG member at any size (docs/bui-front-end-modding.md).
License: GPL v3.
"""
import copy
import struct
import sys

from bui_tree import chain_to, last_id, load, micro, rename_widget, renumber, string_body, string_value, write_loose
from pack_panel_art import LAYOUT, PANEL

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
STATUS = (b'YOU HAVE TIBERIAN FACTIONS ADD-ONS', b'AVAILABLE THAT ARE NOT ENABLED')
SHEEN_SOURCE = b'Button_Scanlines'   # the menu box's moving scanline sheen
VERSION_RECT = (0.426, 0.822, 0.18, 0.017)   # centred on the menu box, on BUILD and VERSION's row
BUTTONS = ((b'TF_Pack_Open', b'ENABLE ADD-ONS'),)
ADDONS_ROW_Y = 0.3978              # LAN MODE's row + one row, in the button column's units
ROW_STEP = 0.0995
OFF_SCREEN_X = -20.0               # far left of the button column, outside any screen
LOWER_ROWS = (b'Button_Replays', b'Button_Video_Options', b'Button_Help', b'Button_Exit')


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


def rect_of(element, name):
    """A widget's rect."""
    w = chain_to(element, name)[-1][1][0][1]
    at, _ = micro(w, 0x02)
    return struct.unpack_from('<4f', w, at)


def addons_row(roots):
    """TIBERIAN FACTIONS ADD-ONS and FACTION ENCYCLOPEDIA under LAN MODE, REPLAY / OBSERVER in BONUS GALLERY's row,
    the rows below it moved down one, then TIBERIAN FACTIONS SETTINGS in OPTIONS' row and OPTIONS in HELP's."""
    exit_root = next(r for r in roots if chain_to(r, b'Button_Exit'))
    exit_button = element_of(exit_root, b'Button_Exit')
    column = next(n for n in chain_to(exit_root, b'Button_Exit') if isinstance(n[1], list) and exit_button in n[1])
    x, _, w, h = rect_of(exit_button, b'Button_Exit')
    bonus = element_in(roots, b'Button_Bonus_Content')
    bonus_y = rect_of(bonus, b'Button_Bonus_Content')[1]
    for name in LOWER_ROWS:
        element = element_in(roots, name)
        rx, ry, rw, rh = rect_of(element, name)
        ry = bonus_y + ROW_STEP if name == b'Button_Replays' else ry + ROW_STEP
        set_header(element, name, name, (rx, ry, rw, rh), hidden=False)
    button = copy.deepcopy(exit_button)
    set_header(button, b'Button_Exit', b'TF_AddOns', (x, ADDONS_ROW_Y, w, h), hidden=False)
    set_label(button, b'TIBERIAN FACTIONS ADD-ONS')
    encyclopedia = copy.deepcopy(exit_button)
    set_header(encyclopedia, b'Button_Exit', b'TF_Encyclopedia', (x, ADDONS_ROW_Y + ROW_STEP, w, h), hidden=False)
    set_label(encyclopedia, b'FACTION ENCYCLOPEDIA')
    help_button = element_in(roots, b'Button_Help')
    options = element_in(roots, b'Button_Video_Options')
    settings = copy.deepcopy(exit_button)
    set_header(settings, b'Button_Exit', b'TF_Settings', rect_of(options, b'Button_Video_Options'), hidden=False)
    set_header(options, b'Button_Video_Options', b'Button_Video_Options', rect_of(help_button, b'Button_Help'),
               hidden=False)
    set_label(settings, b'TIBERIAN FACTIONS SETTINGS')
    for name in (b'Button_Bonus_Content', b'BonusNotification_Group', b'Button_Help'):
        element = element_in(roots, name)
        _, y, w, h = rect_of(element, name)
        set_header(element, name, name, (OFF_SCREEN_X, y, w, h), hidden=True)
    return column, [button, encyclopedia, settings]


def panel(roots):
    """The add-ons notice's widgets, frame and sheen first so the rest draws over them; ids not yet renumbered."""
    quad = element_in(roots, QUAD_SOURCE)
    frame = copy.deepcopy(quad)
    set_header(frame, QUAD_SOURCE, b'TF_Pack_Frame', fitted(*PANEL), hidden=True)
    set_texture(frame, b'tf_ui_pack_panel')
    sheen = copy.deepcopy(element_in(roots, SHEEN_SOURCE))
    set_header(sheen, SHEEN_SOURCE, b'TF_Pack_Sheen', fitted(*PANEL), hidden=True)
    logo = copy.deepcopy(quad)
    set_header(logo, QUAD_SOURCE, b'TF_Pack_Logo', in_panel(*LAYOUT['notice_logo']), hidden=True)
    set_texture(logo, b'tf_ui_pack_logo_addons')
    widgets = [frame, sheen, logo]
    for name, rect, label in ((b'TF_Pack_Status', 'status', STATUS[0]), (b'TF_Pack_Status2', 'status2', STATUS[1])):
        status = copy.deepcopy(element_in(roots, TEXT_SOURCE))
        set_header(status, TEXT_SOURCE, name, in_panel(*LAYOUT[rect]), hidden=True)
        set_label(status, label)
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
    column, menu_rows = addons_row(roots)
    screen_group = chain_to(next(r for r in roots if chain_to(r, SCREEN_GROUP)), SCREEN_GROUP)[-2]
    fresh = last_id(roots)
    for row in menu_rows:
        fresh = renumber(row, fresh)
        column[1].append(row)
    for widget in panel(roots):
        fresh = renumber(widget, fresh)
        screen_group[1].append(widget)
    version = copy.deepcopy(element_in(roots, TEXT_SOURCE))
    set_header(version, TEXT_SOURCE, b'TF_Version', VERSION_RECT, hidden=False)
    set_label(version, b'TIBERIAN FACTIONS')
    assert centre_text(version) == 1
    fresh = renumber(version, fresh)
    screen_group[1].append(version)
    credits = element_in(roots, CREDITS)
    set_header(credits, CREDITS, CREDITS, fitted(*PLATE), hidden=False)
    write_loose(base, roots, out)
    print('wrote', out)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
