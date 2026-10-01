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
                               with a blank scroll bar; it is made nine rows tall, one per RA country and one for Random, so every row
                               the launcher lists is on show.

Each file keeps its byte size (bui_tree.py).
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bui_tree import (headers, leaves, load, micro_floats, replace_texture_set, string_body,  # noqa: E402
                      string_value, write_same_size)

BACKDROP = (b'ui_mainmenubg_01', b'ui_ra_menu_bg')
HEADER_BUTTONS = (b'FlatGreenTextButton', b'TF_MainMenuSteelButton_Textures')
HEADER_LABELS = (b'16 Point Outline', b'G16')
FACTION_QUAD = b'Combo_Quad'
STOCK_QUAD = (0.266, 0.029, 0.4787, 0.1484)
RA_SIZED_QUAD = (0.1332, 0.0417, 0.7442, 0.1231)
FACTION_LIST = b'Combo_Listbox'
STOCK_LIST = (0.0426, 0.2097, 0.7234, 0.5774)
LIST_ROWS = (3, 9)


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


EDITS = {'UI_SKIRMISH_GAMELOBBY': td_screen(4, 4), 'UI_LAN_GAMELOBBY': td_screen(5, 4),
         'UI_LAN_MULTIPLAYERMENU': td_screen(3, 3), 'UI_WORKSHOPMAP_BROWSE': td_screen(0, 0),
         'BUTTONFACTIONCOMBOBOX': faction_quad,
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
