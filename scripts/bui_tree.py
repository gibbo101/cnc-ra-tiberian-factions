"""Read, edit and rewrite the launcher's .BUI screen files as chunk trees, at their fixed size.

A .BUI is a 0x24-byte CH header and a zlib stream holding a ChunkFile tree
(docs/bui-front-end-modding.md): node = [u32 id][u32 spec], a container when spec's top bit is
set (spec counts children), otherwise a leaf of spec bytes. Nodes parse to [id, children] or
[id, bytearray]. Texture-set names sit inside a widget's header leaf as micro-chunks
[u8 id][u8 size][data]; string properties are whole leaves [u16 len][ascii]. A string may change
length: its leaf is rewritten and the tree serialised again, so container counts never change.
The file must keep the base's byte size (the launcher crashes on any other), so the stream is
recompressed at level 9 and zero-padded.
"""
import struct
import zlib

HEADER = 0x24
MSB = 0x80000000


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


def string_body(value):
    return bytearray(struct.pack('<H', len(value)) + value)


def find_headers(node, name):
    """The widget header containers (id 0 or 0x0b) whose name leaf is `name`, in file order."""
    nid, body = node
    if not isinstance(body, list):
        return []
    if nid in (0, 0x0b) and any(c[0] == 5 and not isinstance(c[1], list) and string_value(c[1]) == name
                                for c in body):
        return [node]
    return [h for child in body for h in find_headers(child, name)]


def headers(roots, name):
    return [h for r in roots for h in find_headers(r, name)]


def replace_texture_set(body, old, new):
    """Swap a micro-chunk [0x0f][size][u16 len][name]; returns how many were swapped."""
    chunk = bytes([0x0f, len(old) + 2]) + struct.pack('<H', len(old)) + old
    count = body.count(chunk)
    if count:
        body[:] = body.replace(chunk, bytes([0x0f, len(new) + 2]) + struct.pack('<H', len(new)) + new)
    return count


def micro_floats(header, tag):
    """The four floats of a header leaf's micro-chunk `tag` (02 10 rect, 03 10 tint), and their offset."""
    widget = header[1][0][1]
    at = widget.find(bytes([tag, 0x10]))
    assert at >= 0, f'no {tag:#x} micro-chunk'
    return widget, at + 2


def load(path):
    d = open(path, 'rb').read()
    return d, parse_all(zlib.decompress(d[HEADER:]))


def write_same_size(base_bytes, roots, out):
    """Write the edited tree as a .BUI the size of the base; returns the zero padding used."""
    edited = b''.join(serialise(r) for r in roots)
    parse_all(edited)
    comp = zlib.compress(edited, 9)
    hdr = bytearray(base_bytes[:HEADER])
    struct.pack_into('<I', hdr, 0x10, len(comp))
    body = bytes(hdr) + comp
    pad = len(base_bytes) - len(body)
    assert pad >= 0, f'edited BUI larger than the base ({len(body)} > {len(base_bytes)}); cannot pad'
    open(out, 'wb').write(body + b'\x00' * pad)
    return pad
