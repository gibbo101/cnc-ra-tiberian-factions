#!/usr/bin/env python3
"""Probe: add a TF_Campaigns button to RA_MAIN_MENU.BUI, cloned from Mission Select, in row 10.

usage: menu_new_button.py <in.BUI> <out.BUI>
"""
import copy
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from bui_tree import load, string_body, string_value, write_same_size  # noqa: E402

SOURCE, NAME, LABEL = b'Button_Mission_Select', b'TF_Campaigns', b'CAMPAIGNS'
ROW_Y = 0.8951


def chain_to(node, name, chain=()):
    """The node chain from `node` down to the widget header whose name leaf is `name`."""
    nid, body = node
    if not isinstance(body, list):
        return None
    if any(c[0] == 5 and not isinstance(c[1], list) and string_value(c[1]) == name for c in body):
        return chain + (node,)
    for c in body:
        found = chain_to(c, name, chain + (node,))
        if found:
            return found
    return None


def micro(widget, tag):
    p = 0
    while p + 2 <= len(widget):
        i, s = widget[p], widget[p + 1]
        if i == tag:
            return p + 2, s
        p += 2 + s
    raise KeyError(f'no micro-chunk {tag:#x}')


def instance_ids(node, out):
    nid, body = node
    if isinstance(body, list):
        if nid in (0, 0x0b) and body and body[0][0] == 0 and not isinstance(body[0][1], list):
            w = body[0][1]
            if len(w) >= 6 and w[0] == 1 and w[1] == 4:
                out.append(struct.unpack_from('<I', w, 2)[0])
        for c in body:
            instance_ids(c, out)
    return out


def main(src, out):
    d, roots = load(src)
    chain = next(c for c in (chain_to(r, SOURCE) for r in roots) if c)
    element, parent = chain[-4], chain[-5]
    assert element[0] == 1 and parent[1].count(element) >= 1
    clone = copy.deepcopy(element)
    header = chain_to(clone, SOURCE)[-1]
    for c in header[1]:
        if c[0] == 5 and not isinstance(c[1], list):
            c[1][:] = string_body(NAME)
    widget = header[1][0][1]
    fresh = max(v for r in roots for v in instance_ids(r, []) if v < 0x3F000000) + 0x10000
    at, size = micro(widget, 0x01)
    assert size == 4
    struct.pack_into('<I', widget, at, fresh)
    at, size = micro(widget, 0x02)
    assert size == 16
    struct.pack_into('<f', widget, at + 4, ROW_Y)
    labels = [c for c in clone[1][1][1] if c[0] == 1 and not isinstance(c[1], list)]
    assert len(labels) == 1 and string_value(labels[0][1]) == b'TEXT_MISSION_LIST'
    labels[0][1][:] = string_body(LABEL)
    parent[1].append(clone)
    pad = write_same_size(d, roots, out)
    print(f'wrote {out}: {len(d)} bytes, pad {pad}, id {fresh:#x}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
