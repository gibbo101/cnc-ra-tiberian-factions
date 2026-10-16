#!/usr/bin/env python3
"""Write the ADD-ONS screen, Data/ART/GUI/RA/TF_ADDONS.BUI, from the CAMPAIGNS page's frame.

usage: bui_addons_build.py <loose RA_MISSIONSELECT.BUI> <UI_BONUSCONTENT base BUI> <RA_MAIN_MENU BUI> <out BUI>

The CAMPAIGNS page (scripts/campaigns_page_build.sh) with its campaign widgets hidden and its class swapped for
ClientG's SplashScreen, which binds nothing, so the launcher layer (redalert/tf_launcher.cpp) runs it. Added: in
the top panel a tab per add-on kind, each a clone of Back with a glow when open and a badge counting its changes,
over two lines of text (the pending changes, or how to use the screen); on the left COMING SOON for an empty tab and
ROW_SLOTS rows, each with TD's checkbox from Bonus Gallery, a logo per pack in pack_panel_art.PACK_LOGOS, the
pack's name and state, the Bonus Gallery glow when selected and, under the checkbox, the menu's invisible credits
hot spot to select the row; on the right the selected pack's name, logo, description, what it needs or what needs
it, its status and a 20-segment progress bar. Start becomes APPLY AND RESTART, with UNDO CHANGES (a clone of Back)
beside it. Rects are pixels of a 1280x800 Deck screenshot of the screen. License: GPL v3.
"""
import copy
import struct
import sys

from bui_mainmenu_pack_notice import element_in, set_header, set_label, set_texture
from bui_tree import chain_to, last_id, load, micro, micro_floats, renumber, string_body, write_loose
from pack_panel_art import PACK_LOGOS

FORMAT_GROUP = b'MissionSelectFormatGroup'
ORIGIN, SCALE = (172.0, 62.0), (933.0, 679.0)   # screenshot pixels of the frame group's (0, 0) and its span
HIDE = (b'UI_CampaignSelect_Group', b'MissionList_Box', b'MissionList_Box_SOVIET', b'MissionList_Box_ALLIED',
        b'MissionList_SampleEntry', b'CustomCampaignList_Group', b'TF_Banner_RA', b'TF_Banner_TD', b'TF_Banner_TS',
        b'TF_Coming_Soon', b'UI_MissionDescription_Group', b'CinematicButtonGroup', b'MissionDifficulty_Group',
        b'BackButtonDisabled_Quad', b'StartButtonDisabled_Quad')
BIG_TEXT, SMALL_TEXT = b'UI_MissionName_Text', b'UI_MissionNumber_Text'
WHITE, GREEN, BRIGHT, AMBER = (0.81, 0.81, 0.81, 1), (0.21, 0.75, 0, 1), (0.59, 1, 0.43, 1), (0.94, 0.69, 0.16, 1)
GREY = (0.42, 0.47, 0.42, 1)
LEFT, CENTRE = 0, 1
ROW_TOP, ROW_STEP, ROW_HEIGHT = 353, 70, 64
ROW_SLOTS = 4                                    # rows per tab: ADDON_ROWS in redalert/tf_launcher.cpp
TABS = (b'ASSETS', b'THEATRES', b'CAMPAIGNS')    # KIND_NAMES in redalert/tf_launcher.cpp
TAB_LEFT, TAB_STEP, TAB_WIDTH, TAB_TOP, TAB_HEIGHT = 222, 218, 200, 168, 35
DETAIL_LINES = 4
BAR_SEGMENTS, BAR_LEFT, BAR_STEP = 20, 703, 16
GET_RECT = (0.656, 0.0, 0.344, 1.0)              # in BottomNavButtons_Group, right-aligned like Start
UNDO_RECT = (0.445, 0.0, 0.2, 1.0)               # in BottomNavButtons_Group, left of GET_RECT


def fit(x, y, w, h):
    """Screenshot pixels in the frame group's units."""
    return ((x - ORIGIN[0]) / SCALE[0], (y - ORIGIN[1]) / SCALE[1], w / SCALE[0], h / SCALE[1])


def align(node, value):
    """Set a text widget's alignment: its properties leaf starts with micro-chunk 0x04."""
    nid, body = node
    if isinstance(body, list):
        return sum(align(c, value) for c in body)
    if nid == 3 and len(body) >= 6 and body[0] == 0x04 and body[1] == 4:
        struct.pack_into('<I', body, 2, value)
        return 1
    return 0


def tint(element, name, rgba):
    widget, at = micro_floats(chain_to(element, name)[-1], 0x03)
    struct.pack_into('<4f', widget, at, *rgba)


def text(roots, source, name, rect, label, colour, alignment, hidden=True):
    element = copy.deepcopy(element_in(roots, source))
    set_header(element, source, name, fit(*rect), hidden)
    set_label(element, label)
    tint(element, name, colour)
    assert align(element, alignment) == 1, name
    return element


def quad(roots, source, name, rect, texture, hidden=True):
    element = copy.deepcopy(element_in(roots, source))
    set_header(element, source, name, fit(*rect), hidden)
    if texture is not None:
        set_texture(element, texture)
    return element


def widgets(roots, bonus, menu):
    """The screen's added widgets, in draw order; ids not yet renumbered."""
    out = [text(roots, SMALL_TEXT, b'TF_AO_Intro1', (222, 229, 840, 22), b'INTRO', GREEN, LEFT, hidden=False),
           text(roots, SMALL_TEXT, b'TF_AO_Intro2', (222, 251, 840, 22), b'INTRO', GREEN, LEFT, hidden=False)]
    for tab, label in enumerate(TABS):
        x = TAB_LEFT + tab * TAB_STEP
        out.append(quad(menu, b'BonusButtonGlow_Quad', b'TF_AO_TabGlow%d' % tab,
                        (x - 6, TAB_TOP - 5, TAB_WIDTH + 12, TAB_HEIGHT + 10), None))
        button = copy.deepcopy(element_in(roots, b'Back_Button'))
        set_header(button, b'Back_Button', b'TF_AO_Tab%d' % tab, fit(x, TAB_TOP, TAB_WIDTH, TAB_HEIGHT), hidden=False)
        out.append(button)
        out.append(text(roots, SMALL_TEXT, b'TF_AO_TabText%d' % tab, (x, TAB_TOP + 7, TAB_WIDTH, 22), label, GREY,
                        CENTRE, hidden=False))
        out.append(text(roots, SMALL_TEXT, b'TF_AO_TabOn%d' % tab, (x, TAB_TOP + 7, TAB_WIDTH, 22), label, BRIGHT,
                        CENTRE))
        out.append(text(roots, SMALL_TEXT, b'TF_AO_Badge%d' % tab, (x, TAB_TOP + TAB_HEIGHT + 2, TAB_WIDTH, 18),
                        b'1 CHANGE', AMBER, CENTRE))
    out += [text(roots, BIG_TEXT, b'TF_AO_ListHead', (207, 306, 411, 28), b'ADD-ONS', BRIGHT, CENTRE, hidden=False),
            text(roots, BIG_TEXT, b'TF_AO_Soon', (207, 480, 411, 40), b'COMING SOON', BRIGHT, CENTRE)]
    check = element_in(bonus, b'ShowLocked_Checkbox')
    for row in range(ROW_SLOTS):
        y = ROW_TOP + row * ROW_STEP
        out.append(quad(menu, b'BonusButtonGlow_Quad', b'TF_AO_Glow%d' % row, (209, y - 2, 407, ROW_HEIGHT + 4), None))
        out.append(quad(menu, b'Jurassic_Button_1', b'TF_AO_Row%d' % row, (209, y - 2, 407, ROW_HEIGHT + 4), None))
        box = copy.deepcopy(check)
        set_header(box, b'ShowLocked_Checkbox', b'TF_AO_Check%d' % row, fit(221, y + 21, 22, 22), hidden=True)
        out.append(box)
        for pack in PACK_LOGOS:
            out.append(quad(menu, b'Button_BG', b'TF_AO_Logo%d_%s' % (row, pack.encode()), (253, y + 5, 96, 54),
                            b'tf_ui_pack_logo_' + pack.lower().encode()))
        out.append(text(roots, SMALL_TEXT, b'TF_AO_Name%d' % row, (365, y + 8, 245, 22), b'NAME', BRIGHT, LEFT))
        out.append(text(roots, SMALL_TEXT, b'TF_AO_State%d' % row, (365, y + 31, 245, 20), b'STATE', GREEN, LEFT))
        out.append(text(roots, SMALL_TEXT, b'TF_AO_Warn%d' % row, (365, y + 31, 245, 20), b'STATE', AMBER, LEFT))
    out.append(text(roots, BIG_TEXT, b'TF_AO_DName', (660, 312, 410, 28), b'NAME', BRIGHT, CENTRE))
    for pack in PACK_LOGOS:
        out.append(quad(menu, b'Button_BG', b'TF_AO_DLogo_' + pack.encode(), (765, 364, 200, 64),
                        b'tf_ui_pack_logo_' + pack.lower().encode()))
    out += [text(roots, SMALL_TEXT, b'TF_AO_DDesc1', (680, 432, 380, 19), b'DESCRIPTION', GREEN, LEFT),
            text(roots, SMALL_TEXT, b'TF_AO_DDesc2', (680, 451, 380, 19), b'DESCRIPTION', GREEN, LEFT)]
    for line in range(DETAIL_LINES):
        y = 470 + line * 19
        out.append(text(roots, SMALL_TEXT, b'TF_AO_DLine%d' % line, (680, y, 380, 19), b'LINE', GREEN, LEFT))
        out.append(text(roots, SMALL_TEXT, b'TF_AO_DLineW%d' % line, (680, y, 380, 19), b'LINE', AMBER, LEFT))
    out += [text(roots, BIG_TEXT, b'TF_AO_Status', (690, 573, 350, 40), b'STATUS', BRIGHT, CENTRE),
            text(roots, BIG_TEXT, b'TF_AO_StatusW', (690, 573, 350, 40), b'STATUS', AMBER, CENTRE)]
    for i in range(BAR_SEGMENTS):
        out.append(quad(menu, b'Button_BG', b'TF_AO_Bar%d' % i, (BAR_LEFT + i * BAR_STEP, 622, 15, 9),
                        b'tf_ui_addons_bar'))
    return out


def main(src, bonus_src, menu_src, out):
    base, roots = load(src)
    _, bonus = load(bonus_src)
    _, menu = load(menu_src)
    impl = next(c for c in roots[-1][1] if c[0] == 3)
    assert impl[1] == string_body(b'CNC_MissionSelect'), 'the CAMPAIGNS page no longer names CNC_MissionSelect'
    impl[1][:] = string_body(b'SplashScreen')
    for name in HIDE:
        element = element_in(roots, name)
        header = chain_to(element, name)[-1][1][0][1]
        header[micro(header, 0x09)[0]] = 1
    set_label(element_in(roots, b'UI_MissionSelect_Header_Text'), b'TIBERIAN FACTIONS ADD-ONS')
    for name, rect in ((b'Start_Button', GET_RECT), (b'StartButton_Text', GET_RECT)):
        set_header(element_in(roots, name), name, name, rect, hidden=False)
    set_label(element_in(roots, b'StartButton_Text'), b'APPLY AND RESTART')
    back = element_in(roots, b'Back_Button')
    nav = next(n for n in chain_to(next(r for r in roots if chain_to(r, b'Back_Button')), b'Back_Button')
               if isinstance(n[1], list) and back in n[1])
    undo = []
    for source, name in ((b'Back_Button', b'TF_AO_Undo'), (b'BackButton_Text', b'TF_AO_UndoText')):
        element = copy.deepcopy(element_in(roots, source))
        set_header(element, source, name, UNDO_RECT, hidden=True)
        undo.append(element)
    set_label(undo[1], b'UNDO CHANGES')
    group = chain_to(next(r for r in roots if chain_to(r, FORMAT_GROUP)), FORMAT_GROUP)[-2]
    fresh = last_id(roots)
    for widget in undo:
        fresh = renumber(widget, fresh)
        nav[1].append(widget)
    for widget in widgets(roots, bonus, menu):
        fresh = renumber(widget, fresh)
        group[1].append(widget)
    write_loose(base, roots, out)
    print('wrote', out)


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
