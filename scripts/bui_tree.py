"""Read, edit and rewrite the launcher's .BUI screen files as chunk trees.

A .BUI is a 0x24-byte CH header and a zlib stream holding a ChunkFile tree
(docs/bui-front-end-modding.md): node = [u32 id][u32 spec], a container when spec's top bit is
set (spec counts children), otherwise a leaf of spec bytes. Nodes parse to [id, children] or
[id, bytearray]. Texture-set names sit inside a widget's header leaf as micro-chunks
[u8 id][u8 size][data]; string properties are whole leaves [u16 len][ascii]. A string may change
length: its leaf is rewritten and the tree serialised again, so container counts never change.
A .BUI packed in CONFIG.MEG must keep the base's byte size (the launcher crashes on any other), so
the stream is recompressed at level 9 and zero-padded; a loose one in the mod's Data may be any size.
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


def write_loose(base_bytes, roots, out):
    """Write the edited tree as a loose .BUI of any size (loose files are not size-locked)."""
    edited = b''.join(serialise(r) for r in roots)
    parse_all(edited)
    comp = zlib.compress(edited, 9)
    hdr = bytearray(base_bytes[:HEADER])
    struct.pack_into('<I', hdr, 0x10, len(comp))
    open(out, 'wb').write(bytes(hdr) + comp)


def micro(widget, tag):
    """Offset and size of a header leaf's micro-chunk `tag`."""
    p = 0
    while p + 2 <= len(widget):
        i, s = widget[p], widget[p + 1]
        if i == tag:
            return p + 2, s
        p += 2 + s
    raise KeyError(tag)


def chain_to(node, name, chain=()):
    """The nodes from `node` down to the widget header named `name`, or None."""
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


def instance_ids(node, out):
    """Every widget instance id (header micro-chunk 0x01) under `node`, appended to `out`."""
    nid, body = node
    if isinstance(body, list):
        if nid in (0, 0x0b) and body and body[0][0] == 0 and not isinstance(body[0][1], list):
            w = body[0][1]
            if len(w) >= 6 and w[0] == 1 and w[1] == 4:
                out.append(struct.unpack_from('<I', w, 2)[0])
        for c in body:
            instance_ids(c, out)
    return out


def renumber(node, fresh):
    """Give every widget under a cloned `node` a new instance id after `fresh`; returns the last."""
    nid, body = node
    if not isinstance(body, list):
        return fresh
    if nid in (0, 0x0b) and body and body[0][0] == 0 and not isinstance(body[0][1], list):
        w = body[0][1]
        if len(w) >= 6 and w[0] == 1 and w[1] == 4:
            fresh += 0x10000
            struct.pack_into('<I', w, 2, fresh)
    for c in body:
        fresh = renumber(c, fresh)
    return fresh


def replace_named_micro(body, old, new):
    """Swap a name micro-chunk [tag][size][u16 len][name] of any tag (texture sets are 0x0f,
    effects 0x17); returns how many were swapped."""
    needle = bytes([len(old) + 2]) + struct.pack('<H', len(old)) + old
    count, at = 0, body.find(needle)
    while at > 0:
        body[at:at + len(needle)] = bytes([len(new) + 2]) + struct.pack('<H', len(new)) + new
        count += 1
        at = body.find(needle, at + 1)
    return count


def swap_strings(node, mapping, counts):
    """Rename name micro-chunks and string leaves found in `mapping`, counting each swap."""
    nid, body = node
    if isinstance(body, list):
        for child in body:
            swap_strings(child, mapping, counts)
        return
    for old, new in mapping.items():
        n = replace_named_micro(body, old, new)
        if n:
            counts[old] = counts.get(old, 0) + n
    if len(body) >= 2 and len(body) == 2 + int.from_bytes(body[:2], 'little'):
        value = string_value(body)
        if value in mapping:
            body[:] = string_body(mapping[value])
            counts[value] = counts.get(value, 0) + 1


def rename_widget(node, old, new):
    """Rename every widget header named `old` under `node`; returns how many."""
    nid, body = node
    if not isinstance(body, list):
        return 0
    count = 0
    for c in body:
        if c[0] == 5 and not isinstance(c[1], list) and string_value(c[1]) == old:
            c[1][:] = string_body(new)
            count += 1
        count += rename_widget(c, old, new)
    return count
