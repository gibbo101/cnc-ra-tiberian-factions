#!/usr/bin/env python3
"""Reads members of Tiberian Sun MIX archives by name: encrypted, flagged and bare MIX blobs.

License: GPL v3.
"""
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ra_mix_extract as ra  # noqa: E402


def ts_id(name):
    """Tiberian Sun's MIX name hash: CRC32 of the upper-cased name, padded to a multiple of four."""
    n = name.upper()
    length = len(n)
    whole = length & ~3
    if length & 3:
        n += chr(length - whole)
        n += n[whole] * (3 - (length & 3))
    return zlib.crc32(n.encode("ascii")) & 0xFFFFFFFF


def entries(blob):
    """(entries, data start, bytes the offsets index) of an encrypted, flagged or bare MIX blob."""
    first, second = struct.unpack_from("<hh", blob, 0)
    if first == 0 and second & 0x02:
        parsed = ra._parse_mix_blob(blob)
        if parsed:
            return parsed
    base = 4 if first == 0 else 0
    count = struct.unpack_from("<H", blob, base)[0]
    table = base + 6
    return [struct.unpack_from("<iII", blob, table + i * 12) for i in range(count)], table + count * 12, blob


def member(blob, name):
    """A named member's bytes, or None."""
    found, start, raw = entries(blob)
    want = ts_id(name)
    for crc, offset, size in found:
        if crc & 0xFFFFFFFF == want:
            return raw[start + offset:start + offset + size]
    return None
