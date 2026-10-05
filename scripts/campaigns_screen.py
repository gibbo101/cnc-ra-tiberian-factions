#!/usr/bin/env python3
"""Build the CAMPAIGNS page screen (docs/campaigns-page.md): RA's Mission Select widgets moved into
the two-column layout in TD's look, with game banners over the tabs and a hidden COMING SOON label.

usage: campaigns_screen.py <stock RA_MISSIONSELECT.BUI> <stock TD UI_MISSIONSELECT.BUI> <out .BUI>
"""
import copy
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bui_tree import (load, headers, string_value, string_body, micro, chain_to, last_id,  # noqa: E402
                      swap_strings, write_loose)

TEX_W, TEX_H = 2123.0, 1531.0
CAMPAIGN_GROUP = (58, 188, 2004, 1188)
DESCRIPTION_GROUP = (1078, 540, 984, 820)
TAB_ROW = (100, 380, 1920, 92)
TAB_W, TAB_GAP, PAIR_GAP = 230, 12, 50
TAB_ORDER = [('Ally', 0), ('USSR', 1), ('Aftermath_Allied', 2), ('Aftermath_USSR', 3), ('Ant', 4), ('Custom', 6)]
BANNERS = [(b'TF_Banner_RA', b'RED ALERT', 0), (b'TF_Banner_TD', b'TIBERIAN DAWN', 2),
           (b'TF_Banner_TS', b'TIBERIAN SUN', 4)]
BANNER_Y, BANNER_H = 300, 66
COMING_SOON = (b'TF_Coming_Soon', b'COMING SOON', (81, 950, 938, 80))
TITLE = b'UI_CampaignSelect_Header_Text'

TD_ART = {
    b'Scanline_Sheen_Blue': b'Scanline_Sheen',
    b'Scanline_Sheen_Red': b'Scanline_Sheen',
    b'RA_Soviet_BonusItem_List': b'BonusItem_List',
    b'RA_Allied_BonusItem_List': b'BonusItem_List',
    b'RA_UI_ScrollBar_Border_Left': b'UI_BonusItem_ScrollBar_Border_Left',
    b'RA_UI_ScrollBar_Border_Mid': b'UI_BonusItem_ScrollBar_Border_Mid',
    b'RA_UI_ScrollBar_Border_Right': b'UI_BonusItem_ScrollBar_Border_Right',
    b'RA_UI_ScrollBar_Border_Allied_Left': b'UI_BonusItem_ScrollBar_Border_Left',
    b'RA_UI_ScrollBar_Border_Allied_Mid': b'UI_BonusItem_ScrollBar_Border_Mid',
    b'RA_UI_ScrollBar_Border_Allied_Right': b'UI_BonusItem_ScrollBar_Border_Right',
    b'RA_UI_ScrollBar_Slider': b'UI_BonusItem_ScrollBar_Slider',
    b'RA_UI_ScrollBar_Allied_Slider': b'UI_BonusItem_ScrollBar_Slider',
    b'RA_Search_BTN_Red': b'FlatGreenTextButton',
    b'RA_Option_Menu_TextButton': b'Option_Menu_TextButton',
    b'ra_ui_mainbtn_disabled': b'ui_missionselect_retangle_button_off',
    b'RA_UI_MainBTN': b'Option_Menu_Button',
    b'RA_Mission_Select_Aftermath_Button': b'Mission_Select_GDI_Button',
    b'RA_Mission_Select_CS_Button': b'Mission_Select_NOD_Button',
    b'ra_ui_missionselect_tabicon_aftermath_disabled': b'ui_missionselect_tabicon_gdi_disabled',
    b'ra_ui_missionselect_tabicon_cs_disabled': b'ui_missionselect_tabicon_nod_disabled',
    b'RA_Mission_Select_Allied_Button': b'Mission_Select_Covert_Button',
    b'RA_Mission_Select_Soviet_Button': b'Mission_Select_Controller_Button',
    b'RA_Mission_Select_Ant_Button': b'Mission_Select_Dino_Button',
    b'ra_ui_missionselect_tabicon_allied_disabled': b'ui_missionselect_tabicon_covertops_disabled',
    b'ra_ui_missionselect_tabicon_soviet_disabled': b'ui_missionselect_tabicon_controller_disabled',
    b'ra_ui_missionselect_tabicon_ant_disabled': b'ui_missionselect_tabicon_dino_disabled',
    b'RA_Mission_Select_Custom_Button': b'Mission_Select_Custom_Button',
    b'ra_ui_missionselect_tabicon_custom_pressed': b'ui_missionselect_tabicon_custom_disabled',
    b'24 Point Regular Outline Red': b'24 Point Regular Outline Green',
}
TD_TINT_FROM = {'UI_MissionBriefingHeader_Text_SOVIET': 'UI_MissionBriefingHeader_Text',
                'UI_MissionBriefingHeader_Text_ALLIED': 'UI_MissionBriefingHeader_Text'}


def widget(roots, name):
    found = headers(roots, name.encode())
    assert len(found) == 1, (name, len(found))
    return found[0][1][0][1]


def set_rect(roots, name, rect):
    w = widget(roots, name)
    at, size = micro(w, 0x02)
    assert size == 16
    struct.pack_into('<4f', w, at, *rect)


def set_hidden(roots, name, value):
    w = widget(roots, name)
    at, size = micro(w, 0x09)
    w[at] = value


def in_texture(px):
    x, y, w, h = px
    return (x / TEX_W, y / TEX_H, w / TEX_W, h / TEX_H)


def in_group(group, px):
    gx, gy, gw, gh = group
    x, y, w, h = px
    return ((x - gx) / gw, (y - gy) / gh, w / float(gw), h / float(gh))


def tab_x(slot):
    pair, member = divmod(slot, 2)
    width = 3 * (2 * TAB_W + TAB_GAP) + 3 * PAIR_GAP + TAB_W
    start = (TAB_ROW[2] - width) // 2
    return start + pair * (2 * TAB_W + TAB_GAP + PAIR_GAP) + member * (TAB_W + TAB_GAP)


def copy_text_colours(roots, td_roots):
    """Give every text widget TD's tint (micro-chunk 0x03) and outline colour (leaf 0x13)."""
    names = set()

    def collect(node):
        nid, body = node
        if isinstance(body, list):
            for c in body:
                if c[0] == 5 and not isinstance(c[1], list) and nid in (0, 0x0b):
                    v = string_value(c[1])
                    if v and (v.endswith(b'_Text') or v.decode() in TD_TINT_FROM):
                        names.add(v)
                collect(c)

    for r in roots:
        collect(r)
    for name in sorted(names):
        source = TD_TINT_FROM.get(name.decode(), name.decode()).encode()
        mine, theirs = headers(roots, name), headers(td_roots, source)
        if len(mine) != 1 or len(theirs) != 1:
            continue
        mw, tw = mine[0][1][0][1], theirs[0][1][0][1]
        ma, ms = micro(mw, 0x03)
        ta, ts = micro(tw, 0x03)
        if ms == ts == 16:
            mw[ma:ma + 16] = tw[ta:ta + 16]
        for mc in mine[0][1]:
            for tc in theirs[0][1]:
                if mc[0] == tc[0] == 0x13 and not isinstance(mc[1], list) and len(mc[1]) == len(tc[1]):
                    mc[1][:] = tc[1]


def add_label(roots, name, label, px, hidden):
    """Clone the campaign title text as a literal label `name` at `px` in the campaign group."""
    chain = next(c for c in (chain_to(r, TITLE) for r in roots) if c)
    entry, group = chain[-3], chain[-4]
    assert entry[0] == 1 and group[0] == 0
    fresh = last_id(roots) + 0x10000
    clone = copy.deepcopy(entry)
    header = chain_to(clone, TITLE)[-1]
    for c in header[1]:
        if c[0] == 5 and not isinstance(c[1], list):
            c[1][:] = string_body(name)
    w = header[1][0][1]
    at, size = micro(w, 0x01)
    struct.pack_into('<I', w, at, fresh)
    at, size = micro(w, 0x02)
    struct.pack_into('<4f', w, at, *in_group(CAMPAIGN_GROUP, px))
    if hidden:
        at, size = micro(w, 0x09)
        w[at] = 1
    labels = [c for c in clone[1][1][1] if c[0] == 1 and not isinstance(c[1], list)]
    assert len(labels) == 1
    labels[0][1][:] = string_body(label)
    group[1].append(clone)


def main(src, td_screen, out):
    base, roots = load(src)
    set_rect(roots, 'UI_CampaignSelect_Group', in_texture(CAMPAIGN_GROUP))
    set_rect(roots, TITLE.decode(), in_group(CAMPAIGN_GROUP, (58, 562, 986, 50)))
    set_rect(roots, 'UI_CampaignSelect_ButtonGroup', in_group(CAMPAIGN_GROUP, TAB_ROW))
    for name, slot in TAB_ORDER:
        rect = (tab_x(slot) / float(TAB_ROW[2]), 0.0, TAB_W / float(TAB_ROW[2]), 1.0)
        set_rect(roots, 'CampaignSelect_%s_Button' % name, rect)
        set_rect(roots, 'CampaignSelect_%s_Disabled' % name, rect)
    list_px = (91, 664, 915, 654)
    for name in ('MissionList_Box', 'MissionList_Box_SOVIET', 'MissionList_Box_ALLIED'):
        set_rect(roots, name, in_group(CAMPAIGN_GROUP, list_px))
    set_rect(roots, 'MissionList_SampleEntry', in_group(CAMPAIGN_GROUP, (107, 672, 854, 117)))
    set_rect(roots, 'CustomCampaignList_Group', in_group(CAMPAIGN_GROUP, (91, 650, 915, 672)))

    set_rect(roots, 'UI_MissionDescription_Group', in_texture(DESCRIPTION_GROUP))
    d = DESCRIPTION_GROUP
    set_rect(roots, 'UI_MissionName_Text', in_group(d, (1098, 562, 944, 50)))
    set_rect(roots, 'UI_MissionNumber_Text', in_group(d, (1098, 608, 944, 44)))
    for name in ('UI_MissionDescription_Map_Quad', 'UI_MissionMap_Quad'):
        set_hidden(roots, name, 1)
        set_rect(roots, name, (0.0, 0.0, 0.0, 0.0))
    for name in ('UI_MissionBriefingHeader_Text', 'UI_MissionBriefingHeader_Text_SOVIET',
                 'UI_MissionBriefingHeader_Text_ALLIED'):
        set_rect(roots, name, in_group(d, (1130, 688, 880, 56)))
    for name in ('UI_MissionBriefingDescription_List', 'UI_MissionBriefingDescription_List_SOVIET',
                 'UI_MissionBriefingDescription_List_ALLIED'):
        set_rect(roots, name, in_group(d, (1124, 748, 868, 330)))
    set_rect(roots, 'CinematicButtonGroup', in_group(d, (1175, 1152, 794, 92)))
    set_rect(roots, 'MissionDifficulty_Group', in_group(d, (1203, 1265, 853, 70)))
    set_rect(roots, 'MissionDifficulty_Slider', (0.0, 0.0, 0.860, 0.574))
    set_hidden(roots, 'CameraIcon_Quad', 0)

    _, td_roots = load(td_screen)
    copy_text_colours(roots, td_roots)
    for name, label, slot in BANNERS:
        add_label(roots, name, label, (TAB_ROW[0] + tab_x(slot), BANNER_Y, 2 * TAB_W + TAB_GAP, BANNER_H), False)
    counts = {}
    for r in roots:
        swap_strings(r, TD_ART, counts)
    missing = [k.decode() for k in TD_ART if k not in counts]
    assert not missing, 'stock screen changed, TD art names not found: %s' % missing
    add_label(roots, *COMING_SOON, True)
    write_loose(base, roots, out)
    print('wrote', out)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
