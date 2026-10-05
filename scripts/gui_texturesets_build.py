#!/usr/bin/env python3
"""Build the mod's GUITEXTURESETS.XML from the base copy, same-size.

Adds the texture set the main-menu buttons draw with. The stock menu buttons use
TacticalSidebarSellRepairButton, which the in-game sidebar's sell/repair buttons share, so the
menu gets its own set instead: steel button art (menu_art.py paints it into TD main-menu
button regions that only TD's own main menu draws), with the stock transparent edges. It also
adds the CAMPAIGNS page's own row sets, drawn from campaigns_row_art.py's loose textures.

The set's name is exactly as long as the stock one so RA_MAIN_MENU.BUI can name it in place.
Every CONFIG.MEG member must keep its exact byte size (docs/config-meg-mod-delivery.md), so
whole comment blocks are dropped from the end of the file to make room and the remainder is
padded with whitespace before the closing tag.

usage: gui_texturesets_build.py <base GUITEXTURESETS.XML> <out>
"""
import re
import sys
import xml.etree.ElementTree as ET

STOCK_SET = 'TacticalSidebarSellRepairButton'
MENU_SET = 'TF_MainMenuSteelButton_Textures'
EDGE = 'UI_Sidebar_SellRepairButton_On_Edge.tga'
NORMAL, HOVER, PRESSED = 'UI_Button_Main_06_Mid.tga', 'UI_Button_Main_07_Mid.tga', 'UI_Button_Main_Pressed_06_Mid.tga'

QUADS = (('Background', NORMAL), ('Mouse_Over', HOVER), ('Mouse_Down', PRESSED), ('Toggled_On', NORMAL))

# CAMPAIGNS page row sets: (set name, texture base); campaigns_rows.py names the sets.
ROW_SETS = [('TF_Mission_Select_ListElement_TSGDI', 'TF_UI_MissionSelect_ItemList_TSGDI')]


def menu_set():
    lines = [f'  <TextureSet GUIType="Text_Button" Name="{MENU_SET}">']
    for state, middle in QUADS:
        for side, tex in (('Left', EDGE), ('Middle', middle), ('Right', EDGE)):
            lines.append(f'    <Texture Quad="{state}_{side}"> {tex} </Texture>')
    lines += ['    <Float Value="Mouse_Over_Modifier"> 0.0 </Float>',
              '    <Float Value="Mouse_Down_Modifier"> 0.0 </Float>',
              '    <Float Value="Disabled_Button_Alpha"> 0.1 </Float>',
              '  </TextureSet>', '', '']
    return '\r\n'.join(lines).encode('ascii')


def row_sets():
    lines = []
    for name, texture in ROW_SETS:
        lines += [f'  <TextureSet GUIType="Icon_Button" Name="{name}">',
                  f'    <Texture Quad="Background"> {texture}_Off.tga </Texture>',
                  '    <Texture Quad="Clock"> Empty.tga </Texture>',
                  f'    <Texture Quad="Toggled_On"> {texture}_Selected.tga </Texture>',
                  '    <Texture Quad="Mouse_Over"> UI_MissionSelect_ItemList_Hover.tga </Texture>',
                  '    <Texture Quad="Mouse_Down"> Empty.tga </Texture>',
                  '    <Float Value="Disabled_Button_Alpha"> 0.0 </Float>',
                  '    <Float Value="Mouse_Over_Modifier"> 0.0 </Float>',
                  '    <Float Value="Mouse_Down_Modifier"> 0.0 </Float>',
                  '  </TextureSet>', '', '']
    return '\r\n'.join(lines).encode('ascii')


def main(base_path, out_path):
    assert len(MENU_SET) == len(STOCK_SET)
    base = open(base_path, 'rb').read()
    head = b'<TextureSets>\r\n'
    at = base.index(head) + len(head)
    text = base[:at] + menu_set() + row_sets() + base[at:]
    comments = list(re.finditer(rb'[ \t]*<!--.*?-->(\r\n)?', text, re.S))
    while len(text) > len(base):
        c = comments.pop()
        text = text[:c.start()] + text[c.end():]
    close = text.rindex(b'</TextureSets>')
    text = text[:close] + b' ' * (len(base) - len(text)) + text[close:]
    assert len(text) == len(base)
    root = ET.fromstring(text)
    for name in [MENU_SET] + [n for n, _ in ROW_SETS]:
        assert root.find(f"TextureSet[@Name='{name}']") is not None
    open(out_path, 'wb').write(text)
    print(f'wrote {out_path}: {len(text)} bytes (base {len(base)})')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
