#!/usr/bin/env python3
"""List / extract VQA movies from Tiberian Sun MIX archives (and the encrypted
RA MAIN.MIX / classic TD MOVIES.MIX in the Remastered CNCDATA folder).

Reuses (read-only) the Tiberian Factions repo's crypto + name database:
  scripts/ra_mix_extract.py  (RA/TS Blowfish header)
  scripts/mix_namedb.py      (XCC-derived CRC -> name table, RA and TS hashes)

  tsmix.py list    <mix> [--ts|--ra]            entries, names, sizes, type
  tsmix.py extract <mix> <outdir> [--ts|--ra]   every VQA (header FORM....WVQA)
Names that cannot be resolved are written as <crc8hex>.VQA.
"""
import os, struct, sys, zlib
REPO = '/home/gibbo101/Documents/development/cnc-remastered-mods/cnc-ra-tiberian-factions/scripts'
sys.path.insert(0, REPO)
import ra_mix_extract as ra
from mix_namedb import load as namedb_load
from mix_tools import ww_crc

def ts_id(name):
    n = name.upper(); l = len(n); a = l & ~3
    if l & 3:
        n += chr(l - a); n += n[a] * (3 - (l & 3))
    return zlib.crc32(n.encode('ascii')) & 0xFFFFFFFF

def parse(blob):
    first, second = struct.unpack_from('<hh', blob, 0)
    if first == 0 and (second & 0x02):
        p = ra._parse_mix_blob(blob)
        if p: return p
    if first == 0:
        count, datasize = struct.unpack_from('<HI', blob, 4); base = 10
    else:
        count, datasize = struct.unpack_from('<HI', blob, 0); base = 6
    ents = [struct.unpack_from('<iII', blob, base + i*12) for i in range(count)]
    return ents, base + count*12, blob

EXTRA_NAMES = []  # filled from movie-name candidates (see names_candidates())

def resolver(ts):
    ra_map, ts_map = namedb_load()
    m = dict(ts_map if ts else ra_map)
    for n in EXTRA_NAMES:
        m.setdefault(ts_id(n) if ts else (ww_crc(n) & 0xFFFFFFFF), (n, ''))
    return m

def entries(path, ts):
    blob = open(path, 'rb').read()
    ents, ds, raw = parse(blob)
    m = resolver(ts)
    out = []
    for crc, off, size in ents:
        c = crc & 0xFFFFFFFF
        data = raw[ds+off: ds+off+16]
        kind = 'VQA' if data[:4] == b'FORM' and data[8:12] == b'WVQA' else data[:4].hex()
        name, desc = m.get(c, (None, ''))
        out.append((c, off, size, kind, name, desc))
    return out, ds, raw

if __name__ == '__main__':
    cmd, path = sys.argv[1], sys.argv[2]
    ts = '--ra' not in sys.argv
    if cmd == 'list':
        ents, _, _ = entries(path, ts)
        for c, off, size, kind, name, desc in ents:
            print(f'{c:08x} {size:>10} {kind:9} {name or "?":16} {desc}')
    elif cmd == 'extract':
        outdir = sys.argv[3]; os.makedirs(outdir, exist_ok=True)
        ents, ds, raw = entries(path, ts)
        for c, off, size, kind, name, desc in ents:
            if kind != 'VQA': continue
            fn = name.upper() if name else f'{c:08X}.VQA'
            open(os.path.join(outdir, fn), 'wb').write(raw[ds+off: ds+off+size])
            print(f'{fn} {size}')


def extract_one(mix_path, crc, outdir, inner=None, ts=True):
    """Write the entry with hash `crc` (optionally inside nested mix `inner`,
    given by name) to outdir and return its path."""
    blob = open(mix_path, 'rb').read()
    if inner:
        ents, ds, raw = parse(blob)
        want = ts_id(inner) if ts else (ww_crc(inner) & 0xFFFFFFFF)
        for c, off, size in ents:
            if (c & 0xFFFFFFFF) == want:
                blob = raw[ds + off: ds + off + size]
                break
        else:
            raise KeyError(inner)
    ents, ds, raw = parse(blob)
    for c, off, size in ents:
        if (c & 0xFFFFFFFF) == crc:
            os.makedirs(outdir, exist_ok=True)
            out = os.path.join(outdir, f'{crc:08X}.VQA')
            open(out, 'wb').write(raw[ds + off: ds + off + size])
            return out
    raise KeyError(hex(crc))
