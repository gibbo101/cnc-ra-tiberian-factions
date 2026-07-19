#!/usr/bin/env python3
'''
Reader for the UNENCRYPTED "alternate header" RA MIX flavour — the third
format in the family, sitting between the two archives our other tools handle:

    mix_tools.py       classic Westwood header (count first, no flag word)
    mix_plain_alt.py   4-byte alt header, encryption bit CLEAR  <-- this file
    ra_mix_extract.py  4-byte alt header, encryption bit SET (PK + Blowfish)

The Remastered Collection ships the RA campaign archives in this flavour:
`Data/CNCDATA/RED_ALERT/<CD1|AFTERMATH|COUNTERSTRIKE>/MAIN.MIX` holds a
nested `general.mix`, and the campaign scenario INIs (`scg43ea.ini` and
friends) live inside that. Neither sibling tool can open them — the classic
reader mis-parses the header as a count, and the encrypted reader rejects a
clear encryption bit — so scenario extraction needs this one.

Layout (mirrors common/mixfile.h):
    u16 first    always 0 (distinguishes alt header from classic)
    u16 flags    bit 0x01 = checksummed, bit 0x02 = encrypted
    u16 count    number of SubBlock entries
    u32 datasize total size of the file data region
    count * { i32 crc, u32 offset, u32 size }
    file data, offsets relative to the end of the index

Filename hashing is the shared Westwood CRC (mix_tools.ww_crc).

Usage:
  mix_plain_alt.py list    <mix>
  mix_plain_alt.py extract <mix> <filename> <outdir>

Nested archives extract like any other member, then read directly:
  mix_plain_alt.py extract .../AFTERMATH/MAIN.MIX general.mix /tmp
  mix_plain_alt.py extract /tmp/general.mix scg43ea.ini /tmp

License: GPL v3 (inherited from Vanilla Conquer base).
'''
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mix_tools import ww_crc

try:
    from mix_namedb import resolve as resolve_crc
except ImportError:
    resolve_crc = None

FLAG_ENCRYPTED = 0x02


def parse(path):
    '''Return ([(crc, offset, size)], data_base_offset) for a plain alt-header mix.'''
    with open(path, 'rb') as f:
        first, flags = struct.unpack('<HH', f.read(4))
        if first != 0:
            raise SystemExit(
                f'{path}: not an alt-header mix (first={first}) — try mix_tools.py')
        if flags & FLAG_ENCRYPTED:
            raise SystemExit(
                f'{path}: encrypted mix — use ra_mix_extract.py')
        count, _datasize = struct.unpack('<HI', f.read(6))
        entries = [struct.unpack('<iII', f.read(12)) for _ in range(count)]
        entries = [(crc & 0xFFFFFFFF, off, size) for crc, off, size in entries]
        return entries, f.tell()


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__.strip())
    cmd, path = sys.argv[1], sys.argv[2]
    entries, base = parse(path)

    if cmd == 'list':
        for crc, off, size in sorted(entries, key=lambda e: e[1]):
            name = resolve_crc(crc) if resolve_crc else None
            print(f'  crc=0x{crc:08x} off={off:>12} size={size:>12}  '
                  f'{name or "(unknown)"}')
        print(f'  -- {len(entries)} entries, data base offset {base}')

    elif cmd == 'extract':
        if len(sys.argv) < 5:
            raise SystemExit(__doc__.strip())
        name, outdir = sys.argv[3], sys.argv[4]
        target = ww_crc(name) & 0xFFFFFFFF
        for crc, off, size in entries:
            if crc == target:
                with open(path, 'rb') as f:
                    f.seek(base + off)
                    data = f.read(size)
                os.makedirs(outdir, exist_ok=True)
                out = os.path.join(outdir, name)
                with open(out, 'wb') as f:
                    f.write(data)
                print(f'extracted {name} ({size} bytes) -> {out}')
                return
        raise SystemExit(f'no entry matching CRC of "{name}" (0x{target:08x})')

    else:
        raise SystemExit(__doc__.strip())


if __name__ == '__main__':
    main()
