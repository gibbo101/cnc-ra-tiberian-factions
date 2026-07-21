#!/usr/bin/env python3
"""Rewrite MASTERTEXTFILE string values, keeping the FILE's byte length identical.

The launcher reads CONFIG.MEG members at base-archive offsets, so an edited member must
keep its exact size (docs/config-meg-mod-delivery.md). That constraint applies to the
file, NOT to each string: the .LOC locates a value by summing the lengths ahead of it in
a table, so a value may grow if the table is rewritten and the bytes are taken back
somewhere else in the same file.

    u32 count
    count * (u32 hash, u32 value_len_in_utf16_units, u32 key_len_in_bytes)
    values, UTF-16LE, concatenated in record order   <- position implied by the lengths
    keys, ASCII, concatenated in record order

Each edited value is stored at its own natural length. Any shortfall or surplus against
the original total is absorbed by a slack string, padded or trimmed with spaces; by
default that is the longest edited value, or name one with --slack KEY. Growth beyond
the available slack is refused rather than silently resized.

Usage: loc_relabel.py <in.LOC> <out.LOC> [--slack KEY] KEY=text [KEY=text ...]
       loc_relabel.py <in.LOC> <out.LOC> [--slack KEY] @<edits-file>

An edits file holds one KEY=text per line; blank lines and lines starting with # are
ignored. Prefer it over command-line pairs for anything the build depends on -- the
shipped archive's edits used to live only inside the archive, and a rebuild from the
pristine base silently reverted them.
"""
import struct
import sys


def load(data):
    """Return (records, values, keys); records are dicts with hash/value/key."""
    count = struct.unpack_from("<I", data, 0)[0]
    value_off = 4 + 12 * count
    recs = []
    for i in range(count):
        hashv, vlen, klen = struct.unpack_from("<3I", data, 4 + 12 * i)
        recs.append({"hash": hashv, "vlen": vlen, "klen": klen, "voff": value_off})
        value_off += 2 * vlen
    key_off = value_off
    for r in recs:
        r["key"] = data[key_off:key_off + r["klen"]].decode("ascii", "ignore")
        r["value"] = data[r["voff"]:r["voff"] + 2 * r["vlen"]].decode("utf-16-le")
        key_off += r["klen"]
    return recs


def emit(recs):
    """Rebuild the file from records, recomputing every length in the table."""
    count = len(recs)
    table = bytearray(struct.pack("<I", count))
    values = bytearray()
    keys = bytearray()
    for r in recs:
        encoded = r["value"].encode("utf-16-le")
        table += struct.pack("<3I", r["hash"], len(encoded) // 2, r["klen"])
        values += encoded
        keys += r["key"].encode("ascii").ljust(r["klen"], b"\x00")[:r["klen"]]
    return bytes(table + values + keys)


def main(in_path, out_path, edits, slack_key):
    data = open(in_path, "rb").read()
    size_before = len(data)
    recs = load(data)
    by_key = {r["key"]: r for r in recs}

    edited = []
    for key, text in edits:
        if key not in by_key:
            sys.exit(f"key not found: {key}")
        r = by_key[key]
        grew = len(text) > r["vlen"]
        # Values that still fit keep their original slot, padded as before, so the only
        # lengths that move are the ones that had to. A value that outgrows its slot is
        # stored at its true length and the difference comes out of the slack string.
        print(f"  {key}: {r['value'].strip()!r} -> {text!r}" + (" (grown)" if grew else ""))
        r["value"] = text if grew else text.ljust(r["vlen"])
        edited.append(r)

    if not edited:
        sys.exit("no edits given")

    # Absorb the difference in one string so the file's total length is unchanged.
    slack = by_key[slack_key] if slack_key else max(edited, key=lambda r: len(r["value"]))
    if slack_key and slack_key not in by_key:
        sys.exit(f"slack key not found: {slack_key}")
    rebuilt = emit(recs)
    delta = len(rebuilt) - size_before
    if delta % 2:
        sys.exit("odd byte delta; UTF-16 values cannot absorb it")
    units = delta // 2
    if units > 0:
        trimmed = slack["value"].rstrip()
        if len(slack["value"]) - len(trimmed) < units:
            sys.exit(f"need {units} more chars than {slack['key']} has in trailing space; "
                     f"pick a --slack key with more room")
        slack["value"] = slack["value"][:len(slack["value"]) - units]
    elif units < 0:
        slack["value"] = slack["value"] + " " * (-units)
    print(f"  slack: {slack['key']} adjusted by {-units:+d} chars")

    out = emit(recs)
    assert len(out) == size_before, f"size mismatch: {len(out)} != {size_before}"
    open(out_path, "wb").write(out)
    print(f"wrote {out_path}: {len(out)} bytes (== source)")


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 3:
        sys.exit(__doc__)
    in_path, out_path, rest = args[0], args[1], args[2:]
    slack_key = None
    if "--slack" in rest:
        i = rest.index("--slack")
        slack_key = rest[i + 1]
        rest = rest[:i] + rest[i + 2:]
    expanded = []
    for arg in rest:
        if arg.startswith("@"):
            for line in open(arg[1:], encoding="utf-8"):
                line = line.rstrip("\n")
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                # `!slack=KEY` names the string that gives up (or takes on) trailing space
                # so growth stays byte-neutral. Kept in the edits file so the whole recipe
                # lives in one reviewable place.
                if line.startswith("!slack="):
                    slack_key = line.split("=", 1)[1].strip()
                    continue
                expanded.append(line)
        else:
            expanded.append(arg)
    pairs = []
    for arg in expanded:
        k, _, v = arg.partition("=")
        pairs.append((k, v))
    main(in_path, out_path, pairs, slack_key)
