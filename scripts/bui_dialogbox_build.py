#!/usr/bin/env python3
"""
Rebuild RA_DIALOGBOX_SOVIET.BUI, the confirmation box the main menu opens (Exit Game? and the
like), in the menu's look: Tiberian Dawn's green dialog frame, green text and divider, and the
menu's own steel buttons with green labels.

usage: bui_dialogbox_build.py <base.BUI> <out.BUI>

The payload is a ChunkFile tree (docs/bui-front-end-modding.md): node = [u32 id][u32 spec], a
container when spec's top bit is set (spec counts children), otherwise a leaf of spec bytes.
The texture-set names sit inside a widget's header leaf as micro-chunks [u8 id][u8 size][data];
string properties are whole leaves [u16 len][ascii]. Edits that change a string's length
rewrite its own prefixes and its leaf's size, and the tree is serialised again, so container
counts never change. The file keeps the base's byte size (the launcher crashes on any other):
the stream is recompressed at level 9 and zero-padded. The longer button names don't fit that
budget on their own, so the caption's placeholder sentence, which the launcher replaces with the
dialog's question whenever the box opens, is cut to its first clause.
"""
import struct
import sys
import zlib

HEADER = 0x24
MSB = 0x80000000

# Widget tints, edited in place before parsing: (offset of the 03 10 tag, stock RGBA, new RGBA).
# The green is Tiberian Dawn's own dialog's.
TINTS = ((2012, (0.804, 0.157, 0.157, 1.0), (0.0, 1.0, 0.0, 1.0)),       # caption text
         (2524, (0.804, 0.157, 0.157, 0.604), (0.0, 1.0, 0.0, 0.604)))   # divider line

FRAME_TEXTURES = [(b'RA_UI_Frame_Tooltip_Sidebar_' + q, b'UI_Frame_Tooltip_Sidebar_' + q)
                  for q in (b'M', b'TL', b'TM', b'TR', b'ML', b'BL', b'MR', b'BM', b'BR')]
PLACEHOLDER = (b'Dialog Box Statement or Choices Text - Needs to support text choices of remapping '
               b'the unit, structure and research build command hotkeys. These can be lengthy '
               b'sentences!')
STRING_LEAVES = FRAME_TEXTURES + [(b'20 Point Outline', b'20 Point Outline Green'),
                                  (PLACEHOLDER, b'Dialog Box Statement or Choices Text')]
TEXTURE_SETS = [(b'RA_Frame_Tooltip_Sidebar', b'Frame_Tooltip_Sidebar'),
                (b'RA_Search_BTN_Red', b'TF_MainMenuSteelButton_Textures')]
# How many times each name appears in the base; a different count means the base changed.
EXPECTED = {b'20 Point Outline': 3, b'RA_Search_BTN_Red': 3}


def parse(raw, pos=0):
    nid, spec = struct.unpack_from('<II', raw, pos)
    if spec & MSB:
        children, p = [], pos + 8
        for _ in range(spec & ~MSB):
            child, p = parse(raw, p)
            children.append(child)
        return [nid, children], p
    return [nid, bytearray(raw[pos + 8:pos + 8 + spec])], pos + 8 + spec


def parse_all(raw):
    roots, p = [], 0
    while p < len(raw):
        node, p = parse(raw, p)
        roots.append(node)
    assert p == len(raw), f'tree ends at {p}, payload is {len(raw)}'
    return roots


def serialise(node):
    nid, body = node
    if isinstance(body, list):
        return struct.pack('<II', nid, len(body) | MSB) + b''.join(serialise(c) for c in body)
    return struct.pack('<II', nid, len(body)) + bytes(body)


def leaves(node):
    if isinstance(node[1], list):
        for child in node[1]:
            yield from leaves(child)
    else:
        yield node


def string_value(body):
    if len(body) >= 2 and struct.unpack_from('<H', body)[0] == len(body) - 2:
        return bytes(body[2:])
    return None


def replace_texture_set(body, old, new):
    """Swap a micro-chunk [0x0f][size][u16 len][name]; returns how many were swapped."""
    chunk = bytes([0x0f, len(old) + 2]) + struct.pack('<H', len(old)) + old
    count = body.count(chunk)
    if count:
        body[:] = body.replace(chunk, bytes([0x0f, len(new) + 2]) + struct.pack('<H', len(new)) + new)
    return count


def main(base, out):
    d = open(base, 'rb').read()
    raw = bytearray(zlib.decompress(d[HEADER:]))
    for off, stock, new in TINTS:
        assert raw[off:off + 2] == b'\x03\x10', f'no tint tag at {off}'
        got = tuple(round(v, 3) for v in struct.unpack_from('<4f', raw, off + 2))
        assert got == stock, f'tint at {off} is {got}, expected {stock}'
        struct.pack_into('<4f', raw, off + 2, *new)

    roots = parse_all(raw)
    assert b''.join(serialise(r) for r in roots) == raw, 'tree does not round-trip'

    seen = {}
    for leaf in (lf for r in roots for lf in leaves(r)):
        body = leaf[1]
        value = string_value(body)
        for old, new in STRING_LEAVES:
            if value == old:
                leaf[1] = bytearray(struct.pack('<H', len(new)) + new)
                seen[old] = seen.get(old, 0) + 1
        for old, new in TEXTURE_SETS:
            n = replace_texture_set(body, old, new)
            if n:
                seen[old] = seen.get(old, 0) + n
    for old, _ in STRING_LEAVES + TEXTURE_SETS:
        want = EXPECTED.get(old, 1)
        assert seen.get(old, 0) == want, f'{old!r} found {seen.get(old, 0)} times, expected {want}'

    edited = b''.join(serialise(r) for r in roots)
    parse_all(edited)
    comp = zlib.compress(edited, 9)
    hdr = bytearray(d[:HEADER])
    struct.pack_into('<I', hdr, 0x10, len(comp))
    body = bytes(hdr) + comp
    pad = len(d) - len(body)
    assert pad >= 0, f'edited BUI larger than the base ({len(body)} > {len(d)}); cannot pad'
    open(out, 'wb').write(body + b'\x00' * pad)
    print(f'wrote {out}: {len(d)} bytes (payload {len(raw)} -> {len(edited)}, pad {pad})')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
