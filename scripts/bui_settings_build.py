#!/usr/bin/env python3
"""Write the Settings page, Data/ART/GUI/RA/TF_SETTINGS.BUI, from the CAMPAIGNS page's frame; the layout is in
docs/player-settings.md. License: GPL v3.

usage: bui_settings_build.py <loose RA_MISSIONSELECT.BUI> <UI_BONUSCONTENT base BUI> <RA_MAIN_MENU BUI> <out BUI>
"""
import copy
import sys

from bui_addons_build import (AMBER, BIG_TEXT, BRIGHT, CENTRE, GET_RECT, GREEN, GREY, LEFT, SMALL_TEXT, fit, quad,
                              text)
from bui_encyclopedia_build import set_hidden
from bui_mainmenu_pack_notice import element_in, set_header, set_label
from bui_tree import chain_to, last_id, load, renumber, string_body, write_loose

FORMAT_GROUP = b'MissionSelectFormatGroup'
HIDE = (b'CampaignSelect_Custom_Button', b'CampaignSelect_Custom_Disabled', b'CampaignSelect_Ally_Disabled',
        b'CampaignSelect_USSR_Disabled', b'CampaignSelect_Aftermath_Allied_Disabled',
        b'CampaignSelect_Aftermath_USSR_Disabled', b'CampaignSelect_Ant_Disabled', b'UI_CampaignSelect_Header_Text',
        b'MissionList_Box', b'MissionList_Box_SOVIET', b'MissionList_Box_ALLIED', b'MissionList_SampleEntry',
        b'CustomCampaignList_Group', b'TF_Coming_Soon', b'UI_MissionDescription_Group', b'CinematicButtonGroup',
        b'MissionDifficulty_Group', b'BackButtonDisabled_Quad', b'StartButtonDisabled_Quad', b'TF_Banner_RA',
        b'TF_Banner_TD', b'TF_Banner_TS')
PAGES = (b'GENERAL', b'GAMEPLAY', b'GAME RULES')       # SETTINGS_PAGES in redalert/tf_launcher.cpp
CATEGORY_ROWS = 3                                  # SETTINGS_CATEGORIES in tf_launcher.cpp
PAGE_LEFT, PAGE_STEP, PAGE_WIDTH, PAGE_TOP, PAGE_HEIGHT = 222, 218, 200, 167, 30
MUSIC_ROWS = (b'MIX', b'RED ALERT', b'TIBERIAN DAWN', b'TIBERIAN SUN')   # MUSIC_CHOICES in tf_launcher.cpp
ROW_TOP, ROW_STEP, ROW_HEIGHT = 362, 74, 66
GET_ROW = 3
CHOICE_LEFT, CHOICE_STEP, CHOICE_WIDTH, CHOICE_HEIGHT = 905, 84, 76, 30


def choice_buttons(roots, menu, row, top):
    """A row's two choice buttons, indexed row * 2 + choice: a glow, the button, and grey and lit labels."""
    out = []
    for choice in range(2):
        index = row * 2 + choice
        x = CHOICE_LEFT + choice * CHOICE_STEP
        out.append(quad(menu, b'BonusButtonGlow_Quad', b'TF_ST_OptGlow%d' % index,
                        (x - 5, top - 4, CHOICE_WIDTH + 10, CHOICE_HEIGHT + 8), None))
        button = copy.deepcopy(element_in(roots, b'Back_Button'))
        set_header(button, b'Back_Button', b'TF_ST_Opt%d' % index, fit(x, top, CHOICE_WIDTH, CHOICE_HEIGHT),
                   hidden=True)
        out.append(button)
        out.append(text(roots, SMALL_TEXT, b'TF_ST_OptText%d' % index, (x, top + 5, CHOICE_WIDTH, 22), b'OFF', GREY,
                        CENTRE))
        out.append(text(roots, SMALL_TEXT, b'TF_ST_OptOn%d' % index, (x, top + 5, CHOICE_WIDTH, 22), b'ON', BRIGHT,
                        CENTRE))
    return out


def widgets(roots, bonus, menu):
    """The page's added widgets, in draw order; ids not yet renumbered."""
    out = []
    for page, label in enumerate(PAGES):
        x = PAGE_LEFT + page * PAGE_STEP
        out.append(quad(menu, b'BonusButtonGlow_Quad', b'TF_ST_PageGlow%d' % page,
                        (x - 6, PAGE_TOP - 5, PAGE_WIDTH + 12, PAGE_HEIGHT + 10), None))
        button = copy.deepcopy(element_in(roots, b'Back_Button'))
        set_header(button, b'Back_Button', b'TF_ST_Page%d' % page, fit(x, PAGE_TOP, PAGE_WIDTH, PAGE_HEIGHT),
                   hidden=False)
        out.append(button)
        out.append(text(roots, SMALL_TEXT, b'TF_ST_PageText%d' % page, (x, PAGE_TOP + 5, PAGE_WIDTH, 22), label, GREY,
                        CENTRE, hidden=False))
        out.append(text(roots, SMALL_TEXT, b'TF_ST_PageOn%d' % page, (x, PAGE_TOP + 5, PAGE_WIDTH, 22), label, BRIGHT,
                        CENTRE))
    out += [text(roots, BIG_TEXT, b'TF_ST_Soon', (207, 480, 411, 40), b'COMING SOON', BRIGHT, CENTRE)]
    for row in range(CATEGORY_ROWS):
        y = ROW_TOP + row * ROW_STEP
        out.append(quad(menu, b'BonusButtonGlow_Quad', b'TF_ST_CatGlow%d' % row, (214, y - 2, 397, ROW_HEIGHT + 4),
                        None))
        out.append(quad(menu, b'Jurassic_Button_1', b'TF_ST_Cat%d' % row, (214, y - 2, 397, ROW_HEIGHT + 4), None))
        out.append(text(roots, SMALL_TEXT, b'TF_ST_CatName%d' % row, (230, y + 9, 360, 22), b'NAME', BRIGHT, LEFT))
        out.append(text(roots, SMALL_TEXT, b'TF_ST_CatDesc%d' % row, (230, y + 34, 360, 20), b'ABOUT', GREEN, LEFT))
    out += [text(roots, BIG_TEXT, b'TF_ST_Music', (660, 312, 410, 28), b'MUSIC', BRIGHT, CENTRE),
            quad(menu, b'Button_BG', b'TF_ST_Plate', (657, 355, 417, 311), b'tf_ui_enc_stats')]
    check = element_in(bonus, b'ShowLocked_Checkbox')
    for row, label in enumerate(MUSIC_ROWS):
        y = ROW_TOP + row * ROW_STEP
        out.append(quad(menu, b'BonusButtonGlow_Quad', b'TF_ST_Glow%d' % row, (662, y - 2, 407, ROW_HEIGHT + 4), None))
        out.append(quad(menu, b'Jurassic_Button_1', b'TF_ST_Row%d' % row, (662, y - 2, 407, ROW_HEIGHT + 4), None))
        box = copy.deepcopy(check)
        set_header(box, b'ShowLocked_Checkbox', b'TF_ST_Check%d' % row, fit(674, y + 22, 22, 22), hidden=True)
        out.append(box)
        out.append(text(roots, SMALL_TEXT, b'TF_ST_Name%d' % row, (708, y + 9, 240, 22), label, BRIGHT, LEFT))
        out.append(text(roots, SMALL_TEXT, b'TF_ST_Desc%d' % row, (708, y + 34, 350, 20), b'ABOUT', GREEN, LEFT))
        out.append(text(roots, SMALL_TEXT, b'TF_ST_Warn%d' % row, (708, y + 34, 180, 20), b'NEEDS', AMBER, LEFT))
        out += choice_buttons(roots, menu, row, y + (ROW_HEIGHT - CHOICE_HEIGHT) // 2)
    y = ROW_TOP + CATEGORY_ROWS * ROW_STEP + 12
    out += [text(roots, SMALL_TEXT, b'TF_ST_Note0', (214, y, 397, 22), b'NOTE', GREEN, CENTRE),
            text(roots, SMALL_TEXT, b'TF_ST_Note1', (214, y + 24, 397, 22), b'NOTE', GREEN, CENTRE)]
    y = ROW_TOP + GET_ROW * ROW_STEP
    get = copy.deepcopy(element_in(roots, b'Back_Button'))
    set_header(get, b'Back_Button', b'TF_ST_Get', fit(900, y + 16, 160, 34), hidden=True)
    out += [get, text(roots, SMALL_TEXT, b'TF_ST_GetText', (900, y + 22, 160, 22), b'GET ADD-ON', AMBER, CENTRE)]
    return out


def main(src, bonus_src, menu_src, out):
    base, roots = load(src)
    _, bonus = load(bonus_src)
    _, menu = load(menu_src)
    impl = next(c for c in roots[-1][1] if c[0] == 3)
    assert impl[1] == string_body(b'CNC_MissionSelect'), 'the CAMPAIGNS page no longer names CNC_MissionSelect'
    impl[1][:] = string_body(b'SplashScreen')
    for name in HIDE:
        set_hidden(roots, name)
    set_label(element_in(roots, b'UI_MissionSelect_Header_Text'), b'TIBERIAN FACTIONS SETTINGS')
    for name, rect in ((b'Start_Button', GET_RECT), (b'StartButton_Text', GET_RECT)):
        set_header(element_in(roots, name), name, name, rect, hidden=False)
    set_label(element_in(roots, b'StartButton_Text'), b'DEFAULTS')
    group = chain_to(next(r for r in roots if chain_to(r, FORMAT_GROUP)), FORMAT_GROUP)[-2]
    fresh = last_id(roots)
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
