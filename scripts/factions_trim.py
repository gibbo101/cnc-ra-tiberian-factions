#!/usr/bin/env python3
"""Trim the lobby faction picker to one entry per faction, same-size.

The mod's FACTIONS.XML (in the shipped CONFIG.MEG) lists ten ObjectTypeClass entries; the RA
launcher populates the picker from them. Four are redundant country variants that read as
"Allies"/"Soviet" duplicates. This wraps those entries in XML comments so the launcher never sees
them, and keeps the member byte-for-byte the same length (CONFIG.MEG members must not change
size: offsets resolve against the base archive) by trimming an equal number of whitespace bytes
from the padding inside the commented blocks.

usage: factions_trim.py <base FACTIONS.XML> <out FACTIONS.XML> [Faction6 Faction7 ...]
"""
import re
import sys

DEFAULT_DROP = ['Faction6', 'Faction7', 'Faction8', 'Faction9']  # England, Ukraine, Germany, France


def main(base, out, drop):
    data = open(base, 'rb').read()
    size = len(data)
    for name in drop:
        m = re.search(rb'\t<ObjectTypeClass Name="%s".*?</ObjectTypeClass>\r?\n' % name.encode(), data, re.S)
        if not m:
            sys.exit('entry not found: ' + name)
        block = m.group(0)
        # Neutralise any comment markers inside the block (same length) so the outer comment
        # spans the whole entry; the launcher only sees one big comment.
        inner = block.replace(b'<!--', b'<!  ').replace(b'-->', b'  >').replace(b'--', b'- ')
        wrapped = b'<!--' + inner + b'-->'
        # give back the 7 added bytes from the block's own indentation tabs
        extra = len(wrapped) - len(block)
        stripped = wrapped.replace(b'\t\t\t\t', b'\t\t\t', extra)
        if len(stripped) != len(block):
            sys.exit('could not keep size for ' + name)
        data = data[:m.start()] + stripped + data[m.end():]
    assert len(data) == size, (len(data), size)
    open(out, 'wb').write(data)
    print('%s: %d bytes, dropped %s' % (out, len(data), ', '.join(drop)))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3:] or DEFAULT_DROP)
