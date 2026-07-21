#!/usr/bin/env python3
"""Rewrite MASTERTEXTFILE string values in place, keeping every byte length identical.

The launcher reads CONFIG.MEG members at base-archive offsets, so an edited member must
keep its exact size (docs/config-meg-mod-delivery.md). Inside the .LOC the value table is
indexed by per-record lengths, so each individual string must also keep its own length --
a replacement is padded with spaces to match, and rejected if it is too long.

.LOC layout:
    u32 count
    count * (u32 hash, u32 value_len_in_utf16_units, u32 key_len_in_bytes)
    values, UTF-16LE, concatenated in record order
    keys, ASCII, concatenated in record order

Usage: loc_relabel.py <in.LOC> <out.LOC> KEY=text [KEY=text ...]
       loc_relabel.py <in.LOC> <out.LOC> @<edits-file>

An edits file holds one KEY=text per line; blank lines and lines starting with # are
ignored. Prefer it over command-line pairs for anything the build depends on -- the
shipped archive's edits used to live only inside the archive, and a rebuild from the
pristine base silently reverted them.
"""
import struct
import sys


def records(data):
    count = struct.unpack_from("<I", data, 0)[0]
    value_off = 4 + 12 * count
    out = []
    for i in range(count):
        _hash, vlen, klen = struct.unpack_from("<3I", data, 4 + 12 * i)
        out.append({"value_off": value_off, "vlen": vlen, "klen": klen})
        value_off += 2 * vlen
    key_off = value_off
    for r in out:
        r["key_off"] = key_off
        key_off += r["klen"]
    return out


def main(in_path, out_path, edits):
    data = bytearray(open(in_path, "rb").read())
    size_before = len(data)
    recs = records(data)
    by_key = {}
    for r in recs:
        by_key[bytes(data[r["key_off"]:r["key_off"] + r["klen"]]).decode("ascii", "ignore")] = r

    for key, text in edits:
        if key not in by_key:
            sys.exit(f"key not found: {key}")
        r = by_key[key]
        if len(text) > r["vlen"]:
            sys.exit(f"{key}: replacement is {len(text)} chars, only {r['vlen']} available")
        old = bytes(data[r["value_off"]:r["value_off"] + 2 * r["vlen"]]).decode("utf-16-le")
        padded = text.ljust(r["vlen"])
        data[r["value_off"]:r["value_off"] + 2 * r["vlen"]] = padded.encode("utf-16-le")
        print(f"  {key}: {old!r} -> {padded!r}")

    assert len(data) == size_before, "size changed"
    open(out_path, "wb").write(data)
    print(f"wrote {out_path}: {len(data)} bytes (== source)")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    args = []
    for arg in sys.argv[3:]:
        if arg.startswith("@"):
            for line in open(arg[1:], encoding="utf-8"):
                line = line.rstrip("\n")
                if line.strip() and not line.lstrip().startswith("#"):
                    args.append(line)
        else:
            args.append(arg)
    pairs = []
    for arg in args:
        k, _, v = arg.partition("=")
        pairs.append((k, v))
    main(sys.argv[1], sys.argv[2], pairs)
