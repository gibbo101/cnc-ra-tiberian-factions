#!/usr/bin/env python3
"""Print a .BUI's widget tree: depth, name, rect, hidden flag, texture set and the node ids
around each widget header, to plan a screen rebuild from stock widgets.

usage: bui_dump.py <in.BUI>
"""
import struct
import sys

from bui_tree import load, string_value  # noqa: E402


def micros(widget):
    out, p = {}, 0
    while p + 2 <= len(widget):
        i, s = widget[p], widget[p + 1]
        out.setdefault(i, bytes(widget[p + 2:p + 2 + s]))
        p += 2 + s
    return out


def describe(header):
    body = header[1]
    name = next((string_value(c[1]) for c in body if c[0] == 5 and not isinstance(c[1], list)), b'?')
    widget = body[0][1] if not isinstance(body[0][1], list) else b''
    m = micros(widget)
    rect = struct.unpack('<4f', m[2]) if len(m.get(2, b'')) == 16 else None
    hidden = m.get(9, b'\x00')[0] if 9 in m else None
    tex = m.get(0x0f, b'')[2:].decode('latin1') if 0x0f in m else ''
    return name.decode('latin1'), rect, hidden, tex


def walk(node, path, depth, out):
    nid, body = node
    if not isinstance(body, list):
        return
    is_header = nid in (0, 0x0b) and any(c[0] == 5 and not isinstance(c[1], list) for c in body)
    if is_header:
        name, rect, hidden, tex = describe(node)
        r = '(%.3f %.3f %.3f %.3f)' % rect if rect else '-'
        leaf_ids = ','.join('%x' % c[0] for c in body if not isinstance(c[1], list))
        out.append('%s%-34s %-30s hid=%s tex=%s  path=%s leaves=%s' % (
            '  ' * depth, name, r, hidden, tex or '-', '/'.join('%x' % p for p in path[-3:]), leaf_ids))
        depth += 1
    for child in body:
        walk(child, path + [nid], depth, out)


def main(src):
    _, roots = load(src)
    out = []
    for r in roots:
        walk(r, [], 0, out)
    print('\n'.join(out))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1])
