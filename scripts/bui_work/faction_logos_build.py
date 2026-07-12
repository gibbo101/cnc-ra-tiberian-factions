#!/usr/bin/env python3
"""
GOAL DEAD (2026-07-12) -- RETAINED AS THE .bui STRUCTURAL-INSERT REFERENCE.
A discriminator probe proved ClientG's compiled faction->logo mapping collapses
all RA countries to SideBar_FactionLogo_{Allies,Soviet}; the _GDI/_NOD widgets
this script inserts are structurally valid and render-safe but never queried in
RA mode. See docs/bui-front-end-modding.md "RESOLVED NEGATIVE". The parse/
rewrite/insert machinery below is the worked example for any future .bui
structural edit.

Build RA_TACTICAL_UI.BUI with per-faction HUD sidebar logos (GDI + Nod) and pack
it into a test CONFIG.MEG. See docs/bui-front-end-modding.md "Per-faction HUD
logos".

HOW IT WORKS (format cracked 2026-07-12)
  The .bui payload is a recursive chunk tree:  node = [u32 id][u32 spec];
  spec MSB set -> container holding (spec & 0x7fffffff) CHILD NODES (a count,
  not a byte size); MSB clear -> leaf with spec bytes of data. Leaf data is a
  micro-chunk stream ([u8 tag][u8 size], e.g. 02/10 rect, 03/10 tint) or a
  [u16 len]-prefixed string. Containers carry NO byte sizes, so inserting a
  complete element subtree needs exactly ONE structural fixup: +N on the direct
  parent's child count. (The 2026-07-11 attempt spliced raw bytes mid-node and
  updated nothing -- that is why the whole sidebar vanished.)

  Each sidebar widget is an element subtree shaped:
    C id=1 cnt=2
      L id=2 sz=6                      (type marker)
      C id=4 cnt=3
        C id=11 cnt=5                  (props: micro-stream, name, ...)
          L id=0 sz=99                 (rect/tint/etc micro-chunks)
          L id=5  "SideBar_FactionLogo_Allies"
          L id=19 / L id=20 / L id=39
        C id=1 cnt=2                   (texture ref block)
          L id=2  "ui_sidebar_factionlogo_allies"
          L id=3 sz=6
        L id=7 sz=15

  We copy the complete _Allies element, rewrite its name/texture string leaves
  (updating each leaf's u32 size and u16 length prefix), insert the GDI and Nod
  copies immediately after the _Soviet element, and bump their shared parent
  container's child count by 2. Everything is located by parsing, not by fixed
  offsets, and the edited payload is re-parsed as validation before packing.

WHY: ClientG picks the sidebar crest by widget name from the compiled
  FactionType enum -- it looks for SideBar_FactionLogo_{GDI,NOD,Allies,Soviet,
  DINO} but the base file only defines _Allies/_Soviet, so GDI/Nod fall back to
  the generic "COMMAND & CONQUER" wordmark. The real emblem art already ships
  in the mod's atlas (ui_sidebar_factionlogo_gdi / _nod).

USAGE
  python3 scripts/bui_work/faction_logos_build.py
    -> writes scripts/bui_work/CONFIG.4logos.MEG (gitignored, 44 MB)

DEPLOY (test): copy over the deployed mod's Data/CONFIG.MEG (Linux prefix or
  Deck). RECOVERY: redeploy the normal build (rsync build/remaster/Vanilla_RA/).
  The base install is never touched.
"""
import os, sys, zlib, struct, subprocess, shutil

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MOD_MEG = os.path.join(REPO, 'resources', 'remaster_mods', 'Vanilla_RA', 'Data', 'CONFIG.MEG')
EXTRACT = os.path.join(REPO, 'scripts', 'meg_extract.py')
PACK    = os.path.join(REPO, 'scripts', 'meg_pack.py')
WORK    = os.path.join(REPO, 'scripts', 'bui_work')
OUT_MEG = os.path.join(WORK, 'CONFIG.4logos.MEG')
MEMBER  = 'RA_TACTICAL_UI.BUI'

MSB = 0x80000000

# (new widget name, texture region) -- art already in the mod's in-game atlas
NEW_WIDGETS = [
    (b'SideBar_FactionLogo_GDI', b'ui_sidebar_factionlogo_gdi'),
    (b'SideBar_FactionLogo_NOD', b'ui_sidebar_factionlogo_nod'),
]


class Node:
    __slots__ = ('pos', 'id', 'kind', 'spec', 'end', 'parent', 'children')

    def __init__(self, pos, nid, kind, spec, parent):
        self.pos, self.id, self.kind, self.spec, self.parent = pos, nid, kind, spec, parent
        self.children = []


def parse_tree(raw):
    """Parse the chunk tree; raises on any structural inconsistency."""
    nodes = []

    def parse(pos, parent):
        nid, spec = struct.unpack_from('<II', raw, pos)
        if spec & MSB:
            node = Node(pos, nid, 'C', spec & ~MSB, parent)
            nodes.append(node)
            p = pos + 8
            for _ in range(node.spec):
                p = parse(p, node)
            node.end = p
        else:
            if pos + 8 + spec > len(raw):
                raise ValueError(f'leaf overrun @{pos}')
            node = Node(pos, nid, 'L', spec, parent)
            nodes.append(node)
            node.end = pos + 8 + spec
        if parent is not None:
            parent.children.append(node)
        return node.end

    p = 0
    roots = []
    while p < len(raw):
        n0 = len(nodes)
        p = parse(p, None)
        roots.append(nodes[n0])
    if p != len(raw):
        raise ValueError(f'consumed {p} != {len(raw)}')
    return nodes


def str_leaf(raw, node):
    """Decode a [u16 len][ascii] string leaf; returns bytes or None."""
    if node.kind != 'L' or node.spec < 2:
        return None
    ln = struct.unpack_from('<H', raw, node.pos + 8)[0]
    if ln != node.spec - 2:
        return None
    return raw[node.pos + 10:node.pos + 10 + ln]


def find_logo_element(raw, nodes, name):
    """Return the widget ELEMENT node (C id=1 cnt=2 ancestor) whose subtree
    holds the given widget-name string leaf."""
    for n in nodes:
        if str_leaf(raw, n) == name:
            el = n.parent            # C id=11 (props)
            el = el.parent           # C id=4  (body)
            el = el.parent           # C id=1  (element)
            assert el.kind == 'C' and el.id == 1 and el.spec == 2, \
                f'unexpected element shape for {name}'
            return el
    raise KeyError(name)


def rewrite_strings(blob, replacements):
    """Rewrite [u32 size][u16 len][ascii] string fields inside a copied element
    blob, adjusting both prefixes (leaf sizes change; the element's structure
    -- container COUNTS -- does not)."""
    out = bytearray(blob)
    for old, new in replacements:
        field = struct.pack('<I', len(old) + 2) + struct.pack('<H', len(old)) + old
        i = out.find(field)
        assert i >= 0, f'string field not found: {old}'
        assert out.find(field, i + 1) < 0, f'ambiguous string field: {old}'
        out[i:i + len(field)] = struct.pack('<I', len(new) + 2) + struct.pack('<H', len(new)) + new
    return bytes(out)


def main():
    tmp = os.path.join(WORK, '_4logos_tmp')
    os.makedirs(tmp, exist_ok=True)
    subprocess.run([sys.executable, EXTRACT, 'extract', MOD_MEG, MEMBER, tmp],
                   check=True, capture_output=True)
    src = next(os.path.join(r, f) for r, _, fs in os.walk(tmp) for f in fs
               if f.upper() == MEMBER)
    d = open(src, 'rb').read()
    ORIG, ORIGC = len(d), len(d) - 0x24
    raw = zlib.decompress(d[0x24:])

    nodes = parse_tree(raw)
    allies = find_logo_element(raw, nodes, b'SideBar_FactionLogo_Allies')
    soviet = find_logo_element(raw, nodes, b'SideBar_FactionLogo_Soviet')
    parent = allies.parent
    assert soviet.parent is parent, 'logo widgets have different parents'
    assert parent.kind == 'C'

    template = raw[allies.pos:allies.end]
    new_blobs = b''.join(
        rewrite_strings(template, [
            (b'SideBar_FactionLogo_Allies', name),
            (b'ui_sidebar_factionlogo_allies', tex),
        ])
        for name, tex in NEW_WIDGETS)

    ins = soviet.end
    newraw = bytearray(raw[:ins] + new_blobs + raw[ins:])
    # the single structural fixup: parent child count +2
    struct.pack_into('<I', newraw, parent.pos + 4, (parent.spec + 2) | MSB)
    newraw = bytes(newraw)

    # validate: full reparse + both new widgets present under the same parent
    nodes2 = parse_tree(newraw)
    for name, tex in NEW_WIDGETS:
        el = find_logo_element(newraw, nodes2, name)
        assert el.parent.pos == parent.pos, f'{name} not under expected parent'
        assert any(str_leaf(newraw, n) == tex
                   for n in nodes2 if n.pos >= el.pos and n.end <= el.end), \
            f'{name} texture ref missing'
    print(f'payload {len(raw)} -> {len(newraw)} (+{len(new_blobs)}); '
          f'parent @{parent.pos} count {parent.spec} -> {parent.spec + 2}; reparse OK')

    comp = zlib.compress(newraw, 9)
    assert len(comp) <= ORIGC, f'compressed overflow: {len(comp)} > {ORIGC}'
    hdr = bytearray(d[:0x24])
    struct.pack_into('<I', hdr, 0x10, len(comp))          # csize; [0x08] hash stays stale
    body = bytes(hdr) + comp
    edited = os.path.join(tmp, 'RA_TACTICAL_UI.4logos.BUI')
    open(edited, 'wb').write(body + b'\x00' * (ORIG - len(body)))  # pad to exact size

    shutil.copyfile(MOD_MEG, OUT_MEG)
    subprocess.run([sys.executable, PACK, 'repack', OUT_MEG, OUT_MEG + '.tmp',
                    f'{MEMBER}={edited}'], check=True, capture_output=True)
    os.replace(OUT_MEG + '.tmp', OUT_MEG)
    assert os.path.getsize(OUT_MEG) == os.path.getsize(MOD_MEG), 'MEG size drifted'
    shutil.rmtree(tmp, ignore_errors=True)
    print(f'wrote {OUT_MEG} (member {ORIG}B unchanged, comp {len(comp)}/{ORIGC})')


if __name__ == '__main__':
    main()
