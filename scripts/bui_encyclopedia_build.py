#!/usr/bin/env python3
"""Write the encyclopedia's screen and list row, Data/ART/GUI/RA/TF_ENCY.BUI and TF_ENC_ROW.BUI (docs/encyclopedia.md).

usage: bui_encyclopedia_build.py <loose RA_MISSIONSELECT.BUI> <loose RA_MISSIONSELECT_LISTENTRY.BUI>
                                 <RA_MAIN_MENU BUI> <out GUI/RA dir>

The screen is the CAMPAIGNS page run by ClientG's SplashScreen class, so the launcher layer (redalert/tf_launcher.cpp)
drives it: its faction tabs and banners stay, its mission list lists the open faction's entries in TF_ENC_ROW.BUI
rows, and the briefing side becomes the selected entry in one green box (TF_UI_ENC_STATS,
scripts/encyclopedia_art.py, over the page's briefing box and the slot under it): name, picture (TF_EN_Pic, set at
runtime), description lines, label and value pairs for the stats, a full-width line for what the entry needs, and
the GET TIBERIAN SUN HD ASSETS gate for a missing pack. The row is the mission row with a cameo, a name and a group
heading. Rects are pixels of a 1280x800 Deck screenshot of the screen. License: GPL v3.
"""
import copy
import os
import struct
import sys

from bui_addons_build import (BIG_TEXT, BRIGHT, CENTRE, GREEN, GREY, LEFT, SMALL_TEXT, fit, quad, text)
from bui_mainmenu_pack_notice import element_in, set_header, set_label
from bui_tree import chain_to, last_id, load, micro, renumber, replace_texture_set, string_body, string_value, \
    write_loose

FORMAT_GROUP = b'MissionSelectFormatGroup'
ROW_BUI = b'Art\\GUI\\RA\\TF_Enc_Row.bui'
STOCK_ROW_BUI = b'Art\\GUI\\RA\\RA_MissionSelect_ListEntry.bui'
HIDE = (b'CampaignSelect_Custom_Button', b'CampaignSelect_Custom_Disabled', b'CampaignSelect_Ally_Disabled',
        b'CampaignSelect_USSR_Disabled', b'CampaignSelect_Aftermath_Allied_Disabled',
        b'CampaignSelect_Aftermath_USSR_Disabled', b'CampaignSelect_Ant_Disabled', b'MissionList_Box_SOVIET',
        b'MissionList_Box_ALLIED', b'MissionList_SampleEntry', b'CustomCampaignList_Group', b'TF_Coming_Soon',
        b'UI_MissionDescription_Group', b'CinematicButtonGroup', b'MissionDifficulty_Group',
        b'BackButtonDisabled_Quad', b'StartButtonDisabled_Quad', b'Start_Button', b'StartButton_Text')
DESC_RIGHT, DESC_BELOW = 7, 3        # description lines beside and under the picture: DESC_* in tf_launcher.cpp
STAT_ROWS = 6                        # stats per column, two columns: STAT_SLOTS in tf_launcher.cpp
LIGHT = (0.55, 0.62, 0.55, 1)


def set_hidden(roots, name, hidden=True):
    element = element_in(roots, name)
    header = chain_to(element, name)[-1][1][0][1]
    header[micro(header, 0x09)[0]] = 1 if hidden else 0


def screen_widgets(roots, menu):
    """The detail side's added widgets, in draw order; ids not yet renumbered."""
    out = [quad(menu, b'Button_BG', b'TF_EN_Plate', (657, 355, 417, 311), b'tf_ui_enc_stats', hidden=False),
           text(roots, BIG_TEXT, b'TF_EN_Name', (660, 312, 410, 28), b'NAME', BRIGHT, CENTRE),
           quad(menu, b'Button_BG', b'TF_EN_Pic', (670, 366, 160, 120), None)]
    for line in range(DESC_RIGHT):
        out.append(text(roots, SMALL_TEXT, b'TF_EN_Desc%d' % line, (840, 367 + line * 17, 222, 17), b'LINE', GREEN,
                        LEFT))
    for line in range(DESC_BELOW):
        out.append(text(roots, SMALL_TEXT, b'TF_EN_Desc%d' % (DESC_RIGHT + line), (670, 490 + line * 17, 392, 17),
                        b'LINE', GREEN, LEFT))
    for stat in range(2 * STAT_ROWS):
        x = 674 if stat < STAT_ROWS else 870
        y = 564 + (stat % STAT_ROWS) * 16
        out.append(text(roots, SMALL_TEXT, b'TF_EN_SL%d' % stat, (x, y, 82, 16), b'LABEL', LIGHT, LEFT))
        out.append(text(roots, SMALL_TEXT, b'TF_EN_SV%d' % stat, (x + 82, y, 112, 16), b'VALUE', BRIGHT, LEFT))
    gate = copy.deepcopy(element_in(roots, b'Back_Button'))
    set_header(gate, b'Back_Button', b'TF_EN_Gate', fit(262, 470, 300, 36), hidden=True)
    out += [text(roots, SMALL_TEXT, b'TF_EN_GateNote', (217, 420, 391, 40), b'NOTE', GREEN, CENTRE),
            gate,
            text(roots, SMALL_TEXT, b'TF_EN_GateText', (262, 477, 300, 22), b'GET TIBERIAN SUN HD ASSETS', BRIGHT,
                 CENTRE),
            text(roots, SMALL_TEXT, b'TF_EN_NeedsL', (674, 545, 82, 17), b'NEEDS', LIGHT, LEFT),
            text(roots, SMALL_TEXT, b'TF_EN_Needs', (756, 545, 306, 17), b'BUILDINGS', BRIGHT, LEFT)]
    return out


def screen(src, menu_src, out):
    base, roots = load(src)
    _, menu = load(menu_src)
    impl = next(c for c in roots[-1][1] if c[0] == 3)
    assert impl[1] == string_body(b'CNC_MissionSelect'), 'the CAMPAIGNS page no longer names CNC_MissionSelect'
    impl[1][:] = string_body(b'SplashScreen')
    for name in HIDE:
        set_hidden(roots, name)
    set_label(element_in(roots, b'UI_MissionSelect_Header_Text'), b'FACTION ENCYCLOPEDIA')
    example = element_in(roots, b'MissionList_SampleEntry')
    paths = []

    def find_path(node):
        nid, body = node
        if isinstance(body, list):
            for c in body:
                find_path(c)
        elif string_value(body) == STOCK_ROW_BUI:
            paths.append(node)

    find_path(example)
    assert len(paths) == 1, 'the sample entry no longer names the mission row'
    paths[0][1][:] = string_body(ROW_BUI)
    group = chain_to(next(r for r in roots if chain_to(r, FORMAT_GROUP)), FORMAT_GROUP)[-2]
    fresh = last_id(roots)
    for widget in screen_widgets(roots, menu):
        fresh = renumber(widget, fresh)
        group[1].append(widget)
    write_loose(base, roots, out)
    print('wrote', out)


def row(src, out):
    base, roots = load(src)
    for name in (b'MissionFrameBG_Allied_Group', b'MissionFrameBG_NOD_Group', b'TF_Row_TSGDI',
                 b'MissionFrameBG_Soviet_Group', b'MissionNumber_Text', b'IncompleteText_Group',
                 b'DifficultyCompletionGroup', b'Directory_Group'):
        set_hidden(roots, name)
    set_hidden(roots, b'MissionFrameBG_GDI_Group', hidden=False)
    button = element_in(roots, b'MissionElementButton_GDI')
    assert replace_texture_set(chain_to(button, b'MissionElementButton_GDI')[-1][1][0][1],
                               b'Mission_Select_ListElement_GDI', b'Mission_Select_ListElement') == 1
    title = element_in(roots, b'MissionTitle_Text')
    heading = copy.deepcopy(title)
    set_header(title, b'MissionTitle_Text', b'MissionTitle_Text', (0.17, 0.25, 0.8, 0.55), hidden=False)
    set_header(heading, b'MissionTitle_Text', b'TF_Enc_Heading', (0.03, 0.25, 0.94, 0.55), hidden=True)
    cameo = copy.deepcopy(element_in(roots, b'DifficultyCompletionHard_Quad'))
    set_header(cameo, b'DifficultyCompletionHard_Quad', b'TF_Enc_Cameo', (0.045, 0.17, 0.102, 0.66), hidden=False)
    parent = next(n for n in chain_to(next(r for r in roots if chain_to(r, b'MissionTitle_Text')), b'MissionTitle_Text')
                  if isinstance(n[1], list) and title in n[1])
    fresh = last_id(roots)
    for widget in (cameo, heading):
        fresh = renumber(widget, fresh)
        parent[1].append(widget)
    write_loose(base, roots, out)
    print('wrote', out)


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)
    os.makedirs(sys.argv[4], exist_ok=True)
    screen(sys.argv[1], sys.argv[3], os.path.join(sys.argv[4], 'TF_ENCY.BUI'))
    row(sys.argv[2], os.path.join(sys.argv[4], 'TF_ENC_ROW.BUI'))
