'''
Minimal Megafile (.MEG) reader for C&C Remastered Collection bundles.

Format reference: SOURCECODE/CnCTDRAMapEditor/Utility/Megafile.cs (EA C# code).
Layout: optional 8-byte header (magic 0xFFFFFFFF/0x8FFFFFFF + version), 4 unused
bytes, then num_files/num_strings/string_table_size as uint32. Followed by a
string table (uint16 length-prefixed entries) and a fixed-size file table
(20 bytes per SubFileData with Pack=2 alignment), then the raw data blobs at
absolute offsets recorded in the file table.

Typical use cases for this mod:

  # See what's in a bundle
  scripts/meg_extract.py list ~/.steam/.../Data/CONFIG.MEG

  # Pull every entry whose path contains 'BUILDABLES'
  scripts/meg_extract.py extract ~/.steam/.../Data/CONFIG.MEG BUILDABLES out/

The vanilla DATA\\XML\\OBJECTS\\UNITS\\RABUILDABLES.XML extracted from CONFIG.MEG
is the base our mod's RABUILDABLES.XML must derive from: shipping that exact
file (with our additions appended) keeps the launcher's PAK fallback working
for every vanilla BuildIcon asset we don't override, which keeps the mod
payload small.

License: GPL v3 (inherited from Vanilla Conquer base).
'''
import os
import struct
import sys

SUBFILE_RECORD_SIZE = 20  # ushort, uint, int, uint, uint, ushort with Pack=2


def open_meg(path):
    with open(path, "rb") as f:
        data = f.read()

    off = 0
    magic = struct.unpack_from("<I", data, off)[0]
    if magic in (0xFFFFFFFF, 0x8FFFFFFF):
        off += 8  # skip header_size + version
    off += 4  # one uint32 of unused space, per Megafile.cs

    num_files, num_strings, string_table_size = struct.unpack_from("<III", data, off)
    off += 12

    strings = []
    s_off = off
    for _ in range(num_strings):
        slen = struct.unpack_from("<H", data, s_off)[0]
        s_off += 2
        strings.append(data[s_off:s_off + slen].decode("latin-1"))
        s_off += slen
    off += string_table_size

    files = []
    for _ in range(num_files):
        rec = data[off:off + SUBFILE_RECORD_SIZE]
        _flags, _crc, _idx, size, dat_off, name_idx = struct.unpack("<HIiIIH", rec)
        files.append((strings[name_idx], size, dat_off))
        off += SUBFILE_RECORD_SIZE

    return data, files


def cmd_list(meg_path, pattern=None):
    _, files = open_meg(meg_path)
    for name, size, _ in files:
        if pattern is None or pattern.lower() in name.lower():
            print(f"{size:>10}  {name}")


def cmd_extract(meg_path, pattern, out_dir):
    data, files = open_meg(meg_path)
    os.makedirs(out_dir, exist_ok=True)
    count = 0
    for name, size, dat_off in files:
        if pattern.lower() in name.lower():
            base = os.path.basename(name.replace("\\", "/"))
            with open(os.path.join(out_dir, base), "wb") as out:
                out.write(data[dat_off:dat_off + size])
            count += 1
    print(f"extracted {count} files matching '{pattern}' to {out_dir}")


def usage():
    print("usage:")
    print("  meg_extract.py list <meg> [pattern]")
    print("  meg_extract.py extract <meg> <pattern> <outdir>")
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        usage()
    cmd = sys.argv[1]
    if cmd == "list":
        cmd_list(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif cmd == "extract":
        if len(sys.argv) < 5:
            usage()
        cmd_extract(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        usage()
