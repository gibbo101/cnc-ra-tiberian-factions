#!/usr/bin/env python3
"""Build the mod's FACTIONS.XML (lobby faction picker) from the base copy, same-size.

The RA launcher populates the picker from the ObjectTypeClass entries in FACTIONS.XML (in the
shipped CONFIG.MEG). Three edits, all byte-length-neutral because CONFIG.MEG members must not
change size (offsets resolve against the base archive):

  * ORDER: the visible entries are re-sequenced in document order to GDI, Nod, Allies, Soviet,
    then the four country duplicates. (Entry blocks are moved whole; the launcher's country id
    for each entry is untouched.)
  * ICONS: GDI (Faction3) and Nod (Faction10) point at the full-size 150x80 plates that used to
    hold the Spain and Turkey flags (_03 / _10) instead of the 66x56 _00 / _01 icons, so all
    picker entries share one size. scripts/picker_emblems_paint.py paints those plates.
  * HIDE (optional, off by default): entries named on the command line are wrapped in XML
    comments; the launcher keeps a blank, still-selectable row for each, which is why it is off.

usage: factions_build.py <base FACTIONS.XML> <out FACTIONS.XML> [--hide Faction6 ...]
"""
import re
import sys

ORDER = ['Faction1', 'Faction2', 'Faction3', 'Faction10', 'Faction4', 'Faction5',
         'Faction6', 'Faction7', 'Faction8', 'Faction9']
ICONS = {'Faction3': '03', 'Faction10': '10'}


def blocks_of(data):
    out = {}
    for m in re.finditer(rb'\t<ObjectTypeClass Name="(Faction\d+)".*?</ObjectTypeClass>\r?\n', data, re.S):
        out[m.group(1).decode()] = (m.start(), m.end(), m.group(0))
    return out


def main(base, out, hide):
    data = open(base, 'rb').read()
    size = len(data)
    blocks = blocks_of(data)
    missing = [n for n in ORDER if n not in blocks]
    if missing:
        sys.exit('entries not found: %s' % missing)
    # Keep the text between entries (comments/whitespace) in its original slots so only the
    # entry blocks move.
    orig = sorted(blocks.values(), key=lambda b: b[0])
    first, last = orig[0][0], orig[-1][1]
    head, tail = data[:first], data[last:]
    gaps = [data[orig[i][1]:orig[i + 1][0]] for i in range(len(orig) - 1)] + [b'']
    parts = []
    for slot, name in enumerate(ORDER):
        block = blocks[name][2]
        if name in ICONS:
            old = re.search(rb'<SmallIconName>UI_Multiplayer_PlayerSlot_Faction_(\d\d)\.tga</SmallIconName>', block)
            new = b'<SmallIconName>UI_Multiplayer_PlayerSlot_Faction_' + ICONS[name].encode() + b'.tga</SmallIconName>'
            assert old and len(new) == len(old.group(0))
            block = block[:old.start()] + new + block[old.end():]
        if name in hide:
            inner = block.replace(b'<!--', b'<!  ').replace(b'-->', b'  >').replace(b'--', b'- ')
            wrapped = b'<!--' + inner + b'-->'
            extra = len(wrapped) - len(block)
            block2 = wrapped.replace(b'\t\t\t\t', b'\t\t\t', extra)
            assert len(block2) == len(block), name
            block = block2
        parts.append(block + gaps[slot])
    data = head + b''.join(parts) + tail
    assert len(data) == size, (len(data), size)
    open(out, 'wb').write(data)
    print('%s: %d bytes, order %s, hidden %s' % (out, len(data), ' '.join(ORDER[2:]), hide or 'none'))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    args = sys.argv[3:]
    hide = args[args.index('--hide') + 1:] if '--hide' in args else []
    main(sys.argv[1], sys.argv[2], hide)
