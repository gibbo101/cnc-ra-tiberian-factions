#!/usr/bin/env python3
'''
Repacker for C&C Remastered .MEG (Megafile) archives.

Mirrors EA's MegafileBuilder.cs write format exactly. Critically, the MEG
format has NO checksum, signature, or encryption: the reader (Megafile.cs)
looks files up by their full path string and returns raw bytes at the
recorded offset, validating nothing. So a faithfully rebuilt MEG loads with
no integrity step -- which is what makes editing front-end data (campaign /
faction lists in CONFIG.MEG) possible at all, since those XMLs are NOT
reachable via the ccmod Data/ overlay.

Layout (little-endian):
  u32 magic (0xFFFFFFFF or 0x8FFFFFFF) | f32 version | u32 headerSize
  | u32 numFiles | u32 numStrings | u32 stringTableSize
  string table: numStrings * (u16 len + ASCII chars)   # full UPPERCASE paths
  file table:   numFiles * SubFileData (20B, Pack=2):
      u16 Flags | u32 CRC | i32 Index | u32 Size | u32 Offset | u16 NameIdx
  data: concatenated subfile bytes at their Offset (file-table order)

headerSize == 24 + 20*numFiles + stringTableSize == offset of the data section.

We preserve every record's Flags/CRC/Index/NameIndex and the string table
verbatim; only Size + Offset (and the data bytes) change for edited files.
Lookup is by path string, so preserved CRCs need not be recomputed.

Usage:
  meg_pack.py repack <src.meg> <out.meg> [<innerPathSuffix>=<localfile> ...]
      Rebuild src.meg into out.meg, replacing the bytes of any inner file
      whose stored path ends with <innerPathSuffix> (case-insensitive,
      slash-insensitive) with the contents of <localfile>. With no
      replacements it is a pure round-trip (should be byte-identical).
  meg_pack.py verify <a.meg> <b.meg>
      Report whether the two MEGs have identical file tables (name/size).

License: GPL v3.
'''
import struct
import sys

SUBFILE_FMT = '<HIiIIH'   # Flags, CRC, Index, Size, Offset, NameIdx
SUBFILE_SIZE = 20


def parse(path):
    with open(path, 'rb') as f:
        data = f.read()
    magic = struct.unpack_from('<I', data, 0)[0]
    if magic not in (0xFFFFFFFF, 0x8FFFFFFF):
        raise ValueError(f'not a MEG (magic={magic:#010x})')
    head8 = data[0:8]  # magic + version float, preserved verbatim
    num_files, num_strings, str_table_size = struct.unpack_from('<III', data, 12)
    off = 24
    strings = []  # raw bytes per string (path), preserved verbatim
    for _ in range(num_strings):
        slen = struct.unpack_from('<H', data, off)[0]
        off += 2
        strings.append(data[off:off + slen])
        off += slen
    recs = []  # [flags, crc, idx, size, offset, name_idx, data_bytes]
    for _ in range(num_files):
        flags, crc, idx, size, doff, nidx = struct.unpack_from(SUBFILE_FMT, data, off)
        off += SUBFILE_SIZE
        recs.append([flags, crc, idx, size, doff, nidx, data[doff:doff + size]])
    return head8, strings, recs


def build(head8, strings, recs):
    num_files = len(recs)
    st = b''.join(struct.pack('<H', len(s)) + s for s in strings)
    header_size = 24 + SUBFILE_SIZE * num_files + len(st)
    out = bytearray()
    out += head8
    out += struct.pack('<I', header_size)
    out += struct.pack('<III', num_files, len(strings), len(st))
    out += st
    cur = header_size
    blobs = []
    for flags, crc, idx, _size, _doff, nidx, blob in recs:
        out += struct.pack(SUBFILE_FMT, flags, crc, idx, len(blob), cur, nidx)
        blobs.append(blob)
        cur += len(blob)
    for blob in blobs:
        out += blob
    return bytes(out)


def _norm(p):
    return p.replace('\\', '/').lower()


def repack(src, out, replacements):
    head8, strings, recs = parse(src)
    # Map replacement suffix -> bytes
    repl = {}
    for spec in replacements:
        inner, local = spec.split('=', 1)
        with open(local, 'rb') as f:
            repl[_norm(inner)] = f.read()
    hits = 0
    for r in recs:
        name = strings[r[5]].decode('latin-1')
        n = _norm(name)
        for suffix, blob in repl.items():
            if n.endswith(suffix):
                r[6] = blob
                r[3] = len(blob)
                hits += 1
                print(f'  replaced {name} -> {len(blob)} bytes')
                break
    if len(repl) and hits == 0:
        print('WARNING: no inner files matched any replacement suffix', file=sys.stderr)
    with open(out, 'wb') as f:
        f.write(build(head8, strings, recs))
    print(f'wrote {out} ({len(recs)} files, {hits} replaced)')


def verify(a, b):
    _, sa, ra = parse(a)
    _, sb, rb = parse(b)
    fa = sorted((sa[r[5]].decode('latin-1'), len(r[6])) for r in ra)
    fb = sorted((sb[r[5]].decode('latin-1'), len(r[6])) for r in rb)
    if fa == fb:
        print(f'IDENTICAL file tables: {len(fa)} files, same names+sizes')
        return 0
    print(f'DIFFER: {len(fa)} vs {len(fb)} files')
    sa_set, sb_set = dict(fa), dict(fb)
    for name in sorted(set(sa_set) | set(sb_set)):
        if sa_set.get(name) != sb_set.get(name):
            print(f'  {name}: {sa_set.get(name)} vs {sb_set.get(name)}')
    return 1


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    if argv[1] == 'repack' and len(argv) >= 4:
        repack(argv[2], argv[3], argv[4:])
        return 0
    if argv[1] == 'verify' and len(argv) == 4:
        return verify(argv[2], argv[3])
    print(__doc__.strip(), file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
