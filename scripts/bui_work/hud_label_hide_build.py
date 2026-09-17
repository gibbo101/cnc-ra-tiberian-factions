#!/usr/bin/env python3
"""Hide the side label under the radar crest in RA's tactical HUD scene, same-size.

RA_TACTICAL_UI.BUI draws the picked country's name (Text_FactionSelected) under the sidebar
crest. Every faction now has its own crest, so the label is redundant (Luke, 2026-09-02). The
widget's tint alpha goes to 0; the payload keeps its length, is recompressed at zlib level 9 and
padded to the member's exact original size (docs/bui-front-end-modding.md, the same-size rule).
GDI/Nod load TD's scene instead (scripts/factions_build.py), which has no such label.

usage: hud_label_hide_build.py <base RA_TACTICAL_UI.BUI> <out RA_TACTICAL_UI.BUI>
"""
import struct
import sys
import zlib

WIDGET = b'Text_FactionSelected'


def main(base, out):
    d = open(base, 'rb').read()
    raw = bytearray(zlib.decompress(d[0x24:]))
    i = raw.find(WIDGET)
    assert i > 0, 'label widget not found'
    # A widget's rect/tint tags precede its `26 10` header and name; the tags after the name
    # belong to the NEXT widget (the Allied logo here).
    hdr = raw.rfind(b'\x26\x10', 0, i)
    t = raw.rfind(b'\x03\x10', 0, hdr)      # the label's tint tag: RGBA floats follow
    assert 0 < i - t < 200, 'tint tag not where expected'
    rgba = struct.unpack('<4f', raw[t + 2:t + 18])
    assert rgba[:3] == (1.0, 1.0, 1.0) and abs(rgba[3] - 0.5843) < 0.001, rgba
    raw[t + 14:t + 18] = struct.pack('<f', 0.0)
    comp = zlib.compress(bytes(raw), 9)
    body = d[:0x24] + comp
    assert len(body) <= len(d), 'recompressed payload outgrew the member'
    open(out, 'wb').write(body + b'\x00' * (len(d) - len(body)))
    print('label hidden; %d of %d bytes, %d pad' % (len(body), len(d), len(d) - len(body)))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
