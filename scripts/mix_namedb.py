#!/usr/bin/env python3
'''
CRC -> filename resolver for MIX archives.

Westwood MIX SubBlock entries key files by a CRC of the (uppercased)
filename, not the name itself, so a raw `list` of a mix shows only hashes.
This module reverses those hashes using the name database shipped with
Vanilla Conquer's mixtool: tools/mixtool/mixnamedb_data.cpp, a ~29k-entry
table of {file_name, file_desc, ra_crc, ts_crc} derived from the XCC mix
database (+ tomsons26 contributions).

The `ra_crc` column is exactly what scripts/mix_tools.py ww_crc() computes
(validated against the table), so resolution is a straight dict lookup keyed
by crc & 0xFFFFFFFF.

  from mix_namedb import resolve
  resolve(0x1D597662)            -> '00-0000.aud'
  resolve(crc, want_desc=True)   -> ('00-0000.aud', '<description>')

CLI:
  mix_namedb.py <crc-hex>        # resolve one CRC
  mix_namedb.py --stats          # entry counts

License: GPL v3 (the namedb source is GPL v3, inherited from Vanilla Conquer).
'''
import os
import re
import sys

_DEFAULT_DB = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'tools', 'mixtool', 'mixnamedb_data.cpp')

# Matches:  {"name", "desc", int32_t(0xHEX), int32_t(0xHEX)},
# Names/descs are quoted C strings (allow escaped chars); CRCs are signed
# 32-bit literals written as (optionally negative) hex.
_ENTRY_RE = re.compile(
    r'\{\s*"((?:[^"\\]|\\.)*)"\s*,'
    r'\s*"((?:[^"\\]|\\.)*)"\s*,'
    r'\s*int32_t\(\s*(-?(?:0[xX])?[0-9A-Fa-f]+)\s*\)\s*,'
    r'\s*int32_t\(\s*(-?(?:0[xX])?[0-9A-Fa-f]+)\s*\)\s*\}')

_RA_MAP = None   # crc&0xFFFFFFFF -> (name, desc)
_TS_MAP = None


def _to_u32(literal: str) -> int:
    base = 16 if ('x' in literal.lower() or _looks_hex(literal)) else 10
    val = int(literal, base)
    return val & 0xFFFFFFFF


def _looks_hex(literal: str) -> bool:
    s = literal.lstrip('-')
    return s.startswith(('0x', '0X'))


def load(path: str = None):
    '''Parse the namedb into (ra_map, ts_map). Cached after first call.'''
    global _RA_MAP, _TS_MAP
    if _RA_MAP is not None and path is None:
        return _RA_MAP, _TS_MAP
    src = path or _DEFAULT_DB
    ra_map, ts_map = {}, {}
    with open(src, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    for m in _ENTRY_RE.finditer(text):
        name, desc, ra_lit, ts_lit = m.groups()
        ra = _to_u32(ra_lit)
        ts = _to_u32(ts_lit)
        if ra != 0:
            ra_map.setdefault(ra, (name, desc))
        if ts != 0:
            ts_map.setdefault(ts, (name, desc))
    if path is None:
        _RA_MAP, _TS_MAP = ra_map, ts_map
    return ra_map, ts_map


def resolve(crc: int, want_desc: bool = False, ts: bool = False):
    '''Return the filename for a CRC, or None. RA hash by default.'''
    ra_map, ts_map = load()
    entry = (ts_map if ts else ra_map).get(crc & 0xFFFFFFFF)
    if entry is None:
        return None
    return entry if want_desc else entry[0]


def main(argv):
    if len(argv) < 2 or argv[1] in ('-h', '--help'):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    if argv[1] == '--stats':
        ra_map, ts_map = load()
        print(f'namedb: {len(ra_map)} RA-CRC names, {len(ts_map)} TS-CRC names')
        return 0
    crc = int(argv[1], 16)
    name = resolve(crc, want_desc=True)
    if name is None:
        print(f'{crc & 0xFFFFFFFF:#010x}: (unknown)')
        return 1
    print(f'{crc & 0xFFFFFFFF:#010x}: {name[0]}' + (f'  -- {name[1]}' if name[1] else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
