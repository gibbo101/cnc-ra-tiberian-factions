#!/usr/bin/env python3
"""Build the CAMPAIGNS page's mission row (docs/campaigns-page.md): TD's GDI and Nod crest groups
beside RA's two, plus the mod's own crest groups, all hidden until the DLL shows one per mission.

usage: campaigns_rows.py <stock RA_MISSIONSELECT_LISTENTRY.BUI> <stock TD UI_MISSIONSELECT_LISTENTRY.BUI> <out .BUI>
"""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bui_tree import (load, headers, leaves, micro, chain_to, last_id, renumber, replace_named_micro,  # noqa: E402
                      rename_widget, swap_strings, write_loose)

STOCK_GROUPS = (b'MissionFrameBG_Allied_Group', b'MissionFrameBG_Soviet_Group',
                b'MissionFrameBG_GDI_Group', b'MissionFrameBG_NOD_Group')
TD_GROUPS = (b'MissionFrameBG_GDI_Group', b'MissionFrameBG_NOD_Group')
TD_ROW_ART = {
    b'RA_UI_CustomMapUpLevelTextButton': b'UI_CustomMapUpLevelTextButton',
    b'RA_UI_CustomMapTextButton': b'UI_CustomMapTextButton',
}

# Mod crest groups: (group, button, texture set), cloned from the GDI group. Names fit 15
# characters; the DLL's ExtraRowStyles table names them too.
SOURCE_GROUP = b'MissionFrameBG_GDI_Group'
SOURCE_BUTTON = b'MissionElementButton_GDI'
SOURCE_SET = b'Mission_Select_ListElement_GDI'
MOD_GROUPS = [(b'TF_Row_TSGDI', b'TF_Row_TSGDI_B', b'TF_Mission_Select_ListElement_TSGDI')]


def set_hidden(roots, name):
    found = headers(roots, name)
    assert len(found) == 1, name
    w = found[0][1][0][1]
    at, size = micro(w, 0x09)
    w[at] = 1


def main(src, td_row, out):
    base, roots = load(src)
    _, td_roots = load(td_row)
    anchor = next(c for c in (chain_to(r, b'MissionFrameBG_Allied_Group') for r in roots) if c)
    parent = anchor[-4]
    fresh = last_id(roots)
    for name in TD_GROUPS:
        chain = next(c for c in (chain_to(r, name) for r in td_roots) if c)
        clone = copy.deepcopy(chain[-3])
        fresh = renumber(clone, fresh)
        parent[1].append(clone)
    for name in STOCK_GROUPS:
        set_hidden(roots, name)
    counts = {}
    for r in roots:
        swap_strings(r, TD_ROW_ART, counts)
    assert set(counts) == set(TD_ROW_ART), 'stock row changed, TD art names not found'

    chain = next(c for c in (chain_to(r, SOURCE_GROUP) for r in roots) if c)
    entry, parent = chain[-3], chain[-4]
    fresh = last_id(roots)
    for group, button, texture_set in MOD_GROUPS:
        clone = copy.deepcopy(entry)
        assert rename_widget(clone, SOURCE_GROUP, group) == 1 and rename_widget(clone, SOURCE_BUTTON, button) == 1
        assert sum(replace_named_micro(leaf[1], SOURCE_SET, texture_set) for leaf in leaves(clone)) == 1
        fresh = renumber(clone, fresh)
        parent[1].append(clone)
    write_loose(base, roots, out)
    print('wrote', out)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
