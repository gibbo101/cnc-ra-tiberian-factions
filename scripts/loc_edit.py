#!/usr/bin/env python3
"""Add/overwrite strings in a Remaster MASTERTEXTFILE_<lang>.LOC.

The .LOC binary format (reverse-engineered 2026-06-21, round-trips byte-identical):

  u32 count
  count x record: [u32 keyHash][u32 valLen(chars)][u32 keyLen(bytes)]   (sorted asc by keyHash)
  value section: all values concatenated, UTF-16LE, in record order
  key   section: all keys   concatenated, ASCII,    in record order

keyHash == zlib.crc32(key_ascii) & 0xffffffff. No offsets, no terminators — the
table is walked purely by the per-record lengths, and the launcher binary-searches
the hash column, so records MUST stay hash-sorted.

Unlike same-length in-place value edits (the old constraint), this ADDS records:
insert each new (key,value) in hash-sorted position, bump count, reserialize. The
file grows; meg_pack.py recomputes the MEG offset table, so the resized .LOC repacks
into a structurally valid CONFIG.MEG.

Usage:
  loc_edit.py add <in.loc> <out.loc> KEY=VALUE [KEY=VALUE ...]
  loc_edit.py get <in.loc> KEY
License: GPL v3.
"""
import struct, zlib, sys


def crc(key: str) -> int:
    return zlib.crc32(key.encode('ascii')) & 0xffffffff


def parse(data: bytes):
    count = struct.unpack_from('<I', data, 0)[0]
    recs = []
    off = 4
    for _ in range(count):
        h, vl, kl = struct.unpack_from('<III', data, off)
        off += 12
        recs.append([h, vl, kl])
    vo = off
    ko = off + sum(r[1] for r in recs) * 2
    out = []
    for h, vl, kl in recs:
        val = data[vo:vo + vl * 2]; vo += vl * 2
        key = data[ko:ko + kl];     ko += kl
        out.append((h, val, key))           # (hash, utf16 bytes, ascii bytes)
    return out


def build(recs) -> bytes:
    out = struct.pack('<I', len(recs))
    for h, val, key in recs:
        out += struct.pack('<III', h, len(val) // 2, len(key))
    out += b''.join(r[1] for r in recs)
    out += b''.join(r[2] for r in recs)
    return out


def add(recs, key: str, value: str):
    h = crc(key)
    kb = key.encode('ascii')
    vb = value.encode('utf-16-le')
    # overwrite if key already present (same hash + same key bytes)
    for i, (rh, _v, rk) in enumerate(recs):
        if rh == h and rk == kb:
            recs[i] = (h, vb, kb)
            return 'overwrote'
        if rh == h:
            raise SystemExit(f"FATAL: CRC32 collision adding {key!r} (hash {h:#010x} "
                             f"already used by {rk.decode('latin1')!r}) — pick another key")
    # insert in hash-sorted position
    lo, hi = 0, len(recs)
    while lo < hi:
        mid = (lo + hi) // 2
        if recs[mid][0] < h:
            lo = mid + 1
        else:
            hi = mid
    recs.insert(lo, (h, vb, kb))
    return 'added'


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    cmd = sys.argv[1]
    data = open(sys.argv[2], 'rb').read()
    recs = parse(data)
    if cmd == 'get':
        key = sys.argv[3]; h = crc(key); kb = key.encode('ascii')
        for rh, v, rk in recs:
            if rh == h and rk == kb:
                print(f"{key} = {v.decode('utf-16-le')!r}"); return
        print(f"{key}: NOT FOUND"); return
    if cmd == 'add':
        out = sys.argv[3]
        for kv in sys.argv[4:]:
            k, _, val = kv.partition('=')
            print(f"  {add(recs, k, val)}: {k} = {val!r}")
        # verify sort + reparse round-trips
        assert all(recs[i][0] <= recs[i + 1][0] for i in range(len(recs) - 1)), "sort broken"
        blob = build(recs)
        assert parse(blob) == recs, "round-trip mismatch"
        open(out, 'wb').write(blob)
        print(f"wrote {out}: {len(recs)} records, {len(blob)} bytes (was {len(data)})")
        return
    print(__doc__); sys.exit(1)


if __name__ == '__main__':
    main()
