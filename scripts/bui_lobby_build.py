#!/usr/bin/env python3
"""
Rebuild Tiberian Dawn's lobby screens for the mod's RA front end.

usage: bui_lobby_build.py <base.BUI> <out.BUI>     (the base's file name picks the edit)

factions_build.py points the RA front end's skirmish lobby, LAN lobby, LAN match list and
Workshop map browser at TD's, whose green panels match the mod's menu.

  UI_SKIRMISH_GAMELOBBY.BUI,   their backdrop is TD's main-menu art with the Command & Conquer logo,
  UI_LAN_GAMELOBBY.BUI,        so the backdrop leaf names RA's brushed-steel menu background, the
  UI_LAN_MULTIPLAYERMENU.BUI,  one the loading screen that follows sits on. Their flat green
  UI_WORKSHOPMAP_BROWSE.BUI    buttons (map-list headers, chat send) take the menu's steel button
                               set; that green set is shared with the in-game chat, so it is left
                               as it is, as the slot and row art lobby_art.py repaints steel is not.
                               The list headers' labels take the green copy of their style.
  BUTTONPLAYERNAMECOMBOBOX.BUI, the text on the steel slots, rows and Custom map buttons (player
  BUTTONTEAMCOMBOBOX.BUI,       name, team, map and LAN game columns) takes the green copy of its
  UI_LISTBOX_MAPSELECT_ENTRY.BUI, style that fontlib_build.py adds. A widget tint would not do:
  UI_LISTBOX_LAN_ENTRY.BUI,     the launcher recolours several of these widgets as it fills them.
  UI_CUSTOM_MAP_FILE_ENTRY.BUI
  BUTTONFACTIONCOMBOBOX.BUI    the slot's faction picture (Combo_Quad) is sized for TD's small
                               square icons; RA's picker emblems are 150x80 plates, so it takes the
                               on-screen size RA's own slot gives them, about its centre. Its
                               drop-down list (Combo_Listbox) is three rows tall for TD's factions,
                               with a blank scroll bar; it is made tall enough for the nine entries the launcher lists (each RA
                               country and Random), measured on screen: 8.3 of TD's row heights.
  UI_GAMELOBBY_PLAYERSLOT.BUI  the list answers the mouse only inside the slot's faction group, so the group
                               takes the whole slot content area, grown to hold the nine rows, with every
                               widget in the slot kept at its on-screen place and size. The combo box's
                               children and its list's row height (a fraction of the combo's height) shrink
                               to match, so the rows stay TD's size.

Each file keeps its byte size (bui_tree.py).
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bui_tree import (find_headers, headers, leaves, load, micro_floats, replace_texture_set,  # noqa: E402
                      string_body, string_value, write_same_size)

BACKDROP = (b'ui_mainmenubg_01', b'ui_ra_menu_bg')
HEADER_BUTTONS = (b'FlatGreenTextButton', b'TF_MainMenuSteelButton_Textures')
HEADER_LABELS = (b'16 Point Outline', b'G16')
FACTION_QUAD = b'Combo_Quad'
STOCK_QUAD = (0.266, 0.029, 0.4787, 0.1484)
RA_SIZED_QUAD = (0.1332, 0.0417, 0.7442, 0.1231)
FACTION_LIST = b'Combo_Listbox'
STOCK_LIST = (0.0426, 0.2097, 0.7234, 0.5774)
LIST_ROWS = (3, 8.3)
SLOT_CONTENT = b'Slot_Content_Group'
CONTENT_H = (6.8966, 8.4)
FACTION_GROUP = b'PlayerFactionGroup'
STOCK_FACTION_GROUP = (0.5181, 0.005, 0.1618, 0.6575)
STOCK_ROW_HEIGHT = 0.1711


def faction_group_scale():
    """How much smaller the faction combo's children must be, against its grown group, to keep their size."""
    k = CONTENT_H[0] / CONTENT_H[1]
    y, h = STOCK_FACTION_GROUP[1], STOCK_FACTION_GROUP[3]
    return (h * CONTENT_H[0]) / ((1.0 - y * k) * CONTENT_H[1])


def is_header(node):
    """A widget header: an id 0 or 0x0b container whose first child is the rect/tint leaf."""
    return node[0] in (0, 0x0b) and isinstance(node[1], list) and node[1] and not isinstance(node[1][0][1], list)


def widget_of(roots, name):
    """The widget node whose header is named `name`: [header, then [1][4] holders of child widgets]."""
    def walk(node):
        body = node[1]
        if not isinstance(body, list):
            return []
        if body and is_header(body[0]) and find_headers(body[0], name):
            return [node]
        return [w for child in body for w in walk(child)]
    found = [w for r in roots for w in walk(r)]
    assert len(found) == 1, f'found {len(found)} {name!r} widgets'
    return found[0]


def child_headers(widget):
    """The headers of a widget's direct child widgets. A child sits in a [1][4] holder, either as
    its own widget node or, for a text widget such as the slot number, as the holder's first leaf."""
    out = []
    for c in widget[1][1:]:
        if c[0] != 1 or not isinstance(c[1], list):
            continue
        for g in c[1]:
            if g[0] != 4 or not isinstance(g[1], list) or not g[1]:
                continue
            if is_header(g[1][0]):
                out.append(g[1][0])
            else:
                out += [w[1][0] for w in g[1] if isinstance(w[1], list) and w[1] and is_header(w[1][0])]
    return out


def scale_y(header, factor):
    widget, at = micro_floats(header, 0x02)
    x, y, w, h = struct.unpack_from('<4f', widget, at)
    struct.pack_into('<4f', widget, at, x, y * factor, w, h * factor)


def td_screen(green_buttons, header_labels):
    """RA's backdrop, the screen's flat green buttons in steel and its list headers' labels green."""
    def edit(roots):
        found = [lf for r in roots for lf in leaves(r) if lf[0] == 2 and string_value(lf[1]) == BACKDROP[0]]
        assert len(found) == 1, f'found {len(found)} backdrops'
        found[0][1] = string_body(BACKDROP[1])
        swapped = sum(replace_texture_set(lf[1], *HEADER_BUTTONS) for r in roots for lf in leaves(r))
        assert swapped == green_buttons, f'swapped {swapped} green buttons, expected {green_buttons}'
        labels = [lf for r in roots for lf in leaves(r) if lf[0] == 3 and string_value(lf[1]) == HEADER_LABELS[0]]
        assert len(labels) == header_labels, f'found {len(labels)} header labels, expected {header_labels}'
        for lf in labels:
            lf[1] = string_body(HEADER_LABELS[1])
    return edit


def text_font(node, name):
    """The font leaf of the text widget named `name`: the id 2 string beside its header."""
    nid, body = node
    if not isinstance(body, list):
        return []
    named = any(c[0] in (0, 0x0b) and isinstance(c[1], list) and
                any(g[0] == 5 and not isinstance(g[1], list) and string_value(g[1]) == name for g in c[1])
                for c in body)
    if named:
        return [c for c in body if c[0] == 2 and not isinstance(c[1], list) and string_value(c[1])]
    return [f for child in body for f in text_font(child, name)]


def green_fonts(widgets=(), labels=()):
    """Text widgets (name, green style) and button labels (old style, green style, count) in green."""
    def edit(roots):
        for name, style in widgets:
            found = [f for r in roots for f in text_font(r, name)]
            assert len(found) == 1, f'found {len(found)} fonts for {name!r}'
            found[0][1] = string_body(style)
        for old, style, count in labels:
            found = [lf for r in roots for lf in leaves(r) if lf[0] == 3 and string_value(lf[1]) == old]
            assert len(found) == count, f'found {len(found)} {old!r} labels, expected {count}'
            for lf in found:
                lf[1] = string_body(style)
    return edit


def faction_quad(roots):
    quads = headers(roots, FACTION_QUAD)
    assert len(quads) == 1, f'found {len(quads)} faction pictures'
    widget, at = micro_floats(quads[0], 0x02)
    got = tuple(round(v, 4) for v in struct.unpack_from('<4f', widget, at))
    assert got == STOCK_QUAD, f'faction picture rect is {got}'
    struct.pack_into('<4f', widget, at, *RA_SIZED_QUAD)
    lists = headers(roots, FACTION_LIST)
    assert len(lists) == 1, f'found {len(lists)} faction lists'
    widget, at = micro_floats(lists[0], 0x02)
    got = tuple(round(v, 4) for v in struct.unpack_from('<4f', widget, at))
    assert got == STOCK_LIST, f'faction list rect is {got}'
    x, y, w, h = struct.unpack_from('<4f', widget, at)
    struct.pack_into('<4f', widget, at, x, y, w, h * LIST_ROWS[1] / LIST_ROWS[0])
    for name in (b'Combo_Button', FACTION_QUAD, FACTION_LIST):
        found = headers(roots, name)
        assert len(found) == 1, f'found {len(found)} {name!r}'
        scale_y(found[0], faction_group_scale())
    holder, at = row_height(roots)
    got = round(struct.unpack_from('<f', holder, at)[0], 4)
    assert got == STOCK_ROW_HEIGHT, f'faction list row height is {got}'
    struct.pack_into('<f', holder, at, STOCK_ROW_HEIGHT * faction_group_scale())


def row_height(roots):
    """The list's row height (list box micro-chunk 05), a fraction of the combo box's height: the
    list box's property leaf (id 4) sits in the holder beside the Combo_Listbox widget."""
    def walk(node):
        body = node[1]
        if not isinstance(body, list):
            return []
        if node[0] == 4 and any(isinstance(c[1], list) and c[1] and is_header(c[1][0])
                                and find_headers(c[1][0], FACTION_LIST) for c in body):
            return [c[1] for c in body if c[0] == 4 and not isinstance(c[1], list) and bytes(c[1][:2]) == b'\x05\x04']
        return [x for child in body for x in walk(child)]
    found = [x for r in roots for x in walk(r)]
    assert len(found) == 1, f'found {len(found)} faction list property leaves'
    return found[0], 2


def slot_room(roots):
    """The faction drop-down answers the mouse only inside its slot's PlayerFactionGroup, which TD
    sizes for three rows; nine rows ran past it, so the lower ones closed the list and took no
    clicks. The slot's content area grows to hold the nine, every widget in it keeps its on-screen
    place and size, and the faction group takes the whole area, as the colour group already does."""
    content = headers(roots, SLOT_CONTENT)
    assert len(content) == 1, f'found {len(content)} slot content groups'
    widget, at = micro_floats(content[0], 0x02)
    x, y, w, h = struct.unpack_from('<4f', widget, at)
    assert round(h, 4) == CONTENT_H[0], f'slot content height is {h}'
    struct.pack_into('<4f', widget, at, x, y, w, CONTENT_H[1])
    k = CONTENT_H[0] / CONTENT_H[1]
    scaled = 0
    for header in child_headers(widget_of(roots, SLOT_CONTENT)):
        scale_y(header, k)
        scaled += 1
    assert scaled == 9, f'scaled {scaled} slot widgets, expected 9'
    faction = headers(roots, FACTION_GROUP)
    assert len(faction) == 1, f'found {len(faction)} faction groups'
    widget, at = micro_floats(faction[0], 0x02)
    x, y, w, h = struct.unpack_from('<4f', widget, at)
    assert abs(h - STOCK_FACTION_GROUP[3] * k) < 1e-4, f'faction group height is {h}'
    struct.pack_into('<4f', widget, at, x, y, w, 1.0 - y)


EDITS = {'UI_SKIRMISH_GAMELOBBY': td_screen(4, 4), 'UI_LAN_GAMELOBBY': td_screen(5, 4),
         'UI_LAN_MULTIPLAYERMENU': td_screen(3, 3), 'UI_WORKSHOPMAP_BROWSE': td_screen(0, 0),
         'BUTTONFACTIONCOMBOBOX': faction_quad, 'UI_GAMELOBBY_PLAYERSLOT': slot_room,
         'BUTTONPLAYERNAMECOMBOBOX': green_fonts([(b'Combo_Text', b'G16')]),
         'BUTTONTEAMCOMBOBOX': green_fonts([(b'Combo_Text', b'G18')]),
         'UI_LISTBOX_MAPSELECT_ENTRY': green_fonts([(b'Map_Name_Text', b'G16'), (b'Map_Climate_Text', b'G16'),
                                                    (b'Map_Size_Text', b'G16'), (b'Map_Players_Text', b'G16'),
                                                    (b'HeaderText', b'G18')]),
         'UI_LISTBOX_LAN_ENTRY': green_fonts([(b'Game_Name_Text', b'G15R'), (b'Players_Text', b'G15R'),
                                              (b'Map_Name_Text', b'G15R')]),
         'UI_CUSTOM_MAP_FILE_ENTRY': green_fonts(labels=[(b'18 Point Regular', b'G18R', 1)])}


def main(base, out):
    kind = Path(base).name.split('.')[0].upper()
    d, roots = load(base)
    EDITS[kind](roots)
    pad = write_same_size(d, roots, out)
    print(f'wrote {out}: {len(d)} bytes (pad {pad})')


if __name__ == '__main__':
    if len(sys.argv) != 3 or Path(sys.argv[1]).name.split('.')[0].upper() not in EDITS:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
