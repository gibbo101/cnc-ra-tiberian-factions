#!/usr/bin/env python3
'''
Minimal reader/writer for the classic (pre-RA-encryption) Westwood C&C
MIX file format. Used by Tiberian Factions to extract TD SHPs from
CONQUER.MIX and pack them into a mod-side TFASSETS.MIX that ships
alongside our DLL — needed for classic-graphics-mode rendering of
fully-separated TD buildings (STRUCT_TDOBLI etc.).

Format reference: common/mixfile.h (FileHeader + SubBlock structs) and
common/crc.cpp (CRCEngine — the filename-hashing algorithm).

Filename hash (the SubBlock CRC field):
    - Uppercase the filename (ASCII).
    - Feed bytes through CRCEngine algorithm. The CRC accumulates:
      whenever a 4-byte staging buffer fills, CRC = lrotl(CRC, 1) +
      le32(staging). Partial trailing bytes are zero-padded inside the
      staging buffer and finalised with the same rotation logic.

Per-file SubBlock entries are sorted by signed CRC value (engine uses
binary search on the SubBlock array).

Usage:
  mix_tools.py extract <mixfile> <pattern> <outdir>
  mix_tools.py pack    <outmix> <file1>[:<rename>] [<file2>[:<rename>] ...]
  mix_tools.py list    <mixfile>

License: GPL v3 (inherited from Vanilla Conquer base).
'''
import os
import struct
import sys

try:
    from mix_namedb import resolve as resolve_name
except Exception:
    def resolve_name(crc, **kw):
        return None


def ww_crc(name: str) -> int:
    '''Compute the CRC32-ish hash Westwood uses for MIX file entries.

    Mirrors common/crc.cpp CRCEngine: byte stream into a 4-byte staging
    buffer; whenever filled, CRC = lrotl(CRC, 1) + le32(staging). Partial
    final buffer is zero-padded and folded in via the same rotation. The
    operator()(buffer, length) wrapper handles partial-buffer accounting
    via Index, but for a single contiguous string we can just process
    the whole thing.
    '''
    data = name.upper().encode('ascii')
    crc = 0
    index = 0
    staging = bytearray(4)
    for b in data:
        staging[index] = b
        index += 1
        if index == 4:
            staging_val = struct.unpack('<i', bytes(staging))[0]
            crc = lrotl32(crc, 1) + staging_val
            crc = ((crc + 0x80000000) & 0xFFFFFFFF) - 0x80000000
            staging = bytearray(4)
            index = 0
    if index != 0:
        # Final partial buffer with trailing zeros — mimics what the
        # CRCEngine returns when Value() is called with Index != 0.
        staging_val = struct.unpack('<i', bytes(staging))[0]
        crc = lrotl32(crc, 1) + staging_val
        crc = ((crc + 0x80000000) & 0xFFFFFFFF) - 0x80000000
    return crc


def lrotl32(value: int, shift: int) -> int:
    value &= 0xFFFFFFFF
    return ((value << shift) | (value >> (32 - shift))) & 0xFFFFFFFF


def read_mix(path: str):
    '''Return (count, datasize, [(crc, offset, size), ...], data_blob).

    Assumes the classic (TD-style) unencrypted format: 2-byte count,
    4-byte size, then count SubBlocks of 12 bytes each, then the raw
    data blob. CONQUER.MIX and other TD mix files use this layout.
    '''
    with open(path, 'rb') as f:
        header = f.read(6)
        count, data_size = struct.unpack('<HI', header)
        entries = []
        for _ in range(count):
            crc, offset, size = struct.unpack('<iII', f.read(12))
            entries.append((crc, offset, size))
        data_blob = f.read()
    return count, data_size, entries, data_blob


def cmd_list(args):
    if len(args) < 1:
        print('usage: mix_tools.py list <mixfile>', file=sys.stderr)
        return 2
    count, data_size, entries, data_blob = read_mix(args[0])
    print(f'{count} files, {data_size} bytes of data, {len(data_blob)} bytes blob')
    known = 0
    for crc, offset, size in entries:
        name = resolve_name(crc)
        if name:
            known += 1
        label = name if name else '(unknown)'
        print(f'  crc={crc & 0xFFFFFFFF:#010x} size={size:>9d}  {label}')
    print(f'  -- {known}/{count} names resolved', file=sys.stderr)
    return 0


def cmd_extract(args):
    if len(args) < 3:
        print('usage: mix_tools.py extract <mixfile> <filename> <outdir>', file=sys.stderr)
        print('       (filename is a literal name; we hash it and look up the CRC)', file=sys.stderr)
        return 2
    mixfile, filename, outdir = args[:3]
    count, data_size, entries, data_blob = read_mix(mixfile)
    target_crc = ww_crc(filename)
    for crc, offset, size in entries:
        if crc == target_crc:
            os.makedirs(outdir, exist_ok=True)
            outpath = os.path.join(outdir, filename)
            with open(outpath, 'wb') as f:
                f.write(data_blob[offset:offset + size])
            print(f'extracted {filename} ({size} bytes, crc={crc:#010x}) -> {outpath}')
            return 0
    print(f'no entry matching CRC of "{filename}" ({target_crc:#010x})', file=sys.stderr)
    return 1


def cmd_pack(args):
    if len(args) < 2:
        print('usage: mix_tools.py pack <outmix> <file>[:<rename>] [...]', file=sys.stderr)
        return 2
    outmix = args[0]
    inputs = []
    for arg in args[1:]:
        if ':' in arg:
            path, rename = arg.split(':', 1)
        else:
            path = arg
            rename = os.path.basename(arg)
        with open(path, 'rb') as f:
            data = f.read()
        crc = ww_crc(rename)
        inputs.append((rename, crc, data))

    # Sort entries by signed CRC value — engine does binary search.
    inputs.sort(key=lambda x: x[1])

    # Build the file: 2-byte count + 4-byte data_size + per-entry SubBlocks + data blob.
    count = len(inputs)
    data_size = sum(len(data) for _, _, data in inputs)

    with open(outmix, 'wb') as f:
        f.write(struct.pack('<HI', count, data_size))
        offset = 0
        for name, crc, data in inputs:
            f.write(struct.pack('<iII', crc, offset, len(data)))
            offset += len(data)
        for _, _, data in inputs:
            f.write(data)

    print(f'packed {count} files ({data_size} bytes of data) -> {outmix}')
    for name, crc, data in inputs:
        print(f'  {name:<24s} crc={crc:#010x} size={len(data)}')
    return 0


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    cmd = argv[1]
    args = argv[2:]
    if cmd == 'list':
        return cmd_list(args)
    if cmd == 'extract':
        return cmd_extract(args)
    if cmd == 'pack':
        return cmd_pack(args)
    print(f'unknown command: {cmd}', file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
